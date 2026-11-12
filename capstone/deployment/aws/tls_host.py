"""Root-owned EC2 TLS lifecycle. Never exposes the app through the HTTP listener."""

import argparse
import fcntl
import ipaddress
import json
import subprocess
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization

AGREEMENT = "accepted-v1.8-2026-07-06"
WEBROOT = "/var/lib/music-store/acme"
CERTBOT = "/opt/music-store-certbot/bin/certbot"
CONFIG = Path("/etc/nginx/conf.d/music-store.conf")
CERTDIR = Path("/etc/letsencrypt/live/music-store-v1")
STATE = Path("/var/lib/music-store/tls-state.json")
CAFILE = Path("/etc/pki/tls/certs/ca-bundle.crt")


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=240)


def public_ip():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    token_request = urllib.request.Request(
        "http://169.254.169.254/latest/api/token",
        method="PUT",
        headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
    )
    with opener.open(token_request, timeout=3) as response:
        token = response.read().decode()
    request = urllib.request.Request(
        "http://169.254.169.254/latest/meta-data/public-ipv4",
        headers={"X-aws-ec2-metadata-token": token},
    )
    with opener.open(request, timeout=3) as response:
        value = response.read().decode().strip()
    address = ipaddress.ip_address(value)
    if address.version != 4 or not address.is_global:
        raise ValueError("A public IPv4 address is required")
    return str(address)


def certificate_status(ip, certdir=CERTDIR, cafile=CAFILE, runner=run, now=None):
    """Check SAN, validity, production trust and key pairing before opening HTTPS."""
    now = now or datetime.now(UTC)
    try:
        cert = x509.load_pem_x509_certificate((certdir / "cert.pem").read_bytes())
        key = serialization.load_pem_private_key(
            (certdir / "privkey.pem").read_bytes(), password=None
        )
        encoding = (serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        if key.public_key().public_bytes(*encoding) != cert.public_key().public_bytes(*encoding):
            return None
        names = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        if ipaddress.ip_address(ip) not in names.get_values_for_type(x509.IPAddress):
            return None
        if not cert.not_valid_before_utc <= now < cert.not_valid_after_utc - timedelta(days=1):
            return None
        runner(
            [
                "openssl",
                "verify",
                "-CAfile",
                str(cafile),
                "-untrusted",
                str(certdir / "chain.pem"),
                str(certdir / "cert.pem"),
            ]
        )
        # nginx -t below checks that privkey.pem matches this certificate.
        return {
            "ip": ip,
            "expires": cert.not_valid_after_utc.isoformat(),
            "fingerprint": cert.fingerprint(hashes.SHA256()).hex(),
        }
    except (OSError, ValueError, x509.ExtensionNotFound, subprocess.SubprocessError):
        return None


def nginx_config(ip=None):
    http = f"""server {{
    listen 80 default_server;
    server_name _;
    location ^~ /.well-known/acme-challenge/ {{ root {WEBROOT}; }}
    location / {{ {f"return 308 https://{ip}$request_uri;" if ip else "return 503;"} }}
}}
"""
    if not ip:
        return http
    # Validate even callers outside the metadata adapter; never interpolate arbitrary input.
    address = ipaddress.ip_address(ip)
    if address.version != 4 or not address.is_global:
        raise ValueError("A public IPv4 address is required")
    return (
        http
        + f"""server {{
    listen 443 ssl default_server;
    server_name {ip};
    ssl_certificate {CERTDIR}/fullchain.pem;
    ssl_certificate_key {CERTDIR}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    client_max_body_size 64k;
    location / {{
        limit_req zone=music_requests burst=60 nodelay;
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Host {ip};
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $music_upgrade;
        proxy_set_header X-Forwarded-Proto https;
        proxy_buffering off;
        proxy_read_timeout 180s;
    }}
}}
"""
    )


def apply_state(status, config=CONFIG, state=STATE, runner=run, reload=True):
    try:
        contents = nginx_config(status["ip"] if status else None)
        record = {"ready": bool(status), **(status or {})}
        previous = state.read_text() if state.exists() else ""
        current = json.dumps(record, sort_keys=True) + "\n"
        changed = not config.exists() or config.read_text() != contents or previous != current
        config.parent.mkdir(parents=True, exist_ok=True)
        temporary = config.with_suffix(".pending")
        temporary.write_text(contents)
        temporary.replace(config)
        runner(["nginx", "-t"])
        if reload and changed:
            runner(["systemctl", "reload", "nginx"])
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(current)
    except Exception:
        # Do not retain an old running TLS config after an unsuccessful safety transition.
        try:
            state.parent.mkdir(parents=True, exist_ok=True)
            state.write_text('{"ready": false, "error": "TLS transition failed"}\n')
        except OSError:
            pass  # Disk failure must not prevent the listener being stopped below.
        if reload:
            runner(["systemctl", "stop", "nginx"])
        raise
    return record


def reconcile(ip_getter=public_ip, checker=certificate_status, applier=apply_state):
    try:
        ip = ip_getter()
    except Exception:
        ip = None
    try:
        status = checker(ip) if ip else None
    except Exception:
        status = None
    applier(status)
    return ip, status


def agreement_accepted(path=Path("/etc/music-store/ca-agreement")):
    return path.read_text().strip() == AGREEMENT


def certbot_args(ip, staging=False):
    args = [
        CERTBOT,
        "certonly",
        "--non-interactive",
        "--agree-tos",
        "--register-unsafely-without-email",
        "--webroot",
        "--webroot-path",
        WEBROOT,
        "--preferred-profile",
        "shortlived",
        "--cert-name",
        "music-store-v1",
        "--ip-address",
        ip,
        "--force-renewal",
    ]
    if staging:
        args += [
            "--staging",
            "--config-dir",
            "/var/lib/music-store/staging/config",
            "--work-dir",
            "/var/lib/music-store/staging/work",
            "--logs-dir",
            "/var/log/music-store-staging",
        ]
    return args


def maintain():
    ip, status = reconcile()
    if not ip or not agreement_accepted():
        raise RuntimeError(
            "Certificate issuance requires public IP and recorded CA agreement approval"
        )
    marker = Path("/var/lib/music-store/staging-ip")
    if not status:
        if not marker.exists() or marker.read_text().strip() != ip:
            run(certbot_args(ip, staging=True))
            marker.write_text(ip)
        run(certbot_args(ip))
    else:
        run([CERTBOT, "renew", "--non-interactive", "--cert-name", "music-store-v1"])
    _, status = reconcile()
    if not status:
        raise RuntimeError("No trusted, current public-IP certificate is available")


def execute(action):
    try:
        if action == "acme-only":
            # nginx ExecStartPre: never resume an old-IP TLS listener after boot.
            apply_state(None, reload=False)
        elif action == "maintain":
            maintain()
        elif action == "dry-run":
            if not agreement_accepted():
                raise RuntimeError("Certificate agreement approval is required")
            run(
                [
                    CERTBOT,
                    "renew",
                    "--dry-run",
                    "--non-interactive",
                    "--cert-name",
                    "music-store-v1",
                ]
            )
            reconcile()
        else:
            reconcile()
    except Exception as error:
        # Provider keys, certificate private keys and command output never enter this log.
        print(json.dumps({"ready": False, "error_type": type(error).__name__}))
        raise SystemExit(1) from None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["acme-only", "guard", "maintain", "dry-run"])
    args = parser.parse_args()
    # Serialize timer, boot and operator transitions, including certificate symlink changes.
    with open("/run/music-store-tls.lock", "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"event": "TLS lifecycle already running"}))
            if args.action == "acme-only":
                # A boot reset may not be skipped while an old TLS config remains on disk.
                raise SystemExit(1) from None
            return
        execute(args.action)


if __name__ == "__main__":
    main()

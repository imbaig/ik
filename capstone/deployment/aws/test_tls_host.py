"""Real test certificates exercise public-TLS admission without calling a CA or AWS."""

import importlib.util
import ipaddress
import shutil
import subprocess
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import tls_host as tls
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class TLSAdmission(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.certdir = self.root / "certificate"
        self.certdir.mkdir()
        self.now = datetime.now(UTC)
        self.ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Local test CA only")])
        self.ca = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(self.ca_key.public_key())
            .serial_number(1)
            .not_valid_before(self.now - timedelta(days=1))
            .not_valid_after(self.now + timedelta(days=30))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(self.ca_key, hashes.SHA256())
        )
        self.cafile = self.root / "test-ca.pem"
        self.cafile.write_bytes(self.ca.public_bytes(serialization.Encoding.PEM))
        self.issue()

    def issue(self, ip="1.1.1.1", expires=None, starts=None):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([]))
            .issuer_name(self.ca.subject)
            .public_key(self.key.public_key())
            .serial_number(2)
            .not_valid_before(starts or self.now - timedelta(minutes=1))
            .not_valid_after(expires or self.now + timedelta(days=6))
            .add_extension(
                x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(ip))]),
                critical=True,
            )
            .sign(self.ca_key, hashes.SHA256())
        )
        data = cert.public_bytes(serialization.Encoding.PEM)
        (self.certdir / "cert.pem").write_bytes(data)
        (self.certdir / "chain.pem").write_bytes(self.cafile.read_bytes())
        (self.certdir / "fullchain.pem").write_bytes(data + self.cafile.read_bytes())
        (self.certdir / "privkey.pem").write_bytes(
            self.key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

    def check(self, ip="1.1.1.1"):
        return tls.certificate_status(ip, self.certdir, self.cafile, now=self.now)

    def test_matching_valid_trusted_certificate_is_admitted(self):
        self.assertEqual(self.check()["ip"], "1.1.1.1")

    def test_old_ip_is_rejected_after_address_change(self):
        self.assertIsNone(self.check("8.8.8.8"))

    def test_near_expiry_and_future_certificate_are_rejected(self):
        self.issue(expires=self.now + timedelta(hours=23))
        self.assertIsNone(self.check())
        self.issue(starts=self.now + timedelta(hours=1))
        self.assertIsNone(self.check())

    def test_untrusted_chain_is_rejected_by_actual_openssl(self):
        self.cafile.write_text("not a trusted CA")
        self.assertIsNone(self.check())

    def test_missing_or_mismatched_private_key_is_rejected(self):
        (self.certdir / "privkey.pem").unlink()
        self.assertIsNone(self.check())
        self.issue()
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        (self.certdir / "privkey.pem").write_bytes(
            other.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        self.assertIsNone(self.check())

    def test_malformed_certificate_fails_closed(self):
        (self.certdir / "cert.pem").write_text("not a certificate")
        self.assertIsNone(self.check())

    @unittest.skipUnless(shutil.which("nginx"), "nginx parser exercised in Linux CI/EC2")
    def test_both_rendered_modes_pass_real_nginx_parser(self):
        with patch.object(tls, "CERTDIR", self.certdir):
            for ip in (None, "1.1.1.1"):
                path = self.root / "nginx.conf"
                path.write_text(
                    f"pid {self.root}/nginx.pid; error_log {self.root}/error.log;\n"
                    "events {}\nhttp { access_log off; "
                    f"client_body_temp_path {self.root}/body; "
                    f"proxy_temp_path {self.root}/proxy; "
                    f"fastcgi_temp_path {self.root}/fastcgi; "
                    f"uwsgi_temp_path {self.root}/uwsgi; "
                    f"scgi_temp_path {self.root}/scgi; "
                    "map $http_upgrade $music_upgrade { default upgrade; '' close; } "
                    "limit_req_zone $binary_remote_addr zone=music_requests:1m rate=10r/s;\n"
                    + tls.nginx_config(ip)
                    + "\n}\n"
                )
                result = subprocess.run(
                    [
                        "nginx",
                        "-t",
                        "-p",
                        str(self.root),
                        "-c",
                        str(path),
                        "-e",
                        str(self.root / "error.log"),
                    ],
                    capture_output=True,
                    text=True,
                )
                log = self.root / "error.log"
                diagnostics = result.stderr + (log.read_text() if log.exists() else "")
                self.assertEqual(result.returncode, 0, diagnostics)


class SafeTransitions(unittest.TestCase):
    def test_no_http_chat_and_no_redirect_until_tls_is_ready(self):
        unready = tls.nginx_config()
        self.assertIn("return 503", unready)
        self.assertNotIn("proxy_pass", unready)
        self.assertNotIn("listen 443", unready)
        ready = tls.nginx_config("1.1.1.1")
        http, https = ready.split("listen 443", 1)
        self.assertNotIn("proxy_pass", http)
        self.assertIn("https://1.1.1.1$request_uri", http)
        self.assertIn("http://127.0.0.1:7860", https)
        with self.assertRaises(ValueError):
            tls.nginx_config("1.1.1.1; injected")

    def test_metadata_or_checker_errors_withdraw_public_chat(self):
        states = []

        def fail(*args):
            raise RuntimeError("synthetic adapter error")

        tls.reconcile(fail, lambda ip: {"ip": ip}, states.append)
        tls.reconcile(lambda: "1.1.1.1", fail, states.append)
        self.assertEqual(states, [None, None])

    def test_nginx_validation_failure_stops_old_listener(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []

            def runner(args):
                calls.append(args)
                if args == ["nginx", "-t"]:
                    raise subprocess.CalledProcessError(1, args)

            with self.assertRaises(subprocess.SubprocessError):
                tls.apply_state(
                    None, Path(directory) / "site.conf", Path(directory) / "state.json", runner
                )
            self.assertEqual(calls[-1], ["systemctl", "stop", "nginx"])
            self.assertIn('"ready": false', (Path(directory) / "state.json").read_text())

    def test_config_io_failure_also_stops_old_listener(self):
        with tempfile.TemporaryDirectory() as directory:
            blocked = Path(directory) / "not-a-directory"
            blocked.write_text("file")
            calls = []
            with self.assertRaises(OSError):
                tls.apply_state(
                    None, blocked / "site.conf", Path(directory) / "state.json", calls.append
                )
            self.assertEqual(calls[-1], ["systemctl", "stop", "nginx"])

    def test_pending_agreement_never_calls_certbot(self):
        with (
            patch.object(tls, "reconcile", return_value=("1.1.1.1", None)),
            patch.object(tls, "agreement_accepted", return_value=False),
            patch.object(tls, "run") as runner,
        ):
            with self.assertRaises(RuntimeError):
                tls.maintain()
            runner.assert_not_called()

    def test_staging_keeps_its_certificates_out_of_production_paths(self):
        command = tls.certbot_args("1.1.1.1", staging=True)
        self.assertIn("--staging", command)
        self.assertIn("/var/lib/music-store/staging/config", command)
        self.assertIn("shortlived", command)
        self.assertNotIn("/etc/letsencrypt", command)

    def test_template_excludes_cloudfront_and_closed_ports(self):
        spec = importlib.util.spec_from_file_location(
            "template", Path(__file__).with_name("make_template.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        template = module.template()
        resources = template["Resources"]
        self.assertNotIn("AWS::CloudFront::Distribution", [r["Type"] for r in resources.values()])
        rules = resources["ServerSecurityGroup"]["Properties"]["SecurityGroupIngress"]
        self.assertEqual({r["FromPort"] for r in rules}, {80, 443})
        self.assertEqual(template["Parameters"]["CertificateAgreement"]["Default"], "pending")


if __name__ == "__main__":
    unittest.main()

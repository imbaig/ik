"""Explicit credential-free release checks. Uses only disposable loopback containers."""

import argparse
import http.cookiejar
import json
import os
import secrets
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production", required=True)
    parser.add_argument("--smoke", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--port", type=int, default=17860)
    args = parser.parse_args()
    # Use the local managed daemon explicitly; retain configured proxy/CA settings.
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    env = {
        k: v
        for k, v in os.environ.items()
        if k
        not in {
            "DOCKER_HOST",
            "DOCKER_CONTEXT",
            "DOCKER_TLS",
            "DOCKER_TLS_VERIFY",
            "DOCKER_CERT_PATH",
        }
    }

    def command(*arguments, check=True):
        return subprocess.run(
            docker + list(arguments), env=env, capture_output=True, text=True, check=check
        ).stdout.strip()

    suffix = secrets.token_hex(5)
    name = "capstone-release-check-" + suffix
    password = secrets.token_urlsafe(24)
    login = ["-e", "APP_LOGIN_USER=smoke", "-e", "APP_LOGIN_PASSWORD=" + password]
    base = f"http://127.0.0.1:{args.port}"
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    )

    def get(path, data=None):
        try:
            with opener.open(base + path, data=data, timeout=3) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    created = []
    try:
        command(
            "run",
            "-d",
            "--pull=never",
            "--name",
            name,
            "-p",
            f"127.0.0.1:{args.port}:7860",
            *login,
            args.smoke,
        )
        created.append(name)
        for _ in range(60):
            try:
                status, raw = get("/healthz")
                if status == 200:
                    break
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(1)
        else:
            raise AssertionError("Container health timeout; inspect its redacted logs")
        info = json.loads(raw)
        assert info["ready"] and info["packaging_revision"] == args.revision
        assert info["input_source_revision"] == "7d137081b579b49128068d9dcc4be009cfea9def"
        assert info["mode"] == "deterministic-test-only"
        assert json.loads(get("/version")[1])["packaging_revision"] == args.revision
        for path in ("/config", "/gradio_api/info"):
            assert get(path)[0] == 401, path
        bad = urllib.parse.urlencode({"username": "smoke", "password": "wrong"}).encode()
        assert get("/login", bad)[0] == 400
        good = urllib.parse.urlencode({"username": "smoke", "password": password}).encode()
        assert get("/login", good)[0] == 200
        assert get("/config")[0] == 200
        assert get("/gradio_api/info")[0] == 200
        for path in ("/app/data/provenance.json", "/run/secrets/proxy_ca"):
            assert get("/gradio_api/file=" + path)[0] in {403, 404}, path
        assert command("exec", name, "id", "-u") == "10001"
        result = command(
            "exec",
            name,
            "python",
            "-c",
            """
import sys
sys.path.insert(0, "/opt")
from pathlib import Path
from smoke_entry import service
from music_store.db import initialize_database
from music_store.application_contracts import Action, ActionKind
with_db=initialize_database(Path("/app/data/chinook"))
app=service(with_db)
h=app.new_session()
r=app.dispatch(h,Action(ActionKind.SEND,"Show Queen albums"))
assert r.facts and r.facts[0].tool == "get_albums_by_artist"
assert "Queen" in r.text
r=app.dispatch(h,Action(ActionKind.SEND,"Show my invoices"))
assert r.session.waiting and not r.session.verified
r=app.dispatch(h,Action(ActionKind.RESUME_VERIFICATION,"1"))
assert r.session.verified and r.facts
assert r.facts[0].tool == "get_invoices_by_customer_sorted_by_date"
app.close(h)
with_db.close()
print("real service/catalog/verification/invoice integration passed (deterministic models)")
""",
        )
        print(result)
        # Production never includes test code, developer files or mounted build CA.
        result = command(
            "run",
            "--rm",
            "--pull=never",
            args.production,
            "python",
            "-c",
            """
import os
from pathlib import Path
assert os.getuid() == 10001
for p in ("/opt/ui_harness.py", "/opt/smoke_entry.py", "/app/.env",
          "/app/.git", "/app/tests", "/run/secrets/proxy_ca"):
    assert not Path(p).exists(), p
assert Path("/app/data/chinook").is_dir()
print("production nonroot/file exclusions passed")
""",
        )
        print(result)
        for extra in ([], login):
            failure_name = name + ("-missing-key" if extra else "-missing-login")
            command("create", "--name", failure_name, *extra, args.production)
            created.append(failure_name)
            command("start", "-a", failure_name, check=False)
            code = command("inspect", "--format", "{{.State.ExitCode}}", failure_name)
            assert code != "0"
            logs = command("logs", failure_name)
            # Docker logs may write failures to stderr; inspect both streams explicitly.
            logs += subprocess.run(
                docker + ["logs", failure_name], env=env, capture_output=True, text=True
            ).stderr
            expected = "OPENAI_API_KEY is required" if extra else "Login requires"
            assert expected in logs
            assert password not in logs
            command("rm", failure_name)
            created.remove(failure_name)
        health = json.loads(command("inspect", "--format", "{{json .State.Health}}", name))
        # Wait only for Docker's own periodic healthcheck, not a live provider.
        for _ in range(20):
            if health["Status"] == "healthy":
                break
            time.sleep(1)
            health = json.loads(command("inspect", "--format", "{{json .State.Health}}", name))
        assert health["Status"] == "healthy"
        labels = json.loads(
            command("image", "inspect", "--format", "{{json .Config.Labels}}", args.production)
        )
        assert labels["org.opencontainers.image.revision"] == args.revision
        assert labels["app.input_source_revision"] == info["input_source_revision"]
        print(
            json.dumps(
                {
                    "checks": "passed",
                    "metadata": info,
                    "production_labels": labels,
                    "production_image": command(
                        "image", "inspect", "--format", "{{.Id}}", args.production
                    ),
                    "smoke_image": command("image", "inspect", "--format", "{{.Id}}", args.smoke),
                },
                indent=2,
            )
        )
    finally:
        for container in created:
            command("rm", "-f", container, check=False)


if __name__ == "__main__":
    main()

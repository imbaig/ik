# v0 provider-neutral package (issue12)

This packages the unchanged application from source checkpoint
`7d137081b579b49128068d9dcc4be009cfea9def` (`capstone-v0.0.0-preview`).
The immutable tag is source evidence, not a deployment or merge approval. PR9 remains
an unmerged dependency. The packaging commit is separately recorded in each image's
OCI revision label and `/version`; it must be the exact checked-out package revision.

No hosting provider has been selected and no public deployment is authorized here.
The parent coordinator inspected the deployment slides: pages9/21 teach both Hugging
Face and AWS, pages22–46 cover HF and49–55 an EC2 example. No AWS-only or Azure
mandate was identified. The Python3.11 slide example does not override the project's
Python3.12 requirement. Original course PDFs remain outside Git. No REST application
layer is required by these slides; the two operational routes use Gradio's own server.

## Build from a clean checkout

Run from `capstone`, with Docker/BuildKit and network access to the pinned Python image,
PyPI and pinned public Chinook SQL source. Dependencies are exact versions in
`requirements.lock`; no dependency changes are made by this package.

```sh
PACKAGE_SHA=$(git rev-parse HEAD)
docker build --target production --build-arg PACKAGE_REVISION="$PACKAGE_SHA" \
  -t "capstone-v0:$PACKAGE_SHA" .
docker build --target smoke --build-arg PACKAGE_REVISION="$PACKAGE_SHA" \
  -t "capstone-v0-test:$PACKAGE_SHA" .
```

In the managed cloud, keep the configured Docker proxy and pass its trusted CA bundle
as a BuildKit secret: add `--secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt`.
No certificate is copied into the image. Never disable TLS verification. The Python
base is digest-pinned. Build downloads the existing revision/checksum-pinned Chinook
SQL, verifies it, and runtime re-verifies the cached source before opening its read-only
in-memory database. SQL is in the image, not checked into Git. Bootstrap failure fails
the build. No host database/cache, `.env`, Git history, coursework or raw reports are
in the allowlisted context. Production does not contain the smoke harness.

## Private local run

Supply runtime secrets through a host-managed secret mount or secret environment
injection. Do not use Docker build arguments, Dockerfile ENV, committed env files or
command-line literal application keys. Example assumes host-managed readable files:

```sh
docker run --rm --name music-store-v0 -p 127.0.0.1:7860:7860 \
  --mount type=bind,src=/absolute/private/secrets,dst=/run/secrets,readonly \
  -e APP_LOGIN_USER_FILE=/run/secrets/login-user \
  -e APP_LOGIN_PASSWORD_FILE=/run/secrets/login-password \
  -e OPENAI_API_KEY_FILE=/run/secrets/provider-key \
  "capstone-v0:$PACKAGE_SHA"
```

Files must be readable by container UID/GID10001. Never mount an entire home directory.
Default `APP_ACCESS_MODE=required` fails closed without a nonblank login name and a
password of at least12 characters. The gate protects Gradio UI/config/API routes;
it is demo access control, not customer authentication, rate limiting or production
IAM. Customer verification remains the unchanged server-side demo identifier workflow.
Explicit `local-only` opt-out is accepted only with loopback `HOST`; container-wide
`HOST=0.0.0.0` cannot opt out. HOST defaults0.0.0.0 inside Docker; PORT defaults7860.
Change the container PORT and corresponding host port together. Keep host binding
loopback. Public TLS, ingress, persistent secrets, rate limiting and hosting approval
are separate future decisions. No share tunnel is enabled.

`/healthz` verifies process/database readiness, **not provider availability or model
quality**. `/version` and health metadata are public and contain only version, source,
package and dataset identifiers. They never contain customer/profile/key values.
Missing provider configuration fails normal startup; this is not a successful smoke
run. The normal entrypoint never falls back to a fake application.

## Credential-free container checks

The explicit `smoke` target alone includes `tests/ui_harness.py`, deterministic model
and extractor doubles with real services/graphs/tools/verified database. It displays
a test banner and returns `mode=deterministic-test-only`. This is container integration
evidence, never live-model evidence. Run the committed check from this directory:

```sh
python deployment/check_container.py --production "capstone-v0:$PACKAGE_SHA" \
  --smoke "capstone-v0-test:$PACKAGE_SHA" --revision "$PACKAGE_SHA"
```

It creates synthetic test login values, binds only127.0.0.1, validates health/version,
login and API denial/acceptance, blocked file access, nonroot ownership, actual tool
results via real services, missing configuration and production file exclusions, then
removes its own containers. It never supplies an application API key. Read the script
before use. Docker daemon access is required; failure is reported rather than waived.

## Isolation, rollback and pending checks

Keep v0/v1 images, names, ports, processes and URLs distinct. Do not retag the source
checkpoint or overwrite the current Mac checkout/process. Running an older immutable
image is the rollback; restart loses sessions and all process-local preference memory.
New conversation clears conversation/verification, but process preferences persist for
that verified customer until process exit. Separate v0/v1 processes do not share this
memory. No persistence, migration or subpath gateway is implemented. Prefer separate
URLs first; a shared gateway requires later design/security work.

Original14/16 live evidence is retained. Issues10/11 remain deferred by Imran until
before demo; packaging neither fixes nor silently waives them. Actual provider checks
on the final package and hosting remain pending for the local coordinator. Agent
review and container checks do not constitute Imran's merge or release approval.

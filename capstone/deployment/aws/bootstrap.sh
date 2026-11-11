#!/bin/bash
# CloudFormation substitutes only the three named placeholders below. No secrets here.
set -eu
umask 077
# Fixed calendar deadline survives reboots; stopping leaves the disk billable.
deadline=$(date -u --date='+${StopAfterDays} days' '+%Y-%m-%d %H:%M:%S UTC')
cat > /etc/systemd/system/music-store-stop.service <<'STOP'
[Service]
Type=oneshot
ExecStart=/usr/sbin/shutdown -h now
STOP
cat > /etc/systemd/system/music-store-stop.timer <<STOP
[Timer]
OnCalendar=$deadline
Persistent=true
[Install]
WantedBy=timers.target
STOP
systemctl daemon-reload
systemctl enable --now music-store-stop.timer

dnf install -y docker git nginx python3.11 python3.11-pip openssl
systemctl enable --now docker
mkdir -p /opt/music-store/state /run/music-store
chown 10001:10001 /opt/music-store/state
chmod 700 /opt/music-store/state
# Provide build headroom on the course-permitted 4 GiB grading instance.
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
git clone --no-checkout https://github.com/imbaig/ik.git /opt/music-store/source
cd /opt/music-store/source
git checkout --detach '${SourceRevision}'
cd capstone
docker build --target production --build-arg PACKAGE_REVISION='${SourceRevision}' -t music-store-v1:'${SourceRevision}' .

cat > /usr/local/bin/music-store-secret <<'SECRET'
#!/bin/bash
set -eu
umask 077
install -d -m 700 /run/music-store
aws ssm get-parameter --region us-east-1 --name '${SecretParameterName}' --with-decryption --query Parameter.Value --output text > /run/music-store/provider-key
chown 10001:10001 /run/music-store/provider-key
chmod 400 /run/music-store/provider-key
SECRET
chmod 700 /usr/local/bin/music-store-secret

cat > /etc/systemd/system/music-store-v1.service <<'SERVICE'
[Unit]
Description=Music Store v1 public grading sample
Requires=docker.service
After=docker.service network-online.target
[Service]
Restart=on-failure
RestartSec=10
ExecStartPre=/usr/local/bin/music-store-secret
ExecStartPre=-/usr/bin/docker rm -f music-store-v1
ExecStart=/usr/bin/docker run --name music-store-v1 --read-only --cap-drop ALL --security-opt no-new-privileges --memory=1400m --memory-swap=2g --pids-limit=256 --tmpfs /tmp:rw,nosuid,nodev,size=128m --mount type=bind,src=/run/music-store/provider-key,dst=/run/secrets/provider-key,readonly --mount type=bind,src=/opt/music-store/state,dst=/app/.cache -p 127.0.0.1:7860:7860 -e APP_ACCESS_MODE=public-demo -e PUBLIC_DEMO_ACK=PUBLIC_SAMPLE_DATA_ONLY -e PUBLIC_DEMO_DAILY_ACTIONS=60 -e PUBLIC_DEMO_TOTAL_ACTIONS=300 -e MODEL_MAX_TOKENS=600 -e OPENAI_API_KEY_FILE=/run/secrets/provider-key music-store-v1:${SourceRevision}
ExecStop=/usr/bin/docker stop -t 30 music-store-v1
[Install]
WantedBy=multi-user.target
SERVICE

# Host-only certificate tooling is separate from application dependencies/image.
python3.11 -m venv /opt/music-store-certbot
/opt/music-store-certbot/bin/python -m pip install --require-hashes --only-binary=:all: -r deployment/aws/certbot.lock
install -d -m 755 /usr/local/lib/music-store /var/lib/music-store /var/lib/music-store/acme
install -d -m 700 /etc/music-store
install -m 644 deployment/aws/tls_host.py /usr/local/lib/music-store/tls_host.py
printf '%s\n' '${CertificateAgreement}' > /etc/music-store/ca-agreement
chmod 600 /etc/music-store/ca-agreement
systemctl stop nginx || true
cat > /etc/nginx/nginx.conf <<'NGINX'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /run/nginx.pid;
events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    server_tokens off;
    access_log off;
    map $http_upgrade $music_upgrade { default upgrade; '' close; }
    limit_req_zone $binary_remote_addr zone=music_requests:10m rate=10r/s;
    include /etc/nginx/conf.d/music-store.conf;
}
NGINX
install -d /etc/systemd/system/nginx.service.d
cat > /etc/systemd/system/nginx.service.d/music-store.conf <<'NGINXUNIT'
[Service]
ExecStartPre=
ExecStartPre=/usr/bin/rm -f /run/nginx.pid
ExecStartPre=/opt/music-store-certbot/bin/python /usr/local/lib/music-store/tls_host.py acme-only
ExecStartPre=/usr/sbin/nginx -t
NGINXUNIT
cat > /etc/systemd/system/music-store-certificate.service <<'CERT'
[Unit]
Description=Obtain or renew trusted Music Store public IP certificate
Wants=nginx.service
After=nginx.service network-online.target
[Service]
Type=oneshot
UMask=0077
TimeoutStartSec=600
ExecStart=/opt/music-store-certbot/bin/python /usr/local/lib/music-store/tls_host.py maintain
CERT
cat > /etc/systemd/system/music-store-certificate.timer <<'CERTTIMER'
[Timer]
OnBootSec=2min
OnCalendar=*-*-* 00,12:00:00 UTC
RandomizedDelaySec=300
Persistent=true
[Install]
WantedBy=timers.target
CERTTIMER
cat > /etc/systemd/system/music-store-tls-guard.service <<'GUARD'
[Unit]
Description=Withdraw public chat on invalid, expiring or mismatched TLS certificate
Wants=nginx.service
After=nginx.service network-online.target
[Service]
Type=oneshot
UMask=0077
ExecStart=/opt/music-store-certbot/bin/python /usr/local/lib/music-store/tls_host.py guard
GUARD
cat > /etc/systemd/system/music-store-tls-guard.timer <<'GUARDTIMER'
[Timer]
OnBootSec=30s
OnUnitActiveSec=5min
[Install]
WantedBy=timers.target
GUARDTIMER
systemctl daemon-reload
systemctl enable --now music-store-v1 nginx
systemctl enable --now music-store-certificate.timer music-store-tls-guard.timer
systemctl start music-store-certificate.service

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

dnf install -y docker git nginx
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

# The security group admits only CloudFront origin traffic. No public SSH or Gradio port.
cat > /etc/nginx/conf.d/music-store.conf <<'NGINX'
map $http_upgrade $music_upgrade { default upgrade; '' close; }
limit_req_zone $binary_remote_addr zone=music_requests:10m rate=10r/s;
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 64k;
    location / {
        limit_req zone=music_requests burst=60 nodelay;
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $music_upgrade;
        proxy_set_header X-Forwarded-Proto https;
        proxy_buffering off;
        proxy_read_timeout 180s;
    }
}
NGINX
# Remove the distribution's example server to avoid a duplicate default listener.
python3 - <<'PY'
from pathlib import Path
p = Path('/etc/nginx/nginx.conf')
s = p.read_text()
start = s.find('    server {')
if start >= 0:
    depth, end = 0, start
    for end in range(start, len(s)):
        depth += (s[end] == '{') - (s[end] == '}')
        if end > start and depth == 0 and s[end] == '}':
            break
    s = s[:start] + s[end + 1:]
p.write_text(s)
PY
nginx -t
systemctl daemon-reload
systemctl enable --now music-store-v1 nginx


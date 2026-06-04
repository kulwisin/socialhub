#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SocialHub — Ubuntu Production Server Setup Script
#
# Tested on: Ubuntu 22.04 LTS (AMD64)
#
# Run as root (or with sudo):
#   curl -fsSL https://raw.githubusercontent.com/.../setup-prod.sh | sudo bash
#
# Or clone first:
#   git clone <repo> /opt/socialhub
#   sudo bash /opt/socialhub/scripts/setup-prod.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-ubuntu}"
INSTALL_DIR="/opt/socialhub"
REPO_URL="${REPO_URL:-}"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  SocialHub — Production Server Setup                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── System packages ───────────────────────────────────────────────────────────
echo "▶ Updating system packages…"
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
  curl \
  git \
  make \
  ufw \
  fail2ban \
  logrotate \
  ca-certificates \
  gnupg \
  lsb-release \
  unattended-upgrades

# ── Docker ────────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "▶ Installing Docker Engine…"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
  systemctl enable --now docker
else
  echo "✓ Docker already installed: $(docker --version)"
fi

# Add deploy user to docker group
if id "$DEPLOY_USER" &>/dev/null; then
  usermod -aG docker "$DEPLOY_USER"
  echo "✓ Added $DEPLOY_USER to docker group"
fi

# ── Firewall ──────────────────────────────────────────────────────────────────
echo "▶ Configuring UFW firewall…"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh        # 22
ufw allow http       # 80
ufw allow https      # 443
ufw --force enable
echo "✓ UFW configured (ssh, http, https)"

# ── fail2ban ─────────────────────────────────────────────────────────────────
echo "▶ Enabling fail2ban…"
systemctl enable --now fail2ban
echo "✓ fail2ban enabled"

# ── Application directory ─────────────────────────────────────────────────────
echo "▶ Setting up application directory at ${INSTALL_DIR}…"
if [[ -n "$REPO_URL" ]] && [[ ! -d "${INSTALL_DIR}/.git" ]]; then
  git clone "$REPO_URL" "$INSTALL_DIR"
elif [[ ! -d "$INSTALL_DIR" ]]; then
  mkdir -p "$INSTALL_DIR"
  echo "  Created ${INSTALL_DIR} — clone your repo here manually."
fi

mkdir -p "${INSTALL_DIR}/backups"
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "$INSTALL_DIR"
echo "✓ Application directory ready"

# ── Backup cron ───────────────────────────────────────────────────────────────
CRON_JOB="0 3 * * * cd ${INSTALL_DIR} && bash scripts/backup/backup.sh >> /var/log/socialhub-backup.log 2>&1"
if ! crontab -u "${DEPLOY_USER}" -l 2>/dev/null | grep -qF "socialhub-backup"; then
  (crontab -u "${DEPLOY_USER}" -l 2>/dev/null; echo "$CRON_JOB") | crontab -u "${DEPLOY_USER}" -
  echo "✓ Daily backup cron installed (03:00 UTC)"
fi

# ── Log rotation ──────────────────────────────────────────────────────────────
cat > /etc/logrotate.d/socialhub << 'EOF'
/var/log/socialhub-*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ubuntu ubuntu
}
EOF
echo "✓ Log rotation configured"

# ── Swap (helps on small VMs) ─────────────────────────────────────────────────
if [[ ! -f /swapfile ]]; then
  echo "▶ Creating 2 GB swapfile…"
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  echo "✓ Swap enabled"
fi

# ── Unattended upgrades ───────────────────────────────────────────────────────
dpkg-reconfigure -f noninteractive unattended-upgrades
echo "✓ Unattended security upgrades enabled"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Setup complete!                                         ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Next steps:                                             ║"
echo "║                                                          ║"
echo "║  1. cd /opt/socialhub                                    ║"
echo "║  2. cp .env.example .env && nano .env                    ║"
echo "║  3. cp backend/.env.example backend/.env && nano...      ║"
echo "║  4. docker compose up -d --build                         ║"
echo "║  5. docker compose exec backend alembic upgrade head     ║"
echo "║  6. Set up SSL: see DEPLOYMENT.md → SSL section          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

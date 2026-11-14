#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo 'Install Docker Engine and Docker Compose plugin first.'; exit 1; }
docker compose version >/dev/null || { echo 'Docker Compose plugin missing'; exit 1; }
if [[ ! -f .env ]]; then
  read -rp 'Primary mail domain (example.com): ' domain
  read -rp 'Webmail hostname (webmail.example.com): ' host
  read -rp 'ACME email address: ' acme
  [[ "$domain" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]] || { echo 'Invalid domain'; exit 1; }
  printf 'PRIMARY_DOMAIN=%s\nWEBMAIL_HOST=%s\nACME_EMAIL=%s\nTZ=UTC\n' "$domain" "$host" "$acme" > .env
  chmod 600 .env
fi
set -a; source .env; set +a
printf '%s\n' "$PRIMARY_DOMAIN" >> config/domains.txt
sort -u -o config/domains.txt config/domains.txt
if [[ ! -f "/etc/letsencrypt/live/mail.${PRIMARY_DOMAIN}/fullchain.pem" ]]; then
  echo "Mail TLS certificate missing. Obtain one for mail.${PRIMARY_DOMAIN} with certbot before starting."
  echo "Example: sudo certbot certonly --standalone -d mail.${PRIMARY_DOMAIN} (port 80 must be free)"
  exit 1
fi
docker compose config --quiet
docker compose up -d
printf 'AGMail started. Webmail: https://%s\n' "$WEBMAIL_HOST"

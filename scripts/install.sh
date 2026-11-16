#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -f .env ]] || { echo 'Create .env from .env.example and configure it first'; exit 1; }
mkdir -p config/dms
[[ -f config/domains.txt ]] || cp config/domains.txt.example config/domains.txt
sudo docker compose config --quiet
echo 'Configuration validated. Check ports, DNS and certificates before running docker compose up.'

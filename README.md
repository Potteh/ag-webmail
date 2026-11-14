# AGMail — Multi-domain self-hosted mail for Ubuntu

AGMail is a Docker Compose distribution of docker-mailserver (Postfix, Dovecot, Rspamd) with Roundcube webmail and Caddy HTTPS. A single instance can host mailboxes on multiple domains.

**Status: starter deployment, not production-audited.** The Roundcube Elastic interface is used; AGMail logo and optional CSS are supplied but not automatically applied. Domain/user administration is command-line based.

## Requirements

Ubuntu 22.04/24.04, Docker Engine and Compose v2, public static IP, DNS control, inbound/outbound TCP 25, correct reverse DNS/PTR, and ideally 4 GB RAM. Allow TCP 25, 465, 587, 993, 80 and 443.

## Install

```bash
sudo apt update && sudo apt install -y ca-certificates curl certbot
# Install Docker Engine and Compose plugin: https://docs.docker.com/engine/install/ubuntu/
cp .env.example .env
nano .env
chmod 600 .env
# Set A records first, then obtain a bootstrap mail certificate:
sudo certbot certonly --standalone -d mail.YOUR_PRIMARY_DOMAIN
bash scripts/install.sh
```

Visit https://webmail.YOUR_PRIMARY_DOMAIN once Caddy has issued its HTTPS certificate.

## Multiple domains

```bash
bash scripts/agmail domain add example.org
bash scripts/agmail domain add another.net
bash scripts/agmail domain list
bash scripts/agmail user add alice@example.org
bash scripts/agmail user add bob@another.net
bash scripts/agmail user list
bash scripts/agmail user password alice@example.org
bash scripts/agmail dkim
bash scripts/agmail status
bash scripts/agmail logs
```

Adding a domain registers it in AGMail's inventory; it does not create a mailbox or catch-all. Users sign in with their full email address. Secondary domains share the primary mail host.

## DNS for every domain

- MX: `10 mail.YOUR_PRIMARY_DOMAIN.`
- SPF TXT: `v=spf1 mx -all` (adjust for relays and actual sending hosts)
- DMARC TXT at `_dmarc.DOMAIN`: `v=DMARC1; p=none` initially
- DKIM TXT: publish generated signing key at the configured selector under `_domainkey.DOMAIN`
- A: `mail.YOUR_PRIMARY_DOMAIN` and `webmail.YOUR_PRIMARY_DOMAIN` to your server
- PTR: sending IP reverse DNS to `mail.YOUR_PRIMARY_DOMAIN`

Verify DKIM behavior with docker-mailserver v15/Rspamd before production. Confirm SPF, DKIM and DMARC alignment on externally delivered messages.

## TLS renewal caveat

The standalone Certbot bootstrap command needs port 80 free; Caddy subsequently owns port 80. **Unattended mail TLS renewal is not configured.** Implement DNS-01 or a coordinated challenge flow and a mailserver restart/reload hook before production use. Caddy independently manages web HTTPS certificates.

## Backups and security

Back up `mail-data`, `mail-state`, `roundcube-data`, `config/dms`, and the private `.env`. Test restores, external inbound/outbound delivery, authentication, TLS, and rejection of unauthenticated relaying. Keep Docker images updated. ClamAV is disabled by default. This starter does not include a GUI admin panel, automated backups, verified DKIM automation, or outbound SMTP relay fallback.

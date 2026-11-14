# AGMail — Multi-domain Ubuntu email server

AGMail combines docker-mailserver (Postfix/Dovecot/Rspamd), Roundcube with AGMail branding, Caddy HTTPS, and a local-only admin dashboard for domain and mailbox management.

**Security status: development / staging release. Not production-audited.** The admin service uses the Docker socket (host-root-equivalent access). Never expose port 8787 publicly; keep it bound to 127.0.0.1 and access over SSH. Production deployments should replace this with a narrowly privileged management service.

## Ubuntu setup

Install Docker Engine + Compose plugin from https://docs.docker.com/engine/install/ubuntu/ and Certbot.

```bash
cp .env.example .env
nano .env
chmod 600 .env
# Point mail.example.com and webmail.example.com A records to the server.
# Before starting Caddy, acquire a bootstrap mail TLS certificate:
sudo certbot certonly --standalone -d mail.example.com
mkdir -p config/dms
cp config/domains.txt.example config/domains.txt
# Replace sample domains with your actual domains:
nano config/domains.txt
docker compose config --quiet
docker compose up -d --build
```

Set a **unique random** AGMAIL_ADMIN_PASSWORD of at least 20 characters. Never commit .env, certificates, mailbox data, or private keys. To avoid an accidental default credential, deployment refuses to start if the admin variables are missing; do not use the placeholder password.

### Webmail

Browse https://webmail.example.com. Users sign in with their full email address. The AGMail branding plugin is enabled through Roundcube's plugins environment setting; verify it loads in your image version.

### Admin dashboard (SSH tunnel)

On your local workstation:
```bash
ssh -L 8787:127.0.0.1:8787 YOUR_USER@YOUR_SERVER
```
Open http://127.0.0.1:8787 and enter the admin credentials from .env. The admin UI supports adding domains, listing mailboxes, creating mailboxes and changing passwords. It does not currently delete accounts or manage quotas. It is HTTP Basic authentication over loopback/SSH, not a public SSO login.

### Multi-domain DNS

Each domain needs an MX record pointing to the primary mail host, SPF, DKIM and DMARC. The primary host needs A and PTR records. Generate DKIM keys and publish their TXT records. Test SPF/DKIM/DMARC alignment, sending and receiving, TLS, and anti-relay controls before going live.

### Operations

```bash
docker compose ps
docker compose logs -f --tail=100
bash scripts/agmail domain add second-domain.example
bash scripts/agmail user add person@second-domain.example
```

### Outstanding production work

- Automated mail certificate renewal and mailserver reload; Caddy only renews its own web certificate.
- DKIM signing and alignment verification for each hosted domain.
- Backups and tested restore procedures, monitoring, and security review.
- Docker socket privilege separation for the admin backend.
- Mail delivery testing on a real VPS (outbound port 25 may be blocked).
- SMTP/IMAP client compatibility testing and Roundcube plugin/theme testing.

**No claim is made that these services have been started or end-to-end tested on your VPS.**

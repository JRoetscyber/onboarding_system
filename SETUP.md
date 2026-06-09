# JO4 Dev Onboarding Setup

## Local setup

1. Create a virtual environment and install dependencies.
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in secrets.
3. Run the Flask app.
   ```bash
   flask --app app run
   ```
4. Open `/onboard` for the public form and `/admin/login` for the dashboard.

The app creates the SQLite database automatically in `instance/onboarding.sqlite`.

## Google API setup

1. Create a Google Cloud project.
2. Enable Google Drive API and Google Docs API. Enable Gmail API only if you later replace SMTP with Gmail API sending.
3. Create a service account and download its JSON key.
4. Save the key as `credentials/google_service_account.json`.
5. Create or choose the parent Google Drive folder.
6. Share that Drive folder with the service account email.
7. Put the folder ID in `.env` as `GDRIVE_PARENT_FOLDER_ID`.

If Google credentials are missing, submissions still save locally; Drive and Docs creation is skipped.

## SMTP email setup

1. Configure a sender account such as Gmail with an app password or SendGrid SMTP.
2. Fill in `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, and `ADMIN_EMAIL`.
3. If SMTP credentials are missing, email sending is skipped.

## Docker

Build and start:
```bash
docker compose up -d --build
```

View logs:
```bash
docker compose logs -f web
```

Restart after code changes:
```bash
docker compose up -d --build web
```

Stop everything:
```bash
docker compose down
```

## Ubuntu VPS with Cloudflare Tunnel

This app joins the shared `tunnel-net` Docker network. The shared `cloudflared` container on the server handles routing — no separate tunnel container is needed here.

1. Install Docker and the Docker Compose plugin on the VPS.
2. Clone this repo onto the VPS.
3. Copy `.env.example` to `.env` and fill in all values.
4. Place `google_service_account.json` in `credentials/`.
5. Add the following entry to `/root/.cloudflared/config.yml` **before** the final `http_status:404` line:
   ```yaml
   - hostname: onboard.jo4dev.co.za
     service: http://jo4dev_onboard:6040
   - hostname: www.onboard.jo4dev.co.za
     service: http://jo4dev_onboard:6040
   ```
6. Restart the shared tunnel: `docker restart cloudflared`
7. Add two CNAME records in the Cloudflare DNS dashboard pointing to `031f1933-5ab5-4d2c-b0d7-65ed4aafb07f.cfargotunnel.com` (proxied).
8. Run:
   ```bash
   docker compose up -d --build
   ```

No Nginx, SSL certificate setup, or open inbound VPS ports are required because Cloudflare terminates HTTPS and the tunnel connects outbound.

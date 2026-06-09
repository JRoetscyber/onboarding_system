# JO4 Dev — Client Onboarding & SEO System
## Codex CLI Build Prompt

---

## Project overview

Build a full-stack client onboarding and SEO system for **JO4 Dev**, a full-stack product studio based in Johannesburg, South Africa. The system consists of:

1. A **public-facing client intake form** (hosted at a shareable URL — e.g. `/onboard` — that JO4 Dev sends to each new client)
2. A **private admin dashboard** (password-protected) for JO4 Dev to view submissions, track SEO audits, and manage project tasks
3. **Google Drive integration** — on form submission, automatically create a shared Google Drive folder named after the client's company, save their uploaded logo and any photos there, and create a shared Google Doc with their onboarding summary
4. **Automated confirmation email** sent to the client after they complete the form
5. A **full discovery questionnaire** embedded in the intake form to precisely identify what the client wants

---

## Tech stack

- **Backend:** Python + Flask
- **Frontend:** HTML, CSS (Bootstrap 5), vanilla JavaScript
- **Database:** SQLite (via SQLAlchemy) for storing submissions locally
- **Google APIs:** Google Drive API v3, Google Docs API, Gmail API (or SMTP via Flask-Mail as fallback)
- **Auth:** Simple admin password (environment variable) protecting the dashboard route
- **File uploads:** Werkzeug for handling logo/photo uploads before pushing to Drive

---

## Project structure

```
jo4dev-onboarding/
├── app.py                  # Flask app, routes, Google API logic
├── config.py               # Environment config (loaded from .env)
├── models.py               # SQLAlchemy models
├── requirements.txt
├── .env.example
├── credentials/
│   └── google_service_account.json   # Google service account key (gitignored)
├── templates/
│   ├── base.html
│   ├── onboard.html        # Public client intake form (multi-step)
│   ├── success.html        # Thank-you page shown after submission
│   ├── admin/
│   │   ├── login.html
│   │   ├── dashboard.html  # Submission list + stats
│   │   ├── client.html     # Individual client detail page
│   │   ├── seo_audit.html  # SEO checklist per client
│   │   └── tasks.html      # Kanban task board per client
├── static/
│   ├── css/style.css
│   └── js/form.js          # Multi-step form logic + validation
└── email_templates/
    ├── client_confirmation.html   # HTML email sent to client
    └── admin_notification.html    # Internal notification to JO4 Dev
```

---

## Section 1 — Public intake form (`/onboard`)

Build a **multi-step form** with a progress bar. Each step has client-side validation before allowing Next. Steps:

### Step 1 — About your business
- Company name (required)
- Industry (dropdown: E-commerce, SaaS/Tech, Healthcare, Finance, Hospitality, Education, Real estate, Retail, Non-profit, Other)
- Your full name (required)
- Your job title
- Email address (required, validated)
- Phone number
- Physical address / city
- Existing website URL (optional)
- How did you hear about JO4 Dev? (dropdown: Google, Referral, Social media, LinkedIn, Other)

### Step 2 — Upload brand assets
- Company logo upload (PNG/SVG/JPG, max 5MB) — required
- Additional brand photos (multiple, optional, max 10MB each)
- Brand colours (two colour pickers: primary, secondary)
- Font preferences (free text, optional)

### Step 3 — Project goals & scope
- What services do you need? (multi-select checkboxes):
  - New website from scratch
  - Website redesign
  - SEO (Search Engine Optimisation)
  - E-commerce / online store
  - Web application / portal
  - Content writing
  - Google Ads / paid media
  - Social media management
  - Email marketing
  - Website maintenance & hosting
  - Analytics & reporting
- In one sentence, what is the main goal of this project? (textarea, required)
- Who is your target audience? (textarea — prompt: age range, location, interests, pain points)
- Who are your top 3 competitors? List their websites if possible. (textarea)
- What do you like about your competitors' sites? (textarea)
- What do you dislike or want to do differently? (textarea)

### Step 4 — Website & content discovery
- Do you have existing content (copy, images, videos) to use? (Yes / Partially / No)
- How many pages do you estimate needing? (dropdown: 1–3, 4–7, 8–15, 15+, Not sure)
- Which pages do you definitely need? (multi-select: Home, About, Services, Portfolio/Work, Blog, Contact, FAQ, Pricing, E-commerce store, Login/Portal, Other)
- Do you need a blog or news section? (Yes / No / Maybe)
- Do you sell products or services online? (Products / Services / Both / Neither)
- If e-commerce: how many products approximately? (number field, shown conditionally)
- What languages does your site need? (checkboxes: English, Afrikaans, Zulu, Xhosa, Other)
- Do you need a multilingual site? (Yes / No / Maybe)

### Step 5 — SEO & marketing
- Have you done SEO before? (Yes — currently active / Yes — stopped / No / Not sure)
- Are you currently running any paid advertising? (Google Ads / Meta Ads / Both / None)
- What keywords or phrases do you want to rank for? (textarea, prompt: think about what your customers type into Google)
- Do you have a Google Business Profile? (Yes — verified / Yes — unverified / No / Don't know)
- Do you have Google Analytics or Search Console set up? (Yes — both / Yes — one only / No / Don't know)
- What social media platforms are you active on? (multi-select: Facebook, Instagram, LinkedIn, TikTok, X/Twitter, YouTube, Pinterest, None)

### Step 6 — Timeline & budget
- When do you need the project completed? (date picker + urgency radio: Flexible, Specific deadline, ASAP)
- What is your total budget range? (radio buttons):
  - Under R10,000
  - R10,000 – R25,000
  - R25,000 – R50,000
  - R50,000 – R100,000
  - R100,000 – R250,000
  - R250,000+
  - Prefer not to say / open to discussion
- How would you prefer to pay? (Once-off / Monthly retainer / Milestone-based / Open to discussion)
- Do you have an ongoing maintenance budget after launch? (Yes / No / Discuss later)

### Step 7 — Final details
- How involved do you want to be during the project? (dropdown: Very involved — weekly check-ins / Moderately involved — milestone updates / Hands-off — trust the team)
- Who will be our main point of contact? (name + email — pre-filled from step 1 with option to change)
- Are there any technical requirements or integrations you know of? (textarea: e.g. CRM, booking system, payment gateway, membership portal)
- Is there anything else we should know? (large textarea)
- How would you rate your digital presence today? (1–5 star rating widget)
- Upload any reference files — mood boards, competitor screenshots, brand guidelines (multiple file upload, optional)
- [ ] I confirm the information above is accurate and I agree to JO4 Dev's terms of service (checkbox, required — link terms to `/terms`)

On submit:
- Show a loading spinner
- Validate all required fields
- POST to `/api/onboard/submit`

---

## Section 2 — Backend: form submission handler (`POST /api/onboard/submit`)

On successful form submission, the backend must:

1. **Save to database** — store all form fields in a `Submission` model with timestamp, unique `submission_id`, and status field (default: `new`)

2. **Create Google Drive folder** — using the Google Drive API with a service account:
   - Create a folder named `[CompanyName] — JO4 Dev Onboarding` inside a configured parent folder (set in `.env` as `GDRIVE_PARENT_FOLDER_ID`)
   - Upload the client's logo and any photos to this folder
   - Set the folder as shared (anyone with link can view, or share directly with the client's email)

3. **Create a Google Doc** — inside the same Drive folder:
   - Title: `[CompanyName] — Onboarding Brief`
   - Content: A formatted onboarding summary document containing all questionnaire answers, neatly structured with headings per step
   - Include the logo inline at the top if possible
   - Share the doc with the client's email (Editor or Commenter access)

4. **Send confirmation email to client** — using Flask-Mail (SMTP) or Gmail API:
   - From: `hello@jo4dev.co.za` (or configured sender in `.env`)
   - To: client's email
   - Subject: `Welcome to JO4 Dev, [FirstName]! Your onboarding is complete.`
   - HTML email body (use `email_templates/client_confirmation.html`) containing:
     - JO4 Dev logo header
     - Personalised greeting
     - Summary of what they submitted (services selected, budget range, timeline)
     - Link to their shared Google Doc
     - What happens next (3 clear steps: 1. JO4 Dev reviews, 2. Discovery call scheduled, 3. Proposal delivered)
     - Contact details for JO4 Dev
     - Professional footer

5. **Send internal notification to JO4 Dev admin** — same email setup:
   - Subject: `New onboarding submission: [CompanyName]`
   - Body: full submission summary + link to admin dashboard

6. **Return JSON** `{ "success": true, "submission_id": "..." }` to the frontend

---

## Section 3 — Admin dashboard (`/admin`)

Protect all `/admin` routes with a simple session-based login (password stored in `.env` as `ADMIN_PASSWORD`).

### `/admin/login` — Login page
Plain login form with password field. On success, set session and redirect to dashboard.

### `/admin/dashboard` — Submissions overview
- Stats cards: Total submissions, New (unreviewed), In progress, Completed
- Submissions table: Company name | Contact | Services | Budget | Submitted date | Status | Actions
- Filter by status, date range, service type
- Click a row to go to `/admin/client/<submission_id>`

### `/admin/client/<id>` — Client detail page
- All questionnaire answers displayed neatly
- Status dropdown (New → Reviewed → Proposal sent → Active → Completed → On hold)
- Link to their Google Drive folder and Google Doc
- Notes field (internal notes, not visible to client)
- Tabs:
  - **Overview** — all form answers
  - **SEO Audit** — interactive checklist (same 24-item audit from the prototype, linked to this client)
  - **Tasks** — Kanban board (To do / In progress / Done) with tags: SEO, Design, Dev, Content

### `/admin/client/<id>/seo`
- 24-item SEO checklist as described in the prototype
- Items stored per client in the database
- Progress bar showing % complete
- Export audit as PDF button (use WeasyPrint or similar)

### `/admin/client/<id>/tasks`
- Add / edit / delete tasks
- Drag to change column (use Sortable.js via CDN)
- Tasks stored in database per client

---

## Section 4 — Database models (`models.py`)

```python
# Submission — one per client
# Fields: id, submission_id (uuid), company_name, industry, contact_name,
#         contact_email, phone, address, existing_url, referral_source,
#         services (JSON list), main_goal, target_audience, competitors,
#         likes_competitors, dislikes_competitors, has_content, page_count,
#         pages_needed (JSON), needs_blog, sells_online, product_count,
#         languages (JSON), multilingual, seo_history, paid_ads,
#         target_keywords, google_business, analytics_setup,
#         social_platforms (JSON), launch_date, deadline_urgency, budget,
#         payment_preference, maintenance_budget, involvement_level,
#         main_contact_name, main_contact_email, integrations, other_notes,
#         digital_presence_rating, logo_filename, logo_drive_url,
#         photo_filenames (JSON), gdrive_folder_id, gdrive_folder_url,
#         gdoc_id, gdoc_url, status, admin_notes, submitted_at, updated_at

# SEOAuditItem — one per checklist item per submission
# Fields: id, submission_id (FK), category, item_key, is_complete, updated_at

# Task — one per task per submission
# Fields: id, submission_id (FK), title, tag, column (0/1/2), created_at
```

---

## Section 5 — Environment variables (`.env.example`)

```
FLASK_SECRET_KEY=change_me
ADMIN_PASSWORD=change_me

# Google
GOOGLE_SERVICE_ACCOUNT_JSON=credentials/google_service_account.json
GDRIVE_PARENT_FOLDER_ID=your_google_drive_folder_id_here

# Email (SMTP — e.g. Gmail app password or SendGrid)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=hello@jo4dev.co.za
MAIL_PASSWORD=your_app_password_here
MAIL_DEFAULT_SENDER=hello@jo4dev.co.za
ADMIN_EMAIL=admin@jo4dev.co.za

# Site
BASE_URL=https://onboard.jo4dev.co.za
COMPANY_NAME=JO4 Dev
```

---

## Section 6 — requirements.txt

```
flask
flask-sqlalchemy
flask-mail
flask-session
google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib
werkzeug
python-dotenv
weasyprint
pillow
gunicorn
```

---

## Section 6b — Docker setup

The entire application runs in Docker on an Ubuntu VPS. Traffic is routed through a **Cloudflare Tunnel** (no open inbound ports on the VPS — no Nginx needed, no SSL cert management needed). Cloudflare handles HTTPS termination.

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

# System deps for WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance /app/static/uploads

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```

### `docker-compose.yml`

```yaml
version: "3.9"

services:

  web:
    build: .
    container_name: jo4dev_web
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./instance:/app/instance          # SQLite database persisted
      - ./credentials:/app/credentials    # Google service account JSON
      - ./static/uploads:/app/static/uploads  # Uploaded files persisted
    networks:
      - jo4dev_net

  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: jo4dev_tunnel
    restart: unless-stopped
    command: tunnel --no-autoupdate run
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
    networks:
      - jo4dev_net
    depends_on:
      - web

networks:
  jo4dev_net:
    driver: bridge
```

### How Cloudflare Tunnel connects

The `cloudflared` container connects outbound to Cloudflare's edge using the tunnel token. In the Cloudflare dashboard, configure the tunnel ingress rule to forward `https://onboard.jo4dev.co.za` → `http://web:5000` (using the Docker internal service name `web`). No ports need to be opened on the VPS firewall.

### `.env.example` additions

```
# Cloudflare Tunnel
CLOUDFLARE_TUNNEL_TOKEN=your_cloudflare_tunnel_token_here
```

### Docker commands (include in SETUP.md)

```bash
# First run — build and start
docker compose up -d --build

# View logs
docker compose logs -f web

# Restart after code change
docker compose up -d --build web

# Run database migrations inside the container
docker compose exec web flask db upgrade

# Stop everything
docker compose down
```

---

## Section 7 — Style & UX notes

- Use **Bootstrap 5** (CDN) for all UI
- Admin dashboard: dark sidebar, clean white content area, Bootstrap table-striped for submissions
- Public form: clean, professional, mobile-first, JO4 Dev branding (use CSS variables for primary colour — default `#1a1a1a`)
- Multi-step form: sticky progress bar at top, step labels, animated transitions between steps
- All forms: show inline validation errors, not just on submit
- Success page: show client's company name, link to their Google Doc, and "what happens next" timeline
- Logo: placeholder for JO4 Dev logo in the header of the public form — use an `<img src="/static/img/jo4dev_logo.png">` that the developer can replace

---

## Section 8 — Google API setup instructions (include as `SETUP.md`)

Write a `SETUP.md` file with clear step-by-step instructions for:

1. Creating a Google Cloud project
2. Enabling Drive API and Docs API (and Gmail API if using it)
3. Creating a service account and downloading the JSON key
4. Sharing the target Google Drive parent folder with the service account email
5. Setting up SMTP (Gmail app password) for Flask-Mail
6. Populating `.env` from `.env.example`
7. Running database migrations inside Docker: `docker compose exec web flask db upgrade`
8. Running locally for development: `flask run` (outside Docker) or `docker compose up --build`
9. **Deploying to Ubuntu VPS with Docker + Cloudflare Tunnel:**
   - Install Docker and Docker Compose plugin on the Ubuntu VPS
   - Clone the repo onto the VPS
   - Copy `.env.example` to `.env` and fill in all values including `CLOUDFLARE_TUNNEL_TOKEN`
   - Place `google_service_account.json` in the `credentials/` folder
   - Create the Cloudflare Tunnel in the Cloudflare Zero Trust dashboard, copy the tunnel token to `.env`
   - Set the tunnel public hostname to point to `http://web:5000` (internal Docker service name)
   - Run `docker compose up -d --build`
   - No Nginx needed. No open inbound ports needed. Cloudflare handles HTTPS.

---

## What to build first (suggested order for Codex)

1. Project scaffold — folder structure, `app.py`, `config.py`, `models.py`, `requirements.txt`, `.env.example`
2. Public intake form — all 7 steps, client-side validation, file upload preview
3. Form submission API route — save to DB, return success
4. Google Drive integration — create folder, upload files
5. Google Docs integration — create onboarding brief doc
6. Email — client confirmation + admin notification
7. Admin login + dashboard
8. Admin client detail page (overview + notes + status)
9. SEO audit tab (per client, stored in DB)
10. Task tracker tab (Kanban, per client, stored in DB)
11. `SETUP.md` documentation

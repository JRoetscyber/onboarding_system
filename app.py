import requests
import uuid
from datetime import date
from pathlib import Path

from flask import (
    Flask,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from config import Config
from models import SEOAuditItem, Submission, Task, db


mail = Mail()

SEO_PACKAGES = {
    "basic": {
        "name": "Basic baked-in SEO",
        "summary": "For clients who did not buy SEO. This covers the non-negotiable setup every website should still receive.",
        "items": [
            ("Foundation", "basic_page_titles", "Write a clear unique page title for every main page, including the business name where useful"),
            ("Foundation", "basic_meta", "Write a plain-language meta description for every main page so Google has a useful summary"),
            ("Foundation", "basic_headings", "Use one clear H1 per page and logical H2 sections so pages are easy to scan"),
            ("Foundation", "basic_urls", "Use short readable URLs such as /services or /contact instead of unclear page names"),
            ("Foundation", "basic_image_alt", "Add simple alt text to important images, especially logo, service images, and product images"),
            ("Technical", "basic_mobile", "Check the site works cleanly on mobile, tablet, and desktop"),
            ("Technical", "basic_speed", "Compress large images and avoid obvious speed problems before handover"),
            ("Technical", "basic_indexing", "Make sure the live site is not blocked from search engines"),
            ("Technical", "basic_sitemap", "Generate and submit a sitemap link when the site is ready"),
            ("Tracking", "basic_analytics_ready", "Leave the site ready for Google Analytics/Search Console connection if credentials are not available yet"),
        ],
    },
    "standard": {
        "name": "Standard SEO specialist",
        "summary": "For active SEO work with proper keyword mapping, on-page optimisation, local SEO, and tracking setup.",
        "items": [
            ("Discovery", "std_business_goals", "Confirm the client's top 3 business outcomes for SEO: calls, forms, bookings, sales, or foot traffic"),
            ("Discovery", "std_seed_keywords", "Build a seed keyword list from the client's services, locations, and customer language"),
            ("Discovery", "std_competitor_serp", "Check the top-ranking competitors for the client's main services and location"),
            ("Discovery", "std_keyword_map", "Map one primary keyword and supporting phrases to each important page"),
            ("Technical", "std_crawl", "Run a crawl and fix broken links, missing titles, missing descriptions, and duplicate headings"),
            ("Technical", "std_indexing", "Confirm indexability, canonical tags, sitemap, robots.txt, and redirect behaviour"),
            ("Technical", "std_core_web_vitals", "Review Core Web Vitals and record the main performance fixes needed"),
            ("Technical", "std_schema", "Add organisation, local business, service, product, FAQ, or article schema where relevant"),
            ("On-page", "std_titles", "Optimise page titles for search intent without making them spammy"),
            ("On-page", "std_descriptions", "Optimise meta descriptions with a useful benefit and call to action"),
            ("On-page", "std_headings", "Rewrite headings so each page has a clear topic flow and service focus"),
            ("On-page", "std_body_copy", "Improve page copy so it answers what the service is, who it is for, benefits, process, pricing cues, and next step"),
            ("On-page", "std_internal_links", "Add internal links from related pages using natural anchor text"),
            ("On-page", "std_images", "Rename key image files and add descriptive alt text"),
            ("Local", "std_gbp", "Review Google Business Profile status, categories, services, description, photos, and contact details"),
            ("Local", "std_nap", "Check name, address, and phone consistency across the website and key listings"),
            ("Local", "std_location_pages", "Create or improve location-specific content if the business serves defined areas"),
            ("Content", "std_content_gaps", "List content gaps competitors cover that the client's site does not"),
            ("Content", "std_blog_plan", "Create a practical 90-day content plan with topics and target phrases"),
            ("Authority", "std_backlinks", "Review backlink profile and flag toxic, irrelevant, or strong links"),
            ("Authority", "std_citations", "Identify citation and directory opportunities relevant to South Africa and the client's industry"),
            ("Tracking", "std_ga4", "Set up or verify GA4 with key events"),
            ("Tracking", "std_gsc", "Set up or verify Google Search Console and submit sitemap"),
            ("Tracking", "std_report", "Create the first baseline SEO report with rankings, traffic, conversions, and next actions"),
        ],
    },
    "aggressive": {
        "name": "Aggressive hard-core SEO",
        "summary": "For serious SEO campaigns where rankings, content, authority, technical cleanup, and reporting are pushed hard.",
        "items": [
            ("Strategy", "agr_goal_model", "Define SEO revenue model: target services, estimated lead value, conversion points, and reporting targets"),
            ("Strategy", "agr_market_map", "Map priority service areas, buyer types, and commercial pages needed to compete"),
            ("Strategy", "agr_serp_intent", "Analyse search intent for each priority keyword: service page, local page, guide, comparison, or product page"),
            ("Strategy", "agr_keyword_clusters", "Build keyword clusters with primary, secondary, long-tail, and question-based phrases"),
            ("Strategy", "agr_priority_matrix", "Prioritise SEO work by impact, difficulty, and commercial value"),
            ("Technical", "agr_full_crawl", "Run a full crawl and document every issue by severity: critical, high, medium, low"),
            ("Technical", "agr_logs", "Review crawl behaviour or server logs if available to identify wasted crawl budget"),
            ("Technical", "agr_rendering", "Check JavaScript rendering, lazy-loaded content, and whether Google can see important content"),
            ("Technical", "agr_architecture", "Review site architecture and reduce unnecessary depth for money pages"),
            ("Technical", "agr_redirect_map", "Audit redirects, chains, loops, 404s, soft 404s, and legacy URLs"),
            ("Technical", "agr_canonicals", "Audit canonicals across all indexable page types"),
            ("Technical", "agr_schema_advanced", "Add and validate advanced schema for services, FAQs, products, reviews, breadcrumbs, organisation, and local business"),
            ("Technical", "agr_cwv_fix_plan", "Create a Core Web Vitals fix plan with exact assets, templates, or scripts causing issues"),
            ("Technical", "agr_image_pipeline", "Compress, resize, lazy-load, and convert major images where appropriate"),
            ("Technical", "agr_security", "Check HTTPS, mixed content, security headers, and redirect consistency"),
            ("On-page", "agr_title_testing", "Write improved title options for priority pages and track changes"),
            ("On-page", "agr_meta_testing", "Write stronger meta descriptions focused on click-through and intent"),
            ("On-page", "agr_entity_terms", "Add related entities, service terms, locations, and proof points naturally into copy"),
            ("On-page", "agr_money_pages", "Rebuild priority service pages with benefits, process, FAQs, proof, pricing cues, and conversion sections"),
            ("On-page", "agr_conversion_copy", "Improve calls to action and trust signals on SEO landing pages"),
            ("On-page", "agr_internal_link_graph", "Build an internal linking plan from supporting content to money pages"),
            ("On-page", "agr_anchor_text", "Audit internal anchor text for relevance and over-optimisation"),
            ("Content", "agr_content_audit", "Audit all existing content and mark each page: keep, improve, merge, redirect, or remove"),
            ("Content", "agr_gap_analysis", "Compare competitor content depth and identify missing pages, sections, FAQs, and proof points"),
            ("Content", "agr_calendar", "Create a 12-week content calendar with owner, due date, target keyword, and page type"),
            ("Content", "agr_briefs", "Write detailed content briefs for the first batch of priority pages or articles"),
            ("Content", "agr_eeat", "Add experience, expertise, author, business proof, case studies, and trust signals where relevant"),
            ("Local", "agr_gbp_optimise", "Optimise Google Business Profile categories, services, description, photos, products, posts, and Q&A"),
            ("Local", "agr_review_plan", "Create a review generation plan with timing, message template, and follow-up process"),
            ("Local", "agr_local_pages", "Build a location-page plan with unique local proof and service relevance"),
            ("Local", "agr_citation_cleanup", "Audit and clean citations for NAP consistency across major listings"),
            ("Authority", "agr_link_profile", "Deep review backlink profile by authority, relevance, anchor text, link type, and risk"),
            ("Authority", "agr_competitor_links", "Pull competitor backlink opportunities and sort by realistic outreach value"),
            ("Authority", "agr_outreach_targets", "Create outreach target list for directories, partners, suppliers, associations, and local media"),
            ("Authority", "agr_digital_pr", "Plan one linkable asset or PR angle that can earn relevant links"),
            ("Authority", "agr_disavow_review", "Flag suspicious link patterns for review before any disavow decision"),
            ("Tracking", "agr_ga4_events", "Set up GA4 events for forms, calls, WhatsApp clicks, bookings, purchases, and key buttons"),
            ("Tracking", "agr_gsc_segments", "Segment Search Console tracking by page type, query group, and priority pages"),
            ("Tracking", "agr_rank_tracking", "Set up rank tracking for priority keywords and locations"),
            ("Tracking", "agr_dashboard", "Create an SEO dashboard showing traffic, rankings, conversions, technical health, and completed actions"),
            ("Reporting", "agr_baseline", "Create a baseline report before major changes are made"),
            ("Reporting", "agr_weekly_actions", "Set weekly SEO action list with completed work, blockers, next tasks, and ranking movement"),
            ("Reporting", "agr_monthly_review", "Prepare monthly review: results, what changed, what worked, what is next, and recommended budget focus"),
            ("Reporting", "agr_experiment_log", "Maintain an experiment/change log so ranking and traffic changes can be connected to actions"),
        ],
    },
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path("instance").mkdir(exist_ok=True)
    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_schema()

    return app


def ensure_schema():
    columns = {
        "submission": {
            "priority": "VARCHAR(40) DEFAULT 'normal'",
            "deal_value": "VARCHAR(80)",
            "next_follow_up": "VARCHAR(10)",
            "last_contacted": "VARCHAR(10)",
            "seo_package": "VARCHAR(40) DEFAULT 'basic'",
            "agile_methodology": "VARCHAR(40) DEFAULT 'scrum'",
            "sprint_name": "VARCHAR(120)",
            "sprint_goal": "TEXT",
            "sprint_start": "VARCHAR(10)",
            "sprint_end": "VARCHAR(10)",
            "project_owner": "VARCHAR(140)",
            "sprint_cadence": "VARCHAR(80) DEFAULT 'weekly'",
        },
        "seo_audit_item": {
            "package": "VARCHAR(40) DEFAULT 'basic'",
        },
        "task": {
            "description": "TEXT",
            "priority": "VARCHAR(40) DEFAULT 'normal'",
            "agile_type": "VARCHAR(40) DEFAULT 'task'",
            "sprint": "VARCHAR(120)",
            "estimate_hours": "VARCHAR(20)",
            "acceptance_criteria": "TEXT",
            "blocker": "TEXT",
            "due_date": "VARCHAR(10)",
            "reminder_date": "VARCHAR(10)",
            "reminder_note": "VARCHAR(220)",
        },
    }
    with db.engine.connect() as conn:
        for table, additions in columns.items():
            existing = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")}
            for column, sql_type in additions.items():
                if column not in existing:
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
        conn.commit()


app = create_app()


def selected_values(name):
    raw = request.form.getlist(name)
    if len(raw) == 1 and "," in raw[0]:
        return [value.strip() for value in raw[0].split(",") if value.strip()]
    return [value for value in raw if value]


def save_upload(field_name, multiple=False):
    files = request.files.getlist(field_name) if multiple else [request.files.get(field_name)]
    saved = []
    for file_storage in files:
        if not file_storage or not file_storage.filename:
            continue
        filename = f"{uuid.uuid4().hex}_{secure_filename(file_storage.filename)}"
        path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
        file_storage.save(path)
        saved.append({"filename": filename, "path": str(path)})
    return saved


def send_to_n8n(submission):
    webhook_url = current_app.config.get("N8N_WEBHOOK_URL")
    if not webhook_url:
        current_app.logger.error("N8N_WEBHOOK_URL is not configured.")
        return

    # Prepare data payload (submission details)
    data = {
        "submission_id": submission.submission_id,
        "company_name": submission.company_name,
        "industry": submission.industry,
        "contact_name": submission.contact_name,
        "job_title": submission.job_title,
        "contact_email": submission.contact_email,
        "phone": submission.phone,
        "address": submission.address,
        "existing_url": submission.existing_url,
        "referral_source": submission.referral_source,
        "services": submission.services,
        "main_goal": submission.main_goal,
        "target_audience": submission.target_audience,
        "competitors": submission.competitors,
        "likes_competitors": submission.likes_competitors,
        "dislikes_competitors": submission.dislikes_competitors,
        "has_content": submission.has_content,
        "page_count": submission.page_count,
        "pages_needed": submission.pages_needed,
        "needs_blog": submission.needs_blog,
        "sells_online": submission.sells_online,
        "product_count": submission.product_count,
        "languages": submission.languages,
        "multilingual": submission.multilingual,
        "seo_history": submission.seo_history,
        "paid_ads": submission.paid_ads,
        "target_keywords": submission.target_keywords,
        "google_business": submission.google_business,
        "analytics_setup": submission.analytics_setup,
        "social_platforms": submission.social_platforms,
        "launch_date": submission.launch_date,
        "deadline_urgency": submission.deadline_urgency,
        "budget": submission.budget,
        "payment_preference": submission.payment_preference,
        "maintenance_budget": submission.maintenance_budget,
        "involvement_level": submission.involvement_level,
        "main_contact_name": submission.main_contact_name,
        "main_contact_email": submission.main_contact_email,
        "integrations": submission.integrations,
        "other_notes": submission.other_notes,
        "digital_presence_rating": submission.digital_presence_rating,
        "primary_colour": submission.primary_colour,
        "secondary_colour": submission.secondary_colour,
        "font_preferences": submission.font_preferences,
        "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
        "status": submission.status,
    }

    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        response.raise_for_status()
        current_app.logger.info(f"Successfully sent submission {submission.submission_id} to n8n webhook.")
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to send submission {submission.submission_id} to n8n webhook: {e}")


def brief_text(submission):
    return (
        f"{submission.company_name} - Onboarding Brief\n\n"
        f"Contact: {submission.contact_name} ({submission.contact_email})\n"
        f"Industry: {submission.industry}\n"
        f"Services: {', '.join(submission.services or [])}\n"
        f"Main goal: {submission.main_goal}\n\n"
        f"Target audience:\n{submission.target_audience or ''}\n\n"
        f"Competitors:\n{submission.competitors or ''}\n\n"
        f"Budget: {submission.budget}\n"
        f"Timeline: {submission.launch_date or 'Not specified'} ({submission.deadline_urgency or 'No urgency set'})\n\n"
        f"Technical requirements:\n{submission.integrations or ''}\n\n"
        f"Additional notes:\n{submission.other_notes or ''}\n"
    )


def send_emails(submission):
    if not current_app.config["MAIL_USERNAME"] or not current_app.config["MAIL_PASSWORD"]:
        return
    first_name = submission.contact_name.split()[0]
    client_html = render_template("email/client_confirmation.html", submission=submission, first_name=first_name)
    admin_html = render_template("email/admin_notification.html", submission=submission)
    mail.send(Message(
        subject=f"Welcome to JO4 Dev, {first_name}! Your onboarding is complete.",
        recipients=[submission.contact_email],
        html=client_html,
    ))
    mail.send(Message(
        subject=f"New onboarding submission: {submission.company_name}",
        recipients=[current_app.config["ADMIN_EMAIL"]],
        html=admin_html,
    ))


def require_admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login", next=request.path))
    return None


def ensure_audit_items(submission):
    package = submission.seo_package or "basic"
    existing = {item.item_key for item in submission.seo_items if item.package == package}
    for category, key, label in SEO_PACKAGES[package]["items"]:
        if key not in existing:
            db.session.add(SEOAuditItem(
                submission=submission,
                category=category,
                item_key=key,
                label=label,
                package=package,
            ))
    db.session.commit()


def visible_audit_items(submission):
    package = submission.seo_package or "basic"
    return [item for item in submission.seo_items if item.package == package]


@app.get("/")
def index():
    return redirect(url_for("onboard"))


@app.get("/onboard")
def onboard():
    return render_template("onboard.html")


@app.get("/terms")
def terms():
    return render_template("terms.html")


@app.post("/api/onboard/submit")
def submit_onboarding():
    missing = [f for f in ["company_name", "contact_name", "contact_email", "main_goal", "terms"] if not request.form.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

    submission = Submission(
        submission_id=str(uuid.uuid4()),
        company_name=request.form["company_name"],
        industry=request.form.get("industry"),
        contact_name=request.form["contact_name"],
        job_title=request.form.get("job_title"),
        contact_email=request.form["contact_email"],
        phone=request.form.get("phone"),
        address=request.form.get("address"),
        existing_url=request.form.get("existing_url"),
        referral_source=request.form.get("referral_source"),
        services=selected_values("services"),
        main_goal=request.form.get("main_goal"),
        target_audience=request.form.get("target_audience"),
        competitors=request.form.get("competitors"),
        likes_competitors=request.form.get("likes_competitors"),
        dislikes_competitors=request.form.get("dislikes_competitors"),
        has_content=request.form.get("has_content"),
        page_count=request.form.get("page_count"),
        pages_needed=selected_values("pages_needed"),
        needs_blog=request.form.get("needs_blog"),
        sells_online=request.form.get("sells_online"),
        product_count=request.form.get("product_count") or None,
        languages=selected_values("languages"),
        multilingual=request.form.get("multilingual"),
        seo_history=request.form.get("seo_history"),
        paid_ads=request.form.get("paid_ads"),
        target_keywords=request.form.get("target_keywords"),
        google_business=request.form.get("google_business"),
        analytics_setup=request.form.get("analytics_setup"),
        social_platforms=selected_values("social_platforms"),
        launch_date=request.form.get("launch_date"),
        deadline_urgency=request.form.get("deadline_urgency"),
        budget=request.form.get("budget"),
        payment_preference=request.form.get("payment_preference"),
        maintenance_budget=request.form.get("maintenance_budget"),
        involvement_level=request.form.get("involvement_level"),
        main_contact_name=request.form.get("main_contact_name") or request.form["contact_name"],
        main_contact_email=request.form.get("main_contact_email") or request.form["contact_email"],
        integrations=request.form.get("integrations"),
        other_notes=request.form.get("other_notes"),
        digital_presence_rating=request.form.get("digital_presence_rating") or None,
        primary_colour=request.form.get("primary_colour"),
        secondary_colour=request.form.get("secondary_colour"),
        font_preferences=request.form.get("font_preferences"),
    )
    db.session.add(submission)
    db.session.commit()

    try:
        send_to_n8n(submission)
        send_emails(submission)
        db.session.commit()
    except Exception as exc:
        current_app.logger.exception("Post-submit integration failed: %s", exc)

    return jsonify({"success": True, "submission_id": submission.submission_id})


@app.get("/success/<submission_id>")
def success(submission_id):
    submission = Submission.query.filter_by(submission_id=submission_id).first_or_404()
    return render_template("success.html", submission=submission)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == current_app.config["ADMIN_PASSWORD"]:
            session["admin_logged_in"] = True
            next_page = request.args.get("next", "")
            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("admin_dashboard"))
        flash("Invalid password", "danger")
    return render_template("admin/login.html")


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@app.get("/admin/dashboard")
def admin_dashboard():
    gate = require_admin()
    if gate:
        return gate
    query = Submission.query
    status = request.args.get("status")
    service = request.args.get("service")
    if status:
        query = query.filter_by(status=status)
    if service:
        query = query.filter(Submission.services.contains([service]))
    submissions = query.order_by(Submission.submitted_at.desc()).all()
    today = date.today().isoformat()
    open_tasks = Task.query.filter(Task.column < 2).all()
    due_today = [task for task in open_tasks if task.due_date == today]
    overdue = [task for task in open_tasks if task.due_date and task.due_date < today]
    reminders = [
        task for task in open_tasks
        if task.reminder_date and task.reminder_date <= today
    ]
    stats = {
        "total": Submission.query.count(),
        "new": Submission.query.filter_by(status="new").count(),
        "in_progress": Submission.query.filter(Submission.status.in_(["reviewed", "proposal_sent", "active"])).count(),
        "completed": Submission.query.filter_by(status="completed").count(),
        "due_today": len(due_today),
        "overdue": len(overdue),
        "reminders": len(reminders),
        "hot": Submission.query.filter_by(priority="high").count(),
    }
    return render_template(
        "admin/dashboard.html",
        submissions=submissions,
        stats=stats,
        due_today=due_today,
        overdue=overdue,
        reminders=reminders,
    )


@app.route("/admin/client/<submission_id>", methods=["GET", "POST"])
def admin_client(submission_id):
    gate = require_admin()
    if gate:
        return gate
    submission = Submission.query.filter_by(submission_id=submission_id).first_or_404()
    if not submission.seo_package:
        submission.seo_package = "basic"
        db.session.commit()
    if request.method == "POST":
        submission.status = request.form.get("status", submission.status)
        submission.priority = request.form.get("priority", submission.priority)
        submission.deal_value = request.form.get("deal_value")
        submission.next_follow_up = request.form.get("next_follow_up")
        submission.last_contacted = request.form.get("last_contacted")
        submission.project_owner = request.form.get("project_owner")
        submission.admin_notes = request.form.get("admin_notes")
        db.session.commit()
        flash("Client updated", "success")
        return redirect(url_for("admin_client", submission_id=submission_id))
    ensure_audit_items(submission)
    return render_template("admin/client.html", submission=submission)


@app.route("/admin/client/<submission_id>/seo", methods=["GET", "POST"])
def admin_seo(submission_id):
    gate = require_admin()
    if gate:
        return gate
    submission = Submission.query.filter_by(submission_id=submission_id).first_or_404()
    if not submission.seo_package:
        submission.seo_package = "basic"
        db.session.commit()
    if request.method == "POST":
        submission.seo_package = request.form.get("seo_package", submission.seo_package or "basic")
        ensure_audit_items(submission)
        complete_ids = {int(value) for value in request.form.getlist("complete")}
        for item in visible_audit_items(submission):
            item.is_complete = item.id in complete_ids
        db.session.commit()
        flash("SEO audit updated", "success")
        return redirect(url_for("admin_seo", submission_id=submission_id))
    ensure_audit_items(submission)
    audit_items = visible_audit_items(submission)
    total = len(audit_items)
    done = sum(1 for item in audit_items if item.is_complete)
    progress = round((done / total) * 100) if total else 0
    return render_template(
        "admin/seo_audit.html",
        submission=submission,
        progress=progress,
        audit_items=audit_items,
        seo_packages=SEO_PACKAGES,
    )


@app.route("/admin/client/<submission_id>/tasks", methods=["GET", "POST"])
def admin_tasks(submission_id):
    gate = require_admin()
    if gate:
        return gate
    submission = Submission.query.filter_by(submission_id=submission_id).first_or_404()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if title:
            db.session.add(Task(
                submission=submission,
                title=title,
                description=request.form.get("description"),
                tag=request.form.get("tag", "Dev"),
                agile_type=request.form.get("agile_type", "task"),
                sprint=request.form.get("sprint"),
                estimate_hours=request.form.get("estimate_hours"),
                acceptance_criteria=request.form.get("acceptance_criteria"),
                blocker=request.form.get("blocker"),
                priority=request.form.get("priority", "normal"),
                due_date=request.form.get("due_date"),
                reminder_date=request.form.get("reminder_date"),
                reminder_note=request.form.get("reminder_note"),
            ))
            db.session.commit()
        return redirect(url_for("admin_tasks", submission_id=submission_id))
    return render_template("admin/tasks.html", submission=submission)


@app.route("/admin/client/<submission_id>/agile", methods=["GET", "POST"])
def admin_agile(submission_id):
    gate = require_admin()
    if gate:
        return gate
    submission = Submission.query.filter_by(submission_id=submission_id).first_or_404()
    if request.method == "POST":
        submission.agile_methodology = request.form.get("agile_methodology", "scrum")
        submission.sprint_name = request.form.get("sprint_name")
        submission.sprint_goal = request.form.get("sprint_goal")
        submission.sprint_start = request.form.get("sprint_start")
        submission.sprint_end = request.form.get("sprint_end")
        submission.project_owner = request.form.get("project_owner")
        submission.sprint_cadence = request.form.get("sprint_cadence")
        db.session.commit()
        flash("Agile project settings updated", "success")
        return redirect(url_for("admin_agile", submission_id=submission_id))

    backlog = [task for task in submission.tasks if task.column == 0]
    active = [task for task in submission.tasks if task.column == 1]
    done = [task for task in submission.tasks if task.column == 2]
    blocked = [task for task in submission.tasks if task.blocker]
    return render_template(
        "admin/agile.html",
        submission=submission,
        backlog=backlog,
        active=active,
        done=done,
        blocked=blocked,
    )


@app.post("/admin/task/<int:task_id>/update")
def update_task(task_id):
    gate = require_admin()
    if gate:
        abort(403)
    task = Task.query.get_or_404(task_id)
    payload = request.get_json(force=True)
    task.column = int(payload.get("column", task.column))
    db.session.commit()
    return jsonify({"success": True})


@app.post("/admin/client/<submission_id>/delete")
def delete_client(submission_id):
    gate = require_admin()
    if gate:
        abort(403)
    submission = Submission.query.filter_by(submission_id=submission_id).first_or_404()
    company_name = submission.company_name
    db.session.delete(submission)
    db.session.commit()
    flash(f"{company_name} has been deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/task/<int:task_id>/delete")
def delete_task(task_id):
    gate = require_admin()
    if gate:
        abort(403)
    task = Task.query.get_or_404(task_id)
    submission_id = task.submission.submission_id
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("admin_tasks", submission_id=submission_id))


if __name__ == "__main__":
    app.run(debug=False)

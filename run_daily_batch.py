#!/usr/bin/env python3
"""Daily email batch - writes to log file for tracking."""
import json, os, sys, time, random, smtplib, ssl
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, "data")
LOG_FILE = os.path.join(DIR, "email_batch.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Load configs
config = load_json(os.path.join(DATA_DIR, "email_config.json"))
templates = load_json(os.path.join(DATA_DIR, "templates.json"))
leads_data = load_json(os.path.join(DATA_DIR, "leads.json"))

daily_limit = config.get("daily_limit", 8)
min_delay = config.get("min_delay_seconds", 180)
max_delay = config.get("max_delay_seconds", 300)
log(f"Daily limit: {daily_limit}, delays: {min_delay}-{max_delay}s")

# Find pending leads
seen_emails = set()
antoniopaving_candidates = []
primeproperty_candidates = []

for batch_key in sorted(leads_data.get("leads_by_date", {}).keys()):
    for lead in leads_data["leads_by_date"][batch_key]:
        email = lead.get("email", "")
        company = lead.get("company", "")
        if "contacted" in lead:
            continue
        if lead.get("verified") != "verified":
            continue
        if company.startswith("Test"):
            continue
        if not email.strip():
            continue
        if email in seen_emails:
            continue
        seen_emails.add(email)

        biz_target = lead.get("business_target", "")
        if not biz_target:
            biz_target = "antoniopaving" if lead.get("type") in ("builder", "constructora") else "primeproperty"

        entry = {
            "email": email,
            "company": company,
            "batch_key": batch_key,
            "contact": lead.get("contact", ""),
            "title": lead.get("title", ""),
        }
        if biz_target == "antoniopaving":
            antoniopaving_candidates.append(entry)
        else:
            primeproperty_candidates.append(entry)

# Split evenly, up to daily_limit
half = daily_limit // 2
selected = antoniopaving_candidates[:half] + primeproperty_candidates[:half]
remaining = daily_limit - len(selected)
if remaining > 0:
    extra = antoniopaving_candidates[half:half+remaining] + primeproperty_candidates[half:half+remaining]
    selected.extend(extra[:remaining])

log(f"Found {len(antoniopaving_candidates)} antipaving + {len(primeproperty_candidates)} primeproperty pending leads")
log(f"Sending {len(selected)} emails this batch")

for c in selected:
    log(f"  - {c['company']:30s} {c['email']:35s}")

if not selected:
    log("No emails to send. Exiting.")
    sys.exit(0)

# SMTP connection
log("Connecting to SMTP...")
ctx = ssl.create_default_context()
server = smtplib.SMTP(config["smtp_server"], config["smtp_port"], timeout=30)
server.ehlo()
server.starttls(context=ctx)
server.ehlo()
password = config.get("gmail_app_password") or config.get("password", "")
server.login(config["sender_email"], password)
log(f"SMTP connected as {config['sender_email']}")

# Get template by business id
def get_template(biz_id):
    for tmpl in templates.get("templates", []):
        if tmpl.get("business") == biz_id or tmpl.get("id") == biz_id:
            return tmpl
    return templates["templates"][0] if templates.get("templates") else None

def get_biz_addr(biz_id):
    return config.get("business_addresses", {}).get(biz_id, {})

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sent_count = 0
error_count = 0

# Determine who gets what
# First 4 (half) are antoniopaving, next 4 are primeproperty
for i, candidate in enumerate(selected):
    # Determine business target for this candidate based on which half it came from
    if i < half:
        biz_id = "antoniopaving"
    else:
        biz_id = "primeproperty"

    tmpl = get_template(biz_id)
    biz_addr = get_biz_addr(biz_id)

    from_name = biz_addr.get("from_name", config["sender_name"])
    from_email = biz_addr.get("from_email", config["sender_email"])
    to_email = candidate["email"]
    company = candidate["company"]

    body_text = tmpl["body"].replace("[COMPANY]", company)
    subject = tmpl.get("subject", "Collaboration opportunity")

    # Build email
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    html = f"<html><body style=\"font-family:Arial,sans-serif;line-height:1.6;color:#333;\"><p>{body_text.replace(chr(10), '<br>')}</p></body></html>"
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        server.sendmail(from_email, to_email, msg.as_string())
        log(f"✅ SENT [{biz_id:15s}] -> {to_email:35s} ({company})")
        sent_count += 1
    except Exception as e:
        log(f"❌ ERROR [{biz_id:15s}] -> {to_email:35s}: {e}")
        error_count += 1

    # Mark contacted in leads.json
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    found_in = None
    for bk in leads_data.get("leads_by_date", {}):
        for lead in leads_data["leads_by_date"][bk]:
            if lead.get("email") == to_email:
                lead["contacted"] = now
                lead["contact_status"] = "sent" if error_count == error_count or True else "error"
                lead["sent"] = True
                save_json(os.path.join(DATA_DIR, "leads.json"), leads_data)
                break
        if found_in:
            break

    # Delay (except last)
    if i < len(selected) - 1:
        delay = random.randint(min_delay, max_delay)
        log(f"⏳ Waiting {delay}s before next...")
        time.sleep(delay)

server.quit()
log(f"📊 DONE: {sent_count} sent, {error_count} errors")

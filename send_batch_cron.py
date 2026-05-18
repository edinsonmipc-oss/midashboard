#!/usr/bin/env python3
"""
Daily email batch sender — cron mode.
Sends up to 8 emails split between antoniopaving and primeproperty.
"""
import json, os, sys, time, random, smtplib, ssl, subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "email_config.json")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_qualifying_leads(leads_data, count=8):
    """Find leads not contacted, verified, not Test co, not empty email."""
    antoniopaving = []
    primeproperty = []
    
    for batch_key in sorted(leads_data.get("leads_by_date", {}).keys()):
        for lead in leads_data["leads_by_date"][batch_key]:
            # Skip if already contacted
            if "contacted" in lead and lead["contacted"]:
                continue
            # Skip unverified
            if lead.get("verified") != "verified":
                continue
            # Skip Test companies
            if lead.get("company", "").startswith("Test"):
                continue
            # Skip empty email
            if not lead.get("email", "").strip():
                continue
            
            biz = lead.get("business_target", "")
            if not biz:
                biz = "antoniopaving" if lead.get("type") in ("builder", "constructora") else "primeproperty"
            
            entry = {
                "email": lead["email"],
                "company": lead["company"],
                "business_target": biz,
                "batch_key": batch_key,
            }
            if biz == "antoniopaving":
                antoniopaving.append(entry)
            else:
                primeproperty.append(entry)
    
    # Split evenly
    half = count // 2
    selected = antoniopaving[:half] + primeproperty[:half]
    # If we have room for more, add from whichever has more
    remaining = count - len(selected)
    if remaining > 0:
        extra = antoniopaving[half: half + remaining] + primeproperty[half: half + remaining]
        selected += extra[:remaining]
    
    return selected[:count]

def get_template(templates_data, biz_id):
    for tmpl in templates_data.get("templates", []):
        if tmpl.get("business") == biz_id or tmpl.get("id") == biz_id:
            return tmpl
    return templates_data["templates"][0] if templates_data.get("templates") else None

def render_body(template_body, company):
    return template_body.replace("[COMPANY]", company)

def create_smtp_connection(config):
    ctx = ssl.create_default_context()
    server = smtplib.SMTP(config["smtp_server"], config["smtp_port"], timeout=30)
    server.ehlo()
    if config.get("use_tls", True):
        server.starttls(context=ctx)
        server.ehlo()
    password = config.get("gmail_app_password") or config.get("password", "")
    server.login(config["sender_email"], password)
    log(f"SMTP login OK as {config['sender_email']}")
    return server

def send_email(server, config, to_email, subject, body_text, from_name, from_email):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    # Simple HTML version
    html = f"<html><body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\"><p>{body_text.replace(chr(10), '<br>')}</p></body></html>"
    msg.attach(MIMEText(html, "html", "utf-8"))
    server.sendmail(from_email, to_email, msg.as_string())
    return True

def mark_contacted(email, status="sent"):
    data = load_json(LEADS_FILE)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    for batch_key in data.get("leads_by_date", {}):
        for lead in data["leads_by_date"][batch_key]:
            if lead.get("email") == email:
                lead["contacted"] = now
                lead["contact_status"] = status
                lead["sent"] = (status == "sent")
                save_json(LEADS_FILE, data)
                return True
    return False

def main():
    config = load_json(CONFIG_FILE)
    templates = load_json(TEMPLATES_FILE)
    leads_data = load_json(LEADS_FILE)
    
    daily_limit = config.get("daily_limit", 8)
    min_delay = config.get("min_delay_seconds", 180)
    max_delay = config.get("max_delay_seconds", 300)
    
    log(f"Daily limit: {daily_limit}, delay range: {min_delay}-{max_delay}s")
    
    candidates = get_qualifying_leads(leads_data, daily_limit)
    
    if not candidates:
        log("No qualifying leads found to send.")
        return 0
    
    log(f"Found {len(candidates)} qualifying leads:")
    for c in candidates:
        log(f"  - {c['company']:30s} {c['email']:35s} [{c['business_target']}]")
    
    # Connect SMTP
    server = create_smtp_connection(config)
    
    sent = 0
    errors = 0
    
    for i, candidate in enumerate(candidates):
        biz_id = candidate["business_target"]
        tmpl = get_template(templates, biz_id)
        if not tmpl:
            log(f"No template for {biz_id} — skipping {candidate['company']}")
            continue
        
        biz_addr = config.get("business_addresses", {}).get(biz_id, {})
        from_name = biz_addr.get("from_name", config["sender_name"])
        from_email = biz_addr.get("from_email", config["sender_email"])
        
        body_text = render_body(tmpl["body"], candidate["company"])
        subject = tmpl.get("subject", "Colaboración en servicios")
        
        try:
            send_email(server, config, candidate["email"], subject, body_text, from_name, from_email)
            mark_contacted(candidate["email"], "sent")
            log(f"✅ SENT  [{biz_id:15s}] → {candidate['email']:35s} ({candidate['company']})")
            sent += 1
        except Exception as e:
            log(f"❌ ERROR [{biz_id:15s}] → {candidate['email']:35s}: {e}")
            mark_contacted(candidate["email"], f"error: {str(e)[:50]}")
            errors += 1
        
        # Delay between sends
        if i < len(candidates) - 1:
            delay = random.randint(min_delay, max_delay)
            log(f"⏳ Waiting {delay}s before next send...")
            time.sleep(delay)
    
    try:
        server.quit()
    except:
        pass
    
    log(f"📊 BATCH DONE: {sent} sent, {errors} errors, {len(candidates)} attempted")
    return sent

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result is not None else 1)

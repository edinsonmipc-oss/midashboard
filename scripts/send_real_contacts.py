#!/usr/bin/env python3
"""send_real_contacts.py — Envia emails personalizados a contactos reales.
Usa SOLO texto plano, SIN emojis, SIN HTML, template probado libre de spam."""
import json, smtplib, ssl, time, random, os
from datetime import datetime
from email.mime.text import MIMEText

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADS_FILE = os.path.join(DIR, "data", "leads.json")
LOG_FILE = os.path.join(DIR, "data", "send_real.log")

SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "email": "antonioprimemaintenance@gmail.com",
    "password": "pvir coud cwng udvs",
    "from_name": "Antonio Paving",
    "from_email": "antonioprimemaintenance@gmail.com",
}

# Templates de texto plano — probados sin spam triggers
TEMPLATES = {
    "builder": {
        "subject": "Paving subcontractor capacity — Melbourne South-East",
        "body": """Hi {first_name},

This is Antonio from PrimeScape Construction in Notting Hill.

We are a paving subcontractor working across Melbourne's south-east with capacity for new projects this quarter. We handle brick, bluestone, porcelain, and permeable paving for residential and commercial sites.

I noticed {company} works on projects in our area. Would you be open to a brief conversation about your upcoming subcontractor needs?

Cheers,
Antonio Paving
PrimeScape Construction
0412 345 678
10 Elwood St, Notting Hill VIC 3168""",
    },
}

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def send_email(to_email, subject, body_text):
    """Send a plain-text email via Gmail SMTP."""
    msg = MIMEText(body_text, "plain", "utf-8")
    msg["From"] = f"{SMTP_CONFIG['from_name']} <{SMTP_CONFIG['from_email']}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["List-Unsubscribe"] = "<mailto:antonioprimemaintenance+unsubscribe@gmail.com>"

    ctx = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"], timeout=30)
    server.ehlo()
    server.starttls(context=ctx)
    server.ehlo()
    server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
    server.sendmail(SMTP_CONFIG["from_email"], to_email, msg.as_string())
    server.quit()
    return True

def get_first_name(contact_name):
    """Extract first name from full name."""
    if not contact_name:
        return "there"
    return contact_name.split()[0]

def main():
    print("=" * 60)
    print("SENDING TO REAL CONTACTS - ANTONIO PAVING OUTREACH")
    print("=" * 60)

    with open(LEADS_FILE) as f:
        data = json.load(f)

    # Collect all uncontacted leads
    uncontacted = []
    for batch_key in sorted(data.get("leads_by_date", {}).keys()):
        for lead in data["leads_by_date"][batch_key]:
            email = lead.get("email", "").strip()
            if not email:
                continue
            if lead.get("sent") is True or lead.get("contact_status") == "sent":
                continue
            if lead.get("verified") == "invalid":
                continue

            first_name = get_first_name(lead.get("contact", ""))
            company = lead.get("company", "")
            lead_type = lead.get("type", "")
            notes = lead.get("notes", "")

            template_key = "builder" if lead_type in ("builder", "constructora", "strata") else "builder"
            tmpl = TEMPLATES.get(template_key, TEMPLATES["builder"])

            # Personalizar
            subject = tmpl["subject"]
            body = tmpl["body"].format(first_name=first_name, company=company)

            uncontacted.append({
                "email": email,
                "company": company,
                "contact": lead.get("contact", ""),
                "title": lead.get("title", ""),
                "subject": subject,
                "body": body,
                "batch_key": batch_key,
            })

    # Shuffle for randomization
    random.shuffle(uncontacted)

    print(f"\nTotal uncontacted real contacts: {len(uncontacted)}")
    print()

    if len(uncontacted) == 0:
        print("No uncontacted leads. All sent already!")
        return

    # Ask user to confirm first batch
    batch = uncontacted[:8]  # Send max 8 per run
    print(f"Sending {len(batch)} emails now...")
    print()

    sent_count = 0
    fail_count = 0

    for i, contact in enumerate(batch):
        print(f"[{i+1}/{len(batch)}] Sending to {contact['contact']} ({contact['email']})...")
        print(f"    Subject: {contact['subject']}")
        print(f"    Company: {contact['company']}")
        print()

        try:
            send_email(contact["email"], contact["subject"], contact["body"])
            log(f"SENT | {contact['email']} | {contact['contact']} | {contact['company']}")

            # Mark as sent in leads.json
            for batch_key in data.get("leads_by_date", {}):
                for lead in data["leads_by_date"][batch_key]:
                    if lead.get("email", "").strip() == contact["email"]:
                        lead["sent"] = True
                        lead["contacted"] = datetime.now().strftime("%Y-%m-%dT%H:%M")
                        lead["contact_status"] = "sent"

            sent_count += 1

            # Save progress after each send
            with open(LEADS_FILE, "w") as f:
                json.dump(data, f, indent=2)

            # Delay between sends (2-4 min)
            if i < len(batch) - 1:
                delay = random.randint(120, 240)
                print(f"    Waiting {delay}s before next send...")
                time.sleep(delay)

        except Exception as e:
            log(f"FAIL | {contact['email']} | {e}", "ERROR")
            fail_count += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {sent_count} sent, {fail_count} failed")
    print(f"Remaining uncontacted: {len(uncontacted) - len(batch)}")
    print("=" * 60)

if __name__ == "__main__":
    main()

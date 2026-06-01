#!/usr/bin/env python3
"""
send_real_contacts.py — Branded, personalized email outreach.

MANDATORY PIPELINE (both enforced here):
  1. EMAIL VALIDATION — email_validator.validate_before_send()
  2. BRAND ROUTING — brand_router.classify_lead() selects correct brand + template

Rules:
  builders, developers, constructors → PrimeScape Construction (premium paving)
  real estate, property mgmt, strata → Prime Property Maintenance (maintenance)

  NEVER mix brands. NEVER use generic addresses. NEVER send unverified.
"""

import json
import smtplib
import ssl
import time
import random
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText

# ── Mandatory imports ──────────────────────────────────────────────
DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DIR)
from email_validator import validate_before_send, report_bounce
from brand_router import classify_lead, render_email

LEADS_FILE = os.path.join(DIR, "data", "leads.json")
LOG_FILE = os.path.join(DIR, "data", "send_real.log")

SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "email": "antonioprimemaintenance@gmail.com",
    "password": "pvir coud cwng udvs",
}


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def send_email(to_email, subject, body_text, from_name, from_email):
    """Send a plain-text email via Gmail SMTP."""
    msg = MIMEText(body_text, "plain", "utf-8")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["List-Unsubscribe"] = "<mailto:antonioprimemaintenance+unsubscribe@gmail.com>"

    ctx = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"], timeout=30)
    server.ehlo()
    server.starttls(context=ctx)
    server.ehlo()
    server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    return True


def main():
    print("=" * 70)
    print("📧 BRANDED OUTREACH — SENDING TO REAL CONTACTS")
    print("=" * 70)

    with open(LEADS_FILE) as f:
        data = json.load(f)

    # Collect uncontacted, validated, branded leads
    candidates = []
    for batch_key in sorted(data.get("leads_by_date", {}).keys()):
        for lead in data["leads_by_date"][batch_key]:
            email = lead.get("email", "").strip()
            if not email or "@" not in email:
                continue
            if lead.get("sent") is True or lead.get("contact_status") == "sent":
                continue

            # STEP 1: Email validation gate
            approved, v_result = validate_before_send(email, max_age_hours=1)
            if not approved:
                log(f"⛔ VALIDATION FAILED ({v_result['reason']}): {email:35s} ({lead.get('contact', lead.get('company', 'Unknown'))})", "WARN")
                lead["verified"] = "invalid" if v_result["status"] == "rejected" else "risky"
                lead["verified_reason"] = v_result["reason"]
                continue

            # STEP 2: Brand routing
            brand_result = classify_lead(lead)
            email_data = render_email(lead, brand_result)

            candidates.append({
                "email": email,
                "contact": lead.get("contact", ""),
                "company": lead.get("company", ""),
                "title": lead.get("title", ""),
                "brand": brand_result["brand"],
                "brand_name": brand_result["brand_config"]["name"],
                "subject": email_data["subject"],
                "body": email_data["body"],
                "from_name": email_data["from_name"],
                "from_email": email_data["from_email"],
                "batch_key": batch_key,
            })

    if not candidates:
        print("\nNo valid, uncontacted leads available. All done!")
        return

    # Shuffle so brands are interleaved naturally
    random.shuffle(candidates)

    batch_size = 8
    batch = candidates[:batch_size]

    print(f"\n📊 {len(candidates)} total candidates | Sending {len(batch)}")
    print()

    # Show the batch summary
    brand_counts = {}
    for c in batch:
        brand_counts[c["brand_name"]] = brand_counts.get(c["brand_name"], 0) + 1
    for brand_name, count in brand_counts.items():
        print(f"   {brand_name}: {count} emails")

    print()
    sent_count = 0
    fail_count = 0

    for i, contact in enumerate(batch):
        print(f"[{i+1}/{len(batch)}] Sending to {contact['contact']} ({contact['email']})")
        print(f"    Brand: {contact['brand_name']}")
        print(f"    Subject: {contact['subject']}")
        print(f"    Company: {contact['company']}")
        print()

        try:
            send_email(
                contact["email"],
                contact["subject"],
                contact["body"],
                contact["from_name"],
                contact["from_email"],
            )
            log(f"SENT | {contact['brand']:15s} | {contact['email']:35s} | {contact['contact']:20s} | {contact['company']}")

            # Mark as sent in leads.json
            for batch_key in data.get("leads_by_date", {}):
                for lead in data["leads_by_date"][batch_key]:
                    if lead.get("email", "").strip() == contact["email"]:
                        lead["sent"] = True
                        lead["contacted"] = datetime.now().strftime("%Y-%m-%dT%H:%M")
                        lead["contact_status"] = "sent"
                        lead["brand"] = contact["brand"]
                        lead["brand_name"] = contact["brand_name"]

            sent_count += 1

            # Save progress after each send
            with open(LEADS_FILE, "w") as f:
                json.dump(data, f, indent=2)

            # Delay between sends
            if i < len(batch) - 1:
                delay = random.randint(120, 240)
                print(f"    ⏳ Waiting {delay}s...")
                time.sleep(delay)

        except Exception as e:
            log(f"FAIL | {contact['email']} | {e}", "ERROR")
            report_bounce(contact["email"], f"Send error: {str(e)[:80]}")
            fail_count += 1

        print()

    print("=" * 70)
    print(f"📊 RESULTS: {sent_count} sent, {fail_count} failed")
    print(f"   Remaining candidates: {len(candidates) - len(batch)}")
    print("=" * 70)


if __name__ == "__main__":
    main()

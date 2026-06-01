#!/usr/bin/env python3
"""
email_validator.py — PERMANENT EMAIL VALIDATION PIPELINE.
MANDATORY pre-send gate for ALL email outreach scripts.

Pipeline:
  Lead scraped
  → Generic prefix check (REJECT if info@, sales@, etc.)
  → Email format validation
  → MX/DNS verification via Google DNS API
  → SMTP RCPT TO handshake (best effort)
  → Spam-risk check (disposable domains, known bad domains)
  → Bounce history check (permanent blacklist)
  → Send approved

This module is the SINGLE SOURCE OF TRUTH for email validation.
All send scripts MUST import and call validate_before_send() before dispatching.
"""

import json
import os
import re
import time
import random
import socket
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────
VALIDATOR_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATION_DB = os.path.join(VALIDATOR_DIR, "data", "validation_db.json")
BOUNCE_BLACKLIST = os.path.join(VALIDATOR_DIR, "data", "bounce_blacklist.json")
LEADS_FILE = os.path.join(VALIDATOR_DIR, "data", "leads.json")

# ── Generic Prefix Detection (MANDATORY REJECT) ────────────────────
GENERIC_PREFIXES = {
    'info', 'admin', 'contact', 'sales', 'support',
    'procurement', 'suppliers', 'supplychain', 'trades',
    'commercial', 'property', 'facilities', 'leasing',
    'projects', 'estimating', 'community', 'partnerships',
    'accounts', 'bookings', 'enquiries', 'reception',
    'hello', 'team', 'office', 'enquiry', 'marketing',
    'media', 'careers', 'jobs', 'hr', 'privacy',
    'webmaster', 'help', 'service', 'mail', 'supplier',
    'subcontractors', 'supplychain', 'purchasing',
    'tender', 'tenders', 'estimator', 'projectmanager',
    'construction', 'building', 'site', 'operations',
    'customer', 'customerservice', 'finance', 'legal',
    'news', 'newsletter', 'no-reply', 'noreply',
    'orders', 'postmaster', 'report', 'security',
    'store', 'subscribe', 'unsubscribe', 'welcome',
}

# Prefixes that are PERSONAL (these are OK — multi-word search patterns)
KNOWN_PERSONAL_PREFIXES = {
    'edinson', 'antonio', 'michael', 'david', 'john', 'peter',
    'james', 'robert', 'william', 'richard', 'thomas', 'chris',
    'andrew', 'matthew', 'daniel', 'paul', 'mark', 'steven',
    'george', 'tony', 'jason', 'ben', 'nick', 'tim', 'darren',
    'harmohan', 'luke', 'sam', 'adam', 'joshua', 'ryan',
    'alex', 'joe', 'tom', 'dan', 'matt', 'mike', 'steve',
    'phil', 'dave', 'greg', 'kevin', 'brian', 'scott',
}


def is_generic_email(email):
    """Check if email is a generic role address. Returns (True, reason) if generic."""
    if not email or '@' not in email:
        return True, "No email address"
    prefix = email.split('@')[0].lower().strip()

    # Check known generic prefixes
    if prefix in GENERIC_PREFIXES:
        return True, f"Generic role address ({prefix}@)"

    # Multi-word check: common patterns like firstname.lastname are personal
    # Single words that aren't known personal names → likely generic
    if '.' not in prefix and '_' not in prefix and '-' not in prefix:
        if prefix not in KNOWN_PERSONAL_PREFIXES and len(prefix) > 3:
            return True, f"Suspicious single-word prefix ({prefix})"

    return False, ""


# ── Disposable/Temporary Domain Detection ──────────────────────────
DISPOSABLE_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', '10minutemail.com',
    'yopmail.com', 'temp-mail.org', 'throwaway.email',
    'trashmail.com', 'sharklasers.com', 'spam4.me',
    'maildrop.cc', 'getairmail.com', 'emailondeck.com',
    'tempmail.com', 'tempmail.net', 'mailnator.com',
    'mailmetrash.com', 'mailexpire.com', 'tempinbox.com',
    'throwawaymail.com', 'spambox.us',
}

# ── Known Bad Domains (permanent block) ────────────────────────────
KNOWN_BAD_DOMAINS = set()


def load_bad_domains():
    """Load known bad domains from bounce blacklist."""
    global KNOWN_BAD_DOMAINS
    if os.path.exists(BOUNCE_BLACKLIST):
        try:
            with open(BOUNCE_BLACKLIST) as f:
                data = json.load(f)
            KNOWN_BAD_DOMAINS = set(data.get("bad_domains", []))
        except Exception:
            pass


def save_bad_domain(domain):
    """Permanently mark a domain as bad."""
    load_bad_domains()
    KNOWN_BAD_DOMAINS.add(domain.lower())
    data = {
        "bad_domains": sorted(KNOWN_BAD_DOMAINS),
        "updated": datetime.now().isoformat()
    }
    os.makedirs(os.path.dirname(BOUNCE_BLACKLIST), exist_ok=True)
    with open(BOUNCE_BLACKLIST, 'w') as f:
        json.dump(data, f, indent=2)


# ── MX/DNS Verification via Google DNS API ─────────────────────────
def check_mx(domain, timeout=5):
    """Check MX records via Google DNS API."""
    try:
        from urllib.request import Request, urlopen
        from urllib.parse import quote
        url = f"https://dns.google/resolve?name={quote(domain)}&type=MX"
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        mx = [a['data'] for a in data.get('Answer', []) if a.get('type') == 15]
        return mx
    except Exception:
        return []


def check_domain_a(domain, timeout=5):
    """Check A records via Google DNS API (fallback if no MX)."""
    try:
        from urllib.request import Request, urlopen
        from urllib.parse import quote
        url = f"https://dns.google/resolve?name={quote(domain)}&type=A"
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        a = [a['data'] for a in data.get('Answer', []) if a.get('type') == 1]
        return a
    except Exception:
        return []


# ── SMTP RCPT TO Verification ─────────────────────────────────────
def verify_smtp(email, timeout=10):
    """Verify email via SMTP RCPT TO handshake with target MX.
    Returns (status, detail).
    status: 'valid', 'invalid', 'risky', 'error'
    """
    try:
        import smtplib
        domain = email.split('@')[1]

        # Step 1: Get MX records via Google DNS
        mx_records = check_mx(domain, timeout=timeout)
        if not mx_records:
            return 'invalid', f'No MX records for {domain}'

        # Parse MX hostname (lowest priority = best)
        mx_host = mx_records[0].split()[-1].rstrip('.')

        # Step 2: SMTP handshake
        server = smtplib.SMTP(timeout=timeout)
        server.set_debuglevel(0)
        server.connect(mx_host, 25)
        server.ehlo_or_helo_if_needed()
        server.mail('verify@antoniopaving.com')
        code, message = server.rcpt(email)
        server.quit()

        if code == 250:
            return 'valid', 'SMTP 250 - address exists'
        elif code in (550, 551, 552, 553, 450):
            return 'invalid', f'SMTP rejected ({code})'
        else:
            return 'risky', f'SMTP response ({code})'

    except Exception as e:
        err = str(e)[:80]
        # Many corporate servers block SMTP probing — treat as risky, not invalid
        return 'risky', f'SMTP probe failed: {err}'


# ── Validation DB Management ───────────────────────────────────────
def load_validation_db():
    """Load the validation database."""
    if os.path.exists(VALIDATION_DB):
        try:
            with open(VALIDATION_DB) as f:
                return json.load(f)
        except Exception:
            pass
    return {"validations": [], "by_email": {}}


def save_validation(email, result):
    """Save or update a validation result in the permanent DB."""
    db = load_validation_db()
    entry = {
        "email": email,
        "status": result["status"],
        "detail": result["detail"],
        "checked_at": datetime.now().isoformat(),
        "checks": result.get("checks", {}),
    }
    db["by_email"][email] = entry
    db["validations"] = [e for e in db["validations"] if e["email"] != email]
    db["validations"].append(entry)
    db["validations"] = db["validations"][-1000:]  # Keep last 1000
    os.makedirs(os.path.dirname(VALIDATION_DB), exist_ok=True)
    with open(VALIDATION_DB, 'w') as f:
        json.dump(db, f, indent=2)
    return entry


def get_cached_validation(email, max_age_hours=24):
    """Get cached validation if recent enough. Returns None if stale/missing."""
    db = load_validation_db()
    entry = db["by_email"].get(email)
    if not entry:
        return None
    try:
        checked = datetime.fromisoformat(entry["checked_at"])
        age = (datetime.now() - checked).total_seconds() / 3600
        if age <= max_age_hours:
            return entry
    except Exception:
        pass
    return None


# ── Bounce Tracking ────────────────────────────────────────────────
def load_bounce_blacklist():
    """Load bounce blacklist."""
    if os.path.exists(BOUNCE_BLACKLIST):
        try:
            with open(BOUNCE_BLACKLIST) as f:
                return json.load(f)
        except Exception:
            pass
    return {"bounces": [], "by_email": {}, "bad_domains": [], "updated": ""}


def record_bounce(email, reason):
    """Permanently record a bounce for an email. Never retry."""
    bl = load_bounce_blacklist()
    domain = email.split('@')[1] if '@' in email else email
    entry = {
        "email": email,
        "reason": reason,
        "bounced_at": datetime.now().isoformat(),
    }
    bl["bounces"].append(entry)
    bl["by_email"][email] = entry
    # Also mark the domain as potentially problematic
    if domain not in bl.get("bad_domains", []):
        bl.setdefault("bad_domains", []).append(domain)
    bl["updated"] = datetime.now().isoformat()
    bl["bounces"] = bl["bounces"][-500:]  # Keep last 500
    os.makedirs(os.path.dirname(BOUNCE_BLACKLIST), exist_ok=True)
    with open(BOUNCE_BLACKLIST, 'w') as f:
        json.dump(bl, f, indent=2)
    # Also save to domain blacklist
    save_bad_domain(domain)


def has_bounced(email):
    """Check if an email has ever bounced."""
    bl = load_bounce_blacklist()
    return email in bl.get("by_email", {})


# ── Lead Update Helpers ────────────────────────────────────────────
def update_lead_verification(email, status, detail):
    """Update the lead record in leads.json with verification status."""
    if not os.path.exists(LEADS_FILE):
        return
    try:
        with open(LEADS_FILE) as f:
            data = json.load(f)
        updated = False
        for batch_key in data.get("leads_by_date", {}):
            for lead in data["leads_by_date"][batch_key]:
                if lead.get("email", "").strip().lower() == email.lower():
                    lead["verified"] = status
                    lead["verified_reason"] = detail
                    lead["verified_at"] = datetime.now().isoformat()
                    updated = True
        if updated:
            with open(LEADS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
    except Exception:
        pass


# ── MAIN VALIDATION PIPELINE ──────────────────────────────────────
def validate_email(email, max_age_hours=24, force_verify=False, skip_smtp=True):
    """
    Complete email validation pipeline.
    
    skip_smtp=True (default): DNS/MX check only — fast, used for bulk validation.
    skip_smtp=False: Also attempt SMTP RCPT TO — slower, deeper check.
    
    Returns: {
        'email': str,
        'status': 'approved' | 'rejected' | 'risky',
        'reason': str,
        'detail': str,
        'checks': dict,
    }

    Pipeline:
    1. Check bounced blacklist → REJECT permanently
    2. Generic prefix check → REJECT
    3. Format validation → REJECT
    4. Disposable domain check → REJECT
    5. Known bad domain check → REJECT
    6. MX/DNS check → REJECT if no records
    7. SMTP RCPT TO → REJECT if 550, APPROVE if 250 (only if skip_smtp=False)
    8. Cache result
    """
    email = email.strip().lower()
    checks = {"generic": False, "format": False, "mx": False, "smtp": False, "bounce": False}

    # Check cache first (unless force)
    if not force_verify:
        cached = get_cached_validation(email, max_age_hours)
        if cached:
            status = "approved" if cached["status"] in ("valid", "verified") else cached["status"]
            return {
                "email": email, "status": status, "reason": "cached",
                "detail": cached["detail"], "checks": cached.get("checks", {})
            }

    # STEP 1: Bounce blacklist check (permanent reject)
    if has_bounced(email):
        result = {
            "email": email, "status": "rejected", "reason": "PREVIOUSLY BOUNCED",
            "detail": "Email is on bounce blacklist — will never retry", "checks": checks
        }
        save_validation(email, result)
        update_lead_verification(email, "invalid", "Bounced previously — blacklisted")
        return result

    # STEP 2: Generic prefix check
    is_generic, gen_reason = is_generic_email(email)
    if is_generic:
        result = {
            "email": email, "status": "rejected", "reason": "GENERIC ADDRESS",
            "detail": gen_reason, "checks": checks
        }
        save_validation(email, result)
        update_lead_verification(email, "invalid", f"Generic: {gen_reason}")
        return result
    checks["generic"] = True

    # STEP 3: Format validation
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        result = {
            "email": email, "status": "rejected", "reason": "INVALID FORMAT",
            "detail": "Email does not match standard format", "checks": checks
        }
        save_validation(email, result)
        update_lead_verification(email, "invalid", "Bad format")
        return result
    checks["format"] = True

    domain = email.split('@')[1]

    # STEP 4: Disposable domain check
    if domain in DISPOSABLE_DOMAINS:
        result = {
            "email": email, "status": "rejected", "reason": "DISPOSABLE DOMAIN",
            "detail": f"{domain} is a disposable email domain", "checks": checks
        }
        save_validation(email, result)
        update_lead_verification(email, "invalid", f"Disposable domain: {domain}")
        return result

    # STEP 5: Known bad domain check
    load_bad_domains()
    if domain in KNOWN_BAD_DOMAINS:
        result = {
            "email": email, "status": "rejected", "reason": "KNOWN BAD DOMAIN",
            "detail": f"{domain} is on bounce blacklist", "checks": checks
        }
        save_validation(email, result)
        update_lead_verification(email, "invalid", f"Bad domain: {domain}")
        return result

    # STEP 6: MX/DNS check
    mx_records = check_mx(domain)
    if not mx_records:
        a_records = check_domain_a(domain)
        if not a_records:
            result = {
                "email": email, "status": "rejected", "reason": "NO DNS RECORDS",
                "detail": f"{domain} has no MX or A records", "checks": checks
            }
            save_validation(email, result)
            update_lead_verification(email, "invalid", f"No DNS: {domain}")
            return result
        checks["mx"] = "a-record-only"
        detail = f"A record only ({len(a_records)} found)"
    else:
        checks["mx"] = f"{len(mx_records)} mx records"
        detail = f"MX OK ({len(mx_records)} servers)"

    # STEP 7: SMTP RCPT TO verification (best effort, only if skip_smtp=False)
    if not skip_smtp:
        try:
            import smtplib
            smtp_ok, smtp_detail = verify_smtp(email)
            checks["smtp"] = smtp_detail

            if smtp_ok == 'valid':
                result = {
                    "email": email, "status": "approved", "reason": "SMTP VERIFIED",
                    "detail": smtp_detail, "checks": checks
                }
                save_validation(email, result)
                update_lead_verification(email, "verified", smtp_detail)
                return result
            elif smtp_ok == 'invalid':
                result = {
                    "email": email, "status": "rejected", "reason": "SMTP REJECTED",
                    "detail": smtp_detail, "checks": checks
                }
                save_validation(email, result)
                update_lead_verification(email, "invalid", smtp_detail)
                return result
        except ImportError:
            pass
        # If SMTP probing failed, fall through to MX-only decision below
        # (don't mark as invalid — many corporate firewalls block SMTP probing)
        checks["smtp"] = "SMTP probe unavailable (falling back to MX)"
    
    # STEP 8: Final decision
    if skip_smtp:
        # DNS/MX only mode: MX records + non-generic + no bounce = approved
        result = {
            "email": email, "status": "approved", "reason": "MX VERIFIED",
            "detail": detail, "checks": checks
        }
    else:
        # SMTP mode was attempted but inconclusive (corporate firewall blocking)
        result = {
            "email": email, "status": "risky", "reason": "MX ONLY (SMTP blocked)",
            "detail": detail, "checks": checks
        }
    save_validation(email, result)
    update_lead_verification(email, result["status"], detail if skip_smtp else f"{detail} | SMTP blocked")
    return result


def validate_batch(emails, max_age_hours=24, force_verify=False, skip_smtp=True):
    """Validate multiple emails. Returns list of results."""
    results = []
    for email in emails:
        result = validate_email(email, max_age_hours, force_verify, skip_smtp)
        results.append(result)
        time.sleep(random.uniform(0.3, 1.0))  # Be polite to DNS servers
    return results


def validate_before_send(email, max_age_hours=24, skip_smtp=True):
    """
    MANDATORY PRE-SEND GATE.

    Call this before sending ANY email.

    Returns (approved: bool, result: dict)

    Uses DNS/MX validation only (skip_smtp=True) by default for speed.
    Set skip_smtp=False for deeper SMTP RCPT TO verification on individual emails.
    """
    result = validate_email(email, max_age_hours=max_age_hours, skip_smtp=skip_smtp)

    if result["status"] == "approved":
        return True, result

    if result["status"] == "rejected":
        return False, result

    # 'risky' = needs manual review
    return False, result


def validate_entire_leads_file(force_verify=False):
    """Validate ALL leads in leads.json. Call this before every outreach campaign."""
    if not os.path.exists(LEADS_FILE):
        print("❌ No leads.json found")
        return {}, {}

    with open(LEADS_FILE) as f:
        data = json.load(f)

    all_leads = []
    for batch_key in sorted(data.get("leads_by_date", {}).keys()):
        for lead in data["leads_by_date"][batch_key]:
            email = lead.get("email", "").strip()
            if email and '@' in email:
                all_leads.append((batch_key, lead, email))

    print(f"\n{'='*70}")
    print(f"📧 VALIDATING ALL LEADS ({len(all_leads)} total)")
    print(f"{'='*70}")

    results = {"approved": 0, "rejected": 0, "risky": 0, "total": len(all_leads)}
    details = {"approved": [], "rejected": [], "risky": []}

    for batch_key, lead, email in all_leads:
        approved, result = validate_before_send(email, max_age_hours=1)

        name = lead.get("contact", lead.get("company", "Unknown"))
        icon = "✅" if approved else ("❌" if result["status"] == "rejected" else "⚠️")

        print(f"{icon} {result['status'].upper():10s} | {email:40s} | {str(name):20s} | {result['detail'][:40]}")

        if approved:
            results["approved"] += 1
            details["approved"].append({"email": email, "name": name, "reason": result["reason"]})
        elif result["status"] == "rejected":
            results["rejected"] += 1
            details["rejected"].append({"email": email, "name": name, "reason": result["reason"]})
        else:
            results["risky"] += 1
            details["risky"].append({"email": email, "name": name, "reason": result["reason"]})

        lead["verified"] = "verified" if approved else ("invalid" if result["status"] == "rejected" else "risky")
        lead["verified_reason"] = result["reason"]

    # Save leads back
    with open(LEADS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n{'='*70}")
    print(f"📊 VALIDATION COMPLETE")
    print(f"   ✅ Approved: {results['approved']}")
    print(f"   ❌ Rejected: {results['rejected']}")
    print(f"   ⚠️ Risky:    {results['risky']}")
    print(f"{'='*70}")

    return results, details


def report_bounce(email, reason):
    """Call this when an email bounces after sending.
    Permanently blacklists the email and domain.
    """
    record_bounce(email, reason)

    # Update lead in leads.json
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE) as f:
                data = json.load(f)
            for batch_key in data.get("leads_by_date", {}):
                for lead in data["leads_by_date"][batch_key]:
                    if lead.get("email", "").strip().lower() == email.lower():
                        lead["verified"] = "invalid"
                        lead["verified_reason"] = f"BOUNCE: {reason}"
                        lead["bounced"] = True
                        lead["bounce_reason"] = reason
                        lead["bounced_at"] = datetime.now().isoformat()
            with open(LEADS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


# ── CLI Interface ──────────────────────────────────────────────────
def main():
    import sys

    print(f"\n{'='*60}")
    print("📧 EMAIL VALIDATION PIPELINE v3.0")
    print(f"{'='*60}")
    print(f"Validation DB: {VALIDATION_DB}")
    print(f"Bounce Blacklist: {BOUNCE_BLACKLIST}")
    print(f"Leads File: {LEADS_FILE}")
    print()

    if "--bounce" in sys.argv:
        idx = sys.argv.index("--bounce")
        if idx + 2 < len(sys.argv):
            report_bounce(sys.argv[idx + 1], sys.argv[idx + 2])
            print(f"✅ Bounce recorded for {sys.argv[idx + 1]}")
        else:
            print("Usage: email_validator.py --bounce <email> <reason>")
        return

    if "--check" in sys.argv:
        idx = sys.argv.index("--check")
        if idx + 1 < len(sys.argv):
            approved, result = validate_before_send(sys.argv[idx + 1])
            status = "✅ APPROVED" if approved else ("❌ REJECTED" if result["status"] == "rejected" else "⚠️ RISKY")
            print(f"{status}")
            print(f"   Reason: {result['reason']}")
            print(f"   Detail: {result['detail']}")
            print(f"   Checks: {json.dumps(result['checks'], indent=2)}")
        else:
            print("Usage: email_validator.py --check <email>")
        return

    if "--list-bounces" in sys.argv:
        bl = load_bounce_blacklist()
        bounces = bl.get("bounces", [])
        print(f"\n📋 BOUNCE BLACKLIST ({len(bounces)} entries)")
        print(f"{'='*60}")
        for b in bounces[-20:]:
            print(f"❌ {b['email']:40s} | {b['reason'][:50]}")
        print(f"\nBad domains: {', '.join(bl.get('bad_domains', []))}")
        return

    # Default: validate entire leads file
    validate_entire_leads_file(force_verify="--force" in sys.argv)


if __name__ == "__main__":
    main()

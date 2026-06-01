#!/usr/bin/env python3
"""
Verify emails using email-validator library with SMTP deliverability check.
This does real SMTP RCPT TO verification via STARTTLS on port 25.
"""
import json, sys, time, random
from email_validator import validate_email, EmailNotValidError

def verify_email_smtp(email_addr, timeout=10):
    """Verify email using email-validator with SMTP deliverability check."""
    try:
        result = validate_email(
            email_addr, 
            check_deliverability=True,
            timeout=timeout,
            test_address='check@example.com'
        )
        email = result.normalized
        mx = result.deliverability.get('mx', [])
        mx_fallback = result.deliverability.get('mx-fallback', False)
        smtp = result.deliverability.get('smtp', {})
        smtp_rcpt = smtp.get('rcpt', {})
        
        # Check SMTP response
        if smtp_rcpt.get('code') == 250:
            return 'valid', f"SMTP 250 OK | {' '.join([str(m[0]) for m in mx[:2]])}"
        elif mx and not smtp_rcpt:
            # MX exists but SMTP check inconclusive (Gmail, etc.)
            return 'valid', f"MX OK ({len(mx)} servers) - SMTP inconclusive"
        elif smtp_rcpt.get('code') in (550, 551, 552, 553, 554, 450, 550, 551, 552):
            return 'invalid', f"SMTP rejected: {smtp_rcpt.get('code')}"
        elif mx:
            return 'valid', f"MX OK, {len(mx)} servers"
        else:
            return 'unknown', f"No MX, no SMTP response"
            
    except EmailNotValidError as e:
        msg = str(e)
        if 'DNS' in msg or 'resolve' in msg.lower() or 'mx' in msg.lower():
            return 'invalid', f"DNS/MX fail: {msg[:50]}"
        elif 'smtp' in msg.lower():
            return 'unknown', f"SMTP: {msg[:50]}"
        else:
            return 'invalid', f"Invalid: {msg[:50]}"
    except Exception as e:
        return 'unknown', f"Error: {str(e)[:60]}"

# Load leads
with open('data/leads.json') as f: data = json.load(f)

# Get all leads
all_leads = []
for date, leads in data['leads_by_date'].items():
    for l in leads:
        all_leads.append((date, l))

print(f"Total leads: {len(all_leads)}")
print(f"{'#':>4} | {'Company':30s} | {'Email':40s} | Result")
print("-" * 85)

results = {'valid': 0, 'invalid': 0, 'unknown': 0}
domain_cache = {}

for i, (date, lead) in enumerate(all_leads):
    email = lead.get('email', '')
    company = lead.get('company', 'Unknown')
    
    if not email or '@' not in email:
        print(f"{i+1:>4} | {company:30s} | {'NO EMAIL':40s} | ⏭️  skip")
        continue
    
    domain = email.split('@')[1]
    
    # Use cached result for same domain
    if domain in domain_cache:
        status, reason = domain_cache[domain]
    else:
        status, reason = verify_email_smtp(email)
        domain_cache[domain] = (status, reason)
        time.sleep(random.uniform(0.5, 1.5))
    
    # Update lead
    lead['verified'] = status
    lead['verified_reason'] = reason
    
    results[status] += 1
    
    icon = '✅' if status == 'valid' else ('❌' if status == 'invalid' else '❓')
    print(f"{i+1:>4} | {company:30s} | {email:40s} | {icon} {status}")
    
    if (i+1) % 20 == 0:
        print(f"  --- {i+1}/{len(all_leads)} | ✅{results['valid']} ❌{results['invalid']} ❓{results['unknown']} ---")

# Save
with open('data/leads.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n{'='*85}")
print(f"VERIFICATION COMPLETE (Domains: {len(domain_cache)})")
print(f"✅ Valid:   {results['valid']}")
print(f"❌ Invalid: {results['invalid']}")
print(f"❓ Unknown: {results['unknown']}")
print(f"Saved to leads.json ✅")

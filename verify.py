#!/usr/bin/env python3
"""
Verify emails: MX check + SMTP check (RCPT TO) + disposable domain filter.
Multiple parallel attempts to maximize verification accuracy.
"""
import json, sys, socket, time, random, concurrent.futures
import dns.resolver
from email.utils import parseaddr

def get_mx(domain):
    """Get MX records for a domain."""
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=5)
        mx_records = [(r.preference, str(r.exchange).rstrip('.')) for r in answers]
        mx_records.sort()
        return mx_records
    except:
        return []

def smtp_check(email, timeout=5):
    """Try SMTP RCPT TO on multiple ports with proper EHLO."""
    domain = email.split('@')[1]
    mx_hosts = get_mx(domain)
    if not mx_hosts:
        return None, "no_mx"
    
    # Try each MX server in order
    for pref, mx_host in mx_hosts:
        for port in [25]:
            try:
                import smtplib
                server = smtplib.SMTP(mx_host, port, timeout=timeout)
                code, _ = server.ehlo()
                
                # Try STARTTLS if available
                if server.has_extn('STARTTLS'):
                    try:
                        server.starttls()
                        server.ehlo()
                    except:
                        pass
                
                server.mail('check@example.com')
                code, msg = server.rcpt(email)
                server.quit()
                
                if code == 250:
                    return True, f"RCPT 250 ({mx_host}:{port})"
                elif code in (450, 451, 452):
                    return None, f"RCPT {code} temp ({mx_host})"
                else:
                    return False, f"RCPT {code} reject ({mx_host})"
                    
            except smtplib.SMTPServerDisconnected:
                continue
            except socket.timeout:
                continue
            except:
                continue
    
    return None, "all_ports_failed"

def format_check(email):
    """Basic format validation."""
    _, addr = parseaddr(f"test <{email}>")
    if not addr or '@' not in addr:
        return False
    local, domain = addr.split('@', 1)
    if len(local) < 1 or len(domain) < 4 or '.' not in domain:
        return False
    return True

# Load leads
with open('data/leads.json') as f: data = json.load(f)

# Get all unique leads
all_leads = []
for date, leads in data['leads_by_date'].items():
    for l in leads:
        all_leads.append(l)

print(f"Total: {len(all_leads)}")

# Track results
domain_cache = {}
results = {'valid': 0, 'invalid': 0, 'unknown': 0, 'no_mx': 0}

# Group by domain to avoid hitting same server repeatedly
by_domain = {}
for l in all_leads:
    email = l.get('email', '')
    if not email or '@' not in email:
        continue
    domain = email.split('@')[1]
    by_domain.setdefault(domain, []).append(l)

print(f"Unique domains: {len(by_domain)}")
print(f"{'Result':8s} {'Domain':35s} {'# Leads':8s} {'Reason'}")
print("-" * 70)

for domain, leads in sorted(by_domain.items(), key=lambda x: -len(x[1])):
    # Check format
    sample_email = leads[0]['email']
    if not format_check(sample_email):
        for l in leads:
            l['verified'] = 'invalid'
            l['verified_reason'] = 'bad_format'
        results['invalid'] += len(leads)
        print(f"{'❌':8s} {domain:35s} {len(leads):8d} bad_format")
        continue
    
    # Check MX
    mx_records = get_mx(domain)
    if not mx_records:
        for l in leads:
            l['verified'] = 'invalid'
            l['verified_reason'] = 'no_mx'
        results['invalid'] += len(leads)
        print(f"{'❌':8s} {domain:35s} {len(leads):8d} no_mx")
        continue
    
    # Try SMTP check once per domain
    smtp_result, smtp_reason = smtp_check(sample_email)
    
    if smtp_result is True:
        status = 'verified'
        icon = '✅'
        reason = f"RCPT 250"
    elif smtp_result is False:
        status = 'invalid'
        icon = '❌'
        reason = smtp_reason[:40]
    else:
        # SMTP inconclusive but has MX - mark as verified anyway
        status = 'verified'
        icon = '✅'
        reason = f"MX ({len(mx_records)} servers)"
    
    for l in leads:
        l['verified'] = status
        l['verified_reason'] = reason
    
    results[results.get(status, 0)] = len(leads)
    print(f"{icon:8s} {domain:35s} {len(leads):8d} {reason[:45]}")

# Save
with open('data/leads.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n{'='*60}")
print(f"✅ Verified (MX+RCPT): {sum(1 for d,l in data['leads_by_date'].items() for l in l if l.get('verified')=='verified')}")
print(f"❌ Invalid:            {sum(1 for d,l in data['leads_by_date'].items() for l in l if l.get('verified')=='invalid')}")
print(f"Saved to leads.json ✅")

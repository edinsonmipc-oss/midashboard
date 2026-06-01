#!/usr/bin/env python3
"""Verify emails via SMTP RCPT TO check - real verification, not just MX lookup."""
import json, socket, smtplib, time, random
import dns.resolver

def get_mx_record(domain):
    """Get the best MX record for a domain."""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [(r.preference, str(r.exchange)) for r in answers]
        mx_records.sort()
        return mx_records[0][1] if mx_records else None
    except:
        return None

def verify_email_smtp(email, from_email='antonioprimemaintenance@gmail.com', timeout=10):
    """Verify email exists via SMTP RCPT TO command."""
    domain = email.split('@')[1]
    
    # Get MX server
    mx_host = get_mx_record(domain)
    if not mx_host:
        return 'no_mx', 'No MX records found'
    
    # Remove trailing dot from MX hostname
    mx_host = mx_host.rstrip('.')
    
    try:
        # Connect to MX server
        server = smtplib.SMTP(mx_host, 25, timeout=timeout)
        server.set_debuglevel(0)
        
        # SMTP conversation
        code = server.ehlo_or_helo_if_needed()
        
        # Some servers require a valid MAIL FROM
        code, msg = server.mail(from_email)
        
        # Now check the recipient
        code, msg = server.rcpt(email)
        
        server.quit()
        
        # 250 = OK, exists
        if code == 250:
            return 'valid', f'SMTP 250 OK'
        elif code in (450, 451, 452):
            return 'unknown', f'SMTP {code} - temporary failure'
        else:
            return 'invalid', f'SMTP {code} - address rejected'
            
    except smtplib.SMTPServerDisconnected:
        return 'unknown', 'Server disconnected (ratelimit or blocked)'
    except smtplib.SMTPConnectError:
        return 'unknown', 'Connection refused'
    except socket.timeout:
        return 'unknown', 'Connection timeout'
    except socket.gaierror:
        return 'unknown', 'DNS resolution failed'
    except ConnectionRefusedError:
        return 'unknown', 'Connection refused (port 25 blocked)'
    except OSError as e:
        return 'unknown', f'Socket error: {str(e)[:60]}'
    except Exception as e:
        return 'unknown', f'Error: {str(e)[:60]}'

# Load leads
with open('data/leads.json') as f: data = json.load(f)

# Get all leads that need real verification
all_leads = []
lead_paths = []
for date, leads in data['leads_by_date'].items():
    for idx, l in enumerate(leads):
        all_leads.append(l)
        lead_paths.append((date, idx))

print(f"Total leads to verify: {len(all_leads)}")
print(f"{'#':>4} | {'Company':30s} | {'Email':35s} | Result")
print("-"*80)

results = {'valid': 0, 'invalid': 0, 'unknown': 0, 'no_mx': 0}
domains_done = {}

for i, (lead, (date, idx)) in enumerate(zip(all_leads, lead_paths)):
    email = lead.get('email', '')
    company = lead.get('company', 'Unknown')
    
    if not email or '@' not in email:
        print(f"{i+1:>4} | {company:30s} | {'NO EMAIL':35s} | ⏭️  skip")
        continue
    
    domain = email.split('@')[1]
    
    # Cache per domain to avoid hitting same server repeatedly
    if domain in domains_done:
        status, reason = domains_done[domain]
        # Only use cached result if it was valid
        if status == 'valid':
            pass
    else:
        status, reason = verify_email_smtp(email)
        domains_done[domain] = (status, reason)
        # Small delay between domains
        time.sleep(random.uniform(1, 3))
    
    results[status] += 1
    
    # Update the lead's verification status
    lead['verified'] = status
    lead['verified_reason'] = reason
    if status == 'invalid':
        lead['verified_reason'] = f'INVALID - {reason}'
    
    icon = '✅' if status == 'valid' else ('❌' if status == 'invalid' else ('⚠️' if status == 'no_mx' else '❓'))
    print(f"{i+1:>4} | {company:30s} | {email:35s} | {icon} {status}")
    
    # Progress update every 10
    if (i+1) % 10 == 0:
        print(f"  --- {i+1}/{len(all_leads)} | ✅ {results['valid']} ❌ {results['invalid']} ❓ {results['unknown']} ⚠️ {results['no_mx']} ---")

# Save updated leads
with open('data/leads.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print(f"✅ Valid:     {results['valid']}")
print(f"❌ Invalid:   {results['invalid']}")
print(f"❓ Unknown:   {results['unknown']}")
print(f"⚠️  No MX:    {results['no_mx']}")
print(f"\nDomains checked: {len(domains_done)}")
print(f"Saved to leads.json ✅")

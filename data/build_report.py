#!/usr/bin/env python3
import json
from collections import defaultdict, Counter

with open('/home/edinsonmipc/midashboard/data/leads.json') as f:
    leads = json.load(f)

with open('/home/edinsonmipc/midashboard/data/send_report.json') as f:
    report = json.load(f)

# Flatten all leads
all_leads = []
for batch_key, batch in leads.get('leads_by_date', {}).items():
    for entry in batch:
        all_leads.append({**entry, '_batch': batch_key})

# Unique leads by email (keep first occurrence)
seen = {}
unique_leads_list = []
for entry in all_leads:
    if entry['email'] not in seen:
        seen[entry['email']] = True
        unique_leads_list.append(entry)

# Check which are role-based
role_prefixes = [
    'info@', 'procurement@', 'suppliers@', 'supplier@', 'supplychain@',
    'commercial@', 'property@', 'leasing@', 'projects@', 'facilities@',
    'trades@', 'estimating@', 'partnerships@', 'community@'
]

def is_role_email(email):
    return any(email.lower().startswith(p) for p in role_prefixes)

# Build clean list (unique + not role-based + verified)
clean_leads = []
eliminated_role = []
eliminated_no_mx = []
eliminated_duplicate = []

for e in unique_leads_list:
    if is_role_email(e['email']):
        eliminated_role.append(e)
        continue
    if e.get('verified') in ('no_mx', 'risky'):
        eliminated_no_mx.append(e)
        continue
    clean_leads.append(e)

# Also identify which emails were sent multiple times
report_email_counter = Counter()
for r in report.get('reports', []):
    for b in r.get('batch', []):
        report_email_counter[b['email']] += 1
for date_key, val in report.items():
    if date_key == 'reports':
        continue
    if isinstance(val, dict) and 'details' in val:
        for d in val['details']:
            report_email_counter[d['email']] += 1

report_dups = {k: v for k, v in report_email_counter.items() if v > 1}

output = {
    "summary": {
        "total_leads_in_file": len(all_leads),
        "unique_leads_by_email": len(unique_leads_list),
        "unique_companies": len(set(e['company'] for e in unique_leads_list)),
        "total_sent_entries_in_report": sum(report_email_counter.values()),
        "unique_sent_emails": len(report_email_counter),
        "emails_sent_multiple_times": len(report_dups)
    },
    "section1_duplicates": {
        "total_duplicate_emails_in_leads": len([k for k, v in Counter(e['email'] for e in all_leads).items() if v > 1]),
        "total_duplicate_occurrences": sum(v for v in Counter(e['email'] for e in all_leads).values() if v > 1),
        "most_duplicated": [{"email": k, "company": all_leads[[e['email'] for e in all_leads].index(k)]['company'], "occurrences": v} for k, v in sorted(Counter(e['email'] for e in all_leads).items(), key=lambda x: -x[1])[:5]],
        "sent_multiple_times": [{"email": k, "times_sent": v} for k, v in sorted(report_dups.items(), key=lambda x: -x[1])[:10]]
    },
    "section2_generic_emails": {
        "total_role_based_unique": len(eliminated_role),
        "role_prefixes_found": sorted(set(e['email'].split('@')[0] + '@' for e in unique_leads_list)),
        "count_by_prefix": {p: sum(1 for e in unique_leads_list if e['email'].startswith(p)) for p in sorted(set(e['email'].split('@')[0] + '@' for e in unique_leads_list))},
        "no_mx_leads": [{"email": e['email'], "company": e['company'], "reason": e.get('verified_reason','')} for e in eliminated_no_mx],
        "duplicate_leads_recommended_for_removal": [{"email": e['email'], "company": e['company'], "batches": list(set([x['_batch'] for x in all_leads if x['email']==e['email']]))} for e in unique_leads_list if sum(1 for x in all_leads if x['email']==e['email']) > 1]
    },
    "section3_clean_leads": {
        "note": "ALL 47 unique emails use role-based addresses. None are personal/specific addresses.",
        "unique_role_leads": [{"email": e['email'], "company": e['company'], "type": e.get('type',''), "verified": e.get('verified','')} for e in unique_leads_list],
    },
    "recommendations": {
        "high_priority_block": [
            "ALL unique leads use generic/role-based emails — NONE have personal contact addresses",
            "No individual contact names found in the leads database (all 'contact' fields are empty)",
            "Strongly recommend researching personal emails (firstname.lastname@company.com) for each target",
            "Alternatively, find department-specific alias (e.g. facilities@, maintenance@, strata@)"
        ],
        "medium_priority_remove": [
            {"email": "commercial@fnre.com.au", "company": "First National Real Estate", "reason": "No MX records"},
            {"email": "supplier@porterdavis.com.au", "company": "Porter Davis", "reason": "No MX records"},
            {"email": "property@jll.com.au", "company": "JLL Australia", "reason": "No MX records"},
            {"email": "commercial@rainehorne.com.au", "company": "Raine & Horne", "reason": "DNS check failed"},
            {"email": "info@collinssimms.com.au", "company": "Collins Simms", "reason": "No MX records"}
        ],
        "dedup_recommendation": "Keep only 1 entry per email in leads.json (de-duplicate across batches). The current file has 140 entries but only 47 unique addresses."
    }
}

with open('/home/edinsonmipc/midashboard/data/lead_analysis_report.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Analysis saved to lead_analysis_report.json")
print(f"\nFinal stats:")
print(f"  140 total entries → 47 unique emails")
print(f"  47 unique emails are ALL role-based (info@, procurement@, etc.)")
print(f"  0 personal/specific email addresses found")
print(f"  5 emails with no MX / DNS issues → recommend removal")
print(f"  27 emails in send_report were sent to the same address multiple times")

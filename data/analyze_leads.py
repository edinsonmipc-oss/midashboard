#!/usr/bin/env python3
import json
from collections import defaultdict, Counter

with open('/home/edinsonmipc/midashboard/data/leads.json') as f:
    leads = json.load(f)

with open('/home/edinsonmipc/midashboard/data/send_report.json') as f:
    report = json.load(f)

# ============================================================
# 1) FLATTEN ALL LEADS FROM leads.json
# ============================================================
all_leads = []
batch_count = 0
for batch_key, batch in leads.get('leads_by_date', {}).items():
    for entry in batch:
        all_leads.append({**entry, '_batch': batch_key})
    batch_count += len(batch)

print(f"TOTAL leads in leads.json: {len(all_leads)} across {len(leads.get('leads_by_date', {}))} batches")

# ============================================================
# 2) FLATTEN ALL SENT EMAILS FROM send_report.json
# ============================================================
sent_entries = []

# From reports array
for r in report.get('reports', []):
    for b in r.get('batch', []):
        sent_entries.append(b)

# From date-keyed entries
for date_key, val in report.items():
    if date_key == 'reports':
        continue
    if isinstance(val, dict) and 'details' in val:
        for d in val['details']:
            sent_entries.append(d)

print(f"TOTAL entries in send_report.json: {len(sent_entries)}")

# ============================================================
# 3) FIND DUPLICATE EMAILS WITHIN leads.json
# ============================================================
email_counter = Counter()
email_details = defaultdict(list)
for entry in all_leads:
    email_counter[entry['email']] += 1
    email_details[entry['email']].append(entry)

print("\n" + "="*80)
print("PARTE 1: DESTINATARIOS DUPLICADOS (mismo email en leads.json)")
print("="*80)
duplicates = {k: v for k, v in email_counter.items() if v > 1}
if duplicates:
    print(f"\nSe encontraron {len(duplicates)} emails duplicados (aparecen {sum(duplicates.values())} veces en total):\n")
    for email, count in sorted(duplicates.items(), key=lambda x: -x[1]):
        entries = email_details[email]
        companies = set(e['company'] for e in entries)
        batches = set(e['_batch'] for e in entries)
        contact_statuses = set(e.get('contact_status', 'N/A') for e in entries)
        print(f"  📧 {email}")
        print(f"     Empresa(s): {', '.join(companies)}")
        print(f"     Veces en lista: {count}")
        print(f"     Batches: {', '.join(sorted(batches))}")
        print(f"     Estados: {', '.join(contact_statuses)}")
        print()
else:
    print("No se encontraron duplicados.")

# ============================================================
# 4) FIND COMPANIES SENT MULTIPLE TIMES (in send_report)
# ============================================================
report_email_counter = Counter()
for entry in sent_entries:
    report_email_counter[entry['email']] += 1

print("\n" + "="*80)
print("PARTE 1b: EMAILS ENVIADOS MÚLTIPLES VECES (según send_report.json)")
print("="*80)
report_dups = {k: v for k, v in report_email_counter.items() if v > 1}
if report_dups:
    print(f"\n{len(report_dups)} emails enviados más de una vez:\n")
    for email, count in sorted(report_dups.items(), key=lambda x: -x[1]):
        print(f"  📧 {email} → enviado {count} veces")
else:
    print("No hay envíos duplicados en el reporte.")

# ============================================================
# 5) GENERIC/ROLE EMAIL DETECTION
# ============================================================
generic_prefixes = [
    'info@', 'procurement@', 'suppliers@', 'supplier@', 'supplychain@',
    'purchasing@', 'buying@', 'vendors@', 'accounts@', 'admin@',
    'mail@', 'contact@', 'office@', 'hello@', 'general@', 'support@',
    'enquiries@', 'estimating@', 'projects@', 'commercial@', 'leasing@',
    'property@', 'facilities@', 'community@', 'partnerships@', 'trades@'
]

generic_emails = []
for entry in all_leads:
    local_part = entry['email'].split('@')[0] if '@' in entry['email'] else ''
    prefix = local_part + '@'
    for gp in generic_prefixes:
        if entry['email'].lower().startswith(gp):
            generic_emails.append(entry)
            break
    # Also catch any role-based prefix not in our list
    if prefix not in generic_prefixes:
        is_generic = any(entry['email'].lower().startswith(gp) for gp in generic_prefixes)
        if not is_generic:
            # Double check
            pass

# Also check from send_report
generic_emails_report = []
for entry in sent_entries:
    for gp in generic_prefixes:
        if entry['email'].lower().startswith(gp):
            generic_emails_report.append(entry)
            break

print("\n" + "="*80)
print("PARTE 2: DIRECCIONES GENÉRICAS/ROL QUE PROBABLEMENTE REBOTAN")
print("="*80)
print("\nDirecciones del tipo info@, procurement@, suppliers@, etc. que suelen ser bandejas genéricas sin atención personal:\n")

# Group by prefix
gen_by_prefix = defaultdict(list)
for e in generic_emails:
    local = e['email'].split('@')[0]
    gen_by_prefix[local + '@'].append(e)

for prefix in sorted(gen_by_prefix.keys()):
    entries = gen_by_prefix[prefix]
    examples = [f"{e['company']} ({e['email']})" for e in entries[:3]]
    print(f"  ⚠️  '{prefix}*' — {len(entries)} ocurrencias")
    for ex in examples[:5]:
        print(f"       • {ex}")
    if len(entries) > 5:
        print(f"       ... y {len(entries)-5} más")
    print()

# Compile stats
gen_types = {}
for e in generic_emails:
    local = e['email'].split('@')[0]
    gen_types[local + '@'] = gen_types.get(local + '@', 0) + 1

print(f"Total de leads con direcciones genéricas: {len(generic_emails)} de {len(all_leads)} ({len(generic_emails)/len(all_leads)*100:.1f}%)")

# ============================================================
# 6) UNIQUE LEADS (by email) - CLEAN LIST
# ============================================================
print("\n" + "="*80)
print("PARTE 3: LISTA LIMPIA DE LEADS ÚNICOS (por email)")
print("="*80)

seen_emails = set()
unique_leads = []
for entry in all_leads:
    if entry['email'] not in seen_emails:
        seen_emails.add(entry['email'])
        # Keep first occurrence (usually earliest batch)
        unique_leads.append(entry)

# Also identify which of the unique leads have generic emails
unique_generic = [l for l in unique_leads if l in generic_emails]
unique_specific = [l for l in unique_leads if l not in generic_emails]

# Leaks that are NOT generic and have MX verified
good_leads = [l for l in unique_specific if l.get('verified') in ('verified', None)]

print(f"\nTotal leads únicos (por email): {len(unique_leads)}")
print(f"  - Con direcciones específicas (no genéricas): {len(unique_specific)}")
print(f"  - Con direcciones genéricas: {len(unique_generic)}")
print(f"  - Leads recomendados (específicos + verificados): {len(good_leads)}")

print("\n" + "="*80)
print("SUGERENCIAS DE ELIMINACIÓN/BLOQUEO")
print("="*80)

# Suggestions
print("\n🔴 PRIORIDAD ALTA — Eliminar/Blquear (genéricas + alto riesgo de rebote):\n")
for e in generic_emails:
    company = e['company']
    email = e['email']
    verified = e.get('verified', 'unknown')
    batch = e['_batch']
    print(f"  • {email} ({company}) — {verified} — batch: {batch}")

print("\n🟡 PRIORIDAD MEDIA — Leads sin MX (no verificados, probablemente reboten):\n")
no_mx_leads = [l for l in unique_leads if l.get('verified') in ('no_mx', 'risky', 'failed')]
for e in no_mx_leads:
    company = e['company']
    email = e['email']
    reason = e.get('verified_reason', 'N/A')
    print(f"  • {email} ({company}) — razón: {reason}")

print("\n🟢 RECOMENDADOS — Leads únicos con email específico y verificado:\n")
for e in sorted(good_leads, key=lambda x: x['email']):
    print(f"  ✅ {e['email']} — {e['company']} (type: {e.get('type','?')})")

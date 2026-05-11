#!/usr/bin/env python3
"""generate.py — Dashboard generator. Reads data/*.json, writes index.html"""
import json, os

DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(name):
    with open(os.path.join(DIR, "data", name)) as f:
        return json.load(f)

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def js(v):
    return json.JSONEncoder(indent=None, separators=(",",":")).encode(v)

def generate():
    projects = load_json("projects.json")
    changelog = load_json("changelog.json")
    leads_data = load_json("leads.json")
    health = load_json("health.json")
    templates_data = load_json("templates.json")

    # Process leads
    all_dates = sorted(leads_data.get("leads_by_date",{}).keys(), reverse=True)[:14]
    all_leads = [l for d in all_dates for l in leads_data["leads_by_date"][d]]
    seen = set(); unique = []
    for l in all_leads:
        if l["email"] not in seen:
            seen.add(l["email"]); unique.append(l)

    log_entries = changelog.get("entries",[])[:20]

    biz_list = []
    for p in projects["projects"]:
        biz_list.append({
            "id": p["id"], "name": p["name"], "emoji": p["emoji"],
            "status": p["status"], "description": p["description"],
            "url": p.get("url",""), "metrics": p.get("metrics",{}),
            "notes": p.get("notes",""), "next_steps": p.get("next_steps",[])
        })

    site_items = []
    for s in health.get("sites",[]):
        site_items.append({
            "name": s["name"], "url": s["url"], "status": s["status"],
            "uptime": s.get("uptime_24h","-"),
            "seo": s.get("seo_metrics",{}),
            "score": s.get("seo_score")
        })

    agents = [
        {"id":"seo","icon":"🔍","name":"SEO Agent","status":"Activo","last":"Today 07:00","jobs":"12","uptime":"99%"},
        {"id":"leads","icon":"🎯","name":"Lead Finder","status":"Activo","last":"Today 11:39","jobs":"22","uptime":"100%"},
        {"id":"outreach","icon":"📧","name":"Outreach Agent","status":"Activo","last":"Today 08:00","jobs":"7","uptime":"-"},
        {"id":"content","icon":"📝","name":"Content Writer","status":"Activo","last":"Today 06:30","jobs":"8","uptime":"98%"},
        {"id":"health","icon":"🔌","name":"Health Monitor","status":"Activo","last":"Today 11:39","jobs":"48","uptime":"100%"},
    ]

    TYPE_LABELS = {"builder":"Builders","constructora":"Constructoras","real_estate":"Real Estate","property_mgmt":"Property Managers","strata":"Strata","other":"Other"}
    BIZ_TARGET = {"builder":"antoniopaving","constructora":"antoniopaving","real_estate":"primeproperty","property_mgmt":"primeproperty","strata":"primeproperty"}
    BIZ_COLORS = {"antoniopaving":"#dc2626","primeproperty":"#2563eb"}
    BIZ_NAMES = {"antoniopaving":"Antonio Paving","primeproperty":"Prime Property"}
    BIZ_EMOJIS = {"antoniopaving":"🏗️","primeproperty":"🏢"}

    # Build JS data injection as a simple string (NOT f-string to avoid brace issues)
    JS_DATA_BLOCK = '<script>\n'
    JS_DATA_BLOCK += 'var LEADS = ' + js(unique) + ';\n'
    JS_DATA_BLOCK += 'var TEMPLATES = ' + js(templates_data.get("templates",[])) + ';\n'
    JS_DATA_BLOCK += 'var BIZ_DATA = ' + js(biz_list) + ';\n'
    JS_DATA_BLOCK += 'var SITES_DATA = ' + js(site_items) + ';\n'
    JS_DATA_BLOCK += 'var AGENTS_DATA = ' + js(agents) + ';\n'
    JS_DATA_BLOCK += 'var LOG_DATA = ' + js(log_entries) + ';\n'
    JS_DATA_BLOCK += 'var TYPE_LABELS = ' + js(TYPE_LABELS) + ';\n'
    JS_DATA_BLOCK += 'var BIZ_TARGET = ' + js(BIZ_TARGET) + ';\n'
    JS_DATA_BLOCK += 'var BIZ_COLORS = ' + js(BIZ_COLORS) + ';\n'
    JS_DATA_BLOCK += 'var BIZ_NAMES = ' + js(BIZ_NAMES) + ';\n'
    JS_DATA_BLOCK += 'var BIZ_EMOJIS = ' + js(BIZ_EMOJIS) + ';\n'
    JS_DATA_BLOCK += 'var TRADING_DATA = ' + js(health.get("trading",{})) + ';\n'
    JS_DATA_BLOCK += 'var UPDATED = ' + js(health.get("updated","")) + ';\n'
    JS_DATA_BLOCK += '// ── End injected data ──\n'

    # Read template and inject data
    with open(os.path.join(DIR, "template.html")) as f:
        html = f.read()

    # Use a unique marker instead of fragile string matching
    marker = '<!-- DATA_INJECTION_POINT -->'
    if marker in html:
        # Write data to external file instead
        data_path = os.path.join(DIR, "data.js")
        with open(data_path, "w") as df:
            df.write(JS_DATA_BLOCK)
        html = html.replace(marker, '<script src="data.js"></script>')
    else:
        # Fallback: write to data.js
        data_path = os.path.join(DIR, "data.js")
        with open(data_path, "w") as df:
            df.write(JS_DATA_BLOCK)

    path = os.path.join(DIR, "index.html")
    with open(path, "w") as f:
        f.write(html)

    # Count stats
    total_leads = len(unique)
    emailed = sum(1 for l in unique if l.get("contacted"))
    print(f"✅ Dashboard generated: {total_leads} leads, {emailed} contacted")
    print(f"   {len(biz_list)} businesses, {len(site_items)} sites, {len(agents)} agents")

if __name__ == "__main__":
    generate()

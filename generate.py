#!/usr/bin/env python3
"""generate.py — Hermes Business OS"""

import json, os
from datetime import datetime, date

DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(name):
    with open(os.path.join(DIR, "data", name)) as f:
        return json.load(f)

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def generate():
    projects = load_json("projects.json")
    changelog = load_json("changelog.json")
    leads_data = load_json("leads.json")
    health = load_json("health.json")
    ideas_data = load_json("ideas.json")
    templates = load_json("templates.json") if os.path.exists(os.path.join(DIR, "data", "templates.json")) else {"templates":[]}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_str = date.today().isoformat()

    total_projects = len(projects["projects"])
    activos = sum(1 for p in projects["projects"] if p["status"] == "activo")
    total_leads = leads_data.get("total_leads", 0)
    sites_online = sum(1 for s in health["sites"] if s["status"] == "online")
    sites_total = len(health["sites"])

    # ── Business target mapping ──
    BIZ_TARGET = {
        "builder": "antoniopaving",
        "constructora": "antoniopaving",
        "real_estate": "primeproperty",
        "property_mgmt": "primeproperty",
        "strata": "primeproperty",
    }
    BIZ_NAMES = {
        "antoniopaving": {"name": "Antonio Paving", "emoji": "🏗️", "color": "#dc2626"},
        "primeproperty": {"name": "Prime Property Maintenance", "emoji": "🏢", "color": "#2563eb"},
    }

    def get_biz(lead_type):
        return BIZ_TARGET.get(lead_type, "primeproperty")

    # ── Projects / Businesses ──
    biz_cards = ""
    for p in projects["projects"]:
        sc = {"activo":"#34d399","pendiente":"#fbbf24","idea":"#888","completado":"#60a5fa"}.get(p["status"],"#888")
        metrics = "".join('<div class="m"><span class="ml">%s</span><span class="mv">%s</span></div>' % (esc(k.replace("_"," ").title()), esc(v)) for k,v in p.get("metrics",{}).items())
        steps = "".join('<li class="%s">%s %s</li>' % ("d" if i<1 else "", "&#x2705;" if i<1 else "&#x25CB;", esc(s)) for i,s in enumerate(p.get("next_steps",[])))
        link = '<a href="%s" target="_blank" class="pl">%s</a>' % (esc(p["url"]), esc(p["url"])) if p.get("url") else ""
        notes = '<div class="nt">&#x1F4DD; %s</div>' % esc(p["notes"]) if p.get("notes") else ""
        mg = '<div class="mg">%s</div>' % metrics if metrics else ""
        st = '<ul class="st">%s</ul>' % steps if steps else ""
        biz_cards += '<div class="bc" style="--a:%s"><div class="bch"><span class="be">%s</span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><p class="bd">%s</p>%s%s%s%s</div>' % (sc, p['emoji'], esc(p['name']), sc, p['status'].upper(), esc(p['description']), link, mg, st, notes)

    # ── Leads data ──
    all_dates = sorted(leads_data.get("leads_by_date",{}).keys(), reverse=True)[:14]
    all_leads = [l for d in all_dates for l in leads_data["leads_by_date"][d]]
    seen = set()
    unique = []
    for l in all_leads:
        if l["email"] not in seen:
            seen.add(l["email"]); unique.append(l)
    today_leads = leads_data.get("leads_by_date",{}).get(today_str,[])

    groups = {"builder":[],"constructora":[],"real_estate":[],"property_mgmt":[],"strata":[],"other":[]}
    for l in unique:
        t = l.get("type","other")
        if t not in groups: t = "other"
        groups[t].append(l)

    def verify_badge(status):
        return {'verified':'&#x2705;','risky':'&#x26A0;&#xFE0F;','invalid':'&#x274C;'}.get(status,'&#x2753;')

    def elist(leads, label):
        if not leads:
            return '<div class="eg"><div class="egh"><span class="egl">%s</span><span class="egc">0</span></div><p class="egm">Sin emails</p></div>' % label
        # Determine the business for this group
        first_type = leads[0].get("type", "other")
        biz = get_biz(first_type)
        biz_info = BIZ_NAMES.get(biz, BIZ_NAMES["primeproperty"])
        entries = []
        for l in leads:
            e = (
                '<div class="ei" id="e-%s">'
                '<span class="eic">%s</span>'
                '<span class="eie">%s <span class="evb">%s</span></span>'
                '<span class="ein">%s</span>'
                '<span class="eibb"><span class="eb-badge" style="background:%s">%s</span></span>'
                '<button class="eb eb-gm" onclick="gm(\'%s\',\'%s\',\'%s\')">&#x1F4E7; Enviar</button>'
                '<button class="eb eb-sm" onclick="mc(\'%s\')">&#x2705; Hecho</button></div>'
                % (esc(l["email"]),
                   esc(l["company"]),
                   esc(l["email"]),
                   verify_badge(l.get("verified","")),
                   esc(l.get("notes","")),
                   biz_info["color"],
                   esc(biz_info["emoji"] + " " + biz_info["name"]),
                   esc(l["email"]),
                   esc(biz),
                   esc(l["company"]),
                   esc(l["email"]))
            )
            entries.append(e)
        entries = "".join(entries)
        text = "; ".join(l["email"] for l in leads).replace("'","\\'")
        n = len(leads)
        verified_count = sum(1 for l in leads if l.get("verified") == "verified")
        # Get template subject for this group
        tmpl_subj = templates.get("templates", [])
        t_subj = ""
        for t in tmpl_subj:
            if t["id"] == biz:
                t_subj = t.get("subject", "")
                break
        return '<div class="eg"><div class="egh"><span class="egl">%s</span><span class="egc">%d</span><span class="egv"> &#x2705;%d</span><button class="eb" onclick="ec(\'%s\',%d)">&#x1F4CB; Copiar</button><button class="eb eb-tmpl" onclick="ct(\'%s\')">&#x1F4CB; Copiar Template</button><button class="eb eb-tmpl" onclick="tp(\'%s\')">&#x1F4DD; Ver Template</button></div><div class="eil">%s</div></div>' % (label, n, verified_count, text, n, biz, biz, entries)

    # ── Business Targeting Section ──
    biz_section = '<div class="eg"><div class="egh"><span class="egl">&#x1F3AF; ¿Quién contacta a quién?</span></div><div style="padding:10px 12px;font-size:.82em;color:var(--t2)">'
    biz_section += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'
    for bid, info in BIZ_NAMES.items():
        types = [k for k, v in BIZ_TARGET.items() if v == bid]
        type_labels = {"builder": "🔨 Builders", "constructora": "🏗️ Constructoras", "real_estate": "🏢 Real Estate", "property_mgmt": "📋 Property Mgmt", "strata": "🏠 Strata"}
        type_list = ", ".join(type_labels.get(t, t) for t in types)
        biz_section += '<div style="background:var(--c2);border-radius:8px;padding:10px;border-left:3px solid %s">' % info["color"]
        biz_section += '<div style="font-weight:600;font-size:.9em">%s %s</div>' % (info["emoji"], info["name"])
        biz_section += '<div style="margin-top:4px;font-size:.8em">Contácta: %s</div>' % type_list
        biz_section += '<div style="margin-top:3px"><a href="https://%s" target="_blank" style="color:#818cf8;font-size:.78em;text-decoration:none">%s</a></div>' % (info["name"].lower().replace(" ","")+".com.au" if "paving" in info["name"].lower() else "primepropertymaintenance.au", info["name"].lower().replace(" ","")+".com.au" if "paving" in info["name"].lower() else "primepropertymaintenance.au")
        biz_section += '</div>'
    biz_section += '</div></div></div>'

    outreach = biz_section
    if today_leads:
        outreach += elist(today_leads, "HOY - Leads frescos")
    for key, emoji in [("constructora","Constructoras"),("builder","Builders"),("real_estate","Real Estate"),("property_mgmt","Property Managers"),("strata","Strata"),("other","Otros")]:
        outreach += elist(groups.get(key,[]), emoji)

    all_text = "; ".join(l["email"] for l in unique).replace("'","\\'")
    all_count = len(unique)

    # ── Site Health ──
    health_cards = ""
    for site in health.get("sites",[]):
        up = site["status"] == "online"
        clr = "#34d399" if up else "#ef4444"
        seo = ""
        if site.get("seo_metrics"):
            items = "".join('<div class="m"><span class="ml">%s</span><span class="mv">%s</span></div>' % (esc(k.replace("_"," ").title()), esc(v)) for k,v in site["seo_metrics"].items())
            seo = '<div class="mg">%s</div>' % items
        health_cards += '<div class="sc" style="--a:%s"><div class="sch"><span class="sd" style="background:%s"></span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><div class="shm"><a href="%s" target="_blank" class="pl">%s</a><span>&#x23F1;&#xFE0F; %s</span><span>&#x1F550; %s</span></div>%s</div>' % (clr, clr, esc(site["name"]), clr, "ONLINE" if up else "OFFLINE", esc(site["url"]), esc(site["url"]), esc(site.get("uptime_24h","?")), esc(site.get("last_checked","")), seo)

    # ── Ideas ──
    pots = {"Alto":"#34d399","Muy Alto":"#60a5fa","Medio":"#fbbf24","Bajo":"#888"}
    idea_cards = ""
    for idea in ideas_data.get("ideas",[]):
        pc = pots.get(idea.get("potential",""),"#888")
        notes = '<div class="nt">&#x1F4AD; %s</div>' % esc(idea["notes"]) if idea.get("notes") else ""
        idea_cards += '<div class="ic" style="--a:#7c3aed"><div class="ich"><span>%s</span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><p class="id">%s</p><div class="ih"><span>&#x23F1;&#xFE0F; %s</span><span>&#x1F527; %s</span></div>%s</div>' % (idea["emoji"], esc(idea["name"]), pc, esc(idea.get("potential","")), esc(idea["description"]), esc(idea.get("timeline","?")), esc(idea.get("effort","?")), notes)

    # ── Changelog ──
    em = {"mejora":"&#x1F527;","creacion":"&#x2728;","infra":"&#x2699;&#xFE0F;","analisis":"&#x1F4CA;","idea":"&#x1F4A1;"}
    log_html = "".join('<div class="le"><span class="ld">%s</span><span>%s</span><span class="lp">[%s]</span><span class="ltx">%s</span></div>' % (esc(e["date"]), em.get(e["type"],"&#x1F4CC;"), esc(e["project"]), esc(e["text"])) for e in changelog["entries"][:20])

    # ── AI Agents ──
    agents = [
        ("seo","&#x1F50D;","SEO Agent","Activo","Hoy 07:00","12","99&#x25;"),
        ("leads","&#x1F3AF;","Lead Finder","Activo","Hoy 11:39","22","100&#x25;"),
        ("outreach","&#x1F4E7;","Outreach Agent","Pausado","Ayer","0","-"),
        ("content","&#x1F4DD;","Content Writer","Activo","Hoy 06:30","8","98&#x25;"),
        ("health","&#x1F50C;","Health Monitor","Activo","Hoy 11:39","48","100&#x25;"),
    ]
    agents_html = "".join('<div class="ac"><div class="ach"><span class="ae">%s</span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><div class="ag"><div><span class="agl">Ultima ejecucion</span><span class="agv">%s</span></div><div><span class="agl">Trabajos</span><span class="agv">%s</span></div><div><span class="agl">Uptime</span><span class="agv">%s</span></div></div></div>' % (a[1], a[2], "#34d399" if a[3]=="Activo" else "#fbbf24", a[3], a[4], a[5], a[6]) for a in agents)
    n_active = sum(1 for a in agents if a[3]=="Activo")

    pct_online = "%d%%" % (sites_online*100//sites_total) if sites_total else "0%"
    site_color = "#34d399" if sites_online==sites_total else "#ef4444"

    # Build HTML by parts - no % template conflicts
    html_parts = []

    # CSS
    html_parts.append('''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Hermes OS</title>
<style>
:root{--bg:#0a0a0f;--fg:#e4e4e7;--c1:#111118;--c2:#1c1c24;--c3:#27272a;--t2:#71717a;--t3:#52525b;--ac:#6366f1;--gr:#34d399;--rd:#ef4444}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--fg);min-height:100vh;display:flex}
::selection{background:var(--ac);color:#fff}
.sb{width:200px;min-width:200px;background:#0d0d14;border-right:1px solid var(--c2);padding:12px 0;height:100vh;position:sticky;top:0;overflow-y:auto;display:flex;flex-direction:column}
.sb-l{padding:8px 14px 16px;font-size:.9em;font-weight:700;background:linear-gradient(135deg,var(--fg),#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;border-bottom:1px solid var(--c2);margin-bottom:6px}
.sb-l small{display:block;font-size:.6em;color:var(--t2);-webkit-text-fill-color:var(--t2);font-weight:400;margin-top:2px}
.sb-g{padding:2px 0}
.sb-gl{padding:4px 14px;font-size:.6em;color:var(--t3);text-transform:uppercase;letter-spacing:1px;font-weight:600}
.sb-b{display:flex;align-items:center;gap:7px;padding:7px 14px;font-size:.8em;color:var(--t2);cursor:pointer;transition:all .12s;border:none;background:none;width:100%;text-align:left;font-family:inherit}
.sb-b:hover{background:#14141e;color:var(--fg)}
.sb-b.on{background:#1e1e2a;color:var(--fg);border-right:2px solid var(--ac)}
.sb-b .sbc{margin-left:auto;background:var(--c2);border-radius:8px;padding:0 6px;font-size:.7em;color:var(--t2)}
.sb-b.on .sbc{background:var(--ac);color:#fff}
.sb-sp{flex:1}
.sb-ft{padding:10px 14px;font-size:.65em;color:var(--t3);border-top:1px solid var(--c2)}
.mn{flex:1;max-width:calc(100vw - 200px);overflow-y:auto;height:100vh}
.c{max-width:900px;margin:0 auto;padding:20px}
.sm{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 16px}
.sp{background:var(--c1);border:1px solid var(--c2);border-radius:14px;padding:4px 11px;font-size:.72em;color:var(--t2);display:flex;align-items:center;gap:4px}
.sp b{color:var(--fg)}
.pn{display:none}
.pn.on{display:block}
.ph{font-size:1.2em;font-weight:600;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.ph small{font-size:.6em;color:var(--t2);font-weight:400}
.dg{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:16px}
.dc{background:var(--c1);border:1px solid var(--c2);border-radius:12px;padding:14px;text-align:center}
.dc .dn{font-size:.75em;color:var(--t2)}
.dc .dv{font-size:1.5em;font-weight:700;color:var(--fg);margin:4px 0}
.dc .ds{font-size:.65em;color:var(--t3)}
.btn{display:inline-flex;align-items:center;gap:4px;background:var(--c2);border:1px solid var(--c3);color:var(--t2);padding:5px 12px;border-radius:8px;font-size:.75em;cursor:pointer;transition:all .15s;font-family:inherit}
.btn:hover{background:var(--c3);border-color:#3f3f46;color:var(--fg)}
.btn-p{background:var(--ac);border-color:var(--ac);color:#fff}
.btn-p:hover{background:#818cf8;border-color:#818cf8}
.bc{background:var(--c1);border-radius:12px;padding:16px;border:1px solid var(--c2);margin-bottom:10px;border-left:3px solid var(--a)}
.bc:hover{border-color:var(--c3)}
.bch{display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap}
.bch h3{font-size:1em;font-weight:600}
.be{font-size:1.3em}
.bd{color:var(--t2);font-size:.84em;margin:3px 0 6px;line-height:1.5}
.bg{font-size:.58em;padding:2px 10px;border-radius:10px;color:#fff;font-weight:600;letter-spacing:.4px;white-space:nowrap}
.st{list-style:none;padding:0;margin-top:5px}
.st li{padding:2px 0;font-size:.82em;color:var(--t2)}
.st li.d{color:var(--fg)}
.nt{background:#0d0d14;border-radius:7px;padding:7px 9px;font-size:.8em;color:var(--t2);margin-top:6px}
.pl{color:#818cf8;font-size:.78em;text-decoration:none;display:inline-block;margin:3px 0}
.pl:hover{text-decoration:underline}
.mg{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:5px;margin:8px 0}
.m{background:#0d0d14;border-radius:7px;padding:7px;text-align:center}
.ml{display:block;font-size:.58em;color:var(--t2);text-transform:uppercase;letter-spacing:.3px}
.mv{display:block;font-size:.92em;color:#a78bfa;font-weight:600;margin-top:1px}
.eg{background:var(--c1);border:1px solid var(--c2);border-radius:10px;margin-bottom:10px;overflow:hidden}
.egh{display:flex;align-items:center;gap:8px;padding:10px 12px;border-bottom:1px solid var(--c2);flex-wrap:wrap}
.egl{font-weight:600;font-size:.85em;flex:1}
.egc{background:var(--c2);border-radius:8px;padding:0 7px;font-size:.72em;color:var(--t2)}
.eb{background:var(--c2);border:1px solid var(--c3);border-radius:6px;padding:3px 9px;font-size:.7em;color:var(--t2);cursor:pointer;font-family:inherit}
.eb:hover{background:var(--c3);color:var(--fg)}
.egm{padding:14px;font-size:.82em;color:var(--t2);text-align:center}
.eil{max-height:220px;overflow-y:auto}
.ei{display:flex;gap:6px;padding:5px 12px;border-bottom:1px solid #0d0d14;font-size:.78em;flex-wrap:wrap;align-items:center}
.ei:last-child{border:none}
.eic{color:var(--fg);font-weight:500;min-width:100px}
.eie{color:#818cf8;display:inline-flex;align-items:center;gap:4px}
.evb{font-size:1.1em;cursor:help}
.eb-sm{font-size:.7em;padding:1px 6px;margin-left:auto;background:var(--c2)}
.sc{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:14px;margin-bottom:8px;border-left:3px solid var(--a)}
.sch{display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap}
.sch h3{font-size:.9em;font-weight:600}
.sd{width:7px;height:7px;border-radius:50%;display:inline-block;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.shm{display:flex;gap:10px;flex-wrap:wrap;font-size:.72em;color:var(--t2);margin:5px 0 6px}
.shm a{color:#818cf8;text-decoration:none}
.ic{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:14px;margin-bottom:8px;border-left:3px solid var(--a)}
.ich{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.ich h3{font-size:.9em;font-weight:600;flex:1}
.id{color:var(--t2);font-size:.82em;margin:4px 0 6px;line-height:1.5}
.ih{display:flex;gap:10px;font-size:.72em;color:var(--t2);flex-wrap:wrap}
.ac{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:14px;margin-bottom:8px}
.ach{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.ach h3{font-size:.9em;font-weight:600;flex:1}
.ae{font-size:1.1em}
.ag{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.agl{display:block;font-size:.6em;color:var(--t2);text-transform:uppercase;letter-spacing:.3px}
.agv{display:block;font-size:.85em;color:var(--t2);margin-top:1px}
.tc{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.tcol{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:10px;min-height:200px}
.tcol h4{font-size:.8em;color:var(--t2);margin-bottom:8px;text-transform:uppercase;letter-spacing:.4px}
.ti{background:#0d0d14;border:1px solid var(--c2);border-radius:6px;padding:7px 9px;margin-bottom:5px;font-size:.78em;cursor:pointer}
.ti:hover{border-color:var(--c3)}
.addt{background:none;border:1px dashed var(--c3);border-radius:6px;padding:6px;font-size:.75em;color:var(--t3);cursor:pointer;width:100%;font-family:inherit;text-align:center}
.addt:hover{border-color:#3f3f46;color:var(--t2)}
.le{display:flex;align-items:flex-start;gap:5px;padding:5px 0;border-bottom:1px solid #0d0d14;font-size:.8em;flex-wrap:wrap}
.ld{color:var(--t3);font-size:.85em;white-space:nowrap;min-width:65px}
.lp{color:#7c3aed;flex-shrink:0;font-size:.85em}
.ltx{color:var(--t2);flex:1}
.nts{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:14px;min-height:200px}
.nts textarea{width:100%;min-height:180px;background:#0d0d14;border:1px solid var(--c2);border-radius:8px;color:var(--fg);padding:10px;font-size:.82em;font-family:inherit;resize:vertical}
.nts textarea:focus{outline:none;border-color:var(--ac)}
#to{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(70px);background:var(--gr);color:#fff;padding:9px 18px;border-radius:10px;font-size:.82em;opacity:0;transition:all .3s;pointer-events:none;z-index:999}
#to.sh{opacity:1;transform:translateX(-50%) translateY(0)}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:#0d0d14}
::-webkit-scrollbar-thumb{background:var(--c3);border-radius:3px}
.eibb{display:inline-flex;align-items:center;gap:3px}
.eb-badge{display:inline-block;font-size:.6em;padding:1px 6px;border-radius:8px;color:#fff;font-weight:600;white-space:nowrap}
.eb-gm{background:#2563eb;border-color:#2563eb;color:#fff;font-size:.72em;padding:2px 8px}
.eb-gm:hover{background:#3b82f6;border-color:#3b82f6;color:#fff}
.eb-tmpl{background:#7c3aed;border-color:#7c3aed;color:#fff}
.eb-tmpl:hover{background:#8b5cf6;border-color:#8b5cf6;color:#fff}
/* ── Template Preview Overlay ── */
#tmo{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);z-index:1000;display:none;align-items:center;justify-content:center}
#tmo.sh{display:flex}
#tmp{background:var(--c1);border:1px solid var(--c2);border-radius:14px;max-width:560px;width:90%;max-height:80vh;overflow-y:auto;padding:0}
#tmh{display:flex;align-items:center;padding:14px 16px;border-bottom:1px solid var(--c2);gap:8px}
#tmh h3{flex:1;font-size:.95em;font-weight:600}
#tmx{background:none;border:none;color:var(--t2);font-size:1.2em;cursor:pointer;padding:0 4px;font-family:inherit}
#tmx:hover{color:var(--fg)}
#tmb{padding:14px 16px;font-size:.82em;color:var(--t2);line-height:1.6;white-space:pre-wrap;font-family:inherit}
#tmf{padding:10px 16px 14px;display:flex;gap:8px;flex-wrap:wrap;border-top:1px solid var(--c2)}
#tmf .eb{font-size:.75em}
@media(max-width:700px){
body{flex-direction:column}
.sb{width:100%;min-width:100%;height:auto;position:relative;flex-direction:row;flex-wrap:wrap;padding:6px;border:none;border-bottom:1px solid var(--c2)}
.sb-l{padding:4px 8px;border:none;margin:0;font-size:.8em}
.sb-l small{display:inline;margin-left:4px}
.sb-g{display:flex;flex-wrap:wrap;padding:0}
.sb-gl{display:none}
.sb-b{padding:4px 8px;font-size:.72em;width:auto;border-radius:6px}
.sb-b.on{border-right:none;background:#1e1e2a}
.sb-sp{display:none}
.sb-ft{display:none}
.mn{max-width:100%;height:auto}
.c{padding:10px}
.tc{grid-template-columns:repeat(2,1fr)}
}
</style>
</head>
<body>
''')

    # Sidebar
    html_parts.append('<nav class="sb">')
    html_parts.append('<div class="sb-l">&#x29E7; Hermes OS <small>v2.0</small></div>')
    html_parts.append('<div class="sb-g"><div class="sb-gl">General</div>')
    html_parts.append('<button class="sb-b on" data-pn="dashboard">&#x1F4CA; Dashboard</button>')
    html_parts.append('<button class="sb-b" data-pn="businesses">&#x1F3E2; Negocios</button>')
    html_parts.append('<button class="sb-b" data-pn="outreach">&#x1F4E7; Outreach <span class="sbc">%d</span></button>' % all_count)
    html_parts.append('<button class="sb-b" data-pn="sites">&#x1F50D; Sitios</button>')
    html_parts.append('</div><div class="sb-g"><div class="sb-gl">Operaciones</div>')
    html_parts.append('<button class="sb-b" data-pn="tasks">&#x2705; Tareas</button>')
    html_parts.append('<button class="sb-b" data-pn="agents">&#x1F916; Agentes IA</button>')
    html_parts.append('<button class="sb-b" data-pn="ideas">&#x1F4A1; Ideas</button>')
    html_parts.append('<button class="sb-b" data-pn="notes">&#x1F4DD; Notas</button>')
    html_parts.append('</div><div class="sb-g"><div class="sb-gl">Historial</div>')
    html_parts.append('<button class="sb-b" data-pn="changelog">&#x1F4DC; Cambios</button>')
    html_parts.append('</div>')
    html_parts.append('<div class="sb-sp"></div>')
    html_parts.append('<div class="sb-ft">Actualizado: %s</div>' % now.split()[1])
    html_parts.append('</nav>')

    # Main
    html_parts.append('<main class="mn"><div class="c">')

    # Dashboard panel
    html_parts.append('<div class="pn on" id="pn-dashboard">')
    html_parts.append('<div class="ph">&#x1F4CA; Dashboard</div>')
    html_parts.append('<div class="sm">')
    html_parts.append('<span class="sp">&#x1F4CA; <b>%d</b> negocios</span>' % total_projects)
    html_parts.append('<span class="sp">&#x2705; <b>%d</b> activos</span>' % activos)
    html_parts.append('<span class="sp" style="border-color:var(--ac)">&#x1F3AF; <b>%d</b> leads</span>' % total_leads)
    html_parts.append('<span class="sp" style="border-color:%s">&#x1F50D; <b>%d/%d</b> sitios online</span>' % (site_color, sites_online, sites_total))
    html_parts.append('<span class="sp">&#x1F916; <b>%d</b> agentes</span>' % len(agents))
    html_parts.append('</div>')
    html_parts.append('<div class="dg">')
    html_parts.append('<div class="dc"><div class="dn">Leads Totales</div><div class="dv">%d</div><div class="ds">En %d dias</div></div>' % (total_leads, len(all_dates)))
    html_parts.append('<div class="dc"><div class="dn">Emails Unicos</div><div class="dv">%d</div><div class="ds">Para outreach</div></div>' % all_count)
    html_parts.append('<div class="dc"><div class="dn">Sitios Online</div><div class="dv">%d/%d</div><div class="ds">%s</div></div>' % (sites_online, sites_total, pct_online))
    html_parts.append('<div class="dc"><div class="dn">Agentes Activos</div><div class="dv">%d</div><div class="ds">de %d</div></div>' % (n_active, len(agents)))
    html_parts.append('</div>')
    html_parts.append('<div class="ph" style="font-size:.95em;margin-top:4px">&#x1F3E2; Negocios Activos</div>')
    html_parts.append(biz_cards)
    html_parts.append('</div>')

    # Businesses panel
    html_parts.append('<div class="pn" id="pn-businesses">')
    html_parts.append('<div class="ph">&#x1F3E2; Negocios <small>Todos los proyectos activos</small></div>')
    html_parts.append(biz_cards)
    html_parts.append('</div>')

    # Outreach panel
    html_parts.append('<div class="pn" id="pn-outreach">')
    html_parts.append('<div class="ph">&#x1F4E7; Outreach <small>%d emails unicos</small></div>' % all_count)
    html_parts.append('<div style="margin-bottom:12px"><button class="btn btn-p" onclick="ec(\'%s\',%d)">&#x1F4CB; Copiar TODOS (%d)</button></div>' % (all_text, all_count, all_count))
    html_parts.append(outreach)
    html_parts.append('</div>')

    # Sites panel
    html_parts.append('<div class="pn" id="pn-sites">')
    html_parts.append('<div class="ph">&#x1F50D; Sitios Web <small>Salud y SEO</small></div>')
    html_parts.append('<div class="sm"><span class="sp" style="border-color:%s">%d/%d online</span></div>' % (site_color, sites_online, sites_total))
    html_parts.append(health_cards)
    html_parts.append('</div>')

    # Tasks panel
    html_parts.append('<div class="pn" id="pn-tasks">')
    html_parts.append('<div class="ph">&#x2705; Tareas</div>')
    html_parts.append('<div class="tc">')
    html_parts.append('<div class="tcol" data-col="today"><h4>&#x1F534; Hoy</h4><div class="tl"></div><button class="addt" onclick="at(\'today\')">+ Anadir</button></div>')
    html_parts.append('<div class="tcol" data-col="urgent"><h4>&#x1F7E1; Urgente</h4><div class="tl"></div><button class="addt" onclick="at(\'urgent\')">+ Anadir</button></div>')
    html_parts.append('<div class="tcol" data-col="week"><h4>&#x1F535; Esta Semana</h4><div class="tl"></div><button class="addt" onclick="at(\'week\')">+ Anadir</button></div>')
    html_parts.append('<div class="tcol" data-col="done"><h4>&#x2705; Completadas</h4><div class="tl"></div></div>')
    html_parts.append('</div></div>')

    # Agents panel
    html_parts.append('<div class="pn" id="pn-agents">')
    html_parts.append('<div class="ph">&#x1F916; Agentes IA <small>Automatizaciones activas</small></div>')
    html_parts.append(agents_html)
    html_parts.append('</div>')

    # Ideas panel
    html_parts.append('<div class="pn" id="pn-ideas">')
    html_parts.append('<div class="ph">&#x1F4A1; Ideas de Negocio</div>')
    html_parts.append(idea_cards)
    html_parts.append('</div>')

    # Notes panel
    html_parts.append('<div class="pn" id="pn-notes">')
    html_parts.append('<div class="ph">&#x1F4DD; Notas Rapidas</div>')
    html_parts.append('<div class="nts"><textarea id="na" placeholder="Escribe tus notas aqui... Se guardan automaticamente."></textarea>')
    html_parts.append('<button class="btn" onclick="sn()">&#x1F4BE; Guardar</button>')
    html_parts.append('<span style="font-size:.72em;color:var(--t2);margin-left:8px" id="ns"></span>')
    html_parts.append('</div></div>')

    # Changelog panel
    html_parts.append('<div class="pn" id="pn-changelog">')
    html_parts.append('<div class="ph">&#x1F4DC; Ultimos Cambios</div>')
    html_parts.append(log_html)
    html_parts.append('</div>')

    html_parts.append('</div></main>')

    # ── Toast + Script (main JS) ──
    html_parts.append('''<div id="to"></div>
<script>
var sb=document.querySelectorAll('.sb-b');
sb.forEach(function(b){b.addEventListener('click',function(){
sb.forEach(function(x){x.classList.remove('on')});
document.querySelectorAll('.pn').forEach(function(x){x.classList.remove('on')});
b.classList.add('on');
var p=document.getElementById('pn-'+b.getAttribute('data-pn'));
if(p)p.classList.add('on');
try{localStorage.setItem('hpan',b.getAttribute('data-pn'))}catch(e){}
})});
try{var lp=localStorage.getItem('hpan');if(lp){var b=document.querySelector('.sb-b[data-pn="'+lp+'"]');if(b)b.click()}}catch(e){}

function toast(m){var t=document.getElementById('to');t.textContent=m;t.classList.add('sh');clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('sh')},2500)}

function ec(t,c){
if(navigator.clipboard&&navigator.clipboard.writeText){
navigator.clipboard.writeText(t).then(function(){toast('\\u2705 '+c+' emails copiados')}).catch(function(){fb(t)})
}else{fb(t)}
}
function fb(t){var ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');toast('\\u2705 Copiado')}catch(e){toast('\\u274c Error')}document.body.removeChild(ta)}

// Lead contact tracking (localStorage)
function cm(){try{return JSON.parse(localStorage.getItem('contacted')||'{}')}catch(e){return{}}}
function mc(email){
var m=cm();m[email]=new Date().toISOString().slice(0,10);
try{localStorage.setItem('contacted',JSON.stringify(m))}catch(e){}
var el=document.getElementById('e-'+email);
if(el){el.style.opacity='0.5';el.querySelector('.eb-sm').textContent='\\u2705 Enviado'}
toast('\\u2705 Marcado como contactado')
}
// Hide already contacted on load
(function(){
var m=cm();Object.keys(m).forEach(function(email){
var el=document.getElementById('e-'+email);
if(el){el.style.opacity='0.5';var btn=el.querySelector('.eb-sm');if(btn)btn.textContent='\\u2705 '+m[email]}
})})();

function lt(){try{return JSON.parse(localStorage.getItem('htasks'))||{today:[],urgent:[],week:[],done:[]}}catch(e){return{today:[],urgent:[],week:[],done:[]}}}
function st(d){try{localStorage.setItem('htasks',JSON.stringify(d))}catch(e){}}
function rt(){
var d=lt();['today','urgent','week','done'].forEach(function(c){
var el=document.querySelector('.tcol[data-col="'+c+'"] .tl');if(!el)return;
el.innerHTML=d[c].map(function(t,i){var s=c==='done'?'style="text-decoration:line-through;color:var(--t3)"':'';return '<div class="ti" '+s+' onclick="td(\\''+c+'\\','+i+')">'+t+'</div>'}).join('')})}
function at(col){var t=prompt('Nueva tarea ('+col+'):');if(!t||!t.trim())return;var d=lt();d[col].push(t.trim());st(d);rt()}
function td(col,i){var d=lt();if(col==='done'){d.done.splice(i,1)}else{d.done.push(d[col][i]);d[col].splice(i,1)}st(d);rt();toast('\\u2705 Tarea movida')}
rt();

var ta=document.getElementById('na');
if(ta){try{ta.value=localStorage.getItem('hnotes')||''}catch(e){}}
function sn(){if(!ta)return;try{localStorage.setItem('hnotes',ta.value);document.getElementById('ns').textContent='\\u2705 Guardado'}catch(e){}}
</script>''')

    # ── Email template JS (injected with real data) ──
    tpl_json = json.JSONEncoder(indent=None, separators=(",",":")).encode(templates.get("templates",[]))
    html_parts.append('''<script>
var TEMPLATES = %s;

function gm(e,b,c){
var t=null;for(var i=0;i<TEMPLATES.length;i++){if(TEMPLATES[i].id===b){t=TEMPLATES[i];break}}
if(!t){toast('\\u274c Template no encontrado');return}
var body=t.body.replace('[COMPANY]',c);var subj=t.subject;
var url='https://mail.google.com/mail/?view=cm&fs=1&to='+encodeURIComponent(e)+'&su='+encodeURIComponent(subj)+'&body='+encodeURIComponent(body);
window.open(url,'_blank');toast('\\u2705 Gmail abierto para '+c);}

function ct(b){
var t=null;for(var i=0;i<TEMPLATES.length;i++){if(TEMPLATES[i].id===b){t=TEMPLATES[i];break}}
if(!t){toast('\\u274c Template no encontrado');return}
fb(t.body);toast('\\u2705 Template de '+t.name+' copiado');}

function tp(b){
var t=null;for(var i=0;i<TEMPLATES.length;i++){if(TEMPLATES[i].id===b){t=TEMPLATES[i];break}}
if(!t){toast('\\u274c Template no encontrado');return}
var mo=document.getElementById('tmo');
document.getElementById('tmh').innerHTML='<h3>'+t.emoji+' '+t.name+'</h3><button id="tmx" onclick="tc()">&times;</button>';
document.getElementById('tmb').textContent=t.body;
document.getElementById('tmf').innerHTML='<button class="eb eb-tmpl" onclick="ct(\\''+b+'\\')">\\u{1F4CB} Copiar Template</button><button class="eb eb-gm" onclick="tc();gm(\\'\\',\\''+b+'\\',\\'[COMPANY]\\')">\\u{1F4E7} Abrir en Gmail</button><button class="eb" onclick="tc()">Cerrar</button>';
mo.classList.add('sh');}

function tc(){document.getElementById('tmo').classList.remove('sh')}
</script>
<div id="tmo"><div id="tmp"><div id="tmh"><h3>Template</h3><button id="tmx" onclick="tc()">&times;</button></div><div id="tmb"></div><div id="tmf"><button class="eb" onclick="tc()">Cerrar</button></div></div></div>
</body>
</html>''' % tpl_json)

    html = "\\n".join(html_parts)
    path = os.path.join(DIR, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print("OK: %s (%d bytes)" % (path, len(html)))
    return True

if __name__ == "__main__":
    generate()

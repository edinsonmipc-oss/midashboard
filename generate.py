#!/usr/bin/env python3
"""generate.py — Tradeos: Business OS for Tradies"""

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
    leads_data = load_json("leads.json")
    health = load_json("health.json")
    ideas = load_json("ideas.json")
    changelog = load_json("changelog.json")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_str = date.today().isoformat()

    total_projects = len(projects["projects"])
    total_leads = leads_data.get("total_leads", 0)
    sites_online = sum(1 for s in health["sites"] if s["status"] == "online")
    sites_total = len(health["sites"])

    # Collect all leads
    all_dates = sorted(leads_data.get("leads_by_date",{}).keys(), reverse=True)[:14]
    all_leads = [l for d in all_dates for l in leads_data["leads_by_date"][d]]
    seen = set()
    unique_leads = []
    for l in all_leads:
        if l["email"] not in seen:
            seen.add(l["email"]); unique_leads.append(l)
    today_leads = leads_data.get("leads_by_date",{}).get(today_str,[])

    # Group leads
    groups = {"builder":[],"constructora":[],"real_estate":[],"property_mgmt":[],"strata":[],"other":[]}
    for l in unique_leads:
        t = l.get("type","other")
        if t not in groups: t = "other"
        groups[t].append(l)

    def email_block(leads, label, icon="", cls=""):
        if not leads:
            return '<div class="eg %s"><div class="egh"><span class="egl">%s</span><span class="egc">0</span></div></div>' % (cls, label)
        text = "; ".join(l["email"] for l in leads).replace("'","\\'")
        n = len(leads)
        entries = "".join('<div class="ei"><span class="eic">%s</span><span class="eie">%s</span><span class="ein">%s</span></div>' % (esc(l["company"]), esc(l["email"]), esc(l.get("notes",""))) for l in leads)
        return '<div class="eg %s"><div class="egh"><span class="egl">%s %s</span><span class="egc">%d</span><button class="eb" onclick="cp(\'%s\',%d)">Copy All</button></div><div class="eil">%s</div></div>' % (cls, icon, label, n, text, n, entries)

    all_text = "; ".join(l["email"] for l in unique_leads).replace("'","\\'")
    all_count = len(unique_leads)

    outreach = email_block(today_leads, "Emails Found Today", "\\ud83d\\udd34", "eg-hot")
    for key, icon, label in [("builder","\\ud83d\\udd28","Builders"),("constructora","\\ud83c\\udfd7\\ufe0f","Constructors"),("real_estate","\\ud83c\\udfe0","Real Estate"),("property_mgmt","\\ud83d\\udccb","Property Mgrs"),("strata","\\ud83c\\udfdb\\ufe0f","Strata"),("other","\\ud83d\\udccc","Other")]:
        outreach += email_block(groups.get(key,[]), label, icon)

    # Business cards
    biz_data = []
    for p in projects["projects"]:
        pid = p["id"]
        sc = {"activo":"#34d399","pendiente":"#fbbf24","idea":"#888","completado":"#60a5fa"}.get(p["status"],"#888")
        biz_data.append((pid, p["emoji"], esc(p["name"]), esc(p["description"]), sc, p["status"].upper(), p.get("url",""), p.get("metrics",{}), p.get("next_steps",[]), p.get("notes","")))

    # Health cards
    health_cards = ""
    for site in health.get("sites",[]):
        up = site["status"]=="online"
        clr = "#34d399" if up else "#ef4444"
        seo = ""
        if site.get("seo_metrics"):
            items = "".join('<div class="m"><span class="ml">%s</span><span class="mv">%s</span></div>' % (esc(k.replace("_"," ").title()), esc(v)) for k,v in site["seo_metrics"].items())
            seo = '<div class="mg">%s</div>' % items
        health_cards += '<div class="sc" style="--a:%s"><div class="sch"><span class="sd" style="background:%s"></span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><div class="shm"><a href="%s" target="_blank">%s</a> <span>%s</span></div>%s</div>' % (clr, clr, esc(site["name"]), clr, "ONLINE" if up else "OFFLINE", esc(site["url"]), esc(site["url"]), esc(site.get("uptime_24h","?")), seo)

    # Changelog
    log_html = "".join('<div class="le"><span class="ld">%s</span><span class="lp">[%s]</span><span class="ltx">%s</span></div>' % (esc(e["date"]), esc(e["project"]), esc(e["text"])) for e in changelog["entries"][:15])

    site_color = "#34d399" if sites_online==sites_total else "#ef4444"
    leads_json = json.dumps([{"c":l["company"],"e":l["email"],"n":l.get("notes","")} for l in unique_leads])

    # Build HTML
    P = []
    P.append('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>Tradeos</title>
<style>
:root{--bg:#08080c;--fg:#e8e8ed;--c1:#0e0e14;--c2:#181820;--c3:#22222e;--t2:#6b6b80;--t3:#454558;--ac:#6366f1;--ac2:#818cf8;--gr:#34d399;--rd:#ef4444;--yw:#fbbf24;--bl:#3b82f6;--pu:#8b5cf6}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{font-family:Inter,-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--fg);min-height:100dvh;overflow-x:hidden}
::selection{background:var(--ac);color:#fff}
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--c3);border-radius:2px}

/* Layout */
.app{display:flex;min-height:100dvh}
.sb{width:200px;min-width:200px;background:var(--c1);border-right:1px solid var(--c2);padding:12px 0;height:100dvh;position:sticky;top:0;overflow:hidden;overflow-y:auto;display:flex;flex-direction:column;z-index:100}
.sb-l{padding:4px 14px 14px;font-size:1em;font-weight:700;background:linear-gradient(135deg,var(--fg),var(--ac2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;border-bottom:1px solid var(--c2);margin-bottom:4px}
.sb-l small{display:block;font-size:.5em;color:var(--t2);-webkit-text-fill-color:var(--t2);font-weight:400;margin-top:2px}
.sb-g{padding:2px 0}
.sb-gl{padding:4px 14px;font-size:.55em;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;font-weight:600}
.sb-b{display:flex;align-items:center;gap:7px;padding:6px 14px;font-size:.75em;color:var(--t2);cursor:pointer;transition:all .12s;border:none;background:none;width:100%;text-align:left;font-family:inherit;border-radius:0}
.sb-b:hover{background:var(--c2);color:var(--fg)}
.sb-b.on{background:var(--c2);color:var(--fg);border-right:2px solid var(--ac)}
.sb-b .sbc{margin-left:auto;background:var(--c2);border-radius:4px;padding:0 5px;font-size:.7em;color:var(--t2)}
.sb-b.on .sbc{background:var(--ac);color:#fff}
.sb-sp{flex:1}
.sb-ft{padding:8px 14px;font-size:.55em;color:var(--t3);border-top:1px solid var(--c2)}
.mn{flex:1;overflow-y:auto;height:100dvh;min-width:0}
.c{max-width:960px;margin:0 auto;padding:16px 20px}
.view{display:none}
.view.on{display:block;animation:fIn .2s ease}
@keyframes fIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}

/* Top Bar */
.top{display:flex;align-items:center;gap:8px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--c2);flex-wrap:wrap}
.top h1{font-size:1.2em;font-weight:700;flex:1;letter-spacing:-.3px}
.top h1 small{font-weight:400;color:var(--t2);font-size:.5em;margin-left:6px}
.top-actions{display:flex;gap:6px}
.top-btn{background:var(--c2);border:1px solid var(--c3);border-radius:8px;padding:6px 12px;font-size:.72em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .12s;white-space:nowrap}
.top-btn:hover{background:var(--c3);color:var(--fg)}
.top-btn.prim{background:var(--ac);border-color:var(--ac);color:#fff}
.top-btn.prim:hover{background:var(--ac2)}

/* Dashboard Grid */
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-bottom:20px}
.stat{background:var(--c1);border:1px solid var(--c2);border-radius:12px;padding:14px;position:relative;overflow:hidden}
.stat::before{content:'';position:absolute;top:0;right:0;width:80px;height:80px;background:radial-gradient(circle,color-mix(in srgb,var(--ac) 6%,transparent) 0%,transparent 70%);pointer-events:none}
.stat .sn{font-size:.68em;color:var(--t2);margin-bottom:4px}
.stat .sv{font-size:1.3em;font-weight:700}
.stat .ss{font-size:.65em;color:var(--t3);margin-top:2px}
.stat::after{content:'';position:absolute;bottom:0;left:0;width:100%;height:2px;background:var(--ac);opacity:.3;border-radius:0 0 12px 12px}

/* Money Actions */
.money{margin-bottom:20px}
.money-h{font-size:.8em;font-weight:600;margin-bottom:8px;display:flex;align-items:center;gap:6px;color:var(--fg)}
.money-g{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}
.money-b{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:12px;cursor:pointer;transition:all .15s;text-align:left;font-family:inherit;color:var(--fg);font-size:.78em;display:flex;align-items:center;gap:8px}
.money-b:hover{background:var(--c2);border-color:var(--ac);transform:translateY(-1px)}
.money-b:active{transform:scale(.97)}
.money-b .mi{font-size:1.2em}
.money-b .ml{font-weight:500}

/* Cards */
.card{background:var(--c1);border:1px solid var(--c2);border-radius:12px;padding:16px;margin-bottom:8px}
.card-h{font-size:.82em;font-weight:600;margin-bottom:8px;display:flex;align-items:center;gap:6px}
.badge{font-size:.55em;padding:2px 8px;border-radius:6px;color:#fff;font-weight:600}
.btn-sm{background:var(--c2);border:1px solid var(--c3);border-radius:6px;padding:4px 10px;font-size:.7em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .12s}
.btn-sm:hover{background:var(--c3);color:var(--fg)}
.btn-ac{background:var(--ac);border-color:var(--ac);color:#fff}
.btn-ac:hover{background:var(--ac2);border-color:var(--ac2)}
.btn-gr{background:var(--gr);border-color:var(--gr);color:#fff}
.btn-gr:hover{background:#6ee7b7;border-color:#6ee7b7}

/* Outreach */
.eg{background:var(--c1);border:1px solid var(--c2);border-radius:10px;margin-bottom:6px;overflow:hidden}
.eg-hot{border-color:#2a2030}
.egh{display:flex;align-items:center;gap:6px;padding:8px 12px;border-bottom:1px solid var(--c2)}
.egl{font-weight:500;font-size:.78em;flex:1}
.egc{background:var(--c2);border-radius:4px;padding:0 6px;font-size:.65em;color:var(--t2)}
.eb{background:var(--c2);border:1px solid var(--c3);border-radius:4px;padding:2px 8px;font-size:.65em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .12s}
.eb:hover{background:var(--ac);border-color:var(--ac);color:#fff}
.eil{max-height:180px;overflow-y:auto}
.ei{display:flex;gap:5px;padding:4px 12px;border-bottom:1px solid #0d0d14;font-size:.72em;align-items:center}
.ei:last-child{border:none}
.eic{color:var(--fg);font-weight:500;min-width:90px;font-size:.92em}
.eie{color:var(--ac2);font-size:.92em}
.ein{color:var(--t2);font-size:.85em;margin-left:auto}

/* Kanban */
.kb{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:6px}
.kbc{background:var(--c1);border:1px solid var(--c2);border-radius:8px;padding:8px;min-height:100px}
.kbc h4{font-size:.65em;color:var(--t2);margin-bottom:4px;text-transform:uppercase;letter-spacing:.3px}
.kb-i{background:var(--c2);border:1px solid var(--c3);border-radius:6px;padding:5px 7px;margin-bottom:3px;font-size:.7em;cursor:pointer;transition:all .1s}
.kb-i:hover{border-color:var(--ac)}
.kb-i .kn{font-weight:500;font-size:.92em}
.kb-i .ks{color:var(--t2);font-size:.85em;margin-top:1px}

/* Site Health */
.sc{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:12px;margin-bottom:6px;border-left:3px solid var(--a)}
.sch{display:flex;align-items:center;gap:8px;margin-bottom:2px;flex-wrap:wrap}
.sch h3{font-size:.85em;font-weight:600}
.sd{width:6px;height:6px;border-radius:50%;display:inline-block;animation:pulse 2s infinite}
@keyframes pulse{0%{opacity:1}50%{opacity:.5}100%{opacity:1}}
.shm{display:flex;gap:8px;flex-wrap:wrap;font-size:.68em;color:var(--t2);margin:3px 0 4px}
.shm a{color:var(--ac2);text-decoration:none}

/* Agent cards */
.ac{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:12px;margin-bottom:6px;display:flex;align-items:center;gap:10px}
.ac-l{display:flex;align-items:center;gap:8px;flex:1}
.ac-d{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.ac-n{font-size:.82em;font-weight:500}
.ac-s{font-size:.65em;color:var(--t2);margin-top:1px}
.ac-r{text-align:right;font-size:.68em;color:var(--t2);line-height:1.5}

/* Ideas */
.ic{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:12px;margin-bottom:6px;border-left:3px solid var(--pu)}
.ich{display:flex;align-items:center;gap:6px;margin-bottom:2px}
.ich h3{font-size:.82em;font-weight:600;flex:1}
.id{color:var(--t2);font-size:.75em;margin:2px 0}
.ih{display:flex;gap:8px;font-size:.65em;color:var(--t2)}

/* Changelog */
.le{display:flex;align-items:flex-start;gap:4px;padding:4px 0;border-bottom:1px solid #0d0d14;font-size:.75em}
.ld{color:var(--t3);font-size:.85em;white-space:nowrap;min-width:55px}
.lp{color:var(--pu);flex-shrink:0;font-size:.85em}
.ltx{color:var(--t2);flex:1}

/* Workspace */
.ws-h{display:flex;align-items:center;gap:8px;margin-bottom:14px}
.ws-back{background:var(--c2);border:1px solid var(--c3);border-radius:6px;padding:5px 10px;font-size:.72em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .12s;white-space:nowrap}
.ws-back:hover{background:var(--c3);color:var(--fg)}
.ws-h h2{font-size:1em;font-weight:600;flex:1}
.ws-tabs{display:flex;gap:3px;margin-bottom:12px;flex-wrap:wrap}
.ws-tab{background:var(--c1);border:1px solid var(--c2);border-radius:6px;padding:5px 12px;font-size:.75em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .1s}
.ws-tab:hover{border-color:var(--c3);color:var(--fg)}
.ws-tab.on{background:var(--ac);border-color:var(--ac);color:#fff}
.ws-p{display:none}
.ws-p.on{display:block}
.ws-tasks{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.ws-tcol{background:var(--c1);border:1px solid var(--c2);border-radius:8px;padding:8px;min-height:100px}
.ws-tcol h4{font-size:.65em;color:var(--t2);margin-bottom:4px;text-transform:uppercase;letter-spacing:.3px}
.ws-ti{background:var(--c2);border:1px solid var(--c3);border-radius:5px;padding:5px 7px;margin-bottom:3px;font-size:.7em;cursor:pointer}
.ws-ti:hover{border-color:var(--ac)}
.ws-add{border:1px dashed var(--c3);border-radius:5px;padding:4px;font-size:.65em;color:var(--t3);cursor:pointer;width:100%;background:none;font-family:inherit;text-align:center}
.ws-add:hover{border-color:#3f3f46;color:var(--t2)}
.ws-notes textarea{width:100%;min-height:100px;background:var(--c2);border:1px solid var(--c3);border-radius:6px;color:var(--fg);padding:8px;font-size:.78em;font-family:inherit;resize:vertical}
.ws-notes textarea:focus{outline:none;border-color:var(--ac)}

/* Toast */
#toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(70px);background:var(--gr);color:#fff;padding:8px 20px;border-radius:10px;font-size:.78em;opacity:0;transition:all .3s;pointer-events:none;z-index:9999;box-shadow:0 6px 24px rgba(0,0,0,.5)}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

.mg{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;margin:8px 0}
.m{background:var(--c2);border:1px solid var(--c3);border-radius:6px;padding:6px;text-align:center}
.ml{display:block;font-size:.5em;color:var(--t2);text-transform:uppercase;letter-spacing:.3px}
.mv{display:block;font-size:.8em;color:var(--ac2);font-weight:600;margin-top:1px}

@media(max-width:700px){
.sb{width:100%;min-width:100%;height:auto;position:relative;flex-direction:row;flex-wrap:wrap;padding:6px;border:none;border-bottom:1px solid var(--c2);gap:1px}
.sb-l{padding:2px 8px;border:none;margin:0;font-size:.85em;width:100%}
.sb-l small{display:inline;margin-left:4px;font-size:.6em}
.sb-g{display:flex;flex-wrap:wrap;padding:0;gap:1px}
.sb-gl{display:none}
.sb-b{padding:4px 8px;font-size:.65em;width:auto;border-radius:6px}
.sb-b.on{border-right:none;background:var(--c2)}
.sb-b .sbc{font-size:.55em}
.sb-sp,.sb-ft{display:none}
.mn{height:auto;overflow:visible}
.c{padding:10px 12px}
.stats{grid-template-columns:repeat(2,1fr)}
.money-g{grid-template-columns:repeat(2,1fr)}
.ws-tasks{grid-template-columns:1fr}
.kb{grid-template-columns:repeat(3,1fr)}
}
</style>
</head>
<body>
<div class="app">''')

    # Sidebar
    P.append('<nav class="sb">')
    P.append('<div class="sb-l">Tradeos <small>for tradies</small></div>')
    items = [
        ("home","Home","\\ud83c\\udfe0"),
        ("leads","Leads","\\ud83c\\udfaf"),
        ("outreach","Outreach","\\ud83d\\udce8",all_count),
        ("sites","Sites","\\ud83d\\udd0d"),
        ("agents","AI Tools","\\ud83e\\udd16"),
        ("ideas","Ideas","\\ud83d\\udca1"),
        ("updates","Updates","\\ud83d\\udcdc"),
    ]
    P.append('<div class="sb-g">')
    for item in items:
        name = item[1]; icon = item[2]; pn = item[0]
        badge = item[3] if len(item)>3 else None
        cls = ' class="sb-b on"' if pn=="home" else ' class="sb-b"'
        badge_html = ' <span class="sbc">%d</span>' % badge if badge else ""
        P.append('<button%s data-view="%s">%s %s%s</button>' % (cls, pn, icon, name, badge_html))
    P.append('</div><div class="sb-sp"></div>')
    P.append('<div class="sb-ft">%s</div>' % now.split()[1])
    P.append('</nav>')

    P.append('<main class="mn"><div class="c">')

    # ── HOME ──
    P.append('<div class="view on" id="v-home">')
    P.append('<div class="top"><h1>Tradeos <small>%s</small></h1><div class="top-actions"><button class="top-btn" onclick="switchView(\'outreach\')">\\ud83d\\udce8 Outreach</button><button class="top-btn prim">+ Add Lead</button></div></div>' % now.split()[1])

    # Stats
    P.append('<div class="stats">')
    stats_data = [
        ("\\ud83c\\udfaf New Leads", str(len(today_leads)) if today_leads else "0", "today"),
        ("\\ud83d\\udccb Quotes Waiting", "3", "pending"),
        ("\\ud83d\\udd14 Follow Ups Due", "5", "urgent"),
        ("\\ud83d\\udee0\\ufe0f Jobs This Week", "2", "active"),
        ("\\ud83d\\udcb0 Revenue Month", "$0", "muted"),
        ("\\ud83c\\udfc6 Win Rate", "0%", "muted"),
        ("\\ud83d\\udce8 Emails Ready", str(all_count), "highlight"),
        ("\\ud83c\\udfe0 Site Leads", str(sites_online), "normal"),
    ]
    for icon, val, note in stats_data:
        P.append('<div class="stat"><div class="sn">%s %s</div><div class="sv">%s</div></div>' % (icon, val, note))
    P.append('</div>')

    # Today's Money Actions
    P.append('<div class="money"><div class="money-h">\\u26a1 Today\'s Money Actions</div><div class="money-g">')
    actions = [
        ("\\ud83d\\udcde","Call New Leads",'switchView("leads")'),
        ("\\ud83d\\udccb","Send Pending Quotes",'toast("Opening quotes...")'),
        ("\\ud83d\\udd14","Follow Up Old Quotes",'toast("Opening follow-ups...")'),
        ("\\ud83d\\udce8","Copy Outreach Emails",'switchView("outreach")'),
        ("\\ud83d\\udcc5","Book Site Visit",'toast("Add from leads pipeline")'),
        ("\\ud83d\\udcf7","Upload Job Photos",'toast("Open gallery")'),
        ("\\ud83d\\udd0d","Create SEO Page",'toast("Open SEO tool")'),
        ("\\ud83d\\udc65","Find New Builders",'switchView("outreach")'),
    ]
    for icon, label, onclick in actions:
        P.append('<button class="money-b" onclick="%s"><span class="mi">%s</span><span class="ml">%s</span></button>' % (onclick, icon, label))
    P.append('</div></div></div>')

    # ── LEADS (Kanban) ──
    P.append('<div class="view" id="v-leads">')
    P.append('<div class="top"><h1>\\ud83c\\udfaf Leads Pipeline</h1><div class="top-actions"><button class="top-btn prim">+ Add Lead</button></div></div>')
    P.append('<div class="kb" id="leads-kb"></div>')
    P.append('</div>')

    # ── OUTREACH ──
    P.append('<div class="view" id="v-outreach">')
    P.append('<div class="top"><h1>\\ud83d\\udce8 Outreach <small>%d unique emails</small></h1><div class="top-actions"><button class="top-btn btn-ac" onclick="cp(\'%s\',%d)" style="background:var(--ac);color:#fff;border-color:var(--ac)">\\ud83d\\udccb Copy All (%d)</button></div></div>' % (all_count, all_text, all_count, all_count))
    P.append(outreach)
    P.append('</div>')

    # ── SITES ──
    P.append('<div class="view" id="v-sites"><div class="top"><h1>\\ud83d\\udd0d Websites & SEO</h1><div class="top-actions"><span class="top-btn" style="border-color:%s">%d/%d online</span></div></div>%s</div>' % (site_color, sites_online, sites_total, health_cards))

    # ── AGENTS ──
    agents = [
        ("SEO Generator","Active","12 jobs","99%"),
        ("Lead Finder","Active","22 finds","100%"),
        ("Content Writer","Active","8 pages","98%"),
        ("Health Monitor","Active","48 checks","100%"),
        ("Outreach Agent","Paused","0 sends","-"),
    ]
    agents_html = "".join('<div class="ac"><div class="ac-l"><div class="ac-d" style="background:%s"></div><div><div class="ac-n">%s</div><div class="ac-s">%s</div></div></div><div class="ac-r"><span>%s</span><br><span>%s</span></div></div>' % ("#34d399" if a[1]=="Active" else "#fbbf24", a[0], a[1], a[2], a[3]) for a in agents)
    P.append('<div class="view" id="v-agents"><div class="top"><h1>\\ud83e\\udd16 AI Tools</h1></div>%s</div>' % agents_html)

    # ── IDEAS ──
    pots = {"Alto":"#34d399","Muy Alto":"#60a5fa","Medio":"#fbbf24","Bajo":"#888"}
    idea_cards = "".join('<div class="ic"><div class="ich"><span>%s</span><h3>%s</h3><span class="badge" style="background:%s">%s</span></div><p class="id">%s</p><div class="ih"><span>%s</span><span>%s</span></div></div>' % (idea["emoji"], esc(idea["name"]), pots.get(idea.get("potential",""),"#888"), esc(idea.get("potential","")), esc(idea["description"]), esc(idea.get("timeline","?")), esc(idea.get("effort","?"))) for idea in ideas.get("ideas",[]))
    P.append('<div class="view" id="v-ideas"><div class="top"><h1>\\ud83d\\udca1 Ideas</h1></div>%s</div>' % idea_cards)

    # ── UPDATES ──
    P.append('<div class="view" id="v-updates"><div class="top"><h1>\\ud83d\\udcdc Updates</h1></div>%s</div>' % log_html)

    # Workspace view
    P.append('''<div class="view" id="v-workspace">
<div class="ws-h"><button class="ws-back" onclick="closeWs()">&#x2190; Back</button><span id="ws-e" style="font-size:1.3em"></span><h2 id="ws-n"></h2></div>
<div class="ws-tabs" id="ws-t">
<button class="ws-tab on" onclick="wsT('overview')">Overview</button>
<button class="ws-tab" onclick="wsT('tasks')">Tasks</button>
<button class="ws-tab" onclick="wsT('notes')">Notes</button>
</div>
<div class="ws-p on" id="ws-overview"><div id="ws-oc"></div></div>
<div class="ws-p" id="ws-tasks"><div class="ws-tasks" id="ws-tc"></div></div>
<div class="ws-p" id="ws-notes"><div class="ws-notes"><textarea id="ws-nt" placeholder="Notes..."></textarea><button class="ws-back" style="margin-top:6px" onclick="svn()">Save</button><span style="font-size:.7em;color:var(--t2);margin-left:6px" id="ws-ns"></span></div></div>
</div>''')

    P.append('</div></main></div>')
    P.append('<div id="toast"></div>')

    # JavaScript
    P.append('''<script>
var BTNS = document.querySelectorAll('.sb-b');
BTNS.forEach(function(b){b.addEventListener('click',function(){
if(b.getAttribute('data-view')==='workspace') return;
BTNS.forEach(function(x){x.classList.remove('on')});
document.querySelectorAll('.view').forEach(function(x){x.classList.remove('on')});
b.classList.add('on');
var v = document.getElementById('v-'+b.getAttribute('data-view'));
if(v) v.classList.add('on');
try{localStorage.setItem('tv',b.getAttribute('data-view'))}catch(e){}
})});
try{var lv=localStorage.getItem('tv');if(lv){var b=document.querySelector('.sb-b[data-view="'+lv+'"]');if(b)b.click()}}catch(e){}

function switchView(n){
BTNS.forEach(function(x){x.classList.remove('on')});
document.querySelectorAll('.view').forEach(function(x){x.classList.remove('on')});
var b=document.querySelector('.sb-b[data-view="'+n+'"]');
if(b)b.classList.add('on');
var v=document.getElementById('v-'+n);
if(v)v.classList.add('on');
try{localStorage.setItem('tv',n)}catch(e){}
}

// Leads Kanban
var LC = ['New','Contacted','Site Visit','Quote Sent','Won','Lost'];
function gLD(){try{return JSON.parse(localStorage.getItem('tleads'))||{}}catch(e){return{}}}
function sLD(d){try{localStorage.setItem('tleads',JSON.stringify(d))}catch(e){}}

function rL(){
var ld=gLD();var h='';
LC.forEach(function(c){
var items=ld[c]||[];h+='<div class="kbc"><h4>'+c+' ('+items.length+')</h4>';
items.forEach(function(it,i){h+='<div class="kb-i" onclick="mL(\\''+c+'\\','+i+')"><div class="kn">'+it.n+'</div><div class="ks">'+it.s+'</div></div>'});
h+='</div>';});
h+='<div style="margin-top:8px"><button class="btn-sm btn-ac" onclick="aL()">+ Add Lead</button></div>';
document.getElementById('leads-kb').innerHTML=h;
}

function aL(){
var n=prompt('Client name:');if(!n||!n.trim())return;
var s=prompt('Suburb / service:')||'';var ld=gLD();if(!ld['New'])ld['New']=[];
ld['New'].push({n:n.trim(),s:s});sLD(ld);rL();toast('Lead added');
}

function mL(col,i){
var ld=gLD();var items=ld[col]||[];if(i>=items.length)return;
var item=items.splice(i,1)[0];var idx=LC.indexOf(col);
if(idx>=LC.length-1){items.splice(i,0,item);return;}
var nxt=LC[idx+1];if(!ld[nxt])ld[nxt]=[];ld[nxt].push(item);sLD(ld);rL();toast('Moved to '+nxt);
}
rL();

// Copy
function cp(t,c){
if(navigator.clipboard&&navigator.clipboard.writeText){
navigator.clipboard.writeText(t).then(function(){toast(c+' emails copied')}).catch(function(){fb(t)});
}else{fb(t)}}
function fb(t){var ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');toast('Copied')}catch(e){toast('Error')}document.body.removeChild(ta);}
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('show')},2500);}

// Workspace
var BIZ = ''' + json.dumps({b[0]:{"e":b[1],"n":b[2],"m":dict(b[7]),"steps":list(b[8]),"notes":b[9]} for b in biz_data}) + ''';

function openBiz(id){
var b=BIZ[id];if(!b)return;
document.getElementById('ws-e').textContent=b.e;
document.getElementById('ws-n').textContent=b.n;
document.querySelectorAll('.view').forEach(function(x){x.classList.remove('on')});
document.getElementById('v-workspace').classList.add('on');
rO(id);rT(id);rN(id);wsT('overview');
}
function closeWs(){document.getElementById('v-workspace').classList.remove('on');document.getElementById('v-home').classList.add('on');}
function wsT(n){
document.querySelectorAll('.ws-tab').forEach(function(x){x.classList.remove('on')});
document.querySelectorAll('.ws-p').forEach(function(x){x.classList.remove('on')});
var e=null;document.querySelectorAll('.ws-tab').forEach(function(t){if(t.textContent.toLowerCase().indexOf(n)>=0)e=t});
if(e)e.classList.add('on');var p=document.getElementById('ws-'+n);if(p)p.classList.add('on');
}
function rO(id){
var b=BIZ[id];if(!b)return;
var h='<div class="mg" style="grid-template-columns:repeat(3,1fr)">';
for(var k in b.m){h+='<div class="m"><span class="ml">'+k+'</span><span class="mv">'+b.m[k]+'</span></div>';}
h+='</div>';
if(b.steps&&b.steps.length){h+='<div style="font-size:.8em;color:var(--t2);margin-top:8px;font-weight:600">Next Steps</div><ul style="list-style:none;padding:0;margin-top:4px">';
b.steps.forEach(function(s,i){h+='<li style="padding:2px 0;font-size:.76em;color:var(--t2)">'+(i===0?'\\u2705':'\\u25CB')+' '+s+'</li>'});h+='</ul>';}
if(b.notes)h+='<div style="font-size:.76em;color:var(--t2);margin-top:8px">'+b.notes+'</div>';
document.getElementById('ws-oc').innerHTML=h;
}
function gT(id){try{var d=JSON.parse(localStorage.getItem('wtasks'))||{};if(!d[id])d[id]={today:[],urgent:[],week:[]};return d[id]}catch(e){return{today:[],urgent:[],week:[]}}}
function sT(id,t){try{var d=JSON.parse(localStorage.getItem('wtasks'))||{};d[id]=t;localStorage.setItem('wtasks',JSON.stringify(d))}catch(e){}}
function rT(id){
var t=gT(id);var cs=['today','urgent','week'];var lb=['Today','Urgent','This Week'];
var h='';cs.forEach(function(c,i){var items=t[c]||[];h+='<div class="ws-tcol"><h4>'+lb[i]+' ('+items.length+')</h4>';
items.forEach(function(it,j){h+='<div class="ws-ti" onclick="dT(\\''+id+'\\',\\''+c+'\\','+j+')">'+it+'</div>';});
h+='<button class="ws-add" onclick="aT(\\''+id+'\\',\\''+c+'\\')">+ Add</button></div>';});
document.getElementById('ws-tc').innerHTML=h;
}
function aT(id,c){var t=gT(id);var n=prompt('Task:');if(!n||!n.trim())return;if(!t[c])t[c]=[];t[c].push(n.trim());sT(id,t);rT(id);}
function dT(id,c,i){var t=gT(id);if(!t[c]||i>=t[c].length)return;t[c].splice(i,1);sT(id,t);rT(id);toast('Done');}
function rN(id){var ta=document.getElementById('ws-nt');try{ta.value=localStorage.getItem('wsn_'+id)||''}catch(e){}}
function svn(){var id=document.getElementById('ws-n').textContent;var ta=document.getElementById('ws-nt');try{localStorage.setItem('wsn_'+id,ta.value);document.getElementById('ws-ns').textContent='Saved'}catch(e){}}
</script>
</body>
</html>''')

    html = "\n".join(P)
    path = os.path.join(DIR, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print("OK: %s (%d bytes)" % (path, len(html)))
    return True

if __name__ == "__main__":
    generate()

#!/usr/bin/env python3
"""generate.py — Hermes OS: Premium AI Business OS"""

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

    def email_block(leads, label, cls=""):
        if not leads:
            return '<div class="eg %s"><div class="egh"><span class="egl">%s</span><span class="egc">0</span></div></div>' % (cls, label)
        text = "; ".join(l["email"] for l in leads).replace("'","\\'")
        n = len(leads)
        entries = "".join('<div class="ei"><span class="eic">%s</span><span class="eie">%s</span><span class="ein">%s</span></div>' % (esc(l["company"]), esc(l["email"]), esc(l.get("notes",""))) for l in leads)
        return '<div class="eg %s"><div class="egh"><span class="egl">%s</span><span class="egc">%d</span><button class="eb" onclick="cp(\'%s\',%d)">Copy</button></div><div class="eil">%s</div></div>' % (cls, label, n, text, n, entries)

    all_text = "; ".join(l["email"] for l in unique_leads).replace("'","\\'")
    all_count = len(unique_leads)

    outreach = email_block(today_leads, "Today", "eg-hot")
    for key, emoji in [("constructora","Constructors"),("builder","Builders"),("real_estate","Real Estate"),("property_mgmt","Property Mgmt"),("strata","Strata"),("other","Other")]:
        outreach += email_block(groups.get(key,[]), emoji)

    # Business cards
    biz_data = []
    for p in projects["projects"]:
        pid = p["id"]
        sc = {"activo":"#34d399","pendiente":"#fbbf24","idea":"#888","completado":"#60a5fa"}.get(p["status"],"#888")
        leads_count = 0
        for l in unique_leads:
            lt = l.get("type","")
            if (pid == "leadgen") or \
               (pid == "primeproperty" and lt in ("property_mgmt","real_estate")) or \
               (pid == "antoniopaving" and lt in ("builder","constructora")) or \
               (pid == "toolshubpro"):
                leads_count += 1
        biz_data.append((pid, p["emoji"], esc(p["name"]), esc(p["description"]), sc, p["status"].upper(), p.get("url",""), leads_count, p.get("metrics",{}), p.get("next_steps",[]), p.get("notes","")))

    biz_cards = ""
    for b in biz_data:
        pid, em, name, desc, sc, status, url, lcount, metrics, steps, notes = b
        m_items = "".join('<div class="m"><span class="ml">%s</span><span class="mv">%s</span></div>' % (esc(k.replace("_"," ").title()), esc(v)) for k,v in metrics.items()) if metrics else ""
        biz_cards += '<div class="bc" onclick="openBiz(\'%s\')" style="--a:%s"><div class="bch"><span class="be">%s</span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><p class="bd">%s</p>%s<div class="bqa"><button class="bq" onclick="event.stopPropagation();openBiz(\'%s\')">Open</button><button class="bq bq-o" onclick="event.stopPropagation();switchView(\'outreach\')">Outreach</button></div></div>' % (pid, sc, em, name, sc, status, desc, m_items, pid)

    # Health cards
    health_cards = ""
    for site in health.get("sites",[]):
        up = site["status"]=="online"
        clr = "#34d399" if up else "#ef4444"
        seo = ""
        if site.get("seo_metrics"):
            items = "".join('<div class="m"><span class="ml">%s</span><span class="mv">%s</span></div>' % (esc(k.replace("_"," ").title()), esc(v)) for k,v in site["seo_metrics"].items())
            seo = '<div class="mg">%s</div>' % items
        health_cards += '<div class="sc" style="--a:%s"><div class="sch"><span class="sd" style="background:%s"></span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><div class="shm"><a href="%s" target="_blank">%s</a><span>%s</span></div>%s</div>' % (clr, clr, esc(site["name"]), clr, "ONLINE" if up else "OFFLINE", esc(site["url"]), esc(site["url"]), esc(site.get("uptime_24h","?")), seo)

    # Agents
    agents = [
        ("SEO Agent","Active","12 jobs today","99pct"),
        ("Lead Finder","Active","22 jobs","100pct"),
        ("Outreach Agent","Paused","0 jobs","-"),
        ("Content Writer","Active","8 jobs","98pct"),
        ("Health Monitor","Active","48 checks","100pct"),
    ]
    agents_html = "".join('<div class="ac"><div class="ac-h"><div class="ac-dot" style="background:%s"></div><div><div class="ac-n">%s</div><div class="ac-s">%s</div></div></div><div class="ac-m"><span>%s</span><span>%s</span></div></div>' % ("#34d399" if a[1]=="Active" else "#fbbf24", a[0], a[1], a[2], a[3]) for a in agents)

    # Ideas
    pots = {"Alto":"#34d399","Muy Alto":"#60a5fa","Medio":"#fbbf24","Bajo":"#888"}
    idea_cards = "".join('<div class="ic"><div class="ich"><span>%s</span><h3>%s</h3><span class="bg" style="background:%s">%s</span></div><p class="id">%s</p><div class="ih"><span>%s</span><span>%s</span></div></div>' % (idea["emoji"], esc(idea["name"]), pots.get(idea.get("potential",""),"#888"), esc(idea.get("potential","")), esc(idea["description"]), esc(idea.get("timeline","?")), esc(idea.get("effort","?"))) for idea in ideas.get("ideas",[]))

    # Changelog
    log_html = "".join('<div class="le"><span class="ld">%s</span><span class="lp">[%s]</span><span class="ltx">%s</span></div>' % (esc(e["date"]), esc(e["project"]), esc(e["text"])) for e in changelog["entries"][:15])

    site_color = "#34d399" if sites_online==sites_total else "#ef4444"

    # Biz data for JS
    biz_json = json.dumps({b[0]: {"e":b[1],"n":b[2],"m":dict(b[8]),"steps":list(b[9]),"notes":b[10]} for b in biz_data})
    leads_json = json.dumps([{"c":l["company"],"e":l["email"],"n":l.get("notes","")} for l in unique_leads])

    # Build HTML in parts (avoids %% conflicts)
    P = []
    P.append('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>Hermes OS</title>
<style>
:root{--bg:#0a0a0f;--fg:#e4e4e7;--c1:#111118;--c2:#1c1c24;--c3:#27272a;--t2:#71717a;--t3:#52525b;--ac:#6366f1;--ac2:#818cf8;--gr:#34d399;--rd:#ef4444;--yw:#fbbf24}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{font-family:Inter,-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--fg);min-height:100dvh;overflow-x:hidden}
::selection{background:var(--ac);color:#fff}
.app{display:flex;min-height:100dvh}
.sb{width:220px;min-width:220px;background:#0c0c12;border-right:1px solid var(--c2);padding:16px 0;height:100dvh;position:sticky;top:0;overflow-y:auto;display:flex;flex-direction:column;z-index:100}
.sb-logo{padding:4px 18px 18px;font-size:1em;font-weight:700;background:linear-gradient(135deg,var(--fg),var(--ac2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;border-bottom:1px solid var(--c2);margin-bottom:8px;letter-spacing:-.3px}
.sb-logo small{display:block;font-size:.55em;color:var(--t2);-webkit-text-fill-color:var(--t2);font-weight:400;margin-top:3px;letter-spacing:0}
.sb-g{padding:4px 0}
.sb-gl{padding:4px 18px;font-size:.6em;color:var(--t3);text-transform:uppercase;letter-spacing:1px;font-weight:600}
.sb-b{display:flex;align-items:center;gap:8px;padding:8px 18px;font-size:.8em;color:var(--t2);cursor:pointer;transition:all .12s;border:none;background:none;width:100%;text-align:left;font-family:inherit;border-radius:0}
.sb-b:hover{background:#14141e;color:var(--fg)}
.sb-b.on{background:#1a1a26;color:var(--fg);border-right:2px solid var(--ac)}
.sb-b .sbc{margin-left:auto;background:var(--c2);border-radius:6px;padding:1px 6px;font-size:.7em;color:var(--t2)}
.sb-b.on .sbc{background:var(--ac);color:#fff}
.sb-sp{flex:1}
.sb-ft{padding:12px 18px;font-size:.6em;color:var(--t3);border-top:1px solid var(--c2)}
.mn{flex:1;overflow-y:auto;height:100dvh}
.c{max-width:1000px;margin:0 auto;padding:24px}
.view{display:none}
.view.on{display:block;animation:fadeIn .2s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.hd{margin-bottom:24px}
.hd h1{font-size:1.4em;font-weight:700;letter-spacing:-.5px}
.hd h1 small{font-size:.45em;font-weight:400;color:var(--t2);margin-left:8px;letter-spacing:0}
.hd .sub{color:var(--t2);font-size:.8em;margin-top:4px}
.stats{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0 0}
.stat{background:var(--c1);border:1px solid var(--c2);border-radius:20px;padding:4px 12px;font-size:.72em;color:var(--t2);display:flex;align-items:center;gap:4px}
.stat b{color:var(--fg)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin-bottom:24px}
.bc{background:var(--c1);border:1px solid var(--c2);border-radius:16px;padding:20px;border-left:3px solid var(--a);cursor:pointer;transition:all .2s;position:relative;overflow:hidden}
.bc::before{content:'';position:absolute;top:0;right:0;width:120px;height:120px;background:radial-gradient(circle,color-mix(in srgb,var(--a) 8%,transparent) 0%,transparent 70%);pointer-events:none}
.bc:hover{border-color:var(--c3);transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,0,0,.3)}
.bc:active{transform:translateY(0)}
.bch{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.be{font-size:1.8em}
.bch h3{font-size:1.05em;font-weight:600;flex:1}
.bg{font-size:.55em;padding:2px 10px;border-radius:10px;color:#fff;font-weight:600;letter-spacing:.3px}
.bd{color:var(--t2);font-size:.8em;margin:0 0 12px;line-height:1.5}
.mg{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:12px}
.m{background:#0d0d14;border-radius:8px;padding:8px 6px;text-align:center}
.ml{display:block;font-size:.55em;color:var(--t2);text-transform:uppercase;letter-spacing:.3px}
.mv{display:block;font-size:.85em;color:var(--ac2);font-weight:600;margin-top:2px}
.bqa{display:flex;gap:6px;margin-top:4px}
.bq{flex:1;background:var(--c2);border:1px solid var(--c3);border-radius:8px;padding:7px;font-size:.72em;color:var(--t2);cursor:pointer;text-align:center;font-family:inherit;transition:all .12s}
.bq:hover{background:var(--c3);color:var(--fg)}
.bq-o{background:var(--ac);border-color:var(--ac);color:#fff}
.bq-o:hover{background:var(--ac2);border-color:var(--ac2)}
.ma{margin-bottom:24px}
.ma-h{font-size:.85em;font-weight:600;margin-bottom:10px;color:var(--fg);display:flex;align-items:center;gap:6px}
.ma-g{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.ma-b{background:var(--c1);border:1px solid var(--c2);border-radius:12px;padding:14px 16px;cursor:pointer;transition:all .15s;text-align:left;font-family:inherit;color:var(--fg);font-size:.82em;display:flex;align-items:center;gap:8px}
.ma-b:hover{background:var(--c2);border-color:var(--c3);transform:translateY(-1px)}
.ma-b:active{transform:scale(.97)}
.ma-b .ma-i{font-size:1.1em}
.ma-b .ma-l{font-weight:500}
.eg{background:var(--c1);border:1px solid var(--c2);border-radius:12px;margin-bottom:8px;overflow:hidden}
.eg-hot{border-color:#2a1a1a}
.egh{display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--c2)}
.egl{font-weight:600;font-size:.82em;flex:1}
.egc{background:var(--c2);border-radius:6px;padding:0 7px;font-size:.7em;color:var(--t2)}
.eb{background:var(--c2);border:1px solid var(--c3);border-radius:6px;padding:3px 10px;font-size:.68em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .12s}
.eb:hover{background:var(--ac);border-color:var(--ac);color:#fff}
.eil{max-height:200px;overflow-y:auto}
.ei{display:flex;gap:6px;padding:5px 14px;border-bottom:1px solid #0d0d14;font-size:.75em;align-items:center}
.ei:last-child{border:none}
.eic{color:var(--fg);font-weight:500;min-width:110px;font-size:.9em}
.eie{color:var(--ac2);font-size:.9em}
.ein{color:var(--t2);font-size:.85em;margin-left:auto}
.ws-h{display:flex;align-items:center;gap:10px;margin-bottom:20px}
.ws-back{background:var(--c2);border:1px solid var(--c3);border-radius:8px;padding:6px 12px;font-size:.75em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .12s}
.ws-back:hover{background:var(--c3);color:var(--fg)}
.ws-h h2{font-size:1.2em;font-weight:600}
.ws-h .ws-emoji{font-size:1.5em}
.ws-tabs{display:flex;gap:4px;margin-bottom:16px;flex-wrap:wrap}
.ws-tab{background:var(--c1);border:1px solid var(--c2);border-radius:8px;padding:6px 14px;font-size:.78em;color:var(--t2);cursor:pointer;font-family:inherit;transition:all .12s}
.ws-tab:hover{border-color:var(--c3);color:var(--fg)}
.ws-tab.on{background:var(--ac);border-color:var(--ac);color:#fff}
.ws-p{display:none}
.ws-p.on{display:block}
.kb{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.kbc{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:10px;min-height:140px}
.kbc h4{font-size:.7em;color:var(--t2);margin-bottom:6px;text-transform:uppercase;letter-spacing:.3px}
.kb-i{background:#0d0d14;border:1px solid var(--c2);border-radius:6px;padding:6px 8px;margin-bottom:4px;font-size:.72em;cursor:pointer;transition:all .1s}
.kb-i:hover{border-color:var(--c3)}
.kb-i .kb-n{font-weight:500}
.kb-i .kb-s{font-size:.85em;color:var(--t2);margin-top:1px}
.sc{background:var(--c1);border:1px solid var(--c2);border-radius:12px;padding:16px;margin-bottom:8px;border-left:3px solid var(--a)}
.sch{display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap}
.sch h3{font-size:.9em;font-weight:600}
.sd{width:7px;height:7px;border-radius:50%;display:inline-block;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.shm{display:flex;gap:10px;flex-wrap:wrap;font-size:.72em;color:var(--t2);margin:5px 0 6px}
.shm a{color:var(--ac2);text-decoration:none}
.ac{background:var(--c1);border:1px solid var(--c2);border-radius:12px;padding:14px;margin-bottom:8px;display:flex;align-items:center;gap:12px}
.ac-h{display:flex;align-items:center;gap:10px;flex:1}
.ac-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.ac-n{font-size:.85em;font-weight:500}
.ac-s{font-size:.7em;color:var(--t2);margin-top:1px}
.ac-m{text-align:right;font-size:.72em;color:var(--t2);line-height:1.6}
.ic{background:var(--c1);border:1px solid var(--c2);border-radius:12px;padding:14px;margin-bottom:8px;border-left:3px solid #7c3aed}
.ich{display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap}
.ich h3{font-size:.85em;font-weight:600;flex:1}
.id{color:var(--t2);font-size:.78em;margin:3px 0 4px;line-height:1.5}
.ih{display:flex;gap:10px;font-size:.7em;color:var(--t2)}
.le{display:flex;align-items:flex-start;gap:6px;padding:5px 0;border-bottom:1px solid #0d0d14;font-size:.78em}
.ld{color:var(--t3);font-size:.85em;white-space:nowrap;min-width:62px}
.lp{color:#7c3aed;flex-shrink:0;font-size:.85em}
.ltx{color:var(--t2);flex:1}
.ws-tasks{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.ws-tcol{background:var(--c1);border:1px solid var(--c2);border-radius:10px;padding:10px;min-height:120px}
.ws-tcol h4{font-size:.7em;color:var(--t2);margin-bottom:6px;text-transform:uppercase;letter-spacing:.3px}
.ws-ti{background:#0d0d14;border:1px solid var(--c2);border-radius:6px;padding:6px 8px;margin-bottom:4px;font-size:.72em;cursor:pointer}
.ws-ti:hover{border-color:var(--c3)}
.ws-add{border:1px dashed var(--c3);border-radius:6px;padding:5px;font-size:.7em;color:var(--t3);cursor:pointer;width:100%;background:none;font-family:inherit;text-align:center}
.ws-add:hover{border-color:#3f3f46;color:var(--t2)}
.ws-notes textarea{width:100%;min-height:120px;background:#0d0d14;border:1px solid var(--c2);border-radius:8px;color:var(--fg);padding:10px;font-size:.8em;font-family:inherit;resize:vertical}
.ws-notes textarea:focus{outline:none;border-color:var(--ac)}
#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--gr);color:#fff;padding:10px 22px;border-radius:12px;font-size:.82em;opacity:0;transition:all .3s;pointer-events:none;z-index:9999;box-shadow:0 8px 30px rgba(0,0,0,.5)}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:#0d0d14}
::-webkit-scrollbar-thumb{background:var(--c3);border-radius:2px}
.sh{font-size:.85em;font-weight:600;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.sh small{font-weight:400;color:var(--t2);font-size:.8em}
@media(max-width:700px){
.sb{width:100%;min-width:100%;height:auto;position:relative;flex-direction:row;flex-wrap:wrap;padding:8px;border:none;border-bottom:1px solid var(--c2);gap:2px}
.sb-logo{padding:2px 10px 2px;border:none;margin:0;font-size:.85em;width:100%}
.sb-logo small{display:inline;margin-left:4px;font-size:.65em}
.sb-g{display:flex;flex-wrap:wrap;padding:0;gap:2px}
.sb-gl{display:none}
.sb-b{padding:5px 10px;font-size:.7em;width:auto;border-radius:8px;gap:4px}
.sb-b.on{border-right:none;background:#1a1a26}
.sb-b .sbc{font-size:.6em}
.sb-sp,.sb-ft{display:none}
.mn{height:auto;overflow:visible}
.c{padding:14px}
.grid{grid-template-columns:1fr}
.ma-g{grid-template-columns:repeat(2,1fr)}
.ws-tasks{grid-template-columns:1fr}
.kb{grid-template-columns:repeat(2,1fr)}
}
</style>
</head>
<body>
<div class="app">''')

    # Sidebar
    P.append('<nav class="sb">')
    P.append('<div class="sb-logo">Hermes OS <small>v2</small></div>')
    P.append('<div class="sb-g"><div class="sb-gl">Main</div>')
    P.append('<button class="sb-b on" data-view="home">&#x1F3E0; Home</button>')
    P.append('<button class="sb-b" data-view="outreach">&#x1F4E8; Outreach <span class="sbc">%d</span></button>' % all_count)
    P.append('<button class="sb-b" data-view="sites">&#x1F50D; Sites</button>')
    P.append('<button class="sb-b" data-view="agents">&#x1F916; Agents</button>')
    P.append('</div><div class="sb-g"><div class="sb-gl">Business</div>')
    P.append('<button class="sb-b" data-view="ideas">&#x1F4A1; Ideas</button>')
    P.append('<button class="sb-b" data-view="changelog">&#x1F4DC; Updates</button>')
    P.append('</div><div class="sb-sp"></div>')
    P.append('<div class="sb-ft">%s</div>' % now.split()[1])
    P.append('</nav>')

    # Main content
    P.append('<main class="mn"><div class="c">')

    # Home view
    P.append('<div class="view on" id="v-home">')
    P.append('<div class="hd"><h1>Workspaces <small>%d businesses</small></h1><div class="sub">Select a business to open its workspace</div><div class="stats"><span class="stat">&#x1F3AF; <b>%d</b> leads</span><span class="stat" style="border-color:var(--ac)">&#x1F4E8; <b>%d</b> emails</span><span class="stat" style="border-color:%s">&#x1F50D; <b>%d/%d</b> online</span></div></div>' % (total_projects, total_leads, all_count, site_color, sites_online, sites_total))
    P.append('<div class="grid">%s</div>' % biz_cards)
    P.append('<div class="ma"><div class="ma-h">&#x26A1; Today\'s Money Actions</div><div class="ma-g">')
    P.append('<button class="ma-b" onclick="switchView(\'outreach\')"><span class="ma-i">&#x1F4E8;</span><span class="ma-l">Send Outreach</span></button>')
    P.append('<button class="ma-b"><span class="ma-i">&#x1F4DD;</span><span class="ma-l">Create Quote</span></button>')
    P.append('<button class="ma-b"><span class="ma-i">&#x1F4DE;</span><span class="ma-l">Call Leads</span></button>')
    P.append('<button class="ma-b"><span class="ma-i">&#x1F4F7;</span><span class="ma-l">Upload Photos</span></button>')
    P.append('<button class="ma-b"><span class="ma-i">&#x1F50D;</span><span class="ma-l">Generate SEO</span></button>')
    P.append('<button class="ma-b"><span class="ma-i">&#x1F4CB;</span><span class="ma-l">Follow Up Quotes</span></button>')
    P.append('</div></div></div>')

    # Outreach view
    P.append('<div class="view" id="v-outreach">')
    P.append('<div class="hd"><h1>&#x1F4E8; Outreach <small>%d unique emails</small></h1><div class="stats" style="margin-top:8px"><button class="stat" style="cursor:pointer;border-color:var(--ac);color:var(--fg)" onclick="cp(\'%s\',%d)">&#x1F4CB; Copy All (%d)</button></div></div>' % (all_count, all_text, all_count, all_count))
    P.append(outreach)
    P.append('</div>')

    # Sites view
    P.append('<div class="view" id="v-sites"><div class="hd"><h1>&#x1F50D; Sites</h1><div class="stats"><span class="stat" style="border-color:%s">%d/%d online</span></div></div>%s</div>' % (site_color, sites_online, sites_total, health_cards))

    # Agents view
    P.append('<div class="view" id="v-agents"><div class="hd"><h1>&#x1F916; AI Agents</h1></div>%s</div>' % agents_html)

    # Ideas view
    P.append('<div class="view" id="v-ideas"><div class="hd"><h1>&#x1F4A1; Ideas</h1></div>%s</div>' % idea_cards)

    # Changelog view
    P.append('<div class="view" id="v-changelog"><div class="hd"><h1>&#x1F4DC; Updates</h1></div>%s</div>' % log_html)

    # Workspace view (hidden, shown by JS)
    P.append('''<div class="view" id="v-workspace">
<div class="ws-h"><button class="ws-back" onclick="closeWorkspace()">&#x2190; Back</button><span class="ws-emoji" id="ws-emoji"></span><h2 id="ws-name"></h2></div>
<div class="ws-tabs" id="ws-tabs">
<button class="ws-tab on" onclick="wsTab('overview')">Overview</button>
<button class="ws-tab" onclick="wsTab('leads')">Leads</button>
<button class="ws-tab" onclick="wsTab('outreach')">Outreach</button>
<button class="ws-tab" onclick="wsTab('tasks')">Tasks</button>
<button class="ws-tab" onclick="wsTab('notes')">Notes</button>
</div>
<div class="ws-p on" id="ws-overview"><div id="ws-overview-c"></div></div>
<div class="ws-p" id="ws-leads"><div id="ws-leads-c"></div></div>
<div class="ws-p" id="ws-outreach"><div id="ws-outreach-c"></div></div>
<div class="ws-p" id="ws-tasks"><div class="ws-tasks" id="ws-tasks-c"></div></div>
<div class="ws-p" id="ws-notes"><div class="ws-notes"><textarea id="ws-notes-ta" placeholder="Workspace notes..."></textarea><button class="ws-back" style="margin-top:8px" onclick="saveWsNotes()">Save Notes</button><span style="font-size:.72em;color:var(--t2);margin-left:8px" id="ws-notes-s"></span></div></div>
</div>''')

    P.append('</div></main></div>')
    P.append('<div id="toast"></div>')

    # JavaScript
    P.append('''<script>
var sbBtns = document.querySelectorAll('.sb-b');
sbBtns.forEach(function(b){b.addEventListener('click',function(){
if(b.getAttribute('data-view')==='workspace') return;
sbBtns.forEach(function(x){x.classList.remove('on')});
document.querySelectorAll('.view').forEach(function(x){x.classList.remove('on')});
b.classList.add('on');
var v = document.getElementById('v-'+b.getAttribute('data-view'));
if(v) v.classList.add('on');
try{localStorage.setItem('hv',b.getAttribute('data-view'))}catch(e){}
})});
try{var lv=localStorage.getItem('hv');if(lv){var b=document.querySelector('.sb-b[data-view="'+lv+'"]');if(b)b.click()}}catch(e){}
function switchView(name){
document.querySelectorAll('.sb-b').forEach(function(x){x.classList.remove('on')});
document.querySelectorAll('.view').forEach(function(x){x.classList.remove('on')});
var b=document.querySelector('.sb-b[data-view="'+name+'"]');
if(b)b.classList.add('on');
var v=document.getElementById('v-'+name);
if(v)v.classList.add('on');
try{localStorage.setItem('hv',name)}catch(e){}
}
var BIZ = ''' + biz_json + ''';

function openBiz(id){
var biz = BIZ[id]; if(!biz) return;
document.getElementById('ws-emoji').textContent = biz.e;
document.getElementById('ws-name').textContent = biz.n;
document.querySelectorAll('.view').forEach(function(x){x.classList.remove('on')});
document.getElementById('v-workspace').classList.add('on');
renderOverview(id); renderLeads(id); renderOutreach(id); renderTasks(id); renderNotes(id);
wsTab('overview');
}
function closeWorkspace(){document.getElementById('v-workspace').classList.remove('on');document.getElementById('v-home').classList.add('on')}

function wsTab(name){
document.querySelectorAll('.ws-tab').forEach(function(x){x.classList.remove('on')});
document.querySelectorAll('.ws-p').forEach(function(x){x.classList.remove('on')});
var el=null;
document.querySelectorAll('.ws-tab').forEach(function(t){if(t.textContent.toLowerCase().indexOf(name)>=0)el=t});
if(el)el.classList.add('on');
var p=document.getElementById('ws-'+name);if(p)p.classList.add('on');
}

function renderOverview(id){
var biz=BIZ[id];if(!biz)return;
var h='<div class="mg" style="grid-template-columns:repeat(3,1fr)">';
for(var k in biz.m){h+='<div class="m"><span class="ml">'+k+'</span><span class="mv">'+biz.m[k]+'</span></div>';}
h+='</div>';
if(biz.steps&&biz.steps.length){h+='<div class="sh">Next Steps</div><ul class="st" style="list-style:none;padding:0">';
biz.steps.forEach(function(s,i){h+='<li style="padding:3px 0;font-size:.8em;color:var(--t2)">'+(i===0?'\\u2705':'\\u25CB')+' '+s+'</li>'});h+='</ul>';}
if(biz.notes)h+='<div class="sh">Notes</div><p style="font-size:.82em;color:var(--t2)">'+biz.notes+'</p>';
document.getElementById('ws-overview-c').innerHTML=h;
}

var LEAD_COLS = ['New','Contacted','Site Visit','Quote Sent','Won','Lost'];
function getLD(){try{return JSON.parse(localStorage.getItem('hleads'))||{}}catch(e){return{}}}
function setLD(d){try{localStorage.setItem('hleads',JSON.stringify(d))}catch(e){}}

function renderLeads(id){
var ld=getLD();var bl=ld[id]||{};var h='<div class="kb">';
LEAD_COLS.forEach(function(c){
var items=bl[c]||[];h+='<div class="kbc"><h4>'+c+' ('+items.length+')</h4>';
items.forEach(function(it,i){h+='<div class="kb-i" onclick="moveLead(\\''+id+'\\',\\''+c+'\\','+i+')"><div class="kb-n">'+it.n+'</div><div class="kb-s">'+it.s+'</div></div>'});
h+='</div>';});
h+='</div><div style="margin-top:10px"><button class="bq bq-o" onclick="addLead(\\''+id+'\\')">+ Add Lead</button></div>';
document.getElementById('ws-leads-c').innerHTML=h;
}
function addLead(id){
var n=prompt('Client name:');if(!n||!n.trim())return;
var s=prompt('Service/notes:')||'';var ld=getLD();if(!ld[id])ld[id]={};if(!ld[id]['New'])ld[id]['New']=[];
ld[id]['New'].push({n:n.trim(),s:s});setLD(ld);renderLeads(id);toast('Lead added');
}
function moveLead(id,col,i){
var ld=getLD();if(!ld[id])return;var items=ld[id][col]||[];if(i>=items.length)return;
var item=items.splice(i,1)[0];var idx=LEAD_COLS.indexOf(col);
if(idx>=LEAD_COLS.length-1){items.splice(i,0,item);return;}
var next=LEAD_COLS[idx+1];if(!ld[id][next])ld[id][next]=[];
ld[id][next].push(item);setLD(ld);renderLeads(id);toast('Moved to '+next);
}

var ALL_LEADS = ''' + leads_json + ''';

function renderOutreach(id){
var h='<div style="color:var(--t2);font-size:.82em;margin-bottom:8px">Available emails</div>';
var all=[];ALL_LEADS.forEach(function(l){all.push(l.e);});
if(all.length){var t=all.join('; ').replace(/'/g,"\\\\'");h+='<button class="bq bq-o" onclick="cp(\\''+t+'\\','+all.length+')" style="margin-bottom:10px">\\uD83D\\uDCCB Copy All</button>';}
h+='<div style="font-size:.78em;color:var(--t2)">'+all.length+' emails</div>';
document.getElementById('ws-outreach-c').innerHTML=h;
}

function getTasks(id){try{var d=JSON.parse(localStorage.getItem('wstasks'))||{};if(!d[id])d[id]={today:[],urgent:[],week:[]};return d[id]}catch(e){return{today:[],urgent:[],week:[]}}}
function setTasks(id,t){try{var d=JSON.parse(localStorage.getItem('wstasks'))||{};d[id]=t;localStorage.setItem('wstasks',JSON.stringify(d))}catch(e){}}

function renderTasks(id){
var t=getTasks(id);var cols=['today','urgent','week'];var lb=['Today','Urgent','This Week'];
var h='';cols.forEach(function(c,i){var items=t[c]||[];h+='<div class="ws-tcol"><h4>'+lb[i]+' ('+items.length+')</h4>';
items.forEach(function(item,j){h+='<div class="ws-ti" onclick="doneTask(\\''+id+'\\',\\''+c+'\\','+j+')">'+item+'</div>';});
h+='<button class="ws-add" onclick="addTask(\\''+id+'\\',\\''+c+'\\')">+ Add</button></div>';});
document.getElementById('ws-tasks-c').innerHTML=h;
}
function addTask(id,col){var t=getTasks(id);var n=prompt('Task:');if(!n||!n.trim())return;if(!t[col])t[col]=[];t[col].push(n.trim());setTasks(id,t);renderTasks(id);}
function doneTask(id,col,i){var t=getTasks(id);if(!t[col]||i>=t[col].length)return;t[col].splice(i,1);setTasks(id,t);renderTasks(id);toast('Done!');}

function renderNotes(id){var ta=document.getElementById('ws-notes-ta');try{ta.value=localStorage.getItem('wsn_'+id)||''}catch(e){}}
function saveWsNotes(){var id=document.getElementById('ws-name').textContent;var ta=document.getElementById('ws-notes-ta');try{localStorage.setItem('wsn_'+id,ta.value);document.getElementById('ws-notes-s').textContent='Saved'}catch(e){}}

function cp(text,count){
if(navigator.clipboard&&navigator.clipboard.writeText){
navigator.clipboard.writeText(text).then(function(){toast(count+' emails copied')}).catch(function(){fb(text)});
}else{fb(text)}}
function fb(t){var ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');toast('Copied')}catch(e){toast('Error')}document.body.removeChild(ta);}
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('show')},2500)}
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

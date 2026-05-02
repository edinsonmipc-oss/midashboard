#!/usr/bin/env python3
"""generate.py — Lee data/*.json y genera index.html con leads, ideas y health."""

import json, os
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(name):
    path = os.path.join(DIR, "data", name)
    with open(path) as f:
        return json.load(f)

def status_color(status):
    return {"activo": "limegreen", "pendiente": "orange", "idea": "#888", "completado": "royalblue"}.get(status, "#888")

def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def generate():
    projects = load_json("projects.json")
    changelog = load_json("changelog.json")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # --- Project cards ---
    cards = ""
    activos = pendientes = ideas = 0
    for p in projects["projects"]:
        if p["status"] == "activo": activos += 1
        elif p["status"] == "pendiente": pendientes += 1
        elif p["status"] == "idea": ideas += 1
        metrics = "".join(f'<div class="metric"><span class="metric-label">{k.replace("_"," ").title()}</span><span class="metric-value">{v}</span></div>'
                          for k, v in p.get("metrics", {}).items()) if p.get("metrics") else '<div class="metric" style="color:#666">Sin métricas aún</div>'
        steps = "".join(f'<li>{"✅" if i < 1 else "⬜"} {html_escape(s)}</li>' for i, s in enumerate(p.get("next_steps", []))) if p.get("next_steps") else '<li style="color:#666">Sin pasos definidos</li>'
        url_link = f'<a href="{p["url"]}" target="_blank" style="color:#4af;font-size:0.85em">🌐 {p["url"]}</a>' if p.get("url") else ""
        sc = status_color(p["status"])
        cards += f"""
    <div class="card" style="border-left: 4px solid {sc}">
        <div class="card-header">
            <span style="font-size:1.5em">{p['emoji']}</span>
            <h2>{p['name']}</h2>
            <span class="badge" style="background:{sc}">{p['status'].upper()}</span>
        </div>
        <p style="color:#aaa;margin:8px 0 12px">{p['description']}</p>
        {url_link}
        <div class="metrics-grid">{metrics}</div>
        <div class="section-title">📋 Próximos Pasos</div>
        <ul class="steps">{steps}</ul>
        {f'<div class="note">📝 {html_escape(p["notes"])}</div>' if p.get("notes") else ''}
    </div>"""

    total_projects = len(projects["projects"])

    # --- Changelog ---
    log_entries = ""
    for e in changelog["entries"][:25]:
        emoji = {"mejora": "🔧", "creacion": "✨", "infra": "⚙️", "analisis": "📊", "idea": "💡"}.get(e["type"], "📌")
        log_entries += f"""
    <div class="log-entry">
        <span class="log-date">{e["date"]}</span>
        <span class="log-emoji">{emoji}</span>
        <span class="log-project">[{e["project"]}]</span>
        <span class="log-text">{html_escape(e["text"])}</span>
    </div>"""

    # --- Leads section ---
    leads_data = load_json("leads.json")
    total_leads = leads_data.get("total_leads", 0)
    lead_cards = ""
    for date_key in sorted(leads_data.get("leads_by_date", {}).keys(), reverse=True)[:7]:
        day_leads = leads_data["leads_by_date"][date_key]
        typs = {}
        for l in day_leads:
            t = l.get("type", "other")
            typs[t] = typs.get(t, 0) + 1
        type_badges = "".join(f'<span class="stat-pill" style="border-color:#ff6b6b">{t}: {n}</span>' for t, n in sorted(typs.items()))
        lead_rows = ""
        for l in day_leads:
            lead_rows += f"""
            <tr>
                <td style="color:#e0e0e0">{html_escape(l['company'])}</td>
                <td><a href="mailto:{html_escape(l['email'])}" style="color:#4af;font-size:0.85em">{html_escape(l['email'])}</a></td>
                <td style="color:#888;font-size:0.8em">{html_escape(l.get('website',''))}</td>
                <td style="color:#888;font-size:0.8em">{html_escape(l.get('notes',''))}</td>
            </tr>"""
        lead_cards += f"""
    <div class="card" style="border-left:4px solid #ff6b6b">
        <div class="card-header">
            <span style="font-size:1.2em">📅</span>
            <h2 style="font-size:0.95em">Leads — {date_key}</h2>
            <span class="badge" style="background:#ff6b6b">{len(day_leads)} leads</span>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin:8px 0">{type_badges}</div>
        <table style="width:100%;border-collapse:collapse;font-size:0.85em">
            <thead><tr style="border-bottom:1px solid #1a1a2e">
                <th style="padding:6px 4px;text-align:left;color:#888">Empresa</th>
                <th style="padding:6px 4px;text-align:left;color:#888">Email</th>
                <th style="padding:6px 4px;text-align:left;color:#888">Web</th>
                <th style="padding:6px 4px;text-align:left;color:#888">Notas</th>
            </tr></thead>
            <tbody>{lead_rows}</tbody>
        </table>
    </div>"""

    if not lead_cards:
        lead_cards = """
    <div class="card" style="border-left:4px solid #ff6b6b">
        <p style="color:#888;text-align:center;padding:12px">No hay leads aún. La generación automática comenzará pronto.</p>
    </div>"""

    # --- Health & Improvements ---
    health = load_json("health.json")
    health_cards = ""
    for site in health.get("sites", []):
        status_icon = "✅" if site["status"] == "online" else "❌"
        status_clr = "limegreen" if site["status"] == "online" else "#ff6b6b"
        issues = "".join(f'<li style="color:#ff6b6b;font-size:0.85em">⚠️ {html_escape(i)}</li>' for i in site.get("issues", [])) or '<li style="color:#888;font-size:0.85em">✅ Sin issues</li>'
        improvements = "".join(f'<li style="color:#aaa;font-size:0.85em">💡 {html_escape(i)}</li>' for i in site.get("improvements", [])) or '<li style="color:#888;font-size:0.85em">Sin mejoras sugeridas</li>'
        seo_html = ""
        if site.get("seo_metrics"):
            seo_items = "".join(f'<div class="metric"><span class="metric-label">{k.replace("_"," ").title()}</span><span class="metric-value">{v}</span></div>' for k,v in site["seo_metrics"].items())
            seo_html = f'<div class="metrics-grid" style="margin-top:8px">{seo_items}</div>'
        health_cards += f"""
    <div class="card" style="border-left:4px solid {status_clr}">
        <div class="card-header">
            <span style="font-size:1.2em">{status_icon}</span>
            <h2 style="font-size:0.95em">{html_escape(site['name'])}</h2>
            <span class="badge" style="background:{status_clr}">{site['status'].upper()}</span>
        </div>
        <div style="display:flex;gap:12px;margin:8px 0;flex-wrap:wrap;font-size:0.8em;color:#888">
            <span>🔗 <a href="{site['url']}" target="_blank" style="color:#4af">{site['url']}</a></span>
            <span>⏱️ Uptime: {site.get('uptime_24h','N/A')}</span>
            <span>🕐 {site.get('last_checked','')}</span>
        </div>
        {seo_html}
        <div class="section-title">⚠️ Issues</div>
        <ul class="steps">{issues}</ul>
        <div class="section-title">💡 Mejoras Sugeridas</div>
        <ul class="steps">{improvements}</ul>
    </div>"""

    # --- Digital Ideas ---
    ideas_data = load_json("ideas.json")
    idea_cards = ""
    for idea in ideas_data.get("ideas", []):
        sc = status_color(idea["status"])
        idea_cards += f"""
    <div class="card" style="border-left:4px solid #7b68ee">
        <div class="card-header">
            <span style="font-size:1.2em">{idea['emoji']}</span>
            <h2 style="font-size:0.95em">{html_escape(idea['name'])}</h2>
            <span class="badge" style="background:#7b68ee">{idea.get('potential','').upper()}</span>
            <span class="badge" style="background:{sc};font-size:0.6em">{idea['status'].upper()}</span>
        </div>
        <p style="color:#aaa;margin:8px 0;font-size:0.9em">{html_escape(idea['description'])}</p>
        <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:0.8em;color:#888">
            <span>⏱️ {idea.get('timeline','?')}</span>
            <span>🔧 Esfuerzo: {idea.get('effort','?')}</span>
        </div>
        {f'<div class="note" style="margin-top:8px">💭 ' + html_escape(idea["notes"]) + '</div>' if idea.get("notes") else ''}
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Hermes Dashboard — Edinson</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#0a0a0f; color:#e0e0e0; min-height:100vh; }}
        .container {{ max-width:960px; margin:0 auto; padding:16px; }}
        header {{ text-align:center; padding:24px 0 16px; border-bottom:1px solid #1a1a2e; margin-bottom:20px; }}
        header h1 {{ font-size:1.5em; background:linear-gradient(135deg,#4af,#7b68ee); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        header .subtitle {{ color:#666; font-size:0.85em; margin-top:4px; }}
        header .updated {{ color:#555; font-size:0.75em; margin-top:8px; }}
        header .url {{ margin-top:6px; }}
        header .url a {{ color:#4af; font-size:0.8em; text-decoration:none; opacity:0.7; }}
        .grid {{ display:flex; flex-direction:column; gap:16px; }}
        .card {{ background:#11111a; border-radius:12px; padding:16px; border:1px solid #1a1a2e; }}
        .card-header {{ display:flex; align-items:center; gap:10px; margin-bottom:4px; flex-wrap:wrap; }}
        .card-header h2 {{ font-size:1.1em; flex:1; }}
        .badge {{ font-size:0.65em; padding:2px 8px; border-radius:8px; color:white; font-weight:600; letter-spacing:0.5px; }}
        .metrics-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:8px; margin:10px 0; }}
        .metric {{ background:#0d0d16; border-radius:8px; padding:8px; text-align:center; }}
        .metric-label {{ display:block; font-size:0.65em; color:#888; text-transform:capitalize; }}
        .metric-value {{ display:block; font-size:1em; color:#4af; font-weight:600; margin-top:2px; }}
        .section-title {{ color:#888; font-size:0.85em; margin:12px 0 6px; text-transform:uppercase; letter-spacing:1px; }}
        .steps {{ list-style:none; padding:0; }}
        .steps li {{ padding:4px 0; font-size:0.9em; color:#ccc; }}
        .note {{ background:#1a1a2e; border-radius:6px; padding:8px; font-size:0.85em; color:#888; margin-top:8px; }}
        .changelog {{ margin-top:20px; }}
        .log-entry {{ display:flex; align-items:flex-start; gap:6px; padding:6px 0; border-bottom:1px solid #0d0d16; font-size:0.85em; flex-wrap:wrap; }}
        .log-date {{ color:#555; font-size:0.8em; white-space:nowrap; min-width:80px; }}
        .log-emoji {{ flex-shrink:0; }}
        .log-project {{ color:#7b68ee; flex-shrink:0; }}
        .log-text {{ color:#aaa; flex:1; }}
        .stats-bar {{ display:flex; gap:12px; justify-content:center; margin:12px 0; flex-wrap:wrap; }}
        .stat-pill {{ background:#11111a; border:1px solid #1a1a2e; border-radius:16px; padding:4px 12px; font-size:0.8em; }}
        .section-header {{ color:#888; font-size:1em; margin:24px 0 12px; padding-bottom:6px; border-bottom:1px solid #1a1a2e; display:flex; align-items:center; gap:8px; }}
        @media (max-width:480px) {{
            .metrics-grid {{ grid-template-columns:repeat(2,1fr); }}
            .card-header h2 {{ font-size:1em; }}
        }}
        table {{ width:100%; border-collapse:collapse; font-size:0.85em; }}
        th {{ padding:6px 4px; text-align:left; color:#888; border-bottom:1px solid #1a1a2e; }}
        td {{ padding:5px 4px; border-bottom:1px solid #0d0d16; }}
        tr:hover td {{ background:#14141e; }}
        .tabs {{ display:flex; gap:4px; margin:12px 0; flex-wrap:wrap; }}
        .tab {{ background:#11111a; border:1px solid #1a1a2e; border-radius:8px; padding:6px 14px; font-size:0.8em; color:#888; cursor:pointer; }}
        .tab.active {{ border-color:#4af; color:#4af; }}
        .tab:hover {{ border-color:#555; }}
        .copy-btn {{ background:#1a1a2e; border:none; border-radius:4px; color:#4af; font-size:0.75em; padding:2px 6px; cursor:pointer; }}
        .copy-btn:hover {{ background:#2a2a3e; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Hermes Dashboard</h1>
            <div class="subtitle">Edinson Angarita — Proyectos & Crecimiento</div>
            <div class="url"><a href="https://edinsonmipc-oss.github.io/midashboard/" target="_blank">🔗 edinsonmipc-oss.github.io/midashboard</a></div>
            <div class="updated">🕐 Actualizado: {now} (actualización automática 2x/día)</div>
            <div class="stats-bar">
                <span class="stat-pill">📊 {total_projects} proyectos</span>
                <span class="stat-pill" style="border-color:limegreen">✅ {activos} activos</span>
                <span class="stat-pill" style="border-color:orange">⏳ {pendientes} pendientes</span>
                <span class="stat-pill" style="border-color:#888">💡 {ideas} ideas</span>
                <span class="stat-pill" style="border-color:#ff6b6b">🎯 {total_leads} leads</span>
            </div>
        </header>

        <h3 class="section-header">🛠️ Proyectos</h3>
        <div class="grid">{cards}</div>

        <h3 class="section-header">🎯 Leads Generados</h3>
        <div class="grid">{lead_cards}</div>

        <h3 class="section-header">💡 Ideas de Negocio Digital</h3>
        <div class="grid">{idea_cards}</div>

        <h3 class="section-header">🔍 Salud del Sitio & Mejoras</h3>
        <div class="grid">{health_cards}</div>

        <div class="changelog">
            <h3 style="margin-bottom:8px;color:#888;font-size:0.9em;">📜 Changelog — Últimas actualizaciones</h3>
            {log_entries}
        </div>

        <footer style="text-align:center;padding:24px 0 16px;color:#444;font-size:0.75em;border-top:1px solid #1a1a2e;margin-top:24px;">
            Hermes Agent · Dashboard vivo · Actualización automática 2 veces al día
        </footer>
    </div>
</body>
</html>"""

    path = os.path.join(DIR, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print(f"✅ Dashboard generado: {path} ({len(html)} bytes)")
    return True

if __name__ == "__main__":
    generate()

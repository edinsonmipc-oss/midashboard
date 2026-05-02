#!/usr/bin/env python3
"""generate.py — Lee data/*.json y genera index.html automáticamente."""

import json, os
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(name):
    path = os.path.join(DIR, "data", name)
    with open(path) as f:
        return json.load(f)

def status_color(status):
    return {"activo": "limegreen", "pendiente": "orange", "idea": "#888", "completado": "royalblue"}.get(status, "#888")

def generate():
    projects = load_json("projects.json")
    changelog = load_json("changelog.json")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # --- Build HTML ---
    cards = ""
    for p in projects["projects"]:
        metrics = "".join(f'<div class="metric"><span class="metric-label">{k.replace("_"," ").title()}</span><span class="metric-value">{v}</span></div>'
                          for k, v in p.get("metrics", {}).items()) if p.get("metrics") else '<div class="metric" style="color:#666">Sin métricas aún</div>'
        steps = "".join(f'<li>{"✅" if i < 1 else "⬜"} {s}</li>' for i, s in enumerate(p.get("next_steps", []))) if p.get("next_steps") else '<li style="color:#666">Sin pasos definidos</li>'
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
        {f'<div class="note">📝 {p["notes"]}</div>' if p.get("notes") else ''}
    </div>"""

    # Changelog
    log_entries = ""
    for e in changelog["entries"][:20]:  # last 20
        emoji = {"mejora": "🔧", "creacion": "✨", "infra": "⚙️", "analisis": "📊", "idea": "💡"}.get(e["type"], "📌")
        log_entries += f"""
    <div class="log-entry">
        <span class="log-date">{e["date"]}</span>
        <span class="log-emoji">{emoji}</span>
        <span class="log-project">[{e["project"]}]</span>
        <span class="log-text">{e["text"]}</span>
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
        .container {{ max-width:900px; margin:0 auto; padding:16px; }}
        header {{ text-align:center; padding:24px 0 16px; border-bottom:1px solid #1a1a2e; margin-bottom:20px; }}
        header h1 {{ font-size:1.5em; background:linear-gradient(135deg,#4af,#7b68ee); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        header .subtitle {{ color:#666; font-size:0.85em; margin-top:4px; }}
        header .updated {{ color:#555; font-size:0.75em; margin-top:8px; }}
        header .url {{ margin-top:8px; }}
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
        .lead-section {{ margin-top:20px; }}
        @media (max-width:480px) {{
            .metrics-grid {{ grid-template-columns:repeat(2,1fr); }}
            .card-header h2 {{ font-size:1em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Hermes Dashboard</h1>
            <div class="subtitle">Edinson Angarita — Proyectos & Crecimiento</div>
            <div class="url"><a href="https://edinsonmipc-oss.github.io/midashboard/" target="_blank">🔗 edinsonmipc-oss.github.io/midashboard</a></div>
            <div class="url" style="margin-top:2px"><a href="https://organ-description-herbal-garlic.trycloudflare.com" target="_blank" style="color:#7b68ee">🔄 trycloudflare.com (respaldo)</a></div>
            <div class="updated">🕐 Actualizado: {now} (actualización automática diaria)</div>
            <div class="stats-bar">
                <span class="stat-pill">📊 {projects['stats']['total_projects']} proyectos</span>
                <span class="stat-pill" style="border-color:limegreen">✅ {projects['stats']['activos']} activos</span>
                <span class="stat-pill" style="border-color:orange">⏳ {projects['stats']['pendientes']} pendientes</span>
                <span class="stat-pill" style="border-color:#888">💡 {projects['stats']['ideas']} ideas</span>
            </div>
        </header>

        <div class="grid">
            {cards}
        </div>

        <div class="changelog">
            <h3 style="margin-bottom:8px;color:#888;font-size:0.9em;">📜 Changelog — Últimas actualizaciones</h3>
            {log_entries}
        </div>

        <div class="lead-section">
            <h3 style="margin-bottom:8px;color:#888;font-size:0.9em;">🎯 Lead Generation Targets</h3>
            <div class="card" style="border-left:4px solid #ff6b6b">
                <p style="font-size:0.9em;color:#aaa;margin-bottom:8px;">Buscando builders, contractors y real estate en Melbourne para ofrecer servicios de Prime Property Maintenance, Antonio Paving y más.</p>
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    <span class="stat-pill" style="border-color:#ff6b6b">🏗️ Builders: 0 contactados</span>
                    <span class="stat-pill" style="border-color:#ff6b6b">🔨 Contractors: 0 contactados</span>
                    <span class="stat-pill" style="border-color:#ff6b6b">🏢 Real Estate: 0 contactados</span>
                </div>
            </div>
        </div>

        <footer style="text-align:center;padding:24px 0 16px;color:#444;font-size:0.75em;border-top:1px solid #1a1a2e;margin-top:24px;">
            Hermes Agent · Dashboard vivo · Actualización automática diaria
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

#!/usr/bin/env python3
"""generate.py — Dashboard vivo con UI interactiva y copy de leads para email"""

import json, os
from datetime import datetime, date

DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(name):
    path = os.path.join(DIR, "data", name)
    with open(path) as f:
        return json.load(f)

def html_escape(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def esc(s):
    return html_escape(str(s))

def generate():
    projects = load_json("projects.json")
    changelog = load_json("changelog.json")
    leads_data = load_json("leads.json")
    health = load_json("health.json")
    ideas_data = load_json("ideas.json")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_str = date.today().isoformat()

    # ── Stats ──
    activos = sum(1 for p in projects["projects"] if p["status"] == "activo")
    pendientes = sum(1 for p in projects["projects"] if p["status"] == "pendiente")
    ideas_count = sum(1 for p in projects["projects"] if p["status"] == "idea")
    total_leads = leads_data.get("total_leads", 0)
    sites_online = sum(1 for s in health["sites"] if s["status"] == "online")
    sites_total = len(health["sites"])

    # ── Project Cards ──
    cards_html = ""
    for p in projects["projects"]:
        sc = {"activo": "#34d399", "pendiente": "#fbbf24", "idea": "#888", "completado": "#60a5fa"}.get(p["status"], "#888")
        metrics = "".join(
            f'<div class="metric"><span class="ml">{esc(k.replace("_"," ").title())}</span><span class="mv">{esc(v)}</span></div>'
            for k, v in p.get("metrics", {}).items()
        ) if p.get("metrics") else ""
        steps = "".join(
            f'<li class="{"done" if i<1 else ""}">{"✅" if i<1 else "○"} {esc(s)}</li>'
            for i, s in enumerate(p.get("next_steps", []))
        ) if p.get("next_steps") else ""
        link = f'<a href="{esc(p["url"])}" target="_blank" class="plink">{esc(p["url"])}</a>' if p.get("url") else ""
        cards_html += f"""
    <div class="card pc" style="--accent:{sc}">
        <div class="pch">
            <span class="pemoji">{p['emoji']}</span>
            <h3>{esc(p['name'])}</h3>
            <span class="badge" style="background:{sc}">{p['status'].upper()}</span>
        </div>
        <p class="pdesc">{esc(p['description'])}</p>
        {link}
        {f'<div class="mg">{metrics}</div>' if metrics else ''}
        {f'<ul class="steps">{steps}</ul>' if steps else ''}
        {f'<div class="note">📝 {esc(p["notes"])}</div>' if p.get("notes") else ''}
    </div>"""

    # ── Leads Section ──
    # Build today's leads separately
    today_leads = leads_data.get("leads_by_date", {}).get(today_str, [])
    # All recent leads (last 7 days)
    recent_dates = sorted(leads_data.get("leads_by_date", {}).keys(), reverse=True)[:7]

    # Build email-ready text for today's leads
    today_email_text = "\n".join(
        f"{l['company']} <{l['email']}> — {l.get('notes','')}"
        for l in today_leads
    ) if today_leads else "No hay leads para hoy"

    # All leads email text (all dates)
    all_email_parts = []
    for d in recent_dates:
        for l in leads_data["leads_by_date"][d]:
            all_email_parts.append(f"{l['company']} <{l['email']}> — {l.get('notes','')}")
    all_email_text = "\n".join(all_email_parts) if all_email_parts else "No hay leads"

    leads_html = ""
    for date_key in recent_dates:
        day_leads = leads_data["leads_by_date"][date_key]
        typs = {}
        for l in day_leads:
            t = l.get("type", "other")
            typs[t] = typs.get(t, 0) + 1
        type_badges = "".join(
            f'<span class="tp">{esc(t)} <b>{n}</b></span>' for t, n in sorted(typs.items())
        )
        is_today = date_key == today_str
        rows = ""
        for l in day_leads:
            rows += f"""
            <tr class="lr">
                <td class="lc">{esc(l['company'])}</td>
                <td><a href="mailto:{esc(l['email'])}" class="le">{esc(l['email'])}</a></td>
                <td class="lt">{esc(l.get('type',''))}</td>
                <td class="ln">{esc(l.get('notes',''))}</td>
            </tr>"""
        leads_html += f"""
    <div class="card ldc" data-date="{date_key}"{" data-today" if is_today else ""}>
        <div class="pch">
            <span class="ld-label">{"🔴 HOY" if is_today else "📅"}</span>
            <h3 style="font-size:0.95em;flex:1">{date_key}</h3>
            <span class="badge" style="background:{"#ef4444" if is_today else "#6366f1"}">{len(day_leads)} leads</span>
        </div>
        <div class="tp-wrap">{type_badges}</div>
        <div class="tbl-wrap">
            <table class="ltbl">
                <thead><tr><th>Empresa</th><th>Email</th><th>Tipo</th><th>Notas</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>"""

    if not leads_html:
        leads_html = '<div class="card" style="text-align:center;padding:32px;color:#666"><p>No hay leads aún. La generación automática comenzará pronto.</p></div>'

    # ── Health Cards ──
    health_cards = ""
    for site in health.get("sites", []):
        up = site["status"] == "online"
        issues = "".join(
            f'<li class="iss">⚠️ {esc(site.get("name",""))}: {esc(i)}</li>'
            for i in site.get("issues", [])
        ) if site.get("issues") else '<li class="iss" style="color:#666">✅ Sin issues</li>'
        seo_html = ""
        if site.get("seo_metrics"):
            seo_items = "".join(
                f'<div class="metric"><span class="ml">{esc(k.replace("_"," ").title())}</span><span class="mv">{esc(v)}</span></div>'
                for k, v in site["seo_metrics"].items()
            )
            seo_html = f'<div class="mg">{seo_items}</div>'
        health_cards += f"""
    <div class="card hc" style="--accent:{"#34d399" if up else "#ef4444"}">
        <div class="pch">
            <span class="hdot" style="background:{"#34d399" if up else "#ef4444"}"></span>
            <h3 style="font-size:0.95em">{esc(site['name'])}</h3>
            <span class="badge" style="background:{"#34d399" if up else "#ef4444"}">{'ONLINE' if up else 'OFFLINE'}</span>
        </div>
        <div class="hmeta">
            <a href="{esc(site['url'])}" target="_blank" class="plink">{esc(site['url'])}</a>
            <span>⏱️ {esc(site.get('uptime_24h','?'))}</span>
            <span>🕐 {esc(site.get('last_checked',''))}</span>
        </div>
        {seo_html}
        <ul class="steps">{issues}</ul>
    </div>"""

    # ── Ideas ──
    idea_cards = ""
    for idea in ideas_data.get("ideas", []):
        potentials = {"Alto": "#34d399", "Muy Alto": "#60a5fa", "Medio": "#fbbf24", "Bajo": "#888"}
        pc = "var(--accent)"
        idea_cards += f"""
    <div class="card ic" style="--accent:#7c3aed">
        <div class="pch">
            <span>{idea['emoji']}</span>
            <h3 style="font-size:0.95em;flex:1">{esc(idea['name'])}</h3>
            <span class="badge" style="background:{potentials.get(idea.get('potential',''),'#888')}">{esc(idea.get('potential',''))}</span>
        </div>
        <p class="pdesc">{esc(idea['description'])}</p>
        <div class="hmeta">
            <span>⏱️ {esc(idea.get('timeline','?'))}</span>
            <span>🔧 {esc(idea.get('effort','?'))}</span>
        </div>
        {f'<div class="note">💭 {esc(idea["notes"])}</div>' if idea.get("notes") else ''}
    </div>"""

    # ── Changelog ──
    log_entries = ""
    emoji_map = {"mejora": "🔧", "creacion": "✨", "infra": "⚙️", "analisis": "📊", "idea": "💡"}
    for e in changelog["entries"][:20]:
        em = emoji_map.get(e["type"], "📌")
        log_entries += f"""
    <div class="le">
        <span class="ledate">{esc(e['date'])}</span>
        <span>{em}</span>
        <span class="leproj">[{esc(e['project'])}]</span>
        <span class="letext">{esc(e['text'])}</span>
    </div>"""

    # ── SVG icons inline ──
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>Hermes Dashboard</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif; background:#0a0a0f; color:#e4e4e7; min-height:100vh }}
        .c {{ max-width:1000px; margin:0 auto; padding:16px }}
        ::selection {{ background:#6366f1; color:#fff }}

        /* ── Header ── */
        header {{ text-align:center; padding:28px 0 20px; margin-bottom:20px; position:relative }}
        header::after {{ content:''; display:block; width:60px; height:3px; background:linear-gradient(90deg,#6366f1,#a78bfa); border-radius:2px; margin:16px auto 0 }}
        h1 {{ font-size:1.6em; font-weight:700; background:linear-gradient(135deg,#e4e4e7,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent }}
        .sub {{ color:#71717a; font-size:0.85em; margin-top:4px }}
        .upd {{ color:#52525b; font-size:0.7em; margin-top:8px }}

        /* ── Stats Bar ── */
        .sb {{ display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin:12px 0 20px }}
        .sp {{ background:#111118; border:1px solid #1c1c24; border-radius:20px; padding:6px 14px; font-size:0.8em; color:#a1a1aa; display:flex; align-items:center; gap:5px }}
        .sp b {{ color:#e4e4e7 }}

        /* ── Section headers ── */
        .sh {{ color:#71717a; font-size:0.85em; margin:28px 0 12px; padding-bottom:8px; border-bottom:1px solid #1c1c24; display:flex; align-items:center; gap:8px; letter-spacing:0.3px; text-transform:uppercase; font-weight:600 }}
        .sh-actions {{ margin-left:auto; display:flex; gap:6px }}

        /* ── Buttons ── */
        .btn {{ display:inline-flex; align-items:center; gap:5px; background:#1c1c24; border:1px solid #27272a; color:#a1a1aa; padding:5px 12px; border-radius:8px; font-size:0.75em; cursor:pointer; transition:all .15s; font-family:inherit }}
        .btn:hover {{ background:#27272a; border-color:#3f3f46; color:#e4e4e7 }}
        .btn:active {{ transform:scale(.96) }}
        .btn-p {{ background:#6366f1; border-color:#6366f1; color:#fff }}
        .btn-p:hover {{ background:#818cf8; border-color:#818cf8; color:#fff }}
        .btn-s {{ background:#10b981; border-color:#10b981; color:#fff }}
        .btn-s:hover {{ background:#34d399; border-color:#34d399; color:#fff }}
        .copied {{ background:#10b981 !important; border-color:#10b981 !important; color:#fff !important }}

        /* ── Cards ── */
        .grid {{ display:flex; flex-direction:column; gap:12px }}
        .card {{ background:#111118; border-radius:14px; padding:18px; border:1px solid #1c1c24; transition:border-color .15s,box-shadow .15s }}
        .card:hover {{ border-color:#27272a; box-shadow:0 4px 20px rgba(0,0,0,.3) }}
        .pc {{ border-left:3px solid var(--accent,#888) }}
        .pch {{ display:flex; align-items:center; gap:10px; margin-bottom:6px }}
        .pch h3 {{ font-size:1.05em; font-weight:600 }}
        .pemoji {{ font-size:1.4em }}
        .pdesc {{ color:#a1a1aa; font-size:0.85em; margin:4px 0 8px; line-height:1.5 }}
        .badge {{ font-size:0.6em; padding:2px 10px; border-radius:10px; color:#fff; font-weight:600; letter-spacing:.4px; white-space:nowrap }}
        .mg {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr)); gap:6px; margin:10px 0 }}
        .metric {{ background:#0d0d14; border-radius:8px; padding:8px; text-align:center }}
        .ml {{ display:block; font-size:0.6em; color:#71717a; text-transform:uppercase; letter-spacing:.3px }}
        .mv {{ display:block; font-size:1em; color:#a78bfa; font-weight:600; margin-top:2px }}
        .steps {{ list-style:none; padding:0; margin-top:6px }}
        .steps li {{ padding:3px 0; font-size:0.83em; color:#a1a1aa }}
        .steps li.done {{ color:#e4e4e7 }}
        .note {{ background:#0d0d14; border-radius:8px; padding:8px 10px; font-size:0.82em; color:#a1a1aa; margin-top:8px }}
        .plink {{ color:#818cf8; font-size:0.8em; text-decoration:none; display:inline-block; margin:4px 0 }}
        .plink:hover {{ text-decoration:underline }}

        /* ── Leads ── */
        .ldc {{ border-left:3px solid var(--accent,#6366f1) }}
        .ldc[data-today] {{ border-left-color:#ef4444; border-color:#2a1a1a }}
        .ld-label {{ font-size:0.7em; font-weight:700; letter-spacing:.5px }}
        .tp-wrap {{ display:flex; gap:5px; flex-wrap:wrap; margin:6px 0 10px }}
        .tp {{ background:#0d0d14; border:1px solid #1c1c24; border-radius:12px; padding:2px 10px; font-size:0.72em; color:#a1a1aa }}
        .tp b {{ color:#e4e4e7 }}
        .tbl-wrap {{ overflow-x:auto }}
        .ltbl {{ width:100%; border-collapse:collapse; font-size:0.82em }}
        .ltbl th {{ padding:7px 6px; text-align:left; color:#71717a; border-bottom:1px solid #1c1c24; font-weight:500; font-size:0.75em; text-transform:uppercase; letter-spacing:.3px; white-space:nowrap }}
        .ltbl td {{ padding:6px; border-bottom:1px solid #0d0d14; vertical-align:top }}
        .ltbl tr:hover td {{ background:#14141e }}
        .lc {{ color:#e4e4e7; font-weight:500; white-space:nowrap }}
        .le {{ color:#818cf8; text-decoration:none; font-size:0.9em }}
        .le:hover {{ text-decoration:underline }}
        .lt {{ color:#71717a; font-size:0.8em; white-space:nowrap }}
        .ln {{ color:#a1a1aa; font-size:0.85em }}

        /* ── Health ── */
        .hc {{ border-left:3px solid var(--accent) }}
        .hdot {{ width:8px; height:8px; border-radius:50%; display:inline-block; flex-shrink:0; animation:pulse 2s infinite }}
        @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.5}} }}
        .hmeta {{ display:flex; gap:12px; flex-wrap:wrap; font-size:0.75em; color:#71717a; margin:6px 0 10px }}
        .hmeta a {{ color:#818cf8; text-decoration:none }}
        .hmeta a:hover {{ text-decoration:underline }}
        .iss {{ padding:2px 0; font-size:0.82em; color:#fca5a5 }}

        /* ── Ideas ── */
        .ic {{ border-left:3px solid var(--accent) }}

        /* ── Changelog ── */
        .cl {{ margin-top:24px }}
        .le {{ display:flex; align-items:flex-start; gap:6px; padding:5px 0; border-bottom:1px solid #0d0d14; font-size:0.82em; flex-wrap:wrap }}
        .ledate {{ color:#52525b; font-size:0.85em; white-space:nowrap; min-width:72px }}
        .leproj {{ color:#7c3aed; flex-shrink:0; font-size:0.85em }}
        .letext {{ color:#a1a1aa; flex:1 }}

        /* ── Footer ── */
        footer {{ text-align:center; padding:24px 0 16px; color:#3f3f46; font-size:0.7em; border-top:1px solid #1c1c24; margin-top:24px }}

        /* ── Toast ── */
        #toast {{ position:fixed; bottom:24px; left:50%; transform:translateX(-50%) translateY(80px); background:#10b981; color:#fff; padding:10px 20px; border-radius:12px; font-size:0.85em; opacity:0; transition:all .3s; pointer-events:none; z-index:999; box-shadow:0 4px 20px rgba(0,0,0,.5) }}
        #toast.show {{ opacity:1; transform:translateX(-50%) translateY(0) }}

        /* ── Responsive ── */
        @media (max-width:600px) {{
            .card {{ padding:14px }}
            .mg {{ grid-template-columns:repeat(2,1fr) }}
            .sb {{ gap:5px }}
            .sp {{ font-size:0.72em; padding:4px 10px }}
            .ltbl {{ font-size:0.75em }}
            .lc {{ white-space:normal }}
            .lt {{ white-space:normal }}
            .btn {{ font-size:0.7em; padding:4px 8px }}
            h1 {{ font-size:1.3em }}
        }}
    </style>
</head>
<body>
    <div class="c">
        <header>
            <h1>🚀 Hermes Dashboard</h1>
            <div class="sub">Edinson Angarita — Proyectos & Crecimiento</div>
            <div class="upd">🕐 {now}</div>
        </header>

        <div class="sb">
            <span class="sp">📊 <b>{len(projects['projects'])}</b> proyectos</span>
            <span class="sp">✅ <b>{activos}</b> activos</span>
            <span class="sp">⏳ <b>{pendientes}</b> pendientes</span>
            <span class="sp">💡 <b>{ideas_count}</b> ideas</span>
            <span class="sp" style="border-color:#6366f1">🎯 <b>{total_leads}</b> leads</span>
            <span class="sp" style="border-color:{"#34d399" if sites_online==sites_total else "#ef4444"}">🔍 <b>{sites_online}/{sites_total}</b> online</span>
        </div>

        <!-- ═══ PROYECTOS ═══ -->
        <div class="sh">🛠️ Proyectos</div>
        <div class="grid">{cards_html}</div>

        <!-- ═══ LEADS ═══ -->
        <div class="sh" style="border-color:#27272a">
            🎯 Leads Generados
            <div class="sh-actions">
                <button class="btn btn-s" onclick="copyLeads(event,'today')" title="Copia HOY en formato email">📋 Copiar Hoy</button>
                <button class="btn btn-p" onclick="copyLeads(event,'all')" title="Copia TODOS los leads recientes">📋 Copiar Todos</button>
            </div>
        </div>
        <div class="grid">{leads_html}</div>

        <!-- ═══ SITE HEALTH ═══ -->
        <div class="sh">🔍 Salud de los Sitios</div>
        <div class="grid">{health_cards}</div>

        <!-- ═══ IDEAS ═══ -->
        <div class="sh">💡 Ideas de Negocio Digital</div>
        <div class="grid">{idea_cards}</div>

        <!-- ═══ CHANGELOG ═══ -->
        <div class="cl">
            <div class="sh">📜 Últimas Actualizaciones</div>
            {log_entries}
        </div>

        <footer>Hermes Agent · Dashboard vivo · Actualización automática 2x/día</footer>
    </div>

    <div id="toast"></div>

    <script>
    // ── Data for copy ──
    var LEAD_DATA = {json.dumps({
        "today": [{
            "company": l["company"],
            "email": l["email"],
            "notes": l.get("notes", "")
        } for l in today_leads],
        "all": [{
            "company": l["company"],
            "email": l["email"],
            "notes": l.get("notes", "")
        } for d in recent_dates for l in leads_data["leads_by_date"][d]]
    })};

    function copyLeads(e, mode) {{
        var data = LEAD_DATA[mode];
        if (!data || data.length === 0) {{
            showToast("⚠️ No hay leads para copiar");
            return;
        }}
        // Email-ready format: Company <email> — Notes
        var text = data.map(function(l) {{
            return l.company + " <" + l.email + "> — " + (l.notes || "");
        }}).join("\\n");
        // Also add a subject-friendly summary
        var summary = "📋 " + data.length + " leads" + (mode === "today" ? " (Hoy)" : " (recientes)") + "\\n\\n";
        text = summary + text;

        if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(text).then(function() {{
                showToast("✅ " + data.length + " leads copiados — listos para pegar en email");
            }}).catch(function() {{
                fallbackCopy(text);
            }});
        }} else {{
            fallbackCopy(text);
        }}

        // Visual feedback on button
        var btn = e.currentTarget;
        btn.classList.add("copied");
        var orig = btn.innerHTML;
        btn.innerHTML = "✅ Copiado";
        setTimeout(function() {{ btn.innerHTML = orig; btn.classList.remove("copied") }}, 2000);
    }}

    function fallbackCopy(text) {{
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try {{
            document.execCommand("copy");
            showToast("✅ Leads copiados");
        }} catch(e) {{
            showToast("❌ No se pudo copiar. Selecciona manualmente.");
        }}
        document.body.removeChild(ta);
    }}

    function showToast(msg) {{
        var t = document.getElementById("toast");
        t.textContent = msg;
        t.classList.add("show");
        clearTimeout(t._timer);
        t._timer = setTimeout(function() {{ t.classList.remove("show") }}, 2500);
    }}
    </script>
</body>
</html>"""

    path = os.path.join(DIR, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print(f"✅ Dashboard generado: {path} ({len(html)} bytes)")
    return True

if __name__ == "__main__":
    generate()

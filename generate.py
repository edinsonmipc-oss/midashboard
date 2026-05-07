#!/usr/bin/env python3
"""generate.py — Hermes OS Premium SaaS Dashboard"""
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
    templates_data = load_json("templates.json")

    # Process leads
    all_dates = sorted(leads_data.get("leads_by_date",{}).keys(), reverse=True)[:14]
    all_leads = [l for d in all_dates for l in leads_data["leads_by_date"][d]]
    seen = set(); unique = []
    for l in all_leads:
        if l["email"] not in seen:
            seen.add(l["email"]); unique.append(l)

    log_entries = changelog.get("entries",[])[:20]

    # Business list
    biz_list = []
    for p in projects["projects"]:
        biz_list.append({
            "id": p["id"], "name": p["name"], "emoji": p["emoji"],
            "status": p["status"], "description": p["description"],
            "url": p.get("url",""), "metrics": p.get("metrics",{}),
            "notes": p.get("notes",""), "next_steps": p.get("next_steps",[])
        })

    # Sites
    site_items = []
    for s in health.get("sites",[]):
        site_items.append({
            "name": s["name"], "url": s["url"], "status": s["status"],
            "uptime": s.get("uptime_24h","-"),
            "seo": s.get("seo_metrics",{}),
            "score": s.get("seo_score")
        })

    # Agents
    agents = [
        {"id":"seo","icon":"🔍","name":"SEO Agent","status":"Activo","last":"Today 07:00","jobs":"12","uptime":"99%"},
        {"id":"leads","icon":"🎯","name":"Lead Finder","status":"Activo","last":"Today 11:39","jobs":"22","uptime":"100%"},
        {"id":"outreach","icon":"📧","name":"Outreach Agent","status":"Pausado","last":"Yesterday","jobs":"0","uptime":"-"},
        {"id":"content","icon":"📝","name":"Content Writer","status":"Activo","last":"Today 06:30","jobs":"8","uptime":"98%"},
        {"id":"health","icon":"🔌","name":"Health Monitor","status":"Activo","last":"Today 11:39","jobs":"48","uptime":"100%"},
    ]

    # Type configs
    TYPE_LABELS = {"builder":"Builders","constructora":"Constructoras","real_estate":"Real Estate","property_mgmt":"Property Managers","strata":"Strata","other":"Other"}
    BIZ_TARGET = {"builder":"antoniopaving","constructora":"antoniopaving","real_estate":"primeproperty","property_mgmt":"primeproperty","strata":"primeproperty"}
    BIZ_COLORS = {"antoniopaving":"#dc2626","primeproperty":"#2563eb"}
    BIZ_NAMES = {"antoniopaving":"Antonio Paving","primeproperty":"Prime Property"}
    BIZ_EMOJIS = {"antoniopaving":"🏗️","primeproperty":"🏢"}

    # Encode all data
    def js(v): return json.JSONEncoder(indent=None, separators=(",",":")).encode(v)

    JS = f'''<script>
var LEADS = {js(unique)};
var TEMPLATES = {js(templates_data.get("templates",[]))};
var BIZ_DATA = {js(biz_list)};
var SITES_DATA = {js(site_items)};
var AGENTS_DATA = {js(agents)};
var LOG_DATA = {js(log_entries)};
var TYPE_LABELS = {js(TYPE_LABELS)};
var BIZ_TARGET = {js(BIZ_TARGET)};
var BIZ_COLORS = {js(BIZ_COLORS)};
var BIZ_NAMES = {js(BIZ_NAMES)};
var BIZ_EMOJIS = {js(BIZ_EMOJIS)};

function toggleSidebar(){{document.getElementById('sb').classList.toggle('open')}}

function switchPanel(id){{
  document.querySelectorAll('.pn').forEach(p=>p.classList.remove('on'));
  var pn=document.getElementById('pn-'+id);
  if(pn)pn.classList.add('on');
  document.querySelectorAll('.sb-btn').forEach(b=>b.classList.remove('on'));
  var btn=document.querySelector('.sb-btn[data-pn="'+id+'"]');
  if(btn)btn.classList.add('on');
  try{{localStorage.setItem('hpan',id)}}catch(e){{}}
  var t={{dashboard:'Dashboard',leads:'Leads CRM',sites:'Sites & SEO',businesses:'All Businesses',tasks:'Tasks',agents:'AI Agents',notes:'Notes',changelog:'Changelog'}};
  var s={{dashboard:'Overview',leads:'51 contacts',sites:'6/6 online',businesses:'6 projects',tasks:'Kanban',agents:'5 agents',notes:'Auto-saved',changelog:'Updates'}};
  document.getElementById('page-title').textContent=t[id]||id;
  document.getElementById('page-sub').textContent=s[id]||'';
  if(window.innerWidth<=768)document.getElementById('sb').classList.remove('open')
}}

document.querySelectorAll('.sb-btn').forEach(b=>b.addEventListener('click',()=>switchPanel(b.getAttribute('data-pn'))));
try{{var lp=localStorage.getItem('hpan');if(lp)switchPanel(lp)}}catch(e){{}}

function toast(m){{var t=document.getElementById('to');t.textContent=m;t.classList.add('sh');clearTimeout(t._t);t._t=setTimeout(()=>t.classList.remove('sh'),2500)}}

function copyText(t,cb){{if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t).then(cb).catch(()=>fb(t,cb));else fb(t,cb)}}
function fb(t,cb){{var ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);ta.select();try{{document.execCommand('copy');cb()}}catch(e){{toast('❌ Error')}}document.body.removeChild(ta)}}
function copyAllEmails(){{copyText(LEADS.map(l=>l.email).join('; '),()=>toast('✅ '+LEADS.length+' emails copied'))}}

function getContacted(){{try{{return JSON.parse(localStorage.getItem('contacted')||'{{}}')}}catch(e){{return{{}}}}}}
function markContacted(email){{var m=getContacted();m[email]=new Date().toISOString().slice(0,10);try{{localStorage.setItem('contacted',JSON.stringify(m))}}catch(e){{}}var el=document.getElementById('lc-'+email.replace(/[@.]/g,'_'));if(el)el.style.opacity='0.5';toast('✅ Contacted')}}

function esc(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}}

function renderLeads(){{
  var groups={{}},order=['constructora','builder','real_estate','property_mgmt','strata','other'];
  LEADS.forEach(l=>{{var t=l.type||'other';if(!groups[t])groups[t]=[];groups[t].push(l)}});
  var html='',contacted=getContacted();
  order.forEach(key=>{{
    var items=groups[key];if(!items||!items.length)return;
    var verified=items.filter(l=>l.verified==='verified').length;
    var biz=BIZ_TARGET[key]||'primeproperty';
    html+='<div class="sc block"><div class="sc-h"><h3>'+(TYPE_LABELS[key]||key)+'</h3><span class="sc-count">'+items.length+'</span><span style="font-size:11px;color:var(--green)">✅'+verified+'</span><span class="lb lb-biz" style="background:'+BIZ_COLORS[biz]+'">'+BIZ_EMOJIS[biz]+' '+BIZ_NAMES[biz]+'</span></div><div class="sc-b"><div class="lg">';
    items.forEach(l=>{{
      var eid='lc-'+l.email.replace(/[@.]/g,'_'),done=!!contacted[l.email];
      var vb=l.verified==='verified'?'<span class="lb lb-v">✅ Verified</span>':l.verified==='risky'?'<span class="lb lb-r">⚠️ Risky</span>':'<span class="lb lb-i">❓ Unknown</span>';
      html+='<div class="lc" id="'+eid+'"'+(done?' style="opacity:0.5"':'')+'><div class="lch"><div><div class="lcn">'+esc(l.company)+'</div><div class="lce">'+esc(l.email)+'</div></div><div class="lc-action"><button class="send-btn" onclick="openGmail(\\''+esc(l.email)+'\\',\\''+biz+'\\',\\''+esc(l.company)+'\\')">📧</button><button class="done-btn" onclick="markContacted(\\''+esc(l.email)+'\\')">✓</button></div></div>'+(l.notes?'<div class="lcd">'+esc(l.notes)+'</div>':'')+'<div class="lcf">'+vb+'<span class="lb lb-biz" style="background:'+BIZ_COLORS[biz]+'">'+BIZ_EMOJIS[biz]+' '+BIZ_NAMES[biz]+'</span></div></div>';
    }});
    html+='</div></div></div>';
  }});
  document.getElementById('lead-groups').innerHTML=html;
}}

function openGmail(email,biz,company){{
  var t=TEMPLATES.find(t=>t.id===biz);if(!t)return toast('❌ No template');
  var body=t.body.replace('[COMPANY]',company);
  window.open('https://mail.google.com/mail/?view=cm&fs=1&to='+encodeURIComponent(email)+'&su='+encodeURIComponent(t.subject)+'&body='+encodeURIComponent(body),'_blank');
  toast('✅ Gmail opened');
}}

function renderSites(){{
  document.getElementById('sites-list').innerHTML='<div class="shg">'+SITES_DATA.map(s=>'<div class="shc"><div class="shc-dot" style="background:'+(s.status==='online'?'#22c55e':'#ef4444')+'"></div><div class="shc-info"><div class="shc-name">'+esc(s.name)+'</div><div class="shc-url">'+esc(s.url)+'</div><div class="shc-meta"><span>⏱️ '+esc(s.uptime)+'</span></div></div><div class="shc-status '+(s.status==='online'?'on':'off')+'">'+(s.status==='online'?'● ONLINE':'○ OFFLINE')+'</div></div>').join('')+'</div>';
}}

function renderBiz(){{
  var sc={{activo:'#22c55e',pendiente:'#f59e0b',idea:'#6b6b80'}};
  document.getElementById('biz-list').innerHTML=BIZ_DATA.map(p=>{{
    var c=sc[p.status]||'#6b6b80';
    var m=Object.entries(p.metrics||{{}}).map(([k,v])=>'<div class="bc2-mitem"><div class="bc2-ml">'+k.replace(/_/g,' ').toUpperCase()+'</div><div class="bc2-mv">'+esc(String(v))+'</div></div>').join('');
    var st=(p.next_steps||[]).map((s,i)=>'<li class="'+(i<1?'d':'')+'">'+(i<1?'✅':'○')+' '+esc(s)+'</li>').join('');
    return '<div class="bc2" style="--bcz:'+c+'"><div class="bc2-h"><span class="emoji">'+p.emoji+'</span><h3>'+esc(p.name)+'</h3><span class="st-badge" style="background:'+c+'22;color:'+c+'">'+p.status.toUpperCase()+'</span></div><div class="bc2-d">'+esc(p.description)+'</div>'+(m?'<div class="bc2-m">'+m+'</div>':'')+(p.url?'<a href="'+esc(p.url)+'" target="_blank" class="bc2-url">'+esc(p.url)+' →</a>':'')+(st?'<ul class="bc2-steps">'+st+'</ul>':'')+(p.notes?'<div class="bc2-notes">📝 '+esc(p.notes)+'</div>':'')+'</div>';
  }}).join('');
}}

function renderAgents(){{
  document.getElementById('agents-list').innerHTML=AGENTS_DATA.map(a=>'<div class="ac"><div class="ach"><div class="ac-icon">'+a.icon+'</div><h4>'+esc(a.name)+'</h4><span class="ac-st '+(a.status==='Activo'?'active':'paused')+'">'+(a.status==='Activo'?'● Active':'○ Paused')+'</span></div><div class="ac-stats"><span>Last Run <b>'+esc(a.last)+'</b></span><span>Jobs <b>'+esc(a.jobs)+'</b></span><span>Uptime <b>'+(a.uptime==='-'?'-':esc(a.uptime))+'</b></span></div></div>').join('');
}}

function renderLog(target,count){{var items=count?LOG_DATA.slice(0,count):LOG_DATA;document.getElementById(target).innerHTML=items.map(e=>'<div class="tle"><div class="tle-date">'+esc(e.date)+'</div><div class="tle-text">'+({'mejora':'🔧','creacion':'✨','infra':'⚙️','analisis':'📊','idea':'💡'}[e.type]||'📌')+' <span class="tle-project">['+esc(e.project)+']</span> '+esc(e.text)+'</div></div>').join('')}}

function renderMiniLog(){{renderLog('mini-log',5);document.getElementById('mini-log').innerHTML+='<div class="tle" style="cursor:pointer" onclick="switchPanel(\\'changelog\\')"><div class="tle-text" style="color:var(--accent)">→ View all '+LOG_DATA.length+' entries</div></div>'}}

// Tasks
function getTasks(){{try{{return JSON.parse(localStorage.getItem('htasks'))||{{today:[],urgent:[],week:[],done:[]}}}}catch(e){{return{{today:[],urgent:[],week:[],done:[]}}}}}}
function saveTasks(d){{try{{localStorage.setItem('htasks',JSON.stringify(d))}}catch(e){{}}}}
function renderTasks(){{var d=getTasks();['today','urgent','week','done'].forEach(c=>{{var el=document.querySelector('.tcol[data-col="'+c+'"] .tl2');if(!el)return;el.innerHTML=d[c].map((t,i)=>'<div class="ti"'+(c==='done'?' style="text-decoration:line-through;color:var(--fg3)"':'')+' onclick="moveTask(\\''+c+'\\','+i+')">'+esc(t)+'</div>').join('')}})}}
function addTask(col){{var t=prompt('New task ('+col+'):');if(!t||!t.trim())return;var d=getTasks();d[col].push(t.trim());saveTasks(d);renderTasks()}}
function moveTask(col,i){{var d=getTasks();if(col==='done')d.done.splice(i,1);else{{d.done.push(d[col][i]);d[col].splice(i,1)}}saveTasks(d);renderTasks();toast('✅ Task moved')}}
renderTasks();

// Notes
(function(){{var ta=document.getElementById('na');if(ta)try{{ta.value=localStorage.getItem('hnotes')||''}}catch(e){{}}})()
function saveNotes(){{var ta=document.getElementById('na');if(!ta)return;try{{localStorage.setItem('hnotes',ta.value);document.getElementById('ns').textContent='✅ Saved'}}catch(e){{}}}}

// Template overlay
function tp(biz){{var t=TEMPLATES.find(t=>t.id===biz);if(!t)return toast('❌ No template');document.getElementById('tmh').innerHTML='<h3>'+t.emoji+' '+esc(t.name)+'</h3><button id="tmx" onclick="closeTpl()">✕</button>';document.getElementById('tmb').textContent=t.body;document.getElementById('tmf').innerHTML='<button class="btn" onclick="copyTemplate(\\''+biz+'\\')">📋 Copy</button><button class="btn btn-p" onclick="closeTpl();openGmail(\\'\\',\\''+biz+'\\',\\'[COMPANY]\\')">📧 Open Gmail</button><button class="btn" onclick="closeTpl()">Close</button>';document.getElementById('tmo').classList.add('sh')}}
function closeTpl(){{document.getElementById('tmo').classList.remove('sh')}}
function copyTemplate(biz){{var t=TEMPLATES.find(t=>t.id===biz);if(!t)return toast('❌ No template');copyText(t.body,()=>toast('✅ '+t.name+' template copied'))}}

// Init
renderLeads();renderSites();renderBiz();renderAgents();renderLog('full-log');renderMiniLog();
</script>'''

    # Build HTML combining template parts
    css = open(os.path.join(DIR, "index.html")).read()
    # Replace the JS placeholder
    old_script = "<script>\n// ── Data ──\nvar LEADS = [];\nvar TEMPLATES = [];\nvar BIZ_DATA = [];\nvar SITES_DATA = [];\nvar AGENTS_DATA = [];\nvar LOG_DATA = [];\n</script>"
    if old_script in css:
        html = css.replace(old_script, JS)
    else:
        # Just write the JS at the end
        html = css + JS + '</body>\n</html>'

    path = os.path.join(DIR, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print(f"OK: {path} ({len(html)} bytes)")
    return True

if __name__ == "__main__":
    generate()

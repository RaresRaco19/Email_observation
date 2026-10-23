"""Stage 7: render a single-file dashboard from out/report.json. Numbers come from the report verbatim."""
import json

from . import caught
from .artifacts import artifact_errors, front_matter
from .config import Paths
from .solutions import design_done
from .util import read_json


def build(p: Paths) -> dict:
    report = read_json(p.out / "report.json")
    if report is None:
        raise SystemExit("out/report.json missing; run rank first")
    artifacts, invalid = {}, []
    for o in report["opportunities"]:
        if "artifact" not in o:
            continue
        if artifact_errors(p, o["id"]):
            invalid.append(o["id"])
            continue
        fm, body = front_matter((p.out / o["artifact"]).read_text(encoding="utf-8"))
        artifacts[o["id"]] = {"type": fm.get("type"), "body": body, "path": o["artifact"]}
    designs = {o["id"]: read_json(p.out / "solutions" / f"{o['id']}.json")
               for o in report["opportunities"] if o.get("design") and design_done(p, o["id"])}
    mistakes = caught.summary(p)
    data = json.dumps({"report": report, "artifacts": artifacts, "designs": designs, "caught": mistakes}, ensure_ascii=False).replace("</", "<\\/")
    p.dashboard.mkdir(parents=True, exist_ok=True)
    (p.dashboard / "index.html").write_text(TEMPLATE.replace("__DATA__", data), encoding="utf-8")
    return {"dashboard": "out/dashboard/index.html", "opportunities": len(report["opportunities"]),
            "designs_shown": len(designs), "artifacts_shown": len(artifacts), "artifacts_withheld_invalid": invalid,
            "caught": mistakes}


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Automation Opportunity Audit</title>
<style>
:root{color-scheme:light;--bg:#f4f3f0;--surface:#fcfcfb;--line:#e4e2dc;--ink:#0b0b0b;--ink-2:#52514e;--ink-3:#7a7974;
--accent:#2a78d6;--accent-soft:#e3eefb;--mark:#fff1b8;--ok:#008300;--warn:#b26b00}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#121211;--surface:#1a1a19;--line:#2e2d2a;
--ink:#f0efec;--ink-2:#c3c2b7;--ink-3:#8f8e86;--accent:#3987e5;--accent-soft:#1d2c40;--mark:#5a4a00;--ok:#4fb84f;--warn:#e0a040}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#121211;--surface:#1a1a19;--line:#2e2d2a;--ink:#f0efec;--ink-2:#c3c2b7;--ink-3:#8f8e86;
--accent:#3987e5;--accent-soft:#1d2c40;--mark:#5a4a00;--ok:#4fb84f;--warn:#e0a040}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1120px;margin:0 auto;padding:24px 16px 64px}
header{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:20px}
header h1{font-size:20px;margin:0;font-weight:650;letter-spacing:-.01em}header .sub{color:var(--ink-2);font-size:13px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:20px;margin-bottom:16px}
.hero{display:grid;grid-template-columns:minmax(220px,1.2fr) 3fr;gap:20px;align-items:center}
.hero .big{font-size:44px;font-weight:700;letter-spacing:-.02em;line-height:1.1;font-variant-numeric:tabular-nums}
.label{color:var(--ink-2);font-size:12px;text-transform:uppercase;letter-spacing:.06em}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px}
.tile{border-left:3px solid var(--line);padding:2px 12px}.tile .v{font-size:22px;font-weight:650;font-variant-numeric:tabular-nums}
.tile a{color:var(--ink)}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
th{text-align:left;font-size:12px;color:var(--ink-2);font-weight:600;padding:8px;border-bottom:1px solid var(--line)}
td{padding:10px 8px;border-bottom:1px solid var(--line);vertical-align:middle}tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right}.rank{color:var(--ink-3);width:28px}
.barcell{width:34%}.bar{display:flex;align-items:center;gap:8px}.bar span.b{height:12px;background:var(--accent);border-radius:0 4px 4px 0;min-width:2px}
.bar a{color:var(--ink);font-weight:600;white-space:nowrap}
.pill{display:inline-block;font-size:11px;padding:1px 8px;border-radius:99px;background:var(--accent-soft);color:var(--accent);font-weight:600}
.muted{color:var(--ink-2)}.small{font-size:13px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.formula{font-family:ui-monospace,Menlo,monospace;font-size:13px;background:var(--bg);padding:10px 12px;border-radius:6px;overflow-wrap:anywhere}
.ev{border-top:1px solid var(--line);padding:12px 0}.ev:first-child{border-top:0}
.ev q{display:block;margin:4px 0;padding-left:12px;border-left:3px solid var(--accent);quotes:none;color:var(--ink)}
pre.raw{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.55 ui-monospace,Menlo,monospace;margin:0}
mark{background:var(--mark);color:inherit;padding:1px 0;border-radius:2px}
.md h1,.md h2,.md h3{font-size:16px;margin:16px 0 6px}.md blockquote{margin:6px 0;padding-left:12px;border-left:3px solid var(--line);color:var(--ink-2)}
.md ul,.md ol{padding-left:22px}
svg text{fill:var(--ink-2);font-size:11px}
.crumbs{font-size:13px;margin-bottom:12px}
@media (max-width:720px){.hero,.grid2{grid-template-columns:1fr}.hide-sm{display:none}.hero .big{font-size:36px}}
</style></head><body><div class="wrap" id="app"></div>
<script type="application/json" id="data">__DATA__</script>
<script>
const {report:R, artifacts:A, designs:D, caught:C} = JSON.parse(document.getElementById('data').textContent);
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const usd = n => '$' + Math.round(n).toLocaleString('en-US');
const num = n => Number(n).toLocaleString('en-US');
const msgLink = (id, q, text) => `<a href="#/msg/${encodeURIComponent(id)}${q ? '?q=' + encodeURIComponent(q) : ''}">${text ?? esc(id)}</a>`;
const byId = Object.fromEntries(R.opportunities.map(o => [o.id, o]));
const G = R.generated_from;
const REMEDY = {automation: 'Automation', quick_win: 'Quick win'};

function header(){
  return `<header><div><h1>Automation Opportunity Audit</h1>
  <div class="sub">Enron gas operations email, ${num(G.files)} files analyzed · every figure links to its source message</div></div>
  <div class="small"><a href="#/">Overview</a> · <a href="#/coverage">Method &amp; coverage</a></div></header>`;
}

function overview(){
  const max = Math.max(1, ...R.opportunities.map(o => o.usd_month));
  const rows = R.opportunities.map(o => `<tr>
    <td class="rank">${o.rank}</td>
    <td><a href="#/opp/${o.id}"><b>${esc(o.name)}</b></a> <span class="pill">${REMEDY[o.remedy]}</span><div class="small muted">${esc(o.mailboxes.join(', '))}</div></td>
    <td class="barcell"><div class="bar"><span class="b" style="width:${(o.usd_month / max * 70).toFixed(1)}%"></span>
      <a href="#/opp/${o.id}/formula" title="How this is calculated">${usd(o.usd_month)}</a></div></td>
    <td class="num"><a href="#/opp/${o.id}/formula">${o.hours_month}</a></td>
    <td class="num hide-sm"><a href="#/opp/${o.id}/evidence">${o.messages}</a></td>
    <td class="hide-sm">${D[o.id] ? `<a class="pill" href="#/opp/${o.id}/design">${esc(D[o.id].effort)}</a>` : ''}</td>
    <td class="hide-sm">${A[o.id] ? `<a class="pill" href="#/opp/${o.id}/artifact">${esc(A[o.id].type)}</a>` : ''}</td></tr>`).join('');
  return header() + `<section class="card hero">
    <div><div class="label">Recoverable cost</div><div class="big"><a href="#/total" style="color:inherit">${usd(R.total_usd_month)}</a><span class="muted" style="font-size:18px">/mo</span></div>
    <div class="muted small">${usd(R.total_usd_year)} per year · ${R.total_hours_month} hours/month at $${R.assumptions.rate_usd}/h</div></div>
    <div class="tiles">
      <div class="tile"><div class="label">Files read</div><div class="v"><a href="#/coverage">${num(G.files)}</a></div></div>
      <div class="tile"><div class="label">Unique messages</div><div class="v"><a href="#/coverage">${num(G.unique_messages)}</a></div></div>
      <div class="tile"><div class="label">Opportunities</div><div class="v"><a href="#/total">${R.opportunities.length}</a></div></div>
      <div class="tile"><div class="label">Solution designs</div><div class="v"><a href="#/total">${Object.keys(D).length}</a></div></div>
      <div class="tile"><div class="label">Drafted artifacts</div><div class="v"><a href="#/total">${Object.keys(A).length}</a></div></div>
    </div></section>
  <section class="card"><table><thead><tr><th></th><th>Process</th><th>$ / month</th><th class="num">Hours / mo</th>
    <th class="num hide-sm">Messages</th><th class="hide-sm" title="Implementation effort from the solution design">Effort</th><th class="hide-sm">Draft</th></tr></thead><tbody>${rows ||
    '<tr><td colspan="7" class="muted">No process cleared the evidence bar in this run.</td></tr>'}</tbody></table>
    ${R.below_cutoff.length ? `<p class="small muted" style="margin-bottom:0">Showing opportunities worth at least ${usd(R.assumptions.min_usd_month)}/month, at most ${R.assumptions.top_n}. ${R.below_cutoff.length} smaller opportunities also passed the evidence gates; they are listed in report.md and not counted in the total.</p>` : ''}</section>`;
}

function total(){
  const rows = R.opportunities.map(o => `<tr><td class="rank">${o.rank}</td><td><a href="#/opp/${o.id}">${esc(o.name)}</a></td>
    <td class="num"><a href="#/opp/${o.id}/formula">${usd(o.usd_month)}</a></td></tr>`).join('');
  return header() + `<div class="crumbs"><a href="#/">Overview</a> › Total</div><section class="card">
    <h2 style="margin-top:0">How ${usd(R.total_usd_month)}/month is built</h2>
    <p class="muted">The total is the sum of each ranked process's monthly figure. Each figure is computed by code from validated labels; click one for its formula and evidence.</p>
    <table><tbody>${rows}<tr><td></td><td><b>Total</b></td><td class="num"><b>${usd(R.total_usd_month)}</b></td></tr></tbody></table></section>`;
}

function monthChart(o){
  const ent = Object.entries(o.by_month); if (!ent.length) return '<p class="muted small">No dated messages.</p>';
  const W = 480, H = 120, pad = 20, max = Math.max(...ent.map(e => e[1])), bw = (W - 2) / ent.length;
  const bars = ent.map(([m, c], i) => { const h = Math.max(2, (c / max) * (H - pad - 6));
    return `<rect x="${(i * bw + 1).toFixed(1)}" y="${(H - pad - h).toFixed(1)}" width="${Math.max(1, bw - 2).toFixed(1)}" height="${h.toFixed(1)}" rx="2" fill="var(--accent)"><title>${m}: ${c} message${c > 1 ? 's' : ''}</title></rect>`; }).join('');
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Messages per month">${bars}
    <line x1="0" x2="${W}" y1="${H - pad}" y2="${H - pad}" stroke="var(--line)"/>
    <text x="0" y="${H - 4}">${ent[0][0]}</text><text x="${W}" y="${H - 4}" text-anchor="end">${ent[ent.length - 1][0]}</text></svg>`;
}

function md(text){
  const inline = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/\d+)\]/g, (_, id) => '[' + msgLink(id) + ']');
  let html = '', list = null;
  const close = () => { if (list) { html += `</${list}>`; list = null; } };
  for (const line of text.split('\n')) {
    let m;
    if ((m = line.match(/^(#{1,3})\s+(.*)/))) { close(); html += `<h3>${inline(m[2])}</h3>`; }
    else if ((m = line.match(/^\s*[-*]\s+(\[[ x]\]\s+)?(.*)/))) { if (list !== 'ul') { close(); html += '<ul>'; list = 'ul'; } html += `<li>${m[1] ? '☐ ' : ''}${inline(m[2])}</li>`; }
    else if ((m = line.match(/^\s*\d+[.)]\s+(.*)/))) { if (list !== 'ol') { close(); html += '<ol>'; list = 'ol'; } html += `<li>${inline(m[1])}</li>`; }
    else if ((m = line.match(/^>\s?(.*)/))) { close(); html += `<blockquote>${inline(m[1])}</blockquote>`; }
    else if (!line.trim()) close();
    else { close(); html += `<p>${inline(line)}</p>`; }
  }
  close(); return html;
}

function opp(id, section){
  const o = byId[id]; if (!o) return header() + '<p>Unknown process.</p>';
  const ev = o.evidence.map(e => `<div class="ev"><div class="small muted">${esc((e.date || 'undated').slice(0, 10))} · ${esc(e.from)} · ${esc(e.kind)}${e.stall ? ' · <b style="color:var(--warn)">stall signal</b>' : ''}</div>
    <div><b>${esc(e.subject || '(no subject)')}</b></div><q>${esc(e.quote)}</q>
    <div class="small">${msgLink(e.msg_id, e.quote, 'Open source message ' + esc(e.msg_id) + ' →')}${e.dup_paths.length ? ` <span class="muted">(also at ${e.dup_paths.map(d => msgLink(d)).join(', ')})</span>` : ''}</div></div>`).join('');
  const parts = o.participants.map(p => `<li>${esc(p.address)} <span class="muted">· ${p.messages}</span></li>`).join('');
  const s = o.stall;
  const out = header() + `<div class="crumbs"><a href="#/">Overview</a> › #${o.rank} ${esc(o.name)}</div>
  <section class="card"><div class="label">Rank ${o.rank} of ${R.opportunities.length}</div><h2 style="margin:4px 0 8px">${esc(o.name)}</h2>
    <p>${esc(o.description)}</p><p><b>${REMEDY[o.remedy]}:</b> ${esc(o.action_idea)}</p>
    <div class="tiles">
      <div class="tile"><div class="label">$ / month</div><div class="v"><a href="#/opp/${o.id}/formula">${usd(o.usd_month)}</a></div></div>
      <div class="tile"><div class="label">Hours / month</div><div class="v"><a href="#/opp/${o.id}/formula">${o.hours_month}</a></div></div>
      <div class="tile"><div class="label">Messages</div><div class="v"><a href="#/opp/${o.id}/evidence">${o.messages}</a></div></div>
      <div class="tile"><div class="label">Per month</div><div class="v"><a href="#/opp/${o.id}/formula">${o.messages_per_month}</a></div></div>
      <div class="tile"><div class="label">Median reply gap</div><div class="v"><a href="#/opp/${o.id}/evidence">${s.median_gap_hours ?? '–'}${s.median_gap_hours != null ? ' h' : ''}</a></div></div>
    </div></section>
  <section class="card" id="formula"><h3 style="margin-top:0">How the figure is calculated</h3><div class="formula">${esc(o.formula)}</div>
    <p class="small muted">Message count, date span and arithmetic are computed by code. Median minutes is the median of per-message handling estimates made during labeling; automatable share is a fixed assumption (${Math.round(R.assumptions.automatable_share * 100)}%).</p></section>
  <div class="grid2"><section class="card"><h3 style="margin-top:0">Volume by month</h3>${monthChart(o)}</section>
    <section class="card"><h3 style="margin-top:0">Who touches it</h3><ul class="small" style="padding-left:18px;margin:0">${parts}</ul>
    <p class="small muted">${o.threads} threads · ${s.flagged_messages} messages flagged as stalled · longest reply gap ${s.max_gap_hours ?? '–'} h</p></section></div>
  <section class="card"><h3 style="margin-top:0">Strength of evidence</h3><div class="tiles">
      <div class="tile"><div class="label">Verified quotes</div><div class="v"><a href="#/opp/${o.id}/evidence">${o.confidence.quotes}</a></div></div>
      <div class="tile"><div class="label">Threads</div><div class="v">${o.confidence.threads}</div></div>
      <div class="tile"><div class="label">Mailboxes</div><div class="v">${o.confidence.mailboxes}</div></div>
      <div class="tile"><div class="label">Active months</div><div class="v">${o.confidence.active_months}</div></div>
      <div class="tile"><div class="label">Stall share</div><div class="v">${Math.round(o.confidence.stall_share * 100)}%</div></div>
    </div></section>
  ${D[o.id] ? design(D[o.id], o.remedy) : ''}
  ${A[o.id] ? `<section class="card md" id="artifact"><div class="label">Ready-to-use draft · ${esc(A[o.id].type)}</div>${md(A[o.id].body)}</section>` : ''}
  <section class="card" id="evidence"><h3 style="margin-top:0">Evidence (${o.evidence.length} messages, quotes verified verbatim)</h3>${ev}</section>`;
  setTimeout(() => section && document.getElementById(section)?.scrollIntoView({behavior: 'smooth'}), 0);
  return out;
}

function design(d, remedy){
  const qw = remedy === 'quick_win';
  const s = d.solution, li = xs => xs.map(x => `<li>${esc(x)}</li>`).join('');
  const cites = cs => cs.map(c => msgLink(c)).join(', ');
  return `<section class="card" id="design"><div class="label">${qw ? 'Implementation design' : 'Solution design'} · effort ${esc(d.effort)}</div>
    <p style="margin-top:6px">${esc(d.summary)}</p>
    <div class="grid2"><div><h3>How it works today</h3><ol class="small">${d.current_workflow.map(w =>
      `<li>${esc(w.step)} <span class="muted">(${esc(w.who)})</span> <span class="small">[${cites(w.citations)}]</span></li>`).join('')}</ol></div>
    <div><h3>Where it stalls</h3>${d.stall_points.map(x => `<div class="ev"><div class="small">${esc(x.description)}</div>
      <q>${esc(x.quote)}</q><div class="small">${msgLink(x.citation, x.quote, 'Open source message ' + esc(x.citation) + ' →')}</div></div>`).join('')}</div></div>
    <h3>${qw ? 'Proposed quick win' : 'Proposed automation'}</h3><p>${esc(s.approach)}</p>
    <div class="grid2 small"><div><b>Trigger:</b> ${esc(s.trigger)}<br><b>Inputs:</b> ${esc(s.inputs.join('; '))}<br><b>Outputs:</b> ${esc(s.outputs.join('; '))}</div>
      <div><b>Existing systems:</b> ${esc(s.systems.join(', '))}<br><b>New components:</b> ${esc(s.components.join(', '))}<br><b>Success metric:</b> ${esc(d.success_metric)}</div></div>
    <div class="grid2"><div><h3>Implementation steps</h3><ol class="small">${li(d.implementation_steps)}</ol></div>
      <div><h3>Stays manual</h3><ul class="small">${li(d.stays_manual)}</ul><h3>Risks</h3><ul class="small">${li(d.risks)}</ul></div></div></section>`;
}

function coverage(){
  const f = Object.entries(G.files_by_folder).map(([k, v]) => `<tr><td>${esc(k)}</td><td class="num">${num(v)}</td></tr>`).join('');
  const rej = R.rejected.map(x => `<li>${esc(x.name)}: ${esc(x.reason)}</li>`).join('') || '<li class="muted">None</li>';
  const fb = (G.failed_batches || []).map(b => `<li>${esc(b.id)}: ${esc(b.errors.join('; '))}</li>`).join('') || '<li class="muted">None</li>';
  const cr = Object.entries(C.by_stage).flatMap(([stage, cats]) => Object.entries(cats).map(([cat, n]) =>
    `<tr><td>${esc(stage)}</td><td>${esc(cat)}</td><td class="num">${num(n)}</td></tr>`)).join('');
  return header() + `<div class="crumbs"><a href="#/">Overview</a> › Method &amp; coverage</div><div class="grid2">
  <section class="card"><h3 style="margin-top:0">Files read</h3><table><tbody>${f}<tr><td><b>Total</b></td><td class="num"><b>${num(G.files)}</b></td></tr></tbody></table>
    <p class="small muted">${G.duplicates_removed} duplicate copies removed → ${num(G.unique_messages)} unique messages in ${num(G.threads)} threads. ${num(G.messages_labeled ?? 0)} messages labeled by review agents; ${G.quotes_rejected ?? 0} quotes failed verbatim verification and were discarded.</p></section>
  <section class="card"><h3 style="margin-top:0">Assumptions</h3><ul class="small">
    <li>Blended rate: $${R.assumptions.rate_usd}/hour</li><li>Automatable share of handling time: ${Math.round(R.assumptions.automatable_share * 100)}%</li>
    <li>A process ships only with ≥ ${R.assumptions.min_evidence} verified quotes in ≥ ${R.assumptions.min_threads} threads</li>
    <li>Monthly rate: each mailbox's messages over the period that mailbox was observed, summed across mailboxes</li>
<li>Opportunities worth at least ${usd(R.assumptions.min_usd_month)}/month (at most ${R.assumptions.top_n}, by $/month) are shown and totalled; each gets a solution design (an automation, or the rollout of a quick win) and a draft built on it</li></ul>
    <h3>Not shipped (too little evidence)</h3><ul class="small">${rej}</ul><h3>Failed batches</h3><ul class="small">${fb}</ul></section>
  <section class="card"><h3 style="margin-top:0">Caught by validators</h3><p class="small muted">Agent output rejected by code before it could reach this dashboard (rejected batches, designs and drafts were retried; dropped quotes are not counted as evidence).</p>
    ${cr ? `<table><thead><tr><th>Stage</th><th>Mistake</th><th class="num">Count</th></tr></thead><tbody>${cr}<tr><td></td><td><b>Total</b></td><td class="num"><b>${num(C.total)}</b></td></tr></tbody></table>` : '<p class="small muted">None recorded.</p>'}</section></div>`;
}

async function message(id, q){
  $('#app').innerHTML = header() + `<div class="crumbs"><a href="javascript:history.back()">← Back</a> · <code>corpus/${esc(id)}.</code></div><section class="card"><pre class="raw" id="raw">Loading…</pre></section>`;
  let text;
  try { const r = await fetch('/raw/' + id.split('/').map(encodeURIComponent).join('/')); if (!r.ok) throw new Error(r.status); text = await r.text(); }
  catch (e) { $('#raw').textContent = 'Could not load the raw file (' + e.message + '). Open the dashboard through `python3 -m observer serve`.'; return; }
  let html = esc(text);
  if (q) {
    const pat = q.trim().split(/\s+/).map(w => esc(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('\\s+');
    html = html.replace(new RegExp(pat), m => `<mark id="hit">${m}</mark>`);
  }
  $('#raw').innerHTML = html;
  document.getElementById('hit')?.scrollIntoView({block: 'center'});
}

function route(){
  const [path, qs] = location.hash.slice(1).split('?');
  const seg = (path || '/').split('/').filter(Boolean);
  window.scrollTo(0, 0);
  if (seg[0] === 'msg') return message(decodeURIComponent(seg.slice(1).join('/')), new URLSearchParams(qs || '').get('q'));
  $('#app').innerHTML = seg[0] === 'opp' ? opp(seg[1], seg[2]) : seg[0] === 'coverage' ? coverage() : seg[0] === 'total' ? total() : overview();
}
addEventListener('hashchange', route); route();
</script></body></html>
"""

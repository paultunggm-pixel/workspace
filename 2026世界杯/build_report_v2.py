#!/usr/bin/env python3
"""生成 v2 版站点排查报告：白底、双tab、左右分栏、批次导航"""
import json
from datetime import datetime
from collections import defaultdict

with open('/Users/d.j.f/Documents/Claude/2026世界杯/probe_results.json') as f:
    rows = json.load(f)

# ── 批次定义 ──
BATCH_LABELS = ['6月9日上午', '6月8日', '6月初']

for r in rows:
    d = r['date']
    if d == '6.9':
        r['_batch'] = '6月9日上午'
    elif d == '6.8':
        r['_batch'] = '6月8日'
    else:
        r['_batch'] = '6月初'

def stats(sites):
    v = sum(1 for s in sites if s['is_list'])
    iv = sum(1 for s in sites if not s['is_list'])
    c = sum(1 for s in sites if s['corrected_url'])
    ur = sum(1 for s in sites if s['http_status'] == 0)
    return {'total':len(sites),'valid':v,'invalid':iv,'corrected':c,'unreachable':ur}

def nav(cat):
    """生成左侧批次导航"""
    out = ''
    for bl in BATCH_LABELS:
        batch_sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
        if not batch_sites:
            continue
        n = len(batch_sites)
        active = 'active' if bl == BATCH_LABELS[0] else ''
        out += f'<a class="batch-link {active}" panel-id="panel-{cat}-{bl}">{bl}<span class="bc">{n}</span></a>\n'
    return out

def panel(cat, bl):
    """生成一个批次面板"""
    sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
    if not sites:
        return ''
    s = stats(sites)
    is_intl = (cat == '境外')
    extra_th = '<th>国家</th>' if is_intl else ''

    tbody = ''
    for i, r in enumerate(sites, 1):
        sc = 'ok' if r['is_list'] else ('warn' if r['http_status']==0 else 'no')
        si = '✅' if r['is_list'] else ('🔴' if r['http_status']==0 else '⚠️')
        curl = f'<a href="{r["corrected_url"]}" target="_blank" class="fix-link">{r["corrected_url"][:90]}</a>' if r['corrected_url'] else '-'
        cnote = r.get('corrected_note','')
        extra_td = f'<td>{r.get("country","")}</td>' if is_intl else ''
        ur_cls = ' class="unreachable"' if r['http_status']==0 else ''
        fix_cls = ' class="corrected"' if r['corrected_url'] else ''

        tbody += f'''<tr{ur_cls}{fix_cls}>
<td>{i}</td><td><b>{r['site']}</b></td>
<td class="uc"><a href="{r['url']}" target="_blank">{r['url'][:100]}</a></td>
{extra_td}
<td class="hc">{r['http_status']}</td>
<td class="{sc}">{si}</td>
<td class="pr">{r['probe_result']}</td>
<td class="uc">{curl}<br><small class="note">{cnote}</small></td>
</tr>'''

    display = 'block' if bl == BATCH_LABELS[0] else 'none'

    return f'''<div class="panel" id="panel-{cat}-{bl}" style="display:{display}">
<div class="stats-row">
<span class="st"><em class="green">{s['valid']}</em> 有效</span>
<span class="st"><em class="red">{s['invalid']}</em> 非有效</span>
<span class="st"><em>{s['total']}</em> 总计</span>
<span class="st"><em class="orange">{s['corrected']}</em> 已补充</span>
<span class="st"><em class="gray">{s['unreachable']}</em> 不可达</span>
</div>
<div class="tbl">
<table>
<thead><tr><th style="width:40px">#</th><th style="width:130px">站点</th><th>URL</th>{extra_th}<th style="width:50px">HTTP</th><th style="width:50px">有效</th><th style="width:190px">拨测结果</th><th>补充URL</th></tr></thead>
<tbody>{tbody}</tbody>
</table>
</div>
</div>'''

# ── 组装 HTML ──
cn_nav = nav('国内')
intl_nav = nav('境外')

cn_panels = ''.join(panel('国内', bl) for bl in BATCH_LABELS)
intl_panels = ''.join(panel('境外', bl) for bl in BATCH_LABELS)

cn_s = stats([r for r in rows if r['category']=='国内'])
intl_s = stats([r for r in rows if r['category']=='境外'])
all_s = stats(rows)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026世界杯时效性站点排查报告</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6f8;color:#1a1a2e;line-height:1.6}}

/* header */
.hd{{background:#fff;border-bottom:1px solid #e2e5ea;padding:0 32px;display:flex;align-items:center;justify-content:space-between;height:56px}}
.hd h1{{font-size:17px;font-weight:700;color:#0f172a}}
.hd .ts{{font-size:12px;color:#8893a4}}

/* tabs */
.tabs{{display:flex;background:#fff;padding:0 32px;border-bottom:1px solid #e2e5ea}}
.tb{{padding:14px 28px;font-size:15px;cursor:pointer;border:none;background:none;color:#64748b;font-weight:500;border-bottom:3px solid transparent;transition:.2s}}
.tb:hover{{color:#1e40af}}
.tb.on{{color:#1e40af;border-bottom-color:#1e40af;font-weight:700}}

/* main layout */
.main{{display:none}}
.main.on{{display:flex;height:calc(100vh - 116px)}}
.side{{width:220px;background:#fff;border-right:1px solid #e2e5ea;overflow-y:auto;padding:16px 0;flex-shrink:0}}
.side .ttl{{font-size:11px;color:#8893a4;text-transform:uppercase;letter-spacing:1px;padding:0 20px 12px;font-weight:600}}
.blk{{display:flex;justify-content:space-between;align-items:center;padding:10px 20px;text-decoration:none;color:#475569;font-size:14px;border-left:3px solid transparent;transition:.15s;cursor:pointer}}
.blk:hover{{background:#f1f5f9;color:#1e40af}}
.blk.on{{background:#eff6ff;color:#1e40af;border-left-color:#1e40af;font-weight:600}}
.bc{{font-size:11px;color:#94a3b8;background:#f1f5f9;padding:1px 8px;border-radius:10px}}
.blk.on .bc{{background:#dbeafe;color:#1e40af}}

/* content */
.ctn{{flex:1;overflow-y:auto;padding:24px 32px}}
.panel{{animation:fadeIn .25s}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}

/* stats */
.sr{{display:flex;gap:14px;margin-bottom:22px;flex-wrap:wrap}}
.st{{background:#fff;border:1px solid #e2e5ea;border-radius:10px;padding:12px 20px;text-align:center;min-width:90px;font-size:13px;color:#64748b}}
.st em{{display:block;font-size:26px;font-weight:700;font-style:normal}}
.st em.green{{color:#0d9488}}
.st em.red{{color:#ef4444}}
.st em.orange{{color:#f59e0b}}
.st em.gray{{color:#94a3b8}}

/* table */
.tbl{{background:#fff;border:1px solid #e2e5ea;border-radius:10px;overflow:hidden}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
thead{{background:#f8fafc}}
th{{padding:10px 10px;text-align:left;font-weight:600;color:#475569;font-size:12px;letter-spacing:.3px;white-space:nowrap}}
td{{padding:8px 10px;border-top:1px solid #f1f5f9;vertical-align:middle;font-size:13px}}
tr:hover td{{background:#f8fafc}}
tr.unreachable td{{background:#fef2f2}}
tr.corrected td:first-child{{border-left:3px solid #f59e0b}}
.uc{{font-family:"SF Mono",Menlo,monospace;font-size:11px;word-break:break-all}}
.uc a{{color:#2563eb;text-decoration:none}}
.uc a:hover{{text-decoration:underline}}
.fix-link{{color:#f59e0b!important}}
.ok{{color:#0d9488;font-weight:700;font-size:15px}}
.no{{color:#ef4444;font-weight:700;font-size:15px}}
.warn{{color:#f59e0b;font-weight:700;font-size:15px}}
.hc{{font-weight:600}}
.pr{{font-size:12px;color:#64748b}}
.note{{color:#94a3b8;font-size:11px}}

.ft{{text-align:center;padding:14px;font-size:12px;color:#94a3b8;background:#fff;border-top:1px solid #e2e5ea}}

@media(max-width:768px){{
.main.on{{flex-direction:column}}
.side{{width:100%;flex-direction:row;display:flex;overflow-x:auto;padding:8px 12px;border-right:none;border-bottom:1px solid #e2e5ea;height:auto}}
.side .ttl{{display:none}}
.blk{{border-left:none;border-bottom:3px solid transparent;white-space:nowrap;flex-shrink:0;font-size:13px;padding:8px 14px}}
.blk.on{{border-bottom-color:#1e40af;background:transparent}}
}}
</style>
</head>
<body>
<div class="hd">
<h1>🏆 2026世界杯时效性站点排查报告</h1>
<span class="ts">排查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} · 总URL {all_s['total']} · 有效 {all_s['valid']} · 非有效 {all_s['invalid']}</span>
</div>

<div class="tabs">
<button class="tb on" data-tab="m-domestic">🇨🇳 国内站点 ({cn_s['total']})</button>
<button class="tb" data-tab="m-international">🌍 境外站点 ({intl_s['total']})</button>
</div>

<!-- 国内 -->
<div class="main on" id="m-domestic">
<div class="side">
<div class="ttl">挖掘批次</div>
{cn_nav}
</div>
<div class="ctn">{cn_panels}</div>
</div>

<!-- 境外 -->
<div class="main" id="m-international">
<div class="side">
<div class="ttl">挖掘批次</div>
{intl_nav}
</div>
<div class="ctn">{intl_panels}</div>
</div>

<div class="ft">Generated by AI · {datetime.now().strftime('%Y-%m-%d %H:%M')} · 2026 World Cup Site Audit</div>

<script>
(function(){{
// Tab switching
document.querySelectorAll('.tb').forEach(function(btn){{
btn.addEventListener('click',function(){{
document.querySelectorAll('.tb').forEach(function(b){{b.classList.remove('on')}});
document.querySelectorAll('.main').forEach(function(m){{m.classList.remove('on')}});
this.classList.add('on');
document.getElementById(this.dataset.tab).classList.add('on');
}});
}});

// Batch switching
document.querySelectorAll('.blk').forEach(function(link){{
link.addEventListener('click',function(e){{
e.preventDefault();
var main = this.closest('.main');
main.querySelectorAll('.blk').forEach(function(l){{l.classList.remove('on')}});
this.classList.add('on');
var pid = this.getAttribute('panel-id');
main.querySelectorAll('.panel').forEach(function(p){{p.style.display='none'}});
var panel = document.getElementById(pid);
if(panel) panel.style.display='block';
}});
}});
}})();
</script>
</body>
</html>'''

out = '/Users/d.j.f/Documents/Claude/2026世界杯/世界杯时效性站点排查报告.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'✅ HTML v2 saved: {out}')
print(f'   国内: {cn_s["total"]} sites /  境外: {intl_s["total"]} sites')
print(f'   批次: 6月9日上午 / 6月8日 / 6月初')

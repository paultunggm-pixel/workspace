#!/usr/bin/env python3
"""v3: 修复国内空白、境外排版、批次显示逻辑"""
import json
from datetime import datetime

with open('/Users/d.j.f/Documents/Claude/2026世界杯/probe_results.json') as f:
    rows = json.load(f)

BATCH_LABELS = ['6月9日上午', '6月8日', '6月初']

for r in rows:
    d = r['date']
    if d == '6.9':    r['_batch'] = '6月9日上午'
    elif d == '6.8':  r['_batch'] = '6月8日'
    else:             r['_batch'] = '6月初'

def stats(sites):
    v=sum(1 for s in sites if s['is_list'])
    iv=sum(1 for s in sites if not s['is_list'])
    c=sum(1 for s in sites if s['corrected_url'])
    ur=sum(1 for s in sites if s['http_status']==0)
    return {'total':len(sites),'valid':v,'invalid':iv,'corrected':c,'unreachable':ur}

def make_nav_and_panels(cat):
    """为某个分类生成 侧栏HTML + 面板HTML。返回 (nav_html, panels_html)"""
    # 找出该分类下有数据的批次
    active_batches = []
    for bl in BATCH_LABELS:
        sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
        if sites:
            active_batches.append(bl)

    first_batch = active_batches[0] if active_batches else None

    # 侧栏
    nav = ''
    for bl in BATCH_LABELS:
        sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
        if not sites:
            continue
        on = 'on' if bl == first_batch else ''
        nav += f'<a class="blk {on}" data-pid="panel-{cat}-{bl}">{bl}<span class="bc">{len(sites)}</span></a>\n'

    # 面板
    panels = ''
    for bl in BATCH_LABELS:
        sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
        if not sites:
            continue
        s = stats(sites)
        display = 'block' if bl == first_batch else 'none'
        is_intl = (cat == '境外')
        extra_th = '<th style="width:80px">国家</th>' if is_intl else ''

        tbody = ''
        for i, r in enumerate(sites, 1):
            if r['is_list']:
                si, sc = '✅', 'ok'
            elif r['http_status'] == 0:
                si, sc = '🔴', 'warn'
            else:
                si, sc = '⚠️', 'no'

            curl = ''
            if r['corrected_url']:
                curl = f'<a href="{r["corrected_url"]}" target="_blank" class="fxl">{r["corrected_url"][:90]}</a>'
                cnote = r.get('corrected_note','')
                if cnote:
                    curl += f'<br><small class="note">{cnote}</small>'

            extra_td = f'<td>{r.get("country","")}</td>' if is_intl else ''

            tr_cls = []
            if r['http_status'] == 0:
                tr_cls.append('unr')
            if r['corrected_url']:
                tr_cls.append('fix')
            tr_attr = f' class="{" ".join(tr_cls)}"' if tr_cls else ''

            tbody += f'<tr{tr_attr}><td>{i}</td><td><b>{r["site"]}</b></td><td class="uc"><a href="{r["url"]}" target="_blank">{r["url"][:100]}</a></td>{extra_td}<td class="hc">{r["http_status"]}</td><td class="{sc}">{si}</td><td class="pr">{r["probe_result"]}</td><td class="uc">{curl or "-"}</td></tr>\n'

        panels += f'''<div class="panel" id="panel-{cat}-{bl}" style="display:{display}">
<div class="sr">
<span class="st"><em class="green">{s['valid']}</em> 有效</span>
<span class="st"><em class="red">{s['invalid']}</em> 非有效</span>
<span class="st"><em>{s['total']}</em> 总计</span>
<span class="st"><em class="orange">{s['corrected']}</em> 已补充</span>
<span class="st"><em class="gray">{s['unreachable']}</em> 不可达</span>
</div>
<div class="tbl"><table>
<thead><tr><th style="width:35px">#</th><th style="width:125px">站点</th><th>URL</th>{extra_th}<th style="width:45px">HTTP</th><th style="width:42px">有效</th><th style="width:180px">拨测结果</th><th>补充URL</th></tr></thead>
<tbody>{tbody}</tbody>
</table></div>
</div>\n'''

    return nav, panels

# ── 生成 ──
cn_nav, cn_panels = make_nav_and_panels('国内')
intl_nav, intl_panels = make_nav_and_panels('境外')

cn_s = stats([r for r in rows if r['category']=='国内'])
intl_s = stats([r for r in rows if r['category']=='境外'])
all_s = stats(rows)

now = datetime.now().strftime('%Y-%m-%d %H:%M')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026世界杯时效性站点排查报告</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6f8;color:#1a1a2e;line-height:1.6}}

.hd{{background:#fff;border-bottom:1px solid #e2e5ea;padding:0 32px;display:flex;align-items:center;justify-content:space-between;height:56px;min-width:900px}}
.hd h1{{font-size:17px;font-weight:700;color:#0f172a}}
.hd .ts{{font-size:12px;color:#8893a4}}

.tabs{{display:flex;background:#fff;padding:0 32px;border-bottom:1px solid #e2e5ea;min-width:900px}}
.tb{{padding:14px 28px;font-size:15px;cursor:pointer;border:none;background:none;color:#64748b;font-weight:500;border-bottom:3px solid transparent;transition:.2s}}
.tb:hover{{color:#1e40af}}
.tb.on{{color:#1e40af;border-bottom-color:#1e40af;font-weight:700}}

.main{{display:none}}
.main.on{{display:flex;min-height:calc(100vh - 116px)}}

.side{{width:200px;min-width:200px;background:#fff;border-right:1px solid #e2e5ea;overflow-y:auto;padding:16px 0}}
.side .ttl{{font-size:11px;color:#8893a4;text-transform:uppercase;letter-spacing:1px;padding:0 18px 12px;font-weight:600}}
.blk{{display:flex;justify-content:space-between;align-items:center;padding:10px 18px;text-decoration:none;color:#475569;font-size:14px;border-left:3px solid transparent;transition:.15s;cursor:pointer}}
.blk:hover{{background:#f1f5f9;color:#1e40af}}
.blk.on{{background:#eff6ff;color:#1e40af;border-left-color:#1e40af;font-weight:600}}
.bc{{font-size:11px;color:#94a3b8;background:#f1f5f9;padding:1px 8px;border-radius:10px}}
.blk.on .bc{{background:#dbeafe;color:#1e40af}}

.ctn{{flex:1;overflow-y:auto;padding:24px 28px;min-width:0}}
.panel{{animation:fadeIn .2s}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:translateY(0)}}}}

.sr{{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap}}
.st{{background:#fff;border:1px solid #e2e5ea;border-radius:10px;padding:12px 18px;text-align:center;min-width:85px;font-size:13px;color:#64748b}}
.st em{{display:block;font-size:24px;font-weight:700;font-style:normal;margin-bottom:1px}}
.st em.green{{color:#0d9488}}
.st em.red{{color:#ef4444}}
.st em.orange{{color:#f59e0b}}
.st em.gray{{color:#94a3b8}}

.tbl{{background:#fff;border:1px solid #e2e5ea;border-radius:10px;overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:13px;min-width:700px}}
thead{{background:#f8fafc}}
th{{padding:10px 10px;text-align:left;font-weight:600;color:#475569;font-size:12px;letter-spacing:.3px;white-space:nowrap}}
td{{padding:8px 10px;border-top:1px solid #f1f5f9;vertical-align:middle;font-size:13px;white-space:nowrap}}
td.uc{{white-space:normal;word-break:break-all}}
td.pr{{white-space:normal}}
tr:hover td{{background:#f8fafc}}
tr.unr td{{background:#fef2f2}}
tr.fix td:first-child{{border-left:3px solid #f59e0b}}
.uc{{font-family:"SF Mono",Menlo,monospace;font-size:11px}}
.uc a{{color:#2563eb;text-decoration:none}}
.uc a:hover{{text-decoration:underline}}
.fxl{{color:#f59e0b!important}}
.ok{{color:#0d9488;font-weight:700;font-size:15px}}
.no{{color:#ef4444;font-weight:700;font-size:15px}}
.warn{{color:#f59e0b;font-weight:700;font-size:15px}}
.hc{{font-weight:600}}
.pr{{font-size:12px;color:#64748b}}
.note{{color:#94a3b8;font-size:11px}}

.ft{{text-align:center;padding:14px;font-size:12px;color:#94a3b8;background:#fff;border-top:1px solid #e2e5ea}}
</style>
</head>
<body>
<div class="hd"><h1>🏆 2026世界杯时效性站点排查报告</h1><span class="ts">排查时间: {now} · 总URL {all_s['total']} · 有效 {all_s['valid']} · 非有效 {all_s['invalid']}</span></div>

<div class="tabs">
<button class="tb on" data-tab="m-domestic">🇨🇳 国内站点 ({cn_s['total']})</button>
<button class="tb" data-tab="m-international">🌍 境外站点 ({intl_s['total']})</button>
</div>

<div class="main on" id="m-domestic">
<div class="side"><div class="ttl">挖掘批次</div>{cn_nav}</div>
<div class="ctn">{cn_panels}</div>
</div>

<div class="main" id="m-international">
<div class="side"><div class="ttl">挖掘批次</div>{intl_nav}</div>
<div class="ctn">{intl_panels}</div>
</div>

<div class="ft">Generated by AI · {now} · 2026 World Cup Site Audit</div>

<script>
(function(){{
document.querySelectorAll('.tb').forEach(function(b){{
b.addEventListener('click',function(){{
document.querySelectorAll('.tb').forEach(function(x){{x.classList.remove('on')}});
document.querySelectorAll('.main').forEach(function(x){{x.classList.remove('on')}});
this.classList.add('on');
document.getElementById(this.dataset.tab).classList.add('on');
}});
}});
document.querySelectorAll('.blk').forEach(function(l){{
l.addEventListener('click',function(e){{
e.preventDefault();
var main=this.closest('.main');
main.querySelectorAll('.blk').forEach(function(x){{x.classList.remove('on')}});
this.classList.add('on');
main.querySelectorAll('.panel').forEach(function(p){{p.style.display='none'}});
var panel=document.getElementById(this.dataset.pid);
if(panel)panel.style.display='block';
}});
}});
}})();
</script>
</body>
</html>'''

out = '/Users/d.j.f/Documents/Claude/2026世界杯/世界杯时效性站点排查报告.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
import re
panel_ids = re.findall(r'id="panel-[^"]+"', html)
print(f'Generated: {out}')
print(f'  Total panels: {len(panel_ids)}')
print(f'  Unique panels: {len(set(panel_ids))}')
from collections import Counter
for pid, cnt in Counter(panel_ids).most_common():
    if cnt > 1: print(f'  ⚠️ DUPLICATE: {pid} x{cnt}')
# Check domestic
print(f'  国内 panels: {[p for p in panel_ids if "国内" in p]}')
print(f'  境外 panels: {[p for p in panel_ids if "境外" in p]}')
# Check display states
for p in panel_ids:
    idx = html.find(p)
    chunk = html[idx:idx+200]
    ds = re.search(r'display:(block|none)', chunk)
    print(f'  {p} -> display:{ds.group(1) if ds else "???"}')

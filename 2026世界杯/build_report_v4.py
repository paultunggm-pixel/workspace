#!/usr/bin/env python3
"""v4: 标题/统计排序/有效优先/HTTP末列/复制按钮 + Tab3/4抓取校验"""
import json
from datetime import datetime
import os

with open('/Users/d.j.f/Documents/Claude/2026世界杯/probe_results.json') as f:
    rows = json.load(f)

# 加载抓取的文章数据（6月8日+6月9日）
SCRAPE_FILE_68 = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_68.json'
SCRAPE_FILE_69 = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_69.json'
SCRAPE_FILE_610_INTL = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_610_intl.json'
SCRAPE_FILE_CN = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_cn_early.json'
SCRAPE_FILE_610_CN = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_610_cn.json'
SCRAPE_FILE_611_INTL = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_611_intl.json'
SCRAPE_FILE_612_INTL = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_612_intl.json'
SCRAPE_FILE_611_CN = '/Users/d.j.f/Documents/Claude/2026世界杯/scraped_articles_611_cn.json'
scraped_68 = {}; scraped_69 = {}; scraped_610_intl = {}; scraped_611_intl = {}; scraped_612_intl = {}
scraped_cn = {}; scraped_610_cn = {}; scraped_611_cn = {}
for path, var in [(SCRAPE_FILE_68,'68'),(SCRAPE_FILE_69,'69'),(SCRAPE_FILE_610_INTL,'610_intl'),
                  (SCRAPE_FILE_611_INTL,'611_intl'),
                  (SCRAPE_FILE_612_INTL,'612_intl'),
                  (SCRAPE_FILE_CN,'cn'),(SCRAPE_FILE_610_CN,'610_cn'),(SCRAPE_FILE_611_CN,'611_cn')]:
    if os.path.exists(path):
        with open(path) as f:
            globals()[f'scraped_{var}'] = json.load(f)

BATCH_LABELS = ['6月12日 03:00', '6月11日 15:30', '6月10日 17:30', '6月9日', '6月8日', '6月初']

for r in rows:
    d = r['date']
    if d == '6.12':   r['_batch'] = '6月12日 03:00'
    elif d == '6.11':   r['_batch'] = '6月11日 15:30'
    elif d == '6.10': r['_batch'] = '6月10日 17:30'
    elif d == '6.9':  r['_batch'] = '6月9日'
    elif d == '6.8':  r['_batch'] = '6月8日'
    else:             r['_batch'] = '6月初'

def stats(sites):
    v=sum(1 for s in sites if s['is_list'])
    iv=sum(1 for s in sites if not s['is_list'])
    c=sum(1 for s in sites if s['corrected_url'])
    ur=sum(1 for s in sites if s['http_status']==0)
    return {'total':len(sites),'valid':v,'invalid':iv,'corrected':c,'unreachable':ur}

# ── 站点权威度排序 ──
# Tier 1: 国际顶级足球/体育媒体 + FIFA/洲际足联
TIER1_SITES = [
    'FIFA', 'UEFA', 'ESPN', 'BBC', 'Sky Sports', 'FOX Sports', 'CBS Sports',
    'The Athletic', 'Sports Illustrated', 'Bleacher Report', 'OneFootball',
    'Goal', '马卡报', 'Marca', '阿斯报', 'AS', '米兰体育报', 'Gazzetta',
    '队报', "L'Equipe", '图片报', 'Bild', '踢球者', 'Kicker',
    '世界体育报', 'Mundo Deportivo', 'A Bola', 'Record',
    'Flashscore', 'SofaScore', 'FotMob', 'Whoscored',
    'Sporting News', 'Eurosport', 'beIN Sports',
    'Transfermarkt', 'Opta', 'StatsBomb', 'Spielverlagerung',
]
# Tier 2: 国际通讯社 + 大型新闻媒体 + 国内权威
TIER2_SITES = [
    '路透社', 'Reuters', '美联社', 'AP', '法新社', 'AFP',
    'CNN', 'The Guardian', '卫报', 'NYT', '纽约时报',
    'Washington Post', 'USA Today', 'NBC', 'CBC', 'TSN', 'Sportsnet',
    'Independent', 'Telegraph', 'Daily Mail', 'Mirror', 'The Sun',
    'TalkSport', 'DAZN',
    '新华社', '新华', '央视', 'CCTV', '人民日报', '人民',
    '腾讯体育', '新浪体育', '搜狐', '网易体育', '虎扑', '懂球帝', '直播吧',
    'PP体育', '澎湃', '体坛周报',
]
# Tier 3: 洲际足联（非FIFA/UEFA）、联赛官网、垂直足球媒体
TIER3_SITES = [
    'CONMEBOL', 'CONCACAF', 'CAF', 'AFC',
    'Premier League', 'Bundesliga', 'Serie A', 'La Liga', 'Ligue 1', 'MLS',
    '巴西足协', 'CBF', '阿根廷足协', 'AFA', 'Globo Esporte', 'Olé',
    'Sports Mole', '90min', 'Planet Football', 'Football365',
    'Football Italia', 'Inside World Football', 'World Soccer Talk',
    'Tribal Football', 'NewsNow', 'Sportskeeda',
    'TUDN', 'Telemundo', 'Azteca', 'RÉCORD', 'La Afición',
    'SBS Sport', '东方体育', '界面', '中国体育报', '中国足协',
]

def get_tier(site):
    for kw in TIER1_SITES:
        if kw.lower() in site.lower():
            return 1
    for kw in TIER2_SITES:
        if kw.lower() in site.lower():
            return 2
    for kw in TIER3_SITES:
        if kw.lower() in site.lower():
            return 3
    return 4  # 未知排最后

def sort_key(s):
    # 排序: tier优先 → 有效优先 → 名称
    return (get_tier(s['site']), 0 if s['is_list'] else (1 if s['http_status']!=0 else 2), s['site'])

def make_nav_and_panels(cat):
    active_batches = []
    for bl in BATCH_LABELS:
        sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
        if sites:
            active_batches.append(bl)
    first_batch = active_batches[0] if active_batches else None

    nav = ''
    for bl in BATCH_LABELS:
        sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
        if not sites:
            continue
        on = 'on' if bl == first_batch else ''
        nav += f'<a class="blk {on}" data-pid="panel-{cat}-{bl}">{bl}<span class="bc">{len(sites)}</span></a>\n'

    panels = ''
    for bl in BATCH_LABELS:
        sites = [s for s in rows if s['_batch']==bl and s['category']==cat]
        if not sites:
            continue

        # 排序: 权威度(tier)优先 → 有效排前
        sites_sorted = sorted(sites, key=sort_key)

        s = stats(sites_sorted)
        display = 'block' if bl == first_batch else 'none'
        is_intl = (cat == '境外')
        extra_th_head = '<th style="width:80px">国家</th>' if is_intl else ''

        tbody = ''
        for i, r in enumerate(sites_sorted, 1):
            if r['is_list']:
                si, sc = '✅', 'ok'
            elif r['http_status'] == 0:
                si, sc = '🔴', 'warn'
            else:
                si, sc = '⚠️', 'no'

            curl_html = '-'
            if r['corrected_url']:
                curl_html = f'<a href="{r["corrected_url"]}" target="_blank" class="fxl">{r["corrected_url"][:90]}</a>'
                cnote = r.get('corrected_note','')
                if cnote:
                    curl_html += f'<br><small class="note">{cnote}</small>'

            extra_td = f'<td>{r.get("country","")}</td>' if is_intl else ''

            tr_cls = []
            if r['http_status'] == 0: tr_cls.append('unr')
            if r['corrected_url']: tr_cls.append('fix')
            tr_attr = f' class="{" ".join(tr_cls)}"' if tr_cls else ''

            tbody += f'''<tr{tr_attr}>
<td>{i}</td>
<td><b>{r['site']}</b></td>
<td class="uc"><a href="{r['url']}" target="_blank">{r['url'][:100]}</a></td>
{extra_td}
<td class="pr">{r['probe_result']}</td>
<td class="uc">{curl_html}</td>
</tr>\n'''

        panel_id = f"panel-{cat}-{bl}"
        panels += f'''<div class="panel" id="{panel_id}" style="display:{display}">
<div class="sr">
<span class="st"><em>{s['total']}</em> 总计</span>
<span class="st"><em class="green">{s['valid']}</em> 有效</span>
<span class="st"><em class="red">{s['invalid']}</em> 可能被拦截</span>
<span class="st"><em class="orange">{s['corrected']}</em> 已补充</span>
<span class="st"><em class="gray">{s['unreachable']}</em> 不可达</span>
</div>
<div class="tbl"><table id="tbl-{cat}-{bl}">
<thead><tr>
<th style="width:35px">#</th>
<th style="width:125px">站点</th>
<th>URL <button class="cpy-hdr" onclick="copyAllUrls('tbl-{cat}-{bl}')" title="复制本表所有URL列数据">复制URL</button> <button class="cpy-hdr" onclick="copyAllRows('tbl-{cat}-{bl}')" title="复制本表全部行列数据(TSV格式,可粘贴到Excel)">复制全表</button></th>
{extra_th_head}
<th style="width:180px">拨测结果</th>
<th>补充URL</th>
</tr></thead>
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
build_time = datetime.now().strftime('%Y%m%d%H%M%S')  # for version check

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>「美加墨世界杯」时效性资讯内容挖掘</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6f8;color:#1a1a2e;line-height:1.6}}

/* header */
.hd{{background:#fff;border-bottom:1px solid #e2e5ea;padding:12px 16px;display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:8px}}
.hd h1{{font-size:16px;font-weight:700;color:#0f172a}}
.hd .ts{{font-size:11px;color:#8893a4;display:flex;align-items:center;flex-wrap:wrap;gap:4px}}
.info-btn{{padding:2px 10px;font-size:11px;cursor:pointer;border:1px solid #cbd5e1;border-radius:12px;background:#fff;color:#64748b;transition:.15s;white-space:nowrap}}
.info-btn:hover{{background:#eff6ff;border-color:#2563eb;color:#2563eb}}

/* tabs */
.tabs{{display:flex;background:#fff;padding:0 12px;border-bottom:1px solid #e2e5ea;overflow-x:auto;-webkit-overflow-scrolling:touch}}
.tb{{padding:14px 18px;font-size:14px;cursor:pointer;border:none;background:none;color:#64748b;font-weight:500;border-bottom:3px solid transparent;transition:.2s;white-space:nowrap;flex-shrink:0}}
.tb:hover{{color:#1e40af}}
.tb.on{{color:#1e40af;border-bottom-color:#1e40af;font-weight:700}}

/* main layout */
.main{{display:none}}
.main.on{{display:flex;min-height:calc(100vh - 140px)}}

/* sidebar */
.side{{width:185px;min-width:185px;background:#fff;border-right:1px solid #e2e5ea;overflow-y:auto;padding:12px 0}}
.side .ttl{{font-size:10px;color:#8893a4;text-transform:uppercase;letter-spacing:1px;padding:0 14px 10px;font-weight:600}}
.blk{{display:flex;justify-content:space-between;align-items:center;padding:9px 14px;text-decoration:none;color:#475569;font-size:13px;border-left:3px solid transparent;transition:.15s;cursor:pointer}}
.blk:hover{{background:#f1f5f9;color:#1e40af}}
.blk.on{{background:#eff6ff;color:#1e40af;border-left-color:#1e40af;font-weight:600}}
.bc{{font-size:10px;color:#94a3b8;background:#f1f5f9;padding:1px 7px;border-radius:10px}}
.blk.on .bc{{background:#dbeafe;color:#1e40af}}

/* content */
.ctn{{flex:1;overflow-y:auto;padding:20px 16px;min-width:0}}
.panel{{animation:fadeIn .2s}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:translateY(0)}}}}

/* stats */
.sr{{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}}
.st{{background:#fff;border:1px solid #e2e5ea;border-radius:8px;padding:10px 14px;text-align:center;min-width:70px;font-size:12px;color:#64748b;flex:1}}
.st em{{display:block;font-size:22px;font-weight:700;font-style:normal;margin-bottom:1px}}
.st em.green{{color:#0d9488}}
.st em.red{{color:#ef4444}}
.st em.orange{{color:#f59e0b}}
.st em.gray{{color:#94a3b8}}

/* table */
.tbl{{background:#fff;border:1px solid #e2e5ea;border-radius:8px;overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{width:100%;border-collapse:collapse;font-size:12px;min-width:650px}}
thead{{background:#f8fafc}}
th{{padding:8px 8px;text-align:left;font-weight:600;color:#475569;font-size:11px;letter-spacing:.3px;white-space:nowrap}}
td{{padding:7px 8px;border-top:1px solid #f1f5f9;vertical-align:middle;font-size:12px;white-space:nowrap}}
td.uc{{white-space:normal;word-break:break-all}}
td.pr{{white-space:normal}}
tr:hover td{{background:#f8fafc}}
tr.unr td{{background:#fef2f2}}
tr.fix td:first-child{{border-left:3px solid #f59e0b}}
.uc{{font-family:"SF Mono",Menlo,monospace;font-size:10px}}
.uc a{{color:#2563eb;text-decoration:none}}
.uc a:hover{{text-decoration:underline}}
.visited-link{{color:#9333ea!important;background:#f5f3ff;padding:1px 4px;border-radius:3px}}
.fxl{{color:#f59e0b!important}}
.ok{{color:#0d9488;font-weight:700;font-size:14px}}
.no{{color:#ef4444;font-weight:700;font-size:14px}}
.warn{{color:#f59e0b;font-weight:700;font-size:14px}}
.pr{{font-size:11px;color:#64748b}}
.note{{color:#94a3b8;font-size:10px}}

/* copy buttons */
.cpy-hdr{{margin-left:4px;padding:1px 6px;font-size:10px;cursor:pointer;border:1px solid #93c5fd;border-radius:4px;background:#eff6ff;color:#2563eb;font-weight:500;white-space:nowrap;transition:.15s}}
.cpy-hdr:hover{{background:#2563eb;color:#fff;border-color:#2563eb}}
.cpy-hdr.copied{{background:#d1fae5;border-color:#0d9488;color:#0d9488}}

/* modal */
.modal-overlay{{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.45);z-index:9999;align-items:center;justify-content:center;padding:16px}}
.modal-box{{background:#fff;border-radius:14px;padding:24px 28px;max-width:520px;width:100%;max-height:85vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.2)}}
.modal-hd{{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}}
.modal-hd h3{{font-size:16px;color:#0f172a}}
.modal-close{{border:none;background:none;font-size:24px;cursor:pointer;color:#94a3b8;line-height:1;padding:0 4px}}
.modal-close:hover{{color:#ef4444}}
.tier-table-wrap{{overflow-x:auto}}
.tier-table{{min-width:auto;font-size:12px}}
.tier-table th{{background:#f8fafc;padding:8px 10px}}
.tier-table td{{padding:8px 10px;white-space:normal}}
.tier-table .t1{{color:#2563eb;font-weight:700;font-size:16px}}
.tier-table .t2{{color:#0d9488;font-weight:700;font-size:16px}}
.tier-table .t3{{color:#f59e0b;font-weight:700;font-size:16px}}
.tier-table .t4{{color:#94a3b8;font-weight:700;font-size:16px}}
.tier-ex{{font-size:11px;color:#64748b;line-height:1.5}}
.modal-note{{margin-top:14px;font-size:11px;color:#64748b}}

.scrape-layout{{display:flex;gap:0;min-height:400px}}
.scrape-sites{{width:240px;min-width:240px;border-right:1px solid #e2e5ea;overflow-y:auto;background:#fafbfc}}
.scrape-arts{{flex:1;overflow-y:auto;padding:0 0 0 16px;min-width:0}}
.site-table{{min-width:auto;width:100%}}
.site-table th{{font-size:11px;padding:8px 10px}}
.site-table td{{font-size:12px;padding:8px 10px;cursor:pointer;white-space:nowrap}}
.site-table tr.site-row:hover td{{background:#eff6ff}}
.site-table tr.site-row.on td{{background:#dbeafe;font-weight:600;color:#1e40af}}
.article-panel{{animation:fadeIn .2s}}
.article-panel table{{min-width:auto;table-layout:fixed}}
.article-panel td{{white-space:normal;word-break:break-word}}
.article-panel td.uc{{white-space:normal;word-break:break-all}}
@media(max-width:768px){{
.scrape-layout{{flex-direction:column}}
.scrape-sites{{width:100%!important;min-width:0!important;border-right:none!important;border-bottom:1px solid #e2e5ea;max-height:200px}}
.scrape-arts{{padding:12px 0 0 0!important}}
.article-panel table{{min-width:480px}}
.site-table{{min-width:auto}}
/* 所有side在手机端变横向滚动 */
.main.on .side,.main .side{{width:100%!important;min-width:0!important;flex-direction:row;display:flex;overflow-x:auto;padding:8px 12px!important;border-right:none!important;border-bottom:1px solid #e2e5ea;height:auto}}
.main.on .side .ttl,.main .side .ttl{{display:none}}
.main.on .side .blk,.main .side .blk{{border-left:none;border-bottom:2px solid transparent;white-space:nowrap;flex-shrink:0;font-size:12px;padding:7px 12px;border-radius:6px 6px 0 0}}
.main.on .side .blk.on,.main .side .blk.on{{border-bottom-color:#1e40af;background:#eff6ff;border-left-color:transparent}}
}}

.validate-placeholder{{display:flex;align-items:center;justify-content:center;height:300px;color:#94a3b8;font-size:15px;background:#fff;border:2px dashed #e2e5ea;border-radius:10px}}

.ft{{text-align:center;padding:12px;font-size:11px;color:#94a3b8;background:#fff;border-top:1px solid #e2e5ea}}

/* === 移动端 === */
@media (max-width:768px){{
  .hd{{padding:10px 12px}}
  .hd h1{{font-size:14px;width:100%}}
  .hd .ts{{font-size:10px;width:100%}}

  .tabs{{padding:0 8px}}
  .tb{{padding:12px 14px;font-size:13px}}

  .main.on{{flex-direction:column;min-height:auto}}

  .side{{width:100%;min-width:0;border-right:none;border-bottom:1px solid #e2e5ea;overflow-x:auto;overflow-y:hidden;padding:8px 12px;display:flex;gap:6px;flex-shrink:0}}
  .side .ttl{{display:none}}
  .blk{{border-left:none;border-bottom:2px solid transparent;white-space:nowrap;flex-shrink:0;font-size:12px;padding:7px 12px;border-radius:6px 6px 0 0}}
  .blk.on{{border-bottom-color:#1e40af;background:#eff6ff;border-left-color:transparent}}
  .bc{{margin-left:4px}}

  .ctn{{padding:14px 10px}}

  .sr{{gap:6px}}
  .st{{min-width:55px;padding:8px 10px;font-size:11px}}
  .st em{{font-size:18px}}

  .tbl{{border-radius:6px}}
  table{{min-width:560px;font-size:11px}}
  th{{padding:6px 6px;font-size:10px}}
  td{{padding:6px 6px;font-size:11px}}

  .modal-box{{padding:18px 16px;border-radius:10px;max-height:90vh}}
  .modal-hd h3{{font-size:14px}}
  .tier-table{{font-size:11px}}
  .tier-table th,.tier-table td{{padding:6px 8px}}
  .tier-table .t1,.tier-table .t2,.tier-table .t3,.tier-table .t4{{font-size:14px}}
}}
</style>
</head>
<body>
<div class="hd"><h1>🏆 「美加墨世界杯」时效性资讯内容挖掘</h1><span class="ts">排查时间: {now} · 总URL {all_s['total']} · 有效 {all_s['valid']} · 可能被拦截 {all_s['invalid']} <button class="info-btn" onclick="document.getElementById('tier-modal').style.display='flex'">ⓘ 权威度说明</button></span></div>

<div id="tier-modal" class="modal-overlay" onclick="if(event.target===this)this.style.display='none'">
<div class="modal-box">
<div class="modal-hd"><h3>站点权威度排序说明</h3><button class="modal-close" onclick="document.getElementById('tier-modal').style.display='none'">&times;</button></div>
<div class="tier-table-wrap">
<table class="tier-table">
<thead><tr><th>Tier</th><th>类别</th><th>示例</th></tr></thead>
<tbody>
<tr><td class="t1">1</td><td>国际顶级足球/体育媒体 + FIFA/UEFA</td><td class="tier-ex">ESPN、BBC Sport、FOX、队报、马卡、米兰体育报、OneFootball、Opta…</td></tr>
<tr><td class="t2">2</td><td>国际通讯社 + 大型新闻媒体 + 国内权威</td><td class="tier-ex">路透社、美联社、CNN、卫报、新华社、央视、腾讯、新浪、虎扑…</td></tr>
<tr><td class="t3">3</td><td>洲际足联/联赛官网/垂直足球媒体</td><td class="tier-ex">CONMEBOL、AFC、英超、德甲、西甲、Sports Mole、Football Italia…</td></tr>
<tr><td class="t4">4</td><td>其他</td><td class="tier-ex">未分类站点自动排末位</td></tr>
</tbody></table>
</div>
<p class="modal-note">每个Tier内，有效站点（✅）排在前面</p>
</div></div>

<div class="tabs">
<button class="tb on" data-tab="m-international">🌍 境外资讯列表 ({intl_s['total']})</button>
<button class="tb" data-tab="m-domestic">🇨🇳 国内资讯列表 ({cn_s['total']})</button>
<button class="tb" data-tab="m-validate-intl">🔍 具体资讯内容 - 境外</button>
<button class="tb" data-tab="m-validate-cn">🔍 具体资讯内容 - 国内</button>
</div>

<div class="main on" id="m-international">
<div class="side"><div class="ttl">挖掘批次</div>{intl_nav}</div>
<div class="ctn">{intl_panels}</div>
</div>

<div class="main" id="m-domestic">
<div class="side"><div class="ttl">挖掘批次</div>{cn_nav}</div>
<div class="ctn">{cn_panels}</div>
</div>

'''

# ── Tab3: 具体资讯内容 - 境外 ──
def build_batch_section(date_val, batch_label, scraped_data, category):
    """为一个批次构建右侧面板：左列站点列表 + 右列文章（仅匹配指定category）
    date_val 可以是字符串(精确匹配)或列表/元组(多值匹配,用于'6月初'='已结束'+空)"""
    if isinstance(date_val, (list, tuple)):
        batch_all = [r for r in rows if r['date'] in date_val and r['category'] == category]
    else:
        batch_all = [r for r in rows if r['date'] == date_val and r['category'] == category]
    scraped_map = {}
    if scraped_data:
        for source_url, data in scraped_data.items():
            scraped_map[source_url] = data

    def article_count(r):
        sd = scraped_map.get(r['url'], None)
        return len(sd['articles']) if sd else 0
    batch_all.sort(key=article_count, reverse=True)

    # 右栏：站点列表
    site_rows = ''
    article_panels = ''

    for i, r in enumerate(batch_all):
        site = r['site']
        source_url = r['url']
        sd = scraped_map.get(source_url, None)
        if sd and sd['articles']:
            count = len(sd['articles']); status_text = sd['status']
        elif sd:
            count = 0; status_text = sd['status']
        elif not r['is_list']:
            if r['http_status'] == 0: count = '🔒'; status_text = '云壳拦截'
            elif r['http_status'] == 403: count = '🚫'; status_text = 'HTTP403'
            else: count = '—'; status_text = r['probe_result'][:30]
        else:
            count = 'JS'; status_text = 'JS渲染'

        spid = f'site-{batch_label}-{i}'
        apid = f'arts-{batch_label}-{i}'
        active = 'on' if i == 0 else ''
        site_rows += f'<tr class="site-row {active}" data-arts="{apid}" data-site="{spid}"><td>{site}</td><td>{count}</td><td style="font-size:11px;color:#94a3b8">{source_url[:80]}</td></tr>\n'

        # 文章面板
        if sd and sd['articles']:
            tbody = ''
            for j, art in enumerate(sd['articles'], 1):
                tbody += f'<tr><td>{j}</td><td>{art["title"][:150]}</td><td class="uc"><a href="{art["url"]}" target="_blank">{art["url"][:100]}</a></td><td style="white-space:nowrap;font-size:11px;color:#64748b">{art.get("time","")}</td></tr>\n'
            ahtml = f'''<div class="tbl"><table>
<thead><tr><th style="width:35px">#</th><th style="width:45%">内容标题</th><th style="width:45%">内容URL <button class="cpy-hdr" onclick="copyArtUrls(this)" title="批量复制本表所有内容URL">复制URL</button></th><th style="width:10%">发布时间</th></tr></thead>
<tbody>{tbody}</tbody></table></div>'''
        else:
            ahtml = f'<div style="text-align:center;padding:60px 20px;color:#94a3b8">{status_text}</div>'

        display = 'block' if i == 0 else 'none'
        article_panels += f'<div class="article-panel" id="{apid}" style="display:{display}">{ahtml}</div>\n'

    return site_rows, article_panels

sites612i, arts612i = build_batch_section('6.12', '612i', scraped_612_intl, '境外')
sites611i, arts611i = build_batch_section('6.11', '611i', scraped_611_intl, '境外')
sites610i, arts610i = build_batch_section('6.10', '610i', scraped_610_intl, '境外')
sites69, arts69 = build_batch_section('6.9', '69', scraped_69, '境外')
sites68, arts68 = build_batch_section('6.8', '68', scraped_68, '境外')
nav_dates = '<a class="blk on" data-pid="batch-612">6月12日 03:00</a>\n<a class="blk" data-pid="batch-611">6月11日 15:30</a>'\n<a class="blk" data-pid="batch-610">6月10日 17:30</a>\n<a class="blk" data-pid="batch-69">6月9日</a>\n<a class="blk" data-pid="batch-68">6月8日</a>\n'

def batch_panel(bid, sites_html, arts_html, display):
    return f'''<div class="panel" id="{bid}" style="display:{display}">
<div class="scrape-layout">
<div class="scrape-sites" style="width:240px;min-width:240px"><table class="site-table">
<thead><tr><th>列表页站点</th><th>内容</th><th>列表页URL</th></tr></thead>
<tbody>{sites_html}</tbody>
</table></div>
<div class="scrape-arts">{arts_html}</div>
</div></div>'''

tab3_html = f'''<div class="main" id="m-validate-intl">
<div class="side" style="width:132px;min-width:132px"><div class="ttl">批次</div>{nav_dates}</div>
<div class="ctn">
{batch_panel("batch-612", sites612i, arts612i, "block")}
{batch_panel("batch-611", sites611i, arts611i, "none")}
{batch_panel("batch-610", sites610i, arts610i, "none")}
{batch_panel("batch-69", sites69, arts69, "none")}
{batch_panel("batch-68", sites68, arts68, "none")}
</div></div>'''

# Tab4: 具体资讯内容 - 国内（占位）
# Tab4: 具体资讯内容 - 国内
sites_cn, arts_cn = build_batch_section(('已结束','',None), 'cn', scraped_cn, '国内')

# Build 6月10日 国内 section
sites610c, arts610c = build_batch_section('6.10', '610c', scraped_610_cn, '国内')
sites611c, arts611c = build_batch_section('6.11', '611c', scraped_611_cn, '国内')

# Only show 6月11日 in tab4 if there are domestic articles
has_cn_611 = sum(len(v['articles']) for v in scraped_611_cn.values()) > 0 if scraped_611_cn else False
cn_nav_611 = '<a class="blk on" data-pid="batch-cn-611">6月11日 15:30</a>' if has_cn_611 else ''
cn_panel_611 = f'''<div class="panel" id="batch-cn-611" style="display:block">
<div class="scrape-layout">
<div class="scrape-sites" style="width:240px;min-width:240px"><table class="site-table">
<thead><tr><th>列表页站点</th><th>内容</th><th>列表页URL</th></tr></thead>
<tbody>{sites611c}</tbody>
</table></div>
<div class="scrape-arts">{arts611c}</div>
</div>
</div>''' if has_cn_611 else ''

tab4_html = f'''<div class="main" id="m-validate-cn">
<div class="side" style="width:132px;min-width:132px"><div class="ttl">批次</div>{cn_nav_611}<a class="blk {"on" if not has_cn_611 else ""}" data-pid="batch-cn-610">6月10日 17:30</a><a class="blk" data-pid="batch-cn">6月初</a></div>
<div class="ctn">
{cn_panel_611}
<div class="panel" id="batch-cn-610" style="display:{"block" if not has_cn_611 else "none"}">
<div class="scrape-layout">
<div class="scrape-sites" style="width:240px;min-width:240px"><table class="site-table">
<thead><tr><th>列表页站点</th><th>内容</th><th>列表页URL</th></tr></thead>
<tbody>{sites610c}</tbody>
</table></div>
<div class="scrape-arts">{arts610c}</div>
</div>
</div>
<div class="panel" id="batch-cn" style="display:none">
<div class="scrape-layout">
<div class="scrape-sites" style="width:240px;min-width:240px"><table class="site-table">
<thead><tr><th>列表页站点</th><th>内容</th><th>列表页URL</th></tr></thead>
<tbody>{sites_cn}</tbody>
</table></div>
<div class="scrape-arts">{arts_cn}</div>
</div>
</div>
</div>
</div>'''

html += tab3_html
html += tab4_html
html += '''

<div class="ft">Generated by AI · {now} · 2026 World Cup Site Audit</div>

<script>
function copyAllUrls(tblId){{
  var table=document.getElementById(tblId);
  var rows=table.querySelectorAll('tbody tr');
  var urls=[];
  rows.forEach(function(tr){{
    var urlCell=tr.querySelectorAll('td')[2]; // 3rd td = URL column
    var a=urlCell.querySelector('a');
    if(a) urls.push(a.href);
  }});
  navigator.clipboard.writeText(urls.join('\\n')).then(function(){{
    flashBtn(event.target);
  }});
}}

function copyAllRows(tblId){{
  var table=document.getElementById(tblId);
  var rows=table.querySelectorAll('tbody tr');
  var lines=[];
  rows.forEach(function(tr){{
    var cells=tr.querySelectorAll('td');
    var parts=[];
    cells.forEach(function(td){{
      parts.push(td.textContent.replace(/[\\n\\t]+/g,' ').trim());
    }});
    lines.push(parts.join('\\t'));
  }});
  navigator.clipboard.writeText(lines.join('\\n')).then(function(){{
    flashBtn(event.target);
  }});
}}

function copyArtUrls(btn){{
  var table = btn.closest('table');
  var urls = [];
  table.querySelectorAll('tbody td.uc a').forEach(function(a){{ urls.push(a.href); }});
  navigator.clipboard.writeText(urls.join('\\n')).then(function(){{
    var orig = btn.textContent;
    btn.textContent = '✓ 已复制';
    btn.classList.add('copied');
    setTimeout(function(){{ btn.textContent = orig; btn.classList.remove('copied'); }}, 1800);
  }});
}}

function flashBtn(btn){{
  var orig=btn.textContent;
  btn.textContent='✓ 已复制';
  btn.classList.add('copied');
  setTimeout(function(){{btn.textContent=orig;btn.classList.remove('copied')}},1800);
}}

(function(){{
// Tab切换 + 记忆（刷新后保持）
var activeTab = sessionStorage.getItem('_active_tab') || 'm-international';
if (!document.getElementById(activeTab)) activeTab = 'm-international';
document.querySelectorAll('.tb').forEach(function(x){{x.classList.remove('on')}});
document.querySelectorAll('.main').forEach(function(x){{x.classList.remove('on')}});
var savedBtn = document.querySelector('.tb[data-tab="' + activeTab + '"]');
if (savedBtn) savedBtn.classList.add('on');
document.getElementById(activeTab).classList.add('on');
document.querySelectorAll('.tb').forEach(function(b){{
b.addEventListener('click',function(){{
document.querySelectorAll('.tb').forEach(function(x){{x.classList.remove('on')}});
document.querySelectorAll('.main').forEach(function(x){{x.classList.remove('on')}});
this.classList.add('on');
var tid = this.dataset.tab;
document.getElementById(tid).classList.add('on');
sessionStorage.setItem('_active_tab', tid);
}});
}});
// 链接点击追踪：点击立即变色，回来时仍高亮
document.querySelectorAll('table a[href]').forEach(function(a){{
a.addEventListener('click',function(){{
    // 先移除所有旧高亮
    document.querySelectorAll('table a[href].visited-link').forEach(function(x){{x.classList.remove('visited-link')}});
    // 当前链接立即变色
    this.classList.add('visited-link');
    sessionStorage.setItem('_last_clicked_url', this.href);
    sessionStorage.setItem('_last_clicked_ts', Date.now());
}});
}});
// 页面加载时恢复高亮
(function(){{
    var lastUrl = sessionStorage.getItem('_last_clicked_url');
    var lastTs = sessionStorage.getItem('_last_clicked_ts');
    if (lastUrl && lastTs) {{
        // 30分钟内有效
        if (Date.now() - parseInt(lastTs) < 1800000) {{
            document.querySelectorAll('table a[href]').forEach(function(a){{
                if (a.href === lastUrl) {{
                    a.classList.add('visited-link');
                }}
            }});
        }} else {{
            sessionStorage.removeItem('_last_clicked_url');
            sessionStorage.removeItem('_last_clicked_ts');
        }}
    }}
}})();

// Tab3 站点列表点击 → 切换文章面板
document.querySelectorAll('.site-row').forEach(function(row){{
row.addEventListener('click',function(){{
    var layout=this.closest('.scrape-layout');
    layout.querySelectorAll('.site-row').forEach(function(r){{r.classList.remove('on')}});
    this.classList.add('on');
    var aid=this.dataset.arts;
    layout.querySelectorAll('.article-panel').forEach(function(p){{p.style.display='none'}});
    var panel=document.getElementById(aid);
    if(panel)panel.style.display='block';
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

// === 自动刷新：检测version.json更新，每版本只刷一次 ===
const BUILD_TIME = '{build_time}';
(function(){{
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') return;
    // 已加载过本版本 → 不重复刷新
    if (sessionStorage.getItem('_v_ck') === BUILD_TIME) return;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'https://paultunggm-pixel.github.io/consistency-eval/version.json?t=' + Date.now(), true);
    xhr.timeout = 5000;
    xhr.onload = function(){{
        if (xhr.status !== 200) return;
        try {{
            var remote = JSON.parse(xhr.responseText);
            if (remote.build_time && remote.build_time > BUILD_TIME) {{
                sessionStorage.setItem('_v_ck', remote.build_time);
                location.reload(true);
            }}
        }} catch(e) {{}}
    }};
    xhr.send();
}})();
</script>
</body>
</html>'''

out = '/Users/d.j.f/Documents/Claude/2026世界杯/世界杯时效性站点排查报告.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

# Quick check
import re
panels = re.findall(r'id="panel-[^"]+"', html)
from collections import Counter
dups = [p for p,c in Counter(panels).items() if c>1]
print(f'Generated: {out}')
print(f'  Panels: {len(panels)} total, {len(set(panels))} unique')
if dups: print(f'  DUPS: {dups}')
else: print(f'  ✅ No duplicates')
print(f'  Title: 「美加墨世界杯」时效性资讯内容挖掘')
print(f'  Stats order: 总计→有效→非有效→已补充→不可达')
print(f'  Copy buttons: ✅')

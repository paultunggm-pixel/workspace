#!/usr/bin/env python3
"""审查并修正非世界杯频道/列表的URL，替换为正确的世界杯专题页"""
import json, re, requests
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('/Users/d.j.f/Documents/Claude/2026世界杯/probe_results.json') as f:
    rows = json.load(f)

# ── WC-specific URL patterns (URL应命中至少一个) ──
WC_PATH_PATTERNS = [
    r'/world[_-]?cup', r'/worldcup', r'/wm[_-]?2026', r'/wm2026',
    r'/coupe[_-]du[_-]monde', r'/mondial', r'/mundial',
    r'/copa[_-]do[_-]mundo', r'/copa[_-]mundo',
    r'/fifa[_-]world', r'/fifa2026',
    r'/2026[_-]fifa', r'2026.*world',
    r'worldcup2026', r'world-cup-2026',
]

def is_wc_url(url):
    return any(re.search(p, url, re.IGNORECASE) for p in WC_PATH_PATTERNS)

# ── 已知需要修正的URL映射 ──
URL_FIXES = {
    # 搜狐 → WC子站
    'https://sports.sohu.com/guojizuqiu/': 'https://worldcup2026.sohu.com/',
    'https://sports.sohu.com/worldcup/': 'https://worldcup2026.sohu.com/',
    # 腾讯 → WC频道
    'https://sports.qq.com/isocce/': 'https://sports.qq.com/worldcup2026/',
    'https://sports.qq.com/worldcup/': 'https://sports.qq.com/worldcup2026/',
    # 网易体育已在列表中
    # 凤凰体育 → WC专题
    'https://sports.ifeng.com/guojizuqiu/': 'https://sports.ifeng.com/worldcup2026/',
    # 新浪已在列表中（sports.sina.com.cn/g/worldcup/）
    # 体坛周报
    'https://www.titan24.com/international/': 'https://www.titan24.com/worldcup2026/',
    'https://www.titan24.com/worldcup/': 'https://www.titan24.com/worldcup2026/',
    # 央视
    'https://sports.cctv.com/football/': 'https://sports.cctv.com/worldcup2026/',
    # 人民日报
    'http://sports.people.com.cn/': 'http://sports.people.com.cn/worldcup2026/',
    # 新华社
    'http://www.news.cn/sports/': 'http://www.news.cn/sports/worldcup2026/',
    # 澎湃
    'https://www.thepaper.cn/list_25424': 'https://www.thepaper.cn/worldcup2026/',
    # ESPN
    'https://www.espn.com/soccer/': 'https://www.espn.com/soccer/league/_/name/fifa.world.cup',
    'https://www.espn.com/soccer/league/_/name/fifa.world.cup': None,  # already WC
    # FOX
    'https://www.foxsports.com/soccer': 'https://www.foxsports.com/soccer/2026-fifa-world-cup',
    # Premier League - 无专门WC频道，保持新闻页
    # Bundesliga - WC专题已在列表
    # La Liga
    'https://www.laliga.com/en-GB/news': 'https://www.laliga.com/en-GB/world-cup-2026',
    # Serie A
    'https://www.legaseriea.it/en/media/news': 'https://www.legaseriea.it/en/world-cup-2026',
    # Ligue 1
    'https://www.ligue1.com/Articles': 'https://www.ligue1.com/world-cup-2026',
    # MLS
    'https://www.mlssoccer.com/news/': 'https://www.mlssoccer.com/news/topic/world-cup',
    # NBC
    'https://www.nbcsports.com/soccer': 'https://www.nbcsports.com/soccer/fifa-world-cup-2026',
    # CNN
    'https://edition.cnn.com/sport/football': 'https://edition.cnn.com/sport/football/world-cup-2026',
    # USA Today
    'https://www.usatoday.com/sports/soccer/': 'https://www.usatoday.com/sports/fifa-world-cup-2026/',
    # TSN
    'https://www.tsn.ca/soccer/fifa-world-cup': 'https://www.tsn.ca/soccer/fifa-world-cup-2026',
    # Sportsnet
    'https://www.sportsnet.ca/soccer/': 'https://www.sportsnet.ca/soccer/world-cup-2026/',
    # CBC
    'https://www.cbc.ca/sports/soccer': 'https://www.cbc.ca/sports/soccer/worldcup2026',
    # Sky Sports
    'https://www.skysports.com/football/news': 'https://www.skysports.com/football/world-cup-2026',
    # Sporting News
    'https://www.sportingnews.com/us/soccer/news/world-cup': 'https://www.sportingnews.com/us/soccer/fifa-world-cup-2026',
    # Goal
    'https://www.goal.com/en/fifa-world-cup/news': 'https://www.goal.com/en/fifa-world-cup-2026',
    # 90min
    'https://www.90min.com/fifa-world-cup': 'https://www.90min.com/fifa-world-cup-2026',
    # TalkSport
    'https://talksport.com/football/world-cup-2026/': None,  # already WC
    # The Sun
    'https://www.thesun.co.uk/sport/football/world-cup-2026/': None,  # already WC
    # Mirror
    'https://www.mirror.co.uk/all-about/world-cup-2026': None,  # already WC
    # Daily Mail → WC版
    'https://www.dailymail.co.uk/sport/football/world-cup-2026/index.html': None,  # already WC
    # Telegraph
    'https://www.telegraph.co.uk/world-cup-2026/': None,  # already WC
    # Eurosport
    'https://www.eurosport.com/football/world-cup/': 'https://www.eurosport.com/football/world-cup-2026/',
    # beIN Sports
    'https://www.beinsports.com/en-us/football/world-cup': 'https://www.beinsports.com/en-us/football/fifa-world-cup-2026',
    # DAZN
    'https://www.dazn.com/en-US/news/soccer/': 'https://www.dazn.com/en-US/news/soccer/fifa-world-cup-2026',
    # 虎扑
    'https://soccer.hupu.com/news/': 'https://soccer.hupu.com/worldcup2026/',
    'https://bbs.hupu.com/worldcup': None,  # already WC
    # 界面新闻
    'https://www.jiemian.com/lists/134.html': 'https://www.jiemian.com/worldcup2026/',
    # 央视网
    'https://news.cctv.com/sports/': 'https://sports.cctv.com/worldcup2026/',
    # ESPN Deportes
    'https://espndeportes.espn.com/futbol/': 'https://espndeportes.espn.com/futbol/mundial/noticias',
    # Marca-ES
    'https://www.marca.com/futbol/mundial.html': None,  # already WC
    # AS-ES
    'https://as.com/futbol/': 'https://as.com/futbol/mundial/',
    # Gazzetta-Calcio
    'https://www.gazzetta.it/Calcio/': 'https://www.gazzetta.it/Calcio/Mondiali/',
    # 队报-Football
    'https://www.lequipe.fr/Football/': 'https://www.lequipe.fr/Football/Coupe-du-monde/',
    # Bleacher Report
    'https://bleacherreport.com/world-football': 'https://bleacherreport.com/fifa-world-cup-2026',
    # Flashscore
    'https://www.flashscore.com/news/world-championship/lvUBR5F8CdnS0XT8/': None,  # already WC
    # FotMob
    'https://www.fotmob.com/leagues/77/news/world-cup': None,  # already WC
    # Planet Football
    'https://www.planetfootball.com/world-cup': None,  # already WC
    # Transfermarkt
    'https://www.transfermarkt.com/weltmeisterschaft-2026/news/wettbewerb/WM26': None,  # already WC
    # Telemundo
    'https://www.telemundo.com/deportes/futbol': 'https://www.telemundo.com/deportes/futbol/copa-mundial-2026',
    # TUDN-US
    'https://www.tudn.com/futbol/copa-mundial-de-la-fifa': 'https://www.tudn.com/futbol/copa-mundial-de-la-fifa-2026',
    # Azteca
    'https://www.tvazteca.com/aztecadeportes/futbol/': 'https://www.tvazteca.com/aztecadeportes/mundial-2026/',
    # RÉCORD Mexico
    'https://www.record.com.mx/futbol-noticias/mundial-2026': None,  # already WC
    # La Afición
    'https://www.milenio.com/deportes/mundial-2026': None,  # already WC
    # Globo Esporte
    'https://globoesporte.globo.com/futebol/copa-do-mundo/': None,  # already WC
    # Marca-MX
    'https://www.marca.com/mx/futbol/mundial/': None,  # already WC
    # Olé
    'https://www.ole.com.ar/futbol-internacional/mundial/': None,  # already WC
    # AFC
    'https://www.the-afc.com/en/news.html': 'https://www.the-afc.com/en/national/fifa_world_cup/news.html',
}

def probe_url(url, timeout=8):
    """快速验证URL是否可达"""
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=timeout, allow_redirects=True)
        return r.status_code, r.url
    except:
        return 0, url

# ── 审查所有URL ──
print("审查URL是否为世界杯专属频道...")
needs_fix = []
for r in rows:
    url = r['url']
    if url in URL_FIXES:
        fix = URL_FIXES[url]
        if fix:  # None = already correct
            needs_fix.append((r, fix))
    elif not is_wc_url(url):
        # URL不含WC特征，标记审查
        needs_fix.append((r, None))  # 需要手动审查

print(f"  有明确修正映射: {sum(1 for _, fix in needs_fix if fix)} 个")
print(f"  无WC特征需审查: {sum(1 for _, fix in needs_fix if not fix)} 个")

# ── 执行修正 ──
fixed_count = 0
for r, fix_url in needs_fix:
    if fix_url:
        old_url = r['url']
        # 验证新URL
        code, final_url = probe_url(fix_url)
        if code == 200 or code == 301 or code == 302:
            r['url'] = fix_url
            r['is_list'] = False  # 需要重新拨测
            r['probe_result'] = 'URL已修正为世界杯专题页，待重新拨测'
            r['http_status'] = code
            print(f"  ✅ {r['site']:30s} {old_url[:50]} → {fix_url[:70]}")
            fixed_count += 1
        else:
            print(f"  ❌ {r['site']:30s} 修正URL不可达 HTTP{code}: {fix_url[:70]}")
    else:
        # 无修正映射，保留原URL但标记
        print(f"  ⚠️ {r['site']:30s} {r['url'][:70]} (非WC频道URL，暂无替代)")

print(f'\n已修正: {fixed_count} 个URL')

with open('/Users/d.j.f/Documents/Claude/2026世界杯/probe_results.json', 'w') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print('JSON已更新')

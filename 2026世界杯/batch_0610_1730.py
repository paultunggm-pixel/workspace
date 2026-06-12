#!/usr/bin/env python3
"""6月10日 17:30 批次：权威源增量挖掘"""
import json, requests, re, time, urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

urllib3.disable_warnings()

# ── 权威源 URL 列表 ──
NEW_URLS = [
    # === 国内权威源 ===
    ("新华社体育", "http://www.news.cn/sports/", "国内"),
    ("新华社足球", "http://www.news.cn/sports/zuqiu.htm", "国内"),
    ("央视体育-世界杯", "https://sports.cctv.com/worldcup/", "国内"),
    ("央视体育-足球", "https://sports.cctv.com/football/", "国内"),
    ("央视网体育新闻", "https://news.cctv.com/sports/", "国内"),
    ("人民日报体育", "http://sports.people.com.cn/", "国内"),
    ("中国足协官网-新闻", "https://www.thecfa.cn/news/index.html", "国内"),
    ("体坛周报-国际足球", "https://www.titan24.com/international/", "国内"),
    ("体坛周报-世界杯", "https://www.titan24.com/worldcup/", "国内"),
    ("腾讯体育-国际足球", "https://sports.qq.com/isocce/", "国内"),
    ("腾讯体育-世界杯", "https://sports.qq.com/worldcup/", "国内"),
    ("搜狐体育-国际足球", "https://sports.sohu.com/guojizuqiu/", "国内"),
    ("搜狐体育-世界杯", "https://sports.sohu.com/worldcup/", "国内"),
    ("凤凰体育-国际足球", "https://sports.ifeng.com/guojizuqiu/", "国内"),
    ("虎扑-世界杯", "https://bbs.hupu.com/worldcup", "国内"),
    ("虎扑-国际足球新闻", "https://soccer.hupu.com/news/", "国内"),
    ("澎湃新闻-运动家", "https://www.thepaper.cn/list_25424", "国内"),
    ("界面新闻-体育", "https://www.jiemian.com/lists/134.html", "国内"),
    ("中国体育报", "https://www.sport.gov.cn/n14442/", "国内"),
    ("东方体育日报", "https://www.orientaldaily.com.cn/sports/", "国内"),

    # === 国际足联/洲际足联 ===
    ("FIFA官网-世界杯新闻", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/news", "境外"),
    ("FIFA官网-世界杯首页", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026", "境外"),
    ("FIFA官网-新闻总汇", "https://inside.fifa.com/en/news", "境外"),
    ("UEFA官网-新闻", "https://www.uefa.com/news-media/news/", "境外"),
    ("CONMEBOL-新闻", "https://www.conmebol.com/news/", "境外"),
    ("CONCACAF-新闻", "https://www.concacaf.com/news/", "境外"),
    ("CAF非洲足联-新闻", "https://www.cafonline.com/news/", "境外"),
    ("AFC亚洲足联-新闻", "https://www.the-afc.com/en/news.html", "境外"),

    # === 国际通讯社 ===
    ("路透社-足球", "https://www.reuters.com/sports/soccer/", "境外"),
    ("路透社-世界杯专题", "https://www.reuters.com/topic/event/fifa-world-cup/", "境外"),
    ("美联社-世界杯", "https://apnews.com/hub/fifa-world-cup", "境外"),
    ("美联社-足球", "https://apnews.com/hub/soccer", "境外"),
    ("法新社-体育", "https://www.afp.com/en/news/131/sports", "境外"),
    ("BBC Sport-世界杯", "https://www.bbc.com/sport/football/world-cup", "境外"),
    ("BBC Sport-足球", "https://www.bbc.com/sport/football", "境外"),

    # === 美国/加拿大/墨西哥 本土 ===
    ("ESPN-世界杯", "https://www.espn.com/soccer/league/_/name/fifa.world.cup", "境外"),
    ("ESPN-足球新闻", "https://www.espn.com/soccer/", "境外"),
    ("FOX Sports-世界杯", "https://www.foxsports.com/soccer/2026-fifa-world-cup", "境外"),
    ("FOX Sports-足球", "https://www.foxsports.com/soccer", "境外"),
    ("CBS Sports-世界杯", "https://www.cbssports.com/soccer/world-cup/", "境外"),
    ("NBC Sports-足球", "https://www.nbcsports.com/soccer", "境外"),
    ("Sports Illustrated-世界杯", "https://www.si.com/soccer/world-cup", "境外"),
    ("CNN Sports-足球", "https://edition.cnn.com/sport/football", "境外"),
    ("The Athletic-世界杯", "https://www.nytimes.com/athletic/football/world-cup/", "境外"),
    ("USA Today Sports-足球", "https://www.usatoday.com/sports/soccer/", "境外"),
    ("Washington Post-足球", "https://www.washingtonpost.com/sports/soccer/", "境外"),
    ("TSN加拿大-世界杯2026", "https://www.tsn.ca/soccer/fifa-world-cup", "境外"),
    ("Sportsnet加拿大-足球", "https://www.sportsnet.ca/soccer/", "境外"),
    ("CBC Sports加拿大-足球", "https://www.cbc.ca/sports/soccer", "境外"),
    ("TUDN美国-世界杯", "https://www.tudn.com/futbol/copa-mundial-de-la-fifa", "境外"),
    ("Telemundo Deportes", "https://www.telemundo.com/deportes/futbol", "境外"),
    ("ESPN Deportes-足球", "https://espndeportes.espn.com/futbol/", "境外"),
    ("Azteca Deportes墨西哥", "https://www.tvazteca.com/aztecadeportes/futbol/", "境外"),
    ("TUDN墨西哥-世界杯2026", "https://www.tudn.mx/futbol/copa-mundial-de-la-fifa-2026", "境外"),
    ("Marca墨西哥-世界杯", "https://www.marca.com/mx/futbol/mundial/", "境外"),
    ("RÉCORD墨西哥-世界杯2026", "https://www.record.com.mx/futbol-noticias/mundial-2026", "境外"),
    ("La Afición墨西哥-世界杯", "https://www.milenio.com/deportes/mundial-2026", "境外"),

    # === 欧洲五大联赛/俱乐部 ===
    ("Premier League-新闻", "https://www.premierleague.com/news", "境外"),
    ("Bundesliga-新闻(EN)", "https://www.bundesliga.com/en/bundesliga/news", "境外"),
    ("Bundesliga-世界杯专题", "https://www.bundesliga.com/en/bundesliga/news/2026-fifa-world-cup-live-news-blog-germany-37602", "境外"),
    ("Serie A-新闻(EN)", "https://www.legaseriea.it/en/media/news", "境外"),
    ("Ligue 1-新闻(EN)", "https://www.ligue1.com/Articles", "境外"),
    ("La Liga-新闻(EN)", "https://www.laliga.com/en-GB/news", "境外"),
    ("MLS-新闻", "https://www.mlssoccer.com/news/", "境外"),
    ("MLS-世界杯2026", "https://www.mlssoccer.com/news/topic/world-cup", "境外"),

    # === 南美联赛 ===
    ("巴西足协CBF-新闻", "https://www.cbf.com.br/selecao-brasileira/noticias", "境外"),
    ("Globo Esporte巴西-世界杯", "https://globoesporte.globo.com/futebol/copa-do-mundo/", "境外"),
    ("阿根廷足协AFA-新闻", "https://www.afa.com.ar/es/pages/noticias", "境外"),
    ("Olé阿根廷-世界杯", "https://www.ole.com.ar/futbol-internacional/mundial/", "境外"),

    # === 欧洲主流体育媒体 ===
    ("队报-世界杯", "https://www.lequipe.fr/Football/Coupe-du-monde/", "境外"),
    ("队报-足球新闻", "https://www.lequipe.fr/Football/", "境外"),
    ("马卡报-世界杯(EN)", "https://www.marca.com/en/football/world-cup.html", "境外"),
    ("马卡报-世界杯(ES)", "https://www.marca.com/futbol/mundial.html", "境外"),
    ("阿斯报-世界杯(EN)", "https://en.as.com/soccer/world_cup/", "境外"),
    ("阿斯报-足球(ES)", "https://as.com/futbol/", "境外"),
    ("米兰体育报-世界杯", "https://www.gazzetta.it/Calcio/Mondiali/", "境外"),
    ("米兰体育报-足球", "https://www.gazzetta.it/Calcio/", "境外"),
    ("图片报-世界杯2026", "https://www.bild.de/sport/fussball/fifa-wm-2026-QNToDBgFYEJ5vy2KN6mE", "境外"),
    ("踢球者Kicker-世界杯", "https://www.kicker.de/fifa-wm-2026/news", "境外"),
    ("世界体育报Mundo-世界杯", "https://www.mundodeportivo.com/futbol/mundial/", "境外"),
    ("A Bola葡萄牙-世界杯2026", "https://www.abola.pt/futebol/competicao/mundial-30", "境外"),
    ("Record葡萄牙-世界杯", "https://www.record.pt/internacional/competicoes/mundial-2026", "境外"),

    # === 其他国际体育媒体 ===
    ("The Guardian-世界杯2026", "https://www.theguardian.com/football/world-cup-2026", "境外"),
    ("Sky Sports-足球新闻", "https://www.skysports.com/football/news", "境外"),
    ("Goal-世界杯新闻", "https://www.goal.com/en/fifa-world-cup/news", "境外"),
    ("Bleacher Report-足球", "https://bleacherreport.com/world-football", "境外"),
    ("OneFootball-世界杯", "https://onefootball.com/en/competition/fifa-world-cup-12", "境外"),
    ("90min-世界杯", "https://www.90min.com/fifa-world-cup", "境外"),
    ("Sporting News-世界杯", "https://www.sportingnews.com/us/soccer/news/world-cup", "境外"),
    ("Flashscore-世界杯新闻", "https://www.flashscore.com/news/world-championship/lvUBR5F8CdnS0XT8/", "境外"),
    ("FotMob-世界杯", "https://www.fotmob.com/leagues/77/news/world-cup", "境外"),
    ("SofaScore-足球新闻", "https://www.sofascore.com/news/category/football", "境外"),
    ("BBC Football-世界杯2026", "https://www.bbc.com/sport/football/world-cup/2026", "境外"),
    ("Whoscored-新闻", "https://www.whoscored.com/editorial", "境外"),
    ("Opta Analyst-世界杯", "https://theanalyst.com/competition/fifa-world-cup/articles", "境外"),
    ("Transfermarkt-世界杯2026新闻", "https://www.transfermarkt.com/weltmeisterschaft-2026/news/wettbewerb/WM26", "境外"),
    ("Inside World Football", "https://www.insideworldfootball.com/", "境外"),
    ("World Soccer Talk-世界杯", "https://worldsoccertalk.com/world-cup/", "境外"),
    ("Football Italia", "https://www.football-italia.net/", "境外"),
    ("Tribal Football-世界杯", "https://www.tribalfootball.com/world-cup", "境外"),
    ("Planet Football-世界杯", "https://www.planetfootball.com/world-cup", "境外"),
    ("Football365-世界杯", "https://www.football365.com/world-cup", "境外"),
    ("Sports Mole-世界杯", "https://www.sportsmole.co.uk/football/world-cup-2026/", "境外"),
    ("TalkSport-世界杯2026", "https://talksport.com/football/world-cup-2026/", "境外"),
    ("Daily Mail-世界杯", "https://www.dailymail.co.uk/sport/football/world-cup-2026/index.html", "境外"),
    ("Mirror-世界杯2026", "https://www.mirror.co.uk/all-about/world-cup-2026", "境外"),
    ("The Sun-世界杯2026", "https://www.thesun.co.uk/sport/football/world-cup-2026/", "境外"),
    ("Independent-世界杯", "https://www.independent.co.uk/sport/football/world-cup/", "境外"),
    ("Telegraph-世界杯2026", "https://www.telegraph.co.uk/world-cup-2026/", "境外"),
    ("Eurosport-世界杯", "https://www.eurosport.com/football/world-cup/", "境外"),
    ("beIN Sports-世界杯", "https://www.beinsports.com/en-us/football/world-cup", "境外"),
    ("DAZN-足球新闻", "https://www.dazn.com/en-US/news/soccer/", "境外"),
]

print(f"准备采集 {len(NEW_URLS)} 个权威源URL")

# ── 拨测逻辑（复用已优化的） ──
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

SPORTS_KW = [
    'football', 'soccer', 'fussball', 'calcio', 'futbol', 'fútbol',
    '足球', '体育', '运动', '赛事', '比赛', '联赛', '杯赛',
    'premier league', 'la liga', 'serie a', 'bundesliga', 'ligue 1',
    'champions league', 'mls', '英超', '西甲', '意甲', '德甲', '法甲', '欧冠',
    '中超', '世界杯', 'world cup', 'world-cup', 'worldcup',
    '国际足球', 'transfer', '转会', 'score', '比分',
    'news', '资讯', '新闻', '快讯', 'squad', 'lineup', 'match', 'fixture',
]

LIST_MARKERS = [
    '<article', 'class="article', 'class="post', 'class="news',
    'class="list', 'class="feed', 'class="timeline', 'class="latest',
    'article_list', 'news-list', 'news_list', 'articleList',
    'class="news-item', 'class="hot-news', 'class="content-list',
    'class="story', 'class="headline', 'class="card--',
    'class="entry', 'class="title', 'class="c-news',
    'bbs-list', 'post-list', 'hot-list',
    'rollnews', '<li><a href=', 'class="item',
]

URL_SPORTS_PATTERNS = [
    r'/sport[_-]?sub', r'/touch/sport', r'/news\.htm', r'/home/\d+',
    r'/rollnews', r'/sports?/football', r'/football/news', r'/soccer/news',
    r'/futbol/', r'/calcio/', r'/fussball/', r'/coupe-du-monde',
    r'/mundial/', r'/world[_-]?cup', r'/wm-?2026',
    r'/category/articles', r'/news/(category|list|archive)',
    r'/editorial', r'/preview/', r'/tag/worldcup', r'/all-about/',
    r'/sports/', r'/copa-do-mundo', r'/sports?/soccer',
]

SINGLE_MARKERS = ['article-detail', 'article_detail', 'single-article',
                  'class="article-body', 'article-full', 'article-content']

def probe_one(name, url, cat):
    res = {'site': name, 'url': url, 'category': cat, 'country': '',
           'http_status': 0, 'is_list': False, 'probe_result': '', 'redirect': '',
           'corrected_url': '', 'corrected_note': '', 'date': '6.10', '_batch': '6月10日 17:30'}

    # 境外站点标国家
    if cat == '境外':
        country_map = {
            'fifa.com': '瑞士', 'uefa.com': '瑞士', 'concacaf.com': '美国',
            'conmebol.com': '巴拉圭', 'cafonline.com': '埃及', 'the-afc.com': '马来西亚',
            'reuters.com': '英国', 'apnews.com': '美国', 'afp.com': '法国',
            'bbc.com': '英国', 'bbc.co.uk': '英国', 'espn.com': '美国',
            'foxsports.com': '美国', 'cbssports.com': '美国', 'nbcsports.com': '美国',
            'si.com': '美国', 'cnn.com': '美国', 'nytimes.com': '美国',
            'usatoday.com': '美国', 'washingtonpost.com': '美国',
            'tsn.ca': '加拿大', 'sportsnet.ca': '加拿大', 'cbc.ca': '加拿大',
            'tudn.com': '美国', 'telemundo.com': '美国',
            'tvazteca.com': '墨西哥', 'tudn.mx': '墨西哥', 'record.com.mx': '墨西哥',
            'milenio.com': '墨西哥', 'marca.com': '西班牙',
            'premierleague.com': '英国', 'bundesliga.com': '德国',
            'legaseriea.it': '意大利', 'ligue1.com': '法国', 'laliga.com': '西班牙',
            'mlssoccer.com': '美国', 'cbf.com.br': '巴西',
            'globoesporte.globo.com': '巴西', 'afa.com.ar': '阿根廷',
            'ole.com.ar': '阿根廷', 'lequipe.fr': '法国', 'as.com': '西班牙',
            'gazzetta.it': '意大利', 'bild.de': '德国', 'kicker.de': '德国',
            'mundodeportivo.com': '西班牙', 'abola.pt': '葡萄牙', 'record.pt': '葡萄牙',
            'theguardian.com': '英国', 'skysports.com': '英国',
            'goal.com': '英国', 'bleacherreport.com': '美国',
            'onefootball.com': '德国', '90min.com': '美国',
            'sportingnews.com': '美国', 'flashscore.com': '捷克',
            'fotmob.com': '挪威', 'sofascore.com': '克罗地亚',
            'whoscored.com': '英国', 'theanalyst.com': '英国',
            'transfermarkt.com': '德国', 'insideworldfootball.com': '英国',
            'worldsoccertalk.com': '美国', 'football-italia.net': '意大利',
            'tribalfootball.com': '英国', 'planetfootball.com': '英国',
            'football365.com': '英国', 'sportsmole.co.uk': '英国',
            'talksport.com': '英国', 'dailymail.co.uk': '英国',
            'mirror.co.uk': '英国', 'thesun.co.uk': '英国',
            'independent.co.uk': '英国', 'telegraph.co.uk': '英国',
            'eurosport.com': '法国', 'beinsports.com': '法国', 'dazn.com': '英国',
        }
        for domain, country in country_map.items():
            if domain in url:
                res['country'] = country
                break
        if not res['country']:
            res['country'] = '未知'

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True, verify=False)
        res['http_status'] = resp.status_code
        if resp.url != url:
            res['redirect'] = resp.url

        if resp.status_code in (403, 429):
            res['probe_result'] = f'HTTP {resp.status_code} 访问受限(可能反爬)'
            return res
        if resp.status_code != 200:
            res['probe_result'] = f'HTTP {resp.status_code}'
            return res

        cl = resp.text.lower()
        has_sports = any(kw in cl for kw in SPORTS_KW)
        list_score = sum(1 for m in LIST_MARKERS if m in cl)
        is_single = sum(1 for m in SINGLE_MARKERS if m in cl) >= 2
        url_sports = any(re.search(pat, url, re.IGNORECASE) for pat in URL_SPORTS_PATTERNS)
        title_m = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
        page_title = title_m.group(1)[:200] if title_m else ''
        title_sports = any(kw in page_title.lower() for kw in SPORTS_KW)

        if is_single and list_score < 5:
            res['probe_result'] = '疑似单篇详情页'
        elif list_score >= 3 and has_sports:
            res['is_list'] = True
            res['probe_result'] = '✅ 确认为体育/足球资讯列表页'
        elif list_score >= 5:
            res['is_list'] = True
            res['probe_result'] = '✅ 列表结构明确(含体育相关内容)'
        elif list_score >= 2 and has_sports:
            res['is_list'] = True
            res['probe_result'] = '✅ 体育资讯列表页(列表特征较少但内容相关)'
        elif url_sports and (has_sports or title_sports):
            res['is_list'] = True
            res['probe_result'] = '✅ URL识别为体育资讯列表页(JS渲染·静态HTML特征不足)'
        elif list_score >= 3:
            res['probe_result'] = f'有列表结构但无体育关键词'
        elif not has_sports and not url_sports and not title_sports:
            res['probe_result'] = '非足球/体育类内容'
        else:
            res['probe_result'] = f'列表特征不足({list_score})'

    except requests.Timeout:
        res['probe_result'] = '请求超时'
    except requests.ConnectionError:
        res['probe_result'] = '连接失败'
    except Exception as e:
        res['probe_result'] = f'异常:{str(e)[:60]}'

    return res

# ── 并发拨测 ──
print(f"\n并发拨测（10并发）...")
new_rows = []
with ThreadPoolExecutor(max_workers=10) as pool:
    futures = {pool.submit(probe_one, name, url, cat): (name, url) for name, url, cat in NEW_URLS}
    for i, f in enumerate(as_completed(futures), 1):
        r = f.result()
        new_rows.append(r)
        s = '✅' if r['is_list'] else ('❌' if r['http_status']==0 else '  ')
        print(f'  [{i:3d}/{len(NEW_URLS)}] {s} {r["site"]:30s} HTTP{r["http_status"]} | {r["probe_result"][:60]}')

valid_new = sum(1 for r in new_rows if r['is_list'])
print(f'\n新增有效: {valid_new}/{len(new_rows)}')

# ── 合并到现有数据 ──
with open('probe_results.json') as f:
    existing = json.load(f)

# 去重（按URL）
existing_urls = set(r['url'] for r in existing)
truly_new = [r for r in new_rows if r['url'] not in existing_urls]
dupes = len(new_rows) - len(truly_new)

print(f'去重: {dupes} 个重复URL, 实际新增 {len(truly_new)} 个')

# 合并：新批次放最前面
merged = truly_new + existing

with open('probe_results.json', 'w') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f'合并完成: 总计 {len(merged)} 个URL')
print(f'  新增批次: 6月10日 17:30 ({len(truly_new)} 个)')

# ── 统计 ──
domestic = [r for r in truly_new if r['category']=='国内']
intl = [r for r in truly_new if r['category']=='境外']
print(f'  国内: {len(domestic)} 个 ({sum(1 for r in domestic if r["is_list"])} 有效)')
print(f'  境外: {len(intl)} 个 ({sum(1 for r in intl if r["is_list"])} 有效)')

print('\n✅ 增量挖掘完成')

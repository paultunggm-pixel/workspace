#!/usr/bin/env python3
"""重新拨测：放宽判断——足球/体育资讯列表页即有效"""
import json, requests, re, urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()

with open('/Users/d.j.f/Documents/Claude/2026世界杯/probe_results.json') as f:
    rows = json.load(f)

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

# URL 模式兜底：URL 本身明确指向体育/足球资讯列表
URL_SPORTS_PATTERNS = [
    r'/sport[_-]?sub',      # 网易体育 m.163.com/touch/sport_sub.html
    r'/touch/sport',         # 移动体育频道
    r'/news\.htm',           # 直播吧新闻列表
    r'/home/\d+',            # 懂球帝频道首页
    r'/rollnews',            # PP体育滚动新闻
    r'/sports?/football',    # 足球频道
    r'/football/news',       # 足球新闻
    r'/soccer/news',         # 足球新闻(en)
    r'/sports?/soccer',      # 足球频道(en)
    r'/futbol/',             # 西语足球
    r'/calcio/',             # 意语足球
    r'/fussball/',           # 德语足球
    r'/coupe-du-monde',      # 法语世界杯
    r'/mundial/',            # 西语世界杯
    r'/world[_-]?cup',       # 世界杯
    r'/wm-?2026',            # 德语世界杯2026
    r'/category/articles',   # 文章分类列表
    r'/news/(category|list|archive)',  # 新闻列表
    r'/editorial',           # 编辑精选(whoscored)
    r'/preview/',            # 预览列表(sportsmole)
    r'/tag/worldcup',        # 世界杯标签
    r'/all-about/',          # Mirror专题
]

SINGLE_MARKERS = ['article-detail', 'article_detail', 'single-article',
                  'class="article-body', 'article-full', 'article-content']

def probe(idx):
    r = rows[idx]
    url = r['url']
    old = r['is_list']
    res = {'http_status': 0, 'is_list': False, 'probe_result': ''}

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True, verify=False)
        res['http_status'] = resp.status_code
        if resp.url != url:
            res['redirect'] = resp.url

        if resp.status_code in (403, 429):
            res['probe_result'] = f'HTTP {resp.status_code} 访问受限(可能反爬)'
            return idx, res, old
        if resp.status_code != 200:
            res['probe_result'] = f'HTTP {resp.status_code}'
            return idx, res, old

        cl = resp.text.lower()
        has_sports = any(kw in cl for kw in SPORTS_KW)
        list_score = sum(1 for m in LIST_MARKERS if m in cl)
        is_single = sum(1 for m in SINGLE_MARKERS if m in cl) >= 2

        # URL 兜底: URL 本身明确指向体育/足球列表页
        url_sports = any(re.search(pat, url, re.IGNORECASE) for pat in URL_SPORTS_PATTERNS)
        # 页面标题提取
        title_m = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
        page_title = title_m.group(1)[:200] if title_m else ''
        title_sports = any(kw in page_title.lower() for kw in SPORTS_KW)

        # 新逻辑
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
            # URL明确是体育列表页 + 有体育关键词或标题含体育 → JS渲染页面兜底
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

    return idx, res, old

print(f'并发拨测 {len(rows)} URL...')
with ThreadPoolExecutor(max_workers=10) as pool:
    fs = [pool.submit(probe, i) for i in range(len(rows))]
    for f in as_completed(fs):
        idx, res, old = f.result()
        r = rows[idx]
        r['http_status'] = res['http_status']
        r['is_list'] = res['is_list']
        r['probe_result'] = res['probe_result']
        if 'redirect' in res:
            r['redirect'] = res['redirect']
        changed = '🔄' if old != res['is_list'] else ('✅' if res['is_list'] else '  ')
        print(f'  [{idx+1:2d}/{len(rows)}] {changed} {r["site"]:25s} HTTP{res["http_status"]} | {res["probe_result"]}')

valid = sum(1 for r in rows if r['is_list'])
changes = sum(1 for r in rows if r.get('_old_is_list', r['is_list']) != r['is_list'])
print(f'\n有效:{valid} | 非有效:{len(rows)-valid}')

with open('/Users/d.j.f/Documents/Claude/2026世界杯/probe_results.json', 'w') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print('JSON已更新')

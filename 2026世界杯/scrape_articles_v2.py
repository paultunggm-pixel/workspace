#!/usr/bin/env python3
"""v2: BeautifulSoup解析 → 提取候选 → 逐个访问验证是否为资讯内容页"""
import json, requests, re, urllib3, time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

urllib3.disable_warnings()
H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
     'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
     'Accept-Language': 'en-US,en;q=0.9'}

with open('probe_results.json') as f:
    rows = json.load(f)

targets = [r for r in rows if r['date'] in ('6.8','6.9') and r['is_list'] and r['http_status'] == 200]
print(f'抓取目标: {len(targets)} 个列表页\n')

def extract_candidates(html, base_url):
    """用BeautifulSoup从列表页提取候选文章链接"""
    candidates = []
    seen = set()
    soup = BeautifulSoup(html, 'html.parser')

    # 找所有 article/item/card 容器中的 <a>
    containers = soup.find_all(['article', 'li'], class_=re.compile(r'article|post|news|story|item|card|entry', re.I))
    if len(containers) < 3:
        containers = soup.find_all('div', class_=re.compile(r'article|post|news|story|item|card|entry', re.I))

    # 对每个容器取第一个有意义的 <a>
    for container in containers:
        links = container.find_all('a', href=True)
        for a in links:
            href = a['href']
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            skip = ['/tag/', '/category/', '/author/', '/login', '/cdn-cgi/',
                    'facebook.com', 'twitter.com', '/search?', '/page/',
                    '#comment', '/subscribe', '/privacy', '/about/', '/contact',
                    # 商业/非资讯内容
                    '/buying-guide', '/deals', '/best-', '/review', '/vs-',
                    '/how-to', '/tips', '/tricks', '/guide/', '/top-',
                    '/-ranked', '/compared', '/cheapest', '/budget',
                    '/gift', '/shop', '/coupon', '/discount', '/price',
                    '/stream', '/watch-', '/live-stream', '/tv-schedule',
                    '/fixtures', '/results', '/table', '/standings',
                    '/squad', '/quiz', '/podcast', '/video', '/gallery']
            if any(s in href.lower() for s in skip):
                continue
            full_url = urljoin(base_url, href)
            if full_url in seen:
                continue
            # 排除与base_url相同的（回到列表页自身）
            if full_url.rstrip('/') == base_url.rstrip('/'):
                continue
            seen.add(full_url)
            title = a.get_text(strip=True)[:200]
            if len(title) >= 10:
                candidates.append({'url': full_url, 'candidate_title': title})
                break  # 每个容器只取一个链接

    # 如果容器法提取不够，fallback: 找h2/h3里的<a>
    if len(candidates) < 5:
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            a = heading.find('a', href=True)
            if a:
                full_url = urljoin(base_url, a['href'])
                if full_url not in seen:
                    seen.add(full_url)
                    title = a.get_text(strip=True)[:200]
                    if len(title) >= 10:
                        candidates.append({'url': full_url, 'candidate_title': title})

    print(f'    候选链接: {len(candidates)} 条')
    return candidates[:35]

def validate_article(url, candidate_title):
    """访问URL验证是否为真实资讯内容页 → (real_title, time, is_valid)"""
    try:
        resp = requests.get(url, headers=H, timeout=10, verify=False, allow_redirects=True)
        if resp.status_code != 200:
            return None, None, False

        soup = BeautifulSoup(resp.text, 'html.parser')
        body_text = soup.get_text()
        cl = resp.text.lower()

        # ── 判断是否为真实内容页 ──
        # 1. 找 <article> 或正文容器
        article = soup.find('article')
        if not article:
            article = soup.find(['div', 'section'], class_=re.compile(
                r'article|post-|story|content-|entry', re.I))
        if not article:
            article = soup  # fallback: 整个页面

        article_text = article.get_text() if article else ''
        text_len = len(article_text.strip())

        # 2. 排除明显的非内容页
        title_tag = soup.find('title')
        page_title = title_tag.get_text().lower() if title_tag else ''
        if any(kw in page_title for kw in ['404', 'page not found', 'search results']):
            return None, None, False

        # 只在正文区域（article body）做关键词过滤，避免侧栏/页脚干扰
        article_body = article.get_text().lower() if article else cl

        # 3. 排除商业/导购/博彩内容（仅正文）
        exclude_kw = ['buying guide', "buyer's guide", 'best deals', 'price drop',
                      'where to buy', 'discount code', 'affiliate link',
                      'buy now', 'shop now', 'add to cart']
        if any(kw in article_body for kw in exclude_kw):
            return None, None, False

        # 4. 必须是体育/足球相关内容（仅正文）
        sports_kw = ['football', 'soccer', 'world cup', 'worldcup',
                     'fifa', 'premier league', 'la liga', 'serie a',
                     'bundesliga', 'ligue', 'champions league', 'mls',
                     'uefa', 'conmebol', 'concacaf', 'transfer',
                     'goal', 'match', 'stadium', 'tournament',
                     '世界杯', '足球', '体育']
        if not any(kw in article_body for kw in sports_kw):
            return None, None, False

        # 5. 排除登录/注册/订阅页
        if '/sign-up' in url or '/login' in url or '/subscribe' in url:
            return None, None, False
        if 'sign up' in page_title or 'subscribe' in page_title:
            return None, None, False

        # 6. 内容足够长（>500字符正文）
        if text_len < 500:
            return None, None, False

        # ── 提取真实标题 ──
        real_title = ''
        og = soup.find('meta', property='og:title')
        if og and og.get('content'):
            real_title = og['content']
        else:
            h1 = soup.find('h1')
            if h1:
                real_title = h1.get_text(strip=True)
        if not real_title and title_tag:
            real_title = title_tag.get_text(strip=True)
            real_title = re.sub(r'\s*[|–—-].*$', '', real_title)
        if not real_title or len(real_title) < 10:
            real_title = candidate_title

        real_title = real_title.replace('&amp;', '&').replace('&quot;', '"').replace('&#039;', "'")
        real_title = real_title.strip()[:200]

        # ── 提取时间：modified_time > published_time（后者可能是草稿日）──
        pub_time = ''
        for meta_name in ['article:modified_time', 'article:published_time']:
            mt = soup.find('meta', property=meta_name)
            if mt and mt.get('content'):
                pub_time = mt['content'][:19]
                break
        if not pub_time:
            for t in soup.find_all('time', datetime=True):
                dt = t.get('datetime','')
                if dt and len(dt) >= 10:
                    pub_time = dt[:19]
                    break
        if not pub_time:
            for pat in [r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}', r'\d{4}-\d{2}-\d{2}',
                        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
                        r'\d{4}年\d{1,2}月\d{1,2}日\s*\d{2}:\d{2}:\d{2}', r'\d{4}年\d{1,2}月\d{1,2}日\s*\d{2}:\d{2}']:
                m = re.search(pat, resp.text)
                if m:
                    pub_time = m.group(0)[:21]
                    break

        # ── 日期校验：必须 ≥ 2026-06-01，宁缺毋滥 ──
        if not pub_time:
            return None, None, False
        date_ok = False
        for pat in [r'(\d{4})-(\d{2})-(\d{2})', r'(\d{4})年(\d{1,2})月(\d{1,2})日']:
            dm = re.search(pat, pub_time)
            if dm:
                y, m, d = int(dm.group(1)), int(dm.group(2)), int(dm.group(3))
                if y > 2026 or (y == 2026 and m >= 6):
                    date_ok = True
                break
        if not date_ok:
            return None, None, False

        return real_title, pub_time, True

    except Exception:
        return None, None, False

def process_list_page(r):
    url = r['url']
    site = r['site']
    result = {'site': site, 'source_url': url, 'articles': [], 'status': ''}

    try:
        resp = requests.get(url, headers=H, timeout=15, verify=False, allow_redirects=True)
        if resp.status_code != 200:
            result['status'] = f'HTTP{resp.status_code}'
            return result

        candidates = extract_candidates(resp.text, resp.url)
        if not candidates:
            result['status'] = '无候选链接(页面可能JS渲染)'
            return result

        # 过滤：只保留足球/WC相关URL（排除NFL/NBA等非足球运动）
        football_urls = []
        for c in candidates:
            u = c['url'].lower()
            is_other = any(kw in u for kw in ['/nfl/', '/nba/', '/mlb/', '/nhl/', '/wnba/',
                           '/cricket/', '/rugby/', '/tennis/', '/golf/',
                           '/ufc/', '/boxing/', '/nascar/', '/formula-1/',
                           'player-ratings', 'player-rankings', '/nfl-', '/nba-',
                           'sign-up', '/signup'])
            is_football = any(kw in u for kw in ['football', 'soccer', 'world-cup', 'worldcup',
                              'fifa', 'premier-league', 'la-liga', 'serie-a',
                              'bundesliga', 'ligue', 'champions-league', 'mls',
                              'uefa', 'transfer', 'league', 'cup', 'goal',
                              'match', 'stadium', 'tournament'])
            if not is_other and is_football:
                football_urls.append(c)
        if football_urls:
            candidates = football_urls

        # 逐个验证
        for c in candidates:
            real_title, pub_time, is_valid = validate_article(c['url'], c['candidate_title'])
            if is_valid:
                result['articles'].append({
                    'title': real_title,
                    'url': c['url'],
                    'time': pub_time
                })
                if len(result['articles']) >= 20:
                    break
            time.sleep(0.05)

        result['status'] = f'✅ {len(result["articles"])}篇验证通过'
        return result

    except Exception as e:
        result['status'] = f'错误: {str(e)[:60]}'
        return result

# ── 主流程 ──
results = {}
with ThreadPoolExecutor(max_workers=2) as pool:
    fs = {pool.submit(process_list_page, r): r for r in targets}
    for f in as_completed(fs):
        res = f.result()
        results[res['source_url']] = res
        print(f'  {res["site"]:30s} → {res["status"]}')

# 按日期分拆保存
url_date = {r['url']: r['date'] for r in targets}
results_68 = {k:v for k,v in results.items() if url_date.get(k)=='6.8'}
results_69 = {k:v for k,v in results.items() if url_date.get(k)=='6.9'}

total68 = sum(len(v['articles']) for v in results_68.values())
total69 = sum(len(v['articles']) for v in results_69.values())
print(f'\n6月8日: {total68}篇  |  6月9日: {total69}篇  |  总计: {total68+total69}篇')

with open('scraped_articles_68.json', 'w') as f:
    json.dump(results_68, f, ensure_ascii=False, indent=2)
with open('scraped_articles_69.json', 'w') as f:
    json.dump(results_69, f, ensure_ascii=False, indent=2)
print('保存: scraped_articles_68.json + scraped_articles_69.json')

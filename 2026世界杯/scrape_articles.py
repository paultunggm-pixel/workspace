#!/usr/bin/env python3
"""抓取6月8日批次列表页中的具体资讯内容链接"""
import json, requests, re, urllib3, time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()
H = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
     'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
     'Accept-Language': 'en-US,en;q=0.9'}

with open('probe_results.json') as f:
    rows = json.load(f)

# 6月8日批次 + 有效
targets = [r for r in rows if r['date'] == '6.8' and r['is_list'] and r['http_status'] == 200]
print(f'抓取目标: {len(targets)} 个有效列表页\n')

def extract_articles(html, base_url):
    """从HTML中提取文章链接: (url, title, time_str)"""
    articles = []
    seen = set()

    # 策略1: 找 <article> 或 news-item 等结构化元素
    blocks = re.findall(r'<(?:article|li)[^>]*>.*?</(?:article|li)>', html, re.DOTALL)
    if len(blocks) < 3:
        # 策略2: 找 <a> 标签组合
        blocks = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)

    for block in blocks:
        if isinstance(block, tuple):
            href, text = block
            block_html = text
        else:
            block_html = block
            href_m = re.search(r'href="([^"]*)"', block)
            href = href_m.group(1) if href_m else ''

        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue

        full_url = urljoin(base_url, href)
        if full_url in seen:
            continue
        seen.add(full_url)

        # 提取标题 (去除HTML标签)
        title = re.sub(r'<[^>]+>', '', block_html).strip()
        title = re.sub(r'\s+', ' ', title)[:200]

        # 提取时间
        time_str = ''
        # <time datetime="...">
        tm = re.search(r'<time[^>]*datetime="([^"]*)"', block_html)
        if tm:
            time_str = tm.group(1)[:19]
        else:
            # 常见日期格式
            for pat in [r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
                        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}',
                        r'\d{4}-\d{2}-\d{2}',
                        r'\d{2}/\d{2}/\d{4}',
                        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}']:
                dm = re.search(pat, block_html)
                if dm:
                    time_str = dm.group(0)
                    break

        # 过滤太短或无意义的
        if len(title) < 5:
            continue

        articles.append({
            'url': full_url,
            'title': title,
            'time': time_str
        })

    return articles[:30]  # 最多30条

results = {}  # source_url -> articles

def scrape_one(r):
    url = r['url']
    site = r['site']
    try:
        resp = requests.get(url, headers=H, timeout=15, verify=False, allow_redirects=True)
        if resp.status_code != 200:
            return site, url, [], f'HTTP{resp.status_code}'
        articles = extract_articles(resp.text, resp.url)
        return site, url, articles, f'{len(articles)}条'
    except Exception as e:
        return site, url, [], str(e)[:50]

with ThreadPoolExecutor(max_workers=5) as pool:
    fs = {pool.submit(scrape_one, r): r for r in targets}
    for f in as_completed(fs):
        site, url, articles, status = f.result()
        results[url] = {
            'site': site,
            'source_url': url,
            'articles': articles,
            'status': status
        }
        print(f'  {site:30s} → {status}')

total = sum(len(v['articles']) for v in results.values())
print(f'\n总计抓取: {total} 条文章')

with open('scraped_articles_68.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('已保存: scraped_articles_68.json')

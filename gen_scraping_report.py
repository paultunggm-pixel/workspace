#!/usr/bin/env python3
"""Convert World Cup data scraping plan to MHTML"""
import uuid
from datetime import datetime

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026世界杯实时数据抓取可行性方案</title>
<style>
  :root {
    --bg: #0f1117;
    --card: #1a1d27;
    --border: #2a2d3a;
    --text: #e1e4eb;
    --muted: #888b96;
    --accent: #5b7fff;
    --green: #00c853;
    --orange: #ff9100;
    --red: #ff5252;
    --purple: #b388ff;
    --cyan: #00e5ff;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg); color: var(--text); line-height:1.75;
  }
  .container { max-width:960px; margin:0 auto; padding:40px 24px 80px; }

  .hero {
    text-align:center; padding:40px 0 30px; border-bottom:1px solid var(--border); margin-bottom:40px;
  }
  .hero h1 { font-size:32px; font-weight:800; margin-bottom:10px; }
  .hero .desc { color:var(--muted); font-size:14px; line-height:1.6; }

  section { margin-bottom:48px; }
  h2 {
    font-size:22px; font-weight:700; margin-bottom:16px;
    padding-bottom:10px; border-bottom:2px solid var(--border);
  }
  h3 { font-size:16px; font-weight:600; margin:24px 0 10px; color:var(--accent); }
  h4 { font-size:14px; font-weight:600; margin:16px 0 6px; color:var(--text); }

  p { margin-bottom:12px; color:#c8ccd6; }
  strong { color:var(--text); }
  ul, ol { margin:8px 0 14px 20px; color:#c8ccd6; }
  li { margin-bottom:4px; }

  .callout {
    background:rgba(91,127,255,0.08); border-left:3px solid var(--accent);
    padding:14px 18px; border-radius:0 8px 8px 0; margin:16px 0;
    font-size:14px; color:#bcc3d1;
  }
  .callout strong { color:var(--accent); }

  .table-wrap { overflow-x:auto; margin:16px 0; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th {
    background:var(--card); color:var(--accent); font-weight:600;
    text-align:left; padding:9px 12px; border-bottom:2px solid var(--border);
    white-space:nowrap;
  }
  td { padding:9px 12px; border-bottom:1px solid var(--border); color:#c8ccd6; }
  tr:hover td { background:rgba(255,255,255,0.02); }

  .badge {
    display:inline-block; padding:2px 10px; border-radius:12px;
    font-size:11px; font-weight:600;
  }
  .badge.green { background:rgba(0,200,83,0.15); color:var(--green); }
  .badge.orange { background:rgba(255,145,0,0.15); color:var(--orange); }
  .badge.red { background:rgba(255,82,82,0.15); color:var(--red); }
  .badge.accent { background:rgba(91,127,255,0.15); color:var(--accent); }

  pre {
    background:#0d1117; border:1px solid var(--border); border-radius:8px;
    padding:14px 18px; overflow-x:auto; font-size:12px; line-height:1.5;
    color:#c9d1d9; margin:12px 0;
  }
  code { font-family:"SF Mono", "Fira Code", monospace; font-size:12px; }

  .stars { color:var(--orange); letter-spacing:1px; }

  .divider { height:1px; background:var(--border); margin:28px 0; }

  .tag-row { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0; }
  .tag {
    display:inline-block; padding:3px 12px; border-radius:14px;
    font-size:11px; font-weight:600;
  }
  .tag.green { background:rgba(0,200,83,0.12); color:var(--green); }
  .tag.orange { background:rgba(255,145,0,0.12); color:var(--orange); }
  .tag.red { background:rgba(255,82,82,0.12); color:var(--red); }

  .footer {
    margin-top:50px; padding-top:24px; border-top:1px solid var(--border);
    color:var(--muted); font-size:12px; text-align:center;
  }
</style>
</head>
<body>
<div class="container">

<div class="hero">
  <h1>2026 世界杯实时数据抓取可行性方案</h1>
  <p class="desc">为 AI 世界杯问答产品建立实时数据通道<br>覆盖赛事实况 · 社区互动 · 弹幕舆情三大维度</p>
</div>

<!-- ====== SECTION 1 ====== -->
<section>
  <h2>一、总体策略</h2>

  <div class="callout">
    <strong>一句话：国际免费 API 兜底赛事数据，中文社区爬虫补充舆情内容，500 彩票网补充赔率。</strong>
  </div>

  <div class="table-wrap">
  <table>
    <tr><th>数据层</th><th>来源</th><th>获取方式</th><th>实时性</th><th>成本</th></tr>
    <tr>
      <td>赛事数据（比分/赛程/统计）</td>
      <td>国际免费 API</td>
      <td>REST API 轮询</td>
      <td>秒级~分钟级</td>
      <td><span class="badge green">免费</span></td>
    </tr>
    <tr>
      <td>中文社区内容（帖子/评论）</td>
      <td>虎扑、懂球帝</td>
      <td>爬虫</td>
      <td>分钟级</td>
      <td><span class="badge accent">开发+维护</span></td>
    </tr>
    <tr>
      <td>实时互动/弹幕</td>
      <td>直播吧、懂球帝直播间</td>
      <td>WebSocket 抓包</td>
      <td>秒级</td>
      <td><span class="badge orange">逆向+维护</span></td>
    </tr>
    <tr>
      <td>赔率/盘口</td>
      <td>500 彩票网</td>
      <td>HTML 解析</td>
      <td>分钟级</td>
      <td><span class="badge accent">开发</span></td>
    </tr>
  </table>
  </div>
</section>

<div class="divider"></div>

<!-- ====== SECTION 2 ====== -->
<section>
  <h2>二、目标媒体 &amp; 具体频道</h2>

  <!-- 2.1 直播吧 -->
  <h3>2.1 直播吧 (zhibo8.com)</h3>

  <h4>目标频道/产品</h4>
  <ul>
    <li><strong>世界杯文字直播页</strong>（每场比赛一个独立页面）：实时比分、事件流（进球/黄牌/换人）</li>
    <li><strong>直播间评论区</strong>：用户实时讨论</li>
    <li><strong>赛程/积分榜</strong>页面</li>
  </ul>

  <h4>技术现状</h4>
  <ul>
    <li>无官方公开 API</li>
    <li>直播数据通过 <strong>SSE（Server-Sent Events）</strong> 推送到前端，接口路径形如 <code>/live/stream?id=xxxxx</code>，返回 JSON 事件流</li>
    <li>评论数据通过 <strong>WebSocket</strong> 推送，消息格式为 JSON，在浏览器 DevTools → Network → WS 可直接看到</li>
    <li>反爬：Cloudflare 防护 + IP 频率限制；请求头校验较松</li>
    <li>GitHub 上有 3+ 个直播吧爬虫项目（Python），但世界杯期间大概率会更新反爬策略</li>
  </ul>

  <h4>抓取方案</h4>
  <pre>1. Chrome DevTools 打开一场比赛的直播页
2. Network → WS/EventStream 筛选
3. 找到 SSE 接口的完整 URL 和请求头
4. Python aiohttp + 模拟请求头，接收 SSE 事件流
5. WebSocket 评论数据同理，用 websocket-client 库连接</pre>

  <p><strong>难度：</strong><span class="stars">⭐⭐⭐</span>（中等 · 需逆向 SSE/WS 连接参数）</p>

  <div class="divider"></div>

  <!-- 2.2 懂球帝 -->
  <h3>2.2 懂球帝 (dongqiudi.com / App)</h3>

  <h4>目标频道/产品</h4>
  <ul>
    <li><strong>比赛详情页</strong>（实时比分 + 事件时间线）</li>
    <li><strong>战报/快讯</strong>（赛后 30 秒内发布）</li>
    <li><strong>圈子/评论区</strong>（球迷实时讨论）</li>
    <li><strong>数据页</strong>（控球率、射门、传球等详细统计）</li>
  </ul>

  <h4>技术现状</h4>
  <ul>
    <li>无官方公开 API，但 App 端 API 结构清晰、被社区完整逆向</li>
    <li>核心 API Base：<code>https://api.dongqiudi.com</code>（App 端）</li>
    <li>已知接口路径（非官方）：
      <ul>
        <li>赛程列表：<code>/v3/archive/schedule?season_id=2026</code></li>
        <li>比赛详情：<code>/v3/data/tab/lineup?match_id=xxxx</code></li>
        <li>评论列表：<code>/v3/comment/list?content_id=xxxx&page=1</code></li>
      </ul>
    </li>
    <li>请求需要带签名参数（app_sign、timestamp），签名算法在 App 的 native 层（libsports.so）</li>
    <li>反爬：API 请求签名验证 + IP 频率限制；签名算法不定期更新</li>
    <li>GitHub 上有 4+ 个懂球帝爬虫项目，有完整的逆向教程文档</li>
  </ul>

  <h4>抓取方案</h4>
  <pre><strong>方案 A（推荐 · 短期）：轮询 Web 端接口</strong>
  - Web 端部分接口不需要签名，刷新频率较低（1-2 分钟）
  - requests + BeautifulSoup 或直接抓 JSON 接口
  - 适合赛后战报、深度内容

<strong>方案 B（长期 · 需维护）：逆向 App API</strong>
  - 反编译 APK → 提取签名算法 → Python 复现
  - Frida/Xposed Hook app_sign 生成逻辑
  - 可用 24h 持续拉取，适合实时比分和评论</pre>

  <p><strong>难度：</strong><span class="stars">⭐⭐</span>（Web 端抓取） / <span class="stars">⭐⭐⭐⭐</span>（App API 逆向 + 持续维护）</p>

  <div class="divider"></div>

  <!-- 2.3 虎扑 -->
  <h3>2.3 虎扑体育 (hupu.com)</h3>

  <h4>目标频道/产品</h4>
  <ul>
    <li><strong>世界杯专区</strong> (<code>bbs.hupu.com/worldcup</code>)：赛后热帖、战术分析、球迷投票</li>
    <li><strong>球员评分系统</strong>（赛后用户打分，含分项评分）</li>
    <li><strong>赛后亮帖/热评</strong>（高赞评论含金量高，可做 AI 内容素材）</li>
    <li><strong>比赛热线帖</strong>（赛前 → 赛中 → 赛后持续盖楼，可提取实时情绪变化）</li>
  </ul>

  <h4>技术现状</h4>
  <ul>
    <li>无官方公开 API</li>
    <li>帖子数据通过网页 HTML 渲染，结构规整，CSS 选择器稳定</li>
    <li>已知接口（非官方）：
      <ul>
        <li>帖子列表：<code>bbs.hupu.com/worldcup-{页码}</code></li>
        <li>帖子详情 + 回复：<code>bbs.hupu.com/{帖子ID}.html</code></li>
        <li>搜索接口：<code>bbs.hupu.com/search?q=世界杯</code></li>
      </ul>
    </li>
    <li>反爬：<span class="badge green">相对宽松</span>，无 Cloudflare；主要是 IP 频率限制（~30 req/min 安全）</li>
    <li>GitHub 上有 5+ 个虎扑爬虫项目（含 scrapy 方案）</li>
  </ul>

  <h4>抓取方案</h4>
  <pre><span class="cmt"># 非常简单，直接 requests + lxml/parsel 即可</span>
import requests
from parsel import Selector

<span class="cmt"># 获取专区帖子列表</span>
url = "https://bbs.hupu.com/worldcup"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0..."})
sel = Selector(resp.text)
for post in sel.css(".bbs-hot-list li, .bbs-list-ul li"):
    title = post.css(".title a::text").get()
    link = post.css(".title a::attr(href)").get()
    replies = post.css(".reply-num::text").get()</pre>

  <p><strong>难度：</strong><span class="stars">⭐</span>（最简单 · HTML 解析即可）</p>

  <div class="divider"></div>

  <!-- 2.4 新浪体育 -->
  <h3>2.4 新浪体育 (sports.sina.com.cn)</h3>

  <h4>目标频道/产品</h4>
  <ul>
    <li><strong>世界杯专题页</strong>：赛程、积分、射手榜</li>
    <li><strong>实时比分接口</strong>（JSONP 格式，前端使用）</li>
    <li><strong>体育新闻/快讯</strong></li>
  </ul>

  <h4>技术现状</h4>
  <ul>
    <li>无官方公开 API</li>
    <li>实时比分数据通过 <strong>JSONP 接口</strong>提供，浏览器 Network 可直接看到</li>
    <li>已知接口模式（非官方，路径可能变动）：<code>sports.sina.com.cn/worldcup/score/</code> 返回 JSONP</li>
    <li>反爬：<span class="badge green">基本无防护</span>；IP 频率限制宽松</li>
    <li>JSONP 接口可直接跨域请求，不需要复杂逆向</li>
  </ul>

  <h4>抓取方案</h4>
  <pre>1. 浏览器打开新浪体育世界杯直播页
2. Network → XHR 筛选
3. 找到 callback=jsonp_xxxx 的请求
4. 复制完整 URL，去掉 callback 参数拿纯 JSON
5. Python requests 直接轮询（建议间隔 10-30 秒）</pre>

  <p><strong>难度：</strong><span class="stars">⭐</span>（简单 · JSONP 接口开箱即用）</p>

  <div class="divider"></div>

  <!-- 2.5 雷速体育 -->
  <h3>2.5 雷速体育 (leisu.com / App)</h3>

  <h4>目标频道/产品</h4>
  <ul>
    <li><strong>实时比分 + 事件直播</strong>（文字直播流，比懂球帝更快）</li>
    <li><strong>比赛数据统计</strong></li>
    <li><strong>情报/爆料</strong>（赛前首发、伤病更新）</li>
  </ul>

  <h4>技术现状</h4>
  <ul>
    <li>无官方 API</li>
    <li>PC Web 端文字直播通过 WebSocket 推送（<code>wss://ws.leisu.com/...</code>）</li>
    <li>App API 有签名验证</li>
    <li>反爬：中等（WAF + 频率限制）；WebSocket 连接需携带 token</li>
    <li>GitHub 上有 2 个爬虫项目</li>
  </ul>

  <h4>抓取方案</h4>
  <pre>1. 浏览器打开一场比赛的文字直播页
2. DevTools → Network → WS
3. 观察连接 URL 和初始消息格式
4. Python websockets 库模拟连接</pre>

  <p><strong>难度：</strong><span class="stars">⭐⭐⭐</span>（中等 · 需逆向 WS 连接参数）</p>

  <div class="divider"></div>

  <!-- 2.6 腾讯体育 -->
  <h3>2.6 腾讯体育 (sports.qq.com)</h3>

  <h4>目标频道/产品</h4>
  <ul>
    <li><strong>世界杯专题</strong> (<code>sports.qq.com/worldcup/2026</code>)</li>
    <li><strong>视频直播</strong>（有版权，通常需会员）</li>
    <li><strong>文字直播/实时比分</strong></li>
  </ul>

  <h4>技术现状</h4>
  <ul>
    <li>腾讯云有官方体育数据 API，但是 <strong>B2B 商用产品</strong>，不是公开免费接口</li>
    <li>免费页面上的比分数据通过内部 JSON 接口加载，浏览器可抓</li>
    <li>反爬：<span class="badge orange">较强</span>（腾讯 WAF）；IP 频率限制严格；部分接口需要 Referer 和 Cookie</li>
  </ul>

  <p><strong>难度：</strong><span class="stars">⭐⭐⭐</span>（中等偏上 · 反爬较强 · 建议作为备选）</p>
</section>

<div class="divider"></div>

<!-- ====== SECTION 3 ====== -->
<section>
  <h2>三、开源接口 &amp; 免费 API（兜底方案）</h2>

  <p>以上中文平台均无官方公开 API。但以下<strong>国际免费 API</strong> 可以提供同等的赛事数据，且更稳定：</p>

  <div class="table-wrap">
  <table>
    <tr><th>API 名称</th><th>免费额度</th><th>需要 Key</th><th>世界杯支持</th><th>适合场景</th></tr>
    <tr>
      <td><strong>Highlightly</strong></td>
      <td>100 请求/天</td>
      <td>免费注册</td>
      <td><span class="badge green">已确认</span></td>
      <td>赛程、实时比分、统计</td>
    </tr>
    <tr>
      <td><strong>SportScore</strong></td>
      <td><span class="badge green">完全免费</span></td>
      <td><span class="badge green">不需要</span></td>
      <td><span class="badge green">已确认</span></td>
      <td>比分、射手榜、积分榜</td>
    </tr>
    <tr>
      <td><strong>BSD (BetSportData)</strong></td>
      <td><span class="badge green">无限制</span></td>
      <td><span class="badge green">不需要</span></td>
      <td><span class="badge green">已确认</span></td>
      <td>赔率、盘口、比赛统计</td>
    </tr>
    <tr>
      <td><strong>openfootball</strong></td>
      <td><span class="badge green">完全免费</span></td>
      <td><span class="badge green">不需要</span></td>
      <td>CC0 协议</td>
      <td>104 场赛程（静态）</td>
    </tr>
    <tr>
      <td><strong>football.json</strong></td>
      <td><span class="badge green">完全免费</span></td>
      <td><span class="badge green">不需要</span></td>
      <td>通过 CDN</td>
      <td>赛程（结构化 JSON）</td>
    </tr>
  </table>
  </div>

  <div class="callout">
    <strong>推荐接入优先级：SportScore（无 Key） → Highlightly（补充统计） → BSD（赔率）</strong>
  </div>
</section>

<div class="divider"></div>

<!-- ====== SECTION 4 ====== -->
<section>
  <h2>四、推荐实施路线</h2>

  <h3>第一优先级：赛事数据（开赛前必须就绪）</h3>
  <pre>数据：实时比分、赛程、进球事件、红黄牌、换人
来源：SportScore API（主力）+ 新浪体育 JSONP（备份）
方式：Python asyncio 并发轮询（10-30 秒间隔）
存储：Redis（实时数据） + PostgreSQL（历史数据）</pre>

  <h3>第二优先级：社区舆情（开赛前 1 周就绪）</h3>
  <pre>数据：虎扑热帖+高赞评论、懂球帝圈子讨论、球员赛后评分
来源：虎扑 HTML 解析（主力）+ 懂球帝 Web 端（补充）
方式：Scrapy 定时任务（赛后 5 分钟抓一波，赛中 10 分钟抓一波）
存储：PostgreSQL + Elasticsearch（全文检索）</pre>

  <h3>第三优先级：实时弹幕互动（赛中可用）</h3>
  <pre>数据：直播吧直播间评论、懂球帝比赛实时讨论
来源：直播吧 SSE 流 + 懂球帝 App WebSocket
方式：长连接接收事件流，实时写入 Redis Stream
存储：Redis Stream（实时窗口，保留 2 小时） → ClickHouse（归档）</pre>

  <h3>第四优先级：赔率数据（补充置信度）</h3>
  <pre>数据：胜平负赔率、让球盘、大小球、赔率变化趋势
来源：500 彩票网 HTML 解析（主力）+ BSD API（补充）
方式：定时轮询，5 分钟更新一次
存储：PostgreSQL（时序）</pre>
</section>

<div class="divider"></div>

<!-- ====== SECTION 5 ====== -->
<section>
  <h2>五、技术架构建议</h2>

  <pre style="line-height:1.3;font-size:11px;">
┌─────────────────────────────────────────────────────┐
│                    数据采集层                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ 国际API  │ │ Web爬虫  │ │ WS/SSE   │ │ HTML   │ │
│  │ (轮询)   │ │ (Scrapy) │ │ (长连接) │ │ (解析) │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
├───────┼────────────┼────────────┼────────────┼──────┤
│       ▼            ▼            ▼            ▼      │
│              ┌──────────────┐                        │
│              │  Redis MQ    │  消息队列 + 去重        │
│              └──────┬───────┘                        │
│                     ▼                                │
│              ┌──────────────┐                        │
│              │  数据处理层   │  清洗/格式化/打标       │
│              └──────┬───────┘                        │
├─────────────────────┼────────────────────────────────┤
│                     ▼                                │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │
│  │  Redis   │ │PostgreSQL│ │  Elasticsearch     │   │
│  │ 实时缓存 │ │ 历史存储 │ │  全文检索(社区)     │   │
│  └──────────┘ └──────────┘ └────────────────────┘   │
│                     ｜                                │
│                     ▼                                │
│              ┌──────────────┐                        │
│              │  API 网关层   │  → 统一对外提供        │
│              └──────────────┘                        │
└─────────────────────────────────────────────────────┘</pre>

  <h3>核心原则</h3>
  <ol>
    <li>爬虫进程与 AI 问答服务<strong>完全解耦</strong>（爬虫挂了不影响问答）</li>
    <li><strong>降级链条</strong>：国际 API → 新浪体育 → 本地缓存 → 兜底静态数据</li>
    <li><strong>反反爬统一模块</strong>：所有爬虫共用 IP 池、UA 轮换、请求频率控制</li>
    <li>世界杯期间风控自动升级，每个平台至少准备一个<strong>备份数据源</strong></li>
  </ol>
</section>

<div class="divider"></div>

<!-- ====== SECTION 6 ====== -->
<section>
  <h2>六、风险 &amp; 注意事项</h2>

  <div class="table-wrap">
  <table>
    <tr><th>风险</th><th>严重程度</th><th>应对</th></tr>
    <tr>
      <td><strong>世界杯期间各平台反爬升级</strong></td>
      <td><span class="badge red">高</span></td>
      <td>每个数据源准备备份；国际 API 作为最稳兜底</td>
    </tr>
    <tr>
      <td><strong>懂球帝 App 签名算法更新</strong></td>
      <td><span class="badge orange">中</span></td>
      <td>Web 端作为降级；签名逆向需要持续维护</td>
    </tr>
    <tr>
      <td><strong>部分平台 WebSocket 连接被踢</strong></td>
      <td><span class="badge orange">中</span></td>
      <td>心跳保活 + 断线自动重连 + 指数退避</td>
    </tr>
    <tr>
      <td><strong>IP 被批量封禁</strong></td>
      <td><span class="badge orange">中</span></td>
      <td>住宅代理 IP 池（kuaidaili / zhima）+ 请求频率分散</td>
    </tr>
    <tr>
      <td><strong>法律/合规风险</strong></td>
      <td><span class="badge orange">中</span></td>
      <td>只抓公开可见数据；不抓取付费内容；尊重 robots.txt</td>
    </tr>
    <tr>
      <td><strong>数据格式突然变化</strong></td>
      <td><span class="badge accent">低</span></td>
      <td>加 schema 校验层；异常告警通知</td>
    </tr>
  </table>
  </div>
</section>

<div class="divider"></div>

<!-- ====== SECTION 7 ====== -->
<section>
  <h2>七、需要提前准备</h2>

  <ol>
    <li><strong>IP 代理池</strong> — 至少 50 个可用 IP（推荐芝麻代理或快代理住宅 IP）</li>
    <li><strong>反爬基础设施</strong> — 统一的 UA 轮换池、Cookie 池、请求延迟随机化</li>
    <li><strong>监控告警</strong> — 每个平台的数据新鲜度监控 + 爬虫健康检查</li>
    <li><strong>App 逆向环境</strong> — 一台 Android 设备 + Frida/Hook 框架（用于懂球帝/雷速 App API）</li>
    <li><strong>法律评估</strong> — 法务确认各平台 ToS 和数据使用合规边界</li>
  </ol>
</section>

<div class="footer">
  <p>2026 世界杯实时数据抓取可行性方案 · 2026-05-27</p>
</div>

</div>
</body>
</html>"""

boundary = f"----=_NextPart_{uuid.uuid4().hex}"

mhtml = "\r\n".join([
    "From: <save@localhost>",
    "Subject: 2026 World Cup Data Scraping Plan",
    f"Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}",
    "MIME-Version: 1.0",
    f'Content-Type: multipart/related; boundary="{boundary}"; type="text/html"',
    "",
    f"--{boundary}",
    "Content-Type: text/html; charset=utf-8",
    "Content-Transfer-Encoding: 8bit",
    "Content-Location: report.html",
    "",
    html,
    "",
    f"--{boundary}--",
])

output = "/Users/d.j.f/Documents/Claude/2026世界杯实时数据抓取可行性方案.mhtml"
with open(output, "w", encoding="utf-8") as f:
    f.write(mhtml)

print(f"✅ MHTML 已生成: {output}")
print(f"   文件大小: {len(mhtml):,} bytes")

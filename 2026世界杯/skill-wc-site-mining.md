# 2026世界杯时效性资讯列表网页挖掘

## 触发条件

用户要求进行以下任一操作时触发本 skill：
- "挖掘世界杯资讯列表页"
- "排查世界杯站点"
- "更新站点拨测结果"
- "重新拨测站点"
- "补充世界杯资讯URL"
- "生成站点排查报告"

## 输入

- Excel 文件路径（默认：`~/Documents/Claude/2026世界杯/世界杯时效性站点列表页/世界杯时效性站点列表页.xlsx`）
- Excel 包含列：`网站`（站点名称）、`链接`（URL）、`日期`（挖掘批次日期）

## 处理流程

### 1. 分类站点

对每个 URL 进行国内/境外分类：

**国内站点识别**：域名含以下关键词
- `.cn`、`sina.com.cn`、`163.com`、`qq.com`、`sohu.com`、`zhibo8.com`、`dongqiudi.com`、`hupu.com`、`ppsport.com`、`cctv.com`、`people.com.cn`、`xinhuanet.com`、`ifeng.com`、`toutiao.com`、`lesports.com`、`leisu.com`

**境外站点**：所有其他域名，需标注所属国家（通过域名特征映射，如 `.uk`→英国、`espn.com`→美国、`lequipe.fr`→法国等）

完整国家映射表见脚本 `classify_and_probe_fast.py` 中的 `SITE_COUNTRY` 字典。

### 2. 挖掘批次分组

根据 Excel 中的 `日期` 字段分组：
- `6.9` → **6月9日上午**
- `6.8` → **6月8日**
- `已结束` / 空值 → **6月初**

未来新增批次按 "月+日+时段" 格式命名（如 `6月10日下午`、`6月11日晚`）。

### 3. 拨测URL（核心逻辑）

**并发拨测**：使用 `ThreadPoolExecutor`（10并发），每URL超时10秒。

**判断是否为有效体育资讯列表页**（三级判断）：

**Level 1 — HTML 列表结构检测**：
```
列表特征标记（每个标记+1分，list_score≥3 + 体育关键词 = 有效）：
<article, class="article/post/news/list/feed/timeline/latest,
article_list, news-list, news_list, articleList,
class="news-item/hot-news/content-list/story/headline/card--/entry/title/c-news,
bbs-list, post-list, hot-list, rollnews, <li><a href=, class="item
```

**Level 2 — 体育/足球关键词**（不强制"世界杯"，因为赛前体育列表页不一定有WC内容）：
```
football, soccer, fussball, calcio, futbol, fútbol,
足球, 体育, 运动, 赛事, 比赛, 联赛, 杯赛,
premier league, la liga, serie a, bundesliga, ligue 1,
champions league, mls, 英超, 西甲, 意甲, 德甲, 法甲, 欧冠,
中超, 世界杯, world cup, world-cup, worldcup,
国际足球, transfer, 转会, score, 比分,
news, 资讯, 新闻, 快讯, squad, lineup, match, fixture
```

**Level 3 — URL 模式兜底**（JS渲染的移动页面，静态HTML中列表特征少）：
```
URL匹配以下模式 + 页面含体育关键词或标题含体育 = 有效：
/sport[_-]?sub, /touch/sport, /news\.htm, /home/\d+,
/rollnews, /sports?/football, /football/news, /soccer/news,
/futbol/, /calcio/, /fussball/, /coupe-du-monde,
/mundial/, /world[_-]?cup, /wm-?2026,
/category/articles, /news/(category|list|archive),
/editorial, /preview/, /tag/worldcup, /all-about/
```

**排除条件**：
- 单篇详情页特征 ≥2（`article-detail, article_detail, single-article, article-body, article-full, article-content`）
- HTTP 403/429 → 访问受限
- HTTP 0 → 超时或连接失败

**自动补充 URL**：对非有效页面，尝试在相同域名下查找正确的 WC 列表路径（`/football/world-cup`, `/soccer/world-cup` 等）。

### 4. 生成 HTML 报告

**页面规格**：
- 白底（`background: #f5f6f8`）
- 标题：「2026「美加墨世界杯」时效性资讯列表网页挖掘」
- 顶部双Tab：国内站点 / 境外站点
- 左右分栏：左侧批次导航（200px），右侧内容区

**批次导航**：
- 侧栏显示挖掘批次链接，最新批次最上
- 仅显示有内容的批次
- 点击切换对应批次面板

**统计摘要**（每个批次面板内）：
- 顺序：**总计 → 有效 → 非有效 → 已补充 → 不可达**

**站点列表**：
- 排序：有效（✅）排最前，不可达（🔴）和非有效（⚠️）排后
- 列序：#、站点、URL、国家（境外Tab）、拨测结果、补充URL、HTTP
- HTTP 列在最后一列

**复制按钮**（表头 URL 列内）：
- **复制URL**：批量复制当前表所有行的 URL 列数据（换行分隔）
- **复制全表**：批量复制当前表全部行列数据（TSV格式，可粘贴到Excel）
- 点击后按钮短暂显示「✓ 已复制」反馈

**强制刷新机制**（复用自一致性评测项目）：
- `<meta>` no-cache 标签
- `version.json` 版本检测：加载时异步请求 `version.json`，比对 `BUILD_TIME`
- `sessionStorage` 锁：同会话只检测一次，避免无限重载
- 每次部署自动 bump `version.json`

### 5. 部署

**GitHub Pages**（主渠道）：
- Repo: `paultunggm-pixel/consistency-eval`
- 本地 clone: `~/Documents/Claude/consistency-eval-gh/`
- 文件名: `worldcup-site-audit.html`
- 每次部署步骤：
  1. 生成 HTML → `~/Documents/Claude/2026世界杯/世界杯时效性站点排查报告.html`
  2. 复制到 git repo
  3. Bump `version.json` 的 `build_time`（`date +%Y%m%d%H%M%S`）
  4. Git commit + push

**阿里云 OSS**（备用）：
- Bucket: `consistency-eval`（`oss-cn-hangzhou`）
- 若账户异常（`UserDisable`），仅部署 GitHub Pages

## 脚本文件

| 文件 | 用途 |
|------|------|
| `classify_and_probe_fast.py` | 初始分类+并发拨测 |
| `reprobe_fix.py` | 重新拨测（保留已有数据，仅更新 probe 结果） |
| `build_report_v4.py` | 从 `probe_results.json` 生成 HTML 报告 |
| `probe_results.json` | 中间数据（所有站点分类+拨测结果） |

## 输出文件

| 文件 | 说明 |
|------|------|
| `世界杯时效性站点分类排查结果.xlsx` | Excel 结果（国内/境外/总览 3个Sheet） |
| `世界杯时效性站点排查报告.html` | HTML 可视化报告 |
| `probe_results.json` | 中间 JSON 数据（可被后续脚本复用） |

## 日常使用流程

**新增一批站点URL**：
1. 将新URL追加到源 Excel 中（填入日期如 `6.10`）
2. 运行 `reprobe_fix.py` 重新拨测
3. 运行 `build_report_v4.py` 生成新 HTML
4. 部署到 GitHub Pages（复制HTML + bump version.json + push）

**仅更新HTML布局/样式**：
1. 修改 `build_report_v4.py`
2. 运行 + 部署

## 注意事项

- 所有文件路径必须在 `~/Documents/Claude/` 范围内
- 拨测结果可能受公司网络（云壳）影响，超时/连接失败的站点需在公司网络外验证
- 世界杯截止日前（6月2日），部分球队名单数据不完整是正常现象
- 体育资讯列表页在世界杯开赛前可能暂时没有世界杯专题内容，不能据此判定为无效
- GitHub Pages 有 10 分钟缓存（`cache-control: max-age=600`），更新后需等待或使用带 `?v=` 参数的URL绕过

---
name: model-answer-consistency-eval
description: 多模型解题答案一致性评测——以千问为基准，与豆包/豆包深思/元宝/DeepSeek/Gemini3.1 进行答案一致性比对，输出 HTML 可视化报告+Excel 明细，并上传钉钉文档
triggers:
  - 运行答案一致性评测
  - 生成评测报告
  - 对新日期数据做增量评测
  - 一致性评测
  - 模型答案比对
  - 一致率评测
  - 解题答案评测
---

# 多模型解题【答案一致性】评测

## 概述

以千问(`app_qianwen_text`)为基准模型，分别与豆包、豆包深思、元宝、DeepSeek、Gemini3.1 进行解题答案一致性比对。输出包括：原始数据 Excel、评测明细 Excel、带趋势图的 HTML 可视化报告。

**工作目录**: `~/Documents/Claude/解题答案一致性评测/`
**核心脚本**: `analyze_v3.py`（~2042 行），位于工作目录根部。
**发布**: GitHub Pages (`https://paultunggm-pixel.github.io/consistency-eval/`) + Excel 附件钉钉「解题一致性评测附件excel」

## 进化日志

每次对提取/比对算法的实质性改进，必须在此记录：

| 版本 | 日期 | 改进内容 | 效果 |
|------|------|----------|------|
| v1.10.0 | 2026-06-10 | 防缓存过期：HTML 加 `<meta>` no-cache 头 + 页面显示构建时间戳 + `version.json` 自动版本检测 + `sessionStorage` 锁防死循环；`extract_final_answer_line` 修复「解答」优先提取全文而非文末「答案」 | 任何人打开页面3秒内自动最新版 |
| v1.8.1 | 2026-06-03 | 详情弹窗截图与解题doc改为左右并排布局（截图固定280px左列、doc右列自适应、窄屏自动堆叠）；异动分析面板改为紧凑双列网格布局（inline badge指标 + 左右分栏诊断/建议，垂直空间减少约40%） | 详情弹窗和异动面板布局大幅优化 |
| v1.8.0 | 2026-06-03 | 详情弹窗新增模型解题截图展示（千问/豆包/豆包深思/元宝的 image_url 字段，Gemini 无独立截图）；截图 max-height 800px；disagreements 数据新增 qw_image_url/comp_image_url 字段 | 可直观对比原始截图 |
| v1.7.0 | 2026-06-03 | HTML 报告新增一致率异动分析面板：概览卡片下方自动显示异动指标、模型空文本率诊断、提取失败诊断、排查建议；history.json 增加 `model_stats` 字段 | 报告可读性大幅提升 |
| v1.6.0 | 2026-06-03 | 修复 v1.5 被 `\b([A-E])\b` 短路的问题：调整执行顺序（labeled中文标签优先于\b）；新增子集匹配（choice⊆fill_in字母时判一致）；此策略不修改 extract_choice（避免类型变化导致回归） | 全线+0.4~2.0pp（6.01豆包+2pp、Gemini+2pp），零回归 |
| v1.5.0 | 2026-06-03 | (被 v1.6 修复) `answers_match()` 中 choice vs fill_in 跨类型匹配新增中文标签字母提取 | 未生效（被\b短路） |
| v1.4.0 | 2026-06-02 | (未上线) 尝试 extract_choice 新增中文标签模式+分号分隔符，导致退步已回退 | — |
| v1.3.0 | 2026-06-02 | **重大发现**: 大量"分歧"系数据质量问题——同一query图片URL被API分发给不同模型时返回了不同题目；新增 `is_different_question()` 函数用于检测（已集成到 analyze_v3.py，但暂不主动过滤，作为数据分析参考） | 识别了评测瓶颈的根因 |
| v1.2.0 | 2026-06-02 | `strip_latex_formatting` 新增 `\dfrac`/`\tfrac`/`\cfrac` 及其裸命令变体的处理；JS `wrapNakedLatex` 同步更新 `braceCmds` | 千问-元宝 +0.4~1.2pp |
| v1.1.0 | 2026-06-02 | Claude Code 接管评测体系，迁移钉钉目录至「ClaudeCode版 - 自购token」 | — |
| v1.0.0 | 2026-05-25 | 初始版本（前 agent 工具创建） | — |

### 已知数据质量问题

1. **同URL不同题**: 同一query图片URL，不同模型收到的题目内容不同（API分发问题）。表现：千问和竞赛模型的解题内容属于完全不同的学科/题目
2. **模型文本空率**: 某些日期某些模型的 API 返回文本为空的比例差异大（5.31 元宝空率显著偏高）
3. **DeepSeek 字段未打通**: `ds` 字段内容为日期字符串而非模型输出
4. **豆包输出格式多变**: 6.01 数据中豆包大量使用嵌入式答案格式（"高速马达：A、B、C"、编号列表 `1.B 2.A`），导致 extract_choice 失败退化为 fill_in，产生跨类型假分歧。v1.6 的跨类型匹配增强已部分缓解

**持续进化指令**: 每次执行评测后应主动分析分歧数据，识别假分歧模式，优化提取/比对算法，全量重跑验证，更新钉钉文件，并在此记录。

## 快速执行（CRITICAL）

执行评测时，**必须严格按以下步骤顺序**，不可跳过或自行发挥：

### Step 1: 确定评测日期

- 默认当天日期（格式 `YYYY-MM-DD`），或用户指定日期
- 若用户说"跑一下今天的"即用当天日期

### Step 2: 下载数据

```bash
cd ~/Documents/Claude/解题答案一致性评测/
curl -s "https://quark-study-test.alibaba-inc.com/get_app_Choose_result?find_time={日期}" -o raw_data.json
```

- **必须带 find_time 参数**：不带此参数 API 返回的"最新一天"数据可能不完整（记录数偏少+某模型空率畸高）
- 日期值取记录的 `ds` 字段
- 必须用 `curl -s` 下载（WebFetch 会截断大 JSON）

### Step 3: 运行分析脚本

```bash
cd ~/Documents/Claude/解题答案一致性评测/
python3 analyze_v3.py
```

脚本自动完成：Excel 生成 → 答案提取 → 比对 → 历史追加 → HTML 生成

### Step 4: 验证 HTML 中 JS 语法

```bash
# Node.js v26 不支持 .html 扩展名直接 check，须先提取 script 块
python3 -c "
import re
with open('outputs/evaluation_report.html', 'r') as f:
    html = f.read()
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
with open('/tmp/_eval_check.js', 'w') as f:
    f.write('\n'.join(scripts))
" && node --check /tmp/_eval_check.js
```

### Step 5: 生成无法判断明细 Excel

`analyze_v3.py` **不生成**无法判断明细 Excel，需用独立脚本从 `outputs/history.json` 的 `uncomparables` 字段提取生成。

在 `~/Documents/Claude/解题答案一致性评测/` 下创建 `gen_uncomparable_excel.py`，内容如下：

```python
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs', 'history.json')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')

with open(HISTORY_FILE, 'r') as f:
    history = json.load(f)

thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)
header_font = Font(bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

for entry in history:
    date = entry['date']
    uncomps = entry.get('uncomparables', {})
    
    wb = Workbook()
    ws = wb.active
    ws.title = '无法判断明细'
    
    headers = ['序号', '对比模型对', '原因', 'query', '学段', '学科', '千问答案', '对方答案']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border
    
    row = 2
    for pair_name, items in uncomps.items():
        for item in items:
            vals = [
                item.get('idx', ''),
                pair_name,
                item.get('reason', ''),
                item.get('query', ''),
                item.get('grade', ''),
                item.get('course', ''),
                (item.get('qw_answer', '') or '(无内容)')[:200],
                (item.get('comp_answer', '') or '(无内容)')[:200],
            ]
            for col, v in enumerate(vals, 1):
                cell = ws.cell(row=row, column=col, value=v)
                cell.border = thin_border
            row += 1
    
    # 列宽
    widths = [6, 14, 22, 50, 8, 10, 40, 40]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64+i)].width = w
    ws.freeze_panes = 'A2'
    
    out_path = os.path.join(OUTPUT_DIR, f'无法判断明细-{date}.xlsx')
    wb.save(out_path)
    print(f'已生成: {out_path}')
```

然后运行：
```bash
cd ~/Documents/Claude/解题答案一致性评测/
python3 gen_uncomparable_excel.py
```

### Step 6: 上传 Excel 到钉钉（MANDATORY）

**Excel 上传到钉钉目录「解题一致性评测附件excel」**，HTML 报告不再上传到钉钉（仅发布到 GitHub Pages）。

钉钉 MCP 网关 URL: `https://mcp-gw.dingtalk.com/server/b118049698978765178a66f3088450db5f55827f17eb3f44000a1b21e262b002?key=44b1dc761150599c39d83e79814a9804`

**钉钉目录**: 「解题一致性评测附件excel」

| 目录 | folderId |
|------|----------|
| 主目录 | `r1R7q3QmWew5lo02fZNnXl01JxkXOEP2` |
| 评测明细 | `20eMKjyp810mMdK4H4y1kkgQJxAZB1Gv` |
| 原始数据 | `R1zknDm0WR6XzZ4LtxwPRNeEWBQEx5rG` |
| 无法判断 | `o14dA3GK8gQlkoYwcKwe9Pb7V9ekBD76` |

上传方式：三步流程（`get_file_upload_info` → `curl PUT` → `commit_uploaded_file(folderId=子目录ID)`），按日期命名追加。上传后使用 `get_document_info` 验证 `folderId`。不可依赖 `list_nodes`（bug）。

### Step 7: 同步 GitHub Pages + OSS（MANDATORY）

HTML 报告**仅**发布到 GitHub Pages。`data.json` 需同步上传 OSS 以保证国内访问速度。

```bash
cd ~/Documents/Claude/解题答案一致性评测/

# 1. 注入按钮生成 GitHub Pages 版本
python3 -c "
with open('outputs/evaluation_report.html', 'r') as f:
    html = f.read()
old = '评测方法说明</a>\n</div>'
new = '评测方法说明</a>\n<a href=\"https://alidocs.dingtalk.com/i/nodes/r1R7q3QmWew5lo02fZNnXl01JxkXOEP2?utm_scene=person_space\" target=\"_blank\" class=\"download-btn\" style=\"color:#ffffff;background:#059669;border-color:#059669;\">下载评测明细记录</a>\n</div>'
html = html.replace(old, new, 1)
with open('outputs/evaluation_report_github.html', 'w') as f:
    f.write(html)
"

# 2. 推送到 GitHub Pages
cd ~/Documents/Claude/consistency-eval-gh
cp ~/Documents/Claude/解题答案一致性评测/outputs/evaluation_report_github.html index.html

# 3. 提取 data.json 并上传 OSS（国内加速）
python3 -c "
import json, re
with open('index.html', 'r') as f:
    html = f.read()
# 提取 historyData 内联变量为独立 JSON 文件
match = re.search(r'const historyData = (\[.+?\]);', html, re.DOTALL)
if match:
    with open('data.json', 'w') as out:
        json.dump(json.loads(match.group(1)), out, ensure_ascii=False)
    print('data.json extracted')
"

# 4. 生成 version.json（自动版本检测用，32字节）
python3 -c "
import json, datetime
with open('version.json', 'w') as f:
    json.dump({'build_time': datetime.datetime.now().strftime('%Y%m%d%H%M%S')}, f)
"

# 5. 上传 data.json 到阿里云 OSS（国内加速）
python3 -c "
import os, oss2
auth = oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'], os.environ['OSS_ACCESS_KEY_SECRET'])
bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'consistency-eval')
with open('data.json', 'rb') as f:
    bucket.put_object('data.json', f, headers={
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'public, max-age=86400'
    })
print('data.json uploaded to OSS')
"

# 6. 提交并推送
git add index.html data.json version.json
git commit -m "更新评测报告至 {日期}"
git push origin main
```

**仓库**: `paultunggm-pixel/consistency-eval`（本地目录 `~/Documents/Claude/consistency-eval-gh/`）
**URL**: `https://paultunggm-pixel.github.io/consistency-eval/`
**OSS data.json**: `https://consistency-eval.oss-cn-hangzhou.aliyuncs.com/data.json`
**下载按钮**: 固定跳转 `https://alidocs.dingtalk.com/i/nodes/r1R7q3QmWew5lo02fZNnXl01JxkXOEP2?utm_scene=person_space`

**防缓存机制** (v1.10): HTML 内 `<meta>` no-cache + 构建时间戳显示 + `version.json`(32字节)。JS 加载时请求 `version.json?t=随机数` 绕过 CDN，比较远程 build_time，若更新则 `location.reload()`。`sessionStorage` 锁每会话最多刷新一次防死循环。任何人打开页面 3 秒内自动最新版。

### Step 9: 确认输出

## 数据源

- API: `https://quark-study-test.alibaba-inc.com/get_app_Choose_result?find_time={日期}`
- 参数 `find_time` 格式: `2026-05-25`
- JSON 结构: 列表，每条含 query, grade, course, app_qianwen_text, app_doubao_speed_text, app_doubao_deepthink_text, app_yuanbao_text, ds, gemini-3.1-flash-image-preview 等字段
- query 字段为图片 URL（题目截图）

## 字段映射

```python
FIELD_MAP = [
    ('query', 'query'), ('grade', 'grade'), ('course', 'course'),
    ('app_qianwen_text', '千问'), ('app_doubao_speed_text', '豆包'),
    ('app_doubao_deepthink_text', '豆包深思'), ('app_yuanbao_text', '元宝'),
    ('ds', 'DeepSeek'), ('gemini-3.1-flash-image-preview', 'Gemini3.1'),
]
COMPARISON_PAIRS = [
    ('app_doubao_speed_text', '千问-豆包'),
    ('app_doubao_deepthink_text', '千问-豆包深思'),
    ('app_yuanbao_text', '千问-元宝'),
    ('ds', '千问-DeepSeek'),
    ('gemini-3.1-flash-image-preview', '千问-Gemini3.1'),
]
```

## 输出文件

1. `outputs/原始数据-{日期}.xlsx` — 原始数据表（query + grade + course + 各模型解题文本）
2. `outputs/评测明细-{日期}.xlsx` — 评测明细表（每 query×每对比模型一行，含解题 doc、答案抽取、比对结果）
3. `outputs/无法判断明细-{日期}.xlsx` — 无法比对记录明细
4. `outputs/evaluation_report.html` — 可视化报告（自包含所有数据+JS+CSS）
5. `outputs/history.json` — 历史评测数据（同日期覆盖，跨日期追加）

## HTML 报告结构（概要）

- **视觉主题**: 淡紫+白底 light 主题。侧栏浅紫渐变(#ede9fe→#e0d9fc)+深紫文字
- **模块一**: 总体一致率概览（数值颜色=趋势图颜色）+ 每组"N / M 题一致"+ 灰色小字"无法判断 X 题" + 警示红灯（与前3次均值 diff≥10%时闪烁）
- **v1.7 异动分析面板**: 概览卡片下方⚠️黄色提示框，当有异动时自动显示：异动指标列表、模型空文本率诊断、答案提取失败诊断、排查建议。触发条件：历史≥4次且任一对比对偏离均值≥10pp
- **模块二**: 答案一致率趋势曲线（Chart.js 4.4.1 折线图，5 色对应 5 个对比对）
- **模块三**: 按学段统计一致率表格
- **模块四**: 按学科统计一致率表格（max-height:320px + overflow-y:auto）
- **模块五**: 答案不一致数据明细（Tab 切换各对比对，详情弹窗含 query 图片+完整解题 doc+答案对比）
- **响应式**: 768px 断点切换 PC/移动端布局。`.page-wrap` 物理包裹层防钉钉 WebView 横滑
- **评测方法说明弹窗**: 通过右上角紫色按钮触发

### 关键渲染函数分工

- `renderDocContent()`: 渲染完整解题过程 doc（详情弹窗内）。前置 strip markdown → wrapNakedLatex → 整体 KaTeX 渲染
- `renderAnswerContent()`: 渲染答案标签（明细表答案抽取列）。按 `，`（全角逗号）分段，逐段判断是否为公式再渲染。不能用 renderDocContent——后者会把含中文混合行整行 `$$` 包裹导致中文渲染失败

### 静态资源加载策略（2026-06-08 全面优化）

**所有 JS/CSS 已本地化**，不再依赖任何外部 CDN（bootcdn/cloudflare 等）：

- `js/vendor/chart.umd.min.js` — Chart.js 4.4.1 (200KB)，`defer` 加载
- `js/vendor/katex.min.css` — KaTeX 样式 (23KB)
- `js/vendor/katex.min.js` — KaTeX 0.16.9 (271KB)，`defer` 加载
- `js/vendor/auto-render.min.js` — KaTeX 自动渲染 (3.4KB)，`defer` 加载
- `cover-tool/js/vendor/cover-bundle.js` — SheetJS + JSZip 合并 (1MB)，`defer` 加载

**关键优化原则**（历经 4 轮迭代沉淀）：

| # | 坑 | 解决方案 |
|---|-----|---------|
| 1 | `<script>` 在 `<head>` 中同步加载会完全阻塞渲染 | 所有 `<script>` 移到 `<body>` 末尾或加 `defer` |
| 2 | 多个独立 vendor 文件可能被 GitHub Pages CDN 限制并发导致 pending | 已改回独立文件（之前合并 bundle 导致 Chart 未定义） |
| 3 | `defer` 脚本执行晚于 `fetch().then()` 回调，导致 `typeof Chart === 'undefined'` | `initAll()` 前轮询检查：`setTimeout(tryInit, 100)` 直到 Chart/katex 就绪 |
| 4 | `currentDateIdx = historyData.length - 1` 在异步加载时计算为 -1 | 移入 `initAll()` 中数据就绪后重新计算 |
| 5 | GitHub Pages gzip Content-Length 与实际解压后大小偏差导致进度条超 100% | 使用已知文件大小 `KNOWN_SIZE = 7122203`，`Math.min(pct, 100)` |
| 6 | GitHub Pages 国内访问极慢（跨境 CDN） | `data.json` 同步上传 OSS（`consistency-eval.oss-cn-hangzhou.aliyuncs.com`），优先从 OSS 加载，失败回退 GitHub Pages |
| 7 | OSS 跨域 fetch 需要 CORS 头 | OSS Bucket CORS 配置：`allowed_origins=['*']`, `allowed_methods=['GET','HEAD']` |

### 数据加载架构

```
页面打开 → 57KB HTML 秒渲染 → loading 紫色渐变+转圈+实时进度条
         → fetch('https://consistency-eval.oss-cn-hangzhou.aliyuncs.com/data.json')
         → 实时进度 "正在下载 3.5 / 7.1 MB (50%)"
         → 解析 JSON → 轮询等待 Chart/katex 就绪 → initAll() → 淡出 loading
         → (OSS 失败时自动回退 GitHub Pages data.json)
```

## 答案提取流水线（核心逻辑摘要）

`extract_answer()` 返回 3 元组 `(normalized, type, display)`：
- `normalized`: strip_latex 后用于比对的归一化文本
- `type`: choice/judgment/fill_in/numerical/complex
- `display`: 保留原始 LaTeX 用于报告渲染

按优先级依次尝试：
1. **预处理**: strip_markdown → strip_latex_formatting（含嵌套花括号平衡匹配、裸 frac/sqrt 转换、裸命令符号化）
2. **选择题**: 13+种正则模式匹配 A-E 选项，输出排序后选项集合。"正确答案[是为]?" marker 用 last-match 策略
3. **判断题**: 匹配正确/错误/√/×，归一化为"正确"或"错误"
4. **填空题**: 识别标记词"最终答案/答案/结论/总结/**解答**"后多行扫描(max 8 行)，允许跳过 1 个空行
5. **数值题**: 从文末提取带单位的数值
6. **复杂题**: 以上均失败则标记为 complex，不参与比对

## 答案比对逻辑

`answers_match(ans1, ans2, type1, type2)` — 参数顺序：两答案在前，两类型在后。

- choice vs choice: 选项集合相等
- judgment vs judgment: 归一化后直接比较
- numerical vs numerical: 浮点 epsilon<0.01
- fill_in vs fill_in: 10 层递进匹配（见 analyze_v3.py `answers_match()` 函数）
- 跨类型比较均有对应分支（numerical vs fill_in, choice vs judgment, choice vs fill_in, fill_in vs judgment）

### choice vs fill_in 跨类型匹配策略（v1.6 优化后）

当一方提取为选择题、另一方为填空题时，按以下优先级尝试匹配：

1. **中文标签提取**（优先）：从 fill_in 文本中提取中文标签后的字母（`高速马达：A、B、C`），与 choice 集合比较
   - 严格相等 → 一致
   - choice ⊂ 标签字母 且 标签字母更多（多部分答案场景）→ 一致（子集匹配）
2. **孤立字母提取**（`\b([A-E])\b`）：与 choice 集合比较（含子集匹配）
3. **"答案选X"模式**：匹配"答案选C"/"选C"等显式选择标记

**重要原则**: 跨类型匹配的改进只修改 `answers_match()`，不修改 `extract_choice()`，避免答案类型从 fill_in 变为 choice 后破坏 fill_in vs fill_in 的 10 层递进匹配（曾导致退步 v1.4）。

## 比对前过滤

`is_cannot_answer(text)` 检测前 400 字中"无法作答"模式（关键信息缺失、图片不清/不完整/缺失、无法识别等）。若任一方明确表示无法作答，该记录不计入可比对分母。

## 增量评测

1. 修改 API 的 find_time 参数拉取新日期数据
2. 重新运行脚本 → history.json 自动追加新条目（同日期覆盖）
3. HTML 报告自动包含所有历史数据，趋势图自动更新
4. 当历史≥4 次时，警示红灯功能自动激活

## 算法变更后全量更新（MANDATORY）

**触发条件**: `extract_answer()`、`answers_match()`、`is_cannot_answer()`、`normalize_for_comparison()` 等比对/提取/过滤逻辑的任何修改。

**硬性规则**: 每次优化比对算法后，必须自动完成以下全量更新，无需用户提醒：

1. 取 history.json 中最近 5 个日期（或全部日期，取少者），逐日期用新算法重跑 analyze_v3.py
2. 为这些日期重新生成所有关联 Excel（评测明细 + 无法判断明细）
3. 重新生成 HTML 报告（包含所有历史数据）
4. 将上述全部文件上传钉钉（先删旧再传新）
5. 上传完成后向用户确认：列出每个日期的新一致率 + 已上传文件清单

**不得省略任何步骤，不得仅更新部分日期或部分文件类型。**

全量重跑脚本：
```bash
cd ~/Documents/Claude/解题答案一致性评测/
rm -f outputs/history.json

for date in 2026-05-25 2026-05-26 ...; do
    curl -s "https://quark-study-test.alibaba-inc.com/get_app_Choose_result?find_time=${date}" -o raw_data.json
    python3 analyze_v3.py
done
```

## 钉钉文档关键规则

### URL 稳定性（CRITICAL）

对外分享使用**文件夹 URL**（非文件 URL），因为文件删旧传新会生成新 nodeId 导致旧 URL 失效：

| 内容 | 固定分享 URL |
|------|-------------|
| 报告主页 | `https://paultunggm-pixel.github.io/consistency-eval/` |
| Excel 附件（钉钉） | `https://alidocs.dingtalk.com/i/nodes/r1R7q3QmWew5lo02fZNnXl01JxkXOEP2` |

> HTML 报告仅发布 GitHub Pages（含「下载评测明细记录」按钮跳转钉钉文件夹）。
> Excel 附件按日期命名上传钉钉「解题一致性评测附件excel」目录，分三个子目录（评测明细/原始数据/无法判断）。

### 权限规则
- 删除+重传生成新 nodeId，旧文件分享权限不自动继承
- `add_permission` 仅支持 USER 类型授权
- CONVERSATION（群组）权限须设在父文件夹级别自动继承

### API 参数坑
- `commit_uploaded_file` 必须显式传 `folderId`，否则文件落入默认根目录
- `create_folder` 参数名是 `folderId`（不是 `parentId`）

## 一致率骤降诊断优先级

当某日某对比对一致率突然大幅下降时：
1. **先对比各日期各模型原始文本空率**（json 字段为空的占比）——某模型空率骤增 = 数据源问题
2. **再看题目学段分布变化**（某天突然集中在某个难学段/学科）
3. **最后才查提取/比对算法**

## 诊断与人工抽查

### 分歧题人工抽查法
1. 先按 query 图片 URL 去重
2. 逐题用 Read 工具查看题图，人工判断正确答案
3. 用其余 3 个模型（豆包深思/元宝/Gemini）做多数投票预判谁对谁错
4. 类型不匹配的分歧中，"豆包没用选项字母作答"这类无法靠正则挽救，记录为已知局限

## Pitfalls（关键踩坑清单）

执行过程中必须注意以下所有坑点：

### 数据与API
- 必须用 curl 下载数据，WebFetch 会截断 1.9MB 的 JSON
- ds 字段实际是日期"2026-05-25"而非 DeepSeek 模型文本，DS 抓取暂未打通
- **必须带 find_time 参数**：不带此参数 API 返回数据不完整（记录少+某模型空率畸高）

### LaTeX & 答案提取
- LaTeX 格式包裹的数字（如 `\boldsymbol{3}`）与普通数字(3)必须视为相同
- **嵌套 LaTeX 命令**（如 `\boldsymbol{\frac{1}{8}}`）不能用简单 `[^}]*` 正则，必须用平衡括号匹配
- **千问裸 frac**: 千问输出 `frac{2}{5}`（无反斜杠），元宝输出 `\frac{2}{5}`，必须统一转换
- **千问粘连命令**: 千问输出 `sinfrac{...}`、`cosfrac{...}`（函数名直接粘 frac）
- **"正确答案是"marker 须 last-match**：取最后出现位置，避免捕获中间解释段落
- **extract_final_answer_line 长度过滤**: `len<=1 且不含[一-鿿\w]` 才过滤，允许"三"/"Y"等单字答案
- **元宝无效答案过滤**: "答案见解析"/"详见上述"等指代性无效答案必须过滤
- **extract_numerical 会从中间步骤提取无关数字**：必须让 extract_final_answer_line 优先

### 比对逻辑
- `answers_match` 参数顺序：`(ans1, ans2, type1, type2)` — 两答案在前两类型在后
- fill_in vs fill_in 须经 10 层递进匹配
- 英文单词集合兜底：≥3 字母英文词 set 比较，≥75% 重叠视为一致
- 分段匹配方向选择：按平均段长(avg)而非段数(count)选"答案方"
- **跨类型匹配优化原则**（v1.4→v1.6 教训）：只改 `answers_match()` 不改 `extract_choice()`。改变答案类型（fill_in→choice）会破坏 fill_in vs fill_in 的10层匹配，导致全面退步

### HTML 渲染
- Python `'''` 三引号字符串中 `\n`→换行符、`\b`→退格，会破坏 JS 正则。必须使用 `\\n` 双转义
- wrapNakedLatex Step 2/3 产生的 `$$...$$` 必须存入 prot 数组，防止二次包裹
- Step 7 清理只能用 `/\$\s+\$/g`，绝不能用 `/\$\$/g`（会删除 display math 定界符）
- HTML 内嵌 JSON 数据时需确保无 `</script>` 字符串
- renderAnswerContent ≠ renderDocContent：答案标签渲染必须按全角逗号`，`分段

### 钉钉
- 钉钉文档 API 不支持原地覆盖，必须先 delete 再上传
- **钉钉 WebView 横向滚动**: html/body 的 `overflow-x:hidden` 不被 WebView 尊重，必须加 `.page-wrap` 物理 wrapper div
- **移动端 detail-table-wrap max-height**: 必须 `max-height:none` 让内容自然撑开
- 文件级分享权限覆盖后丢失，须覆盖前备份、覆盖后恢复（或用文件夹 URL 规避）
- `commit_uploaded_file` 必须传 folderId
- **MCP 网关调用**: 当 `mcp__钉钉文档__*` 工具不可用时，使用 `dingtalk.py` 辅助脚本通过 HTTP JSON-RPC 直接调用 MCP 网关
    - **list_nodes API 有 bug**: `parentNodeId` 参数可能被忽略，始终返回工作空间根目录内容（而非目标文件夹的子节点）。**不可依赖 list_nodes 来清空文件夹**——曾导致误删工作空间下无关目录。正确做法：用 `get_document_info` 逐个验证文件归属，或直接 `create_folder` + 上传（不依赖 list）

### 完整性约束
- 每组"可比对数 + 无法判断数 = 总 query 数"，必须严格对齐
- disagreements 必须按日期独立存储，禁止用单一全局变量
- "无法判断"三类：①模型明确无法作答 ②答案无法结构化提取 ③模型文本为空

### 工具链
- Node.js v26 `node --check` 不支持 .html 扩展名，须先用 Python 提取 `<script>` 块到临时 .js 文件

### Web 页面性能（2026-06-08 沉淀）
- **defer 脚本时序竞争**: `fetch().then()` 可能先于 `defer` 脚本执行完成，此时 `typeof Chart === 'undefined'`。必须轮询等待
- **GitHub Pages 并发限制**: 多个独立 script 文件可能被 CDN 限制导致部分 pending，但合并 bundle 可能导致 UMD 模块初始化失败。目前方案：独立文件 + defer + 轮询
- **gzip Content-Length 陷阱**: GitHub Pages gzip 后 Content-Length 是压缩后大小（~2.1MB），ReadableStream 读到的是解压后数据（~7.1MB），进度条计算要用已知实际大小
- **OSS CORS**: 跨域 fetch OSS 需要配置 Bucket CORS 规则
- **GitHub Pages 国内慢**: 数据文件应从 OSS 加载（国内节点），GitHub Pages 作为备用
- **`vercel-deploy` 目录已删除**: 不再使用，统一用 `consistency-eval-gh` 目录对接 `paultunggm-pixel/consistency-eval` 仓库

## Verification

执行完成后必须验证：
- [ ] 脚本无报错，输出显示各对比对的一致率
- [ ] `原始数据-{日期}.xlsx` 行数 = 数据记录数 + 1
- [ ] `评测明细-{日期}.xlsx` 行数 = 数据记录数 × 5(对比对) + 1
- [ ] HTML 内嵌 JS 语法通过 `node --check` 验证
- [ ] history.json 中日期条目正确追加/覆盖
- [ ] 每个日期的无法判断明细条数与 HTML 概览中"无法判断 N 题"一致
- [ ] 钉钉各子目录文件已确认在正确位置
- [ ] 数据完整性: 每组"可比对数 + 无法判断数 = 总 query 数"
- [ ] **Web**: 趋势图正常显示（非 Chart.js CDN 加载失败）
- [ ] **Web**: `data.json` 已上传 OSS 并可从国内访问
- [ ] **Web**: `git push` 后 GitHub Actions 自动部署成功

## badcase 修复原则

- 必须通过通用算法优化+全局数据重跑，**禁止针对单条硬编码**
- 修复后必须验证历史无回归（逐日期重跑确认）

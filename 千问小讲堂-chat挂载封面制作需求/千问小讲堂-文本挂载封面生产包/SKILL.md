---
name: qianwen-cover-production
description: >-
  千问小讲堂课程封面：链路A 按学科产出 A/B/C 钩子/标签/学名/生图指令；
  链路B 确认版表挂载压图(style3/成语/数学)、OSS 回写。
  当用户提到课程封面、3-case、挂载封面、style3、科普妙题、学名确认版、url确认版、run_kepu 时使用。
---

# 千问小讲堂 · 封面生产 Skill

启动包根目录：`output/cover-generator/千问小讲堂-封面生产启动包/`  
链路 A 脚本：`output/cover-generator/scripts/`  
链路 B 脚本：本包 **`脚本/`**（见 `挂载压图分支说明.md`）  
数学压字字体：`output/cover-generator/字体规则.md`

## 0. 开工前必读

1. `00-从这里开始.md` — 先判定 **链路 A（文案）** 还是 **链路 B（挂载压图）**
2. 链路 A → `学科分支说明.md` + `skills-引用/` 对应摘要
3. 链路 B → **`挂载压图分支说明.md`** + `skills-引用/挂载压图-style3-摘要.md` + `scripts-索引/挂载压图脚本.md`

**用户不是技术老师**：用中文说明进度；先 2–3 条样例确认，再全量；全量后必须自检并汇报问题数。

## 1. 统一产出契约（所有学科）

每条课程产出 **3 个 case（A/B/C）**，每 case 四列：

| 字段 | 规则 |
|------|------|
| **钩子** | 主标题，口语化；数学/语文一般 ≤12 字；三式：①悬念反问 ②核心动作 ③情感共鸣 |
| **标签** | 数学：`【年级】★【关键词】` 或 `年级｜关键词`；语文/成语：固定 `千问小讲堂` |
| **学名** | 数学：课程短名；语文：`[类型]《篇目》` 或用户指定仅篇目；成语 tab：**成语名本身**（无书名号） |
| **生图指令** | 一整段连续中文为主 + 必要英文锚句；**严禁画面内任何文字** |

合并进 xlsx 时列布局（与 `build_yuwen.py` / `build_chengyu.py` 一致）：

- 原表列保留
- 追加 12 列：`A钩子 A标签 A学名 A生图` … `C钩子 C标签 C学名 C生图`

## 2. 学科路由（必须先判定）

### A. 数学（低龄 1–3 / 高年级 4–6）

- 规范：`skills-引用/数学-低龄封面-摘要.md`、`skills-引用/数学-高年级封面-摘要.md`
- 库：`scripts/cover_lib.py`（PIXAR / SWISS 模板、配色池、钩子公式）
- 批量：`scripts/batch_gen.py` + `scripts/batch_data.py`；合并 `scripts/build_v2.py`
- 生图负向锚：禁止 Chinese characters in image（见数学 v2 skill）
- **压图**（有底图 url 后）：`scripts/compose_math.py` + `refs/render_covers.py`
  - 小低钩子：造字工房元黑；小高：PuHuiTi Bold；徽标/标签：PuHuiTi；徽标色自适应底图
  - 底图预处理：`normalize_demo.py` 的 `normalize_bg`（边缘像素延展，禁止纯色补边色带）
  - 小低文字：`layout_low_figma`（能一行就一行，≥20 用 1 行）

### B. 语文（古诗词/课文/写作/科普/妙题）

- 规范：`skills-引用/语文-封面一体化-摘要.md`；详规 `scripts/YUWEN_AUTHOR_SPEC.md`
- 库：`scripts/yuwen_lib.py`（中国风、构图铁律、零文字、红色主题 L1/L2）
- 数据：按品类写 `scripts/yuwen_data_<模块>.py`，聚合 `scripts/yuwen_batch.py`
- 合并：`scripts/build_yuwen.py` → `outputs/千问小讲堂-线上内容汇总-0528-FINAL.xlsx`
- 校验：`scripts/validate_yuwen.py`
- 范例：`scripts/yuwen_pilot.py`、`outputs/yuwen-pilot-8-full.md`

### C. 趣学成语 / 成语故事 tab

- 与语文共用 `yuwen_lib.gen_three_cases`
- 数据：`scripts/yuwen_data_chengyu_b1..b4.py`（或新建模块）
- 构建：`scripts/build_chengyu.py`；学名 = **成语名**（用户已确认）
- 输入 CSV 通常在用户 Downloads；输出 `outputs/趣学成语-封面文案-3cases.xlsx`
- 范例：`scripts/chengyu_sample.py`

### D. 数学底图压字（链路 A，非挂载 OSS）

- 读 `字体规则.md`
- 表需含：年级、钩子、标签、底图 url
- 演示：`demo5_low.py`；批量：`compose_math.py` + 旧版 `refs/render_covers.py`

### E. 挂载压图（链路 B，确认版表 → CDN）

- 必读：`挂载压图分支说明.md`、`skills-引用/挂载压图-style3-摘要.md`
- 工程：本包 **`脚本/`**
- **style3 单名**（语文 / 科普 / 妙题）：
  - 输入：`学名·确认版` + `url·确认版`（列名可无中间点）
  - 科普/妙题：**不用钩子**；学名有 `《》` 时 **只压书名号内**（`display_name_from_xueming`）
  - 脚本：`run_kepu.py`（科普妙题）、`run_style3.py`（语文全量）
- **成语双行**：`学名·确认版` + `钩子·确认版` + `url·确认版` → `run_chengyu_all.py`
- **产出**：PNG 无损 + JPG ≤50KB → 回写 `封面压图压缩前url` / `封面压图压缩后url`
- 已跑通：语文 479、成语 50、科普+妙题 105（2026-06）

## 3. 标准工作流

```
【链路 A】判定学科 → 读规范摘要 → 样例确认 → build_*.py → validate → xlsx
          → (数学) normalize_bg → compose_math → png

【链路 B】读 挂载压图分支说明 → 确认表列 → run_kepu / run_style3 / run_chengyu_all
          → 样例 3 条 → 全量 → manifest + 回填 CSV（两列 CDN URL）
```

## 4. 生图通用铁律（语文/成语）

- 前置：`OPENING_RULE` + `NOTEXT_HEAD` + `NOTEXT_PROPS`（`yuwen_lib.py`）
- 主角：全身、上半画布、脚约 50% 高、下半留白地面延续
- 红色主题：必须 `detect_red_theme`；L1 无人物空镜，L2 背影/剪影
- A/B/C：共享考据与 hero，仅轮转 `titles` 三钩子 + 色调/光照变体（`_case_variants`）

## 5. 自检清单（全量后必做）

- [ ] 条数 = 输入清单条数，无漏 row/序号
- [ ] 每条 3 钩子字数、无书名号（除非用户要求）
- [ ] 学名格式符合本学科约定
- [ ] 生图指令含「画布构图铁律」「画面零文字铁律」
- [ ] hero/scene/props 未写牌匾/对联/招牌等带字物件
- [ ] 红色篇目已标 red_theme/red_level
- [ ] 运行对应 validate 脚本，问题数 = 0 或逐条列出

## 6. 并行规模化

- 语文/成语全量：拆 `yuwen_inputs/*.json` + 多 subagent 写 `yuwen_data_*.py`（每 agent ≤15 条）
- 合并前检查 row 不重复、content_kind 正确

## 7. 不要做的事

- 不要未经用户确认改学名格式（如成语是否加「成语《》」）
- 不要全局软投影压字兜底
- 不要在生图 prompt 正文写「留白给文字」「标题区」等正向文字暗示
- 不要 commit 除非用户明确要求

## 8. 关键路径速查

| 用途 | 路径 |
|------|------|
| 启动包说明 | `output/cover-generator/千问小讲堂-封面生产启动包/` |
| 脚本索引 | `.../scripts-索引/README.md` |
| 演进日志 | `.../logs/项目演进记录.md` |
| 挂载压图（本包） | `脚本/render_covers.py` |
| 挂载压图脚本索引 | `文档/scripts-索引/挂载压图脚本.md` |
| 链路 A 数学压图 | mentorx `output/cover-generator/scripts/compose_math.py` |
| 字体（本包） | `脚本/assets/` |
| 桌面统一包 | `~/Desktop/千问小讲堂-封面生产包/` |

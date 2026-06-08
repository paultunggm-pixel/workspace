# 脚本索引

> **链路 A**（文案 + 数学压字）：`output/cover-generator/scripts/`  
> **链路 B**（挂载压图 → OSS）：见 **[挂载压图脚本.md](./挂载压图脚本.md)**（桌面 `~/Desktop/qianwen-cover-generator/`）

---

## 链路 B 速查

| 脚本 | 学科 |
|------|------|
| `run_kepu.py` | 科普 + 妙题（style3，《》内学名，无钩子） |
| `run_style3.py` | 语文单名 |
| `run_chengyu_all.py` | 成语 50 篇（学名+钩子） |

---

## 链路 A（`output/cover-generator/scripts/`）

> 运行前：`cd output/cover-generator/scripts && python3 <脚本>.py`

---

## 一、核心库（被其他脚本 import）

| 文件 | 作用 |
|------|------|
| `cover_lib.py` | 数学：Pixar/Swiss 模板、配色池、钩子公式、`render_prompt` |
| `yuwen_lib.py` | 语文/成语：中国风铁律、零文字、红色主题、`gen_three_cases`、`render_yuwen_prompt` |
| `refs/render_covers.py` | 技术老师压图：徽标/标签/画布常量（`compose_math` 依赖） |

---

## 二、数学 · 文案 + 生图指令

| 文件 | 何时跑 | 产出 |
|------|--------|------|
| `batch_data.py` | 维护课程种子数据 | Python 常量 |
| `batch_gen.py` | 批量生成数学 case | md/json 或中间产物 |
| `build_v2.py` | 合并进带数学的主 xlsx | xlsx +12 列 |
| `validate_v2.py` | 全量后自检 | 终端问题列表 |
| `generate_copy.py` | 单条试写 | 控制台 |
| `merge_into_master.py` | 老版合并逻辑 | xlsx |

---

## 三、语文 · 文案 + 生图指令

| 文件 | 何时跑 | 产出 |
|------|--------|------|
| `yuwen_pilot.py` | 8 条试点数据（人工精修范例） | DATA 列表 |
| `yuwen_data_*.py` | 各品类授权数据（gushi/kewen/kepu…） | DATA 列表 |
| `yuwen_data_chengyu_b1..b4.py` | 趣学成语 50 条 | DATA 列表 |
| `yuwen_batch.py` | 聚合所有 `yuwen_data_*.py` | dict[row]→3 cases |
| `build_yuwen.py` | 写入 FINAL 主表 | `outputs/…FINAL.xlsx` |
| `validate_yuwen.py` | 全量校验 | 问题列表 |
| `render_yuwen_pilot.py` | 试点渲染说明 | md |
| `YUWEN_AUTHOR_SPEC.md` | **给 subagent 的授权规范** | 文档 |

输入 JSON：`yuwen_inputs/*.json`（由主表导出 row/grade/name/intro）

---

## 四、成语 · 独立表

| 文件 | 何时跑 | 产出 |
|------|--------|------|
| `chengyu_sample.py` | 3 条样例 | `outputs/趣学成语-样例3条.md` |
| `build_chengyu.py` | CSV → xlsx 全量 | `outputs/趣学成语-封面文案-3cases.xlsx` |

---

## 五、数学 · 压图合成

| 文件 | 何时跑 | 产出 |
|------|--------|------|
| `compose_math.py` | **主压图脚本**（render + 字体 + 徽标色） | png |
| `normalize_demo.py` | 底图 `normalize_bg` 原型 + 演示 | `examples/norm_*.png` |
| `demo5_low.py` | 5 张小低样例 + 质检打印 | `examples/low_*.png` |
| `demo_shadow.py` | 软投影试验（**已弃用全局**） | 演示 |
| `compare_b.py` | A/B 版式对比 | 演示 |

规范：`../字体规则.md`

---

## 六、依赖安装

```bash
cd output/cover-generator/refs
pip3 install -r requirements.txt
```

字体目录：`output/cover-generator/assets/`

---

## 七、推荐执行顺序（新同事/新 Agent）

```
1. 判定学科 → 读 启动包/skills-引用/
2. 文案阶段：写 data 模块 → batch/build → validate
3. 生图阶段：（人工）按 xlsx 指令出图
4. 压图阶段：cache 底图 → normalize_bg → compose_math → 清单
```

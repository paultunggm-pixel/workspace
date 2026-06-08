# 千问小讲堂 · 封面生产包（桌面统一版）

> **一个文件夹搞定**：说明文档 + Cursor Skill + 可执行脚本 + 历史日志。  
> 可整包复制/U 盘/压缩发给同事；本机也可长期放在桌面随时用。

---

## 第一次打开请看

1. **[00-从这里开始.md](./00-从这里开始.md)** — 选链路 A（文案）还是链路 B（挂载压图）  
2. **[发给Cursor的开场话术.md](./发给Cursor的开场话术.md)** — 复制一段话就能让 AI 开工  
3. 运行 **`./一键自检.sh`**（检查 Python、字体、脚本）

---

## 文件夹结构

```
千问小讲堂-封面生产包/
├── README.md                 ← 本文件
├── 00-从这里开始.md
├── 发给Cursor的开场话术.md
├── 挂载压图分支说明.md       ← 链路 B 主说明（科普/语文/成语压图）
├── 封面生成工作流与需求说明.md
├── SKILL.md                  ← 可安装到 Cursor（见 安装Cursor技能.md）
├── 一键自检.sh
│
├── 脚本/                     ← 【真源】压图代码，在此目录运行命令
│   ├── render_covers.py
│   ├── run_kepu.py           科普+妙题
│   ├── run_style3.py         语文
│   ├── run_chengyu_all.py    成语
│   ├── assets/               字体（约 37MB，发包必需）
│   └── output/               新批次产出放这里（默认可空）
│
├── 文档/                     ← 完整启动包（规范摘要、日志、模板、脚本索引）
│   ├── skills-引用/
│   ├── scripts-索引/
│   ├── logs/
│   └── templates/
│
├── 输入表/                   ← 建议把待生产的 CSV/xlsx 放这里
├── 产出示例/                 ← 历史 manifest/回填表示例（无大图）
└── 如何发给同事.md
```

---

## 链路 B 最快上手（挂载压图）

```bash
cd 脚本
pip3 install -r requirements.txt --user

# 科普+妙题（学名只显示《》内，不要钩子）
python3 run_kepu.py --csv "../输入表/你的表.csv" --out-dir output/kepu

# 语文单名
python3 run_style3.py --csv "../输入表/语文.csv" --out-dir output/style3

# 成语（学名+钩子）
python3 run_chengyu_all.py --csv "../输入表/成语.csv" --out-dir output/chengyu
```

表头需有：`学名·确认版`、`url·确认版`（成语另要 `钩子·确认版`）。

---

## 链路 A（文案 3-case）

规范与索引在 **`文档/`** 内；完整 Python 在 mentorx 仓库  
`Documents/mentorx-a2ui-content/output/cover-generator/scripts/`（未整包打入，体积大）。  
只需文案时：用 Cursor + `文档/SKILL.md` + `发给Cursor的开场话术.md` 即可。

---

## 与旧文件夹的关系

| 旧位置 | 本包对应 |
|--------|----------|
| `Desktop/qianwen-cover-generator/` | → **`脚本/`**（建议以后只维护本包） |
| mentorx `千问小讲堂-封面生产启动包/` | → **`文档/`** + 顶层常用 md |

更新脚本时：改 **`脚本/`** 里的文件即可；需要同步 mentorx 启动包时再单独拷贝 `文档/`。

---

## 环境说明

- **Python 3** + Pillow（`pip3 install -r 脚本/requirements.txt`）
- **上传 CDN**：需本机 `~/Desktop/ossutilmac64`（未打包，涉账号）
- **设计成品图**（成语）：默认路径 `~/Desktop/寓言故事/`（见 `run_chengyu_all.py`）

---

**版本**：2026-06-03 · 含科普/妙题 105 条规则、《》内学名、style3 无钩子

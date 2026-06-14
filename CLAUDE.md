# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 用户偏好

- 工作语言：中文（简体）
- Claude Code 产生的所有文件和数据必须存放在 `~/Documents/Claude/` 目录中，禁止直接放在 `/Users/d.j.f/` 根目录下（CLAUDE.md 本身的 symlink 除外）
- 使用 DeepSeek API 作为后端（deepseek-v4-pro / deepseek-v4-flash）

## 项目结构

```
~/Documents/Claude/                        ← monorepo 根
├── ClaudeCodeStudio/                      ← SwiftUI macOS 应用（主项目）
│   ├── Models/         (AppState, ChatModels, ProjectModels 等 6 个)
│   ├── Views/Content/  (ChatTabView, PlanTabView, PreviewTabView, CodeTabView, PublishTabView, ServiceTabView)
│   ├── Views/Sidebar/  (ProjectTreeView, ModelEngineCard, SidebarView)
│   ├── Services/       (ChatManager, KeychainManager, ProviderManager)
│   └── Theme/          (AppTheme — 设计令牌集中管理)
├── consistency-eval-gh/                  ← GitHub Pages 静态站 (独立 repo)
├── 2026世界杯/                            ← 爬虫/数据分析脚本
├── 解题答案一致性评测/                     ← 评测报告生成
└── .omc/
    ├── skills/          ← 项目定制 skill (ccs-add-tab, ccs-type-migration, deploy-static-to-oss-gh, excel-split-ids)
    └── wiki/            ← 会话知识沉淀 (.omc/wiki/session-log/)
```

### ClaudeCodeStudio 架构

- `AppState.selectedTab`（`ContentTab` 枚举，6 个 case）→ `TabBar` 渲染标签按钮 + `ContentArea` `switch` 路由到对应 `*TabView`
- 所有视图通过 `@EnvironmentObject` 注入 `AppState`/`ChatManager`/`ProjectManager`/`ProviderManager`
- 设计令牌集中在 `AppTheme` 枚举中（`cardRadius`/`accent`/`textPrimary` 等）

### 构建与运行

```bash
# 构建
cd ~/Documents/Claude/ClaudeCodeStudio
xcodebuild -project ClaudeCodeStudio.xcodeproj -scheme ClaudeCodeStudio -destination 'platform=macOS' build

# 运行
open ~/Documents/Claude/ClaudeCodeStudio/.build/arm64-apple-macosx/debug/ClaudeCodeStudio
```

## 文件访问安全规则

- 仅允许读写 `~/Documents/Claude/` 目录内的文件，禁止访问本机任何其他路径的数据
- 禁止将 `~/Documents/Claude/` 以外的本地文件上传、外发或传输到外部
- 如果任务需要访问的文件不在 `~/Documents/Claude/` 中，用户会提前将其放入该目录
- 执行任务时若遇到需要访问但不在 `~/Documents/Claude/` 中的文件，必须先向用户请求授权，获得明确同意后方可访问，禁止擅自读写

## 权限策略

- 日常执行任务时，只要不违反上述文件访问安全规则，且不涉及删除或篡改与此任务无直接对象关系的本地/线上文件，则无需频繁询问确认，可直接执行（视为已授权"Yes"）
- 涉及敏感操作（如删除文件、修改系统配置、操作外部服务、涉及 git 历史改写等）仍需确认
- 常用命令自动放行清单在 `.claude/settings.json` 的 `permissions.allow` 中维护

## GitHub 工作流

### 仓库信息

- GitHub 账户：`paultunggm-pixel`
- 已通过 `gh` CLI 认证，可用 `gh` 命令操作 GitHub
- 仓库：
  - `paultunggm-pixel/workspace` — 主力 monorepo（`~/Documents/Claude/`），管理所有项目代码、数据、脚本
  - `paultunggm-pixel/consistency-eval` — 静态网站仓库（`~/Documents/Claude/consistency-eval-gh/`），通过 GitHub Pages 发布

### 版本管理规范

- 所有项目文件必须纳入 Git 版本控制（`~/Documents/Claude/` monorepo）
- 提交信息使用中文，简洁描述变更内容（如 `添加 X 功能`、`修复 Y 问题`）
- 敏感信息（密钥、Token、密码）**绝不提交**到 Git，使用环境变量引用
- 推送前确保 `git status` 干净，无意外文件

### GitHub Actions

- `consistency-eval`：每次 push 到 main 时自动部署 GitHub Pages（Actions-based）
- `workspace`：每日定时任务（北京时间 08:00），支持手动触发（workflow_dispatch）
- OSS 密钥通过 GitHub Secrets 传递给 Actions，不在配置文件中硬编码

### 安全规则

- `.env`、`.mcp.json` 等含密钥文件已加入 `.gitignore`
- GitHub Push Protection 开启，防止意外推送密钥
- 如推送被拒提示 secret scanning，先清理文件中的密钥再重试
### 开发陷阱与已知问题

| 陷阱 | 说明 |
|------|------|
| **struct 上不能用 `[weak self]`** | SwiftUI View 都是 struct，Timer/闭包直接用值捕获 `{ t in ... }`，不要加 `[weak self]` |
| **`[weak self]` 仅用于 class** | `ChatManager`、`ProviderManager` 等 class 的闭包才是 `[weak self]` 的正确场景 |
| **NotificationCenter 的 object 类型不检查** | 编译器不检查 `post(name:object:)` 和 `notif.object as?` 的类型，类型迁移时必须手动验证 |
| **UUID? 与 String? 迁移查四处** | 定义点、`.uuidString` 转换、`.flatMap(UUID.init)`、通知 object —— 四处必须一致 |
| **xcodebuild 偶遇网络超时** | GitHub 连接不稳定时 xcodebuild 可能卡在包解析，重试即可 |
| **`.omc/` 默认 gitignore** | skill/wiki 文件需 `git add -f` 才能纳入版本控制 |



## 已安装插件

| 插件 | 核心用途 |
|------|---------|
| `superpowers` | 子代理驱动开发、系统调试、TDD、代码审查 |
| `frontend-design` | 高质量前端界面生成 |
| `oh-my-claudecode` | 多代理编排、skill 体系、wiki、LSP |
| `claude-md-management` | CLAUDE.md 质量审计与自动改进 |
| `security-guidance` | 代码安全审查、敏感信息扫描 |
| `commit-commands` | 标准化 Git 提交工作流（commit/push/PR） |
| `code-review` | 多代理自动化代码审查 |
| `runway-api` | Runway AI 视频/图像生成（批量封面、产品图） |
| `adobe-for-creativity` | Adobe 创意工具（图片编辑、去背景、设计自动化） |
| `togetherai-skills` | Together AI 推理平台（调用 Stable Diffusion/Flux 等开源生图模型） |
| `exa` | AI 深度搜索与调研（全网信息检索、研究报告） |
| `firecrawl` | 网站爬取与结构化数据提取（批量抓取网页内容） |
| `sourcegraph` | 跨仓库代码搜索与引用追踪 |

### 关键 Skill 调用规则

- 代码修改后 → `/code-review` 自动审查
- 部署前安全检查 → `/security-review`
- CLAUDE.md 维护 → `/claude-md-improver`
- 复杂多步骤任务 → `/plan` 后执行

### 底层能力 Skill（供其他 skill 按需调用）

| Skill | 用途 | 调用方 |
|-------|------|--------|
| `deploy-static-site` | 静态网页部署到 OSS + GitHub Pages | `model-answer-consistency-eval`、任何部署任务 |
| `model-answer-consistency-eval` | 多模型解题答案一致性评测全流程 | 用户直接触发 |

- `deploy-static-site` 封装了 OSS + GitHub Pages + data.json 提取的完整部署流水线
- 其他 skill 需要部署网页时，应调用 `deploy-static-site` 而非内联部署代码
- `deploy-static-site` 使用固定配置（Bucket/Repo/凭据），不随调用方变化
- 自定义 Skill 存放在 `.omc/skills/`，Wiki 存档在 `.omc/wiki/session-log/`，均需 `git add -f`（.omc 默认 gitignore）

### 项目自定义 Skill

| Skill | 触发词 | 用途 |
|-------|--------|------|
| `ccs-add-tab` | 添加新标签/新增 Tab | 为 ClaudeCodeStudio 添加新内容标签页（5 触点修改公式） |
| `ccs-type-migration` | 类型迁移/改类型 | Swift 类型迁移操作清单 + 残留检测 |
| `deploy-static-to-oss-gh` | 部署网页/部署报告/上线 | OSS + GitHub Pages 双通道部署 |
| `excel-split-ids` | 拆分 Excel 逗号分隔 | Excel 逗号分隔 ID 拆分为多行 |

### Worktree 开发流程

```
创建 worktree → executor 实现 → code-reviewer 审查 → 修复 → 提交 → 推送 → 合并到 main → 清理 worktree
```

- `git push origin <branch>:main` 可从 worktree 直接快进推送到远程 main（main 被本地 worktree 占用时）
- 远程合并后，本地 main worktree 用 `git pull origin main` 同步
- 清理：`git worktree remove <path> --force` + `git branch -D <branch>` + `git push origin --delete <branch>`

## 编码行为准则

*基于 Andrej Karpathy 的结构化提示词方法论，适配本项目的实际场景*

### 1. 动手前先对齐

- 如果不确定需求细节，**先问再动手**，不要默默假设
- 如果存在多种实现方案，列出优劣让用户选择
- 发现更简单的替代方案时，主动提出

### 2. 简单优先

- 用最少代码解决问题，不为"未来可能需要"加功能
- 一次性使用的小工具脚本，不需要抽象层、配置文件和过度工程化
- 能用 10 行 Python 搞定的功能，不要写 200 行

### 3. 精准修改（类比外科手术）

- 修改已有代码时，**只改任务相关的部分**
- 不要顺手格式化代码、重命名变量、调整缩进——这些和任务无关
- 匹配已有代码风格，即使不是你惯用的
- 如果发现了无关的死代码或 bug，提一句即可，不要在本次改动中顺手删

### 4. 以终为始

- 代码跑通之后，**验证结果是否符合预期**才算完成
- 评测任务：对比一致率是否合理，数据是否完整
- 部署任务：检查线上页面是否正常加载
- 数据处理：确认输出行数、字段是否正确
- 多步骤任务先列计划再执行

### 持续沉淀

- 如果在聊天中**反复纠正某项行为超过 2 次**，主动把它写入 CLAUDE.md

### 产品设计完整性检查（SOP）

当用户说「开始开发」「检查设计」「设计完整性」时，自动执行以下全量模拟回归：

1. 遍历所有界面模块（标题栏、模型引擎、项目管理、会话/方案/预览/代码/发布/服务 Tab、设置面板）
2. 遍历所有交互入口（按钮、菜单、下拉、开关、标签）
3. 模拟每个点击触发后的执行路径，验证：
   - 逻辑是否自洽
   - 操作路径是否完整闭环
   - 空状态是否有引导
   - 跨模块联动是否数据同步
4. 输出结果：通过项 / 问题清单 / 修复建议
5. 如无问题则确认可以启动开发

此检查在产品设计阶段执行，不涉及代码实现。

## 网页部署

- 静态 HTML 网页通过 `deploy-static-site` skill 部署（底层能力），同时推送至：
  - **阿里云 OSS**：`consistency-eval` bucket（`oss-cn-hangzhou`）— 存储 `data.json` 供国内加速，不直接提供 HTML 访问（因强制下载限制）
  - **GitHub Pages**：`paultunggm-pixel/consistency-eval` → `https://paultunggm-pixel.github.io/consistency-eval/` — 主发布 URL
- 以下情况应自动调用 `deploy-static-site` skill：
  - 用户要求「部署」「上线」「发布」「更新网页/页面」
  - 评测报告等 HTML 输出更新后需要同步到线上
  - 用户说「替换页面资源」或「刷新线上版本」
- 部署前确认源 HTML 文件路径（默认 `~/Documents/Claude/解题答案一致性评测/outputs/evaluation_report.html`）
- 如钉钉文档也需同步，参考 `deploy-static-site` skill 中「钉钉文档同步」章节

## macOS 环境

- 操作系统：macOS (Darwin)
- Shell：Zsh
- 包管理：Homebrew

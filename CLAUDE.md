# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 用户偏好

- 工作语言：中文（简体）
- Claude Code 产生的所有文件和数据必须存放在 `~/Documents/Claude/` 目录中，禁止直接放在 `/Users/d.j.f/` 根目录下（CLAUDE.md 本身的 symlink 除外）
- 使用 DeepSeek API 作为后端（deepseek-v4-pro / deepseek-v4-flash）

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

### 关键 Skill 调用规则

- 代码修改后 → `/code-review` 自动审查
- 部署前安全检查 → `/security-review`
- CLAUDE.md 维护 → `/claude-md-improver`
- 复杂多步骤任务 → `/plan` 后执行

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

## 网页部署

- 静态 HTML 网页通过 `deploy-static-site` skill 部署，同时推送至：
  - **阿里云 OSS**：`consistency-eval` bucket（`oss-cn-hangzhou`）
  - **GitHub Pages**：`paultunggm-pixel/consistency-eval` → `https://paultunggm-pixel.github.io/consistency-eval/`
- 以下情况应自动调用 `deploy-static-site` skill：
  - 用户要求「部署」「上线」「发布」「更新网页/页面」
  - 评测报告等 HTML 输出更新后需要同步到线上
  - 用户说「替换页面资源」或「刷新线上版本」
- 部署前确认源 HTML 文件路径（默认 `~/Documents/Claude/解题答案一致性评测/outputs/evaluation_report.html`）
- 如钉钉文档也需同步，参考 skill 中「钉钉文档同步」章节

## macOS 环境

- 操作系统：macOS (Darwin)
- Shell：Zsh
- 包管理：Homebrew

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

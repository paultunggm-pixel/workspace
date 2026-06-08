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

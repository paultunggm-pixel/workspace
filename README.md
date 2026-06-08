# Claude Code Workspace

paultunggm-pixel 的 Claude Code 工作空间 — 所有项目、数据、脚本的 Monorepo。

## 目录结构

| 目录/文件 | 说明 |
|----------|------|
| `CLAUDE.md` | Claude Code 项目规则与偏好配置 |
| `解题答案一致性评测/` | AI 解题答案一致性自动评测（含原始数据、分析脚本、报告输出） |
| `2026世界杯名单比对结果/` | 世界杯参赛名单与多数据源比对 |
| `2026世界杯锐评话题PK清单/` | 世界杯锐评话题 PK 对战清单 |
| `千问小讲堂-chat挂载封面制作需求/` | 千问小讲堂 Chat 挂载封面生成工具（含数据归档、生产包、OSS 上传） |
| `千问小讲堂-列表页封面制作需求/` | 列表页封面制作工具（含吸色脚本） |
| `支撑内容范式的数据字段寻找匹配/` | 内容范式数据字段匹配调研 |
| `陈琳颖id汇总整理/` | 陈琳颖 ID 汇总整理 |
| `consistency-eval-gh/` | 独立仓库 — 评测报告 GitHub Pages（[在线访问](https://paultunggm-pixel.github.io/consistency-eval/)） |
| `worldcup-demo/` | 世界杯 Demo 页面 |
| `public-site/` | 公共站点文件 |
| `Polymarket_*` | Polymarket 数据源调研报告 |
| `gen_*.py` / `deploy_*.py` | 报告生成 & OSS 部署脚本 |
| `wc2026_*.py` | 世界杯数据分析与预测脚本 |
| `.env.example` | 环境变量模板（密钥配置参考） |
| `.github/workflows/` | GitHub Actions 定时任务工作流 |

## 安全说明

- **绝不提交密钥**：所有 API 密钥通过环境变量读取（参考 `.env.example`）
- `.env`、`.mcp.json` 已加入 `.gitignore`，不会被提交
- GitHub Push Protection 开启，自动拦截含密钥的推送

## 快速命令

```bash
# 部署静态网站（调用 deploy-static-site skill）
# 自动推送至阿里云 OSS + GitHub Pages

# 运行一致性评测
cd ~/Documents/Claude/解题答案一致性评测
python3 analyze_v3.py
```

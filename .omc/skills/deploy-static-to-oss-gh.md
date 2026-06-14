---
name: deploy-static-to-oss-gh
description: 将静态 HTML 报告/网页部署到阿里云 OSS + GitHub Pages 双通道。适用于 evaluation_report.html、polymarket_report.html、landing page 等静态资源。
triggers:
  - 部署网页
  - 部署报告
  - 部署 HTML
  - 发布页面
  - 上线
  - deploy static
  - OSS 上传
  - GitHub Pages 部署
---

# 静态网页部署：OSS + GitHub Pages 双通道

## 适用场景

将静态 HTML 文件发布到线上，供公网访问。典型场景：
- 解题一致性评测报告 `evaluation_report.html`
- Polymarket 数据报告 `polymarket_report.html`
- 世界杯时效性站点排查报告
- Claude Code Studio landing page

## 架构

```
本地 HTML 文件
    ├──→ 阿里云 OSS (consistency-eval bucket)     → 国内加速 / 备份
    └──→ GitHub Pages (paultunggm-pixel/consistency-eval) → 主发布 URL
```

- **OSS**: `oss-cn-hangzhou`，bucket `consistency-eval`
- **GitHub Pages**: `https://paultunggm-pixel.github.io/consistency-eval/<filename>.html`
- **凭据**: 通过环境变量 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` 注入

## 执行步骤

### 1. 确认源文件

```bash
ls -lh <HTML文件路径>
```

### 2. 部署到 OSS

```bash
python3 << 'PYEOF'
import oss2, os, json

auth = oss2.Auth(os.environ["OSS_ACCESS_KEY_ID"], os.environ["OSS_ACCESS_KEY_SECRET"])
bucket = oss2.Bucket(auth, "oss-cn-hangzhou.aliyuncs.com", "consistency-eval")

# 设置公开读策略（幂等，重复执行安全）
policy = {
    "Version": "1",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["oss:GetObject"],
        "Principal": ["*"],
        "Resource": ["acs:oss:*:*:consistency-eval/*"]
    }]
}
bucket.put_bucket_policy(json.dumps(policy))

# 上传
bucket.put_object_from_file('<OSS上的文件名>', '<本地文件路径>',
    headers={'Content-Type': 'text/html; charset=utf-8'})
print("✅ OSS 上传完成")
PYEOF
```

- OSS 默认不支持直接访问 HTML（会触发下载），静态网站托管需用 `oss-website` 域名

### 3. 部署到 GitHub Pages

```bash
cd ~/Documents/Claude/consistency-eval-gh

# 复制 HTML 到 Pages 仓库
cp <源HTML路径> ./<目标文件名>.html

# 提交并推送
git add .
git commit -m "部署: <描述> - $(date +%Y-%m-%d)"
git push origin main
```

### 4. 提取并上传 data.json

如果页面需要动态数据，同时更新 `data.json`：

```bash
python3 << 'PYEOF'
import json
data = {"key": "value"}  # 替换为实际数据
with open('data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False)
PYEOF

# 同步到 OSS 和 GitHub Pages
# OSS:
python3 -c "
import oss2, os
bucket = oss2.Bucket(oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'], os.environ['OSS_ACCESS_KEY_SECRET']), 'oss-cn-hangzhou.aliyuncs.com', 'consistency-eval')
bucket.put_object_from_file('data.json', 'data.json', headers={'Content-Type': 'application/json'})
"

# GitHub Pages: 同步骤 3，复制 data.json 到 consistency-eval-gh/
```

### 5. 验证

```bash
# GitHub Pages（主 URL）
echo "https://paultunggm-pixel.github.io/consistency-eval/<文件名>.html"

# OSS 直接地址（可能触发下载）
echo "https://consistency-eval.oss-cn-hangzhou.aliyuncs.com/<文件名>"
```

## 常见陷阱

| 陷阱 | 对策 |
|------|------|
| **OSS HTML 被强制下载** | OSS 默认 `Content-Disposition: attachment`。用 `consistency-eval.oss-website-cn-hangzhou.aliyuncs.com` 域名访问，或 GitHub Pages 作为主 URL |
| **GitHub Pages 缓存延迟** | 推送后等 1-2 分钟，加 `?v=<timestamp>` 参数强制刷新 |
| **data.json CORS** | OSS 和 GitHub Pages 跨域时需在 OSS 设置 CORS 规则（已在 bucket policy 中处理） |
| **凭据过期** | OSS 密钥有有效期，检查 `~/.env` 文件中的值是否最新 |
| **两次部署不同步** | 先部署 OSS，再部署 GitHub Pages，确保 data.json 和 HTML 同步更新 |
| **大型 HTML 上传超时** | 文件超过 50MB 时 OSS 用分片上传；GitHub Pages 限制 1GB/repo |

## 环境变量

这些变量必须在当前 shell 环境中可用：

```bash
export OSS_ACCESS_KEY_ID="..."
export OSS_ACCESS_KEY_SECRET="..."
```

## 扩展：钉钉文档同步

如果部署的报告需要同步到钉钉文档，参考 `解题答案一致性评测/dingtalk.py`。

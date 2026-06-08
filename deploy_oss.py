#!/usr/bin/env python3
"""一键部署：配置 OSS 静态网站托管 + 上传 HTML 报告"""

import oss2
import os
import json

# 配置
ACCESS_KEY_ID = os.environ["OSS_ACCESS_KEY_ID"]
ACCESS_KEY_SECRET = os.environ["OSS_ACCESS_KEY_SECRET"]
ENDPOINT = "oss-cn-hangzhou.aliyuncs.com"
BUCKET_NAME = "consistency-eval"
HTML_PATH = os.path.expanduser("~/Documents/Claude/解题答案一致性评测/outputs/evaluation_report.html")

auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

# Step 1: 开启静态网站托管
print("1/4 开启静态网站托管...")
website_config = oss2.models.BucketWebsite(index_file="index.html", error_file="404.html")
bucket.put_bucket_website(website_config)
print("   ✅ 静态网站托管已开启")

# Step 2: 通过 Bucket Policy 设置公开读
print("2/4 设置公开读权限...")
policy = {
    "Version": "1",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["oss:GetObject"],
        "Principal": ["*"],
        "Resource": [f"acs:oss:*:*:{BUCKET_NAME}/*"]
    }]
}
bucket.put_bucket_policy(json.dumps(policy))
print("   ✅ 公开读权限已设置")

# Step 3: 上传 HTML 报告 (重命名为 index.html)
print("3/4 上传 HTML 报告...")
file_size = os.path.getsize(HTML_PATH)
print(f"   文件大小: {file_size / 1024 / 1024:.1f} MB")
with open(HTML_PATH, 'rb') as f:
    bucket.put_object('index.html', f, headers={'Content-Type': 'text/html; charset=utf-8'})
print("   ✅ 上传完成")

# Step 4: 输出访问 URL
website_host = f"{BUCKET_NAME}.oss-website-cn-hangzhou.aliyuncs.com"
oss_url = f"https://{BUCKET_NAME}.oss-cn-hangzhou.aliyuncs.com/index.html"
website_url = f"http://{website_host}/"
print(f"\n🎉 部署完成！")
print(f"   静态网站托管地址: http://{website_host}/")
print(f"   OSS 直接地址:     {oss_url}")

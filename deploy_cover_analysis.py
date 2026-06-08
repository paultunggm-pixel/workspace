#!/usr/bin/env python3
"""部署 HTML 到 OSS — 尝试多种方式避免强制下载"""

import oss2
import os

ACCESS_KEY_ID = os.environ["OSS_ACCESS_KEY_ID"]
ACCESS_KEY_SECRET = os.environ["OSS_ACCESS_KEY_SECRET"]
ENDPOINT = "oss-cn-hangzhou.aliyuncs.com"
BUCKET_NAME = "consistency-eval"

HTML_PATH = os.path.expanduser(
    "~/Documents/Claude/千问小讲堂-chat挂载封面制作需求/千问小讲堂-封面制作业务流程分析.html"
)

auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

# ====== 方案1: 根目录 + 不设 Content-Disposition ======
OBJECT_NAME = "cover-analysis.html"
print(f"方案1: 上传到根目录 {OBJECT_NAME} ...")

with open(HTML_PATH, 'rb') as f:
    result = bucket.put_object(
        OBJECT_NAME, f,
        headers={'Content-Type': 'text/html; charset=utf-8'}
    )
print(f"   状态: {result.status}")

# 验证 headers
resp = bucket.head_object(OBJECT_NAME)
print(f"   Content-Type: {resp.headers.get('Content-Type')}")
print(f"   Content-Disposition: {resp.headers.get('Content-Disposition')}")

url1 = f"https://{BUCKET_NAME}.oss-cn-hangzhou.aliyuncs.com/{OBJECT_NAME}"

# ====== 方案2: 也上传到子目录作为备用 ======
OBJECT_NAME2 = "qianwen-lecture/cover-analysis.html"
print(f"\n方案2: 上传到子目录 {OBJECT_NAME2} ...")

with open(HTML_PATH, 'rb') as f:
    result = bucket.put_object(
        OBJECT_NAME2, f,
        headers={'Content-Type': 'text/html; charset=utf-8'}
    )
print(f"   状态: {result.status}")

url2 = f"https://{BUCKET_NAME}.oss-cn-hangzhou.aliyuncs.com/{OBJECT_NAME2}"

print(f"\n===== 结果 =====")
print(f"🔗 URL1 (根目录): {url1}")
print(f"🔗 URL2 (子目录): {url2}")
print(f"\n请两个都试试，看哪个不会触发下载。")

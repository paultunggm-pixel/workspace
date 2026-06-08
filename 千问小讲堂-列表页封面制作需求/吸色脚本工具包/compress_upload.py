#!/usr/bin/env python3
"""
compress_upload.py - 图片下载、压缩(JPEG quality=95)、上传OSS，返回压缩后URL
用法:
    python3 compress_upload.py batch <input.jsonl> <output.jsonl> --url-field url --postfix _compressed
"""

import requests
import io
import os
import json
import socket
import traceback
import argparse
from urllib.parse import urlparse
from PIL import Image


def upload_to_souti_oss(file_path):
    """上传本地文件到 Souti OSS，返回 CDN URL，失败返回空字符串"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    osscmd = os.path.join(script_dir, 'ossutilmac64')
    oss_ak = os.environ["SOUTI_OSS_ACCESS_KEY_ID"]
    oss_sk = os.environ["SOUTI_OSS_ACCESS_KEY_SECRET"]
    cmd = (f'{osscmd} -e oss-cn-hangzhou.aliyuncs.com '
           f'-i {oss_ak} -k {oss_sk} '
           f'cp -f {file_path} oss://sm-frontend-private-img/souti-imgs-lasting/')
    print(cmd)
    ret = os.system(cmd)
    if ret == 0:
        file_name = os.path.basename(file_path)
        url = f'https://cdn-private.sm.cn/souti-imgs-lasting/{file_name}'
        return url
    else:
        print(f'[ERROR] 上传 {file_path} 到 OSS 失败')
        return ''


def download_image(url):
    """从URL下载图片，返回PIL Image对象"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    response = requests.get(url, timeout=30, headers=headers)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content))
    return img.convert('RGB')


def compress_and_upload(image_url, output_file, quality=95):
    """下载图片，压缩保存为JPEG，上传OSS"""
    print(f'正在下载图片: {image_url}')
    img = download_image(image_url)
    print(f'图片尺寸: {img.size}')
    img.save(output_file, 'JPEG', quality=quality)
    print(f'已压缩保存到: {output_file} (quality={quality})')
    return output_file


def process_batch(input_jsonl, output_jsonl, url_field, quality=95, tmp_dir='tmp', postfix='_compressed'):
    """批量处理JSONL：下载压缩上传，输出新URL"""
    out_field = f'{url_field}{postfix}'
    os.makedirs(tmp_dir, exist_ok=True)

    # 加载已完成记录（增量跳过）
    done_set = set()
    if os.path.exists(output_jsonl):
        with open(output_jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    key = rec.get(url_field, '')
                    if key and rec.get(out_field, ''):
                        done_set.add(key)
                except Exception:
                    pass
        print(f'已载入 {len(done_set)} 条已处理记录，将跳过')

    # 读入全量输入数据
    all_records = []
    with open(input_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            all_records.append(json.loads(line))
    total = len(all_records)
    print(f'共 {total} 条记录')

    fout = open(output_jsonl, 'a', encoding='utf-8')
    success_count = 0
    skip_count = 0
    fail_count = 0

    for idx, rec in enumerate(all_records, 1):
        image_url = rec.get(url_field, '').strip()
        if not image_url:
            print(f'[{idx}/{total}] 字段 {url_field} 为空，跳过')
            skip_count += 1
            continue

        if image_url in done_set:
            print(f'[{idx}/{total}] 已处理，跳过: {image_url}')
            skip_count += 1
            continue

        # 构造本地临时文件名
        parsed = urlparse(image_url)
        orig_name = os.path.basename(parsed.path)
        stem, _ = os.path.splitext(orig_name)
        local_file = os.path.join(tmp_dir, f'{stem}{postfix}.jpg')

        print(f'[{idx}/{total}] 处理: {image_url}')
        try:
            compress_and_upload(image_url, local_file, quality=quality)
        except Exception as e:
            print(f'[{idx}/{total}] 压缩失败: {e}')
            print(traceback.format_exc())
            fail_count += 1
            continue

        oss_url = upload_to_souti_oss(local_file)
        if not oss_url:
            print(f'[{idx}/{total}] OSS上传失败: {local_file}')
            fail_count += 1
            continue

        rec[out_field] = oss_url
        fout.write(json.dumps(rec, ensure_ascii=False) + '\n')
        fout.flush()
        done_set.add(image_url)
        success_count += 1
        print(f'[{idx}/{total}] 完成: {oss_url}')

    fout.close()
    print(f'\n批处理完成：成功 {success_count}，跳过 {skip_count}，失败 {fail_count}')
    print(f'结果已保存到: {output_jsonl}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='图片压缩上传OSS工具')
    parser.add_argument('input_jsonl', help='输入JSONL文件路径')
    parser.add_argument('output_jsonl', help='输出JSONL文件路径')
    parser.add_argument('--url-field', required=True, help='包含图片URL的字段名')
    parser.add_argument('--quality', type=int, default=95, help='JPEG压缩质量 0-100（默认95）')
    parser.add_argument('--tmp-dir', default='tmp', help='临时文件目录（默认 tmp/）')
    parser.add_argument('--postfix', default='_compressed', help='输出字段后缀（默认 _compressed）')

    args = parser.parse_args()
    process_batch(args.input_jsonl, args.output_jsonl, args.url_field, args.quality, args.tmp_dir, args.postfix)

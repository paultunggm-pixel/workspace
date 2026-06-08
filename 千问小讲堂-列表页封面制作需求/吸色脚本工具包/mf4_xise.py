#!/usr/bin/env python3
"""
mf4_xise.py - 图片吸色脚本
从图片URL中提取主色调，按照规范调整HSB值后输出为JPG文件

吸色规范：
- top模式（黑色文字）：H不变，S：7-15，B：94-97，A：100
- bottom模式（白色文字）：H不变，S：40-50，B：35-45，A：100
（用于制作取色渐变蒙层）

用法:
    # 单张模式
    python mf4_xise.py single <图片URL> <输出文件名.jpg>
    python mf4_xise.py single <图片URL> <输出文件名.jpg> --alpha 0.6

    # 批处理模式
    python mf4_xise.py batch <input.jsonl> <output.jsonl> --url-field url
    python mf4_xise.py batch <input.jsonl> <output.jsonl> --url-field cover_url --alpha 0.5
"""

import requests
import numpy as np
from PIL import Image
import colorsys
import io
import os
import json
import socket
import traceback
import argparse
import sys
from urllib.parse import urlparse

try:
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def upload_to_souti_oss(file_path):
    """上传本地文件到 Souti OSS，返回 CDN URL，失败返回空字符串"""
    hostname = socket.gethostname()
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


def get_dominant_color_kmeans(img, n_clusters=5):
    """使用K-means聚类提取图片主色调（更准确）"""
    # 缩小图片以加快处理速度
    img_small = img.resize((100, 100), Image.LANCZOS)
    pixels = np.array(img_small).reshape(-1, 3).astype(float)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(pixels)

    # 找到像素数最多的聚类中心
    counts = np.bincount(kmeans.labels_)
    dominant_idx = np.argmax(counts)
    dominant_color = kmeans.cluster_centers_[dominant_idx]

    return tuple(map(int, dominant_color))


def get_dominant_color_simple(img):
    """简单方式提取主色调：对缩略图取平均色（不依赖sklearn）"""
    img_small = img.resize((50, 50), Image.LANCZOS)
    pixels = np.array(img_small).reshape(-1, 3)
    avg = pixels.mean(axis=0)
    return tuple(map(int, avg))


def get_dominant_color(img):
    """提取图片主色调（优先使用K-means）"""
    if HAS_SKLEARN:
        return get_dominant_color_kmeans(img)
    else:
        print('提示: 未安装 scikit-learn，使用均值方法提取主色调（可 pip install scikit-learn 获得更好效果）')
        return get_dominant_color_simple(img)


def rgb_to_hsb(r, g, b):
    """
    RGB转HSB（即HSV）
    返回: H(0~360), S(0~100), B(0~100)
    """
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return h * 360.0, s * 100.0, v * 100.0


def hsb_to_rgb(h, s, b):
    """
    HSB转RGB
    输入: H(0~360), S(0~100), B(0~100)
    返回: (R, G, B) 各 0~255
    """
    r, g, bv = colorsys.hsv_to_rgb(h / 360.0, s / 100.0, b / 100.0)
    return int(round(r * 255)), int(round(g * 255)), int(round(bv * 255))


def adjust_color_for_overlay(r, g, b, mode='top'):
    """
    按规范调整颜色：H不变
    - top模式（黑色文字）：S：7-15，B：94-97
    - bottom模式（白色文字）：S：40-50，B：35-45
    
    区间数值采样处理：
    - S/B：如果原始值小于下限，调整为下限；如果大于上限，调整为上限；否则保持不变
    
    返回: (r_new, g_new, b_new, h, s_adjusted, b_adjusted)
    """
    h, s, bv = rgb_to_hsb(r, g, b)

    if mode == 'bottom':
        # bottom模式：S：40-50，B：35-45（白色文字）
        s_adjusted = max(40.0, min(s, 50.0))
        b_adjusted = max(35.0, min(bv, 45.0))
    else:
        # top模式：S：7-15，B：94-97（黑色文字）
        s_adjusted = max(7.0, min(s, 15.0))
        b_adjusted = max(94.0, min(bv, 97.0))

    r_new, g_new, b_new = hsb_to_rgb(h, s_adjusted, b_adjusted)
    return r_new, g_new, b_new, h, s_adjusted, b_adjusted


def xise(image_url, output_file, width=None, height=None, overlay_alpha=0.6, mode='top'):
    """
    从图片URL吸色，将调整后的颜色以半透明蒙层叠加在原图上，保存为JPG

    Args:
        image_url: 输入图片URL
        output_file: 输出JPG文件路径
        width: 输出图片宽度（默认与原图一致）
        height: 输出图片高度（默认与原图一致）
        overlay_alpha: 蒙层透明度 0~1，越大蒙层越重（默认0.6）
        mode: 吸色模式，'top'（黑色文字，S：7-15，B：94-97）或 'bottom'（白色文字，S：40-50，B：35-45）

    Returns:
        dict: 包含原始色和调整后色的信息
    """
    print(f'正在下载图片: {image_url}')
    img = download_image(image_url)
    orig_width, orig_height = img.size
    print(f'图片尺寸: {img.size}')

    # 若未指定宽高，则与原图一致
    if width is None:
        width = orig_width
    if height is None:
        height = orig_height

    # 若输出尺寸与原图不同，先缩放原图
    if (width, height) != (orig_width, orig_height):
        img = img.resize((width, height), Image.LANCZOS)

    print('正在提取主色调...')
    r, g, b = get_dominant_color(img)
    h_orig, s_orig, bv_orig = rgb_to_hsb(r, g, b)
    hex_orig = f'#{r:02X}{g:02X}{b:02X}'
    print(f'原始主色调 RGB: ({r}, {g}, {b})  HEX: {hex_orig}')
    print(f'原始主色调 HSB: H={h_orig:.1f}°, S={s_orig:.1f}, B={bv_orig:.1f}')

    print(f'正在调整颜色（mode={mode}，H不变，S/B按规范调整）...')
    r_new, g_new, b_new, h_new, s_new, b_new_val = adjust_color_for_overlay(r, g, b, mode=mode)
    hex_new = f'#{r_new:02X}{g_new:02X}{b_new:02X}'
    print(f'调整后颜色 RGB: ({r_new}, {g_new}, {b_new})  HEX: {hex_new}')
    print(f'调整后颜色 HSB: H={h_new:.1f}°, S={s_new:.1f}, B={b_new_val:.1f}')

    # 将调整后的颜色以渐变蒙层叠加在原图上
    # top模式：上方 alpha=overlay_alpha，下方 alpha=0
    # bottom模式：下方 alpha=overlay_alpha，上方 alpha=0
    img_arr = np.array(img, dtype=float)
    overlay_arr = np.full_like(img_arr, [r_new, g_new, b_new], dtype=float)

    if mode == 'bottom':
        # bottom模式：从下往上渐变，底部 alpha=overlay_alpha -> 顶部 alpha=0
        alpha_grad = np.linspace(0.0, overlay_alpha, height).reshape(height, 1, 1)
        grad_desc = '底部 alpha={} -> 顶部 alpha=0'.format(overlay_alpha)
    else:
        # top模式：从上往下渐变，顶部 alpha=overlay_alpha -> 底部 alpha=0
        alpha_grad = np.linspace(overlay_alpha, 0.0, height).reshape(height, 1, 1)
        grad_desc = '顶部 alpha={} -> 底部 alpha=0'.format(overlay_alpha)

    blended_arr = img_arr * (1.0 - alpha_grad) + overlay_arr * alpha_grad
    blended_arr = np.clip(blended_arr, 0, 255).astype(np.uint8)

    out_img = Image.fromarray(blended_arr, 'RGB')
    out_img.save(output_file, 'JPEG', quality=95)
    print(f'\n已保存到: {output_file}（渐变蒙层：{grad_desc}）')

    result = {
        'original_rgb': (r, g, b),
        'original_hsb': (round(h_orig, 1), round(s_orig, 1), round(bv_orig, 1)),
        'original_hex': hex_orig,
        'adjusted_rgb': (r_new, g_new, b_new),
        'adjusted_hsb': (round(h_new, 1), round(s_new, 1), round(b_new_val, 1)),
        'adjusted_hex': hex_new,
        'output_file': output_file,
    }
    return result


def process_batch(input_jsonl, output_jsonl, url_field, overlay_alpha=0.6, tmp_dir='tmp', postfix='_topxise', mode='top'):
    """
    批量处理JSONL文件：对每条记录中指定字段的URL吸色，并上传OSS

    Args:
        input_jsonl:   输入JSONL文件路径
        output_jsonl:  输出JSONL文件路径
        url_field:     包含图片URL的字段名
        overlay_alpha: 蒙层透明度
        tmp_dir:       临时文件目录
        postfix:       输出字段后缀（默认'_topxise'）
        mode:          吸色模式，'top'或'bottom'
    """
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

        # 已处理的直接跳过
        if image_url in done_set:
            print(f'[{idx}/{total}] 已处理，跳过: {image_url}')
            skip_count += 1
            continue

        # 构造本地临时文件名：原文件名 + postfix.jpg
        parsed = urlparse(image_url)
        orig_name = os.path.basename(parsed.path)          # e.g. abc123.jpg
        stem, _ = os.path.splitext(orig_name)              # e.g. abc123
        local_file = os.path.join(tmp_dir, f'{stem}{postfix}.jpg')

        print(f'[{idx}/{total}] 处理: {image_url}')
        try:
            xise(image_url, local_file, overlay_alpha=overlay_alpha, mode=mode)
        except Exception as e:
            print(f'[{idx}/{total}] 吸色失败: {e}')
            print(traceback.format_exc())
            fail_count += 1
            continue

        # 上传到 OSS
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
    parser = argparse.ArgumentParser(
        description='图片吸色工具 - 提取主色调并调整为适合文字叠加的渐变蒙层背景色\n'
                    'top模式（黑色文字）：H不变，S：7-15，B：94-97\n'
                    'bottom模式（白色文字）：H不变，S：40-50，B：35-45'
    )
    subparsers = parser.add_subparsers(dest='mode', required=True)

    # ---- 单张模式 ----
    p_single = subparsers.add_parser('single', help='处理单张图片')
    p_single.add_argument('image_url', help='输入图片URL')
    p_single.add_argument('output_file', help='输出JPG文件路径，如 output.jpg')
    p_single.add_argument('--width', type=int, default=None, help='输出图片宽度，默认与原图一致')
    p_single.add_argument('--height', type=int, default=None, help='输出图片高度，默认与原图一致')
    p_single.add_argument('--alpha', type=float, default=0.6, help='蒙层透明度 0~1，越大蒙层越重（默认0.6）')
    p_single.add_argument('--xise-mode', choices=['top', 'bottom'], default='top', 
                          help='吸色模式：top（黑色文字，S：7-15，B：94-97）或 bottom（白色文字，S：40-50，B：35-45）')

    # ---- 批处理模式 ----
    p_batch = subparsers.add_parser('batch', help='批量处理JSONL文件并上传OSS')
    p_batch.add_argument('input_jsonl', help='输入JSONL文件路径')
    p_batch.add_argument('output_jsonl', help='输出JSONL文件路径')
    p_batch.add_argument('--url-field', required=True, help='包含图片URL的字段名，如 url 或 cover_url')
    p_batch.add_argument('--alpha', type=float, default=0.6, help='蒙层透明度 0~1（默认0.6）')
    p_batch.add_argument('--tmp-dir', default='tmp', help='临时文件目录（默认 tmp/）')
    p_batch.add_argument('--postfix', default='_topxise', help='输出字段后缀（默认 _topxise）')
    p_batch.add_argument('--xise-mode', choices=['top', 'bottom'], default='top',
                         help='吸色模式：top（黑色文字）或 bottom（白色文字）')

    args = parser.parse_args()

    if args.mode == 'single':
        result = xise(args.image_url, args.output_file, args.width, args.height, args.alpha, args.xise_mode)
        print('\n======= 吸色结果汇总 =======')
        print(f'原始色:  RGB{result["original_rgb"]}  HEX {result["original_hex"]}  HSB(H={result["original_hsb"][0]}°, S={result["original_hsb"][1]}, B={result["original_hsb"][2]})')
        print(f'调整色:  RGB{result["adjusted_rgb"]}  HEX {result["adjusted_hex"]}  HSB(H={result["adjusted_hsb"][0]}°, S={result["adjusted_hsb"][1]}, B={result["adjusted_hsb"][2]})')
        print(f'输出文件: {result["output_file"]}')

    elif args.mode == 'batch':
        process_batch(args.input_jsonl, args.output_jsonl, args.url_field, args.alpha, args.tmp_dir, args.postfix, args.xise_mode)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科普 + 妙题高招：style3 仅学名（从 学名·确认版 的《》内提取）+ url·确认版。

每行生成 PNG（压缩前）+ JPG（≤50K 压缩后），上传 OSS 并回写两列 URL。

用法：
  python3 run_kepu.py \\
      --csv "/Users/xiyunmeng/Downloads/科普+妙题高招线上内容汇总.csv" \\
      --out-dir output/kepu
"""
import argparse
import csv
import hashlib
import os
import re
import sys

import render_covers as rc

COL_NAME = "学名·确认版"
COL_SRC = "url·确认版"
COL_PNG = "封面压图压缩前url"
COL_JPG = "封面压图压缩后url"

BOOK_RE = re.compile(r"《(.+?)》")


def extract_title(raw):
    """取书名号内文字；无书名号则原样返回。"""
    raw = (raw or "").strip()
    m = BOOK_RE.search(raw)
    return m.group(1).strip() if m else raw


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out-dir", default="output/kepu")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    img_dir = os.path.join(args.out_dir, "covers")
    os.makedirs(img_dir, exist_ok=True)
    cache_dir = os.path.join(args.out_dir, "_bg_cache")

    with open(args.csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    idx = {n: i for i, n in enumerate(header)}
    for c in (COL_NAME, COL_SRC):
        if c not in idx:
            print(f"error: CSV 缺列 '{c}'", file=sys.stderr)
            sys.exit(1)
    for c in (COL_PNG, COL_JPG):
        if c not in idx:
            header.append(c)
            idx[c] = len(header) - 1

    url_to_urls = {}
    manifest = []
    count = ok = err = 0

    for n, row in enumerate(rows[1:], start=2):
        if len(row) <= idx[COL_SRC]:
            continue
        raw_name = row[idx[COL_NAME]].strip()
        src = row[idx[COL_SRC]].strip()
        if not raw_name or not src:
            continue
        title = extract_title(raw_name)
        if not title:
            continue
        if args.limit and count >= args.limit:
            break
        count += 1
        try:
            if src in url_to_urls:
                png_url, jpg_url = url_to_urls[src]
            else:
                bg = rc.fetch_bg(src, cache_dir)
                stem = hashlib.md5(src.encode()).hexdigest()
                png_path = os.path.join(img_dir, stem + ".png")
                jpg_path = os.path.join(img_dir, stem + ".jpg")
                img = rc.render(3, bg, title)
                rc.save(img, png_path)
                rc.save(img, jpg_path)
                png_url = rc.upload_to_oss(png_path)
                jpg_url = rc.upload_to_oss(jpg_path)
                url_to_urls[src] = (png_url, jpg_url)
            while len(row) < len(header):
                row.append("")
            row[idx[COL_PNG]] = png_url
            row[idx[COL_JPG]] = jpg_url
            manifest.append([raw_name, title, src, png_url, jpg_url])
            ok += 1
            if ok % 20 == 0:
                print(f"  ...完成 {ok} 行")
        except Exception as e:  # noqa: BLE001
            print(f"  [行{n}] 失败 {raw_name} -> {e}", file=sys.stderr)
            err += 1

    out_csv = os.path.join(args.out_dir, "科普妙题成品_with_urls.csv")
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows[1:])

    man = os.path.join(args.out_dir, "manifest.csv")
    with open(man, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["学名·确认版", "压图标题", "原图url", "压缩前url(png)", "压缩后url(jpg)"])
        w.writerows(manifest)

    print(f"完成 {ok} 行（失败 {err}），唯一图 {len(url_to_urls)}")
    print(f"回填CSV: {out_csv}")
    print(f"清单:   {man}")


if __name__ == "__main__":
    main()

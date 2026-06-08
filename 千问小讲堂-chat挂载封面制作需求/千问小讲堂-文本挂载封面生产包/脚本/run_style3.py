#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语文 style3 全量：学名确认版 + url确认版 → 封面。

每行生成两版并都上传 OSS：
  - PNG（未压缩，无损）  → 写回列『封面压图压缩前url』
  - JPG（压缩 ≤50K）     → 写回列『封面压图压缩后url』

用法：
  python3 run_style3.py \
      --csv "/Users/xiyunmeng/Downloads/语文类内容汇总.csv" \
      --out-dir output/style3 \
      [--limit N]   # 仅跑前 N 行（调试用）
输出：
  <out-dir>/<md5>.png / <md5>.jpg
  <out-dir>/语文成品_with_urls.csv   （原列 + 两列回填）
  <out-dir>/manifest.csv
"""
import argparse
import csv
import hashlib
import os
import sys

import render_covers as rc

COL_NAME = "学名确认版"
COL_SRC = "url确认版"
COL_PNG = "封面压图压缩前url"   # 未压缩
COL_JPG = "封面压图压缩后url"   # 压缩

# 内容表列名变体（中间点 · vs 无点）
COL_NAME_ALIASES = (COL_NAME, "学名·确认版")
COL_SRC_ALIASES = (COL_SRC, "url·确认版")


def resolve_col(header_idx, aliases, header, add_if_missing=False):
    for name in aliases:
        if name in header_idx:
            return name
    if add_if_missing:
        header.append(aliases[0])
        header_idx[aliases[0]] = len(header) - 1
        return aliases[0]
    return None


def md5(s):
    return hashlib.md5(s.encode()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out-dir", default="output/style3")
    ap.add_argument("--out-csv-name", default="", help="回填 CSV 文件名（默认 语文成品_with_urls.csv）")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    cache_dir = os.path.join(args.out_dir, "_bg_cache")

    with open(args.csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    idx = {name: i for i, name in enumerate(header)}
    name_col = resolve_col(idx, COL_NAME_ALIASES, header)
    src_col = resolve_col(idx, COL_SRC_ALIASES, header)
    if not name_col or not src_col:
        print(f"error: CSV 缺列学名/url 确认版 (现有 {header})", file=sys.stderr)
        sys.exit(1)
    png_col = resolve_col(idx, (COL_PNG,), header, add_if_missing=True)
    jpg_col = resolve_col(idx, (COL_JPG,), header, add_if_missing=True)

    # 同一 url 只生成/上传一次
    url_to_urls = {}            # src_url -> (png_url, jpg_url)
    manifest = []
    count = ok = err = 0

    for n, row in enumerate(rows[1:], start=2):
        if len(row) <= idx[src_col]:
            continue
        name = row[idx[name_col]].strip()
        src = row[idx[src_col]].strip()
        if not name or not src:
            continue
        if args.limit and count >= args.limit:
            break
        count += 1
        try:
            if src in url_to_urls:
                png_url, jpg_url = url_to_urls[src]
            else:
                bg = rc.fetch_bg(src, cache_dir)
                stem = md5(src)
                png_path = os.path.join(args.out_dir, stem + ".png")
                jpg_path = os.path.join(args.out_dir, stem + ".jpg")
                img = rc.render(3, bg, name)
                rc.save(img, png_path)   # 无损
                rc.save(img, jpg_path)   # 压缩 ≤50K
                png_url = rc.upload_to_oss(png_path)
                jpg_url = rc.upload_to_oss(jpg_path)
                url_to_urls[src] = (png_url, jpg_url)
            # 回填两列（按需扩展行长度）
            while len(row) < len(header):
                row.append("")
            row[idx[png_col]] = png_url
            row[idx[jpg_col]] = jpg_url
            title = rc.display_name_from_xueming(name)
            manifest.append([title, src, png_url, jpg_url])
            ok += 1
            if ok % 20 == 0:
                print(f"  ...完成 {ok} 行")
        except Exception as e:  # noqa: BLE001
            print(f"  [行{n}] 失败 {name} -> {e}", file=sys.stderr)
            err += 1

    out_name = args.out_csv_name or "语文成品_with_urls.csv"
    out_csv = os.path.join(args.out_dir, out_name)
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows[1:])

    man = os.path.join(args.out_dir, "manifest.csv")
    with open(man, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["学名", "原图url", "未压缩url(png)", "压缩url(jpg)"])
        w.writerows(manifest)

    print(f"完成 {ok} 行（失败 {err}），唯一图 {len(url_to_urls)}")
    print(f"回填CSV: {out_csv}")
    print(f"清单:   {man}")


if __name__ == "__main__":
    main()

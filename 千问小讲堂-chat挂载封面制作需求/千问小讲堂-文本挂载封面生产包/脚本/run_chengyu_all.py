#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成语故事 50 篇封面一体化：

- 设计老师已做好的 20 张成品（/Users/xiyunmeng/Desktop/寓言故事/*.png）→ 直接用
  （其中两个错名按真实成语修正：画龙点睛.png=塞翁失马、画龙点睛-1.png=惊弓之鸟）
- 其余 30 条 → 用 render_chengyu（学名 65W + 钩子 W 70%）按 url·确认版 自动生成

每条都产出两版并上传 OSS：
  - PNG（压缩前，无损/原成品）→ 写回列『封面压图压缩前url』
  - JPG（压缩后 ≤50K）         → 写回列『封面压图压缩后url』
输出：output/chengyu/成语成品_with_urls.csv + manifest.csv
"""
import argparse
import csv
import hashlib
import os
import sys

import render_covers as rc

DESIGNER_DIR = "/Users/xiyunmeng/Desktop/寓言故事"
# 错名修正：文件名(去.png) -> 真实成语
NAME_FIX = {
    "画龙点睛": "塞翁失马",
    "画龙点睛-1": "惊弓之鸟",
}
COL_NAME = "学名·确认版"
COL_HOOK = "钩子·确认版"
COL_SRC = "url·确认版"
COL_PNG = "封面压图压缩前url"
COL_JPG = "封面压图压缩后url"


def designer_map():
    """真实成语 -> 设计成品 PNG 路径。"""
    out = {}
    for fn in os.listdir(DESIGNER_DIR):
        if not fn.lower().endswith(".png"):
            continue
        stem = os.path.splitext(fn)[0]
        name = NAME_FIX.get(stem, stem)
        out[name] = os.path.join(DESIGNER_DIR, fn)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out-dir", default="output/chengyu")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    cache_dir = os.path.join(args.out_dir, "_bg_cache")
    img_dir = os.path.join(args.out_dir, "covers")
    os.makedirs(img_dir, exist_ok=True)

    with open(args.csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    idx = {n: i for i, n in enumerate(header)}
    for c in (COL_NAME, COL_HOOK, COL_SRC):
        if c not in idx:
            print(f"error: CSV 缺列 '{c}'", file=sys.stderr)
            sys.exit(1)
    # 新增两列（若不存在）
    for c in (COL_PNG, COL_JPG):
        if c not in idx:
            header.append(c)
            idx[c] = len(header) - 1

    dmap = designer_map()
    print(f"设计成品 {len(dmap)} 张")

    manifest = []
    count = ok = err = 0
    for n, row in enumerate(rows[1:], start=2):
        if len(row) <= idx[COL_SRC]:
            continue
        name = row[idx[COL_NAME]].strip()
        if not name:
            continue
        if args.limit and count >= args.limit:
            break
        count += 1
        try:
            stem = hashlib.md5(name.encode()).hexdigest()
            png_path = os.path.join(img_dir, stem + ".png")
            jpg_path = os.path.join(img_dir, stem + ".jpg")
            if name in dmap:                       # 用设计成品
                src_kind = "designer"
                img = rc.Image.open(dmap[name]).convert("RGBA")
            else:                                   # 自动生成
                src_kind = "generated"
                hook = row[idx[COL_HOOK]].strip()
                bg = rc.fetch_bg(row[idx[COL_SRC]].strip(), cache_dir)
                img = rc.render_chengyu(bg, name, hook)
            rc.save(img, png_path)                  # 压缩前（无损 PNG）
            rc.save(img, jpg_path)                  # 压缩后（≤50K JPG）
            png_url = rc.upload_to_oss(png_path)
            jpg_url = rc.upload_to_oss(jpg_path)
            while len(row) < len(header):
                row.append("")
            row[idx[COL_PNG]] = png_url
            row[idx[COL_JPG]] = jpg_url
            manifest.append([name, src_kind, png_url, jpg_url])
            ok += 1
            if ok % 10 == 0:
                print(f"  ...完成 {ok}")
        except Exception as e:  # noqa: BLE001
            print(f"  [行{n}] 失败 {name} -> {e}", file=sys.stderr)
            err += 1

    out_csv = os.path.join(args.out_dir, "成语成品_with_urls.csv")
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows[1:])
    man = os.path.join(args.out_dir, "manifest.csv")
    with open(man, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["学名", "来源", "压缩前url(png)", "压缩后url(jpg)"])
        w.writerows(manifest)

    print(f"完成 {ok}（失败 {err}）；设计成品+自动生成已合并")
    print(f"回填CSV: {out_csv}")
    print(f"清单:   {man}")


if __name__ == "__main__":
    main()

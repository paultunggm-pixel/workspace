#!/usr/bin/env python3
"""生成「花月佳期」抖音店铺头像 — 500×500 PNG"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ── 画布 ──────────────────────────────────────────
SIZE = 500
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ── 配色 ──────────────────────────────────────────
BG_TOP = (255, 225, 235)       # 浅粉
BG_BOTTOM = (235, 200, 225)    # 粉紫
TEAPOT_BODY = (210, 155, 175)  # 紫砂壶体 — 粉紫调
TEAPOT_HIGHLIGHT = (235, 200, 215)
TEAPOT_SHADOW = (170, 120, 145)
TEAPOT_LID = (195, 140, 160)
TEAPOT_SPOUT = (200, 145, 165)
TEAPOT_HANDLE = (200, 148, 168)
KNOB = (180, 125, 150)
GOLD_ACCENT = (245, 210, 170)  # 暖金 — 壶钮、装饰线
TEXT_COLOR = (140, 65, 85)     # 深玫红
WHITE_SOFT = (255, 250, 252)
MOON = (255, 245, 240)
FLOWER_PETAL = (255, 190, 200)
FLOWER_PETAL2 = (255, 170, 185)
FLOWER_CENTER = (255, 230, 160)
LEAF = (185, 160, 175)

# ── 背景渐变 ───────────────────────────────────────
for y in range(SIZE):
    t = y / SIZE
    r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
    draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

# ── 柔光光晕 ──────────────────────────────────────
center_x, center_y = SIZE // 2, SIZE // 2
for r in range(200, 50, -1):
    alpha = int(10 * (1 - r / 200))
    if alpha > 0:
        draw.ellipse(
            [center_x - r, center_y - r + 20, center_x + r, center_y + r + 20],
            fill=(255, 240, 245, alpha),
        )

# ── 装饰月亮（右上背景） ─────────────────────────
moon_cx, moon_cy = 395, 95
moon_r = 38
draw.ellipse(
    [moon_cx - moon_r, moon_cy - moon_r, moon_cx + moon_r, moon_cy + moon_r],
    fill=MOON + (220,),
)
# 月晕
for mr in range(moon_r + 8, moon_r + 25, 3):
    a = int(30 * (1 - (mr - moon_r) / 25))
    draw.ellipse([moon_cx - mr, moon_cy - mr, moon_cx + mr, moon_cy + mr],
                 fill=(255, 245, 240, a))

# ── 小星星 / 光点 ──────────────────────────────────
stars = [(80, 70), (430, 55), (60, 150), (450, 170), (120, 380), (380, 390)]
for sx, sy in stars:
    sr = 3
    for i in range(3):
        a = int(80 - i * 25)
        draw.ellipse([sx - sr - i * 2, sy - sr - i * 2, sx + sr + i * 2, sy + sr + i * 2],
                     fill=(255, 245, 250, a))

# ── 核心：西施紫砂壶 ──────────────────────────────
# 壶身 — 扁圆，西施壶特点是矮胖可爱
body_cx, body_cy = 250, 260
body_rx, body_ry = 90, 72
# 壶身阴影（底部加深）
for i in range(3):
    offset = 2 + i * 2
    draw.ellipse(
        [body_cx - body_rx, body_cy - body_ry + offset * 2,
         body_cx + body_rx, body_cy + body_ry + offset * 2],
        fill=(170, 120, 145, 8),
    )
# 壶身主体
draw.ellipse(
    [body_cx - body_rx, body_cy - body_ry, body_cx + body_rx, body_cy + body_ry],
    fill=TEAPOT_BODY + (255,),
    outline=(160, 110, 135, 200),
    width=2,
)
# 壶身高光 — 左上弧形
draw.ellipse(
    [body_cx - 50, body_cy - 40, body_cx + 20, body_cy + 30],
    fill=TEAPOT_HIGHLIGHT + (120,),
)

# 壶口线（壶身与盖子的分界）
line_y = body_cy - body_ry + 18
draw.arc(
    [body_cx - 60, line_y - 4, body_cx + 60, line_y + 8],
    start=0, end=180,
    fill=(155, 105, 130, 200), width=2,
)

# 壶盖 — 扁弧
lid_w, lid_h = 68, 20
lid_y = line_y - lid_h + 3
draw.ellipse(
    [body_cx - lid_w, lid_y, body_cx + lid_w, lid_y + lid_h * 2],
    fill=TEAPOT_LID + (255,),
    outline=(155, 105, 130, 200), width=2,
)
# 壶盖高光
draw.ellipse(
    [body_cx - 25, lid_y + 4, body_cx + 5, lid_y + lid_h],
    fill=TEAPOT_HIGHLIGHT + (130,),
)

# 壶钮（盖上的小圆球）
knob_r = 12
knob_y = lid_y - 6
draw.ellipse(
    [body_cx - knob_r, knob_y - knob_r, body_cx + knob_r, knob_y + knob_r],
    fill=KNOB + (255,),
    outline=(145, 95, 120, 200), width=1,
)
# 壶钮高光
draw.ellipse(
    [body_cx - 4, knob_y - 6, body_cx + 3, knob_y + 2],
    fill=(230, 180, 195, 180),
)

# 壶嘴（短，西施壶特征）— 右侧
spout_start_x, spout_start_y = body_cx + 75, body_cy - 10
spout_points = [
    (spout_start_x, spout_start_y - 10),
    (spout_start_x + 30, spout_start_y - 22),
    (spout_start_x + 35, spout_start_y + 5),
    (spout_start_x, spout_start_y + 10),
]
draw.polygon(spout_points, fill=TEAPOT_SPOUT + (255,),
             outline=(155, 105, 130, 200), width=1)
# 壶嘴高光
spout_hl = [
    (spout_start_x + 4, spout_start_y - 8),
    (spout_start_x + 22, spout_start_y - 16),
    (spout_start_x + 24, spout_start_y - 2),
    (spout_start_x + 4, spout_start_y + 4),
]
draw.polygon(spout_hl, fill=TEAPOT_HIGHLIGHT + (100,))
# 壶嘴口
draw.ellipse(
    [spout_start_x + 27, spout_start_y - 24,
     spout_start_x + 39, spout_start_y + 7],
    fill=(130, 95, 115, 255),
)

# 壶把 — 左侧弧形
handle_points = [
    (body_cx - 85, body_cy - 35),
    (body_cx - 108, body_cy - 20),
    (body_cx - 112, body_cy + 15),
    (body_cx - 95, body_cy + 35),
    (body_cx - 85, body_cy + 25),
    (body_cx - 98, body_cy + 5),
    (body_cx - 94, body_cy - 20),
    (body_cx - 80, body_cy - 30),
]
draw.polygon(handle_points, fill=TEAPOT_HANDLE + (255,),
             outline=(155, 105, 130, 200), width=1)
# 壶把高光
handle_hl = [
    (body_cx - 88, body_cy - 30),
    (body_cx - 100, body_cy - 18),
    (body_cx - 102, body_cy - 5),
    (body_cx - 95, body_cy + 8),
    (body_cx - 90, body_cy + 5),
    (body_cx - 96, body_cy - 5),
    (body_cx - 94, body_cy - 18),
    (body_cx - 86, body_cy - 25),
]
draw.polygon(handle_hl, fill=TEAPOT_HIGHLIGHT + (100,))

# ── 壶身泥绘装饰花 — 中央可爱小花 ─────────────────
flower_cx, flower_cy = body_cx, body_cy + 5
for angle in range(0, 360, 72):
    rad = math.radians(angle)
    px = flower_cx + math.cos(rad) * 18
    py = flower_cy + math.sin(rad) * 18
    draw.ellipse([px - 9, py - 13, px + 9, py + 13],
                 fill=FLOWER_PETAL2 + (200,))
# 花心
draw.ellipse([flower_cx - 6, flower_cy - 6, flower_cx + 6, flower_cy + 6],
             fill=FLOWER_CENTER + (220,))

# 壶身侧面小叶子
for dx, dy, rot in [(-35, 8, -30), (30, -15, 150)]:
    rad = math.radians(rot)
    lx = body_cx + dx
    ly = body_cy + dy
    leaf_pts = [
        (lx, ly - 7),
        (lx + 6, ly - 10),
        (lx + 10, ly + 1),
        (lx + 2, ly + 6),
    ]
    draw.polygon(leaf_pts, fill=LEAF + (160,))

# ── 环绕装饰小花 ───────────────────────────────────
small_flowers = [
    (310, 165), (350, 240), (330, 330),
    (150, 170), (120, 250), (175, 340),
    (220, 155), (260, 345),
]
for fx, fy in small_flowers:
    for a in range(0, 360, 72):
        r = math.radians(a)
        px = fx + math.cos(r) * 7
        py = fy + math.sin(r) * 7
        draw.ellipse([px - 4, py - 6, px + 4, py + 6],
                     fill=FLOWER_PETAL + (150,))
    draw.ellipse([fx - 3, fy - 3, fx + 3, fy + 3],
                 fill=FLOWER_CENTER + (200,))

# ── 底部飘落花瓣 ───────────────────────────────────
petals = [
    (80, 430, 15), (130, 450, -20), (350, 445, 10),
    (400, 430, -10), (420, 460, 25), (60, 410, -5),
    (370, 420, -30), (110, 415, 20),
]
for px, py, angle in petals:
    rad = math.radians(angle)
    l = 8
    w = 5
    # 简单椭圆花瓣
    draw.ellipse([px - l, py - w, px + l, py + w],
                 fill=FLOWER_PETAL + (130,))

# ── 文字：花月佳期 ─────────────────────────────────
# 使用系统自带字体
font_paths = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]
font = None
font_size = 40
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except Exception:
            continue

if font is None:
    font = ImageFont.load_default()

# 文本背景遮罩 — 让文字更清晰
text = "花月佳期"
# 计算文字bbox
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
text_x = (SIZE - tw) // 2
text_y = 430

# 半透明文字底衬
padding = 12
draw.rounded_rectangle(
    [text_x - padding, text_y - padding - 4,
     text_x + tw + padding, text_y + th + padding + 2],
    radius=20,
    fill=(255, 240, 245, 200),
)

# 主文字
draw.text((text_x, text_y), text, fill=TEXT_COLOR + (255,), font=font)

# 标题下一行小英文装饰
sub_font = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            sub_font = ImageFont.truetype(fp, 14)
            break
        except Exception:
            continue
if sub_font is None:
    sub_font = ImageFont.load_default()

sub_text = "Flower Moon · Best Time"
sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
sub_tw = sub_bbox[2] - sub_bbox[0]
sub_text_x = (SIZE - sub_tw) // 2
sub_text_y = text_y + th + 3
draw.text((sub_text_x, sub_text_y), sub_text,
          fill=(160, 100, 120, 180), font=sub_font)

# ── 四角装饰（圆形点阵） ──────────────────────────
corner_r = 3
for cx, cy in [(35, 35), (465, 35), (35, 465), (465, 465)]:
    draw.ellipse([cx - corner_r, cy - corner_r, cx + corner_r, cy + corner_r],
                 fill=FLOWER_PETAL + (180,))
    # 卫星点
    for angle in range(0, 360, 90):
        rad_r = math.radians(angle)
        sx = cx + math.cos(rad_r) * 10
        sy = cy + math.sin(rad_r) * 10
        draw.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5],
                     fill=FLOWER_PETAL + (100,))

# ── 外边框细线 ─────────────────────────────────────
border_pad = 12
radius = 6
# Top
draw.rectangle([border_pad + radius, border_pad, SIZE - border_pad - radius, border_pad + 1],
               fill=FLOWER_PETAL + (100,))
# Bottom
draw.rectangle([border_pad + radius, SIZE - border_pad - 1, SIZE - border_pad - radius, SIZE - border_pad],
               fill=FLOWER_PETAL + (100,))
# Left
draw.rectangle([border_pad, border_pad + radius, border_pad + 1, SIZE - border_pad - radius],
               fill=FLOWER_PETAL + (100,))
# Right
draw.rectangle([SIZE - border_pad - 1, border_pad + radius, SIZE - border_pad, SIZE - border_pad - radius],
               fill=FLOWER_PETAL + (100,))

# ── 保存 ──────────────────────────────────────────
output_path = "/Users/d.j.f/Documents/Claude/huayuejiaqi_avatar.png"
# 转为 RGB 保存 PNG
img_rgb = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
img_rgb.paste(img, mask=img.split()[3])
img_rgb.save(output_path, "PNG")
print(f"✅ 头像已保存: {output_path}")
print(f"   尺寸: {SIZE}×{SIZE} px")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初中数学 · 纯生图指令（4-case A/B/C/D），无钩子/学名/徽标。

基于小高 Swiss 2.5D 构图，背景改为低饱和浅色纯色。
"""
from __future__ import annotations

import hashlib
import re

from cover_lib import pick_palette

# 浅色纯色底 + 中等饱和点缀（对比小高 SWISS_PAIRS 的高饱和底）
JUNIOR_SWISS_PAIRS = [
    (("雾蓝", "#E3F2FD"), ("珊瑚橙", "#FF7043")),
    (("薄荷绿", "#E8F5E9"), ("靛青", "#5C6BC0")),
    (("浅杏", "#FFF3E0"), ("莓紫", "#AB47BC")),
    (("藕荷", "#F3E5F5"), ("松绿", "#43A047")),
    (("云灰蓝", "#ECEFF1"), ("天蓝", "#1E88E5")),
    (("奶油黄", "#FFFDE7"), ("橘红", "#FB8C00")),
    (("浅粉", "#FCE4EC"), ("深青", "#00897B")),
    (("淡青", "#E0F7FA"), ("品红", "#D81B60")),
]

JUNIOR_HEAD = (
    "3:4 vertical illustration, isometric 2.5D perspective, Swiss International Style, "
    "bold uniform black outlines on the subject only, flat color blocks no gradient, "
    "hard-edged flat shadows, clean minimal flat illustration matte paper aesthetic. "
    "The entire canvas is filled completely with soft pastel solid {bg_name} {bg_hex} "
    "low-saturation light tone reaching all four edges with no border no frame no margin "
    "no white edge no drop shadow. "
    "The upper 65% of the canvas is completely empty pure pastel {bg_name} "
    "with absolutely nothing in it not even a thin line or rope or cable or pole. "
    "The left 40% of the canvas is also completely empty. "
    "All illustrated elements are tightly compressed into only the bottom-right corner "
    "occupying no more than 35% of the canvas height and 60% of the canvas width. "
)

JUNIOR_TAIL_VISUAL = (
    "Light grey #F0F0F0 as primary subject color, "
    "one accent color {accent_hex} highlighting the activated elements only, "
    "oversized stylized tool intervening from outside the frame, "
    "captured single action moment, only the touched part transforms into accent color, "
    "maximum 4 core elements in scene. "
    "No inner frame no border no box around the subject, "
    "no inner rectangular border no thin black line surrounding the illustrated elements, "
    "no diagonal lines crossing the canvas as decoration, no decorative lines in the background. "
    "NO vertical cable NO rope NO pole NO connecting rod attached. "
)

JUNIOR_TAIL_TEXT = (
    "Absolutely no text no typography no letters no words no numbers anywhere in the image. "
    "No title area no hook no badge no logo no watermark. "
    "Pure illustration only for a math lesson background."
)

# 4-case 差异：工具 / 光照语气轮转
VARIANT_TOOLS = ["透明三角尺", "圆规", "量角器", "直尺"]
VARIANT_MOODS = [
    "cool morning clarity",
    "warm afternoon study light",
    "neutral classroom daylight",
    "soft overcast even light",
]
CASE_LABELS = ["A", "B", "C", "D"]
NUM_CASES = 4


def map_knowledge_kind(raw: str) -> str:
    s = (raw or "").replace("\u2f74", "方").strip()  # 判定⽅法类 → 判定方法类
    if "概念" in s:
        return "concept"
    if "性质" in s or "定理" in s:
        return "property"
    if "判定" in s:
        return "judge"
    if "方法" in s or "步骤" in s:
        return "method"
    if "公式" in s:
        return "formula"
    if "运算" in s:
        return "compute"
    return "concept"


def _pick_main_keyword(keywords: str, title: str) -> str:
    k = (keywords or "").strip()
    if k:
        parts = re.split(r"[、,，/]", k)
        return parts[0].strip() or title
    return (title or "数学概念")[:12]


def build_junior_scene(row: dict, variant_idx: int = 0) -> dict:
    """根据底表行生成 Swiss 画面四元组。row 字段：title, keywords, explain, kind, chapter。"""
    title = (row.get("title") or row.get("course") or "").strip()
    keywords = row.get("keywords") or ""
    explain = row.get("explain") or ""
    kind = row.get("kind") or map_knowledge_kind(row.get("knowledge_type", ""))
    main = _pick_main_keyword(keywords, title)
    tool = VARIANT_TOOLS[variant_idx % len(VARIANT_TOOLS)]
    text_blob = f"{title} {keywords} {explain}"

    # —— 几何：相交线 / 角 ——
    if any(x in text_blob for x in ("对顶角", "邻补角", "相交线")):
        subject = (
            "画面右下角灰白色2.5D两条直线呈X型相交（粗黑轮廓），"
            "交点处形成四个角楔区，其中一对对顶角位置清晰可辨"
        )
        action = f"一把{tool}从画面右边缘低角度伸入，指向其中一对对顶角位置作识别定格"
        activation = "被工具指向的一对对顶角楔区从灰白色变为点缀色，邻补角仍为灰白色"
    elif "垂线" in text_blob or "垂直" in text_blob:
        subject = "画面右下角灰白色2.5D一条水平直线，另有一条直线与之成90度相交，交点处带小型直角符号几何块（纯形状非文字）"
        action = f"{tool}从右侧水平伸入，正在落点处确认直角关系"
        activation = "直角符号块与垂线相交附近线段变为点缀色，其余保持灰白色"
    elif "垂线段" in text_blob or "点到直线" in text_blob:
        subject = (
            "画面右下角灰白色2.5D一条长水平直线，直线上方一点，"
            "多条斜线段连到直线上，其中一条为垂直落点的垂线段（最短）"
        )
        action = "一把亮色直尺从右下伸入，用边缘对齐那条垂直的短垂线段"
        activation = "垂线段整条变为点缀色，其余斜线段保持灰白色"
    elif "同位角" in text_blob:
        subject = (
            "画面右下角灰白色2.5D两条平行横线被第三条斜线所截，"
            "形成F型同位角位置的一对角楔清晰可辨"
        )
        action = f"{tool}从右侧伸入，指向F型同一侧的一对同位角"
        activation = "这一对同位角楔区变为点缀色，其余角保持灰白色"
    elif any(x in text_blob for x in ("内错角", "Z型")):
        subject = "画面右下角灰白色2.5D两平行线被斜线所截，Z型内错角位置的一对角楔突出"
        action = f"{tool}指向Z型内错角对"
        activation = "内错角对变为点缀色"
    elif "同旁内角" in text_blob or "U型" in text_blob:
        subject = "画面右下角灰白色2.5D两平行线被斜线所截，U型同旁内角位置突出"
        action = f"{tool}指向U型同旁内角区域"
        activation = "同旁内角区域变为点缀色"
    elif any(x in text_blob for x in ("平行线", "平行")) and "判定" in text_blob:
        subject = "画面右下角灰白色2.5D两平行线+截线，一组可用于判定的角关系被强调"
        action = f"{tool}在截线与平行线之间做比对定格"
        activation = "用于判定的那组角变为点缀色"
    elif "平移" in text_blob:
        subject = (
            "画面右下角灰白色2.5D一个简单多边形与其平移后的虚线轮廓副本，"
            "对应顶点间有平行等长的箭头连线（纯几何箭头非文字）"
        )
        action = "亮色推板从右侧推挤多边形向箭头方向移动定格"
        activation = "正在移动的多边形变为点缀色，原位置轮廓保持灰白色"
    elif any(x in text_blob for x in ("平方根", "算术平方根", "开平方")):
        subject = "画面右下角灰白色2.5D正方形面积块被拆成边长方块阵列，体现面积与边长对应"
        action = "亮色直角折尺从右侧对齐正方形一边"
        activation = "被测量的一边及相邻角区变为点缀色"
    elif "立方根" in text_blob:
        subject = "画面右下角灰白色2.5D立方体体积块，一侧被切出分层薄片暗示体积分解"
        action = "亮色刀具从右侧切入立方体一角"
        activation = "被切分薄片层变为点缀色"
    elif kind == "formula":
        subject = f'画面右下角灰白色2.5D与"{main}"相关的公式结构几何化（括号、等号、方块阵列，均无字符）'
        action = f"{tool}从右侧伸入调整公式结构中的一段"
        activation = "被调整的一段结构变为点缀色"
    elif kind == "compute":
        subject = f'画面右下角灰白色2.5D运算流水线（与"{main}"相关的方块与运算符号几何形）'
        action = f"{tool}触发其中一步运算定格"
        activation = "当前运算步变为点缀色"
    else:
        subject = (
            f'画面右下角灰白色2.5D将"{main}"抽象为简洁几何主体（与"{title}"核心概念一致），'
            "轴测视角从左下向右上紧凑排列"
        )
        action = f"一把{tool}从画面右边缘水平伸入，对主体执行与概念相关的单一动作定格"
        activation = "被作用的部分从灰白色变为点缀色，其余保持灰白色"

    return {
        "math_subject": subject,
        "tool": action.split("，")[0] if "，" in action else action,
        "action": action,
        "activation": activation,
        "mood": VARIANT_MOODS[variant_idx % len(VARIANT_MOODS)],
    }


def render_junior_swiss(case: dict) -> str:
    head = JUNIOR_HEAD.format(bg_name=case["bg_name"], bg_hex=case["bg_hex"])
    body = (
        f"{case['math_subject']}。{case['action']}。{case['activation']}。"
        f"Lighting mood: {case.get('mood', 'neutral daylight')}. "
    )
    visual = JUNIOR_TAIL_VISUAL.format(accent_hex=case["accent_hex"])
    return head + body + visual + JUNIOR_TAIL_TEXT


def gen_image_prompts(row: dict, n: int = NUM_CASES) -> list[dict]:
    """产出 n 条生图指令（默认 4 case），无钩子/标签/学名。"""
    seed = f"{row.get('grade', '')}|{row.get('title', '')}|{row.get('keywords', '')}"
    picks = pick_palette(seed, JUNIOR_SWISS_PAIRS, n=n)
    out = []
    for i in range(n):
        bg, accent = picks[i]
        visual = build_junior_scene(row, variant_idx=i)
        case = {
            "bg_name": bg[0],
            "bg_hex": bg[1],
            "accent_name": accent[0],
            "accent_hex": accent[1],
            **visual,
        }
        label = CASE_LABELS[i] if i < len(CASE_LABELS) else chr(ord("A") + i)
        out.append(
            {
                "case": label,
                "bg_name": bg[0],
                "bg_hex": bg[1],
                "accent_name": accent[0],
                "accent_hex": accent[1],
                "prompt": render_junior_swiss(case),
            }
        )
    return out


def gen_three_image_prompts(row: dict) -> list[dict]:
    return gen_image_prompts(row, n=3)


def gen_four_image_prompts(row: dict) -> list[dict]:
    return gen_image_prompts(row, n=4)


def row_from_csv(d: dict) -> dict:
    return {
        "title": d.get("课文标题", ""),
        "keywords": d.get("知识点关键词", ""),
        "explain": d.get("知识点说明", ""),
        "knowledge_type": d.get("知识点类型", ""),
        "kind": map_knowledge_kind(d.get("知识点类型", "")),
        "grade": d.get("学段", ""),
        "chapter": d.get("小章节名称", ""),
        "section": d.get("教材节数", ""),
        "guid": d.get("GUID", ""),
    }

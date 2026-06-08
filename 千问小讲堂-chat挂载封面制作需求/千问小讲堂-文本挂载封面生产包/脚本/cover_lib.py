#!/usr/bin/env python3
"""封面文案 & 生图指令工具库——多 case 版本。

公共组件：
- 模板字符串（PIXAR / SWISS）
- 配色池（低龄数学 9 色 / 高年数 8 对）
- 标签关键词池
- 性格池 / 工具池
- 渲染函数：render_prompt(case) → 完整中文生图指令
- 钩子三公式自动生成 + 学名压缩 + 配色轮转辅助
"""
from copy import deepcopy
import hashlib
import re

# ============================================================
# 模板
# ============================================================
PIXAR_TAIL = (
    "one dominant hero character towering over smaller companions, "
    "hero character is 2-3x larger than sidekicks, "
    "subsurface scattering silicone toy texture, SSS skin-like translucency, "
    "soft glossy surface, wide soft diffuse highlight, "
    "extremely light shadow no dead black, three-point studio lighting, "
    "Pixar Illumination Entertainment animation quality, "
    "each character unique facial expression and personality, "
    "dynamic pose with weight shift, rosy cheeks, "
    "bright muted solid color background, "
    "open composition visual weight bottom-right, upper half naturally empty, "
    "total maximum 5 characters in scene, harmonious premium toy color palette, "
    "3-4颗金黄色四角立体星星紧邻主角周围少量彩色圆点装饰不超过角色群最高点"
)

PIXAR_PREAMBLE = (
    "3:4竖版高分辨率，明亮{bg_name}纯色背景({bg_hex})，"
    "开放式构图所有角色自然聚集在画面右下角区域，"
    "角色群最高点不超过画面整体高度的40%，"
    "上半部完全空白无任何元素。"
)

SWISS_HEAD = (
    "3:4 vertical illustration, isometric 2.5D perspective, Swiss International Style, "
    "bold uniform black outlines on the subject only, flat color blocks no gradient, "
    "hard-edged flat shadows, clean minimal flat illustration matte paper aesthetic. "
    "The entire canvas is filled completely with solid {bg_name} {bg_hex} "
    "reaching all four edges with no border no frame no margin no white edge no drop shadow. "
    "The upper 65% of the canvas is completely empty pure solid {bg_name} "
    "with absolutely nothing in it not even a thin line or rope or cable or pole. "
    "The left 40% of the canvas is also completely empty. "
    "All illustrated elements are tightly compressed into only the bottom-right corner "
    "occupying no more than 35% of the canvas height and 60% of the canvas width. "
)

SWISS_TAIL_VISUAL = (
    "Light grey #F0F0F0 as primary subject color, "
    "one accent color {accent_hex} highlighting the activated elements only, "
    "oversized stylized tool intervening from outside the frame, "
    "captured single action moment, only the touched part transforms into accent color, "
    "maximum 4 core elements in scene. "
    "No inner frame no border no box around the subject, "
    "no inner rectangular border no thin black line surrounding the illustrated elements, "
    "no diagonal lines crossing the canvas, no decorative lines in the background. "
    "NO vertical cable NO rope NO pole NO connecting rod attached. "
)

SWISS_TAIL_TEXT_DEFAULT = (
    "Absolutely no text no typography no letters no words no numbers anywhere in the image."
)


def swiss_tail_text_with_symbol(symbol_desc):
    return (
        "Absolutely no text no typography no letters no words anywhere in the image, "
        f"the only allowed symbol is {symbol_desc} "
        "treated as a pure geometric shape not typography."
    )


# ============================================================
# 配色池
# ============================================================
PIXAR_PALETTE = [
    ('暖红', '#F03C2D'),
    ('暖橙', '#ED7124'),
    ('南瓜橙', '#FBA726'),
    ('暖黄', '#F2B524'),
    ('草叶绿', '#7EBF30'),
    ('天空蓝', '#26B7F8'),
    ('靛蓝', '#228AE5'),
    ('葡萄紫', '#713FF2'),
    ('玫红', '#DD3F79'),
]

SWISS_PAIRS = [
    (('猩红', '#FF3B30'), ('深蓝', '#007AFF')),
    (('亮橙', '#FF9500'), ('深蓝', '#007AFF')),
    (('暖黄', '#FFCC00'), ('洋红', '#FF2D55')),
    (('森林绿', '#34C759'), ('亮橙', '#FF9500')),
    (('青色', '#32ADE6'), ('洋红', '#FF2D55')),
    (('宝蓝', '#007AFF'), ('亮黄', '#FFD600')),
    (('深紫', '#5856D6'), ('青绿', '#32ADE6')),
    (('玫红', '#FF2D55'), ('亮黄', '#FFD600')),
]


def pick_palette(seed_str, palette, n=3):
    """根据 seed_str (e.g. 课程名+学科) 决定从配色池选哪 n 个，
    避免相邻课程撞色，但同一课程的 3 个 case 内部各不相同。"""
    h = int(hashlib.md5(seed_str.encode('utf-8')).hexdigest(), 16)
    start = h % len(palette)
    picks = []
    step = max(1, len(palette) // n)
    for i in range(n):
        picks.append(palette[(start + i * step) % len(palette)])
    return picks


# ============================================================
# 标签关键词池
# ============================================================
PIXAR_TAG_KEYWORDS = {
    'concept': ['数学启蒙', '认知启蒙'],          # 概念课
    'practice': ['近期要学', '超好玩'],            # 应用 / 习题
    'general': ['数学启蒙', '近期要学', '超好玩'],
}

SWISS_TAG_KEYWORDS = {
    '数学·高年级': ['概念透视', '思维进阶', '高频考点', '应试核心', '破解技巧', '中考必会'],
    '妙题高招': ['冷知识揭秘', '字源揭秘', '巧算思维', '历史趣闻', '常识纠错'],
    '科普': ['人体奥秘', '生活物理', '自然奥秘', '生命科学', '物质探索'],
    'AI训练营': ['课程要点', '工具速通', '实战秘诀'],
}


def pick_tag_keywords(seed_str, pool, n=3):
    """根据 seed_str 从关键词池里挑 n 个不同关键词；池子小于 n 时允许复用。"""
    h = int(hashlib.md5(seed_str.encode('utf-8')).hexdigest(), 16)
    if len(pool) <= n:
        return pool[:n] + [pool[-1]] * (n - len(pool))
    start = h % len(pool)
    return [pool[(start + i) % len(pool)] for i in range(n)]


# ============================================================
# 性格池 / 工具池
# ============================================================
PERSONALITIES = [
    '傲娇自信', '慌张好奇', '温柔害羞', '兴奋夸张',
    '疑惑皱眉', '得意洋洋', '惊讶瞪眼', '认真专注',
]

ANIMAL_COMPANIONS = [
    ('小兔子', '粉红色'), ('小狐狸', '橙色'), ('小熊', '棕色'),
    ('小企鹅', '黑白色'), ('小松鼠', '橙黄色'), ('小猫咪', '橘色'),
    ('小鸭子', '亮黄色'), ('小鸡', '柠檬黄色'), ('小猪', '粉色'),
    ('小老鼠', '灰色'), ('小恐龙', '草绿色'), ('小章鱼', '紫色'),
]


# ============================================================
# 渲染函数
# ============================================================
def render_pixar(case):
    """低龄数学 Pixar 模板。case dict 字段：
    bg_name, bg_hex,
    hero, companion1, companion2, companion3, drama, moment
    """
    preamble = PIXAR_PREAMBLE.format(bg_name=case['bg_name'], bg_hex=case['bg_hex'])
    middle = (
        case['hero'] + '。'
        + case['companion1'] + '；'
        + case['companion2'] + '；'
        + case['companion3'] + '。'
        + '戏剧张力：' + case['drama'] + '；'
        + '动态瞬间：' + case['moment'] + '。'
    )
    return preamble + middle + PIXAR_TAIL


def render_swiss(case):
    """高年数 Swiss 模板。case dict 字段：
    bg_name, bg_hex, accent_hex,
    math_subject, tool, action, activation, symbol_exception?
    """
    head = SWISS_HEAD.format(bg_name=case['bg_name'], bg_hex=case['bg_hex'])
    body = (case['math_subject'] + '. '
            + case['tool'] + '. '
            + case['action'] + '. '
            + case['activation'] + '. ')
    visual = SWISS_TAIL_VISUAL.format(accent_hex=case['accent_hex'])
    if case.get('symbol_exception'):
        tail_text = swiss_tail_text_with_symbol(case['symbol_exception'])
    else:
        tail_text = SWISS_TAIL_TEXT_DEFAULT
    return head + body + visual + tail_text


def render_prompt(case, render_style):
    if render_style == 2:
        return render_pixar(case)
    return render_swiss(case)


# ============================================================
# 钩子三公式自动生成（程序化批量用）
# ============================================================
# 低龄数学：①拟人化提问 ②神奇物品比喻 ③生活场景发现
PIXAR_HOOK_FORMULAS = ['①拟人化提问', '②神奇物品比喻', '③生活场景发现']
# 高年级：①揭秘式 ②隐喻式 ③秘诀式
SWISS_HOOK_FORMULAS = ['①揭秘式', '②隐喻式', '③秘诀式']


def gen_pixar_hooks(main_word, action_word, course_name):
    """对低龄数学课程，按三公式自动生成 3 个钩子（≤12字）。"""
    main = main_word or '它'
    act = action_word or '玩'
    h1_candidates = [
        f'{main}宝宝排排队！' if '排' in act or '顺序' in act else None,
        f'{main}有几个？' if '几' in course_name or '认识' in course_name else None,
        f'{main}{act}小本领！',
        f'{main}的小秘密！',
    ]
    h2_candidates = [
        f'神奇的{main}',
        f'{main}藏着小秘密',
        f'{main}的小魔法',
    ]
    h3_candidates = [
        f'生活里的{main}',
        f'{main}{act}小课堂',
        f'{main}怎么{act}？',
    ]
    h1 = _first_short(h1_candidates, fallback=f'{main}小课堂')
    h2 = _first_short(h2_candidates, fallback=f'神奇{main}')
    h3 = _first_short(h3_candidates, fallback=f'生活里的{main}')
    return [h1, h2, h3]


def gen_swiss_hooks(main_word, action_word, course_name):
    """对高年级课程，按三公式自动生成 3 个钩子（≤12字）。"""
    main = main_word or '它'
    act = action_word or '解'
    h1 = _first_short([
        f'{main}背后的秘密',
        f'揭秘{main}的真相',
        f'{main}究竟怎么{act}？',
    ], fallback=f'{main}的真相')
    h2 = _first_short([
        f'读懂{main}',
        f'{main}：思维的钥匙',
        f'看清{main}的本质',
    ], fallback=f'读懂{main}')
    h3 = _first_short([
        f'巧解{main}的3步',
        f'破解{main}小窍门',
        f'{main}速通法',
    ], fallback=f'{main}速通法')
    return [h1, h2, h3]


def _first_short(candidates, fallback, max_len=12):
    for c in candidates:
        if c is not None and 2 <= len(c) <= max_len:
            return c
    return fallback


# ============================================================
# 学名压缩 (≤8字)
# ============================================================
_STOP_PREFIXES = [
    '认识', '理解', '掌握', '学习', '探索', '揭秘',
    '初步', '简单的', '简单',
]
_STOP_SUFFIXES = [
    '的认识', '的意义', '的方法', '的应用', '的计算',
    '及其应用', '的实际应用', '初步', '问题',
]


def compress_card(course_name, max_len=8):
    """从课程名压缩出学名（≤8字）。"""
    s = (course_name or '').strip()
    # 去引号 / 括号说明 / latex
    s = re.sub(r'\$\$.*?\$\$', '', s)
    s = re.sub(r'[\u201C\u201D"]', '', s)
    s = re.sub(r'[（(].*?[)）]', '', s)
    s = s.strip(' ,，。.？?！!')
    if len(s) <= max_len:
        return s
    # 尝试去前缀
    for p in _STOP_PREFIXES:
        if s.startswith(p):
            s = s[len(p):]
            if len(s) <= max_len:
                return s
    # 尝试去后缀
    for q in _STOP_SUFFIXES:
        if s.endswith(q):
            s = s[:-len(q)]
            if len(s) <= max_len:
                return s
    # 截断（保留前 max_len 字）
    return s[:max_len]


def gen_card_variants(course_name, n=3):
    """给一个课程名生成 n 个学名变体，长度都 ≤ 8；
    长课程名/LaTeX/带选项的题，直接 compress 得到一个简短学名，3 个 case 共用。
    """
    s = (course_name or '').strip()
    s = re.sub(r'\$\$.*?\$\$', '', s)
    s = re.sub(r'\$.*?\$', '', s)
    s = re.sub(r'[\u201C\u201D"]', '', s)
    s = re.sub(r'[（(].*?[)）]', '', s)
    s = re.sub(r'[A-D]\.\s*[^A-D]+(?=$|[A-D]\.)', '', s)
    s = s.strip(' ,，。.？?！!')

    v1 = compress_card(s)
    cards = [v1]
    if 4 <= len(s) <= 8 and s != v1:
        cards.append(s)
    for p in _STOP_PREFIXES:
        if s.startswith(p):
            cand = s[len(p):][:8].strip(' ,，。.？?！!')
            if cand and cand not in cards:
                cards.append(cand)
            break

    seen = []
    for c in cards:
        c = (c or '').strip()
        if c and c not in seen and len(c) <= 10:
            seen.append(c)
    if not seen:
        seen = [(course_name or '题目').strip()[:8] or '题目']
    while len(seen) < n:
        seen.append(seen[0])
    return seen[:n]


# ============================================================
# 强制对齐标签里的【年级】（修正晨艳标签错位）
# ============================================================
GRADE_RE = re.compile(r'【[一二三四五六七八九]年级】')


def force_grade_in_tag(tag, target_grade):
    """tag = '【三年级】★【数学启蒙】'，target_grade='二年级' → '【二年级】★【数学启蒙】'"""
    if not tag or not target_grade:
        return tag
    if target_grade in tag:
        return tag
    new_tag = GRADE_RE.sub(f'【{target_grade}】', tag, count=1)
    return new_tag

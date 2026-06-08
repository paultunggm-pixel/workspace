#!/bin/bash
# 千问小讲堂封面生产 · 环境自检（非技术同学可双击或在终端运行）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
REFS="$ROOT/refs"

echo "=== 千问小讲堂 · 封面生产环境自检 ==="
echo "cover-generator 根目录: $ROOT"
echo ""

# Python
if command -v python3 >/dev/null 2>&1; then
  echo "[OK] python3: $(python3 --version)"
else
  echo "[!!] 未找到 python3，请先安装 Python 3"
  exit 1
fi

# 依赖
echo ""
echo "--- 检查 Pillow/openpyxl（压图与 xlsx）---"
python3 -c "import PIL, openpyxl; print('[OK] PIL + openpyxl')" 2>/dev/null || {
  echo "[..] 正在安装依赖（refs/requirements.txt）..."
  pip3 install -r "$REFS/requirements.txt" --user -q || pip3 install Pillow openpyxl numpy --user -q
  python3 -c "import PIL, openpyxl; print('[OK] 安装完成')"
}

# 字体
echo ""
echo "--- 字体文件 ---"
for f in ZaoziGongfangYuanhei-Regular.ttf Alibaba-PuHuiTi-Bold.ttf Alibaba-PuHuiTi-Medium.ttf; do
  if [ -f "$ROOT/assets/$f" ]; then
    echo "[OK] $f"
  else
    echo "[!!] 缺少 $ROOT/assets/$f（数学压图需要）"
  fi
done

# 关键脚本
echo ""
echo "--- 关键脚本 ---"
for s in yuwen_lib.py cover_lib.py compose_math.py build_chengyu.py build_yuwen.py; do
  if [ -f "$SCRIPTS/$s" ]; then
    echo "[OK] scripts/$s"
  else
    echo "[!!] 缺少 scripts/$s"
  fi
done

# 启动包
KIT="$(dirname "$0")"
if [ -f "$KIT/SKILL.md" ]; then
  echo ""
  echo "[OK] 启动包 SKILL.md"
else
  echo "[!!] 启动包不完整"
fi

if [ -f "$ROOT/../../.cursor/skills/qianwen-cover-production/SKILL.md" ]; then
  echo "[OK] Cursor 项目技能已安装"
else
  echo "[..] 可选：复制启动包 SKILL.md 到 .cursor/skills/qianwen-cover-production/"
fi

# 链路 B：桌面挂载压图工程
echo ""
echo "--- 链路 B · 挂载压图（~/Desktop/qianwen-cover-generator）---"
QCG="$HOME/Desktop/qianwen-cover-generator"
QCG_BAK="$ROOT/_qcg/qianwen-cover-generator"
if [ -d "$QCG" ]; then
  echo "[OK] 桌面工程存在: $QCG"
  for s in render_covers.py run_kepu.py run_style3.py run_chengyu_all.py; do
    if [ -f "$QCG/$s" ]; then echo "[OK] $s"; else echo "[!!] 缺少 $QCG/$s"; fi
  done
  if [ -f "$QCG/assets/HYXinRenWenSong65W.ttf" ]; then
    echo "[OK] style3 字体 HYXinRenWenSong65W.ttf"
  else
    echo "[!!] 缺少 style3 字体（挂载压图需要）"
  fi
else
  echo "[!!] 未找到桌面工程，链路 B 无法运行（见 挂载压图分支说明.md）"
fi
if [ -f "$QCG_BAK/render_covers.py" ]; then
  echo "[OK] 仓库内备份: _qcg/qianwen-cover-generator/"
else
  echo "[..] 可选：从桌面同步到 _qcg/（见 refs/qianwen-cover-generator-说明.md）"
fi
if command -v "$HOME/Desktop/ossutilmac64" >/dev/null 2>&1 || [ -x "$HOME/Desktop/ossutilmac64" ]; then
  echo "[OK] ossutil（上传 CDN）"
else
  echo "[..] 未找到 ~/Desktop/ossutilmac64（全量上传 OSS 时需要）"
fi

echo ""
echo "=== 完成 ==="
echo "链路 A（文案）→ 00-从这里开始.md"
echo "链路 B（挂载压图）→ 挂载压图分支说明.md"

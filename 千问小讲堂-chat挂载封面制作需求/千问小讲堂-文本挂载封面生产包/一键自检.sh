#!/bin/bash
# 千问小讲堂封面生产包 · 环境自检
set -e
PKG="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$PKG/脚本"
DOC="$PKG/文档"

echo "=== 千问小讲堂 · 封面生产包自检 ==="
echo "包目录: $PKG"
echo ""

if command -v python3 >/dev/null 2>&1; then
  echo "[OK] python3: $(python3 --version)"
else
  echo "[!!] 未找到 python3"
  exit 1
fi

echo ""
echo "--- Python 依赖 ---"
python3 -c "import PIL; print('[OK] Pillow')" 2>/dev/null || {
  echo "[..] 安装依赖..."
  pip3 install -r "$SCRIPTS/requirements.txt" --user -q 2>/dev/null || pip3 install Pillow --user -q
  python3 -c "import PIL; print('[OK] 安装完成')"
}

echo ""
echo "--- 链路 B · 挂载压图脚本（本包 脚本/）---"
for s in render_covers.py run_kepu.py run_style3.py run_chengyu_all.py run_yuwen_fix.py; do
  if [ -f "$SCRIPTS/$s" ]; then echo "[OK] $s"; else echo "[!!] 缺少 脚本/$s"; fi
done

echo ""
echo "--- 字体（脚本/assets/）---"
for f in HYXinRenWenSong65W.ttf HYXinRenWenSongW.ttf ZaoziGongfangYuanhei-Regular.ttf Alibaba-PuHuiTi-Bold.ttf; do
  if [ -f "$SCRIPTS/assets/$f" ]; then echo "[OK] $f"; else echo "[!!] 缺少 $f"; fi
done

echo ""
echo "--- 说明文档 ---"
for f in README.md 00-从这里开始.md 挂载压图分支说明.md SKILL.md; do
  if [ -f "$PKG/$f" ]; then echo "[OK] $f"; else echo "[!!] 缺少 $f"; fi
done
[ -f "$DOC/logs/项目演进记录.md" ] && echo "[OK] 文档/logs/项目演进记录.md"

if [ -x "$HOME/Desktop/ossutilmac64" ] || [ -f "$HOME/Desktop/ossutilmac64" ]; then
  echo ""
  echo "[OK] ossutil（上传 CDN）"
else
  echo ""
  echo "[..] 未找到 ~/Desktop/ossutilmac64（上传 OSS 时需要，未打入压缩包）"
fi

echo ""
echo "=== 完成 ==="
echo "下一步: 打开 README.md → 00-从这里开始.md"
echo "压图命令请在 脚本/ 目录下执行（见 挂载压图分支说明.md）"

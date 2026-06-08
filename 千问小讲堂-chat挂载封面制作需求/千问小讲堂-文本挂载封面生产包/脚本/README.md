# qianwen-cover-generator

千问小讲堂挂载封面生成脚本，对应 Figma 文件 [小讲堂挂载封面优化](https://www.figma.com/design/fmyMpNSDnBnkt6hXulEqi2/%E5%B0%8F%E8%AE%B2%E5%A0%82%E6%8C%82%E8%BD%BD%E5%B0%81%E9%9D%A2%E4%BC%98%E5%8C%96) 中的 3 种设计稿。

设计稿尺寸 144×192，输出 4× = 576×768 PNG。

| style | 设计稿        | 节点                         | 文案需求               | 徽标样式            |
| ----- | ------------- | ---------------------------- | ---------------------- | ------------------- |
| `1`   | 彩虹里        | `53:3258`                    | 标题 + 副标题 + 标签   | 蓝色垂帘形 `#0293D2` |
| `2`   | 数字 1·百倍超能力 | `50:2915`                | 标题 + 副标题 + 标签   | 绿色下圆角 `#09692A` |
| `3`   | 揠苗助长      | `50:2839`                    | 标题 + 副标题（居中）  | 绿色矩形 `#457447`   |

用户提供：
1. **背景图** — 任意尺寸图片，脚本会按 cover-fit 缩放裁切到 576×768
2. **标题**
3. **副标题** 或 **标签文案**（按 style 不同而定，style 3 不需要标签）

## 依赖安装

```bash
pip3 install -r requirements.txt --break-system-packages --user
```

## 单张生成

```bash
python3 render_covers.py one --style 1 --bg ./bg.jpg \
    --title "彩虹里" --subtitle "藏着几种颜色" --tag "学龄前★生活发现" \
    --output ./out.png

python3 render_covers.py one --style 2 --bg ./bg.jpg \
    --title "数字1" --subtitle "百倍超能力" --tag "四年级｜趣味数学" \
    --output ./out.png

python3 render_covers.py one --style 3 --bg ./bg.jpg \
    --title "揠苗助长" --subtitle "欲速则不达的教训" \
    --output ./out.png
```

## 批量生成

xlsx 表头列（顺序不限，按列名匹配）：

| 列名     | 必填           | 说明                                              |
| -------- | -------------- | ------------------------------------------------- |
| style    | ✓              | 1 / 2 / 3                                         |
| bg       | ✓              | 背景图路径（相对路径会以 xlsx 所在目录为根）       |
| title    | ✓              | 标题                                              |
| subtitle |                | 副标题                                            |
| tag      |                | 标签（style 3 忽略）                              |
| output   |                | 输出文件名，缺省自动编号                          |

```bash
python3 render_covers.py batch --xlsx ./covers.xlsx --out-dir ./output
```

## 字体

- `千问小讲堂` 徽标、标题、副标题、标签：PingFang SC（系统自带，对应 Figma 中的 Alibaba PuHuiTi / MF YuanHei）
- style 3 标题/副标题：Songti SC（系统自带，对应 Figma 中的 HYXinRenWenSong）

## 目录结构

```
qianwen-cover-generator/
├── render_covers.py       # 主脚本
├── requirements.txt
├── assets/                # 从 Figma 抓取的徽标 SVG（脚本通过 PIL 重绘，仅作参考）
├── sample-bg/             # 示例背景图
└── output/                # 生成结果
```

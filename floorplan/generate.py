"""写真の図面（2階平面図）を読み取って SVG 平面図を生成するスクリプト。
座標はすべて mm。X=東向き、Y=南向き（北が上）。
原点 = 階段部分の北西角（主屋の北壁ライン上）。
"""
import math, pathlib

EXT = 150   # 外壁厚
INT = 100   # 内壁厚
CEN = 110   # ユニット境界の壁（図面上の 110）

out = []
def add(s): out.append(s)

# ---------- 部屋の床塗り ----------
rooms = [
    # name, x1,y1,x2,y2, label lines, label pos
    ("階段・ホール", 0, 0, 2060, 4770),
    ("浴室", 2060, -520, 4280, 800),
    ("洗面所", 2060, 800, 4280, 2130),
    ("ホール", 2060, 2130, 4280, 3800),
    ("押入", 4280, 0, 5470, 1850),
    ("物入", 4280, 1850, 5470, 2820),
    ("ホール2", 4280, 2820, 5470, 3800),
    ("洋室③", 5470, 0, 9362, 3800),
    ("廊下", 2060, 3800, 6170, 4770),
    ("洋室①", 2060, 4770, 5530, 7590),
    ("収納B", 5530, 4770, 6170, 6210),
    ("収納A", 5530, 6210, 6170, 7590),
    ("洋室②", 6170, 3800, 9362, 7590),
]
wet = {"浴室", "洗面所"}
store = {"押入", "物入", "収納A", "収納B"}
for n, x1, y1, x2, y2 in rooms:
    cls = "fl-wet" if n in wet else "fl-store" if n in store else "fl-room"
    add(f'<rect class="{cls}" x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}"/>')

# バルコニー
add('<rect class="fl-balc" x="2060" y="7590" width="7302" height="910"/>')
add('<line class="ln-thin" x1="2060" y1="8500" x2="9362" y2="8500"/>')
add('<line class="ln-thin" x1="2060" y1="8440" x2="9362" y2="8440"/>')

# ---------- 壁（開口を除いた区間ごと） ----------
def wall(x1, y1, x2, y2, t, openings=()):
    """openings: 壁方向の座標区間 (a,b) のリスト"""
    horiz = y1 == y2
    a0, a1 = (min(x1, x2), max(x1, x2)) if horiz else (min(y1, y2), max(y1, y2))
    pts = [a0]
    for a, b in sorted(openings):
        pts += [a, b]
    pts.append(a1)
    for i in range(0, len(pts), 2):
        s, e = pts[i], pts[i + 1]
        if e - s <= 0:
            continue
        if horiz:
            add(f'<rect class="wall" x="{s - (t/2 if s==a0 else 0)}" y="{y1 - t/2}" '
                f'width="{e - s + (t/2 if s==a0 else 0) + (t/2 if e==a1 else 0)}" height="{t}"/>')
        else:
            add(f'<rect class="wall" x="{x1 - t/2}" y="{s - (t/2 if s==a0 else 0)}" '
                f'width="{t}" height="{e - s + (t/2 if s==a0 else 0) + (t/2 if e==a1 else 0)}"/>')

# 外壁
wall(0, 0, 2060, 0, EXT)
wall(2060, -520, 2060, 0, EXT)
wall(2060, -520, 4280, -520, EXT)
wall(4280, -520, 4280, 0, EXT)
wall(4280, 0, 9362, 0, EXT, [(7000, 8650)])                 # 洋室③ 北窓
wall(9362, 0, 9362, 7590, EXT, [(900, 2700), (4400, 6200)])   # 東：洋室③・洋室② 窓
wall(2060, 7590, 9362, 7590, EXT, [(2300, 4100), (7400, 9200)])  # 南：全開口1800 ×2
wall(2060, 4770, 2060, 7590, EXT, [(5600, 6800)])            # 洋室① 西窓
wall(0, 4770, 2060, 4770, EXT)
wall(0, 0, 0, 4770, EXT)

# 内壁
wall(2060, 0, 2060, 2130, INT)                       # 浴室・洗面 西
wall(2060, 800, 4280, 800, INT, [(3300, 4000)])       # 浴室/洗面
wall(2060, 2130, 4280, 2130, INT, [(3500, 4250)])     # 洗面 南（2002-13）
wall(4280, 0, 4280, 2820, INT)
wall(4280, 1850, 5470, 1850, INT)
wall(4280, 2820, 5470, 2820, INT, [(4400, 5370)])     # 物入 戸
wall(5470, 0, 5470, 3800, INT, [(100, 1750), (2900, 3700)])  # 押入 襖 / 2002-11
wall(2060, 3800, 4280, 3800, CEN + 40)                # 中央（ユニット境界）
wall(5470, 3800, 9362, 3800, CEN + 40)
wall(2060, 4770, 5530, 4770, INT, [(3700, 4500)])     # 洋室① 北（2002-14）
wall(5530, 4770, 6170, 4770, INT)
wall(5530, 4770, 5530, 7590, INT, [(4880, 6110)])     # 収納B 折戸
wall(5530, 6210, 6170, 6210, INT)
wall(6170, 3800, 6170, 7590, INT, [(3900, 4700), (6320, 7480)])  # 2002-12 / 収納A 折戸

# ---------- 窓 ----------
def window(x1, y1, x2, y2, t):
    if y1 == y2:
        add(f'<rect class="win" x="{x1}" y="{y1-t/2}" width="{x2-x1}" height="{t}"/>')
        add(f'<line class="ln-thin" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y1}"/>')
    else:
        add(f'<rect class="win" x="{x1-t/2}" y="{y1}" width="{t}" height="{y2-y1}"/>')
        add(f'<line class="ln-thin" x1="{x1}" y1="{y1}" x2="{x1}" y2="{y2}"/>')
window(7000, 0, 8650, 0, EXT)
window(9362, 900, 9362, 2700, EXT)
window(9362, 4400, 9362, 6200, EXT)
window(2300, 7590, 4100, 7590, EXT)
window(7400, 7590, 9200, 7590, EXT)
window(2060, 5600, 2060, 6800, EXT)

# ---------- 開き戸 ----------
def door(hx, hy, cx, cy, ox, oy, tag=None, tpos=None):
    """hinge, 閉じた時の戸先, 開いた時の戸先"""
    r = math.hypot(cx - hx, cy - hy)
    # sweep: 外積で回転方向を判定
    cross = (cx - hx) * (oy - hy) - (cy - hy) * (ox - hx)
    sweep = 1 if cross > 0 else 0
    add(f'<line class="door-leaf" x1="{hx}" y1="{hy}" x2="{ox}" y2="{oy}"/>')
    add(f'<path class="door-arc" d="M{cx},{cy} A{r},{r} 0 0 {sweep} {ox},{oy}"/>')
    if tag:
        add(f'<text class="t-tag" x="{tpos[0]}" y="{tpos[1]}">{tag}</text>')

door(4500, 4770, 3700, 4770, 4500, 5570, "2002-14", (3950, 5450))
door(6170, 4700, 6170, 3900, 6970, 4700, "2002-12", (6750, 4500))
door(5470, 3700, 5470, 2900, 6270, 3700, "2002-11", (6050, 3500))
door(4250, 2130, 3500, 2130, 4250, 2880, "2002-13", (3700, 2700))
door(4000, 800, 3300, 800, 4000, 1500)

# ---------- 引戸（襖）・折戸 ----------
def slider_v(x, y1, y2):
    m = (y1 + y2) / 2
    add(f'<rect class="slide" x="{x-50}" y="{y1}" width="35" height="{m-y1+60}"/>')
    add(f'<rect class="slide" x="{x+15}" y="{m-60}" width="35" height="{y2-m+60}"/>')
def slider_h(y, x1, x2):
    m = (x1 + x2) / 2
    add(f'<rect class="slide" x="{x1}" y="{y-50}" width="{m-x1+60}" height="35"/>')
    add(f'<rect class="slide" x="{m-60}" y="{y+15}" width="{x2-m+60}" height="35"/>')
def bifold_v(x, y1, y2, side):
    # side=+1 で東へ、-1 で西へ折れる
    q = (y2 - y1) / 4
    d = 220 * side
    pts = [(x, y1), (x + d, y1 + q), (x, y1 + 2*q), (x + d, y1 + 3*q), (x, y2)]
    add('<polyline class="door-leaf" points="' + " ".join(f"{a},{b}" for a, b in pts) + '"/>')

slider_v(5470, 100, 1750)
slider_h(2820, 4400, 5370)
bifold_v(5530, 4880, 6110, -1)
bifold_v(6170, 6320, 7480, +1)

# ---------- 設備 ----------
# 浴槽
add('<rect class="fix" x="2160" y="-420" width="950" height="1120" rx="60"/>')
add('<rect class="fix" x="2240" y="-340" width="790" height="960" rx="140"/>')
# 洗面台・洗濯機パン
add('<rect class="fix" x="2140" y="900" width="560" height="760"/>')
add('<ellipse class="fix" cx="2400" cy="1280" rx="170" ry="230"/>')
add('<rect class="fix" x="3540" y="1460" width="640" height="600"/>')
add('<circle class="fix" cx="3860" cy="1760" r="220"/>')
add('<text class="t-sm" x="3860" y="1410">洗濯機</text>')
# 押入 中段
add('<line class="ln-dash" x1="4280" y1="0" x2="5470" y2="1850"/>')
add('<line class="ln-dash" x1="5470" y1="0" x2="4280" y2="1850"/>')
add('<line class="ln-dash" x1="4280" y1="1850" x2="5470" y2="2820"/>')
add('<line class="ln-dash" x1="5470" y1="1850" x2="4280" y2="2820"/>')
for nm, x1, y1, x2, y2 in [("B", 5530, 4770, 6170, 6210), ("A", 5530, 6210, 6170, 7590)]:
    add(f'<line class="ln-dash" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    add(f'<line class="ln-dash" x1="{x2}" y1="{y1}" x2="{x1}" y2="{y2}"/>')

# 階段（位置・向きは推定）
sx1, sx2, sy1, sy2 = 1080, 1980, 120, 3150
n = 13
step = (sy2 - sy1) / n
add(f'<rect class="stair" x="{sx1}" y="{sy1}" width="{sx2-sx1}" height="{sy2-sy1}"/>')
for i in range(1, n):
    y = sy1 + i * step
    add(f'<line class="ln-thin" x1="{sx1}" y1="{y:.0f}" x2="{sx2}" y2="{y:.0f}"/>')
mx = (sx1 + sx2) / 2
add(f'<line class="arrow" x1="{mx}" y1="{sy2-150}" x2="{mx}" y2="{sy1+250}" marker-end="url(#ah)"/>')
add(f'<text class="t-sm" x="{mx}" y="{sy2+260}">DN</text>')

# ---------- 室名 ----------
def label(x, y, name, sub=None, cls="t-room"):
    add(f'<text class="{cls}" x="{x}" y="{y}">{name}</text>')
    if sub:
        add(f'<text class="t-sub" x="{x}" y="{y+330}">{sub}</text>')
label(7420, 1750, "洋室③", "約9帖")
label(3800, 6250, "洋室①", "約6帖")
label(7770, 5900, "洋室②", "約7帖")
label(3200, 200 + 50, "浴室", cls="t-room-s")
label(2900, 1950, "洗面所", cls="t-room-s")
label(3150, 3050, "ホール", cls="t-room-s")
label(4875, 1000, "押入", cls="t-room-s")
label(4875, 2420, "物入", cls="t-room-s")
label(4100, 4380, "廊下", cls="t-room-s")
label(5850, 5560, "収納", cls="t-room-n")
label(5850, 6960, "収納", cls="t-room-n")
label(540, 1700, "階段", cls="t-room-s")
label(1030, 4200, "ホール", cls="t-room-s")
label(5711, 8130, "バルコニー", cls="t-room-s")
add('<text class="t-sm" x="3200" y="7400">全開口1800</text>')
add('<text class="t-sm" x="8300" y="7400">全開口1800</text>')
add('<text class="t-sm t-rot" transform="translate(9180 1800) rotate(-90)">引違1800</text>')
add('<text class="t-sm t-rot" transform="translate(9180 5300) rotate(-90)">引違1800</text>')
add('<text class="t-sm" x="2120" y="-650" text-anchor="start" style="text-anchor:start">（520 突出）</text>')

# ---------- 寸法線 ----------
def dim_h(xs, y, ext_from, labels=None):
    add(f'<line class="dim" x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}"/>')
    for x in xs:
        add(f'<line class="dim" x1="{x}" y1="{ext_from}" x2="{x}" y2="{y + (120 if y > ext_from else -120)}"/>')
        add(f'<line class="dim-tick" x1="{x-70}" y1="{y+70}" x2="{x+70}" y2="{y-70}"/>')
    for i in range(len(xs) - 1):
        v = labels[i] if labels else f"{xs[i+1]-xs[i]:,}"
        small = xs[i+1]-xs[i] < 400
        add(f'<text class="t-dim{" t-dim-s" if small else ""}" x="{(xs[i]+xs[i+1])/2}" y="{y-(330 if small else 70)}">{v}</text>')
def dim_v(ys, x, ext_from, labels=None):
    add(f'<line class="dim" x1="{x}" y1="{ys[0]}" x2="{x}" y2="{ys[-1]}"/>')
    for y in ys:
        add(f'<line class="dim" x1="{ext_from}" y1="{y}" x2="{x + 120}" y2="{y}"/>')
        add(f'<line class="dim-tick" x1="{x-70}" y1="{y+70}" x2="{x+70}" y2="{y-70}"/>')
    for i in range(len(ys) - 1):
        v = labels[i] if labels else f"{ys[i+1]-ys[i]:,}"
        cy = (ys[i] + ys[i+1]) / 2
        small = ys[i+1]-ys[i] < 400
        add(f'<text class="t-dim{" t-dim-s" if small else ""}" transform="translate({x-(330 if small else 90)} {cy+(40 if small else 0)}) rotate(-90)">{v}</text>')

# 南側：図面記載の 2,060 / 2,364 / 110 / 2,364 / 110 / 2,354 = 9,362
dim_h([0, 2060, 4424, 4534, 6898, 7008, 9362], 9150, 8550)
dim_h([0, 9362], 9750, 9200)
# 東側：520 / 3,740 / 110 / 3,740 → 7,590
dim_v([-520, 0, 3740, 3850, 7590], 10000, 9450)
dim_v([0, 7590], 10600, 10050)
# 北側：浴室 2,220
dim_h([2060, 4280], -1050, -600, ["2,220"])

# ---------- 方位 ----------
add('<g class="north" transform="translate(8300 -1150)">'
    '<circle r="420" class="ln-thin" fill="none"/>'
    '<path d="M0,-360 L170,250 L0,140 L-170,250 Z" class="n-arrow"/>'
    '<text class="t-dim" y="-470">N</text></g>')

body = "\n".join(out)

STYLE = """
.fl-room{fill:var(--fp-room,#ffffff)}
.fl-wet{fill:var(--fp-wet,#e6eefb)}
.fl-store{fill:var(--fp-store,#eef1f6)}
.fl-balc{fill:var(--fp-balc,#f1f4f9);stroke:var(--fp-line,#1d3b8f);stroke-width:20}
.stair{fill:var(--fp-room,#ffffff);stroke:var(--fp-line,#1d3b8f);stroke-width:20}
.wall{fill:var(--fp-wall,#1d3b8f)}
.win{fill:var(--fp-room,#ffffff);stroke:var(--fp-line,#1d3b8f);stroke-width:18}
.ln-thin{stroke:var(--fp-line,#1d3b8f);stroke-width:14;fill:none}
.ln-dash{stroke:var(--fp-muted,#7d8db5);stroke-width:10;stroke-dasharray:60 50;fill:none}
.door-leaf{stroke:var(--fp-line,#1d3b8f);stroke-width:22;fill:none}
.door-arc{stroke:var(--fp-line,#1d3b8f);stroke-width:10;fill:none;stroke-dasharray:40 30}
.slide{fill:var(--fp-room,#ffffff);stroke:var(--fp-line,#1d3b8f);stroke-width:12}
.fix{fill:none;stroke:var(--fp-line,#1d3b8f);stroke-width:14}
.arrow{stroke:var(--fp-line,#1d3b8f);stroke-width:16}
.dim{stroke:var(--fp-dim,#b0412e);stroke-width:9}
.dim-tick{stroke:var(--fp-dim,#b0412e);stroke-width:18}
.n-arrow{fill:var(--fp-wall,#1d3b8f)}
text{font-family:"Noto Sans JP","Hiragino Sans","Yu Gothic",sans-serif;text-anchor:middle;fill:var(--fp-text,#16223f)}
.t-room{font-size:300px;font-weight:700}
.t-room-s{font-size:200px;font-weight:600}
.t-room-n{font-size:150px;font-weight:600}
.t-sub{font-size:190px;fill:var(--fp-muted,#7d8db5)}
.t-sm{font-size:140px;fill:var(--fp-muted,#7d8db5)}
.t-tag{font-size:120px;fill:var(--fp-muted,#7d8db5)}
.t-dim{font-size:170px;fill:var(--fp-dim,#b0412e);font-variant-numeric:tabular-nums}
.t-dim-s{font-size:120px}
"""

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-700 -1800 11800 11900" role="img" aria-label="2階平面図（写真から再作図）">
<defs><marker id="ah" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--fp-line,#1d3b8f)"/></marker></defs>
<style>{STYLE}</style>
{body}
</svg>'''

here = pathlib.Path(__file__).parent
(here / "2F-floorplan.svg").write_text(svg, encoding="utf-8")
print("ok", len(svg))

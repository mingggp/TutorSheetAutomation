#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ตัววาดรูปทั้งหมดสำหรับชีท TPAT3"""
import os
from PIL import Image, ImageDraw, ImageFont

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(IMG, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, "fonts", "Sarabun-Regular.ttf")
FB = os.path.join(HERE, "fonts", "Sarabun-Bold.ttf")

INK   = (31, 37, 40)
TOPF  = (224, 238, 238)
LEFTF = (176, 202, 204)
RIGHTF= (201, 221, 222)
LINEG = (150, 162, 165)
S = 3

def _save(im, W, H, name):
    im = im.resize((W, H), Image.LANCZOS)
    p = os.path.join(IMG, name + ".png"); im.save(p)
    return name + ".png"

def font(sz, bold=False):
    return ImageFont.truetype(FB if bold else FR, int(sz * S))

# ---------------------------------------------------------------- isometric
def _iso_geom(vox, cell, ch, pad):
    proj = lambda x, y, z: ((x - y) * cell, (x + y) * (cell // 2) - z * ch)
    pts = [proj(x + dx, y + dy, z + dz) for (x, y, z) in vox
           for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)]
    mnx, mxx = min(p[0] for p in pts), max(p[0] for p in pts)
    mny, mxy = min(p[1] for p in pts), max(p[1] for p in pts)
    W, H = int(mxx - mnx) + pad * 2, int(mxy - mny) + pad * 2
    return proj, W, H, -mnx + pad, -mny + pad

def iso(vox, name, cell=26, ch=22, pad=12, labels=None):
    """labels = (top, left, right) ตัวอักษรบนหน้าที่มองเห็น (ใช้กับลูกบาศก์ก้อนเดียว)"""
    vox = sorted(set(vox))
    proj, W, H, ox, oy = _iso_geom(vox, cell, ch, pad)
    im = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(im)
    P = lambda x, y, z: ((proj(x, y, z)[0] + ox) * S, (proj(x, y, z)[1] + oy) * S)
    for (x, y, z) in sorted(vox, key=lambda v: (v[0] + v[1] + v[2], v[2])):
        d.polygon([P(x,y,z+1),P(x+1,y,z+1),P(x+1,y+1,z+1),P(x,y+1,z+1)], fill=TOPF,  outline=INK, width=S)
        d.polygon([P(x,y+1,z+1),P(x+1,y+1,z+1),P(x+1,y+1,z),P(x,y+1,z)], fill=LEFTF, outline=INK, width=S)
        d.polygon([P(x+1,y,z+1),P(x+1,y+1,z+1),P(x+1,y+1,z),P(x+1,y,z)], fill=RIGHTF,outline=INK, width=S)
    if labels:
        quads = {
            "top":   [P(0,0,1), P(1,0,1), P(1,1,1), P(0,1,1)],
            "left":  [P(0,1,1), P(1,1,1), P(1,1,0), P(0,1,0)],
            "right": [P(1,1,1), P(1,0,1), P(1,0,0), P(1,1,0)],
        }
        for key, txt in zip(("top", "left", "right"), labels):
            if not txt: continue
            im.paste(*_glyph_on_quad(txt, quads[key]))
    return _save(im, W, H, name)

def _find_coeffs(dst, src):
    import numpy as np
    M = []
    for (dx, dy), (sx, sy) in zip(dst, src):
        M.append([dx, dy, 1, 0, 0, 0, -sx*dx, -sx*dy])
        M.append([0, 0, 0, dx, dy, 1, -sy*dx, -sy*dy])
    A = np.array(M, dtype=float)
    B = np.array(src, dtype=float).reshape(8)
    return np.linalg.solve(A.T @ A, A.T @ B)

def _glyph_on_quad(txt, quad):
    """quad = (UL, UR, LR, LL) ของหน้าลูกบาศก์ — วางตัวอักษรให้บิดตามหน้า"""
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    bx0, by0 = int(min(xs)), int(min(ys))
    bw, bh = int(max(xs) - bx0) + 1, int(max(ys) - by0) + 1
    N = 240
    tile = Image.new("L", (N, N), 255)
    td = ImageDraw.Draw(tile)
    f = ImageFont.truetype(FB, 150)
    tw = td.textlength(txt, font=f)
    td.text(((N - tw) / 2, N * 0.16), txt, font=f, fill=0)
    dst = [(p[0] - bx0, p[1] - by0) for p in quad]
    src = [(0, 0), (N, 0), (N, N), (0, N)]
    co = _find_coeffs(dst, src)
    out = tile.transform((bw, bh), Image.PERSPECTIVE, co, Image.BICUBIC, fillcolor=255)
    mask = out.point(lambda v: 255 if v < 150 else 0)
    return (Image.new("RGB", (bw, bh), INK), (bx0, by0), mask)

def hm_vox(hm):
    return [(x, y, z) for y, r in enumerate(hm) for x, h in enumerate(r) for z in range(h)]

# ---------------------------------------------------------------- 2D grid
def grid(rows, cols, filled=(), holes=(), name="g", cell=22, pad=8, text=None, center=None):
    W, H = cols * cell + pad * 2, rows * cell + pad * 2
    im = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(im)
    f = font(15, True)
    for r in range(rows):
        for c in range(cols):
            x0, y0 = (pad + c * cell) * S, (pad + r * cell) * S
            x1, y1 = x0 + cell * S, y0 + cell * S
            d.rectangle([x0, y0, x1, y1], fill=TOPF if (r, c) in filled else "white",
                        outline=(196, 204, 206), width=max(1, S // 2))
            if (r, c) in holes:
                m = cell * S * .28
                d.ellipse([x0 + m, y0 + m, x1 - m, y1 - m], fill=INK)
            if text and (r, c) in text:
                t = text[(r, c)]
                tw = d.textlength(t, font=f)
                d.text((x0 + (cell*S - tw)/2, y0 + cell*S*.16), t, font=f, fill=INK)
    d.rectangle([pad*S, pad*S, (pad+cols*cell)*S, (pad+rows*cell)*S], outline=INK, width=S)
    if center:
        fc = font(int(cell * 1.15), True)
        tw = d.textlength(center, font=fc)
        d.text(((W*S - tw)/2, (H*S)/2 - cell*S*0.78), center, font=fc, fill=(120,130,134))
    return _save(im, W, H, name)

def numgrid(rows, name, cell=44, pad=8):
    R, C = len(rows), len(rows[0])
    W, H = C * cell + pad * 2, R * cell + pad * 2
    im = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(im)
    f = font(19, False)
    for r in range(R):
        for c in range(C):
            x0, y0 = (pad + c*cell)*S, (pad + r*cell)*S
            d.rectangle([x0, y0, x0 + cell*S, y0 + cell*S], fill="white", outline=LINEG, width=max(1, S))
            t = str(rows[r][c]); tw = d.textlength(t, font=f)
            d.text((x0 + (cell*S - tw)/2, y0 + cell*S*.20), t, font=f, fill=INK)
    return _save(im, W, H, name)

# ---------------------------------------------------------------- ขาวดำล้วน: แผ่นตาราง / กรอบสัญลักษณ์
# ใช้กับพาร์ท 2 แนวที่ข้อสอบจริงเป็น line art ดำบนขาว
# (อนุกรมรูปภาพ · เมทริกซ์รูปภาพ · ซ้อนแผ่นบังแสง · หารูปไม่เข้าพวก · อุปมาอุปมัยรูปภาพ)
# โทนที่ใช้ได้มีสามระดับเท่านั้น: ขาว(โปร่ง) / เทากลาง / ดำทึบ — ห้ามใช้สีติวเตอร์ในสองฟังก์ชันนี้
import math

_GREY = (128, 128, 128)      # โทนที่สาม
_HAIR = (150, 150, 150)      # เส้นตารางบาง มองเห็นได้ทั้งบนช่องขาวและช่องทึบ
_LW   = max(1, int(round(S * 1.3)))   # เส้นหลัก หนาเท่ากันหมดตามสไตล์ข้อสอบจริง
_HW   = max(1, int(round(S * 0.7)))   # เส้นตารางบาง

def plate(rows, name, cell=16, pad=6, frame=True, grid=True):
    """ตารางช่องทึบ/โปร่ง — ใช้ได้ทั้งแผ่นบังแสง ลายจุด และช่องในเมทริกซ์

    rows  : list[list[int]]  1 = ช่องทึบ (เติมสีเข้ม)  0 = ช่องโปร่ง (ขาว)
            (ส่วนขยาย: 2 = ช่องเทา สำหรับโจทย์ที่ต้องใช้โทนที่สาม)
    grid  : True = ตีเส้นแบ่งช่องจางๆ   False = ไม่ตีเส้น (ให้เห็นเป็นลายทึบล้วน)
    frame : True = ตีกรอบนอกเข้ม
    คืนค่า: ชื่อไฟล์ .png (เหมือน grid/numgrid เดิม)
    """
    R = len(rows)
    C = max((len(r) for r in rows), default=0)
    W, H = C * cell + pad * 2, R * cell + pad * 2
    im = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(im)
    ax, ay = pad * S, pad * S
    bx, by = (pad + C * cell) * S, (pad + R * cell) * S
    for r in range(R):
        for c in range(len(rows[r])):
            v = rows[r][c]
            if not v:
                continue
            x0, y0 = (pad + c * cell) * S, (pad + r * cell) * S
            d.rectangle([x0, y0, x0 + cell * S, y0 + cell * S],
                        fill=_GREY if v == 2 else INK)
    if grid:
        for r in range(R + 1):
            y = (pad + r * cell) * S
            d.line([ax, y, bx, y], fill=_HAIR, width=_HW)
        for c in range(C + 1):
            x = (pad + c * cell) * S
            d.line([x, ay, x, by], fill=_HAIR, width=_HW)
    if frame:
        d.rectangle([ax, ay, bx, by], outline=INK, width=_LW)
    return _save(im, W, H, name)


# ---- คลังรูปสัญลักษณ์ (พิกัดหน่วย ศูนย์กลางที่ (0,0) ครึ่งความกว้างสูงสุด = 1, แกน y ชี้ลงตามภาพ)
def _norm(pts):
    """ย่อ/ขยับให้กรอบรูปอยู่กึ่งกลาง (0,0) และครึ่งด้านที่ยาวที่สุดเท่ากับ 1 — ทุกรูปจึงมีน้ำหนักสายตาเท่ากัน"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    k = max(max(xs) - cx, max(ys) - cy) or 1.0
    return [((x - cx) / k, (y - cy) / k) for x, y in pts]

def _ngon(n, start=-90.0):
    return [(math.cos(math.radians(start + i * 360.0 / n)),
             math.sin(math.radians(start + i * 360.0 / n))) for i in range(n)]

def _plus(t):
    return [(-t,-1),(t,-1),(t,-t),(1,-t),(1,t),(t,t),(t,1),(-t,1),(-t,t),(-1,t),(-1,-t),(-t,-t)]

def _star(n=5, inner=0.42, start=-90.0):
    p = []
    for i in range(n * 2):
        rr = 1.0 if i % 2 == 0 else inner
        a = math.radians(start + i * 180.0 / n)
        p.append((rr * math.cos(a), rr * math.sin(a)))
    return p

def _rotpts(pts, deg):
    """หมุนตามเข็มนาฬิกาบนภาพ (แกน y ชี้ลง)"""
    a = math.radians(float(deg) % 360.0)
    ca, sa = math.cos(a), math.sin(a)
    return [(x * ca - y * sa, x * sa + y * ca) for x, y in pts]

_ARROW = [(0,-1), (0.62,-0.08), (0.26,-0.08), (0.26,1), (-0.26,1), (-0.26,-0.08), (-0.62,-0.08)]

SHAPES = {                      # rot=0 คือท่าตั้งต้น: ปลายแหลม/หัวลูกศรชี้ขึ้น
    "square":   _norm([(-1,-1), (1,-1), (1,1), (-1,1)]),
    "diamond":  _norm(_ngon(4)),
    "triangle": _norm(_ngon(3)),
    "pentagon": _norm(_ngon(5)),
    "hexagon":  _norm(_ngon(6)),
    "star":     _norm(_star()),
    "cross":    _norm(_rotpts(_plus(0.20), 45)),   # กากบาท ×
    "plus":     _norm(_plus(0.24)),                # เครื่องหมายบวก +
    "arrow":    _norm(_ARROW),
}
_POS  = {"c": (.50, .50), "tl": (.28, .28), "tr": (.72, .28), "bl": (.28, .72), "br": (.72, .72)}
_FILL = {"white": "white", "black": INK, "grey": _GREY, "gray": _GREY}

def _sym(d, it, ox, oy, box):
    """วาดสัญลักษณ์หนึ่งตัวลงบน d — ox, oy, box เป็นพิกัดที่คูณ S แล้ว"""
    shape = str(it.get("shape", "circle")).lower()
    posk  = str(it.get("pos", "c")).lower()
    px, py = _POS.get(posk, _POS["c"])
    frac  = float(it.get("size") or (0.55 if posk == "c" else 0.34))
    fill  = _FILL.get(str(it.get("fill", "white")).lower(), "white")
    rot   = it.get("rot", 0) or 0
    cx, cy = ox + px * box, oy + py * box
    r = max(_LW * 1.5, frac * box / 2.0)
    if shape == "circle":       # หมุนแล้วเหมือนเดิม แต่ต้องไม่ error
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=INK, width=_LW)
        return
    if shape not in SHAPES:
        raise ValueError("symbox: ไม่รู้จักรูป %r (มีให้ใช้: circle, %s)"
                         % (shape, ", ".join(sorted(SHAPES))))
    xy = [(cx + x * r, cy + y * r) for x, y in _rotpts(SHAPES[shape], rot)]
    d.polygon(xy, fill=fill)
    d.line(xy + [xy[0]], fill=INK, width=_LW, joint="curve")   # รูปโปร่งต้องมีเส้นขอบเข้มเสมอ

def symbox(items, name, size=74, pad=6, frame=True):
    """กรอบสี่เหลี่ยมหนึ่งกรอบ ข้างในมีสัญลักษณ์ 1-4 ตัว

    items : list ของ dict แต่ละตัวคือสัญลักษณ์หนึ่งตัว คีย์ที่ต้องรองรับ
        "shape" : "circle" | "square" | "triangle" | "diamond" | "star" | "cross" | "arrow"
                  (ส่วนขยาย: "plus" · "pentagon" · "hexagon")
        "fill"  : "white" | "black" | "grey"        (ค่าเริ่มต้น "white")
        "pos"   : "c" | "tl" | "tr" | "bl" | "br"   (กลาง/มุมทั้งสี่ ค่าเริ่มต้น "c")
        "rot"   : 0 | 90 | 180 | 270                 (ค่าเริ่มต้น 0 · หมุนตามเข็มนาฬิกา)
        "size"  : 0.0-1.0 สัดส่วนต่อกรอบ             (ค่าเริ่มต้น 0.55 ถ้า pos="c" ไม่งั้น 0.34)
    ใส่หลายตัวที่ pos เดียวกันแต่ size ต่างกันได้ = รูปซ้อนรูป (ตัวหลังทับตัวหน้า)
    คืนค่า: ชื่อไฟล์ .png
    """
    W = H = size + pad * 2
    im = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(im)
    ox = oy = pad * S
    for it in (items or []):
        _sym(d, it, ox, oy, size * S)
    if frame:
        d.rectangle([ox, oy, ox + size * S, oy + size * S], outline=INK, width=_LW)
    return _save(im, W, H, name)

# ---------------------------------------------------------------- รูปคลี่ลูกบาศก์
NET = {(0,1):"A", (1,0):"B", (1,1):"C", (1,2):"D", (2,1):"E", (3,1):"F"}
def net(labels, name, cell=40, pad=8):
    R, C = 4, 3
    W, H = C*cell + pad*2, R*cell + pad*2
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    f = font(19, True)
    for (r, c), key in NET.items():
        x0, y0 = (pad + c*cell)*S, (pad + r*cell)*S
        d.rectangle([x0, y0, x0 + cell*S, y0 + cell*S], fill=TOPF, outline=INK, width=S)
        t = labels[key]; tw = d.textlength(t, font=f)
        d.text((x0 + (cell*S - tw)/2, y0 + cell*S*.18), t, font=f, fill=INK)
    return _save(im, W, H, name)

# ---------------------------------------------------------------- สามเหลี่ยมปริศนา
def tri(vals, name, w=112, h=100, pad=8):
    """vals = (บน, ซ้ายล่าง, ขวาล่าง, กลาง)"""
    W, H = w + pad*2, h + pad*2
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    A = ((pad + w/2)*S, pad*S); B = (pad*S, (pad + h)*S); C = ((pad + w)*S, (pad + h)*S)
    d.polygon([A, B, C], fill="white", outline=INK, width=S)
    f = font(17, False); fb = font(19, True)
    def put(t, cx, cy, bold=False):
        ff = fb if bold else f
        tw = d.textlength(t, font=ff)
        d.text((cx - tw/2, cy - 11*S), t, font=ff, fill=INK)
    put(str(vals[0]), A[0], A[1] + 22*S)
    put(str(vals[1]), B[0] + 20*S, B[1] - 20*S)
    put(str(vals[2]), C[0] - 20*S, C[1] - 20*S)
    put(str(vals[3]), (pad + w/2)*S, (pad + h*0.62)*S, True)
    return _save(im, W, H, name)

# ---------------------------------------------------------------- ประกอบภาพ
LAB = "กขคงจ"
def strip(files, name, gap=26, labh=26, lab=True, labels=None):
    """labels = ป้ายหน้าตัวเลือกเอง เช่น ["1)","2)",...] สำหรับ TGAT2
    ไม่ใส่ = ใช้ ก. ข. ค. ง. จ. ตามสไตล์เดิม"""
    ims = [Image.open(os.path.join(IMG, f)) for f in files]
    h = max(i.height for i in ims)
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    im = Image.new("RGB", (W*S, (h + (labh if lab else 0))*S), "white")
    d = ImageDraw.Draw(im); f = font(16, False); x = 0
    for k, i2 in enumerate(ims):
        im.paste(i2.resize((i2.width*S, i2.height*S), Image.LANCZOS), (x*S, (h - i2.height)*S))
        if lab:
            t = labels[k] if labels else LAB[k] + "."
            tw = d.textlength(t, font=f)
            d.text((x*S + (i2.width*S - tw)/2, (h + 4)*S), t, font=f, fill=INK)
        x += i2.width + gap
    return _save(im, W, h + (labh if lab else 0), name)

def vstack(files, name, gap=10):
    """ต่อภาพในแนวตั้ง จัดกึ่งกลางแนวนอน — ใช้ประกอบเมทริกซ์รูปภาพจากแถวย่อย"""
    ims = [Image.open(os.path.join(IMG, f)) for f in files]
    W = max(i.width for i in ims)
    H = sum(i.height for i in ims) + gap * (len(ims) - 1)
    im = Image.new("RGB", (W * S, H * S), "white")
    y = 0
    for i2 in ims:
        im.paste(i2.resize((i2.width * S, i2.height * S), Image.LANCZOS),
                 (((W - i2.width) // 2) * S, y * S))
        y += i2.height + gap
    return _save(im, W, H, name)

def compose(files, name, seps=None, gap=18, capt=None, capth=22):
    """ต่อภาพในแนวนอน คั่นด้วยข้อความ (เช่น : กับ ::) และมีคำบรรยายใต้ภาพได้"""
    ims = [Image.open(os.path.join(IMG, f)) for f in files]
    f = font(20, True); fc = font(15, False)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    sepw = [int(tmp.textlength(s, font=f)/S) + gap if s else 0 for s in (seps or [""]*(len(ims)-1))]
    h = max(i.height for i in ims)
    W = sum(i.width for i in ims) + gap*(len(ims)-1) + sum(sepw)
    H = h + (capth if capt else 0)
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    x = 0
    for k, i2 in enumerate(ims):
        im.paste(i2.resize((i2.width*S, i2.height*S), Image.LANCZOS), (x*S, int((h - i2.height)/2)*S))
        if capt and capt[k]:
            tw = d.textlength(capt[k], font=fc)
            d.text((x*S + (i2.width*S - tw)/2, (h + 2)*S), capt[k], font=fc, fill=(90, 100, 104))
        x += i2.width
        if k < len(ims) - 1:
            s = (seps or [""]*(len(ims)-1))[k]
            if s:
                tw = d.textlength(s, font=f)
                d.text((x*S + (gap*S + sepw[k]*S - tw)/2, (h/2 - 14)*S), s, font=f, fill=INK)
            x += gap + sepw[k]
    return _save(im, W, H, name)

# ---------------------------------------------------------------- header flowchart
BOXES = [("ตัวเลข", "15 ข้อ"), ("มิติสัมพันธ์", "15 ข้อ"), ("เชิงกล", "15 ข้อ"),
         ("เชิงวิทย์", "15 ข้อ"), ("ข่าวสาร", "10 ข้อ")]
GROUPS = [("คณิต", 0, 1), ("ฟิสิกส์", 2, 3), ("ข่าว", 4, 4)]
ACTIVE = [(0, 213, 201), (40, 161, 171), (0, 200, 181), (40, 161, 171), (213, 0, 77)]
DIM    = (183, 190, 192)

def header(active, name, bw=172, bh=74, gapin=14, gapout=38, pad=6):
    """active = set ของ index กล่องที่ยังใช้งาน  ที่เหลือเป็นสีจาง"""
    xs, x = [], pad
    for i in range(5):
        xs.append(x)
        x += bw + (gapout if i in (1, 3) else gapin)
    W = x - gapin + pad
    H = pad + bh + 18 + 30
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    ftitle = font(25, True); fsub = font(17, False); fgrp = font(15, True)
    for i, (t1, t2) in enumerate(BOXES):
        on = i in active
        col = ACTIVE[i] if on else DIM
        x0, y0 = xs[i]*S, pad*S
        d.rounded_rectangle([x0, y0, x0 + bw*S, y0 + bh*S], radius=9*S,
                            fill="white", outline=(31,37,40) if on else (208,213,215), width=int(1.6*S))
        tw = d.textlength(t1, font=ftitle)
        d.text((x0 + (bw*S - tw)/2, y0 + bh*S*0.10), t1, font=ftitle, fill=col)
        tw = d.textlength(t2, font=fsub)
        d.text((x0 + (bw*S - tw)/2, y0 + bh*S*0.52), t2, font=fsub,
               fill=(70,80,84) if on else DIM)
    yb = (pad + bh + 9)*S
    for gname, a, b in GROUPS:
        on = a in active
        col = ACTIVE[a] if on else DIM
        x0, x1 = xs[a]*S, (xs[b] + bw)*S
        d.line([x0, yb, x1, yb], fill=col, width=max(1, int(1.4*S)))
        d.line([x0, yb - 4*S, x0, yb], fill=col, width=max(1, int(1.4*S)))
        d.line([x1, yb - 4*S, x1, yb], fill=col, width=max(1, int(1.4*S)))
        tw = d.textlength(gname, font=fgrp)
        d.text(((x0 + x1)/2 - tw/2, yb + 3*S), gname, font=fgrp, fill=col)
    return _save(im, W, H, name)


# ---------------------------------------------------------------- badge (gradient)
GRAD = [(0, 213, 201), (0, 200, 181), (40, 161, 171)]
def badge(text, name, padx=16, pady=7, fs=19):
    f = font(fs, True)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = int(tmp.textlength(text, font=f) / S)
    W, H = tw + padx*2, int(fs*1.55) + pady*2
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    for x in range(W*S):
        t = x / max(1, W*S - 1)
        if t < .5:
            a, b, u = GRAD[0], GRAD[1], t*2
        else:
            a, b, u = GRAD[1], GRAD[2], (t-.5)*2
        d.line([x, 0, x, H*S], fill=tuple(int(a[i] + (b[i]-a[i])*u) for i in range(3)))
    d.text(((W*S - tw*S)/2, pady*S*0.55), text, font=f, fill=(255, 255, 255))
    return _save(im, W, H, name)


# ------------------------------------------------- รูปคลี่รูปทรงอิสระ (ไม่ใช่แค่กากบาท)
def netshape(cells, labels, name, cell=38, pad=8):
    """cells = set ของ (r,c) · labels = dict (r,c) -> ตัวอักษร"""
    rs = [r for r, _ in cells]; cs = [c for _, c in cells]
    r0, c0 = min(rs), min(cs)
    R, C = max(rs) - r0 + 1, max(cs) - c0 + 1
    W, H = C*cell + pad*2, R*cell + pad*2
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    f = font(19, True)
    for (r, c) in sorted(cells):
        x0, y0 = (pad + (c-c0)*cell)*S, (pad + (r-r0)*cell)*S
        d.rectangle([x0, y0, x0 + cell*S, y0 + cell*S], fill=TOPF, outline=INK, width=S)
        t = labels.get((r, c), "")
        if t:
            tw = d.textlength(t, font=f)
            d.text((x0 + (cell*S - tw)/2, y0 + cell*S*.18), t, font=f, fill=INK)
    return _save(im, W, H, name)

# ------------------------------------------------- ป้ายระดับความยาก
LVCOL = {1: (0, 200, 181), 2: (40, 161, 171), 3: (213, 0, 77)}
def levelchip(text, lv, name, padx=14, pady=6, fs=17):
    f = font(fs, True)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = int(tmp.textlength(text, font=f) / S)
    W, H = tw + padx*2, int(fs*1.55) + pady*2
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    col = LVCOL[lv]
    d.rectangle([0, 0, W*S-1, H*S-1], fill=col)
    d.text(((W*S - tw*S)/2, pady*S*0.55), text, font=f, fill=(255, 255, 255))
    return _save(im, W, H, name)


# ---------------------------------------------------------------- ดาวระดับความยาก
STARCOL = (213, 0, 77)
def stars(n, name, size=26, gap=6, pad=2, total=3):
    import math
    W = total*size + (total-1)*gap + pad*2
    H = size + pad*2
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    for i in range(total):
        cx = (pad + i*(size+gap) + size/2)*S
        cy = (pad + size/2)*S + size*S*0.03
        R = size*S*0.50
        pts = []
        for k in range(10):
            ang = math.radians(-90 + k*36)
            rr = R if k % 2 == 0 else R*0.44
            pts.append((cx + rr*math.cos(ang), cy + rr*math.sin(ang)))
        if i < n:
            d.polygon(pts, fill=STARCOL)
        else:
            d.polygon(pts, fill=(255, 255, 255), outline=STARCOL, width=max(1, int(S*0.9)))
    return _save(im, W, H, name)

# ---------------------------------------------------------------- ตัวอย่างไว้ตรวจด้วยตา
if __name__ == "__main__":
    # รัน `python draw.py` แล้วเปิดไฟล์ img/zz*.png ดู — ไฟล์ขึ้นต้น zz คือของสาธิต ไม่ใช่รูปโจทย์
    import random
    rnd = random.Random(7)
    out = []

    # ---- plate: มีเส้น / ไม่มีเส้น / ตารางใหญ่ / ไม่มีกรอบ+มีโทนเทา
    m = [[1 if (r + c) % 3 == 0 else 0 for c in range(5)] for r in range(5)]
    out += [plate(m, "zzplate_grid", cell=20),
            plate(m, "zzplate_nogrid", cell=20, grid=False),
            plate([[0, 1, 0], [1, 2, 1], [0, 1, 0]], "zzplate_tone", cell=24, frame=False)]
    strip(out, "zzsheet_plate", gap=22, lab=False)

    # ---- plate ขนาดแผ่นบังแสงจริง 12x12 พร้อมผลซ้อน (AND ของรูทั้งสองแผ่น)
    A = [[1 if rnd.random() < .55 else 0 for _ in range(12)] for _ in range(12)]
    B = [[1 if rnd.random() < .55 else 0 for _ in range(12)] for _ in range(12)]
    AND = [[1 if (A[r][c] or B[r][c]) else 0 for c in range(12)] for r in range(12)]
    strip([plate(A, "zzmaskA", cell=13), plate(B, "zzmaskB", cell=13),
           plate(AND, "zzmaskC", cell=13)], "zzsheet_mask", gap=26, lab=False)

    # ---- symbox: ทุกรูป x ทุกการเติมสี
    names = ["circle"] + sorted(SHAPES)
    for fl in ("white", "grey", "black"):
        strip([symbox([{"shape": s, "fill": fl}], "zzs_%s_%s" % (fl, s)) for s in names],
              "zzsheet_fill_" + fl, gap=14, lab=False)

    # ---- symbox: ทุกตำแหน่ง (เดี่ยว ๆ และรวมทั้งห้าตำแหน่งในกรอบเดียว)
    ps = ["c", "tl", "tr", "bl", "br"]
    cells = [symbox([{"shape": "square", "fill": "black", "pos": p}], "zzs_pos_" + p) for p in ps]
    cells.append(symbox([{"shape": "circle", "fill": "grey", "size": .24},
                         {"shape": "triangle", "pos": "tl"},
                         {"shape": "cross", "fill": "black", "pos": "tr"},
                         {"shape": "star", "fill": "black", "pos": "bl"},
                         {"shape": "diamond", "fill": "white", "pos": "br"}], "zzs_pos_all"))
    strip(cells, "zzsheet_pos", gap=14, lab=False)

    # ---- symbox: หมุนครบสี่ค่า (star กับ arrow ต้องหมุนจริง · circle หมุนแล้วเหมือนเดิมแต่ต้องไม่ error)
    for sh in ("star", "arrow", "triangle", "square", "circle"):
        strip([symbox([{"shape": sh, "fill": "white", "rot": a}], "zzs_rot_%s_%d" % (sh, a))
               for a in (0, 90, 180, 270)], "zzsheet_rot_" + sh, gap=14, lab=False)
    # หมุนสัญลักษณ์สี่มุมพร้อมกัน = ไทล์อนุกรมแนว "ผังหมุน" (แต่ละไทล์คือไทล์ก่อนหน้าหมุน 90 องศา)
    cn = ["tl", "tr", "br", "bl"]                       # เรียงตามเข็มนาฬิกา
    sh4 = ["arrow", "star", "triangle", "square"]
    strip([symbox([{"shape": sh4[k], "fill": "black", "pos": cn[(k + i) % 4], "rot": 90 * i}
                   for k in range(4)], "zzs_rot4_%d" % i) for i in range(4)],
          "zzsheet_rot_four", gap=14, lab=False)

    # ---- symbox: รูปซ้อนรูปแบบช่องเมทริกซ์ 3x3 (รูปนอกใหญ่ + รูปในเล็ก)
    outer = ["triangle", "square", "circle"]
    inner = ["circle", "star", "diamond"]
    tone  = ["white", "grey", "black"]
    strip([symbox([{"shape": outer[r], "fill": "white", "size": .78},
                   {"shape": inner[c], "fill": tone[(r + c) % 3], "size": .30}],
                  "zzs_mx_%d%d" % (r, c), size=64)
           for r in range(3) for c in range(3)], "zzsheet_matrix", gap=12, lab=False)

    # ---- symbox: ไม่มีกรอบ (ตัวลวงในแนวเมทริกซ์) และรูปหลายตัวในกรอบเดียว
    strip([symbox([{"shape": "hexagon", "fill": "grey"}], "zzs_nf1", frame=False),
           symbox([{"shape": "plus", "fill": "black"}], "zzs_nf2", frame=False),
           symbox([{"shape": "arrow", "fill": "white", "rot": 90}], "zzs_nf3", frame=False),
           symbox([{"shape": "pentagon", "fill": "white", "size": .9},
                   {"shape": "plus", "fill": "black", "size": .28}], "zzs_nf4")],
          "zzsheet_noframe", gap=18, lab=False)

    print("ตัวอย่างวาดเสร็จแล้ว — ดูไฟล์ img/zz*.png")

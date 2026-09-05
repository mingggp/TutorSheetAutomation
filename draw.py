#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ตัววาดรูปทั้งหมดสำหรับชีท TPAT3"""
import os, hashlib
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
HI = 3        # รูปเล็กที่ต้องคมตอนพิมพ์ (โลโก้ ดาว ชิป) เก็บที่ความละเอียด HI เท่า

SAVED = {}     # ชื่อรูป -> จำนวนครั้งที่ถูกเขียน ใช้ดักชื่อชนกันระหว่างเครื่องผลิตคนละตัว
HASH  = {}     # ชื่อรูป -> ภาพย่อขาวดำ 64x64 ใช้ดักตัวเลือกที่ซ้ำกับโจทย์
STRIPS = {}    # ชื่อแถบตัวเลือก -> ไฟล์ที่เอามาต่อกัน ใช้ย้อนดูว่าตัวเลือกไหนคือรูปอะไร
HIRES = {}     # ชื่อรูป -> เก็บที่ความละเอียดกี่เท่า (sharpen.py แตะได้เฉพาะที่ > 1)


def _save(im, W, H, name, hi=1):
    """hi = เก็บไฟล์ที่ความละเอียดกี่เท่าของขนาดที่จะแสดงจริง

    รูปเล็ก ๆ อย่างโลโก้กับดาว ถ้าเก็บเท่าขนาดแสดงจะได้แค่ ~155 dpi ตอนพิมพ์
    ขอบตัวอักษรจะฟุ้ง ต้องเก็บ 3 เท่าแล้วให้ build.js ย่อลงตอนวาง (ธง hi ใน pic())
    """
    im = im.resize((W * hi, H * hi), Image.LANCZOS)
    SAVED[name] = SAVED.get(name, 0) + 1
    HIRES[name] = hi
    # ย่อเป็นขาวดำ 64x64 ก่อนทำลายนิ้วมือ รูปเดียวกันคนละขนาดจะได้ค่าตรงกัน
    # เก็บเป็นภาพย่อ ไม่ใช่ค่าแฮช เพราะโจทย์กับตัวเลือกมักวาดคนละขนาด
    # (rt3stem วาด cell=26 ส่วนตัวเลือก cell=22) ค่าแฮชจึงไม่ตรงกันทั้งที่เป็นรูปเดียวกัน
    HASH[name] = (W * hi, H * hi,
                  im.convert("L").resize((64, 64), Image.LANCZOS).tobytes())
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

# มุมทั้งสี่ของหน้าที่มองเห็น เรียงเป็น (ซ้ายบน, ขวาบน, ขวาล่าง, ซ้ายล่าง) แบบตัวอักษรตั้งตรง
_CORNERS = {
    "top":   [(0,0,1), (1,0,1), (1,1,1), (0,1,1)],
    "left":  [(0,1,1), (1,1,1), (1,1,0), (0,1,0)],
    "right": [(1,1,1), (1,0,1), (1,0,0), (1,1,0)],
}

def _order_quad(corners, rt, dn):
    """เรียงมุมใหม่ตามแกนของกระดาษ (rt = ขวามือของกระดาษ, dn = ด้านล่างของกระดาษ)

    ส่งลำดับนี้เข้า _glyph_on_quad แล้วตัวอักษรจะไปวางตะแคงตรงกับที่พับมาจริง

    กติกาของชุดมุมนี้คือ n = rt x dn  ผู้เรียกต้องส่งแกนที่อยู่ใน "พิกัดของภาพ" มาแล้ว
    (ดู gen.oriented ที่สลับแกน x กับ y ก่อน เพราะการฉายภาพของ iso เป็นภาพกลับด้าน)
    """
    dot = lambda p, v: p[0]*v[0] + p[1]*v[1] + p[2]*v[2]
    s = sorted(corners, key=lambda p: (dot(p, dn), dot(p, rt)))
    return [s[0], s[1], s[3], s[2]]

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
        for key, lab in zip(("top", "left", "right"), labels):
            if not lab: continue
            if isinstance(lab, str):
                txt, corn = lab, _CORNERS[key]          # ตั้งตรงตามค่าเริ่มต้น
            else:
                txt, rt, dn = lab                       # ตะแคงตามที่กระดาษพับมาจริง
                corn = _order_quad(_CORNERS[key], rt, dn)
            im.paste(*_glyph_on_quad(txt, [P(*c) for c in corn]))
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
    STRIPS[name] = list(files)
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

def arrow(name, w=46, h=30):
    """ลูกศรโปร่งชี้ขวา วาดเป็นรูป ไม่ใช้ตัวอักษร

    ฟอนต์ Sarabun ไม่มีอักขระ → กับ │ ถ้าเอาไปใส่เป็นข้อความจะขึ้นเป็นกล่องว่าง
    ข้อสอบจริงก็ใช้ลูกศรโปร่งที่วาดเองเหมือนกัน
    """
    im = Image.new("RGB", (w * S, h * S), "white"); d = ImageDraw.Draw(im)
    X = lambda t: t * w * S
    Y = lambda t: t * h * S
    d.polygon([(X(0), Y(.32)), (X(.58), Y(.32)), (X(.58), Y(.06)),
               (X(1), Y(.5)), (X(.58), Y(.94)), (X(.58), Y(.68)), (X(0), Y(.68))],
              fill="white", outline=INK, width=max(1, S))
    return _save(im, w, h, name)


def divider(name, w=14, h=64):
    """เส้นแบ่งแนวตั้ง ใช้คั่นกรอบตัวอย่างกับกรอบคำถาม"""
    im = Image.new("RGB", (w * S, h * S), "white"); d = ImageDraw.Draw(im)
    d.line([(w * S // 2, 0), (w * S // 2, h * S)], fill=LINEG, width=max(1, S))
    return _save(im, w, h, name)


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

def header(active, name, bw=172, bh=74, gapin=14, gapout=38, pad=6,
           boxes=None, groups=None):
    """flowchart โครงสร้างข้อสอบใต้หัวกระดาษ

    boxes/groups ไม่ใส่ = ใช้ผังของ TPAT3 · ใส่มา = วาดผังของวิชาอื่น
    boxes  = [(ชื่อท่อน, จำนวนข้อ), ...]
    groups = [(ชื่อกลุ่ม, ดัชนีเริ่ม, ดัชนีจบ), ...] วงเล็บครอบท่อนที่อยู่กลุ่มเดียวกัน"""
    boxes = boxes or BOXES
    groups = groups or GROUPS
    """active = set ของ index กล่องที่ยังใช้งาน  ที่เหลือเป็นสีจาง"""
    xs, x = [], pad
    for i in range(5):
        xs.append(x)
        x += bw + (gapout if i in (1, 3) else gapin)
    W = x - gapin + pad
    H = pad + bh + 18 + 30
    im = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(im)
    ftitle = font(25, True); fsub = font(17, False); fgrp = font(15, True)
    for i, (t1, t2) in enumerate(boxes):
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
    for gname, a, b in groups:
        on = a in active
        col = ACTIVE[a] if on else DIM
        x0, x1 = xs[a]*S, (xs[b] + bw)*S
        d.line([x0, yb, x1, yb], fill=col, width=max(1, int(1.4*S)))
        d.line([x0, yb - 4*S, x0, yb], fill=col, width=max(1, int(1.4*S)))
        d.line([x1, yb - 4*S, x1, yb], fill=col, width=max(1, int(1.4*S)))
        tw = d.textlength(gname, font=fgrp)
        d.text(((x0 + x1)/2 - tw/2, yb + 3*S), gname, font=fgrp, fill=col)
    return _save(im, W, H, name, hi=HI)


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
    return _save(im, W, H, name, hi=HI)


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
    return _save(im, W, H, name, hi=HI)


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
    return _save(im, W, H, name, hi=HI)

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


# ================================================================ เชิงกล (วีคฟิสิกส์)
# ของจริงถามแนว "อ่านรูปแล้วตัดสิน" เป็นหลัก ฟังก์ชันสามตัวนี้จึงต้องวาดรูปที่อ่านออกชัด
# ตัวเลขสำคัญ (จำนวนฟัน ระยะ น้ำหนัก) พิมพ์กำกับในรูปเสมอ ไม่ให้เด็กต้องเดาจากขนาด

def _gear_teeth(node):
    """node = จำนวนฟัน (เฟืองเดี่ยว) หรือ (ฟันวงใน, ฟันวงนอก) สำหรับเฟืองซ้อนเพลา"""
    return (node, node) if isinstance(node, int) else (node[0], node[1])


def gear_positions(nodes, parents=None, angles=None, unit=2.0):
    """คำนวณจุดศูนย์กลางและรัศมีของเฟืองทุกตัว ให้ผู้เรียกเอาไปตรวจการชนกันก่อนวาด

    parents[i] = ดัชนีของเฟืองที่ตัว i ไปขบด้วย (ต้องน้อยกว่า i) ถ้าไม่ส่งมาถือว่าต่อเป็นแถว
    โครงแบบต้นไม้ทำให้แตกกิ่งไปหลายทิศได้ ไม่ใช่เรียงเส้นเดียว
    """
    import math
    T = [_gear_teeth(n) for n in nodes]
    R = [(max(9.0, a * unit), max(9.0, b * unit)) for a, b in T]
    par = list(parents or [i - 1 for i in range(len(nodes))])
    ang = list(angles or [0] * (len(nodes) - 1))
    cx, cy = [0.0], [0.0]
    for i in range(1, len(nodes)):
        pi = par[i]
        dist = R[pi][1] + R[i][0]
        a = math.radians(ang[i - 1])
        cx.append(cx[pi] + dist * math.cos(a))
        cy.append(cy[pi] + dist * math.sin(a))
    return cx, cy, [max(r) for r in R], par


def gears(nodes, name, names=None, spin=None, angles=None, parents=None, unit=2.0, pad=18):
    """ชุดเฟือง — วางเรียงเป็นเส้นตรงหรือหักมุมก็ได้ และรองรับเฟืองซ้อนเพลา

    nodes[i] = จำนวนฟัน                          เฟืองเดี่ยว
             = (ฟันที่ขบตัวก่อน, ฟันที่ขบตัวถัดไป)   เฟืองสองวงบนเพลาเดียวกัน
    angles[i] = มุมที่ตัวถัดไปวางเอียงจากแนวนอน (องศา) ยาว len(nodes)-1
    spin = (ดัชนีเฟืองที่โจทย์บอกทิศ, True ถ้าตามเข็ม)

    **เฟืองซ้อนเพลาสำคัญตรงที่มันทำให้อัตราทดคูณกัน** เฟืองเรียงธรรมดาตัวกลางไม่มีผล
    แต่พอมีเฟืองซ้อนเพลาแล้ว ตัวกลางมีผลทันที ซึ่งเป็นกับดักหลักของแนวนี้
    """
    import math
    T = [_gear_teeth(n) for n in nodes]
    R = [(max(9.0, a * unit), max(9.0, b * unit)) for a, b in T]
    cx, cy, rad, _par = gear_positions(nodes, parents, angles, unit)
    x0 = min(c - r for c, r in zip(cx, rad)) - pad
    y0 = min(c - r for c, r in zip(cy, rad)) - pad - (12 if spin is not None else 0)
    W = int(max(c + r for c, r in zip(cx, rad)) + pad - x0)
    H = int(max(c + r for c, r in zip(cy, rad)) + pad + 20 - y0)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    f, fl = font(13, True), font(14, True)

    def ring(X, Y, rr, teeth, fill):
        d.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=fill, outline=INK, width=max(1, S))
        for k in range(teeth):
            a = 2 * math.pi * k / teeth
            d.line([X + math.cos(a) * rr * 0.82, Y + math.sin(a) * rr * 0.82,
                    X + math.cos(a) * rr, Y + math.sin(a) * rr], fill=INK, width=max(1, S))

    later = []
    for i, node in enumerate(nodes):
        X, Y = (cx[i] - x0) * S, (cy[i] - y0) * S
        ti, to = T[i]
        ri, ro = R[i][0] * S, R[i][1] * S
        if ti == to:
            ring(X, Y, ro, to, TOPF)
            hr = ro * 0.58
            d.ellipse([X - hr, Y - hr, X + hr, Y + hr], fill="white", outline=LINEG, width=max(1, S))
            lab = str(to)
            d.text((X - d.textlength(lab, font=f) / 2, Y - 9 * S), lab, font=f, fill=INK)
        else:
            big, small = (ro, ri) if ro > ri else (ri, ro)
            bt, st = (to, ti) if ro > ri else (ti, to)
            ring(X, Y, big, bt, TOPF)
            ring(X, Y, small, st, LEFTF)      # วงในสีเข้มกว่า ให้เห็นว่าเป็นคนละวง
            hr = small * 0.5
            d.ellipse([X - hr, Y - hr, X + hr, Y + hr], fill="white", outline=LINEG, width=max(1, S))
            d.text((X - d.textlength(str(st), font=f) / 2, Y - 8 * S), str(st), font=f, fill=INK)
            later.append((X, Y + big * 0.60, str(bt)))   # เลขวงนอก วาดทีหลังกันโดนทับ
    for X, Y, txt in later:
        tw = d.textlength(txt, font=f)
        d.rectangle([X - tw / 2 - 3 * S, Y - 2 * S, X + tw / 2 + 3 * S, Y + 17 * S], fill="white")
        d.text((X - tw / 2, Y), txt, font=f, fill=INK)

    if names:
        # วาดป้ายชื่อทีหลังทั้งหมด ไม่งั้นเฟืองตัวถัดไปจะทับป้ายของตัวก่อนหน้า
        # (เห็นชัดตอนวางหักมุม เพราะเฟืองสองตัวมาอยู่ใกล้กันในแนวดิ่ง)
        for i, node in enumerate(nodes):
            X, Y = (cx[i] - x0) * S, (cy[i] - y0) * S
            rr = max(R[i]) * S
            nm = names[i]
            tw = d.textlength(nm, font=fl)
            d.rectangle([X - tw / 2 - 3 * S, Y + rr + 3 * S,
                         X + tw / 2 + 3 * S, Y + rr + 21 * S], fill="white")
            d.text((X - tw / 2, Y + rr + 4 * S), nm, font=fl, fill=INK)

    if spin is not None:
        i, cwise = spin
        X, Y = (cx[i] - x0) * S, (cy[i] - y0) * S
        ar = max(R[i]) * S * 1.42
        d.arc([X - ar, Y - ar, X + ar, Y + ar], 202, 338, fill=INK, width=max(1, S))
        a = math.radians(338 if cwise else 202)
        px, py = X + math.cos(a) * ar, Y + math.sin(a) * ar
        sz = 5 * S
        tg = (-math.sin(a), math.cos(a)) if cwise else (math.sin(a), -math.cos(a))
        d.polygon([(px + tg[0] * sz, py + tg[1] * sz),
                   (px - tg[0] * sz * .3 - math.cos(a) * sz, py - tg[1] * sz * .3 - math.sin(a) * sz),
                   (px - tg[0] * sz * .3 + math.cos(a) * sz, py - tg[1] * sz * .3 + math.sin(a) * sz)],
                  fill=INK)
    return _save(im, W, H, name)


def beam(marks, name, span=8, unit=17, pad=14, dimq=None):
    """คานบนจุดหมุนสามเหลี่ยม — marks = [(ตำแหน่งนับเป็นขีด, ป้าย)] ลบคือฝั่งซ้าย

    **ไม่พิมพ์ตัวเลขระยะกำกับ** วาดขีดห่างเท่า ๆ กันบนคานให้นับเอาเอง
    ซึ่งเป็นวิธีที่ข้อสอบจริงใช้ ตัวเลขกำกับทำให้รกและทำให้ข้อง่ายลงโดยไม่จำเป็น

    ผู้เรียกต้องเว้นตำแหน่งให้ห่างกันอย่างน้อย 2 ขีด ไม่งั้นกล่องน้ำหนักจะซ้อนกัน
    (2 ขีด = 34 จุด ส่วนกล่องกว้าง 30 จุด)

    dimq = ดัชนีของก้อนที่ *ระยะ* เป็นสิ่งที่โจทย์ถาม จะลากเส้นบอกระยะจากจุดหมุนไปหาก้อนนั้น
    แล้วติดเครื่องหมายคำถามไว้บนเส้น ไม่ใช่ในกล่อง
    เพราะถ้าใส่ ? ไว้ในกล่องทั้งที่โจทย์บอกมวลมาแล้ว คนอ่านจะนึกว่าตำแหน่งก้อนถูกตรึงไว้แล้ว
    """
    BW = 15
    W = int(span * 2 * unit + pad * 2 + BW * 2)
    H = int(pad * 2 + (112 if dimq is not None else 92))
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    mid = W / 2 * S
    y0 = (pad + 46) * S
    f = font(13, True)
    d.rectangle([(pad + BW) * S, y0, (W - pad - BW) * S, y0 + 7 * S],
                fill=TOPF, outline=INK, width=lw)
    for k in range(-span, span + 1):
        X = mid + k * unit * S
        d.line([X, y0 + 7 * S, X, y0 + (11 if k else 7) * S], fill=LINEG, width=lw)
    d.polygon([(mid, y0 + 7 * S), (mid - 15 * S, y0 + 30 * S), (mid + 15 * S, y0 + 30 * S)],
              fill=LEFTF, outline=INK)
    d.line([mid - 26 * S, y0 + 30 * S, mid + 26 * S, y0 + 30 * S], fill=INK, width=lw)
    for dist, lab in marks:
        X = mid + dist * unit * S
        d.rectangle([X - BW * S, y0 - 24 * S, X + BW * S, y0],
                    fill="white" if lab == "?" else TOPF, outline=INK, width=lw)
        d.text((X - d.textlength(lab, font=f) / 2, y0 - 20 * S), lab, font=f, fill=INK)
    if dimq is not None:
        X = mid + marks[dimq][0] * unit * S
        yd = y0 + 44 * S
        d.line([mid, y0 + 32 * S, mid, yd + 5 * S], fill=LINEG, width=lw)
        d.line([X, y0 + 7 * S, X, yd + 5 * S], fill=LINEG, width=lw)
        d.line([mid, yd, X, yd], fill=INK, width=lw)
        for xe, sgn in ((mid, 1), (X, -1 if X > mid else 1)):
            pass
        for xe in (mid, X):
            sgn = 1 if xe < X else -1
            if xe == X:
                sgn = -1 if X > mid else 1
            d.polygon([(xe, yd), (xe + sgn * 7 * S, yd - 4 * S),
                       (xe + sgn * 7 * S, yd + 4 * S)], fill=INK)
        qm = "?"
        tw = d.textlength(qm, font=f)
        cxq = (mid + X) / 2
        d.rectangle([cxq - tw / 2 - 4 * S, yd - 11 * S, cxq + tw / 2 + 4 * S, yd + 11 * S],
                    fill="white")
        d.text((cxq - tw / 2, yd - 9 * S), qm, font=f, fill=INK)
    return _save(im, W, H, name)


def pulley(n, name, load="W", unit=26, pad=14, mirror=False):
    """ระบบรอก — n คือจำนวนเส้นเชือกที่ช่วยกันรับน้ำหนัก แรงที่ต้องออกคือ W/n

    เชือกเส้นเดียวพาดสลับขึ้นลง ปลายหนึ่งต้องมีจุดยึดเสมอ จุดยึดอยู่ที่ไหนขึ้นกับ n
      n คู่  ปลายผูกไว้กับเพดาน  แล้วอ้อมรอกล่างเป็นคู่แรก
      n คี่  ปลายผูกไว้กับรอกล่าง แล้วอ้อมรอกบนเป็นคู่แรก
    ถ้าวาดผิดข้อนี้ รูปจะกลายเป็นเชือกที่ไม่ได้ยึดกับอะไรเลย ซึ่งยกของไม่ขึ้น

    mirror = สลับซ้ายขวา ใช้เปลี่ยนหน้าตารูปเมื่อชีทมีข้อแนวรอกหลายข้อ
    รอกล่างต้องลอยเหนือคานของบล็อกเคลื่อนที่ ไม่ใช่จมลงไปในคาน
    ไม่งั้นคนอ่านจะนึกว่ารอกฝังอยู่ในแท่ง แล้วนับเส้นเชือกผิด
    """
    RS, WRAP = 7, 11
    W = int(unit * (n - 1) + pad * 2 + 64)
    H = int(pad * 2 + 168)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    yc = (pad + 14) * S
    yb = (pad + 96) * S
    ybar = yb + (WRAP + 9) * S
    x0 = pad + 22
    xs = [(x0 + i * unit) * S for i in range(n)]
    fx = xs[-1] + 30 * S
    MX = W * S
    flip = (lambda x: MX - x) if mirror else (lambda x: x)

    d.rectangle([pad * S, (pad + 2) * S, (W - pad) * S, yc - 8 * S],
                fill=LEFTF, outline=INK, width=lw)
    for x in xs:
        d.line([flip(x), yc, flip(x), yb], fill=INK, width=lw)

    def sheave(xa, xb, y, lower):
        cx = (xa + xb) / 2
        d.arc([min(flip(xa), flip(xb)), y - WRAP * S, max(flip(xa), flip(xb)), y + WRAP * S],
              0 if lower else 180, 180 if lower else 360, fill=INK, width=lw)
        d.ellipse([flip(cx) - RS * S, y - RS * S, flip(cx) + RS * S, y + RS * S],
                  fill=TOPF, outline=INK, width=lw)
        return cx

    for i in range(n - 1):
        low = (i % 2) == (n % 2)
        cx = sheave(xs[i], xs[i + 1], yb if low else yc, low)
        if low:
            d.line([flip(cx), yb + RS * S, flip(cx), ybar], fill=INK, width=lw)
    left = min(flip(xs[0] - 13 * S), flip(xs[-1] + 13 * S))
    right = max(flip(xs[0] - 13 * S), flip(xs[-1] + 13 * S))
    d.rectangle([left, ybar, right, ybar + 13 * S], fill=LEFTF, outline=INK, width=lw)
    if n % 2 == 0:
        d.line([flip(xs[0]), yc - 8 * S, flip(xs[0]), yc], fill=INK, width=lw)
        d.ellipse([flip(xs[0]) - 4 * S, yc - 12 * S, flip(xs[0]) + 4 * S, yc - 4 * S],
                  fill="white", outline=INK, width=lw)
    else:
        d.line([flip(xs[0]), yb, flip(xs[0]), ybar], fill=INK, width=lw)

    bw, bx = 32 * S, flip((xs[0] + xs[-1]) / 2)
    d.line([bx, ybar + 13 * S, bx, ybar + 28 * S], fill=INK, width=lw)
    d.rectangle([bx - bw / 2, ybar + 28 * S, bx + bw / 2, ybar + 51 * S],
                fill=TOPF, outline=INK, width=lw)
    f = font(14, True)
    d.text((bx - d.textlength(load, font=f) / 2, ybar + 32 * S), load, font=f, fill=INK)
    sheave(xs[-1], fx, yc, False)
    d.line([flip(fx), yc, flip(fx), yc + 42 * S], fill=INK, width=lw)
    d.polygon([(flip(fx), yc + 52 * S), (flip(fx) - 6 * S, yc + 39 * S),
               (flip(fx) + 6 * S, yc + 39 * S)], fill=INK)
    d.text((flip(fx) - d.textlength("F", font=f) / 2, yc + 56 * S), "F", font=f, fill=INK)
    return _save(im, W, H, name)


def pulleystack(k, name, load="W", pad=16, dx=44, dy=40):
    """รอกผสม (รอกทวีกำลัง) — รอกเคลื่อนที่ k ตัวเรียงเป็นชั้น แรงลดครึ่งหนึ่งทุกชั้น

    การผูก: เชือกของรอกชั้นล่างสุดรับน้ำหนัก ปลายข้างหนึ่งยึดเพดาน
    ปลายอีกข้างไปผูกที่ *เพลา* ของรอกชั้นถัดขึ้นไป ทำให้แรงถูกหารสองอีกครั้งทุกชั้น
    ผลคือ F = W / 2^k **ไม่ใช่** W / 2k ซึ่งเป็นกับดักหลักของแนวนี้

    ต่างจาก pulley() ที่เป็นรอกพวงชุดเดียว แรงหารด้วยจำนวนเส้นเชือกตรง ๆ
    """
    RS, WRAP = 9, 13
    W = int(pad * 2 + dx * (k - 1) + 112)
    H = int(pad * 2 + dy * (k - 1) + 132)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    f = font(14, True)
    yc = (pad + 12) * S                                  # ใต้เพดาน
    d.rectangle([pad * S, (pad + 1) * S, (W - pad) * S, yc], fill=LEFTF, outline=INK, width=lw)
    cx = [(pad + 26 + i * dx) * S for i in range(k)]
    cy = [(pad + 96 + dy * (k - 1) - i * dy) * S for i in range(k)]
    for i in range(k):
        xl, xr = cx[i] - WRAP * S, cx[i] + WRAP * S
        d.arc([xl, cy[i] - WRAP * S, xr, cy[i] + WRAP * S], 0, 180, fill=INK, width=lw)
        d.line([xl, yc, xl, cy[i]], fill=INK, width=lw)  # เส้นซ้าย ขึ้นไปยึดเพดาน
        d.ellipse([xl - 4 * S, yc, xl + 4 * S, yc + 8 * S], fill="white", outline=INK, width=lw)
        if i + 1 < k:                                    # เส้นขวา ไปผูกเพลาของรอกชั้นบน
            d.line([xr, cy[i], cx[i + 1], cy[i + 1]], fill=INK, width=lw)
        d.ellipse([cx[i] - RS * S, cy[i] - RS * S, cx[i] + RS * S, cy[i] + RS * S],
                  fill=TOPF, outline=INK, width=lw)
        d.ellipse([cx[i] - 2 * S, cy[i] - 2 * S, cx[i] + 2 * S, cy[i] + 2 * S], fill=INK)
    bw = 34 * S
    d.line([cx[0], cy[0] + RS * S, cx[0], cy[0] + 26 * S], fill=INK, width=lw)
    d.rectangle([cx[0] - bw / 2, cy[0] + 26 * S, cx[0] + bw / 2, cy[0] + 50 * S],
                fill=TOPF, outline=INK, width=lw)
    d.text((cx[0] - d.textlength(load, font=f) / 2, cy[0] + 30 * S), load, font=f, fill=INK)
    # ปลายเชือกชั้นบนสุดต้องพาดรอกคงที่ที่ติดเพดานก่อน ถึงจะดึงลงได้
    # ถ้าลากเส้นหักลงกลางอากาศเฉย ๆ จะกลายเป็นรูปที่ดึงแล้วไม่เกิดอะไรขึ้น
    fx = cx[-1] + (WRAP + 42) * S
    yf = yc + (RS + 3) * S                               # รอกคงที่ ใต้เพดานพอดี
    d.line([fx, yc, fx, yf - RS * S], fill=INK, width=lw)
    d.line([cx[-1] + WRAP * S, cy[-1], fx - RS * S, yf], fill=INK, width=lw)
    d.arc([fx - RS * S, yf - RS * S, fx + RS * S, yf + RS * S], 180, 360, fill=INK, width=lw)
    d.ellipse([fx - RS * S, yf - RS * S, fx + RS * S, yf + RS * S],
              fill=TOPF, outline=INK, width=lw)
    d.ellipse([fx - 2 * S, yf - 2 * S, fx + 2 * S, yf + 2 * S], fill=INK)
    ye = yf + 48 * S
    d.line([fx + RS * S, yf, fx + RS * S, ye], fill=INK, width=lw)
    d.polygon([(fx + RS * S, ye + 11 * S), (fx + RS * S - 6 * S, ye - 2 * S),
               (fx + RS * S + 6 * S, ye - 2 * S)], fill=INK)
    d.text((fx + RS * S - d.textlength("F", font=f) / 2, ye + 15 * S), "F", font=f, fill=INK)
    return _save(im, W, H, name)


def _tickstep(vals, lo=4, hi=12):
    """เลือกระยะขีดที่ *ทุกค่าสำคัญตกลงบนขีดพอดี*

    บั๊กเดิม: ใช้ round(max/5) เป็นระยะขีด ทำให้จุดยอดของกราฟลอยอยู่ระหว่างขีด
    เด็กรู้วิธีทำแต่หาค่าที่จะเอาไปคำนวณไม่ได้ ซึ่งเป็นโจทย์ที่ใช้ไม่ได้เลย

    วิธีแก้: ระยะขีดต้องเป็นตัวหารร่วมของทุกค่าที่พล็อต จากตัวหารทั้งหมดของ ห.ร.ม.
    เลือกตัวที่ทำให้จำนวนขีดอยู่ในช่วงที่อ่านสบาย
    """
    from math import gcd
    nz = [int(v) for v in vals if v]
    mx = max([int(v) for v in vals] + [1])
    if not nz:
        return 1
    g = nz[0]
    for v in nz[1:]:
        g = gcd(g, v)
    divs = sorted(d for d in range(1, g + 1) if g % d == 0)
    ok = [d for d in divs if lo <= mx // d <= hi]
    if ok:
        return max(ok)                      # เส้นน้อยที่สุดที่ยังอ่านสบาย
    fit = [d for d in divs if mx // d <= hi]
    return max(fit) if fit else 1


def vtgraph(pts, name, w=250, h=130, pad=16, xlab="t (s)", ylab="v (m/s)", grid=True):
    """กราฟความเร็ว-เวลาแบบเส้นตรงต่อกัน — pts = [(t, v), ...] เรียงตามเวลา

    พื้นที่ใต้กราฟคือระยะทาง ความชันคือความเร่ง เด็กอ่านค่าจากขีดบนแกนได้ตรง ๆ
    จึงต้องพิมพ์ตัวเลขกำกับขีด ไม่ใช่ให้กะเอาจากรูป
    """
    mt = max(p[0] for p in pts)
    mv = max(p[1] for p in pts)
    L, B = pad + 26, pad + 20
    W, H = w + L + pad, h + B + pad + 6
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    X = lambda t: (L + t / mt * w) * S
    Y = lambda v: (pad + h - v / mv * h) * S
    fs = font(11, False)
    fl = font(11, True)
    tstep = _tickstep([p[0] for p in pts])
    vstep = _tickstep([p[1] for p in pts])
    if grid:
        for t in range(0, int(mt) + 1, tstep):
            d.line([X(t), Y(0), X(t), Y(mv)], fill=(232, 238, 239), width=lw)
        for v in range(0, int(mv) + 1, vstep):
            d.line([X(0), Y(v), X(mt), Y(v)], fill=(232, 238, 239), width=lw)
    d.line([X(0), Y(0), X(mt) + 8 * S, Y(0)], fill=INK, width=lw)
    d.line([X(0), Y(0), X(0), Y(mv) - 8 * S], fill=INK, width=lw)
    for t in range(0, int(mt) + 1, tstep):
        d.line([X(t), Y(0), X(t), Y(0) + 4 * S], fill=INK, width=lw)
        s = str(t)
        d.text((X(t) - d.textlength(s, font=fs) / 2, Y(0) + 6 * S), s, font=fs, fill=INK)
    for v in range(0, int(mv) + 1, vstep):
        d.line([X(0) - 4 * S, Y(v), X(0), Y(v)], fill=INK, width=lw)
        s = str(v)
        d.text((X(0) - 7 * S - d.textlength(s, font=fs), Y(v) - 6 * S), s, font=fs, fill=INK)
    d.text((X(mt) - d.textlength(xlab, font=fl) / 2, Y(0) + 18 * S), xlab, font=fl, fill=INK)
    d.text((X(0) + 5 * S, (pad - 11) * S), ylab, font=fl, fill=INK)
    xy = [(X(t), Y(v)) for t, v in pts]
    d.polygon([(X(0), Y(0))] + xy + [(xy[-1][0], Y(0))], fill=(238, 247, 247))
    d.line(xy, fill=(0, 160, 160), width=max(2, S))
    for p in xy:
        d.ellipse([p[0] - 2 * S, p[1] - 2 * S, p[0] + 2 * S, p[1] + 2 * S], fill=(0, 140, 140))
    return _save(im, W, H, name)


def _ohm(d, x, y, h, lw):
    """วาดอักขระโอห์มเอง เพราะฟอนต์ Sarabun ไม่มีอักขระนี้ (จะขึ้นเป็นกล่องว่าง)

    (x, y) คือมุมซ้ายบนของกรอบตัวอักษร h คือความสูง
    คืนความกว้างที่ใช้ไป เพื่อให้ผู้เรียกจัดกลางได้
    """
    r = h * 0.46
    cx, cy = x + r, y + r + h * 0.04
    d.arc([cx - r, cy - r, cx + r, cy + r], 146, 394, fill=INK, width=max(lw, 2))
    import math
    for a, sgn in ((146, -1), (394, 1)):
        px = cx + math.cos(math.radians(a)) * r
        py = cy + math.sin(math.radians(a)) * r
        d.line([px, py, px + sgn * r * 0.62, py + r * 0.34], fill=INK, width=max(lw, 2))
    return r * 2.4


def ohmlabel(d, cx, y, num, f, lw):
    """พิมพ์ค่าความต้านทานพร้อมหน่วยโอห์ม จัดกลางที่ cx

    วัดกรอบจริงของตัวเลขด้วย textbbox แล้ววางอักขระโอห์มให้สูงเท่ากันและนั่งบนเส้นบรรทัดเดียวกัน
    ถ้ากะจากขนาดฟอนต์ตรง ๆ อักขระจะลอยสูงกว่าตัวเลข เพราะ Sarabun เผื่อที่ด้านบนไว้มาก
    """
    txt = str(num) + " "
    tw = d.textlength(txt, font=f)
    bb = d.textbbox((0, 0), str(num), font=f)      # (x0, y0, x1, y1) ของตัวเลขจริง
    top, bot = bb[1], bb[3]
    oh = bot - top
    ow = oh * 1.30
    x0 = cx - (tw + ow) / 2
    d.text((x0, y), txt, font=f, fill=INK)
    _ohm(d, x0 + tw, y + top, oh, lw)


def _zig(d, x1, x2, y, lw, n=6, amp=7):
    """สัญลักษณ์ตัวต้านทานแบบซิกแซก วาดคร่อมเส้นลวดระหว่าง x1 ถึง x2"""
    body = (x2 - x1) * 0.62
    a = x1 + ((x2 - x1) - body) / 2
    d.line([x1, y, a, y], fill=INK, width=lw)
    pts = [(a, y)]
    for k in range(n):
        pts.append((a + body * (k + 0.5) / n, y + (amp * S if k % 2 == 0 else -amp * S)))
    pts.append((a + body, y))
    d.line(pts, fill=INK, width=lw, joint="curve")
    d.line([a + body, y, x2, y], fill=INK, width=lw)


def circuit(blocks, name, emf=None, bw=54, gap=22, pad=16):
    """วงจรตัวต้านทาน — blocks เรียงกันแบบอนุกรม สายลวดต่อเนื่องตลอด

    แต่ละ block เป็นได้สองแบบ
      "R1"                        ตัวเดียว
      [["R1","R2"], ["R3"]]       ขนานกัน แต่ละสาขาต่ออนุกรมกันได้อีก

    ตัวต้านทานวาดเป็น**สัญลักษณ์ซิกแซกจริง** ไม่ใช่กล่องสี่เหลี่ยม
    และทุกช่องว่างต้องมีเส้นลวดคาดไว้ ไม่งั้นคนอ่านจะนึกว่าเป็นวงจรเปิด
    ตัวเลขไม่ใส่หน่วย เพราะฟอนต์ Sarabun ไม่มีอักขระโอห์ม ต้องไปบอกหน่วยในตัวโจทย์
    """
    BH = 30
    def bwidth(b):
        if isinstance(b, str):
            return bw
        return max(len(br) for br in b) * bw
    def bheight(b):
        return BH if isinstance(b, str) else len(b) * BH + (len(b) - 1) * gap

    tot = sum(bwidth(b) for b in blocks) + gap * (len(blocks) + 1)
    inner = max(bheight(b) for b in blocks)
    W = int(tot + pad * 2 + 46)
    H = int(inner + 104 + pad * 2)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    f = font(12, True)
    ytop = (pad + 26) * S
    ybot = ytop + (inner + 64) * S
    x = pad + 46

    def part(xa, xb, y, lab):
        _zig(d, xa, xb, y, lw)
        ohmlabel(d, (xa + xb) / 2, y - 26 * S, lab, f, lw)

    d.line([(pad + 20) * S, ytop, x * S, ytop], fill=INK, width=lw)
    for b in blocks:
        bwid = bwidth(b)
        if isinstance(b, str):
            part(x * S, (x + bwid) * S, ytop, b)
        else:
            xl, xr = x * S, (x + bwid) * S
            for k, br in enumerate(b):
                yy = ytop + k * (BH + gap) * S
                step = bwid / len(br)
                for j, lab in enumerate(br):
                    part(x * S + j * step * S, x * S + (j + 1) * step * S, yy, lab)
            d.line([xl, ytop, xl, ytop + (len(b) - 1) * (BH + gap) * S], fill=INK, width=lw)
            d.line([xr, ytop, xr, ytop + (len(b) - 1) * (BH + gap) * S], fill=INK, width=lw)
        x += bwid
        d.line([x * S, ytop, (x + gap) * S, ytop], fill=INK, width=lw)   # สายเชื่อมระหว่างบล็อก
        x += gap
    d.line([(x - gap) * S, ytop, (W - pad - 20) * S, ytop], fill=INK, width=lw)
    d.line([(W - pad - 20) * S, ytop, (W - pad - 20) * S, ybot], fill=INK, width=lw)
    d.line([(pad + 20) * S, ytop, (pad + 20) * S, ybot], fill=INK, width=lw)
    d.line([(pad + 20) * S, ybot, (W - pad - 20) * S, ybot], fill=INK, width=lw)
    cx = W / 2 * S
    d.line([cx - 5 * S, ybot - 11 * S, cx - 5 * S, ybot + 11 * S], fill=INK, width=lw)
    d.line([cx + 5 * S, ybot - 6 * S, cx + 5 * S, ybot + 6 * S], fill=INK, width=max(2, S * 2))
    d.rectangle([cx - 5 * S, ybot - lw, cx + 5 * S, ybot + lw], fill="white")
    if emf:
        d.text((cx - d.textlength(emf, font=f) / 2, ybot + 14 * S), emf, font=f, fill=INK)
    return _save(im, W, H, name)


def bridge(labels, name, emf=None, arm=92, pad=20):
    """วงจรบริดจ์ (วีตสโตน) — labels = (บนซ้าย, บนขวา, ล่างซ้าย, ล่างขวา, กลาง)

    สี่เหลี่ยมข้าวหลามตัด มีตัวต้านทานสี่แขน และมีมิเตอร์คาดกลาง
    บริดจ์สมดุลเมื่อ (บนซ้าย)(ล่างขวา) = (บนขวา)(ล่างซ้าย) ซึ่งตอนนั้นมิเตอร์อ่านค่าศูนย์
    เด็กที่ไม่รู้เงื่อนไขนี้จะไปนั่งย่อวงจรแบบอนุกรม-ขนาน ซึ่งย่อไม่ได้
    """
    W, H = int(arm * 2 + pad * 2 + 56), int(arm * 2 + pad * 2 + 46)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    f = font(12, True)
    cx, cy = W / 2 * S, (pad + arm) * S
    L = (cx - arm * S, cy)
    R = (cx + arm * S, cy)
    T = (cx, cy - arm * 0.72 * S)
    B = (cx, cy + arm * 0.72 * S)

    def limb(p, q, lab):
        d.line([p, q], fill=INK, width=lw)
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        r = 13 * S
        d.ellipse([mx - r, my - r, mx + r, my + r], fill="white", outline="white")
        d.line([mx - r, my - r * 0.0, mx + r, my], fill=INK, width=lw)
        _zig(d, mx - 22 * S, mx + 22 * S, my, lw, n=4, amp=5)
        d.rectangle([mx - 12 * S, my - 20 * S, mx + 12 * S, my - 6 * S], fill="white")
        d.text((mx - d.textlength(lab, font=f) / 2, my - 22 * S), lab, font=f, fill=INK)

    for p, q, lab in ((L, T, labels[0]), (T, R, labels[1]),
                      (L, B, labels[2]), (B, R, labels[3])):
        d.line([p, q], fill=INK, width=lw)
    for p, q, lab in ((L, T, labels[0]), (T, R, labels[1]),
                      (L, B, labels[2]), (B, R, labels[3])):
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        d.rectangle([mx - 20 * S, my - 9 * S, mx + 20 * S, my + 9 * S], fill="white")
        _zig(d, mx - 20 * S, mx + 20 * S, my, lw, n=4, amp=5)
        if lab == "?":
            d.text((mx - d.textlength(lab, font=f) / 2, my - 29 * S), lab, font=f, fill=INK)
        else:
            ohmlabel(d, mx, my - 29 * S, lab, f, lw)
    d.line([T, B], fill=INK, width=lw)                     # แขนกลางที่มีมิเตอร์
    gr = 13 * S
    d.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill="white", outline=INK, width=lw)
    d.text((cx - d.textlength(labels[4], font=f) / 2, cy - 9 * S), labels[4], font=f, fill=INK)
    yb = (pad + arm * 2 + 14) * S
    d.line([L[0], L[1], L[0], yb], fill=INK, width=lw)
    d.line([R[0], R[1], R[0], yb], fill=INK, width=lw)
    d.line([L[0], yb, R[0], yb], fill=INK, width=lw)
    d.line([cx - 5 * S, yb - 11 * S, cx - 5 * S, yb + 11 * S], fill=INK, width=lw)
    d.line([cx + 5 * S, yb - 6 * S, cx + 5 * S, yb + 6 * S], fill=INK, width=max(2, S * 2))
    d.rectangle([cx - 5 * S, yb - lw, cx + 5 * S, yb + lw], fill="white")
    if emf:
        d.text((cx - d.textlength(emf, font=f) / 2, yb + 12 * S), emf, font=f, fill=INK)
    return _save(im, W, H, name)


def _switch(d, x, y, lw, lab, f, up=16, below=False):
    """สวิตช์เปิดอยู่ — ขาโยกกางขึ้น วาดเปิดเสมอ เพราะโจทย์ถามว่าต้องปิดตัวไหน"""
    r = 3 * S
    d.ellipse([x - 13 * S - r, y - r, x - 13 * S + r, y + r], fill=INK)
    d.ellipse([x + 13 * S - r, y - r, x + 13 * S + r, y + r], fill=INK)
    d.line([x - 13 * S, y, x + 9 * S, y - up * S], fill=INK, width=lw)
    ly = y + 6 * S if below else y - (up + 20) * S
    d.text((x - d.textlength(lab, font=f) / 2, ly), lab, font=f, fill=INK)


def _bulb(d, x, y, lw, lab, f, r=13):
    """หลอดไฟ — วงกลมมีกากบาทข้างใน ตามสัญลักษณ์มาตรฐาน"""
    rr = r * S
    d.ellipse([x - rr, y - rr, x + rr, y + rr], fill="white", outline=INK, width=lw)
    k = rr * 0.70
    d.line([x - k, y - k, x + k, y + k], fill=INK, width=lw)
    d.line([x - k, y + k, x + k, y - k], fill=INK, width=lw)
    d.text((x - d.textlength(lab, font=f) / 2, y + rr + 3 * S), lab, font=f, fill=INK)


def switchboard(sw, bulbs, name, emf="E", pad=20):
    """วงจรหลอดไฟกับสวิตช์ — โครงตายตัวหนึ่งแบบ ใช้ถามว่าต้องปิดสวิตช์ตัวใดบ้าง

    โครง (S0 เป็นสวิตช์ประธานอยู่บนสายหลัก)
      สาขาบน   S1 อนุกรมกับหลอด L1
      สาขาล่าง S3 อนุกรมกับหลอด L2 แล้วต่อกับ (L3 ขนานกับ S2)

    จุดที่ทำให้ข้อนี้ไม่ง่าย คือ **S2 คร่อมหลอด L3** ปิด S2 แล้ว L3 จะดับ ไม่ใช่ติด
    เพราะกระแสลัดผ่านสวิตช์แทนที่จะผ่านไส้หลอด เด็กที่คิดว่าปิดสวิตช์ = หลอดติดจะพลาดข้อนี้
    """
    W, H = 344, 212
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    f = font(12, True)
    XL, XR = (pad + 14) * S, (W - pad - 14) * S
    Y1, Y2 = (pad + 30) * S, (pad + 94) * S
    YB = (H - pad - 8) * S
    d.line([XL, Y1, XR, Y1], fill=INK, width=lw)          # สาขาบน
    _switch(d, XL + 62 * S, Y1, lw, sw[1], f)
    _bulb(d, XL + 168 * S, Y1, lw, bulbs[0], f)
    d.line([XL, Y2, XR, Y2], fill=INK, width=lw)          # สาขาล่าง
    _switch(d, XL + 44 * S, Y2, lw, sw[3], f)
    _bulb(d, XL + 116 * S, Y2, lw, bulbs[1], f)
    xa, xb = XL + 156 * S, XL + 238 * S                   # ท่อนที่ L3 ขนานกับ S2
    ymid = Y2
    ylow = Y2 + 38 * S
    _bulb(d, (xa + xb) / 2, ymid, lw, bulbs[2], f)
    d.line([xa, ymid, xa, ylow], fill=INK, width=lw)
    d.line([xb, ymid, xb, ylow], fill=INK, width=lw)
    d.line([xa, ylow, xb, ylow], fill=INK, width=lw)
    _switch(d, (xa + xb) / 2, ylow, lw, sw[2], f, up=13, below=True)
    d.line([XL, Y1, XL, Y2], fill=INK, width=lw)
    d.line([XR, Y1, XR, Y2], fill=INK, width=lw)
    d.line([XL, Y2, XL, YB], fill=INK, width=lw)          # สายหลักลงไปหาแบตเตอรี่
    d.line([XR, Y2, XR, YB], fill=INK, width=lw)
    d.line([XL, YB, XR, YB], fill=INK, width=lw)
    _switch(d, XL + 62 * S, YB, lw, sw[0], f, up=14)
    cx = XR - 56 * S
    d.line([cx - 5 * S, YB - 11 * S, cx - 5 * S, YB + 11 * S], fill=INK, width=lw)
    d.line([cx + 5 * S, YB - 6 * S, cx + 5 * S, YB + 6 * S], fill=INK, width=max(2, S * 2))
    d.rectangle([cx - 5 * S, YB - lw, cx + 5 * S, YB + lw], fill="white")
    d.text((cx - d.textlength(emf, font=f) / 2, YB + 14 * S), emf, font=f, fill=INK)
    return _save(im, W, H, name)


def bulb_states(s0, s1, s2, s3):
    """สถานะหลอด (L1, L2, L3) จากสถานะสวิตช์ — True คือปิดสวิตช์ / หลอดติด

    L3 ดับเมื่อ S2 ปิด เพราะกระแสลัดผ่านสวิตช์ที่คร่อมอยู่
    """
    power = s0
    return (power and s1, power and s3, power and s3 and not s2)

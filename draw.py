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

def gears(teeth, name, names=None, spin=None, unit=2.0, pad=16):
    """ชุดเฟืองขบกันเรียงเป็นแถว รัศมีแปรตามจำนวนฟัน

    teeth = จำนวนฟันของแต่ละตัว · names = ป้ายใต้เฟือง เช่น ["ก","ข","ค"]
    spin  = (ดัชนีเฟืองที่โจทย์บอกทิศ, True ถ้าตามเข็ม) วาดลูกศรโค้งกำกับให้ตัวนั้น

    ขีดรอบขอบมีจำนวนเท่าจำนวนฟันจริง เด็กที่อยากนับจึงนับได้ ไม่ใช่รูปประดับ
    """
    import math
    R = [max(9.0, t * unit) for t in teeth]
    cx = [R[0]]
    for i in range(1, len(R)):
        cx.append(cx[-1] + R[i - 1] + R[i])
    top = 26 if spin is not None else 8
    W = int(cx[-1] + R[-1] + pad * 2)
    H = int(max(R) * 2 + pad * 2 + top + 30)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    cy = (pad + top + max(R)) * S
    f = font(13, True)
    fl = font(14, True)
    for i, t in enumerate(teeth):
        X, rr = (cx[i] + pad) * S, R[i] * S
        d.ellipse([X - rr, cy - rr, X + rr, cy + rr], fill=TOPF, outline=INK, width=max(1, S))
        for k in range(t):
            a = 2 * math.pi * k / t
            d.line([X + math.cos(a) * rr * 0.82, cy + math.sin(a) * rr * 0.82,
                    X + math.cos(a) * rr, cy + math.sin(a) * rr], fill=INK, width=max(1, S))
        hr = rr * 0.58
        d.ellipse([X - hr, cy - hr, X + hr, cy + hr], fill="white", outline=LINEG, width=max(1, S))
        lab = str(t)
        d.text((X - d.textlength(lab, font=f) / 2, cy - 9 * S), lab, font=f, fill=INK)
        if names:
            nm = names[i]
            d.text((X - d.textlength(nm, font=fl) / 2, cy + rr + 9 * S), nm, font=fl, fill=INK)
    if spin is not None:
        i, cwise = spin
        X, rr = (cx[i] + pad) * S, R[i] * S
        ar = rr * 1.42
        box = [X - ar, cy - ar, X + ar, cy + ar]
        d.arc(box, 202, 338, fill=INK, width=max(1, S))
        ex = 338 if cwise else 202
        a = math.radians(ex)
        px, py = X + math.cos(a) * ar, cy + math.sin(a) * ar
        s = 5 * S
        tang = (-math.sin(a), math.cos(a)) if cwise else (math.sin(a), -math.cos(a))
        d.polygon([(px + tang[0] * s, py + tang[1] * s),
                   (px - tang[0] * s * .3 - math.cos(a) * s, py - tang[1] * s * .3 - math.sin(a) * s),
                   (px - tang[0] * s * .3 + math.cos(a) * s, py - tang[1] * s * .3 + math.sin(a) * s)],
                  fill=INK)
    return _save(im, W, H, name)


def beam(marks, name, unit=15, pad=14, bar=250):
    """คานบนจุดหมุนสามเหลี่ยม — marks = list ของ (ระยะจากจุดหมุน, ป้าย)

    ระยะติดลบคือฝั่งซ้าย · ป้าย "?" คือช่องที่โจทย์ถาม
    น้ำหนักวางอยู่ *บน* คาน จุดหมุนอยู่ใต้คาน จะได้ไม่บังกัน
    ตัวเลขระยะพิมพ์กำกับไว้เหนือก้อนน้ำหนัก เด็กจึงอ่านโมเมนต์ได้โดยไม่ต้องวัดจากรูป
    """
    W = int(bar + pad * 2)
    H = int(pad * 2 + 96)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    mid = (pad + bar / 2) * S
    y0 = (pad + 52) * S                     # ผิวบนของคาน
    f = font(13, True)
    fs = font(11, False)
    d.rectangle([pad * S, y0, (pad + bar) * S, y0 + 7 * S],
                fill=TOPF, outline=INK, width=max(1, S))
    d.polygon([(mid, y0 + 7 * S), (mid - 15 * S, y0 + 32 * S), (mid + 15 * S, y0 + 32 * S)],
              fill=LEFTF, outline=INK)
    d.line([mid - 26 * S, y0 + 32 * S, mid + 26 * S, y0 + 32 * S], fill=INK, width=max(1, S))
    for dist, lab in marks:
        X = mid + dist * unit * S
        d.rectangle([X - 15 * S, y0 - 25 * S, X + 15 * S, y0],
                    fill="white" if lab == "?" else TOPF, outline=INK, width=max(1, S))
        d.text((X - d.textlength(lab, font=f) / 2, y0 - 21 * S), lab, font=f, fill=INK)
        dl = str(abs(dist))
        d.text((X - d.textlength(dl, font=fs) / 2, y0 - 42 * S), dl, font=fs, fill=LINEG)
    return _save(im, W, H, name)


def pulley(n, name, load="W", unit=26, pad=14):
    """ระบบรอก — n คือจำนวนเส้นเชือกที่ช่วยกันรับน้ำหนัก แรงที่ต้องออกคือ W/n

    เชือกเส้นเดียวพาดสลับขึ้นลง ปลายหนึ่งต้องมีจุดยึดเสมอ จุดยึดอยู่ที่ไหนขึ้นกับ n
      n คู่  ปลายผูกไว้กับเพดาน  แล้วอ้อมรอกล่างเป็นคู่แรก
      n คี่  ปลายผูกไว้กับรอกล่าง แล้วอ้อมรอกบนเป็นคู่แรก
    ถ้าวาดผิดข้อนี้ รูปจะกลายเป็นเชือกที่ไม่ได้ยึดกับอะไรเลย ซึ่งยกของไม่ขึ้น
    """
    W = int(unit * (n - 1) + pad * 2 + 62)
    H = int(pad * 2 + 152)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    yc = (pad + 14) * S                     # ระดับรอกบน (ใต้เพดาน)
    yb = (pad + 100) * S                    # ระดับรอกล่าง
    x0 = pad + 20
    xs = [(x0 + i * unit) * S for i in range(n)]
    d.rectangle([pad * S, (pad + 2) * S, (W - pad) * S, yc - 8 * S],
                fill=LEFTF, outline=INK, width=lw)
    for x in xs:                            # เส้นเชือกแนวดิ่ง
        d.line([x, yc, x, yb], fill=INK, width=lw)
    def sheave(xa, xb, y, lower):
        cx = (xa + xb) / 2
        d.arc([xa, y - 11 * S, xb, y + 11 * S], 0 if lower else 180, 180 if lower else 360,
              fill=INK, width=lw)
        d.ellipse([cx - 7 * S, y - 7 * S, cx + 7 * S, y + 7 * S],
                  fill=TOPF, outline=INK, width=lw)
    for i in range(n - 1):
        low = (i % 2) == (n % 2)            # ที่มาของกฎนี้อยู่ในคำอธิบายด้านบน
        sheave(xs[i], xs[i + 1], yb if low else yc, low)
    d.rectangle([xs[0] - 13 * S, yb, xs[-1] + 13 * S, yb + 14 * S],
                fill=LEFTF, outline=INK, width=lw)
    if n % 2 == 0:                          # จุดยึดที่เพดาน
        d.line([xs[0], yc - 8 * S, xs[0], yc], fill=INK, width=lw)
        d.ellipse([xs[0] - 4 * S, yc - 12 * S, xs[0] + 4 * S, yc - 4 * S],
                  fill="white", outline=INK, width=lw)
    bw, bx = 32 * S, (xs[0] + xs[-1]) / 2
    d.line([bx, yb + 14 * S, bx, yb + 30 * S], fill=INK, width=lw)
    d.rectangle([bx - bw / 2, yb + 30 * S, bx + bw / 2, yb + 54 * S],
                fill=TOPF, outline=INK, width=lw)
    f = font(14, True)
    d.text((bx - d.textlength(load, font=f) / 2, yb + 35 * S), load, font=f, fill=INK)
    fx = xs[-1] + 30 * S                    # ปลายเชือกที่มือดึง
    sheave(xs[-1], fx, yc, False)
    d.line([fx, yc, fx, yc + 44 * S], fill=INK, width=lw)
    d.polygon([(fx, yc + 54 * S), (fx - 6 * S, yc + 41 * S), (fx + 6 * S, yc + 41 * S)], fill=INK)
    d.text((fx - d.textlength("F", font=f) / 2, yc + 58 * S), "F", font=f, fill=INK)
    return _save(im, W, H, name)


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
    tstep = max(1, round(mt / 6))
    vstep = max(1, round(mv / 5))
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


def circuit(blocks, name, emf=None, bw=44, bh=20, gap=26, pad=16):
    """วงจรตัวต้านทาน — blocks เรียงกันแบบอนุกรม

    แต่ละ block เป็นได้สองแบบ
      "R1"                        ตัวเดียว
      [["R1","R2"], ["R3"]]       ขนานกัน แต่ละสาขาเป็นตัวต้านทานต่ออนุกรมกันได้อีก
    โครงนี้พอสำหรับวงจรลึกสองชั้น ซึ่งครอบแนว "ย่อวงจร" ที่ข้อสอบจริงถาม
    """
    LEAD = 15                       # ช่องว่างหัวท้ายสาขา ให้เห็นเส้นลวดที่ต่อขนาน
    def bwidth(b):
        if isinstance(b, str):
            return bw
        n = max(len(br) for br in b)
        return n * bw + (n + 1) * LEAD
    def bheight(b):
        return bh if isinstance(b, str) else len(b) * bh + (len(b) - 1) * gap

    tot = sum(bwidth(b) for b in blocks) + gap * (len(blocks) + 1)
    inner = max(bheight(b) for b in blocks)
    W = int(tot + pad * 2 + 46)
    H = int(inner + 96 + pad * 2)
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)
    lw = max(1, S)
    f = font(12, True)
    ytop = (pad + 20) * S
    ybot = ytop + (inner + 62) * S
    x = pad + 46

    def box(cx, cy, lab):
        d.rectangle([cx - bw / 2 * S, cy - bh / 2 * S, cx + bw / 2 * S, cy + bh / 2 * S],
                    fill=TOPF, outline=INK, width=lw)
        d.text((cx - d.textlength(lab, font=f) / 2, cy - 8 * S), lab, font=f, fill=INK)

    d.line([(pad + 20) * S, ytop, x * S, ytop], fill=INK, width=lw)
    for b in blocks:
        bwid = bwidth(b)
        if isinstance(b, str):
            d.line([x * S, ytop, (x + bwid) * S, ytop], fill=INK, width=lw)
            box((x + bwid / 2) * S, ytop, b)
        else:
            xl, xr = x * S, (x + bwid) * S
            for k, br in enumerate(b):
                yy = ytop + k * (bh + gap) * S
                d.line([xl, yy, xr, yy], fill=INK, width=lw)
                for j, lab in enumerate(br):
                    box((x + LEAD + j * (bw + LEAD) + bw / 2) * S, yy, lab)
            d.line([xl, ytop, xl, ytop + (len(b) - 1) * (bh + gap) * S], fill=INK, width=lw)
            d.line([xr, ytop, xr, ytop + (len(b) - 1) * (bh + gap) * S], fill=INK, width=lw)
        x += bwid + gap
    d.line([(x - gap) * S, ytop, (W - pad - 20) * S, ytop], fill=INK, width=lw)
    d.line([(W - pad - 20) * S, ytop, (W - pad - 20) * S, ybot], fill=INK, width=lw)
    d.line([(pad + 20) * S, ytop, (pad + 20) * S, ybot], fill=INK, width=lw)
    d.line([(pad + 20) * S, ybot, (W - pad - 20) * S, ybot], fill=INK, width=lw)
    cx = W / 2 * S                                    # แบตเตอรี่อยู่กลางเส้นล่าง
    d.line([cx - 5 * S, ybot - 11 * S, cx - 5 * S, ybot + 11 * S], fill=INK, width=lw)
    d.line([cx + 5 * S, ybot - 6 * S, cx + 5 * S, ybot + 6 * S], fill=INK, width=max(2, S * 2))
    d.rectangle([cx - 5 * S, ybot - lw, cx + 5 * S, ybot + lw], fill="white")
    if emf:
        d.text((cx - d.textlength(emf, font=f) / 2, ybot + 14 * S), emf, font=f, fill=INK)
    return _save(im, W, H, name)

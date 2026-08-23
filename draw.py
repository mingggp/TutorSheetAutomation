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
def strip(files, name, gap=26, labh=26, lab=True):
    ims = [Image.open(os.path.join(IMG, f)) for f in files]
    h = max(i.height for i in ims)
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    im = Image.new("RGB", (W*S, (h + (labh if lab else 0))*S), "white")
    d = ImageDraw.Draw(im); f = font(16, False); x = 0
    for k, i2 in enumerate(ims):
        im.paste(i2.resize((i2.width*S, i2.height*S), Image.LANCZOS), (x*S, (h - i2.height)*S))
        if lab:
            t = LAB[k] + "."
            tw = d.textlength(t, font=f)
            d.text((x*S + (i2.width*S - tw)/2, (h + 4)*S), t, font=f, fill=INK)
        x += i2.width + gap
    return _save(im, W, h + (labh if lab else 0), name)

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

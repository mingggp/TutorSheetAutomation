#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""กติกาการพับรูปคลี่เป็นลูกบาศก์ + การหมุนลูกบาศก์ (ใช้ตรวจคำตอบให้แน่ใจว่าถูกข้อเดียว)"""
UP, DN, RT, LF, BK, FR = (0,0,1), (0,0,-1), (1,0,0), (-1,0,0), (0,1,0), (0,-1,0)
NEG = lambda v: (-v[0], -v[1], -v[2])

def _apply(v, i, j, k):
    for _ in range(i): v = (v[0], -v[2], v[1])
    for _ in range(j): v = (v[2], v[1], -v[0])
    for _ in range(k): v = (v[1], -v[0], v[2])
    return v

_seen, ROTS = set(), []
for _i in range(4):
    for _j in range(4):
        for _k in range(4):
            _f = lambda v, i=_i, j=_j, k=_k: _apply(v, i, j, k)
            _key = tuple(_f(b) for b in [(1,0,0), (0,1,0), (0,0,1)])
            if _key in _seen: continue
            _seen.add(_key); ROTS.append(_f)
assert len(ROTS) == 24

def frames_of(cells):
    """คลี่ -> dict cell -> (normal, paper-right, paper-down)  (None ถ้าพับไม่ได้)

    paper-right / paper-down คือทิศที่ "ขวามือ" กับ "ด้านล่าง" ของกระดาษไปโผล่ในสามมิติ
    สองตัวนี้บอกว่าตัวอักษรบนหน้านั้นตะแคงไปทางไหนหลังพับเสร็จ
    เดิม fold() คำนวณไว้แล้วแต่โยนทิ้ง เก็บแค่ normal ตัวอักษรจึงถูกวาดตั้งตรงเสมอ
    ทั้งที่ของจริงมันตะแคง (ติวเตอร์ทักที่ข้อ 33 ว่า "position matter")
    """
    cells = set(cells)
    start = min(cells)
    frames = {start: (FR, RT, DN)}          # (normal, paper-right, paper-down)
    stack = [start]
    while stack:
        cur = stack.pop()
        n, rt, dn = frames[cur]
        r, c = cur
        moves = {(r, c+1): (rt, NEG(n), dn),
                 (r, c-1): (NEG(rt), n, dn),
                 (r+1, c): (dn, rt, NEG(n)),
                 (r-1, c): (NEG(dn), rt, n)}
        for nb, fr in moves.items():
            if nb in cells and nb not in frames:
                frames[nb] = fr; stack.append(nb)
    if len(frames) != len(cells): return None
    if len({f[0] for f in frames.values()}) != 6: return None   # หน้าทับกัน = พับไม่ได้
    return frames

def fold(cells):
    """คลี่ -> dict cell -> ทิศของหน้าลูกบาศก์  (None ถ้าพับไม่ได้)"""
    fr = frames_of(cells)
    return None if fr is None else {c: f[0] for c, f in fr.items()}

def is_net(cells):
    return fold(cells) is not None

def triples(dirs_to_label):
    """คืน set ของ (บน, ซ้าย, ขวา) ที่มองเห็นได้ทั้ง 24 มุม"""
    out = set()
    for R in ROTS:
        f = {R(d): lab for d, lab in dirs_to_label.items()}
        # ลำดับนี้คือ (บน, ซ้าย, ขวา) ตามที่ draw.iso วาดออกมาจริง
        # การฉายภาพของ iso เป็นภาพกลับด้าน (det[UP,BK,RT] = -1) หน้าที่โผล่ทางซ้ายของภาพ
        # จึงเป็นหน้า +x ไม่ใช่ +y ถ้าเรียงตามแกนตรง ๆ ลูกบาศก์ที่ได้จะเป็นภาพกระจกของลูกจริง
        out.add((f[UP], f[RT], f[BK]))
    return out

def label_dirs(cells, labels):
    """cells + labels(cell->ตัวอักษร)  ->  dict ทิศ -> ตัวอักษร"""
    d = fold(cells)
    if d is None: return None
    return {d[c]: labels[c] for c in cells}

def opposite(dirs_to_label, x):
    inv = {v: k for k, v in dirs_to_label.items()}
    return dirs_to_label[NEG(inv[x])]

# ---------- polycube ----------
def norm(v):
    mx, my, mz = min(a for a,_,_ in v), min(b for _,b,_ in v), min(c for _,_,c in v)
    return frozenset((a-mx, b-my, c-mz) for a, b, c in v)

def place(v):
    mx, my, mz = min(a for a,_,_ in v), min(b for _,b,_ in v), min(c for _,_,c in v)
    return [(a-mx, b-my, c-mz) for a, b, c in v]

def all_rots(v):
    return {norm([R(p) for p in v]) for R in ROTS}

def connected(vs):
    vs = set(vs)
    if not vs: return False
    st = [next(iter(vs))]; seen = set(st)
    D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    while st:
        c = st.pop()
        for d in D6:
            nb = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
            if nb in vs and nb not in seen: seen.add(nb); st.append(nb)
    return seen == vs

def neighbours(vox):
    """ทรงที่ต่างออกไปหนึ่งก้อน (ยังเชื่อมกันเป็นชิ้นเดียว)"""
    vs = set(vox); out = []
    D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    for rem in list(vs):
        rest = vs - {rem}
        if not connected(rest): continue
        for c in rest:
            for d in D6:
                nb = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
                if nb not in rest: out.append(sorted(rest | {nb}))
    return out

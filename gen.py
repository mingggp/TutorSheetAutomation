#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TPAT3 · วีคคณิต ชุดที่ 1 (v4) — สร้างโจทย์ + รูปทั้งหมด"""
import json, os, random, itertools
import draw as D

OUT = os.path.dirname(os.path.abspath(__file__))
SEED = int(os.environ.get("TPAT_SEED", "0"))   # เปลี่ยนเลขนี้ = ได้ชุดใหม่
QS = []
LV = [1]                      # ระดับความยากของกลุ่มที่กำลังเพิ่ม

def setlv(n): LV[0] = n

def add(part, arche, stem, choices, ansIdx, img=None, optimg=None, lvl=None):
    QS.append({"part": part, "arche": arche, "stem": stem,
               "choices": [str(c) for c in choices], "ansIdx": ansIdx,
               "img": img, "optimg": optimg, "lvl": lvl or LV[0]})

def numch(ans, seed, spread=None):
    rng = random.Random(seed * 7919 + ans * 31 + SEED * 104729)
    step = spread or max(1, round(abs(ans) * 0.12))
    while step > 1 and ans - 4 * step <= 0: step -= 1
    below = [ans - i*step for i in range(1, 5) if ans - i*step > 0]
    above = [ans + i*step for i in range(1, 5)]
    t = rng.randint(max(0, 4 - len(above)), min(4, len(below)))
    out = sorted(below[:t] + above[:4-t] + [ans])
    return out, out.index(ans)

def addnum(part, arche, stem, ans, spread=None, img=None, lvl=None):
    c, i = numch(ans, len(QS) + 1, spread)
    add(part, arche, stem, c, i, img=img, lvl=lvl)

# ==================================================================
# พาร์ทที่ 1 — ความสามารถทางตัวเลข (25 ข้อ)
# ==================================================================
P1 = "พาร์ทที่ 1"

# ลำดับ (4)
setlv(1)
for st, an, lv in [("7, 13, 19, 25, ?", 31, 1), ("1215, 405, 135, 45, ?", 15, 1),
                   ("4, 5, 8, 13, 20, ?", 29, 2), ("5, 40, 10, 34, 15, 28, 20, ?", 22, 2)]:
    addnum(P1, "ลำดับ", st, an, lvl=lv)

# ปริศนาตัวอักษร (2)
setlv(1)
add(P1, "ปริศนาตัวอักษร", "B, D, G, K, P, ?", ["T", "U", "V", "W", "X"], 2)
add(P1, "ปริศนาตัวอักษร", "ถ้า CAT เขียนเป็นรหัสว่า DBU แล้ว DOG จะเขียนเป็นรหัสว่าอย่างไร",
    ["CNF", "EPH", "EOG", "DPH", "FQI"], 1, lvl=1)

# เมทริกซ์ตัวเลข (2)
setlv(2)
add(P1, "เมทริกซ์ตัวเลข", "จากตาราง ตัวเลขในช่อง ? คือข้อใด (ทุกแถวใช้กฎเดียวกัน)",
    ["11", "12", "13", "14", "15"], 2, img=D.numgrid([[4,9,13],[6,7,13],[8,5,"?"]], "mx1"))
add(P1, "เมทริกซ์ตัวเลข", "จากตาราง ตัวเลขในช่อง ? คือข้อใด (ทุกแถวใช้กฎเดียวกัน)",
    ["42", "44", "46", "48", "54"], 3, img=D.numgrid([[2,3,8],[4,5,24],[6,7,"?"]], "mx2"))

# การดำเนินการสมมติ (2)
setlv(2)
add(P1, "การดำเนินการสมมติ", "กำหนดให้  a ✦ b = 2a − b   จงหาค่าของ  (5 ✦ 3) ✦ 4",
    ["8", "9", "10", "11", "12"], 2, lvl=1)
add(P1, "การดำเนินการสมมติ",
    "กำหนดให้  a ◆ b = (a + b)(a − b)   ถ้า  x ◆ 3 = 40  และ x > 0  แล้ว x มีค่าเท่าใด",
    ["5", "6", "7", "8", "9"], 2)

# ปริศนาเรขาคณิต (3)
setlv(2)
t1 = D.tri((3,4,5,27), "tr1a"); t2 = D.tri((2,6,3,18), "tr1b"); t3 = D.tri((5,2,4,"?"), "tr1c")
add(P1, "ปริศนาเรขาคณิต", "รูปสามเหลี่ยมทั้งสามใช้กฎเดียวกัน ตัวเลขในช่อง ? คือข้อใด",
    ["24","26","28","30","32"], 3, img=D.compose([t1,t2,t3], "trq1", seps=["",""], gap=26))
u1 = D.tri((8,3,2,13), "tr2a"); u2 = D.tri((9,4,3,16), "tr2b"); u3 = D.tri((7,6,2,"?"), "tr2c")
add(P1, "ปริศนาเรขาคณิต", "รูปสามเหลี่ยมทั้งสามใช้กฎเดียวกัน ตัวเลขในช่อง ? คือข้อใด",
    ["13","15","17","19","21"], 1, img=D.compose([u1,u2,u3], "trq2", seps=["",""], gap=26))
addnum(P1, "ปริศนาเรขาคณิต", "รูปหลายเหลี่ยมด้านเท่ารูปหนึ่งมี 12 ด้าน จะลากเส้นทแยงมุมได้ทั้งหมดกี่เส้น", 54, 6)

# โจทย์ปัญหาคณิต (5)
setlv(2)
addnum(P1, "โจทย์ปัญหาคณิต",
       "เงินจำนวนหนึ่งแบ่งให้ ก : ข : ค เป็นอัตราส่วน 3 : 4 : 5 ถ้า ค ได้มากกว่า ก อยู่ 480 บาท เงินทั้งหมดมีกี่บาท", 2880, 240, lvl=1)
addnum(P1, "โจทย์ปัญหาคณิต",
       "สินค้าราคาป้าย 1,200 บาท ลด 20% แล้วลดอีก 15% จากราคาที่ลดแล้ว ผู้ซื้อต้องจ่ายเงินกี่บาท", 816, 24, lvl=1)
addnum(P1, "โจทย์ปัญหาคณิต",
       "ก ทำงานชิ้นหนึ่งเสร็จใน 12 วัน  ข ทำงานชิ้นเดียวกันเสร็จใน 6 วัน ถ้าช่วยกันทำจะเสร็จในกี่วัน", 4, 1)
addnum(P1, "โจทย์ปัญหาคณิต",
       "รถวิ่งจาก A ไป B ด้วยอัตราเร็ว 60 กม./ชม. และวิ่งกลับด้วยอัตราเร็ว 40 กม./ชม. อัตราเร็วเฉลี่ยตลอดการเดินทางไป-กลับเป็นกี่ กม./ชม.", 48, 3)
addnum(P1, "โจทย์ปัญหาคณิต",
       "นักเรียน 8 คนมีคะแนนเฉลี่ย 72 คะแนน ถ้าเพิ่มนักเรียนอีก 2 คนที่ได้ 90 และ 84 คะแนน ค่าเฉลี่ยใหม่เป็นเท่าใด", 75, 1, lvl=1)

# มุมเข็มนาฬิกา (1)
setlv(2)
addnum(P1, "มุมเข็มนาฬิกา",
       "เวลา 15:20 น. เข็มสั้นกับเข็มยาวทำมุมกันกี่องศา (ตอบมุมที่เล็กกว่า)", 20, 5)

# อายุ (1)
setlv(2)
addnum(P1, "โจทย์ปัญหาคณิต",
       "ปัจจุบันพ่ออายุเป็น 4 เท่าของลูก อีก 12 ปีข้างหน้าพ่อจะมีอายุเป็น 2 เท่าของลูก ปัจจุบันพ่ออายุกี่ปี", 24, 3)

# เชาวน์ปัญญา (2)
setlv(2)
addnum(P1, "เชาวน์ปัญญา",
       "ท่อนไม้ยาว 10 เมตร ต้องการตัดออกเป็นท่อนย่อยยาวท่อนละ 2 เมตร จะต้องตัดทั้งหมดกี่ครั้ง", 4, 1, lvl=1)
addnum(P1, "เชาวน์ปัญญา",
       "ในห้องประชุมมีคน 8 คน ทุกคนจับมือทักทายกันครบทุกคู่ คู่ละหนึ่งครั้ง จะมีการจับมือทั้งหมดกี่ครั้ง", 28, 4)

# ความน่าจะเป็น (1)
setlv(2)
add(P1, "ความน่าจะเป็น",
    "ทอดลูกเต๋าที่เที่ยงตรงสองลูกพร้อมกัน ความน่าจะเป็นที่ผลรวมของแต้มเท่ากับ 8 เป็นเท่าใด",
    ["1/12", "1/9", "5/36", "1/6", "7/36"], 2)

# หน่วยและการประมาณค่าเชิงวิศวกรรม (2)
setlv(2)
addnum(P1, "หน่วยและการประมาณค่า",
       "ถังทรงกระบอกรัศมี 50 เซนติเมตร สูง 1 เมตร บรรจุน้ำได้เต็มถังพอดี จะบรรจุน้ำได้ประมาณกี่ลิตร (ใช้ π ≈ 3.14)", 785, 60)
# unseen (1)
setlv(1)
addnum(P1, "unseen",
       "กระดาษแผ่นหนึ่งพับครึ่งซ้ำกัน 8 ครั้ง เมื่อพับเสร็จกระดาษจะซ้อนกันกี่ชั้น", 256, 32)

n1 = sum(1 for q in QS if q["part"] == P1)
assert n1 == 25, n1

# ==================================================================
# พาร์ทที่ 2 — ความสามารถทางมิติสัมพันธ์ (25 ข้อ)
# ==================================================================
P2 = "พาร์ทที่ 2"

# ---------- Block Counting (4) : โจทย์ 4 แบบไม่ซ้ำ ----------
setlv(1)
hm = [[3,2],[2,1]]
addnum(P2, "Block Counting", "กองลูกบาศก์นี้ประกอบด้วยลูกบาศก์หน่วยทั้งหมดกี่ก้อน (ไม่มีก้อนลอยและไม่มีช่องโหว่ภายใน)",
       sum(sum(r) for r in hm), 1, img=D.iso(D.hm_vox(hm), "bc1"))

hm = [[4,2,1],[3,1,1],[2,1,1]]
vox = D.hm_vox(hm); mz = max(z for _,_,z in vox)
addnum(P2, "Block Counting", "ถ้ายกลูกบาศก์ทุกก้อนที่อยู่ในชั้นสูงสุดออกไป กองนี้จะเหลือลูกบาศก์กี่ก้อน",
       sum(1 for v in vox if v[2] != mz), 1, img=D.iso(vox, "bc2"))

hm = [[3,2,2],[2,2,1],[1,1,1]]
addnum(P2, "Block Counting", "ต้องเติมลูกบาศก์หน่วยอีกกี่ก้อน กองนี้จึงจะเป็นทรงสี่เหลี่ยมมุมฉากทึบขนาด 3 × 3 × 3 พอดี",
       27 - sum(sum(r) for r in hm), 1, img=D.iso(D.hm_vox(hm), "bc3"), lvl=2)

hm = [[2,1],[1,1]]
vox = set(D.hm_vox(hm))
surf = sum(1 for v in vox for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
           if (v[0]+d[0], v[1]+d[1], v[2]+d[2]) not in vox)
addnum(P2, "Block Counting", "กองลูกบาศก์นี้สร้างจากลูกบาศก์หน่วยด้านยาว 1 หน่วย พื้นที่ผิวทั้งหมด (รวมด้านที่ติดพื้น) เท่ากับกี่ตารางหน่วย",
       surf, 2, img=D.iso(sorted(vox), "bc4"), lvl=2)

# ---------- helper ภาพฉาย ----------
def cols_of(hm, kind):
    ny, nx = len(hm), len(hm[0])
    if kind == "front": return [max(hm[y][x] for y in range(ny)) for x in range(nx)]
    return [max(hm[y][x] for x in range(nx)) for y in range(ny)]
def cells_of(cols, mh): return {(mh-1-h, c) for c, v in enumerate(cols) for h in range(v)}
def top_cells(hm): return {(r,c) for r in range(len(hm)) for c in range(len(hm[0])) if hm[r][c] > 0}
def views(hm): return (tuple(cols_of(hm,"front")), tuple(cols_of(hm,"side")), tuple(sorted(top_cells(hm))))

# ---------- ภาพฉาย : ทรง → ภาพ (3) ----------
setlv(1)
ORTHO = [([[3,1,2],[2,1,1]], "front", "ด้านหน้า"),
         ([[2,3,1],[1,2,1],[1,1,1]], "side", "ด้านข้าง"),
         ([[3,2,2],[2,2,0],[1,0,0]], "top", "ด้านบน")]
for qi, (hm, kind, thai) in enumerate(ORTHO, 1):
    rng = random.Random(500 + qi + SEED * 104729)
    stem = D.iso(D.hm_vox(hm), f"or{qi}")
    if kind == "top":
        R, C = len(hm), len(hm[0]); correct = top_cells(hm)
        allc = {(r,c) for r in range(R) for c in range(C)}
        vs = [correct]
        while len(vs) < 5:
            cand = set(correct); free = sorted(allc-cand); used = sorted(cand)
            if free and rng.random() < .5: cand.add(rng.choice(free))
            elif len(used) > 1: cand.discard(rng.choice(used))
            if cand not in vs: vs.append(cand)
    else:
        base = cols_of(hm, kind); pool = [list(base)]
        while len(pool) < 5:
            c2 = list(base); i = rng.randrange(len(c2))
            c2[i] = max(1, min(max(base)+1, c2[i] + rng.choice([-2,-1,1,2])))
            if c2 not in pool: pool.append(c2)
        mh = max(max(c) for c in pool)
        vs = [cells_of(c, mh) for c in pool]; R, C = mh, len(base)
    order = list(range(5)); rng.shuffle(order)
    files = [D.grid(R, C, filled=vs[o], name=f"or{qi}o{j}", cell=25) for j, o in enumerate(order)]
    add(P2, "ภาพฉาย", f"ภาพที่มองกองลูกบาศก์นี้จาก{thai} คือข้อใด", [""]*5,
        order.index(0), img=stem, optimg=D.strip(files, f"or{qi}opt"), lvl=1 if qi < 3 else 2)

# ---------- ISOMETRIC : ภาพฉาย → ทรง (3, โจทย์ต่างกัน) ----------
setlv(2)
ISOQ = [([[2,1],[1,1]], "pick"), ([[3,2],[1,1]], "pick"), ([[2,2,1],[1,1,1]], "count")]
for qi, (hm, mode) in enumerate(ISOQ, 1):
    rng = random.Random(600 + qi + SEED * 104729)
    mh = max(max(r) for r in hm)
    fv = D.grid(mh, len(hm[0]), filled=cells_of(cols_of(hm,"front"), mh), name=f"iv{qi}f", cell=28)
    sv = D.grid(mh, len(hm), filled=cells_of(cols_of(hm,"side"), mh), name=f"iv{qi}s", cell=28)
    tv = D.grid(len(hm), len(hm[0]), filled=top_cells(hm), name=f"iv{qi}t", cell=28)
    stem = D.compose([fv, sv, tv], f"iv{qi}stem", seps=["",""], gap=30,
                     capt=["ด้านหน้า","ด้านข้าง","ด้านบน"])
    if mode == "count":
        addnum(P2, "ISOMETRIC",
               "ทรงที่ตรงกับภาพฉายทั้งสามด้านนี้ สร้างจากลูกบาศก์หน่วยอย่างน้อยที่สุดกี่ก้อน",
               sum(sum(r) for r in hm), 1, img=stem, lvl=3)
        continue
    target = views(hm); pool = [hm]; tries = 0
    while len(pool) < 5 and tries < 900:
        tries += 1
        cand = [r[:] for r in rng.choice(pool)]
        r = rng.randrange(len(cand)); c = rng.randrange(len(cand[0]))
        cand[r][c] = max(0, min(mh+1, cand[r][c] + rng.choice([-1,1])))
        if sum(sum(x) for x in cand) == 0: continue
        if views(cand) == target: continue
        if any(views(cand) == views(p) for p in pool): continue
        pool.append(cand)
    assert len(pool) == 5, qi
    order = list(range(5)); rng.shuffle(order)
    files = [D.iso(D.hm_vox(pool[o]), f"iv{qi}o{j}", cell=23, ch=19) for j, o in enumerate(order)]
    add(P2, "ISOMETRIC", "ภาพฉายทั้งสามด้านนี้ตรงกับทรงในข้อใด", [""]*5,
        order.index(0), img=stem, optimg=D.strip(files, f"iv{qi}opt"))

# ---------- พับกระดาษเจาะรู (3 แบบพับต่างกัน) ----------
setlv(1)
FOLDS = [
    ("v", 4, [(0,1),(2,0)], "พับฝั่งขวาไปทับฝั่งซ้ายหนึ่งครั้ง"),
    ("h", 4, [(0,0),(1,3)], "พับครึ่งล่างขึ้นไปทับครึ่งบนหนึ่งครั้ง"),
    ("vh", 4, [(0,1),(1,0)], "พับฝั่งขวาไปทับฝั่งซ้าย แล้วพับครึ่งล่างขึ้นทับครึ่งบน"),
]
for qi, (mode, N, punch, how) in enumerate(FOLDS, 1):
    rng = random.Random(700 + qi + SEED * 104729)
    correct = set()
    for (r, c) in punch:
        pts = {(r, c)}
        if "v" in mode: pts |= {(rr, N-1-cc) for (rr, cc) in pts}
        if "h" in mode: pts |= {(N-1-rr, cc) for (rr, cc) in pts}
        correct |= pts
    if mode == "v":    stem = D.grid(N, N//2, holes=set(punch), name=f"pf{qi}stem", cell=26)
    elif mode == "h":  stem = D.grid(N//2, N, holes=set(punch), name=f"pf{qi}stem", cell=26)
    else:              stem = D.grid(N//2, N//2, holes=set(punch), name=f"pf{qi}stem", cell=26)
    allc = {(r,c) for r in range(N) for c in range(N)}
    vs = [correct]
    while len(vs) < 5:
        cand = set(correct); used = sorted(cand); free = sorted(allc-cand)
        op = rng.choice(["mv","add","del"])
        if op == "mv" and used and free: cand.discard(rng.choice(used)); cand.add(rng.choice(free))
        elif op == "add" and free: cand.add(rng.choice(free))
        elif len(used) > 2: cand.discard(rng.choice(used))
        if cand not in vs: vs.append(cand)
    order = list(range(5)); rng.shuffle(order)
    files = [D.grid(N, N, holes=vs[o], name=f"pf{qi}o{j}", cell=24) for j, o in enumerate(order)]
    add(P2, "พับกระดาษ",
        f"นำกระดาษสี่เหลี่ยมจัตุรัสมา{how} แล้วเจาะรูตามภาพ เมื่อคลี่กระดาษออกจนสุดจะได้รูปแบบใด",
        [""]*5, order.index(0), img=stem, optimg=D.strip(files, f"pf{qi}opt"), lvl=1 if qi < 3 else 2)

# ---------- ลูกบาศก์: กติกาการพับ ----------
UP, DN, RT, LF, BK, FR = (0,0,1), (0,0,-1), (1,0,0), (-1,0,0), (0,1,0), (0,-1,0)
NETDIR = {"A": UP, "E": DN, "B": LF, "D": RT, "C": FR, "F": BK}
OPP = {"A":"E","E":"A","B":"D","D":"B","C":"F","F":"C"}

def _apply(v, i, j, k):
    for _ in range(i): v = (v[0], -v[2], v[1])
    for _ in range(j): v = (v[2], v[1], -v[0])
    for _ in range(k): v = (v[1], -v[0], v[2])
    return v
_seen, ROTS = set(), []
for i in range(4):
    for j in range(4):
        for k in range(4):
            f = lambda v, i=i, j=j, k=k: _apply(v, i, j, k)
            key = tuple(f(b) for b in [(1,0,0),(0,1,0),(0,0,1)])
            if key in _seen: continue
            _seen.add(key); ROTS.append(f)
assert len(ROTS) == 24

def triples(labels):
    base = {NETDIR[k]: v for k, v in labels.items()}
    return {(lambda f: (f[UP], f[BK], f[RT]))({R(d): l for d, l in base.items()}) for R in ROTS}

def opposite_of(labels, x):
    inv = {v: k for k, v in labels.items()}
    return labels[OPP[inv[x]]]

# --- (1) รูปคลี่ → ลูกบาศก์ ---
setlv(2)
lab1 = {"A":"P","B":"Q","C":"R","D":"S","E":"T","F":"U"}
rng = random.Random(801 + SEED * 104729)
good = sorted(triples(lab1)); correct = rng.choice(good)
letters = sorted(lab1.values())
bad = [t for t in itertools.permutations(letters, 3) if t not in set(good)]
rng.shuffle(bad)
picked, seen = [], {frozenset(correct)}
for t in bad:
    if frozenset(t) in seen: continue
    seen.add(frozenset(t)); picked.append(t)
    if len(picked) == 4: break
cands = [correct] + picked
order = list(range(5)); rng.shuffle(order)
files = [D.iso([(0,0,0)], f"n1o{j}", cell=34, ch=29, labels=cands[o]) for j, o in enumerate(order)]
add(P2, "พับกล่อง / รูปคลี่", "เมื่อพับรูปคลี่นี้ขึ้นเป็นลูกบาศก์ จะได้ลูกบาศก์ตรงกับข้อใด",
    [""]*5, order.index(0), img=D.net(lab1, "n1stem"), optimg=D.strip(files, "n1opt"), lvl=1)

# --- (2) ลูกบาศก์ → รูปคลี่ ---
lab2 = {"A":"1","B":"2","C":"3","D":"4","E":"5","F":"6"}
rng = random.Random(802 + SEED * 104729)
shown = rng.choice(sorted(triples(lab2)))
vals = sorted(lab2.values())
alts = []
for perm in itertools.permutations(vals):
    cand = dict(zip(["A","B","C","D","E","F"], perm))
    if shown in triples(cand): continue
    if any(cand == a for a in alts): continue
    alts.append(cand)
    if len(alts) > 200: break
rng.shuffle(alts)
netcands = [lab2] + alts[:4]
order = list(range(5)); rng.shuffle(order)
files = [D.net(netcands[o], f"n2o{j}", cell=30) for j, o in enumerate(order)]
add(P2, "พับกล่อง / รูปคลี่", "ลูกบาศก์ในภาพพับขึ้นมาจากรูปคลี่ในข้อใด", [""]*5, order.index(0),
    img=D.iso([(0,0,0)], "n2stem", cell=40, ch=34, labels=shown),
    optimg=D.strip(files, "n2opt", gap=20))

# --- (3) ลูกบาศก์ที่เป็นไปไม่ได้ ---
lab3 = {"A":"A","B":"B","C":"C","D":"D","E":"E","F":"F"}
rng = random.Random(803 + SEED * 104729)
good3 = sorted(triples(lab3)); letters3 = sorted(lab3.values())
imposs = [t for t in itertools.permutations(letters3, 3) if t not in set(good3)]
wrong = rng.choice(imposs)
right4, used = [], set()
for t in good3:
    if frozenset(t) in used or frozenset(t) == frozenset(wrong): continue
    used.add(frozenset(t)); right4.append(t)
    if len(right4) == 4: break
cands = [wrong] + right4
order = list(range(5)); rng.shuffle(order)
files = [D.iso([(0,0,0)], f"n3o{j}", cell=34, ch=29, labels=cands[o]) for j, o in enumerate(order)]
add(P2, "พับกล่อง / รูปคลี่", "จากรูปคลี่นี้ ลูกบาศก์ในข้อใดเป็นไปไม่ได้", [""]*5, order.index(0),
    img=D.net(lab3, "n3stem"), optimg=D.strip(files, "n3opt"))

# --- (4) หน้าตรงข้าม ---
lab4 = {"A":"ก","B":"ข","C":"ค","D":"ง","E":"จ","F":"ฉ"}
ansv = opposite_of(lab4, "ข")
ch4 = sorted(set([ansv] + [v for v in lab4.values() if v not in ("ข", ansv)][:4]))
add(P2, "พับกล่อง / รูปคลี่", "เมื่อพับรูปคลี่นี้เป็นลูกบาศก์ หน้าใดจะอยู่ตรงข้ามกับหน้า ข",
    ch4, ch4.index(ansv), img=D.net(lab4, "n4stem"), lvl=1)

# ---------- ลูกเต๋าหมุน (3, โจทย์ต่างกัน) ----------
setlv(2)
def matchings(items):
    if not items: yield []
    else:
        a = items[0]
        for i in range(1, len(items)):
            for rest in matchings(items[1:i] + items[i+1:]):
                yield [(a, items[i])] + rest

def unique_views(lab, seed):
    rng = random.Random(seed)
    good = sorted(triples(lab)); letters = sorted(lab.values())
    for _ in range(600):
        vs = rng.sample(good, 3)
        ok = [m for m in matchings(letters)
              if all(not any(x in v and y in v for v in vs) for (x, y) in m)]
        if len(ok) == 1: return vs
    raise RuntimeError

DICE = [({"A":"1","B":"2","C":"3","D":"4","E":"5","F":"6"}, "opp"),
        ({"A":"P","B":"Q","C":"R","D":"S","E":"T","F":"U"}, "adj"),
        ({"A":"W","B":"X","C":"Y","D":"Z","E":"J","F":"K"}, "stmt")]
for qi, (lab, mode) in enumerate(DICE, 1):
    vs = unique_views(lab, 900 + qi + SEED * 104729)
    letters = sorted(lab.values())
    files = [D.iso([(0,0,0)], f"dc{qi}v{j}", cell=34, ch=29, labels=v) for j, v in enumerate(vs)]
    stem = D.compose(files, f"dc{qi}stem", seps=["",""], gap=30,
                     capt=["ภาพที่ 1","ภาพที่ 2","ภาพที่ 3"])
    if mode == "opp":
        ask = letters[0]; ansv = opposite_of(lab, ask)
        opts = sorted(set([ansv] + [x for x in letters if x not in (ask, ansv)][:4]))
        add(P2, "ลูกเต๋าหมุน", f"ภาพทั้งสามคือลูกเต๋าลูกเดียวกันที่ถูกหมุนไป หน้าที่อยู่ตรงข้ามกับหน้า {ask} คือหน้าใด",
            opts, opts.index(ansv), img=stem)
    elif mode == "adj":
        ask = letters[0]; opp = opposite_of(lab, ask)
        opts = sorted(set([opp] + [x for x in letters if x not in (ask, opp)][:4]))
        add(P2, "ลูกเต๋าหมุน", f"ภาพทั้งสามคือลูกเต๋าลูกเดียวกันที่ถูกหมุนไป หน้าใดที่ไม่มีทางอยู่ติดกับหน้า {ask}",
            opts, opts.index(opp), img=stem)
    else:
        rng = random.Random(950 + qi + SEED * 104729)
        pairs = [(x, opposite_of(lab, x)) for x in letters]
        true_pair = pairs[0]
        false_pairs = []
        for x in letters:
            for y in letters:
                if x >= y: continue
                if opposite_of(lab, x) == y: continue
                false_pairs.append((x, y))
        rng.shuffle(false_pairs)
        opts = [f"หน้า {true_pair[0]} อยู่ตรงข้ามกับหน้า {true_pair[1]}"] + \
               [f"หน้า {a} อยู่ตรงข้ามกับหน้า {b}" for a, b in false_pairs[:4]]
        order = list(range(5)); rng.shuffle(order)
        sh = [opts[o] for o in order]
        add(P2, "ลูกเต๋าหมุน", "ภาพทั้งสามคือลูกเต๋าลูกเดียวกันที่ถูกหมุนไป ข้อความในข้อใดถูกต้อง",
            sh, order.index(0), img=stem)

# ---------- แผนภาพแบบหมุน (3, มีข้อ "ไม่ใช่" ด้วย) ----------
setlv(2)
def norm(v):
    mx, my, mz = min(a for a,_,_ in v), min(b for _,b,_ in v), min(c for _,_,c in v)
    return frozenset((a-mx, b-my, c-mz) for a, b, c in v)
def all_rots(v): return {norm([R(p) for p in v]) for R in ROTS}
def place(v):
    mx, my, mz = min(a for a,_,_ in v), min(b for _,b,_ in v), min(c for _,_,c in v)
    return [(a-mx, b-my, c-mz) for a, b, c in v]
def neighbours(vox):
    vs = set(vox); out = []
    DIRS = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    for rem in list(vs):
        rest = vs - {rem}
        if not rest: continue
        st = [next(iter(rest))]; seen = set(st)
        while st:
            c = st.pop()
            for d in DIRS:
                nb = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
                if nb in rest and nb not in seen: seen.add(nb); st.append(nb)
        if seen != rest: continue
        for c in rest:
            for d in DIRS:
                nb = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
                if nb not in rest: out.append(sorted(rest | {nb}))
    return out

SHAPES = [([(0,0,0),(1,0,0),(2,0,0),(2,1,0),(2,1,1)], "same"),
          ([(0,0,0),(0,1,0),(1,1,0),(1,1,1),(2,1,1)], "same"),
          ([(0,0,0),(1,0,0),(1,1,0),(1,1,1),(0,0,1)], "odd")]
for qi, (sh, mode) in enumerate(SHAPES, 1):
    rng = random.Random(1000 + qi + SEED * 104729)
    stem = D.iso(sh, f"rt{qi}stem")
    R0 = all_rots(sh)
    if mode == "same":
        Rc = ROTS[rng.randrange(1, 24)]
        correct = place([Rc(p) for p in sh])
        while norm(correct) == norm(sh):
            Rc = ROTS[rng.randrange(1, 24)]; correct = place([Rc(p) for p in sh])
        pool = [[(-x, y, z) for (x, y, z) in sh]] + neighbours(sh)
        rng.shuffle(pool)
        picked, classes = [], [R0]
        for cand in pool:
            cr = all_rots(place(cand))
            if any(cr & c for c in classes): continue
            classes.append(cr); picked.append(place(cand))
            if len(picked) == 4: break
        assert len(picked) == 4, qi
        def spin(c):
            R = ROTS[rng.randrange(24)]
            return place([R(p) for p in c])
        cands = [correct] + [spin(c) for c in picked]
        assert [j for j, c in enumerate(cands) if all_rots(c) & R0] == [0], qi
        text = "ทรงในข้อใดคือทรงเดียวกับภาพข้างบน เพียงแต่ถูกหมุนไปเท่านั้น"
    else:
        odd = None
        for cand in [[(-x, y, z) for (x, y, z) in sh]] + neighbours(sh):
            if not (all_rots(place(cand)) & R0): odd = place(cand); break
        assert odd, qi
        seenr = set()
        rots4 = []
        for R in ROTS:
            c = place([R(p) for p in sh])
            if norm(c) in seenr: continue
            seenr.add(norm(c)); rots4.append(c)
            if len(rots4) == 4: break
        cands = [odd] + rots4
        assert [j for j, c in enumerate(cands) if not (all_rots(c) & R0)] == [0], qi
        text = "ทรงในข้อใดไม่ใช่ทรงเดียวกับภาพข้างบน"
    order = list(range(5)); rng.shuffle(order)
    files = [D.iso(cands[o], f"rt{qi}o{j}", cell=22, ch=19) for j, o in enumerate(order)]
    add(P2, "แผนภาพแบบหมุน", text, [""]*5, order.index(0), img=stem,
        optimg=D.strip(files, f"rt{qi}opt"), lvl=1 if qi == 1 else 2)

# ---------- อุปมาอุปมัยภาพ (2) ----------
setlv(2)
ANA = [(4, {(0,0),(0,1),(1,2),(2,1),(3,3)}, {(0,2),(1,0),(2,2),(2,3),(3,1)}, "rot90"),
       (4, {(0,1),(1,1),(1,2),(2,3),(3,0)}, {(0,0),(1,2),(2,0),(2,1),(3,3)}, "flip")]
def tf(cells, N, kind):
    if kind == "rot90": return {(c, N-1-r) for (r, c) in cells}
    return {(r, N-1-c) for (r, c) in cells}
for qi, (N, a, c, kind) in enumerate(ANA, 1):
    rng = random.Random(1100 + qi + SEED * 104729)
    b = tf(a, N, kind); correct = tf(c, N, kind)
    ia = D.grid(N, N, filled=a, name=f"an{qi}a"); ib = D.grid(N, N, filled=b, name=f"an{qi}b")
    ic = D.grid(N, N, filled=c, name=f"an{qi}c")
    iq = D.grid(N, N, filled=set(), name=f"an{qi}q", center="?")
    stem = D.compose([ia, ib, ic, iq], f"an{qi}stem", seps=[":", "::", ":"], gap=16)
    allc = {(r, cc) for r in range(N) for cc in range(N)}
    vs = [correct]
    while len(vs) < 5:
        cand = set(correct); used = sorted(cand); free = sorted(allc-cand)
        if rng.random() < .5 and used and free: cand.discard(rng.choice(used)); cand.add(rng.choice(free))
        elif free: cand.add(rng.choice(free))
        if cand not in vs: vs.append(cand)
    order = list(range(5)); rng.shuffle(order)
    files = [D.grid(N, N, filled=vs[o], name=f"an{qi}o{j}") for j, o in enumerate(order)]
    add(P2, "แผนภาพอุปมาอุปมัย", "รูปที่ควรอยู่ในช่องว่างคือข้อใด", [""]*5,
        order.index(0), img=stem, optimg=D.strip(files, f"an{qi}opt"))

n2 = sum(1 for q in QS if q["part"] == P2)
assert n2 == 25, n2

import hard
setlv(3)
hard.build(add, addnum, P1, P2)

# แนวที่ข้อสอบจริงออกมากที่สุดในพาร์ท 2 แต่คลังเคยมี 0 ข้อ
# (ดู reference/DIGEST-part2.md หัวข้อ 3.1) — ตัวนี้กำหนด lvl มาเองในแต่ละข้อ
import spatial
spatial.build(add, P2, random.Random(5300 + SEED * 104729))

D.header({0, 1}, "hdr_math")
D.header({2, 3}, "hdr_phys")
D.badge("mingsmileyface", "badge")
D.levelchip("ระดับ 1 · ปูพื้น", 1, "chip1")
D.levelchip("ระดับ 2 · มาตรฐาน", 2, "chip2")
D.levelchip("ระดับ 3 · เข้มข้น", 3, "chip3")
for _n in (1, 2, 3): D.stars(_n, f"star{_n}")

from collections import Counter
stems = Counter(q["stem"] for q in QS)
print("โจทย์ที่ข้อความซ้ำ:", {k[:28]: v for k, v in stems.items() if v > 1})
print("แนวโจทย์:", len({q["arche"] for q in QS}), "| ตำแหน่งคำตอบ:", dict(sorted(Counter(q["ansIdx"] for q in QS).items())))
with open(os.path.join(OUT, "questions.json"), "w", encoding="utf-8") as _f:
    json.dump(QS, _f, ensure_ascii=False, indent=1)
for lv in (1, 2, 3):
    a = sum(1 for q in QS if q["lvl"] == lv and q["part"] == P1)
    b = sum(1 for q in QS if q["lvl"] == lv and q["part"] == P2)
    print(f"  ระดับ {lv}: ตัวเลข {a} · มิติ {b} · รวม {a+b}")
print("ข้อ:", len(QS), "| รูป:", len(os.listdir(D.IMG)))

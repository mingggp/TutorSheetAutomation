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
    ["11", "12", "13", "14", "15"], 2, img=D.numgrid([[4,9,13],[6,7,13],[8,5,"?"]], "mx1"), lvl=1)
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
    ["13","15","17","19","21"], 1, img=D.compose([u1,u2,u3], "trq2", seps=["",""], gap=26), lvl=1)
addnum(P1, "ปริศนาเรขาคณิต", "รูปหลายเหลี่ยมด้านเท่ารูปหนึ่งมี 12 ด้าน จะลากเส้นทแยงมุมได้ทั้งหมดกี่เส้น", 54, 6, lvl=1)

# โจทย์ปัญหาคณิต (5)
setlv(2)
addnum(P1, "โจทย์ปัญหาคณิต",
       "เงินจำนวนหนึ่งแบ่งให้ ก : ข : ค เป็นอัตราส่วน 3 : 4 : 5 ถ้า ค ได้มากกว่า ก อยู่ 480 บาท เงินทั้งหมดมีกี่บาท", 2880, 240, lvl=1)
addnum(P1, "โจทย์ปัญหาคณิต",
       "สินค้าราคาป้าย 1,200 บาท ลด 20% แล้วลดอีก 15% จากราคาที่ลดแล้ว ผู้ซื้อต้องจ่ายเงินกี่บาท", 816, 24, lvl=1)
addnum(P1, "โจทย์ปัญหาคณิต",
       "ก ทำงานชิ้นหนึ่งเสร็จใน 12 วัน  ข ทำงานชิ้นเดียวกันเสร็จใน 6 วัน ถ้าช่วยกันทำจะเสร็จในกี่วัน", 4, 1)
# ตัวเลือกต้องมี 50 ด้วย เพราะเป็นคำตอบของคนที่เฉลี่ยแบบ (60+40)/2 ซึ่งเป็นกับดักหลักของข้อนี้
# ถ้าไม่ใส่ เด็กที่คิดผิดจะหาช้อยของตัวเองไม่เจอ แล้วกลับไปคิดใหม่ ข้อนี้ก็ไม่ได้วัดอะไร
add(P1, "โจทย์ปัญหาคณิต",
    "รถวิ่งจาก A ไป B ด้วยอัตราเร็ว 60 กม./ชม. และวิ่งกลับด้วยอัตราเร็ว 40 กม./ชม. "
    "อัตราเร็วเฉลี่ยตลอดการเดินทางไป-กลับเป็นกี่ กม./ชม.",
    ["45", "48", "50", "52", "55"], 1)
addnum(P1, "โจทย์ปัญหาคณิต",
       "นักเรียน 8 คนมีคะแนนเฉลี่ย 72 คะแนน ถ้าเพิ่มนักเรียนอีก 2 คนที่ได้ 90 และ 84 คะแนน ค่าเฉลี่ยใหม่เป็นเท่าใด", 75, 1, lvl=1)

# มุมเข็มนาฬิกา (1)
setlv(2)
addnum(P1, "มุมเข็มนาฬิกา",
       "เวลา 15:20 น. เข็มสั้นกับเข็มยาวทำมุมกันกี่องศา (ตอบมุมที่เล็กกว่า)", 20, 5, lvl=1)

# อายุ (1)
setlv(2)
addnum(P1, "โจทย์ปัญหาคณิต",
       "ปัจจุบันพ่ออายุเป็น 4 เท่าของลูก อีก 12 ปีข้างหน้าพ่อจะมีอายุเป็น 2 เท่าของลูก ปัจจุบันพ่ออายุกี่ปี", 24, 3, lvl=1)

# เชาวน์ปัญญา (2)
setlv(2)
addnum(P1, "เชาวน์ปัญญา",
       "ท่อนไม้ยาว 12 เมตร ตัดออกเป็นท่อนย่อยยาวท่อนละ 2 เมตร\n"
       "การตัดหนึ่งครั้งใช้เวลา 4 นาที และต้องพัก 2 นาทีระหว่างการตัดแต่ละครั้ง\n"
       "ตั้งแต่เริ่มตัดครั้งแรกจนตัดครั้งสุดท้ายเสร็จ ใช้เวลาทั้งหมดกี่นาที",
       (12 // 2 - 1) * 4 + (12 // 2 - 2) * 2, 1, lvl=2)
addnum(P1, "เชาวน์ปัญญา",
       "ในห้องประชุมมีคน 8 คน ทุกคนจับมือทักทายกันครบทุกคู่ คู่ละหนึ่งครั้ง จะมีการจับมือทั้งหมดกี่ครั้ง", 28, 4, lvl=1)

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
# ตัวเลือกต้องเป็นกำลังของ 2 ทั้งห้า ไม่งั้นเด็กตัดตัวเลือกที่ไม่ใช่ 2^n ทิ้งแล้วตอบได้เลย
add(P1, "unseen", "กระดาษแผ่นหนึ่งพับครึ่งซ้ำกัน 8 ครั้ง เมื่อพับเสร็จกระดาษจะซ้อนกันกี่ชั้น",
    ["64", "128", "256", "512", "1024"], 2)

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
    """ภาพฉายของกองลูกบาศก์ — กติกาการจัดวางอ้างการเขียนแบบ

    ในภาพ isometric แกน x พุ่งไปทางขวาล่าง แกน y พุ่งไปทางซ้ายล่าง
    แถวที่ y มากที่สุดจึงเป็นแถว "หน้า" ที่อยู่ใกล้คนดูที่สุด

    ด้านหน้า  มองจากซ้ายล่าง  เรียง x ซ้ายไปขวาตามที่เห็นในภาพ
    ด้านขวา   มองจากขวาล่าง   **ขอบหน้าของทรงต้องอยู่ซ้ายมือของภาพ** จึงต้องไล่ y จากมากไปน้อย
              (เดิมไล่ y จาก 0 ขึ้นไป = เอาด้านหลังไว้ซ้าย ซึ่งกลับข้าง — ติวเตอร์จับได้จากข้อ 30/31)
    ด้านบน    มองจากบน ขอบหน้าอยู่ล่างสุด จึงใช้ (y, x) ตรง ๆ
    """
    ny, nx = len(hm), len(hm[0])
    if kind == "front": return [max(hm[y][x] for y in range(ny)) for x in range(nx)]
    return [max(hm[y][x] for x in range(nx)) for y in range(ny - 1, -1, -1)]
def cells_of(cols, mh): return {(mh-1-h, c) for c, v in enumerate(cols) for h in range(v)}
def top_cells(hm): return {(r,c) for r in range(len(hm)) for c in range(len(hm[0])) if hm[r][c] > 0}
def views(hm): return (tuple(cols_of(hm,"front")), tuple(cols_of(hm,"side")), tuple(sorted(top_cells(hm))))

# ---------- ภาพฉาย : ทรง → ภาพ (3) ----------
setlv(1)
ORTHO = [([[3,1,2],[2,1,1]], "front", "ด้านหน้า"),
         ([[2,3,1],[1,2,1],[1,1,1]], "side", "ด้านขวา"),
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
                     capt=["ด้านหน้า","ด้านขวา","ด้านบน"])
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
    # (บน, ซ้าย, ขวา) ตามที่ draw.iso วาดจริง — ดูคำอธิบายใน cube.triples
    return {(lambda f: (f[UP], f[RT], f[BK]))({R(d): l for d, l in base.items()}) for R in ROTS}

# ทิศของกระดาษบนแต่ละหน้า อ่านจากรูปคลี่ที่วาดจริง (draw.NET) ไม่ใช่เขียนค่าตายตัวไว้
# จึงเปลี่ยนรูปคลี่เมื่อไหร่ ตัวเลขก็ตะแคงตามเองโดยไม่ต้องแก้ตรงนี้
import cube as _CU
_NF = _CU.frames_of(set(D.NET))
assert _NF is not None, "รูปคลี่ใน draw.NET พับเป็นลูกบาศก์ไม่ได้"
NETFRAME = {D.NET[c]: _NF[c] for c in D.NET}
assert all(_CU.NEG(NETFRAME[k][0]) == NETFRAME[OPP[k]][0] for k in NETFRAME),     "ตาราง OPP ไม่ตรงกับรูปคลี่ที่วาดจริง"

# สลับแกน x กับ y = พลิกภาพหนึ่งครั้ง ใช้หักล้างกับการฉายภาพของ draw.iso ที่พลิกอยู่แล้ว
MIR = lambda v: (v[1], v[0], v[2])

def _no_mirror_check():
    """พิสูจน์สองอย่างที่การพับกระดาษจริงห้ามละเมิด

    1. ลูกบาศก์ที่วาดต้องไม่ใช่ภาพกระจกของลูกจริง
       บนจอ หน้าบน -> หน้าซ้าย -> หน้าขวา ไล่ทวนเข็มนาฬิกา ดังนั้น normal ของสามหน้านี้
       ต้องเรียงแบบถนัดขวา (det > 0) เหมือนลูกเต๋าสากลที่เลข 1 2 3 ไล่ทวนเข็มรอบมุมร่วม
       ถ้า det ติดลบ แปลว่าทุกช้อยกลายเป็นทรงที่พับไม่ได้ทั้งหมด

    2. ตัวอักษรบนแต่ละหน้าต้องไม่กลับด้าน วัดจากทิศการวนมุมบนจอ

    ครอบทั้ง 24 มุมหมุน x 3 หน้าที่มองเห็น
    """
    cell, ch = 26, 22
    pj = lambda x, y, z: ((x - y) * cell, (x + y) * (cell // 2) - z * ch)
    det = lambda a, b, c: (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
                           + a[2]*(b[0]*c[1]-b[1]*c[0]))
    base = {NETFRAME[k][0]: (k, NETFRAME[k][1], NETFRAME[k][2]) for k in NETFRAME}
    for R in ROTS:
        f = {MIR(R(n)): (lab, MIR(R(rt)), MIR(R(dn))) for n, (lab, rt, dn) in base.items()}
        tru = {lab: R(n) for n, (lab, _rt, _dn) in base.items()}   # ป้าย -> normal จริง
        top, left, right = f[UP][0], f[BK][0], f[RT][0]
        # เทียบด้วย normal จริง ไม่ใช่ normal ในพิกัดภาพ (ในพิกัดภาพมันติดลบเสมอโดยนิยาม)
        assert det(tru[top], tru[left], tru[right]) > 0, "ลูกบาศก์ที่วาดเป็นภาพกระจก"
        for key, nrm in (("top", UP), ("left", BK), ("right", RT)):
            _l, rt, dn = f[nrm]
            UL, UR, LR, LL = [pj(*c) for c in D._order_quad(D._CORNERS[key], rt, dn)]
            ax, ay = UR[0] - UL[0], UR[1] - UL[1]
            bx, by = LL[0] - UL[0], LL[1] - UL[1]
            assert ax * by - ay * bx > 0, f"ตัวอักษรกลับด้านที่หน้า {key}"
_no_mirror_check()

def oriented(labels):
    """เหมือน triples() แต่พก "ทิศของตัวอักษร" มาด้วย

    ตัวอักษรบนหน้าลูกบาศก์ตะแคงได้ 4 แบบ ลูกบาศก์ที่เลข 3 ตั้งตรงกับที่เลข 3 ตะแคง
    จึงเป็นคนละภาพ ไม่ใช่ภาพเดียวกัน ถ้าไม่คิดตรงนี้ โจทย์พับกล่องจะมีคำตอบถูกหลายข้อ
    โดยที่ตัวตรวจไม่รู้ตัว (ติวเตอร์จับได้ที่ข้อ 33 และทำให้ข้อ 34 อ่านแล้วขัดใจ)

    คืน set ของ ((ตัวอักษรบน, rt, dn), (ซ้าย, rt, dn), (ขวา, rt, dn)) ครบทั้ง 24 มุมมอง
    """
    base = {NETFRAME[k][0]: (v, NETFRAME[k][1], NETFRAME[k][2]) for k, v in labels.items()}
    out = set()
    for R in ROTS:
        # MIR สลับแกน x กับ y = พลิกภาพหนึ่งครั้ง เพื่อหักล้างกับการฉายภาพของ iso
        # ที่พลิกอยู่แล้ว (พิสูจน์แล้วว่า r x u ชี้ออกจากผู้ดู และ det[UP,BK,RT] = -1)
        # ถ้าไม่หักล้าง ลูกบาศก์ที่วาดจะเป็นภาพกระจกของลูกจริง
        # ผลคือช้อยที่ควรเป็นไปได้กลายเป็นเป็นไปไม่ได้หมด (ติวเตอร์จับได้ที่ข้อ 33/34)
        f = {MIR(R(n)): (lab, MIR(R(rt)), MIR(R(dn))) for n, (lab, rt, dn) in base.items()}
        out.add((f[UP], f[BK], f[RT]))
    return out

def relabel(view, letters3):
    """เปลี่ยนตัวอักษรบนสามหน้าที่เห็น โดยคงทิศการตะแคงไว้เหมือนเดิม

    ตัวลวงต้องตะแคงเหมือนตัวถูก ไม่งั้นเด็กจับได้ทันทีว่าข้อไหนคือเฉลย
    """
    return tuple((letters3[i], view[i][1], view[i][2]) for i in range(3))

def opposite_of(labels, x):
    inv = {v: k for k, v in labels.items()}
    return labels[OPP[inv[x]]]

def rank_bad(view, lab, letters, rng):
    """เรียงตัวลวงจาก "ผิดชัด" ไป "ผิดละเอียด"

    ผิดชัด = สามหน้านั้นมาอยู่ด้วยกันไม่ได้เลย (มีคู่ตรงข้ามปนมา หรือเรียงกลับมือ)
             แก้ได้ด้วยวิธีคลาสสิกคือดูคู่ตรงข้ามกับทิศการวน
    ผิดละเอียด = หน้าถูกแต่ตัวอักษรตะแคงผิด ต้องไล่ทีละหน้า

    เอาผิดชัดขึ้นก่อน ไม่งั้นทั้งข้อจะเหลือแต่ตัวลวงที่ต้องเพ่งทิศตัวอักษรอย่างเดียว
    """
    plain = triples(lab)
    out = [(t in plain, t, relabel(view, t))      # False = ผิดชัด มาก่อน
           for t in itertools.permutations(letters, 3)]
    rng.shuffle(out)                              # สลับก่อน แล้วค่อยเรียง
    out.sort(key=lambda x: x[0])                  # sort ของ python เสถียร ลำดับในกลุ่มจึงยังสุ่มอยู่
    return out

# --- (1) รูปคลี่ → ลูกบาศก์ ---
setlv(2)
lab1 = {"A":"P","B":"Q","C":"R","D":"S","E":"T","F":"U"}
rng = random.Random(801 + SEED * 104729)
goodo = sorted(oriented(lab1)); goodset = set(goodo)
correct = rng.choice(goodo)
letters = sorted(lab1.values())
ranked = rank_bad(correct, lab1, letters, rng)
bad = [v for _p, _t, v in ranked if v not in goodset]
picked, seen = [], {tuple(x[0] for x in correct)}
for v in bad:
    k = tuple(x[0] for x in v)
    if k in seen: continue
    seen.add(k); picked.append(v)
    if len(picked) == 4: break
assert len(picked) == 4
cands = [correct] + picked
order = list(range(5)); rng.shuffle(order)
files = [D.iso([(0,0,0)], f"n1o{j}", cell=34, ch=29, labels=cands[o]) for j, o in enumerate(order)]
add(P2, "พับกล่อง / รูปคลี่", "เมื่อพับรูปคลี่นี้ขึ้นเป็นลูกบาศก์ จะได้ลูกบาศก์ตรงกับข้อใด",
    [""]*5, order.index(0), img=D.net(lab1, "n1stem"), optimg=D.strip(files, "n1opt"), lvl=1)

# --- (2) ลูกบาศก์ → รูปคลี่ ---
lab2 = {"A":"1","B":"2","C":"3","D":"4","E":"5","F":"6"}
rng = random.Random(802 + SEED * 104729)
shown = rng.choice(sorted(oriented(lab2)))
vals = sorted(lab2.values())
alts = []
for perm in itertools.permutations(vals):
    cand = dict(zip(["A","B","C","D","E","F"], perm))
    if shown in oriented(cand): continue
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
goodo3 = sorted(oriented(lab3)); goodset3 = set(goodo3)
letters3 = sorted(lab3.values())
base3 = rng.choice(goodo3)
imposs = [v for _p, _t, v in rank_bad(base3, lab3, letters3, rng) if v not in goodset3]
wrong = imposs[0]          # เอาตัวที่ผิดตั้งแต่การจัดวางหน้า ไม่ใช่ผิดแค่ทิศตัวอักษร
right4, used = [], {frozenset(x[0] for x in wrong)}
for v in goodo3:
    k = frozenset(x[0] for x in v)
    if k in used: continue
    used.add(k); right4.append(v)
    if len(right4) == 4: break
assert len(right4) == 4
cands = [wrong] + right4
# พิสูจน์ด้วยโค้ดว่ามีข้อที่เป็นไปไม่ได้แค่ข้อเดียวจริง ๆ
assert sum(1 for c in cands if c not in goodset3) == 1
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
        # นับว่าแต่ละหน้าโผล่ในสามภาพกี่ครั้ง แล้วถามหน้าที่โผล่น้อยที่สุด
        # หน้าที่เห็นครั้งเดียวต้องไล่เทียบข้ามภาพกว่าจะรู้ว่าใครอยู่ตรงข้าม
        # (เดิมถามหน้าแรกตามตัวอักษรเสมอ ซึ่งมักเป็นหน้าที่เห็นชัดที่สุด — ติวเตอร์ว่าง่ายไป)
        cnt3 = {x: sum(1 for v in vs for f in v if f[0] == x) for x in letters}
        ask = min(letters, key=lambda x: (cnt3[x], x)); opp = opposite_of(lab, ask)
        opts = sorted(set([opp] + [x for x in letters if x not in (ask, opp)][:4]))
        add(P2, "ลูกเต๋าหมุน", f"ภาพทั้งสามคือลูกเต๋าลูกเดียวกันที่ถูกหมุนไป หน้าใดที่ไม่มีทางอยู่ติดกับหน้า {ask}",
            opts, opts.index(opp), img=stem, lvl=3)
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
        # ROTS[0] คือการหมุน 0 องศา ถ้าไม่กันไว้ ตัวเลือกแรกจะเป็นรูปเดิมของโจทย์เป๊ะ ๆ
        # เด็กเห็นแล้วตัดทิ้งได้ทันที (ติวเตอร์จับได้ที่ข้อ 38)
        # ใส่ norm(sh) ลงกล่องที่เห็นแล้วตั้งแต่ต้น จึงกันทั้งการหมุน 0 องศา
        # และมุมหมุนอื่นที่บังเอิญให้ทรงกลับมาทับรูปเดิมพอดี
        seenr = {norm(sh)}
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
    # กลางกรอบใช้เส้นแบ่งแนวตั้งที่วาดเป็นรูป ไม่ใช่ "::" ซึ่งอ่านแล้วสับสนคอนเซปต์
    dv = D.divider(f"an{qi}dv", h=54)
    stem = D.compose([ia, ib, dv, ic, iq], f"an{qi}stem", seps=[":", "", "", ":"], gap=16)
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
# (ดู reference/tpat3/DIGEST-part2.md หัวข้อ 3.1) — ตัวนี้กำหนด lvl มาเองในแต่ละข้อ
import spatial
spatial.build(add, P2, random.Random(5300 + SEED * 104729))

# แนวพาร์ทตัวเลขที่ข้อสอบจริงออกแต่คลังเคยมี 0 ข้อ (ดูรายงาน calibrator ช่องโหว่ 3-8)
# ---------- ท่อนเชิงกล (วีคฟิสิกส์) ----------
P3 = "พาร์ทที่ 3"
import mech
mech.build(add, P3, random.Random(8100 + SEED * 104729))

import concept
concept.build(add, P3)

import numeric
numeric.build(add, P1, random.Random(6100 + SEED * 104729))

# ==================================================================
# TGAT2 — เอาเฉพาะ 3 ท่อนหลัง ติวเตอร์ไม่สอนตอนที่ 1 (ความสามารถทางภาษา)
# ผังข้อสอบพิมพ์อยู่ในตัวข้อสอบเอง ดู reference/tgat2/DIGEST.md
# ==================================================================
G_NUM, G_SPA, G_REA = "ตอนที่ 2", "ตอนที่ 3", "ตอนที่ 4"

import compare
compare.build(add, G_NUM, random.Random(7100 + SEED * 104729), n=5, lvl=2)

import solid
_nsol = solid.build(add, G_SPA, random.Random(7200 + SEED * 104729), n_rot=5, n_odd=5, lvl=2)

TG_BOXES = [("ภาษา", "20 ข้อ"), ("จำนวน", "20 ข้อ"),
            ("มิติสัมพันธ์", "20 ข้อ"), ("เหตุผล", "20 ข้อ")]
TG_GROUPS = [("ไม่สอน", 0, 0), ("ที่สอน", 1, 3)]
D.header({1, 2, 3}, "hdr_tgat2", boxes=TG_BOXES, groups=TG_GROUPS)

D.header({0, 1}, "hdr_math")
D.header({2, 3}, "hdr_phys")
D.badge("mingsmileyface", "badge")
D.levelchip("ระดับ 1 · ปูพื้น", 1, "chip1")
D.levelchip("ระดับ 2 · มาตรฐาน", 2, "chip2")
D.levelchip("ระดับ 3 · เข้มข้น", 3, "chip3")
for _n in (1, 2, 3): D.stars(_n, f"star{_n}")

from collections import Counter
stems = Counter(q["stem"] for q in QS)
# ---------- ด่านกันชื่อรูปชนกัน ----------
# เครื่องผลิตคนละตัวเคยใช้ชื่อไฟล์เดียวกันโดยไม่รู้ตัว (an1o0.png ของ
# "แผนภาพอุปมาอุปมัย" เดิม ชนกับ "อุปมาอุปไมยรูปภาพ" ตัวใหม่)
# ตัวหลังเขียนทับตัวแรก ทำให้โจทย์กับตัวเลือกมาจากคนละข้อ และไม่มีอะไรฟ้องเลย
_dup = {k: v for k, v in D.SAVED.items() if v > 1}
if _dup:
    raise SystemExit("ชื่อรูปชนกัน (เครื่องผลิตคนละตัวเขียนทับกัน): " +
                     ", ".join(f"{k} x{v}" for k, v in sorted(_dup.items())))

# ---------- ด่านกันตัวเลือกซ้ำกับโจทย์ / ซ้ำกันเอง ----------
# ติวเตอร์จับได้ที่ข้อ 38 ว่ามีตัวเลือกเป็นรูปเดียวกับในโจทย์เป๊ะ ๆ
# แบบนี้เด็กตัดตัวเลือกนั้นทิ้งได้ทันทีโดยไม่ต้องคิด และถ้าเผอิญเป็นเฉลย โจทย์ก็พัง
# เทียบด้วยลายนิ้วมือของภาพจริง (draw.HASH) ไม่ใช่ด้วยชื่อไฟล์ จึงจับได้แม้คนละชื่อ
def _diff(a, b):
    return sum(abs(x - y) for x, y in zip(a[2], b[2])) / len(a[2])

_bad = []
for _q in QS:
    _opt = D.STRIPS.get((_q.get("optimg") or "")[:-4])
    if not _opt:
        continue
    _h = [D.HASH.get(f[:-4]) for f in _opt]
    _stem = D.HASH.get((_q.get("img") or "")[:-4])
    # โจทย์กับตัวเลือกมักวาดคนละขนาด (rt3stem cell=26 · ตัวเลือก cell=22)
    # จึงเทียบเฉพาะคู่ที่อัตราส่วนใกล้กัน แล้วยอมให้ต่างได้จากการย่อภาพ
    for _j, _hh in enumerate(_h):
        if not (_stem and _hh):
            continue
        _ra, _rb = _stem[0] / _stem[1], _hh[0] / _hh[1]
        if abs(_ra - _rb) <= 0.06 * _ra and _diff(_stem, _hh) <= 6.0:
            _bad.append(f'{_q["arche"]}: ตัวเลือกที่ {_j+1} เป็นรูปเดียวกับโจทย์')
    # ตัวเลือกด้วยกันวาดจากคำสั่งเดียวกันเสมอ ขนาดจึงต้องเท่ากันเป๊ะ
    # เกณฑ์ตรงนี้ต้องแคบมาก เพราะบางแนว (อุปมาอุปมัย) ตัวเลือกต่างกันแค่ช่องเดียว
    # ซึ่งวัดได้แค่ 0.8 ถ้าตั้งกว้างกว่านี้จะไปจับโจทย์ที่ปกติดี
    for _j in range(len(_h)):
        for _k in range(_j + 1, len(_h)):
            if not (_h[_j] and _h[_k]):
                continue
            if _h[_j][:2] == _h[_k][:2] and _diff(_h[_j], _h[_k]) <= 0.05:
                _bad.append(f'{_q["arche"]}: ตัวเลือกที่ {_j+1} กับ {_k+1} เป็นรูปเดียวกัน')
if _bad:
    raise SystemExit("ตัวเลือกซ้ำ:\n  " + "\n  ".join(sorted(set(_bad))))

print("โจทย์ที่ข้อความซ้ำ:", {k[:28]: v for k, v in stems.items() if v > 1})
print("แนวโจทย์:", len({q["arche"] for q in QS}), "| ตำแหน่งคำตอบ:", dict(sorted(Counter(q["ansIdx"] for q in QS).items())))
# บอก sharpen.py ว่ารูปไหนตั้งใจเก็บความละเอียดสูงไว้ให้สลับกลับตอนทำ PDF
# ถ้าไม่จำกัดไว้ มันจะเดาจับคู่รูปโจทย์ผิดข้อแล้วสลับทับกัน (เคยทำข้อ 34 พังมาแล้ว)
with open(os.path.join(OUT, "img", "_hires.json"), "w", encoding="utf-8") as _f:
    json.dump(sorted(k for k, v in D.HIRES.items() if v > 1), _f)

with open(os.path.join(OUT, "questions.json"), "w", encoding="utf-8") as _f:
    json.dump(QS, _f, ensure_ascii=False, indent=1)
for lv in (1, 2, 3):
    a = sum(1 for q in QS if q["lvl"] == lv and q["part"] == P1)
    b = sum(1 for q in QS if q["lvl"] == lv and q["part"] == P2)
    print(f"  ระดับ {lv}: ตัวเลข {a} · มิติ {b} · รวม {a+b}")
print("ข้อ:", len(QS), "| รูป:", len(os.listdir(D.IMG)))

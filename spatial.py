#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์มิติสัมพันธ์แบบตาราง — ซ้อนแผ่นบังแสง และ อนุกรมรูปภาพ

สองแนวนี้ข้อสอบจริงออกรวมกัน 20% ของพาร์ท 2 แต่คลังเรามี 0 ข้อ
(ดู reference/tpat3/DIGEST-part2.md หัวข้อ 3.1)

ตรรกะแยกขาดจากการวาดโดยตั้งใจ — ส่วนที่ตัดสินว่าคำตอบถูกไหมอยู่ในไฟล์นี้ทั้งหมด
และทดสอบได้โดยไม่ต้องพึ่ง draw.py เลย ส่วนการวาดค่อยเรียก D.plate() ทีหลัง

ตารางแทนด้วย tuple ของ tuple ของ 0/1 เพื่อให้เอาไปเทียบและใส่ set ได้ตรงๆ
"""

# ============================================================
#  งานพื้นฐานบนตาราง
# ============================================================

def norm(g):
    return tuple(tuple(int(v) for v in row) for row in g)


def OR(a, b):
    return tuple(tuple(x | y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def AND(a, b):
    return tuple(tuple(x & y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def XOR(a, b):
    return tuple(tuple(x ^ y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def rot90(g):
    """หมุนตามเข็มนาฬิกา 90 องศา"""
    return tuple(tuple(g[len(g) - 1 - c][r] for c in range(len(g))) for r in range(len(g[0])))


def flip_h(g):
    return tuple(tuple(reversed(row)) for row in g)


def flip_v(g):
    return tuple(reversed(g))


def shift(g, dr, dc):
    """เลื่อนแบบวนขอบ"""
    R, C = len(g), len(g[0])
    return tuple(tuple(g[(r - dr) % R][(c - dc) % C] for c in range(C)) for r in range(R))


def density(g):
    return sum(sum(row) for row in g)


def perturb(g, rng, k=1):
    """สลับสถานะ k ช่องแบบสุ่ม — ใช้ปั้นตัวลวงที่ 'เกือบถูก'"""
    R, C = len(g), len(g[0])
    cells = [(r, c) for r in range(R) for c in range(C)]
    rng.shuffle(cells)
    m = [list(row) for row in g]
    for r, c in cells[:k]:
        m[r][c] ^= 1
    return norm(m)


def _rand_grid(rng, n, lo=0.28, hi=0.45):
    """ตารางสุ่มที่ความหนาแน่นอยู่ในช่วงที่อ่านออก ไม่โล่งไม่ทึบเกินไป"""
    while True:
        p = rng.uniform(lo, hi)
        g = norm([[1 if rng.random() < p else 0 for _ in range(n)] for _ in range(n)])
        d = density(g)
        if n * n * lo * 0.7 <= d <= n * n * hi * 1.3:
            return g


def _pick5(truth, pool, rng):
    """เลือกตัวลวง 4 ตัวที่ไม่ซ้ำกันและไม่ซ้ำคำตอบ คืน None ถ้าหาไม่พอ"""
    seen = {truth}
    out = []
    for cand in pool:
        if cand in seen:
            continue
        seen.add(cand)
        out.append(cand)
        if len(out) == 4:
            return out
    return None


def _place(opts, ans, want):
    rest = [o for o in opts if o != ans]
    return rest[:want] + [ans] + rest[want:], want


# ============================================================
#  ซ้อนแผ่นบังแสง — คำตอบคือ OR ของสองแผ่น พิสูจน์ได้ตรงๆ ด้วยนิยาม
# ============================================================

def overlay(rng, want=0, n=6):
    """แผ่นใสสองแผ่นมีช่องทึบคนละที่ ซ้อนกันแล้วช่องไหนทึบบ้าง

    ช่องจะทึบถ้ามีแผ่นใดแผ่นหนึ่งทึบ = OR ตามนิยาม ไม่มีทางตีความเป็นอย่างอื่น
    คืน (A, B, choices, ansIdx)
    """
    for _ in range(500):
        A = _rand_grid(rng, n)
        B = _rand_grid(rng, n)
        truth = OR(A, B)

        # ต้องมีช่องที่ทับกันจริงบ้าง ไม่งั้น OR กับ XOR จะได้ผลเหมือนกัน โจทย์จะกำกวม
        if density(AND(A, B)) < 2:
            continue
        # ห้ามทึบเกือบเต็มตาราง จะดูไม่ออกว่าต่างกันตรงไหน
        if density(truth) > n * n * 0.72:
            continue

        pool = [AND(A, B), XOR(A, B), A, B,
                perturb(truth, rng, 1), perturb(truth, rng, 2),
                flip_h(truth), shift(truth, 0, 1)]
        rng.shuffle(pool)
        wrong = _pick5(truth, pool, rng)
        if wrong is None:
            continue

        opts, idx = _place([truth] + wrong, truth, want)
        if sum(1 for o in opts if o == truth) != 1:
            continue
        return A, B, opts, idx
    raise RuntimeError("สร้างโจทย์ซ้อนแผ่นบังแสงไม่สำเร็จ")


# ============================================================
#  อนุกรมรูปภาพ — สร้างจากกฎจริง คำตอบถูกโดยการก่อสร้าง
# ============================================================

RULES = {
    "หมุนตามเข็ม 90°": lambda g: rot90(g),
    "เลื่อนลง 1 แถว": lambda g: shift(g, 1, 0),
    "เลื่อนขวา 1 ช่อง": lambda g: shift(g, 0, 1),
    "เลื่อนทแยงลงขวา": lambda g: shift(g, 1, 1),
    "พลิกซ้าย-ขวา": lambda g: flip_h(g),
    "หมุน 90° แล้วเลื่อนขวา": lambda g: shift(rot90(g), 0, 1),
    "เลื่อนลงแล้วพลิกซ้าย-ขวา": lambda g: flip_h(shift(g, 1, 0)),
    "หมุนทวนเข็ม 90° แล้วเลื่อนลง": lambda g: shift(rot90(rot90(rot90(g))), 1, 0),
}

# กฎชั้นเดียวใช้ทำข้อสองดาว · กฎซ้อนสองชั้นใช้ทำข้อสามดาว
#
# ห้ามใส่ "พลิกซ้าย-ขวา" ไว้ในรายการที่ใช้สร้างลำดับ เพราะมันมีคาบ 2
# พลิกสองครั้งได้ภาพเดิม ลำดับเลยวนซ้ำจนเดาไม่ออกว่าภาพไหนคือภาพถัดไป
# เก็บไว้ใน RULES ได้ เพราะยังใช้ปั้นตัวลวงที่น่าเชื่อได้อยู่
SIMPLE = ["หมุนตามเข็ม 90°", "เลื่อนลง 1 แถว", "เลื่อนขวา 1 ช่อง", "เลื่อนทแยงลงขวา"]
COMPOUND = ["หมุน 90° แล้วเลื่อนขวา", "เลื่อนลงแล้วพลิกซ้าย-ขวา", "หมุนทวนเข็ม 90° แล้วเลื่อนลง"]


def series(rng, want=0, n=5, steps=3, hard=False):
    """ให้ภาพ steps ภาพที่เดินตามกฎเดียวกัน ถามภาพถัดไป

    คืน (frames, choices, ansIdx, rule_name)
    """
    names = COMPOUND if hard else SIMPLE
    for _ in range(500):
        rule = rng.choice(names)
        step = RULES[rule]
        g0 = _rand_grid(rng, n, 0.25, 0.42)

        frames = [g0]
        for _ in range(steps - 1):
            frames.append(step(frames[-1]))
        truth = step(frames[-1])

        # ถ้ากฎวนกลับมาซ้ำภาพเดิมภายในลำดับ ผู้สอบจะเดาไม่ออกว่าอันไหนคืออันถัดไป
        if len(set(frames)) != steps or truth in frames[:-1]:
            continue

        pool = []
        for other in RULES:
            if other != rule:
                cand = RULES[other](frames[-1])
                if cand != truth:
                    pool.append(cand)
        pool += [frames[-1], step(truth), perturb(truth, rng, 1), perturb(truth, rng, 2)]
        rng.shuffle(pool)
        wrong = _pick5(truth, pool, rng)
        if wrong is None:
            continue

        opts, idx = _place([truth] + wrong, truth, want)
        if sum(1 for o in opts if o == truth) != 1:
            continue
        return frames, opts, idx, rule
    raise RuntimeError("สร้างโจทย์อนุกรมรูปภาพไม่สำเร็จ")


# ============================================================
#  แนวเพิ่มจากรายงาน digest — ข้อสอบจริงออกรวมกัน 17% แต่คลังเคยมี 0 ข้อ
#
#  ภาพสะท้อนกระจก (5%) · หารูปไม่เข้าพวก (5%) · อุปมาอุปไมยรูปภาพ (7%)
#  ทั้งสามใช้เครื่องวาด plate() ที่มีอยู่แล้ว ไม่ต้องเขียนเครื่องวาดใหม่
# ============================================================

MIRROR_STEM = "ภาพด้านบนเมื่อสะท้อนกับกระจกที่วางในแนวตั้งทางขวามือ จะได้ภาพในข้อใด"
ODDG_STEM = "ภาพในข้อใด**ไม่เข้าพวก**กับภาพอื่น"
ANALOGY_STEM = ("ทางซ้ายของเส้นแบ่ง ภาพแรกเปลี่ยนเป็นภาพที่สองด้วยกฎอย่างหนึ่ง\n"
                "ถ้าใช้กฎเดียวกันกับภาพทางขวาของเส้นแบ่ง จะได้ภาพในข้อใด")


def rot180(g):
    return rot90(rot90(g))


def rot270(g):
    return rot90(rot180(g))


def _rots4(g):
    return [g, rot90(g), rot180(g), rot270(g)]


def mirror(rng, want=0, n=5):
    """ภาพสะท้อนกระจก — คำตอบคือ flip_h ของภาพต้นแบบ

    กันกรณีที่สะท้อนแล้วได้ผลเหมือนการหมุน ไม่งั้นตัวลวงที่เป็นภาพหมุนจะถูกด้วย
    """
    for _ in range(500):
        A = _rand_grid(rng, n, 0.28, 0.44)
        truth = flip_h(A)
        if truth in _rots4(A):          # ภาพนี้สะท้อนแล้วเหมือนหมุน โจทย์จะมีคำตอบซ้ำ
            continue
        pool = [g for g in _rots4(A) if g != truth]
        pool += [flip_v(A), perturb(truth, rng, 1), perturb(truth, rng, 2)]
        rng.shuffle(pool)
        wrong = _pick5(truth, pool, rng)
        if wrong is None:
            continue
        opts, idx = _place([truth] + wrong, truth, want)
        if sum(1 for o in opts if o == truth) != 1:
            continue
        return A, opts, idx
    raise RuntimeError("สร้างโจทย์ภาพสะท้อนกระจกไม่สำเร็จ")


def oddgrid(rng, want=0, n=5):
    """หารูปไม่เข้าพวก — สี่ภาพเป็นภาพเดียวกันที่หมุนไป มีภาพเดียวที่ต่างออกไป"""
    for _ in range(500):
        P = _rand_grid(rng, n, 0.28, 0.44)
        fam = []
        for g in _rots4(P):
            if g not in fam:
                fam.append(g)
        if len(fam) != 4:               # ภาพสมมาตร หมุนแล้วซ้ำ ใช้ไม่ได้
            continue
        Q = perturb(P, rng, 2)
        if any(Q == g for g in _rots4(Q)[1:]) or Q in fam:
            continue
        if any(Q in _rots4(g) for g in fam):
            continue
        opts, idx = _place([Q] + fam, Q, want)
        if len(set(opts)) != 5:
            continue
        # ต้องมีภาพเดียวที่ไม่ใช่สมาชิกของตระกูล
        if sum(1 for o in opts if o not in fam) != 1:
            continue
        return opts, idx
    raise RuntimeError("สร้างโจทย์หารูปไม่เข้าพวกไม่สำเร็จ")


def analogy(rng, want=0, n=5):
    """A→B สอนกฎ · C→? ให้ใช้กฎเดียวกัน — กฎต้องถอดได้แบบเดียวเท่านั้น"""
    names = SIMPLE + COMPOUND
    for _ in range(500):
        rule = rng.choice(names)
        step = RULES[rule]
        A = _rand_grid(rng, n, 0.25, 0.42)
        B = step(A)
        if B == A:
            continue
        # ต้องมีกฎเดียวที่พา A ไป B ได้ ไม่งั้นถอดกฎได้หลายแบบ
        fits = [r for r in RULES if RULES[r](A) == B]
        if len(fits) != 1:
            continue
        C = _rand_grid(rng, n, 0.25, 0.42)
        if C == A:
            continue
        truth = step(C)
        pool = [RULES[r](C) for r in RULES if r != rule]
        pool += [C, perturb(truth, rng, 1), perturb(truth, rng, 2)]
        pool = [g for g in pool if g != truth]
        rng.shuffle(pool)
        wrong = _pick5(truth, pool, rng)
        if wrong is None:
            continue
        opts, idx = _place([truth] + wrong, truth, want)
        if sum(1 for o in opts if o == truth) != 1:
            continue
        return A, B, C, opts, idx
    raise RuntimeError("สร้างโจทย์อุปมาอุปไมยรูปภาพไม่สำเร็จ")


# ============================================================
#  เมทริกซ์รูปภาพ 3×3 ช่องขวาล่างหาย — ของจริงออก 10% ของพาร์ท 2
#
#  ทุกคุณลักษณะเดินเป็นจตุรัสละติน: ในหนึ่งแถวและหนึ่งหลัก
#  ค่าของคุณลักษณะนั้นจะปรากฏครบทั้งสามค่าพอดี ไม่ซ้ำไม่ขาด
#  ช่องที่หายจึงถูกบังคับค่าเดียวโดยอัตโนมัติ และผู้สอบอนุมานได้จริง
#  ไม่ใช่คำตอบที่ถูกเพราะคนออกบอกว่าถูก
# ============================================================

M_SHAPES = ["circle", "square", "triangle", "diamond", "star", "hexagon", "cross", "plus"]
M_ROTSHAPES = ["triangle", "arrow", "star", "pentagon"]   # เฉพาะรูปที่หมุนแล้วเห็นความต่าง
M_FILLS = ["white", "black", "grey"]
M_ROTS = [0, 90, 180, 270]


def _latin(vals, r, c, a, b):
    """ค่าของคุณลักษณะที่ตำแหน่ง (r,c) — (a*r + b*c) mod 3 เป็นจตุรัสละตินเสมอเมื่อ b ไม่หารด้วย 3 ลงตัว"""
    return vals[(a * r + b * c) % 3]


def matrix(rng, want=0, attrs=2):
    """attrs=2 → รูปทรง + การเติมสี (★★☆) · attrs=3 → เพิ่มการหมุนอีกชั้น (★★★)

    คืน (cells, choices, ansIdx) โดย cells เป็นตาราง 3×3 ของ (shape, fill, rot)
    ช่อง (2,2) คือช่องที่ต้องเดา — ตัวเรียกต้องวาดเป็น "?" แทน
    """
    for _ in range(400):
        pool = M_ROTSHAPES if attrs == 3 else M_SHAPES
        sh = rng.sample(pool, 3)
        fl = rng.sample(M_FILLS, 3)
        rt = rng.sample(M_ROTS, 3) if attrs == 3 else [0, 0, 0]

        def cell(r, c):
            return (_latin(sh, r, c, 1, 1),
                    _latin(fl, r, c, 1, 2),
                    _latin(rt, r, c, 2, 1) if attrs == 3 else 0)

        cells = [[cell(r, c) for c in range(3)] for r in range(3)]
        truth = cells[2][2]

        cand = [(s, f, t) for s in sh for f in fl for t in (rt if attrs == 3 else [0])]
        rng.shuffle(cand)
        wrong = _pick5(truth, cand, rng)
        if wrong is None:
            continue

        opts, idx = _place([truth] + wrong, truth, want)
        if sum(1 for o in opts if o == truth) != 1:
            continue
        return cells, opts, idx
    raise RuntimeError("สร้างโจทย์เมทริกซ์รูปภาพไม่สำเร็จ")


def forced(cells, k):
    """ค่าที่ช่อง (2,2) ถูกบังคับให้เป็น เมื่อดูจากคุณลักษณะที่ k ของอีก 8 ช่อง

    คืน None ถ้าแถวกับหลักบังคับไม่ตรงกัน หรือบังคับไม่ได้ — แปลว่าโจทย์ใช้ไม่ได้
    """
    row = [cells[2][c][k] for c in range(2)]
    col = [cells[r][2][k] for r in range(2)]
    allv = {cells[r][c][k] for r in range(3) for c in range(3) if (r, c) != (2, 2)}
    from_row = [v for v in allv if v not in row]
    from_col = [v for v in allv if v not in col]
    if len(from_row) != 1 or len(from_col) != 1 or from_row[0] != from_col[0]:
        return None
    return from_row[0]


# ============================================================
#  ต่อเข้ากับเครื่องวาด — import ข้างในฟังก์ชันโดยตั้งใจ
#  เพื่อให้ตัวตรวจด้านล่างรันได้โดยไม่ต้องพึ่ง draw.py และ Pillow
# ============================================================

OVERLAY_STEM = ("แผ่นใสสองแผ่นด้านบนมีช่องทึบแสงคนละตำแหน่งกัน\n"
                "ถ้านำแผ่นทั้งสองมาวางซ้อนกันสนิทแล้วส่องไฟผ่าน ภาพที่ได้คือข้อใด")

SERIES_STEM = ("ภาพทั้งสามด้านบนเรียงตามกฎเดียวกัน ภาพลำดับถัดไปคือข้อใด")

MATRIX_STEM = ("จากตารางด้านบน ทุกแถวและทุกหลักเดินตามกฎเดียวกัน ภาพในช่อง ? คือข้อใด")


def _cellimg(spec, name):
    """วาดหนึ่งช่องของเมทริกซ์จาก (shape, fill, rot)"""
    import draw as D
    s, f, t = spec
    return D.symbox([{"shape": s, "fill": f, "rot": t}], name)


def render_matrix(cells, opts, tag):
    import draw as D
    rows = []
    for r in range(3):
        imgs = []
        for c in range(3):
            if (r, c) == (2, 2):
                # ขนาดต้องเท่า symbox พอดี: size 74 + pad 6 สองข้าง = 86
                imgs.append(D.grid(1, 1, name=f"{tag}qm", cell=74, pad=6, center="?"))
            else:
                imgs.append(_cellimg(cells[r][c], f"{tag}c{r}{c}"))
        rows.append(D.strip(imgs, f"{tag}r{r}", gap=8, lab=False))
    stem = D.vstack(rows, tag + "q", gap=8)
    files = [_cellimg(o, f"{tag}o{i}") for i, o in enumerate(opts)]
    return stem, D.strip(files, tag + "opt")


def render_overlay(A, B, opts, tag, cell=15):
    """คืน (img, optimg) สำหรับส่งเข้า add()"""
    import draw as D
    a = D.plate(A, tag + "a", cell=cell)
    b = D.plate(B, tag + "b", cell=cell)
    stem = D.compose([a, b], tag + "q", seps=["+"], gap=24,
                     capt=["แผ่นที่ 1", "แผ่นที่ 2"])
    files = [D.plate(o, f"{tag}o{i}", cell=cell - 2) for i, o in enumerate(opts)]
    return stem, D.strip(files, tag + "opt")


def render_series(frames, opts, tag, cell=15):
    import draw as D
    fs = [D.plate(f, f"{tag}f{i}", cell=cell) for i, f in enumerate(frames)]
    stem = D.compose(fs, tag + "q", seps=[""] * (len(fs) - 1), gap=22,
                     capt=[f"ภาพที่ {i+1}" for i in range(len(fs))])
    files = [D.plate(o, f"{tag}o{i}", cell=cell - 2) for i, o in enumerate(opts)]
    return stem, D.strip(files, tag + "opt")


def render_mirror(A, opts, tag, cell=17):
    import draw as D
    stem = D.plate(A, tag + "s", cell=cell + 3)
    files = [D.plate(o, f"{tag}o{i}", cell=cell) for i, o in enumerate(opts)]
    return stem, D.strip(files, tag + "opt")


def render_oddgrid(opts, tag, cell=17):
    import draw as D
    files = [D.plate(o, f"{tag}o{i}", cell=cell) for i, o in enumerate(opts)]
    return D.strip(files, tag + "opt")


def render_analogy(A, B, Cc, opts, tag, cell=17):
    """A → B │ C → ?  — ลูกศรกับเส้นแบ่งวาดเป็นรูป เพราะฟอนต์ไม่มีอักขระพวกนี้"""
    import draw as D
    a = D.plate(A, tag + "a", cell=cell)
    b = D.plate(B, tag + "b", cell=cell)
    c = D.plate(Cc, tag + "c", cell=cell)
    q = D.grid(1, 1, name=tag + "q", cell=cell * 5, pad=3, center="?")
    stem = D.compose([a, D.arrow(tag + "r1"), b, D.divider(tag + "dv"),
                      c, D.arrow(tag + "r2"), q], tag + "s", gap=10)
    files = [D.plate(o, f"{tag}o{i}", cell=cell - 2) for i, o in enumerate(opts)]
    return stem, D.strip(files, tag + "opt")


def build(add, P2, rng):
    """เติมโจทย์สองแนวนี้เข้าคลัง — เรียกจาก gen.py

    ตำแหน่งเฉลยถูกบังคับให้ไล่ ก-จ ครบวง เพื่อแก้ปัญหาที่ตัวเลือก จ.
    แทบไม่เคยเป็นเฉลยเลยในคลังเดิม (กติกาข้อ 4)
    """
    want = 0
    for qi in range(2):                       # ★★☆ ซ้อนแผ่นบังแสง
        A, B, opts, idx = overlay(rng, want=want, n=6)
        img, optimg = render_overlay(A, B, opts, f"ov{qi}")
        add(P2, "ซ้อนแผ่นบังแสง", OVERLAY_STEM, [""] * 5, idx,
            img=img, optimg=optimg, lvl=2)
        want = (want + 2) % 5

    for qi in range(2):                       # ★★☆ อนุกรมรูปภาพ กฎชั้นเดียว
        frames, opts, idx, _ = series(rng, want=want, hard=False)
        img, optimg = render_series(frames, opts, f"sr{qi}")
        add(P2, "อนุกรมรูปภาพ", SERIES_STEM, [""] * 5, idx,
            img=img, optimg=optimg, lvl=2)
        want = (want + 2) % 5

    for qi in range(2):                       # ★★★ อนุกรมรูปภาพ กฎซ้อนสองชั้น
        frames, opts, idx, _ = series(rng, want=want, hard=True)
        img, optimg = render_series(frames, opts, f"sh{qi}")
        add(P2, "อนุกรมรูปภาพ", SERIES_STEM, [""] * 5, idx,
            img=img, optimg=optimg, lvl=3)
        want = (want + 2) % 5

    A, B, opts, idx = overlay(rng, want=want, n=8)   # ★★★ ตารางใหญ่ ภาระสายตาสูง
    img, optimg = render_overlay(A, B, opts, "ovh", cell=12)
    add(P2, "ซ้อนแผ่นบังแสง", OVERLAY_STEM, [""] * 5, idx,
        img=img, optimg=optimg, lvl=3)
    want = (want + 2) % 5

    for qi in range(2):                       # ★★☆ เมทริกซ์ สองคุณลักษณะ
        cells, opts, idx = matrix(rng, want=want, attrs=2)
        img, optimg = render_matrix(cells, opts, f"mx{qi}")
        add(P2, "เมทริกซ์รูปภาพ", MATRIX_STEM, [""] * 5, idx,
            img=img, optimg=optimg, lvl=2)
        want = (want + 2) % 5

    for qi in range(2):                       # ★★★ เมทริกซ์ สามคุณลักษณะ มีการหมุนซ้อน
        cells, opts, idx = matrix(rng, want=want, attrs=3)
        img, optimg = render_matrix(cells, opts, f"mh{qi}")
        add(P2, "เมทริกซ์รูปภาพ", MATRIX_STEM, [""] * 5, idx,
            img=img, optimg=optimg, lvl=3)
        want = (want + 2) % 5

    for qi in range(3):                       # ★★☆ ภาพสะท้อนกระจก
        A, opts, idx = mirror(rng, want=want)
        img, optimg = render_mirror(A, opts, f"mr{qi}")
        add(P2, "ภาพสะท้อนกระจก", MIRROR_STEM, [""] * 5, idx,
            img=img, optimg=optimg, lvl=2)
        want = (want + 2) % 5

    for qi in range(3):                       # ★★☆ หารูปไม่เข้าพวก
        opts, idx = oddgrid(rng, want=want)
        add(P2, "หารูปไม่เข้าพวก", ODDG_STEM, [""] * 5, idx,
            optimg=render_oddgrid(opts, f"og{qi}"), lvl=2)
        want = (want + 2) % 5

    for qi in range(3):                       # ★★★ อุปมาอุปไมยรูปภาพ
        A, B, Cc, opts, idx = analogy(rng, want=want)
        img, optimg = render_analogy(A, B, Cc, opts, f"an{qi}")
        add(P2, "อุปมาอุปไมยรูปภาพ", ANALOGY_STEM, [""] * 5, idx,
            img=img, optimg=optimg, lvl=3)
        want = (want + 2) % 5


# ============================================================
#  ตัวตรวจ — พิสูจน์ว่าโจทย์ที่ผลิตออกมาตอบได้ทางเดียวจริง
#  รันได้โดยไม่ต้องมี draw.py: python spatial.py
# ============================================================

if __name__ == "__main__":
    import random, sys

    bad = []

    def check(cond, msg):
        if not cond:
            bad.append(msg)

    for s in range(120):
        rng = random.Random(s)
        want = s % 5

        A, B, opts, idx = overlay(rng, want=want)
        check(len(opts) == 5, f"overlay s={s}: ตัวเลือกไม่ครบ 5")
        check(len(set(opts)) == 5, f"overlay s={s}: ตัวเลือกซ้ำกัน")
        check(idx == want, f"overlay s={s}: บังคับตำแหน่งเฉลยไม่ได้")
        check(opts[idx] == OR(A, B), f"overlay s={s}: เฉลยไม่ใช่ OR ของสองแผ่น")
        check(sum(1 for o in opts if o == OR(A, B)) == 1, f"overlay s={s}: มีคำตอบถูกเกินหนึ่ง")

        for hard in (False, True):
            frames, opts, idx, rule = series(rng, want=want, hard=hard)
            step = RULES[rule]
            check(len(set(opts)) == 5, f"series s={s} hard={hard}: ตัวเลือกซ้ำกัน")
            check(idx == want, f"series s={s} hard={hard}: บังคับตำแหน่งเฉลยไม่ได้")
            check(opts[idx] == step(frames[-1]),
                  f"series s={s} hard={hard}: เฉลยไม่ตรงกับกฎ '{rule}'")
            check(sum(1 for o in opts if o == opts[idx]) == 1,
                  f"series s={s} hard={hard}: มีคำตอบถูกเกินหนึ่ง")
            # ทุกภาพในลำดับต้องเดินตามกฎเดียวกันจริง
            for i in range(len(frames) - 1):
                check(step(frames[i]) == frames[i + 1],
                      f"series s={s} hard={hard}: ภาพที่ {i+2} ไม่ได้มาจากกฎ")

    for attrs in (2, 3):
        cells, opts, idx = matrix(rng, want=want, attrs=attrs)
        truth = cells[2][2]
        check(len(set(opts)) == 5, f"matrix s={s} attrs={attrs}: ตัวเลือกซ้ำกัน")
        check(idx == want, f"matrix s={s} attrs={attrs}: บังคับตำแหน่งเฉลยไม่ได้")
        check(opts[idx] == truth, f"matrix s={s} attrs={attrs}: เฉลยไม่ใช่ช่องที่หาย")
        check(sum(1 for o in opts if o == truth) == 1,
              f"matrix s={s} attrs={attrs}: มีคำตอบถูกเกินหนึ่ง")
        # หัวใจ: ผู้สอบต้องอนุมานได้จริงจาก 8 ช่องที่เห็น ไม่ใช่ถูกเพราะคนออกบอกว่าถูก
        for k in range(3 if attrs == 3 else 2):
            check(forced(cells, k) == truth[k],
                  f"matrix s={s} attrs={attrs}: คุณลักษณะที่ {k} อนุมานจากแถว/หลักไม่ได้")
        # ทุกแถวและทุกหลักต้องมีค่าครบสามค่า ไม่ซ้ำไม่ขาด
        for k in range(3 if attrs == 3 else 2):
            for r in range(3):
                check(len({cells[r][c][k] for c in range(3)}) == 3,
                      f"matrix s={s} attrs={attrs}: แถว {r} คุณลักษณะ {k} ไม่ครบสามค่า")
            for c in range(3):
                check(len({cells[r][c][k] for r in range(3)}) == 3,
                      f"matrix s={s} attrs={attrs}: หลัก {c} คุณลักษณะ {k} ไม่ครบสามค่า")


    def show(g):
        return "\n      ".join("".join("██" if v else "·　" for v in row) for row in g)

    r = random.Random(3)
    A, B, opts, idx = overlay(r, want=2)
    print("ตัวอย่าง ซ้อนแผ่นบังแสง\n" + "-" * 46)
    print("  แผ่นที่ 1\n      " + show(A))
    print("  แผ่นที่ 2\n      " + show(B))
    print(f"  เฉลย = ตัวเลือก {'กขคงจ'[idx]}\n      " + show(opts[idx]))

    r = random.Random(5)
    frames, opts, idx, rule = series(r, want=4, hard=True)
    print(f"\nตัวอย่าง อนุกรมรูปภาพ (กฎ: {rule})\n" + "-" * 46)
    for i, f in enumerate(frames, 1):
        print(f"  ภาพที่ {i}\n      " + show(f))
    print(f"  เฉลย = ตัวเลือก {'กขคงจ'[idx]}\n      " + show(opts[idx]))

    print()
    if bad:
        for m in bad[:12]:
            print("[พัง]", m)
        print(f"พบปัญหา {len(bad)} จุด")
        sys.exit(1)
    print("ตรวจผ่าน 600 ข้อ — ซ้อนแผ่น 120 · อนุกรม 240 · เมทริกซ์ 240")

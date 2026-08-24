#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์มิติสัมพันธ์แบบตาราง — ซ้อนแผ่นบังแสง และ อนุกรมรูปภาพ

สองแนวนี้ข้อสอบจริงออกรวมกัน 20% ของพาร์ท 2 แต่คลังเรามี 0 ข้อ
(ดู reference/DIGEST-part2.md หัวข้อ 3.1)

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
    print("ตรวจผ่าน 360 ข้อ (ซ้อนแผ่น 120 · อนุกรมสองดาว 120 · อนุกรมสามดาว 120)")

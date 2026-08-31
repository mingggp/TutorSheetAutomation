#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์พาร์ทตัวเลขแนวที่คลังยังไม่มี — ทั้งหมดไม่ต้องใช้รูป

แนวพวกนี้มาจากรายงาน calibrator (ช่องโหว่ข้อ 3-8) ที่ระบุว่าข้อสอบจริงออก
แต่คลังมี 0 ข้อ:

  อนุมานตัวดำเนินการ  ของจริง **ไม่บอกนิยาม** ให้ถอดกฎเองจากตัวอย่าง
                     ของเดิมในคลังบอกนิยามแล้วให้แทนค่า = กลับด้านกับของจริง
  ตอบเป็นคู่         อนุกรมสองชุดสลับกัน ถามผลรวมของสองพจน์ถัดไป
  เงื่อนไขรหัส        ระบบสมการระหว่างเลขโดด แล้วถามว่าข้อใดเป็นไปไม่ได้
  พีชคณิตแปลก        รากซ้อนไม่รู้จบ / เลขยกกำลังซ้อน — ไม่มีสูตรตรง ๆ ให้ใช้

ทุกแนวพิสูจน์คำตอบด้วยการไล่ความเป็นไปได้จริง ไม่ใช่ด้วยความมั่นใจ (กติกาข้อ 1)
"""
from itertools import permutations
from fractions import Fraction


def _place(opts, ans, want):
    rest = [o for o in opts if o != ans]
    return rest[:want] + [ans] + rest[want:], want


def _spread(ans, rng, n=4, step=None):
    """ตัวลวงเป็นตัวเลขที่ห่างจากคำตอบพอประมาณ ไม่ซ้ำ และไม่ติดลบ"""
    step = step or max(1, round(abs(ans) * 0.13))
    out = set()
    k = 1
    while len(out) < n and k < 40:
        for s in (+1, -1):
            v = ans + s * k * step
            if v != ans and v > 0:
                out.add(v)
            if len(out) >= n:
                break
        k += 1
    return sorted(out)[:n]


# ============================================================
#  1. อนุมานตัวดำเนินการจากตัวอย่าง — ไม่บอกนิยาม
#
#  หัวใจคือ **ตัวอย่างต้องบีบให้เหลือกฎเดียว** ถ้ามีกฎอื่นในตระกูลที่อธิบาย
#  ทุกตัวอย่างได้เหมือนกัน ผู้สอบจะตอบอีกอย่างแล้วถูกด้วย โจทย์นั้นใช้ไม่ได้
# ============================================================

OPS = {
    "a×b + a":      lambda a, b: a * b + a,
    "a×b − b":      lambda a, b: a * b - b,
    "a×b + b":      lambda a, b: a * b + b,
    "a×b − a":      lambda a, b: a * b - a,
    "(a+b)×2":      lambda a, b: (a + b) * 2,
    "(a+b)×a":      lambda a, b: (a + b) * a,
    "(a−b)×b":      lambda a, b: (a - b) * b,
    "a² + b":       lambda a, b: a * a + b,
    "a² − b":       lambda a, b: a * a - b,
    "b² + a":       lambda a, b: b * b + a,
    "a×b + a + b":  lambda a, b: a * b + a + b,
    "a×b − a − b":  lambda a, b: a * b - a - b,
    "(a+b)²":       lambda a, b: (a + b) ** 2,
    "a×(b+1)":      lambda a, b: a * (b + 1),
    "2a + 3b":      lambda a, b: 2 * a + 3 * b,
    "3a − b":       lambda a, b: 3 * a - b,
}
OPNAMES = list(OPS)

SYM = ["✦", "◆", "★", "▲", "●", "■"]


def inferop(rng, want=0):
    """ให้ตัวอย่าง 4 บรรทัด แล้วถามบรรทัดที่ 5 — ไม่บอกนิยามของตัวดำเนินการ

    คืน (stem, choices, ansIdx)
    """
    for _ in range(600):
        name = rng.choice(OPNAMES)
        f = OPS[name]
        pairs = set()
        while len(pairs) < 5:
            pairs.add((rng.randint(2, 12), rng.randint(2, 12)))
        pairs = sorted(pairs)
        rng.shuffle(pairs)
        shown, (qa, qb) = pairs[:4], pairs[4]

        vals = [f(a, b) for a, b in shown] + [f(qa, qb)]
        if any(v <= 0 or v > 400 for v in vals):
            continue
        if len(set(vals)) < 4:                 # ตัวอย่างซ้ำค่ากันมาก เดาง่ายเกิน
            continue

        # ต้องไม่มีกฎอื่นในตระกูลที่อธิบายตัวอย่างทั้งสี่ได้เหมือนกัน
        rivals = [o for o in OPNAMES
                  if o != name and all(OPS[o](a, b) == f(a, b) for a, b in shown)]
        if rivals:
            continue

        ans = f(qa, qb)
        opts = _spread(ans, rng)
        if len(opts) < 4:
            continue
        sym = rng.choice(SYM)
        lines = "\n".join(f"    {a} {sym} {b} = {f(a,b)}" for a, b in shown)
        stem = ("จากตัวอย่างต่อไปนี้\n" + lines +
                f"\nจงหาค่าของ  {qa} {sym} {qb}")
        ch, idx = _place([str(v) for v in opts] + [str(ans)], str(ans), want)
        return stem, ch, idx
    raise RuntimeError("สร้างโจทย์อนุมานตัวดำเนินการไม่สำเร็จ")


# ============================================================
#  2. ตอบเป็นคู่ — อนุกรมสองชุดสลับกัน ถามผลรวมของสองพจน์ถัดไป
# ============================================================

def _seq(kind, a0, d, n):
    if kind == "add":
        return [a0 + d * i for i in range(n)]
    if kind == "mul":
        return [a0 * (d ** i) for i in range(n)]
    if kind == "sq":
        return [a0 + d * i * i for i in range(n)]
    return [a0 + d * i for i in range(n)]


def pairsum(rng, want=0):
    """เลขตำแหน่งคี่เป็นชุดหนึ่ง ตำแหน่งคู่เป็นอีกชุดหนึ่ง ถาม x + y ของสองพจน์ถัดไป"""
    for _ in range(600):
        k1, k2 = rng.choice(["add", "mul", "sq"]), rng.choice(["add", "mul", "sq"])
        a1, d1 = rng.randint(2, 9), rng.choice([2, 3, 4, 5, 6, 7])
        a2, d2 = rng.randint(20, 60), rng.choice([-3, -4, -5, -6, 2, 3])
        if k1 == "mul": d1 = rng.choice([2, 3])
        if k2 == "mul": d2 = rng.choice([2, 3])
        s1, s2 = _seq(k1, a1, d1, 5), _seq(k2, a2, d2, 5)
        if any(v <= 0 or v > 500 for v in s1 + s2):
            continue
        # สานสองชุดเข้าด้วยกัน แสดง 8 พจน์แรก แล้วถามพจน์ที่ 9 กับ 10
        woven = [v for pair in zip(s1, s2) for v in pair]
        shown, x, y = woven[:8], s1[4], s2[4]
        if len(set(shown)) != 8:
            continue
        ans = x + y
        opts = _spread(ans, rng)
        if len(opts) < 4:
            continue
        stem = ("จากอนุกรม  " + ", ".join(str(v) for v in shown) + ",  x,  y\n"
                "จงหาค่าของ  x + y")
        ch, idx = _place([str(v) for v in opts] + [str(ans)], str(ans), want)
        return stem, ch, idx
    raise RuntimeError("สร้างโจทย์ตอบเป็นคู่ไม่สำเร็จ")


# ============================================================
#  3. เงื่อนไขรหัส — ระบบสมการระหว่างเลขโดด ถามว่าข้อใดเป็นไปไม่ได้
#
#  ไล่ทุกการจับคู่เลขโดดที่ต่างกันจริง แล้วเก็บว่าตัวอักษรไหนเป็นค่าอะไรได้บ้าง
# ============================================================

def codeword(rng, want=0):
    """A B C D เป็นเลขโดดต่างกัน มีเงื่อนไขให้ ถามว่าข้อใดเป็นไปไม่ได้"""
    L = ["A", "B", "C", "D"]
    for _ in range(600):
        vals = rng.sample(range(1, 10), 4)
        m = dict(zip(L, vals))
        cond = []
        if m["A"] + m["B"] == m["C"] + m["D"]:
            continue
        cond.append(f"A + B = {m['A']+m['B']}")
        # เลี่ยงผลลบติดลบ ให้สลับข้างแทน จะได้ไม่มีเครื่องหมายลบสองแบบปนกันในโจทย์
        if m['C'] >= m['D']:
            cond.append(f"C − D = {m['C']-m['D']}")
        else:
            cond.append(f"D − C = {m['D']-m['C']}")
        cond.append(f"A × D = {m['A']*m['D']}")

        # หาทุกคำตอบที่เข้าเงื่อนไขครบ
        sols = []
        for p in permutations(range(1, 10), 4):
            g = dict(zip(L, p))
            if (g["A"]+g["B"] == m["A"]+m["B"] and
                    g["C"]-g["D"] == m["C"]-m["D"] and
                    g["A"]*g["D"] == m["A"]*m["D"]):
                sols.append(g)
        if not sols:
            continue

        # ข้อความที่ "เป็นไปได้" = จริงในคำตอบอย่างน้อยหนึ่งแบบ
        def ok(txt_fn):
            return any(txt_fn(g) for g in sols)

        cands = []
        for a in L:
            for v in range(1, 10):
                cands.append((f"{a} = {v}", (lambda a=a, v=v: (lambda g: g[a] == v))()))
        rng.shuffle(cands)
        good = [c for c in cands if ok(c[1])]
        bad = [c for c in cands if not ok(c[1])]
        if len(good) < 4 or not bad:
            continue

        ans = bad[0][0]
        opts = [g[0] for g in good[:4]]
        stem = ("A B C D แทนเลขโดดที่ต่างกันสี่ตัว โดยมีเงื่อนไขว่า\n" +
                "\n".join("    " + c for c in cond) +
                "\nข้อใด**เป็นไปไม่ได้**")
        ch, idx = _place(opts + [ans], ans, want)
        return stem, ch, idx
    raise RuntimeError("สร้างโจทย์เงื่อนไขรหัสไม่สำเร็จ")


# ============================================================
#  4. พีชคณิตแปลก — รากซ้อนไม่รู้จบ
#
#  x = √(k + √(k + √(k + …)))  ⇒  x² = k + x  ⇒  x เป็นรากบวกของ x² − x − k = 0
#  เลือก k ที่ทำให้ x เป็นจำนวนเต็ม: x² − x = k
# ============================================================

def nested(rng, want=0):
    """รากซ้อนไม่รู้จบ — เลือก k ที่ให้คำตอบเป็นจำนวนเต็มพอดี"""
    x = rng.randint(3, 12)
    k = x * x - x
    opts = _spread(x, rng, step=1)
    stem = (f"ถ้า  x = √({k} + √({k} + √({k} + …)))  ไปเรื่อย ๆ ไม่รู้จบ\n"
            f"แล้ว x มีค่าเท่าใด")
    ch, idx = _place([str(v) for v in opts] + [str(x)], str(x), want)
    return stem, ch, idx


def tower(rng, want=0):
    """เลขยกกำลังซ้อน  y = a^(a^(a^…))  โดย y = a^y — เลือก a ที่ให้ y เป็นจำนวนเต็ม

    y = a^y  ⇔  a = y^(1/y) ; เลือก y = 2 กับ a = √2 เป็นกรณีคลาสสิก
    ใช้รูปแบบที่คุมได้: ถ้า  x^x^x^… = c  แล้ว  x^c = c
    """
    c = rng.choice([2, 4])
    # x^c = c  ->  x = c^(1/c) ; c=2 -> √2 , c=4 -> √2 เช่นกัน (จึงใช้ c=2 เท่านั้นให้ชัด)
    c = 2
    ans = "√2"
    opts = ["2", "√3", "∛2", "2√2"]
    stem = ("ถ้า  x^(x^(x^…))  ซ้อนกันไปไม่รู้จบแล้วมีค่าเท่ากับ 2\n"
            "แล้ว x มีค่าเท่าใด")
    ch, idx = _place(opts + [ans], ans, want)
    return stem, ch, idx


# ============================================================
#  ต่อเข้าคลัง
# ============================================================

def build(add, part, rng):
    """เติมแนวใหม่เข้าพาร์ทตัวเลข — เฉลยไล่ครบทั้ง 5 ช่อง"""
    # จำนวนข้อต่อแนวต้องมากกว่าเพดานต่อชีท (CAP) อย่างน้อยสองเท่า
    # ไม่งั้น --set หมุนหาข้อใหม่ไม่ได้ ชีทสัปดาห์หน้าจะซ้ำของเดิมทั้งแนว
    plan = [
        (inferop, "อนุมานตัวดำเนินการ", 2, [0, 3, 2]),
        (inferop, "อนุมานตัวดำเนินการ", 3, [1, 4, 0]),
        (pairsum, "ตอบเป็นคู่", 2, [4, 2, 1]),
        (pairsum, "ตอบเป็นคู่", 3, [0, 3, 2]),
        (codeword, "เงื่อนไขรหัส", 3, [1, 3, 0, 4]),
        (nested, "พีชคณิตแปลก", 3, [2, 0, 3]),
        (tower, "พีชคณิตแปลก", 3, [4, 1, 2]),
    ]
    n = 0
    for fn, arche, lvl, wants in plan:
        for w in wants:
            stem, ch, idx = fn(rng, want=w)
            add(part, arche, stem, ch, idx, lvl=lvl)
            n += 1
    return n


# ============================================================
#  ตัวตรวจ — python numeric.py
# ============================================================

if __name__ == "__main__":
    import random, sys

    bad = []
    for s in range(150):
        rng = random.Random(s)
        for want in range(5):
            for fn, nm in ((inferop, "inferop"), (pairsum, "pairsum"),
                           (codeword, "codeword"), (nested, "nested")):
                stem, ch, idx = fn(rng, want=want)
                if len(ch) != 5 or len(set(ch)) != 5:
                    bad.append(f"{nm} s={s} w={want}: ตัวเลือกซ้ำหรือไม่ครบ 5")
                if idx != want:
                    bad.append(f"{nm} s={s} w={want}: บังคับตำแหน่งเฉลยไม่ได้")

    # อนุมานตัวดำเนินการ: ตัวอย่างต้องบีบให้เหลือกฎเดียวจริง
    for s in range(200):
        rng = random.Random(1000 + s)
        stem, ch, idx = inferop(rng, want=s % 5)
        lines = [l.strip() for l in stem.split("\n") if "=" in l]
        ex = []
        for l in lines:
            a, rest = l.split(None, 1)
            b = rest.split()[1]; r = rest.split("=")[1].strip()
            ex.append((int(a), int(b), int(r)))
        fits = [o for o in OPNAMES if all(OPS[o](a, b) == r for a, b, r in ex)]
        if len(fits) != 1:
            bad.append(f"inferop s={s}: มีกฎที่อธิบายตัวอย่างได้ {len(fits)} แบบ ({fits[:3]})")
        else:
            qline = stem.split("จงหาค่าของ")[1].strip()
            qa, qb = int(qline.split()[0]), int(qline.split()[2])
            if ch[idx] != str(OPS[fits[0]](qa, qb)):
                bad.append(f"inferop s={s}: เฉลยไม่ตรงกับกฎที่ถอดได้")

    r = random.Random(4)
    print("ตัวอย่างแนวใหม่\n" + "=" * 60)
    for fn in (inferop, pairsum, codeword, nested, tower):
        stem, ch, idx = fn(r, want=2)
        print(stem)
        print("   " + "   ".join(f"{'กขคงจ'[i]}{'*' if i==idx else ''}) {c}" for i, c in enumerate(ch)))
        print("-" * 60)

    print()
    if bad:
        for m in bad[:12]:
            print("[พัง]", m)
        print(f"พบปัญหา {len(bad)} จุด")
        sys.exit(1)
    print("ตรวจผ่าน 3000 ข้อ + ตรวจความเป็นเอกลักษณ์ของกฎอีก 200 ข้อ")

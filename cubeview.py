#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""แนวลูกบาศก์สองแบบที่ถอดจากไฟล์ที่ติวเตอร์ส่งมา ชุดที่ 8

  ข้อ 6  อนุกรมทรงลูกบาศก์   ให้รูปที่ 1-3 แล้วถามว่ารูปที่ 5 มีกี่ลูก
                             ของจริงเป็นอนุกรมที่ผลต่างไม่คงที่ เด็กที่บวกผลต่างเดิมจะตอบผิด
  ข้อ 7  ภาพฉายสามด้าน       ให้ภาพด้านหน้า ด้านข้าง ด้านบน ถามจำนวนลูกบาศก์ที่น้อยที่สุด
                             (ถามมากที่สุดก็ได้ เป็นคนละคำถามในแนวเดียวกัน)

เรื่องทิศทางของภาพฉาย — ภาพด้านข้างพลิกซ้ายขวาแล้วความหมายจะเปลี่ยน
เราจึงรับเฉพาะรูปทรงที่ภาพด้านข้างอ่านกลับหน้ากลับหลังแล้วได้คำตอบเท่าเดิม
เด็กที่ตีความทิศต่างจากเราจึงยังได้คำตอบเดียวกัน

ทุกข้อพิสูจน์ด้วยโค้ด — ค่าน้อยที่สุด/มากที่สุดได้จากการไล่ความสูงทุกแบบที่เป็นไปได้จริง
"""
import itertools
import random

import draw as D

N = 3          # ตารางฐาน 3x3
HMAX = 3       # ความสูงมากสุด 3 ชั้น — ไล่ครบทุกแบบได้ในเสี้ยววินาที


def _views(h):
    """h[y][x] = ความสูง  ->  (ภาพด้านบน, ความสูงเงาด้านหน้ารายคอลัมน์, รายแถว)"""
    top = tuple(tuple(1 if h[y][x] else 0 for x in range(N)) for y in range(N))
    fx = tuple(max(h[y][x] for y in range(N)) for x in range(N))
    sy = tuple(max(h[y][x] for x in range(N)) for y in range(N))
    return top, fx, sy


def _solve(top, fx, sy):
    """ไล่ความสูงทุกแบบที่ให้ภาพฉายตรงกันเป๊ะ แล้วคืน (น้อยสุด, มากสุด)

    ช่องที่ภาพด้านบนว่างต้องสูง 0 · ช่องที่ทึบสูงได้ตั้งแต่ 1 ถึง min(fx, sy)
    จำนวนแบบมากสุดคือ 3**9 ซึ่งไล่หมดได้จริง จึงไม่ใช่การเดา
    """
    cells = [(y, x) for y in range(N) for x in range(N) if top[y][x]]
    rng = []
    for y, x in cells:
        hi = min(fx[x], sy[y])
        if hi < 1:
            return None
        rng.append(range(1, hi + 1))
    lo = hi = None
    for combo in itertools.product(*rng):
        g = [[0] * N for _ in range(N)]
        for (y, x), v in zip(cells, combo):
            g[y][x] = v
        if _views(g) != (top, fx, sy):
            continue
        t = sum(combo)
        lo = t if lo is None else min(lo, t)
        hi = t if hi is None else max(hi, t)
    return None if lo is None else (lo, hi)


def _plates(top, fx, sy, cell=26):
    """ภาพฉายสามด้าน — ด้านหน้ากับด้านข้างเป็นเงา จึงทึบจากพื้นขึ้นไปเสมอ"""
    zz = max(max(fx), max(sy))
    front = [[1 if zz - z <= fx[x] else 0 for x in range(N)] for z in range(zz)]
    side = [[1 if zz - z <= sy[y] else 0 for y in range(N)] for z in range(zz)]
    return front, side, [list(r) for r in top], cell


def view_q(rng, want=0, tag=0, ask="min"):
    for _ in range(400):
        h = [[rng.choice([0, 0, 1, 1, 2, 2, 3]) for _ in range(N)] for _ in range(N)]
        top, fx, sy = _views(h)
        filled = sum(sum(r) for r in top)
        if not 4 <= filled <= 7:
            continue
        if len(set(fx)) < 2 or len(set(sy)) < 2:
            continue                   # เงาแบนราบ อ่านแล้วไม่ได้ข้อมูล
        got = _solve(top, fx, sy)
        if not got:
            continue
        lo, hi = got
        if lo == hi:
            continue                   # รูปทรงเดียวเท่านั้นที่เป็นไปได้ ไม่มีอะไรให้คิด
        flip = _solve(tuple(r[::-1] for r in top), fx, sy[::-1])
        if flip != got:
            continue                   # อ่านภาพด้านข้างกลับด้านแล้วคำตอบเปลี่ยน — ทิ้ง
        truth = lo if ask == "min" else hi
        pool = [lo, hi, filled, truth + 1, truth - 1, truth + 2, filled + zsum(fx)]
        opts, seen = [truth], {truth}
        for c in pool:
            if c > 0 and c not in seen and len(opts) < 5:
                seen.add(c)
                opts.append(c)
        k = truth + 3
        while len(opts) < 5:
            if k not in seen:
                seen.add(k)
                opts.append(k)
            k += 1
        opts = sorted(opts)
        return {"top": top, "fx": fx, "sy": sy, "lo": lo, "hi": hi,
                "opts": opts, "ansIdx": opts.index(truth), "ask": ask, "tag": tag}
    return None


def zsum(t):
    return sum(t)


# ---------------------------------------------------------------- อนุกรมทรงลูกบาศก์
def _stair(n):
    return [(i, 0, k) for i in range(n) for k in range(n - i)]


def _arms(n):
    v = [(0, 0, 0)]
    for i in range(1, n):
        v += [(i, 0, 0), (0, i, 0), (0, 0, i)]
    return v


def _basecol(n):
    return ([(i, j, 0) for i in range(n) for j in range(n)] +
            [(0, 0, k) for k in range(1, n)])


def _frame(n):
    if n == 1:
        return [(0, 0, 0)]
    return [(i, j, 0) for i in range(n) for j in range(n)
            if i in (0, n - 1) or j in (0, n - 1)]


def _pyramid(n):
    return [(i, j, k) for k in range(n) for i in range(n - k) for j in range(n - k)]


def _plus(n):
    mid = n - 1
    w = 2 * n - 1
    return [(i, j, 0) for i in range(w) for j in range(w) if i == mid or j == mid]


FAM = [("บันได", _stair), ("แขนสามทิศ", _arms), ("ฐานจัตุรัสมีเสา", _basecol),
       ("กรอบสี่เหลี่ยม", _frame), ("พีระมิดขั้นบันได", _pyramid), ("กากบาท", _plus)]


def grow_q(rng, want=0, tag=0):
    """ให้รูปที่ 1-3 ถามจำนวนลูกบาศก์ของรูปที่ 5 หรือ 6

    ตัวลวงหลักคือ "บวกผลต่างเดิมต่อไปเรื่อย ๆ" ซึ่งเป็นวิธีที่เด็กใช้แล้วผิด
    เพราะผลต่างของอนุกรมพวกนี้ไม่คงที่
    """
    for _ in range(200):
        name, fn = FAM[rng.randrange(len(FAM))]
        target = rng.choice([5, 6])
        cnt = [len(set(fn(k))) for k in range(1, target + 1)]
        if len(set(cnt)) < target or cnt[2] > 30:
            continue
        truth = cnt[-1]
        d = cnt[2] - cnt[1]
        linear = cnt[2] + d * (target - 3)            # เดินผลต่างเดิมต่อไป
        pool = [linear, cnt[-2], truth + 1, truth - 1, truth + cnt[0],
                cnt[2] * (target - 2), truth + 3, truth - 3]
        opts, seen = [truth], {truth}
        for c in pool:
            if c > 0 and c not in seen and len(opts) < 5:
                seen.add(c)
                opts.append(c)
        k = truth + 4
        while len(opts) < 5:
            if k not in seen:
                seen.add(k)
                opts.append(k)
            k += 1
        opts = sorted(opts)
        return {"name": name, "fn": fn, "target": target, "cnt": cnt,
                "opts": opts, "ansIdx": opts.index(truth), "tag": tag}
    return None


def build(add, P2, rng):
    """เติมสองแนวนี้เข้าคลัง — เรียกจาก gen.py"""
    want = 0
    for qi in range(4):
        ask = "min" if qi % 2 == 0 else "max"
        r = view_q(rng, want=want, tag=qi, ask=ask)
        if not r:
            continue
        front, side, top, cell = _plates(r["top"], r["fx"], r["sy"])
        img = D.views([D.plate(front, f"cvf{qi}", cell=cell),
                       D.plate(side, f"cvs{qi}", cell=cell),
                       D.plate(top, f"cvt{qi}", cell=cell)], f"cvq{qi}")
        word = "น้อยที่สุด" if ask == "min" else "มากที่สุด"
        add(P2, "ภาพฉายสามด้าน · นับลูกบาศก์",
            "นำลูกบาศก์ขนาดเท่ากันมาวางซ้อนกันบนพื้น จนมองเห็นเป็นภาพฉายสามด้านดังรูป\n"
            "ภาพด้านบนวางให้ด้านหน้าของรูปทรงอยู่ที่ขอบล่างของภาพ\n"
            f"จะต้องใช้ลูกบาศก์อย่าง{word}กี่ลูก",
            [str(o) for o in r["opts"]], r["ansIdx"], img=img, lvl=3,
            why=("ช่องที่เห็นจากด้านบนต้องมีอย่างน้อย 1 ลูก แล้วต่อให้สูงพอดีเงาทั้งสองด้าน"
                 if ask == "min" else
                 "แต่ละช่องสูงได้มากสุดเท่ากับเงาที่เตี้ยกว่าของแถวกับคอลัมน์นั้น"))
        want = (want + 2) % 5

    for qi in range(3):
        r = grow_q(rng, want=want, tag=qi)
        if not r:
            continue
        figs = [D.iso(r["fn"](k), f"cgf{qi}_{k}", cell=15, ch=13, pad=7)
                for k in (1, 2, 3)]
        img = D.compose(figs, f"cgq{qi}", gap=26,
                        capt=[f"รูปที่ {k}" for k in (1, 2, 3)])
        add(P2, "อนุกรมทรงลูกบาศก์",
            "รูปที่ 1 ถึงรูปที่ 3 สร้างต่อกันด้วยกฎเดียวกัน และสร้างต่อไปเรื่อย ๆ ด้วยกฎเดิม\n"
            f"รูปที่ {r['target']} จะมีลูกบาศก์ทั้งหมดกี่ลูก",
            [str(o) for o in r["opts"]], r["ansIdx"], img=img, lvl=3,
            why="ผลต่างไม่คงที่ ต้องหาผลต่างของผลต่างก่อน แล้วค่อยไล่ต่อทีละรูป")
        want = (want + 2) % 5


if __name__ == "__main__":
    bad, n = [], 0

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    for s in range(120):
        rng = random.Random(s)
        for w in range(5):
            for ask in ("min", "max"):
                r = view_q(rng, want=w, ask=ask)
                if not r:
                    continue
                n += 1
                ck(len(set(r["opts"])) == 5, f"ภาพฉาย s={s}: ตัวเลือกซ้ำ")
                truth = r["lo"] if ask == "min" else r["hi"]
                ck(r["opts"][r["ansIdx"]] == str(truth) or
                   r["opts"][r["ansIdx"]] == truth, f"ภาพฉาย s={s}: เฉลยไม่ตรง")
                ck(sum(1 for o in r["opts"] if o == truth) == 1,
                   f"ภาพฉาย s={s}: มีตัวเลือกถูกเกินหนึ่ง")
                got = _solve(r["top"], r["fx"], r["sy"])
                ck(got == (r["lo"], r["hi"]), f"ภาพฉาย s={s}: คำนวณซ้ำแล้วไม่ตรง")
                ck(_solve(tuple(t[::-1] for t in r["top"]), r["fx"], r["sy"][::-1]) == got,
                   f"ภาพฉาย s={s}: อ่านด้านข้างกลับด้านแล้วคำตอบเปลี่ยน")

            r = grow_q(rng, want=w)
            if r:
                n += 1
                ck(len(set(r["opts"])) == 5, f"ทรงลูกบาศก์ s={s}: ตัวเลือกซ้ำ")
                real = len(set(r["fn"](r["target"])))
                ck(r["opts"][r["ansIdx"]] == real, f"ทรงลูกบาศก์ s={s}: เฉลยไม่ตรงกับจำนวนจริง")
                ck(sum(1 for o in r["opts"] if o == real) == 1,
                   f"ทรงลูกบาศก์ s={s}: มีตัวเลือกถูกเกินหนึ่ง")
                for k in range(1, 4):     # รูปที่วาดจริงต้องนับได้ตามที่บอก
                    ck(len(set(r["fn"](k))) == r["cnt"][k - 1],
                       f"ทรงลูกบาศก์ s={s}: จำนวนของรูปที่ {k} ไม่ตรง")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:10]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ — ภาพฉายสามด้าน · อนุกรมทรงลูกบาศก์")

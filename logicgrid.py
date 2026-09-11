#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""แนวพาร์ทมิติสัมพันธ์ที่ถอดจากไฟล์ที่ติวเตอร์ส่งมา

  เมทริกซ์ตรรกะ    คอลัมน์ที่สามมาจากสองคอลัมน์แรกด้วยกฎตรรกะระดับช่อง
                   ชุดที่ 5 ข้อ 23 ลายมือเขียนกฎไว้ตรง ๆ ว่า
                   ดำ+ขาว=ดำ · ดำ+ดำ=ขาว · ขาว+ขาว=ขาว ซึ่งคือ XOR
  อนุกรมช่องกลางหาย  ไม่ได้ถามภาพถัดไป แต่ถามภาพที่หายกลางลำดับ
                   ยากกว่าเพราะต้องต่อจากทั้งสองทาง ไม่ใช่เดินหน้าอย่างเดียว

ทุกข้อพิสูจน์ด้วยโค้ด — ยืนยันว่ามีตัวเลือกเดียวที่ตรงกับกฎ (กติกาข้อ 1)
"""
import random

import draw as D

OPS = {
    "xor": (lambda a, b: a ^ b, "ต่างกันได้ทึบ เหมือนกันได้โปร่ง"),
    "and": (lambda a, b: a & b, "ทึบทั้งคู่จึงได้ทึบ"),
    "or":  (lambda a, b: a | b, "ทึบอย่างน้อยหนึ่งช่องก็ได้ทึบ"),
    "nor": (lambda a, b: 1 - (a | b), "โปร่งทั้งคู่จึงได้ทึบ"),
}


def _rand(rng, n, p=0.4):
    return tuple(tuple(1 if rng.random() < p else 0 for _ in range(n))
                 for _ in range(n))


def _combine(a, b, f):
    return tuple(tuple(f(x, y) for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def _cells(g):
    return [(r, c) for r, row in enumerate(g) for c, v in enumerate(row) if v]


def _qmark(n, name, cell=20):
    """ช่องเครื่องหมายคำถามขนาดเท่าตารางอื่น — D.grid รับ text เป็น dict ของช่อง"""
    mid = (n // 2, n // 2) if n % 2 else (n // 2 - 1, n // 2)
    return D.grid(n, n, name=name, cell=cell, text={mid: "?"})


def matrix_q(rng, want=0, n=4, tag=0):
    """สามแถว แต่ละแถวคอลัมน์ที่สามมาจากสองคอลัมน์แรกด้วยกฎเดียวกัน"""
    for _ in range(500):
        key = rng.choice(list(OPS))
        f, why = OPS[key]
        rows = []
        for _ in range(3):
            a, b = _rand(rng, n, rng.uniform(.3, .5)), _rand(rng, n, rng.uniform(.3, .5))
            rows.append((a, b, _combine(a, b, f)))
        truth = rows[2][2]
        if sum(sum(r) for r in truth) in (0, n * n):
            continue                       # ผลลัพธ์โล่งหรือทึบหมด เดาได้ง่ายเกิน
        opts, seen = [truth], {truth}
        a3, b3 = rows[2][0], rows[2][1]
        for k2 in OPS:                     # ตัวลวง = ใช้กฎตรรกะตัวอื่น
            if k2 == key:
                continue
            cand = _combine(a3, b3, OPS[k2][0])
            if cand not in seen:
                seen.add(cand)
                opts.append(cand)
        for cand in (a3, b3):              # และ = ลอกคอลัมน์มาตรง ๆ
            if cand not in seen:
                seen.add(cand)
                opts.append(cand)
        if len(opts) < 5:
            continue
        opts = opts[:5]
        rest = [o for o in opts if o != truth]
        opts = rest[:want] + [truth] + rest[want:]
        opts = opts[:5]
        return {"rows": rows, "opts": opts, "ansIdx": opts.index(truth),
                "key": key, "why": why, "n": n, "tag": tag}
    return None


def _inv(g):
    return tuple(tuple(1 - v for v in r) for r in g)


def _rot(g):
    return tuple(zip(*g[::-1]))


def _down(g):
    return (g[-1],) + g[:-1]


def _right(g):
    return tuple((r[-1],) + r[:-1] for r in g)


# กฎเดี่ยวบนตาราง 4x4 มีคาบ 4 พอดี ภาพที่ 5 จึงซ้ำภาพแรกเสมอ
# กฎผสมที่ต่อด้วยการสลับทึบ-โปร่งจะมีคาบ 8 จึงวางลำดับ 5 ภาพได้ และยากขึ้นด้วย
RULES = {
    "หมุนตามเข็ม 90 องศา": _rot,
    "เลื่อนลง 1 แถว": _down,
    "เลื่อนขวา 1 ช่อง": _right,
    "หมุนตามเข็ม 90 องศาแล้วสลับทึบกับโปร่ง": lambda g: _inv(_rot(g)),
    "เลื่อนลง 1 แถวแล้วสลับทึบกับโปร่ง": lambda g: _inv(_down(g)),
    "เลื่อนขวา 1 ช่องแล้วสลับทึบกับโปร่ง": lambda g: _inv(_right(g)),
}


def middle_q(rng, want=0, n=4, tag=0):
    """ลำดับห้าภาพ ซ่อนภาพกลาง ถามว่าภาพที่หายคือภาพใด

    ต้องตรวจว่าไม่มีภาพอื่นในลำดับซ้ำกับคำตอบ ไม่งั้นเดาจากภาพข้าง ๆ ได้
    """
    for _ in range(500):
        name = rng.choice(list(RULES))
        step = RULES[name]
        g0 = _rand(rng, n, rng.uniform(.3, .45))
        frames = [g0]
        for _ in range(4):
            frames.append(step(frames[-1]))
        if len(set(frames)) < 5:
            frames = frames[:4]            # กฎคาบสั้น ใช้ลำดับสี่ภาพแทน ไม่ต้องทิ้งข้อ
        if len(set(frames)) < len(frames):
            continue
        hide = rng.choice(list(range(1, len(frames) - 1)))
        truth = frames[hide]
        opts, seen = [truth], {truth}
        for cand in (frames[hide - 1], frames[hide + 1],
                     step(step(truth)), _rand(rng, n, .4)):
            if cand not in seen:
                seen.add(cand)
                opts.append(cand)
        while len(opts) < 5:
            cand = _rand(rng, n, .4)
            if cand not in seen:
                seen.add(cand)
                opts.append(cand)
        opts = opts[:5]
        rest = [o for o in opts if o != truth]
        opts = rest[:want] + [truth] + rest[want:]
        opts = opts[:5]
        return {"frames": frames, "hide": hide, "opts": opts,
                "ansIdx": opts.index(truth), "name": name, "n": n, "tag": tag}
    return None


def build(add, P2, rng):
    """เติมสองแนวนี้เข้าคลัง — เรียกจาก gen.py"""
    want = 0
    for qi in range(3):
        r = matrix_q(rng, want=want, tag=qi)
        if not r:
            continue
        n = r["n"]
        rowimgs = []
        for k, (a, b, c) in enumerate(r["rows"]):
            cells = [D.grid(n, n, filled=_cells(a), name=f"lga{qi}{k}", cell=20),
                     D.grid(n, n, filled=_cells(b), name=f"lgb{qi}{k}", cell=20)]
            cells.append(D.grid(n, n, filled=_cells(c), name=f"lgc{qi}{k}", cell=20)
                         if k < 2 else
                         _qmark(n, f"lgq{qi}"))
            rowimgs.append(D.compose(cells, f"lgr{qi}{k}", seps=["+", "="], gap=14))
        img = D.vstack(rowimgs, f"lgm{qi}", gap=12)
        files = [D.grid(n, n, filled=_cells(o), name=f"lgo{qi}_{j}", cell=20)
                 for j, o in enumerate(r["opts"])]
        add(P2, "เมทริกซ์ตรรกะ",
            "ทุกแถวใช้กฎเดียวกันในการรวมสองตารางซ้ายให้เป็นตารางขวา\n"
            "ตารางในช่องเครื่องหมายคำถามคือข้อใด",
            [""] * 5, r["ansIdx"], img=img, optimg=D.strip(files, f"lgopt{qi}"),
            lvl=3, why="กฎรวมระดับช่อง · " + r["why"])
        want = (want + 2) % 5

    for qi in range(3):
        r = middle_q(rng, want=want, tag=qi)
        if not r:
            continue
        n = r["n"]
        seq = []
        for k, g in enumerate(r["frames"]):
            seq.append(_qmark(n, f"lmq{qi}")
                       if k == r["hide"] else
                       D.grid(n, n, filled=_cells(g), name=f"lms{qi}{k}", cell=20))
        img = D.compose(seq, f"lmr{qi}", seps=[""] * (len(seq) - 1), gap=12)
        files = [D.grid(n, n, filled=_cells(o), name=f"lmo{qi}_{j}", cell=20)
                 for j, o in enumerate(r["opts"])]
        add(P2, "อนุกรมรูปช่องกลางหาย",
            f"ภาพทั้ง{'ห้า' if len(r['frames']) == 5 else 'สี่'}เรียงตามกฎเดียวกัน "
            "ภาพในช่องเครื่องหมายคำถามคือข้อใด",
            [""] * 5, r["ansIdx"], img=img, optimg=D.strip(files, f"lmopt{qi}"),
            lvl=3, why="ต่อจากภาพข้างหน้าและถอยจากภาพข้างหลังให้ตรงกัน · " + r["name"])
        want = (want + 2) % 5


if __name__ == "__main__":
    bad, n = [], 0

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    for s in range(300):
        rng = random.Random(s)
        for w in range(5):
            r = matrix_q(rng, want=w)
            if r:
                n += 1
                ck(len(set(r["opts"])) == 5, f"เมทริกซ์ตรรกะ s={s}: ตัวเลือกซ้ำ")
                f = OPS[r["key"]][0]
                a3, b3, c3 = r["rows"][2]
                ck(_combine(a3, b3, f) == c3, f"เมทริกซ์ตรรกะ s={s}: แถวสุดท้ายไม่ตรงกฎ")
                ck(r["opts"][r["ansIdx"]] == c3, f"เมทริกซ์ตรรกะ s={s}: เฉลยไม่ตรง")
                ck(sum(1 for o in r["opts"] if o == c3) == 1,
                   f"เมทริกซ์ตรรกะ s={s}: มีตัวเลือกถูกเกินหนึ่ง")
                for a, b, c in r["rows"]:      # ทุกแถวต้องใช้กฎเดียวกันจริง
                    ck(_combine(a, b, f) == c, f"เมทริกซ์ตรรกะ s={s}: กฎไม่สม่ำเสมอ")

            r = middle_q(rng, want=w)
            if r:
                n += 1
                ck(len(set(r["opts"])) == 5, f"ช่องกลางหาย s={s}: ตัวเลือกซ้ำ")
                ck(r["opts"][r["ansIdx"]] == r["frames"][r["hide"]],
                   f"ช่องกลางหาย s={s}: เฉลยไม่ใช่ภาพที่หาย")
                step = RULES[r["name"]]
                for k in range(len(r["frames"]) - 1):
                    ck(step(r["frames"][k]) == r["frames"][k + 1],
                       f"ช่องกลางหาย s={s}: ลำดับไม่เดินตามกฎ")
                ck(len(set(r["frames"])) == len(r["frames"]),
                   f"ช่องกลางหาย s={s}: มีภาพซ้ำในลำดับ")
                ck(0 < r["hide"] < len(r["frames"]) - 1,
                   f"ช่องกลางหาย s={s}: ภาพที่ซ่อนไม่ได้อยู่กลางลำดับ")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:10]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ — เมทริกซ์ตรรกะ · อนุกรมรูปช่องกลางหาย")

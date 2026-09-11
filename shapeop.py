#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ตัวดำเนินการสัญลักษณ์รูป — แนวที่ข้อสอบจริงออกราว 8 เปอร์เซ็นต์ของพาร์ทมิติสัมพันธ์

ที่มา: ไฟล์ที่ติวเตอร์ส่งมา ชุดที่ 4 ข้อ 21 และชุดที่ 6 ข้อ 24-25
ชุดที่ 6 พิมพ์ตารางความหมายของตัวดำเนินการไว้ครบ เราจึงใช้ชุดเดียวกับของจริง

    กลับหัวทุกรูป · เลื่อนซ้าย 1 · เลื่อนขวา 1 · สลับหัวท้าย · หมุนตามเข็ม 90 · สลับการระบาย

**สองรูปแบบคำถาม** ตามที่ของจริงออก
  chain    ให้แถวตั้งต้นกับลำดับตัวดำเนินการ ถามผลลัพธ์
  missing  ให้แถวตั้งต้นกับแถวผลลัพธ์ ถามว่าตัวดำเนินการที่หายไปคือตัวใด

ทุกข้อพิสูจน์ด้วยโค้ด — ไล่ผลของทุกตัวเลือกแล้วยืนยันว่ามีตัวเดียวที่ตรง (กติกาข้อ 1)
"""
import random

import draw as D

OPS = {
    "flip":  lambda r: [(k, (d + 180) % 360, f) for k, d, f in r],
    "rotcw": lambda r: [(k, (d + 90) % 360, f) for k, d, f in r],
    "left":  lambda r: r[1:] + r[:1],
    "right": lambda r: r[-1:] + r[:-1],
    "swap":  lambda r: [r[-1]] + r[1:-1] + [r[0]],
    "fill":  lambda r: [(k, d, not f) for k, d, f in r],
}
NAMES = list(OPS)


def apply_all(row, ops):
    for o in ops:
        row = OPS[o](row)
    return row


def _rand_row(rng, n=4):
    """แถวตั้งต้นต้องมีรูปไม่ซ้ำกันและมีทั้งทึบทั้งโปร่ง ไม่งั้นตัวดำเนินการบางตัวไม่เห็นผล"""
    kinds = rng.sample(D.SHAPE_KINDS, n)
    row = [(k, rng.choice([0, 90, 180, 270]), rng.random() < .5) for k in kinds]
    if len({f for _k, _d, f in row}) < 2:
        row[0] = (row[0][0], row[0][1], not row[0][2])
    return row


def _place(opts, truth, want):
    rest = [o for o in opts if o != truth]
    out = rest[:want] + [truth] + rest[want:]
    return out[:5], want


def chain_q(rng, want=0, steps=3, tag=0):
    """ให้ลำดับตัวดำเนินการ ถามแถวผลลัพธ์ — ตัวลวงมาจากลำดับที่ผิดจริง"""
    for _ in range(500):
        row = _rand_row(rng)
        ops = [rng.choice(NAMES) for _ in range(steps)]
        if len(set(ops)) < 2:
            continue
        truth = tuple(apply_all(row, ops))
        if truth == tuple(row):
            continue                      # ผลลัพธ์เท่าเดิม ข้อนี้ไม่วัดอะไร
        seen, opts = {truth}, [truth]
        for _ in range(400):              # ตัวลวง = สลับลำดับ หรือใช้ตัวดำเนินการผิดตัว
            alt = ops[:]
            if rng.random() < .5:
                i, j = rng.randrange(steps), rng.randrange(steps)
                alt[i], alt[j] = alt[j], alt[i]
            else:
                alt[rng.randrange(steps)] = rng.choice(NAMES)
            cand = tuple(apply_all(row, alt))
            if cand in seen:
                continue
            seen.add(cand)
            opts.append(cand)
            if len(opts) == 5:
                break
        if len(opts) < 5:
            continue
        opts, _ = _place(opts, truth, want)
        used = sorted(set(ops), key=NAMES.index)
        mark = {o: D.OP_MARK[i] for i, o in enumerate(used)}
        legend = [(mark[o], D.OP_TEXT[o]) for o in used]
        order = " ".join(mark[o] for o in ops)
        return {"row": row, "ops": ops, "legend": legend, "order": order,
                "opts": [list(o) for o in opts], "ansIdx": opts.index(truth),
                "mark": mark, "tag": tag}
    return None


def missing_q(rng, want=0, steps=3, tag=0):
    """ซ่อนตัวดำเนินการหนึ่งตัวในลำดับ ถามว่าตัวที่หายคือตัวใด

    ต้องยืนยันว่ามีตัวดำเนินการเดียวเท่านั้นที่เติมแล้วได้ผลลัพธ์ตรง
    ไม่งั้นข้อนี้จะมีคำตอบถูกหลายข้อ (เช่น บางแถวหมุน 90 กับกลับหัวให้ผลเหมือนกัน)
    """
    for _ in range(600):
        row = _rand_row(rng)
        ops = [rng.choice(NAMES) for _ in range(steps)]
        hide = rng.randrange(steps)
        out = tuple(apply_all(row, ops))
        fits = [o for o in NAMES
                if tuple(apply_all(row, ops[:hide] + [o] + ops[hide + 1:])) == out]
        if len(fits) != 1:
            continue
        truth = ops[hide]
        others = [o for o in NAMES if o != truth]
        rng.shuffle(others)
        opts = [truth] + others[:4]
        if len(opts) < 5:
            continue
        opts, _ = _place(opts, truth, want)
        shown = [o for i, o in enumerate(ops) if i != hide]
        used = sorted(set(ops) | set(opts), key=NAMES.index)
        mark = {o: D.OP_MARK[i % len(D.OP_MARK)] for i, o in enumerate(used)}
        return {"row": row, "ops": ops, "hide": hide, "out": list(out),
                "opts": opts, "ansIdx": opts.index(truth), "shown": shown,
                "tag": tag}
    return None


def inverse_q(rng, want=0, steps=2, tag=0):
    """ให้ผลลัพธ์กับลำดับตัวดำเนินการ ถามว่าแถวตั้งต้นคือข้อใด (ชุดที่ 8 ข้อ 10)

    ของจริงถามย้อนทาง ซึ่งยากกว่าถามไปข้างหน้าเพราะต้องถอดตัวดำเนินการกลับทีละขั้น
    ตัวลวงคือแถวที่เดินไปข้างหน้าแล้วได้ผลอื่น จึงผิดจริง ไม่ใช่ผิดแบบเดาได้
    """
    for _ in range(500):
        row = _rand_row(rng)
        ops = [rng.choice(NAMES) for _ in range(steps)]
        if len(set(ops)) < 2:
            continue
        out = tuple(apply_all(row, ops))
        if out == tuple(row):
            continue
        truth = tuple(row)
        seen, opts = {truth}, [truth]
        for _ in range(400):
            alt = _rand_row(rng)
            if rng.random() < .6:              # ตัวลวงใกล้เคียง: เพี้ยนจากคำตอบไปขั้นเดียว
                alt = OPS[rng.choice(NAMES)](list(truth))
            cand = tuple(alt)
            if cand in seen or tuple(apply_all(list(cand), ops)) == out:
                continue                       # ถ้าเดินหน้าแล้วได้ผลเดียวกัน จะมีคำตอบถูกสองข้อ
            seen.add(cand)
            opts.append(cand)
            if len(opts) == 5:
                break
        if len(opts) < 5:
            continue
        opts, _ = _place(opts, truth, want)
        used = sorted(set(ops), key=NAMES.index)
        mark = {o: D.OP_MARK[i] for i, o in enumerate(used)}
        legend = [(mark[o], D.OP_TEXT[o]) for o in used]
        order = " ".join(mark[o] for o in ops)
        return {"row": row, "ops": ops, "out": list(out), "legend": legend,
                "order": order, "opts": [list(o) for o in opts],
                "ansIdx": opts.index(truth), "tag": tag}
    return None


def build(add, P2, rng):
    """เติมโจทย์ตัวดำเนินการสัญลักษณ์รูปเข้าคลัง — เรียกจาก gen.py"""
    want = 0
    for qi in range(4):
        r = chain_q(rng, want=want, steps=2 + qi % 2, tag=qi)
        if not r:
            continue
        leg = D.oplegend(r["legend"], f"sol{qi}")
        start = D.shaperow(r["row"], f"sos{qi}")
        img = D.vstack([leg, start], f"soq{qi}", gap=14)
        files = [D.shaperow(o, f"soo{qi}_{j}") for j, o in enumerate(r["opts"])]
        add(P2, "ตัวดำเนินการสัญลักษณ์รูป",
            "ตารางข้างบนบอกความหมายของตัวดำเนินการแต่ละตัว "
            "และแถวล่างคือรูปตั้งต้น\n"
            f"เมื่อทำตามลำดับ  {r['order']}  จะได้ผลลัพธ์ตรงกับข้อใด",
            [""] * 5, r["ansIdx"], img=img, optimg=D.strip(files, f"soopt{qi}"),
            lvl=2 if len(r["ops"]) == 2 else 3,
            why="ทำทีละขั้นตามลำดับที่โจทย์บอก อย่าสลับลำดับ ผลลัพธ์ต่างกัน")
        want = (want + 2) % 5

    for qi in range(3):
        r = inverse_q(rng, want=want, steps=2 + qi % 2, tag=qi)
        if not r:
            continue
        leg = D.oplegend(r["legend"], f"sil{qi}")
        end = D.shaperow(r["out"], f"sie{qi}")
        img = D.vstack([leg, end], f"siq{qi}", gap=14)
        files = [D.shaperow(o, f"sio{qi}_{j}") for j, o in enumerate(r["opts"])]
        add(P2, "ตัวดำเนินการสัญลักษณ์รูป",
            "ตารางข้างบนบอกความหมายของตัวดำเนินการแต่ละตัว "
            "และแถวล่างคือผลลัพธ์ที่ได้แล้ว" + chr(10) +
            f"เมื่อทำตามลำดับ  {r['order']}  แถวตั้งต้นก่อนทำคือข้อใด",
            [""] * 5, r["ansIdx"], img=img, optimg=D.strip(files, f"siopt{qi}"),
            lvl=3, why="ถอดกลับจากขั้นสุดท้ายไปขั้นแรก หรือลองเดินหน้าทีละตัวเลือก")
        want = (want + 2) % 5

    for qi in range(3):
        r = missing_q(rng, want=want, tag=qi)
        if not r:
            continue
        start = D.shaperow(r["row"], f"sms{qi}")
        end = D.shaperow(r["out"], f"sme{qi}")
        img = D.vstack([start, end], f"smq{qi}", gap=18)
        txt = [D.OP_TEXT[o] for o in r["opts"]]
        seq = []
        for i, o in enumerate(r["ops"]):
            seq.append("?" if i == r["hide"] else D.OP_TEXT[o])
        add(P2, "ตัวดำเนินการสัญลักษณ์รูป",
            "แถวบนคือรูปตั้งต้น แถวล่างคือผลลัพธ์หลังทำครบทุกขั้นตามลำดับนี้\n"
            + "\n".join(f"    ขั้นที่ {i + 1}  {s}" for i, s in enumerate(seq))
            + "\nขั้นที่มีเครื่องหมายคำถามคือข้อใด",
            txt, r["ansIdx"], img=img, lvl=3,
            why="ลองเติมทีละตัวแล้วไล่ทั้งลำดับ มีตัวเดียวที่ได้แถวล่างพอดี")
        want = (want + 2) % 5


if __name__ == "__main__":
    bad, n = [], 0

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    for s in range(400):
        rng = random.Random(s)
        for w in range(5):
            r = chain_q(rng, want=w)
            if r:
                n += 1
                ck(r["ansIdx"] == w, f"chain s={s}: ตำแหน่งเฉลยไม่ตรง")
                got = [tuple(map(tuple, o)) for o in r["opts"]]
                ck(len(set(got)) == 5, f"chain s={s}: ตัวเลือกซ้ำ")
                real = tuple(apply_all(r["row"], r["ops"]))
                ck(tuple(map(tuple, r["opts"][r["ansIdx"]])) == real,
                   f"chain s={s}: เฉลยไม่ตรงกับผลของลำดับจริง")
                ck(sum(1 for o in got if o == real) == 1,
                   f"chain s={s}: มีตัวเลือกถูกมากกว่าหนึ่ง")

            r = inverse_q(rng, want=w)
            if r:
                n += 1
                got = [tuple(map(tuple, o)) for o in r["opts"]]
                ck(len(set(got)) == 5, f"inverse s={s}: ตัวเลือกซ้ำ")
                out = tuple(map(tuple, r["out"]))
                fits = [o for o in got
                        if tuple(apply_all([tuple(x) for x in o], r["ops"])) == out]
                ck(len(fits) == 1, f"inverse s={s}: เดินหน้าแล้วตรง {len(fits)} ข้อ")
                ck(fits and fits[0] == tuple(map(tuple, r["opts"][r["ansIdx"]])),
                   f"inverse s={s}: เฉลยไม่ใช่ข้อที่เดินหน้าแล้วตรง")

            r = missing_q(rng, want=w)
            if r:
                n += 1
                ck(len(set(r["opts"])) == 5, f"missing s={s}: ตัวเลือกซ้ำ")
                out = tuple(map(tuple, r["out"]))
                fits = [o for o in r["opts"]
                        if tuple(apply_all(r["row"],
                                           r["ops"][:r["hide"]] + [o] +
                                           r["ops"][r["hide"] + 1:])) == out]
                ck(len(fits) == 1, f"missing s={s}: เติมได้ {len(fits)} ตัว")
                ck(fits and fits[0] == r["opts"][r["ansIdx"]],
                   f"missing s={s}: เฉลยไม่ใช่ตัวที่เติมแล้วตรง")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:10]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ — ตัวดำเนินการสัญลักษณ์รูป (หาผลลัพธ์ · หาตัวที่หาย · หาตัวตั้ง)")

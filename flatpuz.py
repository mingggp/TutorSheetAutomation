#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""สามแนวหน้าเรียบที่ถอดจากไฟล์ที่ติวเตอร์ส่งมา

  ชุดที่ 8 ข้อ 8   วงกลมแปดส่วน — ให้ตัวอย่างสองแถว **ไม่บอกกฎ** ต้องถอดกฎเอง
                   ลายมือติวเตอร์ไล่กฎไว้ว่า ขาว+ขาว=ดำ · ที่เหลือ=ขาว ซึ่งคือ NOR
  ชุดที่ 8 ข้อ 9   พับกระดาษเจาะรู — พับแล้วเจาะทะลุทุกชั้น คลี่ออกได้รอยกี่รู ตรงไหน
  ชุดที่ 6 ข้อ 26  หารูปไม่เข้าพวก — สี่รูปมีอัตราส่วนจุดทึบต่อจุดโปร่งเท่ากัน อีกรูปไม่เท่า

ทุกข้อพิสูจน์ด้วยโค้ด
  วงกลม     ไล่กฎทุกตัวกับทั้งสองแถวตัวอย่าง ยืนยันว่ามีกฎเดียวที่เข้าได้ทั้งคู่
  เจาะรู     คลี่จริงทีละชั้นด้วยตารางพิกัด ไม่ได้วาดด้วยสายตา
  ไม่เข้าพวก ทุกรูปมีจุดรวมเท่ากันหมด ต่างกันแค่อัตราส่วน จึงมีรูปเดียวที่หลุดกลุ่ม
"""
import random

import draw as D

# ---------------------------------------------------------------- วงกลมแปดส่วน
PIE_OPS = {
    "nor":  (lambda a, b: 1 - (a | b), "โปร่งทั้งคู่จึงได้ทึบ นอกนั้นได้โปร่ง"),
    "xor":  (lambda a, b: a ^ b,       "ต่างกันได้ทึบ เหมือนกันได้โปร่ง"),
    "and":  (lambda a, b: a & b,       "ทึบทั้งคู่จึงได้ทึบ"),
    "or":   (lambda a, b: a | b,       "ทึบอย่างน้อยหนึ่งช่องก็ได้ทึบ"),
    "xnor": (lambda a, b: 1 - (a ^ b), "เหมือนกันได้ทึบ ต่างกันได้โปร่ง"),
}
NSEC = 8


def _rp(rng, p=.5):
    return tuple(1 if rng.random() < p else 0 for _ in range(NSEC))


def _comb(a, b, f):
    return tuple(f(x, y) for x, y in zip(a, b))


def pie_q(rng, want=0, tag=0):
    """สองแถวแรกเป็นตัวอย่างสอนกฎ แถวที่สามถาม — กฎต้องเดาได้ทางเดียวเท่านั้น"""
    for _ in range(500):
        key = rng.choice(list(PIE_OPS))
        f, why = PIE_OPS[key]
        rows = []
        for _ in range(3):
            a, b = _rp(rng), _rp(rng)
            rows.append((a, b, _comb(a, b, f)))
        fits = [k for k in PIE_OPS
                if all(_comb(a, b, PIE_OPS[k][0]) == c for a, b, c in rows[:2])]
        if fits != [key] and set(fits) != {key}:
            continue                    # ตัวอย่างสองแถวยังแยกกฎไม่ออก ทิ้ง
        if len(fits) != 1:
            continue
        a3, b3, truth = rows[2]
        if sum(truth) in (0, NSEC):
            continue                    # ทึบหมดหรือโปร่งหมด เดาได้โดยไม่ต้องใช้กฎ
        opts, seen = [truth], {truth}
        for k2 in PIE_OPS:              # ตัวลวง = ใช้กฎอื่นที่เข้ากับตัวอย่างไม่ได้
            if k2 == key:
                continue
            cand = _comb(a3, b3, PIE_OPS[k2][0])
            if cand not in seen:
                seen.add(cand)
                opts.append(cand)
        for cand in (a3, b3, tuple(1 - v for v in truth)):
            if len(opts) >= 5:
                break
            if cand not in seen:
                seen.add(cand)
                opts.append(cand)
        if len(opts) < 5:
            continue
        opts = opts[:5]
        rest = [o for o in opts if o != truth]
        opts = (rest[:want] + [truth] + rest[want:])[:5]
        return {"rows": rows, "opts": opts, "ansIdx": opts.index(truth),
                "key": key, "why": why, "tag": tag}
    return None


# ---------------------------------------------------------------- พับกระดาษเจาะรู
PW = PH = 4


def _fold(layers, w, h, kind):
    """พับครึ่ง — v = พับขวาทับซ้าย · h = พับล่างทับบน

    layers = ลิสต์ของ dict ที่แปลงพิกัดบนกระดาษที่พับแล้ว กลับไปเป็นพิกัดบนกระดาษเดิม
    พับหนึ่งครั้งชั้นเพิ่มเป็นสองเท่า เจาะทีเดียวจึงทะลุทุกชั้น
    """
    if kind == "v":
        nw = w // 2
        out = []
        for L in layers:
            out.append({(r, c): L[(r, c)] for r in range(h) for c in range(nw)})
            out.append({(r, c): L[(r, w - 1 - c)] for r in range(h) for c in range(nw)})
        return out, nw, h
    nh = h // 2
    out = []
    for L in layers:
        out.append({(r, c): L[(r, c)] for r in range(nh) for c in range(w)})
        out.append({(r, c): L[(h - 1 - r, c)] for r in range(nh) for c in range(w)})
    return out, w, nh


FOLDS = {
    ("v",): "พับครึ่งโดยพับขอบขวาไปทับขอบซ้าย",
    ("h",): "พับครึ่งโดยพับขอบล่างขึ้นไปทับขอบบน",
    ("v", "h"): "พับครึ่งโดยพับขอบขวาไปทับขอบซ้าย แล้วพับขอบล่างขึ้นไปทับขอบบนอีกครั้ง",
    ("h", "v"): "พับครึ่งโดยพับขอบล่างขึ้นไปทับขอบบน แล้วพับขอบขวาไปทับขอบซ้ายอีกครั้ง",
}


def _asgrid(cells):
    return [[1 if (r, c) in cells else 0 for c in range(PW)] for r in range(PH)]


def punch_q(rng, want=0, tag=0):
    """เจาะรูบนกระดาษที่พับแล้ว คลี่ออกได้รอยตรงไหน — คลี่ด้วยการแมปพิกัดจริง"""
    for _ in range(400):
        seq = rng.choice(list(FOLDS))
        layers, w, h = [{(r, c): (r, c) for r in range(PH) for c in range(PW)}], PW, PH
        for k in seq:
            layers, w, h = _fold(layers, w, h, k)
        npunch = rng.choice([2, 2, 3]) if w * h >= 4 else 2
        spots = rng.sample([(r, c) for r in range(h) for c in range(w)], npunch)
        truth = frozenset(L[s] for s in spots for L in layers)
        if len(truth) != npunch * len(layers):
            continue                       # รูซ้อนทับกันเอง นับรูไม่ตรง ทิ้ง
        wrong = [
            frozenset(layers[0][s] for s in spots),                    # ลืมว่าเจาะทะลุทุกชั้น
            frozenset(L[s] for s in spots for L in layers[:2]),        # คลี่แค่รอยพับเดียว
            frozenset((c, r) for (r, c) in truth),                     # สลับแกน
            frozenset((PH - 1 - r, c) for (r, c) in truth),            # พลิกบนล่างทั้งแผ่น
            frozenset((r, PW - 1 - c) for (r, c) in truth),            # พลิกซ้ายขวาทั้งแผ่น
        ]
        opts, seen = [truth], {truth}
        for cand in wrong:
            if cand not in seen and len(cand) > 0 and len(opts) < 5:
                seen.add(cand)
                opts.append(cand)
        guard = 0
        while len(opts) < 5 and guard < 300:
            guard += 1
            alt = rng.sample([(rr, cc) for rr in range(h) for cc in range(w)], npunch)
            cand = frozenset(L[t] for t in alt for L in layers)
            if cand not in seen and len(cand) == len(truth):
                seen.add(cand)
                opts.append(cand)
        if len(opts) < 5:
            continue
        rest = [o for o in opts if o != truth]
        opts = (rest[:want] + [truth] + rest[want:])[:5]
        return {"seq": seq, "text": FOLDS[seq], "spots": spots, "fw": w, "fh": h,
                "nlayer": len(layers), "truth": truth, "opts": opts,
                "ansIdx": opts.index(truth), "tag": tag}
    return None


# ---------------------------------------------------------------- หารูปไม่เข้าพวก
def _ratio(a, b):
    from math import gcd
    g = gcd(a, b) or 1
    return (a // g, b // g)


def odd_q(rng, want=0, tag=0, n=4):
    """ห้าตารางมีจุดรวมเท่ากันหมด ต่างกันแค่สัดส่วนทึบต่อโปร่ง — มีรูปเดียวที่หลุดกลุ่ม

    ที่ให้จุดรวมเท่ากันทุกรูปเพราะไม่อยากให้มี "กฎที่สอง" มาแย่งเป็นคำตอบ
    ถ้าจำนวนจุดไม่เท่ากัน เด็กอาจชี้รูปอื่นว่าไม่เข้าพวกด้วยเหตุผลที่ก็ฟังขึ้น
    """
    for _ in range(300):
        # ติวเตอร์ว่า "ง่ายเกินไปแบบชัดเจนมาก" เพราะสัดส่วนเดิมต่างกันมากจนเห็นด้วยตาเปล่า
        # บังคับให้จุดทึบต่างกันแค่หนึ่งจุด ต้องนับจริงทั้งห้ารูปถึงจะรู้ว่ารูปไหนหลุด
        total = rng.choice([10, 11, 12, 13])
        fa = rng.randrange(3, total - 2)
        fb = fa + rng.choice([-2, -1, 1, 2])
        if not 2 <= fb <= total - 2:
            continue
        if _ratio(fa, total - fa) == _ratio(fb, total - fb):
            continue
        cells = [(r, c) for r in range(n) for c in range(n)]
        if total > len(cells):
            continue
        grids, ok = [], True
        for i in range(5):
            f = fb if i == 0 else fa
            pos = rng.sample(cells, total)
            g = [[0] * n for _ in range(n)]
            for j, (r, c) in enumerate(pos):
                g[r][c] = 1 if j < f else 2
            grids.append(tuple(tuple(row) for row in g))
        if len(set(grids)) < 5:
            continue
        truth = grids[0]
        order = list(range(5))
        rng.shuffle(order)
        grids = [grids[i] for i in order]
        opts = grids
        ansIdx = opts.index(truth)
        rest = [o for o in opts if o != truth]
        opts = (rest[:want] + [truth] + rest[want:])[:5]
        if not ok:
            continue
        return {"opts": opts, "ansIdx": opts.index(truth), "total": total,
                "ratio": _ratio(fa, total - fa), "odd": _ratio(fb, total - fb),
                "tag": tag}
    return None


# ---------------------------------------------------------------- เข้าคลัง
def build(add, P2, rng):
    want = 0
    for qi in range(3):
        r = pie_q(rng, want=want, tag=qi)
        if not r:
            continue
        rowimgs = []
        for k, (a, b, c) in enumerate(r["rows"]):
            cells = [D.pie(a, f"fpa{qi}{k}", r=30), D.pie(b, f"fpb{qi}{k}", r=30)]
            cells.append(D.pie(c, f"fpc{qi}{k}", r=30) if k < 2 else
                         D.pie([0] * NSEC, f"fpq{qi}", r=30, q=True))
            rowimgs.append(D.compose(cells, f"fpr{qi}{k}", seps=["+", "="], gap=14))
        img = D.vstack(rowimgs, f"fpm{qi}", gap=10)
        files = [D.pie(o, f"fpo{qi}_{j}", r=30) for j, o in enumerate(r["opts"])]
        add(P2, "วงกลมแบ่งส่วน · ถอดกฎเอง",
            "สองแถวบนเป็นตัวอย่างที่ทำถูกแล้ว โจทย์ไม่ได้บอกกฎไว้ ต้องถอดกฎจากตัวอย่างเอง\n"
            "วงกลมในช่องเครื่องหมายคำถามคือข้อใด",
            [""] * 5, r["ansIdx"], img=img, optimg=D.strip(files, f"fpopt{qi}"),
            lvl=3, why="กฎคิดทีละส่วนเทียบส่วนต่อส่วน · " + r["why"])
        want = (want + 2) % 5

    for qi in range(3):
        r = punch_q(rng, want=want, tag=qi)
        if not r:
            continue
        fold = [[1 if (rr, cc) in r["spots"] else 0 for cc in range(r["fw"])]
                for rr in range(r["fh"])]
        img = D.dotgrid(fold, f"fdq{qi}", cell=30, lines=False)
        files = [D.dotgrid(_asgrid(o), f"fdo{qi}_{j}", cell=22, lines=False)
                 for j, o in enumerate(r["opts"])]
        add(P2, "พับกระดาษเจาะรู",
            "กระดาษสี่เหลี่ยมจัตุรัสแผ่นหนึ่ง " + r["text"] + "\n"
            "จากนั้นเจาะรูทะลุกระดาษที่พับแล้วตามตำแหน่งในรูป\n"
            "เมื่อคลี่กระดาษออกจนเป็นแผ่นเดิม จะได้รอยเจาะตรงกับข้อใด",
            [""] * 5, r["ansIdx"], img=img, optimg=D.strip(files, f"fdopt{qi}"),
            lvl=3, why=f"พับ {len(r['seq'])} ครั้งได้ {r['nlayer']} ชั้น "
                       f"เจาะ {len(r['spots'])} จุดจึงได้ {len(r['truth'])} รู")
        want = (want + 2) % 5

    for qi in range(2):
        r = odd_q(rng, want=want, tag=qi)
        if not r:
            continue
        files = [D.dotgrid([list(row) for row in o], f"foo{qi}_{j}", cell=20)
                 for j, o in enumerate(r["opts"])]
        add(P2, "หารูปไม่เข้าพวก · อัตราส่วนจุด",
            "ทุกตารางมีจุดรวมเท่ากัน แต่มีตารางหนึ่งที่ไม่เข้าพวกกับอีกสี่ตาราง\n"
            "ตารางในข้อใดไม่เข้าพวก",
            [""] * 5, r["ansIdx"], optimg=D.strip(files, f"fooopt{qi}"),
            lvl=3, why=f"เทียบอัตราส่วนจุดทึบต่อจุดโปร่ง สี่รูปได้ "
                       f"{r['ratio'][0]}:{r['ratio'][1]} อีกรูปไม่ใช่")
        want = (want + 2) % 5


if __name__ == "__main__":
    bad, n = [], 0

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    for s in range(300):
        rng = random.Random(s)
        for w in range(5):
            r = pie_q(rng, want=w)
            if r:
                n += 1
                ck(len(set(r["opts"])) == 5, f"วงกลม s={s}: ตัวเลือกซ้ำ")
                f = PIE_OPS[r["key"]][0]
                for a, b, c in r["rows"]:
                    ck(_comb(a, b, f) == c, f"วงกลม s={s}: แถวไม่ตรงกฎ")
                fits = [k for k in PIE_OPS
                        if all(_comb(a, b, PIE_OPS[k][0]) == c for a, b, c in r["rows"][:2])]
                ck(fits == [r["key"]], f"วงกลม s={s}: ตัวอย่างเข้าได้ {len(fits)} กฎ")
                ck(r["opts"][r["ansIdx"]] == r["rows"][2][2], f"วงกลม s={s}: เฉลยไม่ตรง")

            r = punch_q(rng, want=w)
            if r:
                n += 1
                ck(len(set(r["opts"])) == 5, f"เจาะรู s={s}: ตัวเลือกซ้ำ")
                ck(r["opts"][r["ansIdx"]] == r["truth"], f"เจาะรู s={s}: เฉลยไม่ตรง")
                ck(len(r["truth"]) == len(r["spots"]) * r["nlayer"],
                   f"เจาะรู s={s}: จำนวนรูไม่เท่าจุดเจาะคูณชั้น")
                ck(r["nlayer"] == 2 ** len(r["seq"]),
                   f"เจาะรู s={s}: จำนวนชั้นไม่ตรงกับจำนวนครั้งที่พับ")
                ck(all(0 <= a < PH and 0 <= b < PW for a, b in r["truth"]),
                   f"เจาะรู s={s}: รูหลุดออกนอกกระดาษ")

            r = odd_q(rng, want=w)
            if r:
                n += 1
                ck(len(set(r["opts"])) == 5, f"ไม่เข้าพวก s={s}: ตัวเลือกซ้ำ")
                tot = [sum(1 for row in o for v in row if v) for o in r["opts"]]
                ck(len(set(tot)) == 1, f"ไม่เข้าพวก s={s}: จุดรวมไม่เท่ากันทุกรูป")
                rat = [_ratio(sum(1 for row in o for v in row if v == 1),
                              sum(1 for row in o for v in row if v == 2))
                       for o in r["opts"]]
                odd = [i for i, x in enumerate(rat) if rat.count(x) == 1]
                ck(odd == [r["ansIdx"]],
                   f"ไม่เข้าพวก s={s}: รูปที่หลุดกลุ่มไม่ใช่ข้อที่เฉลย")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:10]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ — วงกลมแบ่งส่วน · พับกระดาษเจาะรู · หารูปไม่เข้าพวก")

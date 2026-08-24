#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""คลังโจทย์ระดับ 3 (ยาก) — ต้องประยุกต์ / มีสองขั้นขึ้นไป / คิดย้อนกลับ"""
import os, random, itertools
SEED = int(os.environ.get("TPAT_SEED", "0"))
import draw as D
import cube as C
import logic as L

def build(add, addnum, P1, P2):
    # เครื่องผลิตโจทย์ตรรกะยาว — บังคับตำแหน่งเฉลยให้กระจายครบ ก-จ
    _lg = random.Random(4200 + SEED * 104729)

    def logic_item(fn, arche, want):
        stem, opts, idx = fn(_lg, want=want)
        add(P1, arche, stem, opts, idx)

    # ============================== พาร์ทที่ 1 (15) ==============================
    addnum(P1, "ลำดับ", "2, 3, 10, 15, 26, ?", 35, 4)
    addnum(P1, "ลำดับ", "1, 3, 12, 60, 360, ?", 2520, 300)
    addnum(P1, "ลำดับ",
           "ลำดับเลขคณิตลำดับหนึ่งมีพจน์ที่ 5 เท่ากับ 23 และผลบวก 10 พจน์แรกเท่ากับ 255 พจน์แรกของลำดับนี้มีค่าเท่าใด", 3, 1)
    add(P1, "ปริศนาตัวอักษร",
        "ถ้า MOUSE เขียนเป็นรหัสว่า NPVTF แล้ว KEYBOARD จะเขียนเป็นรหัสว่าอย่างไร",
        ["JDXAMZQC", "LFZCPBSE", "LFZBPBSE", "LEZCPBSE", "KFZCPBSE"], 1)
    add(P1, "เมทริกซ์ตัวเลข", "จากตาราง ตัวเลขในช่อง ? คือข้อใด (ทุกแถวใช้กฎเดียวกัน)",
        ["30", "32", "35", "36", "40"], 3,
        img=D.numgrid([[3, 5, 16], [4, 6, 25], [5, 7, "?"]], "hmx1"))
    addnum(P1, "โจทย์ปัญหาคณิต",
           "จำนวนเต็มบวกสามหลักที่หารด้วย 7 ลงตัว และมีเลขโดดหลักหน่วยเป็น 0 มีทั้งหมดกี่จำนวน", 13, 2)
    logic_item(L.seating, "ตรรกะจัดลำดับ", 4)
    logic_item(L.liars, "ตรรกะจริง-เท็จ", 0)
    add(P1, "มุมเข็มนาฬิกา",
        "หลังเวลา 4 นาฬิกา เข็มสั้นกับเข็มยาวจะทับกันสนิทครั้งแรกเมื่อเวลาผ่านไปกี่นาที",
        ["20 นาที", "21 3/11 นาที", "21 9/11 นาที", "22 2/11 นาที", "23 1/11 นาที"], 2)
    logic_item(L.seating, "ตรรกะจัดลำดับ", 1)
    addnum(P1, "เชาวน์ปัญญา",
           "นาฬิกาเรือนหนึ่งเดินช้ากว่าความเป็นจริงวันละ 3 นาทีอย่างสม่ำเสมอ ถ้าตั้งเวลาให้ตรงในตอนเริ่มต้น อีกกี่วันหน้าปัดจึงจะแสดงเวลาตรงกับเวลาจริงอีกครั้ง",
           240, 30)
    logic_item(L.liars, "ตรรกะจริง-เท็จ", 3)
    addnum(P1, "ปริศนาเรขาคณิต",
           "สี่เหลี่ยมจัตุรัสด้านยาว 10 เซนติเมตร ถูกตัดมุมออกทั้งสี่มุม แต่ละมุมเป็นสามเหลี่ยมมุมฉากที่มีด้านประกอบมุมฉากยาว 3 เซนติเมตร รูปที่เหลือมีพื้นที่กี่ตารางเซนติเมตร",
           82, 6)
    addnum(P1, "หน่วยและการประมาณค่า",
           "ปั๊มน้ำสูบน้ำได้ 15 ลิตรต่อนาที ต้องใช้เวลากี่ชั่วโมงจึงจะสูบน้ำเต็มถังขนาด 5.4 ลูกบาศก์เมตร", 6, 1)
    addnum(P1, "unseen",
           "แบคทีเรียชนิดหนึ่งแบ่งตัวเพิ่มเป็นสองเท่าทุก 20 นาที ถ้าเริ่มจาก 1 ตัว เมื่อเวลาผ่านไป 4 ชั่วโมงจะมีแบคทีเรียกี่ตัว",
           4096, 500)

    # ============================== พาร์ทที่ 2 (12) ==============================
    D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

    def unpainted(vox):
        vs = set(vox); n = 0
        for (x, y, z) in vs:
            hidden = True
            for d in D6:
                nb = (x+d[0], y+d[1], z+d[2])
                if nb in vs: continue
                if d == (0,0,-1) and z == 0: continue      # ด้านที่ติดพื้น ไม่ถูกทาสี
                hidden = False; break
            if hidden: n += 1
        return n

    # (1)(2) ทาสีเฉพาะผิวที่สัมผัสอากาศ
    for qi, hm in enumerate([[[3]*4 for _ in range(4)], [[4,4,4],[4,3,4],[4,4,4]]], 1):
        vox = D.hm_vox(hm)
        addnum(P2, "Block Counting",
               "นำกองลูกบาศก์นี้ไปทาสีทุกผิวที่สัมผัสอากาศ (ไม่ทาด้านที่ติดพื้น) จะมีลูกบาศก์หน่วยกี่ก้อนที่ไม่โดนสีเลย",
               unpainted(vox), 2, img=D.iso(vox, f"hp{qi}", cell=22, ch=19))

    # (3)(4) ภาพฉาย -> จำนวนก้อนมากที่สุด
    def cols_of(hm, kind):
        ny, nx = len(hm), len(hm[0])
        if kind == "front": return [max(hm[y][x] for y in range(ny)) for x in range(nx)]
        return [max(hm[y][x] for x in range(nx)) for y in range(ny)]
    def cells_of(cols, mh): return {(mh-1-h, c) for c, v in enumerate(cols) for h in range(v)}
    def top_cells(hm): return {(r,c) for r in range(len(hm)) for c in range(len(hm[0])) if hm[r][c] > 0}

    for qi, hm in enumerate([[[3,1,2],[2,1,1]], [[2,3,1],[1,2,1],[1,1,1]]], 1):
        fr, sd = cols_of(hm, "front"), cols_of(hm, "side")
        mh = max(max(fr), max(sd))
        mx = sum(min(fr[c], sd[r]) for (r, c) in top_cells(hm))
        fv = D.grid(mh, len(hm[0]), filled=cells_of(fr, mh), name=f"hv{qi}f", cell=28)
        sv = D.grid(mh, len(hm), filled=cells_of(sd, mh), name=f"hv{qi}s", cell=28)
        tv = D.grid(len(hm), len(hm[0]), filled=top_cells(hm), name=f"hv{qi}t", cell=28)
        stem = D.compose([fv, sv, tv], f"hv{qi}stem", seps=["", ""], gap=30,
                         capt=["ด้านหน้า", "ด้านข้าง", "ด้านบน"])
        addnum(P2, "ภาพฉาย",
               "ทรงที่ให้ภาพฉายทั้งสามด้านตรงตามภาพนี้ ประกอบด้วยลูกบาศก์หน่วยได้มากที่สุดกี่ก้อน",
               mx, 1, img=stem)

    # (5)(6) หมุนทรง 6 ก้อน
    BIG = [[(0,0,0),(1,0,0),(2,0,0),(2,1,0),(2,1,1),(0,0,1)],
           [(0,0,0),(0,1,0),(1,1,0),(2,1,0),(2,1,1),(2,0,1)]]
    for qi, sh in enumerate(BIG, 1):
        rng = random.Random(2000 + qi + SEED * 104729)
        R0 = C.all_rots(sh)
        Rc = C.ROTS[rng.randrange(1, 24)]
        correct = C.place([Rc(p) for p in sh])
        while C.norm(correct) == C.norm(sh):
            Rc = C.ROTS[rng.randrange(1, 24)]
            correct = C.place([Rc(p) for p in sh])
        pool = [[(-x, y, z) for (x, y, z) in sh]] + C.neighbours(sh)
        rng.shuffle(pool)
        picked, classes = [], [R0]
        for cand in pool:
            cr = C.all_rots(C.place(cand))
            if any(cr & c for c in classes): continue
            classes.append(cr); picked.append(C.place(cand))
            if len(picked) == 4: break
        assert len(picked) == 4
        def spin(c, rng=rng):
            R = C.ROTS[rng.randrange(24)]
            return C.place([R(p) for p in c])
        cands = [correct] + [spin(c) for c in picked]
        assert [j for j, c in enumerate(cands) if C.all_rots(c) & R0] == [0]
        order = list(range(5)); rng.shuffle(order)
        files = [D.iso(cands[o], f"hrt{qi}o{j}", cell=20, ch=17) for j, o in enumerate(order)]
        add(P2, "แผนภาพแบบหมุน", "ทรงในข้อใดคือทรงเดียวกับภาพข้างบน เพียงแต่ถูกหมุนไปเท่านั้น",
            [""]*5, order.index(0), img=D.iso(sh, f"hrt{qi}stem", cell=24, ch=20),
            optimg=D.strip(files, f"hrt{qi}opt"))

    # ---------- รูปคลี่รูปทรงอิสระ ----------
    def hexominoes(seed, want, valid=True):
        rng = random.Random(seed); out = []
        tries = 0
        while len(out) < want and tries < 20000:
            tries += 1
            cells = {(0, 0)}
            while len(cells) < 6:
                r, c = rng.choice(sorted(cells))
                cells.add(rng.choice([(r+1,c),(r-1,c),(r,c+1),(r,c-1)]))
            rs = min(r for r,_ in cells); cs = min(c for _,c in cells)
            cells = frozenset((r-rs, c-cs) for r, c in cells)
            if (C.is_net(cells) != valid): continue
            if cells in out: continue
            if cells == frozenset({(0,1),(1,0),(1,1),(1,2),(2,1),(3,1)}): continue
            out.append(cells)
        return out

    LETT = ["A", "B", "C", "D", "E", "F"]
    # (7)(8) รูปคลี่อิสระ -> ลูกบาศก์
    shapes = hexominoes(3001 + SEED * 104729, 2)
    for qi, cells in enumerate(shapes, 1):
        rng = random.Random(3100 + qi + SEED * 104729)
        cl = sorted(cells)
        labels = {c: LETT[i] for i, c in enumerate(cl)}
        dirs = C.label_dirs(cells, labels)
        good = sorted(C.triples(dirs))
        correct = rng.choice(good)
        bad = [t for t in itertools.permutations(LETT, 3) if t not in set(good)]
        rng.shuffle(bad)
        picked, seen = [], {frozenset(correct)}
        for t in bad:
            if frozenset(t) in seen: continue
            seen.add(frozenset(t)); picked.append(t)
            if len(picked) == 4: break
        cands = [correct] + picked
        order = list(range(5)); rng.shuffle(order)
        files = [D.iso([(0,0,0)], f"hn{qi}o{j}", cell=32, ch=27, labels=cands[o]) for j, o in enumerate(order)]
        add(P2, "พับกล่อง / รูปคลี่", "เมื่อพับรูปคลี่นี้ขึ้นเป็นลูกบาศก์ จะได้ลูกบาศก์ตรงกับข้อใด",
            [""]*5, order.index(0),
            img=D.netshape(cells, labels, f"hn{qi}stem", cell=34),
            optimg=D.strip(files, f"hn{qi}opt"))

    # (9) รูปคลี่ใดพับไม่ได้
    rng = random.Random(3200 + SEED * 104729)
    ok4 = hexominoes(3201 + SEED * 104729, 4, valid=True)
    bad1 = hexominoes(3202 + SEED * 104729, 1, valid=False)[0]
    cands = [bad1] + ok4
    order = list(range(5)); rng.shuffle(order)
    files = [D.netshape(cands[o], {}, f"hnb o{j}".replace(" ", ""), cell=20) for j, o in enumerate(order)]
    add(P2, "พับกล่อง / รูปคลี่", "รูปคลี่ในข้อใดพับขึ้นเป็นลูกบาศก์ไม่ได้", [""]*5,
        order.index(0), optimg=D.strip(files, "hnbopt", gap=22))

    # (10) รูปคลี่ใดที่ A อยู่ตรงข้าม D
    rng = random.Random(3300 + SEED * 104729)
    pool = hexominoes(3301 + SEED * 104729, 40, valid=True)
    hit, miss = [], []
    for cells in pool:
        cl = sorted(cells)
        labels = {c: LETT[i] for i, c in enumerate(cl)}
        dirs = C.label_dirs(cells, labels)
        (hit if C.opposite(dirs, "A") == "D" else miss).append((cells, labels))
    assert hit and len(miss) >= 4
    cands = [hit[0]] + miss[:4]
    order = list(range(5)); rng.shuffle(order)
    files = [D.netshape(cands[o][0], cands[o][1], f"hno{j}", cell=20) for j, o in enumerate(order)]
    add(P2, "พับกล่อง / รูปคลี่", "รูปคลี่ในข้อใดเมื่อพับเป็นลูกบาศก์แล้ว หน้า A จะอยู่ตรงข้ามกับหน้า D",
        [""]*5, order.index(0), optimg=D.strip(files, "hnoopt", gap=22))

    # (11) พับกระดาษสองครั้ง เจาะสามรู
    rng = random.Random(3400 + SEED * 104729)
    N = 4; punch = [(0, 1), (1, 0), (1, 1)]
    correct = set()
    for (r, c) in punch:
        pts = {(r, c)}
        pts |= {(rr, N-1-cc) for (rr, cc) in pts}
        pts |= {(N-1-rr, cc) for (rr, cc) in pts}
        correct |= pts
    stem = D.grid(N//2, N//2, holes=set(punch), name="hpf1stem", cell=28)
    allc = {(r, c) for r in range(N) for c in range(N)}
    vs = [correct]
    while len(vs) < 5:
        cand = set(correct); used = sorted(cand); free = sorted(allc - cand)
        op = rng.choice(["mv", "add", "del"])
        if op == "mv" and used and free: cand.discard(rng.choice(used)); cand.add(rng.choice(free))
        elif op == "add" and free: cand.add(rng.choice(free))
        elif len(used) > 3: cand.discard(rng.choice(used))
        if cand not in vs: vs.append(cand)
    order = list(range(5)); rng.shuffle(order)
    files = [D.grid(N, N, holes=vs[o], name=f"hpf1o{j}", cell=24) for j, o in enumerate(order)]
    add(P2, "พับกระดาษ",
        "นำกระดาษสี่เหลี่ยมจัตุรัสมาพับฝั่งขวาไปทับฝั่งซ้าย แล้วพับครึ่งล่างขึ้นทับครึ่งบน จากนั้นเจาะรูตามภาพ เมื่อคลี่กระดาษออกจนสุดจะได้รูปแบบใด",
        [""]*5, order.index(0), img=stem, optimg=D.strip(files, "hpf1opt"))

    # (12) ลูกเต๋าไทย — ข้อความใดถูกต้อง
    cross = {(0,1),(1,0),(1,1),(1,2),(2,1),(3,1)}
    labels = dict(zip(sorted(cross), ["ก","ข","ค","ง","จ","ฉ"]))
    dirs = C.label_dirs(cross, labels)
    letters = sorted(labels.values())
    good = sorted(C.triples(dirs))
    rng = random.Random(3500 + SEED * 104729)

    def matchings(items):
        if not items: yield []
        else:
            a = items[0]
            for i in range(1, len(items)):
                for rest in matchings(items[1:i] + items[i+1:]):
                    yield [(a, items[i])] + rest

    chosen = None
    for _ in range(800):
        vs3 = rng.sample(good, 3)
        ok = [m for m in matchings(letters)
              if all(not any(x in v and y in v for v in vs3) for (x, y) in m)]
        if len(ok) == 1: chosen = vs3; break
    assert chosen
    files = [D.iso([(0,0,0)], f"hdc{j}", cell=32, ch=27, labels=v) for j, v in enumerate(chosen)]
    stem = D.compose(files, "hdcstem", seps=["", ""], gap=30,
                     capt=["ภาพที่ 1", "ภาพที่ 2", "ภาพที่ 3"])
    true_pair = (letters[0], C.opposite(dirs, letters[0]))
    false_pairs = [(x, y) for x in letters for y in letters
                   if x < y and C.opposite(dirs, x) != y]
    rng.shuffle(false_pairs)
    opts = [f"หน้า {true_pair[0]} อยู่ตรงข้ามกับหน้า {true_pair[1]}"] + \
           [f"หน้า {a} อยู่ตรงข้ามกับหน้า {b}" for a, b in false_pairs[:4]]
    order = list(range(5)); rng.shuffle(order)
    add(P2, "ลูกเต๋าหมุน", "ภาพทั้งสามคือลูกเต๋าลูกเดียวกันที่ถูกหมุนไป ข้อความในข้อใดถูกต้อง",
        [opts[o] for o in order], order.index(0), img=stem)

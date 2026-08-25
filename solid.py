#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์ทรงสามมิติของ TGAT2 — แบบหมุนภาพสามมิติ และ แบบหาภาพต่าง

สองแนวนี้รวมกัน 10 จาก 60 ข้อของ TGAT2 ในขอบเขตที่ติวเตอร์สอน
(`reference/tgat2/DIGEST.md` — ท่อนมิติสัมพันธ์ แนวย่อยที่ 2 และ 3)

ต่อยอดจาก `cube.py` ทั้งหมด ไม่ได้เขียนกลไกหมุนใหม่:
    ROTS       24 ฟังก์ชันหมุน
    norm()     ย้ายทรงมาชิดมุมแล้วคืนเป็น frozenset — ใช้เทียบว่าทรงเดียวกันไหม
    all_rots() เซตของทุกมุมหมุนในรูปมาตรฐาน
    neighbours() ทรงที่ขยับก้อนเดียวแล้วยังต่อกันเป็นชิ้นเดียว

**คำตัดสินของติวเตอร์ (24 ส.ค. 69)** — "แบบหาภาพต่าง" ถามว่า **ข้อใดไม่ใช่ทรงเดียวกับรูปอ้างอิง**
ตัวเลือก 4 ข้อเป็นทรงเดียวกันที่ถูกหมุนไป มีข้อเดียวที่ต่างออกไป
ข้อสอบจริงไม่พิมพ์คำสั่งกำกับไว้ อาศัยหัวข้อท่อน — ของเราต้องเขียนคำสั่งให้ชัดทุกข้อ
"""
import cube as C

ROT_STEM = ("ทางซ้ายของเส้นแบ่ง ทรงแรกถูกหมุนไปอยู่ในท่าของทรงที่สอง\n"
            "ถ้าหมุนทรงทางขวาของเส้นแบ่งด้วยวิธีเดียวกัน จะได้ทรงในข้อใด")

ODD_STEM = ("รูปด้านบนคือทรงสามมิติที่กำหนดให้\n"
            "ข้อใด**ไม่ใช่**ทรงเดียวกันกับรูปที่กำหนดให้")


# ============================================================
#  สร้างและเทียบทรง
# ============================================================

D6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def same(a, b):
    """b เป็นทรงเดียวกับ a ที่ถูกหมุนไปหรือเปล่า — เทียบครบทั้ง 24 มุมหมุน"""
    return C.norm(b) in C.all_rots(a)


def no_hidden(vox):
    """ทุกก้อนต้องมองเห็นได้ในภาพไอโซเมตริก

    ก้อนที่มีเพื่อนบ้านครบทั้งทิศ +x +y +z จะถูกบังสนิท วาดออกมาแล้วหายไปเลย
    (ทดลองยืนยันแล้วกับทรง 2x2x2: เอาก้อน (0,0,0) ออก ภาพไม่เปลี่ยนแม้แต่ไบต์เดียว)

    ถ้าปล่อยผ่าน ทรงสองอันที่ต่างกันเฉพาะก้อนที่ถูกบัง จะวาดออกมาเหมือนกันเป๊ะ
    ผู้สอบจะหาคำตอบไม่เจอ เพราะสิ่งที่ต่างกันมองไม่เห็น
    """
    vs = set(map(tuple, vox))
    for (x, y, z) in vs:
        if {(x + 1, y, z), (x, y + 1, z), (x, y, z + 1)} <= vs:
            return False
    return True


def rand_solid(rng, n=6, tries=300, full=False):
    """สุ่มทรงต่อกัน n ก้อน ที่ไม่สมมาตรจนเกินไป

    ทรงที่สมมาตรมาก (เช่น แท่งตรง) พอหมุนแล้วได้ภาพเดิม โจทย์จะดูเหมือนมีตัวเลือกซ้ำ
    เลยบังคับว่าต้องมีมุมหมุนที่ให้ผลต่างกันอย่างน้อย 20 จาก 24 แบบ
    และต้องกินพื้นที่ทั้งสามแกน ไม่ใช่แบนอยู่ระนาบเดียว
    """
    for _ in range(tries):
        vox = {(0, 0, 0)}
        while len(vox) < n:
            base = rng.choice(sorted(vox))
            d = rng.choice(D6)
            vox.add((base[0] + d[0], base[1] + d[1], base[2] + d[2]))
        v = C.place(sorted(vox))
        span = [max(p[i] for p in v) - min(p[i] for p in v) for i in range(3)]
        if min(span) < 1:                       # แบนอยู่ระนาบเดียว มองยาก
            continue
        nrot = len(C.all_rots(v))
        if nrot < 20 or (full and nrot != 24):  # สมมาตรเกินไป
            continue
        if not no_hidden(v):                    # มีก้อนที่วาดออกมาแล้วมองไม่เห็น
            continue
        return v
    raise RuntimeError("สุ่มทรงไม่สำเร็จ")


def rotations_of(vox, k, rng, exclude=()):
    """คืน k ท่าหมุนของทรงเดิม ที่หน้าตาไม่ซ้ำกัน (เว้นท่าที่อยู่ใน exclude)"""
    seen, out = set(exclude), []
    order = list(range(24))
    rng.shuffle(order)
    for i in order:
        r = C.place([C.ROTS[i](p) for p in vox])
        key = C.norm(r)
        if key in seen or not no_hidden(r):
            continue
        seen.add(key)
        out.append(r)
        if len(out) == k:
            return out
    return None


def different_from(vox, k, rng, pool_size=60):
    """คืน k ทรงที่ **ต่างจริง** จาก vox และต่างกันเองด้วย

    ใช้ neighbours() ขยับก้อนเดียว แล้วกรองทิ้งทุกตัวที่บังเอิญเป็นมุมหมุนของทรงเดิม
    — ขั้นกรองนี้คือหัวใจ ถ้าไม่กรอง โจทย์จะมีคำตอบถูกมากกว่าหนึ่งข้อ
    """
    base_rots = C.all_rots(vox)
    out, seen = [], set()
    cand = C.neighbours(vox)
    rng.shuffle(cand)
    for c in cand[:pool_size]:
        v = C.place(c)
        key = C.norm(v)
        if key in base_rots:                    # เป็นทรงเดิมที่หมุนไป ไม่ใช่ทรงต่าง
            continue
        if any(key in C.all_rots(o) for o in out):   # ซ้ำกับตัวลวงที่เลือกไปแล้ว
            continue
        if len(C.all_rots(v)) < 20 or not no_hidden(v):
            continue
        seen.add(key)
        out.append(v)
        if len(out) == k:
            return out
    return None


def _place5(opts, ans_i, want):
    """ย้ายตัวเลือกที่ตำแหน่ง ans_i ไปอยู่ตำแหน่ง want"""
    ans = opts[ans_i]
    rest = [o for j, o in enumerate(opts) if j != ans_i]
    return rest[:want] + [ans] + rest[want:], want


# ============================================================
#  แนวที่ 1 — แบบหมุนภาพสามมิติ : A→B สอนมุมหมุน แล้ว C→? ให้ใช้มุมเดียวกัน
#
#  รูปแบบนี้ถอดมาจากข้อสอบจริง (TGAT2 Dek66 หน้า 17 ข้อ 51-52 · TGATV68 หน้า 58-62)
#  **ไม่ใช่** "ข้อใดคือทรงเดียวกัน" — ข้อสอบจริงไม่มีแนวหาภาพเหมือน มีแต่หาภาพต่าง
#
#  เงื่อนไขที่ขาดไม่ได้: ทรง A ต้องไม่สมมาตรเลย (มุมหมุนต่างกันครบ 24 แบบ)
#  ถ้า A สมมาตร จะมีมุมหมุนหลายมุมที่พา A ไป B ได้ แปลว่าถอดกฎได้หลายแบบ
#  แล้วโจทย์จะมีคำตอบถูกมากกว่าหนึ่งข้อทันที
# ============================================================

def rotpair(rng, want=0, n=6):
    """คืน (A, B, Cc, opts, ansIdx) — ตัวเลือกคือทรง Cc ในท่าต่าง ๆ มีท่าเดียวที่ถูก"""
    for _ in range(400):
        A = rand_solid(rng, n, full=True)
        ri = rng.randrange(24)
        B = C.place([C.ROTS[ri](p) for p in A])
        if C.norm(B) == C.norm(A) or not no_hidden(B):
            continue                       # ไม่ได้หมุนจริง หรือมีก้อนถูกบัง

        # ต้องมีมุมหมุน *เดียว* ที่พา A ไป B ได้ ไม่งั้นถอดกฎได้หลายแบบ
        hits = [i for i in range(24)
                if C.norm([C.ROTS[i](p) for p in A]) == C.norm(B)]
        if len(hits) != 1:
            continue

        Cc = rand_solid(rng, n, full=True)
        if same(A, Cc):                    # ให้ต่างจาก A จะได้ไม่ใช่โจทย์เดิมซ้ำ
            continue
        ans = C.place([C.ROTS[ri](p) for p in Cc])
        if not no_hidden(ans):
            continue

        wrong = rotations_of(Cc, 4, rng, exclude={C.norm(ans)})
        if not wrong:
            continue
        opts, idx = _place5([ans] + wrong, 0, want)
        if sum(1 for o in opts if C.norm(o) == C.norm(ans)) != 1:
            continue
        return A, B, Cc, opts, idx
    raise RuntimeError("สร้างโจทย์หมุนภาพสามมิติไม่สำเร็จ")


# ============================================================
#  แนวที่ 2 — แบบหาภาพต่าง : มีทรงคนละอันซ่อนอยู่ 1 ข้อ
# ============================================================

def oddone(rng, want=0, n=6):
    """คืน (base, opts, ansIdx) — ตัวเลือกเดียวที่ **ไม่ใช่** ทรงเดิม ที่เหลือเป็นทรงเดิมหมุนไป"""
    for _ in range(200):
        base = rand_solid(rng, n)
        rots = rotations_of(base, 4, rng)
        if not rots:
            continue
        odd = different_from(base, 1, rng)
        if not odd:
            continue
        opts, idx = _place5([odd[0]] + rots, 0, want)
        if sum(1 for o in opts if not same(base, o)) != 1:
            continue
        return base, opts, idx
    raise RuntimeError("สร้างโจทย์หาภาพต่างไม่สำเร็จ")


# ============================================================
#  ต่อเข้าเครื่องวาด
# ============================================================

TG_LABELS = ["1)", "2)", "3)", "4)", "5)"]


def _opts_img(opts, tag, labels=TG_LABELS):
    """วาดแถบตัวเลือก และตีตกถ้าภาพซ้ำกันเป๊ะ

    ทรงคนละท่าอาจฉายเป็นภาพไอโซเมตริกที่เหมือนกันได้ ถ้าปล่อยผ่านจะได้โจทย์
    ที่ดูเหมือนมีตัวเลือกซ้ำ หรือแย่กว่านั้นคือมีคำตอบถูกสองข้อในสายตาผู้สอบ
    เทียบไฟล์ภาพทีละไบต์เป็นด่านสุดท้าย
    """
    import os
    import draw as D
    files = [D.iso(o, f"{tag}o{i}", cell=22, ch=19) for i, o in enumerate(opts)]
    blobs = [open(os.path.join(D.IMG, f), "rb").read() for f in files]
    if len(set(blobs)) != len(blobs):
        return None
    return D.strip(files, tag + "opt", labels=labels)


def _render_odd(base, opts, tag):
    """หาภาพต่าง: ทรงอ้างอิงหนึ่งรูปด้านบน"""
    import draw as D
    o = _opts_img(opts, tag)
    return (D.iso(base, tag + "s", cell=27, ch=23), o) if o else None


def _render_pair(A, B, Cc, opts, tag):
    """หมุนภาพสามมิติ: A → B │ C → ?  ต่อกันเป็นแถวเดียวตามข้อสอบจริง

    ลูกศรกับเส้นแบ่งวาดเป็นรูป ไม่ใช้ตัวอักษร เพราะฟอนต์ Sarabun ไม่มีอักขระพวกนั้น
    ใส่เป็นข้อความแล้วจะขึ้นเป็นกล่องว่างในชีท
    """
    import draw as D
    a = D.iso(A, tag + "a", cell=23, ch=19)
    b = D.iso(B, tag + "b", cell=23, ch=19)
    c = D.iso(Cc, tag + "c", cell=23, ch=19)
    q = D.grid(1, 1, name=tag + "q", cell=48, pad=6, center="?")
    ar1 = D.arrow(tag + "r1"); ar2 = D.arrow(tag + "r2")
    dv = D.divider(tag + "dv")
    stem = D.compose([a, ar1, b, dv, c, ar2, q], tag + "s", gap=11)
    o = _opts_img(opts, tag)
    return (stem, o) if o else None


def build(add, part, rng, n_rot=5, n_odd=5, lvl=2):
    """เติมโจทย์สองแนวนี้เข้าคลัง — เฉลยไล่ครบทั้ง 5 ช่อง"""
    made = 0
    for i in range(n_rot):
        for _ in range(30):
            A, B, Cc, opts, idx = rotpair(rng, want=i % 5)
            r = _render_pair(A, B, Cc, opts, f"tgrot{i}")
            if r:
                add(part, "แบบหมุนภาพสามมิติ", ROT_STEM, [""] * 5, idx,
                    img=r[0], optimg=r[1], lvl=lvl)
                made += 1
                break
    for i in range(n_odd):
        for _ in range(30):
            base, opts, idx = oddone(rng, want=(i + 2) % 5)
            r = _render_odd(base, opts, f"tgodd{i}")
            if r:
                add(part, "แบบหาภาพต่าง", ODD_STEM, [""] * 5, idx,
                    img=r[0], optimg=r[1], lvl=lvl)
                made += 1
                break
    return made


# ============================================================
#  ตัวตรวจ — python solid.py
# ============================================================

if __name__ == "__main__":
    import random, sys

    bad = []
    for s in range(120):
        rng = random.Random(s)
        want = s % 5

        A, B, Cc, opts, idx = rotpair(rng, want=want)
        if idx != want:
            bad.append(f"rotpair s={s}: บังคับตำแหน่งเฉลยไม่ได้")
        # มุมหมุนที่พา A ไป B ต้องมีเดียว ไม่งั้นถอดกฎได้หลายแบบ
        hits = [i for i in range(24) if C.norm([C.ROTS[i](p) for p in A]) == C.norm(B)]
        if len(hits) != 1:
            bad.append(f"rotpair s={s}: มีมุมหมุนที่พา A ไป B ได้ {len(hits)} แบบ")
        else:
            want_ans = C.place([C.ROTS[hits[0]](p) for p in Cc])
            if C.norm(opts[idx]) != C.norm(want_ans):
                bad.append(f"rotpair s={s}: เฉลยไม่ตรงกับมุมหมุนที่ถอดได้จาก A→B")
        if len({C.norm(o) for o in opts}) != 5:
            bad.append(f"rotpair s={s}: ตัวเลือกซ้ำกัน")
        if not all(same(Cc, o) for o in opts):
            bad.append(f"rotpair s={s}: ตัวเลือกบางข้อไม่ใช่ทรง C")
        if not all(no_hidden(o) for o in opts + [A, B, Cc]):
            bad.append(f"rotpair s={s}: มีก้อนที่ถูกบังจนมองไม่เห็น")

        base, opts, idx = oddone(rng, want=want)
        if idx != want:
            bad.append(f"oddone s={s}: บังคับตำแหน่งเฉลยไม่ได้")
        if same(base, opts[idx]):
            bad.append(f"oddone s={s}: เฉลยดันเป็นทรงเดียวกับรูปอ้างอิง")
        if sum(1 for o in opts if not same(base, o)) != 1:
            bad.append(f"oddone s={s}: มีทรงที่ต่างมากกว่าหนึ่งข้อ")
        for j, o in enumerate(opts):
            if j != idx and not same(base, o):
                bad.append(f"oddone s={s}: ตัวเลือก {j+1} ควรเป็นทรงเดิมแต่ไม่ใช่")

    # ตรวจ same() ด้วยกรณีที่รู้คำตอบแน่ๆ
    L = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0)]          # ทรงตัว L
    L_rot = C.place([C.ROTS[5](p) for p in L])
    if not same(L, L_rot):
        bad.append("same(): ทรงเดิมที่หมุนแล้วควรถือว่าเหมือนกัน")
    L_diff = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0)]     # ทรงตัว T
    if same(L, L_diff):
        bad.append("same(): ทรง L กับ T ไม่ควรถือว่าเหมือนกัน")

    print(f"ตรวจแล้ว 240 ข้อ + same() 2 กรณี")
    if bad:
        for m in bad[:10]:
            print("[พัง]", m)
        print(f"พบปัญหา {len(bad)} จุด")
        sys.exit(1)
    print("ผ่านทั้งหมด")

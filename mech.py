#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์ท่อนเชิงกล (วีคฟิสิกส์) — ข้อ 31-45 ของข้อสอบจริง

แนวที่เลือกมาทำก่อน มาจาก `reference/tpat3/DIGEST-part3.md` สามแนวที่ของจริงถามบ่อย
และเป็นแนวที่พิสูจน์คำตอบด้วยโค้ดได้เป๊ะ ไม่ต้องอาศัยความมั่นใจ (กติกาข้อ 1)

  ระบบรอก      แรงที่ต้องออก = น้ำหนัก หารด้วยจำนวนเส้นเชือกที่รับน้ำหนัก
  ชุดเฟือง     ทิศสลับกันทีละตัว · อัตราเร็วขึ้นกับเฟืองต้นกับเฟืองปลายเท่านั้น
  คานสมดุล     ผลรวมโมเมนต์สองฝั่งเท่ากัน

รันไฟล์นี้ตรง ๆ = ตรวจตัวเองว่าทุกโจทย์ที่ผลิตได้มีคำตอบถูกข้อเดียวจริง
"""
from fractions import Fraction as F
import random

import draw as D

CH = "กขคงจ"


def _place(opts, truth, want):
    """ดันคำตอบถูกไปอยู่ตำแหน่งที่สั่ง เพื่อให้เฉลยกระจายครบ ก-จ (กติกาข้อ 4)"""
    rest = [o for o in opts if o != truth]
    out = rest[:want] + [truth] + rest[want:]
    return out[:5], want


# ---------------------------------------------------------------- ระบบรอก
# เลือกคู่ (จำนวนเส้นเชือก, น้ำหนัก) ที่หารด้วย n-1 n n+1 ลงตัว
# ตัวลวงจะได้เป็นจำนวนเต็มสวย ๆ เหมือนคำตอบ เด็กจึงตัดตัวเลือกด้วยรูปร่างเลขไม่ได้
PULLEY_SETS = [(2, 120), (3, 120), (4, 120), (5, 120), (6, 120),
               (2, 60), (3, 60), (4, 60), (2, 240), (4, 240), (6, 240)]


def pulley_q(rng, want=0):
    n, W = rng.choice(PULLEY_SETS)
    truth = W // n
    cand = [W // n, W // (n - 1), W // (n + 1), W // 2, W, W * 2 // n if n > 2 else W // 4]
    opts = []
    for c in cand:
        if c > 0 and c not in opts:
            opts.append(c)
    if len(opts) < 5:
        return None
    opts, idx = _place(opts[:6], truth, want)
    if truth not in opts:
        return None
    return n, W, [str(o) for o in opts], opts.index(truth)


# ---------------------------------------------------------------- ชุดเฟือง
def gear_dirs(teeth, drive, cwise):
    """ทิศหมุนของเฟืองทุกตัว เมื่อรู้ทิศของตัวหนึ่ง — เฟืองที่ขบกันหมุนสวนทางเสมอ"""
    return [cwise if (i - drive) % 2 == 0 else not cwise for i in range(len(teeth))]


def gear_dir_q(rng, want=0, k=4):
    teeth = rng.sample([10, 12, 15, 16, 18, 20, 24, 25, 30, 36], k)
    drive = rng.randrange(k)
    cwise = rng.random() < .5
    real = gear_dirs(teeth, drive, cwise)
    ask = [i for i in range(k) if i != drive]
    truth = tuple(real[i] for i in ask)
    seen = {truth}
    opts = [truth]
    for _ in range(400):
        c = tuple(rng.random() < .5 for _ in ask)
        if c in seen:
            continue
        seen.add(c)
        opts.append(c)
        if len(opts) == 5:
            break
    if len(opts) < 5:
        return None
    opts, idx = _place(opts, truth, want)
    return teeth, drive, cwise, ask, opts, opts.index(truth)


# เฟืองต้นกับเฟืองปลายเท่านั้นที่กำหนดอัตราเร็ว เฟืองกลางไม่มีผล
# เด็กที่คูณไล่ทุกตัวจะได้คำตอบผิด ซึ่งเป็นกับดักหลักของแนวนี้
def gear_speed_q(rng, want=0, k=3):
    for _ in range(300):
        teeth = rng.sample([10, 12, 15, 20, 24, 30, 36, 40], k)
        rpm = rng.choice([60, 90, 120, 150, 180, 240])
        if (rpm * teeth[0]) % teeth[-1]:
            continue
        truth = rpm * teeth[0] // teeth[-1]
        cand = [truth, rpm * teeth[-1] // teeth[0] if (rpm * teeth[-1]) % teeth[0] == 0 else None,
                rpm * teeth[0] // teeth[1] if (rpm * teeth[0]) % teeth[1] == 0 else None,
                rpm * teeth[1] // teeth[-1] if (rpm * teeth[1]) % teeth[-1] == 0 else None,
                rpm, truth * 2, max(1, truth // 2)]
        opts = []
        for c in cand:
            if c and c > 0 and c not in opts:
                opts.append(c)
        if len(opts) < 5:
            continue
        opts, idx = _place(opts[:6], truth, want)
        if truth not in opts:
            continue
        return teeth, rpm, [str(o) for o in opts], opts.index(truth)
    return None


# ---------------------------------------------------------------- คานสมดุล
def beam_q(rng, want=0):
    """วางน้ำหนักสองก้อนฝั่งซ้าย หนึ่งก้อนฝั่งขวา แล้วถามระยะที่ทำให้สมดุล"""
    for _ in range(400):
        m1, d1 = rng.choice([2, 3, 4, 6, 8]), rng.randint(2, 7)
        m2, d2 = rng.choice([2, 3, 4, 6, 8]), rng.randint(2, 7)
        m3 = rng.choice([2, 3, 4, 6, 8, 12])
        tot = m1 * d1 + m2 * d2
        if tot % m3:
            continue
        x = tot // m3
        if not (2 <= x <= 8) or d1 == d2:
            continue
        cand = [x, x + 1, x - 1, x + 2, max(1, tot // (m1 + m2)), max(1, x * 2)]
        opts = []
        for c in cand:
            if c > 0 and c not in opts:
                opts.append(c)
        if len(opts) < 5:
            continue
        opts, idx = _place(opts[:6], x, want)
        if x not in opts:
            continue
        return (m1, d1, m2, d2, m3, x), [str(o) for o in opts], opts.index(x)
    return None


# ---------------------------------------------------------------- วงจรไฟฟ้า
# ตัวเลขในกล่องไม่ใส่หน่วย เพราะฟอนต์ Sarabun ไม่มีอักขระโอห์ม จะขึ้นเป็นกล่องว่าง
# (กับดักเดียวกับลูกศรกับเส้นตั้ง ดูหมายเหตุเรื่องฟอนต์ใน CLAUDE.md)
def _par(vals):
    tot = sum(F(1, v) for v in vals)
    return F(1) / tot


def circuit_q(rng, want=0, kind=None):
    """คืน (blocks, Rtot, แรงดัน, ตัวเลือก, ดัชนีเฉลย, ชนิดคำถาม)"""
    kind = kind or rng.choice(["r", "i"])
    for _ in range(500):
        a, b, c = (rng.choice([2, 3, 4, 6, 8, 12]) for _ in range(3))
        shape = rng.choice(["ss", "ps", "sp", "bp"])
        if shape == "ss":
            blocks, R = [str(a), str(b), str(c)], F(a + b + c)
            naive = F(a + b + c)
        elif shape == "ps":
            blocks, R = [[[str(a)], [str(b)]], str(c)], _par([a, b]) + c
            naive = F(a + b + c)
        elif shape == "sp":
            blocks, R = [str(a), [[str(b)], [str(c)]]], a + _par([b, c])
            naive = F(a + b + c)
        else:
            blocks, R = [[[str(a), str(b)], [str(c)]]], _par([a + b, c])
            naive = F(a + b + c)
        if R.denominator != 1 or R < 2:
            continue
        R = int(R)
        V = rng.choice([12, 24, 36, 48, 60])
        if kind == "i" and V % R:
            continue
        truth = R if kind == "r" else V // R
        # ตัวลวงมาจากวิธีคิดที่ผิดจริง ไม่ใช่สุ่มเลขมั่ว
        wrong = [int(naive), a + b + c - min(a, b, c), max(2, truth + 1), max(1, truth - 1),
                 truth * 2, max(1, truth // 2)]
        if kind == "i":
            wrong = [V // x for x in (int(naive), a, c) if x and V % x == 0]
            wrong += [max(1, truth + 1), max(1, truth - 1), truth * 2]
        opts = [truth]
        for w in wrong:
            if w > 0 and w not in opts:
                opts.append(w)
        if len(opts) < 5:
            continue
        opts, _ = _place(opts[:6], truth, want)
        if truth not in opts:
            continue
        return blocks, R, V, [str(o) for o in opts], opts.index(truth), kind
    return None


# ---------------------------------------------------------------- กราฟความเร็ว-เวลา
def vt_q(rng, want=0, kind=None):
    """กราฟสามช่วง เร่ง - คงที่ - หน่วง · ระยะทางคือพื้นที่ใต้กราฟ"""
    kind = kind or rng.choice(["d", "a"])
    for _ in range(400):
        v = rng.choice([8, 10, 12, 15, 16, 20])
        t1 = rng.choice([2, 3, 4, 5])
        t2 = t1 + rng.choice([4, 5, 6, 8, 10])
        t3 = t2 + rng.choice([2, 3, 4, 5, 6])
        if kind == "a" and v % t1:
            continue
        dist2 = v * ((t3) + (t2 - t1))          # สองเท่าของพื้นที่สี่เหลี่ยมคางหมู
        if dist2 % 2:
            continue
        dist = dist2 // 2
        truth = dist if kind == "d" else v // t1
        if kind == "d":
            wrong = [v * t3, v * (t2 - t1), v * t3 // 2, dist + v, max(1, dist - v)]
        else:
            wrong = [v * t1, max(1, v // t3), max(1, truth + 1), max(1, truth - 1), truth * 2]
        opts = [truth]
        for w in wrong:
            if w > 0 and w not in opts:
                opts.append(w)
        if len(opts) < 5:
            continue
        opts, _ = _place(opts[:6], truth, want)
        if truth not in opts:
            continue
        return (v, t1, t2, t3), [str(o) for o in opts], opts.index(truth), kind
    return None


# ---------------------------------------------------------------- ต่อเข้าคลัง
DIRW = {True: "ตามเข็มนาฬิกา", False: "ทวนเข็มนาฬิกา"}


def build(add, P3, rng):
    """เติมโจทย์ท่อนเชิงกลเข้าคลัง — เรียกจาก gen.py"""
    want = 0

    for qi in range(3):                       # ★☆☆-★★☆ ระบบรอก
        r = pulley_q(rng, want=want)
        if not r:
            continue
        n, W, opts, idx = r
        add(P3, "ระบบรอก",
            f"ระบบรอกดังรูปใช้ยกวัตถุที่มีน้ำหนัก {W} นิวตัน\n"
            "ถ้าเชือกและรอกเบามาก และไม่มีความฝืด "
            "จะต้องออกแรง F อย่างน้อยกี่นิวตันจึงจะยกวัตถุขึ้นได้",
            opts, idx, img=D.pulley(n, f"pl{qi}"), lvl=1 if n <= 3 else 2)
        want = (want + 2) % 5

    for qi in range(3):                       # ★★☆ ทิศหมุนของเฟือง
        r = gear_dir_q(rng, want=want)
        if not r:
            continue
        teeth, drive, cwise, ask, opts, idx = r
        nm = [CH[i] for i in range(len(teeth))]
        txt = ["  ".join(f"{nm[i]} {DIRW[c]}" for i, c in zip(ask, o)) for o in opts]
        add(P3, "ชุดเฟือง",
            f"เฟืองทั้งสี่ตัวขบกันดังรูป ถ้าเฟือง {nm[drive]} หมุน{DIRW[cwise]}\n"
            "เฟืองที่เหลือจะหมุนในทิศใดบ้าง",
            txt, idx,
            img=D.gears(teeth, f"gd{qi}", names=nm, spin=(drive, cwise)), lvl=2)
        want = (want + 2) % 5

    for qi in range(2):                       # ★★☆ อัตราเร็วของเฟือง
        r = gear_speed_q(rng, want=want)
        if not r:
            continue
        teeth, rpm, opts, idx = r
        nm = [CH[i] for i in range(len(teeth))]
        add(P3, "ชุดเฟือง",
            f"เฟืองสามตัวขบกันดังรูป เฟือง {nm[0]} หมุนด้วยอัตรา {rpm} รอบต่อนาที\n"
            f"เฟือง {nm[-1]} จะหมุนด้วยอัตรากี่รอบต่อนาที",
            opts, idx, img=D.gears(teeth, f"gs{qi}", names=nm), lvl=2)
        want = (want + 2) % 5

    for qi in range(4):                       # ★★☆ วงจรไฟฟ้า
        r = circuit_q(rng, want=want, kind="r" if qi % 2 == 0 else "i")
        if not r:
            continue
        blocks, R, V, opts, idx, kind = r
        q = ("ความต้านทานรวมของวงจรนี้เท่ากับกี่โอห์ม" if kind == "r"
             else "กระแสไฟฟ้าที่ไหลผ่านแบตเตอรี่เท่ากับกี่แอมแปร์")
        add(P3, "วงจรไฟฟ้า",
            "จากวงจรในรูป ตัวเลขที่กำกับตัวต้านทานแต่ละตัวมีหน่วยเป็นโอห์ม\n" + q,
            opts, idx, img=D.circuit(blocks, f"ck{qi}", emf=f"{V} V"),
            lvl=2 if kind == "r" else 3)
        want = (want + 2) % 5

    for qi in range(4):                       # ★★☆ กราฟความเร็ว-เวลา
        r = vt_q(rng, want=want, kind="d" if qi % 2 == 0 else "a")
        if not r:
            continue
        (v, t1, t2, t3), opts, idx, kind = r
        q = ("รถคันนี้เคลื่อนที่ได้ระยะทางทั้งหมดกี่เมตร" if kind == "d"
             else "ความเร่งของรถในช่วงแรกเท่ากับกี่เมตรต่อวินาทีกำลังสอง")
        add(P3, "กราฟความเร็ว-เวลา",
            "กราฟแสดงความเร็วของรถคันหนึ่งเทียบกับเวลา\n" + q,
            opts, idx,
            img=D.vtgraph([(0, 0), (t1, v), (t2, v), (t3, 0)], f"vt{qi}"),
            lvl=2)
        want = (want + 2) % 5

    # รูปแบบคำถามชั้นที่สอง ใช้รูปเดิมแต่ถามคนละอย่าง เพิ่มจำนวนข้อโดยไม่ต้องวาดใหม่
    for qi in range(2):                       # ★★☆ รอก ถามความยาวเชือก
        n = rng.choice([2, 3, 4, 5, 6])
        h = rng.choice([2, 3, 4, 5])
        truth = n * h
        cand = [truth, h, h * (n - 1), h * (n + 1), n, truth + h]
        opts = []
        for c in cand:
            if c > 0 and c not in opts:
                opts.append(c)
        if len(opts) < 5:
            continue
        opts, _ = _place(opts[:6], truth, want)
        add(P3, "ระบบรอก",
            "ระบบรอกดังรูปใช้ยกวัตถุขึ้นในแนวดิ่ง เชือกและรอกเบามาก ไม่มีความฝืด\n"
            f"ถ้าต้องการยกวัตถุขึ้นสูง {h} เมตร จะต้องดึงปลายเชือกเป็นระยะกี่เมตร",
            [str(o) for o in opts], opts.index(truth),
            img=D.pulley(n, f"plr{qi}"), lvl=3)
        want = (want + 2) % 5

    for qi in range(2):                       # ★★☆ คาน ถามมวลแทนระยะ
        r = beam_q(rng, want=want)
        if not r:
            continue
        (m1, d1, m2, d2, m3, x), _o, _i = r
        cand = [m3, m3 + 1, max(1, m3 - 1), m3 * 2, max(1, m3 // 2), m1 + m2]
        opts = []
        for c in cand:
            if c > 0 and c not in opts:
                opts.append(c)
        if len(opts) < 5:
            continue
        opts, _ = _place(opts[:6], m3, want)
        add(P3, "คานสมดุล",
            f"คานเบาสม่ำเสมอวางบนจุดหมุนดังรูป ฝั่งซ้ายวางมวล {m1} และ {m2} กิโลกรัม\n"
            f"ห่างจากจุดหมุน {d1} และ {d2} เมตรตามลำดับ\n"
            f"ถ้าวางมวลอีกก้อนไว้ฝั่งขวาห่างจากจุดหมุน {x} เมตรแล้วคานสมดุลพอดี\n"
            "มวลก้อนนั้นหนักกี่กิโลกรัม",
            [str(o) for o in opts], opts.index(m3),
            img=D.beam([(-d1, f"{m1} kg"), (-d2, f"{m2} kg"), (x, "?")], f"bmm{qi}"), lvl=2)
        want = (want + 2) % 5

    for qi in range(3):                       # ★★☆ คานสมดุล
        r = beam_q(rng, want=want)
        if not r:
            continue
        (m1, d1, m2, d2, m3, x), opts, idx = r
        marks = [(-d1, f"{m1} kg"), (-d2, f"{m2} kg"), (x, "?")]
        add(P3, "คานสมดุล",
            f"คานเบาสม่ำเสมอวางบนจุดหมุนดังรูป ฝั่งซ้ายวางมวล {m1} และ {m2} กิโลกรัม\n"
            f"ห่างจากจุดหมุน {d1} และ {d2} เมตรตามลำดับ\n"
            f"ถ้านำมวล {m3} กิโลกรัมไปวางฝั่งขวา ต้องวางห่างจากจุดหมุนกี่เมตรคานจึงสมดุล",
            opts, idx, img=D.beam(marks, f"bm{qi}"), lvl=2)
        want = (want + 2) % 5


# ---------------------------------------------------------------- ตรวจตัวเอง
if __name__ == "__main__":
    bad = []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    n = 0
    for s in range(300):
        rng = random.Random(s)
        for w in range(5):
            r = pulley_q(rng, want=w)
            if r:
                n += 1
                nn, W, opts, idx = r
                check(len(set(opts)) == 5, f"รอก s={s}: ตัวเลือกซ้ำ")
                check(int(opts[idx]) * nn == W, f"รอก s={s}: เฉลยไม่ใช่ W/n")
                check(idx == w, f"รอก s={s}: บังคับตำแหน่งเฉลยไม่ได้")

            r = gear_dir_q(rng, want=w)
            if r:
                n += 1
                teeth, drive, cwise, ask, opts, idx = r
                real = gear_dirs(teeth, drive, cwise)
                check(len(set(opts)) == 5, f"เฟืองทิศ s={s}: ตัวเลือกซ้ำ")
                check(opts[idx] == tuple(real[i] for i in ask),
                      f"เฟืองทิศ s={s}: เฉลยไม่ตรงกับกฎสลับทิศ")
                check(sum(1 for o in opts if o == opts[idx]) == 1,
                      f"เฟืองทิศ s={s}: มีคำตอบถูกเกินหนึ่ง")
                check(real[drive] == cwise, f"เฟืองทิศ s={s}: ตัวที่โจทย์บอกทิศเพี้ยน")

            r = gear_speed_q(rng, want=w)
            if r:
                n += 1
                teeth, rpm, opts, idx = r
                check(len(set(opts)) == 5, f"เฟืองเร็ว s={s}: ตัวเลือกซ้ำ")
                # เฟืองกลางต้องไม่มีผลต่ออัตราเร็วของตัวปลาย
                check(int(opts[idx]) * teeth[-1] == rpm * teeth[0],
                      f"เฟืองเร็ว s={s}: เฉลยไม่ตรงกับอัตราส่วนฟัน")

            r = circuit_q(rng, want=w)
            if r:
                n += 1
                blocks, R, V, opts, idx, kind = r
                check(len(set(opts)) == 5, f"วงจร s={s}: ตัวเลือกซ้ำ")
                want_v = R if kind == "r" else V // R
                check(int(opts[idx]) == want_v, f"วงจร s={s}: เฉลยไม่ตรงกับที่คำนวณ")
                check(sum(1 for o in opts if o == opts[idx]) == 1,
                      f"วงจร s={s}: มีคำตอบถูกเกินหนึ่ง")

            r = vt_q(rng, want=w)
            if r:
                n += 1
                (v, t1, t2, t3), opts, idx, kind = r
                check(len(set(opts)) == 5, f"กราฟ s={s}: ตัวเลือกซ้ำ")
                area = v * ((t3) + (t2 - t1)) // 2      # พื้นที่ใต้กราฟ = ระยะทาง
                check(int(opts[idx]) == (area if kind == "d" else v // t1),
                      f"กราฟ s={s}: เฉลยไม่ตรงกับพื้นที่ใต้กราฟ")
                check(t1 < t2 < t3, f"กราฟ s={s}: เวลาไม่เรียงกัน")

            r = beam_q(rng, want=w)
            if r:
                n += 1
                (m1, d1, m2, d2, m3, x), opts, idx = r
                check(len(set(opts)) == 5, f"คาน s={s}: ตัวเลือกซ้ำ")
                check(m1 * d1 + m2 * d2 == m3 * int(opts[idx]),
                      f"คาน s={s}: โมเมนต์สองฝั่งไม่เท่ากัน")
                check(sum(1 for o in opts if o == opts[idx]) == 1,
                      f"คาน s={s}: มีคำตอบถูกเกินหนึ่ง")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:10]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ — รอก · เฟือง · คาน · วงจร · กราฟ v-t")

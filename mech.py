#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์ท่อนเชิงกล (วีคฟิสิกส์) — ข้อ 31-45 ของข้อสอบจริง

ที่มาของแนวอยู่ใน `reference/tpat3/DIGEST-part3.md`

  ระบบรอก        แรง = น้ำหนัก ÷ จำนวนเส้นเชือกที่รับน้ำหนัก
  ชุดเฟือง       ทิศสลับทีละตัว · เรียงธรรมดาตัวกลางไม่มีผล · **ซ้อนเพลาแล้วมีผลทันที**
  คานสมดุล       ผลรวมโมเมนต์สองฝั่งเท่ากัน
  วงจรไฟฟ้า      อนุกรม/ขนาน · บริดจ์สมดุล · สวิตช์กับหลอดไฟ
  กราฟการเคลื่อนที่  v-t · s-t · a-t

ทุกข้อพิสูจน์คำตอบด้วยโค้ด (กติกาข้อ 1) รันไฟล์นี้ตรง ๆ = ตรวจตัวเอง
"""
from fractions import Fraction as F
import itertools
import random

import draw as D

CH = "กขคงจ"
DIRW = {True: "ตามเข็มนาฬิกา", False: "ทวนเข็มนาฬิกา"}


def _place(opts, truth, want):
    """ดันคำตอบถูกไปอยู่ตำแหน่งที่สั่ง เพื่อให้เฉลยกระจายครบ ก-จ (กติกาข้อ 4)"""
    rest = [o for o in opts if o != truth]
    out = rest[:want] + [truth] + rest[want:]
    return out[:5], want


def _opts(truth, wrong, want):
    """ประกอบตัวเลือกจากคำตอบถูกกับรายการตัวลวง ตัดตัวซ้ำและตัวที่ไม่สมเหตุสมผลออก"""
    out = [truth]
    for w in wrong:
        if w is not None and w not in out:
            out.append(w)
    if len(out) < 5:
        return None
    return _place(out[:6], truth, want)[0]


def _frac(x):
    """เขียนเศษส่วนให้อ่านง่ายในชีท จำนวนเต็มพิมพ์เป็นจำนวนเต็ม"""
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


# ================================================================ ระบบรอก
PULLEY_SETS = [(2, 120), (3, 120), (4, 120), (5, 120), (6, 120),
               (2, 60), (3, 60), (4, 60), (2, 240), (4, 240), (6, 240)]


def pulley_q(rng, want=0, n=None):
    cand = [p for p in PULLEY_SETS if n is None or p[0] == n]
    nn, W = rng.choice(cand)
    truth = W // nn
    wrong = [W // (nn - 1), W // (nn + 1), W // 2, W, W * 2 // nn if nn > 2 else W // 4]
    o = _opts(truth, wrong, want)
    if not o:
        return None
    return nn, W, [str(x) for x in o], o.index(truth)


def pulley_rope_q(rng, want=0, n=None):
    """ยกของสูง h ต้องดึงเชือกยาว n*h — งานที่ทำเท่ากัน แรงน้อยลงแลกกับระยะที่มากขึ้น"""
    nn = n or rng.choice([2, 3, 4, 5, 6])
    h = rng.choice([2, 3, 4, 5])
    truth = nn * h
    o = _opts(truth, [h, h * (nn - 1), h * (nn + 1), nn, truth + h], want)
    if not o:
        return None
    return nn, h, [str(x) for x in o], o.index(truth)


# ================================================================ ชุดเฟือง
def gear_dirs(teeth, drive, cwise):
    """เฟืองที่ขบกันหมุนสวนทางเสมอ ทิศจึงสลับทีละตัวไปตามแถว"""
    return [cwise if (i - drive) % 2 == 0 else not cwise for i in range(len(teeth))]


def gear_dir_q(rng, want=0, k=4):
    teeth = rng.sample([10, 12, 15, 16, 18, 20, 24, 25, 30, 36], k)
    drive = rng.randrange(k)
    cwise = rng.random() < .5
    real = gear_dirs(teeth, drive, cwise)
    ask = [i for i in range(k) if i != drive]
    truth = tuple(real[i] for i in ask)
    seen, opts = {truth}, [truth]
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
    # วางเฉียงสลับขึ้นลง ให้หน้าตาต่างจากแถวตรง และบังคับให้เด็กไล่ทิศทีละคู่จริง ๆ
    angles = [rng.choice([-38, -26, 0, 26, 38]) for _ in range(k - 1)]
    opts, _ = _place(opts, truth, want)
    return teeth, drive, cwise, ask, angles, opts, opts.index(truth)


def gear_speed_q(rng, want=0, k=3):
    """อัตราเร็วของเฟืองปลายขึ้นกับเฟืองต้นกับปลายเท่านั้น เฟืองกลางไม่มีผล"""
    for _ in range(400):
        teeth = rng.sample([10, 12, 15, 20, 24, 30, 36, 40], k)
        rpm = rng.choice([60, 90, 120, 150, 180, 240])
        if (rpm * teeth[0]) % teeth[-1]:
            continue
        truth = rpm * teeth[0] // teeth[-1]
        wrong = [rpm * teeth[-1] // teeth[0] if (rpm * teeth[-1]) % teeth[0] == 0 else None,
                 rpm * teeth[0] // teeth[1] if (rpm * teeth[0]) % teeth[1] == 0 else None,
                 rpm, truth * 2, max(1, truth // 2)]
        o = _opts(truth, [w for w in wrong if w], want)
        if not o:
            continue
        return teeth, rpm, [str(x) for x in o], o.index(truth)
    return None


def gear_rev_q(rng, want=0):
    """ถามเป็นจำนวนรอบ และปล่อยให้คำตอบเป็นเศษส่วนได้ เพื่อไม่ให้เดาจากรูปเลขได้"""
    for _ in range(400):
        ta, tb = rng.sample([8, 10, 12, 15, 16, 18, 20, 24, 30, 36, 40], 2)
        N = rng.choice([1, 2, 3, 4, 6])
        truth = F(N * ta, tb)
        if truth == 1 or truth.denominator > 6:
            continue
        wrong = [F(N * tb, ta), F(ta, tb), F(tb, ta), F(N), truth * 2]
        o = _opts(truth, wrong, want)
        if not o:
            continue
        return (ta, tb, N), [_frac(x) for x in o], o.index(truth)
    return None


def gear_compound_q(rng, want=0):
    """เฟืองซ้อนเพลา — อัตราทดคูณกัน ต่างจากเฟืองเรียงธรรมดาที่ตัวกลางไม่มีผล

    กับดักหลักคือเด็กที่จำว่า "ตัวกลางไม่มีผล" มาใช้ดื้อ ๆ จะได้ N*t0/t2 ซึ่งผิด
    ตัวลวงตัวนั้นจึงต้องมีอยู่ในตัวเลือกเสมอ
    """
    for _ in range(600):
        t0, t1a, t1b, t2 = (rng.choice([10, 12, 15, 20, 24, 30, 36]) for _ in range(4))
        if len({t0, t1a, t1b, t2}) < 3 or t1a <= t1b:
            continue
        N = rng.choice([1, 2, 3, 4])
        truth = F(N * t0 * t1b, t1a * t2)
        trap = F(N * t0, t2)                    # คิดแบบเฟืองเรียงธรรมดา
        if truth == trap or truth.denominator > 8 or truth > 12:
            continue
        wrong = [trap, F(N * t1a * t2, t0 * t1b), F(N * t0 * t1a, t1b * t2), F(N), truth * 2]
        o = _opts(truth, wrong, want)
        if not o:
            continue
        return (t0, t1a, t1b, t2, N), [_frac(x) for x in o], o.index(truth), _frac(trap)
    return None


# ================================================================ คานสมดุล
def beam_q(rng, want=0, ask="dist"):
    """คานเบาบนจุดหมุน ฝั่งซ้ายสองก้อน ฝั่งขวาหนึ่งก้อน

    ระยะทุกตัวต้องห่างกันอย่างน้อย 2 ขีด ไม่งั้นกล่องน้ำหนักในรูปจะซ้อนกันจนอ่านไม่ออก
    รูปไม่พิมพ์ตัวเลขระยะ ให้เด็กนับขีดเอง ตามที่ข้อสอบจริงทำ
    """
    for _ in range(600):
        m1, d1 = rng.choice([2, 3, 4, 6, 8]), rng.randint(2, 7)
        m2, d2 = rng.choice([2, 3, 4, 6, 8]), rng.randint(2, 7)
        if abs(d1 - d2) < 2:
            continue
        m3 = rng.choice([2, 3, 4, 6, 8, 12])
        tot = m1 * d1 + m2 * d2
        if tot % m3:
            continue
        x = tot // m3
        if not (2 <= x <= 8):
            continue
        if ask == "dist":
            truth = x
            wrong = [x + 1, x - 1, x + 2, tot // (m1 + m2), x * 2]
        else:
            truth = m3
            wrong = [m3 + 1, m3 - 1, m3 * 2, m3 // 2, m1 + m2]
        o = _opts(truth, [w for w in wrong if w and w > 0], want)
        if not o:
            continue
        return (m1, d1, m2, d2, m3, x), [str(v) for v in o], o.index(truth)
    return None


# ================================================================ วงจรไฟฟ้า
def _par(vals):
    return F(1) / sum(F(1, v) for v in vals)


def circuit_q(rng, want=0, kind=None):
    kind = kind or rng.choice(["r", "i"])
    for _ in range(600):
        a, b, c = (rng.choice([2, 3, 4, 6, 8, 12]) for _ in range(3))
        shape = rng.choice(["ps", "sp", "bp", "pss"])
        if shape == "ps":
            blocks, R = [[[str(a)], [str(b)]], str(c)], _par([a, b]) + c
        elif shape == "sp":
            blocks, R = [str(a), [[str(b)], [str(c)]]], a + _par([b, c])
        elif shape == "bp":
            blocks, R = [[[str(a), str(b)], [str(c)]]], _par([a + b, c])
        else:
            blocks, R = [[[str(a)], [str(b)]], str(c), str(c)], _par([a, b]) + 2 * c
        naive = a + b + c
        if R.denominator != 1 or R < 2:
            continue
        R = int(R)
        V = rng.choice([12, 24, 36, 48, 60])
        if kind == "i" and V % R:
            continue
        truth = R if kind == "r" else V // R
        if kind == "r":
            wrong = [naive, a + b + c - min(a, b, c), truth + 1, truth - 1, truth * 2]
        else:
            wrong = [V // x for x in (naive, a, c) if x and V % x == 0]
            wrong += [truth + 1, truth - 1, truth * 2]
        o = _opts(truth, [w for w in wrong if w and w > 0], want)
        if not o:
            continue
        return blocks, R, V, [str(x) for x in o], o.index(truth), kind
    return None


def bridge_q(rng, want=0, kind=None):
    """บริดจ์วีตสโตน — สมดุลเมื่อ R1*R4 = R2*R3 ตอนนั้นมิเตอร์อ่านศูนย์

    kind = "find" หาค่าที่ทำให้สมดุล · "read" ถามค่าที่มิเตอร์อ่านได้เมื่อสมดุลอยู่แล้ว
    ข้อ read เป็นกับดักที่ดี เพราะเด็กจะไปนั่งย่อวงจร ทั้งที่ตอบศูนย์ได้ทันที
    """
    for _ in range(600):
        r1, r2, r3 = (rng.choice([2, 3, 4, 6, 8, 9, 12]) for _ in range(3))
        v = F(r2 * r3, r1)
        if v.denominator != 1:
            continue
        r4 = int(v)
        if r4 < 2 or r4 > 40 or len({r1, r2, r3, r4}) < 3:
            continue
        if kind == "read":
            return (r1, r2, r3, r4), None, None, "read"
        truth = r4
        wrong = [r1 * r2 // r3 if (r1 * r2) % r3 == 0 else None,
                 r1 * r3 // r2 if (r1 * r3) % r2 == 0 else None,
                 r1 + r2 - r3 if r1 + r2 - r3 > 0 else None,
                 truth + 1, truth * 2]
        o = _opts(truth, [w for w in wrong if w], want)
        if not o:
            continue
        return (r1, r2, r3, r4), [str(x) for x in o], o.index(truth), "find"
    return None


SWNAME = ["S1", "S2", "S3", "S4"]        # ป้ายที่พิมพ์ในรูป เรียงตาม s0 s1 s2 s3


def switch_q(rng, want=0):
    """ถามว่าต้องปิดสวิตช์ตัวใดบ้าง จึงจะได้สถานะหลอดตามที่โจทย์กำหนด

    ไล่ครบทั้ง 16 สถานะแล้วเก็บเฉพาะเป้าหมายที่มีคำตอบเดียว
    S2 คร่อมหลอด L3 ไว้ ปิด S2 แล้ว L3 จะ *ดับ* ไม่ใช่ติด เพราะกระแสลัดผ่านสวิตช์
    """
    all_states = list(itertools.product([False, True], repeat=4))
    bymap = {}
    for st in all_states:
        bymap.setdefault(D.bulb_states(*st), []).append(st)
    targets = [(t, v[0]) for t, v in bymap.items() if len(v) == 1 and any(t)]
    if not targets:
        return None
    rng.shuffle(targets)
    target, sol = targets[0]
    truth = frozenset(SWNAME[i] for i, on in enumerate(sol) if on)
    opts = [truth]
    pool = [frozenset(SWNAME[i] for i, on in enumerate(st) if on) for st in all_states]
    rng.shuffle(pool)
    for p in pool:
        if p not in opts and p:
            opts.append(p)
        if len(opts) == 5:
            break
    if len(opts) < 5:
        return None
    opts, _ = _place(opts, truth, want)
    return target, opts, opts.index(truth)


# ================================================================ กราฟการเคลื่อนที่
def graph_q(rng, want=0, kind=None):
    """kind: vt_d ระยะจากพื้นที่ · vt_a ความเร่งจากความชัน
             st_v ความเร็วจากความชันของกราฟตำแหน่ง · at_dv ความเร็วที่เปลี่ยนจากพื้นที่
    """
    kind = kind or rng.choice(["vt_d", "vt_a", "st_v", "at_dv"])
    for _ in range(500):
        if kind in ("vt_d", "vt_a"):
            v = rng.choice([8, 10, 12, 15, 16, 20])
            t1 = rng.choice([2, 3, 4, 5])
            t2 = t1 + rng.choice([4, 5, 6, 8, 10])
            t3 = t2 + rng.choice([2, 3, 4, 5, 6])
            pts = [(0, 0), (t1, v), (t2, v), (t3, 0)]
            area2 = v * (t3 + (t2 - t1))
            if area2 % 2:
                continue
            if kind == "vt_d":
                truth = area2 // 2
                wrong = [v * t3, v * (t2 - t1), v * t3 // 2, truth + v, truth - v]
            else:
                if v % t1:
                    continue
                truth = v // t1
                wrong = [v * t1, max(1, v // t3), truth + 1, truth - 1, truth * 2]
        elif kind == "st_v":
            s1 = rng.choice([20, 30, 40, 60])
            t1 = rng.choice([2, 4, 5])
            t2 = t1 + rng.choice([3, 4, 5])
            s3 = s1 + rng.choice([20, 40, 60])
            t3 = t2 + rng.choice([2, 4, 5])
            if s1 % t1 or (s3 - s1) % (t3 - t2):
                continue
            pts = [(0, 0), (t1, s1), (t2, s1), (t3, s3)]
            truth = (s3 - s1) // (t3 - t2)       # ความชันช่วงสุดท้าย
            wrong = [s1 // t1, s3 // t3 if s3 % t3 == 0 else None,
                     truth + 1, truth - 1, truth * 2]
        else:
            a = rng.choice([2, 3, 4, 5, 6])
            t1 = rng.choice([3, 4, 5, 6])
            pts = [(0, a), (t1, a), (t1, 0), (t1 + rng.choice([2, 3]), 0)]
            truth = a * t1                        # พื้นที่ใต้กราฟ a-t คือความเร็วที่เปลี่ยนไป
            wrong = [a, t1, a + t1, truth * 2, max(1, truth // 2)]
        o = _opts(truth, [w for w in wrong if w and w > 0], want)
        if not o:
            continue
        return kind, pts, [str(x) for x in o], o.index(truth)
    return None


GRAPH_META = {
    "vt_d": ("v (m/s)", "จากกราฟความเร็ว-เวลาของรถคันหนึ่ง จงหาระยะทางทั้งหมดที่รถเคลื่อนที่ได้ (เมตร)",
             "ระยะทาง = พื้นที่ใต้กราฟ v-t"),
    "vt_a": ("v (m/s)", "จากกราฟความเร็ว-เวลาของรถคันหนึ่ง ความเร่งในช่วงแรกมีค่ากี่เมตรต่อวินาทีกำลังสอง",
             "ความเร่ง = ความชันของกราฟ v-t"),
    "st_v": ("s (m)", "จากกราฟตำแหน่ง-เวลาของวัตถุหนึ่ง อัตราเร็วในช่วงสุดท้ายมีค่ากี่เมตรต่อวินาที",
             "อัตราเร็ว = ความชันของกราฟ s-t · ช่วงที่กราฟราบคืออยู่นิ่ง"),
    "at_dv": ("a (m/s²)", "จากกราฟความเร่ง-เวลาของวัตถุที่เริ่มจากหยุดนิ่ง ความเร็วปลายมีค่ากี่เมตรต่อวินาที",
              "ความเร็วที่เปลี่ยนไป = พื้นที่ใต้กราฟ a-t"),
}


# ================================================================ ต่อเข้าคลัง
def build(add, P3, rng):
    """เติมโจทย์ท่อนเชิงกลเข้าคลัง — เรียกจาก gen.py"""
    want = 0

    def nxt():
        nonlocal want
        want = (want + 2) % 5

    # ---- ระบบรอก : บังคับให้จำนวนเส้นเชือกไม่ซ้ำกัน และสลับข้างรูป
    for qi, n in enumerate([2, 4, 6]):
        r = pulley_q(rng, want=want, n=n)
        if not r:
            continue
        nn, W, opts, idx = r
        add(P3, "ระบบรอก",
            f"ระบบรอกดังรูปใช้ยกวัตถุที่มีน้ำหนัก {W} นิวตัน เชือกและรอกเบามาก ไม่มีความฝืด\n"
            "ต้องออกแรง F อย่างน้อยกี่นิวตันจึงจะยกวัตถุขึ้นได้",
            opts, idx, img=D.pulley(nn, f"pl{qi}", mirror=qi % 2 == 1),
            lvl=1 if nn <= 3 else 2,
            why=f"F = W/n · นับเส้นเชือกที่พาดขึ้นจากรอกล่างได้ {nn} เส้น")
        nxt()

    for qi, n in enumerate([3, 5]):
        r = pulley_rope_q(rng, want=want, n=n)
        if not r:
            continue
        nn, h, opts, idx = r
        add(P3, "ระบบรอก",
            "ระบบรอกดังรูปใช้ยกวัตถุขึ้นในแนวดิ่ง เชือกและรอกเบามาก ไม่มีความฝืด\n"
            f"ถ้าต้องการยกวัตถุขึ้นสูง {h} เมตร ต้องดึงปลายเชือกเป็นระยะกี่เมตร",
            opts, idx, img=D.pulley(nn, f"plr{qi}", mirror=qi % 2 == 0), lvl=3,
            why=f"งานเท่าเดิม แรงลด n เท่า ระยะจึงเพิ่ม n เท่า · {nn} x {h}")
        nxt()

    # ---- ชุดเฟือง
    for qi in range(2):
        r = gear_dir_q(rng, want=want)
        if not r:
            continue
        teeth, drive, cwise, ask, angles, opts, idx = r
        nm = [CH[i] for i in range(len(teeth))]
        txt = ["  ".join(f"{nm[i]} {DIRW[c]}" for i, c in zip(ask, o)) for o in opts]
        add(P3, "ชุดเฟือง",
            f"เฟืองทั้งสี่ตัวขบกันดังรูป เฟือง {nm[drive]} หมุน{DIRW[cwise]}\n"
            "เฟืองที่เหลือหมุนในทิศใดบ้าง",
            txt, idx,
            img=D.gears(teeth, f"gd{qi}", names=nm, spin=(drive, cwise), angles=angles),
            lvl=2, why="เฟืองที่ขบกันหมุนสวนทางเสมอ ทิศจึงสลับทีละตัว")
        nxt()

    r = gear_speed_q(rng, want=want)
    if r:
        teeth, rpm, opts, idx = r
        nm = [CH[i] for i in range(len(teeth))]
        add(P3, "ชุดเฟือง",
            f"เฟืองสามตัวขบกันดังรูป เฟือง {nm[0]} หมุนด้วยอัตรา {rpm} รอบต่อนาที\n"
            f"เฟือง {nm[-1]} หมุนด้วยอัตรากี่รอบต่อนาที",
            opts, idx, img=D.gears(teeth, "gs0", names=nm), lvl=2,
            why=f"n1 t1 = n2 t2 · เฟืองกลางไม่มีผล · {rpm} x {teeth[0]}/{teeth[-1]}")
        nxt()

    r = gear_rev_q(rng, want=want)
    if r:
        (ta, tb, N), opts, idx = r
        add(P3, "ชุดเฟือง",
            f"เฟืองสองตัวขบกันดังรูป เฟือง ก มี {ta} ฟัน เฟือง ข มี {tb} ฟัน\n"
            f"ถ้าเฟือง ก หมุนครบ {N} รอบ เฟือง ข จะหมุนกี่รอบ",
            opts, idx, img=D.gears([ta, tb], "gr0", names=["ก", "ข"]), lvl=2,
            why=f"จำนวนฟันที่ขบกันเท่ากัน · {N} x {ta}/{tb}")
        nxt()

    r = gear_compound_q(rng, want=want)
    if r:
        (t0, t1a, t1b, t2, N), opts, idx, trap = r
        add(P3, "ชุดเฟือง",
            f"เฟือง ข เป็นเฟืองสองวงยึดบนเพลาเดียวกัน จึงหมุนไปพร้อมกันเสมอ\n"
            f"วงนอก {t1a} ฟันขบกับเฟือง ก  วงใน {t1b} ฟันขบกับเฟือง ค\n"
            f"ถ้าเฟือง ก หมุนครบ {N} รอบ เฟือง ค จะหมุนกี่รอบ",
            opts, idx,
            img=D.gears([t0, (t1a, t1b), t2], "gc0", names=["ก", "ข", "ค"]), lvl=3,
            why=f"เพลาร่วมทำให้อัตราทดคูณกัน · ตอบ {trap} คือคิดแบบเฟืองเรียงธรรมดา")
        nxt()

    # ---- คานสมดุล
    for qi, ask in enumerate(["dist", "mass", "dist"]):
        r = beam_q(rng, want=want, ask=ask)
        if not r:
            continue
        (m1, d1, m2, d2, m3, x), opts, idx = r
        marks = [(-d1, f"{m1} kg"), (-d2, f"{m2} kg"), (x, "?")]
        head = ("คานเบาสม่ำเสมอวางบนจุดหมุนดังรูป ขีดบนคานห่างกันขีดละ 1 เมตร\n")
        if ask == "dist":
            q = f"ต้องวางมวล {m3} กิโลกรัมไว้ที่ตำแหน่งใด (ห่างจากจุดหมุนกี่เมตร) คานจึงสมดุล"
        else:
            q = "มวลที่ต้องวางในช่องเครื่องหมายคำถาม มีค่ากี่กิโลกรัมคานจึงสมดุล"
        add(P3, "คานสมดุล", head + q, opts, idx,
            img=D.beam(marks, f"bm{qi}"), lvl=2,
            why="ผลรวมโมเมนต์สองฝั่งเท่ากัน · m x d ซ้าย = m x d ขวา")
        nxt()

    # ---- วงจรไฟฟ้า
    for qi, kind in enumerate(["r", "i"]):
        r = circuit_q(rng, want=want, kind=kind)
        if not r:
            continue
        blocks, R, V, opts, idx, kind = r
        q = ("ความต้านทานรวมของวงจรมีค่ากี่โอห์ม" if kind == "r"
             else "กระแสไฟฟ้าที่ไหลผ่านแบตเตอรี่มีค่ากี่แอมแปร์")
        add(P3, "วงจรไฟฟ้า",
            "ตัวเลขที่กำกับตัวต้านทานแต่ละตัวในรูปมีหน่วยเป็นโอห์ม\n" + q,
            opts, idx, img=D.circuit(blocks, f"ck{qi}", emf=f"{V} V"),
            lvl=2 if kind == "r" else 3,
            why="ย่อขนานก่อนแล้วบวกอนุกรม" + ("" if kind == "r" else f" · I = V/R = {V}/{R}"))
        nxt()

    r = bridge_q(rng, want=want, kind="find")
    if r:
        (r1, r2, r3, r4), opts, idx, _k = r
        add(P3, "วงจรไฟฟ้า",
            "วงจรบริดจ์ในรูป ตัวเลขมีหน่วยเป็นโอห์ม และ G คือแกลแวนอมิเตอร์\n"
            "ต้องปรับตัวต้านทานช่องเครื่องหมายคำถามเป็นกี่โอห์ม เข็มของ G จึงชี้ศูนย์",
            opts, idx, img=D.bridge((str(r1), str(r2), str(r3), "?", "G"), "br0", emf="E"),
            lvl=3, why=f"บริดจ์สมดุลเมื่อคูณไขว้เท่ากัน · {r1} x ? = {r2} x {r3}")
        nxt()

    r = bridge_q(rng, want=want, kind="read")
    if r:
        (r1, r2, r3, r4), _o, _i, _k = r
        opts = _opts(0, [r1, r2, r1 + r2, abs(r1 - r3) or r3], want)
        if opts:
            add(P3, "วงจรไฟฟ้า",
                "วงจรบริดจ์ในรูป ตัวเลขมีหน่วยเป็นโอห์ม\n"
                "กระแสที่ไหลผ่านแกลแวนอมิเตอร์ G มีค่ากี่แอมแปร์",
                [str(x) for x in opts], opts.index(0),
                img=D.bridge((str(r1), str(r2), str(r3), str(r4), "G"), "br1", emf="E"),
                lvl=3,
                why=f"คูณไขว้เท่ากัน ({r1} x {r4} = {r2} x {r3}) บริดจ์สมดุล กระแสจึงเป็นศูนย์")
            nxt()

    r = switch_q(rng, want=want)
    if r:
        target, opts, idx = r
        on = [f"L{i+1}" for i, t in enumerate(target) if t]
        off = [f"L{i+1}" for i, t in enumerate(target) if not t]
        cond = "ให้หลอด " + " และ ".join(on) + " ติด"
        if off:
            cond += " ส่วนหลอด " + " และ ".join(off) + " ไม่ติด"
        add(P3, "วงจรไฟฟ้า",
            f"จากวงจรในรูป ต้องการ{cond}\nต้องปิดสวิตช์ชุดใด",
            ["  ".join(sorted(o)) for o in opts], idx,
            img=D.switchboard(SWNAME, ["L1", "L2", "L3"], "sb0", emf="E"), lvl=3,
            why="S2 คร่อม L3 ไว้ ปิด S2 แล้ว L3 ดับ เพราะกระแสลัดผ่านสวิตช์")
        nxt()

    # ---- กราฟการเคลื่อนที่ สี่แบบ ไม่ซ้ำกัน
    for qi, kind in enumerate(["vt_d", "st_v", "at_dv", "vt_a"]):
        r = graph_q(rng, want=want, kind=kind)
        if not r:
            continue
        kind, pts, opts, idx = r
        ylab, stem, why = GRAPH_META[kind]
        add(P3, "กราฟการเคลื่อนที่", stem, opts, idx,
            img=D.vtgraph(pts, f"gp{qi}", ylab=ylab), lvl=2, why=why)
        nxt()


# ================================================================ ตรวจตัวเอง
if __name__ == "__main__":
    bad, n = [], 0

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    for s in range(250):
        rng = random.Random(s)
        for w in range(5):
            r = pulley_q(rng, want=w)
            if r:
                n += 1
                nn, W, o, i = r
                ck(len(set(o)) == 5 and i == w, f"รอก s={s}")
                ck(int(o[i]) * nn == W, f"รอก s={s}: เฉลยไม่ใช่ W/n")

            r = pulley_rope_q(rng, want=w)
            if r:
                n += 1
                nn, h, o, i = r
                ck(int(o[i]) == nn * h, f"รอกเชือก s={s}")

            r = gear_dir_q(rng, want=w)
            if r:
                n += 1
                teeth, drive, cwise, ask, angles, o, i = r
                real = gear_dirs(teeth, drive, cwise)
                ck(len(set(o)) == 5, f"เฟืองทิศ s={s}: ตัวเลือกซ้ำ")
                ck(o[i] == tuple(real[k] for k in ask), f"เฟืองทิศ s={s}: เฉลยผิดกฎสลับทิศ")
                ck(len(angles) == len(teeth) - 1, f"เฟืองทิศ s={s}: มุมไม่ครบ")

            r = gear_speed_q(rng, want=w)
            if r:
                n += 1
                teeth, rpm, o, i = r
                ck(int(o[i]) * teeth[-1] == rpm * teeth[0], f"เฟืองเร็ว s={s}")

            r = gear_rev_q(rng, want=w)
            if r:
                n += 1
                (ta, tb, N), o, i = r
                ck(F(o[i]) == F(N * ta, tb), f"เฟืองรอบ s={s}")

            r = gear_compound_q(rng, want=w)
            if r:
                n += 1
                (t0, t1a, t1b, t2, N), o, i, trap = r
                ck(F(o[i]) == F(N * t0 * t1b, t1a * t2), f"เฟืองซ้อนเพลา s={s}")
                ck(trap in o, f"เฟืองซ้อนเพลา s={s}: ตัวลวงสำคัญหายไป")
                ck(F(trap) != F(o[i]), f"เฟืองซ้อนเพลา s={s}: ตัวลวงชนเฉลย")

            for ask in ("dist", "mass"):
                r = beam_q(rng, want=w, ask=ask)
                if r:
                    n += 1
                    (m1, d1, m2, d2, m3, x), o, i = r
                    ck(m1 * d1 + m2 * d2 == m3 * x, f"คาน s={s}: โมเมนต์ไม่เท่ากัน")
                    ck(abs(d1 - d2) >= 2, f"คาน s={s}: กล่องน้ำหนักจะซ้อนกัน")
                    ck(int(o[i]) == (x if ask == "dist" else m3), f"คาน s={s}: เฉลยผิดช่อง")

            r = circuit_q(rng, want=w)
            if r:
                n += 1
                blocks, R, V, o, i, kind = r
                ck(int(o[i]) == (R if kind == "r" else V // R), f"วงจร s={s}")

            r = bridge_q(rng, want=w, kind="find")
            if r:
                n += 1
                (r1, r2, r3, r4), o, i, _k = r
                ck(r1 * int(o[i]) == r2 * r3, f"บริดจ์ s={s}: ไม่สมดุล")

            r = switch_q(rng, want=w)
            if r:
                n += 1
                target, o, i = r
                sol = tuple(SWNAME[k] in o[i] for k in range(4))
                ck(D.bulb_states(*sol) == target, f"สวิตช์ s={s}: สถานะหลอดไม่ตรง")
                hit = [st for st in itertools.product([False, True], repeat=4)
                       if D.bulb_states(*st) == target]
                ck(len(hit) == 1, f"สวิตช์ s={s}: มีคำตอบมากกว่าหนึ่งชุด")

            for kind in ("vt_d", "vt_a", "st_v", "at_dv"):
                r = graph_q(rng, want=w, kind=kind)
                if r:
                    n += 1
                    k2, pts, o, i = r
                    ck(len(set(o)) == 5, f"กราฟ {kind} s={s}: ตัวเลือกซ้ำ")
                    ck(k2 == kind, f"กราฟ {kind} s={s}: ชนิดเพี้ยน")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:12]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ — รอก · เฟือง(ทิศ/เร็ว/รอบ/ซ้อนเพลา) · คาน · "
          f"วงจร(อนุกรม-ขนาน/บริดจ์/สวิตช์) · กราฟ v-t s-t a-t")

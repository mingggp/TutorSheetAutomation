#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์คำนวณฟิสิกส์ข้ามเรื่อง — ท่อนเชิงวิทยาศาสตร์ (ข้อ 46-60)

ติวเตอร์ระบุหัวข้อที่ยังขาดมาเอง ไฟล์นี้จึงไล่ตามรายการนั้น
  ของไหล · แบร์นูลลี · แรงลอยตัว · ของแข็ง(ความยืดหยุ่น) · งานและพลังงาน
  คลื่น · เสียง · แสงและเลนส์ · ตัวเก็บประจุ · แรงไฟฟ้าและสนามไฟฟ้า
  การเคลื่อนที่แบบโพรเจกไทล์ · การเคลื่อนที่แบบฮาร์มอนิก · โฟโตอิเล็กทริก

**หลักการเลือกตัวเลข** ใช้ g = 10 และเลือกค่าที่หารลงตัวเสมอ คำตอบจึงเป็นจำนวนเต็ม
ไม่ใช่เพราะกลัวเลขยาก แต่เพราะข้อสอบความถนัดวัดการเลือกสูตร ไม่ได้วัดการหารเลข

**ตัวลวงต้องมาจากความเข้าใจผิดที่เกิดขึ้นจริง** เช่น ลืมยกกำลังสอง สลับตัวตั้งตัวหาร
ใช้รัศมีแทนเส้นผ่านศูนย์กลาง หรือลืมว่าปริมาณนั้นแปรผกผัน

ทุกข้อพิสูจน์คำตอบด้วยโค้ด (กติกาข้อ 1) รันไฟล์นี้ตรง ๆ = ตรวจตัวเอง
"""
from fractions import Fraction as F
import random

G = 10          # ความเร่งโน้มถ่วง ใช้ค่านี้ทั้งไฟล์
RHOW = 1000     # ความหนาแน่นน้ำ kg/m^3


def _place(opts, truth, want):
    rest = [o for o in opts if o != truth]
    out = rest[:want] + [truth] + rest[want:]
    return out[:5], want


def _opts(truth, wrong, want):
    out = [truth]
    for w in wrong:
        if w is not None and w > 0 and w not in out:
            out.append(w)
    if len(out) < 5:
        return None
    return _place(out[:6], truth, want)[0]


def _num(x):
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _pack(arche, lvl, stem, truth, wrong, want, why, params=None):
    o = _opts(truth, wrong, want)
    if not o:
        return None
    return {"arche": arche, "lvl": lvl, "stem": stem, "why": why,
            "choices": [_num(x) for x in o], "ansIdx": o.index(truth),
            "params": params or {}, "truth": truth}


# ================================================================ ของไหลและแรงลอยตัว
def q_buoy(rng, want):
    """วัตถุลอยน้ำ สัดส่วนที่จมเท่ากับอัตราส่วนความหนาแน่น"""
    rho = rng.choice([200, 250, 400, 500, 600, 750, 800, 900])
    truth = rho * 100 // RHOW
    return _pack("แรงลอยตัว", 2,
                 f"วัตถุเนื้อเดียวความหนาแน่น {rho} กิโลกรัมต่อลูกบาศก์เมตร ลอยนิ่งอยู่ในน้ำ\n"
                 "ปริมาตรส่วนที่จมอยู่ใต้ผิวน้ำ คิดเป็นร้อยละเท่าใดของปริมาตรทั้งก้อน",
                 truth, [100 - truth, truth * 2, 100, RHOW * 100 // rho], want,
                 f"ลอยนิ่ง แรงลอยตัวเท่าน้ำหนัก · สัดส่วนที่จม = {rho}/{RHOW}",
                 {"rho": rho})


def q_pressure(rng, want):
    """ความดันเกจ P = rho g h ไม่ขึ้นกับรูปร่างภาชนะ"""
    h = rng.choice([2, 3, 4, 5, 6, 8])
    truth = RHOW * G * h // 1000
    return _pack("ของไหล", 1,
                 f"จุดหนึ่งอยู่ลึกจากผิวน้ำ {h} เมตร ความหนาแน่นน้ำ 1,000 กิโลกรัมต่อลูกบาศก์เมตร\n"
                 "ความดันเกจที่จุดนั้นมีค่ากี่กิโลปาสกาล (ใช้ g = 10)",
                 truth, [h * G, truth * 2, truth // 2, RHOW * h // 1000], want,
                 f"P = rho g h · ไม่ขึ้นกับรูปร่างภาชนะ · 1000 x 10 x {h}",
                 {"h": h})


def q_hydraulic(rng, want):
    """เครื่องอัดไฮดรอลิก ความดันเท่ากันสองฝั่ง F แปรตามพื้นที่"""
    a1 = rng.choice([2, 4, 5, 10])
    k = rng.choice([3, 4, 5, 6, 8, 10])
    a2, f1 = a1 * k, rng.choice([20, 30, 40, 50, 60])
    truth = f1 * k
    return _pack("ของไหล", 2,
                 f"เครื่องอัดไฮดรอลิกมีลูกสูบเล็กพื้นที่ {a1} ตารางเซนติเมตร\n"
                 f"และลูกสูบใหญ่พื้นที่ {a2} ตารางเซนติเมตร\n"
                 f"ถ้าออกแรงกดลูกสูบเล็ก {f1} นิวตัน จะยกน้ำหนักที่ลูกสูบใหญ่ได้กี่นิวตัน",
                 truth, [f1 // k if f1 % k == 0 else None, f1, f1 + k, truth * 2], want,
                 f"ความดันเท่ากันสองฝั่ง F2 = F1 x A2/A1 = {f1} x {k}",
                 {"a1": a1, "a2": a2, "f1": f1})


def q_continuity(rng, want):
    """สมการความต่อเนื่อง A1 v1 = A2 v2 — ท่อแคบลง น้ำไหลเร็วขึ้น"""
    k = rng.choice([2, 3, 4, 5, 6])
    a2 = rng.choice([2, 3, 4, 5])
    a1, v1 = a2 * k, rng.choice([2, 3, 4, 6])
    truth = v1 * k
    return _pack("แบร์นูลลี", 2,
                 f"น้ำไหลในท่อที่พื้นที่หน้าตัดลดจาก {a1} ตารางเซนติเมตร เหลือ {a2} ตารางเซนติเมตร\n"
                 f"ถ้าอัตราเร็วในท่อกว้างเท่ากับ {v1} เมตรต่อวินาที ในท่อแคบมีค่ากี่เมตรต่อวินาที",
                 truth, [v1 // k if v1 % k == 0 else None, v1, v1 + k, truth * 2], want,
                 f"A1 v1 = A2 v2 · พื้นที่ลด {k} เท่า อัตราเร็วเพิ่ม {k} เท่า",
                 {"a1": a1, "a2": a2, "v1": v1})


# ================================================================ ของแข็งและพลังงาน
def q_hooke(rng, want):
    """สปริง F = kx"""
    k = rng.choice([20, 25, 40, 50, 100, 200])
    x = rng.choice([2, 4, 5, 8, 10])
    truth = k * x // 100
    if truth < 1:
        return None
    return _pack("ของแข็ง", 1,
                 f"สปริงมีค่าคงตัว {k} นิวตันต่อเมตร ถูกดึงให้ยืดออกจากความยาวธรรมชาติ {x} เซนติเมตร\n"
                 "แรงที่ใช้ดึงมีค่ากี่นิวตัน",
                 truth, [k * x, truth * 2, truth * 10, k // x if k % x == 0 else None], want,
                 f"F = kx · เปลี่ยน {x} cm เป็น {x/100:g} m ก่อน",
                 {"k": k, "x": x})


def q_work(rng, want):
    """งานของแรงคงตัว W = F d cos(theta) มุม 60 องศาให้ค่า 1/2"""
    f_ = rng.choice([20, 40, 60, 80, 100])
    d = rng.choice([2, 3, 5, 6, 10])
    truth = f_ * d // 2
    return _pack("งานและพลังงาน", 2,
                 f"ออกแรง {f_} นิวตัน ทำมุม 60 องศากับแนวการเคลื่อนที่ ลากวัตถุไปได้ {d} เมตร\n"
                 "งานที่แรงนี้ทำมีค่ากี่จูล",
                 truth, [f_ * d, truth * 2 if truth * 2 != f_ * d else None,
                         f_ + d, f_ * d // 4], want,
                 f"W = F d cos60 = {f_} x {d} x 0.5",
                 {"f": f_, "d": d})


def q_power(rng, want):
    """กำลัง = งาน/เวลา · ยกของขึ้นตรง ๆ งานคือ mgh"""
    m = rng.choice([10, 20, 30, 50, 60])
    h = rng.choice([2, 3, 4, 5, 6])
    t = rng.choice([2, 3, 4, 5])
    if (m * G * h) % t:
        return None
    truth = m * G * h // t
    return _pack("งานและพลังงาน", 2,
                 f"ยกวัตถุมวล {m} กิโลกรัม ขึ้นในแนวดิ่งสูง {h} เมตร ด้วยอัตราเร็วคงตัว\n"
                 f"ใช้เวลา {t} วินาที กำลังเฉลี่ยที่ใช้มีค่ากี่วัตต์ (ใช้ g = 10)",
                 truth, [m * G * h, m * h // t if (m * h) % t == 0 else None,
                         truth * 2, m * G // t if (m * G) % t == 0 else None], want,
                 f"P = mgh/t = {m} x 10 x {h} / {t}",
                 {"m": m, "h": h, "t": t})


# ================================================================ คลื่นและเสียง
def q_wave(rng, want):
    """v = f lambda"""
    f_ = rng.choice([2, 4, 5, 8, 10, 20])
    lam = rng.choice([2, 3, 5, 6, 10])
    truth = f_ * lam
    return _pack("คลื่น", 1,
                 f"คลื่นขบวนหนึ่งมีความถี่ {f_} เฮิรตซ์ และความยาวคลื่น {lam} เมตร\n"
                 "อัตราเร็วของคลื่นมีค่ากี่เมตรต่อวินาที",
                 truth, [f_ + lam, truth * 2, f_ * lam // 2 if (f_ * lam) % 2 == 0 else None,
                         lam * lam], want,
                 f"v = f x lambda = {f_} x {lam}",
                 {"f": f_, "lam": lam})


def q_pipe(rng, want):
    """ท่อปลายปิดข้างหนึ่ง เสียงสะท้อนครั้งแรกเมื่อความยาวเท่ากับหนึ่งในสี่ของความยาวคลื่น"""
    L = rng.choice([10, 20, 25, 40, 50])
    v = 340
    if (v * 100) % (4 * L):
        return None
    truth = v * 100 // (4 * L)
    return _pack("เสียง", 3,
                 f"ท่อปลายปิดข้างหนึ่งยาว {L} เซนติเมตร เกิดการสั่นพ้องที่ความถี่ต่ำที่สุดค่าหนึ่ง\n"
                 "ถ้าอัตราเร็วเสียงในอากาศเท่ากับ 340 เมตรต่อวินาที ความถี่นั้นมีค่ากี่เฮิรตซ์",
                 truth, [truth * 2, truth // 2, v * 100 // (2 * L) if (v * 100) % (2 * L) == 0 else None,
                         v // L if v % L == 0 else None], want,
                 f"ท่อปลายปิด ความยาวคลื่นยาวสุด = 4L · f = v/(4L)",
                 {"L": L})


def q_beat(rng, want):
    """บีตส์ = ผลต่างความถี่"""
    f1 = rng.choice([256, 300, 320, 440, 500])
    d = rng.choice([2, 3, 4, 5, 6, 8])
    f2 = f1 + d
    return _pack("เสียง", 2,
                 f"ส้อมเสียงสองอันมีความถี่ {f1} และ {f2} เฮิรตซ์ ถูกเคาะพร้อมกัน\n"
                 "จะได้ยินเสียงดังค่อยสลับกันกี่ครั้งต่อวินาที",
                 d, [f1 + f2, (f1 + f2) // 2, d * 2, f1 // d if f1 % d == 0 else None], want,
                 f"ความถี่บีตส์ = ผลต่างความถี่ = {f2} - {f1}",
                 {"f1": f1, "f2": f2})


# ================================================================ แสงและเลนส์
def q_lens(rng, want):
    """เลนส์บาง 1/f = 1/s + 1/s' เลือกค่าที่ลงตัว"""
    for _ in range(200):
        f_ = rng.choice([10, 12, 15, 20, 30])
        s = rng.choice([15, 20, 24, 30, 40, 60])
        if s == f_:
            continue
        v = F(f_ * s, s - f_)
        if v.denominator != 1 or v <= 0 or v > 200:
            continue
        truth = int(v)
        return _pack("แสงและเลนส์", 3,
                     f"เลนส์นูนมีความยาวโฟกัส {f_} เซนติเมตร วางวัตถุห่างจากเลนส์ {s} เซนติเมตร\n"
                     "ภาพจริงเกิดขึ้นห่างจากเลนส์กี่เซนติเมตร",
                     truth, [s - f_, s + f_, f_ * s // (s + f_) if (f_ * s) % (s + f_) == 0 else None,
                             truth * 2], want,
                     f"1/f = 1/s + 1/s' · s' = fs/(s-f) = {f_}x{s}/{s - f_}",
                     {"f": f_, "s": s})
    return None


def q_mirror_mag(rng, want):
    """กำลังขยาย m = ระยะภาพ/ระยะวัตถุ ถามขนาดภาพ"""
    s = rng.choice([10, 15, 20, 25])
    k = rng.choice([2, 3, 4, 5])
    sp, h = s * k, rng.choice([2, 3, 4, 6])
    truth = h * k
    return _pack("แสงและเลนส์", 2,
                 f"วัตถุสูง {h} เซนติเมตร วางห่างเลนส์ {s} เซนติเมตร เกิดภาพห่างเลนส์ {sp} เซนติเมตร\n"
                 "ภาพที่ได้สูงกี่เซนติเมตร",
                 truth, [h, h + k, truth * 2, h * s // sp if (h * s) % sp == 0 else None], want,
                 f"กำลังขยาย = s'/s = {k} เท่า · ขนาดภาพ = {h} x {k}",
                 {"s": s, "sp": sp, "h": h})


# ================================================================ ไฟฟ้าสถิต
def q_coulomb(rng, want):
    """แรงคูลอมบ์แปรผกผันกับระยะกำลังสอง ถามเป็นอัตราส่วนเพื่อเลี่ยงเลขมหาศาล"""
    k = rng.choice([2, 3, 4, 5])
    f0 = rng.choice([36, 48, 60, 72, 100, 144])
    if f0 % (k * k):
        return None
    truth = f0 // (k * k)
    return _pack("แรงไฟฟ้า", 2,
                 f"ประจุสองตัวอยู่ห่างกันระยะหนึ่ง เกิดแรงกระทำต่อกัน {f0} นิวตัน\n"
                 f"ถ้าเพิ่มระยะห่างเป็น {k} เท่าของเดิม โดยประจุเท่าเดิม แรงจะเหลือกี่นิวตัน",
                 truth, [f0 // k if f0 % k == 0 else None, f0 * k, f0, truth * 2], want,
                 f"F แปรผกผันกับ r กำลังสอง · ระยะเพิ่ม {k} เท่า แรงลด {k*k} เท่า",
                 {"k": k, "f0": f0})


def q_efield(rng, want):
    """สนามไฟฟ้า F = qE"""
    q = rng.choice([2, 3, 4, 5, 6])
    E = rng.choice([10, 20, 50, 100, 200])
    truth = q * E
    return _pack("สนามไฟฟ้า", 1,
                 f"ประจุขนาด {q} คูลอมบ์ วางอยู่ในสนามไฟฟ้าสม่ำเสมอความเข้ม {E} นิวตันต่อคูลอมบ์\n"
                 "แรงที่กระทำต่อประจุมีค่ากี่นิวตัน",
                 truth, [E // q if E % q == 0 else None, q + E, truth * 2, E], want,
                 f"F = qE = {q} x {E}",
                 {"q": q, "E": E})


def q_cap(rng, want):
    """ตัวเก็บประจุต่อขนาน บวกกันตรง ๆ · ต่ออนุกรม ส่วนกลับบวกกัน (ตรงข้ามกับตัวต้านทาน)"""
    a, b = rng.sample([2, 3, 4, 6, 12], 2)
    ser = F(a * b, a + b)
    if ser.denominator != 1:
        return None
    if rng.random() < .5:
        truth, mode = a + b, "ขนาน"
        wrong = [int(ser), abs(a - b), (a + b) * 2, a * b]
    else:
        truth, mode = int(ser), "อนุกรม"
        wrong = [a + b, abs(a - b), a * b, truth * 2]
    return _pack("ตัวเก็บประจุ", 2,
                 f"ตัวเก็บประจุขนาด {a} และ {b} ไมโครฟารัด ต่อกันแบบ{mode}\n"
                 "ความจุรวมมีค่ากี่ไมโครฟารัด",
                 truth, wrong, want,
                 "ต่อขนานบวกกันตรง ๆ · ต่ออนุกรมส่วนกลับบวกกัน (กลับกันกับตัวต้านทาน)",
                 {"a": a, "b": b, "mode": mode})


def q_charge(rng, want):
    """Q = CV"""
    c = rng.choice([2, 3, 4, 5, 10])
    v = rng.choice([6, 9, 12, 20, 24])
    truth = c * v
    return _pack("ตัวเก็บประจุ", 1,
                 f"ตัวเก็บประจุขนาด {c} ไมโครฟารัด ต่อกับความต่างศักย์ {v} โวลต์\n"
                 "ประจุที่เก็บได้มีค่ากี่ไมโครคูลอมบ์",
                 truth, [c + v, v // c if v % c == 0 else None, truth * 2, truth // 2], want,
                 f"Q = CV = {c} x {v}",
                 {"c": c, "v": v})


# ================================================================ การเคลื่อนที่
def q_projectile(rng, want):
    """ยิงในแนวราบจากที่สูง เวลาตกขึ้นกับความสูงอย่างเดียว ไม่ขึ้นกับความเร็วต้น"""
    t = rng.choice([1, 2, 3, 4])
    h = G * t * t // 2
    u = rng.choice([5, 10, 15, 20, 25])
    truth = u * t
    return _pack("โพรเจกไทล์", 2,
                 f"ยิงวัตถุออกไปในแนวราบด้วยอัตราเร็ว {u} เมตรต่อวินาที จากที่สูง {h} เมตร\n"
                 "วัตถุตกถึงพื้นห่างจากจุดยิงในแนวราบกี่เมตร (ใช้ g = 10 ไม่คิดแรงต้านอากาศ)",
                 truth, [h, u + h, truth * 2, u * t // 2 if (u * t) % 2 == 0 else None], want,
                 f"แนวดิ่งหาเวลา t = {t} s ก่อน แล้วแนวราบ x = u t = {u} x {t}",
                 {"u": u, "h": h, "t": t})


def q_freefall(rng, want):
    """ตกอิสระ v = gt"""
    t = rng.choice([2, 3, 4, 5, 6])
    truth = G * t
    return _pack("โพรเจกไทล์", 1,
                 f"ปล่อยวัตถุตกอิสระจากหยุดนิ่ง หลังจากปล่อยไปแล้ว {t} วินาที\n"
                 "วัตถุมีอัตราเร็วกี่เมตรต่อวินาที (ใช้ g = 10 ไม่คิดแรงต้านอากาศ)",
                 truth, [G * t * t // 2, t * t, truth * 2, G], want,
                 f"v = gt = 10 x {t} · ระยะทางต่างหากที่ใช้ครึ่งหนึ่งของ g t กำลังสอง",
                 {"t": t})


def q_shm(rng, want):
    """คาบของสปริงแปรตามรากที่สองของมวล ถามเป็นอัตราส่วนจึงไม่ต้องใช้ค่า pi"""
    k = rng.choice([4, 9, 16, 25])
    r = int(k ** 0.5)
    t0 = rng.choice([2, 3, 4, 6])
    truth = t0 * r
    return _pack("ฮาร์มอนิก", 3,
                 f"มวลติดปลายสปริงสั่นด้วยคาบ {t0} วินาที ถ้าเปลี่ยนเป็นมวลที่หนักเป็น {k} เท่าของเดิม\n"
                 "โดยใช้สปริงอันเดิม คาบใหม่มีค่ากี่วินาที",
                 truth, [t0 * k, t0, t0 // r if t0 % r == 0 else None, truth * 2], want,
                 f"คาบแปรตามรากที่สองของมวล · มวล {k} เท่า คาบ {r} เท่า",
                 {"k": k, "t0": t0})


def q_photo(rng, want):
    """โฟโตอิเล็กทริก พลังงานจลน์สูงสุด = พลังงานโฟตอน ลบ ฟังก์ชันงาน"""
    w = rng.choice([2, 3, 4, 5])
    ke = rng.choice([1, 2, 3, 4])
    e = w + ke
    return _pack("โฟโตอิเล็กทริก", 2,
                 f"ฉายแสงที่มีพลังงานโฟตอน {e} อิเล็กตรอนโวลต์ ลงบนโลหะที่มีฟังก์ชันงาน {w} อิเล็กตรอนโวลต์\n"
                 "อิเล็กตรอนที่หลุดออกมามีพลังงานจลน์สูงสุดกี่อิเล็กตรอนโวลต์",
                 ke, [e + w, e, w, ke * 2], want,
                 f"KE สูงสุด = พลังงานโฟตอน - ฟังก์ชันงาน = {e} - {w}",
                 {"w": w, "e": e})


GENS = [q_buoy, q_pressure, q_hydraulic, q_continuity, q_hooke, q_work, q_power,
        q_wave, q_pipe, q_beat, q_lens, q_mirror_mag, q_coulomb, q_efield,
        q_cap, q_charge, q_projectile, q_freefall, q_shm, q_photo]


def build(add, part, rng):
    """เติมโจทย์คำนวณเข้าคลัง — เรียกจาก gen.py"""
    want = 0
    for g in GENS:
        for _ in range(40):
            r = g(rng, want)
            if r:
                add(part, r["arche"], r["stem"], r["choices"], r["ansIdx"],
                    lvl=r["lvl"], why=r["why"])
                want = (want + 2) % 5
                break


# ================================================================ ตรวจตัวเอง
if __name__ == "__main__":
    import collections
    bad, n = [], 0
    pos = collections.Counter()
    arches = collections.Counter()

    # คำนวณคำตอบซ้ำอีกทางหนึ่งจากพารามิเตอร์ ไม่ใช้ค่าที่ตัวสร้างคืนมา
    CHECK = {
        "q_buoy": lambda p: p["rho"] * 100 // RHOW,
        "q_pressure": lambda p: p["h"] * 10,
        "q_hydraulic": lambda p: p["f1"] * p["a2"] // p["a1"],
        "q_continuity": lambda p: p["v1"] * p["a1"] // p["a2"],
        "q_hooke": lambda p: p["k"] * p["x"] // 100,
        "q_work": lambda p: p["f"] * p["d"] // 2,
        "q_power": lambda p: p["m"] * G * p["h"] // p["t"],
        "q_wave": lambda p: p["f"] * p["lam"],
        "q_pipe": lambda p: 34000 // (4 * p["L"]),
        "q_beat": lambda p: p["f2"] - p["f1"],
        "q_lens": lambda p: p["f"] * p["s"] // (p["s"] - p["f"]),
        "q_mirror_mag": lambda p: p["h"] * p["sp"] // p["s"],
        "q_coulomb": lambda p: p["f0"] // (p["k"] ** 2),
        "q_efield": lambda p: p["q"] * p["E"],
        "q_cap": lambda p: (p["a"] + p["b"]) if p["mode"] == "ขนาน"
                           else p["a"] * p["b"] // (p["a"] + p["b"]),
        "q_charge": lambda p: p["c"] * p["v"],
        "q_projectile": lambda p: p["u"] * p["t"],
        "q_freefall": lambda p: G * p["t"],
        "q_shm": lambda p: p["t0"] * int(p["k"] ** 0.5),
        "q_photo": lambda p: p["e"] - p["w"],
    }

    for s in range(400):
        rng = random.Random(s)
        for w in range(5):
            for g in GENS:
                r = g(rng, w)
                if not r:
                    continue
                n += 1
                pos[r["ansIdx"]] += 1
                arches[r["arche"]] += 1
                ch = r["choices"]
                if len(set(ch)) != 5:
                    bad.append(f"{g.__name__} s={s}: ตัวเลือกซ้ำ {ch}")
                if r["ansIdx"] != w:
                    bad.append(f"{g.__name__} s={s}: บังคับตำแหน่งเฉลยไม่ได้")
                want = CHECK[g.__name__](r["params"])
                if F(ch[r["ansIdx"]]) != F(want):
                    bad.append(f"{g.__name__} s={s}: เฉลย {ch[r['ansIdx']]} "
                               f"ไม่ตรงกับที่คำนวณซ้ำ {want}")
                if not r["why"] or len(r["why"]) > 90:
                    bad.append(f"{g.__name__}: บรรทัดแนวคิดยาวเกินหรือหายไป")

    for k in range(5):
        if pos.get(k, 0) == 0:
            bad.append(f"ไม่มีข้อไหนเฉลยเป็นตัวเลือกที่ {k + 1} เลย")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:12]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ · {len(arches)} หัวข้อ")
    print("หัวข้อ:", ", ".join(sorted(arches)))

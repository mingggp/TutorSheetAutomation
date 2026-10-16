#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""แนวใหม่ของวีคฟิสิกส์ ถอดจาก reference/tpat3/FEST2026_TPAT3.pdf ตอนที่ 3 (16 ต.ค. 69)

ติวเตอร์บอกว่าไฟล์นี้ "ยากกว่าความเป็นจริงนิดหน่อย แต่เอามาเป็นแนวได้ ห้ามก๊อป"
จึงเอาแค่กลไกของแนว แล้วลดความยากลงมาที่ระดับข้อสอบจริง ตัวเลข ถ้อยคำ และรูปแต่งใหม่ทั้งหมด

  เครื่องแอดวูด        รอกตายตัวคล้องมวลสองก้อน ปล่อยจากหยุดนิ่ง (FEST ข้อ 36)
  แท่งไม้เข้าพื้นฝืด    แรงเสียดทานคิดเฉพาะส่วนที่อยู่บนพื้นฝืด (FEST ข้อ 33)
  แท่งไม้ซ้อนเหลื่อม    ติดกาวเป็นก้อนเดียว จุดศูนย์กลางมวลเลยขอบโต๊ะเมื่อไรก็หล่น (FEST ข้อ 45)
  จัดวงจรตัวต้านทาน     ต่อสามตัวแบบใดก็ได้ ให้กำลังน้อยที่สุดหรือมากที่สุด (FEST ข้อ 37)
  ขว้างของจากกระดาน     โมเมนตัมคงตัว แต่พลังงานจลน์แบ่งกันตามส่วนกลับของมวล (FEST ข้อ 34)
  เลือกวัสดุถังแก๊ส     ความดันสัมบูรณ์แปรตามอุณหภูมิเคลวิน + การกัดกร่อนเพิ่มเป็นเท่าตัว (FEST ข้อ 42)

แยกไฟล์และใช้ตัวสุ่มของตัวเอง เพื่อไม่ให้ลำดับการสุ่มของ physgen เปลี่ยน
พาร์ทเชิงวิทย์ของวีคฟิสิกส์ชุดที่ 2 ซึ่งติวเตอร์บอกว่าดีแล้ว จึงได้ข้อเดิมทุกข้อ

ทุกข้อพิสูจน์ด้วยโค้ด ตัวตรวจท้ายไฟล์คำนวณซ้ำด้วยวิธีที่สอง (กติกาข้อ 1)
"""
import itertools
import math
import random
from fractions import Fraction as Fr

import draw as D

NL = chr(10)
G = 10


def _fmt(x):
    if isinstance(x, Fr):
        return str(x.numerator) if x.denominator == 1 else f"{float(x):g}"
    return str(x)


def _pack(arche, lvl, stem, truth, wrong, want, why, params, unit=""):
    out = [truth]
    for w in wrong:
        if w is None or w in out:
            continue
        if isinstance(w, (int, Fr)) and w <= 0:
            continue
        if isinstance(w, Fr) and w.denominator not in (1, 2, 4, 5, 10):
            continue
        out.append(w)
    if len(out) < 5:
        return None
    out = out[:5]
    rest = [o for o in out if o != truth]
    out = rest[:want] + [truth] + rest[want:]
    ch = [x if isinstance(x, str) else _fmt(x) + (" " + unit if unit else "") for x in out]
    if len(set(ch)) < 5:
        return None
    return {"arche": arche, "lvl": lvl, "stem": stem, "choices": ch,
            "ansIdx": out.index(truth), "why": why, "params": params}


# ---------------------------------------------------------------- เครื่องแอดวูด
def q_atwood(rng, want):
    """A หนักกว่า B ปล่อยจากหยุดนิ่ง A สูงจากพื้น h ถามอัตราเร็วตอน A แตะพื้น หรือความเร่ง หรือแรงตึง

    a = (mA - mB) g / (mA + mB) · v² = 2 a h · T = 2 mA mB g / (mA + mB)
    ตัวลวงหลักคือลืมว่าก้อน B ก็ต้องถูกเร่งไปด้วย (ใช้ g ตรง ๆ หรือหารด้วย mA อย่างเดียว)
    """
    for _ in range(400):
        mA, mB = rng.randint(2, 9), rng.randint(1, 8)
        if mA <= mB:
            continue
        a = Fr((mA - mB) * G, mA + mB)
        ask = rng.choice(["v", "v", "a", "T"])
        if ask == "v":
            h = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
            v2 = 2 * a * h
            v = math.isqrt(int(v2)) if v2.denominator == 1 else -1
            if v < 1 or v * v != v2:
                continue
            truth = Fr(v)
            fall = 2 * G * h
            wrong = [Fr(math.isqrt(fall)) if math.isqrt(fall) ** 2 == fall else None,
                     truth * 2, truth + 1, truth - 1, Fr(v * v, 2), truth + 2]
            q = (f"ก้อน A อยู่สูงจากพื้น h = {h} m ขณะที่ก้อน B วางอยู่บนพื้น"
                 + NL + "ปล่อยระบบจากหยุดนิ่ง ก้อน A จะกระทบพื้นด้วยอัตราเร็วเท่าใด")
            unit, params = "m/s", {"mA": mA, "mB": mB, "h": h, "ask": ask, "truth": truth}
        elif ask == "a":
            if a.denominator not in (1, 2):
                continue
            truth = a
            wrong = [Fr(G), Fr((mA - mB) * G, mA), Fr((mA + mB) * G, mA), a * 2, Fr(mB * G, mA + mB)]
            q = "ปล่อยระบบจากหยุดนิ่ง ความเร่งของก้อน A มีขนาดเท่าใด"
            unit, params = "m/s²", {"mA": mA, "mB": mB, "ask": ask, "truth": truth}
        else:
            T = Fr(2 * mA * mB * G, mA + mB)
            if T.denominator != 1:
                continue
            truth = T
            wrong = [Fr(mA * G), Fr(mB * G), Fr((mA - mB) * G), Fr((mA + mB) * G, 2), T + 5]
            q = "ปล่อยระบบจากหยุดนิ่ง แรงตึงในเส้นเชือกมีขนาดเท่าใด"
            unit, params = "N", {"mA": mA, "mB": mB, "ask": ask, "truth": truth}
        stem = (f"ก้อน A มวล {mA} kg และก้อน B มวล {mB} kg ผูกไว้คนละปลายของเชือกเบาที่คล้องผ่านรอกลื่นดังรูป"
                + NL + q + f"  (ให้ g = {G} m/s²)")
        r = _pack("เครื่องแอดวูด", 3 if ask == "v" else 2, stem, truth, wrong, want,
                  "ทั้งสองก้อนเร่งไปด้วยกัน แรงลัพธ์ (mA - mB)g ต้องเร่งมวลรวม mA + mB",
                  params, unit=unit)
        if r:
            r["draw"] = lambda t, h=(ask == "v"): D.atwood(f"m2atw{t}", h_label="h" if h else None)
            return r
    return None


# ---------------------------------------------------------------- แท่งไม้เข้าพื้นฝืด
def q_rough(rng, want):
    """แท่งไม้สม่ำเสมอไถลจากพื้นลื่นเข้าพื้นฝืด ขณะที่เข้าไปได้ x จาก L
    แรงเสียดทาน = μ (m x/L) g จึงหน่วง a = μ g x / L ไม่ใช่ μ g
    """
    for _ in range(300):
        L = rng.choice([2, 4, 5, 6, 8, 10])
        x = rng.randint(1, L - 1)
        mu = Fr(rng.choice([1, 2, 3, 4, 5]), 10)
        m = rng.choice([2, 4, 5, 10, 20])
        a = mu * G * Fr(x, L)
        if a.denominator not in (1, 2, 4, 5, 10):
            continue
        ask = rng.choice(["a", "f"])
        if ask == "a":
            truth = a
            wrong = [mu * G, mu * G * Fr(L - x, L), a * 2, mu * G * Fr(x, L + x), a + Fr(1, 2)]
            q = "ขณะนั้นแท่งไม้มีความหน่วงเท่าใด"
            unit = "m/s²"
        else:
            truth = a * m
            wrong = [mu * m * G, mu * m * G * Fr(L - x, L), truth * 2, truth + 2, mu * x * G]
            q = "ขณะนั้นแรงเสียดทานที่กระทำต่อแท่งไม้มีขนาดเท่าใด"
            unit = "N"
        stem = (f"แท่งไม้สม่ำเสมอมวล {m} kg ยาว {L} m ไถลบนพื้นลื่นเข้าไปในพื้นฝืด "
                f"ที่มีสัมประสิทธิ์ความเสียดทานจลน์ {_fmt(mu)}" + NL +
                f"เมื่อแท่งไม้เข้าไปอยู่บนพื้นฝืดได้ {x} m ดังรูป {q}  (ให้ g = {G} m/s²)")
        r = _pack("แท่งไม้เข้าพื้นฝืด", 3, stem, truth, wrong, want,
                  "แรงเสียดทานคิดเฉพาะน้ำหนักส่วนที่อยู่บนพื้นฝืด คือ x/L ของทั้งแท่ง",
                  {"L": L, "x": x, "mu": mu, "m": m, "ask": ask, "truth": truth}, unit=unit)
        if r:
            r["draw"] = lambda t, L=L, x=x: D.roughstrip(f"{L} m", f"{x} m", f"m2rgh{t}", frac=x / L)
            return r
    return None


# ---------------------------------------------------------------- แท่งไม้ซ้อนเหลื่อม
def _stack_com(n, a, d, L):
    """จุดศูนย์กลางมวลของแท่งไม้ n แท่ง วัดจากขอบโต๊ะ (บวก = เลยขอบออกไป)"""
    return sum(a + k * d - Fr(L, 2) for k in range(n)) / n


def q_stack(rng, want):
    """แท่งไม้ยาว L เท่ากันซ้อนเหลื่อม แท่งล่างยื่นเลยขอบโต๊ะ a แท่งถัดไปยื่นเลยแท่งล่างอีก d
    ติดกาวกันแน่น จึงเป็นก้อนเดียว หล่นเมื่อจุดศูนย์กลางมวลรวมเลยขอบโต๊ะ
    a ไม่เท่ากับ d เพื่อไม่ให้คำตอบออกมาเป็น L/d ตายตัว
    ตัวลวงหลัก: คิดว่าหล่นเมื่อจุดศูนย์กลางของแท่งบนสุดเลยขอบโต๊ะ (ได้จำนวนน้อยเกิน)
    """
    for _ in range(300):
        d = rng.choice([2, 3, 4, 5])
        k = rng.choice([6, 7, 8, 9, 10, 12])
        L = k * d
        a = Fr(d * rng.choice([1, 3, 4, 5]), 2)
        if a == d or 2 * a >= L:
            continue
        n = next(m for m in range(1, 80) if _stack_com(m, a, d, L) > 0)
        if not 3 <= n <= 12:
            continue
        balanced = _stack_com(n - 1, a, d, L) == 0
        top = next(m for m in range(1, 80) if a + (m - 1) * d - Fr(L, 2) > 0)
        truth = n
        wrong = [top, n - 1, n + 1, k, n + 2, top - 1]
        stem = (f"แท่งไม้สม่ำเสมอยาว L = {L} cm มวลเท่ากันหลายแท่ง วางซ้อนกันบนโต๊ะ "
                f"แท่งล่างสุดยื่นเลยขอบโต๊ะ a = {_fmt(a)} cm" + NL +
                f"แท่งถัดขึ้นไปแต่ละแท่งยื่นเลยปลายแท่งที่อยู่ข้างล่างอีก d = {d} cm ดังรูป "
                "และติดกาวทุกแท่งให้เป็นก้อนเดียวกัน" + NL +
                "ต้องวางซ้อนอย่างน้อยกี่แท่ง ทั้งก้อนจึงจะพลิกหล่นจากโต๊ะ")
        r = _pack("แท่งไม้ซ้อนเหลื่อม", 3, stem, truth, wrong, want,
                  "หล่นเมื่อจุดศูนย์กลางมวลรวม (ไม่ใช่ของแท่งบนสุด) เลยขอบโต๊ะ"
                  + (" · พอดีขอบยังไม่หล่น" if balanced else ""),
                  {"L": L, "a": a, "d": d, "n": n}, unit="แท่ง")
        if r:
            r["draw"] = lambda t, k=k, f=float(a / d): D.plankstack(f"m2stk{t}", k=k, first=f)
            return r
    return None


# ---------------------------------------------------------------- จัดวงจรตัวต้านทาน
def _nets(rs):
    """ความต้านทานรวมของทุกวิธีต่อตัวต้านทานสามตัว โดยต้องใช้ครบทุกตัว — 8 แบบ"""
    par = lambda *x: 1 / sum(Fr(1, v) for v in x)
    a, b, c = rs
    out = {"อนุกรมทั้งหมด": Fr(a + b + c), "ขนานทั้งหมด": par(a, b, c)}
    for i in range(3):
        one = rs[i]
        p, q = [rs[j] for j in range(3) if j != i]
        out[f"{p}+{q} ขนานกับ {one}"] = par(p + q, one)
        out[f"{p}∥{q} อนุกรมกับ {one}"] = par(p, q) + one
    return out


def q_resnet(rng, want):
    """ต่อตัวต้านทานสามตัวกับแบตเตอรี่แบบใดก็ได้ (ใช้ครบทุกตัว) ไล่ครบ 8 แบบ

    min / max  น้อยสุดเมื่ออนุกรมทั้งหมด มากสุดเมื่อขนานทั้งหมด — ตัวลวงคือค่าของแบบผสม
    not        ข้อใดเป็นค่าที่ต่อแบบใดก็ไม่ได้ — ต้องไล่จริงทุกแบบ
               เฉลยคือกำลังที่ได้เมื่อแอบใช้แค่สองตัว ซึ่งขัดเงื่อนไข "ใช้ครบสามตัว"
    """
    for _ in range(600):
        rs = sorted(rng.sample([2, 3, 4, 5, 6, 8, 10, 12, 15, 20], 3))
        V = rng.choice([6, 10, 12, 20, 24, 30])
        nets = _nets(rs)
        P = {k: Fr(V * V) / r for k, r in nets.items()}
        ok = sorted({p for p in P.values() if p.denominator == 1})
        ask = rng.choice(["min", "max", "not", "not"])
        if ask == "not":
            par = lambda x, y: Fr(x * y, x + y)
            two = {Fr(V * V) / R for x, y in itertools.combinations(rs, 2) for R in (Fr(x + y), par(x, y))}
            two |= {Fr(V * V, x) for x in rs}
            cand = sorted(p for p in two if p.denominator == 1 and p not in P.values())
            if not cand or len(ok) < 4:
                continue
            truth = rng.choice(cand)
            wrong = rng.sample(ok, len(ok))
            q = "ค่าใดต่อไปนี้ไม่สามารถเป็นกำลังไฟฟ้าที่วงจรใช้ได้"
            why = "ไล่ครบ 8 แบบ (อนุกรม ขนาน และแบบผสม) ค่าที่เหลือได้จากการใช้ไม่ครบสามตัว"
        else:
            truth = min(P.values()) if ask == "min" else max(P.values())
            if truth.denominator != 1:
                continue
            others = [p for p in ok if p != truth]
            if len(others) < 3:
                continue
            wrong = others + [truth * 2, truth + 10]
            q = f"กำลังไฟฟ้าที่วงจรใช้มีค่า{'น้อยที่สุด' if ask == 'min' else 'มากที่สุด'}เท่าใด"
            why = "P = V²/R รวม · อนุกรมทั้งหมดได้ R มากสุด กำลังน้อยสุด · ขนานทั้งหมดกลับกัน"
        stem = (f"มีแบตเตอรี่ {V} V และตัวต้านทาน {rs[0]} โอห์ม {rs[1]} โอห์ม และ {rs[2]} โอห์ม "
                "อย่างละหนึ่งตัว นำมาต่อเป็นวงจรแบบใดก็ได้" + NL +
                "โดยต้องใช้ตัวต้านทานครบทั้งสามตัวและไม่ลัดวงจร " + q)
        r = _pack("จัดวงจรตัวต้านทาน", 3 if ask == "not" else 2, stem, truth, wrong, want, why,
                  {"rs": rs, "V": V, "ask": ask, "truth": truth}, unit="W")
        if r:
            return r
    return None


# ---------------------------------------------------------------- ขว้างของจากกระดาน
def q_recoil(rng, want):
    """คนยืนบนกระดานบนพื้นลื่น ขว้างลูกบอลออกไปแนวระดับ
    โมเมนตัมรวมเป็นศูนย์ ความเร็วแปรผกผันกับมวล พลังงานจลน์จึงแปรผกผันกับมวลด้วย
      V  ถามอัตราเร็วถอยหลัง (ระดับ 2)
      K  ให้อัตราเร็วลูกบอล ถามพลังงานจลน์ของคนกับกระดาน
      R  ให้พลังงานจลน์ลูกบอล ถามพลังงานจลน์ของคนกับกระดาน — ใช้สัดส่วนมวลได้ทันที
    """
    for _ in range(300):
        m = Fr(rng.choice([1, 2, 4, 5, 10]), rng.choice([1, 2, 10]))
        M = rng.choice([40, 50, 60, 80, 100])
        v = rng.choice([5, 8, 10, 12, 15, 20, 25])
        V = m * v / M
        kb = m * v * v / 2
        kp = M * V * V / 2
        ask = rng.choice(["V", "K", "R", "R"])
        throw = f"ออกไปในแนวระดับด้วยอัตราเร็ว {v} m/s"
        if ask == "V":
            truth = V
            wrong = [Fr(v), V * 2, Fr(v, 2), m * v, V * 10]
            q = "หลังขว้าง คนกับกระดานเคลื่อนที่ถอยหลังด้วยอัตราเร็วเท่าใด"
            unit = "m/s"
            why = "โมเมนตัมรวมเป็นศูนย์ mv = MV ฝั่งที่มวลมากกว่าถอยช้ากว่า"
        else:
            if kb.denominator != 1:
                continue
            truth = kp
            wrong = [kb, kb / 2, kb - kp, kp * 2, kp * 10, Fr(kb * M, m) if kb * M / m < 10 ** 4 else None]
            q = "หลังขว้าง คนกับกระดานมีพลังงานจลน์เท่าใด"
            unit = "J"
            why = "โมเมนตัมเท่ากัน พลังงานจลน์ p²/2m จึงแบ่งตามส่วนกลับของมวล"
            if ask == "R":
                throw = f"ออกไปในแนวระดับ ลูกบอลได้พลังงานจลน์ {_fmt(kb)} J"
        if truth.denominator not in (1, 2, 4, 5, 10) or truth <= 0:
            continue
        stem = (f"คนกับกระดานมีมวลรวม {M} kg อยู่นิ่งบนพื้นน้ำแข็งที่ลื่นมาก" + NL +
                f"คนขว้างลูกบอลมวล {_fmt(m)} kg " + throw + NL + q)
        r = _pack("ขว้างของจากกระดาน", 2 if ask == "V" else 3, stem, truth, wrong, want, why,
                  {"m": m, "M": M, "v": v, "ask": ask, "truth": truth}, unit=unit)
        if r:
            return r
    return None


# ---------------------------------------------------------------- เลือกวัสดุถังแก๊ส
def q_material(rng, want):
    """ถังปิดบรรจุแก๊สที่อุณหภูมิห้อง แล้วร้อนขึ้นเมื่อเครื่องจักรทำงาน
    ความดันสัมบูรณ์แปรตามอุณหภูมิเคลวิน (ความดันเกจ = สัมบูรณ์ - 1 atm)
    การกัดกร่อนเพิ่มเป็นสองเท่าทุก ๆ step องศา — เลือกวัสดุที่ผ่านทั้งสองเงื่อนไข

    วัสดุแต่ละตัวจัดบทบาทไว้ก่อน ไม่สุ่มลอย ๆ เพื่อให้กับดักทุกอันมีผลจริง
      ok      ผ่านทั้งสองเงื่อนไข
      gauge   ผ่านถ้าคิดผิดว่าความดันเกจแปรตามเคลวิน (ได้ค่าต่ำกว่าจริง)
      corr    ผ่านถ้าลืมว่าการกัดกร่อนเพิ่มเป็นสองเท่าตามอุณหภูมิ
      bad     ไม่ผ่านแม้คิดผิด
    """
    for _ in range(600):
        T1 = rng.choice([177, 227, 327, 427])
        steps = [s for s in (50, 75, 100, 150, 200) if (T1 - 27) % s == 0 and 2 <= (T1 - 27) // s <= 4]
        step = rng.choice(steps)
        k = (T1 - 27) // step
        mult = 2 ** k
        ratio = Fr(T1 + 273, 300)
        pa0 = rng.choice([p for p in range(4, 16) if (p * ratio).denominator == 1])
        g0 = pa0 - 1
        g1 = pa0 * ratio - 1                     # ความดันเกจจริงตอนร้อน
        g1w = g0 * ratio                         # คิดผิดด้วยความดันเกจ
        lim = Fr(rng.choice([4, 6, 8, 12, 16]), 10)
        cap = lim / mult                         # อัตรากัดกร่อนที่ 27 °C สูงสุดที่ยังผ่าน
        lo = [Fr(i, 100) for i in range(1, 100) if Fr(i, 100) <= cap]
        hi = [Fr(i, 100) for i in range(1, 100) if cap < Fr(i, 100) <= lim]
        if len(lo) < 2 or len(hi) < 2:
            continue
        half = lambda a, b: [Fr(i, 2) for i in range(math.ceil(2 * a), math.floor(2 * b) + 1)]
        p_ok = half(g1, g1 + 5)
        p_trap = [p for p in half(g1w, g1) if p < g1]
        p_low = half(max(1, g0 - 2), g1w - Fr(1, 2))
        if not p_trap or not p_low:
            continue
        roles = ["ok", "gauge", "corr", rng.choice(["ok", "bad"])]
        rng.shuffle(roles)
        mats = []
        for lab, role in zip("ABCD", roles):
            if role == "ok":
                mats.append((lab, rng.choice(lo), rng.choice(p_ok)))
            elif role == "gauge":
                mats.append((lab, rng.choice(lo), rng.choice(p_trap)))
            elif role == "corr":
                mats.append((lab, rng.choice(hi), rng.choice(p_ok)))
            else:
                mats.append((lab, rng.choice(hi + lo), rng.choice(p_low)))

        def pick(need, m):
            return [lab for lab, r_, p_ in mats if r_ * m <= lim and p_ >= need]
        truth_set = pick(g1, mult)
        alt_g = pick(g1w, mult)                  # คิดสัดส่วนด้วยความดันเกจ
        alt_c = pick(g1, 1)                      # ลืมการกัดกร่อนเพิ่มตามอุณหภูมิ
        alt_b = pick(g1w, 1)                     # พลาดทั้งสองอย่าง
        alt_a = pick(g1 + 1, mult)               # ลืมลบความดันบรรยากาศกลับเป็นความดันเกจ
        if not truth_set or len({tuple(x) for x in (truth_set, alt_g, alt_c, alt_b)}) < 4:
            continue
        fmt = lambda s: (", ".join(s[:-1]) + " และ " + s[-1] if len(s) > 1 else s[0]) if s else "ไม่มีวัสดุใดใช้ได้"
        truth = fmt(truth_set)
        wrong = [fmt(alt_g), fmt(alt_c), fmt(alt_b), fmt(alt_a)]
        combos = [fmt(list(c)) for r in (1, 2, 3) for c in itertools.combinations("ABCD", r)]
        rng.shuffle(combos)
        wrong += combos
        stem = ("ถังโลหะปิดสนิทบรรจุแก๊สที่อุณหภูมิห้อง 27 °C อ่านความดันเกจได้ "
                f"{g0} atm เมื่อเครื่องจักรทำงานเต็มที่ แก๊สในถังร้อนขึ้นถึง {T1} °C" + NL +
                f"วัสดุทุกชนิดมีอัตราการกัดกร่อนเพิ่มเป็นสองเท่าทุก ๆ {step} °C ที่อุณหภูมิสูงขึ้น" + NL +
                f"ข้อกำหนด ขณะเครื่องทำงานเต็มที่ อัตราการกัดกร่อนต้องไม่เกิน {_fmt(lim)} มม./ปี "
                "และถังต้องรับความดันเกจของแก๊สได้" + NL +
                "วัสดุใดในตารางใช้สร้างถังได้  (ให้ความดันบรรยากาศ 1 atm และ 0 °C = 273 K)")
        r = _pack("เลือกวัสดุถังแก๊ส", 3, stem, truth, wrong, want,
                  "ความดันสัมบูรณ์ (เกจ + 1) แปรตามเคลวิน ค่อยลบ 1 กลับ · กัดกร่อนคูณ 2 ทุกช่วงอุณหภูมิ",
                  {"T1": T1, "step": step, "pa0": pa0, "lim": lim, "mats": mats,
                   "truth_set": truth_set})
        if r:
            hf = lambda p: str(p.numerator) if p.denominator == 1 else f"{float(p):.1f}"
            rows = [["วัสดุ", "อัตรากัดกร่อนที่ 27 °C (มม./ปี)", "ความดันเกจสูงสุดที่รับได้ (atm)"]]
            rows += [[lab, f"{float(r_):.2f}", hf(p_)] for lab, r_, p_ in mats]
            r["draw"] = lambda t, rows=rows: D.table(rows, f"m2mat{t}")
            return r
    return None


# วีคฟิสิกส์แบ่งพาร์ทเป็นเชิงกล (3) กับเชิงวิทย์ (4) ต่างจาก FEST ที่รวมเป็นตอนเดียว
# วงจรไฟฟ้าและแก๊สร้อนจึงไปอยู่พาร์ทที่ 4 คู่กับค่าไฟฟ้าในบ้านและกราฟการเปลี่ยนสถานะ
GENS3 = [q_atwood, q_rough, q_stack, q_recoil]
GENS4 = [q_resnet, q_material]
GENS = GENS3 + GENS4


def build(add, P3, P4, rng, per=3):
    """เติมแนวใหม่เข้าคลัง แนวละ per ข้อ — เรียกจาก gen.py เป็นตัวสุดท้าย"""
    want, tag = 0, 0
    for g in GENS:
        part = P3 if g in GENS3 else P4
        made, sig = 0, set()
        for _ in range(per * 40):
            r = g(rng, want)
            tag += 1
            if not r:
                continue
            key = r["stem"] + "|".join(sorted(r["choices"]))   # ข้อเดียวกันที่แค่สลับตัวเลือกก็นับว่าซ้ำ
            if key in sig:
                continue
            sig.add(key)
            img = r["draw"](tag) if r.get("draw") else None
            add(part, r["arche"], r["stem"], r["choices"], r["ansIdx"],
                img=img, lvl=r["lvl"], why=r["why"])
            want = (want + 2) % 5
            made += 1
            if made >= per:
                break


if __name__ == "__main__":
    import collections
    bad, n = [], 0
    pos, arch = collections.Counter(), collections.Counter()

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    for s in range(400):
        rng = random.Random(s)
        for g in GENS:
            w = s % 5
            r = g(rng, w)
            if not r:
                continue
            n += 1
            nm = g.__name__
            arch[r["arche"]] += 1
            pos[r["ansIdx"]] += 1
            p = r["params"]
            ans = r["choices"][r["ansIdx"]]
            ck(len(set(r["choices"])) == 5, f"{nm} s={s}: ตัวเลือกซ้ำ")
            ck(r["ansIdx"] == w, f"{nm} s={s}: ตำแหน่งเฉลยไม่ตรง")
            ck(len(r["why"]) <= 90, f"{nm} s={s}: บรรทัดแนวคิดยาวเกิน")
            if nm == "q_atwood":
                mA, mB = p["mA"], p["mB"]
                if p["ask"] == "v":
                    # พลังงาน: (mA - mB) g h = ½ (mA + mB) v²
                    v = math.sqrt(2 * (mA - mB) * G * p["h"] / (mA + mB))
                    ck(abs(v - float(p["truth"])) < 1e-9, f"atwood s={s}: อัตราเร็วไม่ตรงกับพลังงาน")
                elif p["ask"] == "a":
                    # แยกวัตถุ: mA a = mA g - T , mB a = T - mB g
                    a = (mA - mB) * G / (mA + mB)
                    T = mB * (a + G)
                    ck(abs(mA * a - (mA * G - T)) < 1e-9 and abs(a - float(p["truth"])) < 1e-9,
                       f"atwood s={s}: ความเร่งไม่ตรง")
                else:
                    a = (mA - mB) * G / (mA + mB)
                    ck(abs(mB * (a + G) - float(p["truth"])) < 1e-9, f"atwood s={s}: แรงตึงไม่ตรง")
            elif nm == "q_rough":
                # แบ่งแท่งเป็นชิ้นเล็ก ๆ แล้วรวมแรงเสียดทานเฉพาะชิ้นที่อยู่บนพื้นฝืด
                N = p["L"] * 100      # ให้ x/L ลงตัวกับจำนวนชิ้นเสมอ
                on = sum(1 for i in range(N) if (i + .5) / N * p["L"] > p["L"] - p["x"])
                f = float(p["mu"]) * p["m"] * G * on / N
                exp = f / p["m"] if p["ask"] == "a" else f
                ck(abs(exp - float(p["truth"])) < 1e-6, f"rough s={s}: แรงเสียดทานไม่ตรง")
            elif nm == "q_stack":
                # วัดจากปลายซ้ายของแท่งล่างสุด ขอบโต๊ะอยู่ที่ L - a · หาแท่งแรกที่ทอร์กรอบขอบโต๊ะพาหล่น
                L, a, d = p["L"], float(p["a"]), p["d"]
                edge = L - a
                for m in range(1, 80):
                    torque = sum((k * d + L / 2) - edge for k in range(m))
                    if torque > 1e-9:
                        break
                ck(m == p["n"] and ans == f"{m} แท่ง", f"stack s={s}: จำนวนแท่งไม่ตรง")
            elif nm == "q_resnet":
                # ไล่ทุกต้นไม้ของการต่ออนุกรม/ขนานแบบที่ใช้ครบสามตัว
                a, b, c = p["rs"]
                par = lambda x, y: x * y / (x + y)
                Rs = []
                for x, y, z in itertools.permutations((a, b, c)):
                    for op1 in ("s", "p"):
                        for op2 in ("s", "p"):
                            r1 = x + y if op1 == "s" else par(x, y)
                            Rs.append(r1 + z if op2 == "s" else par(r1, z))
                Ps = [p["V"] ** 2 / R for R in Rs]
                hit = lambda x: any(math.isclose(x, q_, rel_tol=1e-9) for q_ in Ps)
                if p["ask"] == "not":
                    vals = [float(c_.split()[0]) for c_ in r["choices"]]
                    ck(not hit(float(p["truth"])), f"resnet s={s}: เฉลยต่อได้จริง")
                    ck(sum(hit(x) for x in vals) == 4, f"resnet s={s}: ตัวลวงต่อไม่ได้")
                else:
                    exp = min(Ps) if p["ask"] == "min" else max(Ps)
                    ck(math.isclose(exp, float(p["truth"]), rel_tol=1e-9), f"resnet s={s}: กำลังไม่ตรง")
            elif nm == "q_recoil":
                V = float(p["m"]) * p["v"] / p["M"]
                exp = V if p["ask"] == "V" else .5 * p["M"] * V * V
                ck(abs(exp - float(p["truth"])) < 1e-9, f"recoil s={s}: ค่าไม่ตรง")
                ck(abs(p["M"] * V - float(p["m"]) * p["v"]) < 1e-9, f"recoil s={s}: โมเมนตัมไม่คงตัว")
            elif nm == "q_material":
                Tk0, Tk1 = 300.0, p["T1"] + 273.0
                need = p["pa0"] * Tk1 / Tk0 - 1
                mult = 2 ** ((p["T1"] - 27) / p["step"])
                exp = [lab for lab, r_, pm in p["mats"] if float(r_) * mult <= float(p["lim"]) + 1e-12
                       and pm >= need - 1e-9]
                ck(exp == p["truth_set"], f"material s={s}: ชุดวัสดุไม่ตรง")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:12]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ · {len(arch)} แนว · ตำแหน่งเฉลย {dict(sorted(pos.items()))}")
    for a, c in sorted(arch.items()):
        print(f"   {c:4d}  {a}")

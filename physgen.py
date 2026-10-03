#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""แนวใหม่ของวีคฟิสิกส์ — ถอดจากท่อนเชิงกลและเชิงวิทย์ของไฟล์ที่ติวเตอร์ส่งมา (3 ต.ค. 69)

ที่มาของแต่ละแนว (ดูรายละเอียดใน reference/tpat3/DIGEST-part3.md หัวข้อ 4)
  ชุดที่ 4  สะพานรับแรง · ขบวนมวลผูกเชือก · ถังต่อกัน · เติมน้ำในภาชนะแล้วถามกราฟ · แรงกับเวลา
  ชุดที่ 6  เชือกสามเส้น · ล้อกับสายพาน · พลังงานบนพื้นเอียง · วัตถุลอย · ท่อเรียว · หลอดตัวยู
            แรงบนลวดในสนามแม่เหล็ก · นับครั้งผ่านจุดสมดุล
  ชุดที่ 8  ความร้อน กราฟการเปลี่ยนสถานะ (ค่ายวิศวฯ)
  digest เดิม  กระจกสองบาน · ครึ่งชีวิต · ค่าไฟฟ้า · ผสมน้ำ · อ่านกราฟคลื่น · สปริง

**ห้ามลอก** — ทุกข้อแต่งใหม่ ตัวเลข ถ้อยคำ และรูปสร้างจากโค้ดทั้งหมด (กติกาข้อ 3)
**ทุกข้อพิสูจน์ด้วยโค้ด** — ตัวตรวจท้ายไฟล์คำนวณคำตอบซ้ำด้วยวิธีที่สองจากพารามิเตอร์ (กติกาข้อ 1)
"""
import math
import random
from fractions import Fraction as Fr

import draw as D

NL = chr(10)


def _fmt(x):
    """เลขสวย — เศษส่วนที่ลงตัวพิมพ์เป็นจำนวนเต็ม ไม่ลงตัวพิมพ์ทศนิยมหนึ่งตำแหน่ง"""
    if isinstance(x, Fr):
        if x.denominator == 1:
            return str(x.numerator)
        return f"{float(x):g}"
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def _opts(truth, wrong, want):
    out = [truth]
    for w in wrong:
        if w is None or w in out:
            continue
        # ทศนิยมไม่รู้จบ (1666.67) ดูออกทันทีว่าเป็นตัวลวง คัดทิ้ง
        if isinstance(w, Fr) and w.denominator not in (1, 2, 4, 5, 10):
            continue
        if isinstance(w, (int, Fr, float)) and w <= 0:
            continue
        out.append(w)
    if len(out) < 5:
        return None
    out = out[:5]
    rest = [o for o in out if o != truth]
    out = rest[:want] + [truth] + rest[want:]
    return out


def _pack(arche, lvl, stem, truth, wrong, want, why, params, img=None, optimg=None,
          unit=""):
    o = _opts(truth, wrong, want)
    if not o:
        return None
    ch = [(_fmt(x) + (" " + unit if unit else "")) if not isinstance(x, str) else x for x in o]
    if len(set(ch)) < 5:
        return None
    return {"arche": arche, "lvl": lvl, "stem": stem, "choices": ch,
            "ansIdx": o.index(truth), "why": why, "params": params,
            "img": img, "optimg": optimg}


def _ratio(a, b):
    g = math.gcd(a, b)
    return f"{a // g} : {b // g}"


# ================================================================ พาร์ทที่ 3 เชิงกล

def q_belt(rng, want, tag=0):
    """ล้อกับสายพาน — ล้อ A มีล้อในติดเพลาเดียวกัน สายพานจากล้อในของ A ไป B แล้ว B ไป C

    ความเร็วของสายพานเท่ากันทุกจุด ล้อที่สายพานคล้องจึงหมุนได้ (จำนวนรอบ x รัศมี) เท่ากัน
    ล้อในกับล้อนอกติดเพลาเดียวกัน หมุนได้จำนวนรอบเท่ากัน
    สายพานไขว้กลับทิศ สายพานธรรมดาทิศเดิม
    """
    for _ in range(300):
        RA, rA = rng.choice([30, 36, 40]), rng.choice([10, 12, 15])
        RB, RC = rng.choice([20, 24, 30]), rng.choice([10, 12, 15, 18])
        crossed = rng.random() < .5
        nC = rng.choice([2, 3, 4, 5, 6])
        cw = rng.random() < .5
        nB = Fr(nC * RC, RB)
        nA = Fr(nB * RB, rA)                 # สายพาน A-B คล้องล้อในของ A
        if nA.denominator not in (1, 2) or nA > 30:
            continue
        dirB = cw if not crossed else not cw
        dirA = dirB                           # สายพาน A-B ไม่ไขว้
        ask = rng.choice(["rev", "both"])
        word = lambda c: "ตามเข็มนาฬิกา" if c else "ทวนเข็มนาฬิกา"
        if ask == "rev":
            truth = nA
            wrong = [Fr(nC * RC, RA), Fr(nC * RC, rA) * 2, nB, Fr(nC * RA, RC),
                     nA * 2, nA + 1, Fr(nC * rA, RC)]
            q = "ล้อ A หมุนได้กี่รอบ"
            unit = "รอบ"
        else:
            truth = f"{_fmt(nA)} รอบ {word(dirA)}"
            wrong = [f"{_fmt(nA)} รอบ {word(not dirA)}",
                     f"{_fmt(Fr(nC * RC, RA))} รอบ {word(dirA)}",
                     f"{_fmt(Fr(nC * RC, RA))} รอบ {word(not dirA)}",
                     f"{_fmt(nB)} รอบ {word(dirA)}", f"{_fmt(nB)} รอบ {word(not dirA)}"]
            q = "ล้อ A หมุนกี่รอบ และหมุนในทิศใด"
            unit = ""
        stem = (f"ล้อ A มีรัศมี {RA} cm และมีล้อเล็กรัศมี {rA} cm ติดอยู่บนเพลาเดียวกัน "
                f"ล้อ B รัศมี {RB} cm ล้อ C รัศมี {RC} cm" + NL +
                "สายพานคล้องล้อทั้งหมดดังรูปโดยไม่ลื่นไถล "
                f"ถ้าล้อ C หมุน{word(cw)} {nC} รอบ " + q)

        def draw(t, RA=RA, rA=rA, RB=RB, RC=RC, crossed=crossed, cw=cw):
            s = 1.25
            wheels = [(RA * s, RA * s, rA * s, "A"),
                      (RA * s * 2 + RB * s + 50, RB * s, None, "B"),
                      (RA * s * 2 + RB * s * 2 + RC * s + 100, RC * s, None, "C")]
            return D.belts(wheels, [(0, True, 1, False, False), (1, False, 2, False, crossed)],
                           f"pbelt{t}", drive=(2, cw), ask=0)
        r = _pack("ล้อและสายพาน", 3, stem, truth, wrong, want,
                  "สายพานเร็วเท่ากันทุกจุด รอบ x รัศมีเท่ากัน · ล้อติดเพลาเดียวกันหมุนเท่ากัน"
                  + (" · ไขว้กลับทิศ" if crossed else ""),
                  {"RA": RA, "rA": rA, "RB": RB, "RC": RC, "nC": nC, "crossed": crossed,
                   "cw": cw, "ask": ask, "nA": nA, "dirA": dirA}, unit=unit)
        if r:
            r["draw"] = draw
            return r
    return None


def q_train(rng, want, tag=0):
    """มวลหลายก้อนผูกเชือกเป็นขบวน ดึงด้วยแรงคงที่บนพื้นที่มีแรงเสียดทานเท่ากันทุกก้อน

    แรงเสียดทานแปรตามมวลเหมือนแรงที่ต้องใช้เร่ง จึงตัดกันหมด
    แรงตึงเชือกเส้นใด = F x (มวลที่อยู่หลังเชือกเส้นนั้น) / (มวลรวม)
    ตัวลวงสำคัญคือ "หาไม่ได้เพราะไม่รู้สัมประสิทธิ์ความเสียดทาน" ซึ่งผิด
    """
    for _ in range(300):
        n = rng.choice([3, 4, 5])
        ms = [rng.randint(1, 5) for _ in range(n)]
        link = rng.randrange(n - 1)
        tot = sum(ms)
        behind = sum(ms[:link + 1])
        F = rng.choice([20, 24, 30, 36, 40, 45, 48, 60])
        T = Fr(F * behind, tot)
        if T.denominator != 1 or T in (0, F):
            continue
        wrong = [Fr(F * (tot - behind), tot), Fr(F, n), Fr(F * (link + 1), n),
                 "หาไม่ได้ เพราะไม่ทราบค่าสัมประสิทธิ์ความเสียดทาน", T + Fr(F, tot), F]
        labs = [f"{m}m" if m > 1 else "m" for m in ms]
        stem = (f"มวล {n} ก้อนผูกต่อกันด้วยเชือกเบา วางบนพื้นราบที่มีสัมประสิทธิ์ความเสียดทาน"
                "เท่ากันทุกก้อน" + NL +
                f"ถูกดึงด้วยแรง {F} N ทางขวาจนเคลื่อนที่ไปด้วยกัน "
                "แรงตึงในเชือกเส้นที่มีป้าย T มีขนาดเท่าใด")
        r = _pack("ขบวนมวลผูกเชือก", 3, stem, T, wrong, want,
                  "แรงเสียดทานแปรตามมวลเหมือนแรงเร่ง จึงตัดกัน T = F x มวลหลังเชือก / มวลรวม",
                  {"ms": ms, "link": link, "F": F, "T": T}, unit="N")
        if r:
            r["choices"] = [c if "หาไม่ได้" not in c else "หาไม่ได้ เพราะไม่ทราบค่าสัมประสิทธิ์ความเสียดทาน"
                            for c in r["choices"]]
            r["draw"] = lambda t, labs=labs, link=link: D.train(labs, f"ptrain{t}", link)
            return r
    return None


def q_support(rng, want, tag=0):
    """สะพานวางบนจุดรองรับสองปลาย รับน้ำหนักเป็นจุด ถามแรงที่จุดรองรับ

    โมเมนต์รอบ A:  R_B x L = ผลรวม (แรง x ระยะจาก A) + W x L/2
    """
    for _ in range(300):
        L = rng.choice([8, 10, 12, 15, 20])
        k = rng.choice([1, 2])
        pos = sorted(rng.sample(range(1, L), k))
        Fs = [rng.choice([20, 30, 40, 50, 60, 80]) for _ in pos]
        W = rng.choice([0, 0, 20, 40])
        mB = Fr(sum(f * p for f, p in zip(Fs, pos)), L) + Fr(W, 2)
        mA = sum(Fs) + W - mB
        ask = rng.choice(["A", "B"])
        truth = mA if ask == "A" else mB
        if truth.denominator != 1 or truth <= 0:
            continue
        other = mB if ask == "A" else mA
        wrong = [other, Fr(sum(Fs) + W, 2), sum(Fs) + W,
                 Fr(sum(f * (L - p) for f, p in zip(Fs, pos)), L) + (0 if ask == "A" else Fr(W, 2)),
                 truth + 10, truth - 10]
        loads = [(p, f"{f} kN") for p, f in zip(pos, Fs)]
        wt = f" และคานมีน้ำหนัก {W} kN กระจายสม่ำเสมอ" if W else " (คานเบามาก ไม่ต้องคิดน้ำหนักคาน)"
        stem = (f"สะพานยาว {L} m วางบนจุดรองรับ A และ B ที่ปลายทั้งสอง รับแรงกดดังรูป{wt}" + NL +
                f"แรงที่จุดรองรับ {ask} ดันสะพานขึ้นมีขนาดเท่าใด")
        r = _pack("คานรับน้ำหนักบนจุดรองรับ", 3, stem, truth, wrong, want,
                  f"ใช้โมเมนต์รอบจุดรองรับอีกฝั่ง แรงที่ไกลจุด {ask} มากจะส่งมาที่ {ask} น้อย",
                  {"L": L, "pos": pos, "Fs": Fs, "W": W, "ask": ask, "truth": truth}, unit="kN")
        if r:
            r["draw"] = lambda t, L=L, loads=loads, W=W: D.supported(
                L, loads, f"psup{t}", unit=max(14, 260 // L), wq=bool(W))
            return r
    return None


def q_lami(rng, want, tag=0):
    """เชือกสามเส้นผูกที่ห่วงเดียวกัน ถามว่าเส้นใดตึงที่สุด (หรือหย่อนที่สุด)

    ทฤษฎีของลามี  T_A / sin(มุม BC) = T_B / sin(มุม CA) = T_C / sin(มุม AB)
    เส้นที่ตึงที่สุดคือเส้นที่ "มุมระหว่างอีกสองเส้น" มี sin มากที่สุด ไม่ใช่มุมที่ใหญ่ที่สุด
    """
    for _ in range(400):
        tCA = rng.randrange(100, 176, 5)
        tBC = rng.randrange(100, 176, 5)
        tAB = 360 - tCA - tBC
        if not 30 <= tAB <= 170:
            continue
        sA, sB, sC = (math.sin(math.radians(x)) for x in (tBC, tCA, tAB))
        vals = sorted([sA, sB, sC])
        if vals[1] - vals[0] < .05 or vals[2] - vals[1] < .05:
            continue                         # ใกล้กันเกินไป ตัดสินด้วยสายตาไม่ได้
        most = rng.random() < .65
        T = {"A": sA, "B": sB, "C": sC}
        pick = max(T, key=T.get) if most else min(T, key=T.get)
        opts = ["เชือก A", "เชือก B", "เชือก C", "เชือก A กับ B ตึงเท่ากัน", "ทั้งสามเส้นตึงเท่ากัน"]
        truth = "เชือก " + pick
        wrong = [o for o in opts if o != truth]
        dirs = [270 - tCA, tBC - 90, 270]
        stem = ("ห่วงเบาถูกดึงด้วยเชือกสามเส้นจนอยู่นิ่ง เชือก C แขวนก้อนน้ำหนักไว้ "
                "มุมระหว่างเชือกเป็นดังรูป" + NL +
                f"เชือกเส้นใดมีแรงตึง{'มากที่สุด' if most else 'น้อยที่สุด'}")
        r = _pack("เชือกสามเส้นสมดุล", 3, stem, truth, wrong, want,
                  "แรงตึงของแต่ละเส้นแปรตาม sin ของมุมระหว่างอีกสองเส้น (ทฤษฎีของลามี)",
                  {"tAB": tAB, "tBC": tBC, "tCA": tCA, "most": most, "pick": pick})
        if r:
            r["draw"] = lambda t, dirs=dirs, a=(tAB, tBC, tCA): D.ring3(
                dirs, [(0, 1, f"{a[0]}°"), (1, 2, f"{a[1]}°"), (2, 0, f"{a[2]}°")], f"plami{t}")
            return r
    return None


def q_tanks(rng, want, tag=0):
    """ถังสองใบต่อกันที่ก้นด้วยท่อมีวาล์ว เปิดวาล์วแล้วระดับน้ำเท่ากัน

    ปริมาตรรวมคงที่  ระดับสุดท้าย = (A_a h_a + A_b h_b) / (A_a + A_b)
    ตัวลวงหลักคือเฉลี่ยความสูงตรง ๆ ซึ่งใช้ได้เฉพาะเมื่อพื้นที่หน้าตัดเท่ากัน
    """
    for _ in range(300):
        Aa, Ab = rng.choice([(20, 30), (30, 20), (10, 30), (20, 60), (40, 10), (25, 50), (30, 45)])
        ha, hb = rng.randint(10, 50), rng.randint(5, 45)
        if abs(ha - hb) < 12:
            continue
        h = Fr(Aa * ha + Ab * hb, Aa + Ab)
        if h.denominator != 1:
            continue
        ask = rng.choice(["level", "drop"])
        hi = "A" if ha > hb else "B"
        if ask == "level":
            truth = h
            wrong = [Fr(ha + hb, 2), Fr(Ab * ha + Aa * hb, Aa + Ab), max(ha, hb), min(ha, hb), h + 5]
            q = "เมื่อเปิดวาล์วจนน้ำหยุดไหล ระดับน้ำในถังทั้งสองสูงจากก้นถังเท่าใด"
        else:
            truth = abs((ha if hi == "A" else hb) - h)
            wrong = [abs((ha if hi == "A" else hb) - Fr(ha + hb, 2)), abs(ha - hb),
                     abs((hb if hi == "A" else ha) - h), truth + 5, truth * 2]
            q = f"เมื่อเปิดวาล์วจนน้ำหยุดไหล ระดับน้ำในถัง {hi} ลดลงกี่เซนติเมตร"
        stem = (f"ถัง A มีพื้นที่หน้าตัด {Aa} cm² ถัง B มีพื้นที่หน้าตัด {Ab} cm² "
                "ต่อกันที่ก้นด้วยท่อเล็ก ๆ ที่มีวาล์วปิดอยู่ ระดับน้ำเริ่มต้นเป็นดังรูป" + NL + q)
        r = _pack("ถังต่อกัน", 2, stem, truth, wrong, want,
                  "ปริมาตรรวมคงที่ ระดับสุดท้าย = (A1h1 + A2h2)/(A1 + A2) ไม่ใช่เฉลี่ยความสูงตรง ๆ",
                  {"Aa": Aa, "Ab": Ab, "ha": ha, "hb": hb, "ask": ask, "truth": truth}, unit="cm")
        if r:
            r["draw"] = lambda t, Aa=Aa, Ab=Ab, ha=ha, hb=hb: D.tanks(
                Aa * 1.4, Ab * 1.4, ha, hb, f"ptank{t}", unit=3)
            return r
    return None


VKINDS = list(D.VESSELS)
VNAME = {"cyl": "ทรงกระบอก", "cone_up": "ก้นแคบปากกว้าง", "cone_dn": "ก้นกว้างปากแคบ",
         "bulb": "ป่องตรงกลาง", "waist": "คอดตรงกลาง", "step_dn": "ล่างกว้างบนแคบ",
         "step_up": "ล่างแคบบนกว้าง"}


def _curve_sig(kind):
    """ลายเซ็นของกราฟ h-t ไว้ยืนยันว่าตัวเลือกห้ารูปต่างกันจริง ไม่ใช่ต่างแค่ชื่อ"""
    ts = D.vessel_time(kind, 40)
    return tuple(round(t, 2) for t in ts[::5])


def q_vessel(rng, want, tag=0):
    """เติมน้ำด้วยอัตราคงที่ลงภาชนะรูปทรงต่าง ๆ ถามกราฟความสูงของระดับน้ำกับเวลา

    ส่วนที่แคบระดับน้ำขึ้นเร็ว ส่วนที่กว้างขึ้นช้า กราฟจึงชันหรือลาดตามความกว้างของภาชนะ
    ถามได้สองทาง ให้ภาชนะหากราฟ หรือให้กราฟหาภาชนะ
    """
    kind = rng.choice([k for k in VKINDS if k != "cyl"])
    others = [k for k in VKINDS if k != kind]
    rng.shuffle(others)
    picks = [kind] + others[:4]
    if len({_curve_sig(k) for k in picks}) < 5:
        return None
    order = list(range(5))
    rng.shuffle(order)
    order = [o for o in order if o != 0]
    order = order[:want] + [0] + order[want:]
    seq = [picks[o] for o in order]
    mode = rng.choice(["graph", "vessel"])
    if mode == "graph":
        stem = ("เปิดน้ำเติมลงในภาชนะดังรูปด้วยอัตราการไหลคงที่ จนน้ำเต็มภาชนะพอดี" + NL +
                "กราฟระหว่างความสูงของระดับน้ำ (h) กับเวลา (t) เป็นดังข้อใด")

        def draw(t, kind=kind, seq=seq):
            img = D.vessel(kind, f"pves{t}")
            files = [D.hgraph(k, f"pvg{t}_{j}") for j, k in enumerate(seq)]
            return img, D.strip(files, f"pvgopt{t}")
    else:
        stem = ("เปิดน้ำเติมลงในภาชนะใบหนึ่งด้วยอัตราการไหลคงที่ จนน้ำเต็มภาชนะพอดี "
                "ได้กราฟระหว่างความสูงของระดับน้ำ (h) กับเวลา (t) ดังรูป" + NL +
                "ภาชนะใบนั้นมีรูปร่างดังข้อใด")

        def draw(t, kind=kind, seq=seq):
            img = D.hgraph(kind, f"pvh{t}", w=130, h=90)
            files = [D.vessel(k, f"pvv{t}_{j}", w=74, h=82, tap=False) for j, k in enumerate(seq)]
            return img, D.strip(files, f"pvvopt{t}")
    return {"arche": "เติมน้ำในภาชนะ", "lvl": 3, "stem": stem, "choices": [""] * 5,
            "ansIdx": want, "why": "ช่วงที่ภาชนะแคบ ระดับน้ำขึ้นเร็ว กราฟชัน · ช่วงที่กว้าง ขึ้นช้า กราฟลาด",
            "params": {"kind": kind, "seq": seq, "mode": mode}, "draw2": draw}


def q_ramp(rng, want, tag=0):
    """วัตถุไถลขึ้นพื้นเอียงลื่นจากจุดล่างสุด แล้วหยุดที่จุดหนึ่ง จุดบนพื้นเอียงห่างเท่ากัน

    พลังงานกลคงที่ ที่จุดที่ k (นับจาก A = 0) ถ้าหยุดที่จุด n
    พลังงานศักย์ : พลังงานจลน์ = k : (n - k)
    """
    for _ in range(200):
        n = rng.randint(5, 10)
        k = rng.randint(1, n - 1)
        if math.gcd(k, n - k) == min(k, n - k) and k == n - k:
            continue
        truth = _ratio(k, n - k)
        wrong = [_ratio(n - k, k), _ratio(k, n), _ratio(n - k, n), "1 : 1", _ratio(k + 1, n - k)]
        stem = (f"วัตถุเล็ก ๆ ถูกส่งให้ไถลขึ้นพื้นเอียงที่ลื่นจากจุด A แล้วหยุดชั่วขณะที่จุด {D.AZLAB[n]}" + NL +
                "จุดบนพื้นเอียงอยู่ห่างกันเท่า ๆ กัน และให้พลังงานศักย์ที่จุด A เป็นศูนย์" + NL +
                f"ขณะวัตถุผ่านจุด {D.AZLAB[k]} อัตราส่วนพลังงานศักย์ต่อพลังงานจลน์เป็นเท่าใด")
        r = _pack("พลังงานบนพื้นเอียง", 2, stem, truth, wrong, want,
                  "พลังงานกลคงที่ ความสูงแปรตามระยะบนพื้นเอียง ศักย์:จลน์ = ระยะที่ขึ้นมา : ระยะที่เหลือ",
                  {"n": n, "k": k})
        if r:
            r["draw"] = lambda t, n=n: D.ramp(n, f"pramp{t}", n, unit=max(20, 200 // n))
            return r
    return None


def q_force_time(rng, want, tag=0):
    """เข็นของหนักจากหยุดนิ่งให้ไปได้ระยะเท่าเดิม ถ้าอยากใช้เวลาน้อยลงต้องเพิ่มแรงเท่าไร

    ระยะคงที่  s = a t²/2  ดังนั้น a แปรผกผันกับ t²  และแรงลัพธ์แปรตาม a
    ลดเวลาเหลือ 1/k ต้องใช้แรงลัพธ์ k² เท่า (ไม่มีแรงเสียดทาน)
    """
    for _ in range(100):
        k = rng.choice([2, 3])
        p = rng.choice([1, 1, 2])
        need = p * k * k
        add = need - p
        truth = add
        wrong = [p * k - p, need, p * k, add + 1, add - 1, p * (k * k + 1)]
        frac = {2: "ครึ่งหนึ่ง", 3: "หนึ่งในสาม"}[k]
        who = "นักเรียนคนหนึ่ง" if p == 1 else "นักเรียนสองคน"
        stem = (f"{who}เข็นตู้บนพื้นลื่นจากหยุดนิ่งด้วยแรงคงที่ จากหน้าห้องไปหลังห้องใช้เวลา t" + NL +
                f"ถ้าต้องการให้เคลื่อนที่ระยะเท่าเดิมโดยใช้เวลาเหลือ{frac}ของเดิม "
                "ต้องเรียกเพื่อนที่ออกแรงเท่ากันมาช่วยเพิ่มอีกกี่คน")
        r = _pack("แรงกับเวลา", 3, stem, truth, wrong, want,
                  f"ระยะเท่าเดิม a แปรผกผันกับ t² เวลาเหลือ 1/{k} ต้องใช้แรง {k * k} เท่า",
                  {"k": k, "p": p}, unit="คน")
        if r:
            return r
    return None


def q_spring(rng, want, tag=0):
    """สปริงสองตัวต่ออนุกรมหรือขนาน แขวนมวลแล้วถามระยะยืด

    อนุกรม  1/k = 1/k1 + 1/k2  (ยืดรวมเท่ากับผลบวกระยะยืดของแต่ละตัว)
    ขนาน     k = k1 + k2       (ต้องให้ทั้งสองตัวยืดเท่ากัน)
    """
    for _ in range(300):
        k1, k2 = rng.choice([100, 200, 300, 400, 600]), rng.choice([100, 200, 300, 400, 600])
        F = rng.choice([12, 24, 30, 36, 48, 60, 120])
        mode = rng.choice(["series", "parallel"])
        kk = Fr(k1 * k2, k1 + k2) if mode == "series" else Fr(k1 + k2)
        x = Fr(F, 1) / kk * 100          # เซนติเมตร
        if x.denominator != 1 or not 1 <= x <= 60:
            continue
        other = Fr(F, 1) / (Fr(k1 + k2) if mode == "series" else Fr(k1 * k2, k1 + k2)) * 100
        wrong = [other, Fr(F * 100, k1), Fr(F * 100, k2), x * 2, x + 1]
        how = "ต่อกันเป็นแนวเดียว (อนุกรม) แล้วแขวนวัตถุไว้ที่ปลายล่าง" if mode == "series" else \
              "แขวนเคียงกัน (ขนาน) แล้วแขวนวัตถุไว้ที่คานเบาที่ผูกปลายล่างของทั้งสองตัว โดยคานอยู่ในแนวระดับ"
        stem = (f"สปริงเบาสองตัวมีค่าคงตัวสปริง {k1} N/m และ {k2} N/m {how}" + NL +
                f"ถ้าวัตถุหนัก {F} N ระยะที่วัตถุเลื่อนลงจากตำแหน่งที่สปริงยังไม่ยืดเป็นเท่าใด")
        r = _pack("สปริงต่อกัน", 2, stem, x, wrong, want,
                  "อนุกรม ยืดรวม = ผลบวกระยะยืดแต่ละตัว · ขนาน ค่าคงตัวรวม = k1 + k2",
                  {"k1": k1, "k2": k2, "F": F, "mode": mode, "x": x}, unit="cm")
        if r:
            return r
    return None


# ================================================================ พาร์ทที่ 4 เชิงวิทย์

def q_utube(rng, want, tag=0):
    """หลอดตัวยูบรรจุน้ำ เทของเหลว X ที่ไม่ผสมกับน้ำลงแขนซ้าย

    ที่ระดับรอยต่อ ความดันสองแขนเท่ากัน  ρX hX = ρน้ำ hน้ำ
    """
    for _ in range(300):
        hx = rng.choice([10, 12, 15, 16, 20, 24, 25, 30])
        hw = rng.randint(6, hx - 2)
        rho = Fr(1000 * hw, hx)
        if rho.denominator != 1 or rho % 10:
            continue
        ask = rng.choice(["rho", "hw"])
        if ask == "rho":
            truth = rho
            wrong = [Fr(1000 * hx, hw), 1000 - (hx - hw) * 10, rho + 50, rho - 50, Fr(1000 * hw, hx + hw)]
            stem = ("หลอดตัวยูบรรจุน้ำ (ความหนาแน่น 1,000 kg/m³) แล้วเทของเหลว X ซึ่งไม่ผสมกับน้ำ"
                    "ลงในแขนซ้าย จนระดับนิ่งดังรูป" + NL + "ของเหลว X มีความหนาแน่นเท่าใด")
            unit = "kg/m³"
        else:
            truth = Fr(hw)
            wrong = [Fr(hx), Fr(hx - hw), Fr(hx * 1000, int(rho)), Fr(hw + 2), Fr(hw - 2)]
            stem = (f"หลอดตัวยูบรรจุน้ำ (ความหนาแน่น 1,000 kg/m³) แล้วเทของเหลว X ความหนาแน่น {rho} kg/m³ "
                    f"ซึ่งไม่ผสมกับน้ำลงในแขนซ้ายจนเป็นลำสูง {hx} cm" + NL +
                    "ผิวน้ำในแขนขวาอยู่สูงกว่ารอยต่อระหว่างของเหลวกับน้ำกี่เซนติเมตร")
            unit = "cm"
        r = _pack("หลอดตัวยู", 2, stem, truth, wrong, want,
                  "ที่ระดับรอยต่อความดันสองแขนเท่ากัน ρX hX = ρน้ำ hน้ำ",
                  {"hx": hx, "hw": hw, "rho": rho, "ask": ask}, unit=unit)
        if r:
            r["draw"] = (lambda t, hx=hx, hw=hw: D.utube(hx, hw, f"putube{t}")) if ask == "rho" else None
            return r
    return None


def q_float(rng, want, tag=0):
    """วัตถุหลายก้อนลอยน้ำ แต่ละก้อนตีเส้นแบ่งเป็นชั้นเท่า ๆ กัน นับส่วนที่จมได้

    วัตถุลอย  ρวัตถุ / ρน้ำ = ส่วนที่จม / ทั้งก้อน
    """
    for _ in range(300):
        nb = rng.choice([2, 3])
        blocks = []
        for lab in "ABC"[:nb]:
            q = rng.randint(3, 6)
            p = rng.randint(1, q - 1)
            blocks.append((lab, p, q))
        dens = [Fr(p, q) for _, p, q in blocks]
        if len(set(dens)) < nb:
            continue
        if nb == 2:
            r_ = dens[1] / dens[0]
            truth = f"{r_.numerator} : {r_.denominator}"
            inv = dens[0] / dens[1]
            wrong = [f"{inv.numerator} : {inv.denominator}",
                     _ratio(blocks[1][1], blocks[0][1]), _ratio(blocks[1][2], blocks[0][2]),
                     _ratio(blocks[1][2] - blocks[1][1], blocks[0][2] - blocks[0][1]), "1 : 1"]
            q = "อัตราส่วนความหนาแน่นของก้อน B ต่อก้อน A เป็นเท่าใด"
        else:
            order = sorted(range(3), key=lambda i: -dens[i])
            truth = " > ".join("ABC"[i] for i in order)
            import itertools
            wrong = [" > ".join(p) for p in itertools.permutations("ABC") if " > ".join(p) != truth]
            rng.shuffle(wrong)
            q = "ข้อใดเรียงความหนาแน่นของวัตถุจากมากไปน้อยได้ถูกต้อง"
        stem = ("วัตถุทรงสี่เหลี่ยมลอยนิ่งอยู่ในน้ำดังรูป แต่ละก้อนแบ่งเป็นชั้นหนาเท่ากันตามเส้นที่ขีดไว้" + NL + q)
        r = _pack("วัตถุลอยหลายก้อน", 2 if nb == 2 else 3, stem, truth, wrong, want,
                  "วัตถุที่ลอย ความหนาแน่นเทียบน้ำ = ส่วนที่จม ÷ ทั้งก้อน (นับชั้น ไม่ใช่ดูความสูงที่โผล่)",
                  {"blocks": blocks})
        if r:
            r["draw"] = lambda t, b=blocks: D.floaters(b, f"pfloat{t}")
            return r
    return None


def q_taper(rng, want, tag=0):
    """ท่อแนวนอนหน้าตัดไม่เท่ากัน ของเหลวไหลเต็มท่อ ถามลำดับอัตราเร็วหรือความดัน

    ต่อเนื่อง  Av คงที่ → ช่วงแคบไหลเร็ว
    แบร์นูลลี (ท่อระดับเดียวกัน) → ช่วงที่ไหลเร็วความดันต่ำ
    """
    import itertools
    for _ in range(300):
        n = 3
        radii = rng.sample([8, 11, 14, 18, 22, 26], n)
        ask = rng.choice(["speed", "pressure"])
        key = (lambda i: radii[i]) if ask == "speed" else (lambda i: -radii[i])
        order = sorted(range(n), key=key)          # จากมากไปน้อย ของปริมาณที่ถาม
        truth = " > ".join("ABC"[i] for i in order)
        wrong = [" > ".join(p) for p in itertools.permutations("ABC") if " > ".join(p) != truth]
        rng.shuffle(wrong)
        wrong = [" > ".join("ABC"[i] for i in order[::-1])] + wrong
        word = "อัตราเร็วของของเหลว" if ask == "speed" else "ความดันของของเหลว"
        stem = ("ของเหลวไหลเต็มท่อแนวระดับที่มีหน้าตัดไม่เท่ากันดังรูป" + NL +
                f"ข้อใดเรียง{word}ที่จุด A B และ C จากมากไปน้อยได้ถูกต้อง")
        r = _pack("ท่อเรียว", 3 if ask == "pressure" else 2, stem, truth, wrong, want,
                  "Av คงที่ ตรงแคบไหลเร็ว · ท่อระดับเดียวกัน ตรงที่ไหลเร็วความดันต่ำ",
                  {"radii": radii, "ask": ask})
        if r:
            r["draw"] = lambda t, rr=radii: D.taper(rr, f"ptaper{t}")
            return r
    return None


def q_mix(rng, want, tag=0):
    """ผสมน้ำสองอุณหภูมิในภาชนะที่ไม่รับและไม่เสียความร้อน
    ความร้อนที่น้ำร้อนเสีย = ความร้อนที่น้ำเย็นรับ  T = (m1T1 + m2T2)/(m1 + m2)
    """
    for _ in range(300):
        m1, m2 = rng.choice([100, 200, 300, 400, 500]), rng.choice([100, 200, 300, 400, 500])
        T1, T2 = rng.randint(60, 95), rng.randint(5, 35)
        T = Fr(m1 * T1 + m2 * T2, m1 + m2)
        if T.denominator != 1 or m1 == m2:
            continue
        wrong = [Fr(T1 + T2, 2), Fr(m2 * T1 + m1 * T2, m1 + m2), T + 5, T - 5, Fr(T1 - T2, 2)]
        stem = (f"ผสมน้ำร้อน {m1} g อุณหภูมิ {T1} °C กับน้ำเย็น {m2} g อุณหภูมิ {T2} °C "
                "ในภาชนะที่ไม่รับและไม่ถ่ายเทความร้อน" + NL + "อุณหภูมิสุดท้ายของน้ำผสมเป็นเท่าใด")
        r = _pack("ผสมน้ำร้อนน้ำเย็น", 2, stem, T, wrong, want,
                  "ความร้อนที่ฝั่งร้อนเสีย = ฝั่งเย็นรับ ได้ค่าเฉลี่ยถ่วงน้ำหนักด้วยมวล",
                  {"m1": m1, "m2": m2, "T1": T1, "T2": T2, "T": T}, unit="°C")
        if r:
            return r
    return None


def q_heatcurve(rng, want, tag=0):
    """ให้ความร้อนด้วยอัตราคงที่แก่ของแข็ง ได้กราฟอุณหภูมิกับเวลามีช่วงราบสองช่วง

    อัตราให้ความร้อนคงที่ → ความร้อนแปรตามเวลา
    ความร้อนแฝงการกลายเป็นไอ / ความร้อนแฝงการหลอมเหลว = ความยาวช่วงราบที่สอง / ช่วงราบแรก
    ความจุความร้อนจำเพาะ ของเหลว / ของแข็ง = ความชันช่วงของแข็ง / ความชันช่วงของเหลว
    """
    for _ in range(300):
        T0, Tm, Tb = 10, rng.choice([30, 40, 50]), rng.choice([80, 90, 100])
        # เวลาเป็นเลขคู่ทั้งหมด ขีดบนแกนเวลาจะห่างทีละ 2 ไม่แน่นจนอ่านไม่ออก
        a = rng.choice([2, 4])                    # เวลาช่วงของแข็ง
        f = rng.choice([2, 4, 6, 8])              # ช่วงหลอมเหลว
        b = rng.choice([2, 4, 6])                 # ช่วงของเหลว
        v = rng.choice([4, 6, 8, 10, 12])         # ช่วงเดือด
        ask = rng.choice(["latent", "spec"])
        t1, t2, t3, t4 = a, a + f, a + f + b, a + f + b + v
        if t4 > 28 or v <= f:
            continue                      # ของจริงความร้อนแฝงการกลายเป็นไอมากกว่าการหลอมเหลวเสมอ
        pts = [(0, T0), (t1, Tm), (t2, Tm), (t3, Tb), (t4, Tb)]
        if ask == "latent":
            truth = _ratio(v, f)
            wrong = [_ratio(f, v), _ratio(v, b), _ratio(Tb, Tm), _ratio(t4 - t3, t3), _ratio(v + f, f)]
            # ตัดบรรทัดเอง Word ตัดคำไทยกลางคำ ("หลอมเห / ลว") ถ้าปล่อยให้ยาวเกินบรรทัด
            q = ("อัตราส่วนของความร้อนแฝงจำเพาะของการกลายเป็นไอ" + NL +
                 "ต่อความร้อนแฝงจำเพาะของการหลอมเหลวมีค่าเท่าใด")
            why = "อัตราให้ความร้อนคงที่ ความร้อนแฝงแปรตามความยาวช่วงที่อุณหภูมิคงที่"
        else:
            sl_s, sl_l = Fr(Tm - T0, a), Fr(Tb - Tm, b)
            r_ = sl_s / sl_l
            if r_ == 1:
                continue
            truth = f"{r_.numerator} : {r_.denominator}"
            inv = 1 / r_
            wrong = [f"{inv.numerator} : {inv.denominator}", _ratio(b, a), _ratio(Tb - Tm, Tm - T0),
                     "1 : 1", _ratio(a + b, b)]
            q = ("อัตราส่วนของความจุความร้อนจำเพาะของสารในสถานะของเหลว" + NL +
                 "ต่อความจุความร้อนจำเพาะในสถานะของแข็งมีค่าเท่าใด")
            why = "ความชันยิ่งน้อย ความจุความร้อนจำเพาะยิ่งมาก c แปรผกผันกับความชันของกราฟ"
        stem = ("ให้ความร้อนแก่ของแข็งชนิดหนึ่งด้วยอัตราคงที่ วัดอุณหภูมิกับเวลาได้กราฟดังรูป "
                "โดยไม่มีการสูญเสียความร้อน" + NL + q)
        r = _pack("กราฟการเปลี่ยนสถานะ", 3, stem, truth, wrong, want, why,
                  {"pts": pts, "ask": ask})
        if r:
            r["draw"] = lambda t, pts=pts: D.vtgraph(pts, f"pheat{t}", xlab="t (นาที)",
                                                       ylab="T (°C)", w=280, h=150,
                                                       fill=False, z=1.3)
            return r
    return None


def q_wavegraph(rng, want, tag=0):
    """อ่านความยาวคลื่นและแอมพลิจูดจากกราฟ แล้วใช้ v = f λ"""
    for _ in range(200):
        lam = rng.choice([2, 4, 6, 8])
        amp = rng.choice([2, 3, 4, 5])
        f = rng.choice([2, 3, 4, 5, 10])
        ask = rng.choice(["v", "f", "amp"])
        if ask == "v":
            truth = f * lam
            wrong = [f * lam // 2, f * lam * 2, Fr(lam, f) if lam % f == 0 else f + lam, f * amp, f * lam + f]
            q = f"ถ้าแหล่งกำเนิดสั่นด้วยความถี่ {f} Hz คลื่นนี้มีอัตราเร็วเท่าใด"
            unit = "m/s"
        elif ask == "f":
            v = f * lam
            truth = f
            wrong = [Fr(v, lam * 2), v * lam, Fr(2 * v, lam), f + 1, Fr(v, amp) if v % amp == 0 else f + 3]
            q = f"ถ้าคลื่นนี้เคลื่อนที่ด้วยอัตราเร็ว {v} m/s แหล่งกำเนิดสั่นด้วยความถี่เท่าใด"
            unit = "Hz"
        else:
            truth = amp
            wrong = [amp * 2, Fr(amp, 2) if amp % 2 == 0 else amp + 1, amp * 4, lam, amp + 3]
            q = "แอมพลิจูดของคลื่นนี้มีค่าเท่าใด"
            unit = "cm"
        stem = "กราฟแสดงการกระจัดของอนุภาคตัวกลางกับระยะทางตามแนวที่คลื่นเคลื่อนที่ ณ ขณะหนึ่ง" + NL + q
        r = _pack("อ่านกราฟคลื่น", 2, stem, truth, wrong, want,
                  "ความยาวคลื่นนับจากยอดถึงยอดถัดไป · แอมพลิจูดวัดจากแนวสมดุลถึงยอด · v = fλ",
                  {"lam": lam, "amp": amp, "f": f, "ask": ask}, unit=unit)
        if r:
            r["draw"] = lambda t, lam=lam, amp=amp: D.wave(amp, lam, 2, f"pwave{t}")
            return r
    return None


def q_halflife(rng, want, tag=0):
    """ครึ่งชีวิต — หลังผ่านไป n ครึ่งชีวิต เหลือ 1/2ⁿ ของเดิม"""
    for _ in range(100):
        T = rng.choice([2, 3, 4, 5, 6, 8, 10])
        n = rng.randint(2, 5)
        m0 = rng.choice([64, 80, 96, 128, 160, 192, 240, 320])
        rest = Fr(m0, 2 ** n)
        ask = rng.choice(["left", "decayed", "time"])
        if rest.denominator != 1:
            continue
        if ask == "left":
            truth = rest
            wrong = [Fr(m0, 2 * n), m0 - rest, Fr(m0, 2 ** (n - 1)), Fr(m0, 2 ** (n + 1)), Fr(m0, n)]
            q = f"เมื่อเวลาผ่านไป {n * T} วัน จะเหลือสารนี้กี่กรัม"
            unit = "g"
        elif ask == "decayed":
            truth = m0 - rest
            wrong = [rest, m0 - Fr(m0, 2 ** (n - 1)), m0 - Fr(m0, 2 * n), m0 - Fr(m0, 2 ** (n + 1)), Fr(m0, 2)]
            q = f"เมื่อเวลาผ่านไป {n * T} วัน สารนี้สลายไปแล้วกี่กรัม"
            unit = "g"
        else:
            truth = n * T
            wrong = [Fr(n * T, 2), (n + 1) * T, (n - 1) * T, T * 2 ** n, n * T + 1]
            q = f"ต้องใช้เวลานานเท่าใด สารนี้จึงเหลือ {rest} กรัม"
            unit = "วัน"
        stem = f"สารกัมมันตรังสีชนิดหนึ่งมีครึ่งชีวิต {T} วัน เริ่มต้นมีสารนี้ {m0} กรัม" + NL + q
        r = _pack("ครึ่งชีวิต", 2, stem, truth, wrong, want,
                  "ผ่านไปหนึ่งครึ่งชีวิตเหลือครึ่งหนึ่ง นับจำนวนครึ่งชีวิตก่อน แล้วหารสองไปทีละครั้ง",
                  {"T": T, "n": n, "m0": m0, "ask": ask, "truth": truth}, unit=unit)
        if r:
            return r
    return None


def q_mirrors(rng, want, tag=0):
    """กระจกเงาราบสองบานทำมุมกัน จำนวนภาพ = 360/θ − 1 (เมื่อ 360/θ เป็นจำนวนเต็ม)"""
    th = rng.choice([30, 36, 40, 45, 60, 72, 90, 120])
    n = 360 // th - 1
    ask = rng.choice(["count", "angle"])
    if ask == "count":
        truth = n
        wrong = [n + 1, n - 1, 360 // th, 180 // th, n + 2]
        stem = (f"วางกระจกเงาราบสองบานให้ขอบชิดกันและทำมุม {th} องศา "
                "แล้ววางเทียนไว้ระหว่างกระจกทั้งสอง" + NL + "จะเห็นภาพของเทียนในกระจกทั้งหมดกี่ภาพ")
        unit = "ภาพ"
    else:
        truth = th
        wrong = [360 // n if 360 % n == 0 else th + 10, 360 // (n + 2), th * 2, Fr(th, 2), th + 15]
        stem = (f"วางกระจกเงาราบสองบานให้ขอบชิดกัน แล้ววางวัตถุไว้ระหว่างกระจก เห็นภาพของวัตถุ {n} ภาพ"
                + NL + "กระจกทั้งสองบานทำมุมกันกี่องศา")
        unit = "องศา"
    return _pack("กระจกสองบาน", 2, stem, truth, wrong, want,
                 "จำนวนภาพ = 360 ÷ มุมระหว่างกระจก แล้วลบหนึ่ง (ลบตัววัตถุจริงออก)",
                 {"th": th, "ask": ask, "truth": truth}, unit=unit)


APPL = [("หลอดไฟ LED", [9, 10, 12, 18, 20]), ("พัดลม", [40, 50, 60, 75]),
        ("ตู้เย็น", [100, 120, 150]), ("โทรทัศน์", [80, 100, 120, 150]),
        ("เครื่องปรับอากาศ", [1000, 1200, 1500, 2000]), ("หม้อหุงข้าว", [500, 600, 800]),
        ("เตารีด", [1000, 1200]), ("คอมพิวเตอร์", [200, 250, 300])]


def q_bill(rng, want, tag=0):
    """ค่าไฟฟ้าในบ้าน — พลังงาน (kWh) = กำลัง (kW) x ชั่วโมง แล้วคูณราคาต่อหน่วย"""
    for _ in range(400):
        items = rng.sample(APPL, rng.choice([2, 3]))
        rows, wh = [], 0
        for nm, ws in items:
            w = rng.choice(ws)
            cnt = rng.choice([1, 1, 2, 4]) if w < 100 else 1
            h = rng.choice([2, 3, 4, 5, 6, 8, 10])
            rows.append((nm, w, cnt, h))
            wh += w * cnt * h
        days = rng.choice([10, 20, 30])
        rate = rng.choice([3, 4, 5])
        kwh = Fr(wh * days, 1000)
        cost = kwh * rate
        if cost.denominator != 1 or not 50 <= cost <= 3000:
            continue
        wrong = [Fr(wh * rate, 1000) * 30 if days != 30 else cost * 2, kwh, cost + rate * 10,
                 Fr(wh * days * rate, 100), Fr(cost, 2)]
        lines = NL.join(f"    {nm} {w} วัตต์" + (f" จำนวน {c} เครื่อง" if c > 1 else "") +
                        f" ใช้วันละ {h} ชั่วโมง" for nm, w, c, h in rows)
        stem = ("บ้านหลังหนึ่งใช้เครื่องใช้ไฟฟ้าดังนี้" + NL + lines + NL +
                f"ถ้าใช้แบบนี้ทุกวันเป็นเวลา {days} วัน และค่าไฟฟ้าหน่วยละ {rate} บาท "
                "ต้องจ่ายค่าไฟฟ้ากี่บาท")
        r = _pack("ค่าไฟฟ้าในบ้าน", 2, stem, cost, wrong, want,
                  "หน่วยไฟฟ้า = กิโลวัตต์ x ชั่วโมง ระวังแปลงวัตต์เป็นกิโลวัตต์และคูณจำนวนวัน",
                  {"rows": rows, "days": days, "rate": rate, "cost": cost}, unit="บาท")
        if r:
            return r
    return None


def q_bil(rng, want, tag=0):
    """แรงแม่เหล็กบนลวดตรงที่มีกระแส F = B I L sinθ — ข้อใดไม่ถูกต้อง

    สร้างข้อความห้าข้อ แต่ละข้อปรับปริมาณหนึ่งหรือสองตัวแล้วบอกผลของแรง
    คำนวณผลจริงด้วยการคูณตัวคูณ แล้วยืนยันว่ามีข้อเดียวที่บอกผลผิด
    """
    qty = {"I": "กระแสไฟฟ้า", "L": "ความยาวของลวดในสนาม", "B": "ขนาดของสนามแม่เหล็ก"}
    mult = {2: "2 เท่า", 3: "3 เท่า", Fr(1, 2): "ครึ่งหนึ่ง"}
    for _ in range(300):
        stmts = []
        seen = set()
        while len(stmts) < 5:
            keys = rng.sample(list(qty), rng.choice([1, 1, 2]))
            fac = {k: rng.choice(list(mult)) for k in keys}
            sig = tuple(sorted((k, str(v)) for k, v in fac.items()))
            if sig in seen:
                continue
            seen.add(sig)
            real = Fr(1)
            for v in fac.values():
                real *= v
            stmts.append((fac, real))
        bad = rng.randrange(5)
        out = []
        for i, (fac, real) in enumerate(stmts):
            claim = real
            if i == bad:
                cands = [x for x in (real * 2, real / 2, Fr(1), real * 4, Fr(real.denominator, real.numerator))
                         if x != real and x > 0]
                claim = rng.choice(cands)
            parts = []
            for k, v in fac.items():
                parts.append(f"เพิ่ม{qty[k]}เป็น {mult[v]}" if v != Fr(1, 2) else f"ลด{qty[k]}เหลือครึ่งหนึ่ง")
            res = f"{_fmt(claim)}F" if claim != 1 else "F เท่าเดิม"
            out.append(" และ".join(parts) + f" แรงแม่เหล็กจะเป็น {res}")
        if len(set(out)) < 5:
            continue
        truth = out[bad]
        wrong = [o for i, o in enumerate(out) if i != bad]
        stem = ("ลวดตรงมีกระแสไฟฟ้าผ่าน วางตั้งฉากกับสนามแม่เหล็กสม่ำเสมอ "
                "พบว่าลวดถูกแรงแม่เหล็กขนาด F" + NL + "ข้อความใด**ไม่**ถูกต้อง")
        r = _pack("แรงบนลวดในสนามแม่เหล็ก", 2, stem, truth, wrong, want,
                  "F = BIL ทั้งสามตัวคูณกัน ผลคูณของตัวคูณคือเท่าของแรงใหม่",
                  {"stmts": [({k: str(v) for k, v in f.items()}, str(rv)) for f, rv in stmts],
                   "bad": bad, "out": out})
        if r:
            return r
    return None


def q_shm(rng, want, tag=0):
    """การเคลื่อนที่แบบฮาร์มอนิก — นับครั้งที่ผ่านจุดสมดุล

    เริ่มจากปลายสุด  ผ่านสมดุลครั้งแรกที่ T/4 แล้วทุก ๆ T/2
    เริ่มจากสมดุล (ไม่นับตอนเริ่ม)  ผ่านครั้งที่ n ที่ nT/2
    """
    for _ in range(100):
        T = rng.choice([2, 4, 6, 8, 12])
        n = rng.randint(3, 7)
        start = rng.choice(["edge", "mid"])
        t = Fr(T, 4) + (n - 1) * Fr(T, 2) if start == "edge" else n * Fr(T, 2)
        if t.denominator != 1:
            continue
        alt = n * Fr(T, 2) if start == "edge" else Fr(T, 4) + (n - 1) * Fr(T, 2)
        wrong = [alt, n * T, (n - 1) * Fr(T, 2), t + Fr(T, 2), Fr(n * T, 4)]
        where = "ปล่อยจากตำแหน่งที่ยืดออกมากที่สุด" if start == "edge" else \
                "เริ่มจับเวลาขณะผ่านตำแหน่งสมดุลพอดี (ไม่นับครั้งนี้)"
        stem = (f"วัตถุติดปลายสปริงสั่นแบบฮาร์มอนิกอย่างง่ายด้วยคาบ {T} วินาที โดย{where}" + NL +
                f"วัตถุจะผ่านตำแหน่งสมดุลเป็นครั้งที่ {n} เมื่อเวลาผ่านไปกี่วินาที")
        r = _pack("ฮาร์มอนิก · นับครั้งผ่านสมดุล", 3, stem, t, wrong, want,
                  "หนึ่งคาบผ่านสมดุลสองครั้ง ห่างกันครึ่งคาบ ถ้าเริ่มที่ปลายสุดครั้งแรกใช้แค่ T/4",
                  {"T": T, "n": n, "start": start, "t": t}, unit="วินาที")
        if r:
            return r
    return None


P3_GENS = [q_belt, q_train, q_support, q_lami, q_tanks, q_vessel, q_ramp, q_force_time, q_spring]
P4_GENS = [q_utube, q_float, q_taper, q_mix, q_heatcurve, q_wavegraph, q_halflife, q_mirrors,
           q_bill, q_bil, q_shm]


def build(add, P3, P4, rng, per=3):
    """เติมแนวใหม่เข้าคลัง แนวละ per ข้อ — เรียกจาก gen.py"""
    want, tag = 0, 0
    for part, gens in ((P3, P3_GENS), (P4, P4_GENS)):
        for g in gens:
            made, sig = 0, set()
            for _ in range(per * 30):
                r = g(rng, want, tag)
                tag += 1
                if not r:
                    continue
                key = r["stem"] + "|".join(r["choices"])
                if key in sig:
                    continue
                sig.add(key)
                img = optimg = None
                if r.get("draw2"):
                    img, optimg = r["draw2"](tag)
                elif r.get("draw"):
                    img = r["draw"](tag)
                add(part, r["arche"], r["stem"], r["choices"], r["ansIdx"],
                    img=img, optimg=optimg, lvl=r["lvl"], why=r["why"])
                want = (want + 2) % 5
                made += 1
                if made >= per:
                    break


# ================================================================ ตรวจตัวเอง
if __name__ == "__main__":
    import collections
    bad, n = [], 0
    pos, arch = collections.Counter(), collections.Counter()

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    def got(r):
        return r["choices"][r["ansIdx"]]

    for s in range(250):
        rng = random.Random(s)
        for g in P3_GENS + P4_GENS:
            w = s % 5
            r = g(rng, w)
            if not r:
                continue
            n += 1
            nm = g.__name__
            arch[r["arche"]] += 1
            pos[r["ansIdx"]] += 1
            p = r["params"]
            ck(len(set(r["choices"])) == 5 or nm == "q_vessel", f"{nm} s={s}: ตัวเลือกซ้ำ")
            ck(r["ansIdx"] == w, f"{nm} s={s}: ตำแหน่งเฉลยไม่ตรงที่สั่ง")
            ck(r["why"] and len(r["why"]) <= 90, f"{nm} s={s}: บรรทัดแนวคิดหายหรือยาวเกิน {len(r['why'] or '')}")
            ans = got(r)
            if nm == "q_belt":
                # ไล่จากล้อ C ย้อนไป A ด้วย "ความเร็วสายพานเท่ากัน" อีกทางหนึ่ง
                v = p["nC"] * 2 * math.pi * p["RC"]           # ระยะที่สายพาน B-C วิ่ง
                nB = v / (2 * math.pi * p["RB"])
                v2 = nB * 2 * math.pi * p["RB"]               # สายพาน A(ใน)-B
                nA = v2 / (2 * math.pi * p["rA"])
                ck(abs(nA - float(p["nA"])) < 1e-9, f"belt s={s}: รอบไม่ตรง")
                dirB = p["cw"] != p["crossed"]
                ck(dirB == p["dirA"], f"belt s={s}: ทิศไม่ตรง")
                ck(ans.startswith(_fmt(p["nA"])), f"belt s={s}: เฉลยไม่ใช่ค่าที่คำนวณ")
                if p["ask"] == "both":
                    w_ = "ตามเข็มนาฬิกา" if dirB else "ทวนเข็มนาฬิกา"
                    ck(ans.endswith(w_), f"belt s={s}: ทิศในเฉลยผิด")
            elif nm == "q_train":
                ms, F, k = p["ms"], p["F"], p["link"]
                # คิดแบบแยกวัตถุ: ความเร่งร่วม a = (F - μgΣm)/Σm ทุก μ ให้ผลเดียวกัน
                for mu_g in (0.0, 1.0, 2.5):
                    a = (F - mu_g * sum(ms)) / sum(ms)
                    T = sum(ms[:k + 1]) * (a + mu_g)
                    ck(abs(T - float(p["T"])) < 1e-9, f"train s={s}: ค่า μ เปลี่ยนแล้วแรงตึงเปลี่ยน")
                ck(ans == f"{_fmt(p['T'])} N", f"train s={s}: เฉลยไม่ตรง")
            elif nm == "q_support":
                L, W = p["L"], p["W"]
                RA = sum(f * (L - x) for f, x in zip(p["Fs"], p["pos"])) / L + W / 2
                RB = sum(p["Fs"]) + W - RA
                want_v = RA if p["ask"] == "A" else RB
                ck(abs(want_v - float(p["truth"])) < 1e-9, f"support s={s}: โมเมนต์รอบ B ไม่ตรง")
            elif nm == "q_lami":
                # แก้สมดุลแรงจริงด้วยเวกเตอร์ แล้วดูว่าเส้นไหนตึงสุด
                dirs = {"A": 270 - p["tCA"], "B": p["tBC"] - 90, "C": 270}
                u = {k: (math.cos(math.radians(v)), math.sin(math.radians(v))) for k, v in dirs.items()}
                # T_C = 1 (น้ำหนัก) แก้ T_A u_A + T_B u_B = -u_C
                a11, a12, a21, a22 = u["A"][0], u["B"][0], u["A"][1], u["B"][1]
                det = a11 * a22 - a12 * a21
                bx, by = -u["C"][0], -u["C"][1]
                TA = (bx * a22 - a12 * by) / det
                TB = (a11 * by - bx * a21) / det
                T = {"A": TA, "B": TB, "C": 1.0}
                ck(TA > 0 and TB > 0, f"lami s={s}: เชือกต้องตึง ไม่ใช่ถูกดัน")
                pick = max(T, key=T.get) if p["most"] else min(T, key=T.get)
                ck(pick == p["pick"] and ans == "เชือก " + pick, f"lami s={s}: เส้นที่เฉลยไม่ตรงกับการแก้สมการ")
            elif nm == "q_tanks":
                V = p["Aa"] * p["ha"] + p["Ab"] * p["hb"]
                h = V / (p["Aa"] + p["Ab"])
                if p["ask"] == "level":
                    ck(abs(h - float(p["truth"])) < 1e-9, f"tanks s={s}: ระดับไม่ตรง")
                else:
                    hi = max(p["ha"], p["hb"])
                    ck(abs(hi - h - float(p["truth"])) < 1e-9, f"tanks s={s}: ระดับที่ลดไม่ตรง")
            elif nm == "q_vessel":
                ck(p["seq"][r["ansIdx"]] == p["kind"], f"vessel s={s}: เฉลยไม่ใช่รูปของภาชนะนี้")
                ck(len({_curve_sig(k) for k in p["seq"]}) == 5, f"vessel s={s}: กราฟตัวเลือกซ้ำ")
            elif nm == "q_ramp":
                PE, KE = p["k"], p["n"] - p["k"]
                ck(ans == _ratio(PE, KE), f"ramp s={s}: อัตราส่วนไม่ตรง")
            elif nm == "q_force_time":
                k, pp = p["k"], p["p"]
                ck(ans == f"{pp * k * k - pp} คน", f"force_time s={s}: จำนวนคนไม่ตรง")
            elif nm == "q_spring":
                k1, k2, F = p["k1"], p["k2"], p["F"]
                x = F / k1 + F / k2 if p["mode"] == "series" else F / (k1 + k2)
                ck(abs(x * 100 - float(p["x"])) < 1e-9, f"spring s={s}: ระยะยืดไม่ตรง")
            elif nm == "q_utube":
                rho = 1000 * p["hw"] / p["hx"]
                ck(abs(rho - float(p["rho"])) < 1e-9, f"utube s={s}: ความหนาแน่นไม่ตรง")
                exp = f"{_fmt(p['rho'])} kg/m³" if p["ask"] == "rho" else f"{p['hw']} cm"
                ck(ans == exp, f"utube s={s}: เฉลยไม่ตรง")
            elif nm == "q_float":
                dens = {lab: pp / q for lab, pp, q in p["blocks"]}
                if len(dens) == 2:
                    rr = Fr(p["blocks"][1][1] * p["blocks"][0][2], p["blocks"][1][2] * p["blocks"][0][1])
                    ck(ans == f"{rr.numerator} : {rr.denominator}", f"float s={s}: อัตราส่วนไม่ตรง")
                else:
                    ck(ans == " > ".join(sorted(dens, key=lambda x: -dens[x])), f"float s={s}: ลำดับไม่ตรง")
            elif nm == "q_taper":
                rad = dict(zip("ABC", p["radii"]))
                v = {k: 1 / x ** 2 for k, x in rad.items()}           # Av คงที่
                P_ = {k: 100 - .5 * vv * 1e3 for k, vv in v.items()}  # แบร์นูลลี
                q = v if p["ask"] == "speed" else P_
                ck(ans == " > ".join(sorted(q, key=lambda x: -q[x])), f"taper s={s}: ลำดับไม่ตรง")
            elif nm == "q_mix":
                Q = lambda T: p["m1"] * (p["T1"] - T) - p["m2"] * (T - p["T2"])
                ck(abs(Q(float(p["T"]))) < 1e-9, f"mix s={s}: ความร้อนไม่สมดุล")
            elif nm == "q_heatcurve":
                (t0, T0), (t1, Tm), (t2, _), (t3, Tb), (t4, _) = p["pts"]
                if p["ask"] == "latent":
                    ck(ans == _ratio(t4 - t3, t2 - t1), f"heat s={s}: อัตราส่วนความร้อนแฝงไม่ตรง")
                else:
                    cs = (t1 - t0) / (Tm - T0)          # c แปรตาม เวลา / อุณหภูมิที่เพิ่ม
                    cl = (t3 - t2) / (Tb - Tm)
                    rr = Fr(cl).limit_denominator(100) / Fr(cs).limit_denominator(100)
                    ck(ans == f"{rr.numerator} : {rr.denominator}", f"heat s={s}: อัตราส่วน c ไม่ตรง")
            elif nm == "q_wavegraph":
                exp = {"v": p["f"] * p["lam"], "f": p["f"], "amp": p["amp"]}[p["ask"]]
                ck(ans.split()[0] == str(exp), f"wave s={s}: เฉลยไม่ตรง")
            elif nm == "q_halflife":
                left = p["m0"] * 0.5 ** p["n"]
                exp = {"left": left, "decayed": p["m0"] - left, "time": p["n"] * p["T"]}[p["ask"]]
                ck(abs(exp - float(p["truth"])) < 1e-9, f"halflife s={s}: ค่าไม่ตรง")
            elif nm == "q_mirrors":
                k = 360 / p["th"]
                exp = k - 1 if p["ask"] == "count" else p["th"]
                ck(abs(exp - float(p["truth"])) < 1e-9, f"mirrors s={s}: ค่าไม่ตรง")
            elif nm == "q_bill":
                kwh = sum(w * c * h for _, w, c, h in p["rows"]) / 1000 * p["days"]
                ck(abs(kwh * p["rate"] - float(p["cost"])) < 1e-6, f"bill s={s}: ค่าไฟไม่ตรง")
            elif nm == "q_bil":
                wrongs = 0
                for i, txt in enumerate(p["out"]):
                    fac, real = p["stmts"][i]
                    claim = txt.split("แรงแม่เหล็กจะเป็น ")[1]
                    real_s = "F เท่าเดิม" if Fr(real) == 1 else f"{_fmt(Fr(real))}F"
                    wrongs += claim != real_s
                ck(wrongs == 1, f"bil s={s}: มีข้อความผิด {wrongs} ข้อ")
                ck(ans == p["out"][p["bad"]], f"bil s={s}: เฉลยไม่ใช่ข้อที่ผิด")
            elif nm == "q_shm":
                # จำลองการสั่นจริง นับครั้งที่ผ่าน x = 0
                T, cnt, tt = p["T"], 0, 0.0
                ph = math.pi / 2 if p["start"] == "edge" else 0.0
                dt = T / 4000
                prev = math.sin(ph)
                while cnt < p["n"]:
                    tt += dt
                    cur = math.sin(2 * math.pi * tt / T + ph)
                    if (prev > 0 >= cur) or (prev < 0 <= cur):
                        cnt += 1
                    prev = cur
                ck(abs(tt - float(p["t"])) < T / 500, f"shm s={s}: เวลาไม่ตรงกับการจำลอง {tt} vs {p['t']}")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:15]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ · {len(arch)} แนว · ตำแหน่งเฉลย {dict(sorted(pos.items()))}")
    for a, c in sorted(arch.items(), key=lambda kv: kv[0]):
        print(f"   {c:4d}  {a}")

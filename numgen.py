#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์พาร์ทที่ 1 แบบสุ่มตัวเลขจริง — แทนข้อที่เคยเขียนสดในโค้ด

**ทำไมต้องมีไฟล์นี้**
ติวเตอร์ทักว่าชีทชุดใหม่ "ไม่เปลี่ยนเลขเลยด้วยซ้ำ" ซึ่งจริง
วัดแล้วพบว่า 40 จาก 62 ข้อของพาร์ทที่ 1 เป็นคำถามเดิมเป๊ะไม่ว่าจะสั่งชุดไหน
เพราะเขียนโจทย์ไว้ตายตัวใน gen.py เปลี่ยนแค่ตัวลวงเท่านั้น
(พาร์ทที่ 2 ไม่มีปัญหานี้ เพราะรูปสุ่มใหม่ทุกครั้งอยู่แล้ว)

ไฟล์นี้ผลิตโจทย์แนวเดิมแบบสุ่มพารามิเตอร์ และผลิตแนวละหลายข้อ
เพื่อให้ `--set` มีของให้หมุนจริง ไม่ใช่วนกลับมาข้อเดิม

**แนวใหม่ที่เพิ่มเข้ามา** มาจากข้อสอบจริงปี 66 ที่ยังไม่เคยทำ
  รหัสดำ-ขาว   ทายรหัสจากคำใบ้ว่าถูกกี่ตัวถูกกี่ตำแหน่ง
  อนุกรมวันที่  ลำดับที่เดินทั้งวันและเดือนพร้อมกัน
  นับเส้นทาง    นับทางเดินบนตารางที่มีช่องต้องห้าม

ทุกข้อพิสูจน์คำตอบด้วยโค้ด (กติกาข้อ 1) รันไฟล์นี้ตรง ๆ = ตรวจตัวเอง
"""
from fractions import Fraction as F
import itertools
import random

import draw as D

TH_MONTH = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]


def _place(opts, truth, want):
    rest = [o for o in opts if o != truth]
    out = rest[:want] + [truth] + rest[want:]
    return out[:5], want


def _opts(truth, wrong, want, positive=True):
    out = [truth]
    for w in wrong:
        if w is None or w in out:
            continue
        if positive and isinstance(w, int) and w <= 0:
            continue
        out.append(w)
    if len(out) < 5:
        return None
    return _place(out[:6], truth, want)[0]


def _pack(arche, lvl, stem, truth, wrong, want, why, params=None, draw=None):
    """draw = ฟังก์ชันวาดรูป จะถูกเรียก *หลัง* ข้อผ่านแล้วเท่านั้น

    ถ้าวาดก่อนตรวจ ข้อที่ถูกทิ้งจะทิ้งไฟล์รูปค้างไว้ในโฟลเดอร์ img เป็นพัน ๆ ไฟล์
    """
    o = _opts(truth, wrong, want)
    if not o:
        return None
    return {"arche": arche, "lvl": lvl, "stem": stem, "why": why,
            "choices": [str(x) for x in o], "ansIdx": o.index(truth),
            "params": params or {}, "draw": draw}


# ================================================================ ลำดับตัวเลข
def q_seq(rng, want):
    """อนุกรมห้าแบบ สุ่มทั้งชนิดและตัวเลข — เดิมเขียนไว้ตายตัวสี่ข้อ"""
    kind = rng.choice(["arith", "geom", "diff2", "inter", "mul_add"])
    for _ in range(200):
        if kind == "arith":
            a0, d = rng.randint(3, 19), rng.randint(3, 12)
            xs = [a0 + d * i for i in range(5)]
            why = f"บวก {d} ทุกขั้น"
        elif kind == "geom":
            r = rng.choice([2, 3, 4])
            a0 = rng.choice([2, 3, 5, 7]) * r ** 3
            xs = [a0 // r ** i for i in range(5)]
            if xs[-1] < 1:
                continue
            why = f"หารด้วย {r} ทุกขั้น"
        elif kind == "diff2":
            a0, d0, dd = rng.randint(2, 9), rng.randint(1, 4), rng.randint(1, 4)
            xs, cur, step = [a0], a0, d0
            for _ in range(4):
                cur += step
                step += dd
                xs.append(cur)
            why = f"ผลต่างเพิ่มทีละ {dd} ขั้นถัดไปบวก {step}"
        elif kind == "inter":
            a0, da = rng.randint(3, 12), rng.randint(3, 8)
            b0, db = rng.randint(30, 60), rng.randint(4, 9)
            xs = []
            for i in range(4):
                xs.append(a0 + da * i)
                xs.append(b0 - db * i)
            if min(xs) < 1:
                continue
            why = f"อนุกรมซ้อนสองชุด ตำแหน่งคี่บวก {da} ตำแหน่งคู่ลบ {db}"
        else:
            a0, m, c = rng.randint(2, 6), rng.choice([2, 3]), rng.randint(1, 6)
            xs = [a0]
            for _ in range(4):
                xs.append(xs[-1] * m + c)
            why = f"คูณ {m} แล้วบวก {c} ทุกขั้น"
        ans = xs[-1]
        if ans <= 0 or ans > 5000 or len(set(xs)) < len(xs):
            continue
        shown = ", ".join(str(v) for v in xs[:-1]) + ", ?"
        step = max(1, abs(ans) // 9)
        wrong = [ans + step, ans - step, ans + 2 * step, ans - 2 * step,
                 xs[-2] + xs[-3] if len(xs) > 2 else None]
        return _pack("ลำดับ", 1 if kind in ("arith", "geom") else 2,
                     shown, ans, wrong, want, why, {"xs": xs, "kind": kind})
    return None


# ================================================================ เมทริกซ์ตัวเลข
def q_numgrid(rng, want, tag=0):
    """ตาราง 3 คอลัมน์ คอลัมน์ที่สามมาจากสองคอลัมน์แรกด้วยกฎเดียวกันทุกแถว"""
    rules = [("บวกกันแล้วคูณ {k}", lambda a, b, k: (a + b) * k),
             ("คูณกันแล้วลบ {k}", lambda a, b, k: a * b - k),
             ("ผลต่างยกกำลังสองบวก {k}", lambda a, b, k: (a - b) ** 2 + k),
             ("คอลัมน์แรกยกกำลังสองลบคอลัมน์ที่สอง คูณ {k}",
              lambda a, b, k: (a * a - b) * k)]
    for _ in range(300):
        name, f = rng.choice(rules)
        k = rng.randint(1, 4)
        rows = []
        for _ in range(3):
            a, b = rng.randint(2, 9), rng.randint(2, 9)
            v = f(a, b, k)
            if not (2 <= v <= 200):
                rows = []
                break
            rows.append([a, b, v])
        if len(rows) < 3:
            continue
        ans = rows[2][2]
        cells = [r[:] for r in rows]
        cells[2][2] = "?"
        step = max(1, abs(ans) // 8)
        wrong = [ans + step, ans - step, ans + 2 * step,
                 rows[2][0] + rows[2][1], rows[2][0] * rows[2][1]]
        return _pack("เมทริกซ์ตัวเลข", 2,
                     "จากตาราง ตัวเลขในช่อง ? คือข้อใด (ทุกแถวใช้กฎเดียวกัน)",
                     ans, wrong, want, "กฎคือ " + name.format(k=k),
                     {"rows": rows, "k": k, "name": name},
                     draw=lambda t: D.numgrid(cells, f"ngx{t}"))
    return None


# ================================================================ การดำเนินการสมมติ
def q_customop(rng, want):
    """นิยามตัวดำเนินการให้ แล้วถามค่าที่ต้องแทนซ้อนกันสองชั้น"""
    forms = [("{p}a − {q}b", lambda a, b, p, q: p * a - q * b),
             ("{p}a + {q}b", lambda a, b, p, q: p * a + q * b),
             ("a×b − {q}", lambda a, b, p, q: a * b - q),
             ("{p}(a + b)", lambda a, b, p, q: p * (a + b))]
    for _ in range(200):
        name, f = rng.choice(forms)
        p, q = rng.randint(2, 4), rng.randint(1, 5)
        a, b, c = (rng.randint(2, 9) for _ in range(3))
        inner = f(a, b, p, q)
        ans = f(inner, c, p, q)
        if not (1 <= inner <= 90) or not (1 <= ans <= 400):
            continue
        sym = rng.choice(["✦", "◆", "★", "▲", "●"])
        expr = name.format(p=p, q=q).replace("a", "a").replace("b", "b")
        step = max(1, abs(ans) // 8)
        wrong = [f(a, f(b, c, p, q), p, q), ans + step, ans - step, ans + 2 * step, inner]
        return _pack("การดำเนินการสมมติ", 2,
                     f"กำหนดให้  a {sym} b = {expr}\n"
                     f"จงหาค่าของ  ({a} {sym} {b}) {sym} {c}",
                     ans, wrong, want,
                     f"ทำวงเล็บในก่อน ได้ {inner} แล้วค่อยทำกับ {c}",
                     {"a": a, "b": b, "c": c, "p": p, "q": q, "name": name})
    return None


# ================================================================ มุมเข็มนาฬิกา
def q_clock(rng, want):
    """มุมระหว่างเข็มที่เวลาใดก็ได้ · เลือกนาทีที่ทำให้คำตอบเป็นจำนวนเต็ม"""
    for _ in range(300):
        h = rng.randint(1, 12)
        m = rng.choice([0, 10, 20, 30, 40, 50, 4, 8, 16, 24, 36, 44, 52])
        ang = abs((30 * h + 0.5 * m) - 6 * m)
        ang = min(ang, 360 - ang)
        if ang != int(ang) or ang == 0:
            continue
        ans = int(ang)
        wrong = [abs(30 * h - 6 * m) if abs(30 * h - 6 * m) != ans else None,
                 ans + 5, ans - 5, ans + 15, 360 - ans if 360 - ans != ans else None]
        return _pack("มุมเข็มนาฬิกา", 2,
                     f"เวลา {h:02d}:{m:02d} น. เข็มสั้นกับเข็มยาวทำมุมกันกี่องศา "
                     "(ตอบมุมที่เล็กกว่า)",
                     ans, wrong, want,
                     "เข็มสั้นเดิน 0.5 องศาต่อนาทีด้วย อย่าคิดว่ามันหยุดอยู่ที่เลขชั่วโมง",
                     {"h": h, "m": m})
    return None


# ================================================================ ความน่าจะเป็น
def q_prob(rng, want):
    """ทอดลูกเต๋าสองลูก ถามความน่าจะเป็นของผลรวม ตอบเป็นเศษส่วนอย่างต่ำ"""
    s = rng.randint(4, 10)
    cnt = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == s)
    ans = F(cnt, 36)
    fmt = lambda x: f"{x.numerator}/{x.denominator}"
    cand = [F(c, 36) for c in (cnt - 1, cnt + 1, cnt + 2, cnt - 2, 6)]
    wrong = [fmt(c) for c in cand if 0 < c < 1 and c != ans]
    return _pack("ความน่าจะเป็น", 2,
                 f"ทอดลูกเต๋าที่เที่ยงตรงสองลูกพร้อมกัน "
                 f"ความน่าจะเป็นที่ผลรวมของแต้มเท่ากับ {s} เป็นเท่าใด",
                 fmt(ans), wrong, want,
                 f"กรณีทั้งหมด 36 · ผลรวม {s} เกิดได้ {cnt} วิธี",
                 {"s": s, "cnt": cnt})


# ================================================================ รหัสดำ-ขาว (แนวใหม่)
def _pegs(guess, code):
    """คืน (ดำ, ขาว) — ดำคือถูกทั้งเลขและตำแหน่ง ขาวคือเลขถูกแต่ตำแหน่งผิด"""
    black = sum(1 for g, c in zip(guess, code) if g == c)
    common = sum(min(guess.count(d), code.count(d)) for d in set(guess))
    return black, common - black


def q_mastermind(rng, want, tag=0):
    """ทายรหัสจากคำใบ้ — แนวที่ข้อสอบจริงปี 66 ออก

    เลือกคำใบ้จนกว่าจะเหลือรหัสที่เข้าได้เพียงชุดเดียว พิสูจน์ด้วยการไล่ครบทุกรหัส
    """
    digits = list(range(1, 7))
    for _ in range(400):
        code = tuple(rng.sample(digits, 4))
        pool = [c for c in itertools.permutations(digits, 4)]
        clues = []
        for _ in range(4):
            g = tuple(rng.sample(digits, 4))
            if g == code or any(g == c[0] for c in clues):
                continue
            b, w = _pegs(g, code)
            clues.append((g, b, w))
            pool = [c for c in pool if _pegs(g, c) == (b, w)]
            if len(pool) == 1:
                break
        if len(pool) != 1 or len(clues) < 2:
            continue
        lines = "\n".join(f"    {' '.join(map(str, g))}   ดำ {b} · ขาว {w}"
                          for g, b, w in clues)
        ans = "".join(map(str, code))
        wrong, seen = [], {ans}
        for c in itertools.permutations(digits, 4):
            t = "".join(map(str, c))
            if t not in seen and sum(1 for x, y in zip(c, code) if x == y) >= 2:
                seen.add(t)
                wrong.append(t)
            if len(wrong) == 5:
                break
        return _pack("รหัสดำ-ขาว", 3,
                     "รหัสลับเป็นเลขโดด 4 ตัวที่ไม่ซ้ำกัน เลือกจาก 1 ถึง 6\n"
                     "การทายแต่ละครั้งได้ผลดังนี้ "
                     "(ดำ = เลขถูกและตำแหน่งถูก · ขาว = เลขถูกแต่ตำแหน่งผิด)\n"
                     + lines + "\nรหัสลับคือข้อใด",
                     ans, wrong, want,
                     "ตัดรหัสที่ขัดกับคำใบ้ทีละบรรทัด เริ่มจากบรรทัดที่ให้ข้อมูลมากที่สุด",
                     {"code": code, "clues": clues})
    return None


# ================================================================ อนุกรมวันที่ (แนวใหม่)
def q_dateseq(rng, want):
    """วันที่ที่เดินทั้งวันและเดือนพร้อมกัน — แนวที่ข้อสอบจริงปี 66 ออก"""
    for _ in range(200):
        d0, m0 = rng.randint(1, 6), rng.randint(1, 3)
        dd, dm = rng.randint(1, 3), rng.randint(1, 2)
        seq = []
        d, m, step = d0, m0, 1
        for i in range(5):
            seq.append((d, m))
            d += dd * step
            m += dm * step
            step += 1
        if seq[-1][1] > 12 or seq[-1][0] > 28:
            continue
        shown = "   ".join(f"{a} {TH_MONTH[b]}" for a, b in seq[:-1])
        ans = f"{seq[-1][0]} {TH_MONTH[seq[-1][1]]}"
        wrong, seen = [], {ans}
        for da, dm2 in ((0, 1), (1, 0), (dd, dm), (-dd, 0), (0, -dm)):
            t = f"{seq[-2][0] + da} {TH_MONTH[min(12, max(1, seq[-2][1] + dm2))]}"
            if t not in seen:
                seen.add(t)
                wrong.append(t)
        return _pack("อนุกรมวันที่", 3,
                     "จากความสัมพันธ์ต่อไปนี้ จงหาวันและเดือนถัดไป\n" + shown,
                     ans, wrong, want,
                     f"วันเพิ่มทีละ {dd} เท่าของลำดับขั้น เดือนเพิ่มทีละ {dm} เท่าของลำดับขั้น",
                     {"seq": seq, "dd": dd, "dm": dm})
    return None


# ================================================================ นับเส้นทางบนตาราง (แนวใหม่)
def q_paths(rng, want, tag=0):
    """นับเส้นทางเดินขวาหรือลงเท่านั้น บนตารางที่มีช่องต้องห้าม

    นับด้วยการไล่ตารางจริง จึงพิสูจน์คำตอบได้แน่นอน
    """
    for _ in range(400):
        R, C = rng.choice([(3, 4), (4, 4), (3, 5), (4, 5)])
        holes = set()
        for _ in range(rng.randint(1, 3)):
            r, c = rng.randrange(R), rng.randrange(C)
            if (r, c) not in ((0, 0), (R - 1, C - 1)):
                holes.add((r, c))
        dp = [[0] * C for _ in range(R)]
        dp[0][0] = 1
        for r in range(R):
            for c in range(C):
                if (r, c) in holes:
                    dp[r][c] = 0
                    continue
                if r:
                    dp[r][c] += dp[r - 1][c]
                if c:
                    dp[r][c] += dp[r][c - 1]
        ans = dp[R - 1][C - 1]
        if not (4 <= ans <= 60):
            continue
        step = max(1, ans // 6)
        wrong = [ans + step, ans - step, ans + 2 * step, ans - 2 * step, ans * 2]
        return _pack("นับเส้นทาง", 3,
                     "เดินจากช่องซ้ายบนไปช่องขวาล่าง โดยเดินได้เฉพาะไปทางขวาหรือลงล่าง\n"
                     "ห้ามผ่านช่องที่ระบายทึบ มีเส้นทางที่เป็นไปได้ทั้งหมดกี่เส้นทาง",
                     ans, wrong, want,
                     "ไล่เติมจำนวนเส้นทางทีละช่องจากซ้ายบน แต่ละช่องเท่ากับช่องบนบวกช่องซ้าย",
                     {"R": R, "C": C, "holes": sorted(holes), "ans": ans},
                     draw=lambda t: D.grid(R, C, filled=sorted(holes),
                                           name=f"pth{t}", cell=26))
    return None


# ================================================================ ตัวเลขผสมตัวอักษร
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def q_alnum(rng, want):
    """อนุกรมที่ตัวอักษรกับตัวเลขเดินคนละกฎ ต้องแยกสองเส้นออกจากกันก่อน

    เป็นแนวที่ระบุไว้ใน DIGEST ว่าข้อสอบจริงออก แต่โรงงานยังไม่เคยทำ
    """
    for _ in range(200):
        i0, di = rng.randint(0, 8), rng.randint(1, 4)
        n0, dn = rng.randint(2, 12), rng.randint(2, 7)
        mode = rng.choice(["add", "mul"])
        letters, nums = [], []
        for k in range(5):
            li = i0 + di * k
            if li >= 26:
                break
            letters.append(AZ[li])
            nums.append(n0 + dn * k if mode == "add" else n0 * (dn ** k))
        if len(letters) < 5 or nums[-1] > 3000:
            continue
        shown = ", ".join(f"{a}{b}" for a, b in zip(letters[:4], nums[:4])) + ", ?"
        ans = f"{letters[4]}{nums[4]}"
        wrong, seen = [], {ans}
        for dl, dv in ((1, 0), (0, 1), (-1, 0), (1, 1), (2, 0)):
            li = i0 + di * 4 + dl
            if not (0 <= li < 26):
                continue
            t = f"{AZ[li]}{nums[4] + dv * dn}"
            if t not in seen:
                seen.add(t)
                wrong.append(t)
        rule = f"บวก {dn}" if mode == "add" else f"คูณ {dn}"
        return _pack("ตัวเลขผสมตัวอักษร", 2,
                     "จากอนุกรมต่อไปนี้ ลำดับถัดไปคือข้อใด\n" + shown,
                     ans, wrong, want,
                     f"แยกสองเส้น ตัวอักษรข้ามทีละ {di} ตำแหน่ง ส่วนตัวเลข{rule}",
                     {"letters": letters, "nums": nums})
    return None


# ================================================================ เติมเครื่องหมาย
def q_fillop(rng, want):
    """ใส่เครื่องหมายลงในช่องว่างให้สมการเป็นจริง — ไล่ครบทุกแบบจึงพิสูจน์ได้ว่ามีคำตอบเดียว"""
    import itertools as _it
    ops = ["+", "−", "×"]
    ev = {"+": lambda a, b: a + b, "−": lambda a, b: a - b, "×": lambda a, b: a * b}
    for _ in range(400):
        a, b, c, d = (rng.randint(2, 9) for _ in range(4))
        good = []
        for combo in _it.product(ops, repeat=3):
            v = a
            for op, nxt in zip(combo, (b, c, d)):
                v = ev[op](v, nxt)
            good.append((combo, v))
        target = rng.choice(good)[1]
        hit = [k for k, v in good if v == target]
        if len(hit) != 1 or not (5 <= target <= 200):
            continue
        truth = " ".join(hit[0])
        wrong, seen = [], {truth}
        for k, v in good:
            t = " ".join(k)
            if t not in seen:
                seen.add(t)
                wrong.append(t)
            if len(wrong) == 5:
                break
        return _pack("เติมเครื่องหมาย", 3,
                     "เติมเครื่องหมายลงในช่องว่างตามลำดับ ให้ประโยคต่อไปนี้เป็นจริง\n"
                     f"    {a} __ {b} __ {c} __ {d} = {target}\n"
                     "(คิดตามลำดับจากซ้ายไปขวา ไม่ต้องคิดลำดับความสำคัญของเครื่องหมาย)",
                     truth, wrong, want,
                     "คิดซ้ายไปขวาเสมอ ไล่ลองทีละชุดจากชุดที่ทำให้ค่าใกล้เป้าหมายที่สุด",
                     {"a": a, "b": b, "c": c, "d": d, "target": target, "hit": hit})
    return None


# ================================================================ ปริศนาตัวอักษร
def q_letterseq(rng, want):
    """ลำดับตัวอักษรที่ระยะห่างเดินตามกฎ — เดิมเขียนไว้ตายตัวสามข้อ"""
    for _ in range(200):
        i0 = rng.randint(0, 5)
        g0, dg = rng.randint(1, 3), rng.randint(1, 2)
        idx, cur, gap = [i0], i0, g0
        for _ in range(4):
            cur += gap
            gap += dg
            idx.append(cur)
        if idx[-1] >= 26:
            continue
        shown = ", ".join(AZ[i] for i in idx[:4]) + ", ?"
        ans = AZ[idx[4]]
        wrong, seen = [], {ans}
        for off in (-2, -1, 1, 2, 3):
            j = idx[4] + off
            if 0 <= j < 26 and AZ[j] not in seen:
                seen.add(AZ[j])
                wrong.append(AZ[j])
        return _pack("ปริศนาตัวอักษร", 2,
                     "จากลำดับตัวอักษรต่อไปนี้ ตัวถัดไปคือข้อใด\n" + shown,
                     ans, wrong, want,
                     f"แปลงเป็นลำดับที่ก่อน ระยะห่างเริ่มที่ {g0} แล้วเพิ่มทีละ {dg}",
                     {"idx": idx})
    return None


GENS = [q_seq, q_numgrid, q_customop, q_clock, q_prob,
        q_mastermind, q_dateseq, q_paths,
        q_alnum, q_fillop, q_letterseq]
NEEDS_TAG = {"q_numgrid", "q_mastermind", "q_paths"}


def build(add, part, rng, per=6):
    """เติมโจทย์พาร์ทที่ 1 แบบสุ่มจริงเข้าคลัง

    per = จำนวนข้อต่อแนว ต้องมากกว่าเพดานต่อชีท (CAP) อย่างน้อยสองเท่า
    ไม่งั้น --set หมุนหาข้อใหม่ไม่ได้ ชีทชุดถัดไปจะซ้ำของเดิม
    """
    want = 0
    tag = 0
    for g in GENS:
        made = 0
        for _ in range(per * 40):
            r = (g(rng, want, tag) if g.__name__ in NEEDS_TAG else g(rng, want))
            tag += 1
            if not r:
                continue
            img = r["draw"](tag) if r.get("draw") else None
            add(part, r["arche"], r["stem"], r["choices"], r["ansIdx"],
                lvl=r["lvl"], why=r["why"], img=img)
            want = (want + 2) % 5
            made += 1
            if made >= per:
                break


# ================================================================ ตรวจตัวเอง
if __name__ == "__main__":
    import collections
    bad, n = [], 0
    pos, arch = collections.Counter(), collections.Counter()
    tag = 0

    def ck(ok, msg):
        if not ok:
            bad.append(msg)

    for s in range(200):
        rng = random.Random(s)
        for w in range(5):
            for g in GENS:
                r = (g(rng, w, tag) if g.__name__ in NEEDS_TAG else g(rng, w))
                tag += 1
                if not r:
                    continue
                n += 1
                pos[r["ansIdx"]] += 1
                arch[r["arche"]] += 1
                ch = r["choices"]
                ck(len(set(ch)) == 5, f"{g.__name__} s={s}: ตัวเลือกซ้ำ {ch}")
                ck(r["ansIdx"] == w, f"{g.__name__} s={s}: บังคับตำแหน่งเฉลยไม่ได้")
                ck(bool(r["why"]) and len(r["why"]) <= 90,
                   f"{g.__name__}: บรรทัดแนวคิดหายหรือยาวเกิน")
                p = r["params"]
                got = ch[r["ansIdx"]]
                if g.__name__ == "q_seq":
                    ck(str(p["xs"][-1]) == got, f"ลำดับ s={s}: เฉลยไม่ใช่พจน์ถัดไป")
                elif g.__name__ == "q_clock":
                    a = abs((30 * p["h"] + 0.5 * p["m"]) - 6 * p["m"])
                    ck(str(int(min(a, 360 - a))) == got, f"นาฬิกา s={s}: มุมไม่ตรง")
                elif g.__name__ == "q_prob":
                    ck(F(got) == F(p["cnt"], 36), f"ความน่าจะเป็น s={s}: ค่าไม่ตรง")
                elif g.__name__ == "q_mastermind":
                    code = p["code"]
                    ck("".join(map(str, code)) == got, f"รหัส s={s}: เฉลยไม่ใช่รหัสจริง")
                    hit = [c for c in itertools.permutations(range(1, 7), 4)
                           if all(_pegs(gg, c) == (b, ww) for gg, b, ww in p["clues"])]
                    ck(len(hit) == 1, f"รหัส s={s}: มีรหัสที่เข้าได้ {len(hit)} ชุด")
                elif g.__name__ == "q_paths":
                    ck(str(p["ans"]) == got, f"นับเส้นทาง s={s}: จำนวนไม่ตรง")
                elif g.__name__ == "q_alnum":
                    ck(f'{p["letters"][4]}{p["nums"][4]}' == got,
                       f"ตัวเลขผสมตัวอักษร s={s}: เฉลยไม่ตรง")
                elif g.__name__ == "q_fillop":
                    ck(len(p["hit"]) == 1, f"เติมเครื่องหมาย s={s}: มีคำตอบมากกว่าหนึ่งชุด")
                    ck(" ".join(p["hit"][0]) == got, f"เติมเครื่องหมาย s={s}: เฉลยไม่ตรง")
                elif g.__name__ == "q_letterseq":
                    ck(AZ[p["idx"][4]] == got, f"ปริศนาตัวอักษร s={s}: เฉลยไม่ตรง")

    for k in range(5):
        if pos.get(k, 0) == 0:
            bad.append(f"ไม่มีข้อไหนเฉลยเป็นตัวเลือกที่ {k + 1} เลย")

    if bad:
        print("ไม่ผ่าน", len(bad), "กรณี")
        for b in bad[:12]:
            print(" ", b)
        raise SystemExit(1)
    print(f"ตรวจผ่าน {n} ข้อ · {len(arch)} แนว")
    print("แนว:", ", ".join(sorted(arch)))

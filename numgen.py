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


NL = chr(10)      # เขียนเป็น chr เพราะสคริปต์แพตช์ที่ผ่าน heredoc กิน backslash


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
            a0, d = rng.randint(5, 40), rng.randint(4, 19)
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
            # ช่วงเดิมแคบเกิน (128 แบบ) ชุดต่างกันจึงชนกันได้ง่าย และได้อนุกรมง่ายอย่าง 3 4 6 9
            a0, d0, dd = rng.randint(2, 24), rng.randint(2, 9), rng.randint(2, 7)
            xs, cur, step = [a0], a0, d0
            last = d0
            for _ in range(4):
                last = step                      # ผลต่างที่ใช้จริงในการข้ามไปพจน์สุดท้าย
                cur += step
                step += dd
                xs.append(cur)
            # เดิมใช้ step ซึ่งถูกบวกเกินไปอีกหนึ่งรอบแล้ว บรรทัดแนวคิดจึงบอกผลต่างผิดไป dd
            why = f"ผลต่างเพิ่มทีละ {dd} ขั้นถัดไปบวก {last}"
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
        # ตัวลวงต้องไม่เกิน 180 เพราะโจทย์บอกให้ตอบมุมที่เล็กกว่า
        # ถ้าปล่อยให้เกิน เด็กตัดตัวเลือกนั้นทิ้งได้ทันทีโดยไม่ต้องคิด
        naive = abs(30 * h - 6 * m)                  # ลืมว่าเข็มสั้นก็เดิน
        naive = min(naive, 360 - naive)
        cand = [naive, ans + 5, ans - 5, ans + 15, ans - 15, ans + 30]
        wrong = [c for c in cand if c is not None and 0 < c <= 180 and c != ans]
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


# ================================================================ อนุกรมกลับหลักตัวเลข
def q_revseq(rng, want):
    """พจน์จริงเป็นกำลังสองหรือกำลังสาม แต่พิมพ์กลับหลัก ต้องกลับก่อนถึงเห็นกฎ

    ถอดมาจากข้อสอบจริงที่ติวเตอร์ส่งมา เป็นแนวที่ "เปลี่ยนมุมมองก่อน" ไม่ใช่ "คำนวณหนัก"
    ห้ามให้พจน์ลงท้ายด้วยศูนย์ เพราะกลับหลักแล้วจะมีศูนย์นำ ทำให้กำกวม
    """
    for _ in range(300):
        p = rng.choice([2, 2, 3])
        n0 = rng.randint(4, 9) if p == 2 else rng.randint(3, 5)
        vals = [(n0 + i) ** p for i in range(6)]
        if any(v % 10 == 0 or v < 10 for v in vals):
            continue
        shown = [int(str(v)[::-1]) for v in vals]
        if len(set(shown)) < 6:
            continue
        ans = shown[5]
        body = ", ".join(str(v) for v in shown[:5]) + ", ?"
        wrong = [vals[5], shown[4] + (shown[4] - shown[3]),
                 int(str((n0 + 6) ** p)[::-1]), ans + 9, abs(ans - 9)]
        return _pack("อนุกรมกลับหลัก", 3,
                     "จากอนุกรมต่อไปนี้ ตัวเลขถัดไปคือข้อใด\n" + body,
                     ans, wrong, want,
                     f"กลับหลักทุกพจน์ก่อน จะได้กำลัง{'สอง' if p == 2 else 'สาม'}เรียงกัน",
                     {"vals": vals, "shown": shown, "p": p, "n0": n0})
    return None


# ================================================================ สัญลักษณ์แทนตัวเลข
SHAPES = ["star", "diamond", "tri", "circle", "square"]


def q_symsum(rng, want, tag=0):
    """ตารางสัญลักษณ์ มีผลรวมกำกับสามแถว ถามผลรวมของแถวที่สี่

    ต้องพิสูจน์ว่าค่าของสัญลักษณ์ถูกกำหนดได้ค่าเดียวจากสามสมการ
    ไล่ค่าทุกชุดในช่วงที่ใช้จริง ถ้าเจอมากกว่าหนึ่งชุดให้ทิ้งโจทย์นั้น
    """
    for _ in range(500):
        kinds = rng.sample(SHAPES, 3)
        rows = [[rng.choice(kinds) for _ in range(4)] for _ in range(4)]
        if any(len(set(r)) == 1 for r in rows):
            continue
        val = {k: rng.randint(2, 12) for k in kinds}
        if len(set(val.values())) < 3:
            continue
        tot = [sum(val[c] for c in r) for r in rows]
        # ค่าของสัญลักษณ์ต้องถูกบังคับได้ชุดเดียวจากสามแถวแรก
        hits = []
        for a in range(2, 13):
            for b in range(2, 13):
                for c in range(2, 13):
                    cand = dict(zip(kinds, (a, b, c)))
                    if all(sum(cand[x] for x in rows[i]) == tot[i] for i in range(3)):
                        hits.append(cand)
        if len(hits) != 1:
            continue
        ans = tot[3]
        step = max(1, ans // 8)
        wrong = [ans + step, ans - step, ans + 2 * step, tot[0], tot[2]]
        return _pack("สัญลักษณ์แทนตัวเลข", 3,
                     "ตัวเลขท้ายแถวคือผลรวมของสัญลักษณ์ในแถวนั้น\n"
                     "สัญลักษณ์เดียวกันมีค่าเท่ากันเสมอ ผลรวมของแถวสุดท้ายคือข้อใด",
                     ans, wrong, want,
                     "ตั้งสมการจากสามแถวแรก แก้หาค่าของแต่ละสัญลักษณ์ก่อน",
                     {"rows": rows, "tot": tot, "val": val, "kinds": kinds},
                     draw=lambda t: D.symgrid(rows, tot[:3] + [None], f"sym{t}"))
    return None


# ================================================================ อนุกรมอักษรไทยผสมอังกฤษ
THAI = list("กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ")


def q_thaieng(rng, want):
    """อักษรไทยเดินไปข้างหน้า อักษรอังกฤษเดินถอยหลัง คนละอัตรา

    แนวนี้เจอในข้อสอบจริงที่ติวเตอร์ส่งมา จุดยากคือต้องแยกสองเส้นออกจากกันก่อน
    """
    for _ in range(200):
        ti, dt = rng.randint(0, 6), rng.randint(1, 3)
        ei, de = rng.randint(18, 25), rng.randint(1, 3)
        pairs = []
        for k in range(6):
            t, e = ti + dt * k, ei - de * k
            if t >= len(THAI) or e < 0:
                break
            pairs.append(THAI[t] + AZ[e])
        if len(pairs) < 6:
            continue
        ans = pairs[5]
        body = "   ".join(pairs[:5]) + "   ?"
        wrong, seen = [], {ans}
        for dtt, dee in ((1, 0), (0, 1), (-1, 0), (1, 1), (0, -1)):
            t, e = ti + dt * 5 + dtt, ei - de * 5 + dee
            if 0 <= t < len(THAI) and 0 <= e < 26:
                cand = THAI[t] + AZ[e]
                if cand not in seen:
                    seen.add(cand)
                    wrong.append(cand)
        return _pack("อนุกรมอักษรไทยผสมอังกฤษ", 3,
                     "จากอนุกรมต่อไปนี้ ลำดับถัดไปคือข้อใด\n" + body,
                     ans, wrong, want,
                     f"แยกสองเส้น อักษรไทยข้ามทีละ {dt} ตัว อักษรอังกฤษถอยหลังทีละ {de} ตัว",
                     {"pairs": pairs, "dt": dt, "de": de})
    return None


# ================================================================ ตรรกะจริง-เท็จแบบกำหนดจำนวน
NAMES = ["กร", "ขวัญ", "คราม", "ชมพู่", "จินนี่", "ดาว", "ตูน"]


def q_liarcount(rng, want, n=5):
    """บอกจำนวนคนที่พูดจริง แล้วให้หาว่าใครบ้าง

    ต่างจากแบบเดิมที่ไม่บอกจำนวน การบอกจำนวนทำให้ตัดกรณีได้เร็วขึ้น
    แต่ต้องคุมให้เหลือคำตอบชุดเดียวจริง ๆ จึงต้องไล่ครบทุกการจัดสรร
    """
    import itertools as _it
    who = NAMES[:n]
    for _ in range(600):
        k = rng.randint(2, n - 2)
        claims = []
        for i in range(n):
            j = rng.choice([x for x in range(n) if x != i])
            claims.append((i, j, rng.random() < .5))      # i พูดว่า j พูดจริง/โกหก
        ok = []
        for mask in _it.product([False, True], repeat=n):
            if sum(mask) != k:
                continue
            good = True
            for i, j, says_true in claims:
                stated = (mask[j] == says_true)
                if mask[i] != stated:
                    good = False
                    break
            if good:
                ok.append(mask)
        if len(ok) != 1:
            continue
        truth = ", ".join(who[i] for i in range(n) if ok[0][i])
        lines = "\n".join(
            f"    {who[i]} บอกว่า {who[j]}พูด{'ความจริง' if t else 'โกหก'}"
            for i, j, t in claims)
        wrong, seen = [], {truth}
        for combo in _it.combinations(range(n), k):
            t = ", ".join(who[i] for i in combo)
            if t not in seen:
                seen.add(t)
                wrong.append(t)
            if len(wrong) == 5:
                break
        return _pack("ตรรกะจริง-เท็จ", 3,
                     f"ในกลุ่มนี้มีคนพูดความจริงเสมอ {k} คน ที่เหลือพูดโกหกเสมอ\n"
                     + lines + "\nคนที่พูดความจริงคือใครบ้าง",
                     truth, wrong, want,
                     f"ไล่ทุกแบบที่มีคนพูดจริง {k} คน แล้วตัดแบบที่ขัดกับคำพูดของตัวเอง",
                     {"claims": claims, "k": k, "n": n, "ok": ok[0], "who": who})
    return None


# ================================================================ ปริศนาสามเหลี่ยม
def q_tripuz(rng, want, tag=0):
    """สามเหลี่ยมสามรูป มุมสามค่ากับค่ากลาง ใช้กฎเดียวกันทุกรูป"""
    rules = [("ผลบวกมุมสามข้างคูณ {k}", lambda a, b, c, k: (a + b + c) * k),
             ("ผลคูณสองค่าแรกลบค่าที่สาม แล้วคูณ {k}", lambda a, b, c, k: (a * b - c) * k),
             ("ผลบวกสองค่าแรกคูณค่าที่สาม หารด้วย {k}",
              lambda a, b, c, k: (a + b) * c // k)]
    for _ in range(400):
        name, f = rng.choice(rules)
        k = rng.randint(1, 4)
        tris = []
        for _ in range(3):
            a, b, c = (rng.randint(2, 9) for _ in range(3))
            if "หารด้วย" in name and ((a + b) * c) % k:
                tris = []
                break
            v = f(a, b, c, k)
            if not (3 <= v <= 200):
                tris = []
                break
            tris.append((a, b, c, v))
        if len(tris) < 3:
            continue
        ans = tris[2][3]
        step = max(1, ans // 8)
        wrong = [ans + step, ans - step, ans + 2 * step,
                 tris[2][0] + tris[2][1] + tris[2][2], tris[0][3]]
        cells = [list(t) for t in tris]
        cells[2][3] = "?"
        return _pack("ปริศนาเรขาคณิต", 2,
                     "สามเหลี่ยมทั้งสามรูปใช้กฎเดียวกัน ตัวเลขในช่อง ? คือข้อใด",
                     ans, wrong, want, "กฎคือ " + name.format(k=k),
                     {"tris": tris, "k": k},
                     draw=lambda t: D.compose(
                         [D.tri(tuple(c), f"trx{t}_{i}") for i, c in enumerate(cells)],
                         f"trq{t}", seps=["", ""], gap=20))
    return None


# ================================================================ โจทย์ปัญหา
def q_work(rng, want):
    """งานร่วมกัน — อัตราทำงานบวกกันได้ เลือกเลขที่ผลลัพธ์ลงตัว"""
    for _ in range(300):
        a, b = rng.sample([3, 4, 6, 8, 12, 15, 20, 24], 2)
        num, den = a * b, a + b
        if num % den:
            continue
        ans = num // den
        wrong = [a + b, (a + b) // 2, abs(a - b), ans + 1, ans * 2]
        return _pack("โจทย์ปัญหาคณิต", 2,
                     f"คนแรกทำงานชิ้นหนึ่งเสร็จใน {a} วัน คนที่สองทำงานชิ้นเดียวกันเสร็จใน {b} วัน\n"
                     "ถ้าช่วยกันทำตั้งแต่ต้น จะเสร็จในกี่วัน",
                     ans, wrong, want,
                     f"อัตราบวกกัน 1/{a} + 1/{b} แล้วกลับเศษเป็นส่วน",
                     {"a": a, "b": b})
    return None


def q_avgspeed(rng, want):
    """อัตราเร็วเฉลี่ยไป-กลับ คือค่าเฉลี่ยฮาร์มอนิก ไม่ใช่ค่าเฉลี่ยเลขคณิต"""
    for _ in range(300):
        u, v = rng.sample([20, 30, 40, 50, 60, 80, 100, 120], 2)
        num, den = 2 * u * v, u + v
        if num % den:
            continue
        ans = num // den
        trap = (u + v) // 2
        if ans == trap:
            continue
        wrong = [trap, ans + 2, ans - 2, u, v]
        return _pack("โจทย์ปัญหาคณิต", 2,
                     f"รถวิ่งจากเมือง A ไปเมือง B ด้วยอัตราเร็ว {u} กิโลเมตรต่อชั่วโมง\n"
                     f"แล้ววิ่งกลับเส้นทางเดิมด้วยอัตราเร็ว {v} กิโลเมตรต่อชั่วโมง\n"
                     "อัตราเร็วเฉลี่ยตลอดการเดินทางไป-กลับเป็นกี่กิโลเมตรต่อชั่วโมง",
                     ans, wrong, want,
                     f"ระยะเท่ากันให้ใช้ 2uv/(u+v) · ตอบ {trap} คือเฉลี่ยแบบผิด",
                     {"u": u, "v": v})
    return None


# ================================================================ เชาวน์ปัญญา
def q_cutlog(rng, want):
    """จำนวนรอยตัดน้อยกว่าจำนวนท่อนหนึ่งเสมอ และช่วงพักน้อยกว่าจำนวนรอยตัดอีกหนึ่ง"""
    for _ in range(200):
        piece = rng.choice([2, 3, 4])
        parts = rng.randint(4, 8)
        L = piece * parts
        cut, rest = rng.choice([3, 4, 5, 6]), rng.choice([1, 2, 3])
        cuts = parts - 1
        ans = cuts * cut + (cuts - 1) * rest
        wrong = [parts * cut + parts * rest, cuts * cut, parts * cut,
                 ans + cut, ans - rest]
        return _pack("เชาวน์ปัญญา", 2,
                     f"ท่อนไม้ยาว {L} เมตร ตัดออกเป็นท่อนย่อยยาวท่อนละ {piece} เมตร\n"
                     f"การตัดหนึ่งครั้งใช้เวลา {cut} นาที และต้องพัก {rest} นาทีระหว่างการตัดแต่ละครั้ง\n"
                     "ตั้งแต่เริ่มตัดครั้งแรกจนตัดครั้งสุดท้ายเสร็จ ใช้เวลาทั้งหมดกี่นาที",
                     ans, wrong, want,
                     f"ได้ {parts} ท่อนใช้การตัดแค่ {cuts} ครั้ง และพักแค่ {cuts - 1} ช่วง",
                     {"L": L, "piece": piece, "cut": cut, "rest": rest, "parts": parts})
    return None


# ================================================================ หน่วยและการประมาณค่า
def q_unit(rng, want):
    """ปริมาตรทรงกระบอกแล้วเปลี่ยนหน่วยเป็นลิตร จุดพลาดอยู่ที่การเปลี่ยนหน่วย"""
    for _ in range(200):
        r_cm = rng.choice([10, 20, 25, 30, 40, 50])
        h_cm = rng.choice([50, 60, 80, 100, 120])
        vol = 314 * r_cm * r_cm * h_cm // 100          # ใช้ pi = 3.14
        if vol % 1000:
            continue
        ans = vol // 1000
        wrong = [ans * 10, ans // 10 if ans >= 10 else None, ans * 2,
                 ans + 20, vol // 100]
        return _pack("หน่วยและการประมาณค่า", 2,
                     f"ถังทรงกระบอกรัศมี {r_cm} เซนติเมตร สูง {h_cm} เซนติเมตร\n"
                     "บรรจุน้ำได้เต็มถังพอดี จะบรรจุน้ำได้ประมาณกี่ลิตร (ใช้ pi ประมาณ 3.14)",
                     ans, wrong, want,
                     "หาปริมาตรเป็นลูกบาศก์เซนติเมตรก่อน แล้วหารพัน เพราะพันลูกบาศก์เซนติเมตรเท่ากับหนึ่งลิตร",
                     {"r": r_cm, "h": h_cm, "vol": vol})
    return None


# ================================================================ เติบโตแบบทวีคูณ
def q_double(rng, want):
    """แบ่งตัวเป็นสองเท่าทุกช่วงเวลา ถามเวลาที่ต้องใช้ ไม่ใช่ถามจำนวน

    ถามเวลาทำให้ยากกว่าถามจำนวน เพราะต้องถอยกลับจากกำลังสอง
    """
    for _ in range(200):
        per = rng.choice([2, 3, 4, 5])
        k = rng.randint(3, 6)
        mult = 2 ** k
        t0 = per * rng.randint(2, 5)
        ans = t0 + per * k
        wrong = [t0 * mult, t0 + k, t0 * k, ans + per, ans - per]
        return _pack("เติบโตแบบทวีคูณ", 3,
                     f"แบคทีเรียชนิดหนึ่งแบ่งตัวจาก 1 ตัวเป็น 2 ตัวทุก ๆ {per} วินาที\n"
                     f"เริ่มจากแบคทีเรีย 1 ตัว ใช้เวลา {t0} วินาทีจึงเต็มขวดโหลใบหนึ่งพอดี\n"
                     f"ถ้าต้องการให้ได้จำนวนเท่ากับ {mult} ขวดโหล ต้องใช้เวลาทั้งหมดกี่วินาที",
                     ans, wrong, want,
                     f"เพิ่ม {mult} เท่าคือแบ่งตัวอีก {k} รอบ ใช้เวลาเพิ่ม {per} x {k} วินาที",
                     {"per": per, "k": k, "t0": t0, "mult": mult})
    return None


# ================================================================ รหัสเลื่อนอักษร
def q_caesar(rng, want):
    """เลื่อนอักษรทีละตำแหน่งไม่เท่ากัน ยากกว่าการเลื่อนคงที่"""
    for _ in range(200):
        words = ["MOUSE", "PLANT", "CHAIR", "BRICK", "STONE", "CLOUD", "GRAPE"]
        w = rng.choice(words)
        mode = rng.choice(["fix", "ramp"])
        d0 = rng.randint(1, 4)
        if mode == "fix":
            enc = "".join(AZ[(AZ.index(c) + d0) % 26] for c in w)
            why = f"เลื่อนไปข้างหน้าทีละ {d0} ตำแหน่งเท่ากันทุกตัว"
        else:
            enc = "".join(AZ[(AZ.index(c) + d0 + i) % 26] for i, c in enumerate(w))
            why = f"ตัวแรกเลื่อน {d0} แล้วเพิ่มทีละ 1 ในตัวถัดไป"
        w2 = rng.choice([x for x in words if x != w])
        if mode == "fix":
            ans = "".join(AZ[(AZ.index(c) + d0) % 26] for c in w2)
        else:
            ans = "".join(AZ[(AZ.index(c) + d0 + i) % 26] for i, c in enumerate(w2))
        wrong, seen = [], {ans}
        for off in (1, -1, 2, -2, 3):
            cand = "".join(AZ[(AZ.index(c) + off) % 26] for c in w2)
            if cand not in seen:
                seen.add(cand)
                wrong.append(cand)
        return _pack("ปริศนาตัวอักษร", 2,
                     f"ถ้า {w} เขียนเป็นรหัสว่า {enc}\nแล้ว {w2} จะเขียนเป็นรหัสว่าอย่างไร",
                     ans, wrong, want, why, {"w": w, "enc": enc, "w2": w2,
                                             "mode": mode, "d0": d0})
    return None



# ================================================================ อุปมาอุปไมยตัวเลข
# ที่มา: ชุดที่ 8 ข้อ 5 — กฎไม่ได้อยู่ที่ตัวเลขทั้งจำนวน แต่อยู่ที่หลักแต่ละหลัก
ANA = {
    "mulsum":  (lambda a, b: f"{a*b}{a+b}",      "คูณสองหลักได้เลขตัวหน้า บวกสองหลักได้เลขตัวหลัง"),
    "summul":  (lambda a, b: f"{a+b}{a*b}",      "บวกสองหลักได้เลขตัวหน้า คูณสองหลักได้เลขตัวหลัง"),
    "sqsq":    (lambda a, b: f"{a*a}{b*b}",      "ยกกำลังสองทีละหลักแล้วเขียนต่อกัน"),
    "diffsum": (lambda a, b: f"{abs(a-b)}{a+b}", "ลบสองหลักได้เลขตัวหน้า บวกสองหลักได้เลขตัวหลัง"),
    "sumdiff": (lambda a, b: f"{a+b}{abs(a-b)}", "บวกสองหลักได้เลขตัวหน้า ลบสองหลักได้เลขตัวหลัง"),
}


def _ana(key, x):
    return ANA[key][0](x // 10, x % 10)


def q_analogy(rng, want):
    """สามคู่ตัวอย่างสอนกฎ คู่ที่สี่ถาม — ถามตัวตั้งหรือถามผลลัพธ์ก็ได้

    ต้องยืนยันสองชั้น
      1. มีกฎเดียวในคลังที่เข้ากับตัวอย่างทั้งสามคู่ ไม่งั้นถอดกฎได้หลายทาง
      2. ถ้าถามตัวตั้ง ต้องมีเลขสองหลักเดียวที่ให้ผลลัพธ์นั้น ไม่งั้นมีคำตอบถูกหลายข้อ
    """
    for _ in range(300):
        key = rng.choice(list(ANA))
        pool = [v for v in range(11, 99) if v % 10]
        rng.shuffle(pool)
        picks = pool[:4]
        outs = [_ana(key, v) for v in picks]
        if len(set(outs)) < 4:
            continue
        fits = [k for k in ANA
                if all(_ana(k, v) == o for v, o in zip(picks[:3], outs[:3]))]
        if fits != [key]:
            continue
        back = rng.random() < .5
        tgt, ans_in = picks[3], outs[3]
        pairs = [f"{v}  :  {o}" for v, o in zip(picks[:3], outs[:3])]
        if back:
            if [v for v in range(10, 100) if _ana(key, v) == ans_in] != [tgt]:
                continue
            truth = tgt
            wrong = []
            for k2 in ANA:
                if k2 == key:
                    continue
                hit = [v for v in range(10, 100) if _ana(k2, v) == ans_in]
                if hit:
                    wrong.append(hit[0])
            wrong += [tgt % 10 * 10 + tgt // 10, tgt + 9, tgt - 9, tgt + 11]
            tail = f"    ?  :  {ans_in}"
        else:
            truth = int(ans_in)
            wrong = [int(_ana(k2, tgt)) for k2 in ANA if k2 != key]
            wrong += [truth + 10, truth - 10]
            tail = f"    {tgt}  :  ?"
        stem = ("จากความสัมพันธ์ต่อไปนี้" + NL + "    " +
                (NL + "    ").join(pairs) + NL + tail + NL +
                "เครื่องหมาย ? แทนจำนวนใด")
        return _pack("อุปมาอุปไมยตัวเลข", 3, stem, truth, wrong, want,
                     "กฎอยู่ที่หลักแต่ละหลัก · " + ANA[key][1],
                     params={"key": key, "picks": picks, "back": back})
    return None


# ================================================================ อนุกรมสลับสองชุด
def q_interleave(rng, want):
    """ตำแหน่งคี่กับตำแหน่งคู่เป็นคนละอนุกรม (ชุดที่ 8 ข้อ 3)

    ตัวลวงหลักคือเอากฎของอีกชุดมาต่อ ซึ่งเป็นความผิดพลาดที่เกิดขึ้นจริงตอนทำ
    """
    for _ in range(300):
        ka = rng.choice(["dbl", "dbp", "trm"])
        a0 = rng.randint(2, 9)
        A = [a0]
        for _ in range(4):
            if ka == "dbl":
                A.append(A[-1] * 2 - 1)
            elif ka == "dbp":
                A.append(A[-1] * 2 + 1)
            else:
                A.append(A[-1] * 3 - 2)
        wa = {"dbl": "คูณสองแล้วลบหนึ่ง", "dbp": "คูณสองแล้วบวกหนึ่ง",
              "trm": "คูณสามแล้วลบสอง"}[ka]
        b0, db = rng.randint(3, 15), rng.randint(2, 9)
        B = [b0 + db * i for i in range(4)]
        if A[-1] > 4000 or len(set(A) & set(B)) > 1:
            continue
        shown = [A[0], B[0], A[1], B[1], A[2], B[2], A[3], B[3]]
        if len(set(shown)) < 8:
            continue
        truth = A[4]
        wrong = [B[3] + db, shown[-1] + db, A[3] * 2, A[3] + A[2],
                 truth + db, truth - 1, A[3] * 2 + 1]
        stem = ("จงหาพจน์ถัดไปของลำดับต่อไปนี้" + NL + "    " +
                ", ".join(str(v) for v in shown) + ", ...")
        return _pack("อนุกรมสลับสองชุด", 3, stem, truth, wrong, want,
                     f"แยกเป็นสองชุด ชุดตำแหน่งคี่{wa} ชุดตำแหน่งคู่บวก {db}",
                     params={"ka": ka, "db": db})
    return None


# ================================================================ พีชคณิตแปลก
def q_funceq(rng, want):
    """สมการฟังก์ชัน — แทน x ด้วย k ลบ x อีกรอบ จะได้สมการสองตัวแปรแล้วแก้ได้

    a*f(x) + b*f(k-x) = p*x + q
    แทน x ด้วย k-x:  a*f(k-x) + b*f(x) = p*(k-x) + q
    คูณไขว้แล้วลบกัน จะได้ (a*a - b*b) * f(x) = a*(p*x+q) - b*(p*(k-x)+q)
    เรารับเฉพาะชุดที่ f ที่จุดที่ถามออกมาเป็นจำนวนเต็ม จึงตอบเป็นเลขสวยเสมอ
    """
    from fractions import Fraction
    for _ in range(400):
        a = rng.randint(1, 4)
        b = rng.randint(1, 4)
        if a == b or a * a == b * b:
            continue
        k = rng.randint(3, 12)
        p = rng.randint(1, 6)
        q = rng.randint(-8, 8)
        t = rng.randint(1, k - 1)
        num = Fraction(a * (p * t + q) - b * (p * (k - t) + q), a * a - b * b)
        if num.denominator != 1:
            continue
        truth = int(num)
        other = Fraction(a * (p * (k - t) + q) - b * (p * t + q), a * a - b * b)
        wrong = [truth + 1, truth - 1, p * t + q, int(other) if other.denominator == 1 else None,
                 truth * 2, truth + k, p * t]
        lhs = (f"{a} f(x)" if a != 1 else "f(x)")
        rhs = (f"{b} f({k} - x)" if b != 1 else f"f({k} - x)")
        sign = "+" if q >= 0 else "-"
        stem = (f"กำหนดให้ {lhs} + {rhs} = {p}x {sign} {abs(q)} สำหรับทุกจำนวนจริง x" + NL +
                f"จงหาค่าของ f({t})")
        return _pack("สมการฟังก์ชัน", 3, stem, truth, wrong, want,
                     f"แทน x ด้วย {k} - x อีกครั้ง จะได้สองสมการแล้วกำจัด f({k} - x) ทิ้ง",
                     params={"a": a, "b": b, "k": k, "p": p, "q": q, "t": t})
    return None


def q_nestrad(rng, want):
    """รากซ้อนไม่รู้จบ — ตั้ง y แทนค่าทั้งก้อนแล้วยกกำลังสอง จะได้สมการกำลังสอง

    เครื่องหมายบวก  y กำลังสอง = k + y  จึงเลือก k = y*y - y
    เครื่องหมายลบ   y กำลังสอง = k - y  จึงเลือก k = y*y + y
    คำตอบเป็นจำนวนเต็มพอดีทั้งสองแบบ จึงพิสูจน์ได้เป๊ะ
    เขียนคำว่า "รากที่สองของ" เป็นตัวอักษร เพราะฟอนต์ชีทไม่มีเครื่องหมายกรณฑ์
    """
    y = rng.randint(3, 9)
    plus = rng.random() < .5
    k = y * y - y if plus else y * y + y
    sign = "บวก" if plus else "ลบ"
    truth = y
    wrong = [y + 1, y - 1, k, k // 2, y * y, y + 2, k - y]
    stem = ("จงหาค่าของจำนวนจริงบวกที่เขียนเป็นรากซ้อนกันไปไม่รู้จบดังนี้" + NL +
            f"    รากที่สองของ ( {k} {sign} รากที่สองของ ( {k} {sign} "
            f"รากที่สองของ ( {k} {sign} ... ) ) )")
    return _pack("รากซ้อนไม่รู้จบ", 3, stem, truth, wrong, want,
                 f"ตั้ง y แทนทั้งก้อน จะได้ y ยกกำลังสอง = {k} {sign} y",
                 params={"y": y, "k": k, "plus": plus})


GENS = [q_seq, q_numgrid, q_customop, q_clock, q_prob,
        q_mastermind, q_dateseq, q_paths,
        q_alnum, q_fillop, q_letterseq,
        q_revseq, q_symsum, q_thaieng, q_liarcount,
        q_tripuz, q_work, q_avgspeed, q_cutlog, q_unit, q_double, q_caesar,
        q_analogy, q_interleave, q_funceq, q_nestrad]
NEEDS_TAG = {"q_numgrid", "q_mastermind", "q_paths", "q_symsum", "q_tripuz"}


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
                    if p["kind"] == "diff2":
                        # บรรทัดแนวคิดต้องบอกผลต่างจริงของขั้นสุดท้าย ไม่ใช่ขั้นถัดไปอีกขั้น
                        real = p["xs"][-1] - p["xs"][-2]
                        ck(f"บวก {real}" in r["why"],
                           f"ลำดับ s={s}: แนวคิดบอกผลต่างผิด ควรเป็น {real}")
                elif g.__name__ == "q_clock":
                    a = abs((30 * p["h"] + 0.5 * p["m"]) - 6 * p["m"])
                    ck(str(int(min(a, 360 - a))) == got, f"นาฬิกา s={s}: มุมไม่ตรง")
                    ck(all(0 < int(x) <= 180 for x in ch),
                       f"นาฬิกา s={s}: มีตัวเลือกเกิน 180 องศา {ch}")
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
                elif g.__name__ == "q_revseq":
                    ck(str(p["shown"][5]) == got, f"กลับหลัก s={s}: เฉลยไม่ตรง")
                    ck(all(int(str(v)[::-1]) == w
                           for v, w in zip(p["vals"], p["shown"])),
                       f"กลับหลัก s={s}: กลับหลักไม่ตรงกับพจน์จริง")
                elif g.__name__ == "q_symsum":
                    ck(str(p["tot"][3]) == got, f"สัญลักษณ์ s={s}: ผลรวมไม่ตรง")
                    ck(all(sum(p["val"][c] for c in r) == t
                           for r, t in zip(p["rows"], p["tot"])),
                       f"สัญลักษณ์ s={s}: ผลรวมแถวไม่ตรงกับค่าที่ตั้ง")
                elif g.__name__ == "q_thaieng":
                    ck(p["pairs"][5] == got, f"ไทยผสมอังกฤษ s={s}: เฉลยไม่ตรง")
                elif g.__name__ == "q_work":
                    ck(int(got) * (p["a"] + p["b"]) == p["a"] * p["b"],
                       f"งานร่วม s={s}: เฉลยไม่ตรงกับอัตรารวม")
                elif g.__name__ == "q_avgspeed":
                    ck(int(got) * (p["u"] + p["v"]) == 2 * p["u"] * p["v"],
                       f"อัตราเร็วเฉลี่ย s={s}: ไม่ใช่ค่าเฉลี่ยฮาร์มอนิก")
                elif g.__name__ == "q_cutlog":
                    cuts = p["parts"] - 1
                    ck(int(got) == cuts * p["cut"] + (cuts - 1) * p["rest"],
                       f"ตัดไม้ s={s}: นับรอยตัดหรือช่วงพักผิด")
                elif g.__name__ == "q_unit":
                    ck(int(got) * 1000 == p["vol"], f"หน่วย s={s}: เปลี่ยนหน่วยผิด")
                elif g.__name__ == "q_double":
                    ck(int(got) == p["t0"] + p["per"] * p["k"],
                       f"ทวีคูณ s={s}: เวลาไม่ตรง")
                elif g.__name__ == "q_liarcount":
                    ok, who, claims = p["ok"], p["who"], p["claims"]
                    ck(", ".join(who[i] for i in range(p["n"]) if ok[i]) == got,
                       f"จริงเท็จ s={s}: เฉลยไม่ตรง")
                    for i, j, t in claims:      # ทุกคำพูดต้องสอดคล้องกับสถานะที่เฉลย
                        ck(ok[i] == (ok[j] == t), f"จริงเท็จ s={s}: คำพูดขัดกับเฉลย")

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

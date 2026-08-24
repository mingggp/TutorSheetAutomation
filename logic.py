#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เครื่องผลิตโจทย์ตรรกะยาว — แนวที่ข้อสอบจริงใช้ทำข้อสามดาว แต่คลังยังไม่มีเลยสักข้อ

หลักการเดียวกับ cube.py: ทุกข้อถูกพิสูจน์ด้วยการไล่ทุกความเป็นไปได้จริง
ไม่ใช่ด้วยความมั่นใจ (กติกาข้อ 1 ของโปรเจกต์)

ทุกฟังก์ชันคืนค่า (stem, choices, ansIdx) และรับ `want` = ตำแหน่งที่อยากให้เฉลยไปตก (0-4)
เพื่อบังคับให้เฉลยกระจายครบทั้ง ก-จ (กติกาข้อ 4 ซึ่งคลังเดิมทำพลาด — ตัวเลือก จ. เป็นเฉลยแค่ 3 ครั้งใน 77 ข้อ)
"""
from itertools import permutations, product

NAMES = ["อ้น", "บอย", "ซี", "ดิว", "เอิร์ธ", "ฟ้า", "แก้ม", "จูน"]


def _place(opts, ans, want):
    """เอาคำตอบไปวางไว้ตำแหน่ง want แล้วเรียงตัวลวงที่เหลือลงช่องว่าง"""
    rest = [o for o in opts if o != ans]
    out = rest[:want] + [ans] + rest[want:]
    return out[:5], want


# ============================================================
#  จัดที่นั่ง / จัดลำดับ — ไล่ทุกการเรียงสับเปลี่ยนเพื่อยืนยันว่าคำตอบมีทางเดียว
# ============================================================

def _seat_pool(target):
    """เงื่อนไขที่ 'จริง' ทั้งหมดสำหรับการเรียงเป้าหมาย — เดี๋ยวค่อยเลือกใช้บางข้อ"""
    n = len(target)
    pos = {p: i for i, p in enumerate(target)}
    pool = []

    for a in target:
        for b in target:
            if a == b:
                continue
            if pos[a] < pos[b]:
                pool.append((f"{a} นั่งอยู่ทางซ้ายของ {b}",
                             lambda q, a=a, b=b: q.index(a) < q.index(b)))
            if abs(pos[a] - pos[b]) == 1 and a < b:
                pool.append((f"{a} นั่งติดกับ {b}",
                             lambda q, a=a, b=b: abs(q.index(a) - q.index(b)) == 1))
            if abs(pos[a] - pos[b]) > 1 and a < b:
                pool.append((f"{a} ไม่ได้นั่งติดกับ {b}",
                             lambda q, a=a, b=b: abs(q.index(a) - q.index(b)) != 1))
            gap = abs(pos[a] - pos[b]) - 1
            if gap >= 1 and a < b:
                pool.append((f"ระหว่าง {a} กับ {b} มีคนนั่งคั่นอยู่ {gap} คน",
                             lambda q, a=a, b=b, g=gap: abs(q.index(a) - q.index(b)) - 1 == g))

    for p in target:
        i = pos[p]
        if i == 0:
            pool.append((f"{p} นั่งหัวแถว", lambda q, p=p: q.index(p) == 0))
        elif i == n - 1:
            pool.append((f"{p} นั่งท้ายแถว", lambda q, p=p: q.index(p) == n - 1))
        else:
            pool.append((f"{p} ไม่ได้นั่งหัวแถวและไม่ได้นั่งท้ายแถว",
                         lambda q, p=p: 0 < q.index(p) < n - 1))
    return pool


def _solutions(names, rules, cap=2):
    """นับว่ามีการเรียงกี่แบบที่ผ่านทุกเงื่อนไข หยุดนับเมื่อเกิน cap"""
    found = []
    for q in permutations(names):
        if all(f(q) for _, f in rules):
            found.append(q)
            if len(found) > cap:
                break
    return found


def seating(rng, want=0, n=5):
    """คนนั่งเรียงแถวเดียว n คน ให้เงื่อนไขมาชุดหนึ่ง แล้วถามว่าใครนั่งตรงไหน

    คืน (stem, choices, ansIdx) โดยตัวเลือกคือชื่อคนทั้ง n คน
    """
    for _ in range(400):
        names = rng.sample(NAMES, n)
        target = list(names)
        rng.shuffle(target)

        pool = _seat_pool(target)
        rng.shuffle(pool)

        rules = []
        for cand in pool:
            rules.append(cand)
            if len(_solutions(names, rules)) == 1:
                break
        else:
            continue  # ชุดนี้บีบไม่ลง เอาใหม่

        # ตัดเงื่อนไขที่ไม่จำเป็นออก ให้เหลือชุดที่สั้นที่สุดเท่าที่ยังตอบได้ทางเดียว
        i = 0
        while i < len(rules):
            trial = rules[:i] + rules[i + 1:]
            if trial and len(_solutions(names, trial)) == 1:
                rules = trial
            else:
                i += 1

        if not (3 <= len(rules) <= 6):
            continue

        spot = rng.choice([0, n // 2, n - 1])
        where = {0: "หัวแถว", n // 2: "ตรงกลางแถว", n - 1: "ท้ายแถว"}[spot]
        ans = target[spot]

        lines = [f"{chr(48 + k + 1)}) {t}" for k, (t, _) in enumerate(rules)]
        stem = (f"{'  '.join(names)} นั่งเรียงเป็นแถวหน้ากระดานแถวเดียว หันหน้าไปทางเดียวกัน "
                f"โดยมีเงื่อนไขดังนี้\n" + "\n".join(lines) +
                f"\nคนที่นั่ง{where}คือใคร")
        opts, idx = _place(names, ans, want)
        return stem, opts, idx
    raise RuntimeError("สร้างโจทย์จัดที่นั่งไม่สำเร็จ")


# ============================================================
#  พูดจริง-พูดโกหก — ไล่ทุกความเป็นไปได้ของใครจริงใครโกหก
# ============================================================

def _liar_stmts(names, truth):
    """สร้างคำพูดให้แต่ละคน โดยคนพูดจริงต้องพูดสิ่งที่จริง คนโกหกต้องพูดสิ่งที่เท็จ

    คืนลิสต์ของ (ข้อความ, ฟังก์ชันประเมินค่าความจริงภายใต้สมมติฐาน t)
    """
    n = len(names)
    out = []
    for i, who in enumerate(names):
        forms = []
        for j, other in enumerate(names):
            if i == j:
                continue
            forms.append((f"{other} พูดความจริง", lambda t, j=j: t[j]))
            forms.append((f"{other} พูดโกหก", lambda t, j=j: not t[j]))
        for k in range(n + 1):
            forms.append((f"พวกเรามีคนพูดความจริงอยู่ {k} คน",
                          lambda t, k=k: sum(t) == k))
        # เลือกคำพูดที่ค่าความจริงตรงกับสถานะของคนพูด
        ok = [f for f in forms if f[1](truth) == truth[i]]
        if not ok:
            return None
        out.append(ok)
    return out


def _liar_consistent(stmts, n, cap=2):
    """หาสมมติฐานทั้งหมดที่สอดคล้องกันเอง — คนพูดจริงพูดจริง คนโกหกพูดเท็จ"""
    good = []
    for t in product([True, False], repeat=n):
        if all(f(t) == t[i] for i, (_, f) in enumerate(stmts)):
            good.append(t)
            if len(good) > cap:
                break
    return good


def liars(rng, want=0, n=5):
    """แต่ละคนพูดหนึ่งประโยค ถามว่ามีคนพูดความจริงกี่คน

    ต้องมีสมมติฐานที่สอดคล้องกันได้เพียงแบบเดียวเท่านั้น
    """
    for _ in range(600):
        names = rng.sample(NAMES, n)
        truth = tuple(rng.random() < 0.5 for _ in range(n))
        if not (1 <= sum(truth) <= n - 1):
            continue

        banks = _liar_stmts(names, truth)
        if banks is None:
            continue
        stmts = [rng.choice(b) for b in banks]

        good = _liar_consistent(stmts, n)
        if len(good) != 1 or good[0] != truth:
            continue

        k = sum(truth)
        lines = [f"{who} พูดว่า “{txt}”" for who, (txt, _) in zip(names, stmts)]
        stem = ("ในกลุ่มเพื่อนกลุ่มหนึ่ง แต่ละคนพูดความจริงเสมอ หรือไม่ก็พูดโกหกเสมอ อย่างใดอย่างหนึ่ง\n"
                + "\n".join(lines)
                + "\nมีคนพูดความจริงทั้งหมดกี่คน")
        pool = [str(v) for v in range(0, n + 1) if v != k]
        rng.shuffle(pool)
        opts, idx = _place([str(k)] + pool[:4], str(k), want)
        return stem, opts, idx
    raise RuntimeError("สร้างโจทย์พูดจริง-พูดโกหกไม่สำเร็จ")


# ============================================================
#  ตัวตรวจ — รันไฟล์นี้ตรงๆ เพื่อพิสูจน์ว่าโจทย์ที่ผลิตออกมาตอบได้ทางเดียวจริง
# ============================================================

if __name__ == "__main__":
    import random, sys

    bad = 0
    for s in range(60):
        rng = random.Random(s)
        for fn in (seating, liars):
            stem, opts, idx = fn(rng, want=s % 5)
            if len(opts) != 5 or len(set(opts)) != 5:
                print(f"[พัง] {fn.__name__} seed={s}: ตัวเลือกซ้ำหรือไม่ครบ 5"); bad += 1
            if not (0 <= idx < 5):
                print(f"[พัง] {fn.__name__} seed={s}: ตำแหน่งเฉลยผิด"); bad += 1
            if idx != s % 5:
                print(f"[พัง] {fn.__name__} seed={s}: บังคับตำแหน่งเฉลยไม่ได้"); bad += 1

    print("ตัวอย่างโจทย์จัดที่นั่ง\n" + "-" * 60)
    r = random.Random(7); st, op, ix = seating(r, want=3)
    print(st); print("   " + " | ".join(f"{'กขคงจ'[i]}{'*' if i == ix else ''}) {o}" for i, o in enumerate(op)))
    print("\nตัวอย่างโจทย์พูดจริง-พูดโกหก\n" + "-" * 60)
    r = random.Random(11); st, op, ix = liars(r, want=4)
    print(st); print("   " + " | ".join(f"{'กขคงจ'[i]}{'*' if i == ix else ''}) {o}" for i, o in enumerate(op)))

    print("\n" + ("ตรวจผ่านทั้งหมด 120 ข้อ" if bad == 0 else f"พบปัญหา {bad} จุด"))
    sys.exit(1 if bad else 0)

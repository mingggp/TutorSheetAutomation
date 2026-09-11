#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""วัดว่าชีทชุดที่ 1 กับชุดที่ 2 ซ้ำกันกี่ข้อ — เทียบลายนิ้วมือจริง ไม่ใช่เทียบชื่อแนว

ลายนิ้วมือ = ข้อความโจทย์ + ตัวเลือกทุกตัว + ไบต์ของรูปโจทย์และแถบตัวเลือก
ถ้าเปลี่ยนแค่ตัวลวงหรือสลับตำแหน่งเฉลย จะยังนับว่าซ้ำ ซึ่งเป็นสิ่งที่ติวเตอร์ทัก

    python dupcheck.py [จำนวนข้อ] [วิชา]
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
N = sys.argv[1] if len(sys.argv) > 1 else "50"
SUBJ = sys.argv[2] if len(sys.argv) > 2 else "tpat3"
ROW = re.compile(r"^\s*(\d+)\s{2}(.+?)\s{2}ลว\.(\d)\s{2}(.+?)\s{2}(\S+)\s{2}(\S+)$")


def fileh(name):
    if not name or name == "-":
        return ""
    p = os.path.join(HERE, "img", name)
    if not os.path.exists(p):
        return "?" + name
    return hashlib.sha1(open(p, "rb").read()).hexdigest()[:12]


def one(setno):
    env = dict(os.environ, TPAT_SEED=str(setno), PYTHONIOENCODING="utf-8")
    subprocess.run([sys.executable, "gen.py"], cwd=HERE, env=env,
                   check=True, capture_output=True)
    bank = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
    out = subprocess.run(["node", "build.js", "--subject", SUBJ, "--mix", "std",
                          "--n", N, "--set", str(setno), "--list"],
                         cwd=HERE, check=True, capture_output=True,
                         encoding="utf-8", errors="replace")
    rows, used = [], set()
    lines = out.stdout.splitlines()
    for i, ln in enumerate(lines):
        m = ROW.match(ln)
        if not m:
            continue
        _, part, lvl, arche, img, optimg = m.groups()
        head = lines[i + 1].strip() if i + 1 < len(lines) else ""
        hit = None
        for k, q in enumerate(bank):
            if k in used:
                continue
            if (q["arche"] == arche.strip() and (q.get("img") or "-") == img
                    and (q.get("optimg") or "-") == optimg
                    and q["stem"].split("\n")[0][:70].strip() == head):
                hit = k
                break
        if hit is None:
            rows.append(("ไม่พบในคลัง|" + arche + head, arche.strip()))
            continue
        used.add(hit)
        q = bank[hit]
        fp = "|".join([q["stem"]] + list(q["choices"]) +
                      [fileh(q.get("img")), fileh(q.get("optimg"))])
        rows.append((hashlib.sha1(fp.encode()).hexdigest()[:16], q["arche"]))
    return rows


a = one(1)
b = one(2)
sa = {h for h, _ in a}
same = [(h, ar) for h, ar in b if h in sa]
print(f"ชุดที่ 1: {len(a)} ข้อ · ชุดที่ 2: {len(b)} ข้อ")
print(f"ซ้ำกันเป๊ะ (โจทย์+ตัวเลือก+รูปเหมือนกันหมด): {len(same)} ข้อ")
for h, ar in same:
    print("   ", ar)
arche1 = {ar for _, ar in a}
arche2 = {ar for _, ar in b}
print("แนวที่ชุด 2 มีแต่ชุด 1 ไม่มี:", ", ".join(sorted(arche2 - arche1)) or "-")
print("จำนวนแนวในชีท: ชุด 1 =", len(arche1), "· ชุด 2 =", len(arche2))

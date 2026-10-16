#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""สร้างหน้าสถานะคลังโจทย์ — ตัวเลขทุกตัวอ่านจาก questions.json ไม่ได้พิมพ์มือ

    python mkstatus.py [ไฟล์ปลายทาง]

ค่าเริ่มต้นเขียนลง scratchpad ของ session แล้วค่อยส่งขึ้นเป็น artifact
หน้าเดิมอยู่ที่ https://claude.ai/code/artifact/088e8404-0e1c-4008-8ac6-f7001355c699
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out", "status.html")
QS = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
NIMG = len(os.listdir(os.path.join(HERE, "img")))
CAP = 2      # เพดานข้อต่อแนวต่อชีท — แนวที่มีไม่ถึง 2 เท่าของค่านี้ ถือว่าตื้น

LINES = [
    ("วีคคณิต", "#d5004d", "สอนแล้ว 2 คาบ · ชุดที่ 3 พร้อม", "ok",
     "ท่อนตัวเลข + ท่อนมิติสัมพันธ์ · ข้อ 1-30 ของข้อสอบจริง",
     [("ความสามารถทางตัวเลข", "พาร์ทที่ 1"),
      ("ความสามารถทางมิติสัมพันธ์", "พาร์ทที่ 2")]),
    ("วีคฟิสิกส์", "#d5004d", "ชุดที่ 2 ปรับแล้ว รอตรวจอีกรอบ", "warn",
     "ท่อนเชิงกล + ท่อนเชิงวิทยาศาสตร์ · ข้อ 31-60 ของข้อสอบจริง",
     [("ความสามารถด้านเชิงกล", "พาร์ทที่ 3"),
      ("ความสามารถด้านเชิงวิทยาศาสตร์", "พาร์ทที่ 4")]),
    ("TGAT2", "#ffb500", "พักไว้", "off",
     "ติวเตอร์ไม่ได้สอนแล้ว (13 ต.ค. 69) · เก็บโค้ดและคลังไว้ครบ ไม่ลบ",
     [("ความสามารถทางจำนวน", "ตอนที่ 2"),
      ("ความสามารถด้านมิติสัมพันธ์", "ตอนที่ 3"),
      ("ความสามารถทางเหตุผล", "ตอนที่ 4")]),
]

PROOF = [
    ("mech.py", "รอก เฟือง คาน วงจร กราฟ", "21,358", True),
    ("numgen.py", "พาร์ทตัวเลข สุ่มจริง 24 แนว", "25,172", True),
    ("physics.py", "โจทย์คำนวณ 14 หัวข้อ", "16,195", True),
    ("physgen.py", "วีคฟิสิกส์ 20 แนวใหม่ ตรวจซ้ำด้วยวิธีที่สอง", "4,975", True),
    ("mech2.py", "วีคฟิสิกส์ 6 แนวจาก FEST2026 ตรวจซ้ำด้วยวิธีที่สอง", "2,400", True),
    ("shapeop.py", "ตัวดำเนินการสัญลักษณ์รูป สามทิศทางคำถาม", "6,000", True),
    ("flatpuz.py", "วงกลมแบ่งส่วน พับกระดาษเจาะรู อัตราส่วนจุด", "4,500", True),
    ("numeric.py", "แนวตัวเลขนามธรรม", "3,200", True),
    ("logicgrid.py", "เมทริกซ์ตรรกะ อนุกรมรูปช่องกลางหาย", "3,000", True),
    ("cubeview.py", "ภาพฉายสามด้าน อนุกรมทรงลูกบาศก์", "1,800", True),
    ("spatial.py", "อนุกรม เมทริกซ์ ซ้อนแผ่น", "600", True),
    ("logic.py", "ตรรกะจัดลำดับ จริง-เท็จ", "120", True),
    ("cube.py", "พับกล่อง ครบ 24 มุมหมุน", "ทุกกรณี", True),
    ("concept.py", "แนวคิดฟิสิกส์ เขียนมือ", "36 · โครงสร้างเท่านั้น", False),
]

GAPS = [
    ("ไม่มีข้อซ้ำระหว่างชุดแล้ว", "ledger.json จดทุกชีทที่ออกไป ชุดถัดไปเลี่ยงข้อเดิมเอง · ฟิสิกส์ชุด 2 ซ้ำชุด 1 = 0 จาก 40",
     "ok", "ปิดจบแล้ว"),
    ("ข้อหน้าตาเหมือนกันในชีทเดียว", "รอก เฟือง คาน จำกัดตระกูลละ 1 ข้อต่อชีท · ฟิสิกส์ชุด 2 เปลี่ยน 4 ข้อแล้ว (16 ต.ค.)",
     "ok", "ปิดจบแล้ว"),
    ("โจทย์แนวคิดใหม่ 8 ข้อรอติวเตอร์อ่าน", "โดยเฉพาะข้อลูกโป่งฮีเลียมในรถเบรก ซึ่งเฉลยต่างจากที่วงไว้ในไฟล์ชุดที่ 6",
     "hold", "รอติวเตอร์อ่าน"),
    ("พาร์ทที่ 2 ยังมีแนวที่ตื้น", "ต้องมีข้อต่อแนวอย่างน้อยสองเท่าของเพดานต่อชีท",
     "warn", "ต้องเพิ่มคลัง"),
    ("แนวที่ถอดไว้แล้วแต่ยังไม่ได้สร้าง", "ให้ภาพบนกับภาพหน้า หาภาพข้าง · ปริมาตรจากภาพฉาย · กฎการแปลงรูปแถวสอนกฎ",
     "warn", "ทำต่อ"),
    ("เนื้อหาใน concept.py ยังไม่ผ่านสายตาคน", "เป็นแนวที่พิสูจน์ด้วยโค้ดไม่ได้โดยธรรมชาติ",
     "hold", "รอติวเตอร์อ่าน"),
    ("ท่อนข่าวสาร ข้อ 61-70 ยังไม่เริ่ม", "ยังไม่ได้ถอดแนวจากข้อสอบอ้างอิง",
     "off", "ยังไม่เริ่ม"),
    ("TGAT2 พักไว้", "ติวเตอร์ไม่ได้สอนแล้ว เก็บของที่ทำไว้ทั้งหมด ถ้ากลับมาสอนค่อยทำต่อ",
     "off", "พักไว้"),
]

TOTAL_CHECKED = "112,000+"


TH_MONTH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
            "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
STATUS = {"taught": ("ok", "สอนแล้ว"), "review": ("warn", "รอติวเตอร์ตรวจ"),
          "ready": ("ready", "พร้อมสอน"), "next": ("off", "ยังไม่ออก")}
CHECK = ('<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6.3l2.3 2.3 4.7-5" '
         'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
         'stroke-linejoin="round"/></svg>')


def thdate(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {TH_MONTH[m - 1]}"


def _step(state, label, sub):
    """state: done = ทำแล้ว · now = กำลังรอขั้นนี้ · todo = ยังไม่ถึง"""
    mark = CHECK if state == "done" else ""
    return (f'<li class="step {state}"><span class="tick">{mark}</span>'
            f'<span class="sl">{esc(label)}</span><span class="ss">{esc(sub)}</span></li>')


def timeline_html():
    tl = json.load(open(os.path.join(HERE, "timeline.json"), encoding="utf-8"))
    led = json.load(open(os.path.join(HERE, "ledger.json"), encoding="utf-8"))
    count = collections.Counter()
    cols = []
    for wk in tl["weeks"]:
        L = led.get(wk["key"], {})
        items = []
        for st in wk["sets"]:
            n = st["set"]
            count[st["status"]] += 1
            cls, chip = STATUS[st["status"]]
            e = L.get(str(n), {})
            prev = L.get(str(n - 1), {})
            if st["status"] == "next":
                items.append(
                    f'<li class="set next"><div class="sh"><h3>ชุดที่ {n}</h3>'
                    f'<span class="chip off">{chip}</span></div>'
                    f'<p class="sn">{esc(st.get("note", ""))}</p></li>')
                continue
            rv = st.get("reviews", [])
            s1 = _step("done", "ออกชีท", thdate(st["built"]))
            if rv and st["status"] == "review":
                # ตรวจแล้วสั่งแก้ แก้เสร็จแล้วส่งกลับไปให้ตรวจอีกรอบ
                s2 = _step("now", f"ติวเตอร์ตรวจรอบที่ {len(rv) + 1}", f"แก้ตามรอบ {thdate(rv[-1])} แล้ว")
            elif rv:
                s2 = _step("done", f"ติวเตอร์ตรวจ {len(rv)} รอบ", "ถึง " + thdate(rv[-1]))
            elif st["status"] == "review":
                s2 = _step("now", "ติวเตอร์ตรวจ", "กำลังรอ")
            else:
                s2 = _step("todo", "ติวเตอร์ตรวจ", "ยังไม่ได้ตรวจ")
            if st.get("taught"):
                s3 = _step("done", "สอนในคาบ", "แจ้ง " + thdate(st["taught"]))
            elif st["status"] == "ready":
                s3 = _step("now", "สอนในคาบ", "รอสอน")
            else:
                s3 = _step("todo", "สอนในคาบ", "หลังตรวจเสร็จ")
            facts = []
            if e.get("n"):
                facts.append(f'{e["n"]} ข้อ')
            if e.get("stars"):
                a, b, c = e["stars"]
                tot = max(1, a + b + c)
                facts.append(
                    '<span class="mix" title="ง่าย / กลาง / ยาก">'
                    f'<span class="bar"><i class="s1" style="width:{a * 100 / tot:.0f}%"></i>'
                    f'<i class="s2" style="width:{b * 100 / tot:.0f}%"></i>'
                    f'<i class="s3" style="width:{c * 100 / tot:.0f}%"></i></span>'
                    f'ง่าย {a} · กลาง {b} · ยาก {c}</span>')
            if e.get("repeat") is not None:
                facts.append(f'ซ้ำชุดก่อน {e["repeat"]} ข้อ')
            if e.get("arche") and prev.get("arche"):
                new = len(set(e["arche"]) - set(prev["arche"]))
                facts.append(f'แนวที่ชุดก่อนไม่มี {new}')
            sep = ' <span class="dot">·</span> '
            items.append(
                f'<li class="set {cls}"><div class="sh"><h3>ชุดที่ {n}</h3>'
                f'<span class="chip {cls}">{chip}</span></div>'
                f'<ol class="steps">{s1}{s2}{s3}</ol>'
                f'<p class="sf">{sep.join(facts)}</p>'
                f'<p class="sn">{esc(st.get("note", ""))}</p></li>')
        cols.append(f'<div class="week"><h4>{esc(wk["name"])}</h4>'
                    f'<ol class="track">{"".join(items)}</ol></div>')
    paused = "".join(
        f'<p class="paused"><span class="chip off">พักไว้</span> <strong>{esc(p["name"])}</strong> '
        f'เริ่ม {thdate(p["start"])} · พัก {thdate(p["paused"])} · {esc(p["note"])}</p>'
        for p in tl.get("paused", []))
    summary = (f'สอนไปแล้ว {count["taught"]} ชุด · พร้อมสอน {count["ready"]} ชุด · '
               f'รอติวเตอร์ตรวจ {count["review"]} ชุด')
    return (f'<section id="timeline"><h2>ไทม์ไลน์ชีท</h2>'
            f'<p class="note wide">{summary}</p>'
            f'<div class="weeks">{"".join(cols)}</div>{paused}</section>')


def part(key):
    return [q for q in QS if q["part"] == key]


def bar(qs):
    n = len(qs) or 1
    w = [sum(1 for q in qs if q["lvl"] == lv) * 100.0 / n for lv in (1, 2, 3)]
    return ("<span class=\"bar\">"
            + "".join(f'<i class="s{i+1}" style="width:{v:.1f}%"></i>'
                      for i, v in enumerate(w))
            + "</span>")


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


rows_line, cols_depth = [], []
for name, colour, chip, chipcls, note, parts in LINES:
    tot = sum(len(part(k)) for _n, k in parts)
    body = []
    for label, key in parts:
        qs = part(key)
        c = collections.Counter(q["arche"] for q in qs)
        thin = sum(1 for v in c.values() if v <= CAP)
        tag = (f'<span class="tiny warn">{thin} แนวตื้น</span>' if thin
               else '<span class="tiny ok">ลึกพอ</span>')
        body.append(
            f'<tr><th>{esc(label)}</th><td class="num">{len(qs)}</td>'
            f'<td class="num">{len(c)} แนว</td><td>{bar(qs)}</td><td>{tag}</td></tr>')
        if c:
            top = max(c.values())
            items = "".join(
                f'<li class="{"thin" if v <= CAP else ""}"><span class="nm">{esc(a)}</span>'
                f'<span class="track"><i style="width:{v*100//top}%"></i></span>'
                f'<span class="num">{v}</span></li>'
                for a, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
            cols_depth.append(
                f'<div class="col" style="--line:{colour}"><h4>{esc(name)} · {esc(label)}</h4>'
                f'<ul class="depth">{items}</ul></div>')
    rows_line.append(
        f'<article class="line" style="--line:{colour}">'
        f'<div class="line-head"><h3>{esc(name)}</h3>'
        f'<span class="chip {chipcls}">{esc(chip)}</span></div>'
        f'<p class="note">{esc(note)}</p>'
        f'<p class="big"><span>{tot}</span> ข้อ</p>'
        f'<table class="mini"><tbody>{"".join(body)}</tbody></table></article>')

proof_rows = "".join(
    f'<tr><td class="mono">{f}</td><td>{esc(c)}</td><td class="num mono">{n}</td>'
    f'<td><span class="chip {"ok" if ok else "warn"}">'
    f'{"ได้" if ok else "ไม่ได้ ต้องให้คนอ่าน"}</span></td></tr>'
    for f, c, n, ok in PROOF)

gap_rows = "".join(
    f'<li><div class="g-what">{esc(w)}</div><div class="g-why">{esc(y)}</div>'
    f'<span class="chip {cls}">{esc(tag)}</span></li>'
    for w, y, cls, tag in GAPS)

CSS = open(os.path.join(HERE, "status.css"), encoding="utf-8").read()

HTML = f"""<title>สถานะคลังโจทย์</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
{CSS}</style>
<div class="wrap">
<header class="top">
<p class="eyebrow">โรงงานผลิตชีทโจทย์ · mingsmileyface</p>
<h1>สถานะคลังโจทย์</h1>
<p class="lede">ทุกข้อในคลังถูกพิสูจน์ว่ามีคำตอบถูกข้อเดียวด้วยการคำนวณ ไม่ใช่ด้วยความมั่นใจ หน้านี้บอกว่าตอนนี้ผลิตอะไรได้แล้ว และตรงไหนที่ยังบาง</p>
<dl class="totals">
<div><dt>ข้อในคลัง</dt><dd>{len(QS)}</dd></div>
<div><dt>รูปที่โค้ดวาดเอง</dt><dd>{NIMG}</dd></div>
<div><dt>แนวโจทย์</dt><dd>{len({q["arche"] for q in QS})}</dd></div>
<div><dt>ข้อที่ตรวจซ้ำด้วยโค้ด</dt><dd>{TOTAL_CHECKED}</dd></div>
</dl></header>
{timeline_html()}
<section><h2>สายการผลิต</h2><div class="lines">
{"".join(rows_line)}
</div>
<p class="legend"><span class="key s1"></span>หนึ่งดาว<span class="key s2"></span>สองดาว<span class="key s3"></span>สามดาว · แนวตื้นคือแนวที่มีไม่เกิน {CAP} ข้อ ซึ่งหมุนหาข้อใหม่ให้ชีทชุดถัดไปไม่ได้</p>
</section>
<section><h2>ความลึกรายแนว</h2>
<p class="note wide">แถบยาวเท่ากับจำนวนข้อในแนวนั้น แนวที่ยาวไม่ถึงสองเท่าของเพดาน {CAP} ข้อต่อชีท จะออกซ้ำเมื่อสั่งชีทชุดถัดไป จึงระบายเป็นสีเตือนไว้</p>
<div class="cols">
{"".join(cols_depth)}
</div></section>
<section><h2>การพิสูจน์ความถูกต้อง</h2>
<p class="note wide">กติกาข้อ 1 ของโปรเจกต์บังคับว่าทุกโจทย์ต้องมีคำตอบถูกข้อเดียว และต้องพิสูจน์ด้วยโค้ด ตัวเลขคือจำนวนข้อที่เครื่องผลิตแต่ละตัวสร้างขึ้นแล้วตรวจซ้ำ ทุกครั้งที่รันไฟล์นั้น</p>
<div class="scroll"><table class="proof"><thead><tr><th>เครื่องผลิต</th><th>ครอบแนว</th><th class="num">ตรวจซ้ำแล้ว</th><th>พิสูจน์ด้วยโค้ด</th></tr></thead><tbody>
{proof_rows}
</tbody></table></div>
<p class="note wide"><strong>concept.py เป็นข้อยกเว้นเดียว</strong> — โจทย์แนวคิดฟิสิกส์ไม่มีตัวเลขให้คำนวณ ความถูกต้องอยู่ที่หลักฟิสิกส์ล้วน ๆ ตัวตรวจดูได้แค่ว่าตัวเลือกไม่ซ้ำ เฉลยมีข้อเดียว และเฉลยกระจายครบ ก ถึง จ ส่วนเนื้อหาต้องให้คนอ่านทวนก่อนใช้สอน</p>
</section>
<section><h2>ที่ยังขาด</h2><ol class="gaps">
{gap_rows}
</ol></section>
<footer><p>ตัวเลขทุกตัวอ่านจาก questions.json ตอนสร้างหน้านี้ ไม่ได้พิมพ์มือ · สร้างด้วย mkstatus.py</p></footer>
</div>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(HTML)
print(OUT, len(HTML), "ตัวอักษร")

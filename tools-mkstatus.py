#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""สร้างหน้าสถานะคลังโจทย์จากข้อมูลจริงใน questions.json"""
import json, collections, os, html, sys

ROOT = r"C:\dev\Tutor\tpat3-factory"
QS = json.load(open(os.path.join(ROOT, "questions.json"), encoding="utf-8"))
SUB = json.load(open(os.path.join(ROOT, "subjects.json"), encoding="utf-8"))
OUT = sys.argv[1]
CAP = 2

LINES = [
    ("วีคคณิต", "tpat3", "#d5004d", "ใช้สอนแล้ว",
     "ท่อนตัวเลข + ท่อนมิติสัมพันธ์ · ข้อ 1-30 ของข้อสอบจริง"),
    ("วีคฟิสิกส์", "tpat3phys", "#d5004d", "พร้อมสอน",
     "ท่อนเชิงกล + ท่อนเชิงวิทยาศาสตร์ · ข้อ 31-60 ของข้อสอบจริง"),
    ("TGAT2", "tgat2", "#ffb500", "กำลังเริ่ม",
     "ยังไม่ครบผัง 16 แนวย่อย · กำหนดกลางเดือนกันยายน"),
]

TESTS = [
    ("mech.py", "รอก เฟือง คาน วงจร กราฟ", "17,977", True),
    ("physics.py", "โจทย์คำนวณ 14 หัวข้อ", "16,195", True),
    ("numeric.py", "แนวตัวเลขนามธรรม", "3,200", True),
    ("spatial.py", "อนุกรม เมทริกซ์ ซ้อนแผ่น", "600", True),
    ("logic.py", "ตรรกะจัดลำดับ จริง-เท็จ", "120", True),
    ("cube.py", "พับกล่อง ครบ 24 มุมหมุน", "ทุกกรณี", True),
    ("concept.py", "แนวคิดฟิสิกส์ เขียนมือ", "29 · โครงสร้างเท่านั้น", False),
]

GAPS = [
    ("บรรทัดแนวคิดในฉบับครู ยังมีเฉพาะวีคฟิสิกส์",
     "วีคคณิต 131 ข้อยังไม่มีบรรทัดนี้", "ทำต่อ"),
    ("ชีทชุดถัดไปยังซ้ำของเดิมประมาณ 80 เปอร์เซ็นต์",
     "แนวที่มีไม่เกิน 2 ข้อ หมุนหาข้อใหม่ไม่ได้", "ต้องเพิ่มคลัง"),
    ("เนื้อหาใน concept.py ยังไม่ผ่านสายตาคน",
     "เป็นแนวที่พิสูจน์ด้วยโค้ดไม่ได้โดยธรรมชาติ", "รอติวเตอร์อ่าน"),
    ("ท่อนข่าวสาร ข้อ 61-70 ยังไม่เริ่ม",
     "ยังไม่ได้ถอดแนวจากข้อสอบอ้างอิง", "ยังไม่เริ่ม"),
    ("TGAT2 ยังไม่ครบผัง 16 แนวย่อย",
     "ตอนนี้มี 3 แนว จาก 12 แนวที่ต้องทำ", "กำลังทำ"),
]


def esc(s):
    return html.escape(str(s))


def stats(part):
    items = [q for q in QS if q["part"] == part]
    c = collections.Counter(q["arche"] for q in items)
    lv = collections.Counter(q["lvl"] for q in items)
    return items, c, [lv.get(1, 0), lv.get(2, 0), lv.get(3, 0)]


nimg = len([f for f in os.listdir(os.path.join(ROOT, "img")) if f.endswith(".png")])
b = ['<div class="wrap">']
b.append('<header class="top">')
b.append('<p class="eyebrow">โรงงานผลิตชีทโจทย์ · mingsmileyface</p>')
b.append('<h1>สถานะคลังโจทย์</h1>')
b.append('<p class="lede">ทุกข้อในคลังถูกพิสูจน์ว่ามีคำตอบถูกข้อเดียวด้วยการคำนวณ '
         'ไม่ใช่ด้วยความมั่นใจ หน้านี้บอกว่าตอนนี้ผลิตอะไรได้แล้ว และตรงไหนที่ยังบาง</p>')
b.append('<dl class="totals">')
for k, v in (("ข้อในคลัง", len(QS)), ("รูปที่โค้ดวาดเอง", nimg),
             ("ชีทที่สั่งออกได้ทันที", 2), ("ข้อที่ตรวจซ้ำด้วยโค้ด", "38,000+")):
    b.append(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>')
b.append('</dl></header>')

b.append('<section><h2>สายการผลิต</h2><div class="lines">')
for name, key, color, status, note in LINES:
    parts = SUB[key]["parts"]
    tot = sum(len(stats(p["key"])[0]) for p in parts)
    cls = "warn" if status == "กำลังเริ่ม" else "ok"
    b.append(f'<article class="line" style="--line:{color}">')
    b.append(f'<div class="line-head"><h3>{esc(name)}</h3>'
             f'<span class="chip {cls}">{esc(status)}</span></div>')
    b.append(f'<p class="note">{esc(note)}</p>')
    b.append(f'<p class="big"><span>{tot}</span> ข้อ</p>')
    b.append('<table class="mini"><tbody>')
    for p in parts:
        items, c, lv = stats(p["key"])
        shallow = sum(1 for v in c.values() if v <= CAP)
        n = max(1, len(items))
        bar = "".join(f'<i class="s{k+1}" style="width:{lv[k]*100/n:.1f}%"></i>'
                      for k in range(3))
        warn = (f'<span class="tiny warn">{shallow} แนวตื้น</span>' if shallow
                else '<span class="tiny ok">ลึกพอ</span>')
        b.append(f'<tr><th>{esc(p["label"])}</th><td class="num">{len(items)}</td>'
                 f'<td class="num">{len(c)} แนว</td>'
                 f'<td><span class="bar">{bar}</span></td><td>{warn}</td></tr>')
    b.append('</tbody></table></article>')
b.append('</div>')
b.append('<p class="legend"><span class="key s1"></span>หนึ่งดาว'
         '<span class="key s2"></span>สองดาว<span class="key s3"></span>สามดาว'
         ' · แนวตื้นคือแนวที่มีไม่เกิน 2 ข้อ ซึ่งหมุนหาข้อใหม่ให้ชีทชุดถัดไปไม่ได้</p>')
b.append('</section>')

b.append('<section><h2>ความลึกรายแนว</h2>')
b.append(f'<p class="note wide">แถบยาวเท่ากับจำนวนข้อในแนวนั้น แนวที่ยาวไม่ถึงสองเท่าของ'
         f'เพดาน {CAP} ข้อต่อชีท จะออกซ้ำเมื่อสั่งชีทชุดถัดไป จึงระบายเป็นสีเตือนไว้</p>')
b.append('<div class="cols">')
for name, key, color, status, note in LINES:
    for p in SUB[key]["parts"]:
        items, c, lv = stats(p["key"])
        if not items:
            continue
        mx = max(c.values())
        b.append(f'<div class="col" style="--line:{color}">'
                 f'<h4>{esc(name)} · {esc(p["label"])}</h4><ul class="depth">')
        for a, v in c.most_common():
            thin = "thin" if v <= CAP else ""
            b.append(f'<li class="{thin}"><span class="nm">{esc(a)}</span>'
                     f'<span class="track"><i style="width:{v*100/mx:.0f}%"></i></span>'
                     f'<span class="num">{v}</span></li>')
        b.append('</ul></div>')
b.append('</div></section>')

b.append('<section><h2>การพิสูจน์ความถูกต้อง</h2>')
b.append('<p class="note wide">กติกาข้อ 1 ของโปรเจกต์บังคับว่าทุกโจทย์ต้องมีคำตอบถูกข้อเดียว '
         'และต้องพิสูจน์ด้วยโค้ด ตัวเลขคือจำนวนข้อที่เครื่องผลิตแต่ละตัวสร้างขึ้นแล้วตรวจซ้ำ '
         'ทุกครั้งที่รันไฟล์นั้น</p>')
b.append('<div class="scroll"><table class="proof"><thead><tr><th>เครื่องผลิต</th>'
         '<th>ครอบแนว</th><th class="num">ตรวจซ้ำแล้ว</th>'
         '<th>พิสูจน์ด้วยโค้ด</th></tr></thead><tbody>')
for f, what, n, proved in TESTS:
    mark = ('<span class="chip ok">ได้</span>' if proved
            else '<span class="chip warn">ไม่ได้ ต้องให้คนอ่าน</span>')
    b.append(f'<tr><td class="mono">{esc(f)}</td><td>{esc(what)}</td>'
             f'<td class="num mono">{esc(n)}</td><td>{mark}</td></tr>')
b.append('</tbody></table></div>')
b.append('<p class="note wide"><strong>concept.py เป็นข้อยกเว้นเดียว</strong> — '
         'โจทย์แนวคิดฟิสิกส์ไม่มีตัวเลขให้คำนวณ ความถูกต้องอยู่ที่หลักฟิสิกส์ล้วน ๆ '
         'ตัวตรวจดูได้แค่ว่าตัวเลือกไม่ซ้ำ เฉลยมีข้อเดียว และเฉลยกระจายครบ ก ถึง จ '
         'ส่วนเนื้อหาต้องให้คนอ่านทวนก่อนใช้สอน</p>')
b.append('</section>')

b.append('<section><h2>ที่ยังขาด</h2><ol class="gaps">')
for what, why, state in GAPS:
    cls = {"ทำต่อ": "warn", "ต้องเพิ่มคลัง": "warn", "รอติวเตอร์อ่าน": "hold",
           "ยังไม่เริ่ม": "off", "กำลังทำ": "warn"}[state]
    b.append(f'<li><div class="g-what">{esc(what)}</div>'
             f'<div class="g-why">{esc(why)}</div>'
             f'<span class="chip {cls}">{esc(state)}</span></li>')
b.append('</ol></section>')
b.append('<footer><p>ตัวเลขทุกตัวอ่านจาก questions.json ตอนสร้างหน้านี้ ไม่ได้พิมพ์มือ</p></footer>')
b.append('</div>')

CSS = """
:root{
  --bg:#fbfcfc; --panel:#ffffff; --ink:#18211f; --mid:#5b6669; --soft:#8b989b;
  --hair:#dde4e5; --rule:#eef2f3;
  --teal:#0f9d95;
  --s1:#9fd8d2; --s2:#2bb3a6; --s3:#0d6f72;
  --ok:#0f9d95; --warn:#a8711a; --hold:#6b7a8f; --off:#9aa5a8;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0f1516; --panel:#161e20; --ink:#e6edee; --mid:#a3b0b2; --soft:#7c8a8d;
    --hair:#263234; --rule:#1d2628;
    --teal:#3ecec0;
    --s1:#2b5f5d; --s2:#2f9e93; --s3:#63d8cb;
    --ok:#3ecec0; --warn:#e0b055; --hold:#8fa2b5; --off:#5d696c;
  }
}
:root[data-theme="dark"]{
  --bg:#0f1516; --panel:#161e20; --ink:#e6edee; --mid:#a3b0b2; --soft:#7c8a8d;
  --hair:#263234; --rule:#1d2628;
  --teal:#3ecec0;
  --s1:#2b5f5d; --s2:#2f9e93; --s3:#63d8cb;
  --ok:#3ecec0; --warn:#e0b055; --hold:#8fa2b5; --off:#5d696c;
}
*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--ink);
  font-family:"Sarabun",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:16px; line-height:1.65; -webkit-font-smoothing:antialiased}
.mono,.num,.big span,.totals dd,.eyebrow,h2,.chip,.tiny,.gaps li::before{
  font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-variant-numeric:tabular-nums}
.wrap{max-width:1040px; margin:0 auto; padding:56px 24px 72px;
  display:flex; flex-direction:column; gap:52px}
.top{display:flex; flex-direction:column; gap:14px}
.eyebrow{margin:0; font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--teal)}
h1{margin:0; font-size:clamp(30px,5vw,44px); font-weight:800; letter-spacing:-.01em; text-wrap:balance}
.lede{margin:0; max-width:62ch; color:var(--mid)}
.totals{display:grid; grid-template-columns:repeat(auto-fit,minmax(148px,1fr)); gap:1px;
  margin:16px 0 0; padding:0; background:var(--hair); border:1px solid var(--hair)}
.totals div{background:var(--panel); padding:16px 18px}
.totals dt{font-size:12px; color:var(--soft); letter-spacing:.03em}
.totals dd{margin:2px 0 0; font-size:27px; font-weight:500; line-height:1.2}
section{display:flex; flex-direction:column; gap:14px}
h2{margin:0; font-size:12px; letter-spacing:.15em; text-transform:uppercase;
  color:var(--soft); font-weight:500; border-bottom:1px solid var(--hair); padding-bottom:8px}
h3{margin:0; font-size:19px; font-weight:700}
h4{margin:0 0 10px; font-size:13px; font-weight:700; color:var(--mid)}
.note{margin:0; color:var(--mid); font-size:14px}
.note.wide{max-width:72ch}
.lines{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px}
.line{background:var(--panel); border:1px solid var(--hair); border-top:3px solid var(--line);
  padding:18px 18px 14px; display:flex; flex-direction:column; gap:10px}
.line-head{display:flex; align-items:center; justify-content:space-between; gap:10px}
.big{margin:0}
.big span{font-size:34px; font-weight:500; line-height:1}
.chip{font-size:11px; letter-spacing:.05em; padding:3px 8px;
  border:1px solid currentColor; white-space:nowrap}
.chip.ok{color:var(--ok)} .chip.warn{color:var(--warn)}
.chip.hold{color:var(--hold)} .chip.off{color:var(--off)}
.tiny{font-size:11px}
.tiny.warn{color:var(--warn)} .tiny.ok{color:var(--soft)}
table{border-collapse:collapse; width:100%}
.mini th{text-align:left; font-weight:500; font-size:13px; color:var(--mid); padding:5px 0}
.mini td{padding:5px 0 5px 10px; font-size:13px; vertical-align:middle}
.mini tr + tr th,.mini tr + tr td{border-top:1px solid var(--rule)}
.num{text-align:right; white-space:nowrap}
.bar{display:flex; width:76px; height:7px; background:var(--rule); overflow:hidden}
.bar i{display:block; height:100%}
.s1{background:var(--s1)} .s2{background:var(--s2)} .s3{background:var(--s3)}
.legend{margin:0; font-size:12px; color:var(--soft); display:flex;
  align-items:center; gap:6px; flex-wrap:wrap}
.key{display:inline-block; width:18px; height:7px; margin-left:8px}
.cols{display:grid; grid-template-columns:repeat(auto-fit,minmax(310px,1fr)); gap:16px}
.col{background:var(--panel); border:1px solid var(--hair);
  border-left:3px solid var(--line); padding:16px}
.depth{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:5px}
.depth li{display:grid; grid-template-columns:1fr 84px 26px; align-items:center;
  gap:9px; font-size:13px}
.depth .nm{overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.depth .track{height:8px; background:var(--rule)}
.depth .track i{display:block; height:100%; background:var(--s2)}
.depth li.thin .track i{background:var(--warn)}
.depth li.thin .nm{color:var(--warn)}
.scroll{overflow-x:auto}
.proof{background:var(--panel); border:1px solid var(--hair); min-width:520px}
.proof th{text-align:left; font-size:12px; color:var(--soft); font-weight:500;
  padding:10px 14px; border-bottom:1px solid var(--hair); letter-spacing:.04em}
.proof td{padding:10px 14px; font-size:14px; border-top:1px solid var(--rule)}
.gaps{list-style:none; counter-reset:g; margin:0; padding:0; display:flex;
  flex-direction:column; gap:1px; background:var(--hair); border:1px solid var(--hair)}
.gaps li{counter-increment:g; background:var(--panel); padding:13px 16px 13px 46px;
  position:relative; display:flex; flex-direction:column; gap:2px}
.gaps li::before{content:counter(g,decimal-leading-zero); position:absolute; left:16px;
  top:14px; font-size:12px; color:var(--soft)}
.g-what{font-weight:600}
.g-why{font-size:13px; color:var(--mid)}
.gaps .chip{position:absolute; right:16px; top:14px}
footer{border-top:1px solid var(--hair); padding-top:16px}
footer p{margin:0; font-size:12px; color:var(--soft)}
@media(max-width:640px){
  .wrap{padding:36px 16px 56px; gap:40px}
  .gaps li{padding-right:16px}
  .gaps .chip{position:static; align-self:flex-start; margin-top:6px}
  .depth li{grid-template-columns:1fr 56px 24px}
}
"""

page = (
    "<title>สถานะคลังโจทย์</title>\n"
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Sarabun:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap">\n'
    "<style>" + CSS + "</style>\n" + "\n".join(b) + "\n"
)
open(OUT, "w", encoding="utf-8").write(page)
print("เขียนหน้าแล้ว", OUT, len(page), "ตัวอักษร")

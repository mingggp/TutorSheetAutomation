#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เรนเดอร์หน้า PDF ออกมาเป็นภาพ วางเรียงหลายหน้าต่อภาพ ไว้เปิดดูชีทที่ออกหรือสแกนอ้างอิง

    python pdfview.py <ไฟล์> <หน้าแรก> <หน้าสุดท้าย> <กี่หน้าต่อภาพ> <dpi> <โฟลเดอร์ปลายทาง>

หน้านับเริ่มที่ 1 · เขียนเลขหน้ากำกับไว้มุมบน
เดิมอยู่ใน scratchpad ของ session ซึ่งถูกล้างเป็นระยะ ต้องเขียนใหม่ทุกครั้ง จึงย้ายมาไว้ในโปรเจกต์
CLAUDE.md กำหนดว่า "แก้รูปแล้วต้องเปิดรูปดูจริง" — เครื่องมือนี้คือวิธีเปิดดู
"""
import os
import sys

import pymupdf
from PIL import Image, ImageDraw


def render(f, p0, p1, per, dpi, out):
    os.makedirs(out, exist_ok=True)
    d = pymupdf.open(f)
    p1 = min(p1, len(d))
    base = os.path.splitext(os.path.basename(f))[0]
    made = []
    for start in range(p0, p1 + 1, per):
        pages = list(range(start, min(start + per, p1 + 1)))
        ims = []
        for n in pages:
            pm = d[n - 1].get_pixmap(dpi=dpi)
            im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
            lab = Image.new("RGB", (im.width, im.height + 22), "white")
            lab.paste(im, (0, 22))
            ImageDraw.Draw(lab).text((8, 4), f"page {n}", fill=(200, 0, 80))
            ims.append(lab)
        sheet = Image.new("RGB", (sum(i.width for i in ims), max(i.height for i in ims)), "white")
        x = 0
        for i in ims:
            sheet.paste(i, (x, 0))
            x += i.width
        path = os.path.join(out, f"{base}_p{pages[0]:02d}-{pages[-1]:02d}.png")
        sheet.save(path)
        made.append(path)
    return made


if __name__ == "__main__":
    f, p0, p1, per, dpi, out = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                                int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
    print("\n".join(render(f, p0, p1, per, dpi, out)))

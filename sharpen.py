#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เอารูปต้นฉบับความละเอียดเต็มยัดกลับเข้าไปใน PDF ที่ Word พ่นออกมา

**ทำไมต้องมีขั้นนี้**
Word บีบรูปทุกรูปเหลือราว 200 dpi ตอน export PDF ไม่ว่าจะสั่งด้วย SaveAs หรือ
ExportAsFixedFormat แบบเน้นงานพิมพ์ก็ตาม (ทดสอบแล้วทั้งสองวิธี ได้ 199 dpi เท่ากัน)
และ Options.DefaultPictureResolution ก็ตั้งผ่าน COM ไม่ได้

ผลคือโลโก้ mingsmileyface ที่เก็บไว้ 498 px เหลือ 214 px ในไฟล์จริง ขอบตัวอักษรฟุ้ง
ขั้นนี้จับคู่รูปในPDFกับไฟล์ต้นฉบับใน img/ แล้วสลับกลับเป็นตัวเต็ม

    python sharpen.py "out/.../[TPAT3] Medium.pdf" [...]
"""
import sys, os, io, json

try:
    import pymupdf
    from PIL import Image
except ImportError as e:
    sys.exit(f"ต้องลง pymupdf กับ pillow ก่อน ({e})")

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
THUMB = 48          # ย่อทั้งสองฝั่งเท่านี้ก่อนเทียบ จะได้ไม่แพ้เรื่องความละเอียด


def _thumb(im):
    return im.convert("L").resize((THUMB, THUMB), Image.LANCZOS)


def _diff(a, b):
    pa, pb = a.tobytes(), b.tobytes()
    return sum(abs(x - y) for x, y in zip(pa, pb)) / (THUMB * THUMB)


def load_sources():
    """โหลดเฉพาะรูปที่ตั้งใจเก็บความละเอียดสูง พร้อม thumbnail ไว้เทียบ

    **ห้ามโหลดทุกไฟล์ใน img/** เพราะการเดาจับคู่ด้วยภาพย่อไม่แม่นพอ
    แถบตัวเลือกของคนละข้อหน้าตาคล้ายกันมาก เคยสลับทับกันจนข้อ 34 แสดงตัวเลือกของข้ออื่น
    รายชื่อมาจาก img/_hires.json ที่ gen.py เขียนไว้ (รูปที่ _save เก็บด้วย hi > 1)
    """
    manifest = os.path.join(IMG, "_hires.json")
    if not os.path.exists(manifest):
        print("    ไม่เจอ img/_hires.json — ข้ามขั้นทำรูปให้คม (รัน gen.py ก่อน)")
        return []
    with open(manifest, encoding="utf-8") as fh:
        allow = {n + ".png" for n in json.load(fh)}
    out = []
    for f in os.listdir(IMG):
        if f not in allow:
            continue
        p = os.path.join(IMG, f)
        try:
            im = Image.open(p); im.load()
        except Exception:
            continue
        out.append((p, im.size, _thumb(im)))
    return out


def sharpen(path, sources, tol=10.0):
    doc = pymupdf.open(path)
    swapped = 0
    seen = set()
    for pno in range(len(doc)):
        page = doc[pno]
        for info in page.get_images(full=True):
            xref = info[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                raw = doc.extract_image(xref)
                cur = Image.open(io.BytesIO(raw["image"])); cur.load()
            except Exception:
                continue
            ct = _thumb(cur)
            ratio = cur.width / max(1, cur.height)

            best, bestd, second = None, 1e9, 1e9
            for p, (w, h), th in sources:
                if abs((w / max(1, h)) - ratio) > 0.06 * ratio:
                    continue            # อัตราส่วนต่างกันมาก ไม่ใช่รูปเดียวกันแน่
                if w <= cur.width:
                    continue            # ต้นฉบับไม่ได้ละเอียดกว่า ไม่ต้องสลับ
                d = _diff(ct, th)
                if d < bestd:
                    best, bestd, second = p, d, bestd
                elif d < second:
                    second = d
            # ต้องชนะอันดับสองขาดลอย ไม่งั้นแปลว่าเดาไม่ขาด อย่าเสี่ยงสลับ
            if best and bestd <= tol and second - bestd >= 4.0:
                try:
                    page.replace_image(xref, filename=best)   # เป็นเมธอดของ Page ไม่ใช่ Document
                    swapped += 1
                except Exception as e:
                    print(f"    สลับรูปไม่สำเร็จ ({type(e).__name__}: {e})")
    if swapped:
        tmp = path + ".tmp"
        doc.save(tmp, garbage=3, deflate=True)
        doc.close()
        os.replace(tmp, path)
    else:
        doc.close()
    return swapped


def main():
    files = sys.argv[1:]
    if not files:
        sys.exit("ใช้: python sharpen.py <ไฟล์.pdf> [...]")
    sources = load_sources()
    for f in files:
        if not os.path.exists(f):
            print(f"  ไม่เจอไฟล์: {f}"); continue
        n = sharpen(f, sources)
        print(f"  คมขึ้น {n} รูป  ·  {os.path.basename(f)}")


if __name__ == "__main__":
    main()

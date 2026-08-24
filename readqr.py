#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""อ่าน QR code จากไฟล์ PDF ในโฟลเดอร์ reference/

หนังสือติวหลายเล่มพิมพ์ QR "สแกนดูเฉลย" ไว้ท้ายหน้า ซึ่งเป็นทางเดียวที่จะได้เฉลย
เพราะในตัวเล่มไม่มีเฉลยพิมพ์ไว้เลย

    python readqr.py                          อ่านทุกไฟล์ใน reference/
    python readqr.py reference/tgat2          อ่านเฉพาะโฟลเดอร์นั้น
    python readqr.py "reference/tgat2/TGAT2 Dek66.pdf"

**เคล็ดสำคัญ** — อย่าเรนเดอร์ทั้งหน้าแล้วค่อยหา QR ลายจะเบลอจนถอดไม่ออก
ให้ดึงรูปที่ฝังอยู่ใน PDF ออกมาถอดทีละรูปแทน ได้บิตแมปคมชัดเต็มความละเอียดเดิม
(ทดสอบแล้ว: เรนเดอร์ทั้งหน้าที่ 350 dpi ถอดไม่ออก · ดึงรูปฝัง 100x100 ถอดออกทันที)
"""
import sys, os, io, glob

try:
    import pymupdf, cv2, numpy as np
    from PIL import Image
except ImportError as e:
    sys.exit(f"ต้องลงไลบรารีก่อน: pip install pymupdf opencv-python-headless pillow numpy  ({e})")

DET = cv2.QRCodeDetector()


def decode_image(raw):
    """ลองถอด QR จากบิตแมปหนึ่งรูป ขยายหลายขนาดเผื่อรูปเล็กเกินไป"""
    try:
        im = Image.open(io.BytesIO(raw)).convert("L")
    except Exception:
        return None
    w, h = im.size
    if h == 0 or not (0.8 < w / h < 1.25) or min(w, h) < 40:
        return None                      # QR เป็นจัตุรัสเสมอ อย่างอื่นข้าม
    for scale in (1, 3, 6):
        arr = np.array(im.resize((w * scale, h * scale), Image.NEAREST))
        txt, _, _ = DET.detectAndDecode(arr)
        if txt:
            return txt
    return None


def scan_pdf(path, verbose=False):
    """คืน dict {ข้อความที่ถอดได้: [เลขหน้าที่เจอ]}"""
    found = {}
    try:
        doc = pymupdf.open(path)
    except Exception as e:
        print(f"  เปิดไม่ได้: {e}")
        return found
    for pno in range(len(doc)):
        for info in doc[pno].get_images(full=True):
            try:
                raw = doc.extract_image(info[0])["image"]
            except Exception:
                continue
            txt = decode_image(raw)
            if txt:
                found.setdefault(txt, []).append(pno + 1)
        if verbose and pno % 25 == 24:
            print(f"    ...หน้า {pno+1}/{len(doc)}", flush=True)
    doc.close()
    return found


def targets(arg):
    if arg is None:
        arg = "reference"
    if os.path.isfile(arg):
        return [arg]
    return sorted(glob.glob(os.path.join(arg, "**", "*.pdf"), recursive=True))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    files = targets(sys.argv[1] if len(sys.argv) > 1 else None)
    if not files:
        sys.exit("ไม่เจอไฟล์ PDF")

    total = 0
    for f in files:
        print(f"\n=== {os.path.relpath(f)} ===", flush=True)
        found = scan_pdf(f, verbose=True)
        if not found:
            print("  ไม่เจอ QR")
            continue
        for txt, pages in sorted(found.items(), key=lambda kv: kv[1][0]):
            total += 1
            span = f"หน้า {pages[0]}" if len(pages) == 1 else f"หน้า {pages[0]}–{pages[-1]} ({len(pages)} หน้า)"
            print(f"  {span:<28} {txt}")

    print(f"\nรวมเจอ {total} รหัสที่ไม่ซ้ำกัน")
    if total:
        print("QR พวกนี้มักเป็นลิงก์เฉลย — เปิดดูเองก่อนใช้ว่าตรงกับชุดไหน")


if __name__ == "__main__":
    main()

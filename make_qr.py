#!/usr/bin/env python3
"""Make a print-ready QR code (SVG) for every video page, for the book layout.

Run once the domain is registered:  pip install qrcode  then  python make_qr.py
Each code points at https://<domain>/<slug>, which never changes even if the video does.
"""
import json, os
import qrcode, qrcode.image.svg

ROOT = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(ROOT, "videos.json"), encoding="utf-8"))
domain = data["site"]["domain"]
out = os.path.join(ROOT, "qr")
os.makedirs(out, exist_ok=True)
for v in data["videos"]:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2,
                       image_factory=qrcode.image.svg.SvgPathImage)
    qr.add_data(f"https://{domain}/{v['slug']}")
    qr.make(fit=True)
    qr.make_image().save(os.path.join(out, f"{v['slug']}.svg"))
print(f"Wrote {len(data['videos'])} QR codes to qr/ for https://{domain}/...")

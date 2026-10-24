"""Run once on your laptop to make the Stage 2 QR image.

    pip install "qrcode[pil]"
    python tools/make_qr.py

The PNG goes in backend/app/assets (NOT in static), so the server only
hands it out to the right player after the right question is solved.
"""

from pathlib import Path

import qrcode

TEXT = "ATTACKER SCRATCHPAD // my caesar shift is 3 // do not forget"

out = (
    Path(__file__).resolve().parent.parent
    / "backend" / "app" / "assets" / "stage2_scratch_qr.png"
)
out.parent.mkdir(parents=True, exist_ok=True)
qrcode.make(TEXT, box_size=10, border=4).save(out)
print("Saved", out)
"""Run once on your laptop to make the 6 QR tiles for Round 4.

    pip install qrcode
    python tools/make_qr_tiles.py

It writes stage4_tile1.png ... stage4_tile6.png into backend/app/assets (NOT
into static, so the server only hands each tile out after its lock is open).
It also writes tools/stage4_qr_preview.png: the finished QR code. Scan THAT
with your phone once to check that the text says KS-4D91.

Tiles are numbered left to right, top to bottom: 1 2 3 / 4 5 6.
"""

import struct
import zlib
from pathlib import Path

TEXT = "KS-4D91"   # fragment 4: this is what the phone shows after scanning
PX = 12            # pixels per QR square in the tile images (the board shows them 1:1)
COLS, ROWS = 3, 2  # board layout: 3 tiles across, 2 down
QUIET = 4          # white border around the code, in squares

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "backend" / "app" / "assets"
PREVIEW = Path(__file__).resolve().parent / "stage4_qr_preview.png"


def get_matrix(text: str) -> list[list[bool]]:
    """The QR code as rows of True (dark) and False (light) squares."""
    import qrcode

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=1, border=0
    )
    qr.add_data(text)
    qr.make(fit=True)
    return [[bool(cell) for cell in row] for row in qr.get_matrix()]


def make_canvas(matrix: list[list[bool]]) -> list[list[bool]]:
    """Put the code on a white canvas whose side divides evenly into the tiles."""
    side = len(matrix) + 2 * QUIET
    while side % COLS or side % ROWS:
        side += 1
    canvas = [[False] * side for _ in range(side)]
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            canvas[y + QUIET][x + QUIET] = dark
    return canvas


def write_png(path: Path, grid: list[list[bool]], px: int) -> None:
    """Write a black and white PNG without needing any imaging library."""
    height, width = len(grid) * px, len(grid[0]) * px
    raw = bytearray()
    for row in grid:
        line = bytearray([0])  # filter type 0
        for dark in row:
            line.extend((0 if dark else 255) for _ in range(px))
        raw.extend(line * px)

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def cut_tiles(canvas: list[list[bool]]) -> list[list[list[bool]]]:
    side = len(canvas)
    tile_w, tile_h = side // COLS, side // ROWS
    tiles = []
    for r in range(ROWS):
        for c in range(COLS):
            tiles.append(
                [row[c * tile_w:(c + 1) * tile_w]
                 for row in canvas[r * tile_h:(r + 1) * tile_h]]
            )
    return tiles


def main() -> None:
    canvas = make_canvas(get_matrix(TEXT))
    ASSETS.mkdir(parents=True, exist_ok=True)
    for n, tile in enumerate(cut_tiles(canvas), start=1):
        write_png(ASSETS / f"stage4_tile{n}.png", tile, PX)
    write_png(PREVIEW, canvas, PX)
    side = len(canvas)
    print(f"Saved 6 tiles in {ASSETS}")
    print(f"Tile size: {side // COLS * PX} x {side // ROWS * PX} pixels")
    print(f"Saved preview {PREVIEW}  (scan it: it must say {TEXT})")


if __name__ == "__main__":
    main()
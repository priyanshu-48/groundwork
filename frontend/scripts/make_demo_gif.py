"""Assembles captioned frames into the README GIF (a storyboard, not a screen recording).

From backend/:  uv run --with pillow python ../frontend/scripts/make_demo_gif.py <frames-dir> ../docs/demo.gif
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CAPTIONS = {
    "login": "Try the demo: no account needed",
    "documents": "325 synthetic documents: 25 contracts and 300 invoices",
    "suggestions": "Ask in plain language, or pick a suggestion",
    "working": "The agent searches the documents, then answers",
    "answer": "Every claim carries a citation, like [C1]",
    "source": "Click it: the exact page and sentence it came from",
    "steps": "Steps show each tool call and how long it took",
    "aggregate": "Totals come from a parameterised SQL tool, not guesses",
    "multihop": "Multi-hop: contract terms plus invoice sums in one call",
}
WIDTH = 960
BAR = 54


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def frame(path: Path, caption: str) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img = img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)
    canvas = Image.new("RGB", (WIDTH, img.height + BAR), (15, 23, 42))
    canvas.paste(img, (0, 0))
    draw = ImageDraw.Draw(canvas)
    f = font(24)
    w = draw.textlength(caption, font=f)
    draw.text(((WIDTH - w) / 2, img.height + 13), caption, fill=(255, 255, 255), font=f)
    return canvas


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    frames = []
    for p in sorted(src.glob("*.png")):
        key = p.stem.split("-", 1)[1]
        frames.append(frame(p, CAPTIONS[key]))
    # one shared palette keeps the file small and the colours stable between frames
    paletted = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    paletted[0].save(dst, save_all=True, append_images=paletted[1:], duration=2400, loop=0, optimize=True)
    print(f"{len(frames)} frames -> {dst} ({dst.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

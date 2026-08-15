#!/usr/bin/env python3
"""Generate cover art.

Produces:
  figures/cover-ebook.png     1600x2560, Kindle / KDP ebook
  figures/cover-web.png       1000x1600, the website
  figures/favicon.png         192x192
  figures/cover-paperback.png full wrap for KDP 6x9 paperback, with the
                              spine width computed from the actual page
                              count of dist/The-Evidence-Behind.pdf

The cover sets in TeX Gyre Pagella, the same face as the book's interior,
by loading the OTF straight out of the TeX tree. Nothing to install.

The visual idea is the book's argument: four bars for GRADE's four
certainty levels, each shorter than the last, under a single confident
"STRONG" stamp. The label stays the same width while the evidence
underneath it thins out.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "figures"

TITLE = "The\nEvidence\nBehind"
SUBTITLE = "What we actually know about\nlooking after your teeth"
AUTHOR = "Ahmad Sofi-Mahmudi"

# --- palette -------------------------------------------------------
INK = (18, 26, 31)          # near-black slate
PAPER = (246, 244, 239)     # warm off-white
ACCENT = (196, 152, 62)     # brass, the "Strong" stamp
MUTED = (138, 150, 158)

# --- typefaces -----------------------------------------------------
# The four faces are vendored into _assets/fonts/ (GUST Font License, see
# the README there) so this runs on a CI box with no TeX installed. The
# TeX tree is only a fallback for a partial checkout.
FONT_ROOTS = [
    ROOT / "_assets/fonts",
    Path.home() / "Library/TinyTeX/texmf-dist/fonts/opentype/public/tex-gyre",
    Path("/usr/local/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre"),
    Path("/usr/local/texlive/2025/texmf-dist/fonts/opentype/public/tex-gyre"),
    Path("/usr/share/texmf/fonts/opentype/public/tex-gyre"),
]


def find_font(name: str) -> Path:
    for root in FONT_ROOTS:
        p = root / name
        if p.exists():
            return p
    raise SystemExit(
        f"Font {name} not found. Looked in:\n  "
        + "\n  ".join(str(r) for r in FONT_ROOTS)
    )


SERIF_BOLD = find_font("texgyrepagella-bold.otf")
SERIF_REG = find_font("texgyrepagella-regular.otf")
SERIF_ITAL = find_font("texgyrepagella-italic.otf")
SANS_BOLD = find_font("texgyreheros-bold.otf")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def draw_front(img: Image.Image, x0: int, y0: int, w: int, h: int) -> None:
    """Draw the front panel into img at (x0, y0) with size (w, h)."""
    d = ImageDraw.Draw(img)
    s = w / 1600.0  # scale everything off a 1600px-wide reference

    def S(v: float) -> int:
        return int(round(v * s))

    d.rectangle([x0, y0, x0 + w, y0 + h], fill=INK)

    margin = S(150)
    left = x0 + margin

    # --- the "STRONG" stamp ---------------------------------------
    stamp_y = y0 + S(230)
    f_stamp = font(SANS_BOLD, S(46))
    label = "STRONG"
    # letterspace it by hand; PIL has no tracking control
    tracked = "  ".join(label)
    d.text((left, stamp_y), tracked, font=f_stamp, fill=ACCENT)
    bbox = d.textbbox((left, stamp_y), tracked, font=f_stamp)
    d.rectangle(
        [left - S(28), stamp_y - S(30), bbox[2] + S(28), bbox[3] + S(26)],
        outline=ACCENT,
        width=S(3),
    )

    # --- the thinning bars ----------------------------------------
    # High, moderate, low, very low. Each shorter than the one above.
    bars_y = stamp_y + S(150)
    bar_h = S(14)
    gap = S(26)
    widths = [1.00, 0.72, 0.44, 0.19]
    # `full` is already in panel pixels because `margin` is scaled, so it
    # must not go through S() again.
    full = w - 2 * margin
    for i, frac in enumerate(widths):
        y = bars_y + i * (bar_h + gap)
        split = left + int(full * frac)
        d.rectangle([left, y, split, y + bar_h], fill=PAPER)
        d.rectangle([split, y, left + full, y + bar_h], fill=(38, 48, 55))

    # --- title -----------------------------------------------------
    # Sits low enough that the space under the subtitle reads as margin
    # rather than as a hole. The stamp and bars keep the top third.
    title_y = bars_y + 4 * (bar_h + gap) + S(430)
    f_title = font(SERIF_BOLD, S(178))
    for i, line in enumerate(TITLE.split("\n")):
        d.text((left, title_y + i * S(184)), line, font=f_title, fill=PAPER)

    # --- rule ------------------------------------------------------
    rule_y = title_y + 3 * S(184) + S(90)
    d.rectangle([left, rule_y, left + S(240), rule_y + S(6)], fill=ACCENT)

    # --- subtitle --------------------------------------------------
    sub_y = rule_y + S(80)
    f_sub = font(SERIF_ITAL, S(58))
    for i, line in enumerate(SUBTITLE.split("\n")):
        d.text((left, sub_y + i * S(76)), line, font=f_sub, fill=MUTED)

    # --- author ----------------------------------------------------
    f_auth = font(SANS_BOLD, S(52))
    ab = d.textbbox((0, 0), AUTHOR, font=f_auth)
    d.text(
        (left, y0 + h - margin - (ab[3] - ab[1])),
        AUTHOR,
        font=f_auth,
        fill=PAPER,
    )


def make_front(width: int, height: int, out: Path) -> None:
    img = Image.new("RGB", (width, height), INK)
    draw_front(img, 0, 0, width, height)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    print(f"  {out.relative_to(ROOT)}  {width}x{height}")


def make_favicon(out: Path) -> None:
    size = 192
    img = Image.new("RGB", (size, size), INK)
    d = ImageDraw.Draw(img)
    # The thinning bars alone, which is the book's argument in one glyph.
    for i, frac in enumerate([1.00, 0.72, 0.44, 0.19]):
        y = 44 + i * 30
        d.rectangle([32, y, 32 + int(128 * frac), y + 14], fill=PAPER)
    img.save(out, "PNG")
    print(f"  {out.relative_to(ROOT)}  {size}x{size}")


def pdf_page_count(pdf: Path) -> int | None:
    if not pdf.exists():
        return None
    try:
        out = subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
        ).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        return int(m.group(1)) if m else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def make_paperback_wrap(pages: int, out: Path) -> None:
    """Full KDP wrap: back cover, spine, front cover, plus bleed.

    KDP 6x9in, white paper: spine = pages x 0.002252in.
    Bleed is 0.125in on top, bottom and outer edges.
    """
    DPI = 300
    trim_w, trim_h = 6.0, 9.0
    bleed = 0.125
    spine_in = pages * 0.002252

    total_w_in = trim_w * 2 + spine_in + bleed * 2
    total_h_in = trim_h + bleed * 2

    W, H = int(total_w_in * DPI), int(total_h_in * DPI)
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)

    bleed_px = int(bleed * DPI)
    front_w = int(trim_w * DPI)
    spine_px = int(spine_in * DPI)

    front_x = bleed_px + front_w + spine_px
    draw_front(img, front_x, bleed_px, front_w, int(trim_h * DPI))

    # --- spine ------------------------------------------------------
    spine_x = bleed_px + front_w
    d.rectangle(
        [spine_x, 0, spine_x + spine_px, H], fill=(12, 19, 23)
    )
    if spine_in >= 0.25:  # KDP will not print spine text below this
        f = font(SERIF_BOLD, int(spine_px * 0.42))
        txt = "The Evidence Behind    ·    Sofi-Mahmudi"
        tmp = Image.new("RGB", (int(trim_h * DPI), spine_px), (12, 19, 23))
        td = ImageDraw.Draw(tmp)
        tb = td.textbbox((0, 0), txt, font=f)
        td.text(
            ((tmp.width - (tb[2] - tb[0])) // 2,
             (tmp.height - (tb[3] - tb[1])) // 2 - tb[1]),
            txt, font=f, fill=PAPER,
        )
        img.paste(tmp.rotate(-90, expand=True), (spine_x, bleed_px))

    # --- back cover -------------------------------------------------
    bx = bleed_px
    by = bleed_px
    bw, bh = front_w, int(trim_h * DPI)
    d.rectangle([0, 0, spine_x, H], fill=INK)

    m = int(0.6 * DPI)
    f_blurb = font(SERIF_REG, 46)
    blurb = (
        "Britain's national oral health guidance labels\n"
        "some of its advice “Strong.” This book follows\n"
        "each of those labels back to the study it rests\n"
        "on, and asks a single question: does that study\n"
        "answer the question the advice asks?\n\n"
        "Often it does not. Not because anyone was\n"
        "careless, but because a recommendation can\n"
        "bundle several pieces of advice together and\n"
        "let the best-evidenced one award a Strong\n"
        "badge to all of them.\n\n"
        "A dentist and research methodologist shows\n"
        "his working, chapter by chapter, and says\n"
        "plainly what he would need to change his mind."
    )
    d.multiline_text((bx + m, by + m), blurb, font=f_blurb,
                     fill=PAPER, spacing=18)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", dpi=(DPI, DPI))
    print(
        f"  {out.relative_to(ROOT)}  {W}x{H}px "
        f"({total_w_in:.3f}x{total_h_in:.3f}in, spine {spine_in:.3f}in "
        f"for {pages} pages)"
    )


def main() -> int:
    print("covers:")
    make_front(1600, 2560, FIGS / "cover-ebook.png")
    make_front(1000, 1600, FIGS / "cover-web.png")
    make_favicon(FIGS / "favicon.png")

    pdf = ROOT / "dist" / "The-Evidence-Behind.pdf"
    pages = pdf_page_count(pdf)
    if pages:
        make_paperback_wrap(pages, FIGS / "cover-paperback.png")
    else:
        print("  (paperback wrap skipped: build the print PDF first, "
              "the spine width depends on its page count)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

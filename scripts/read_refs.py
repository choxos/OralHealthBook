#!/usr/bin/env python3
"""Extract readable text from the supplied reference library.

documentation/refs/ holds Cochrane full texts (HTML + PDF), their
"characteristics of included studies" companions, and a pile of primary
reports. This turns all of it into plain text in the scratchpad so the
audits can quote from the actual documents rather than from abstracts.

Nothing here is written into the repository. documentation/ is gitignored;
this writes to the scratchpad only.
"""
from __future__ import annotations
import re, sys, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
SRC = Path("documentation/refs")
OUT = Path("/private/tmp/claude-501/-Users-choxos-Documents-GitHub-OralHealthBook"
           "/28c7e511-fc53-4c96-a7d4-04b5e25040a5/scratchpad/refs")
OUT.mkdir(parents=True, exist_ok=True)


def clean(t: str) -> str:
    t = t.replace("\xa0", " ").replace("‐", "-")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    return t.strip()


def from_html(p: Path) -> str:
    from bs4 import BeautifulSoup
    s = BeautifulSoup(p.read_text(encoding="utf-8", errors="replace"), "html.parser")
    for j in s(["script", "style", "nav", "header", "footer"]):
        j.decompose()
    main = s.find("article") or s.find("main") or s.find(id="content") or s
    return clean(main.get_text("\n"))


def from_pdf(p: Path) -> str:
    from pypdf import PdfReader
    r = PdfReader(str(p))
    return clean("\n".join(
        f"\n=== [page {i+1}] ===\n" + (pg.extract_text() or "")
        for i, pg in enumerate(r.pages)))


def from_docx(p: Path) -> str:
    import zipfile
    with zipfile.ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    return clean(re.sub(r"<[^>]+>", "", xml))


def main() -> int:
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    rows = []
    for p in sorted(SRC.iterdir()):
        if p.is_dir() or p.name.startswith("."):
            continue
        if want and want.lower() not in p.name.lower():
            continue
        try:
            if p.suffix.lower() in (".html", ".htm"):
                txt = from_html(p)
            elif p.suffix.lower() == ".pdf":
                txt = from_pdf(p)
            elif p.suffix.lower() == ".docx":
                txt = from_docx(p)
            else:
                continue
        except Exception as e:
            rows.append((p.name, f"FAILED: {type(e).__name__}: {e}", 0))
            continue
        # Keep HTML and PDF separately: Cochrane PDFs extract with spaced
        # glyphs, so "longer" is not "better". Suffix by source format.
        tag = {".html": "-html", ".htm": "-html", ".pdf": "-pdf", ".docx": "-docx"}[p.suffix.lower()]
        dest = OUT / (re.sub(r"[^\w.-]+", "_", p.stem) + tag + ".txt")
        dest.write_text(txt, encoding="utf-8")
        rows.append((p.name, dest.name, len(txt)))

    w = max(len(r[0]) for r in rows) if rows else 10
    for name, dest, n in rows:
        print(f"{name:<{w}}  {n:>9,}  {dest}")
    print(f"\n{len(rows)} file(s) -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

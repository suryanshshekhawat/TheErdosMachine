#!/usr/bin/env python3
"""
extract_erdos.py  -  pull the problem-statement box out of every page of an
erdosproblems.com print-to-PDF and build a dictionary keyed by problem.

Pipeline
  1. render each PDF page to an image (PyMuPDF, vector -> crisp at any DPI)
  2. detect the bordered problem box(es) on the page  (OpenCV, no model needed)
  3. read the PDF text layer clipped to that box  (free, exact IF it survived)
  4. optionally transcribe the crop to LaTeX with a vision model
  5. parse status / prize / categories and dump JSON

Usage
  # FIRST: see whether the text layer is usable (no OCR needed if it is)
  python extract_erdos.py --pdf erdos.pdf --diagnose

  # crop everything + keep text layer, no transcription yet
  python extract_erdos.py --pdf erdos.pdf --out problems.json --crops crops/

  # also transcribe each crop to LaTeX with Claude (needs ANTHROPIC_API_KEY)
  python extract_erdos.py --pdf erdos.pdf --out problems.json --crops crops/ \
                          --transcribe claude

Deps:  pip install pymupdf opencv-python-headless numpy pillow
       (+ anthropic   if --transcribe claude)
"""
import argparse, base64, json, os, re, sys
import numpy as np, cv2, fitz   # fitz == pymupdf


# ----------------------------------------------------------------------------
# CV: find the bordered problem box(es) on a page image.  All thresholds are
# fractions of W/H, so it is resolution independent.
# ----------------------------------------------------------------------------
def _lines(ink, frac, axis, dim):
    k = (int(frac * dim), 1) if axis == 0 else (1, int(frac * dim))
    ker = cv2.getStructuringElement(cv2.MORPH_RECT, k)
    L = cv2.morphologyEx(ink, cv2.MORPH_OPEN, ker)
    proj = L.sum(axis=1 - axis)
    idx = np.where(proj > 0.5 * dim * 255)[0]
    groups = []
    if len(idx):
        s = p = idx[0]
        for v in idx[1:]:
            if v - p > 5:
                groups.append((s + p) // 2); s = v
            p = v
        groups.append((s + p) // 2)
    return L, groups


def detect_boxes(img):
    """Return list of (x0,y0,x1,y1) for each problem box on the page (0,1,2...)."""
    H, W = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ink = (gray < 245).astype(np.uint8) * 255
    _, hrows = _lines(ink, 0.45, 0, W)   # long horizontal borders (top/bottom)
    Lv, _    = _lines(ink, 0.10, 1, H)   # box side borders
    boxes = []
    for i in range(0, len(hrows) - 1, 2):            # pair (top, bottom)
        top, bot = hrows[i], hrows[i + 1]
        if not (40 < bot - top < 0.92 * H):
            continue
        band = Lv[top:bot, :]
        cols = np.where(band.sum(axis=0) > 0.6 * (bot - top) * 255)[0]
        x0, x1 = (cols.min(), cols.max()) if len(cols) >= 2 else (0, W - 1)
        # walk upward to swallow the OPEN/SOLVED status tab that breaks the border
        t = top
        while t > 0 and ink[t - 1, x0 + 5:x0 + 120].sum() > 0:
            t -= 1
        boxes.append((int(max(0, x0 - 3)), int(max(0, min(top, t) - 3)),
                      int(min(W, x1 + 4)),  int(min(H, bot + 3))))
    return boxes


# ----------------------------------------------------------------------------
# light parsing of the box text layer
# ----------------------------------------------------------------------------
def parse_meta(text):
    m = {"status": None, "prize": None, "categories": None, "references": None}
    s = re.search(r"\b(OPEN|SOLVED)\b", text)
    if s:
        m["status"] = s.group(1)
    p = re.search(r"\$\s*([\d,]+)", text)          # prize like  $500
    if p:
        m["prize"] = "$" + p.group(1)
    # category line: the trailing  "number theory | additive combinatorics"
    cat = re.findall(r"([a-z][a-z &-]+\|[a-z &|-]+)", text)
    if cat:
        m["categories"] = [c.strip() for c in cat[-1].split("|")]
    refs = re.findall(r"\[[A-Za-z]{2,}\d{2,}[a-z]?(?:,[^\]]*)?\]", text)
    if refs:
        m["references"] = refs
    return m


# ----------------------------------------------------------------------------
# transcription back-ends  (crop image -> structured fields incl. LaTeX)
# ----------------------------------------------------------------------------
TR_PROMPT = (
    "This is a single problem box from erdosproblems.com. Transcribe it. "
    "Return ONLY minified JSON with keys: status (OPEN or SOLVED), prize "
    "(string like \"$500\" or null), statement_latex (the full problem "
    "statement, using $...$ for inline math and \\[...\\] for display math, "
    "verbatim, no commentary), categories (array of strings). No markdown fences."
)

def transcribe_claude(png_path, model="claude-sonnet-4-6"):
    import anthropic
    client = anthropic.Anthropic()                 # reads ANTHROPIC_API_KEY
    b64 = base64.standard_b64encode(open(png_path, "rb").read()).decode()
    r = client.messages.create(
        model=model, max_tokens=1500,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64",
             "media_type": "image/png", "data": b64}},
            {"type": "text", "text": TR_PROMPT}]}])
    txt = "".join(b.text for b in r.content if b.type == "text").strip()
    txt = re.sub(r"^```\w*|```$", "", txt).strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return {"statement_latex": txt}            # keep raw if it isn't clean JSON

def transcribe_pix2tex(png_path):
    # offline fallback. NOTE: LaTeX-OCR is trained on pure equations and mangles
    # the prose around the math; weights download from HuggingFace on first run.
    from pix2tex.cli import LatexOCR
    from PIL import Image
    if not hasattr(transcribe_pix2tex, "_m"):
        transcribe_pix2tex._m = LatexOCR()
    return {"statement_latex": transcribe_pix2tex._m(Image.open(png_path))}


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default="problems.json")
    ap.add_argument("--crops", default="crops")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--diagnose", action="store_true",
                    help="dump text layer of the first 3 boxes and exit")
    ap.add_argument("--transcribe", choices=["none", "claude", "pix2tex"],
                    default="none")
    ap.add_argument("--model", default="claude-sonnet-4-6")
    a = ap.parse_args()

    os.makedirs(a.crops, exist_ok=True)
    doc = fitz.open(a.pdf)
    zoom = a.dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    out, idx, diagnosed = [], 0, 0

    for pno in range(len(doc)):
        page = doc[pno]
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if pix.n >= 3 else \
              cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        for (x0, y0, x1, y1) in detect_boxes(img):
            # text layer clipped to this box (image px -> pdf points)
            clip = fitz.Rect(x0 / zoom, y0 / zoom, x1 / zoom, y1 / zoom)
            text = page.get_text("text", clip=clip).strip()

            if a.diagnose:
                print(f"\n=== page {pno+1} box @({x0},{y0},{x1},{y1}) ===")
                print(text if text else "  <no text layer — needs OCR/transcribe>")
                diagnosed += 1
                if diagnosed >= 3:
                    return
                continue

            idx += 1
            crop_path = os.path.join(a.crops, f"p{idx:03d}.png")
            cv2.imwrite(crop_path, img[y0:y1, x0:x1])

            rec = {"idx": idx, "page": pno + 1, "crop": crop_path,
                   "text_layer": text, "statement_latex": None}
            rec.update(parse_meta(text))

            if a.transcribe != "none":
                fn = transcribe_claude if a.transcribe == "claude" else transcribe_pix2tex
                try:
                    tr = fn(crop_path) if a.transcribe == "pix2tex" \
                         else fn(crop_path, a.model)
                    for k in ("status", "prize", "categories", "statement_latex"):
                        if tr.get(k):
                            rec[k] = tr[k]
                except Exception as e:
                    rec["transcribe_error"] = str(e)

            out.append(rec)
            print(f"[{idx:>3}] page {pno+1:>3}  {rec.get('status')}  "
                  f"{rec.get('prize') or ''}")

    if not a.diagnose:
        json.dump(out, open(a.out, "w"), indent=2, ensure_ascii=False)
        print(f"\n{len(out)} problems -> {a.out}   crops -> {a.crops}/")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
erdos_statements.py  --  extract every problem STATEMENT (as LaTeX) from an
erdosproblems.com print-to-PDF into a plain .txt.   Pure CV for layout; a local
offline math-OCR model for the LaTeX (no LLM / no API calls).

What it does
  1. render each page (PyMuPDF)
  2. CV-detect the bordered problem box(es) on the page, classifying each as
     starts (has top border) / ends (has bottom border).  A box may therefore
     be split across a page break: start on page N (top border, no bottom),
     continue/finish on page N+1 (bottom border, no top).
  3. stitch split halves back into one box and crop its interior
  4. OCR the interior to LaTeX, strip the status tab / references / category
     lines, keep only the statement
  5. write statements to a .txt, one per problem

OCR engines (--ocr):
  text     PDF text layer via PyMuPDF. Instant, no model. Prose comes out clean;
           MathJax math usually does NOT round-trip to LaTeX. Run this FIRST to
           see what your particular PDF already contains for free.
  nougat   facebook/nougat-base (default). Vision-OCR for scientific docs,
           emits inline $...$ / \\[...\\]. Best for mixed prose+math. Offline
           after a one-time weight download from HuggingFace.
  pix2tex  LaTeX-OCR. Good for equation-dominant statements, weak on prose.

Deps:  pip install pymupdf opencv-python-headless numpy pillow
  nougat:  pip install transformers torch                (downloads ~1.4GB once)
  pix2tex: pip install "pix2tex[cli]"
"""
import argparse, re, sys
import numpy as np, cv2
try:                       # PyMuPDF's own name; avoids the unrelated PyPI 'fitz' pkg
    import pymupdf as fitz
except ImportError:
    import fitz


# ===========================================================================
# CV  --  detect problem boxes, including page-split halves
# ===========================================================================
def _runs(idx, gap):
    g = []
    if len(idx):
        s = p = int(idx[0])
        for v in idx[1:]:
            v = int(v)
            if v - p > gap:
                g.append((s, p)); s = v
            p = v
        g.append((s, p))
    return g


def detect_boxes(img, header_frac=0.05, footer_frac=0.04):
    """List of dict(x0,x1,y0,y1, starts, ends) top-to-bottom.
    starts = top border present (box begins here);  ends = bottom border present.
    A split box is (starts=True, ends=False) on page N then
                   (starts=False, ends=True) on page N+1."""
    H, W = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ink = (gray < 230).astype(np.uint8) * 255          # faint OR bold borders
    htop, hbot = header_frac * H, H - footer_frac * H

    vk = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(20, int(0.06 * H))))
    V = cv2.morphologyEx(ink, cv2.MORPH_OPEN, vk)       # tall side borders
    hk = cv2.getStructuringElement(cv2.MORPH_RECT, (max(40, int(0.40 * W)), 1))
    Hh = cv2.morphologyEx(ink, cv2.MORPH_OPEN, hk)      # long top/bottom borders
    hrows = [(a + b) // 2 for a, b in _runs(np.where(Hh.sum(1) > 0.40 * W * 255)[0], 6)]

    xcl = _runs(np.where(V.sum(0) > 0.05 * H * 255)[0], int(0.05 * W))
    xcl = [c for c in xcl if 3 < (c[0] + c[1]) // 2 < W - 3]   # drop edge artifacts
    boxes = []
    if len(xcl) >= 2:
        x0 = (xcl[0][0] + xcl[0][1]) // 2
        x1 = (xcl[-1][0] + xcl[-1][1]) // 2
        if (x1 - x0) < 0.70 * W:                       # reject narrow chrome
            return boxes
        side = (V[:, max(0, x0 - 3):x0 + 4].sum(1) +
                V[:, x1 - 3:min(W, x1 + 4)].sum(1))
        for ya, yb in _runs(np.where(side > 0)[0], int(0.05 * H)):
            if yb - ya < 0.05 * H:
                continue
            top = [r for r in hrows if ya - 0.12 * H <= r <= ya + 0.04 * H]
            bot = [r for r in hrows if yb - 0.04 * H <= r <= yb + 0.12 * H]
            starts = bool(top) and ya > htop
            ends   = bool(bot) and yb < hbot
            y0 = min([ya] + top) if starts else int(htop)
            y1 = max([yb] + bot) if ends   else int(hbot)
            boxes.append(dict(x0=x0, x1=x1, y0=int(y0), y1=int(y1),
                              starts=starts, ends=ends))
    return boxes


# ===========================================================================
# OCR engines  (image / pdf-region  ->  raw text with LaTeX)
# ===========================================================================
class TextLayer:
    name = "text"
    def __init__(self, *_): pass
    def read(self, page, zoom, x0, y0, x1, y1, img):
        clip = fitz.Rect(x0 / zoom, y0 / zoom, x1 / zoom, y1 / zoom)
        return page.get_text("text", clip=clip).strip()

class Nougat:
    name = "nougat"
    def __init__(self, *_):
        from transformers import NougatProcessor, VisionEncoderDecoderModel
        import torch
        self.torch = torch
        self.proc = NougatProcessor.from_pretrained("facebook/nougat-base")
        self.model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-base")
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.dev).eval()
    def read(self, page, zoom, x0, y0, x1, y1, img):
        from PIL import Image
        crop = Image.fromarray(cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2RGB))
        pv = self.proc(crop, return_tensors="pt").pixel_values.to(self.dev)
        with self.torch.no_grad():
            out = self.model.generate(pv, max_new_tokens=512,
                                      bad_words_ids=[[self.proc.tokenizer.unk_token_id]])
        seq = self.proc.batch_decode(out, skip_special_tokens=True)[0]
        return self.proc.post_process_generation(seq, fix_markdown=False).strip()

class Pix2Tex:
    name = "pix2tex"
    def __init__(self, *_):
        import torch
        _o = torch.load
        torch.load = lambda *a, **k: _o(*a, **{**k, "weights_only": False})
        from pix2tex.cli import LatexOCR
        self.m = LatexOCR()
    def read(self, page, zoom, x0, y0, x1, y1, img):
        from PIL import Image
        crop = Image.fromarray(cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2RGB))
        return self.m(crop)

ENGINES = {e.name: e for e in (TextLayer, Nougat, Pix2Tex)}


# ===========================================================================
# strip status tab / references / category, keep the statement
# ===========================================================================
REF_RE  = re.compile(r"\[[A-Za-z]{2,}\d{2,}[a-z]?(?:,\s*[^\]]*)?\]")
CAT_RE  = re.compile(r"^[a-z][a-z &'-]+(\|[a-z &'|-]+)+$")
STAT_RE = re.compile(r"^\s*(OPEN|SOLVED)\b.*$", re.I)
NUM_RE  = re.compile(r"#\s*(\d+)\b")
# running page furniture: timestamp / site title / footer url / page number
FURNITURE_RE = re.compile(
    r"(\d{1,2}/\d{1,2}/\d{2,4})|erdosproblems\.com|Erd[oő]s\s+Problems"
    r"|^\s*\d+\s*/\s*\d+\s*$", re.I)

def clean_statement(raw):
    num = None
    m = NUM_RE.search(raw)
    if m:
        num = int(m.group(1))
    out = []
    for ln in raw.splitlines():
        s = ln.strip()
        if not s:
            continue
        if FURNITURE_RE.search(s):           # timestamp / title / url / page num
            continue
        if STAT_RE.match(s):                 # OPEN / SOLVED  ($prize)
            continue
        if s.lstrip().startswith("#") and REF_RE.search(s):   # "#15: [Er97...]"
            continue
        if CAT_RE.match(s):                  # "number theory | primes"
            continue
        s = REF_RE.sub("", s).strip()        # stray inline refs
        if s:
            out.append(s)
    return num, " ".join(out).strip()


# ===========================================================================
# main  --  page loop + split stitching
# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default="statements.txt")
    ap.add_argument("--ocr", choices=list(ENGINES), default="text")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--crops", default=None, help="dir to dump box crops (debug)")
    a = ap.parse_args()

    if a.crops:
        import os; os.makedirs(a.crops, exist_ok=True)
    eng = ENGINES[a.ocr]()
    doc = fitz.open(a.pdf)
    zoom = a.dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    problems, pending = [], None   # pending = open (un-closed) split box

    def emit(parts):
        raw = "\n".join(p["raw"] for p in parts).strip()
        num, stmt = clean_statement(raw)
        problems.append(dict(num=num,
                             pages=[p["page"] for p in parts],
                             statement=stmt))

    for pno in range(len(doc)):
        page = doc[pno]
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if pix.n >= 3 \
              else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        for bi, b in enumerate(detect_boxes(img)):
            ins = int(0.012 * pix.w)
            x0, x1 = b["x0"] + ins, b["x1"] - ins
            y0 = b["y0"] + ins if b["starts"] else b["y0"]
            y1 = b["y1"] - ins if b["ends"]   else b["y1"]
            if a.crops:
                cv2.imwrite(f"{a.crops}/p{pno+1:03d}_{bi}.png", img[y0:y1, x0:x1])
            part = {"page": pno + 1,
                    "raw": eng.read(page, zoom, x0, y0, x1, y1, img)}

            if b["starts"] and b["ends"]:                 # complete box
                if pending: emit(pending); pending = None
                emit([part])
            elif b["starts"] and not b["ends"]:           # split: start
                if pending: emit(pending)
                pending = [part]
            elif not b["starts"] and not b["ends"]:       # split: middle
                (pending or []).append(part)
            else:                                          # split: end
                emit((pending or []) + [part]); pending = None
    if pending:
        emit(pending)

    with open(a.out, "w", encoding="utf-8") as f:
        f.write(f"% {len(problems)} statements from {a.pdf}  (ocr={a.ocr})\n\n")
        for i, p in enumerate(problems, 1):
            tag = f"#{p['num']}" if p["num"] else f"seq{i}"
            pg = "-".join(map(str, sorted(set(p["pages"]))))
            f.write(f"% ===== {tag}  (page {pg}) =====\n{p['statement']}\n\n")
    print(f"{len(problems)} statements -> {a.out}")
    multi = [p for p in problems if len(set(p['pages'])) > 1]
    if multi:
        print(f"  ({len(multi)} of them were stitched across a page break)")


if __name__ == "__main__":
    main()
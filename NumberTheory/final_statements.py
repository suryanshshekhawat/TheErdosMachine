#!/usr/bin/env python3
"""
final_statements.py  --  stage 2.  Take the same PDF, re-detect the boxes with a
CONSERVATIVE split-stitcher (no runaway merges), then send each problem image to
a vision model that (a) transcribes it to clean LaTeX and (b) judges whether it
is actually a self-contained problem statement.  Non-problems are dropped.

Output: final_statements.txt   (only real statements, clean LaTeX, deduped, sorted)

Why a model here: recovering \\sum / \\frac from MathJax-rendered glyphs cannot be
done by CV or by the PDF text layer (that is why stage-1 'text' came out scrambled).
The vision call also returns is_problem, which filters junk in the same pass.

Run:
  pip install pymupdf opencv-python-headless numpy pillow anthropic
  set ANTHROPIC_API_KEY=...          (PowerShell:  $env:ANTHROPIC_API_KEY="...")
  python final_statements.py --pdf problem_set.pdf
  python final_statements.py --pdf problem_set.pdf --limit 15   # cheap dry run
"""
import argparse, base64, hashlib, io, json, os, re, sys
import numpy as np, cv2
try:
    import pymupdf as fitz
except ImportError:
    import fitz


# --------------------------------------------------------------------------
# CV box detection (same proven detector as stage 1)
# --------------------------------------------------------------------------
def _runs(idx, gap):
    g = []
    if len(idx):
        s = p = int(idx[0])
        for v in idx[1:]:
            v = int(v)
            if v - p > gap: g.append((s, p)); s = v
            p = v
        g.append((s, p))
    return g

def detect_boxes(img, header_frac=0.05, footer_frac=0.04):
    H, W = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ink = (gray < 230).astype(np.uint8) * 255
    htop, hbot = header_frac * H, H - footer_frac * H
    vk = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(20, int(0.06 * H))))
    V = cv2.morphologyEx(ink, cv2.MORPH_OPEN, vk)
    hk = cv2.getStructuringElement(cv2.MORPH_RECT, (max(40, int(0.40 * W)), 1))
    Hh = cv2.morphologyEx(ink, cv2.MORPH_OPEN, hk)
    hrows = [(a + b) // 2 for a, b in _runs(np.where(Hh.sum(1) > 0.40 * W * 255)[0], 6)]
    xcl = _runs(np.where(V.sum(0) > 0.05 * H * 255)[0], int(0.05 * W))
    xcl = [c for c in xcl if 3 < (c[0] + c[1]) // 2 < W - 3]
    boxes = []
    if len(xcl) >= 2:
        x0 = (xcl[0][0] + xcl[0][1]) // 2; x1 = (xcl[-1][0] + xcl[-1][1]) // 2
        if (x1 - x0) < 0.70 * W:
            return boxes
        side = (V[:, max(0, x0 - 3):x0 + 4].sum(1) + V[:, x1 - 3:min(W, x1 + 4)].sum(1))
        for ya, yb in _runs(np.where(side > 0)[0], int(0.05 * H)):
            if yb - ya < 0.05 * H: continue
            top = [r for r in hrows if ya - 0.12 * H <= r <= ya + 0.04 * H]
            bot = [r for r in hrows if yb - 0.04 * H <= r <= yb + 0.12 * H]
            starts = bool(top) and ya > htop
            ends   = bool(bot) and yb < hbot
            y0 = min([ya] + top) if starts else int(htop)
            y1 = max([yb] + bot) if ends   else int(hbot)
            boxes.append(dict(x0=x0, x1=x1, y0=int(y0), y1=int(y1),
                              starts=starts, ends=ends))
    return boxes


# --------------------------------------------------------------------------
# vision model: image -> {is_problem, status, number, statement_latex}
# --------------------------------------------------------------------------
PROMPT = (
    "This is one box clipped from erdosproblems.com (possibly two stitched halves "
    "of a box that spanned a page break). Return ONLY minified JSON, no fences, "
    "keys exactly: is_problem (bool), status (\"open\"|\"solved\"|null), "
    "number (int or null, from a leading #N if visible), statement_latex (string). "
    "Set is_problem true ONLY if the image contains a complete self-contained "
    "mathematical problem/conjecture/question. statement_latex must be the "
    "statement transcribed verbatim as LaTeX (inline $...$, display \\[...\\]); "
    "do NOT include the OPEN/SOLVED tag, the prize, the [Ref] citations, the "
    "category line, or any page header/footer. If not a problem, is_problem=false "
    "and statement_latex=\"\"."
)

def ask_vision(png_bytes, model):
    import anthropic
    client = ask_vision._c if hasattr(ask_vision, "_c") else anthropic.Anthropic()
    ask_vision._c = client
    b64 = base64.standard_b64encode(png_bytes).decode()
    r = client.messages.create(
        model=model, max_tokens=1200,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64",
             "media_type": "image/png", "data": b64}},
            {"type": "text", "text": PROMPT}]}])
    txt = "".join(b.text for b in r.content if b.type == "text").strip()
    txt = re.sub(r"^```\w*|```$", "", txt).strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return {"is_problem": True, "status": None, "number": None,
                "statement_latex": txt}


# --------------------------------------------------------------------------
# image helpers
# --------------------------------------------------------------------------
def crop_of(img, b):
    ins = int(0.012 * img.shape[1])
    x0, x1 = b["x0"] + ins, b["x1"] - ins
    y0 = b["y0"] + ins if b["starts"] else b["y0"]
    y1 = b["y1"] - ins if b["ends"]   else b["y1"]
    return img[y0:y1, x0:x1].copy()

def vstack_pad(crops):
    if len(crops) == 1:
        return crops[0]
    w = max(c.shape[1] for c in crops)
    rows = [cv2.copyMakeBorder(c, 0, 0, 0, w - c.shape[1],
            cv2.BORDER_CONSTANT, value=(255, 255, 255)) for c in crops]
    sep = np.full((12, w, 3), 255, np.uint8)
    out = rows[0]
    for r in rows[1:]:
        out = np.vstack([out, sep, r])
    return out

def png_bytes(img):
    return cv2.imencode(".png", img)[1].tobytes()


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default="final_statements.txt")
    ap.add_argument("--model", default="claude-sonnet-4-6")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--limit", type=int, default=0, help="only first N (dry run)")
    ap.add_argument("--cache", default="vision_cache.jsonl")
    ap.add_argument("--vision", default=None,
                    help="(internal) override vision fn for testing")
    a = ap.parse_args()

    vision = a.vision or (lambda b: ask_vision(b, a.model))

    # ---- pass 1: gather all boxes, then group with the CONSERVATIVE stitcher ----
    doc = fitz.open(a.pdf)
    zoom = a.dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    flat = []                                   # (page, box, crop)
    for pno in range(len(doc)):
        pix = doc[pno].get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if pix.n >= 3 \
              else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        for b in detect_boxes(img):
            flat.append((pno + 1, b, crop_of(img, b)))

    # group: a start-half (starts & !ends) absorbs the IMMEDIATELY following
    # continuation(s) until one with ends=True, capped so a misdetection can't
    # eat the whole document. complete boxes and orphans stand alone.
    groups, i, n, warnings = [], 0, len(flat), []
    while i < n:
        pg, b, cr = flat[i]
        if b["starts"] and b["ends"]:                     # complete
            groups.append([(pg, cr)]); i += 1
        elif b["starts"] and not b["ends"]:               # start of a split
            run, j, prev = [(pg, cr)], i + 1, pg
            while j < n and flat[j][0] <= prev + 1 and not flat[j][1]["starts"] \
                    and len(run) < 3:
                run.append((flat[j][0], flat[j][2])); prev = flat[j][0]
                if flat[j][1]["ends"]:
                    j += 1; break
                j += 1
            if len(run) == 1:
                warnings.append(f"unclosed start on page {pg}")
            groups.append(run); i = j
        else:                                              # orphan continuation
            groups.append([(pg, cr)]); i += 1            # statement usually lives here

    if a.limit:
        groups = groups[:a.limit]

    # ---- pass 2: vision transcribe + filter (cached) ----
    cache = {}
    if os.path.exists(a.cache):
        for line in open(a.cache, encoding="utf-8"):
            try:
                d = json.loads(line); cache[d["h"]] = d["r"]
            except Exception:
                pass
    cf = open(a.cache, "a", encoding="utf-8")

    kept, dropped, results = 0, 0, []
    for gi, run in enumerate(groups, 1):
        crops = [c for _, c in run]
        pages = sorted({p for p, _ in run})
        png = png_bytes(vstack_pad(crops))
        h = hashlib.sha1(png).hexdigest()
        if h in cache:
            res = cache[h]
        else:
            res = vision(png)
            cache[h] = res
            cf.write(json.dumps({"h": h, "r": res}) + "\n"); cf.flush()
        sys.stderr.write(f"\r[{gi}/{len(groups)}] kept={kept} dropped={dropped}")
        if res.get("is_problem"):
            kept += 1
            results.append(dict(number=res.get("number"), pages=pages,
                                status=res.get("status"),
                                latex=(res.get("statement_latex") or "").strip()))
        else:
            dropped += 1
    cf.close(); sys.stderr.write("\n")

    # dedup by number, sort
    seen, final = set(), []
    for r in sorted(results, key=lambda x: (x["number"] is None, x["number"] or 0)):
        key = r["number"] if r["number"] is not None else id(r)
        if key in seen:
            continue
        seen.add(key); final.append(r)

    with open(a.out, "w", encoding="utf-8") as f:
        f.write(f"% {len(final)} problem statements from {a.pdf} (model={a.model})\n\n")
        for i, r in enumerate(final, 1):
            tag = f"#{r['number']}" if r["number"] else f"seq{i}"
            st = f" [{r['status']}]" if r["status"] else ""
            pg = "-".join(map(str, r["pages"]))
            f.write(f"% ===== {tag}{st} (page {pg}) =====\n{r['latex']}\n\n")

    print(f"groups={len(groups)}  kept={kept}  dropped(non-problem)={dropped}  "
          f"final(after dedup)={len(final)}  -> {a.out}")
    splits = sum(1 for g in groups if len({p for p, _ in g}) > 1)
    print(f"split boxes stitched across pages: {splits}")
    if warnings:
        print(f"{len(warnings)} warnings (e.g. {warnings[0]})")


if __name__ == "__main__":
    main()
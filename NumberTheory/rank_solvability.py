#!/usr/bin/env python3
"""
rank_solvability.py  --  triage every statement in final_statements.txt by an
ATTEMPTABILITY index (NOT a solvability prediction -- these are open problems).

The model rates four surface axes (1-5) it can actually judge from the statement;
Python computes the weighted composite locally, so you can re-rank with different
WEIGHTS for free (no re-calling the API -- results are cached).

  accessibility            5 = stated with integers/primes/finite sets only
  computational_handle     5 = code can search small cases / gather real evidence
  counterexample_reachable 5 = a feasible search could find a counterexample
  depth_required           5 = looks incremental   1 = needs one famous-hard idea

Output: solvability_ranked.csv  (sorted best-target-first; open in Excel)

Run:
  pip install anthropic
  $env:ANTHROPIC_API_KEY="sk-ant-..."
  python rank_solvability.py --in final_statements.txt --limit 10   # dry run
  python rank_solvability.py --in final_statements.txt --model claude-haiku-4-5-20251001
"""
import argparse, csv, hashlib, json, os, re, sys

# ---- re-rank for free by editing these (composite is computed in Python) ----
WEIGHTS = {
    "computational_handle":     0.35,
    "counterexample_reachable": 0.30,
    "accessibility":            0.20,
    "depth_required":           0.15,
}
AXES = list(WEIGHTS)

PROMPT = """You are a triage analyst for an automated, AI-plus-code pipeline that will
ATTEMPT open Erdős problems. You are NOT predicting whether a problem can be solved
(they are all famous open problems; that prior is essentially zero). You are rating
how good a TARGET this problem is for an AI+code attempt, using ONLY the statement.

Rate each axis as an integer 1-5. Be discriminating: do NOT cluster scores. Most open
problems should score LOW on the computational axes.

accessibility            -- how elementary the objects are.
  5 = only integers, primes, finite sets, basic sums/divisibility
  3 = standard undergrad combinatorics / number theory / basic analysis
  1 = needs specialized advanced theory even to state precisely
computational_handle     -- can code make REAL progress on small cases?
  5 = directly checkable on small finite cases; experiments give strong evidence
  3 = some experiments possible but cannot settle or strongly inform it
  1 = purely asymptotic/infinitary, no finite computation gives traction
  RULE: if you cannot name a concrete finite computation, this is <= 2.
counterexample_reachable -- only for universal ("is it true that for all ...") claims:
  could a FEASIBLE search plausibly find a counterexample and thus resolve it?
  5 = small search space, counterexamples (if any) likely small and findable
  1 = existence/constant/asymptotic problem where this does not apply, OR search hopeless
depth_required           -- inverse difficulty read.
  5 = looks incremental / amenable to standard techniques
  1 = clearly needs one deep new idea (the reason it is still open)

If the statement looks garbled, truncated, or is not actually a math problem, set ALL
axes to 1 and say so in rationale.

Return ONLY minified JSON, no fences, keys exactly:
{"problem_type":"universal"|"existence"|"asymptotic"|"exact_value"|"decision"|"other",
 "accessibility":int,"computational_handle":int,"counterexample_reachable":int,
 "depth_required":int,"attack_vector":"one concrete first thing to try, or 'needs proof - deprioritize'",
 "rationale":"<= 2 sentences"}

PROBLEM:
"""

def parse_statements(path):
    recs, cur = [], None
    hdr = re.compile(r"^%\s*=+\s*(#?\w+)(?:\s*\[([^\]]+)\])?")
    for line in open(path, encoding="utf-8"):
        m = hdr.match(line)
        if m:
            if cur: recs.append(cur)
            label = m.group(1)
            num = int(re.sub(r"\D", "", label)) if any(c.isdigit() for c in label) else None
            cur = {"label": label, "number": num, "status": m.group(2), "latex": []}
        elif cur is not None:
            s = line.rstrip("\n")
            if s.strip() and not s.startswith("% "):
                cur["latex"].append(s.strip())
    if cur: recs.append(cur)
    for r in recs:
        r["latex"] = " ".join(r["latex"]).strip()
    return [r for r in recs if r["latex"]]

def score_one(latex, model):
    import anthropic
    client = score_one._c if hasattr(score_one, "_c") else anthropic.Anthropic()
    score_one._c = client
    r = client.messages.create(model=model, max_tokens=600,
        messages=[{"role": "user", "content": PROMPT + latex}])
    txt = "".join(b.text for b in r.content if b.type == "text").strip()
    txt = re.sub(r"^```\w*|```$", "", txt).strip()
    return json.loads(txt)

def composite(s):
    try:
        return round(sum(WEIGHTS[a] * int(s[a]) for a in AXES) / 5 * 100, 1)
    except (KeyError, ValueError, TypeError):
        return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="final_statements.txt")
    ap.add_argument("--out", default="solvability_ranked.csv")
    ap.add_argument("--model", default="claude-sonnet-4-6")
    ap.add_argument("--cache", default="score_cache.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--score", default=None, help="(internal) test hook")
    a = ap.parse_args()
    scorer = a.score or (lambda latex: score_one(latex, a.model))

    recs = parse_statements(a.inp)
    if a.limit: recs = recs[:a.limit]

    cache = {}
    if os.path.exists(a.cache):
        for line in open(a.cache, encoding="utf-8"):
            try: d = json.loads(line); cache[d["h"]] = d["r"]
            except Exception: pass
    cf = open(a.cache, "a", encoding="utf-8")

    rows = []
    for i, r in enumerate(recs, 1):
        h = hashlib.sha1(r["latex"].encode("utf-8")).hexdigest()
        if h in cache:
            s = cache[h]
        else:
            try:
                s = scorer(r["latex"])
            except Exception as e:
                s = {"problem_type": "other", "attack_vector": "", "rationale": f"score error: {e}"}
            cache[h] = s
            cf.write(json.dumps({"h": h, "r": s}) + "\n"); cf.flush()
        row = {"number": r["number"], "label": r["label"], "status": r["status"] or "",
               "composite": composite(s), "problem_type": s.get("problem_type", ""),
               **{a_: s.get(a_, "") for a_ in AXES},
               "attack_vector": s.get("attack_vector", ""),
               "rationale": s.get("rationale", ""), "statement": r["latex"]}
        rows.append(row)
        sys.stderr.write(f"\r[{i}/{len(recs)}] scored")
    cf.close(); sys.stderr.write("\n")

    rows.sort(key=lambda x: x["composite"], reverse=True)
    cols = ["number", "label", "status", "composite", *AXES, "problem_type",
            "attack_vector", "rationale", "statement"]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

    print(f"scored {len(rows)} problems -> {a.out}  (weights={WEIGHTS})")
    print("\ntop 10 targets:")
    for r in rows[:10]:
        print(f"  {r['composite']:5.1f}  {r['label']:>5}  {r['attack_vector'][:60]}")

if __name__ == "__main__":
    main()
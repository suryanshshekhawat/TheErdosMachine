#!/usr/bin/env python3
"""
attempt_problems.py  --  for each top-ranked problem, run an iterative
"propose code -> execute -> observe -> refine" loop, then write a short LaTeX
report.  Promising results are escalated to the strongest model, whose job is
to ATTACK the claim (find the bug) before anything is reported as real.

  numbers come from top_ten_targets.txt; full statements from solvability_ranked.csv

SAFETY: this runs LLM-written Python on your machine. The static blocklist +
isolated subprocess + timeout are guardrails, NOT a sandbox. Prefer a VM/WSL.
Use --dry-run first to inspect generated code before it executes.

Run:
  pip install anthropic numpy sympy
  $env:ANTHROPIC_API_KEY="sk-ant-..."
  python attempt_problems.py --dry-run                 # write code, don't run it
  python attempt_problems.py                            # run the loop
  python attempt_problems.py --rounds 5 --timeout 90
"""
import argparse, csv, json, os, re, subprocess, sys, time

# --- guardrail: refuse to execute code that touches the system / net / disk ---
BLOCK = re.compile(
    r"\bos\s*\.\s*(system|popen|remove|removedirs|rmdir|unlink|rename|environ|exec|spawn)"
    r"|\bsubprocess\b|\bshutil\b|\bsocket\b|\brequests\b|\burllib\b|\bhttp\b"
    r"|\bsmtplib\b|\bctypes\b|\bpickle\s*\.\s*load|\bmarshal\b"
    r"|__import__|\beval\s*\(|\bexec\s*\(|\bopen\s*\([^)]*['\"][\s]*[waxr]\+?b?['\"]"
    r"|\bPath\s*\([^)]*\)\s*\.\s*(write|unlink|rmdir|mkdir)", re.I)

EXPLORE_RULES = (
    "You are exploring an OPEN Erdős problem with a small Python sandbox: standard "
    "library + numpy + sympy ONLY. No network, no file I/O, no os/subprocess/system "
    "access. Respond EACH turn in exactly this format:\n"
    "1. ONE fenced Python block ```python ... ``` with a COMPLETE self-contained "
    "program that PRINTS its findings (omit the block entirely if no code this turn).\n"
    "2. Then a final line: a minified JSON object with keys exactly "
    "{\"plan\":str,\"done\":bool,\"promising\":bool,\"note\":str}. Do NOT put code in "
    "the JSON.\n"
    "Keep each program's runtime well under the per-run timeout (search modest ranges "
    "first). Goal: concrete computational evidence -- counterexample search, small-case "
    "verification, pattern-finding. Do NOT claim to prove or solve the problem. If a run "
    "looks like a counterexample, set promising=true and INDEPENDENTLY re-verify it next "
    "round before concluding. Set done=true when more computation won't help."
)

REPORT_RULES = (
    "Write a SHORT LaTeX report section, body only: begin with \\section{{Erdős #{n}}} "
    "and use amsmath; NO preamble/document tags. Cover, briefly: the problem in one "
    "line; what was attempted; what the computation actually showed; what went wrong "
    "or was inconclusive. Be skeptical and precise -- 'no counterexample up to N, "
    "consistent with the conjecture' is the expected honest outcome and is NOT progress "
    "on the open problem. End with one line: \\textbf{{Verdict:}} ... . Return ONLY LaTeX."
)
VERIFY_PREFIX = (
    "You are the senior reviewer using the strongest model. A cheaper model flagged a "
    "possibly-promising result. Your PRIMARY job is to ATTACK it: look for off-by-one, "
    "integer overflow, a misread definition, or a search that didn't test what it "
    "claimed. If a counterexample is claimed, re-derive by hand whether it truly "
    "violates the statement. Assume a bug until proven otherwise. Then: "
)


def parse_targets(path):
    nums = []
    for line in open(path, encoding="utf-8"):
        m = re.search(r"#(\d+)", line)
        if m:
            nums.append(int(m.group(1)))
    return nums

def load_csv(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rows[int(re.sub(r"\D", "", r.get("label") or r.get("number") or ""))] = r
            except ValueError:
                pass
    return rows

def extract_code(text):
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    return m.group(1).strip() if m else ""

def extract_flags(text):
    tail = text.rsplit("```", 1)[-1] if "```" in text else text   # after the code
    for c in reversed(re.findall(r"\{[^{}]*\}", tail, re.S)):
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            pass
    low = text.lower()                                            # keyword fallback
    return {"plan": "", "note": "(flags unparsed)",
            "done": '"done": true' in low or '"done":true' in low,
            "promising": '"promising": true' in low or '"promising":true' in low}

def call(client, model, messages, max_tokens=1500):
    r = client.messages.create(model=model, max_tokens=max_tokens, messages=messages)
    return "".join(b.text for b in r.content if b.type == "text")

def run_code(code, workdir, timeout):
    if len(code) > 20000:
        return False, "BLOCKED: code too long"
    hit = BLOCK.search(code)
    if hit:
        return False, f"BLOCKED disallowed construct: {hit.group(0)!r}"
    os.makedirs(workdir, exist_ok=True)
    p = os.path.abspath(os.path.join(workdir, "snippet.py"))
    open(p, "w", encoding="utf-8").write(code)
    try:
        r = subprocess.run([sys.executable, "-I", p], cwd=workdir,
                           capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr else "")
        return True, out.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"
    except Exception as e:
        return False, f"RUN ERROR: {e}"


def attempt(client, rec, num, models, rounds, workdir, timeout, execute):
    explore_model, verify_model = models
    os.makedirs(workdir, exist_ok=True)
    latex = rec.get("statement", "")
    attack = rec.get("attack_vector", "")
    msgs = [{"role": "user", "content":
             f"{EXPLORE_RULES}\n\nOpen Erdős problem #{num}.\nStatement: {latex}\n"
             f"Suggested first angle: {attack}\nReturn the first JSON turn."}]
    transcript, promising = [], False
    for k in range(1, rounds + 1):
        try:
            reply = call(client, explore_model, msgs, max_tokens=4000)
        except Exception as e:
            transcript.append({"round": k, "error": f"model error: {e}"}); break
        msgs.append({"role": "assistant", "content": reply})
        code = extract_code(reply)
        j = extract_flags(reply)
        promising = promising or bool(j.get("promising"))
        rec_round = {"round": k, "plan": j.get("plan", ""), "code": code,
                     "note": j.get("note", ""), "promising": bool(j.get("promising"))}
        if code:
            open(os.path.join(workdir, f"round{k}.py"), "w", encoding="utf-8").write(code)
        if not execute:
            rec_round["output"] = "(dry-run: not executed)"
            transcript.append(rec_round)
            if j.get("done"):
                break
            msgs.append({"role": "user", "content": "Dry run; assume it ran. "
                         "Refine or set done=true. Return JSON."})
            continue
        if code:
            ok, out = run_code(code, workdir, timeout)
            out = out[:4000]
            rec_round["output"] = out
            open(os.path.join(workdir, f"round{k}.out"), "w", encoding="utf-8").write(out)
        else:
            ok, out = True, "(no code this turn)"
            rec_round["output"] = out
        transcript.append(rec_round)
        if j.get("done"):
            break
        msgs.append({"role": "user", "content":
                     f"RUN OUTPUT (truncated):\n{out}\n\nIf this looks like a "
                     "counterexample, re-verify it carefully next turn. Otherwise "
                     "refine or set done=true. Return JSON."})

    # --- report (strong model + attack instructions if promising) ---
    rules = REPORT_RULES.format(n=num)
    convo = "\n\n".join(
        f"-- round {t['round']} --\nplan: {t.get('plan','')}\ncode:\n{t.get('code','')[:1500]}"
        f"\noutput:\n{t.get('output','')[:1500]}" for t in transcript)
    model = verify_model if promising else explore_model
    prompt = (VERIFY_PREFIX if promising else "") + rules + \
             f"\n\nProblem #{num} statement: {latex}\n\nAttempt transcript:\n{convo}"
    try:
        tex = call(client, model, [{"role": "user", "content": prompt}], max_tokens=1800)
    except Exception as e:
        tex = f"\\section{{Erdős #{num}}}\nReport generation failed: {e}"
    tex = re.sub(r"^```\w*|```$", "", tex.strip()).strip()
    return promising, model, transcript, tex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default="top_ten_targets.txt")
    ap.add_argument("--csv", default="solvability_ranked.csv")
    ap.add_argument("--out", default="report.tex")
    ap.add_argument("--workroot", default="attempts")
    ap.add_argument("--explore-model", default="claude-sonnet-4-6")
    ap.add_argument("--verify-model", default="claude-opus-4-8")   # strongest
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true", help="write code, do NOT execute")
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()

    import anthropic
    client = anthropic.Anthropic()
    nums = parse_targets(a.targets)
    recs = load_csv(a.csv)
    sections, summary = [], []

    for num in nums:
        rec = recs.get(num)
        if not rec:
            print(f"#{num}: not found in {a.csv}, skipping"); continue
        wd = os.path.join(a.workroot, str(num))
        done_flag = os.path.join(wd, "section.tex")
        if os.path.exists(done_flag) and not a.redo:
            sections.append(open(done_flag, encoding="utf-8").read())
            print(f"#{num}: cached"); continue
        os.makedirs(wd, exist_ok=True)
        print(f"#{num}: attempting ({'dry-run' if a.dry_run else 'executing'}) ...")
        promising, model, transcript, tex = attempt(
            client, rec, num, (a.explore_model, a.verify_model),
            a.rounds, wd, a.timeout, execute=not a.dry_run)
        json.dump(transcript, open(os.path.join(wd, "transcript.json"), "w"), indent=2)
        open(done_flag, "w", encoding="utf-8").write(tex)
        sections.append(tex)
        summary.append((num, promising, model))
        print(f"   -> {'PROMISING (escalated to '+model+')' if promising else 'done'}")

    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\\documentclass[11pt]{article}\n"
                "\\usepackage{amsmath,amssymb,amsthm}\n"
                "\\usepackage[margin=1in]{geometry}\n\\usepackage{hyperref}\n"
                "\\title{Erdős Problems: Computational Attempt Log}\\author{}\\date{\\today}\n"
                "\\begin{document}\\maketitle\n\n")
        f.write("\n\n\\clearpage\n\n".join(sections))
        f.write("\n\n\\end{document}\n")

    print(f"\nreport -> {a.out}   (compile with pdflatex; artifacts in {a.workroot}/)")
    if summary:
        flagged = [n for n, p, _ in summary if p]
        print("promising (verify by hand!):", flagged or "none")


if __name__ == "__main__":
    main()
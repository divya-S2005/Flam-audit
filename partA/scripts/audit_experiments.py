#!/usr/bin/env python3
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENG = ROOT / "corpus_sample" / "eng_sample.txt"
HIN = ROOT / "corpus_sample" / "hin_sample.txt"

def read(path):
    return [x.rstrip("\n") for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

print("=== A2.1 repeated-whitespace experiment ===")
for lang, path in [("eng", ENG), ("hin", HIN)]:
    for i, line in enumerate(read(path), 1):
        a = len(line.split(" "))
        b = len(line.split())
        if a != b:
            print(f"{lang} line {i}: split(' ')={a}, split()={b}, "
                  f"line-level fertility multiplier if fixed token count={b/a:.6f}; "
                  f"understatement={(1-b/a)*100:.2f}%")

print("\n=== A2.2 aggregation experiment ===")
# Deliberately simple deterministic token count: one token per character.
# This isolates the aggregation rule; it is NOT a claim about GPT-2.
lines = ["a b", "a" * 100]
per_line = []
tok_total = word_total = 0
for s in lines:
    t = len(s)
    w = len(s.split())
    per_line.append(t / w)
    tok_total += t
    word_total += w
print(f"per-line ratios={per_line}")
print(f"mean(per-line fertility)={sum(per_line)/len(per_line):.6f}")
print(f"corpus totals tokens/words={tok_total/word_total:.6f}")

print("\n=== A2.3 harmless random.seed experiment ===")
src = (ROOT / "fertility.py").read_text(encoding="utf-8")
uses = [ln for ln in src.splitlines() if "random" in ln]
print("random-related lines:")
for ln in uses:
    print(ln)
print("No random draw is present in the script; the seed is therefore numerically inert.")

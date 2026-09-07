#!/usr/bin/env python3
import argparse, json, re, unicodedata
from pathlib import Path
import pandas as pd

def load_tok(spec):
    if spec.startswith("hf:"):
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(spec[3:])
        return lambda s: tok.encode(s, add_special_tokens=False)
    import tiktoken
    enc = tiktoken.get_encoding(spec)
    return enc.encode

def graphemes(s):
    # regex \X approximates Unicode extended grapheme clusters.
    import regex
    return regex.findall(r"\X", s)

ap = argparse.ArgumentParser()
ap.add_argument("--corpus", required=True)
ap.add_argument("--tokenizers", nargs="+", required=True)
ap.add_argument("--out", default="partA/results/corrected_tokenizer_metrics.csv")
args = ap.parse_args()

df = pd.read_csv(args.corpus)
id_col = df.columns[0]
langs = list(df.columns[1:])

rows = []
for spec in args.tokenizers:
    encode = load_tok(spec)
    for lang in langs:
        total_tok = total_words = total_graph = total_bytes = total_sent = 0
        per_line = []
        for text in df[lang].fillna("").astype(str):
            text = unicodedata.normalize("NFC", text)
            ids = encode(text)
            words = text.split()
            gc = graphemes(text)
            b = len(text.encode("utf-8"))
            total_tok += len(ids)
            total_words += len(words)
            total_graph += len(gc)
            total_bytes += b
            total_sent += 1
            per_line.append(len(ids) / max(len(words), 1))
        rows.append({
            "tokenizer": spec,
            "language": lang,
            "sentences": total_sent,
            "tokens_per_sentence": total_tok / total_sent,
            "tokens_per_whitespace_word": total_tok / total_words,
            "tokens_per_grapheme": total_tok / total_graph,
            "tokens_per_utf8_byte": total_tok / total_bytes,
            "mean_per_sentence_tok_per_word": sum(per_line) / len(per_line),
        })

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(out, index=False)
print(pd.DataFrame(rows).to_string(index=False))
print(f"Wrote {out}")

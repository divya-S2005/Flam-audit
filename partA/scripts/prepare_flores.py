#!/usr/bin/env python3

import argparse
from pathlib import Path
import pandas as pd
from datasets import load_dataset

ap = argparse.ArgumentParser()
ap.add_argument("--languages", nargs="+", required=True)
ap.add_argument("--split", default="devtest")
ap.add_argument("--n", type=int, default=200)
ap.add_argument("--out", default="partA/corpus/flores_selected.csv")
args = ap.parse_args()

rows = {}

for lang in args.languages:
    print(f"Loading {lang}...")

    ds = load_dataset(
        "facebook/flores",
        lang,
        split=args.split
    )

    ds = ds.select(range(min(args.n, len(ds))))

    if "id" not in ds.column_names:
        raise RuntimeError(
            f"No id column found for {lang}. "
            f"Columns: {ds.column_names}"
        )

    if "sentence" not in ds.column_names:
        raise RuntimeError(
            f"No sentence column found for {lang}. "
            f"Columns: {ds.column_names}"
        )

    for row in ds:
        rows.setdefault(row["id"], {})[lang] = row["sentence"]

df = pd.DataFrame.from_dict(rows, orient="index")
df.index.name = "id"
df = df.reset_index()

df = df.dropna()

out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(out_path, index=False)

print(f"Wrote {len(df)} aligned sentences to {out_path}")
print(f"Saved to: {out_path}")
print(df.head())
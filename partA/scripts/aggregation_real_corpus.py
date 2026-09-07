from pathlib import Path
import tiktoken

ROOT = Path(__file__).resolve().parents[2]

enc = tiktoken.get_encoding("gpt2")

for lang in ["eng", "hin"]:
    path = ROOT / "corpus_sample" / f"{lang}_sample.txt"

    lines = [
        line.rstrip("\n")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    per_line = []
    total_tokens = 0
    total_words = 0

    for line in lines:
        tokens = enc.encode(line)

        # Match the original fertility.py denominator
        words = line.split(" ")

        per_line.append(len(tokens) / len(words))
        total_tokens += len(tokens)
        total_words += len(words)

    mean_per_line = sum(per_line) / len(per_line)
    corpus_ratio = total_tokens / total_words

    print(f"\n{lang}")
    print("-" * 40)
    print(f"Mean per-line fertility : {mean_per_line:.6f}")
    print(f"Corpus tokens / words   : {corpus_ratio:.6f}")
    print(f"Difference              : {mean_per_line - corpus_ratio:.6f}")
    print(
        f"Relative difference     : "
        f"{(mean_per_line - corpus_ratio) / corpus_ratio * 100:.2f}%"
    )
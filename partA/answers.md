# Part A — Tokenizer Audit

## A1 — Real multilingual evaluation corpus

**Corpus:** FLORES-200 `devtest`, using 200 aligned sentence IDs shared across:
- English (`eng_Latn`)
- Hindi (`hin_Deva`)
- Kannada (`kan_Knda`)
- Tamil (`tam_Taml`)

**Domain:** FLORES-200 is a multilingual machine-translation evaluation corpus containing written material drawn from sources such as news, travel and informational text. It is appropriate for a controlled cross-language tokenizer comparison because the same sentence IDs provide parallel content.

**Size:** 200 aligned sentences × 4 languages = 800 sentence instances. The checked-in `flores_selected.csv` contains the exact material used by the corrected analysis.

**Preprocessing:** UTF-8 decoding; NFC Unicode normalization before tokenization; no lowercasing for A3; whitespace-word denominator uses Unicode whitespace splitting; grapheme denominator uses Unicode extended grapheme clusters; UTF-8 byte denominator uses the encoded byte length. Sentence alignment is preserved by ID.

**What this corpus cannot tell us:** This is a controlled benchmark, not a production traffic sample. Two hundred aligned sentences are too small to establish the full distribution of prompt lengths, punctuation, code-switching, names, emojis, tables, URLs, or domain-specific terminology seen in an assistant. Parallel translations also do not guarantee identical surface-form length or identical production semantics. Therefore the corpus can compare tokenization efficiency under controlled content, but it cannot by itself predict end-to-end production cost per user request.

## A2 — Audit of `fertility.py`

### A2.1 Real code bug: `split(" ")` treats repeated spaces as words

The original code uses:

```python
words = line.split(" ")
```

Python's explicit-separator split creates empty fields for repeated spaces. The supplied sample contains two affected lines:

| line | `split(" ")` | `split()` | denominator change | line-level fertility understatement if token count is fixed |
|---|---:|---:|---:|---:|
| English 7 | 8 | 7 | +1 empty field | 12.50% |
| Hindi 10 | 6 | 5 | +1 empty field | 16.67% |

**Minimal experiment:**

```bash
python partA/scripts/audit_experiments.py
```

The script prints the affected lines and the exact denominator multiplier. Because the numerator is unchanged, adding an empty field can only reduce the reported tokens/word for that line. The fix is `line.split()`.

### A2.2 Conceptual problem: mean of line ratios is not corpus-level fertility

The script computes `mean(tokens_i / words_i)`, which gives every sentence equal weight. For a cost/routing estimate, that is not generally the same as the aggregate token burden `sum(tokens_i) / sum(words_i)`; longer and shorter requests should not receive identical weight unless that is explicitly the desired estimand.

**Minimal isolation experiment:** `audit_experiments.py` uses a deterministic one-token-per-character toy encoder solely to isolate the arithmetic. For two lines with ratios 1.5 and 100:

- mean of per-line ratios = **50.75**
- total tokens / total words = **34.33**
- difference = **16.42**, or **47.8% above** the aggregate ratio.

This is an arithmetic demonstration of the weighting distortion, not a claim about GPT-2. The corrected A3 analysis therefore reports aggregate denominators as well as the unweighted per-sentence statistic.

### A2.3 Suspicious but harmless: `random.seed(1337)`

The seed looks suspicious because the script does not otherwise use `random`. It is nevertheless numerically inert: there is no random draw anywhere in `fertility.py`.

**Minimal experiment:**

```bash
grep -nE '\brandom\b|random\.' fertility.py
python partA/scripts/audit_experiments.py
```

The only random-related statements are the import and seed call. Removing the seed cannot alter the current deterministic computation. It is unnecessary, but it is **not a numerical bug**.

## A3 — Corrected cross-language analysis

Two tokenizers are evaluated:

1. **GPT-2 BPE** (`gpt2`) — the legacy baseline used by the intern.
2. **XLM-R base** (`FacebookAI/xlm-roberta-base`) — a multilingual tokenizer with broad Indic-language coverage.

The checked-in `partA/results/corrected_tokenizer_metrics.csv` reports these denominators:

- tokens / aligned sentence
- tokens / whitespace word
- tokens / grapheme cluster
- tokens / UTF-8 byte
- mean of per-sentence tokens/word

### Corrected headline

For routing and cost, the single headline number should be **tokens per aligned sentence** for this controlled parallel experiment. The sentence ID holds the intended semantic content approximately constant across languages; a raw whitespace-word denominator does not, because languages differ in word segmentation conventions. UTF-8 bytes and grapheme clusters answer useful normalization questions but are not the production billing unit.

Measured tokens/sentence:

| tokenizer | English | Hindi | Kannada | Tamil |
|---|---:|---:|---:|---:|
| GPT-2 | 27.23 | 202.33 | 372.10 | 426.24 |
| XLM-R | 31.05 | 38.99 | 42.05 | 42.59 |

This shows why the tokenizer matters: GPT-2's Indic token counts are dramatically higher than its English count, while XLM-R compresses the cross-language gap substantially. The appropriate routing decision is therefore **not** “Indic traffic costs 6× because Hindi has more characters”; it is to benchmark the actual tokenizer/model stack on representative production requests and route only when the measured total cost/latency benefit justifies it.

The A3 result is a controlled tokenizer comparison, not a claim that all production requests have these exact ratios.

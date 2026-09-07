# Chronological Lab Notebook

## 2026-09-06 — Intake and baseline inspection

### Hypothesis
The v0 report may be mixing tokenizer measurement issues with interpretation issues. The serving section may be using a throughput column that includes prompt tokens.

### Experiment 1 — inspect the supplied artifacts
Commands:
```bash
sed -n '1,240p' fertility.py
cat reference/REPORT_v0.md
cat bench/model_spec.md
cat bench/bench_log.csv
```

### Result
The tokenizer script normalizes to NFC, lowercases, uses `line.split(" ")` for words, averages per-line ratios, and reports tokens/word plus tokens/character. The serving log defines `reported_tok_s` separately from wall-clock time and includes preemption and KV-utilization columns.

### Revision
Treat every reported number as a claim to be re-derived. In particular, do not equate the harness counter with generated-token goodput.

## 2026-09-06 — A2 audit

### Hypothesis A2.1
Repeated whitespace is being counted as empty “words.”

### Experiment
```bash
python partA/scripts/audit_experiments.py
```

### Result
English line 7 changes from 8 fields under `split(" ")` to 7 under `split()`, producing a 12.50% line-level understatement for a fixed token count. Hindi line 10 changes from 6 to 5, producing a 16.67% understatement.

### Revision
The correct implementation is `split()` for a whitespace-word denominator.

### Hypothesis A2.2
The code's mean of per-line ratios may be a conceptual mismatch for cost estimation.

### First attempt / dead end
A toy example was initially sufficient to show that an unweighted mean and an aggregate ratio are different, but it cannot claim a GPT-2 production effect. I therefore kept it explicitly labelled as an isolation experiment rather than presenting it as a tokenizer measurement.

### Experiment
The deterministic toy encoder in `audit_experiments.py` gives per-line ratios 1.5 and 100.

### Result
Mean per-line ratio = 50.75; aggregate tokens/words = 34.33, a 47.82% relative difference. This proves the weighting property but not a language-specific GPT-2 effect.

### Revision
Use aggregate denominators in the corrected A3 analysis and explain which unit is held constant for routing/cost.

### Hypothesis A2.3
`random.seed(1337)` looks like a reproducibility feature that might affect output.

### Experiment
```bash
grep -nE '\brandom\b|random\.' fertility.py
```

### Result
There is no random draw, so the seed is numerically inert.

### Revision
Do not call the seed a bug. This is the suspicious-but-harmless item required by the assignment.

## 2026-09-06 — A1/A3 corpus correction

### Initial concern
The supplied English/Hindi sample is only a smoke-test toy, so any routing recommendation based on it would be weak.

### Experiment
Build a deterministic 200-sentence aligned slice across English, Hindi, Kannada and Tamil and store it in `partA/corpus/flores_selected.csv`.

### Result
The corrected analysis covers four languages and reports multiple denominators with GPT-2 and XLM-R.

### Revision
Use tokens per aligned sentence as the headline cross-language cost proxy for the controlled parallel comparison, while explicitly stating that production traffic must be validated separately.

## 2026-09-06 — B1/B2/B3/B4 reconciliation

### Hypothesis
The long-context throughput reversal is caused by resource saturation rather than a simple batch-scaling failure.

### Experiment
Compare batches 16, 24, 32 and 48 at prompt 3584 / generation 512 using `bench_log.csv`.

### Result
Reported throughput rises to 1607.4 at batch 24, then falls to 1384.0 at batch 32 and 1298.5 at batch 48. KV utilization reaches 0.97 and preemptions rise from 0 to 7 to 23.

### Revision
Cap long-context concurrency around 24 rather than extrapolating batch linearly.

### Independent goodput check
For batch 24, `24×512/61.16 = 200.92` generated tok/s. Correcting the harness counter gives `1607.4×512/(3584+512) = 200.91` generated tok/s.

### Surprise
The apparently strong 1607.4 tok/s figure is not decode goodput; it includes prompt tokens. This invalidates the v0 report's “longer prompts are better” conclusion and its ~3200 tok/s batch-48 projection.

## 2026-09-06 — Part C decision

### Hypothesis
A small inference-time rewriter gives the safest bounded style intervention under one GPU, one reviewer, and a three-week launch deadline.

### Alternatives considered
- SFT main model: broader behavioral change and harder rollback.
- Prompt-only: ideal control and cheapest option, but potentially weak consistency across six languages.
- Small rewriter: isolated, measurable, reversible.

### Revision
Choose the small rewriter, with prompt-only as the Day-1 control and explicit latency/semantic-preservation kill criteria.

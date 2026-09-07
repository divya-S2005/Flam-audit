# The Audit — Submission

This repository audits the supplied tokenizer/serving report and contains the evidence, corrected analysis, calculations, and decision memo requested in the assignment.

## Submission map

- `NOTEBOOK.md` — chronological hypothesis → experiment → result → revision log, including dead ends.
- `AI_USAGE.md` — honest disclosure of AI assistance and verification boundaries.
- `partA/` — corpus construction, audit findings (`answers.md`), corrected tokenizer analysis, and A4 recommendation memo (`memo.md`).
- `partB/` — B1–B4 calculations and written answers (`answers.md`).
- `partC/memo.md` — decision memo.
- `reference/REPORT_v0.md` — the original report being audited; retained as reference only.

## Reproduction

```bash
pip install -r requirements.txt

python fertility.py --corpus eng=corpus_sample/eng_sample.txt --corpus hin=corpus_sample/hin_sample.txt --tokenizer gpt2
python partA/scripts/audit_experiments.py
python partA/scripts/prepare_flores.py --languages eng_Latn hin_Deva kan_Knda tam_Taml --split devtest --n 200
python partA/scripts/corrected_analysis.py --corpus partA/corpus/flores_selected.csv --tokenizers gpt2 hf:FacebookAI/xlm-roberta-base
```

The checked-in CSVs under `partA/results/` and `partB/` record the measurements used in the memos; the scripts are the source of truth for rerunning them.

## Important interpretation

The old report's `reported_tok_s` is a harness counter that includes prompt and generated tokens. It is not decode goodput. Part B derives the honest generated-token goodput independently from wall-clock time and from the counter definition.

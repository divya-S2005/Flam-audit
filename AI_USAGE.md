# AI_USAGE.md

AI was used as a reasoning and coding assistant for repository organization, arithmetic checks, experiment-script drafting, and memo structure.

AI-generated hypotheses were treated as hypotheses, not evidence. In particular, a suspicious-looking line was not classified as a bug until an experiment was designed to isolate its effect. The final A2 conclusions are tied to the checked-in audit script and output; the A3 measurements are tied to the checked-in corrected-analysis CSV and reproducible script.

Human verification responsibilities before and during the defense:
- rerun the supplied commands in the target environment;
- verify tokenizer/model versions and dataset provenance;
- explain the denominator choice and every arithmetic step;
- modify the code live if asked;
- distinguish measured results from illustrative isolation experiments.

AI could mislead this audit by confidently treating `random.seed(1337)` as a bug or by interpreting `reported_tok_s` as generated-token throughput. Those interpretations were rejected because the code/log definitions and independent calculations do not support them.

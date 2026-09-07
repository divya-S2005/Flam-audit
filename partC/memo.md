# Part C — Decision Memo

**Recommendation: (b) a small (≤1B) inference-time rewriter, with prompt-only as the Day-1 control.**

### Assumptions
- Use an open 0.5–1B multilingual instruction model that can run locally on the available A100-80GB.
- Create **36,000 synthetic pairs**: 6,000 per language × 6 languages.
- Average source+target length: ~150 tokens/pair.
- Train for 3 epochs; use the A100 only for local training/evaluation.
- The reviewer is available 10 h/week and can judge ~40 examples/hour at ~1.5 min/example.

### Back-of-envelope arithmetic
**Data volume:** `36,000 × 150 = 5.4M tokens/epoch`; three epochs = **16.2M training tokens**.

**Training compute:** using the standard dense-transformer approximation `~6 × parameters × training tokens`, a 1B model is `6 × 1B × 16.2M ≈ 9.7×10^16 FLOPs`. Even allowing substantial real-world inefficiency, this is comfortably inside the two-week single-A100 window; budget **2–6 GPU-hours** for fine-tuning plus evaluation/iteration rather than assuming peak FLOPs.

**Reviewer throughput:** `10 h/week × 40 examples/hour = ~400 judgments/week`; over 3 weeks the theoretical capacity is ~1,200 judgments. Reserve ~600 for the launch evaluation and ~600 for calibration/regression checks. Reviewer time is therefore a constraint, but sufficient for targeted human evaluation rather than full synthetic-data labeling.

**Serving cost assumption:** if the rewriter processes one output after the main model and averages 300 tokens/request, at an assumed sustained 20 requests/s on the A100, that is ~6,000 rewriter tokens/s. The exact throughput must be measured on the selected model on Day 1; if the measured rewriter adds >20% end-to-end latency, it fails the launch trade-off regardless of style score.

### Success metric
On a blinded **600-example** evaluation (100/language), require **≥80% casual/natural**, **≥95% semantic preservation**, and no language below **70% casualness**. Also require rewriter latency overhead ≤20%.

### Kill criterion
By the end of **week 1**, abandon the rewriter and ship the prompt-only control if one trained iteration cannot reach **≥65% casualness** while maintaining **≥95% semantic preservation**, or if measured latency overhead exceeds 20%. Do not spend week 2 polishing a transformation that is not moving both style and preservation metrics.

### Day-1 experiment
Create a 120-example pilot: 20 prompts × 6 languages. Compare **(1) base**, **(2) prompt-only**, and **(3) small rewriter**. Have the reviewer score all Hindi and Kannada examples for casualness and meaning preservation, and measure latency for all six languages. If prompt-only already reaches ≥75% casualness with ≥95% preservation and ≤20% overhead, keep it as the launch baseline; otherwise begin rewriter fine-tuning immediately.

### Why not SFT the main model?
It couples a style intervention to general model behavior and makes rollback harder. Under a three-week launch constraint and one reviewer, the isolated rewriter gives a bounded intervention with a clean kill switch.

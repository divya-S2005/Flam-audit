# Part B — Capacity Reconciliation

## B1 — KV cache arithmetic

From `bench/model_spec.md`:

`KV bytes/token = 2 × layers × KV_heads × head_dim × bytes_per_fp16`

`= 2 × 28 × 8 × 128 × 2 = 114,688 bytes/token = 112 KiB/token`.

A full 4096-token sequence therefore requires:

`114,688 × 4096 = 469,762,048 bytes = 448 MiB`.

The L4 has 24 GiB. With `gpu_memory_utilization = 0.92`, the configured usable budget is:

`24 × 0.92 = 22.08 GiB`.

FP16 weights require approximately:

`4.2B × 2 bytes = 8.4 GB ≈ 7.82 GiB`.

Subtracting the stated ~1.6 GiB non-KV overhead leaves:

`22.08 − 7.82 − 1.6 ≈ 12.66 GiB` for KV.

`12.66 GiB / 448 MiB ≈ 28.9` full sequences, so the simple arithmetic predicts **about 28 simultaneous 4096-token sequences**.

The load log reaches 0.93 KV utilization at batch 24 with zero preemptions, then 0.97 at batches 32 and 48 with preemptions. This is directionally consistent with the simple capacity model; runtime block allocation and scheduler overhead explain why the model should not be treated as an exact admission limit.

## B2 — Long-context throughput anomaly

At prompt length 3584 and generation length 512:

| batch | wall clock (s) | reported tok/s | KV util | preempted sequences |
|---:|---:|---:|---:|---:|
| 16 | 49.97 | 1311.4 | 0.62 | 0 |
| 24 | 61.16 | 1607.4 | 0.93 | 0 |
| 32 | 94.71 | 1384.0 | 0.97 | 7 |
| 48 | 151.41 | 1298.5 | 0.97 | 23 |

The anomaly is the reversal after batch 24: increasing batch from 24 to 32 increases offered concurrency by 33% but **reduces** the harness counter from 1607.4 to 1384.0 tok/s (−223.4 tok/s, −13.9%). At the same point KV utilization is ~0.97 and preemptions rise from 0 to 7, then to 23 at batch 48.

**Mechanism:** the pattern is consistent with KV-cache pressure pushing the scheduler into preemption/recomputation. More concurrent long sequences stop producing useful parallelism and instead create scheduling overhead.

**Deployment change:** cap long-context concurrency at **24 sequences** (or an equivalent `max_num_seqs` policy). The observed batch-24 operating point is 1607.4 reported tok/s with zero preemptions, versus 1384.0 at batch 32. This avoids the measured preemption regime and improves the harness counter by 16.1% relative to batch 32.

## B3 — Correct goodput

The misleading column is **`reported_tok_s`**. The harness counter includes prompt tokens as well as generated tokens.

For batch 24, prompt 3584, generation 512:

**Method 1 — wall clock:**

`24 × 512 / 61.16 = 200.92 generated tok/s`.

**Method 2 — correct the harness counter:**

`1607.4 × 512 / (3584 + 512) = 200.91 generated tok/s`.

The independent derivations agree: honest generated-token goodput is **~200.9 tok/s**.

Therefore the report should **not** say longer prompts provide better generation throughput. Longer prompts increase the prompt+generation token counter, which can make `reported_tok_s` look better without improving decode goodput. The report also should not project batch 48 to ~3200 tok/s: the observed long-context curve turns downward at batch 32 as KV saturation and preemption appear.

## B4 — Confirming counter

Pull the serving scheduler's **KV-cache preemption count/rate** (and, if available, preemption/recompute time). If the mechanism above is correct, the counter should be near zero around batch 24 and rise materially at batch 32 and 48, matching the supplied `preempted_seqs` values of 0, 7 and 23. A corresponding rise in recompute/scheduler time would strengthen the causal explanation.

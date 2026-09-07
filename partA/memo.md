# A4 — Recommendation Memo

**Headline:** The original report should not drive routing or cost decisions. Its 5.89× Hindi claim is based on a tiny two-language smoke test and a denominator that is not held constant across languages. The corrected 200-sentence, four-language analysis shows a much more useful result: with GPT-2, tokens/sentence are 27.23 (English), 202.33 (Hindi), 372.10 (Kannada), and 426.24 (Tamil); with XLM-R they are 31.05, 38.99, 42.05, and 42.59 respectively.

**Routing recommendation:** Do not hard-code a “6× Hindi cost” multiplier. For the controlled parallel test, use aggregate tokens per aligned sentence as the cross-language cost proxy because sentence content is the unit held approximately constant. Validate the same decision on a production-like request sample before changing routing.

**Biggest caveat:** FLORES-200 devtest is written evaluation text, not production assistant traffic, and the 200-sentence slice cannot represent code-switching, long prompts, URLs, names, emojis, or domain-specific workloads.

**Production metric:** Monitor **generated + prompt tokens per request and end-to-end latency by language/model route**. A widening gap between offline token-cost predictions and observed production token usage is the signal that this analysis no longer represents traffic.

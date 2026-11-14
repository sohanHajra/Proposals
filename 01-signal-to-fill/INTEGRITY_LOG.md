# Integrity log

After each work session I check three things and write down what I found, including the embarrassing parts.
1. **Logic.** Does every conclusion follow from what was actually run?
2. **Sources.** Does every citation and number match its source (paper, dataset, or a file in `results/`)?
3. **Bias.** Is anything framed to look better than it is: selection of data, hindsight, a hypothesis written as if it were a finding?

## 2026-11-14
**Found and fixed**
- The literature review said every entry was checked at the publisher page. Not true: Perold (1988) and Almgren & Chriss (2001) were not re-checked, and every paper was checked at abstract level only. Wording corrected.
- The novelty claim said the delay grid starts at 0 ms. The audit showed exchange timestamps are whole milliseconds, so 0 and 1 ms are indistinguishable. Corrected to 1 to 500 ms.
- The README stated "the passive side is where delay should matter most" as a current belief. It is a hypothesis from one measured fact (one-tick spread on 95.5% of updates). Relabelled as untested.
- "Prior art" is a patent term; renamed to literature review.

**Open**
- The closest prior work (Quantitative Finance, 2025) has been read by abstract only. Novelty claim 1 stays provisional until the full text is read.
- Calendar bias: free Tardis days are all first-of-month. Added to Limits; cannot be fixed without paid data.
- LOBSTER sample is one day in June 2012, before several market-structure changes. Results from it describe that day, not today's Nasdaq.

**Checked, no issue**
- Every number in the README and lab notebook traces to `results/audit/tardis_2026-09-01.json`.
- Adopted from a researcher friend's method: every source now records how deeply it was read, sources I have not opened sit in an Unverified list, and absence claims are worded as "not found in this review". Perold (1988) and Almgren & Chriss (2001) moved to Unverified.

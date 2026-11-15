# Integrity log

After each work session I check three things and write down what I found, including the embarrassing parts.
1. **Logic.** Does every conclusion follow from what was actually run?
2. **Sources.** Does every citation and number match its source (paper, dataset, or a file in `results/`)?
3. **Bias.** Is anything framed to look better than it is, such as selection of data, hindsight, a hypothesis written as if it were a finding?

## 2026-11-14
**Found and fixed**
- The literature review said every entry was checked at the publisher page. Not true. Perold (1988) and Almgren & Chriss (2001) were not checked again, and every paper was checked at abstract level only. Wording corrected.
- The novelty claim said the delay grid starts at 0 ms. The audit showed exchange timestamps are whole milliseconds, so 0 and 1 ms are indistinguishable. Corrected to 1 to 500 ms.
- The README stated "the passive side is where delay should matter most" as a current belief. It is a hypothesis from one measured fact (a one tick spread on 95.5% of updates). Relabelled as untested.
- "Prior art" is a patent term; renamed to literature review.

**Open**
- The closest prior work (Quantitative Finance, 2025) has been read by abstract only. Novelty claim 1 stays provisional until the full text is read.
- Calendar bias. Free Tardis days are all the first of a month. Added to Limits; cannot be fixed without paid data.
- LOBSTER sample is one day in June 2012, before several market structure changes. Results from it describe that day, not today's Nasdaq.

**Checked, no issue**
- Every number in the README and lab notebook traces to `results/audit/tardis_2026-09-01.json`.
- Adopted from a researcher friend's method. Every source now records how deeply it was read, sources I have not opened sit in an Unverified list, and absence claims are worded as "not found in this review". Perold (1988) and Almgren & Chriss (2001) moved to Unverified.
- Style pass on all public notes. I write without dashes and keep colons out of prose, so the notes read the way I talk. Hyphens stay only where they belong to someone else's words or to identifiers (paper titles, dates, DOIs, file and folder names). PROPOSAL.md is left exactly as I wrote the original PDF.

## 2026-11-14 (evening)
**Found and fixed**
- The planned passive model relied on one queue rule. After reading Danait et al. (2026) in full, the passive leg now uses three matched cancellation rules and a sign must hold under all three.
**Open**
- Three papers found in their reference list are listed as Unverified, not used as evidence.
- My guess that delay and the cancellation rule interact is labelled as my inference and untested.
**Checked, no issue**
- Every number quoted from the paper (8.01 and 7.39 points, 18.15% and 10.14% completion, 1.010 and 0.384 bps) matches its abstract, Table 2 and Section 7 in v3.

## 2026-11-15
No second reviewer was available for this pass, so I did it myself by rereading every changed file against its source (the two papers, `results/audit/lobster_2012-06-21.json`, `results/audit/tardis_2026-09-01.json`).

**Found and fixed**
- The lab notebook said AAPL, AMZN and GOOG have a one tick spread on 0.5% or less of updates. AMZN is 0.59%. Now reads under 1%.
- The notebook rounded both INTC and MSFT to a quarter of orders living 1.5 ms or less. INTC is 1.29 ms and MSFT 1.528 ms, so both values are now given.
- The literature review called the Albers et al. slippage fits weighted R². Their text gives the R² values but I could not confirm from the text alone that these are the weighted version. The word is removed.
- The first draft of the materiality bar for H1 cited 0.1 to 0.3 bps from Albers et al. Their text gives 0.1, 0.07 and 0.3 bps across three markets, and the number is conditional on a 2 bps markout. Range corrected and the conditioning stated next to the bar.
- The repository description on GitHub promised a pace of new proposals. I don't want to promise one, so it now just says what the repo is.
- H2c compared markouts of fills at 1 ms and 500 ms. Those are different sets of decisions, so the comparison carries selection. Added a second comparison on decisions that fill at both delays.

**Open**
- RQ2 is now restricted to INTC and MSFT. I chose this from the spread audit before computing any fill or markout number, but it is still a choice made after seeing data, and it is written down as such.
- The 0.1 bps bar is a judgement call. It is fixed now so it cannot move after results.
- Tables and figures in Albers et al. did not render and some Yueshen figure pages were images I did not view. Only numbers stated in their text are quoted.
- LOBSTER files only carry messages inside the 10 level window, so lifecycle shares describe orders that stayed in view.

**Checked, no issue**
- Every LOBSTER number in the notebook and README traces to `results/audit/lobster_2012-06-21.json`.
- Albers et al. counts (3,138,814 market orders on Bybit BTC, 40,588 on Binance, about 1.06 million on Bybit ETH, 1.354% failure rate) match Sections 3.2, 3.3.2 and 5.2 of the full text.
- Yueshen is described as a theory paper and its predictions are labelled as model predictions, not measurements.
- The preregistration states what had been seen before it was written. No replay output and no test day data existed.

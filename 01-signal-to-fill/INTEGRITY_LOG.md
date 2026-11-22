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

## 2026-11-14 (evening)
**Found and fixed**
- The planned passive model relied on one queue rule. After reading Danait et al. (2026) in full, the passive leg now uses three matched cancellation rules and a sign must hold under all three.
**Open**
- Three papers found in their reference list are listed as Unverified, not used as evidence.
- My guess that delay and the cancellation rule interact is labelled as my inference and untested.
**Checked, no issue**
- Every number quoted from the paper (8.01 and 7.39 points, 18.15% and 10.14% completion, 1.010 and 0.384 bps) matches its abstract, Table 2 and Section 7 in v3.

## 2026-11-15
This time I did it by rereading every changed file against its source (the two papers, `results/audit/lobster_2012-06-21.json`, `results/audit/tardis_2026-09-01.json`).

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

## 2026-11-15 (afternoon)
**Found and fixed**
- The literature review still said the Albers et al. tables were not viewed. Updated after reading the PDF.

**Open**
- Their supplementary material is unread.

**Checked, no issue**
- Table 7 slopes reproduce the 0.07 to 0.3 bps range used for the H1 bar (slope × 2 bps).
- Table 6 R² is weighted per their text. Table 7 R² is not described, so the review does not call it weighted.
- Self check. I did it in the same short sitting as the work.


## 2026-11-16
I did this check myself.
- **Found and fixed.** The first replay sanity wording implied a reason for the 58% exact print share. Rewritten as an untested guess.
- **Open.** The 58% and 54% exact print shares are unexplained. Top of book only, so no walk through deeper levels.
- **Checked, no issue.** Every number in today's notebook entry matches `results/replay/sanity_2026-09-01.json` and the audit row count. Tests pass. No test day touched. No Alpaca order sent.

## 2026-11-17
I did this check myself.
- **Found and fixed.** The first draft of the notebook entry called the tail share a result. It is a ratio over a near zero total (negative 170), so it is now labelled not interpretable. The prereg said a five level walk and the code does not walk. Logged under Deviations with the flag rate.
- **Open.** Dev day only, so H1 is untested. The H1b split uses the future second of the book and is descriptive. Random decisions make a small cost likely by construction.
- **Checked, no issue.** Every number in today's entry matches `results/taker/taker_dev_2026-09-01.json`. Tests pass. No test day touched, no Alpaca order sent.

## 2026-11-18
I did this check myself.
- **Found and fixed.** Added a note that flat fill probability across delay is partly built into the design, so it is not read as proof that delay is harmless for passive orders. Choices the prereg left open are logged under Deviations.
- **Open.** Dev day only, so H2 and H2b are untested. Cancels are inferred from size drops and the rate of misclassified trade versus book timing is unmeasured.
- **Checked, no issue.** Notebook numbers match `results/passive/passive_dev_2026-09-01.json`. Fifteen tests pass. No test day touched, no Alpaca order sent.

## 2026-11-18 (reread in a separate sitting)
I went back over the notes, the code and every results file at commit a16dd69 in a separate sitting, against my review checklist. This is what I found and what I did about each.

**Found and fixed**
- Both primary tests reprice on arrival, so with random decisions H1 and H2 are close to zero by construction. Logged under Deviations before any test day, with a fixed price passive arm (H5) added as exploratory. H1 and H2 stay as registered.
- Yueshen (2026) was recorded as read in full. It was not. The files I saved as the paper were bot challenge pages. Moved to the Unverified list at abstract level, year given as 2026, a claim not in the abstract removed, and a dated correction added to the lab notebook. H2c stays because the abstract supports it. The 11-15 entries of this log that mention Yueshen figure pages were wrong for the same reason. A copy of the paper has since arrived and is being read. *(Read in full later the same afternoon, see below.)*
- No committed code produced `results/replay/sanity_2026-09-01.json`. Added `src/s2f/sanity.py` and `make sanity`. The rerun reproduces the file exactly.
- `make reproduce` left out the sanity check, the taker and the passive leg. It now runs the audits, the tests, the sanity check, the taker and the passive leg. The rerun taker file matched the committed one byte for byte.
- The flag rate was 0.13% to 0.31%, not 0.17% to 0.31%. My 11-17 entry here said every number matched. That was wrong. Corrected in the notebook and with a dated note under Deviations.
- The taker tie flip affects only 6 of 8,425 decisions, so it was a weak check presented as robustness. Measured with `src/s2f/tie_share.py` and said so in the notebook and under Deviations.
- The 11-18 notebook entry left out the matched markouts, which run against H2c under all three rules, and the share of orders whose level left the top five (about 38%). Both added. The phrasings that read as support for Yueshen, and "does not depend on delay", are removed.
- The H1b split is partly mechanical, and the comparison with Albers et al. was worded too strongly. Corrected in the notebook and noted under Deviations.
- The passive code nets each book update instead of applying trades, then cancellations, then additions. Logged under Deviations. The 600 s end of day cut was also unlogged and is now there.
- The LOBSTER note said the INTC and MSFT choice came before anything about fills was computed. Fill shares came from the same audit. Corrected to say only that it came before any markout.
- PROPOSAL.md had an added section and was missing the line "I have not run the study". Restored to the PDF as written, and the added section moved to the project README.
- Smaller items. "about 21 points" now "about 22", the Albers PDF described as the published version, the decomposition claim marked as planned, the Danait zero latency point marked as my reading, a dead line in `passive.py` removed, and the project status line updated.

**Disclosed**
- On 2026-11-15, before the preregistration commit, I rewrote the messages of the commits made up to then with `git filter-branch` and pushed the result, which replaced commits that were already public (for example 754cc9e). Only messages changed. The branch `backup-before-msg-rewrite` holds the old commits and its tree is identical to 759cf4c. I should have said this at the time.

**Open**
- No interval yet for H1b or for the matched H2c markouts. The RQ3 split and a working tie flip in the passive leg are not built. All are due before the test days.
- The ranking reversal shares from Danait et al. are read off a chart. Their supplementary material and that of Albers et al. are unread.

**Checked, no issue**
- The reread found no test day data on disk, and the preregistration commit comes before the replay engine and every taker and passive result.
- All other audit, taker and passive numbers in the notes match their results files. Seventeen tests pass.
- Later the same afternoon the full text of Yueshen (2026) was read, all pages viewed, the proofs for structure only and the online appendix not at all. It moves back into the main table of the literature review with that depth. The size ratio claim removed this morning is in Proposition 4(i) and is restored with its condition (fast and slow makers together). The delay to markout step in H2c is not in the paper. It is my inference, now said so in the notebook, the review and under Deviations.

## 2026-11-18 (evening, Moallemi & Sağlam read)
**Checked, no issue**
- The one line in the literature review that cites Moallemi & Sağlam (2013) was checked against the full text, claim by claim. Venue, closed form, stylised model, calibration on equities and the missing drift against queue split all hold. Its reading depth is raised to full text and the row now says what the model leaves out.
- No hypothesis, metric or test changed. No test day data touched. No Alpaca order sent.

**Open**
- On my reading of their Figure 9 the drop in median implied latency is about one order of magnitude, while their text says two. I do not cite the two orders figure. On a fresh read I should look at the same chart again.
- I didn't reread this in a separate sitting.

## 2026-11-18 (Wed, evening) · edit to this log
- I removed two formatting notes from earlier entries. They were about how the notes are written, not the research, and nothing else in those entries changed.

## 2026-11-18 (Wed, night) · library notes for Danait, Albers and Yueshen
- **Found and fixed.** The literature review said Danait's zero latency was my reading, but the paper states it (Section 9). Fixed and logged in the notebook.
- **Open.** The 11-16 Danait entry says the tables were read from a PDF, and no PDF copy is in my files now. Table 2 and Figure 1 need checking against the PDF pages. The Albers supplement is still unread.
- **Checked, no issue.** Albers Tables 1, 4, 6 and 7 and the Yueshen Lemma 1, Proposition 1 and Proposition 4 references match the papers. I did this check myself.


## 2026-11-18 (Wed, night) · Albers supplement read
- Read the Albers supplement in full. Main paper page refs still match the journal pages, and the SSRN page mapping is recorded in the library note. One contradiction with my notes, the colocated 2 ms point, corrected with a pointer. The journal text's pointer to bootstrap standard errors in Supplementary Material E finds nothing there. No hypothesis, metric or test changed, and no test day data was touched. Not reread in a separate sitting.

## 2026-11-18 (Wed, late night) · Budish, Cramton & Shim read
- **Checked, no issue.** The one review line citing the paper was checked claim by claim against the full manuscript. Sniping costs for stale quotes are there as a model result (Proposition 1, Remark 1), and the RQ3 motivation fits the comparative statics and the volatility link in the data, with "concentrated" marked as my framing. Reading depth raised to full text, with the version named. The companion is added with its own depth. No hypothesis, metric or test changed. No test day data touched.
- **Found, noted.** The copy I hold is the February 2015 manuscript, not the journal article, so its pages are cited and the QJE pages are kept only from the DOI record. The paper's calibration product is misprinted by a factor of 1,000, while its stated bounds are right.
- **Bias check.** The paper argues for a design, so its facts were not read as a neutral survey. What it adds against my own results went in plainly. The missing race likely inflates the replay's delay cost in jump moments, which would flatter H3 if it passes.
- **Open.** Not reread in a separate sitting.

## 2026-11-19 (Thu, afternoon) · dev day follow ups
I went back over this work myself, in the same sitting that did it.

**Found and fixed**
- The passive code's flipped tie rule changed only the book my order sees and quietly dropped every trade, ticker row and snapshot stamped exactly at arrival. It had never been run, so no result was affected. It now replays those events after my order, with a test.
- `passive.one` failed on an empty event window. That never happens on the real day (the reruns of both passive legs reproduce the committed summaries exactly), but the small test case hit it. Guarded.
- The registered tail share is meaningless when the total latency cost is near zero. On random decisions it comes out as negative 170. Said so in the notebook rather than reporting it as a number.

**Open**
- The five level walk reads a snapshot that updates every 26 ms at the median, and on signal decisions it runs out of levels on 40.7% of cases at 1 ms. Its deeper prices can be stale. Not fixable with these files.
- The Budish jump split and stale liquidity count are not built. Their thresholds must be set on the dev day before the test days or they are dropped.

**Checked, no issue**
- Spec before outcome. The Deviations entry and all the follow up code went into commit 1fa991e, pushed before the first run. The only values seen before writing it were the 11-18 point values, the signal threshold and the decision count, and the entry says so.
- No test day file was downloaded or read. Both new scripts refuse any day other than the dev day unless that is turned on on purpose.
- Every number in today's notebook entry was read back from the two results files. Thirty two tests pass.
- Bias. Two pieces lean toward a tidy story and both are labelled exploratory. Split B for H1b, written today before it ran, and H5 without the marketable orders, which picks decisions by an outcome of delay. The big signal decision taker cost rests partly on a thin 1 ms touch that a live order would likely lose to someone faster, and the notebook calls it an upper end. The H2c and RQ3 results that went against my hypotheses are reported as plainly as the rest.

## 2026-11-19 (Thu, evening) · RQ2 and queue positions on LOBSTER
I went back over this work myself, in the same sitting that did it.

**Checked, no issue**
- Spec before outcome. The Deviations entry and `lobster_rq2.py` went into commit f3f5623, pushed before the first run. Only the earlier audit file had been seen. No spec, threshold or sample rule changed after the run.
- Every number in the notebook entry was read back from `results/lobster/rq2_2012-06-21.json`.
- H4 judged as registered. The raw negative coefficient is reported, and so is its loss after controls, which the preregistration calls a null.
- The tests for the distance and the book reader pass.

**Open**
- The queue position result keeps under half of deletions in INTC and MSFT, and the filter may favour levels built during the day. Stated as a limit.
- "Back is closest" is closest of three, not a fit. The notebook says how far off it is.
- The reading that back of queue cancels come from quick in and out orders is untested and labelled so.

**Bias check.** The queue result points to my back rule being nearer reality, which makes passive numbers look worse for me, and it's reported as found. H4 failing goes against my own hypothesis and is stated as plainly as the rest. No test day data was touched.

## 2026-11-19 (Thu, night) · Cartea & Sánchez-Betancourt (2021) read
- **Checked, no issue.** The one review row citing the paper was checked claim by claim against the journal article. Missed fills from latency, taker side only and proprietary LMAX data are all there (pp. 255, 260). "Concentrated in high volatility" holds in direction (Tables 5 and 8) and the row now carries the caveats. Depth raised to full text. The quartile shares of misses were recomputed from the tables and match the paper. No hypothesis, metric or test changed. No test day data touched.
- **Found and fixed.** The Not found line was true as written, since their replay is on proprietary data, but it left out the nearest case. Section 7 is now named there, and the claim of what is new says public data.
- **Bias check.** The paper's volatility result points the way H3 does, and it would be easy to lean on it. Its windows were tuned to that result and its closest test of extra delay splits between the two traders, so it is cited for the fill side only and the T2 result against H3 is written down beside the T1 one.
- **Open.** Not reread in a separate sitting.

## 2026-11-19 (Thu, night) · Hasbrouck & Saar (2013) read
- **Checked, no issue.** The one review row citing the paper was checked against the journal article. Strategic runs from NASDAQ message data (pp. 658 to 659) and the market quality focus (pp. 647, 664) are both there. Depth raised to full text. The arithmetic behind the slips I list was redone by hand. No hypothesis, metric or test changed. No test day data touched.
- **Found and fixed.** Nothing was wrong. The row was thin and now says what the paper found and where it stops.
- **Bias check.** The paper's Table 2 makes my untested back of queue reading look plausible, and it would be easy to lean on that. It is written as one possible story, from 2007 data, and the idea that follows from it is a single descriptive count with its stop point set now. The paper's weaker spots (the volatility link without instruments, the effective spread coefficients bunched around zero stock by stock) are in the library note next to its headline.
- **Open.** Not reread in a separate sitting.

## 2026-11-19 (Thu, late night) · jump moment split
I went back over this work myself, in the same sitting that did it.

**Checked, no issue**
- Spec before outcome. The specs, window, horizons, thinning, seed and the too small rule went into commit 281affd at 23:04 CST, and the first run wrote its results 31 s later. Nothing in `jumps.py` changed after the run. All three specs are reported, including B, which is too small to read.
- Spec A's counts and its 1 ms stale share were recomputed by a different route (a time join in polars) and match. Every number in the notebook entry carries a tag and claimcheck agrees with the results file. 39 tests pass.
- No test day file downloaded or read. The script refuses any day but the dev day unless that is turned on on purpose.
- Sources. The 7 ms median duration and the 100 ms batch example are from the Budish et al. library note, the 2 to 3 ms reaction time from Hasbrouck and Saar, both as read in full. The fee tiers are from the Binance USD-M fee page as shown on 2026-11-19, and the notebook says it may differ from September.

**Found and fixed**
- While tagging, I had written 18.5% for the spec C stale share at 1 ms. The file gives 18.4%. Corrected before commit.

**Open**
- Signal decisions fire when one side of the touch is nearly empty, which is also what a fast move tends to leave behind. So the A signal split mixes the two and rests on 39 decisions.
- The stale baseline is taken at random microsecond times, while jumps sit on a ticker stamp in the middle of activity. A fairer baseline would be the same count at random ticker stamps. Not run, and not added after the look.
- The spread refill reading is my subtraction of two means, not a direct measure.

**Bias check.** The stale count came out the way my reading of Budish, Cramton and Shim led me to expect, which is a reason to be careful with it. The notebook says plainly that part of it is the move carrying on, that the baseline isn't like for like, and that the H3 split on random decisions came out empty. Nothing about H1 to H5 changed.

## 2026-11-19 reread before test days
I went back over tonight's work and the test day setup in a separate sitting, against my review checklist. No test day or breadth day file was downloaded or read.

**Found and fixed**
- LAB_NOTEBOOK, jump decisions. "Both sides gain from waiting" was stronger than the data, since the interval for going with the jump runs from negative 0.28 to 0.06. It now says both means are negative and that interval covers zero, and the spread refill stays marked as a reading.
- LAB_NOTEBOOK, signal decisions after a jump. "Lower than the rest by negative 1.13" read as a double negative. It now says their ΔS(100 ms) minus that of the rest is negative 1.13. Same number, same tag.
- LAB_NOTEBOOK, the Alpaca latency gaps and the breadth day limits. Seven labels written as a word and a colon now end in a full stop, as in the newer entries.

**Open**
- Signal threshold on the test days. `taker_followups.py` and `passive_followups.py` call `make_signal_decisions(book)` with no threshold, so on a test day they would take the 90th percentile of that day and not the dev day value. Only `jumps.py` passes the frozen value, and it passes 0.9863 where the dev day file stores 0.98630194. Needs a fix committed before any test day run.
- Robustness checks 1, 3, 5, 6 and 8 in the preregistration (fees, local capture order, 1 BTC orders, passive horizon of 1 s and 60 s, 15 minute blocks) have no code yet. The tie flip, the placebo and signal decisions do. Either the code is written and committed on the dev day before the test days, or a dated Deviation says how they will be handled.
- No single test day run. Every Makefile target is fixed to 2026-09-01, so the test day session runs each module by hand with `S2F_ALLOW_TEST_DAY=1`. `taker.py`, `passive.py`, `sanity.py` and `tie_share.py` have no dev day guard, and every results file name says dev even on a test day.
- Which taker fill is primary for H1 on the test days, top of book as built (Deviation of 2026-11-17) or the five level walk (2026-11-19 afternoon), should be stated once before the run.
- The jump count line says the day fell, so most thinned jumps are down moves. The share is in the file (33.5% up under A), but the day's fall doesn't imply it.
- The breadth day Deviation has a prose colon before its list of dates. Registered text, left as is.
- README lines 16 and 17 use a bold label and a colon, from an edit of 2026-11-18. Left as is.

**Checked**
- Jump split order. 281affd at 23:04:23 CST holds the code, thresholds and notebook entry. The results file was written at 23:04:54 CST, and fb5e645 followed at 23:09:48. `jumps.py` has not changed since 281affd. Specs A, B and C, the 5 ms window, the 1, 2 and 5 ms horizons, the 1 s thinning and seed 20261115 + 101 in the code match the notebook and the Deviation.
- Jump numbers against `results/jump/jump_split_2026-09-01.json`. Spec A stale share at 1 ms 12.4% (8.0% to 16.9%) against 0.09%, 1 of 8,425 random decisions in the window, 39 signal decisions, 194 thinned jumps. All match. The entries are labelled exploratory and the reading is marked untested.
- Preregistration order. 913347d on 2026-11-15. Everything above the Deviations heading is unchanged since then, and every later change sits under Deviations with a date. 2d31501 and 1a87f6e came before any test data, and none exists in `data/raw`, `results` or git history.
- `get_data.py` fetches 2026-10-01 and 2026-11-01 for test and the six breadth days, each behind the preregistration check, and skips files already present. Bootstrap code uses 5 minute blocks, 2,000 resamples and seed 20261115 throughout.
- Unit tests 39 passed, claimcheck tests 81 passed. claimcheck on 01 exits 0, 676 PASS lines, no failure, 33 untagged warnings.
- Sources. Spot checks of the Cartea and Sánchez-Betancourt and Hasbrouck and Saar notes against the article text (the 36.5% and 40.0% shares, 20.02 ms to 2.34 ms, 9,483 misses, footnote 4, the 2 to 3 ms peak, footnote 22) all match. Both rows say full text and the PDFs are on file.
- Dashes, prose hyphens and colons in prose added since 2026-11-19, and commit messages. Nothing else found.

## 2026-11-20 reread of pre test fixes
I went back over commits 4718a82 to 47bc3ae in a separate sitting. No test day or breadth day file was downloaded or read, and nothing was run on any date but the dev day.

**Found and fixed**
- LAB_NOTEBOOK, H1 under both fills. It said the walk Deviation went in before I computed or read any walk number in this session. Before 0ce7979 I did see two signal decision walk values while searching the files, the 0.104 slope and the 40.7% share past five levels. Both had been in the results since 85ec66f and in the notes since the 2026-11-19 follow ups, so nothing new was learned, and the entry now names them. The Deviation text is registered and is left as written.
- LAB_NOTEBOOK, dry run. It said all fourteen files matched with no difference at all. Thirteen match byte for byte and the audit file matches in every value but is written with a different indent. The entry now says so.
- `scripts/guard` refused any commit message with the word rule, which would have stopped messages about the tie rule or the back rule on the test days. It now refuses only the longer phrases it was meant for.

**Open**
- Robustness item 7, the placebo, exists for H1 under both fills but not for H2. The registered text names no leg. Either a dated Deviation says it applies to H1 only, or an H2 placebo is built and committed before 2026-10-01 is run.
- H1b and H3 stay on the top of book cost (Deviation 0ce7979), while RQ1a defines ΔS on the five level walk. On random decisions the touch is short of the order on at most 0.31% of decisions, so the effect is small there, but on signal decisions the touch is thin half the time. The reason given is only that the code was committed that way.
- Fees are frozen at 2 and 5 bps from the page as read on 2026-11-19. The Deviation says the page is not read during the run but that a changed tier would be noted. Someone has to open the page on the day and write down what it shows.
- `run_test_day` does not check that both test days have run before it accepts a breadth day, and it does not apply the one hour gap cut for breadth days. The order and the cut are left to the person running it.
- `data_audit.py` run on its own has no dev day guard. Only the runner reaches it on a test day today.
- If a run stops part way, the script refuses a second start and leaves the call to the person running it.

**Checked**
- Order. 0ce7979 at 23:41:31 CST came before any new walk computation. The taker follow ups rerun was written at 23:43:27 and the new walk lines in the taker file at 23:54:03. The robustness spec 4b23f3a at 23:47:15 came before the first robustness file at 23:47:44, `robustness.py` has not changed since, and no robustness output is in git before dea0e59. The local order check ran before the runner refactor was committed, as the notebook says, and the dry run on the committed code reproduces it byte for byte.
- The random decision walk numbers for H1 were already in `results/taker/followups_dev_2026-09-01.json` from 85ec66f, as the Deviation says, and `primary_five_level_walk` equals them. The return to the walk is the registered spec, and both fills are null on the dev day.
- Robustness choices against the registered list. Fees frozen rather than read on the day, horizon counted from arrival, local capture order with decisions redrawn, 1 BTC on the walk for both legs, 15 minute blocks, and the scope of H1 and H2 on random decisions are all in the Deviation of 4b23f3a. The tie flip, the placebo for H1 and signal decisions (items 2, 4 and 7) run inside `taker.py` and the follow ups.
- Threshold. Every signal path in `taker_followups.py`, `passive_followups.py` and `jumps.py` reads 0.9863019382810347 from the stored dev file through `frozen_threshold`, and nothing calls the percentile function. The three dev files are the same bytes before and after de18889.
- Runner. Only the two test days and six breadth days pass, the dev day only through the dry run. One argument, no options, seed 20261115 checked, outputs and saved arrays checked before anything runs, and each write refuses an existing file. Test day steps run the primary tests first, then the follow ups with H1b, H2c, RQ3, signal decisions and H5 without the marketable orders, then the robustness checks, then the jump split. The H5 code without the marketable orders is unchanged since 2d31501. Every module stops on a test day unless the runner sets the switch. The dry run output in `/tmp/s2f_dryrun_ae07swwy` matches all fourteen committed files.
- Hooks. `.git/hooks/pre-commit` and `.git/hooks/commit-msg` are installed and executable and call `scripts/guard`. Every commit message in the range passes it, and no dash, prose colon or prose hyphen was added to the notes.
- Unit tests 64 passed, claimcheck tests 81 passed. claimcheck on 01 exits 0 with no failure and 34 untagged warnings.

## 2026-11-20 (Fri, morning) · claimcheck on the whole folder, and the list from the 11-18 reread
I checked this myself, in the same sitting.

**What claimcheck caught**
- The 0.067 bps in the 11-18 passive entry, where the file gives 0.0665. Found when the dev day numbers were first tagged on 11-19 and corrected then with a pointer.
- Two right numbers flagged as wrong because they sat exactly half a unit from the stored value and floating point put them just outside the tolerance. Fixed in the checker, not in the notes.
- Nothing else. Today's full run has 458 claims and 501 tags all agreeing with the files, every literature row with a depth, nothing on the Unverified list cited, the preregistration first committed in 913347d with no test results yet, and 56 untagged numbers as warnings. Exit 0.

**What the 11-18 reread found, and where each item ended up**
- High items. Primary tests null by construction, logged under Deviations with the fixed price arm as exploratory. Yueshen depth corrected, then read in full the same afternoon. Sanity code added with `make sanity`, and it reproduces the file. All on 11-18.
- Medium items. `make reproduce` now covers sanity, taker and passive. Flag range corrected to 0.13% to 0.31%. Tie flip reported as a weak check and measured. Matched H2c markouts and the 38% left the top five added. Yueshen framing removed. H1b split called partly mechanical. Netted updates and the 600 s cut logged. LOBSTER selection statement narrowed. All on 11-18.
- Low items. All handled on 11-18 as listed in that entry, including the disclosure of the commit message rewrite.
- What was still open after 11-18. The H1b interval, an interval for the matched H2c markouts, the RQ3 split and a working tie flip in the passive leg were all built on the dev day on 11-19 (afternoon entry in the notebook), before any test day. H2c fails on the dev day under all three rules with intervals above zero. The Danait ranking reversal shares now come from the printed values in their Section 7.2, which agree with what I read off the chart. The Albers supplement was read in full on 11-18.

**Open**
- 56 untagged numbers in the notebook, which must reach zero before release.
- Whether the result files regenerate exactly was checked for the taker on 11-18 and for all fourteen dev day files in the 11-20 dry run. Not rechecked today.
- No file can prove test day data was never fetched outside `get_data.py`. The preregistration check only reads git history.
- I haven't looked for a supplement to Danait et al.

**Checked**
- claimcheck tests 84 pass. No dash, prose colon or prose hyphen in these two entries. No test day or breadth day file was downloaded, read or run.

## 2026-11-20 (Fri) · test days, breadth days and the cut first start
I checked this myself, in the same sitting, and didn't reread it separately. A fresh read of my own is still owed before release.

**Found and fixed**
- The first start on 2026-10-01 was cut off by the machine's 20 minute job limit inside the robustness step. Partial outputs were moved out of the repo with checksums, the runner got fixed parts (dfe8b61) and the day was rerun once from the start. All ten files and twelve saved replays the cut start had written came back identical.
- The 2026-03-01 file opens with whole number prices and the csv reader guessed an integer column, so its first start stopped in the audit before writing anything. Price and amount columns are now always read as decimals (c3a1861). On the dev day the audit and sanity files come out the same, and on both test days the trade and five level files read identically with and without the change. No output for 2026-03-01 existed when it was restarted.
- The first start on 2026-07-01 stopped in the audit with a read error from the disk. The three raw files test as intact gzip, nothing had been written, and the restart went through.

**Open**
- Steps after the cut on 2026-10-01 and every step on 2026-11-01 ran only in parts. Parts reload the day where one process would pass it along. The dev day dry run and the identical rerun of the first ten files are the evidence that this changes nothing. I haven't run a full test day in one process.
- The breadth gap rule is about the total of gaps over 1 s. The audit stores only the count and the longest gap, so the table uses count times longest as an upper bound. Every day used is far under an hour on that bound.
- The fixed price slope without marketable orders held by the 2d31501 rule. The kept set changes with delay, so this is a description and a candidate for later work, not a result.
- Today's numbers are not tagged for claimcheck yet.

**Checked**
- Order. Prereg 913347d, the H5 rule 2d31501 and the breadth rule 1a87f6e all predate the first test day result (4854717). The breadth table code was committed (68093fd) before any breadth day number was read. No calculation module changed between the dev day dry run and the test days except the csv reading, which is checked above.
- Each test and breadth day ran once. Nothing was rerun after a look, no seed or threshold or window was changed, and every spec in the runner is reported.
- Source fidelity. No new source was read or cited today.
- Bias. The two nulls are stated as nulls, H5 and H2c are reported as pointing the other way, and the signal decision costs are kept secondary.
- No dash, prose colon or prose hyphen in today's notebook and log entries.
- The csv reading change (c3a1861), checked again once every day had finished. I did this myself. For the dev day 2026-09-01 and both test days I loaded the raw files through the reader as it stood at c25f8bb (a separate git worktree) and through the current reader, calling the real audit and five level setup code on both clocks, and kept each frame the reader returned. That is 8 frames a day, book ticker, trades and five level snapshots. Every frame matched the other version in columns, dtypes and every value, nulls included. Price columns were Float64 in both, amounts Float64 in the audit and trades and Float32 in the book replay, as before. No results file was opened for this. The two test days were read from a local copy after the shared disk gave a read error. The copies match the originals by sha256.

## 2026-11-20 (Fri, evening) · Cartea & Sánchez-Betancourt (2023) read
- **Checked, no issue.** The one review row citing the paper was checked against the preprint. Marketable limit orders under random latency (pp. 1, 9 to 15) and theory with FX data (Sections 3 and 4) are both there. Depth raised to full text, and the row says it was the preprint. Volume and pages come from the DOI's Crossref record, not from the typeset paper. Two library notes that said I hadn't read it now link to it. No hypothesis, metric, test or test day result changed. This reading came after the test days and breadth days.
- **Found and fixed.** Nothing was wrong. The Not found paragraph was true as written but missed a second near case, Section 4 and Table 9 of this paper, which is now named.
- **Bias check.** Two things here would be easy to lean on. Their fixed and random latency strategies perform alike, which flatters my fixed grid, and their news result sounds like support for latency risk in volatile moments. The first is about an optimised strategy and the second is about a limit order strategy against market orders, so neither is cited as support for my design or for H3, and the note says H3 was null. Their weaker spots (no proof of optimality, tests on runs that share price paths, the spread filter at the value where gains peak) sit in the library note next to the headline.
- **Open.** Not reread in a separate sitting. The typeset version not read.

## 2026-11-20 (Fri, night) · Moallemi & Yuan (2017) read
- **Checked.** Both repo lines citing the paper were checked against the June 2017 working paper. The review row's "queue position has economic value, large for large tick assets" holds (pp. 1, 6, 20, 23 to 24), with the catch that large tick is assumed, not compared. Depth raised from the SSRN listing to full text, and the row now says it is the working paper. No hypothesis, metric, test or test day result changed. This reading came after the test days and breadth days.
- **Found and fixed.** The 2026-11-14 notebook line said the paper predicts queue value is largest for large tick assets and used that to expect a lot from queue position on BTCUSDT. The paper argues the premise and doesn't predict a ranking, and its reason, a tick that is economically significant, doesn't hold at about 0.013 bps. Correction entry added in the notebook, with a pointer on the old line. Nothing registered rested on it.
- **Bias check.** The flattening fill probability in a deep queue would make a neat story for the H2 null. It's written up as my inference, consistent with the null and not evidence for it. The paper's weaker spots (impact borrowed from another paper, no standard errors, day counts that don't agree) sit in the library note next to the headline, and the abstract's "same order of magnitude as the spread" is set against the measured gaps of 0.03 to 0.22 ticks.
- **Open.** Not reread in a separate sitting. No published version read.


## 2026-11-21 (Sat) · first draft of the final report
I checked this myself, in the same sitting. A fresh read of my own is still owed before release.

**Found and fixed**
- My first draft gave a source count for the literature review that I had not counted. The count is removed.

**Open**
- Numbers in FINAL_REPORT.md are not tagged for claimcheck yet, and the notebook still has untagged warnings from 2026-11-20. Both have to reach zero before release.
- No reread in a separate sitting yet.

**Checked**
- Every number in the draft was compared with the 2026-11-20 notebook entries, which cite their results files. Tests (74) pass and claimcheck reports all tagged checks agree. No test or breadth day file was touched.

## 2026-11-21 (Sat) · numbers tied to files, report figures, my own pass
I did this check myself, in the same sitting that wrote the tags, the figures and the report changes. It is not a fresh reading. A reread in a separate sitting is still owed before release.

**Logic**
- Every number in the report, the README and the notebook now either points at a field in a results file or is marked as not a result. The marked ones in old entries are listed in the notebook entry of today, sorted into hand worked and checked, design settings, and not in any file.
- Each hand worked number in an old entry was recomputed today from the fields it came from, and each one holds. The tightest was the bound on unconditional markouts in the 18 Nov entry, which holds by a hair.
- Two old remarks have no file behind them at all, the median update gap of the five level snapshot (19 Nov afternoon) and the stopped first broker run (19 Nov). They stay as written and marked. The report uses neither.
- The figures read results files and nothing else. No statistic in them is new. Rerunning the script gives identical files.
- No analysis was run, and no hypothesis, threshold, seed, spec or day changed. PREREGISTRATION.md was not touched.

**Found and fixed**
- README status gave the signal cost by 500 ms as from 0.5, which rounds the smaller test day too far. It now gives the file value.
- README results said random decisions lose nothing measurable on any of the eight days. On 2026-07-01 the H1 interval sits just above zero, so that was too strong. It now says so.
- README Limits counted three crypto days. There are nine.
- In my own first edit of the report today I wrote that no two robustness misses shared a rule and a day, which I hadn't checked. It went back to what the 11-20 entry says, that none holds across rules or days.

**Source fidelity**
- No source was read or newly cited today. The report's literature paragraph is unchanged, and the source check finds every review row with a depth and no unread work cited.

**Bias**
- The two primary nulls lead the report and are stated as nulls. H2c and H5 are reported as pointing the wrong way where they point at all.
- The signal decision result stays labelled secondary, and the report now says the 1 ms baseline makes it an upper end.
- The breadth days and the dev day calibration appear in figures next to the test days. Captions and text say verdicts come from the test days only.
- The fixed price exploration stays exploratory, with the reason (the kept set changes with delay) next to its range.

**Open**
- Nothing since 2026-11-20 has been reread in a separate sitting.
- The two untraceable remarks above.
- Whether every results file regenerates exactly was last checked in the 11-20 dry run on the dev day, not on the test days.

**Checked**
- `make verify` exits clean with no untagged numbers, every tag matching its file, sources clean and the preregistration order intact. The proposal tests and the checker's own tests pass.

## 2026-11-21 (Sat, later) · a fresh read of the report, and what I changed after
I went back over the report, both READMEs, the notebook, the preregistration and the code at commit 7d1b87d in a separate sitting, against my review checklist, and changed nothing in the repo while I read. Then I made the changes below. No analysis was run, no day, spec, threshold or seed changed, and PREREGISTRATION.md was not touched. Every new number in the report and README is an existing field in `results/`, now tied to it in `claims.yaml`.

**Found and fixed**
- The report left out H4 and the broker latency measurement, both registered. H4 (null by its registered rule, INTC and MSFT on the LOBSTER day) and the latency (median, 90th and 99th percentile over 200 orders, a broker paper venue and not Binance) are now in the report's results, the bottom line and the README results.
- The Deviation of 2026-11-18 promised to say plainly next to H1 and H2 that random decisions which reprice on arrival make them uninformative by construction. The report didn't, and its bottom line read as a finding that delay costs nothing. That sentence now sits after both primary results, in the bottom line and in the README, and the old "my inference, not tested" line about the nulls is gone.
- The signal headline had no caveat in the bottom line. It now says the number is an upper end, gives the test day share of decisions where the touch at 1 ms held less than the order, says the walk ran out of shares too and why (the five level snapshot can lag the touch), and says the S numbers are the top of book fill while the slope is the walk.
- H5 sat under Secondary. It now sits under an exploratory heading, says why the cost falls with delay (orders that can trade on arrival get a free option in a replay with no race), and reports the fixed price fill slopes, below zero under all three rules on 2026-10-01 and mixed on 2026-11-01.
- Robustness item 2, the tie flip, was not reported. It changed no cell on either test day, and the report now says so and why.
- The Honesty box and README Limits now name the missing race, the modelled queue, the netting inside one update, the share of repricing orders lost when their price leaves the top five, the stale snapshot in the walk, the frozen fee tier and that the latency was a broker paper venue.
- The repo said `make reproduce` reruns every number. It reruns the dev day work. The 01 README now says what it does and does not redo, and how a test day could be rerun. The root README line is narrowed to match.
- The root README's "What I believe now" still called the passive side an untested hypothesis. It now says what the test days showed and what they can't show.
- Smaller things. H1b split B on the test days, the H2c framing as my own inference, the |I| split and the tail share, the cancellation placement and jump split, the breadth verdict labels, that the signal intervals may be too narrow, a clause on the placebo intervals, a `pytest.ini` so the proposal tests run without setting the path by hand, the stale comment at the top of `claims.yaml`, two lines in the literature review (the LMAX fill rate, which is about 80% to 90% on p. 255, and the netting inside one update), and one wording line in the root README.

**Open**
- The report stays marked draft until one last read before release.
- A heading in the Deviations of the preregistration was edited after it was committed. Commit 5483ec5 changed "2026-11-18 evening" to "2026-11-18, later in the afternoon", six minutes after 59a5cee first committed it. That was before any test day and only the time label changed, but it is an edit to registered text outside a new dated entry. I leave it as it is rather than edit registered text again, and note it here.
- Whether the H1 and H2 files written by the cut first start on 2026-10-01 were opened before the rerun. I can't tell from the record. The rerun was byte identical, so nothing could have changed either way.
- Figure 3 uses matplotlib's offset notation in a corner of most panels, which is easy to miss on a scaled image. Not changed. *(Fixed 2026-11-21 night, see that entry.)*
- The checker's own tests still need to be run from the repo root.
- Test and breadth day results have not been regenerated to check them. Only the dev day has a dry run.

**Checked**
- I matched 22 values in the report against their results files by hand, found the preregistration history clean, and found every Deviation before the test data on disk. I saw no number that disagreed with its file.
- After the changes, claimcheck reports every tag agreeing with its file and no untagged numbers, the source and preregistration checks pass, and the proposal and checker tests pass.

## 2026-11-21 (Sat, night) · Danait et al. read again from the PDF
- **Found and fixed.** I had written that the 7911.T front and back passive intervals touch. They overlap a little. The library note is fixed, the correction is in the notebook, and the 11-16 entry stays as written.
- **Closed, from the 11-18 night entry.** The 11-16 entry's claim that the tables were read from the PDF. The PDF I have now is version 3, the same text as the web page the notes cite, and Table 1, Table 2 and Figure 1 on its pages match every number in that entry. Which copy I read on 11-16 isn't in my files, so that part can't be shown, and I don't claim it.
- **Checked.** The version and every page reference in the library note against the PDF. The literature review row now names the version and says when it was read again.
- No hypothesis, test or result changed. I did this myself.

## 2026-11-21 (Sat, night) · Figure 3 scale on the axis
- **Found and fixed.** Figure 3 showed its scale only as small offset text in the corner of each panel. The scale now sits in the axis label (for example "bps per log ms, ×10⁻³") and the corner text is gone. Only the drawing changed. The tick values, points and intervals are the same, and the script still reads nothing but the results files.
- **Checked.** I ran the figure script again. Figures 1, 2, 4 and 5 came out byte identical to the committed files, and Figure 3 comes out the same on a second run. I looked at the new Figure 3 at full size, and no label is clipped or sits on another.

## 2026-11-21 (Sat, late night) · tonight's changes and every Danait citation
I did this check myself. It covers the Danait reread, the Figure 3 change, and every place in this folder and the library that cites Danait et al.

**Found and fixed**
- In tonight's notebook entry I first wrote that every Danait number I quote sits in Tables 1 and 2 or in Sections 7.1 and 7.2. Some come from Sections 4 and 6 (the sample dates, the probe and parent sizes, the resample count). The line now says so. All of them are on the PDF pages.

**Open**
- Figures 4 and 5 still show their scale as offset text in a corner, the same thing Figure 3 had. Left as they are tonight.
- The literature review row for Danait gives sections, not pages. The pages are in the library note.
- Which copy I read on 11-16 stays unknown. The item is closed on the numbers, as above.

**Checked**
- Logic. The interval correction makes the 7911.T rule gap look weaker, and the 11-16 line already called it marginal. Nothing registered rests on it. In the literature review, calling front my best case and back my worst case matches their finding that front is most favourable to passive orders and back least (Section 8.2, pp. 6 to 7), and the same section of my review says these are not true bounds.
- Source fidelity. Version 3 everywhere a version is named (the literature review, the library note and its index row, the 11-14 entry). Every page reference in the library note against the PDF. Every Danait number in the library note, the literature review row and the 11-14, 11-16 and 11-18 notebook entries is on the PDF pages. The two bar readings on 11-16 are marked approximate and agree with the printed shares. Reading depth says only what I did. The whole paper read, the bars taken by eye, their interval method not checked, no supplement looked for. The preregistration line on applying trades, then cancellations, then additions matches Section 3.1 (p. 2). The report and the READMEs don't cite the paper by name.
- Bias. Nothing tonight makes a result look better. The one correction cuts against the tidier story.
- Figure 3. Only the drawing changed. The script reads the same results files, the other four figures are byte identical, and the new image has no clipped or overlapping text.
- From the repo root, claimcheck has every check agreeing and no untagged numbers. Proposal tests 74 pass and the checker's tests 84 pass.
- Every line added tonight is free of dashes, prose hyphens and prose colons, makes no time cadence claim, and names no reader from outside the project.
- No hypothesis, test, threshold, seed or day changed. PREREGISTRATION.md and the claimcheck folder were not touched.

## 2026-11-22 (Sun) · weekend count and fixes before release
**Found and fixed**
- The report and the 01 README said two of the crypto days fall on weekends. It is three, because 2026-11-01 is a Sunday. The 11-20 notebook entry called it a Saturday. Report and README fixed, correction in today's notebook entry, old lines kept.
- The report didn't say why the H2 placebo was rerun over 200 shuffles on the dev day. The single registered shuffle had missed zero under random, and the report now says so.
- The robustness sentence lumped three horizon misses together. Two are the same cost slope on 2026-10-01 under two rules and one is an H2 slope on 2026-11-01. They are now named one by one.
- The H5 bullet called 2026-10-01 the only place random decisions show a stale price effect, and pointed at Figure 2 for fixed price fill probability, which isn't plotted there. Both fixed.
- The Figure 1 caption said the y axes differ by two orders of magnitude. It is more than one, and the caption now gives the top of each panel from the results files.
- The root README said I write hypotheses down before I look at any results. H5 came after the dev look, so it now says test results. Its two ranges of signal cost now say roughly, since the lowest breadth day is a little under half a bp.
- The report's bottom line said my machine where the rest says this project's machine. Now the same.
- The Danait library note said the gap between its two names is not a liquidity effect. The paper only says the comparison is descriptive, so the note now says it can't be read as one.
- The broker latency script's docstring gave the old order size. It now says the smallest quantity that clears the 10 USD minimum, as the code does, and its line on the account secret says only that it is added outside the script.
- The cut run line in the report now says the json files came back byte identical and the saved arrays value for value, and that all of 2026-11-01 ran in stages.
- Older entries in this log and the notebook read as if another person had checked the work. Those were my own rereads in a separate sitting against my review checklist, and the entries now say so, including the 11-21 later entry. Nobody outside the project has read the work.
- Figures 4 and 5 now show their scale in the axis label, like Figure 3.

**Open**
- One line in the 11-18 Deviation of the preregistration still reads as if another person pointed out the null by construction problem. That was my own reread too. It is registered text, so it stays as written, and this line is the pointer.
- The report and README stay drafts until one last review before release.

**Checked**
- claimcheck has every tag agreeing with its file and no untagged numbers. The one new tag, the top of the random panel in Figure 1, is an existing field in a results file. Proposal tests pass.
- Figures 1 to 3 came out byte identical after the change, and Figures 4 and 5 the same on a second run. I looked at both at full size, and no label is clipped.
- No hypothesis, test, threshold, seed or day changed. PREREGISTRATION.md was not touched.

I did this check myself.

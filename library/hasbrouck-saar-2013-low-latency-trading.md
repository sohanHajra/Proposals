# Hasbrouck & Saar (2013), Low-latency trading

## Citation
Joel Hasbrouck and Gideon Saar (2013). *Low-latency trading*. Journal of Financial Markets 16(4):646-679. [doi:10.1016/j.finmar.2013.05.003](https://doi.org/10.1016/j.finmar.2013.05.003). Received January 16, 2013, accepted May 13, 2013, online May 22, 2013. Part of the journal's special issue on high frequency trading.

I read the published article, pages 646 to 679. Page numbers in this note are from it. I have no other version.

## Reading depth
I read it all the way through, every table and figure included. There is no appendix and no proof to follow. A few robustness tables (the alternative versions of their measure and the size and market share subsamples) are only "available from the authors" (footnotes 19 and 26, pp. 662 and 673), so I haven't seen them. Values I quote from Figures 1 to 3 are read off the charts and are approximate.

## Core idea
Public message data don't say who sent an order, but fast algorithms leave a trail. An order is cancelled and an order of the same size on the same side comes back within a few milliseconds, again and again. The authors link those messages into "strategic runs", count how many long runs are active in a stock over ten minutes, and use that as a stand in for high frequency activity. Then they ask whether more of it goes with better or worse market quality, in a calm month and in a falling one (pp. 648, 658 to 659).

## Setting and its assumptions
- NASDAQ in October 2007 (23 days, a flat market) and June 2008 (21 days, NASDAQ down about 8% after Bear Stearns). The 500 largest NASDAQ listed common stocks, cut to 351 and 399 stocks by a rule that drops a stock when more than a tenth of its ten minute intervals have fewer than 250 messages (p. 650).
- Every order on NASDAQ is a limit order. The data show displayed orders being added, cancelled and executed, and executions against hidden orders, but not hidden orders arriving or leaving (p. 649).
- A run is built by linking a cancellation to a later submission or execution on the same side, for the same size, within 100 ms. This is inferred, since nothing in the data ties two orders to one trader. It links about 60% of cancellations in 2007 and 54% in 2008, and 49% of the linked gaps are 0 or 1 ms (p. 658).
- Only runs of 10 messages or more count, a cutoff they call "somewhat arbitrary" (p. 659). The measure, RunsInProcess, weights each run by the share of the ten minutes it was active.
- They are open that it is a proxy. It may pick up fast agency algorithms and miss strategies that only send marketable orders (pp. 661 to 662).
- The instrument in the 2SLS work assumes that one algorithm doesn't trade hundreds of stocks at once, which they base on conversations with industry people and regulators (footnote 23, p. 667).

## Data
NASDAQ TotalView ITCH with millisecond timestamps, CRSP for the stock list, TAQ for spreads on other venues, and NASDAQ's HFT dataset of 120 stocks for a validation check (pp. 649 to 650, 662). In 2007 the median stock had 26,862 limit order submissions, 24,015 cancellations and 2,482 marketable executions a day, with a median quoted spread of $0.025 (Table 1, p. 651). They find about 46.0 million runs in 2007 and 67.1 million in 2008 (Table 3, p. 660).

## Methods
- Clock time periodicity. The millisecond within each second at which messages arrive, against a uniform line (Figure 1, p. 653).
- Speed of response. Hazard rates of same side submissions, same side cancellations and executions in the 50 ms after a quote improves, with every other event treated as censoring (Figure 2, p. 655).
- Validation. Correlation of RunsInProcess with four measures from the NASDAQ HFT dataset over 60 stocks in June 2008 (Table 4, p. 663).
- Market quality regressions on ten minute intervals, every series standardised within stock. Quoted spread, effective spread, displayed depth within 10 cents, and the high low range of the midquote in bps. Three specifications with lagged volume, then market return and its absolute value, then morning and afternoon dummies. Each one is estimated by OLS, by 2SLS with the average activity in unrelated stocks as the instrument, and as a two equation system that also instruments market quality with the effective spread on other venues. Driscoll and Kraay standard errors (pp. 664 to 672).

## Main results
- The fastest responders react to a better quote in about 2 to 3 ms, clearest for executions against the new quote (Figure 2, p. 654). They note that is faster than a light speed round trip from New York to Chicago (p. 678).
- Message arrivals bunch shortly after each second, at about 10 to 30 ms and about 150 ms, with a broad rise near 600 ms, in both months. They read this as agency algorithms checking the market on a clock (pp. 652 to 653).
- RunsInProcess correlates with the HFT dataset measures at 0.809 to 0.818 (Spearman) and 0.634 to 0.685 (Pearson) (Table 4, p. 663).
- More low latency activity goes with narrower quoted and effective spreads, more depth near the best prices and a smaller high low range, in both months and in every main specification (Tables 5 to 7). In the 2SLS version with lagged volume, the coefficient on RunsInProcess for the quoted spread is −0.682 in 2007 and −0.959 in 2008 (Table 6, p. 668).
- In money terms, one standard deviation more activity goes with spreads 26% lower in 2007 and 32% lower in 2008, depth 20% and 34% higher, and short term volatility 29% and 32% lower (p. 670). The effects are larger in the stressed month.
- Run stock by stock, almost every stock has a negative spread coefficient (Figure 3, p. 674).

## Limits
- It is about the market as a whole. They say themselves that spreads and depth measure liquidity, not what any investor pays to trade (footnote 22, p. 664). Nothing in it is the cost of one order arriving late.
- The activity measure is a proxy built from inferred links, with an arbitrary cutoff, and the robustness versions aren't shown.
- Causality rests on the instruments. The cross stock instrument fails if one algorithm trades many stocks at once, which they argue against from conversations, not data (footnote 23, p. 667).
- With time of day dummies, the plain OLS link to volatility disappears in both months (Table 5, Panel C, p. 666, coefficients −0.004 and −0.009 with p values 0.775 and 0.346). The text calls the OLS panels "generally similar" (p. 665). The 2SLS and system versions keep the link. In the 2SLS version with dummies the depth coefficient in 2008 is borderline (p value 0.051, Table 6, p. 668).
- Stock by stock, effective spread coefficients pile up around zero, and a good share of stocks sit in the bin at or just above zero (Figure 3, p. 674, read off the chart). The pooled effective spread result is weaker in the cross section than the quoted spread one.
- Two months on one venue, 2007 and 2008. They say the result does not cover flash crash type episodes (footnote 4, p. 648, and p. 677).
- Small slips. The Table 4 caption gives 60 × 819 as 49,410 where the product is 49,140. The Panel B run is said to last 78.5 s and to add 0.129 to the measure, but 78.5/600 is 0.131, and the times in Table 2 give about 77.4 s, which does match 0.129. The message counts given for Table 2 don't add up to the rows shown plus the "additional" messages (132 against 137 in Panel A, 138 against 142 in Panel B). The effective spread carries a factor of two in Table 1 and not on p. 663. None of this changes a direction.

## What it means for my work (my own inference)
- It confirms the two things my review row said and adds no evidence about the cost of delay for one order. I don't cite it for any number in my results.
- Their fastest responders sit at about 2 to 3 ms on NASDAQ in 2007 and 2008. That is old and a different venue, so it only says that the low end of my 1 to 500 ms grid has been where fast traders live for a long time. It is not a benchmark.
- On my LOBSTER day, cancelled orders in INTC and MSFT sit near the back of the queue, and I wrote down an untested guess that many of them join and leave quickly. Their Table 2 shows exactly that kind of behaviour, an algorithm posting at the touch and cancelling within about 10 ms, over and over (pp. 655 to 657). That makes the guess plausible. It does not test it.
- Their run linking (same size, same side, within 100 ms of a cancel) could be applied to my LOBSTER file to see how many back of queue cancels are followed by a resubmission. I logged that as an idea only.
- My decisions are drawn at random times, so the clock time bunching in their Figure 1 can't enter my replay through when decisions happen.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Background on what fast traders do on a millisecond scale and how public message data can show it. Not used as a benchmark for any of my numbers.

## Open questions
- Do back of queue cancellations on my LOBSTER day come back as same size resubmissions within 100 ms, as their runs would?
- Do their results hold in the alternative measures they didn't print?
- Would the clock time bunching show up in crypto message data, where many bots run on timers?

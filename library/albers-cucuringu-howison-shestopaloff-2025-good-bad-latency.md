# Albers, Cucuringu, Howison & Shestopaloff (2025), The good, the bad, and latency

## Citation
Jakob Albers, Mihai Cucuringu, Sam Howison and Alexander Y. Shestopaloff (2025). *The good, the bad, and latency: exploratory trading on Bybit and Binance*. Quantitative Finance 25(6):919-947. [doi:10.1080/14697688.2025.2515933](https://doi.org/10.1080/14697688.2025.2515933). Received 1 February 2024, accepted 29 May 2025, online 24 June 2025. Open access under CC BY NC ND 4.0.

I hold two copies. The published version, the open access copy held on the Oxford repository, is the one I read first, and page numbers for the main paper in this note are the journal's. The second is the SSRN copy (abstract 4677989), 54 pages, which carries the supplementary material on its pages 41 to 54. Its main text is laid out differently and numbered 1 to 40. Supplement references below are SSRN pages and say so.

## Reading depth
I read the whole published paper, tables and figures included. On 2026-11-18 I read the supplementary material all the way through, every table and figure. Where I give a value from a figure I read it off the chart and say it is approximate. I have not seen the journal's own supplementary file, only the one bound into the SSRN copy. Its section letters A to E match the ones the journal text points to, but I can't say the two files are word for word the same.

## Page numbers in the two copies
I checked the main paper references this note uses against both copies on 2026-11-18. The journal pages still match the published copy. The SSRN copy has the same tables with the same values, on other pages.

| Item | Journal page | SSRN page |
|---|---|---|
| Table 1, fees | 922 | 5 |
| Table 4, markout horizon | 928 | 14 |
| Pointer to Supplementary Material C | 929 | 17 |
| Send time of about 2 ms | 932 | 20 to 21 |
| Section 5.2, Binance run 14:02 to 15:00 UTC | 933 | 21 |
| Table 6, failure model | 935 | 25 |
| Table 7, slippage model | 943 | 29 |
| Conclusion, Binance run "a few hours" | 945 | 37 |
| Data on failed attempts needed | 946 | 39 |

## Core idea
A taker who reacts to the last book snapshot is aiming at a book that may have changed by the time the order lands. The authors sent millions of minimum size orders from a colocated server and compared each fill with what the last snapshot promised. The gap is not random. Orders that would have made money (positive short term markout) are the ones that fail to fill at the touch or slip, while orders that would have lost money almost always fill as expected (abstract, p. 919; Section 5.1, pp. 930 to 931). So a backtest that fills at the last seen price flatters exactly the trades a strategy wants.

## Setting and its assumptions
- Observational and live: The order stream follows no strategy. Whenever any of nine large Bitcoin markets traded more than 9,500 USD since the last trigger, they sent one buy and one sell market order plus two IOC orders priced so they could not fill, the latter only to confirm that IOC orders see the same latency (Section 3.1.2, pp. 924 to 925, Algorithm 1 on p. 926).
- An IOC order at the touch would have failed exactly when the matching market order filled worse than the snapshot price, so one market order gives both outcomes (equation 4, p. 925; Section 3.3.2, p. 927). With minimum size orders IOC and FOK are the same (p. 927).
- Minimum size orders only, 1 USD on Bybit, so slippage figures are a lower bound for larger orders (p. 937).
- Markouts are in event time, over the time it takes for ten more triggers, measured on the touch on the side traded, and before fees (equation 7, p. 927; p. 928).
- One realised latency per order. Latency is measured, not varied by design.
- They argue a synthetic version of the experiment would need a model of latency that depends on future returns, which they call not practically feasible (p. 923).

## Data
- Bybit BTC inverse perpetual, 19:43:04 UTC 14 April 2023 to 20:10:02 UTC 21 April 2023. 6,277,628 orders, half of them (3,138,814) market orders. Trading losses about 990 USD. Annualised volatility over the week 42.49% (Section 3.2, p. 927).
- Binance BTC inverse perpetual, 40,588 market orders from 14:02:39 to 15:00:00 UTC on 20 July 2023. Minimum order 100 USD (Section 5.2, p. 933).
- Bybit ETH inverse perpetual, 1,056,203 market orders from 10:12:01 UTC 9 October 2024 to 08:49:57 UTC 11 October 2024 (Section 5.2, p. 933).
- Their own order records with exchange timestamps, plus L2 snapshots of the top 50 levels arriving every 20 to 200 ms. No market by order data exists on either exchange (Section 3.1.4, p. 926).
- Bybit tick 0.5 USD, about 0.164 to 0.184 bps over the week (p. 930).

## Methods
- Failure rate against volatility: Correlations over windows from 1 s to 4 h (Table 5, p. 929) and failure rate by bins of 10 minute microprice volatility with an OLS line, R² 72.2% (Figure 2, pp. 929 to 930).
- Failure rate by markout bucket, one tick wide, dropping buckets with fewer than ten orders (Section 5.1, p. 930).
- A piecewise failure model: A constant for non positive markouts and a line for positive ones, fitted by weighted least squares with the order count as weight (equation 17, pp. 934 to 935).
- A line for average slippage against markout, also weighted by order count (Section 6.1, pp. 937 to 938).
- A toy model of a lottery among takers and cancelling makers after a public signal (equation 16, p. 932).
- Two backtests on Bybit, an order book imbalance rule and a lead lag rule against Binance, comparing naive, actual and simulated PnL. Models fitted on the first day and tested on the other six (Section 7, pp. 940 to 945).

## Main results
- Overall failure rate at the touch is 1.354% (p. 927).
- Failure rises with volatility (Table 5, Figure 2, pp. 928 to 930). The main text also says it rises with latency and falls with liquidity, with that evidence in the supplement (p. 929, p. 946). The supplement shows both as correlations, summarised below.
- The main result: Orders with negative markouts almost always fill. There is a jump in failure rate as the markout crosses zero, and failure rises steadily with the markout after that (Figure 3, p. 931). The jump is about 5% on Bybit BTC, 6% on Bybit ETH and 12% on Binance (p. 933).
- Failure model fits, from Table 6 (p. 935). Constant c is 0.00088, 0.00037 and 0.01407, intercept 0.0424, 0.1658 and 0.04691, slope per bp 0.02187, 0.07432 and 0.01790, for Bybit BTC, Binance BTC and Bybit ETH. The R² of 0.928, 0.637 and 0.895 is the weighted version on the positive side, and the paper says so.
- Slippage fits, from Table 7 (p. 943). Slope against markout is −0.0486 (Bybit BTC), −0.1526 (Binance BTC) and −0.0337 (Bybit ETH), intercept 0.0000 in all three, R² 0.659, 0.830 and 0.942. At a 2 bps markout that is about 0.1, 0.3 and 0.07 bps of slippage (p. 938). The fits are weighted least squares (p. 938). The paper does not say whether this R² is the weighted one.
- Markout horizon, Table 4 (p. 928). Mean 1.48 s, standard deviation 1.08 s, median 1.14 s, quartiles 0.65 s and 2.01 s, range 0.10 s to 5.00 s.
- Fees, Table 1 (p. 922), the best public tiers at the time of writing. Binance USDT margined perpetual taker 1.7 bps and maker 0.0. Bybit USDT margined taker 3.0, maker 0.0. Binance inverse taker 2.5, maker −1.0.
- From a colocated server, the time to send a message to the exchange averages about 2 ms with a standard deviation of about 1 ms (p. 932). Their own measurement in the supplement puts submission to matching at a median of 9.51 ms, so I'm not sure which quantity this sentence describes. See Supplementary Material B below.
- Slippage distributions peak at zero and grow a left tail as the markout rises, with a second peak near −2.2 bps at a 2 bps markout on Bybit (Section 6.2, pp. 938 to 940).
- Backtests: Moving from naive to actual PnL, the imbalance strategy loses about 17% of its average markout and the lead lag strategy about 30%, with the realised PnL measure falling much further (p. 944). Neither strategy beats the 3 bps Bybit taker fee (p. 943). The simulated adjustment recovers part of the gap but stays too optimistic (pp. 944 to 945).

## Supplementary material
Pages in this section are SSRN pages.

### A, the sample week (SSRN p. 41)
Annualised volatility is 53.02% from 8 daily returns, 42.49% from 170 hourly returns and 40.53% from 10,108 minute returns (Table A1). They call the week typical next to the 40% to 50% implied volatility of Bitcoin options.

### B, latency (SSRN pp. 42 to 44)
Bybit only, over all of about 6.3 million orders.
- Time inside the exchange, UpdatedTime minus CreatedTime (Table B1, p. 42). Median 2 ms, mean 1.94 ms, standard deviation 0.51 ms, 99th percentile 3 ms, 99.9th 6 ms, 99.999th 34.8 ms. Market and IOC orders show no difference.
- Their ping to Bybit's server is about 0.3 ms with little variation (p. 42).
- Their submission stamp to the exchange's matching stamp (Table B2, p. 43). Median 9.51 ms, mean 10.29 ms, standard deviation 3.28 ms, 1st percentile 7.64 ms, 99th 22.57 ms, 99.999th 93.57 ms.
- Matching to their receipt of the status update (Table B3, p. 43). Median 4.10 ms, mean 4.24 ms, standard deviation 1.64 ms, 99.999th 60.30 ms.
- Table B2 subtracts a stamp from their clock from a stamp on the exchange's clock. Neither the paper nor the supplement says how the two clocks were aligned, so I treat those numbers as approximate.
- The main text's send time of about 2 ms with a standard deviation of about 1 ms (p. 932) is closer to Table B1, the time inside the exchange, than to Table B2. On their own end to end measurement a colocated order takes about 10 ms to reach matching.

### C.1, failures cluster (SSRN pp. 44 to 45)
Failures of orders on the same side are autocorrelated. The correlation is 0.1473 at lag 1, 0.0675 at lag 2 and 0.0411 at lag 3, and settles near 0.015 to 0.017 from lag 8 to lag 15 (Table C1, p. 45). Across sides it is close to zero, slightly negative from lag 0 (−0.0132) to lag 6 and slightly positive after. One lag is about 418 ms on average, median 159 ms. In the whole week only three pairs had the buy and the sell fail together (p. 44).

### C.2, failures and latency (SSRN pp. 46 to 49)
This is the evidence behind the main text's latency claim. Latency 1 is their submission stamp to receipt of the API response. Latency 2 is CreatedTime to UpdatedTime on the exchange.
- They split the orders into bins of n consecutive orders and correlate the maximum latency in a bin with the failure rate in that bin (Table C2, p. 47). For bins of 50 to 12,800 orders the same bin correlation is 0.28 to 0.32 for Latency 1 and 0.25 to 0.34 for Latency 2. Using the previous bin's maximum gives 0.13 to 0.22 and 0.14 to 0.21. They took the maximum rather than the mean or median because it gave the highest correlations (p. 46).
- Failure rate by latency (Figure C3, p. 49, R² in the text on p. 48). They cut the range from the minimum to the 99.99th percentile into 100 equal bins and fit an OLS line, R² 0.869 for Latency 1 and 0.665 for Latency 2. Read off the chart, so approximate, Latency 1 failure rises from about 1% in the shortest bins to about 10% at 0.1 s and roughly 25% to 30% near 0.4 s. Latency 2 comes in 1 ms steps. Failure is near zero at 0 ms, about 1% at 1 and 2 ms, about 5% at 3 ms, about 10% at 4 ms and about 12% at 5 ms, then scattered between about 17% and 40% from 6 ms to about 19 ms.
- The line is fitted to bins, not orders, with no weights. Table B1 puts 99.9% of orders at or below 6 ms of Latency 2, so the steep part of Figure C3b rests on very few orders. No bin counts are given, and Latency 1 has no summary table at all.

### C.3, failures and book thinness (SSRN pp. 48 to 52)
Thinness is the distance in bps from the touch to the VWAP of a 400,000 USD order on the side the order takes (equations C8 to C10). They say results hold from 100,000 to 1,000,000 USD (p. 49). The correlation with failure rate is 0.18 for single orders and rises with bin size to 0.57 for bins of 6,400 orders. Lagged it is 0.15 to 0.26 (Table C3, p. 50). Failure rate by thinness bin (Figure C5, p. 52) has an OLS R² of about 0.723 (p. 51). Read off the chart, failure is near zero for the deepest books, about 5% at 2 bps, about 15% at 5 bps and noisy beyond 6 bps, where points run from about 7% to 30%.
- They say thin books usually come with high volatility and higher latency (p. 48). Nothing in the supplement separates the three. Every analysis takes one factor at a time.

### D, sample size (SSRN pp. 51 to 52)
They refit the failure model on 100 random runs of 40,000 consecutive Bybit orders (Table D1, p. 52). The constant c has mean 0.000291, standard deviation 0.0002785 and range 0 to 0.00152. The intercept α has mean 0.0461, standard deviation 0.0045, range 0.036 to 0.0766. The slope β has mean 0.0184, standard deviation 0.0032, range 0.0102 to 0.0338. The SEM row (1.3926×10⁻⁵, 0.0002, 0.0002) is the error of the mean across subsamples, not the error of one fit. Next to the full week values in Table 6 (c 0.00088, intercept 0.0424, slope 0.02187) the subsample mean of c is about a third. The paper doesn't comment on that.

### E, volatility (SSRN pp. 53 to 54)
400 subsamples of 40,000 orders, with volatility as the standard deviation of 500 ms microprice log returns. On my reading of Figure E1, c climbs steadily from near zero at the calmest subsamples (volatility about 20×10⁻⁶) to about 0.0015 at the most volatile (about 130×10⁻⁶). The slope β spreads from about 0.010 to 0.027 in calm subsamples and narrows to about 0.017 in volatile ones. The intercept α moves between about 0.036 and 0.055 with no pattern I can see. The authors call the rise in c slight and conclude there is no discernible dependence on volatility (pp. 53 to 54). In absolute terms c stays under 0.2%, so slight is fair. In relative terms it is a many fold change, and the summary sentence is stronger than their own plot of c.

### Cross references that don't match
The journal text says the bootstrap standard errors for Table 6 and the sample size analysis are in Supplementary Material E (p. 935). In this copy E is the volatility analysis and has no standard errors. The sample size analysis is D, and no standard error for the full week Table 6 fit appears anywhere in the supplement. D's spread across 40,000 order subsamples is the nearest thing. The journal text also says D shows that a few hours of data give comparable parameters (p. 943). D works in orders and doesn't say how many hours 40,000 orders cover.

## Limits
- Taker only. Nothing on passive orders or queue position.
- One realised latency per order, so latency is correlated with everything else going on. They relate outcomes to measured latency rather than set it.
- One week on Bybit, under an hour on Binance and two days on ETH. The conclusion describes the Binance run as "a few hours" (p. 945), while Section 5.2 gives just under one hour (p. 933). I go with Section 5.2.
- Minimum size orders, so no walking the book. Fees left out of markouts.
- Their explanation for differences across venues, different pools of takers and makers, is a hypothesis they say needs data nobody has, including failed attempts to take or cancel (p. 946).
- The toy model assumes a random arrival order among simultaneous messages. They argue for it from send time noise of about 1 ms against reaction differences of microseconds (p. 932), which is reasoning, not a measurement.
- The latency evidence in the supplement is correlation between measured latency and failure, one factor at a time. Slow moments are also busy, volatile and thin (SSRN pp. 43, 48), so the latency curve mixes delay with market state.

## What it means for my work (my own inference)
- Closest prior work for 01. They don't replay one decision across a set of delays. I do, on public data. That is what claim 1 in my literature review rests on, as far as my search went.
- My H1 materiality bar of 0.1 bps comes from their Table 7 slopes at a 2 bps markout. It is conditional on that markout, which I say next to the bar.
- Their main finding gave me H1b. On my dev day the split is partly built into how I defined the groups, so a match with their shape says little there. I logged that.
- Their markout horizon has a median of 1.14 s, close to my 1 s. Their markout is in event time and uses the touch on the side traded, so their numbers and mine are not the same quantity.
- A 0.1 bps latency cost is small next to a 1.7 bps taker fee, and I should say that plainly whenever I report H1.
- My replay keeps the real book path, which already contains other traders' reactions, but my order never races anyone. Their toy model is exactly the race my replay can't see.
- Their Binance arm is the BTC inverse perpetual over under an hour, not the USD margined contract I use. Not a direct benchmark.
- My grid starts at 1 ms. I first wrote that their colocated send time of about 2 ms (p. 932) puts the low end of my grid where colocated traders already are. Their own measurement from submission to matching has a median of 9.51 ms and a 1st percentile of 7.64 ms (Table B2, SSRN p. 43). On that number my 1 to 5 ms points sit below what their colocated stack saw end to end, 10 ms is near their median and 25 ms is near their 99th percentile. The clock caveat above applies.
- Their latency curve (Figure C3) and my delay grid are different things. Theirs sorts orders by the latency they happened to get, which comes bundled with load, volatility and thin books. Mine changes delay alone on the same decision and the same book path. So their curve can't be a benchmark for my slopes, and my replay can't show the part of their effect that comes from the state of the market.
- On my dev day the fixed price arm (H5) got cheaper with delay. The orders that had become marketable on arrival were cheap, because they took a touch that had moved toward them with nobody racing them. I haven't yet traced how much of the slope they carry. Their main result says those are the orders that fail in a live market, and the supplement adds that failures bunch together and come with slow, thin moments. So the first thing I suspect behind that negative slope is the race my replay leaves out. Their numbers are for IOC orders at the touch, though, so they don't tell me how big a correction would be.
- Their same side failures are correlated over a few lags of a few hundred ms each (Table C1). My block bootstrap uses 5 minute blocks, far longer than that.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Closest prior work, the source of the H1 materiality bar, the origin of H1b, and fee context.

## Open questions
- Their supplement answers my old question about latency only as correlation. How much of the latency curve is left once volatility and thinness are held fixed? They don't say.
- Which quantity is the 2 ms send time on p. 932?
- Is the R² in Table 7 weighted like the one in Table 6?
- Their predictions on numbers of takers and makers need data on failed attempts. Could LOBSTER order IDs test the maker side for Nasdaq names?
- Does the adverse selection split hold for passive orders, which they don't study? Yueshen's model says yes for the back of a queue, in expectation.

## Related notes
- [Moallemi & Sağlam (2013)](moallemi-saglam-2013-cost-of-latency.md). Their stale price cost is a different channel from the race studied here.
- [Yueshen (2026)](yueshen-2026-queuing-uncertainty.md).
- [Danait, Zamora & Boier (2026)](danait-zamora-boier-2026-same-book-different-fills.md).

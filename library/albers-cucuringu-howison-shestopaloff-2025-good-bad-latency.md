# Albers, Cucuringu, Howison & Shestopaloff (2025), The good, the bad, and latency

## Citation
Jakob Albers, Mihai Cucuringu, Sam Howison and Alexander Y. Shestopaloff (2025). *The good, the bad, and latency: exploratory trading on Bybit and Binance*. Quantitative Finance 25(6):919-947. [doi:10.1080/14697688.2025.2515933](https://doi.org/10.1080/14697688.2025.2515933). Received 1 February 2024, accepted 29 May 2025, online 24 June 2025. Open access under CC BY NC ND 4.0.

I read the published version, the open access copy held on the Oxford repository. Page numbers are the journal's.

## Reading depth
I read the whole paper, tables and figures included. I haven't read the supplementary material. That is where the latency data, the analysis of failures against latency and book liquidity, the bootstrap standard errors and the sample size checks live, so for those I only know what the main text says about them.

## Core idea
A taker who reacts to the last book snapshot is aiming at a book that may have changed by the time the order lands. The authors sent millions of minimum size orders from a colocated server and compared each fill with what the last snapshot promised. The gap is not random. Orders that would have made money (positive short term markout) are the ones that fail to fill at the touch or slip, while orders that would have lost money almost always fill as expected (abstract, p. 919; Section 5.1, pp. 930 to 931). So a backtest that fills at the last seen price flatters exactly the trades a strategy wants.

## Setting and its assumptions
- Observational and live. The order stream follows no strategy. Whenever any of nine large Bitcoin markets traded more than 9,500 USD since the last trigger, they sent one buy and one sell market order plus two IOC orders priced so they could not fill, the latter only to confirm that IOC orders see the same latency (Section 3.1.2, pp. 924 to 925, Algorithm 1 on p. 926).
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
- Failure rate against volatility. Correlations over windows from 1 s to 4 h (Table 5, p. 929) and failure rate by bins of 10 minute microprice volatility with an OLS line, R² 72.2% (Figure 2, pp. 929 to 930).
- Failure rate by markout bucket, one tick wide, dropping buckets with fewer than ten orders (Section 5.1, p. 930).
- A piecewise failure model. A constant for non positive markouts and a line for positive ones, fitted by weighted least squares with the order count as weight (equation 17, pp. 934 to 935).
- A line for average slippage against markout, also weighted by order count (Section 6.1, pp. 937 to 938).
- A toy model of a lottery among takers and cancelling makers after a public signal (equation 16, p. 932).
- Two backtests on Bybit, an order book imbalance rule and a lead lag rule against Binance, comparing naive, actual and simulated PnL. Models fitted on the first day and tested on the other six (Section 7, pp. 940 to 945).

## Main results
- Overall failure rate at the touch is 1.354% (p. 927).
- Failure rises with volatility (Table 5, Figure 2, pp. 928 to 930). The main text also says it rises with latency and falls with liquidity, with that evidence in the supplement (p. 929, p. 946).
- The main result. Orders with negative markouts almost always fill. There is a jump in failure rate as the markout crosses zero, and failure rises steadily with the markout after that (Figure 3, p. 931). The jump is about 5% on Bybit BTC, 6% on Bybit ETH and 12% on Binance (p. 933).
- Failure model fits, from Table 6 (p. 935). Constant c is 0.00088, 0.00037 and 0.01407, intercept 0.0424, 0.1658 and 0.04691, slope per bp 0.02187, 0.07432 and 0.01790, for Bybit BTC, Binance BTC and Bybit ETH. The R² of 0.928, 0.637 and 0.895 is the weighted version on the positive side, and the paper says so.
- Slippage fits, from Table 7 (p. 943). Slope against markout is −0.0486 (Bybit BTC), −0.1526 (Binance BTC) and −0.0337 (Bybit ETH), intercept 0.0000 in all three, R² 0.659, 0.830 and 0.942. At a 2 bps markout that is about 0.1, 0.3 and 0.07 bps of slippage (p. 938). The fits are weighted least squares (p. 938). The paper does not say whether this R² is the weighted one.
- Markout horizon, Table 4 (p. 928). Mean 1.48 s, standard deviation 1.08 s, median 1.14 s, quartiles 0.65 s and 2.01 s, range 0.10 s to 5.00 s.
- Fees, Table 1 (p. 922), the best public tiers at the time of writing. Binance USDT margined perpetual taker 1.7 bps and maker 0.0. Bybit USDT margined taker 3.0, maker 0.0. Binance inverse taker 2.5, maker −1.0.
- From a colocated server, the time to send a message to the exchange averages about 2 ms with a standard deviation of about 1 ms (p. 932).
- Slippage distributions peak at zero and grow a left tail as the markout rises, with a second peak near −2.2 bps at a 2 bps markout on Bybit (Section 6.2, pp. 938 to 940).
- Backtests. Moving from naive to actual PnL, the imbalance strategy loses about 17% of its average markout and the lead lag strategy about 30%, with the realised PnL measure falling much further (p. 944). Neither strategy beats the 3 bps Bybit taker fee (p. 943). The simulated adjustment recovers part of the gap but stays too optimistic (pp. 944 to 945).

## Limits
- Taker only. Nothing on passive orders or queue position.
- One realised latency per order, so latency is correlated with everything else going on. They relate outcomes to measured latency rather than set it.
- One week on Bybit, under an hour on Binance and two days on ETH. The conclusion describes the Binance run as "a few hours" (p. 945), while Section 5.2 gives just under one hour (p. 933). I go with Section 5.2.
- Minimum size orders, so no walking the book. Fees left out of markouts.
- Their explanation for differences across venues, different pools of takers and makers, is a hypothesis they say needs data nobody has, including failed attempts to take or cancel (p. 946).
- The toy model assumes a random arrival order among simultaneous messages. They argue for it from send time noise of about 1 ms against reaction differences of microseconds (p. 932), which is reasoning, not a measurement.

## What it means for my work (my own inference)
- Closest prior work for 01. They don't replay one decision across a set of delays. I do, on public data. That is what claim 1 in my literature review rests on, as far as my search went.
- My H1 materiality bar of 0.1 bps comes from their Table 7 slopes at a 2 bps markout. It is conditional on that markout, which I say next to the bar.
- Their main finding gave me H1b. On my dev day the split is partly built into how I defined the groups, so a match with their shape says little there. I logged that.
- Their markout horizon has a median of 1.14 s, close to my 1 s. Their markout is in event time and uses the touch on the side traded, so their numbers and mine are not the same quantity.
- A 0.1 bps latency cost is small next to a 1.7 bps taker fee, and I should say that plainly whenever I report H1.
- My replay keeps the real book path, which already contains other traders' reactions, but my order never races anyone. Their toy model is exactly the race my replay can't see.
- Their Binance arm is the BTC inverse perpetual over under an hour, not the USD margined contract I use. Not a direct benchmark.
- My grid starts at 1 ms. Their colocated send time of about 2 ms means the low end of my grid sits where colocated traders already are.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Closest prior work, the source of the H1 materiality bar, the origin of H1b, and fee context.

## Open questions
- What does their supplement show on failure against latency itself? I haven't read it, and it bears on my question more directly than anything in the main text.
- Is the R² in Table 7 weighted like the one in Table 6?
- Their predictions on numbers of takers and makers need data on failed attempts. Could LOBSTER order IDs test the maker side for Nasdaq names?
- Does the adverse selection split hold for passive orders, which they don't study? Yueshen's model says yes for the back of a queue, in expectation.

## Related notes
- [Moallemi & Sağlam (2013)](moallemi-saglam-2013-cost-of-latency.md). Their stale price cost is a different channel from the race studied here.
- [Yueshen (2026)](yueshen-2026-queuing-uncertainty.md).
- [Danait, Zamora & Boier (2026)](danait-zamora-boier-2026-same-book-different-fills.md).

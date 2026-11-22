# Budish, Cramton & Shim (2015), The High-Frequency Trading Arms Race

## Citation
Eric Budish, Peter Cramton and John Shim (2015). *The High-Frequency Trading Arms Race: Frequent Batch Auctions as a Market Design Response*. Quarterly Journal of Economics 130(4):1547-1621. [doi:10.1093/qje/qjv027](https://doi.org/10.1093/qje/qjv027).

Which version I read: The copy I have is the authors' manuscript dated February 3, 2015, 84 pages with the appendices. It is not the typeset journal article, so I have not seen the QJE page numbers. The volume, issue and pages above come from the DOI record I checked on 2026-11-14, not from this file. Page numbers in this note are the manuscript's own printed numbers (the title page is unnumbered, so page 1 is the start of the introduction). The manuscript mentions a separate earlier "working paper version" in a footnote (p. 46, footnote 40), which I have not seen.

Their short companion piece on how to run the auctions in practice has its own note, [budish-cramton-shim-2014-implementation-details-frequent-batch-auctions.md](budish-cramton-shim-2014-implementation-details-frequent-batch-auctions.md). I read it first for the big picture. Everything below was checked in the main paper itself.

## Reading depth
I read the whole manuscript, front to back, including Appendix A on other policy responses, Appendix B on the data work, Appendix C with the proofs and the calibration, and the reference list. I looked closely at every table and figure. I followed each proof in Appendix C for how it runs and what it assumes, but I did not rederive them. I have not read the published journal version, so if the journal text changed anything after February 2015 I would not know. Values I quote from charts are read by eye and are approximate. Values from tables and text are as printed.

## Core idea
In a continuous limit order book, every public piece of news starts a race. When a correlated price jumps, the firm whose quote is now stale sends a cancel, and every other fast firm sends an order to hit that quote. The exchange handles messages one at a time, so the quote's owner only escapes if her cancel beats all of the others. With N equally fast firms she is picked off with probability (N − 1)/N, even though everyone saw the news at the same moment (p. 4, Proposition 1 on p. 28). That cost goes into the spread and makes the book thin, and it pays for a speed race that does not shrink the prize (Propositions 3 to 5, pp. 34 to 35). Their fix is to run the market as uniform price auctions at short discrete intervals, about every 100 ms in their example (abstract, p. 1), which turns a race on speed into competition on price.

## Model and its assumptions
- One security x and a public signal y. The value of x is perfectly correlated with y and x can always be sold at y at no cost. So there is no inventory risk and no private information (pp. 22 to 23). The authors call this a best case for the continuous book.
- y moves by compound Poisson jumps at rate λ_jump, with a symmetric bounded jump size (p. 23).
- Investors arrive at Poisson rate λ_invest, need to buy or sell one unit, only take liquidity, and dislike delay (pp. 23 to 24).
- Trading firms are risk neutral, have no demand of their own, and at first have zero latency. Messages that arrive at the same instant are processed in random order, which they read as a tiny random latency (p. 24, footnote 18 on colocation).
- Prices are continuous, so there is no tick. Footnote 20 (p. 25) notes that with a tick firms would strictly prefer to be the liquidity provider and would race for the front of the queue too.
- The equilibrium concept is pure strategy static Nash (p. 25, footnote 19), so collusion is ruled out. Depth is one unit a side in the basic model. The multi unit version assumes investors trade their whole size at once, which the authors say is not optimal for them (p. 29).
- For the speed race, everyone sees y with latency δ_slow and firms can rent speed δ_fast at cost c_speed per unit time (pp. 32 to 33).
- For the batch auction, net investor demand in each interval is bounded (p. 43).

## Data
- Exchange direct feeds with millisecond stamps set by the exchange. CME Globex market depth for the E-mini S&P 500 future (ES) and NYSE ArcaBook for the SPDR S&P 500 ETF (SPY), January 2005 to December 2011, 1560 trading days after dropping roll days, half days, bad files and a three month NYSE gap in 2007 (pp. 11 to 12). Before November 2008 the CME stamps are to the centisecond (footnote 10).
- SPY comes from one venue. NYSE had a mean 25.9% share of SPY volume, so profits are scaled up by one over that share to estimate all venues (p. 16, footnote 15).
- Correlation checks on equity pairs and on the five largest S&P 500 stocks for 2011 (Table 3, p. 67).

## Methods
- Correlation of ES and SPY midpoint returns across return intervals from 1 ms to 60 s, with twelve variants (equal or size weighted mids, simple or averaged returns, New York, Chicago or neutral timing) in Table 2 (p. 65).
- A mechanical arbitrage detector (Appendix B.2.1, pp. 66 to 70). The level gap between the two is tracked with a moving average. An opportunity starts when the instantaneous spread crosses that average after paying the spread in both markets, needs at least 0.05 index points of profit, and ends when the market uncrosses. It is a "bad arb" if it does not reverse in time. Opportunities shorter than 4 ms, the one way light time between Chicago and New York, are dropped (9 ms before late 2008). A shadow book stops the strategy from counting liquidity twice.
- A game theory model solved for equilibrium, with comparative statics. Then the same model under batch auctions.
- A rough calibration of how long the batch interval needs to be (Appendix C.2.1, pp. 81 to 82).

## Main results
- Correlation breaks down at short horizons. The 2011 median ES and SPY return correlation is 0.1016 at 10 ms and 0.0080 at 1 ms (pp. 2, 13), and it is near zero at 1 ms under every variant in Table 2 (p. 65). In 2011 it reaches 0.50 at 142 ms, while in 2005 it took 2.6 s (p. 14). Equity pairs trading in the same building show the same pattern (Table 3, p. 67).
- The race got faster but the prize did not shrink. Median arbitrage duration fell from 97 ms in 2005 to 7 ms in 2011 (p. 17, Figure 5.3). Median profit per unit stayed near 0.08 index points apart from 2008 (Figure 5.4, p. 19). The number of opportunities per day moves with volatility. A regression of the daily count on the day's ES "distance traveled", the sum of absolute midpoint changes, has R² of 0.87 (p. 19).
- Size of the prize: Table 1 (p. 16) gives a mean of 801 opportunities a day (median 439), a mean of 13.83 ES lots each, mean profit $98.02 (median $17.05), and mean daily profit of $79k on NYSE data and $306k scaled to all venues. That is about $75M a year on average, from $35M in 2005 to $151M in 2008 (p. 21). 88.56% start with a move in ES. The authors argue this is an underestimate and only one of many such races (pp. 21 to 22), but decline to give a total.
- In the model, the liquidity provider is picked off with probability (N − 1)/N on any jump bigger than half the spread. The spread is set by λ_invest · s/2 = λ_jump · Pr(J > s/2) · E(J − s/2 | J > s/2), which does not depend on N (equation 6.3, p. 27; Proposition 1, p. 28). The spread is positive with no private information, inventory or search costs (Remark 1, p. 31), and spreads widen with size (Proposition 2, p. 30).
- With paid speed, the total prize, total speed spending and investors' spread cost are equal (Proposition 3, p. 34). Firms are in a prisoner's dilemma (Proposition 4, p. 35). The prize rises with jump frequency and with more spread out jumps, and does not depend on the cost of speed or on how fast the fast firms are (Proposition 5, p. 35). They read this as matching the data, durations fall while the prize stays put.
- Prices are efficient in time but not in volume. A positive share of trade happens at quotes everyone fast knows are stale (Proposition 6, pp. 36 to 37).
- Batch auctions: A δ speed edge only matters for jumps in a window of length δ at the end of an interval of length τ, so its value falls by δ/τ (pp. 40 to 41, Figure 7.1). With the same news seen by many, the auction makes them compete on price, so a symmetrically informed quote is never picked off (Proposition 7, p. 42). With exogenous entry the spread goes to zero and depth to the maximum needed for any τ > 0 (Proposition 8, p. 44). With paid speed, a long enough interval removes the speed race, at the cost of investors waiting up to τ (Proposition 9, p. 46). They do not claim a net welfare result for that case.
- Interval length: The calibration gives lower bounds of about 16 ms and 400 ms under two readings of δ, and "on the order of 10ms or 100ms" overall, which they call "no more than an extremely rough sense of magnitudes" (pp. 47 to 48, 81 to 82). The paper says it does not pick an optimal interval (p. 6, footnote 6).
- Other responses (Appendix A): A transaction tax cuts the race but raises investors' all in costs, and would need about 10 bps to remove 90% of the ES and SPY prize (pp. 58 to 59). Minimum resting times make sniping worse (p. 60). Random delays leave the pick off probability near (N − 1)/N and invite message spam (Proposition 11, pp. 60 to 61). An asymmetric delay on marketable orders, as at IEX and TMX, stops sniping in the model but not the race for the front of the queue at a tick (pp. 61 to 63).

## Limits
- The empirical part measures the profit of a hypothetical mechanical strategy on one pair of markets. It does not observe who won races or what stale quotes actually lost. The cost to liquidity providers comes from the model.
- SPY is one venue scaled up by market share, and the CME public feed may lag private fills by several ms, which the authors think makes them miss the largest opportunities (p. 21).
- The model is deliberately bare (p. 51). No private information, no inventory risk, no tick in the main model, unit depth, inelastic investors, random tie breaking. Results such as "never sniped" in batch auctions are an artefact of the latency model, as footnote 36 says (p. 41). With small random latency the exposed share of an interval is ε/(2τ).
- The calibration rests on industry figures, GETCO's 2012 filing and the assumption that ES and SPY is 1% of the whole race. The printed product in Appendix C.2.1, "2 ∗ 200,000 ∗ 0.01 ∗ 40,000 = 160,000 annualized" (p. 81), works out to 160,000,000. The 16 ms and 400 ms bounds they state follow from 160 million, so I take the printed 160,000 as a slip in units. It does not change their numbers.
- They state openly that welfare, the optimal interval, competition between exchanges and market stability are left for future work (pp. 46, 51).
- The paper argues for a design. Its framing is in favour of batch auctions throughout, and the empirical section is chosen to motivate that. That is fine for what it is, but I should not read its facts as a neutral survey of how latency costs are spread.

## What it means for my work (my own inference)
- Their cost falls on a resting quote that cannot cancel in time after a public jump. In my replay only the fixed price passive arm (H5) holds a price that can go stale. The primary taker and passive legs read the book again on arrival, so in their terms those orders are never the stale quote.
- The replay has no race in it, and their model says that matters most exactly in the moments RQ3 looks at. The recorded book already contains the race other traders ran. A replay order sent 1 ms after a jump is treated as if it took whatever stale liquidity was still printed 1 ms later, while in their model it would be one of N racers and would usually lose. So in jump moments my 1 ms baseline is probably too kind, and that pushes the measured cost of extra delay up, not down. If H3 comes out above zero on the test days, part of that could be this. I will say so when I report it, and not read a positive H3 as the race cost they describe.
- RQ3 splits by realised volatility over the 10 s before the decision. Their mechanism is a jump in a related price. A backward volatility window mixes jump moments with merely busy ones, so H3 is a loose stand in for their idea. That does not change H3, which is registered as it is.
- Their numbers do not carry over. They are for a 2011 futures and ETF pair across two cities, with median arbitrage durations of 7 ms that year. I have no measure of how long stale prices last on Binance BTCUSDT.
- Their race for the front of the queue at a coarse tick (p. 22, p. 25 footnote 20, pp. 61 to 63) is the setting of my passive leg, since BTCUSDT sits at a one tick spread most of the time. They name it and do not model it. Yueshen (2026) and Moallemi (2014) are the closer references for that part.
- My replay uses one venue. Their main facts come from staleness across venues, which my data cannot show.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Background for RQ3, the idea that latency cost sits in race moments. It is a motivation, not a benchmark for any number of mine.

## Open questions
- Did the journal version change any number or result from this February 2015 manuscript? I would need the published PDF to check.
- How long do stale prices last on BTCUSDT perpetuals, measured the way they measure ES and SPY durations? Their method would need a second, faster leading market.
- How big is the replay's missing race in jump moments? A rough bound might come from how often the recorded book shows stale liquidity vanishing within a few ms after a large mid move. That is an idea, not something I have done.
- How do their facts hold up under later direct measurement of races? I have not read that work and do not cite it.

## Related notes
- [Their 2014 companion on implementation](budish-cramton-shim-2014-implementation-details-frequent-batch-auctions.md)
- [Moallemi & Sağlam (2013)](moallemi-saglam-2013-cost-of-latency.md), cost of latency from stale prices for one trader with no race
- [Yueshen (2026)](yueshen-2026-queuing-uncertainty.md), random queue position among makers posting at the same time
- [Albers et al. (2025)](albers-cucuringu-howison-shestopaloff-2025-good-bad-latency.md), live evidence that orders which would have made money fail more often

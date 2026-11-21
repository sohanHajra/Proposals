# Cartea & Sánchez-Betancourt (2023), Optimal execution with stochastic delay

## Citation
Álvaro Cartea and Leandro Sánchez-Betancourt (2023). *Optimal execution with stochastic delay*. Finance and Stochastics 27(1):1-47. [doi:10.1007/s00780-022-00491-w](https://doi.org/10.1007/s00780-022-00491-w). Received June 1, 2022, accepted July 6, 2022, online December 1, 2022. Open access.

The copy I read is the authors' preprint on SSRN (abstract 3812324), 36 pages, marked as forthcoming in Finance and Stochastics and dated July 8, 2022. I have not read the typeset journal version, so every page number in this note is the preprint's and won't match the journal's pages 1 to 47.

## Reading depth
I read the preprint all the way through, every table and both figures included, and the two appendices. I followed the proofs in Appendix A to see how they go and what they rest on, but I did not rederive them. Several of them are only sketched in the paper itself, which I say below. Table values are as printed. Where I give a ratio or a share, I worked it out myself from the tables.

## Core idea
A trader taking liquidity never knows exactly how long her order will take to reach the book. During that time the best quote can flicker, meaning it jumps a few ticks for a moment and comes back. She uses marketable limit orders, which take liquidity at once but cancel if the limit can't be met. The paper treats latency as random and asks how she should choose when to send each order and what limit to put on it while working a large order (pp. 1 to 3).

The answer depends on patience. An impatient trader sets limits below the bid so her sells fill. A patient one mostly sends speculative orders priced above the fundamental bid. They fill only if a flicker moves the price her way, and she retries when they miss. A fast patient trader uses her speed to send more of these, not to finish early (pp. 1, 19 to 21).

## Model and its assumptions
- The best bid is a fundamental bid plus a flicker. Only the flicker at the moment the exchange processes her order matters. Flickers are independent draws from a law with an atom at zero and exponential tails for improvement and slippage (equations 2 and 3, pp. 9 to 10). The authors say any law with two moment conditions would work.
- Latency is exponential, so it is memoryless and independent of everything else (Lemma 1, p. 10). The proofs lean on that memoryless property (p. 26). Other delay distributions are left open (p. 24).
- She can have at most one order pending. While it is in flight she can't send another (p. 11). More than one pending order under random latency is also left open (p. 24).
- Child orders are one unit and always find enough size at the best quote, so in the model they never walk the book and have no temporary impact (p. 12). A filled order moves the fundamental bid down by a fixed permanent impact. A missed order has no impact because nobody else sees it (pp. 2, 12).
- The fill rule is a step function smoothed into a sigmoid so the maths stays continuous (p. 11).
- The objective is terminal cash, a terminal cost of walking the book for leftover inventory, a running penalty on inventory for urgency, and a fee on each fill (equations 10 and 11, p. 14).
- The value function is shown to be the unique viscosity solution of the dynamic programming equation (Theorem 3, p. 31). This assumes a linear growth bound on the value function rather than proving it (equation A.14, p. 30). The comparison result is given as a list of steps borrowed from Bruder and Pham (2009) rather than a full proof (pp. 30 to 31), and part of the dynamic programming proof is left out (footnote 9, p. 15). The authors say there is no verification theorem, so optimality of the strategy is not proved. They take its outperformance of the benchmarks as support (p. 32). Convergence of the finite difference scheme isn't studied (footnote 10, p. 15).

## Data
- Proprietary LMAX Exchange FX data, ten currency pairs, September 1, 2019 to February 29, 2020, stamped to the microsecond. They have the size at the best bid and ask but nothing deeper in the book, every taker order with its type, trader ID, limit and outcome, and the average price paid (p. 5).
- Submission times and the quote the trader saw when deciding are not in the data. Only the exchange processing time is (p. 7).
- In every pair, marketable limit orders carry more volume than any other taker order type (Table 1, p. 6). In EUR/USD, 41.0% of them filled in full, 1.9% in part and 57.1% missed. They made up 56.9% of volume against 13.5% for market orders (p. 3).
- Taker orders rarely need more than the size shown at the best quote. Between 0.1% and 8.8% of trades exceed it, depending on the pair and the measure (Table 3, p. 9).
- The strategy tests use EUR/USD only. Parameters come from August 2019 and the test runs from September 2019 to February 2020, 128 days (pp. 16, 18). News times come from the FXStreet calendar, 117 high impact releases (p. 22).

## Methods
- The fundamental bid is taken as the last bid at which the spread was under 11 ticks (p. 16).
- The flicker law is fitted by simulating over a million limit orders priced at the fundamental bid through the August book, with exponential latency of mean 10, 30, 60 or 90 ms, and taking maximum likelihood estimates (p. 17).
- The strategy is solved numerically on a grid with Monte Carlo for the expectations (Appendix A.3, p. 33).
- Testing is a replay through the recorded LMAX top of book. Prices and flickers are real. The only thing simulated is the order's latency, drawn 100 times for each six second window, so 1,280,000 runs for each of three ten minute windows a day (pp. 16, 18). Permanent impact is set to zero and the orders don't change the book (p. 17, footnote 11).
- The task is to sell €5 million (ten lots of €500,000) within six seconds, with no urgency penalty in the main case. Fees are 3 USD per million (pp. 16 to 17).
- The strategy is compared with the same problem solved for a fixed latency, with zero latency market orders, with TWAP, and with one market order at the start with enough size assumed (p. 15). The measure is the difference in mean terminal cash in USD per million EUR (equation 17, p. 18).

## Main results
- Against the benchmarks the strategy gains a few USD per million EUR, about the size of the fees. At 9 am with 30 ms expected latency it beats TWAP by 3.80, zero latency market orders by 3.40 and the one order benchmark by 2.57 (Table 5, p. 19).
- The gain shrinks as latency grows. Against TWAP it is 5.14 at 10 ms, 3.80 at 30, 3.09 at 60 and 2.65 at 90 (Table 5). Slower traders get fewer retries and end with more inventory to dump at the end (pp. 19 to 20).
- The random latency and fixed latency strategies can't be told apart statistically. Their limits round to the same tick in most simulations, and the gap is always under 0.5 USD per million (footnote 14, p. 18).
- The patient strategy sends about 195 orders in six seconds, 188 of them speculative, and fills about 10 (Table 6, p. 20). So about 95% of its orders miss, by my count from the table. With a high urgency penalty it sends about 10 orders priced to fill, misses about 2%, and its edge over TWAP falls to 0.79 (p. 21, Table 7).
- When the trader assumes 30 ms but her real expected latency is 20, 30 or 40 ms, the gain over TWAP is 4.20, 3.79 and 3.50 (Table 9, p. 22).
- The gain is smallest at 7 pm, the quietest window (Table 8, p. 22). Around news it is much larger. Within one minute of a release it beats TWAP by 29.45 and zero latency market orders by 36.31 (Table 10, p. 23). The fitted flicker law shows why. Within a minute of news the chance of slippage at the best bid goes from 0.057 to 0.229 and its mean size grows about sixfold, while the chance of a price improvement only goes from 0.042 to 0.056 (Table 11, p. 23).
- Results hold across spread filters of 7 to 13 ticks or none, and the gains move by at most 0.4 USD per million when volatility is set anywhere from 1 to 3 × 10⁻⁴ instead of the estimate (Table 12 and p. 24).

## Limits
- One venue, one pair for the tests, proprietary data. Nothing can be rerun.
- The replay can't show impact or how others would react to the orders. Permanent impact is set to zero (pp. 16 to 17).
- The model assumes orders never walk the book. In the replay they do when the limit allows, though the data have no depth beyond the best quote, and the paper doesn't say exactly how that walking is priced (pp. 5, 16).
- The claim that the results are robust to model and parameter misspecification (p. 16) goes further than shown. Only the price path is real. The strategy itself comes from the fitted model.
- Optimality is not proved, and outperforming TWAP doesn't show it.
- The significance tests treat 1,280,000 runs as independent, but they share 128 days of real price paths with 100 latency draws each. My reading is that the p values are too small. Not rejecting that the random and fixed latency strategies perform the same is also not the same as showing they do.
- The spread filter used throughout, 11 ticks, is the one where the gain peaks (Table 12). I don't read that as tuning, but it is the best case.
- Some details disagree. Flickers at the bid are said to be mostly negative on pp. 6 and 8 and mostly positive on p. 16. Table 3 isn't monotone where it has to be. For AUD/JPY, 1.5% of trades exceed the time weighted size of 88/90 lots but only 0.1% exceed the mode of 50. Table 4 labels the flicker rates but prints what look like their means. The text promises results for urgency 5 × 10⁻⁵ and gives them for 10⁻⁴ (p. 21). Table 12 at 11 ticks doesn't match Table 5 for the same window and latency. None of this changes the direction of a result.

## What it means for my work (my own inference)
- Its Section 4 is a second published replay where only the timing of the order changes and the price path is the recorded one. Unlike the clones in Cartea and Sánchez-Betancourt (2021), the order really lands later here. Table 9 keeps one strategy and changes its true latency to 20, 30 and 40 ms. It still isn't my design. Latency is random, the strategy retries, so later orders depend on earlier fills and the same decision isn't replayed at each delay, the outcome is cash against benchmarks rather than shortfall per decision, and the data are proprietary. My claim of a paired design on public data stands, but this paper now sits next to the 2021 one as a near case.
- In their setting, treating latency as fixed lost almost nothing against treating it as random. My grid uses fixed delays, so that is mildly reassuring. It is about the value of an optimised strategy, though, not the cost curve of a single decision, so I don't lean on it.
- The flicker picture matters for my taker leg. My order pays the touch it finds on arrival, and at millisecond scale that touch is sometimes a flicker that widens the spread for a moment. My registered cost uses the raw arrival touch and stays that way. How often my arrivals land on such moments is a fair thing to describe later.
- Table 5 is a latency cost, the value of a patient limit order strategy falling as it gets slower, but its value comes from retries of speculative orders. It isn't comparable with H1, where random decisions reprice on arrival.
- The news result fits the picture that latency risk sits in event moments, like the jumps in Budish, Cramton and Shim (2015). My H3 split on past 10 s volatility is a loose stand in for that and came out null on the test days. This paper doesn't count as evidence for or against H3.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Background on random latency and marketable limit orders, a second near precedent for replaying the recorded book with only latency changed, and the flicker picture of the top of book at millisecond scale. Not a benchmark for any of my numbers.

## Open questions
- How is walking the book priced in the replay when the data hold only the best quotes?
- Would the significance of the gains survive a test that treats each day, rather than each run, as the unit?
- Are the gains near news mostly from avoiding slippage rather than from filled speculative orders? Table 11 suggests slippage is what changes most, while the text credits the speculative fills.
- Do the flicker laws look the same on a crypto perpetual book like Binance BTCUSDT? I'd need the same spread filter fixed in advance to say.
- I haven't read the typeset journal version. If anything changed after July 2022, this note doesn't know.

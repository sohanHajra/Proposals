# Cartea & Sánchez-Betancourt (2021), The Shadow Price of Latency

## Citation
Álvaro Cartea and Leandro Sánchez-Betancourt (2021). *The Shadow Price of Latency: Improving Intraday Fill Ratios in Foreign Exchange Markets*. SIAM Journal on Financial Mathematics 12(1):254-294. [doi:10.1137/19M1258888](https://doi.org/10.1137/19M1258888). Received April 30, 2019, revised October 26, 2020, published March 1, 2021.

I read the typeset journal article, pages 254 to 294. Page numbers in this note are the journal's. The appendices with the proofs and the robustness tables are part of the article, and I know of no separate supplement.

## Reading depth
I read it all the way through, every table and figure included, and the appendices too. I followed the proofs in Appendix A to see how each step goes and what it rests on, but I did not rederive them. Values I quote from figures are read off the charts, so treat them as approximate. Table values are as printed, and I checked a few of the sums myself.

## Core idea
A trader who takes liquidity with a price limit aims at the best quote she saw. By the time her order lands the quote may have moved. If it moved away she misses, and if it moved toward her she gets a better price. She can either pay to be faster or let each order walk the book a little (the "discretion"). The paper builds a rule that sets that discretion order by order, then asks what reaching the same fill ratio by cutting latency would be worth. That money figure is the shadow price of latency (pp. 254 to 256).

## Model and its assumptions
- Latency is defined broadly, from the moment the exchange streams the quote to the moment it processes the order, decision time included (pp. 257 to 258).
- Orders are fill or kill or immediate or cancel with a limit price. Discretion is the gap between the limit and the best quote the trader saw (p. 260).
- Volatility of the microprice follows a mean reverting process, with an Ornstein Uhlenbeck and a Heston version as checks (p. 262).
- The trader's rolling fill ratio is itself modelled as mean reverting. Volatility above its long run level pushes it down and discretion pushes it up, linearly and without a bound (equations 9 and 10, pp. 262 to 263). This is a reduced form for the fill ratio, not a model of the book or the queue.
- She penalises discretion and distance from a target fill ratio quadratically and guards against a wrong fill model with an entropy penalty (pp. 264 to 265). The result is a closed form feedback rule. Discretion rises when the fill ratio is below target and when volatility is above its mean (Theorem 1, p. 266, and p. 267).
- The noise in the fill ratio is independent of the noise in volatility. With correlation the closed form survives for two of the three volatility models (footnote 5, p. 263). The main result needs the ambiguity aversion to stay below a stated bound (Theorem 1).

## Data
- Proprietary LMAX Exchange data for two liquidity takers in USD/JPY, December 2016 to March 2017. T1 sends fill or kill orders and T2 immediate or cancel orders, both with zero discretion. Neither posts limit orders (p. 260).
- For each order they have side, exchange processing time, size, type, limit and fills. The send time and decision time are not known (p. 276). The book is available at millisecond intervals, with over 63 million best quote updates in the period (p. 260).
- T1 made 116,912 attempts and T2 68,129 (Table 1, p. 260). After warm up the test sample is 110,458 for T1 and 63,268 for T2 (p. 271). One tick is 0.001 JPY.

## Methods
- Volatility is the standard deviation of 500 ms log returns of the microprice over a 10 minute rolling window (p. 261). The fill window of 50 orders and the 10 minute volatility window were chosen because they made the daily correlation between fill ratio and volatility most negative (footnote 4, p. 261).
- Parameters are estimated each day by least squares on the discretised equations. The effect of discretion is estimated by replaying the day's orders through the recorded book with fixed discretion of 0 to 5 ticks (pp. 267 to 268). Each day uses the previous day's estimates (p. 271).
- Performance is a counterfactual replay through the recorded book. The cost of the extra fills is set against sending a market order with no limit 20 ms or 100 ms after the exchange received the missed order (p. 271).
- For the shadow price, 51 clones of T1 send the same orders at the same arrival times, but each aims at the quote as it stood 0 to 50 ms earlier. That maps latency to fill ratio day by day (pp. 276 to 278).

## Main results
- Misses rise with volatility. Across pooled volatility quartiles T1's fill rate goes 94.7%, 92.7%, 90.8%, 87.5% (Table 5, p. 273) and T2's 94.5%, 92.0%, 89.9%, 84.3% (Table 8, p. 275). The top quartile holds 36.5% of T1's misses and 40.0% of T2's (p. 255, and it matches the tables).
- With the rule and a target discretion of zero, T1 would have filled 8,318 of its 9,483 misses at 1.76 ticks on average. A market order 20 ms or 100 ms later would have cost 2.01 or 2.58 ticks on those same trades (Table 4, p. 272). For T2 the numbers are 6,283 of 7,038 at 1.24 ticks against 2.82 and 2.75 (Table 7, p. 275).
- In the top volatility quartile the gap is wider. T1 1.88 ticks against 3.04 for the 100 ms retry, T2 1.86 against 3.31 (Tables 5 and 8).
- Implied latency: T1's naive orders fill as if her latency were 20.02 ms on average (median 18), and the rule's fills match a latency of about 2.34 ms (Table 9, p. 278). On one day the map runs from 100% at 0 ms to 89% at 50 ms (p. 277).
- Shadow price: T1 would pay about 3 million JPY (about 30,000 USD) over the period to go from 20.02 ms to 2.34 ms, with about 5 million JPY as an upper bound (Table 10, p. 279). The authors say this is below what colocation and hardware cost, on the word of market participants (p. 279).
- Results barely move with the horizon, the volatility model, or shocks of 20% to the volatility parameters (Tables 11 to 18, pp. 290 to 293).

## Limits
- Two traders, one currency pair, four months, one venue, all proprietary. Nothing can be rerun.
- Every result is a replay through the recorded book. The bigger orders change nothing in it and nobody reacts to them.
- The fill ratio model is reduced form and linear in discretion. The volatility effect on fills came out negative on 12 of 83 days (Table 16, p. 292), and the windows were picked to make the volatility link strongest (footnote 4).
- The comparison with retries looks only at trades that were missed, which are the ones where the book had already moved away.
- Latency in the clones is fixed, and only the quote they aim at changes. Arrival time stays the same. The authors note that a faster T1 might have traded differently (p. 277).
- Some numbers in the paper disagree with each other. On January 5, 2017 the rule's fill ratio is 99.17% on p. 269 and 98.73% on p. 277, and T1's implied latency that day is 27 ms on p. 277 but 22 ms on p. 279. The text gives T1's mean daily fill as 91.0% where Table 9 says 91.9%. Tables 13 and 14 disagree on extra fills for two volatility models, and Table 17 repeats each row twice. None of this changes the direction of any result.
- The conclusion says most misses happen when volatility is high. That holds for the top half (about 63% and 66% of misses by my count from Tables 5 and 8), not for the top quartile.

## What it means for my work (my own inference)
- It is the closest published support for the direction of H3, on the fill side. Misses rise steadily with volatility. But it is observational and pooled over days, the windows were tuned to the link, and it measures fill rates of orders with no discretion, not the shortfall of an order that walks the book.
- The closest thing in it to my delay grid is the retry cost at 20 ms against 100 ms by volatility quartile. For T1 the extra 80 ms costs more as volatility rises (0.25 ticks in the lowest quartile, 0.85 in the highest, my subtraction from Table 5). For T2 it does not. The 100 ms retry is cheaper than the 20 ms one in three quartiles and overall (Tables 7 and 8). So the paper gives mixed evidence on exactly what H3 tests, and I don't cite it as support for H3 itself.
- The clone exercise in Section 7 replays the same orders across a controlled set of latencies, 0 to 50 ms, which is close to my paired design. It differs in that the data are proprietary, it measures fill ratio and not shortfall, and latency changes which quote is targeted rather than when the order lands. My review used to say I had found no replay of the same decision across a delay grid. That is still true for public data, but this paper should be named as the nearest case, and I have done that.
- Their naive trader's implied latency of about 18 to 20 ms sits inside my grid of 1 to 500 ms, which is a useful sense of scale for a real taker in a fast FX book.
- Their volatility is a 10 minute window of 500 ms microprice returns. Mine is 10 s of 100 ms mid changes, and my high group is a within day top fifth. The two splits are not the same thing.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Background for RQ3 (missed fills rise with volatility), the nearest precedent for the paired delay replay, and a sense of a real taker's latency. Not a benchmark for any of my numbers.

## Open questions
- Why does T2's retry cost fall from 20 ms to 100 ms when T1's rises? Order size, the partial fills of immediate or cancel orders, or something in when T2 trades?
- How much of the volatility link survives windows that were fixed in advance rather than picked for the strongest correlation?
- Does the T1 count in Table 1 (106,878 fills of 116,912, which is 91.4%) use a different fill measure from the 90.78% printed beside it?
- Cartea and Sánchez-Betancourt (2023) treat latency as random. I have read it since, see [its note](cartea-sanchez-betancourt-2023-execution-stochastic-delay.md). In that setting a strategy built for fixed latency did about as well as one built for random latency.

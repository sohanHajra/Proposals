# Moallemi & Sağlam (2013), The Cost of Latency in High-Frequency Trading

## Citation
Ciamac C. Moallemi and Mehmet Sağlam (2013). *OR Forum—The Cost of Latency in High-Frequency Trading*. Operations Research 61(5):1070-1086. [doi:10.1287/opre.2013.1165](https://doi.org/10.1287/opre.2013.1165). Received July 2011, accepted December 2012, online April 25, 2013.

Two versions read.
- The published article, pages 1070 to 1086. Page numbers in this note are from it.
- The working paper dated February 5, 2013, 55 pages. Its first 33 pages are the same paper. The last 22 pages are the electronic companion with the proofs (Appendices A to D), which the published file I hold does not contain. Where a point exists only there, I say "working paper" and give its PDF page.

## Reading depth
I read both versions all the way through. Everything I cite comes from the published article, and I went to the working paper for the proofs. I followed the proofs in Appendices A to C closely enough to see how each argument runs and what it leans on, but I did not rederive them line by line. Appendix D states the jump results without proof. Figure values I quote are read off the charts, so treat them as approximate.

## Core idea
A trader who works a limit order needs to keep its price in step with the market. With latency, the price she picks now only reaches the book later, on information that has gone stale. She protects herself by pricing a little worse, and that safety margin costs money. The paper puts a value on that cost for one trader, holding everything else fixed. Its answer is a closed form that depends on one ratio, the standard deviation of the price over the latency interval divided by the bid offer spread (p. 1072, Corollary 1 on p. 1078).

## Model and its assumptions
- One risk neutral, uninformed trader must sell one share within a short horizon T, on the order of seconds, and is forced to sell at the bid at T (p. 1073). One share stands for one atomic child order of a larger parent order (p. 1074).
- The bid follows an additive Brownian motion. Impatient buyers arrive at random, independent of the price, and each pays up to the spread δ above the bid (p. 1074). With no latency the best policy is to peg the order at bid plus δ, worth δ(1 − e^(−μT)), which the paper calls the cost of immediacy (Lemma 1, p. 1075).
- With latency Δt the trader sees prices at once but her orders reach the market Δt later. She resets the price once per slot of length Δt. A stale order that the bid crosses fills at the bid (p. 1076).
- The authors say what is left out. Only the stale information channel is modelled. Races against other traders, time priority, queues and price discreteness are not (p. 1071, p. 1085). The model has no other agents reacting (p. 1075). In their words it "exaggerates the gains to be earned by placing limit orders rather than market orders, because we do not include adverse selection costs incurred by limit orders" (p. 1075).
- The theorems hold for Δt "sufficiently small", a threshold the proofs do not put a number on (working paper pp. 38 to 51). The closed form also needs the spread to be large next to the price move over Δt, since its log term must stay positive.

## Data
- One stock day. Goldman Sachs on January 4, 2010, from TAQ through WRDS, NYSE trades and quotes in regular hours. Spread $0.058 (3.4 basis points), 12.03 market orders per minute, daily volatility $1.92 (about 17.9% a year), horizon 10 seconds (p. 1080).
- Daily volatility and average spread estimates for all NYSE common stocks from June 1, 1995 to December 31, 2005, taken from Aït-Sahalia and Yu (2009), not computed by the authors. A stock day is kept when it has more than 200 trades. Between 61 and 1,278 stocks a day, 653 on average (p. 1082).
- No order book data and no order level data. The authors call the empirical part "a first-order study to obtain a rough calibration" (p. 1080) and note that the volatility estimate filters out microstructure noise and so understates what a trader with a one second horizon faces (p. 1080).

## Methods
- Dynamic programming. The value function collapses to one number per time slot, and the best policy is a peg at a time varying premium over the bid (Theorem 1, p. 1077; proof in working paper pp. 34 to 38).
- Bounds on the optimal limit price for small Δt (Theorem 2, p. 1077; proof in working paper pp. 38 to 45) and an asymptotic expansion of the value (Theorem 3, p. 1078; proof in working paper pp. 45 to 51). The proofs rest on Gaussian tail bounds and on buyer arrivals being independent of the price.
- A check that discrete time alone costs only order Δt, so the effect is latency and not the time grid (Lemma 2, p. 1079).
- The exact cost computed numerically for the one stock day, then the closed form applied to the NYSE panel at a fixed 500 ms, and inverted to get the latency needed for a fixed cost (pp. 1080 to 1084).

## Main results
- The closed form. Latency cost, as a share of the cost of immediacy, is about (σ√Δt / δ) times √log(δ² / (2πσ²Δt)) as Δt goes to zero (Corollary 1, p. 1078). It does not depend on the horizon or the arrival rate, it is larger for volatile or liquid assets, and the gain from cutting latency grows as latency falls (p. 1079).
- On the safety margin, for the Goldman day the final limit price is shaded by about 2.1, 1.6 and 1.4 standard deviations of the price over the interval at 50, 250 and 500 ms (Figure 5, p. 1081). The cost falls from about 20% of the cost of immediacy at 500 ms to about 5% at 5 ms, and the closed form tracks the exact cost closely (Figure 7, pp. 1081 to 1082).
- Over time. At a fixed 500 ms, the "human time scale", the median cost rose from about 5% to about 14% from 1995 to 2005, with jumps at the tick size cuts of June 1997 and January 2001 (Figure 8, pp. 1082 to 1083). The authors read this as tighter spreads raising the value of speed.
- Implied latency. Holding the cost at 10%, the authors report that the median latency needed fell by "approximately two orders of magnitude" (p. 1082, Figure 9 on p. 1084, also the abstract).
- In money terms, with the cost of immediacy set to one cent, going from 500 ms to under 1 ms is worth about $0.0015 to $0.0025 a share, the same order as institutional commissions and fees and as reported high frequency profits (p. 1083).
- Jumps. Adding Gaussian jumps lowers the value even with no latency but leaves the latency cost formula unchanged (working paper Appendix D, Theorem 6, pp. 53 to 54). The paper states this without proof, and the non Gaussian case is labelled a conjecture (working paper p. 55).

## Differences between the versions
I found no difference in results, assumptions or numbers. The theorems, the figures and every number I compared match. The published title adds "OR Forum". Some references were updated to their published forms (Easley et al., Hendershott et al., Cohen and Szpruch). The proofs are only in the working paper's electronic companion.

## Limits
- One trader, one share, no competitors, no queue and no adverse selection. The authors say all of this themselves (pp. 1071, 1075, 1085).
- Fixed latency that equals the decision interval. Real latency is random and has its own distribution.
- The closed form is asymptotic, with an unquantified "small enough" condition, and it needs the spread to be wide next to price moves over the latency.
- The calibration rests on one stock day and on published daily estimates. On my reading of Figure 9 the median implied latency falls from roughly 2,800 ms in 1995 to roughly 200 to 250 ms by the end of 2005, about one order of magnitude rather than two. The formula itself points the same way, since a cost that roughly triples at a fixed latency, scaling with √Δt, means the latency for a fixed cost falls by roughly nine times, log term aside. This is my reading of a log scale chart, so I hold it loosely, and I do not cite the two orders figure.
- Small slips. The note to Figure 6 calls 0.05 a "0.05-cent spread", but the spread is $0.058 and 0.05 is the dollar value of the cost of immediacy. The spread is said to be rounded "to the nearest cent" and is given as $0.058 (pp. 1080 to 1081).

## What it means for my work (my own inference)
- Their cost of latency comes only from a price chosen before the order lands. In my primary taker and passive legs the order reads the book again on arrival, so in their terms it carries no stale information at all. That is a second, independent reason to expect H1 and H2 to sit near zero on random decisions, which I already logged on 2026-11-18. The fixed price passive arm (H5) is the closer match to their setup, though their trader shades her price on purpose and mine does not.
- In their model a stale order that the market crosses fills at the bid, no worse than a market order. Nobody races it. My dev day fixed price arm shows the same kind of free option when the book has moved toward the order. Their model does not predict a cost from that crossing either. Its cost is the spread the trader gives up.
- The name "latency cost" in my preregistration is a different quantity. Theirs is lost value as a share of the cost of immediacy for a trader who optimises. Mine is the shortfall at a delay minus the shortfall at 1 ms, in basis points, for an order that does not optimise. I keep my definition as registered and do not compare the two numbers.
- BTCUSDT has a one tick spread on almost every update of the dev day. If the price moves more than the tick over even a few milliseconds, which I have not measured, their closed form is outside its range there and only the dynamic programme would apply.
- The paper says nothing about queue position. It gives no support to the queue loss part of my question.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Background on why latency costs a limit order and on the stale price channel, and a reference point for the fixed price passive arm. Not used as a benchmark for any of my numbers.

## Open questions
- Is the drop in median implied latency about one order of magnitude or two? The figure and the formula suggest one.
- How do they convert a daily volatility to the per second volatility the formula needs? The paper does not say.
- Do the jump results hold with proofs, and for jump sizes that are not Gaussian?
- With random latency instead of a fixed one, does the √(Δt log(1/Δt)) shape survive? Cartea and Sánchez-Betancourt (2023) study stochastic delay, but I have read them since and they don't derive a cost of latency curve, so they don't answer this ([note](cartea-sanchez-betancourt-2023-execution-stochastic-delay.md)).

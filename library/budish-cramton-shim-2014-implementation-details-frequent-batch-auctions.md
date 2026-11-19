# Budish, Cramton & Shim (2014), Implementation Details for Frequent Batch Auctions

## Citation
Eric Budish, Peter Cramton and John Shim (2014). *Implementation Details for Frequent Batch Auctions: Slowing Down Markets to the Blink of an Eye*. American Economic Review: Papers & Proceedings 104(5):418-424. [doi:10.1257/aer.104.5.418](https://doi.org/10.1257/aer.104.5.418). Venue, year and pages are as printed on the article itself. It was in the "Frontiers of Market Design" session.

I read the published seven pages. Page numbers below are the journal's, 418 to 424. The paper cites the main paper as their 2013 working paper, so it was written before the journal version of the [arms race paper](budish-cramton-shim-2015-hft-arms-race.md).

## Reading depth
I read all seven pages, including the footnotes, the two figures and the step by step procedure in Section II. There are no proofs and no data analysis in it. I used it to get the big picture before the main paper, and I don't rely on it for any claim about the main paper.

## Core idea
A short engineering companion. It explains how frequent batch auctions would actually run. Orders are taken during an interval, the exchange clears one uniform price auction at its end, and then reports the result. It also shows how such an auction could sit inside the fragmented US equity market under Reg NMS, and lists what should set the length of the interval.

## Model or setting and its assumptions
- No model. It restates the argument of the main paper in one paragraph (p. 418). The continuous book processes messages one at a time, so after news the firm with a stale quote has to beat every sniper, and that cost ends up in spreads and depth.
- Design choices are made to stay as close as possible to the continuous book, to keep transition costs and surprises low (p. 419).

## Data
- None beyond one footnote. On a handful of random days in 2011, SPY had no trades in 14% of one second intervals, JPM in 38% and GOOG in 73% (p. 420, footnote 2).
- Latency figures come from conversations with industry participants or quick simulations, not measurement (p. 423).

## Methods
- Description of the process flow (Figure 1, p. 419) and of the clearing rule (Figure 2, p. 420).
- A rule for folding liquidity from continuous venues into the auction when the batch price would trade through the national best price (pp. 421 to 422).
- A list of what the interval should be long relative to (p. 423).

## Main results
- Order submission (p. 419). Orders are price, size and side, can be changed or pulled freely, and carry over to the next auction until filled or cancelled. They are not shown during the interval. Footnote 1 says displaying them would invite gaming. The optimal tick is left open, with a guess that it should be at least as fine as in the continuous market.
- Auction (p. 420). If supply and demand don't cross there is no trade. If they cross, all orders better than the clearing price fill in full. At the clearing price one side is rationed, pro rata within an interval, with earlier intervals first. If the curves meet vertically the price is the midpoint.
- Reporting (p. 420). Price or no trade, quantity and the aggregate curves are published, and each sender hears privately about their own order. They suggest not publishing individual orders. The main paper's later text says all orders entered in the auction are displayed after it (p. 39 of the 2015 manuscript). That may only mean the book without names, but as written the two differ.
- Footnote 3 (p. 420) is the closest thing in either paper to my own question. In any continuous market there is latency, so "the best a trader can do in a CLOB is see the limit order book as it was a short time ago (e.g., 1ms ago) and act on this limit order book a short time later (e.g., 1ms later)", and liquidity seen at the decision "may or may not be there" when the order is processed.
- Fragmentation (pp. 421 to 422). Sealed orders don't display a crossed book, so they think that part of Reg NMS is no issue. When the batch price would be worse than the national best ask, the auction adds the continuous venues' asks to its supply, sweeps them, and rebates any surplus to filled batch orders. They note that small latencies could make the sweep fall short and give two ways to handle it.
- Interval length (p. 423). The theory says it should be long relative to the speed gap between the fastest firms and the next tier (they were told under 1 ms) and to the random spread in speed among the fastest (under 0.1 ms). In practice it also needs time to compute the auction (a C++ simulation at Flash Crash message rates always cleared in under 10 ms on an ordinary laptop), to sweep New Jersey venues (about 0.5 ms round trip), to send results around the world (at most about 135 ms at light speed), and to let algorithms decide.

## Limits
- No evidence for the main argument here. It summarises it.
- The race timescales on p. 418, 10 ms in 2005, 1 ms in 2008 and 0.1 ms "presently", have no source given. The main paper's measured analogue is the median ES and SPY arbitrage duration, 97 ms in 2005 and 7 ms in 2011. I don't cite the companion's three numbers as measurements.
- The title's "blink of an eye (roughly 0.5 seconds)" is not a recommended interval. Neither paper picks one.
- Written for US equities and Reg NMS. Crypto venues have no such rule.

## What it means for my work (my own inference)
- Footnote 3 says the premise of 01 in their words. A decision is made on a book that is already old, and the order lands on a book that has moved. It is framing, not evidence.
- The pro rata within an interval rule is a clean contrast to the time priority my passive leg assumes. In a batch market, arriving a few ms later inside the same interval would cost nothing in queue terms. That only sharpens what my passive leg measures in a continuous book. I have no batch data and don't plan any.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Read for intuition before the main paper. Nothing in 01 rests on it.

## Open questions
- Where do the p. 418 race timescales come from?
- Did the information policy change between this piece and the journal version of the main paper, or are the two passages saying the same thing in different words?

## Related notes
- [Budish, Cramton & Shim (2015), the main paper](budish-cramton-shim-2015-hft-arms-race.md)

# Danait, Zamora & Boier (2026), Same Book, Different Fills

## Citation
Riya Danait, Yuliana Zamora and Ioana Boier (2026). *Same Book, Different Fills: Partial Identification of FIFO Execution from Aggregate Order Books*. arXiv 2609.13597, version 3, dated 17 October 2026. [doi:10.48550/arXiv.2609.13597](https://doi.org/10.48550/arXiv.2609.13597). CC BY 4.0. Danait is at the Oxford Mathematical Institute, Zamora and Boier at NVIDIA.

A preprint, not yet published as far as I know. Version 3 has no journal page numbers, so this note points to sections, tables and equations instead.

## Reading depth
I read the whole paper, tables and figures included. I haven't checked their interval method. The ranking reversal chart in Figure 1 I only looked at, and the exact shares I quote come from the text of Section 7.2.

## Core idea
Level two data shows how much rests at each price but not the queue of orders behind it, so it can't say which order a cancellation removed. A backtest of passive orders on such data quietly picks one answer. The paper holds the whole observed book path fixed, builds order level histories that all reproduce it, and changes only where cancellations land in the queue (front, quantity weighted random, back). It then measures how much passive fills and costs move. The authors frame it as partial identification, so the result is a range that comes from the reconstruction rules, not an estimate of the true queue (Section 1, Section 3.3).

## Model and its assumptions
- One observed path per replay block. Each change in displayed size at a price is split into a market removal matched to an L1 trade, then one residual cancellation or one residual addition, never both in the same cell. Inside a transition the order is removals, then cancellations, then additions, the same under every rule (Section 3.1, equations 1 and 2).
- Initial depth and later additions are cut into latent orders using the sizes of positive additions seen in January to May. These pieces are drawing inputs, not claimed to be real order sizes (Section 5.1).
- The three rules differ only in the residual cancellation. Front removes the oldest quantity, back the newest, and random samples live orders in proportion to their size until the amount is used up (Section 3.2).
- The policy order is a virtual marker. It records quantity ahead and never touches the background book. Later additions at its price join behind it, and a cancellation helps it only when the rule removes quantity ahead of it (Section 3.3, equations 6 and 7). Aggressive orders run against a copy of the book that is then thrown away.
- Proposition 3.1 orders the fills (back at most random at most front) for one marker while the best price stays unchanged, and only when each cancellation removes at least as much ahead of the marker under front as under random, and under random as under back (Section 3.4). Front and back are not bounds on general policy outcomes (Section 3.3, Section 8.2).
- The authors list what is assumed away. The shadow policies have zero latency, no fees or rebates, no market impact, and terminal inventory crossed on a copied book (Section 9).

## Data
- Proprietary LSEG data for two Tokyo Stock Exchange names, 1301.T and 7911.T, from 6 January to 25 July 2025. Ten level L2 snapshots plus L1 trades, continuous session only (Section 4.1).
- Tick size 5 yen for 1301.T and 1 yen for 7911.T, 136 and 137 usable dates, 843,135 and 9,062,080 continuous L2 rows, 24,607 and 319,046 regular trades (Table 1).
- January to May for estimation, June for choosing settings, July as the held out month with 18 dates. Everything was fixed before any July FIFO outcome was looked at (Section 4.4). Each name has 1,080 five minute episodes in July (Table 1, Section 7.1).
- Data quality. Unresolved transitions are 4.14% to 6.11% of rows on 1301.T and 5.09% to 6.59% on 7911.T. Boundary transitions are 11.10% to 16.00% and 8.39% to 12.32% (Table 1).

## Methods
- A compiler turns each block into an order level message stream under each rule, with the same seeds, partitions, additions, trades and block boundaries. After every transition the live orders must add back to the observed L2 state (Section 5.2). A sample of streams was replayed through JAX LOB, an outside matching engine, as a separate check (Section 5.2, Section 7.1).
- Tagged probes. A virtual 100 share order at the best price every five seconds, lasting at most 15 seconds, paired across the three rules (Section 6.1).
- Three policies over 300 second episodes on both sides. Aggressive TWAP, passive at touch, and a hybrid that crosses any shortfall against schedule at ten checkpoints. Parent size is 100 shares for 1301.T and 200 for 7911.T (Section 6.2).
- Implementation shortfall against the arrival mid in basis points, with any residual crossed against the terminal book (equation 10). They also report completion before the terminal cross and how often the cheapest policy changes when only the rule changes (Section 6.3).
- Outcomes are averaged within each date and the 18 dates weighted equally. Section 6.4 describes the intervals as resampling whole dates. Policy change shares are pooled and descriptive, with no intervals.

## Main results
- Every one of the 354,774 (1301.T) and 370,992 (7911.T) matched probe triplets satisfies the fill ordering of Proposition 3.1 (Section 7.1). Probe fills over 15 seconds are tiny, about 0.01% on 1301.T and 0.22% to 0.50% on 7911.T.
- The aggressive benchmark does not move with the rule. It is 10.010 bps on 1301.T and 2.400 bps on 7911.T under all three (Table 2).
- Passive completion before the terminal cross on 1301.T is 18.15% (front), 15.29% (random) and 10.14% (back), a gap of 8.01 points. On 7911.T it is 97.20%, 95.52% and 89.81%, a gap of 7.39 points (Table 2, Section 7.2).
- Passive at touch shortfall on 1301.T runs from 8.008 bps (front) to 9.018 bps (back), and on 7911.T from 0.765 to 1.149 bps. The front minus back gaps are 1.010 and 0.384 bps (Table 2, Section 7.2). On 1301.T the front and back intervals do not overlap ([7.480, 8.531] against [8.656, 9.401]). On 7911.T they touch ([0.547, 0.974] against [0.932, 1.357]).
- Passive at touch is the cheapest policy for both names under every rule (Section 7.2).
- The cheapest policy changes in 0.83% to 4.49% of cross rule comparisons on 1301.T and 3.63% to 14.26% on 7911.T. When it changes, the extra cost is 14.277 to 17.354 bps on 1301.T and 2.366 to 3.723 bps on 7911.T (Section 7.2).
- Robustness. Fixed 100 share partitions leave the front minus back gaps unchanged. On stricter blocks the passive gap shrinks to −0.397 bps on 1301.T and to −0.325 bps on 7911.T, whose interval reaches zero. The authors call that strict sample not conclusive on its own (Section 7.2).

## Limits
- Two names, one held out month, the same 18 dates for both, so 36 instrument days in all (Section 9).
- Front and back are endpoints of their own reconstruction, not bounds on what the real queue did, and the latent partition is a modelling choice (Section 3.3, Section 8.2).
- The two names differ in price, tick, activity and parent size, so the gap between them is not a liquidity effect (Section 4.1, Section 8.2).
- No latency, fees, rebates or impact in the shadow policies (Section 9).
- Each cell allows a cancellation or an addition, not both. Cells that need both end the block, so the busiest moments may be the ones left out. That last point is my reading, not theirs.

## What it means for my work (my own inference)
- My passive leg on Binance L2 has the same blind spot. Any fill rate I report depends on a cancellation rule I can't see. That is why I run three matched rules and only count a delay effect whose sign holds under all three.
- On my dev day the rule gap in fill probability is about 22 points, far larger than anything delay does. That fits their point in direction. The size is not comparable, given a different market, tick regime and queue depth.
- Their policies have zero latency, and they say so in Section 9. I vary delay on the same path. Delay and the rule may interact. Under back, cancellations never shrink the queue ahead of me, so arriving late costs me the quantity that joined ahead during the delay, and under front early cancellations can undo part of it. That is a hypothesis, not a result.
- My replay nets the size change per update, so an add and a cancel inside one update offset each other. Their compiler refuses such cells and ends the block. My approach keeps those moments but blurs them, and I log it as a deviation.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). The reason the passive leg uses three matched cancellation rules and reports every passive number as a range. It also gave me the idea, marked exploratory, of reporting how often the best delay setting changes when only the rule changes.

## Open questions
- How close is any of the three rules to where cancellations really land? LOBSTER has order IDs and might show it for Nasdaq names. I have not checked.
- Would a wider envelope, beyond their three rules, change the conclusions? They say the three rules are only a subset of the histories the data allows (Section 3.3).
- Do the gaps survive on a large tick crypto book where the queue is huge next to a typical order?

## Related notes
- [Yueshen (2026)](yueshen-2026-queuing-uncertainty.md), which they cite for queue uncertainty from latency. Theirs comes after the fact, from data that has lost the order IDs.
- [Moallemi & Sağlam (2013)](moallemi-saglam-2013-cost-of-latency.md).
- [Albers et al. (2025)](albers-cucuringu-howison-shestopaloff-2025-good-bad-latency.md).

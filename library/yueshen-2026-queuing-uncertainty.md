# Yueshen (2026), Queuing Uncertainty of Limit Orders

## Citation
Bart Zhou Yueshen (2026). *Queuing Uncertainty of Limit Orders*. Management Science 72(6):4760-4779. [doi:10.1287/mnsc.2023.03371](https://doi.org/10.1287/mnsc.2023.03371). Received 16 October 2023, revised August 2024 and January 2025, accepted 26 February 2025, online in Articles in Advance 17 September 2025. Open access, CC BY 4.0. Singapore Management University.

The copy I read is the open access one from the SMU repository, which is the Articles in Advance version, pages 1 to 20. The issue page numbers 4760 to 4779 don't appear on it, so page numbers in this note are the Articles in Advance pages. Some other papers cite it as 2025, the online year.

## Reading depth
I read the whole paper, figures included. I followed the proofs for structure but didn't check them line by line. I haven't read the online appendix, which holds the microfoundation of the queue distribution and the other ways of modelling liquidity demand. Figure values I quote are read off the charts, so treat them as approximate.

## Core idea
Makers who send limit orders to the same price at about the same time can't know where theirs will land in the queue, because latency decides the order. Units at the front of a queue make money and units at the back lose it, since a deep unit only fills against a big market order, and big market orders carry more information. With queue position uncertain, every maker bids for a front place, and the book ends up deeper than the level where the last unit breaks even. So in equilibrium the last unit in the queue loses money in expectation (abstract, p. 1; Lemma 1, p. 7; Proposition 1, p. 8). The uncertainty works like a measure of competition, between a monopolist and perfect competition (Example 2, p. 9).

## Model and its assumptions
- A one shot, one tick book that starts empty. Only the ask side is studied (Section 2, pp. 4 to 5; Remark 1, p. 5).
- n risk neutral makers each post one order at time 0. The queue order is a random permutation with a known distribution, independent of size. A faster maker is more likely to be early. Ties are ruled out (Remark 2, p. 5).
- With some probability makers learn their places before the market order and may cut their size, never raise it. Revising doesn't change the queue (Section 2, p. 5; Remark 3, p. 6).
- One investor arrives last and sends one market buy. She hedges an endowment shock and speculates on a private signal, so hedging is where makers earn and speculation is where they are adversely selected (pp. 5 to 6). The market order always arrives last by design, and there is no news (Remark 2, p. 5).
- Latency only sets queue order. There is no price path after a fill, no horizon, no markout and no delay in milliseconds. Latency is a number between 0 and 1.
- The author leaves out several ticks with size discreteness, fees, other priority rules, rationing and queue jumping (Remark 5, p. 6). Lemma 2 shows only that an equilibrium exists, and there may be more than one (p. 8 and endnote 6).
- Results need the ask high enough and hedging demand large enough, both above thresholds (Lemma 1, p. 7). Lemma 3 and Proposition 4 hold in the limit of a large sector of makers.

## Data
None used for testing. The only data is one descriptive figure of all TAQ messages for 400 randomly chosen US stocks over the trading hours of 2018, 25.39 billion messages in total. Trades are 5.7% of messages and quotes 94.3%, and the single largest category, at 59.9%, is quote updates that change NBBO depth with the price unchanged (Figure 1, p. 2). No regression or estimate is run.

## Methods
Equilibrium analysis of the one shot game. The marginal profit of each unit of depth is worked out from the investor's optimal order (pp. 5 to 6), then the makers' first order conditions with and without revision, two worked examples, comparative statics, and a welfare analysis (Sections 3 and 4, pp. 6 to 15). Proofs are in the appendix of the article (pp. 16 to 19).

## Main results
- Top of queue advantage: Marginal profit starts positive, crosses zero once and stays negative after that. Units at the end of the queue are less likely to fill and, if they fill, more likely to meet a more informed market order (Lemma 1 and Figure 3, p. 7).
- Liquidity overshoot: Without revision, equilibrium depth is at least the break even depth, so the last unit loses money in expectation. The overshoot is strict unless some maker is sure to be first (Proposition 1, p. 8). With two makers equally likely to be first, depth is four thirds of the break even level, the largest overshoot in that example (Example 1, pp. 8 to 9).
- With one maker the book sits at the break even depth. As the number of equally fast makers grows, it goes to the depth where total profit is zero (Example 2, p. 9).
- Revision makes the overshoot stronger, not weaker (Proposition 2, p. 10). Once places are known, makers cut back to the break even depth, so the prediction is clustered submissions followed by quick cancellations, and the cancellations fall on the tail of new queues (Prediction 1 and Figure 4, pp. 10 to 11).
- Cancel to add count ratio. More adverse selection lowers it (Lemma 3 and Proposition 3, p. 11). The introduction gives the empirical form, cancellations relative to submissions should fall as order flow gets more toxic (p. 3).
- Cancel to add size ratio. With identical makers it goes to one. Proposition 4 says that with a large sector of fast and slow makers it is (i) below one and (ii) higher with more fast makers (pp. 12 to 13). The fast orders are larger and sit near the front, so cancellations come mostly from the smaller slow orders at the back (p. 13). In Figure 6 it rises from roughly 0.85 to 1.00 as the share of fast makers goes from zero to one (p. 13, read off the chart).
- One sentence in the introduction reads the other way on direction. It says a smaller cancellation size relative to addition size indicates more fast suppliers (p. 3). Proposition 4(ii) and Figure 6 say the ratio is higher with more fast makers. My reading is that the introduction means fast makers being present at all, since a ratio below one needs a mix of speeds. I cite Proposition 4 for the direction.
- Welfare: It rises with depth beyond the break even level, peaks, then falls (Proposition 5, p. 13). The loss comes from the investor speculating too much once the book is deep (pp. 13 to 14). A speed bump on market orders only can hurt welfare (Corollary 1, p. 15).

## Limits
- A model. Nothing is tested on data.
- One shot, one tick, empty book, one investor who always comes last (Remarks 1 and 2, p. 5). The author calls the setting extremely stylized.
- "End of the queue" means the depth beyond the break even level in a freshly formed queue of competitors who posted in the same burst. It is an expected value of the marginal unit, not a statement about any one order.
- Large sector limits and symmetric strategies for the ratio results. Equilibrium may not be unique.
- The online appendix, which I haven't read, carries the microfoundation and the other demand setups. The paper says they don't change Section 3 qualitatively (Remark 4, p. 6).

## What it means for my work (my own inference)
- The back of queue loss is supported by Lemma 1 and Proposition 1, as a model statement in expectation. That is what I cite it for.
- The size ratio below one is supported by Proposition 4(i), only for a sector that mixes fast and slow makers. For the direction of change I cite Proposition 4, not the introduction.
- The paper never says an order sent later has a worse markout over a fixed horizon. H2c in my preregistration takes that step, and it is my own inference from the end of queue result, not the paper's. In the paper being late means sitting behind same burst competitors. In my replay a late order joins whatever queue stands when it arrives, and nobody reacts to it. So my dev day matched markouts, which run against H2c, don't contradict the paper. They test a mechanism it doesn't model.
- My across rule pattern, back rule fills losing more than front rule fills, points the same way as the end of queue result. It compares cancellation rules, not measured places in a queue, and back rule fills are a selected set, so I treat it as consistent in direction and nothing more.
- Cancellations in the model happen only when places become known, never because of news. Any cancellation pattern I see on Binance has both causes mixed in.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). The theory behind H2c and the reason the passive leg measures what a filled order earns, not only whether it fills. Background on why cancellations bunch at the tail of new queues.

## Open questions
- Does the online appendix's microfoundation of the queue distribution say anything about how latency maps to queue order? I haven't read it.
- Is there an empirical test of the count or size ratio predictions? None is in the paper.
- In a book where my order joins an existing queue rather than a fresh burst, does any version of the end of queue loss carry over? The model doesn't cover it.

## Related notes
- [Danait, Zamora & Boier (2026)](danait-zamora-boier-2026-same-book-different-fills.md), queue uncertainty from data that has lost order IDs, which they contrast with this paper.
- [Albers et al. (2025)](albers-cucuringu-howison-shestopaloff-2025-good-bad-latency.md), adverse selection of taker orders in a latency race.
- [Moallemi & Sağlam (2013)](moallemi-saglam-2013-cost-of-latency.md), which has no queue at all.

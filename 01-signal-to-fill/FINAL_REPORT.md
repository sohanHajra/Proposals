# From Signal to Fill. Final report (draft for review)

## Bottom line
On Binance BTCUSDT perpetual data, I found no measurable cost of delay for decisions made at random moments. That holds for taker orders and for passive orders under all three cancellation rules, on both registered test days. Both primary tests, H1 and H2, are null. Where delay did cost something was an order that acts on a signal. A taker trading on top of book imbalance paid about 0.085 bps at 1 ms and 0.66 bps at 500 ms on 2026-10-01, and 0.071 and 0.52 bps on 2026-11-01. That was not a registered primary test, so I report it as the clearest secondary result and nothing more.

This is a simulation with injected delay on three free crypto days plus six more first of month days. It cannot say anything about real routing speed, other venues or other kinds of day.

## What I tested
The question is in [PROPOSAL.md](PROPOSAL.md) and the pass and fail rules are in [PREREGISTRATION.md](PREREGISTRATION.md), committed before any test day was downloaded. I replayed the same decision at nine delays from 1 to 500 ms against recorded top of book, five level and trade data, so market conditions are identical across delays by construction.

## Quant section
All numbers come from files in `results/`, and the notebook entry of 2026-11-20 gives the source file for each.

**H1 primary (taker, five level walk).** Null on both days. The slope on log delay is 0.00079 bps per log ms on 2026-10-01 (interval negative 0.00021 to 0.00183) and 0.0000044 on 2026-11-01 (negative 0.00041 to 0.00042). The mean extra shortfall at 500 ms is far below the 0.1 bps bar on both days.

**H2 primary (passive fill probability).** Null on both days under front, random and back cancellation. All six intervals cover zero. Fill probability at 1 ms runs from 45% to 71% on 2026-10-01 and from 22% to 59% on 2026-11-01, so the queue rule matters a great deal for the level and not for the slope.

**Secondary.** H1b is supported by its rule but is partly mechanical. H2b, H2c, H3 and H5 are not supported, and H5 and H2c point the other way where they point at all.

**Breadth, eight days.** The two test days and six more first of month days. Counts are registered side, opposite side, covering zero. H1 reads 1, 0, 7. H2 reads 0, 0, 8 under every rule. The signal decision cost is positive on every one of the eight days. Verdicts come only from the two test days.

**Exploratory.** The fixed price arm without orders that are marketable on arrival came out positive on both test days under every rule. It is a description, since the kept set changes with delay, and it is a candidate for later work and not a result here.

## My inference, not published
A random decision that reprices on arrival has little to lose to delay, so the nulls are what I would expect. The signal result is the case where an order knows something that decays. That reading is mine and I have not tested it against a model.

## What the literature says
The sources are in [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md), with how deeply I read each one. The nearest work uses proprietary data or optimised strategies, so the question of a paired delay replay on public data is not found in this review, which is a weaker claim than saying nobody has done it.

## Honesty box
- Days. Two test days and six breadth days, all first of month, two on weekends. One 2012 equity day for the order lifecycle part.
- The first start on 2026-10-01 was cut off by the machine. I reran it once. Steps after the cut ran only in parts, and the only check that one process gives the same answer is the dev day dry run.
- The breadth gap rule used count times longest gap as an upper bound, not the real total.
- No second reader has checked the write up yet. A cold review is owed before release.
- Numbers in this draft are not yet all tagged for claimcheck. Untagged ones are warnings in the check output and have to reach zero before release.
- Not available. Real decision timestamps, order IDs for BTCUSDT, and more than one free day a month. More days, a second venue and queue data would tighten every conclusion.

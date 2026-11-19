# Preregistration

Written 2026-11-15, before the replay engine exists and before any test day is downloaded. The git commit that adds this file is the timestamp. `python -m s2f.get_data test` refuses to run until this file is in git history.

## What I had seen when I wrote this
- The dev day audit for Binance USD-M BTCUSDT on 2026-09-01 (`results/audit/tardis_2026-09-01.json`).
- The LOBSTER audit for AAPL, AMZN, GOOG, INTC and MSFT on 2012-06-21 (`results/audit/lobster_2012-06-21.json`).
- No replay output of any kind. No test day data. No Alpaca orders.

Anything below that turns out to be unworkable gets changed only through the Deviations section at the bottom, dated, with the reason, and before the test days are run. After the test days are run, nothing in the primary tests changes.

## Data
| Role | Data | Days |
|---|---|---|
| Dev | Tardis free CSVs for Binance USD-M BTCUSDT. `book_ticker` (top of book), `book_snapshot_5` (five levels), `trades` | 2026-09-01 |
| Test | Same files | 2026-10-01 and 2026-11-01, each analysed on its own |
| RQ2 | LOBSTER Nasdaq samples, 10 levels, with order IDs | 2012-06-21 |

Events are ordered by exchange timestamp. Within one millisecond, trades go before book updates, and each file keeps its own order.

## Decisions
A decision is a moment `t` (exchange time) and a side. The book seen at `t` is the last update with exchange time at or before `t`.
1. **Random decisions (primary).** Poisson times with a mean gap of 10 s, side chosen by a fair coin. Seed 20261115.
2. **Signal decisions (secondary).** Top of book imbalance `I = (bid size − ask size) / (bid size + ask size)`. A decision fires when `|I|` is at or above the 90th percentile of `|I|` on the dev day, side equal to the sign of `I`, at most one decision per second. The threshold is computed once on the dev day and then frozen for the test days.

Order size is 0.01 BTC. Decisions closer than 60 s to either of the dev day's two feed gaps over 1 s, or to any gap over 1 s on a test day, are dropped.

## Delay grid and timing
Added delay `d` in {1, 2, 5, 10, 25, 50, 100, 250, 500} ms. The order reaches the book at `t + d`. Exchange timestamps are whole milliseconds, so 1 ms is the smallest delay I can resolve and it is the baseline.

Tie rule (primary). My order is processed after every event stamped at or before `t + d`. This is the cautious choice. Robustness flips it so my order goes before events stamped exactly at `t + d`.

Every decision is replayed at every delay on the same path. All comparisons are paired within a decision.

## RQ1a Taker orders
A marketable order of 0.01 BTC walks the five level snapshot at arrival.
- **Shortfall** `S(d)` in bps is `side × (fill VWAP − mid at t) / mid at t × 10^4`.
- **Split.** `S(d)` = drift `side × (mid at t+d − mid at t)` plus arrival cost `side × (VWAP − mid at t+d)`, both in bps.
- **Latency cost** `ΔS(d) = S(d) − S(1 ms)`, per decision.

**H1.** Latency cost rises with delay. I estimate the slope `β` of `ΔS(d)` on `log(d)` across all decisions and delays, with a block bootstrap over 5 minute blocks (2,000 resamples, 95% interval).

**H1 counts as a finding** only if on each test day separately the interval for `β` is above zero, and the mean `ΔS(500 ms)` is at least 0.1 bps on each test day. I chose 0.1 bps because Albers et al. (2025) report roughly 0.07 to 0.3 bps of average slippage for a market order whose markout would have been 2 bps (about 0.1 on Bybit BTC, 0.07 on Bybit ETH, 0.3 on Binance BTC inverse), so a smaller effect would sit below what a live study already sees. The anchor is loose. Their number is conditional on a 2 bps markout and comes from colocated orders, while mine is an average over all decisions at 500 ms.

**H1 is a null** if the interval covers zero on either test day or the signs differ between days. I will report it as a null.

**H1b (secondary).** Albers et al. found that orders that would have made money are the ones that slip. I split decisions by the sign of `side × (mid at t+1 s − mid at t)` and compare mean `ΔS(100 ms)` between the positive and the rest, with the same bootstrap. Supported if the positive group's latency cost is larger, with the interval above zero, on both test days.

## RQ1b Passive orders
A limit order of 0.01 BTC joins the best price on its own side at `t + d`. Queue ahead is the displayed size at that price at arrival. The order never changes the book.

Inside one book update I apply trades first, then cancellations, then additions (following Danait, Zamora and Boier, 2026).
- Trades at my price reduce the queue ahead. Once it is used up, further traded size fills me.
- A drop in displayed size not explained by trades is a cancellation. Where it lands is set by one of three rules, run on the same path, seeds and trades.
  - **Front.** Cancels remove the oldest quantity first. Best case for me.
  - **Random.** Cancels land at a position drawn in proportion to quantity. Seed 20261115.
  - **Back.** Cancels remove the newest quantity first. Worst case for me.
- A rise in displayed size joins behind me.
- A trade at a price through mine fills the rest of my order.
- I track my level with the five level snapshot. If it leaves the top five, I count the order as unfilled from that moment.

Horizon `H` = 10 s. Metrics per decision and delay.
- Fill probability within `H` (full fills; partial fills reported separately).
- For filled orders, markout at 1 s and 10 s from the maker side.
- **Post then cross cost.** If the order is not filled by `H`, it crosses the spread at `H` as a marketable order. The total cost in bps against the mid at `t` gives one number that is comparable to the taker leg.

**H2.** Passive fill probability falls with delay. Slope of fill probability on `log(d)`, same bootstrap.

**H2 counts as a finding** only if, under all three cancellation rules and on both test days, the interval for the slope is below zero. If the sign holds under some rules and not others, I report that the data cannot decide it. Every passive number is reported as a range across the three rules, never as one value.

**H2b (my own hypothesis, labelled).** Delay and the cancellation rule interact. The drop in fill probability from 1 ms to 500 ms is larger under the back rule than under the front rule. Supported only if the paired difference has an interval excluding zero on both test days. Otherwise it stays a hypothesis.

**H2c (secondary, from Yueshen 2026).** In Yueshen's model, orders at the end of a queue lose money when they fill. If that shows up here, fills at 500 ms have worse 10 s markouts than fills at 1 ms. Reported under all three rules, not counted as a finding unless the sign holds under all three on both test days. The comparison is conditional on filling, so the orders that fill at 500 ms are not the same decisions as those that fill at 1 ms. I will also report the comparison on decisions that fill at both delays.

## RQ3 Is latency cost a tail
- Regime split by realised volatility of the mid over the 10 s before `t` (top fifth against the rest), and by `|I|` at `t` (top fifth against the rest).
- **H3.** Mean `ΔS(100 ms)` is higher in the high volatility fifth. Same bootstrap. Finding only if the interval is above zero on both test days.
- Descriptive, not tested. The share of total `ΔS(100 ms)` that comes from the worst 10% of decisions.

## RQ2 Real order lifecycles (LOBSTER, observational)
Main sample INTC and MSFT, the two names in the sample where the spread is one tick on about 77% of book updates. AAPL, AMZN and GOOG are reported descriptively.
- Orders submitted at the best price on their side, with at least one visible execution in the file.
- Rest time is submission to first visible execution, in ms.
- Outcome is the markout of the mid 1 s after the first fill, from the resting order's side, in bps.
- Controls are spread, displayed size at the order's price at submission, top of book imbalance, mid volatility over the previous minute, and half hour of the day.

**H4.** Longer rest before the first fill goes with a worse markout for the resting order. OLS of markout on `log(rest time)` plus controls, standard errors clustered by minute. Supported only if the coefficient is negative with a 95% interval below zero in both INTC and MSFT. A coefficient that loses its sign after controls is reported as a null. This is one Nasdaq day in 2012 and describes that day only.

**Exploratory.** Where cancellations land inside a queue, from order IDs. Which of the three rules looks closer on this day. Labelled as Nasdaq 2012 only, not as evidence about Binance.

## Real decision to acknowledgement latency (Alpaca paper account)
The replay injects delay. I also want to know what one real retail stack looks like, so that I can mark it on the delay grid.
- From this project's machine, send 200 limit buy orders for the smallest quantity Alpaca's paper crypto venue accepts on BTC/USD, priced at half the current best bid so they cannot fill, one every 3 s, each cancelled right after its acknowledgement.
- Measure local monotonic time from just before the HTTP request to the HTTP response. Also record the `submitted_at` time Alpaca returns.
- Report median, 90th and 99th percentile, and the failure count.
- Used only to locate one realistic point on the delay grid. Alpaca paper fills are simulated, so no fill, price or shortfall from Alpaca is ever used. The path is to a broker API, not to Binance's matching engine, and the result says nothing about colocated latency.

## Robustness (run on the test days after the primary tests, all reported)
1. Fees. Binance USD-M published base tier taker and maker fees, read on the day of the run and cited, added to shortfall and to the post then cross cost.
2. Tie rule flipped.
3. Event order by local capture time instead of exchange time.
4. Signal decisions instead of random decisions.
5. Order size 1 BTC instead of 0.01 BTC.
6. Passive horizon 1 s and 60 s.
7. Placebo. Delay labels shuffled within each decision. The slope should be indistinguishable from zero.
8. Five minute blocks replaced by 15 minute blocks in the bootstrap.

## Primary and secondary
Primary tests are H1 and H2. Everything else is secondary or exploratory and will be called that in the report. Because each primary test must hold on two separate test days (and H2 under three rules), I do not add a further multiple testing correction, and I say so here so it is a choice on record rather than an omission.

## Known limits, stated in advance
- Decision to send latency is injected, never observed in market data.
- Nothing below 1 ms is resolvable.
- My simulated order never moves the market and never competes for the same liquidity in the same millisecond. A replay cannot capture other traders reacting to my own order. Albers et al. (2025) argue that a synthetic study would need latency that depends on future returns. The replay keeps the real future of the book but cannot model my order's place in a race.
- Queue position is modelled, which is why the passive leg carries three rules.
- Three crypto days, all the first of a month, and one 2012 equity day.

## Deviations
**2026-11-17, before any test day is touched.** The taker leg as built fills at the best price shown at arrival and flags an order if the displayed size is smaller than 0.01 BTC, instead of walking the five level snapshot. On the dev day that flag fires on 0.17% to 0.31% of decisions across the delay grid (`results/taker/taker_dev_2026-09-01.json`), so for 0.01 BTC the two methods should differ very little. I have not run the walk, so I do not know that. The 1 BTC robustness check will need the walk, and I will build it before that check runs.

**2026-11-18, before any test day is touched.** Choices the passive leg made that the text above leaves open. The 10 s horizon is counted from the arrival of my order, not from the decision. Partial fills count as not filled for fill probability, and the unfilled part crosses at the horizon in the post then cross cost. Maker markouts use the fill price as the reference. Where the book update and a trade show the same drop in size I count it once, through the trade. I did not pick any of these after looking at a result, but I did write them down after building the engine.

**2026-11-18 afternoon, before any test day is touched. Written after looking at the dev day.** A second reader pointed out something I should have seen. In both primary legs my order reads the book again when it arrives. The taker fills at the arrival touch and the passive order joins the arrival best. With random decision times and a coin flip side, the arrival is just another random moment, so the mean latency cost in H1 and the change in fill probability in H2 are close to zero by construction. A null on H1 or H2 therefore cannot tell me whether latency matters. It only tells me that an uninformed order which reprices on arrival loses little. I keep H1 and H2 exactly as registered and will report them, but I will say this plainly next to them.

I add one arm, labelled exploratory because it was written after the dev look.
- **Fixed price passive (H5).** The limit price is the best price on my side at decision time `t` and does not change. At `t + d` the order is posted at that price. If the book has moved through it, the part that is marketable fills against the arrival book as a taker. If the best on my side has moved away, the order sits behind the new best and only fills if the price comes back. Queue rules, horizon, markouts and post then cross cost are the same as RQ1b, under all three cancellation rules. Metrics are fill probability, 10 s maker markout of filled orders, and post then cross cost, each against delay, with the same bootstrap.
- **H5.** Post then cross cost rises with delay for fixed price passive orders. Supported only if the slope on `log(d)` has an interval above zero under all three rules on both test days.
- For the taker leg a fixed price changes little on random decisions, because a marketable order that misses must cross at the arrival touch anyway. The place where a taker latency cost can show up is the signal decisions, already registered as secondary. I will run both legs and H5 on the signal decisions too and report them next to the random ones.

**2026-11-18, later in the afternoon, before any test day is touched. Corrections and gaps found on a second read.**
- *Correction to the 2026-11-17 entry.* The flag for small displayed size fires on 0.13% (at 5 ms) to 0.31% (at 500 ms) of decisions, not 0.17% to 0.31%. The lower end was misread from `flagged_share_by_delay_ms` in `results/taker/taker_dev_2026-09-01.json`. The conclusion of that entry does not change.
- *Event order inside one update.* The text above says trades, then cancellations, then additions inside one book update. The passive code does not do that. It applies trades from the trade feed first and then compares the displayed size at my price with the size it tracks, so each book update contributes one net change. An addition and a cancellation inside the same update offset each other and are never applied separately. I keep the code as it is and report this as a limit.
- *End of day.* The decision generator drops every decision in the last 600 s of the day, which keeps the horizon and the markouts inside the file. This was not written down before.
- *Tie rule.* Decision times are drawn in microseconds and book stamps are whole milliseconds, so the tie flip changes the arrival book for only 6 of 8,425 dev day decisions (`results/taker/tie_share_dev_2026-09-01.json`). As built, robustness item 2 is a weak check and will be reported as one. The passive leg has no working tie flip yet.
- *H1b.* The 100 ms latency cost contains part of the 1 s move that defines the H1b groups, so the split is partly mechanical. H1b stays as registered and is reported with that caveat.
- *H2c source.* H2c rests on the abstract of Yueshen (2026), which states that end of queue limit orders always lose money. The full text had not been read when the hypothesis was written.

**2026-11-18, after reading Yueshen (2026) in full, before any test day is touched.** H2c says that fills at 500 ms have worse 10 s markouts than fills at 1 ms. The paper does not say this. It has no markout horizon and no delay in milliseconds. What it shows is that in equilibrium end of queue orders lose money and that deeper units which fill are more likely to meet an informed market order (Lemma 1, Proposition 1). The delay to markout prediction is my own inference motivated by that result. The test itself is unchanged, and it will be reported as my inference rather than as a test of the paper.

**2026-11-19 morning, before the latency test and before any test day.** The latency script first read the smallest quantity from the asset listing (0.000015986 BTC). The paper venue refuses anything under 10 USD of cost, so my first three attempts came back as HTTP 403 and no order was created. I changed the quantity rule to the smallest quantity that clears 10 USD at each order's limit price, which is what "smallest quantity the venue accepts" means in practice. Count, spacing, price rule and venue are unchanged. The three refused calls are not part of the 200 and the script runs from the start.

**2026-11-19 10:20, before any test day.** The first full run stopped at order 13 when the public quote call returned no quote and my script did not handle it. 13 orders had been sent and cancelled, all acknowledged with HTTP 200 at about 250 to 280 ms. I added up to four tries for the quote and a count of orders skipped for lack of a quote, and I am rerunning all 200 from the start. Those 13 are not part of the result. Count, spacing, price rule and venue are unchanged.

# 01.b Preregistration

Written 2026-11-22, after 01 was released and before any 01.b day was downloaded or opened. The commit that adds this file is the timestamp. The data script for 01.b refuses to fetch a listed day until this file is in git history.

## Why 01.b exists
01 was a preregistered test of whether execution delay costs money on orders placed at random moments. Its primary tests came out null on both test days and on the six breadth days, and by design they could hardly have shown a cost. Two results that were not primary did look real.

1. Signal decisions, secondary in 01. On decisions taken at extreme top of book imbalance, the five level walk slope of ΔS on log delay was between 0.068<!--c:prior.sig.slope.min--> and 0.113<!--c:prior.sig.slope.max--> bps per log ms across the eight test and breadth days. Mean shortfall went from between 0.041<!--c:prior.sig.S1.min--> and 0.085<!--c:prior.sig.S1.max--> bps at 1 ms to between 0.47<!--c:prior.sig.S500.min--> and 0.76<!--c:prior.sig.S500.max--> bps at 500 ms.
2. Fixed price passive without the orders marketable on arrival, exploratory in 01. The slope was above zero with its interval above zero under all three cancellation rules on both test days, from 0.0010<!--c:prior.fpx.min--> to 0.0058<!--c:prior.fpx.max--> bps per log ms.

My rule for a promising secondary or exploratory result is one deeper check. The rules are written first, the data is unseen, and it runs once. 01.b is that check and nothing more. If a result holds it becomes a finding. If it fails it is reported and dropped.

## What I had seen when I wrote this
Everything in 01, including all results on 2026-09-01 (dev), 2026-10-01 and 2026-11-01 (test) and the six breadth days 2026-03-01 to 2026-08-01. Nothing from any day listed under Data below, apart from 2026-09-01, which is the 01 dev day.

## Data
Tardis free CSVs only cover the first day of each month. CryptoStruct sells full Binance USDT-M days (every trade, L2 book feed and top of book, exchange timestamps) at 1 EUR per instrument day, with coverage from February 2021. Bybit publishes daily ob500 book and trade files for free. All three read on their own sites on 2026-11-20.

The twelve test days follow a rule fixed before purchase. Each is the Wednesday closest to the 15th of each month from December 2025 to November 2026. If that day is a listed exchange incident day or the seller shows a data notice for it, the Thursday after is used. The seller shows a notice for 2026-06-17 (most files start between about 01:00 and 14:00 UTC), so 2026-06-18 replaces it. If 2026-06-18 also shows a notice at purchase, that month is left out and reported.

| Role | Data | Days |
|---|---|---|
| Build | Tardis BTCUSDT 2026-09-01 (the 01 dev day), plus the CryptoStruct file for the same day to build the new loader and check it against Tardis | 2026-09-01 only |
| Test | CryptoStruct Binance USDT-M BTCUSDT, one mid month weekday per month | 2025-12-17, 2026-01-14, 2026-02-18, 2026-03-18, 2026-04-15, 2026-05-13, 2026-06-18, 2026-07-15, 2026-08-12, 2026-09-16, 2026-10-14, 2026-11-18 |
| Stress day, secondary | CryptoStruct free sample, Binance USDT-M BTCUSDT, labelled by the seller as a high volatility Bitcoin day | 2026-07-06, reported alone and never in a verdict, since it was picked for its volatility |
| Extra recent day, secondary | CryptoStruct free rolling sample, Binance USDT-M BTCUSDT | 2026-11-13, reported alone and not in a verdict, since it sits outside the Wednesday rule |
| First of month, secondary | Tardis free BTCUSDT | Twelve unused days, 2025-03-01 to 2026-02-01 |
| Out of asset, secondary | Tardis free ETHUSDT | The same twelve first of month days |
| Out of venue, secondary | Bybit BTCUSDT linear, free ob500 and trades | The same twelve test days |

CryptoStruct days older than about a month sit in cold storage and take about twelve hours to restore, so I buy the twelve test days and the 2026-09-01 build file (EUR 13) right after this commit. The two free samples were saved to my Drive on 2026-11-20 and not opened. They are copied in only after this commit. If the CryptoStruct days can't be bought, the twelve Tardis first of month days become the test set, and that goes under Deviations before any of them is opened.

A day is left out only if its download fails or its gaps over 1 s add up to more than one hour. This is done in code, and every day left out is reported. If fewer than ten test days survive, the verdicts below are reported as underpowered.

## Where the files came from
Every 01.b data file gets a SHA256 checksum written to `data/MANIFEST.md` when it first lands, with its source and the date. That manifest is committed after this file, so the history shows no test file was in hand before the rules were. On the build day, the CryptoStruct and Tardis files for 2026-09-01 are compared before anything else is built. I compare trade count, first and last trade, and the share of trades that match on time, price and size. The loader is used only if they agree, and how well they agree is reported either way.

## Frozen from 01
Everything not listed as a change is the 01 code at tag v0.1-signal-to-fill. Signal threshold |I| at or above 0.98630194<!--c:prior.threshold-->, computed on the 01 dev day and frozen for BTCUSDT. Delay grid {1, 2, 5, 10, 25, 50, 100, 250, 500} ms, 1 ms baseline, cautious tie rule primary. Order size 0.01 BTC. 5 minute block bootstrap, 2,000 resamples, seed 20261115, 95% percentile interval. Fees 2 bps maker and 5 bps taker in the fee check. Three cancellation rules.

For ETHUSDT the threshold is the 90th percentile of |I| on ETHUSDT 2026-09-01, computed once and stored before any other ETHUSDT day is downloaded. The ETHUSDT order size is the same notional as 0.01 BTC on 2026-09-01, stored with the threshold.

## C1 Signal decisions pay for delay (primary)
Statistic: on signal decisions, the slope of walk ΔS(d) on log d, per day.

C1 holds on BTCUSDT if the slope interval is above zero on at least 10 of the surviving test days and below zero on none, and the mean walk ΔS(500 ms) is at least 0.1 bps on at least 10 of the surviving test days. Otherwise C1 is reported as not holding, with the counts.

Also reported per day, as description, is the drift and arrival cost split of ΔS(500 ms), so a reader can see how much is the predicted move happening while the order waits and how much is the book thinning at arrival.

## C2 Fixed price passive without marketable orders (primary)
Statistic: the H5 slope of post then cross cost on log d, with every decision that is marketable on arrival at any delay left out, as coded in 01. Random decisions, all three cancellation rules.

C2 holds on BTCUSDT if under each of the three rules the slope interval is above zero on at least 10 of the surviving test days and below zero on none. Otherwise it is reported as not holding. Which decisions drop depends on delay, so even if C2 holds it is stated as a description of these orders, not as a causal effect of delay.

## Secondary
- C1 and C2 on ETHUSDT with the same rules, on the first of month days. Reported next to BTCUSDT and never pooled into a verdict.
- C1 and C2 on the twelve Tardis first of month BTCUSDT days and on Bybit, each reported on its own.
- Race sensitivity for C1, built on 2026-09-01 before any test day is downloaded. A pessimistic version in which my order, at each delay, only gets the arrival touch if it is still there 1 ms after arrival, and otherwise walks the book as it stands then. It bounds how much of C1 could come from the replay having no race, and is reported as a range next to C1.
- The tie rule flip, fees, 15 minute blocks and the shuffle placebo for C1 and C2, as in 01.

## Multiple testing
Two primary statements on one asset, each needing 10 of 12 days. A slope with no real effect would rarely clear 10 of 12 one sided intervals by luck, so I don't add a further correction. That is a choice, stated here.

## Changes to the code from v0.1, all built on 2026-09-01 before any test day is downloaded
1. A runner for 01.b that accepts only the listed days, refuses reruns, writes the gap rule decision into each day's audit, and refuses ETHUSDT days until every BTCUSDT test day has run.
2. A loader for CryptoStruct files, checked against Tardis as above.
3. The race sensitivity above.
4. ETHUSDT and Bybit symbol support, with the threshold and size as above.

Nothing else changes. No parameter, window, threshold or sample is chosen or changed after any test day output exists.

## Known limits stated in advance
- One venue for the verdicts. Bybit is a second venue but only secondary.
- The replay still has no real race. The race sensitivity bounds this, it doesn't remove it.
- Signal decisions are chosen at extreme imbalance, so C1 measures the cost of waiting on a signal that already predicts the move. It says nothing about weaker signals.
- The build day is the 01 dev day, so it isn't new.
- The secondary first of month days include four weekends (2025-03-01, 2025-06-01, 2025-11-01 and 2026-02-01) and New Year's Day (2026-01-01).
- A paid Tardis month would give every day of a month instead of one day per month. That is out of budget for now.

## Deviations

### 2026-11-22. Two more extra recent days
The free CryptoStruct folder also holds 2026-11-14 and 2026-11-15, and I've decided to use them. They go in exactly like 2026-11-13. Each is reported alone and never in a verdict, since they also sit outside the Wednesday rule. 2026-11-14 is a Saturday and 2026-11-15 is a Sunday, so they're also weekend days. I'm adding this before any of the three recent days, or any test day, is opened. Nothing else changes. The runner's list of allowed days adds these two.

### 2026-11-23. Details the text left open, fixed on the build day
Written on 2026-11-23 while building on 2026-09-01, before the CryptoStruct and Tardis trades for that day were compared and before any test day was downloaded. None of them changes a rule above. They pin down choices the text didn't make, so the code can't make them later.

1. When the loader agrees with Tardis. On 2026-09-01, at least 99% of Tardis trades have a CryptoStruct trade with the same exchange time, price and size, and at least 99% of CryptoStruct trades have a Tardis match. Each trade is matched once at most. If either share is below 99%, I don't use the loader, I write down why, and I decide what to do before any test day is opened.
2. The day. A CryptoStruct file starts a few minutes before midnight and ends just after the next one. I keep the rows received between 00:00 and 24:00 UTC, the way Tardis cuts its files by capture time. The book is built from the first snapshot in the file, so it is already full at midnight.
3. Five levels. CryptoStruct has no five level file, so the five levels come from its depth stream. A row is written each time the top five on either side change. Where the event chain breaks or the feed reports an error, no row is written until the next full snapshot. Top of book comes from its own top of book stream, as in the Tardis files.
4. The gap rule in code. For each day I add up every gap over 1 s between top of book rows on capture time, plus the stretch from 00:00 to the first row and from the last row to 24:00 if either is over 1 s. If the total is over 3600 s the day is left out. The total and the decision go into the day's audit file. The same rule applies to every source.
5. ETHUSDT size. 0.01 BTC times the median BTCUSDT top of book mid on 2026-09-01, divided by the median ETHUSDT mid that day, rounded to the 0.001 ETH lot. It is stored with the ETHUSDT threshold.
6. Bybit. The threshold is the frozen BTCUSDT value, since the text freezes it for BTCUSDT and Bybit's is BTCUSDT too. Bybit's free book file has no separate top of book stream, so top of book and the five levels both come from its 500 level book, and trades from its trade file. Fees stay at 2 and 5 bps as above, although Bybit's base taker fee is a little higher.
7. Race sensitivity. For a signal decision at delay d, the arrival touch counts only if, 1 ms after arrival, the opposite side's best price is the same and shows at least my size. Otherwise the order walks the ticker touch and the five levels as they stand 1 ms after arrival. ΔS under this rule uses its own 1 ms baseline. The C1 slope and mean ΔS(500 ms) are reported under it next to the primary numbers, with the share of cells it changed.
8. The drift and arrival split. Drift(d) is the move of the mid from t to t plus d, signed by side, in bps of the mid at t. Arrival(d) is the walk shortfall minus drift. The split of ΔS(500 ms) is the mean change of each from 1 ms to 500 ms.
9. The secondary checks for C1 and C2. The tie flip reruns both under the other tie rule. Fees add 5 bps to every walk fill for C1, and maker or taker fees by filled share for C2, as in 01. The 15 minute blocks only change the bootstrap. The placebo shuffles the delay labels within each decision with 01's draws (seed 20261116), on the walk ΔS for C1 and on the kept decisions' cost for C2.

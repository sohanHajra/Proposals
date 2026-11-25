# 01.b Signal Cost Confirm

A sequel to [01 From Signal to Fill](../01-signal-to-fill/). Two things in 01 looked real but weren't its main tests. A taker acting on top of book imbalance paid more the longer its order took to reach the book, and a fixed price passive order looked costlier with delay once the orders marketable on arrival were left out. 01.b checks both once, on twelve days I haven't seen, with the rules written first.

## Status

🟢 Released 2026-11-25. C1 and C2 both hold on the twelve test days.

- [Preregistration](PREREGISTRATION.md)
- [Lab notebook](LAB_NOTEBOOK.md)
- [Integrity log](INTEGRITY_LOG.md)

## Bottom line

Both leads hold on the twelve CryptoStruct BTCUSDT test days, under the rules I wrote before opening any of them.

- **C1 holds.** A taker acting on extreme imbalance pays more the longer its order takes. The slope interval is above zero on 12<!--c:test.c1.above--> of 12<!--nc--> days. Slopes run 0.077<!--c:test.c1.slope.min--> to 0.110<!--c:test.c1.slope.max--> bps per log ms, and the extra cost at 500<!--nc--> ms is 0.48<!--c:test.c1.dS500.min--> to 0.68<!--c:test.c1.dS500.max--> bps. All of it comes from the predicted move happening while the order waits. The book at arrival takes a hair back.
- **C2 holds, but only just under back.** Among the passive orders kept, with the ones marketable on arrival left out, cost is higher at longer delays. Under front and random every day is above zero. Under back 11<!--c:test.c2.back.above--> days are, and 2026-02-18 covers zero. Back is the smallest effect on every day, and its intervals are probably a little too narrow.

C2 is small. From 1<!--nc--> ms to 500<!--nc--> ms it adds 0.021<!--c:chk.c2.scale.front.min--> to 0.090<!--c:chk.c2.scale.front.max--> bps under front and 0.009<!--c:chk.c2.scale.back.min--> to 0.028<!--c:chk.c2.scale.back.max--> bps under back, next to fees of 2<!--nc--> and 5<!--nc--> bps. It also describes these orders rather than a causal effect of delay, because which orders get left out depends on delay.

## Results on the test days

No day was left out by the gap rule, so all 12<!--c:chk.days--> test days count, and no C1 or C2 interval is below zero on any of them. The registered checks sit next to the main numbers.

| C1 version | Slope, bps per log ms | Extra cost at 500<!--nc--> ms, bps | Days above zero |
|---|---|---|---|
| Main | 0.077<!--c:chk.c1.walk.min--> to 0.110<!--c:chk.c1.walk.max--> | 0.48<!--c:chk.c1.walk.ds.min--> to 0.68<!--c:chk.c1.walk.ds.max--> | 12<!--c:chk.c1.walk.above--> |
| Race rule | 0.073<!--c:chk.c1.race.min--> to 0.103<!--c:chk.c1.race.max--> | 0.45<!--c:chk.c1.race.ds.min--> to 0.62<!--c:chk.c1.race.ds.max--> | 12<!--c:chk.c1.race.above--> |
| Other tie rule | 0.082<!--c:chk.c1.tie.min--> to 0.117<!--c:chk.c1.tie.max--> | 0.51<!--c:chk.c1.tie.ds.min--> to 0.71<!--c:chk.c1.tie.ds.max--> | 12<!--c:chk.c1.tie.above--> |

The race rule gives my order the touch only if it's still there 1<!--nc--> ms after arrival. It's a sensitivity, not a bound. It changes 9%<!--c:chk.c1.race.changed.min--> to 12%<!--c:chk.c1.race.changed.max--> of cells, 8.6%<!--c:chk.c1.race.worse.min--> to 11.7%<!--c:chk.c1.race.worse.max--> for the worse and 0.40%<!--c:chk.c1.race.better.min--> to 0.73%<!--c:chk.c1.race.better.max--> for the better, and takes a little off C1. The 15<!--nc--> minute blocks only change the intervals, and every day stays above zero. The fee check adds a flat 5<!--nc--> bps that cancels in ΔS, so it isn't a check on C1. It only moves the level, and mean S at 500<!--nc--> ms with fees is 5.54<!--c:chk.c1.fees.min--> to 5.75<!--c:chk.c1.fees.max--> bps. The C1 placebo covers zero on all 12<!--c:chk.c1.placebo--> days. It's read on the slope only. The level field next to it in the results files isn't recentred after the shuffle, so it doesn't mean anything as a placebo.

**Where the C1 cost comes from.** Drift is the mid moving while the order waits. Arrival is what the book adds or takes away when it gets there. Drift is larger than the whole ΔS on all 12<!--c:chk.c1.drift.above--> days.

| Day | ΔS at 500<!--nc--> ms, bps | Drift | Arrival |
|---|---|---|---|
| 2025-12-17 | 0.631<!--c:split.d20251217.ds--> | 0.654<!--c:split.d20251217.drift--> | -0.023<!--c:split.d20251217.arr--> |
| 2026-01-14 | 0.543<!--c:split.d20260114.ds--> | 0.564<!--c:split.d20260114.drift--> | -0.021<!--c:split.d20260114.arr--> |
| 2026-02-18 | 0.606<!--c:split.d20260218.ds--> | 0.635<!--c:split.d20260218.drift--> | -0.029<!--c:split.d20260218.arr--> |
| 2026-03-18 | 0.638<!--c:split.d20260318.ds--> | 0.658<!--c:split.d20260318.drift--> | -0.020<!--c:split.d20260318.arr--> |
| 2026-04-15 | 0.551<!--c:split.d20260415.ds--> | 0.565<!--c:split.d20260415.drift--> | -0.014<!--c:split.d20260415.arr--> |
| 2026-05-13 | 0.484<!--c:split.d20260513.ds--> | 0.496<!--c:split.d20260513.drift--> | -0.011<!--c:split.d20260513.arr--> |
| 2026-06-18 | 0.676<!--c:split.d20260618.ds--> | 0.693<!--c:split.d20260618.drift--> | -0.017<!--c:split.d20260618.arr--> |
| 2026-07-15 | 0.493<!--c:split.d20260715.ds--> | 0.509<!--c:split.d20260715.drift--> | -0.016<!--c:split.d20260715.arr--> |
| 2026-08-12 | 0.525<!--c:split.d20260812.ds--> | 0.537<!--c:split.d20260812.drift--> | -0.012<!--c:split.d20260812.arr--> |
| 2026-09-16 | 0.623<!--c:split.d20260916.ds--> | 0.637<!--c:split.d20260916.drift--> | -0.014<!--c:split.d20260916.arr--> |
| 2026-10-14 | 0.543<!--c:split.d20261014.ds--> | 0.556<!--c:split.d20261014.drift--> | -0.014<!--c:split.d20261014.arr--> |
| 2026-11-18 | 0.639<!--c:split.d20261118.ds--> | 0.656<!--c:split.d20261118.drift--> | -0.017<!--c:split.d20261118.arr--> |

| C2 | Front | Random | Back |
|---|---|---|---|
| Days above zero, main | 12<!--c:chk.c2.main.front--> | 12<!--c:chk.c2.main.random--> | 11<!--c:chk.c2.main.back--> |
| Days above zero, with fees | 12<!--c:chk.c2.fees.front--> | 12<!--c:chk.c2.fees.random--> | 11<!--c:chk.c2.fees.back--> |
| Days above zero, other tie rule | 12<!--c:chk.c2.tie.front--> | 12<!--c:chk.c2.tie.random--> | 11<!--c:chk.c2.tie.back--> |
| Days above zero, 15<!--nc--> minute blocks | 12<!--c:chk.c2.b15.front--> | 12<!--c:chk.c2.b15.random--> | 11<!--c:chk.c2.b15.back--> |
| Placebo covers zero | 12<!--c:chk.c2.plac.front--> | 12<!--c:chk.c2.plac.random--> | 10<!--c:chk.c2.plac.back--> |

The other tie rule gives exactly the main numbers on 10<!--c:chk.c2.tie.same--> of 12<!--nc--> days, because random decisions fall between whole milliseconds and rarely tie with the book. So its row isn't much of a check on C2. The two placebo misses under back sit on opposite sides of zero. On the build day the placebo already missed too often under back, so I can't read much into them. The notebook has a rough, exploratory look at how much that matters.

## Secondary days

None of these is in the verdict. Each source and each CryptoStruct day is reported on its own. A 1<!--nc--> means the day passes that claim's day rule.

| CryptoStruct day | C1 | C2 front | C2 random | C2 back |
|---|---|---|---|---|
| 2026-07-06, stress day | 1<!--c:sec.cs.0706.c1--> | 1<!--c:sec.cs.0706.front--> | 1<!--c:sec.cs.0706.random--> | 1<!--c:sec.cs.0706.back--> |
| 2026-11-13 | 1<!--c:sec.cs.1113.c1--> | 1<!--c:sec.cs.1113.front--> | 1<!--c:sec.cs.1113.random--> | 1<!--c:sec.cs.1113.back--> |
| 2026-11-14, Saturday | 1<!--c:sec.cs.1114.c1--> | 1<!--c:sec.cs.1114.front--> | 1<!--c:sec.cs.1114.random--> | 0<!--c:sec.cs.1114.back--> |
| 2026-11-15, Sunday | 1<!--c:sec.cs.1115.c1--> | 1<!--c:sec.cs.1115.front--> | 1<!--c:sec.cs.1115.random--> | 0<!--c:sec.cs.1115.back--> |

| Source | Days | C1 | C2 front | C2 random | C2 back |
|---|---|---|---|---|---|
| Tardis BTCUSDT, first of month | 12<!--c:sec.tz.days--> | 12<!--c:sec.tz.c1--> | 12<!--c:sec.tz.front--> | 11<!--c:sec.tz.random--> | 10<!--c:sec.tz.back--> |
| Tardis ETHUSDT, first of month | 12<!--c:sec.eth.days--> | 12<!--c:sec.eth.c1--> | 12<!--c:sec.eth.front--> | 11<!--c:sec.eth.random--> | 10<!--c:sec.eth.back--> |
| Bybit BTCUSDT, on the twelve test dates | 12<!--c:sec.by.days--> | 12<!--c:sec.by.c1--> | 10<!--c:sec.by.front--> | 5<!--c:sec.by.random--> | 5<!--c:sec.by.back--> |
| Bybit, frozen Binance threshold | 12<!--c:sec.by.days--> | 12<!--c:sec.by.frozen.holds--> | not rerun | not rerun | not rerun |

C1 shows up on every secondary day. Bybit's slopes are 0.039<!--c:sec.by.c1.min--> to 0.060<!--c:sec.by.c1.max--> under its own threshold and 0.047<!--c:sec.by.frozen.min--> to 0.065<!--c:sec.by.frozen.max--> under the frozen one, higher on all 12<!--c:sec.by.frozen.higher--> days. So the threshold change I made after seeing Bybit's build day made Bybit's C1 smaller, not bigger. No C2 slope estimate is below zero on any secondary day, but C2 thins out under back, and on Bybit most intervals cover zero under random and back. C2 uses random decisions, so Bybit's threshold doesn't touch it. Bybit's book moves in steps of about 100<!--nc--> ms and its placebo was already off. Across all secondary days 7<!--c:sec.plac.miss--> of 160<!--c:sec.plac.n--> placebo intervals miss zero. They all reuse one seed, so they aren't 160<!--c:sec.plac.n--> separate draws and I don't compare the count with chance.

## Limits

- The verdict is one venue, one symbol and one day a month for a year.
- The replay still has no real race for the touch. The race rule is a sensitivity, not a bound.
- C1 is the cost of waiting on a signal that already predicts the move. It says nothing about weaker signals.
- C2 is a description of the orders kept, not a causal effect, and it is small.
- The C2 placebo is off under back on CryptoStruct and under every rule on Bybit, so it can't back C2 there. The likely cause is the 5<!--nc--> minute block interval running a little narrow on those arrays.
- Bybit's book changes about every 100<!--nc--> ms, so it says little about delays below that.
- I changed Bybit's threshold after seeing its build day. Both versions ran on every test day.

The preregistration and the notebook list the rest.

## How to rerun

From this folder, `make env` builds the 01 environment this reuses, `make test` runs the tests and `make verify` checks every number here against its results file. A listed day reruns one step at a time with `make next SRC=cryptostruct SYM=BTCUSDT DAY=2026-01-14`, and `make status` shows where it is. The data files aren't in the repo. data/MANIFEST.md says where each comes from and gives its checksum.

Dates in the notes are US Central. Commit times on GitHub are UTC.

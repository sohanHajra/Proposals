# 01.b Signal Cost Confirm

A sequel to [01 From Signal to Fill](../01-signal-to-fill/). Two things in 01 looked real but weren't its main tests. A taker acting on top of book imbalance paid more the longer its order took to reach the book, and a fixed price passive order looked costlier with delay once the orders marketable on arrival were left out. 01.b checks both once, on twelve days I haven't seen, with the rules written first.

## Status

🟡 Test days and secondary days run. Write up in progress, not released.

- [Preregistration](PREREGISTRATION.md)
- [Lab notebook](LAB_NOTEBOOK.md)
- [Integrity log](INTEGRITY_LOG.md)

## Bottom line

Both leads hold on the twelve CryptoStruct BTCUSDT test days, under the rules I wrote before opening any of them.

- **C1 holds.** A taker acting on extreme imbalance pays more the longer its order takes. The slope interval is above zero on 12<!--c:test.c1.above--> of 12<!--nc--> days. Slopes run 0.077<!--c:test.c1.slope.min--> to 0.110<!--c:test.c1.slope.max--> bps per log ms, and the extra cost at 500<!--nc--> ms is 0.48<!--c:test.c1.dS500.min--> to 0.68<!--c:test.c1.dS500.max--> bps.
- **C2 holds, but only just under back.** A fixed price passive order, with the orders marketable on arrival left out, costs more with delay. Under front and random every day is above zero. Under back 11<!--c:test.c2.back.above--> days are, and 2026-02-18 covers zero. Back is the smallest effect on every day, and its intervals are probably a little too narrow.

C2 describes these orders. It isn't a causal effect of delay, because which orders get left out depends on delay.

## Results on the test days

The registered checks next to the main numbers, across the 12<!--c:chk.days--> test days.

| C1 version | Slope, bps per log ms | Extra cost at 500<!--nc--> ms, bps | Days above zero |
|---|---|---|---|
| Main | 0.077<!--c:chk.c1.walk.min--> to 0.110<!--c:chk.c1.walk.max--> | 0.48<!--c:chk.c1.walk.ds.min--> to 0.68<!--c:chk.c1.walk.ds.max--> | 12<!--c:chk.c1.walk.above--> |
| Race rule | 0.073<!--c:chk.c1.race.min--> to 0.103<!--c:chk.c1.race.max--> | 0.45<!--c:chk.c1.race.ds.min--> to 0.62<!--c:chk.c1.race.ds.max--> | 12<!--c:chk.c1.race.above--> |
| Other tie rule | 0.082<!--c:chk.c1.tie.min--> to 0.117<!--c:chk.c1.tie.max--> | 0.51<!--c:chk.c1.tie.ds.min--> to 0.71<!--c:chk.c1.tie.ds.max--> | 12<!--c:chk.c1.tie.above--> |

The race rule is the pessimistic one, where my order only gets the touch if it's still there 1<!--nc--> ms after arrival. It changes 9%<!--c:chk.c1.race.changed.min--> to 12%<!--c:chk.c1.race.changed.max--> of cells and takes a little off C1, not much. The 15<!--nc--> minute blocks only change the intervals, and every day stays above zero. The fee check adds a flat 5<!--nc--> bps that cancels in ΔS, so it isn't a check on C1. The C1 placebo covers zero on all 12<!--c:chk.c1.placebo--> days.

| C2 | Front | Random | Back |
|---|---|---|---|
| Days above zero, main | 12<!--c:chk.c2.main.front--> | 12<!--c:chk.c2.main.random--> | 11<!--c:chk.c2.main.back--> |
| Days above zero, with fees | 12<!--c:chk.c2.fees.front--> | 12<!--c:chk.c2.fees.random--> | 11<!--c:chk.c2.fees.back--> |
| Days above zero, 15<!--nc--> minute blocks | 12<!--c:chk.c2.b15.front--> | 12<!--c:chk.c2.b15.random--> | 11<!--c:chk.c2.b15.back--> |
| Days above zero, other tie rule | 12<!--c:chk.c2.tie.front--> | 12<!--c:chk.c2.tie.random--> | 11<!--c:chk.c2.tie.back--> |
| Placebo covers zero | 12<!--c:chk.c2.plac.front--> | 12<!--c:chk.c2.plac.random--> | 10<!--c:chk.c2.plac.back--> |

The two placebo misses under back sit on opposite sides of zero. On the build day the placebo already missed too often under back, so I can't read much into them. The notebook has a rough, exploratory look at how much that matters.

## Secondary days

None of these is in the verdict. Each source is reported on its own.

| Source | Days | C1 | C2 front | C2 random | C2 back |
|---|---|---|---|---|---|
| CryptoStruct stress and recent | 4<!--c:sec.cs.days--> | 4<!--c:sec.cs.c1--> | 4<!--c:sec.cs.front--> | 4<!--c:sec.cs.random--> | 2<!--c:sec.cs.back--> |
| Tardis BTCUSDT, first of month | 12<!--c:sec.tz.days--> | 12<!--c:sec.tz.c1--> | 12<!--c:sec.tz.front--> | 11<!--c:sec.tz.random--> | 10<!--c:sec.tz.back--> |
| Tardis ETHUSDT, first of month | 12<!--c:sec.eth.days--> | 12<!--c:sec.eth.c1--> | 12<!--c:sec.eth.front--> | 11<!--c:sec.eth.random--> | 10<!--c:sec.eth.back--> |
| Bybit BTCUSDT, test days | 12<!--c:sec.by.days--> | 12<!--c:sec.by.c1--> | 10<!--c:sec.by.front--> | 5<!--c:sec.by.random--> | 5<!--c:sec.by.back--> |

C1 shows up on every secondary day, on the Tardis first of month days, on ETHUSDT and on Bybit. No C2 slope estimate is below zero on any of them, but C2 thins out under back and is mostly lost in the noise on Bybit, where the book moves in steps of about 100<!--nc--> ms and the placebo was already off.

## Limits

- The verdict is one venue, one symbol and one day a month for a year.
- The replay still has no real race for the touch. The race rule is a sensitivity, not a bound.
- C1 is the cost of waiting on a signal that already predicts the move. It says nothing about weaker signals.
- C2 is a description of the orders kept, not a causal effect.
- The C2 placebo is off under back on CryptoStruct and under every rule on Bybit, so it can't back C2 there.
- Bybit's book changes about every 100<!--nc--> ms, so it says little about delays below that.
- I changed Bybit's threshold after seeing its build day. Both versions ran on every test day.

The preregistration and the notebook list the rest.

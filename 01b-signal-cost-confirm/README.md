# 01.b Signal Cost Confirm

A sequel to [01 From Signal to Fill](../01-signal-to-fill/). Two things in 01 looked real but weren't its main tests. A taker acting on top of book imbalance paid more the longer its order took to reach the book, and a fixed price passive order looked costlier with delay once the orders marketable on arrival were left out. 01.b checks both once, on twelve days I haven't seen, with the rules written first.

## Status

🟡 Preregistered 2026-11-22 Central time (the commit reads 2026-11-23 01:45 UTC). Loader, runner, race rule, ETHUSDT and Bybit readers built on 2026-09-01 on 2026-11-23. The twelve test days ran on 2026-11-23. C1 and C2 both hold on CryptoStruct BTCUSDT, with C2 weakest under the back rule. Secondary sources and the write up are still to come.

- [Preregistration](PREREGISTRATION.md)
- [Lab notebook](LAB_NOTEBOOK.md)
- [Integrity log](INTEGRITY_LOG.md)

## Limits

Still one venue for the verdicts, and the replay still has no race for the touch. Bybit's free book only changes about every 100 ms, so it says little about delays below that. The preregistration lists the rest.

# Prior art

What is already known, and where this project tries to add something. Every entry was checked against the publisher or author page on 2026-11-14.

| Work | What it establishes | What it leaves open for this project |
|---|---|---|
| Perold (1988), *The Implementation Shortfall: Paper versus Reality*, Journal of Portfolio Management | Decision-price benchmark for execution cost | The metric used here (signed shortfall vs decision mid) |
| Almgren & Chriss (2001), *Optimal Execution of Portfolio Transactions*, Journal of Risk 3:5-40 | Impact vs risk trade-off in execution | Not about latency; context only |
| Moallemi & Sağlam (2013), *The Cost of Latency in High-Frequency Trading*, Operations Research 61(5):1070-1086, [doi:10.1287/opre.2013.1165](https://doi.org/10.1287/opre.2013.1165) | Closed-form cost of latency in a stylised model, calibrated on equities | Model-based; does not decompose drift vs queue loss on raw book data |
| Hasbrouck & Saar (2013), *Low-latency trading*, Journal of Financial Markets 16(4):646-679, [doi:10.1016/j.finmar.2013.05.003](https://doi.org/10.1016/j.finmar.2013.05.003) | Millisecond strategic runs measured from Nasdaq message data | Market-quality focus, not per-order execution cost |
| Budish, Cramton & Shim (2015), *The High-Frequency Trading Arms Race*, QJE 130(4):1547-1621, [doi:10.1093/qje/qjv027](https://doi.org/10.1093/qje/qjv027) | Speed races create sniping costs for stale quotes | Motivates RQ3 (cost concentrated in "race" moments) |
| Moallemi & Yuan (2017), *A Model for Queue Position Valuation in a Limit Order Book*, SSRN 2996221 | Queue position has economic value, large for large-tick assets | The passive leg here measures queue loss empirically per ms of delay |
| Cartea & Sánchez-Betancourt (2021), *The Shadow Price of Latency*, SIAM J. Financial Math 12(1), [doi:10.1137/19M1258888](https://doi.org/10.1137/19M1258888) | Latency-driven missed fills in FX, concentrated in high volatility | Taker side only; proprietary LMAX data |
| Cartea & Sánchez-Betancourt (2023), *Optimal execution with stochastic delay*, Finance and Stochastics, [doi:10.1007/s00780-022-00491-w](https://doi.org/10.1007/s00780-022-00491-w) | Optimal marketable limit orders under random latency | Theory plus FX data |
| *The good, the bad, and latency: exploratory trading on Bybit and Binance* (2025), Quantitative Finance 25(6), [doi:10.1080/14697688.2025.2515933](https://doi.org/10.1080/14697688.2025.2515933) | Live experiment: millions of taker orders on Binance/Bybit; slippage vs snapshot tied to volatility, latency, liquidity; adverse selection for takers | **Closest prior work.** Live, taker-only, one realised latency per order. This project instead replays the *same* decision across a controlled delay grid using only public data, adds the passive leg, and splits cost into drift vs queue loss |

## What is new here (claimed modestly)
1. A paired counterfactual design: identical decision moments at 0 to 500 ms, so the latency effect is not confounded by when slow orders happen to occur.
2. A decomposition of latency cost into price drift and queue-position loss, on public data anyone can rerun.
3. A test of whether latency cost is a tail phenomenon (RQ3) rather than a mean shift.

## Known gap
I have not yet read the full text of the 2025 Quantitative Finance paper (abstract only). If it already does a paired replay, claim 1 is withdrawn and the log will say so.

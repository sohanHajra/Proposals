# 01 · From Signal to Fill

> When market conditions are similar, do orders that take longer to reach an outcome receive worse prices or fill less often?

| | |
|---|---|
| Status | 🟡 Preregistered. Replay engine, taker grid, passive leg and the fixed price passive arm built and previewed on the dev day only. Test days not yet run |
| Preregistration | [PREREGISTRATION.md](PREREGISTRATION.md) |
| Proposal | [PROPOSAL.md](PROPOSAL.md) |
| Literature review | [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md) |
| Lab notebook | [LAB_NOTEBOOK.md](LAB_NOTEBOOK.md) |
| Reproduce | `make reproduce` |

## From proposal to experiment
This section is added here and is not part of the proposal, which is kept as written. Public data has no decision timestamps for anyone's orders, so the experiment splits the question in two.
1. **Counterfactual replay (simulated).** Take a decision moment from real Binance USD-M BTCUSDT data and replay *the same* decision at several injected delays. Market conditions are identical across delays by construction.
2. **Real order lifecycles (observational).** LOBSTER's Nasdaq message files carry order IDs, so the third stage (acknowledgement to fill or cancel) is observable for real orders, though decision time is not.

The full design and its pass and fail rules are in [PREREGISTRATION.md](PREREGISTRATION.md). Everything that went wrong is in [LAB_NOTEBOOK.md](LAB_NOTEBOOK.md).

## The three stages of delay

```mermaid
sequenceDiagram
    participant S as Strategy
    participant X as Exchange
    participant B as Order book
    Note over S: decision (mid observed)
    S->>X: send order
    Note over S,X: stages 1 and 2, decision → ack<br/>(software + network)
    X->>B: acknowledged, rests in queue
    Note over X,B: stage 3, ack → fill or cancel<br/>(market, not software)
    B-->>S: fill or cancel
```

## Data
| Source | What | Limits |
|---|---|---|
| [Tardis.dev](https://docs.tardis.dev/downloadable-csv-files) free first of month CSVs | Binance USD-M BTCUSDT top of book, five level snapshots, trades. Dev day 2026-09-01. Test days 2026-10-01 and 2026-11-01 (locked until the preregistration was committed) | One free day a month; millisecond exchange timestamps; no order IDs |
| [LOBSTER samples](https://data.lobsterdata.com/info/DataSamples.php) | Nasdaq AAPL, AMZN, GOOG, INTC, MSFT on 2012-06-21, 10 levels, with order IDs | One old day. No decision timestamps. Only INTC and MSFT have a one tick spread most of the time. Messages outside the 10 level window are missing |

Raw data is not committed. `make data` downloads it.

## Limits (what this cannot show)
- Decision to send latency is injected in simulation, not observed. No public data has decision timestamps.
- Exchange timestamps are in whole milliseconds, so nothing below 1 ms is resolvable.
- The simulator assumes our order does not move the market, and queue position is modelled, not seen.
- The simulated order never races other traders for the same liquidity in the same millisecond.
- Three crypto days and one 2012 equity day. Enough to falsify a claim but not to generalise one.
- The free crypto days are all the first of a month, so any month start effect is baked in.
- A positive result would still not prove faster routing improves trading performance.

## Results
None yet. This section fills only from files in `results/`.

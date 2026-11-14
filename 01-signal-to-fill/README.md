# 01 · From Signal to Fill

> When market conditions are similar, do orders that take longer to reach an outcome receive worse prices or fill less often?

| | |
|---|---|
| Status | 🟡 Data audited; preregistration next |
| Proposal | [PROPOSAL.md](PROPOSAL.md) |
| Literature review | [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md) |
| Lab notebook | [LAB_NOTEBOOK.md](LAB_NOTEBOOK.md) |
| Reproduce | `make reproduce` |

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
| [Tardis.dev](https://docs.tardis.dev/downloadable-csv-files) free first of month CSVs | Binance USD-M BTCUSDT top of book, 5-level snapshots, trades. Dev: 2026-09-01. Test: 2026-10-01, 2026-11-01 (locked) | One free day a month; millisecond exchange timestamps; no order IDs |
| [LOBSTER samples](https://data.lobsterdata.com/info/DataSamples.php) | Nasdaq AAPL, AMZN, GOOG, INTC, MSFT on 2012-06-21, 10 levels, with order IDs | One old day; no decision timestamps |

Raw data is not committed. `make data` downloads it.

## Limits (what this cannot show)
- Decision to send latency is injected in simulation, not observed. No public data has decision timestamps.
- Exchange timestamps are in whole milliseconds, so nothing below 1 ms is resolvable.
- The simulator assumes our order does not move the market, and queue position is modelled, not seen.
- Three crypto days and one 2012 equity day: enough to falsify a claim but not to generalise one.
- The free crypto days are all the first of a month, so any month-start effect is baked in.
- A positive result would still not prove faster routing improves trading performance.

## Results
None yet. This section fills only from files in `results/`.

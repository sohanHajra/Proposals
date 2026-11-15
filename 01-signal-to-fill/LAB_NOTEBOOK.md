# Lab notebook

Dated entries, never edited after the fact. Hypotheses, what I tried, what broke, what I changed. Times are US Central.

## 2026-11-14 (Sat) · setup and first look
- **Plan.** Proposal converted into two arms. Counterfactual delay replay on Binance USD-M BTCUSDT (Tardis free first of month data) and real order lifecycles in LOBSTER Nasdaq samples.
- **Data rule.** Dev day is 2026-09-01. Test days (2026-10-01, 2026-11-01) will not be downloaded until PREREGISTRATION.md is committed.
- **Dead end, already.** LOBSTER's main site now serves a web app shell for sample URLs (HTTP 200, HTML body with a .zip name). The legacy host php.lobsterdata.com still serves real zips. `get_data.py` checks the file is a real zip so this can't fail silently.
- **Literature surprise.** A 2025 Quantitative Finance paper ran a live taker experiment on Binance and Bybit. It is close to RQ1. The novelty claim was narrowed to the paired delay grid, the passive leg and the drift vs queue decomposition (see LITERATURE_REVIEW.md).
- **Dev day audit (2026-09-01, BTCUSDT perp), from `make audit`.** 36,920,623 top of book updates, 3,602,361 trades, 149,388 BTC traded. No crossed or locked books, no negative feed latency, no out of order exchange timestamps, 2 local gaps over 1 s (max 1.193 s). Exchange timestamps are whole milliseconds, so delays below 1 ms cannot be resolved. The 0 ms and 1 ms grid points are not distinguishable and the delay grid will start at 1 ms.
- **Feed latency is itself a finding to keep.** Capture time minus exchange time for book updates is median 2.9 ms, p99 19.5 ms, p99.9 108.5 ms. For trades it is median 3.1 ms, p99 142 ms, p99.9 589 ms. The trade stream's tail is much fatter than the book stream's, so the order of events in a merged replay is not always the order they happened. Replay will sort on exchange time and treat local time disagreements as a robustness check.
- **Large tick market.** The spread is exactly one tick (0.1 USDT) on 95.5% of updates. At about 78,000 USDT a tick is roughly 0.013 bps, so taker shortfall will be dominated by drift, not spread, while queue position should matter a lot for passive orders (Moallemi & Yuan predict queue value is largest for large tick assets). Revised expectation. The passive leg is where latency should bite hardest.
- **Limits and gaps (today).**
  - *Missing:* no real decision timestamps anywhere in public data, so the proposal's stage 1 (decision to send) is simulated, never observed. LOBSTER has no decision time either, only rest time.
  - *Fell short:* Tardis exchange timestamps are whole milliseconds, so sub millisecond latency (where colocated firms compete) is out of reach. One free day per month means three days total. That is enough to falsify but not enough to estimate regime dependence.
  - *Not yet read:* the full text of the closest prior work (Quantitative Finance 2025). Novelty is provisional until it is.
  - *More resources would buy:* paid Tardis access (many days, full L2 depth) for regime and seasonality tests; a live paper trading account on Binance testnet to measure real stage 1 and 2 latency instead of assuming it.

## 2026-11-14 (Sat, evening) · a paper that changes the queue model
- **Read in full.** Danait, Zamora & Boier, *Same Book, Different Fills* (arXiv 2609.13597 v3). On the same L2 path, changing only which quantity a cancellation removes moves passive completion by 8.01 points on 1301.T and 7.39 points on 7911.T. The aggressive benchmark does not move.
- **Why it matters here.** My passive leg runs on Binance L2 data, which has no order IDs. One queue rule would have quietly decided my passive result.
- **Change, made before any passive result exists.** Three matched cancellation rules (front, random, back). A passive latency effect counts only if its sign holds under all three, and every passive number is reported as a range. This goes into PREREGISTRATION.md.
- **Limits and gaps.**
  - *Missing:* I have no ground truth for where cancellations land in a Binance queue. LOBSTER order IDs might give a check on Nasdaq, not on Binance.
  - *Fell short:* my first plan used a single queue rule. This paper caught that before it cost anything.
  - *Not yet read:* Yueshen (2025) on queue uncertainty from latency, which may be close to my passive leg.

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

## 2026-11-15 (Sun) · LOBSTER audit, two papers read in full, preregistration
- **LOBSTER audit, from `make audit`** (`results/audit/lobster_2012-06-21.json`). 2,110,860 messages across the five names. Message and book rows match line for line, no crossed or locked books, no halts, no out of order times. The smallest gap between distinct timestamps is 169 to 303 ns, so this data resolves far below the 1 ms floor of the Binance files.
- **Surprise.** Only two of the five names behave like a large tick market. The spread is one tick on 76.7% of INTC updates and 76.9% of MSFT updates, but on under 1% for AAPL, AMZN and GOOG, whose median spreads are 15, 13 and 28 ticks. Queue position only means much where the spread is pinned at one tick, so the RQ2 test now runs on INTC and MSFT and the other three are descriptive. I made this choice from the spread numbers, before computing anything about fills or markouts.
- **Most real orders never trade.** Of orders submitted and ended inside the file, only 5.3% (AMZN) to 9.3% (AAPL) had any visible execution. The rest were deleted. In INTC and MSFT a quarter of these orders lived no more than 1.3 ms and 1.5 ms, and a tenth lived under 0.07 ms. Between 26% (GOOG) and 39% (INTC) of the orders deleted without a fill were gone within 100 ms.
- **Read in full. Albers et al. (2025).** Their live study is taker only and observational, with one realised latency per order. It does not replay a decision across a delay grid, so my claim 1 stands within this review. Their main finding is that the orders that would have made money are the ones that slip. I added a check (H1b) for whether my replay shows the same split. They also argue a synthetic study would need latency that depends on future returns. My replay keeps the real book path but my order never races anyone, and that is now written into the limits.
- **Read in full. Yueshen (2026).** A theory paper. Orders at the back of a queue lose money when they fill. That means the passive leg should measure what a late order earns when filled, not only whether it fills (H2c).
- **Preregistration written and committed** before the replay engine exists and before any test day is downloaded. Delay grid 1, 2, 5, 10, 25, 50, 100, 250, 500 ms. Primary tests are the taker slope (H1) and the passive slope under all three cancellation rules (H2), each required on both test days.
- **Limits and gaps.**
  - *Missing:* the replay engine, so there is still no latency result of any kind.
  - *Fell short:* the Albers et al. tables and figures did not render, so I quote only numbers from their text. Some figure pages of Yueshen were images I did not view.
  - *Weakness in the LOBSTER files:* they only carry messages inside the 10 level window. An order that drifts out of the window can look open at the close, and fill and delete shares are for orders whose whole life stayed in view.
  - *Judgement call on record:* the 0.1 bps materiality bar for H1 is anchored loosely on Albers et al., whose figure is conditional on a 2 bps markout. A reader could argue for a different bar.
  - *More resources would buy:* LOBSTER data for recent years and more days, which would show whether the 2012 pattern still holds.

## 2026-11-15 (Sun, afternoon) · the Albers et al. tables
- The tables that did not render this morning are in the open access PDF on the Oxford repository. I read all nine tables and the main figures.
- **The H1 bar holds.** Table 7 slopes give about 0.10, 0.31 and 0.07 bps of slippage at a 2 bps markout, the same numbers I had taken from their text. Nothing in the committed preregistration changes.
- **Context I did not have.** Best public Binance USDT margined taker fee at the time was 1.7 bps (Table 1). Their markout horizon has a median of 1.14 s (Table 4), close to my 1 s. Colocated send time was about 2 ms (text, Section 5.1).
- **Limits and gaps.**
  - *Still missing:* the replay engine. No latency result yet.
  - *Not checked:* their supplementary material (latency and liquidity analysis, robustness of the fits). I have not opened it.
  - *Fees:* Table 1 is the best tier in 2023. My account tier and today's schedule may differ.


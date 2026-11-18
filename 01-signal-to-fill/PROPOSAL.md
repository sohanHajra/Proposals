SOHAN HAJRA RESEARCH PROPOSAL / OCTOBER 2026

# From Signal to Fill
A question about execution delays and order outcomes

**The question.** When market conditions are similar, do orders that take longer to reach an outcome tend to receive worse execution prices or have a lower chance of filling?

### 01 The idea
I want to know whether time spent between a trading decision and an order outcome is associated with execution quality. I would not assume that every kind of delay has the same explanation.

Where the logs allow it, I would look at three stages: the decision to send the order, the send to exchange acknowledgement, and the acknowledgement to fill or cancellation. The final stage can reflect time resting in the order book, not necessarily slow software.

### 02 How I would start
I would begin with one liquid instrument and a consistent order type. I would ask for decision and order event timestamps, side, size, venue, fills, cancellations and the market price at decision time. Spread, volatility, available liquidity and fees would help make the comparisons fair.

For filled orders, I would measure signed shortfall against the decision mid, using the average execution price for partial fills. I would report fill rates and price movement to a fixed horizon separately for cancelled or unfilled orders.

I would compare similar orders by side, size, time of day, spread and liquidity, while keeping different venues and order types separate. I would reserve later trading dates for a fresh check. Before drawing conclusions, I would inspect missing events, clock alignment, partial fills and whether market drift or routing choice explains the pattern.

### 03 What I would look for
I would plot fill probability and execution shortfall across delay ranges, with sample sizes alongside the results. If the relationship disappears once market conditions are comparable, that would be useful to know. If it persists on later dates, it would give me a more specific question to investigate. It would not, by itself, prove that faster routing improves trading performance.

*This is a question I would like to explore. I have not run the study, and the approach would depend on what order event data is available.*

### 04 What led me to this question
**Nasdaq auction research** Working with fixed time horizons taught me how much the timing of information matters. [sohanHajra/nasdaq-closing-auction-research](https://github.com/sohanHajra/nasdaq-closing-auction-research)

**Walk forward trading system** Testing unseen periods with transaction costs made me more skeptical of results that look good under one set of assumptions. [sohanHajra/quant_trading_system](https://github.com/sohanHajra/quant_trading_system)

**ChainDEX prototype** Looking again at swap quotes and slippage reminded me that a quoted price and an executed trade are different things. [sohanHajra/ChainDEX](https://github.com/sohanHajra/ChainDEX)

**UIUC / B.S. MATHEMATICS & COMPUTER SCIENCE** linkedin.com/in/sohan-hajra | github.com/sohanHajra | sohanhajra.github.io | sohancollege27@gmail.com

# Moallemi & Yuan (2017), A Model for Queue Position Valuation in a Limit Order Book

## Citation
Ciamac C. Moallemi and Kai Yuan (2017). *A Model for Queue Position Valuation in a Limit Order Book*. Working paper, Columbia Business School. SSRN 2996221. First version December 2016, revised June 2017.

The copy I read is the June 2017 revision, 33 pages with the proofs in a supplement at the back (pp. 27 to 33). I don't know of a published version and haven't looked for one, so every page number here is the working paper's.

## Reading depth
I read it all the way through, every table and figure and the supplement with the proofs. I followed the proofs to see how they go and what they rest on, but I did not rederive them. Values from Tables 1 to 3 are as printed. Values I give from Figure 3 are read off the plot, so they are rough. Where I give a difference between two table cells, I worked it out myself.

## Core idea
In a price time priority book, an order near the front of the queue is worth more than one at the back. The paper splits that value into two parts (pp. 1, 4). One is static. When an order at the back fills, it is because a large trade came through, and large trades are more likely informed, so back of queue fills carry more adverse selection. The other is dynamic. An order that doesn't fill now moves up as trades and cancellations eat the queue ahead, and holding a place has option value.

The value of a sell order at the ask is written as fill probability times the premium earned minus adverse selection, V = α(δ − AS) (equation 1, p. 8). The model gives α and AS as functions of queue position, from a handful of quantities you can estimate from data.

## Model and its assumptions
- Large tick assets only, where the spread is almost always one tick. They take the definition from Eisler et al. (2012), the spread rarely exceeds one tick, and give the reason that such a tick is economically significant, so traders queue instead of improving the price (p. 6). For small tick assets they say queueing matters less and leave them out.
- Bid and ask are taken as fixed over the life of the order and the spread as one tick (p. 6). One exchange, one side, an order of infinitesimal size, risk neutral, zero interest (p. 7).
- The efficient price moves only through trades and jumps (equation 2, p. 9). Trades arrive as a Poisson process with i.i.d. signed sizes and move the price by a linear permanent impact λ times the size. Jumps arrive as a separate Poisson process with i.i.d. sizes of mean zero (p. 10).
- An upward jump fills every order at the ask, and a downward jump cancels them (pp. 9, 11 to 12). The order is never requeued at a new price.
- Cancellations shrink the whole queue by a random fraction, so they land evenly through it, and they carry no information. The authors note that Cont et al. (2014) find cancellations do move with prices and leave that out (p. 12).
- With these, V(q, δ) is linear in the premium δ and the two coefficients solve Volterra integral equations (Theorem 1, p. 14). Value depends on ratios of event rates, not their levels, because there is no time value (pp. 14 to 15).
- Theorem 2 (p. 15) gives the shape. Fill probability doesn't rise with queue position, adverse selection is positive, and with no cancellations a very deep order fills only on an upward jump. The monotone fill probability comes from a coupling of two orders in the same queue (p. 30).
- The proofs are light in places. Linearity in δ is found by assuming it and checking that it works (pp. 27 to 28), and existence and uniqueness come from a standard Volterra result (Hackbusch 1995, p. 28). The positivity proof of Theorem 2 part 3 says α is increasing where it means not increasing, and cites the wrong equation (p. 30). Theorem 3, the closed form for exponential trade sizes, gives the decay rate b and one coefficient differently in the statement (p. 16) and at the end of the proof (p. 33). None of the paper's numbers use Theorem 3.

## Data
- NASDAQ ITCH market by order data for August 2013, NASDAQ book only (pp. 16 to 17). Daily closing prices from Yahoo Finance.
- Calibration is shown for Bank of America over 22 trading days (Table 1, p. 19). BAC traded about 88 million shares a day and its one tick spread was about 7 bps (p. 16).
- The backtest covers nine liquid names with spreads near one tick, BAC, CSCO, GE, F, INTC, PFE, PBR, EEM and EFA (Table 2, p. 22).

## Methods
- Parameters are fitted day by day (p. 17). A price jump is any change in the bid or ask, and executions that clear the queue count as jumps, not trades. Jump size is the price change one minute after the move, as a stand in for the change in the efficient price. Fills on the same side within 2 ms are merged into one market order, and trade sizes are fitted as lognormal.
- Cancellations are fitted as a Beta distributed fraction of the queue (p. 18).
- The impact λ is not estimated from their data. It comes from Kyle and Obizhaeva's invariance formula with their constant C = 0.0156 (equation 11 and footnote 9, p. 18).
- The premium earned is half the spread plus NASDAQ's 0.3 tick rebate, 0.8 ticks (p. 18).
- Validation is a backtest with artificial orders of no size placed at 1,000 random times a day between 10:00 and 15:30 on a random side (pp. 22 to 23). Regular orders join the back of the queue and touch orders are put at the very front. An artificial order fills when a real order behind it at the same price fills, and is cancelled when a better price appears on its side. Its value is the fill price against the mid one minute after the fill.

## Main results
- In BAC the parameters are steady from day to day except the ratios of jump and cancellation rates to the trade rate (p. 18, Table 1). Cancellations are far more frequent than the trades the model counts, around 86 to 178 a minute against 0.8 to 2.3 (Table 1).
- Fill probability falls with queue position and flattens out, adverse selection rises, so value falls (p. 20, Figure 3). An order at the front of the queue was worth about 0.26 ticks more than one at the average queue length on 8/9/2013 and 0.21 ticks more on 8/20/2013 (p. 20).
- The lower values on 8/20/2013 go with more jumps per trade, 0.69 against 0.43 (p. 20).
- Model and backtest agree closely, on value, fill probability and adverse selection (Table 3, p. 23). For BAC a back of queue order is worth 0.14 ticks in both, fills 0.62 against 0.60 of the time, and pays 0.57 ticks of adverse selection in both. PBR comes out slightly negative in both.
- Front of queue orders are worth more than back of queue orders for every name (p. 24). From Table 3 the gap runs from 0.03 to 0.22 ticks in the model and 0.05 to 0.17 ticks in the backtest. BAC and CSCO have the largest gaps.
- The paper's case for a model when a backtest exists is that the backtest is too noisy to track daily changes in the rates, while the model can be fed the rates as they move (p. 24).

## Limits
- The impact that drives adverse selection is borrowed from another paper's formula, not fitted to this data. Part of the adverse selection result is therefore assumed.
- The model counts an order as filled on any upward jump. The backtest uses a different fill rule. The two agree on fill probability, which is reassuring, but the model's rule is an assumption.
- No standard errors, no test of how close "very close" is, and no out of sample split (Table 3). The one minute mid is admitted to be noisy (p. 23).
- The day count doesn't line up. Table 2 says 21 trading days of August 2013, Section 5.1 and Table 3 say 30 trading days, and Table 1 lists 22 days for BAC.
- The abstract says queue value can be of the same order of magnitude as the spread. The gaps measured are about a fifth of a tick at most, and for some names a few hundredths. A fifth of a spread is meaningful. "Same order of magnitude" reads generously.
- Cancellations are uninformed and spread evenly by assumption, though in their own data they are about a hundred times more frequent than the trades they model.
- Smaller slips: The spread column of Table 2 is labelled in dollars but shows values near 1. The EEM of Table 2 is EMM in Table 3. On p. 24 PFE is said to have a gap under 0.1 ticks, while its backtest gap works out at 0.10. Figure 2 is a slide from Quantitative Brokers on futures, pasted in with its own caption.
- Working paper. I don't know whether it changed later.

## What it means for my work (my own inference)
- Their cancellation model, a uniform shrink of the whole queue, is in expectation my quantity weighted random rule. They assume it and don't test it against front or back placement, so it says nothing about which of my three rules is closer to the truth. Their backtest runs on real order IDs and doesn't need a rule at all.
- Fill probability in their model flattens once the queue ahead is deep relative to trade sizes. Extra queue ahead from a late arrival then hardly changes the chance of a fill. That is one possible reason my H2, fill probability falling with delay, came out null on BTCUSDT, where the queue is deep next to typical trades. It is consistent with the null and isn't evidence for it, and I haven't tested it.
- Their values are in ticks. BAC's tick was about 7 bps. On BTCUSDT a tick is about 0.013 bps, so the same fifth of a tick would be a tiny amount in bps. BTCUSDT meets their definition of large tick (the spread is one tick almost all the time) but not their reason for it (a tick that is costly to cross). An earlier line in my notebook took their large tick argument to mean queue position should matter a lot for my passive orders. That went further than the paper does, and the notebook now says so. If position matters on BTCUSDT, it would be through whether the order fills and what the price does after, which H2 and H2c already measure, not through the spread earned.
- Their backtest, orders of no size pushed through the real book and valued against the mid one minute later, is close kin to my passive replay. Their contrast is front against back of queue at the same moment. Mine is the same decision at different delays.

## Used in
- [01-signal-to-fill](../01-signal-to-fill/LITERATURE_REVIEW.md). Background on why queue position has value in a large tick book, and a published precedent for valuing artificial orders against the real order flow. Not a benchmark for any of my numbers, and none of my hypotheses rest on it.

## Open questions
- How much of the adverse selection result survives if λ is fitted from the data rather than taken from the invariance formula?
- With cancellations about a hundred times as frequent as modelled trades, does their uninformed, uniform assumption matter for the value at the back of the queue? LOBSTER order IDs could show where cancellations land, which my notebook already plans to describe.
- What would the touch against regular contrast look like in ticks on the LOBSTER day, using their one minute mid rule? An idea for after the test days, not run.
- Which number of trading days is right for Table 3, 21 or 30?
- Is there a later or published version that fixes Theorem 3?

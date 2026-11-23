# Data manifest, 01.b

One row per data file, written when it first lands, after the preregistration (commit b81f5f6). The files themselves aren't in the repo. Each one was checked against the MD5 its source showed before the SHA256 was taken.

| File | Source | Role | Landed | SHA256 |
|---|---|---|---|---|
| binance_swap-BTCUSDT-2026-07-06.txt.zst | CryptoStruct free sample, saved to my Drive 2026-11-20 | Stress day, secondary | 2026-11-22 | ddc90bbe64776315f9115b7bd51175608374075b8089a96f2aa6f63ac6558246 |
| binance_swap-BTCUSDT-2026-11-13.txt.zst | CryptoStruct free rolling sample, saved to my Drive 2026-11-20 | Extra recent day, secondary | 2026-11-22 | 0d8132f3cbf30f6490386fb03b13680145060bee357810f3244547f9462361ee |
| binance_swap-BTCUSDT-2026-11-14.txt.zst | CryptoStruct free rolling sample, saved to my Drive 2026-11-20 | Extra recent day, secondary, added under Deviations | 2026-11-22 | 090319017e644ea6b2dc6a7ec8ffa7fa3e701a3af512e2b395eb3581575f30fa |
| binance_swap-BTCUSDT-2026-11-15.txt.zst | CryptoStruct free rolling sample, saved to my Drive 2026-11-20 | Extra recent day, secondary, added under Deviations | 2026-11-22 | f7e34d741543e9e282a86f99d44d19a349daab10ebfecd19158dac1078dd711e |
| binance_swap-BTCUSDT-2026-09-01.txt.zst | CryptoStruct, bought 2026-11-22 | Build day | 2026-11-22 | e7185bbcccb06c578385e287f4075f155d7f5b36186ff5fa081fa14c82243bfd |
| binance-futures_trades_2026-09-01_ETHUSDT.csv.gz | Tardis free first of month CSV | Build day, ETHUSDT threshold and size | 2026-11-23 | ab99308c5e79a637ec69ab942a78ac7aec385f3f4173dedc2b6cd78c28700234 |
| binance-futures_book_ticker_2026-09-01_ETHUSDT.csv.gz | Tardis free first of month CSV | Build day, ETHUSDT threshold and size | 2026-11-23 | 7bd9d0389eb83ffed58f9495f11e6906dbb3fb56ff5e0416fb5428d13ec99208 |
| binance-futures_book_snapshot_5_2026-09-01_ETHUSDT.csv.gz | Tardis free first of month CSV | Build day, ETHUSDT threshold and size | 2026-11-23 | 0c2c606b73dffba989e72d895ced5d079418cd9a256c5ea598e3a4e790074f7f |
| 2026-09-01_BTCUSDT_ob200.data.zip | Bybit free book file, quote-saver.bycsi.com | Build day, Bybit support | 2026-11-23 | 6fdc870a8b66a32fd44c245ddec06850f933233ea0ad0feee585b89d07907f6e |
| BTCUSDT2026-09-01.csv.gz | Bybit free trade file, public.bybit.com | Build day, Bybit support | 2026-11-23 | a321d10bffc3f6130c2e76609d58988dafa3898538f18fcabf7567891f00296e |

2026-11-14 and 2026-11-15 were added under Deviations on 2026-11-22, before any file was opened.

The twelve bought test days are in my Drive and stay there until the runner, the loader and the race sensitivity are built on 2026-09-01.

Tardis and Bybit show no checksum on their sites, so the five files from 2026-11-23 have only my SHA256, taken when they landed.

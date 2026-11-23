# Data manifest, 01.b

One row per data file, written when it first lands, after the preregistration (commit b81f5f6). The files themselves aren't in the repo. Each CryptoStruct file was checked against the MD5 its source showed before the SHA256 was taken.

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


Tardis and Bybit show no checksum on their sites, so the five files from 2026-11-23 have only my SHA256, taken when they landed.

## Test files in my Drive, not copied in yet
The twelve bought test days, with the MD5 and size my Drive reports for each, written down before any of them is copied in (Deviation of 2026-11-23, afternoon). A file is used only if its MD5 matches its row here. Its SHA256 goes in the table above when it lands.

| File | MD5 | Bytes |
|---|---|---|
| binance_swap-BTCUSDT-2025-12-17.txt.zst | 91969d912ba93c1f03cb72be21472388 | 1,582,999,946 |
| binance_swap-BTCUSDT-2026-01-14.txt.zst | 29daadbe420684f39bc9b4b9b16b4075 | 1,302,489,140 |
| binance_swap-BTCUSDT-2026-02-18.txt.zst | ac662e6285ac348255666e82b4faf044 | 1,456,871,836 |
| binance_swap-BTCUSDT-2026-03-18.txt.zst | 0eb09cc97deb637119f9d7e0318d9e40 | 1,473,270,668 |
| binance_swap-BTCUSDT-2026-04-15.txt.zst | 8398757e5dda78c0dfaad6c3df88bd23 | 1,204,947,737 |
| binance_swap-BTCUSDT-2026-05-13.txt.zst | 4f1463fcf6584faecdb870ce645212f5 | 1,137,539,284 |
| binance_swap-BTCUSDT-2026-06-18.txt.zst | 6973b2e8caa0c3a48b1edeb23c535b98 | 1,505,822,847 |
| binance_swap-BTCUSDT-2026-07-15.txt.zst | 2392142e5f7cf6435b4332c9f9304e98 | 1,115,429,729 |
| binance_swap-BTCUSDT-2026-08-12.txt.zst | 1997a27c67f30165b49c4a9521bf006f | 855,852,243 |
| binance_swap-BTCUSDT-2026-09-16.txt.zst | 9b7c384456c43076b95f7c5e27d61c21 | 1,537,392,617 |
| binance_swap-BTCUSDT-2026-10-14.txt.zst | 47349ff9c74b837d3da7fbe8ad7a2226 | 1,613,530,298 |
| binance_swap-BTCUSDT-2026-11-18.txt.zst | e01b7bfc82241c4a24cfb62e6c022691 | 2,096,390,969 |

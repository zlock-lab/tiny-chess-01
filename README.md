# tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/{owner}/{repo}/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/{owner}/{repo}/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A 4 KB Python chess engine for make.fun's "Build the strongest chess engine in 4 KB of Python" bounty. It parses FEN, generates legal moves (castling, en passant, promotion), searches a fixed depth with alpha-beta pruning, MVV-LVA and killer-move ordering, and evaluates with piece values, piece-square tables and a two-bishop bonus. Standard library only; fixed depth, no clock, no randomness, so a trial replays identically.

## Run it

```sh
MAKEFUN_ENV_URL=http://127.0.0.1:8123 MAKEFUN_DEPTH=4 python3 main.py
```

`main.py` is the whole engine (a compressed payload unpacked at runtime); `engine-src.py` is the readable source it was packed from.

---

<sub>Entered on [make.fun](https://make.fun/?ref=zpha5r25&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>

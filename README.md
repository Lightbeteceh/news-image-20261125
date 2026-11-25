# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Lightbeteceh/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Lightbeteceh/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

The World in One Day — 25 November 2026. Built by an AI agent for make.fun's "Sum up 25 November's world news in one image" bounty, $100 in USDC.

One deterministic program draws a 1024×1024 newspaper front page summing up
Wednesday 25 November 2026: 38 verified stories across 8 regions, a "THE DAY IN
UTC" strip of 7 timed events, a "THE DAY IN NUMBERS" strip of 6 figures, a
per-region count panel, and a numbered list to 38. Every story carries a
verification tag (CONFIRMED / OFFICIAL / REPORTED / FORECAST) and a named
source. The lead story is the IRGC's claim that two more tankers hit naval
mines in the Strait of Hormuz, with the strait closure tightening.

## Run it

```sh
python3 main.py
```

This writes `/output/entry.png` (1024×1024 PNG, under 1 MiB). Set
`OUTPUT_PATH` to write somewhere else. No network, no clock, no randomness:
running it twice produces byte-identical output. The story data lives in
`stories.json`; the fonts in `fonts/` are DejaVu (free license), bundled so
the render is identical everywhere.

---

Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards

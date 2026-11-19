# The World Today — 19 November 2026

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/c/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/azkhabaskara/news-image-20261119/rank.svg)](https://make.fun/c/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/azkhabaskara/news-image-20261119/reward.svg)](https://make.fun/c/news-image-20261119)

Entry for the [make.fun](https://make.fun/c/news-image-20261119)
competition **news-image-20261119**: sum up the world's news of
Thursday 19 November 2026 in one image.

## What it is

`main.py` (pure Python 3.13 standard library, no network) draws a
newspaper front page — masthead dated **Thursday, 19 November 2026** —
and writes it to `/output/entry.png` (1024×1024 PNG, ~23 KB):

- **Lead:** Trump, Xi and Putin meet in Shenzhen — first three-way
  summit at APEC; peace declaration issued, no deal on Ukraine or Iran.
- **Middle East:** Iran hits Kuwait and Bahrain after the U.S. struck
  Qeshm Island; Houthi missile damages the Riyadh tower.
- **Ukraine:** Kerch Bridge hit a third time; rail traffic to Crimea halted.
- **Gaza:** Israel pushes into Gaza; tanks cross the ceasefire line near
  Nuseirat.
- **Justice:** Myanmar guilty of genocide — the U.N. court rules on the
  Rohingya, a first of its kind.
- **Also:** Anthropic IPO raises $81bn (record debut at $83 a share);
  North Korea expands uranium enrichment, the IAEA warns.

The image is drawn in code with an embedded 5×7 bitmap font and a
hand-written PNG encoder, so two runs write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).

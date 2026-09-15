# `@meterapp/car-image` (CLI)

Node.js 20+. No install needed:

```bash
npx @meterapp/car-image                      # run without installing
npm install -g @meterapp/car-image           # or pnpm add -g / bun add -g
curl -fsSL https://carimage.dev/install.sh | sh
```

## Signing in

```bash
car-image login       # browser device flow; stores the key at $XDG_CONFIG_HOME/car-image-api/config.json, mode 0600
car-image whoami      # credits, auto-reload, payment method, 30-day usage, masked key prefix, scopes
car-image logout
```

`CAR_IMAGE_API_KEY` in the environment overrides the stored key — that is what CI should use. The key prints exactly once at login; it is not recoverable afterwards.

## Commands

| Command | What it does |
| --- | --- |
| `get --make --model --year [--view] [--color] [--size \| --width [--height] [--fit contain\|cover\|inside]] [--background transparent\|white\|black\|<hex>] [--trim [--padding 0-50]] [--format png\|webp\|jpg\|auto] [--out file\|-] [--url] [--json]` | Downloads one image (1 credit). `--out -` writes to stdout. `--url` prints a signed URL instead. See "Sizing" below. |
| `url --make … [same sizing flags] [--ttl 3600] [--max-uses 0] [--renew [--renew-days 365]] [--idempotency-key <key>] [--json]` | Creates one signed delivery URL (1 credit). `--renew` keeps it alive past the TTL at 1 credit per opened window. |
| `url --batch file.json [--ttl 3600] [--max-uses 0] [--renew [--renew-days 365]] [--idempotency-key <key>] [--json]` | Up to 50 signed URLs in one call (1 credit each). Entries may carry `view`, `color`, `size`, `width`, `height`, `fit`, `background`, `trim`, `padding`, `format`. |
| `resolve <free text…>` | Free text → parameters, candidates, confidence (`high`, `medium` or `low`), and a ready-to-run `car-image get …`. Free. |
| `search <query…> [--limit] [--year]` | Fuzzy catalog search. Free, no key required. |
| `options` | Views with yaw angles, colors with hex, sizes, fit modes, backgrounds, trim limits, formats, pricing, catalog coverage. Free. |
| `describe [operationId\|path\|all] [--json]` | Explains any REST endpoint from `/openapi.json`: parameters, enums, defaults, response headers, error codes. |
| `feedback (--request-id ID \| --make … --year …) (--rating 1-5 \| --good \| --bad) [--reason]` | Rates a delivered image. Free. |
| `doctor [--json] [--yes] [--no-image]` | Smoke-tests every endpoint with status, latency, cache state and fix hints. Exit 1 on any failure. |
| `billing [--credits …] [--portal]` | Opens hosted Stripe Checkout or the billing portal. The CLI never touches card data. |
| `mcp [--toolset core\|all]` | Runs the stdio MCP server: `core` (default) is the eight image tools, `all` adds the request board. |
| `agent-config [--host claude-code\|claude-desktop\|cursor\|chatgpt\|generic] [--remote] [--json]` | Prints ready-to-paste MCP configuration (core toolset, with the `?toolset=all` opt-in noted). |
| `config path \| get <key> \| set <key> <value> \| list` | Keys: `autoUpdate`, `telemetry`, `baseUrl`. |

Global flags: `--json`, `--quiet`, `--base-url`, `--api-key`, `--no-color`, `-h`, `-v`.
Environment: `CAR_IMAGE_API_KEY`, `CAR_IMAGE_API_URL`, `CAR_IMAGE_CONFIG`, `CAR_IMAGE_TELEMETRY=0`.
Exit codes: `0` ok, `1` failure, `2` usage error.

## Sizing

`get`, `url` and every `--batch` entry share the sizing options. `--width`/`--height` are 1–1024 px; one keeps the aspect ratio, both together return exactly that box (`--width 600 --height 400` is 600×400, no longer a square), placed by `--fit contain` (default: whole car, padded), `cover` (fill and centre-crop) or `inside` (may return a smaller image). `--trim` crops to the car's own bounds before sizing so it fills a non-square slot; `--padding 0-50` keeps a margin (percent of the car's longer side) and only applies with `--trim`. `--background` is `transparent` (default), `white`, `black` or hex (`rrggbb`, `#rrggbb`, `rgb`, `#rgb`); it flattens PNG and WebP too, and `jpg` defaults to white. `--format auto` lets each client negotiate WebP or PNG from its `Accept` header — on a signed URL, on every load. Nothing is upscaled past 1024.

```bash
car-image get --make Porsche --model 911 --year 2024 --view side --width 1024 --height 512 --trim --padding 6 --out hero.png
car-image url --make Porsche --model 911 --year 2024 --width 600 --height 338 --trim --format auto --ttl 604800
```

A batch file is an array (or `{"images": [...]}`) of 1–50 entries such as `{ "make": "Toyota", "model": "RAV4", "year": 2023, "width": 512, "height": 320, "trim": true, "padding": 5, "background": "white", "format": "webp" }`.

`url` sends an `Idempotency-Key` on every call — generated, or `--idempotency-key <key>` (1–255 characters of letters, digits, `.` `_` `:` `-`). The same key with the same request within 24 hours replays the first response (`Idempotent-Replayed: true`) instead of billing again; a different request under the same key is a `422`, and a retry that overtakes the first request still running is a `409` with `Retry-After`. Choose the key yourself when a job queue or a rerun may repeat the command.

## Scripting

`--json` on any command gives machine-readable output. Pair it with `jq`:

```bash
# What does this batch cost, and can I afford it?
credits=$(car-image whoami --json | jq .data.credits)
echo "have $credits credits"

# Resolve, then render
params=$(car-image resolve "blue 2022 bmw m3" --json)
make=$(jq -r .data.params.make <<<"$params")
model=$(jq -r .data.params.model <<<"$params")
year=$(jq -r .data.params.year <<<"$params")
car-image get --make "$make" --model "$model" --year "$year" --out m3.png
```

A resumable batch over a CSV of `make,model,year`:

```bash
#!/usr/bin/env bash
set -euo pipefail
mkdir -p out
while IFS=, read -r make model year; do
  out="out/${year}-${make}-${model}.png"
  [ -f "$out" ] && continue                   # already done; do not re-bill
  if ! car-image get --make "$make" --model "$model" --year "$year" --out "$out" --quiet; then
    echo "failed: $year $make $model" >&2      # 404s and capacity limits land here
  fi
done < vehicles.csv
```

Checking for the file first is what makes a rerun free.

## In CI

```yaml
- run: npx -y @meterapp/car-image get --make Porsche --model 911 --year 2024 --out car.png
  env:
    CAR_IMAGE_API_KEY: ${{ secrets.CAR_IMAGE_API_KEY }}
    CAR_IMAGE_TELEMETRY: "0"
```

Put the key in the secret store, never in the workflow file. `car-image doctor --json --no-image` is a good health gate that spends nothing.

## When something is wrong

`car-image doctor` first. It tests health, options, catalog lookups, search, resolve, account, a signed-URL mint and redeem, and optionally a keyed image fetch, printing latency, cache state, credits and a fix hint for each failure.

Errors print as `Title: detail`, a hint (`401 → car-image login`, `402 → car-image billing`, `429 → wait Retry-After`) and the `request_id`. Quote the `request_id` when reporting a problem; never paste the key.

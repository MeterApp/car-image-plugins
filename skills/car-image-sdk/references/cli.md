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
| `get --make --model --year [--view] [--color] [--size\|--width --height] [--format] [--out file\|-] [--url] [--json]` | Downloads one image (1 credit). `--out -` writes to stdout. `--url` prints a signed URL instead. |
| `url --make … [--ttl 3600] [--max-uses 0] [--batch file.json] [--json]` | Creates signed delivery URLs (1 credit each, up to 50 per batch). |
| `resolve <free text…>` | Free text → parameters, candidates, confidence, and a ready-to-run `car-image get …`. Free. |
| `search <query…> [--limit] [--year]` | Fuzzy catalog search. Free, no key required. |
| `options` | Views with yaw angles, colors with hex, sizes, formats, pricing, catalog coverage. Free. |
| `describe [operationId\|path\|all] [--json]` | Explains any REST endpoint from `/openapi.json`: parameters, enums, defaults, response headers, error codes. |
| `feedback (--request-id ID \| --make … --year …) (--rating 1-5 \| --good \| --bad) [--reason]` | Rates a delivered image. Free. |
| `doctor [--json] [--yes] [--no-image]` | Smoke-tests every endpoint with status, latency, cache state and fix hints. Exit 1 on any failure. |
| `billing [--credits …] [--portal]` | Opens hosted Stripe Checkout or the billing portal. The CLI never touches card data. |
| `mcp` | Runs the stdio MCP server. |
| `agent-config [--host claude-code\|claude-desktop\|cursor\|chatgpt\|generic] [--remote] [--json]` | Prints ready-to-paste MCP configuration. |
| `config path \| get <key> \| set <key> <value> \| list` | Keys: `autoUpdate`, `telemetry`, `baseUrl`. |

Global flags: `--json`, `--quiet`, `--base-url`, `--api-key`, `--no-color`, `-h`, `-v`.
Environment: `CAR_IMAGE_API_KEY`, `CAR_IMAGE_API_URL`, `CAR_IMAGE_CONFIG`, `CAR_IMAGE_TELEMETRY=0`.
Exit codes: `0` ok, `1` failure, `2` usage error.

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

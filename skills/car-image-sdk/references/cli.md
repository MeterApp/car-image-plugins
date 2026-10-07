# `@meterapp/car-image` (CLI)

Node.js 20+. No install needed:

```bash
npx @meterapp/car-image                      # run without installing
npm install -g @meterapp/car-image           # or pnpm add -g / bun add -g
curl -fsSL https://carimage.dev/install.sh | sh
```

A global install keeps itself current: when npm has a newer version, a background process installs it with the same package manager and the next command runs it, with nothing printed for scripts or agents. `npx @meterapp/car-image@latest` always runs the newest release; a bare `npx @meterapp/car-image` reuses whatever copy npx finds first.

## Signing in

```bash
car-image login       # browser device flow; saves the key for the CLI, readable by your user only
car-image whoami      # credits, auto-reload, payment method, 30-day usage, masked key prefix, scopes
car-image logout
```

`CAR_IMAGE_API_KEY` in the environment overrides the stored key — that is what CI should use. The key prints exactly once at login; it is not recoverable afterwards.

## Commands

| Command | What it does |
| --- | --- |
| `get --make --model --year \| --vehicle veh_… [--view] [--color <preset\|#1a2b3c>] [--size \| --width [--height] [--fit contain\|cover\|inside]] [--background transparent\|white\|black\|<hex>] [--trim [--padding 0-50]] [--format png\|webp\|jpg\|auto] [--out file\|-] [--url] [--json]` | Downloads one image (1 credit). `--vehicle` is a stable catalog id in place of make, model and year; `--color` takes a preset or any hex. `--out -` writes to stdout. `--url` prints a signed URL instead. See "Sizing" below. |
| `url --make … [same sizing flags] [--ttl 3600] [--max-uses 0] [--renew [--renew-days 365]] [--idempotency-key <key>] [--json]` | Creates one signed delivery URL (1 credit). `--renew` keeps it alive past the TTL at 1 credit per opened window. |
| `url --batch file.json [--ttl 3600] [--max-uses 0] [--renew [--renew-days 365]] [--idempotency-key <key>] [--json]` | Up to 50 signed URLs in one call (1 credit each). Entries may carry `view`, `color`, `size`, `width`, `height`, `fit`, `background`, `trim`, `padding`, `format`. |
| `resolve <free text…>` | Free text → parameters (with the vehicle id), candidates, confidence (`high`, `medium` or `low`), and a ready-to-run `car-image get …`. Free. |
| `check <file.csv\|file.json\|-> [--out <file>] [--format csv\|json] [--json]` | Which vehicles of a list the catalog carries, each read the way `get` reads it (CSV columns `make`, `model`, `year`, or `vehicle`, plus an optional `ref`; or a JSON array). `--out` writes the file back with `status`, `vehicle_id`, `match`, `reason` and `suggested_vehicle_id` per row. Any length, 2,000 per request. Free. |
| `search <query…> [--limit] [--year]` | Fuzzy catalog search, with a vehicle id per model year. Free, no key required. |
| `vin <VIN> [--year] [--json]` | Decodes a full or partial VIN (`*` for unknown positions): year, make, model, trim, engine, every vPIC attribute, the catalog vehicle id and a ready-to-run `car-image get --vehicle …`. Free. |
| `3d create --make --model --year [--color] [--vehicle] [--webhook-url] [--webhook-secret] [--publish] [--wait] [--out <dir>] [--json]` | Requests a 3D model (100 credits, charged at creation, free for a vehicle and color you already own; an `Idempotency-Key` is sent). `--publish` hosts it at once and prints the embed. `--wait` polls until ready or failed; with `--out` it then downloads GLB, USDZ, FBX and the thumbnail into the directory. |
| `3d get <id> [--wait] [--json]` | Status, progress and file URLs of a 3D request; `--wait` blocks until it settles. Free. |
| `3d download <id> [--format glb\|glb_web\|usdz\|fbx\|thumbnail] [--out <file>]` | Downloads one file of a ready model (default `glb`; `glb_web` is the browser build), following the signed redirect. Free. |
| `3d publish <id> [--unpublish] [--json]` | Key-free URLs and a two-line `<car-3d>` embed hosted by Car Image, printed ready to paste; `--unpublish` takes them down. Free. |
| `3d list [--limit] [--json]` | Your recent 3D requests, newest first. Free. |
| `options` | Views with yaw angles, preset colors with hex and the hex paint rule, sizes, fit modes, backgrounds, trim limits, formats, pricing, catalog coverage, the vehicle-id format. Free. |
| `describe [operationId\|path\|all] [--json]` | Explains any REST endpoint from `/openapi.json`: parameters, enums, defaults, response headers, error codes. |
| `doctor [--json] [--yes] [--no-image]` | Smoke-tests every endpoint with status, latency, cache state and fix hints. Exit 1 on any failure. |
| `billing [--plan pro\|business [--yearly]] [--credits …] [--portal]` | Opens hosted Stripe Checkout for a plan or extra credits, or the billing portal. The CLI never touches card data; an agent runs it only when the human asked. |
| `mcp [--toolset core\|all]` | Runs the stdio MCP server: `core` (default) is the seven core tools (lookups, VIN, images, signed URLs, account), `all` adds make logos, 3D models, image options, the API reference, pricing, help and billing links. |
| `agent-config [--host claude-code\|claude-desktop\|cursor\|chatgpt\|generic] [--remote] [--json]` | Prints ready-to-paste MCP configuration (core toolset, with the `?toolset=all` opt-in noted). |
| `update [--check] [--no-plugins] [--json]` | Updates the CLI now and refreshes the car-image plugin in Claude Code and Codex; `--check` only reports the installed and latest versions. It changes what is installed on the machine, so run it when the user asks. |
| `config path \| get <key> \| set <key> <value> \| list` | Keys: `autoUpdate` (`always`, the default: install updates in the background; `ask`; `never`), `telemetry`, `baseUrl`. |

Global flags: `--json`, `--quiet`, `--base-url`, `--api-key`, `--no-color`, `-h`, `-v`.
Environment: `CAR_IMAGE_API_KEY`, `CAR_IMAGE_API_URL`, `CAR_IMAGE_CONFIG`, `CAR_IMAGE_TELEMETRY=0`, `CAR_IMAGE_NO_UPDATE_CHECK=1` (no background update check or install; `CI` does the same).
Exit codes: `0` ok, `1` failure, `2` usage error.

## Sizing

`get`, `url` and every `--batch` entry share the sizing options. `--width`/`--height` are delivered up to 1024 px (a larger size is clamped by the API, a box keeping its shape); one keeps the aspect ratio, both together return exactly that box (`--width 600 --height 400` is 600×400, no longer a square), placed by `--fit contain` (default: whole car, padded), `cover` (fill and centre-crop) or `inside` (may return a smaller image). `--trim` crops to the car's own bounds before sizing so it fills a non-square slot; `--padding 0-50` keeps a margin (percent of the car's longer side) and only applies with `--trim`. `--background` is `transparent` (default), a CSS color name (`white`, `whitesmoke`) or hex (`rrggbb`, `#rrggbb`, `rgb`, `#rgb`); it flattens PNG and WebP too, and `jpg` defaults to white. `--format auto` lets each client negotiate WebP or PNG from its `Accept` header — on a signed URL, on every load. Nothing is upscaled past 1024.

```bash
car-image get --make Porsche --model 911 --year 2024 --view side --width 1024 --height 512 --trim --padding 6 --out hero.png
car-image url --make Porsche --model 911 --year 2024 --width 600 --height 338 --trim --format auto --ttl 604800
```

A batch file is an array (or `{"images": [...]}`) of 1–50 entries such as `{ "make": "Toyota", "model": "RAV4", "year": 2023, "width": 512, "height": 320, "trim": true, "padding": 5, "background": "white", "format": "webp" }`; an entry may name the vehicle as `"vehicle": "veh_…"` instead, and `"color": "#1a2b3c"` is any paint.

## VINs and 3D models

```bash
car-image vin 1HGCM82633A004352 --json | jq .data.vehicle.id      # -> "veh_3qfyk22gfhsx3", free
car-image get --vehicle veh_3qfyk22gfhsx3 --view front-3-4 --color "#1a2b3c" --out accord.png

car-image 3d create --make Toyota --model Camry --year 2025 --color red --wait --out ./camry   # 100 credits, then downloads every file
car-image 3d get <id> --json | jq .data.status                      # queued | processing | ready | failed
car-image 3d download <id> --format usdz --out camry.usdz
```

`3d create` charges 100 credits the moment it is accepted, cached or not, unless the account already owns that vehicle in that color (then it is free), so a script should keep the returned `id` and rerun `3d get <id> --wait` rather than creating again. The first model of a vehicle takes 10–20 minutes; another color of the same vehicle 1–2 minutes.

`url` sends an `Idempotency-Key` on every call — generated, or `--idempotency-key <key>` (1–255 characters of letters, digits, `.` `_` `:` `-`). The same key with the same request within 24 hours replays the first response (`Idempotent-Replayed: true`) instead of billing again; a different request under the same key is a `422`, and a retry that overtakes the first request still running is a `409` with `Retry-After`. Choose the key yourself when a job queue or a rerun may repeat the command.

## Scripting

`--json` on any command gives machine-readable output. Pair it with `jq`:

```bash
# What does this batch cost, and can I afford it?
credits=$(car-image whoami --json | jq .data.credits)
echo "have $credits credits"

# Resolve, then render by id
resolved=$(car-image resolve "blue 2022 bmw m3" --json)
if [ "$(jq -r .data.confidence <<<"$resolved")" = low ]; then
  echo "ambiguous: $(jq -c '[.data.candidates[].model_slug]' <<<"$resolved")" >&2
  exit 2
fi
car-image get --vehicle "$(jq -r .data.params.vehicle_id <<<"$resolved")" \
  --view "$(jq -r .data.params.view <<<"$resolved")" --color "$(jq -r .data.params.color <<<"$resolved")" --out m3.png
```

The id is what to keep: `--vehicle` cannot be misspelled, and a name the catalog files differently (a "Mazda MX-5 Miata" is `mx-5`) resolves once instead of answering `404` per image.

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

## Make logos

Use MCP `get_make_logo({make: "toyota", width: 256, trim: true})` for an inline
logo, or `car-image logo --make Toyota --width 256 --trim --out toyota-logo.png`
to save it. Both accept the image transforms; MCP `format: "auto"` returns PNG.
Each successful delivery costs 1 credit, including cache hits. There is no signed
logo URL: download and host the file for a site. Do not use the vehicle image URL
tools for logos. On 402, stop and ask the human; never buy credits.

SDK: `client.getMakeLogo({ make: "toyota", width: 256, trim: true })` returns bytes and billing metadata.

Generated logos can be inaccurate; inspect before use. Logos are third-party trademarks,
for referential display only; no license is granted and they sit outside every
VehiclesDB indemnity. [Logo docs](https://carimage.dev/docs/logos?ref=plugin)
· [API terms](https://carimage.dev/terms?ref=plugin#logos).

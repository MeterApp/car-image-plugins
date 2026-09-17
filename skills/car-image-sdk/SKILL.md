---
name: car-image-sdk
description: Write code that calls the Car Image API — the zero-dependency TypeScript SDK (@meterapp/car-image-sdk), the CLI (@meterapp/car-image) for shells, scripts and CI, or plain REST with fetch or curl in any language. Covers client setup, typed errors, retries, batching, keeping the key server-side, downloading renders in bulk, decoding VINs and creating, polling and downloading 3D models from code. Use when implementing or reviewing code that talks to the API; do not use for deciding which vehicle to render (vehicle-catalog) or connecting an agent over MCP (car-image-mcp).
---

# Calling the API from code

Three surfaces, one API. Pick by where the code runs.

| Surface | Use it when |
| --- | --- |
| `@meterapp/car-image-sdk` | TypeScript or JavaScript — Node 20+, edge runtimes, Deno, Bun |
| `@meterapp/car-image` (CLI) | Shell scripts, CI, one-off downloads, bulk jobs |
| REST + `fetch`/`curl` | Any other language |

Full details: [references/typescript.md](references/typescript.md) and [references/cli.md](references/cli.md).

## The SDK in three lines

```bash
npm install @meterapp/car-image-sdk
```

```ts
import { CarImageClient } from "@meterapp/car-image-sdk";

const client = new CarImageClient({ apiKey: process.env.CAR_IMAGE_API_KEY });
const image = await client.getImage({ make: "Porsche", model: "911", year: 2024, view: "side", color: "red", width: 800, height: 450, trim: true });
// image.bytes, image.source ("cache" | "generated"), image.creditsCharged, image.creditsRemaining, image.requestId
```

Zero runtime dependencies. `apiKey` and `baseUrl` fall back to `CAR_IMAGE_API_KEY` and `CAR_IMAGE_API_URL` on a server. Retries on `429` and `503` with full jitter, honoring `Retry-After`, are built in — **and it never retries a `402`**, because being out of credits is not a transient failure.

`ImageParams` takes the vehicle (`make`, `model`, `year`, or `vehicle: "veh_…"`, a stable id), `view`, `color` (a preset name or any hex such as `"#1a2b3c"`), and the sizing options: `size` (`thumb|small|medium|large`) or `width`/`height` (1–1024; both together return exactly that box), `fit` (`contain` default, `cover`, `inside`), `background` (`transparent` default, `white`, `black` or hex), `trim` with `padding` (0–50 %), and `format` (`png`, `webp`, `jpg`, `auto`). The `car-image` skill explains when to use which.

Beyond images (SDK 1.6.0): `client.decodeVin(vin, { year? })` decodes a VIN for free and returns the catalog `vehicle` with its id; `client.vehicle(id)` looks an id up; `client.create3dModel({ make, model, year | vehicle }, { color?, webhookUrl?, webhookSecret?, publish? })` starts a 3D model (1,000 credits, charged at creation; free once the account owns that vehicle and color, `billing.already_owned`), `client.get3dModel(id)` polls it, `client.list3dModels({ limit? })` lists them, `client.download3dModel(id, "glb" | "glb_web" | "usdz" | "fbx" | "thumbnail")` follows the signed redirect and returns the bytes, and `client.publish3dModel(id)` / `client.unpublish3dModel(id)` host a model at key-free URLs with a two-line `<car-3d>` embed (`data.public`). The `car-3d` skill covers the lifecycle, the price and the embed.

## The CLI in one line

```bash
npx @meterapp/car-image get --make Porsche --model 911 --year 2024 --view side --color red --width 800 --height 450 --trim --out porsche.png
```

`car-image login` does a browser device flow and stores the key with mode `0600`. `car-image doctor` smoke-tests every endpoint and tells you what is wrong. `car-image resolve <free text>` prints the parameters and a ready-to-run command. `get` and `url` take `--vehicle veh_…` (instead of make, model and year), `--color` as a preset or `#1a2b3c`, `--fit`, `--background`, `--trim [--padding 0-50]` and `--format png|webp|jpg|auto`; `url` also takes `--idempotency-key`. `car-image vin <VIN> [--year] [--json]` decodes a VIN for free (CLI 1.3.0); `car-image 3d create --make --model --year [--color] [--vehicle] [--webhook-url] [--webhook-secret] [--wait] [--out <dir>] [--json]`, `3d get <id> [--wait] [--json]`, `3d download <id> [--format glb|usdz|fbx|thumbnail] [--out <file>]` and `3d list [--limit] [--json]` handle 3D models.

## Errors are typed

```ts
import { CarImageError } from "@meterapp/car-image-sdk";

try {
  await client.getImage({ make, model, year });
} catch (error) {
  if (error instanceof CarImageError) {
    if (error.status === 402) {
      // Out of credits. Surface it to a human; do not buy credits in code.
      throw new Error(`Car Image API out of credits (request ${error.requestId})`);
    }
    if (error.status === 404) {
      // Not in the catalog — resolve or search for the canonical name.
    }
  }
  throw error;
}
```

`CarImageError` carries `status`, `title`, `detail`, `requestId` and the raw RFC 9457 problem. **Log `requestId`; never log the key.**

## Rules that matter more than the syntax

**The key is a server-side secret.** `process.env.CAR_IMAGE_API_KEY` in a server file, a route handler, a script, or a CI secret. Never in a client component, never in `NEXT_PUBLIC_*`, never in a committed `.env`. If the browser needs the image, mint a signed URL — the `car-image-urls` skill covers it.

**Every image is a credit.** A loop over 500 vehicles costs 500 credits ($0.50). That is fine if intended and a surprise if not, so:

- Check `get_account` / `client.account()` before a large job.
- Print progress and a running credit count in bulk scripts.
- Make bulk scripts resumable — skip files that already exist on disk, so a crash at item 400 does not re-bill the first 399.
- Never write a retry loop around a `402`. A `402` with `code: "plan_vehicle_limit"` is not a balance problem: the job named more new distinct vehicles than the plan allows this month (`plan`, `vehicles_this_month`, `vehicles_per_month`, `requested` on the problem); report it and stop.

**Batch what can be batched.** `createImageUrls` takes up to 50 images in one call. Fifty separate calls cost the same credits but waste time and rate limit.

**Retries of a paid `POST` are already safe.** `createImageUrls` sends an `Idempotency-Key` (`sdk_<uuid>`) with every call, so the SDK's own retry after a dropped connection replays the first response instead of minting and billing again. When the retry may come from another process — a job queue, a cron, a rebuilt page — pass `{ idempotencyKey }` yourself (1–255 characters of letters, digits, `.` `_` `:` `-`): the server replays the same key with the same body for 24 hours (`Idempotent-Replayed: true`), answers `422` to the same key with a different body, and `409` with `Retry-After` while the first request is still running. Over plain REST, set the header on `POST /api/v1/image-urls`.

**Respect the rate limit.** 120 requests per minute per key on Free and Pro, 600 on Business, 1,200 on Enterprise, plus a per-account limit across every key (`code: "account_rate_limited"` on the 429). In a bulk job, run a small concurrency (4-8) rather than firing everything at once, and let the SDK's backoff handle `429`.

**Cache on identity.** The same make/model/year/view/color/size is the same image. Key your cache on those — or better, on the stable `vehicle_id` every response echoes — not on a URL, and you will stop paying for renders you already have.

**A 3D model is 1,000 credits, once.** `create3dModel` charges at creation for a vehicle and color the account does not own yet, so guard it the way you would a purchase: check `client.account()`, keep the request `id` so a rerun polls `get3dModel` instead of creating again, and let the SDK's `Idempotency-Key` cover a dropped connection. A vehicle and color the account already owns is free to order again (`billing.already_owned`), so a re-run is never a second bill. Poll every 10–15 seconds; a faster loop only sees the same answer. For a web page, pass `publish: true` (or call `publish3dModel`) and put `data.public.embed.html` in the page: the files are hosted by Car Image and no key is needed.

## A bulk download that behaves

```ts
import { CarImageClient, CarImageError } from "@meterapp/car-image-sdk";
import { writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";

const client = new CarImageClient({ apiKey: process.env.CAR_IMAGE_API_KEY });

async function download(vehicles: Array<{ make: string; model: string; year: number }>) {
  await mkdir("out", { recursive: true });
  const { data: account } = await client.account();
  if (account.credits < vehicles.length) {
    throw new Error(`Need ${vehicles.length} credits, have ${account.credits}. Top up before running.`);
  }

  for (const vehicle of vehicles) {
    const file = `out/${vehicle.year}-${vehicle.make}-${vehicle.model}.png`.toLowerCase().replace(/\s+/g, "-");
    if (existsSync(file)) continue; // resumable: never re-bill a finished item

    try {
      const image = await client.getImage({ ...vehicle, view: "front-3-4", size: "medium" });
      await writeFile(file, image.bytes);
      console.log(`${file}  ${image.source}  ${image.creditsRemaining} credits left`);
    } catch (error) {
      if (error instanceof CarImageError && error.status === 402) throw error; // stop; do not burn the rest
      if (error instanceof CarImageError && error.status === 404) {
        console.warn(`skip ${vehicle.make} ${vehicle.model} ${vehicle.year}: not in the catalog`);
        continue;
      }
      throw error;
    }
  }
}
```

Checks the budget first, skips finished work, stops dead on `402`, and reports what it skipped and why.

## REST directly

```bash
curl --fail-with-body -H "Authorization: Bearer $CAR_IMAGE_API_KEY" \
  "https://carimage.dev/api/v1/images/car?make=porsche&model=911&year=2024&view=front-3-4&color=red&size=medium&format=webp" \
  --output porsche-911.webp

# Exactly 600×400, car trimmed to fill the box, on a light grey background (hex without the #)
curl --fail-with-body -H "Authorization: Bearer $CAR_IMAGE_API_KEY" \
  "https://carimage.dev/api/v1/images/car?make=porsche&model=911&year=2024&view=side&w=600&h=400&trim=1&padding=6&background=f4f4f4" \
  --output porsche-911-600x400.png
```

The query spells the vehicle as `make`, `model` and `year`, or as `vehicle=veh_…` (a stable id); the paint as `color=<preset>` or `color=1a2b3c` (bare hex; responses echo `#1a2b3c`); the dimensions `w` and `h` (1–1024), with `fit=contain|cover|inside` (default `contain`), `background=transparent|white|black|<hex>`, `trim=1` with `padding=0-50`, and `format=png|webp|jpg|auto` (`auto` answers with `Vary: Accept`). `GET /api/v1/vin/{vin}` decodes a VIN for free; `POST /api/v1/3d` (1,000 credits, send an `Idempotency-Key`), `GET /api/v1/3d/{id}` and `GET /api/v1/3d/{id}/files/{kind}` (a 302 to a one-hour signed URL; `curl -L`) are the 3D endpoints. Response headers carry `X-Credits-Charged`, `X-Credits-Remaining`, `X-Image-Source` (`cache` or `generated`), `X-Image-Width`, `X-Image-Height` and `X-Request-Id`. The machine-readable contract is [`/openapi.json`](https://carimage.dev/openapi.json); `car-image describe <operationId>` explains any endpoint from it.

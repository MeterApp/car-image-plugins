---
name: car-image-sdk
description: Write code that calls the Car Image API — the zero-dependency TypeScript SDK (@meterapp/car-image-sdk), the CLI (@meterapp/car-image) for shells, scripts and CI, or plain REST with fetch or curl in any language. Covers client setup, typed errors, retries, batching, keeping the key server-side, and downloading renders in bulk. Use when implementing or reviewing code that talks to the API; do not use for deciding which vehicle to render (vehicle-catalog) or connecting an agent over MCP (car-image-mcp).
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
const image = await client.getImage({ make: "Porsche", model: "911", year: 2024, view: "side", color: "red" });
// image.bytes, image.source ("cache" | "generated"), image.creditsCharged, image.creditsRemaining, image.requestId
```

Zero runtime dependencies. `apiKey` and `baseUrl` fall back to `CAR_IMAGE_API_KEY` and `CAR_IMAGE_API_URL` on a server. Retries on `429` and `503` with full jitter, honoring `Retry-After`, are built in — **and it never retries a `402`**, because being out of credits is not a transient failure.

## The CLI in one line

```bash
npx @meterapp/car-image get --make Porsche --model 911 --year 2024 --view side --color red --out porsche.png
```

`car-image login` does a browser device flow and stores the key with mode `0600`. `car-image doctor` smoke-tests every endpoint and tells you what is wrong. `car-image resolve <free text>` prints the parameters and a ready-to-run command.

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
- Never write a retry loop around a `402`.

**Batch what can be batched.** `createImageUrls` takes up to 50 images in one call. Fifty separate calls cost the same credits but waste time and rate limit.

**Respect the rate limit.** 120 requests per minute per key by default. In a bulk job, run a small concurrency (4-8) rather than firing everything at once, and let the SDK's backoff handle `429`.

**Cache on identity.** The same make/model/year/view/color/size is the same image. Key your cache on those, not on a URL, and you will stop paying for renders you already have.

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
```

Response headers carry `X-Credits-Charged`, `X-Credits-Remaining`, `X-Image-Source` (`cache` or `generated`) and `X-Request-Id`. The machine-readable contract is [`/openapi.json`](https://carimage.dev/openapi.json); `car-image describe <operationId>` explains any endpoint from it.

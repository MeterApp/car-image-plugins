# `@meterapp/car-image-sdk`

Zero runtime dependencies. Node 20+, Vercel and Cloudflare edge runtimes, Deno, Bun, and browsers (browsers may only redeem signed URLs — never give one a key).

```bash
npm install @meterapp/car-image-sdk
```

## Constructing the client

```ts
import { CarImageClient } from "@meterapp/car-image-sdk";

const client = new CarImageClient({
  apiKey: process.env.CAR_IMAGE_API_KEY, // falls back to CAR_IMAGE_API_KEY on a server
  baseUrl: process.env.CAR_IMAGE_API_URL, // falls back to CAR_IMAGE_API_URL, default https://carimage.dev
});
```

Construct it once per process, at module scope. It holds no connection state, so a single instance is safe to share.

## Methods

| Method | Returns | Costs |
| --- | --- | --- |
| `getImage(params, options?)` | `ImageResult` — `bytes`, `contentType`, `width`, `height`, `creditsCharged`, `creditsRemaining`, `source`, `etag`, `requestId` | 1 credit |
| `getImageUrl(params, options?)` | One signed delivery URL | 1 credit |
| `createImageUrls(images, { ttlSeconds, maxUses }?)` | `data[]` of `{ id, url, expires_at, max_uses, … }` — 1 to 50 images | 1 credit per URL |
| `resolve(query, options?)` | `data.params`, `candidates`, `confidence` | free |
| `searchVehicles(query, options?)` | Canonical makes, models and available years | free |
| `vehicles(filter?, options?)` | Years, or makes for a year, or models for a year and make | free |
| `options(options?)` | Views with yaw angles, colors with hex, sizes, formats, pricing | free |
| `account(options?)` | `data.credits`, `auto_reload`, `has_payment_method`, `pricing`, `usage_30d`, `key.scopes` | free |
| `feedback(input, options?)` | Acknowledgement | free |
| `health(options?)` / `openapi(options?)` | Service status / the OpenAPI document | free |

`vehicles()` is overloaded: no filter returns years, `{ year }` returns makes, `{ year, makeId }` returns models.

`ImageParams`: `make`, `model`, `year`, and optionally `view`, `color`, `size` (`thumb|small|medium|large`) or `width`/`height` up to 1024, and `format` (`png|webp|jpg`).

## Errors

```ts
import { CarImageError } from "@meterapp/car-image-sdk";
```

`CarImageError` exposes `status`, `title`, `detail`, `requestId` and the raw RFC 9457 problem document. Everything else throws normally (network failures, aborts).

Built-in retry: `429` and `503` with full jitter, honoring `Retry-After`. **`402` is never retried.** Do not wrap calls in your own retry loop — you would fight the built-in backoff and risk re-billing.

`createImageUrls` validates the batch locally and throws `RangeError` for an empty array or more than 50 images, before spending anything.

## Next.js

Keep the client in a server-only module and hand the browser signed URLs.

```ts
// lib/car-image.ts   (server only)
import "server-only";
import { CarImageClient } from "@meterapp/car-image-sdk";

export const carImage = new CarImageClient({ apiKey: process.env.CAR_IMAGE_API_KEY });
```

```ts
// app/api/car-image/route.ts
import { carImage } from "@/lib/car-image";
import { CarImageError } from "@meterapp/car-image-sdk";

export async function POST(request: Request) {
  const { make, model, year } = await request.json();
  try {
    const { data } = await carImage.createImageUrls([{ make, model, year, view: "side" }], {
      ttlSeconds: 24 * 60 * 60,
      maxUses: 0,
    });
    return Response.json({ url: data[0].url, expiresAt: data[0].expires_at });
  } catch (error) {
    if (error instanceof CarImageError) {
      return Response.json({ error: error.detail, requestId: error.requestId }, { status: error.status });
    }
    throw error;
  }
}
```

Cache the result keyed on the vehicle parameters. Without a cache, every request to this route bills a credit.

`CAR_IMAGE_API_KEY` belongs in your platform's environment variables — never in `NEXT_PUBLIC_*`, never in a committed `.env`, never in a client component.

## Edge runtimes

The SDK is `fetch`-based with no Node built-ins, so it runs unchanged on Vercel Edge, Cloudflare Workers and Deno Deploy. `getImage` returns `bytes` as a `Uint8Array`; stream or re-wrap it rather than converting to a Node `Buffer` on an edge runtime.

## MCP tool definitions

`@meterapp/car-image-sdk/mcp` exports the shared tool definitions used by both the hosted and the stdio MCP servers — names, descriptions, JSON schemas and annotations. Import them if you are building your own agent surface and want the tool contracts to match the official ones exactly.

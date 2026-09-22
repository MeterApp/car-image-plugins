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
| `createImageUrls(images, { ttlSeconds, maxUses, renew, renewDays, idempotencyKey }?)` | `data[]` of `{ id, url, expires_at, max_uses, renews_until, … }` — 1 to 50 images; `renew: true` keeps a URL alive past the TTL at 1 credit per opened window (email, CMS, PDFs); an `Idempotency-Key` (generated unless `idempotencyKey` is given) makes a retry replay instead of re-bill | 1 credit per URL, plus 1 per opened renewal window |
| `resolve(query, options?)` | `data.params` (with `vehicle_id`), `candidates`, `confidence` (`"high"`, `"medium"` or `"low"`) | free |
| `searchVehicles(query, options?)` | Canonical makes, models, available years and a vehicle id per year | free |
| `vehicles(filter?, options?)` | Years, or makes for a year, or models for a year and make (with ids) | free |
| `vehicle(id, options?)` | One catalog vehicle by its stable `veh_…` id: make, model, year, every year, image paths | free |
| `decodeVin(vin, { year? }?, options?)` | `data.valid`, `errors`, `year`, `make`, `model`, `trim`, `engine`, `attributes` (every vPIC variable) and `vehicle` (`{ id, make, model, year, image_path }` or null); full or partial VINs | free |
| `create3dModel({ make, model, year \| vehicle }, { color?, webhookUrl?, webhookSecret?, publish?, idempotencyKey? }?)` | `data` (the 3D request: `id`, `status`, `progress`, `files` once ready, `public` once published) and `billing` (`already_owned` when the account already had the vehicle and color: free); an `Idempotency-Key` is sent unless given | 100 credits at creation |
| `get3dModel(id, options?)` | The same request, refreshed; poll every 10–15 s until `status` is `ready` or `failed` | free |
| `list3dModels({ limit? }?, options?)` | Recent 3D requests, newest first, plus `pricing.credits_per_model` | free |
| `download3dModel(id, "glb" \| "glb_web" \| "usdz" \| "fbx" \| "thumbnail", options?)` | The file's bytes (follows the one-hour signed redirect) with `contentType` | free |
| `publish3dModel(id, options?)` / `unpublish3dModel(id, options?)` | The request with `data.public` (`id`, key-free `url` and `files`, `embed.html` to paste) or with `public: null` again | free |
| `options(options?)` | Views with yaw angles, colors with hex, sizes, fit modes (`fits`, `default_fit`), `backgrounds`, `trim` limits, formats, pricing | free |
| `account(options?)` | `data.credits`, `auto_reload`, `has_payment_method`, `pricing`, `usage_30d`, `key.scopes` | free |
| `feedback(input, options?)` | Acknowledgement | free |
| `health(options?)` / `openapi(options?)` | Service status / the OpenAPI document | free |

`vehicles()` is overloaded: no filter returns years, `{ year }` returns makes, `{ year, makeId }` returns models.

`ImageParams`: `make`, `model`, `year` (or `vehicle`, a stable `veh_…` id in place of the three), and optionally `view`, `color` (a preset name or any hex such as `"#1a2b3c"`), `size` (`thumb|small|medium|large`) or `width`/`height` (1–1024 each), `fit` (`contain` default, `cover`, `inside` — only matters with both dimensions, which return exactly `width`×`height`), `background` (`transparent` default, `white`, `black`, or hex as `rrggbb`, `#rrggbb`, `rgb`, `#rgb`; `jpg` defaults to white), `trim` (crop to the car's bounds before sizing) with `padding` (0–50 % of its longer side, only with `trim`), and `format` (`png|webp|jpg|auto`; `auto` negotiates WebP or PNG from `Accept`). `assertImageParams` throws before any request for dimensions outside 1–1024 or a `padding` without `trim`. The constants `FITS`, `REQUEST_FORMATS`, `MAX_DIMENSION` and `MAX_PADDING_PERCENT` are exported for validation and UI.

Retrying `createImageUrls` is safe by construction: every call carries an `Idempotency-Key` (`sdk_<uuid>`), so a `POST` whose connection dropped is retried like a `GET` and the server replays the first answer rather than minting again. Pass `idempotencyKey` yourself when the retry may come from another process; the server keeps a key for 24 hours, answers `422` to the same key with a different body and `409` (`Retry-After`) while the original is still running.

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

Tools come in two sets: `MCP_TOOLSETS.core` (`DEFAULT_MCP_TOOLSET`, `"core"`) is the twelve core tools (images, signed URLs, catalog, `decode_vin`, `create_3d_model`, `get_3d_model`, `publish_3d_model`) and `MCP_TOOLSETS.all` adds the eight request-board tools; `McpToolset` is the type, `isMcpToolset(value)` validates a name from a URL or flag, and `mcpInstructions(toolset)` returns the server instructions for either set. The hosted server serves `core` at `https://carimage.dev/api/mcp` and `all` at `https://carimage.dev/api/mcp?toolset=all`; the stdio server takes `car-image mcp --toolset all`.

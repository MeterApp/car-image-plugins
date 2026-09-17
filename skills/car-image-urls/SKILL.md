---
name: car-image-urls
description: Put a vehicle image into a web page, React component, email, Markdown file, PDF or slide deck using signed delivery URLs, so the browser loads the image without ever holding an API key. Use whenever the output is HTML, JSX, Markdown, CSS, an email template, a document or a spreadsheet rather than bytes on disk; covers TTL and use caps, batching up to 50, caching, alt text and expiry. Do not use for downloading bytes in a script (car-image), or for finding which vehicle to render (vehicle-catalog).
---

# Signed delivery URLs

A signed URL is a key-free link to one rendered vehicle image. You mint it server-side; the browser, email client or PDF reader loads it directly. **This is the only correct way to show a Car Image render in something a user's browser opens.**

## Why not just call the image endpoint from the page

`GET /api/v1/images/car` needs `Authorization: Bearer cimg_…`. Anything in a browser — an `<img src>`, a `fetch` in client-side JavaScript, a CSS `background-image` — is readable by the user and by anyone they share the page with. Putting the key there leaks it permanently.

Signed URLs solve this: the signature authorizes exactly one image for a limited time, and carries no key.

## The call

With MCP connected, use `create_car_image_urls`. Over REST it is `POST /api/v1/image-urls`:

```json
{
  "images": [
    { "make": "Porsche", "model": "911", "year": 2024, "view": "side", "color": "red", "width": 768, "height": 432, "trim": true, "format": "auto" }
  ],
  "ttl_seconds": 86400,
  "max_uses": 0
}
```

Each entry returns `id`, `url`, `expires_at`, `max_uses`, `renews_until` and the normalized vehicle (which opens with `vehicle_id` and echoes `fit`, `background`, `trim` and `padding`). An entry may name the vehicle as `"vehicle": "veh_…"` (a stable id) instead of make, model and year, and `"color": "#1a2b3c"` is any paint at the same price.

- **`images`** — 1 to 50 per call. Body limit is 64 KiB; split larger jobs into batches of 50. Each entry takes the same sizing options as `get_car_image`: `size` or `width`/`height` (1–1024; both together return exactly that box), `fit` (`contain` default, `cover`, `inside`), `background` (`transparent` default, `white`, `black` or hex), `trim` with `padding` (0–50 %), and `format` (`png`, `webp`, `jpg`, `auto`). The `car-image` skill has the full table.
- **`ttl_seconds`** — 60 to 604800 (7 days). Default 3600.
- **`max_uses`** — `0` means unlimited loads until expiry. A positive number caps redemptions and returns `410` afterwards.
- **`renew`** — `true` makes the URL auto-renew: the first load in each further window of `ttl_seconds` bills one more credit and keeps it alive, until `renew_days` (1–365, default 365) from creation. Requires `max_uses: 0`. See "Surfaces that outlive a TTL" below.
- **`Idempotency-Key` header** — send one (1–255 characters of letters, digits, `.` `_` `:` `-`) whenever the call might be repeated: a job queue, a build step, a retried request. The same key with the same body within 24 hours replays the first response (`Idempotent-Replayed: true`) instead of minting and billing a second batch; the same key with a different body is a `422`; a retry that overtakes the original still in flight is a `409` with `Retry-After`. The SDK sends a generated key on every `createImageUrls` call (pass `idempotencyKey` to choose it), the CLI takes `--idempotency-key`, and the MCP tool takes `idempotency_key` as an argument (a replay comes back with `idempotent_replayed: true`).

## What it costs

**1 credit per URL, charged when the URL is created.** Loading it is free, however many times, until it expires. Ten URLs cost 10 credits (1¢) whether they are loaded once or a million times.

So: mint once, cache the URL, reuse it. Do not re-mint the same image on every page render — that bills a credit every time.

## Choosing a TTL

The TTL is a cache lifetime, not a security boundary — anyone with the URL can load it until it expires. Match it to how the page is served.

| Surface | TTL | Why |
| --- | --- | --- |
| Static site, build-time generation | 7 days (`604800`), re-mint on each build | Longest window; the build owns the refresh. |
| Server-rendered page, cached in your DB | 1-7 days | Store `url` and `expires_at`; re-mint when `expires_at` is near. |
| Per-request SSR with no storage | 1 hour (default) | The page outlives the URL only if the user leaves the tab open. |
| Email | 7 days, `max_uses: 0`, `renew: true` | Mail is opened days, months or a year later. A renewable URL keeps working at one credit per opened week; a plain 7-day URL is a broken image by week two. |
| CMS page or PDF nobody re-publishes | 7 days, `renew: true` | Same reasoning as email: the surface is rendered once and read for a long time. |
| One-off share link | Short TTL plus `max_uses` | The only case where a use cap helps. |

**Never mint a URL inside a React render, a `useEffect`, or a hot request path without caching.** That is a credit per call.

## Surfaces that outlive a TTL

An email, a PDF or a page in a CMS nobody re-publishes is rendered once and opened whenever the reader gets to it. For those, mint with `renew: true`:

```json
{ "images": [{ "make": "Porsche", "model": "911", "year": 2024, "view": "front-3-4", "color": "red", "width": 480 }], "ttl_seconds": 604800, "renew": true }
```

- The URL is created and charged like any other. When it is loaded after `expires_at`, the first load in each new window of `ttl_seconds` bills **one more credit** and renews it; every further load in that window is free and cacheable, exactly like the first window. Windows nobody opens cost nothing.
- With the 7-day maximum TTL the ceiling is one credit per image per opened week, about five cents for an image opened every week for a year.
- Billing is once per window whatever the open count: the ledger reference `renew:<id>:<window>` is unique, so two mail proxies racing on the first open pay once.
- An account that cannot pay a renewal gets `402` on that load and the image shows as broken until credits land; the URL itself stays valid and resumes on its next load. Suggest auto-reload for production accounts.
- Revoking the key still ends the URL (`403`), renewals included.
- `renew` cannot be combined with a use cap (`max_uses` must be 0).

Store `renews_until` next to the URL. The story at https://carimage.dev/customers/car-images-in-email?ref=plugin shows the exact email HTML.

## Patterns

### Next.js — server component

```tsx
import { CarImageClient } from "@meterapp/car-image-sdk";

const client = new CarImageClient({ apiKey: process.env.CAR_IMAGE_API_KEY });

export default async function Hero() {
  const { data } = await client.createImageUrls(
    [{ make: "Porsche", model: "911", year: 2024, view: "side", color: "red", width: 768, height: 432, trim: true, format: "auto" }],
    { ttlSeconds: 86_400, idempotencyKey: "hero-porsche-911-2024-side-red" }
  );
  return <img src={data[0].url} alt="2024 Porsche 911, side view, red" width={768} height={432} />;
}
```

`width` and `height` together return exactly 768×432, so the `<img>` attributes match the bytes; `trim` makes the car fill that wide box instead of floating in a square. Wrap it in your data cache (`unstable_cache`, ISR, or your own table) keyed by the vehicle parameters so a page view does not mint a new URL — the idempotency key stops a retried build from paying twice, not a hot path from minting on every request.

### A batch for a comparison grid

```ts
const vehicles = [
  { make: "Toyota", model: "RAV4", year: 2023 },
  { make: "Honda", model: "CR-V", year: 2023 },
  { make: "Mazda", model: "CX-5", year: 2023 },
];
const { data } = await client.createImageUrls(
  vehicles.map((v) => ({ ...v, view: "front-3-4", color: "silver", width: 512 })),
  { ttlSeconds: 604_800 }
);
```

One call, three credits. Results come back in request order.

### Markdown and email

```md
![2022 BMW M3, front three-quarter view, blue](https://carimage.dev/api/v1/delivery/eyJ2IjoxLCJ…)
```

Transparent PNG sits on any background, which is what you want in a document. For email, ask for a solid `background` (`"white"`, or the hex of the surrounding table cell) — it flattens PNG and WebP too, and `jpg` defaults to white — because some older mail clients render PNG transparency as black.

## Getting the image right

- **Transparent by default.** `format: "png"` has a real alpha channel, so the render drops onto any background without a box around it. Choose `webp` for smaller files with transparency, `jpg` only when the surface cannot do alpha, and `auto` for an `<img>` any browser will load: the URL negotiates WebP or PNG from each client's `Accept` header on every load.
- **Ask for the box you will display**, up to 1024 on each side. With both `width` and `height` the image comes back exactly that size (`fit: "contain"`, the default, keeps the whole car and pads the rest; `"cover"` fills the box and crops). For a non-square slot add `trim: true` so the car fills it instead of floating in the square source frame, with `padding` (0–50 %) for breathing room. A 512 px render in a 256 px slot wastes bytes; a 256 px render in a 512 px slot looks soft, and nothing is upscaled past 1024. For retina, request 2× the CSS size.
- **Set `width` and `height` on the `<img>`** so the page does not reflow while it loads — the values you asked for, since that is exactly what comes back.
- **Alt text describes the vehicle**: "2024 Porsche 911, side view, red". Not "car", not "image".
- **Cache publicly.** Delivery URLs are safe to put behind a CDN for their TTL; that is the point of them.

## Expiry is a real state

`expires_at` comes back with every URL. Whatever stores the URL must store that too.

- Re-mint before expiry, not after a user reports a broken image.
- A `403` on a delivery URL means expired, invalid, the key that created it was revoked, or `code: "origin_not_allowed"`: the page loading it is on a site the issuing key's allowed origins (set on the key in the dashboard) do not list; loads without a `Referer` or `Origin`, such as email clients, pass. A `410` means a use-capped URL hit its cap. Both are fixed by minting a fresh URL, not by retrying the old one. A `402` means a renewable URL entered a new window the account could not pay for; add credits and the same URL resumes.
- If you hand a user a URL in chat, tell them when it expires.

## Do not

- Put `CAR_IMAGE_API_KEY` in client-side code, an `<img src>`, or a committed config file. Mint a signed URL instead.
- Mint a URL per request or per render without caching — each one is a credit.
- Treat a signed URL as private. It is unguessable, not access-controlled.
- Present a render as a photograph of one specific listed vehicle. It represents the model.

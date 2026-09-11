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
    { "make": "Porsche", "model": "911", "year": 2024, "view": "side", "color": "red", "width": 768, "format": "webp" }
  ],
  "ttl_seconds": 86400,
  "max_uses": 0
}
```

Each entry returns `id`, `url`, `expires_at`, `max_uses` and the normalized vehicle.

- **`images`** — 1 to 50 per call. Body limit is 64 KiB; split larger jobs into batches of 50.
- **`ttl_seconds`** — 60 to 604800 (7 days). Default 3600.
- **`max_uses`** — `0` means unlimited loads until expiry. A positive number caps redemptions and returns `410` afterwards.

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
| Email | 7 days, `max_uses: 0` | Mail clients fetch images late, re-fetch on every open, and proxy through caches. A short TTL means a broken image a week later. |
| One-off share link | Short TTL plus `max_uses` | The only case where a use cap helps. |

**Never mint a URL inside a React render, a `useEffect`, or a hot request path without caching.** That is a credit per call.

## Patterns

### Next.js — server component

```tsx
import { CarImageClient } from "@meterapp/car-image-sdk";

const client = new CarImageClient({ apiKey: process.env.CAR_IMAGE_API_KEY });

export default async function Hero() {
  const { data } = await client.createImageUrls(
    [{ make: "Porsche", model: "911", year: 2024, view: "side", color: "red", width: 768 }],
    { ttlSeconds: 86_400 }
  );
  return <img src={data[0].url} alt="2024 Porsche 911, side view, red" width={768} height={432} />;
}
```

Wrap it in your data cache (`unstable_cache`, ISR, or your own table) keyed by the vehicle parameters so a page view does not mint a new URL.

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

Transparent PNG sits on any background, which is what you want in a document. For email, prefer `jpg` or `webp` with a solid backdrop in the surrounding table cell — some older mail clients render PNG transparency as black.

## Getting the image right

- **Transparent by default.** `format: "png"` has a real alpha channel, so the render drops onto any background without a box around it. Choose `webp` for smaller files with transparency, `jpg` only when the surface cannot do alpha.
- **Ask for the width you will display**, up to 1024. A 512 px render in a 256 px slot wastes bytes; a 256 px render in a 512 px slot looks soft. For retina, request 2× the CSS width.
- **Set `width` and `height` on the `<img>`** so the page does not reflow while it loads.
- **Alt text describes the vehicle**: "2024 Porsche 911, side view, red". Not "car", not "image".
- **Cache publicly.** Delivery URLs are safe to put behind a CDN for their TTL; that is the point of them.

## Expiry is a real state

`expires_at` comes back with every URL. Whatever stores the URL must store that too.

- Re-mint before expiry, not after a user reports a broken image.
- A `403` on a delivery URL means expired, invalid, or the key that created it was revoked. A `410` means a use-capped URL hit its cap. Both are fixed by minting a fresh URL, not by retrying the old one.
- If you hand a user a URL in chat, tell them when it expires.

## Do not

- Put `CAR_IMAGE_API_KEY` in client-side code, an `<img src>`, or a committed config file. Mint a signed URL instead.
- Mint a URL per request or per render without caching — each one is a credit.
- Treat a signed URL as private. It is unguessable, not access-controlled.
- Present a render as a photograph of one specific listed vehicle. It represents the model.

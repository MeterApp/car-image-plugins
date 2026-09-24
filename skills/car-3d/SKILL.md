---
name: car-3d
description: Get a textured 3D model (GLB, USDZ, FBX and a thumbnail) of any real vehicle in any paint color from the Car Image API, for AR views, configurators, game assets, product pages and 3D scenes, and put it on a web page with a two-line embed that Car Image hosts. Covers what a model costs (100 credits, charged at creation, free once the account owns that vehicle in that color), how long it takes, polling versus webhooks, verifying the webhook signature, downloading the files, publishing a model and the <car-3d> element. Use when the user wants a 3D model, a GLB, a USDZ, an FBX, an AR-ready asset of a car, or a 3D car on a page; do not use for 2D renders (car-image), signed image URLs (car-image-urls) or finding which vehicle to model (vehicle-catalog).
---

# 3D models of real vehicles

`POST /api/v1/3d` turns any catalog vehicle, in any paint, into a textured 3D model: **GLB, USDZ, FBX, a thumbnail and `glb_web`**, a browser build of the GLB a tenth the size. Models are built from the same renders the image API serves, so a model matches the pictures the user already shows, and every color of a vehicle is one mesh with a different texture.

With MCP connected the tools are `create_3d_model`, `get_3d_model` and `publish_3d_model`. Over REST: `POST /api/v1/3d`, `GET /api/v1/3d/{id}`, `GET /api/v1/3d/{id}/files/{kind}`, `GET /api/v1/3d?limit=`, `POST|DELETE /api/v1/3d/{id}/publish`, and the key-free `GET /api/v1/3d/public/{public_id}`. The CLI has `car-image 3d create|get|download|list|publish`; the SDK has `create3dModel`, `get3dModel`, `list3dModels`, `download3dModel`, `publish3dModel` and `unpublish3dModel`. Full reference: [`/docs/3d`](https://carimage.dev/docs/3d?ref=plugin).

## What it costs — say this first

- **100 credits ($1.00) per vehicle and color**, charged at creation whether the model is cached, in progress or new. Cache state never changes the price, exactly as with images.
- **Free once owned.** An account that already holds a live request for a vehicle in a color owns it: ordering it again creates a new request for nothing (`billing.credits_charged: 0`, `billing.already_owned: true`), whatever spelling, whether the model is ready or still being made, and even after Car Image rebuilds models with a better recipe. So a re-order is never a second bill; only a failed model (refunded, not owned) makes the next attempt a charged one.
- Polling, listing, downloads, webhook deliveries, **publishing and every load of a published model are free**.
- A model that **fails is refunded** in full. A `503` at capacity charges nothing.
- A request is a hundred times an image: **tell the user the price and confirm before calling `create_3d_model`** for a vehicle and color the account does not own yet, and call `get_account` first when the balance may be short. Never retry a `402`.

## How long it takes

| Case | Wall time | Why |
| --- | --- | --- |
| First model of a vehicle | **10–20 minutes** | The four source views are rendered and waited for (`stage: views`), the mesh is built and finished (`geometry`) and the color composed (`texture`). |
| Another color of the same vehicle | **1–2 minutes** | The finished mesh already exists; only the paint changes. |
| Someone already asked for this vehicle in this color | immediate | `200` with `status: "ready"` and the files; charged unless the account already owns it. |

Say this before the user waits. Do not present a model as instant.

## The request

```json
{ "make": "Toyota", "model": "Camry", "year": 2025, "color": "red", "publish": true }
```

- Name the vehicle with `make`, `model` and `year`, **or** with `vehicle`, a stable catalog id such as `veh_errc87t1jgata` (from `search_vehicles`, `resolve_vehicle` or `decode_vin`). Both together is a `400`; an unknown id is a `404`.
- `color` is one of the 15 presets or any hex (`"#1a2b3c"` or `"1a2b3c"`); the response echoes `#1a2b3c`. Default `silver`.
- `publish: true` publishes the model at once (below). Free. Pass it whenever the model is for a web page.
- `webhook_url` (public HTTPS) and `webhook_secret` are optional; see below.
- Send an `Idempotency-Key` header over REST so a retried request replays the first answer instead of charging again (the SDK and CLI do this for you).

Resolve free text first (`vehicle-catalog` skill): a model of the wrong car costs 100 credits.

## The response and its lifecycle

`202 Accepted` while the model is queued or processing, `200` when it was already ready:

```json
{
  "data": {
    "id": "0c5e0b2a-…", "object": "3d_model",
    "status": "processing", "progress": 35, "stage": "geometry",
    "vehicle": { "id": "veh_errc87t1jgata", "make": "toyota", "model": "camry", "year": 2025 },
    "color": "red", "generator": "meshy-7.1",
    "files": null, "polycount": null, "error": null,
    "estimated_seconds_remaining": 170, "webhook": null,
    "public": { "id": "m3d_7f2k9q4hxn2b5c8d", "url": "https://carimage.dev/api/v1/3d/public/m3d_7f2k9q4hxn2b5c8d", "files": null, "embed": { "script": "https://carimage.dev/embed/3d.js", "html": "<script src=\"https://carimage.dev/embed/3d.js\" async></script>\n<car-3d model=\"m3d_7f2k9q4hxn2b5c8d\"></car-3d>" }, "published_at": "…" },
    "created_at": "…", "updated_at": "…", "ready_at": null
  },
  "billing": { "charged_on": "creation", "credits_charged": 100, "credits_remaining": 3870, "already_owned": false },
  "request_id": "…"
}
```

`status` goes `queued` → `processing` → `ready` or `failed`. `progress` is 0–100; `estimated_seconds_remaining` is a rough guide, not a promise. When `ready`, `files` holds `glb`, `glb_web`, `usdz`, `fbx` and `thumbnail`, each `{url, bytes, content_type}`. When `failed`, `error` carries `{code, message}` and the credits were refunded; asking again makes a fresh attempt. `public` is `null` until the request is published.

`id` is the user's request; the shared model behind it is never exposed. Every request is its own record with its own webhook and its own publish state.

## Waiting: poll or webhook

**Poll** `get_3d_model` / `GET /api/v1/3d/{id}` every **10–15 seconds**. The server re-reads the generator only when its last look is older than 15 seconds, so a tighter loop sees the same answer and wastes the rate limit. Stop on `ready` or `failed`. In a script, `car-image 3d get <id> --wait` and `car-image 3d create … --wait` do the waiting.

**Webhook**: pass `webhook_url` and the API POSTs once when the model settles:

- Body: `{"event": "3d_model.ready" | "3d_model.failed", "data": <the same JSON as GET>, "sent_at": "…"}`.
- Headers: `X-CarImage-Event`, `X-CarImage-Delivery` (unique per attempt; ignore a duplicate) and, when `webhook_secret` was given, `X-CarImage-Signature: sha256=<hex HMAC-SHA256 of the raw body keyed with the secret>`.
- The endpoint must answer any `2xx` within 10 seconds; a non-2xx or a timeout is retried with backoff up to five times.

Verify the signature over the **raw bytes**, with a constant-time compare, before parsing:

```ts
import { createHmac, timingSafeEqual } from "node:crypto";

const expected = "sha256=" + createHmac("sha256", process.env.CAR_IMAGE_WEBHOOK_SECRET).update(rawBody).digest("hex");
const given = request.headers.get("x-carimage-signature") ?? "";
if (given.length !== expected.length || !timingSafeEqual(Buffer.from(given), Buffer.from(expected))) {
  return new Response("bad signature", { status: 401 });
}
```

Use a webhook when the user's app has a public HTTPS endpoint; poll otherwise. Never send a `webhook_secret` anywhere but the request body.

## On a web page: publish it

When the model is for a page — a listing, a product page, a configurator, a demo — do not download and host files. **Publish** it, with `publish: true` at creation or `publish_3d_model` (`POST /api/v1/3d/{id}/publish`, `car-image 3d publish <id>`, `client.publish3dModel(id)`) at any time, and paste `public.embed.html`:

```html
<script src="https://carimage.dev/embed/3d.js" async></script>
<car-3d model="m3d_7f2k9q4hxn2b5c8d" view="front-3-4" spin backdrop="studio" ar></car-3d>
```

- The script goes on the page once; each `<car-3d>` shows one model. **No API key anywhere near the browser** — the element reads the model's public JSON and Car Image serves the files from its CDN. Free, every load.
- It shows the poster at once, loads Google's `<model-viewer>` the first time it scrolls into view, and, if the model is still being made, shows a progress note and updates itself when it is ready — so you can publish at creation and ship the page before the model exists.
- Attributes: `view` (`front-3-4` default, `front`, `side`, `rear-3-4`, `rear`, `rear-3-4-right`, `side-right`, `front-3-4-right`, `top`: the image views' eight angles plus a top view), `spin` (or a number of degrees per second), `backdrop` (`none` default, `light`, `dark`, `studio`, or any CSS background: `#0f1117`, a gradient, `url(…)`), `ar` (an AR button on phones), `static` (no controls), `no-zoom`, `alt`. Anything else (`exposure`, `camera-orbit`, `shadow-intensity`, …) is passed to `<model-viewer>`. Size it with CSS: it is `display: block`, 100% wide, 4:3 by default.
- Pages that already load `<model-viewer>` can skip the script and use `public.files` directly: `model.glb` (the browser build), `model.usdz` (for `ios-src`) and `poster.png` are stable URLs that redirect to immutable copies on the CDN, readable from any origin. `GET /api/v1/3d/public/{public_id}` (no key) returns the same JSON the element reads, `embed.model_viewer` included.
- `public.id` is unguessable, not secret: anyone holding the link can load the model. Unpublish (`unpublish: true`, `DELETE`, `--unpublish`) when it should not be: the links stop working within the hour, and a later publish gets a new id.

## Downloading the files

For an app, a game engine, Blender or a pipeline, download instead. `GET /api/v1/3d/{id}/files/{glb|glb_web|usdz|fbx|thumbnail}` needs the API key and answers `302` with a signed URL on our storage that is valid for one hour and needs no key. `curl -L` and every download tool follow it; `car-image 3d download <id> --format glb --out car.glb` and `client.download3dModel(id, "glb")` do the same. Before the model is ready it answers `409` with `Retry-After`.

| File | Content type | Typical size | Use |
| --- | --- | --- | --- |
| `glb` | `model/gltf-binary` | about 100 MB | The original, unremeshed (about three million triangles, 4k textures): three.js, Blender, Unity, Unreal, further processing |
| `glb_web` | `model/gltf-binary` | about 25 MB | The browser build (meshopt, WebP textures): any web viewer, when you host it yourself |
| `usdz` | `model/vnd.usdz+zip` | about 100 MB | iOS AR Quick Look, visionOS |
| `fbx` | `application/octet-stream` | similar to the GLB | Maya, 3ds Max, older pipelines |
| `thumbnail` | `image/png` | a few hundred KB | A transparent still for posters and lists |

Never put the API key, or the hour-long signed URL, in a page. Publishing exists so you never have to.

## When something fails

| Status | Meaning | Do |
| --- | --- | --- |
| 400 | Bad body: `vehicle` with make/model/year, an unparseable `color`, a `publish` that is not a boolean, a `webhook_url` that is not public HTTPS, a `webhook_secret` without a URL. | Fix and retry once. Nothing was charged. |
| 402 | Fewer than 100 credits. | **Stop and ask the human** to top up. Never buy credits on your own. |
| 404 | Vehicle not in the catalog, unknown vehicle id, a request id that is not the user's, or an unpublished public id. | Resolve or search the catalog; check the id. |
| 409 | A file was asked for before `ready`, a failed model was asked to publish, or an `Idempotency-Key` retry overtook the first request. | Wait `Retry-After`, then poll `get_3d_model`. |
| 503 | 3D generation is at its daily capacity (`code: model_3d_at_capacity`, `retry_after_seconds`) or switched off. Nothing charged; images are unaffected. | Tell the user when it resumes; do not loop. |

Every failure is `application/problem+json` with a `request_id`; keep it. The full table is in the `car-image` skill's [references/errors.md](../car-image/references/errors.md).

## Never do these on your own

- Create a model the user did not ask for, or a batch of them. Confirm the count and the cost (100 credits each, unless the account already owns that vehicle in that color) first.
- Retry a `402`, or poll faster than every 10 seconds.
- Put the API key, a `webhook_secret` or a signed file URL in a page, a repository or a log. Publish instead.
- Publish a model the user wanted kept private, or leave one published after they asked for it to be taken down.
- Claim the model reproduces a specific trim, options package or an individual listed vehicle: it is built from catalog-bounded studio renders, not a scan of a real car.

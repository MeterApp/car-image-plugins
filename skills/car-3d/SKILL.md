---
name: car-3d
description: Get a textured 3D model (GLB, USDZ, FBX and a thumbnail) of any real vehicle in any paint color from the Car Image API, for AR views, configurators, game assets, product pages and 3D scenes, and put it on a web page with a two-line embed that Car Image hosts. Covers the order of work (look the vehicle up, say the price, create by vehicle id, hand the human the Checkout link, create again once it is paid), what a model costs (a beta at $5 per vehicle and color, paid upfront by the human in Stripe Checkout, free once the account owns that vehicle in that color), how long it takes and how to wait in a conversation, polling versus webhooks, verifying the webhook signature, downloading the files, publishing a model and the <car-3d> element. Use when the user wants a 3D model, a GLB, a USDZ, an FBX, an AR-ready asset of a car, or a 3D car on a page; do not use for 2D renders (car-image), signed image URLs (car-image-urls) or finding which vehicle to model (vehicle-catalog).
---

# 3D models of real vehicles

`POST /api/v1/3d` turns any catalog vehicle, in any paint, into a textured 3D model: **GLB, USDZ, FBX, a thumbnail and `glb_web`**, a smaller browser build of the GLB. Models are built from the same renders the image API serves, so a model matches the pictures the user already shows, and every color of a vehicle is one mesh with a different texture. 3D models are in **beta** and cost **$5 per vehicle and color**, paid upfront by a person in Stripe Checkout before anything is built.

With MCP connected the tools are `create_3d_model`, `get_3d_model` and `publish_3d_model`; the hosted endpoint and marketplace plugin include them by default, and stdio includes them with `--toolset all` (the `car-image-mcp` skill). Over REST: `POST /api/v1/3d`, `GET /api/v1/3d/{id}`, `GET /api/v1/3d/{id}/files/{kind}`, `GET /api/v1/3d?limit=`, `POST|DELETE /api/v1/3d/{id}/publish`, and the key-free `GET /api/v1/3d/public/{public_id}`. The CLI has `car-image 3d create|get|download|list|publish`; the SDK has `create3dModel`, `get3dModel`, `list3dModels`, `download3dModel`, `publish3dModel` and `unpublish3dModel`. Full reference: [`/docs/3d`](https://carimage.dev/docs/3d?ref=plugin).

## The order of work

1. **Look the vehicle up** (free; the `vehicle-catalog` skill): `resolve_vehicle` for a name, `decode_vin` for a VIN. Keep the vehicle id. A model of the wrong car costs the human $5, so this step is never skipped, and a lookup that is not `high` confidence in the year asked for goes back to the user first.
2. **Say what it is and what it costs, and wait for a yes**: the year, make and model the lookup named, the paint, that 3D models are in beta and cost $5 per vehicle and color, paid upfront in Stripe Checkout (nothing when the account already owns it), and ten to twenty minutes for a first model. A preview image of that vehicle in that paint (one vehicle image of the plan's month, no credits; the `car-image` skill shows one in the reply) is a cheap way to agree on both before anyone pays.
3. **Create it by id**: `create_3d_model({ vehicle: "veh_…", color, publish: true })`. When the account already owns that vehicle in that color, this returns the request: keep its `id` and go to step 5.
4. **On the `402` (`code: "model_3d_payment_required"`), stop.** Nothing was started and nothing was charged. Give the human `checkout_url` with the price ($5, beta). They sign in and pay in the browser, and the payment starts the build. Never pay it yourself, never look for credits to cover it, and do not call again until they say they have paid. Then call `create_3d_model` again with the same vehicle and color: it returns the model for nothing (`billing.already_owned: true`). Keep the request `id`.
5. **Wait without hammering** (`get_3d_model`), then hand over the files or the embed.

## What it costs — say this first

- **Beta: $5 per vehicle and color**, a one-time payment the human makes upfront in Stripe Checkout, before anything is built. Credits do not buy a 3D model and no plan includes one; nothing else buys one either. The price is the same whether the model already exists, is in progress or is new.
- **Free once owned.** An account that has paid for a vehicle in a color owns it: ordering it again creates a new request for nothing (`billing.amount_cents: 0`, `billing.already_owned: true`), whatever spelling, whether the model is ready or still being made, and even after Car Image rebuilds models with a better recipe. So a re-order is never a second bill; only a failed model (refunded, not owned) needs a new payment. Models ordered with credits before 2026-11-25 stay owned.
- Polling, listing, downloads, webhook deliveries, **publishing and every load of a published model are free**.
- A model that **cannot be built is refunded to the card automatically**, in full. A `503` charges nothing, and Checkout does not open.
- **Tell the user the price and confirm before calling `create_3d_model`** for a vehicle and color the account does not own yet. The `402` it answers is the payment step: hand the human `checkout_url` and stop. Never retry a `402`, and never pay one or change anything in billing on your own.

## How long it takes

| Case | Wall time | Why |
| --- | --- | --- |
| First model of a vehicle | **10–20 minutes** | The four source views are rendered and waited for (`stage: views`), the mesh is built and finished (`geometry`) and the color composed (`texture`). |
| Another color of the same vehicle | **1–2 minutes** | The finished mesh already exists; only the paint changes. |
| The model already exists (someone asked for this vehicle in this color) | immediate once paid | `200` with `status: "ready"` and the files. The price is the same: an account that has not paid gets the `402` first. |

Say this before the user waits. Do not present a model as instant.

## The request

```json
{ "make": "Toyota", "model": "Camry", "year": 2025, "color": "red", "publish": true }
```

- Name the vehicle with `make`, `model` and `year`, **or** with `vehicle`, a stable catalog id such as `veh_errc87t1jgata` (from `search_vehicles`, `resolve_vehicle` or `decode_vin`). Both together is a `400`; an unknown id is a `404`.
- `color` is one of the 15 presets or any hex (`"#1a2b3c"` or `"1a2b3c"`); the response echoes `#1a2b3c`. Default `silver`.
- `publish: true` publishes the model at once (below). Free. Pass it whenever the model is for a web page.
- `webhook_url` (public HTTPS) and `webhook_secret` are optional; see below.
- Send the same body before and after the payment. A request for a model that is not paid yet creates nothing, so `publish` and `webhook_url` take effect on the call that returns the request.
- Send an `Idempotency-Key` header over REST so a retried request replays the first answer (the SDK and CLI do this for you). A `402` is never stored under a key, so the same key works again once the model is paid.

Prefer `vehicle`: the id comes from the lookup, so the model is of the car the user confirmed. A name typed from memory can answer `404`, or resolve to a neighbouring model, and a model of the wrong car costs the human $5.

## The response and its lifecycle

For a vehicle and color the account has not paid for, `402` (`application/problem+json`). Nothing is started and nothing is charged:

```json
{
  "title": "Payment required",
  "status": 402,
  "detail": "3D models are in beta and are paid upfront: one model of a vehicle in a color is $5.00, and credits or a plan's allowance do not buy one. Nothing was charged and nothing was started. …",
  "request_id": "…",
  "code": "model_3d_payment_required",
  "retryable": false,
  "beta": true,
  "price_cents": 500,
  "currency": "usd",
  "checkout_url": "…/dashboard/checkout?model_3d=veh_errc87t1jgata&color=red&ref=agent-api"
}
```

`checkout_url` is for a person: they open it, sign in and pay $5, and **the payment starts the build**. It is a full link on carimage.dev, shortened here: pass it on exactly as it came (the tool's link ends `ref=agent-mcp`). The paid order shows in `GET /api/v1/3d` and on the dashboard.

After the payment the same request answers `202 Accepted` while the model is queued or processing, `200` when it is ready:

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
  "billing": { "charged_on": "checkout", "amount_cents": 0, "currency": "usd", "already_owned": true, "credits_charged": 0, "credits_remaining": 100 },
  "request_id": "…"
}
```

`status` goes `queued` → `processing` → `ready` or `failed`. `progress` is 0–100; `estimated_seconds_remaining` is a rough guide, not a promise. When `ready`, `files` holds `glb`, `glb_web`, `usdz`, `fbx`, `thumbnail` and `paint_mask`, each `{url, bytes, content_type}`. When `failed`, `error` carries `{code, message, image_url}` and says what happened to the payment: `refunded` (`false` only while the refund is pending), `amount_refunded_cents` (500), `refunded_at`, `retryable: true` and `retry`, one sentence on ordering again (`credits_refunded` is set only on orders made with credits before the beta). A refunded model is not owned, so creating it again answers a new `402` with a new Checkout link (confirm with the human first), and that build is refunded too if it fails. `billing.credits_charged` is always 0 and `credits_remaining` is the account's balance, which a 3D order never touches. `public` is `null` until the request is published.

`id` is the user's request; the shared model behind it is never exposed. Every request is its own record with its own webhook and its own publish state.

## Waiting: poll or webhook

**Poll** `get_3d_model` / `GET /api/v1/3d/{id}` every **10–15 seconds**. The server re-reads the generator only when its last look is older than 15 seconds, so a tighter loop sees the same answer and wastes the rate limit. Stop on `ready` or `failed`. In a script, `car-image 3d get <id> --wait` and `car-image 3d create … --wait` do the waiting.

**Webhook**: pass `webhook_url` on the call that returns the request (after the payment) and the API POSTs once when the model settles:

- Body: `{"event": "3d_model.ready" | "3d_model.failed", "data": <the same JSON as GET>, "sent_at": "…"}`.
- Headers: `X-CarImage-Event`, `X-CarImage-Delivery` (unique per attempt; ignore a duplicate) and, when `webhook_secret` was given, `X-CarImage-Signature: sha256=<hex HMAC-SHA256 of the raw body keyed with the secret>`.
- The endpoint must answer any `2xx` within 10 seconds; a non-2xx or a timeout is retried with backoff up to five times.

Verify the signature over the **raw bytes**, with a constant-time compare, before parsing:

```ts
import { createHmac, timingSafeEqual } from "node:crypto";

/** `secret` is the webhook_secret the model was requested with, from the app's own secret settings. */
export function signatureIsValid(rawBody: Buffer, given: string, secret: string): boolean {
  const expected = "sha256=" + createHmac("sha256", secret).update(rawBody).digest("hex");
  return given.length === expected.length && timingSafeEqual(Buffer.from(given), Buffer.from(expected));
}

// In the handler, before parsing the body:
if (!signatureIsValid(rawBody, request.headers.get("x-carimage-signature") ?? "", secret)) {
  return new Response("bad signature", { status: 401 });
}
```

Use a webhook when the user's app has a public HTTPS endpoint; poll otherwise. Never send a `webhook_secret` anywhere but the request body. An app that already has an account webhook endpoint also receives `3d_model.ready` and `3d_model.failed` there, signed differently (`t=…,sha256=…`; [account webhooks](https://carimage.dev/docs/webhooks?ref=plugin)), so it needs no `webhook_url` per request.

## In a conversation

A chat has no page to embed into and no terminal to download with, so plan for what the user can open.

- **Publish at creation** (`publish: true`). The `files` URLs need the account's credential on the first hop; the `public.files` URLs do not, so they are the links a person can click: `glb` to download or drop into any 3D viewer, `usdz` to open in AR on an iPhone or iPad, `poster` for a still. Say that anyone with a public link can load the model, and offer to unpublish when they are done.
- **Do not hold the conversation for the wait.** After creating, say how long it should take (`estimated_seconds_remaining`), check `get_3d_model` once or twice at most while you have something else to do, and otherwise tell the user to ask for the model again later: the request id is all you need, and the wait costs nothing.
- **When it is ready**, give the links with their sizes (`bytes`), say which to use for what, and show the still.
- **When the answer is the `402`**, show `checkout_url` as a link with the price ($5, beta) and say the model starts building as soon as it is paid. Then wait for the human to say they paid.
- **When it fails**, the $5 went back to the card automatically. Say so, and offer another attempt (a new Checkout link) rather than starting one.

## On a web page: publish it

When the model is for a page — a listing, a product page, a configurator, a demo — do not download and host files. **Publish** it, with `publish: true` at creation or `publish_3d_model` (`POST /api/v1/3d/{id}/publish`, `car-image 3d publish <id>`, `client.publish3dModel(id)`) at any time, and paste `public.embed.html`:

```html
<script src="https://carimage.dev/embed/3d.js" async></script>
<car-3d model="m3d_7f2k9q4hxn2b5c8d" view="front-3-4" spin backdrop="studio" ar></car-3d>
```

- The script goes on the page once; each `<car-3d>` shows one model. **No API key anywhere near the browser** — the element reads the model's public JSON and Car Image serves the files from its CDN. Free, every load.
- It shows the poster at once, loads Google's `<model-viewer>` the first time it scrolls into view, and, if the model is still being made, shows a progress note and updates itself when it is ready — so you can publish at creation and ship the page before the model exists.
- Attributes: `view` (`front-3-4` default, `front`, `side`, `rear-3-4`, `rear`, `rear-3-4-right`, `side-right`, `front-3-4-right`, `top`: the image views' nine angles), `spin` (or a number of degrees per second), `backdrop` (`none` default, `light`, `dark`, `studio`, or any CSS background: `#0f1117`, a gradient, `url(…)`), `ar` (an AR button on phones), `static` (no controls), `no-zoom`, `alt`. Anything else (`exposure`, `camera-orbit`, `shadow-intensity`, …) is passed to `<model-viewer>`. Size it with CSS: it is `display: block`, 100% wide, 4:3 by default.
- Pages that already load `<model-viewer>` can skip the script and use `public.files` directly: `model.glb` (the browser build), `model.usdz` (for `ios-src`) and `poster.png` are stable URLs that redirect to immutable copies on the CDN, readable from any origin. `GET /api/v1/3d/public/{public_id}` (no key) returns the same JSON the element reads, `embed.model_viewer` included.
- `public.id` is unguessable, not secret: anyone holding the link can load the model. Unpublish (`unpublish: true`, `DELETE`, `--unpublish`) when it should not be: the links stop working within the hour, and a later publish gets a new id.

## Downloading the files

For an app, a game engine, Blender or a pipeline, download instead. `GET /api/v1/3d/{id}/files/{glb|glb_web|usdz|fbx|thumbnail|paint_mask}` needs the API key and answers `302` with a signed URL on our storage that is valid for one hour and needs no key. `curl -L` and every download tool follow it; `car-image 3d download <id> --format glb --out car.glb` and `client.download3dModel(id, "glb")` do the same. Before the model is ready it answers `409` with `Retry-After`.

| File | Content type | Typical size | Use |
| --- | --- | --- | --- |
| `glb` | `model/gltf-binary` | about 100 MB | The original, unremeshed (about three million triangles, 4k textures): three.js, Blender, Unity, Unreal, further processing |
| `glb_web` | `model/gltf-binary` | about 30 MB | The browser build (meshopt, WebP textures): any web viewer, when you host it yourself |
| `usdz` | `model/vnd.usdz+zip` | about 25 MB | iOS AR Quick Look, visionOS; converted from a decimated build (about 300,000 triangles, the same 4k textures) |
| `fbx` | `application/octet-stream` | similar to the GLB | Maya, 3ds Max, older pipelines |
| `thumbnail` | `image/png` | a few hundred KB | A transparent still for posters and lists |
| `paint_mask` | `image/png` | tens of KB | Grayscale, the size of the GLB's base-colour texture and aligned through the same UVs: white where the texel is paint. For recolouring the paint live in the user's own viewer: a paint texel is the ordered color times its shading in linear light, so multiply by new ÷ ordered where the mask is white (a light color, or `#ffffff`, divides cleanly). The same for every color of a vehicle. |

Never put the API key, or the hour-long signed URL, in a page. Publishing exists so you never have to.

## When something fails

| Status | Meaning | Do |
| --- | --- | --- |
| 400 | Bad body: `vehicle` with make/model/year, an unparseable `color`, a `publish` that is not a boolean, a `webhook_url` that is not public HTTPS, a `webhook_secret` without a URL. | Fix and retry once. Nothing was charged. |
| 402 | The account has not paid for this vehicle in this color (`code: "model_3d_payment_required"`, `beta: true`, `price_cents: 500`, `currency: "usd"`, `checkout_url`). Nothing was started and nothing was charged. | **Stop and give the human `checkout_url` with the price ($5, beta).** They pay in the browser, which starts the build; when they say they have paid, call again with the same vehicle and color. Never pay, look for credits or retry on your own. |
| 404 | Vehicle not in the catalog under that name, unknown vehicle id, a request id that is not the user's, or an unpublished public id. Nothing was charged. | Look the vehicle up (`resolve_vehicle`; the problem's `suggestions` carry ids) and create by `vehicle`; check the id. |
| 409 | A file was asked for before `ready`, a failed model was asked to publish, or an `Idempotency-Key` retry overtook the first request. | Wait `Retry-After`, then poll `get_3d_model`. |
| 503 | 3D generation is at its daily capacity (`code: model_3d_at_capacity`, `retry_after_seconds`) or cannot build right now (`model_3d_unavailable`). Nothing was charged and Checkout does not open; images are unaffected. | Tell the user when it resumes; do not loop. |

Every failure is `application/problem+json` with a `request_id`; keep it. The full table is in the `car-image` skill's [references/errors.md](../car-image/references/errors.md).

## Never do these on your own

- Create a model of a vehicle you have not looked up, or one the user has not confirmed by name.
- Create a model the user did not ask for, or a batch of them. Confirm the count and the cost ($5 each, paid by the human in Checkout, unless the account already owns that vehicle in that color) first.
- Pay for a model, look for credits or a plan to cover one, or treat the `402` as anything but a link to hand the human.
- Retry a `402` before the human says they paid, or poll faster than every 10 seconds.
- Put the API key, a `webhook_secret` or a signed file URL in a page, a repository or a log. Publish instead.
- Publish a model the user wanted kept private, or leave one published after they asked for it to be taken down.
- Claim the model reproduces a specific trim, options package or an individual listed vehicle: it is built from catalog-bounded studio renders, not a scan of a real car.

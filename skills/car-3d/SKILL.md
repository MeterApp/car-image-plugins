---
name: car-3d
description: Get a textured 3D model (GLB, USDZ, FBX and a thumbnail) of any real vehicle in any paint color from the Car Image API, for AR views, configurators, game assets, product pages and 3D scenes. Covers what a model costs (1,000 credits, charged at creation), how long it takes, polling versus webhooks, verifying the webhook signature, downloading the files and embedding them with <model-viewer>. Use when the user wants a 3D model, a GLB, a USDZ, an FBX or an AR-ready asset of a car; do not use for 2D renders (car-image), signed image URLs (car-image-urls) or finding which vehicle to model (vehicle-catalog).
---

# 3D models of real vehicles

`POST /api/v1/3d` turns any catalog vehicle, in any paint, into a textured 3D model: **GLB, USDZ, FBX and a thumbnail**. Models are built from the same renders the image API serves, so a model matches the pictures the user already shows, and every color of a vehicle is one mesh with a different texture.

With MCP connected the tools are `create_3d_model` and `get_3d_model`. Over REST: `POST /api/v1/3d`, `GET /api/v1/3d/{id}`, `GET /api/v1/3d/{id}/files/{kind}`, `GET /api/v1/3d?limit=`. The CLI has `car-image 3d create|get|download|list`; the SDK has `create3dModel`, `get3dModel`, `list3dModels` and `download3dModel`. Full reference: [`/docs/3d`](https://carimage.dev/docs/3d?ref=plugin).

## What it costs — say this first

- **1,000 credits ($1.00) per request**, charged at creation whether the model is cached, in progress or new. Cache state never changes the price, exactly as with images.
- Polling, listing, downloads and webhook deliveries are **free**.
- A model that **fails is refunded** in full. A `503` at capacity charges nothing.
- A request is a thousand times an image: **tell the user the price and confirm before calling `create_3d_model`**, and call `get_account` first when the balance may be short. Never retry a `402`.

## How long it takes

| Case | Wall time | Why |
| --- | --- | --- |
| First model of a vehicle | **3–5 minutes** | The four source views are rendered, the mesh is built (`stage: geometry`) and textured (`texture`). |
| Another color of the same vehicle | **1–2 minutes** | The mesh already exists; only the texture is repainted. |
| Someone already asked for this vehicle in this color | immediate | `200` with `status: "ready"` and the files, still charged. |

Say this before the user waits. Do not present a model as instant.

## The request

```json
{ "make": "Toyota", "model": "Camry", "year": 2025, "color": "red" }
```

- Name the vehicle with `make`, `model` and `year`, **or** with `vehicle`, a stable catalog id such as `veh_errc87t1jgata` (from `search_vehicles`, `resolve_vehicle` or `decode_vin`). Both together is a `400`; an unknown id is a `404`.
- `color` is one of the 15 presets or any hex (`"#1a2b3c"` or `"1a2b3c"`); the response echoes `#1a2b3c`. Default `silver`.
- `webhook_url` (public HTTPS) and `webhook_secret` are optional; see below.
- Send an `Idempotency-Key` header over REST so a retried request replays the first answer instead of charging again (the SDK and CLI do this for you).

Resolve free text first (`vehicle-catalog` skill): a model of the wrong car costs 1,000 credits.

## The response and its lifecycle

`202 Accepted` while the model is queued or processing, `200` when it was already ready:

```json
{
  "data": {
    "id": "0c5e0b2a-…", "object": "3d_model",
    "status": "processing", "progress": 35, "stage": "geometry",
    "vehicle": { "id": "veh_errc87t1jgata", "make": "toyota", "model": "camry", "year": 2025 },
    "color": "red", "generator": "meshy-7",
    "files": null, "polycount": null, "error": null,
    "estimated_seconds_remaining": 170, "webhook": null,
    "created_at": "…", "updated_at": "…", "ready_at": null
  },
  "billing": { "charged_on": "creation", "credits_charged": 1000, "credits_remaining": 3870 },
  "request_id": "…"
}
```

`status` goes `queued` → `processing` → `ready` or `failed`. `progress` is 0–100; `estimated_seconds_remaining` is a rough guide, not a promise. When `ready`, `files` holds `glb`, `usdz`, `fbx` and `thumbnail`, each `{url, bytes, content_type}`. When `failed`, `error` carries `{code, message}` and the credits were refunded; asking again makes a fresh attempt.

`id` is the user's request; the shared model behind it is never exposed.

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

## Downloading and embedding

`GET /api/v1/3d/{id}/files/{glb|usdz|fbx|thumbnail}` needs the API key and answers `302` with a signed URL on our storage that is valid for one hour and needs no key. `curl -L` and every download tool follow it; `car-image 3d download <id> --format glb --out car.glb` and `client.download3dModel(id, "glb")` do the same. Before the model is ready it answers `409` with `Retry-After`.

| File | Content type | Typical size | Use |
| --- | --- | --- | --- |
| `glb` | `model/gltf-binary` | about 6 MB | Web viewers, three.js, Blender, Unity, Unreal |
| `usdz` | `model/vnd.usdz+zip` | about 7 MB | iOS AR Quick Look, visionOS |
| `fbx` | `application/octet-stream` | similar to the GLB | Maya, 3ds Max, older pipelines |
| `thumbnail` | `image/png` | a few hundred KB | A transparent still for posters and lists |

**Host the files yourself.** Download them server-side with the key, store them with the user's other assets, and embed with Google's `<model-viewer>` (the thumbnail makes a good `poster`):

```html
<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script>
<model-viewer src="/models/camry-2025-red.glb" ios-src="/models/camry-2025-red.usdz" poster="/models/camry-2025-red.png"
  alt="2025 Toyota Camry, red" camera-controls auto-rotate ar shadow-intensity="1" style="width:100%;aspect-ratio:1"></model-viewer>
```

Never put the API key, or the hour-long signed URL, in a page. A server may hand the signed `Location` to a browser for the hour, which is the right move for a one-off preview.

## When something fails

| Status | Meaning | Do |
| --- | --- | --- |
| 400 | Bad body: `vehicle` with make/model/year, an unparseable `color`, a `webhook_url` that is not public HTTPS, a `webhook_secret` without a URL. | Fix and retry once. Nothing was charged. |
| 402 | Fewer than 1,000 credits. | **Stop and ask the human** to top up. Never buy credits on your own. |
| 404 | Vehicle not in the catalog, unknown vehicle id, or a request id that is not the user's. | Resolve or search the catalog; check the id. |
| 409 | A file was asked for before `ready`, or an `Idempotency-Key` retry overtook the first request. | Wait `Retry-After`, then poll `get_3d_model`. |
| 503 | 3D generation is at its daily capacity (`code: model_3d_at_capacity`, `retry_after_seconds`) or switched off. Nothing charged; images are unaffected. | Tell the user when it resumes; do not loop. |

Every failure is `application/problem+json` with a `request_id`; keep it. The full table is in the `car-image` skill's [references/errors.md](../car-image/references/errors.md).

## Never do these on your own

- Create a model the user did not ask for, or a batch of them. Confirm the count and the cost (1,000 credits each) first.
- Retry a `402`, or poll faster than every 10 seconds.
- Put the API key, a `webhook_secret` or a signed file URL in a page, a repository or a log.
- Claim the model reproduces a specific trim, options package or an individual listed vehicle: it is built from catalog-bounded studio renders, not a scan of a real car.

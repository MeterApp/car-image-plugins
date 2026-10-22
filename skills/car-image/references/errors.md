# Handling Car Image API errors

Every JSON failure is an [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) problem document (`application/problem+json`) carrying `type`, `title`, `status`, `detail` and `request_id`. The `type` URL points at the matching section of the canonical reference at <https://carimage.dev/errors.md>, which is always current — read it when a status below does not explain what you are seeing.

**Log the `request_id`. Never log an API key or a delivery token.**

## The billing rule

Only a `200` that delivers an image or mints signed URLs costs credits. Every error costs nothing, and a render that fails after being charged is refunded automatically. You never need to "undo" a charge after an error.

## Not errors

| Status | What it means |
| --- | --- |
| 304 | You sent `If-None-Match` and the image is unchanged. Free. Keep the bytes you have. |
| 308 | A non-canonical spelling (`brand=Ford`, `format=jpeg`, `angle=rear`) redirecting to the canonical URL so caches hold one copy. Follow it. A URL with a tracking tag or cache buster ignored, or a size above 1024 clamped, is answered with the image instead, with `X-Ignored-Parameters` or `X-Clamped-Parameters` and a `Content-Location` naming the canonical URL. |

## Fix the request

| Status | Cause | Action |
| --- | --- | --- |
| 400 | A query parameter the endpoint does not read (`parameter` names it, `allowed` lists the names it reads), a repeated query parameter, or one sent under two spellings (`w` and `width`, `make` and `brand`, `view` and `angle`), `vehicle` (an id) together with make, model or year, a `color` that is neither one of the 15 presets, a CSS color name nor a hex, an unknown `fit` or `format`, an unparseable `background`, `background=transparent` with `jpg`, `padding` without `trim` or above 50, a malformed `Idempotency-Key`, malformed JSON, an empty `query`, a VIN that is not 5–17 characters of A–Z (no I, O, Q), 0–9 and `*`, a `webhook_url` that is not public HTTPS. | Fix it and retry once. Retrying unchanged always fails. For an unknown query parameter, send one of `allowed` instead (`angle`, `paint` and `bg` already work for `view`, `color` and `background`); only tracking tags and cache busters (`utm_source`, `gclid`, `v`, `t`…) are ignored, and named in `X-Ignored-Parameters`. A size above 1024 is clamped, not refused (`X-Clamped-Parameters`). Batch problems carry `index` for the offending item; `list_image_options` lists every valid value, including the fit modes, background vocabulary, padding ceiling and the vehicle-id format. |
| 404 | The make/model/year is not in the catalog, no vehicle has that id, a VIN pattern is unknown to NHTSA (`VIN not recognized`), no 3D request of the user's has that id, `mode=cached` asked for a variant never rendered, or a preview URL names a render no /cars page shows (`not_a_preview`). | A vehicle `404` (`code: "vehicle_not_found"`) means the render was asked for by a name the catalog does not file the car under. Read its `suggestions` (real catalog vehicles with ids, closest first) and retry with `vehicle: <id>` when one is plainly the car; otherwise look the vehicle up (`resolve_vehicle`, or `decode_vin` for a VIN; the `vehicle-catalog` skill) and render by the id it returns. A `VIN not recognized` goes back to the user instead: have them re-check it, above all the first three characters (the maker code), or decode what they are sure of as a partial VIN with `*` and a `year`; NHTSA's data covers vehicles made for the US market, so find any other car by name. Do not retry unchanged, and do not silently substitute a different vehicle. |
| 413 | Body too large: 64 KiB for `POST /api/v1/image-urls`, 4 KiB for resolve. | Split into batches of at most 50 images. |
| 422 | The `Idempotency-Key` on `POST /api/v1/image-urls` was already used, within the last 24 hours, for a different body. | Send a new key for a new request, or the identical body to replay the earlier response. Nothing was charged. |

## Stop and involve the human

| Status | Cause | Action |
| --- | --- | --- |
| 401 | No usable credential — missing, malformed or revoked key (`WWW-Authenticate: Bearer error="invalid_token"`). | For the plugin, reconnect through the host’s MCP sign-in controls (`/mcp` in Claude Code), or replace the key saved in the plugin's options. For an explicit API-key connection, the user updates the key where that host or application keeps it (`npx @meterapp/car-image login` issues a new one). Never guess a key, and never move a key into a URL. |
| 402 | `Insufficient credits`: out of credits. The problem carries `balance` and `required_credits` (1 for an image, 100 for a 3D model), and `renewal_window` when a renewing signed URL meets an empty balance. Or `Plan limit reached` with `code: "plan_vehicle_limit"`: the request named more new distinct vehicles than the plan allows this month (`scope`, `plan`, `vehicles_this_month`, `vehicles_per_month`, `requested`; on a written agreement capped over its term, `scope: "term"` with `vehicles_this_term` and `vehicles_per_term`). Nothing was charged either way. | **Stop.** Report the balance and what the job needs, or the plan and its cap, then let the human decide. Hand over `checkout_url` (Stripe Checkout for the pack or plan that fixes it, after sign-in) with the price from `pricing`. Buy credits or change a plan only when the human asks or a spending mandate they set covers it. |
| 403 | The key lacks the required scope (`required_scope`: `images:read`, `account:read`, `billing:write`), or a delivery URL is expired/invalid, or the key that created it was revoked. | Create a correctly scoped key or a fresh URL. Scope changes are the user's call. |
| 410 | A use-capped delivery URL (`max_uses > 0`) has been loaded its maximum number of times. | Create a new URL. Unlimited URLs (`max_uses: 0`) never return 410. |

## Wait, then retry

| Status | Cause | Action |
| --- | --- | --- |
| 409 | A `POST /api/v1/image-urls` or `POST /api/v1/3d` with the same `Idempotency-Key` is still being processed; or `3D model not ready`: a file of a 3D model was asked for before its `status` reached `ready`. | Wait the seconds in `Retry-After`, then repeat the identical request (you receive the first request's response, marked `Idempotent-Replayed: true`, and pay nothing more), or poll `get_3d_model` until it is ready. |
| 429 | Rate limited — 120 requests per minute per key by default. `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset` are on every authenticated response. | Wait the integer seconds in `Retry-After`, then retry with exponential backoff and jitter. Never hammer. |
| 500 | Unexpected server failure. Nothing was charged. | Retry once with backoff. Include the `request_id` when reporting. |
| 502 | The render failed (the credit was refunded), or `VIN decoder unavailable` (nothing charged). | Retry once after a pause, or try a different view. For a VIN, retry later. |
| 503 | A dependency is temporarily unavailable; new image renders are at the day's capacity (`"code": "generation_at_capacity"`, see below); or, on `POST /api/v1/3d`, `3D generation at capacity` (`"code": "model_3d_at_capacity"`, `retry_after_seconds`) or `3D models unavailable` — nothing charged, images unaffected. | Honor `Retry-After`. For a delivery URL, a 503 means the URL was not consumed; just retry it. For 3D, tell the user when it resumes; do not loop. |

### A 503 at render capacity

- **`"code": "generation_at_capacity"`** (a `503` with `Retry-After`) — new renders have hit the service's daily ceiling. The problem also carries `retry_after_seconds` and `reset_at`. Already-rendered images keep serving normally, so cached variants still work. **Retrying before `reset_at` cannot succeed** — do not loop. Tell the user when capacity resets, and offer vehicles that are already cached if they need something now.

## Reporting a problem

Give the user, or `support@carimage.dev`, the `request_id` and the status. That is enough to trace a single request end to end. Do not paste the key, the full request URL of a signed delivery URL, or response headers that contain either.

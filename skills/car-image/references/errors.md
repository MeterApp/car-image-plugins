# Handling Car Image API errors

Every JSON failure is an [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) problem document (`application/problem+json`) carrying `type`, `title`, `status`, `detail` and `request_id`. The `type` URL points at the matching section of the canonical reference at <https://carimage.dev/errors.md>, which is always current — read it when a status below does not explain what you are seeing.

**Log the `request_id`. Never log an API key or a delivery token.**

## The billing rule

Only a `200` that delivers an image or mints signed URLs costs credits. Every error costs nothing, and a render that fails after being charged is refunded automatically. You never need to "undo" a charge after an error.

## Not errors

| Status | What it means |
| --- | --- |
| 304 | You sent `If-None-Match` and the image is unchanged. Free. Keep the bytes you have. |
| 308 | A non-canonical spelling (`brand=Ford`, `format=jpeg`) redirecting to the canonical URL so caches hold one copy. Follow it. |

## Fix the request

| Status | Cause | Action |
| --- | --- | --- |
| 400 | Unknown or repeated query parameter, `make` and `brand` together, a color outside the 15 presets, a dimension above 1024, an unknown `fit` or `format`, an unparseable `background`, `background=transparent` with `jpg`, `padding` without `trim` or above 50, a malformed `Idempotency-Key`, malformed JSON, an empty `query`. | Fix it and retry once. Retrying unchanged always fails. Batch problems carry `index` for the offending item; `list_image_options` lists every valid value, including the fit modes, background vocabulary and padding ceiling. |
| 404 | The make/model/year is not in the catalog, `mode=cached` asked for a variant never rendered, or feedback referenced a request that delivered no image. | Search the catalog for the canonical slugs (`vehicle-catalog` skill). Do not retry unchanged, and do not silently substitute a different vehicle. |
| 413 | Body too large: 64 KiB for `POST /api/v1/image-urls`, 8 KiB for feedback, 4 KiB for resolve. | Split into batches of at most 50 images. |
| 422 | The `Idempotency-Key` on `POST /api/v1/image-urls` was already used, within the last 24 hours, for a different body. | Send a new key for a new request, or the identical body to replay the earlier response. Nothing was charged. |

## Stop and involve the human

| Status | Cause | Action |
| --- | --- | --- |
| 401 | No usable credential — missing, malformed or revoked key (`WWW-Authenticate: Bearer error="invalid_token"`). | Ask the user to run `npx @meterapp/car-image login` or set `CAR_IMAGE_API_KEY`. Never guess a key, and never move a key into a URL. |
| 402 | Out of credits. The problem carries `balance` and `required_credits`. | **Stop.** Report the balance and what the job needs, then let the human decide. A hosted Stripe page exists, but only a human completes a purchase. Never buy credits autonomously. |
| 403 | The key lacks the required scope (`required_scope`: `images:read`, `account:read`, `billing:write`), or a delivery URL is expired/invalid, or the key that created it was revoked. | Create a correctly scoped key or a fresh URL. Scope changes are the user's call. |
| 410 | A use-capped delivery URL (`max_uses > 0`) has been loaded its maximum number of times. | Create a new URL. Unlimited URLs (`max_uses: 0`) never return 410. |

## Wait, then retry

| Status | Cause | Action |
| --- | --- | --- |
| 409 | A `POST /api/v1/image-urls` with the same `Idempotency-Key` is still being processed. | Wait the seconds in `Retry-After`, then repeat the identical request: you receive the first request's response, marked `Idempotent-Replayed: true`, and pay nothing more. |
| 429 | Rate limited — 120 requests per minute per key by default. `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset` are on every authenticated response. | Wait the integer seconds in `Retry-After`, then retry with exponential backoff and jitter. Never hammer. |
| 500 | Unexpected server failure. Nothing was charged. | Retry once with backoff. Include the `request_id` when reporting. |
| 502 | The render failed. The credit was refunded. | Check the `code` extension member first — see below. |
| 503 | A dependency is temporarily unavailable. | Honor `Retry-After`. For a delivery URL, a 503 means the URL was not consumed; just retry it. |

### The two kinds of 502

Tell them apart by the `code` member on the problem document:

- **No `code`** — the render itself failed. An immediate retry is reasonable, or try a different view.
- **`"code": "generation_at_capacity"`** — new renders have hit a daily ceiling. The problem also carries `retry_after_seconds` and `reset_at`. Already-rendered images keep serving normally, so cached variants still work. **Retrying before `reset_at` cannot succeed** — do not loop. Tell the user when capacity resets, and offer vehicles that are already cached if they need something now.

## Reporting a problem

Give the user, or `hello@meterapp.co`, the `request_id` and the status. That is enough to trace a single request end to end. Do not paste the key, the full request URL of a signed delivery URL, or response headers that contain either.

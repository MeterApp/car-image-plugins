---
name: car-image
description: Fetch studio-quality, transparent-background images of real vehicles (any make, model and year from 1990-2027) for product pages, listings, dealer tools, comparison sites, emails, decks and datasets. Covers the Car Image API by Meter — authentication, the per-image credit cost, which call to make, and how to handle 402 and 429. Use for any request involving a picture of a car, truck, motorcycle or other vehicle; do not use for embedding URLs in a browser or document (car-image-urls), catalog lookups (vehicle-catalog), SDK and CLI code (car-image-sdk), or connection setup (car-image-mcp).
---

# Car Image API

Studio-quality, transparent-background renders of any vehicle in the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) catalog — 1,599 makes, 44,254 models, model years 1990-2027.

- **Views:** `front`, `front-3-4`, `side`, `side-right`, `rear`, `rear-3-4`
- **Colors:** `white black gray silver blue red green brown beige tan orange yellow gold burgundy purple`
- **Formats:** `png` (transparent), `webp`, `jpg`, or `auto` (WebP or PNG negotiated from `Accept`), up to 1024 px
- **Sizing:** `size=thumb|small|medium|large` (256/512/768/1024), or `width`/`height` 1–1024 — both together return exactly that box, placed by `fit=contain|cover|inside`; `trim` crops to the car first; `background` flattens onto a solid color. See [Getting the size right](#getting-the-size-right).

Base URL `https://carimage.dev`. Docs: [`/docs`](https://carimage.dev/docs?ref=plugin), [`/agents.md`](https://carimage.dev/agents.md), [`/openapi.json`](https://carimage.dev/openapi.json).

## What an image costs — say this before a big batch

- Every delivered image costs **exactly 1 credit**, whether it was generated or served from cache.
- A signed delivery URL costs **1 credit when created**. Loading it is free until it expires.
- **$1 = 1,000 credits.** Every account starts with **100 free credits**. There is no subscription.
- Catalog search, resolve, options, account, feedback and the request board (vehicle and feature requests) are **free**.

Twenty images cost 20 credits (2¢). Tell the user the number before rendering a batch they did not explicitly size, and call `get_account` first when the batch is large.

## Pick the right call

| You need | Use |
| --- | --- |
| Image bytes in a script, backend or notebook | `get_car_image` — returns the image inline plus `credits_charged`, `credits_remaining`, `source` (`cache`/`generated`), `request_id` |
| A URL a browser, email or document can load | `create_car_image_urls` → see the `car-image-urls` skill |
| Free text like "red 2024 porsche 911 side view" | `resolve_vehicle` first → see the `vehicle-catalog` skill |
| To confirm a vehicle exists, or list a make's models | `search_vehicles` (free) |
| Valid views, colors, sizes, formats, pricing | `list_image_options` (free) |
| Credits remaining before a batch | `get_account` (free) |
| To report a bad render | `rate_image` (free) |
| A vehicle the catalog does not have | `request_vehicle` (free) — files it for the team, or upvotes the existing request; the user is emailed when it is live |
| A feature idea for the API, CLI, SDK or tools | `request_feature` (free) |
| To see what others have asked for, or upvote it | `list_requests`, `get_request`, `upvote_request`, `comment_on_request` (free; listing needs no key) |
| To tell the team who you are, privately | `share_building` (what the user is building), `share_referral` (how they found the API) — only the Car Image team reads these |

The rows from `request_vehicle` down exist only when the server was connected with `?toolset=all` (the plugin does this) or `car-image mcp --toolset all`; a bare `https://carimage.dev/api/mcp` exposes the eight core tools above them. The `car-image-mcp` skill explains both.

Without MCP tools connected, the same operations are REST endpoints — `GET /api/v1/images/car`, `POST /api/v1/image-urls`, `POST /api/v1/images/resolve`, `GET /api/v1/vehicles`, `GET /api/v1/images/options`, `GET /api/v1/account`, `POST /api/v1/feedback`, `GET|POST /api/v1/requests`, `GET /api/v1/requests/{id}`, `POST /api/v1/requests/{id}/votes`, `GET|POST /api/v1/requests/{id}/comments`, `POST /api/v1/account/building`, `POST /api/v1/account/referral`. The `car-image-sdk` skill covers calling them from code; the CLI equivalents are `car-image request …` and `car-image about …`.

## Getting the size right

`get_car_image` and each `create_car_image_urls` entry take the same sizing inputs as the REST endpoints. The source render is square; nothing is upscaled past 1024 px.

| Input | Values | Use it when |
| --- | --- | --- |
| `size` | `thumb` 256, `small` 512, `medium` 768, `large` 1024 | A square is fine. |
| `width`, `height` | 1–1024 px each | The layout has a box. One dimension keeps the aspect ratio; both together return exactly `width`×`height` (600×400 is 600×400, no longer a 400×400 square). |
| `fit` | `contain` (default), `cover`, `inside` | Only matters with both dimensions. `contain` keeps the whole car and pads with transparency or the `background`; `cover` fills the box and centre-crops; `inside` keeps the car within the box and may return a smaller image (the old behaviour). |
| `trim`, `padding` | `true`; 0–50 | The slot is not square. `trim` crops to the car's alpha bounds before sizing so it fills the box instead of floating in the square source frame; `padding` keeps a margin, as a percentage of the car's longer side, and only applies with `trim`. |
| `background` | `transparent` (default), `white`, `black`, hex as `rrggbb`, `#rrggbb`, `rgb` or `#rgb` | The surface cannot show transparency or wants a flat color. A solid background flattens PNG and WebP too; `jpg` cannot be transparent and defaults to white. |
| `format` | `png` (default), `webp`, `jpg`, `auto` | `auto` negotiates WebP or PNG from each client's `Accept` header (`Vary: Accept`); a signed URL created with `auto` negotiates on every load. |

A 16:9 hero: `width: 1024, height: 576, trim: true, padding: 6`. A thumbnail on a grey card: `size: "thumb", background: "#f4f4f4"`. The same vehicle, view and color is one render however it is sized, so different boxes of the same car stay fast.

## Authentication

The key lives in the environment as `CAR_IMAGE_API_KEY` and looks like `cimg_…`. Send it as `Authorization: Bearer $CAR_IMAGE_API_KEY`.

**Never** put a key in a URL, in HTML, in client-side JavaScript, in a commit, in a log line, in a screenshot, in a config file that gets committed, or in a prompt. If the key is missing, tell the user to run `npx @meterapp/car-image login` (browser device flow, stored with mode `0600`) or create one at [the dashboard](https://carimage.dev/dashboard?ref=plugin). Do not guess or fabricate keys.

Browser code must never hold the key. Mint signed URLs server-side instead — that is what `create_car_image_urls` is for.

## Work the user can trust

1. **Resolve before you spend.** When the request is free text, resolve it first. Rendering the wrong vehicle still costs a credit.
2. **Ask when it is ambiguous.** `confidence` is `high`, `medium` or `low`. On `low`, or when several candidates fit, show the candidates and let the user pick; on `medium`, say in one line which vehicle you chose. "Civic" spans four decades.
3. **Reuse parameters.** Identical make/model/year/view/color hits the cache, so repeated requests stay cheap and fast.
4. **Write real alt text.** "2024 Porsche 911, side view, red" — not "car image".
5. **These are renders, not photographs.** They are generated product visuals. Never claim a specific trim, options package or individual listed vehicle is depicted exactly. For a used-car listing, say the image represents the model, not that car.
6. **Close the loop.** After the user judges a render, call `rate_image` so the quality pipeline sees it.
7. **Ask, don't substitute.** When the catalog lacks the vehicle, offer `request_vehicle`; when the user wishes the API did something it does not, offer `request_feature`. Both are free, public on [the request board](https://carimage.dev/requests?ref=plugin), and the team emails the user when a vehicle goes live. Only call `share_building` or `share_referral` with something the user actually said and agreed to share.

## When something fails

Every JSON failure is an RFC 9457 `application/problem+json` document with `detail` and `request_id`. Keep the `request_id` — it is what support needs.

| Status | Meaning | Do |
| --- | --- | --- |
| 400 | Invalid parameter | Views, colors, `fit` and `format` are fixed enums; `padding` needs `trim`; `jpg` cannot be `transparent`; dimensions stop at 1024. Fix the value with `list_image_options` or `resolve_vehicle`. |
| 401 | Missing or invalid key | Ask the user to log in or set `CAR_IMAGE_API_KEY`. Never guess a key. |
| 402 | Out of credits | **Stop and ask the human** to top up at [the dashboard](https://carimage.dev/dashboard?ref=plugin#billing) or with `car-image billing`. Never buy credits on your own. |
| 404 | Vehicle not in the catalog | Search for the canonical make/model/year. If it is really missing, offer to file it with `request_vehicle` — the team adds requested vehicles and emails the user when it is live. Do not invent vehicles or substitute a different one without saying so. |
| 429 | Rate limited | Wait `Retry-After` seconds, retry once. Never hammer. |
| 502/503 | Render or upstream failure | Credits are refunded. Retry once later; report with the `request_id`. |

The full table, including every `type` URI, is in [references/errors.md](references/errors.md).

## Never do these on your own

- Buy credits, change a plan, or touch billing. A `402` is a question for the human, not a purchase to make.
- Render a large batch the user did not ask for. Confirm the count and the cost first.
- Put the API key anywhere a browser, a repository or a log can see it.
- Claim an image is a photograph of a specific vehicle.

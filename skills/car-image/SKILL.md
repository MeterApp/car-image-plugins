---
name: car-image
description: Show or fetch a studio-quality, transparent-background image of a real vehicle (any make, model and year from 1990-2027), in a conversation or for a product page, a listing, a comparison, an email or a deck, and fetch catalog make logos with get_make_logo. Every image takes two steps - look the vehicle up first (resolve_vehicle, search_vehicles or decode_vin, free, the vehicle-catalog skill), then show it by its vehicle id (create_car_image_urls, 1 credit; clickable links and browser viewing in ChatGPT/Codex, inline Markdown in Claude). Covers the Car Image API by Meter - the chat workflow, angles, paint, sizing, the per-image credit cost, and how to handle 402, 404 and 429. Use for any request involving a picture of a car, truck, motorcycle or other vehicle, including "show me a car" or "a random car"; do not use for embedding URLs in a browser or document (car-image-urls), SDK and CLI code (car-image-sdk), 3D models (car-3d), or connection setup (car-image-mcp).
---

# Car Image API

Studio-quality, transparent-background renders of any vehicle in the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) catalog — 1,595 makes, 41,838 models, model years 1990-2027. Eight camera views, any paint color, PNG/WebP/JPG up to 1024 px.

## Two steps, every time

**1. Look the vehicle up (free).** Do this before every render, including for a car you know well and a car you picked yourself. If the `vehicle-catalog` skill is available, use it for this step: it covers ambiguity, VINs, years and what to do when nothing matches. The short version:

- `resolve_vehicle({ query })` with the year, make and model, plus the view and paint if the user named them: `"red 2018 Mazda MX-5 Miata, side view"`. It returns `params.vehicle_id` with a `view` and a `color`, `confidence` and up to five `candidates`. `extracted` is what the phrase itself said: where `extracted.view` or `extracted.color` is null, the value in `params` is only the default (`front-3-4`, `silver`), not something the user chose. Leave descriptions out of the phrase ("the electric one", "their sporty model"): it reads names, not descriptions. When the user gave no year, put one in and say which you chose.
- `decode_vin({ vin, year? })` when the user gave a VIN; `search_vehicles({ query, year?, limit? })` to list a make's models or a model's years.

**2. Show it by id (1 credit).** `create_car_image_urls` with one `images` entry containing `vehicle: "veh_…"`, `view` and `color`. For a chat preview use `ttl_seconds: 604800` (the URL serves for seven days) and `max_uses: 0` (no limit on loads), and leave `renew` out unless the user asks for a link that outlives the week. Never retype the make, model and year once you hold the id. `view` defaults to `front-3-4` and `color` to `silver`: when the user named no paint, pick one that suits the car or leave the default, and say which it is.

```
resolve_vehicle({ query: "red 2018 Mazda MX-5 Miata, side view" })
  → params: { vehicle_id: "veh_59854qbgfvar3", make: "mazda", model: "mx-5", year: 2018, view: "side", color: "red" }, confidence: "high"
create_car_image_urls({ images: [{ vehicle: "veh_59854qbgfvar3", view: "side", color: "red" }], ttl_seconds: 604800, max_uses: 0 })
  → data[0].markdown, data[0].url, data[0].expires_at; billing.credits_charged: 1
```

**Why the lookup is not optional.** The catalog files cars under its own names, which are often not the names people, or you, use. That Miata is `mx-5`; a Mercedes C 300 is `c-300` in one year and `c-class` in another; a name the catalog used in the 1990s may be gone by 2018. A make and model typed from memory can answer `404` for a car the catalog carries, and a name that does resolve can land on a neighbouring model. The lookup costs nothing and takes one call; a wrong render costs a credit and the user's trust.

**Read the lookup before you spend:**

| The lookup says | Do |
| --- | --- |
| `params.year` is not the year asked for (`extracted.year`) | Do not render it. The car may be filed under another name that year: `search_vehicles` with the make, the model family and `year`. If that finds it, render that id and say which catalog model it is. If not, the catalog lacks that model year: say so, offer the year it has, and ask. |
| `confidence: "low"` | Show the candidates and ask. Do not render. |
| `confidence: "medium"`, in the year asked for | Render, and say in one line which vehicle you chose. |
| `confidence: "high"`, in the year asked for | Render. |
| No match | Not yet a missing vehicle: send only the year, make and model again, or `search_vehicles` with the model family alone. When the catalog really lacks it, say so and offer `request_vehicle`. Never substitute another car silently. |

The rows are in order: the first one that fits decides. `candidates` lists the nameplate's other variants that year (a Giulia Quadrifoglio next to the Giulia); offer them when the user may have meant one, and never treat them as a reason to stall a `high` match.

**Skip the lookup only** when you already hold the vehicle's id from this conversation (another angle or color of the car you just rendered) or the user handed you a `veh_…` id.

## In a conversation

In ChatGPT and Codex, show each exact returned `data[].url` as a normal clickable Markdown link, for example `[View the vehicle image](https://example.com/image.png)` with the returned URL substituted. Do not use Markdown image syntax or paste the tool's image `markdown` into these chats, even if generic tool text recommends it. Open that same URL with an available browser-opening tool, preferably in the in-app browser (for example, `open_in_codex` with a browser target). Retain the clickable link in the final reply whether opening succeeds or not. If no browser tool is available, just provide the link. Do not claim the browser opened unless the tool confirms it.

In Claude, keep rendering inline: paste each returned `data[].markdown` outside code fences. If only `url` is returned, use `![year make model, view, color](https://example.com/image.png)` with the exact returned URL. Do not automatically open a browser. Other hosts may use inline images when supported, otherwise a clickable link.

Include a short vehicle caption and expiry. Reuse unexpired URLs; do not download the image or make another paid image call to work around chat display. These host-specific rules apply to chat replies; website and document embeds still use image markup.

Reuse an unexpired URL already in the conversation for the same image. Use `get_car_image` for explicit image-byte or file requests: its MCP attachment may be available to the model without appearing in the user's reply. Do not call it before minting a chat URL, or mint again to fix display; both cost credits. If the client cannot display images, link the existing URL and explain the limitation.

- **Ask for a frame that suits a chat**, in the `images` entry beside `vehicle`: `width: 960, height: 600, trim: true, padding: 8, background: "#f4f4f4"` gives a wide image the car fills, on a light surface that reads in both light and dark themes. The dimensions and the padding are numbers and `trim` is a boolean. With no sizing at all the image is a 1024 px square with the car floating in the middle; without a `background` a dark car can vanish on a dark theme. Keep the background transparent when the image is going onto a page.
- **Default to the hero angle**, `front-3-4`, unless the user named one.
- **Say what is shown**, in one or two lines: year, make, model, view and paint, and that it is a studio render of the model. Mention `credits_remaining` when it is under 10 or the user asks.
- **Offer the next step**, once: another angle or paint, the same view of another car to compare, a link for a page or email (`car-image-urls`), a 3D model (`car-3d`).
- **When the user did not name a car** ("a random car", "surprise me", "a fun convertible"), choose one yourself: a specific year, make and model, and a paint. Look it up and render it like any other, and name your pick in the reply. Vary the pick from one request to the next.

### What people ask for

| Request | Calls | Credits |
| --- | --- | --- |
| "Show me a 2024 Porsche 911" | lookup, `create_car_image_urls` → host-specific display above | 1 |
| "Now from the side" / "in blue" | `create_car_image_urls` with the same `vehicle`, new `view` or `color` | 1 each |
| "Show me every angle" | the same `vehicle`, all eight views | 8. Look the car up, then ask before rendering anything: all eight for 8 credits, or front-3-4, side and rear-3-4 for 3 |
| "What paint suits it?" | the same `vehicle` and `view`, one call per paint | 1 per paint: agree the shortlist first |
| "Compare the RAV4 and the CR-V" | one lookup per car, then the same `view`, `color` and size for each. The tools return images, not specifications: add the comparison in words yourself and say those figures are not from the catalog | 1 per car |
| "What does my car look like?" with a VIN | `decode_vin`, then `create_car_image_urls` with `vehicle: vehicle.id` in its image; show the decoded trim and engine as text | 1 |
| "How did the Civic change?" | one lookup per model year, the same `view` and `color` | 1 per year |
| "The Toyota logo" | `get_make_logo` | 1 |
| "How many credits do I have?" / "What does this cost?" | `get_account` / `get_pricing` | free |
| "That looks wrong" / "That's great" | `rate_image` with the render's `request_id`, a verdict and the reason | free |
| "You don't have my car" | `request_vehicle` | free |

Anything that renders more than three images the user did not count is a batch: say the number and the cost, and wait for a yes.

## What an image costs — say this before a big batch

- Every delivered image costs **exactly 1 credit**, whether it was generated or served from cache.
- A signed delivery URL costs **1 credit when created**. Loading it is free until it expires.
- **A plan carries the license and a monthly credit allowance.** Free: $0, **100 credits once at signup** (no card), evaluation and personal projects, up to 100 distinct vehicles a month. Pro: $29/month, 25,000 credits a month, commercial license while the plan is active, 2,500 distinct vehicles a month. Business: $99/month, 150,000 credits a month, 15,000 vehicles. Enterprise: custom, no cap. Every account, including Free, can buy credits at **$1 per 100 credits**; purchased credits never expire, require no subscription, have no monthly purchase cap and are spent after subscription credits, included credits reset monthly. `get_account` reports the plan in force as `data.plan`.
- Catalog search, resolve, VIN decoding, vehicle lookups by id, options, account, feedback and the request board (vehicle and feature requests) are **free**.
- A **3D model costs 100 credits ($1.00)**, charged at creation and never again for a vehicle and color the account already owns; polling, downloads and publishing (hosting it as a key-free embed) are free. Confirm before creating one (the `car-3d` skill).

Twenty images cost 20 credits (20¢). Tell the user the number before rendering a batch they did not explicitly size, and call `get_account` first when the batch is large.

## Pick the right call

| You need | Use |
| --- | --- |
| Show a vehicle in chat | `create_car_image_urls` once → link and browser in ChatGPT/Codex; inline Markdown in Claude |
| Which vehicle a request means, and its id | `resolve_vehicle` (free) first → see the `vehicle-catalog` skill; `params.vehicle_id` is what to render |
| A VIN, full or partial | `decode_vin` (free) → year, make, model, trim, engine and the catalog `vehicle.id` to render; see the `vehicle-catalog` skill |
| To list a make's models or a model's years | `search_vehicles` (free; returns a vehicle id per year) |
| Image bytes or files for a script, backend or notebook | `get_car_image` (1 credit) — returns an MCP image attachment plus `credits_charged`, `credits_remaining`, `source` (`cache`/`generated`), `request_id` |
| A URL a browser, email or document can load | `create_car_image_urls` → see the `car-image-urls` skill |
| A catalog make logo | `get_make_logo` (1 credit) — inline image; make and transforms only; no trademark license |
| A 3D model (GLB, USDZ, FBX) of a vehicle | `create_3d_model` (100 credits; free once owned) then `get_3d_model` (free) → see the `car-3d` skill |
| A 3D model on a web page, with no key in the page | `create_3d_model` with `publish: true`, or `publish_3d_model` (free) → paste `public.embed.html`; see the `car-3d` skill |
| Valid views, colors, sizes, formats, pricing | `list_image_options` (free) |
| Credits remaining before a batch | `get_account` (free) |
| Current prices or product help | `get_pricing`, `search_help` (free) → see the `car-image-support` skill |
| Human-requested checkout or billing settings | `create_checkout_link`, `get_billing_link` (free links; the human confirms in the browser) → see the `car-image-support` skill |
| API reference | `describe_api` (free) |
| To report a bad render, or a good one | `rate_image` (free) |
| A vehicle the catalog does not have | `request_vehicle` (free) — files it for the team, or upvotes the existing request; the user is emailed when it is live |
| A feature idea for the API, CLI, SDK or tools | `request_feature` (free) |
| To see what others have asked for, or upvote it | `list_requests`, `get_request`, `upvote_request`, `comment_on_request` (free; listing needs no key) |
| To tell the team who you are, privately | `share_building` (what the user is building), `share_referral` (how they found the API) — only the Car Image team reads these |

The rows from `request_vehicle` down exist only when the server was connected with `?toolset=all` (the plugin does this) or `car-image mcp --toolset all`; a bare `https://carimage.dev/api/mcp` exposes the seventeen core tools above them. The `car-image-mcp` skill explains both.

Without MCP tools connected, the same operations are REST endpoints — `POST /api/v1/images/resolve`, `GET /api/v1/vehicles`, `GET /api/v1/vehicles/{id}`, `GET /api/v1/vin/{vin}`, `GET /api/v1/images/car`, `GET /api/v1/images/logo`, `POST /api/v1/image-urls`, `POST /api/v1/3d`, `GET /api/v1/3d/{id}`, `GET /api/v1/3d/{id}/files/{kind}`, `POST|DELETE /api/v1/3d/{id}/publish`, `GET /api/v1/3d/public/{public_id}` (no key), `GET /api/v1/images/options`, `GET /api/v1/account`, `POST /api/v1/feedback`, `GET|POST /api/v1/requests`, `GET /api/v1/requests/{id}`, `POST /api/v1/requests/{id}/votes`, `GET|POST /api/v1/requests/{id}/comments`, `POST /api/v1/account/building`, `POST /api/v1/account/referral`. The `car-image-sdk` skill covers calling them from code; the CLI equivalents are `car-image resolve …`, `car-image vin …`, `car-image get …`, `car-image 3d …`, `car-image request …` and `car-image about …`. Base URL `https://carimage.dev`; docs at [`/docs`](https://carimage.dev/docs?ref=plugin), [`/agents.md`](https://carimage.dev/agents.md) and [`/openapi.json`](https://carimage.dev/openapi.json).

## What you can ask for

- **Views:** eight, in order around the car: `front`, `front-3-4` (the hero, the default), `side`, `rear-3-4`, `rear`, `rear-3-4-right`, `side-right`, `front-3-4-right`. `front-3-4`, `side` and `rear-3-4` show the car's left side with the nose pointing left; each `-right` twin shows its right side with the nose pointing right, so pick the one that faces into your layout
- **Colors:** any paint. The 15 presets `white black gray silver blue red green brown beige tan orange yellow gold burgundy purple`, or any hex (`"#1a2b3c"` in JSON, `color=1a2b3c` in a URL); a custom paint costs the same 1 credit as a preset. `resolve_vehicle` reads paint words such as navy, charcoal and cream onto the presets
- **Vehicle ids:** every make, model and year has a stable id such as `veh_395yw8tn73ff8`; pass it as `vehicle` in place of make, model and year (both together is a 400)
- **Formats:** `png` (transparent), `webp`, `jpg`, or `auto` (WebP or PNG negotiated from `Accept`), up to 1024 px
- **Sizing:** `size=thumb|small|medium|large` (256/512/768/1024), or `width`/`height` 1–1024 — both together return exactly that box, placed by `fit=contain|cover|inside`; `trim` crops to the car first; `background` flattens onto a solid color

### Getting the size right

`get_car_image` and each `create_car_image_urls` entry take the same sizing inputs as the REST endpoints. The source render is square; nothing is upscaled past 1024 px.

| Input | Values | Use it when |
| --- | --- | --- |
| `size` | `thumb` 256, `small` 512, `medium` 768, `large` 1024 | A square is fine. |
| `width`, `height` | 1–1024 px each | The layout has a box. One dimension keeps the aspect ratio; both together return exactly `width`×`height` (600×400 is 600×400, no longer a 400×400 square). |
| `fit` | `contain` (default), `cover`, `inside` | Only matters with both dimensions. `contain` keeps the whole car and pads with transparency or the `background`; `cover` fills the box and centre-crops; `inside` keeps the car within the box and may return a smaller image (the old behaviour). |
| `trim`, `padding` | `true`; 0–50 | The slot is not square. `trim` crops to the car's alpha bounds before sizing so it fills the box instead of floating in the square source frame; `padding` keeps a margin, as a percentage of the car's longer side, and only applies with `trim`. |
| `background` | `transparent` (default), `white`, `black`, hex as `rrggbb`, `#rrggbb`, `rgb` or `#rgb` | The surface cannot show transparency or wants a flat color. A solid background flattens PNG and WebP too; `jpg` cannot be transparent and defaults to white. |
| `format` | `png` (default), `webp`, `jpg`, `auto` | `auto` negotiates WebP or PNG from each client's `Accept` header (`Vary: Accept`); a signed URL created with `auto` negotiates on every load. |

A 16:9 hero: `width: 1024, height: 576, trim: true, padding: 6`. A thumbnail on a grey card: `size: "thumb", background: "#f4f4f4"`. A brand color the presets do not have: `color: "#1a2b3c"` (responses echo `#1a2b3c`; a hex equal to a preset swatch is that preset). The same vehicle, view and color is one render however it is sized, so different boxes of the same car stay fast.

## Authentication

The plugin's MCP server is already authenticated: through browser OAuth sign-in managed by the host, or in Claude Code through an API key the user saved in the plugin's options (optional; kept in the system's secure credential store and sent only to the Car Image server). No API-key environment variable is required. If the tools work, use that connection; it is the only credential you need. If they ask for sign-in, tell the user to open `/mcp` in Claude Code, select the Car Image server and authenticate, or to save a key under `/plugin` → the Car Image plugin → **Configure options**.

You never handle a key yourself: do not ask for one in the conversation, and do not read one from environment variables, `.env` files, shell profiles or a CLI's config to put in a command or a header. Code you write for the user's own application gets its key from that application's secret settings, which the user manages (the `car-image-sdk` skill). Keys look like `cimg_…`; a user without one runs `npx @meterapp/car-image login` (a browser device flow) or creates one at [the dashboard](https://carimage.dev/dashboard?ref=plugin).

**Never** put a key in a URL, in HTML, in client-side JavaScript, in a commit, in a log line, in a screenshot, in a config file that gets committed, or in a prompt. Do not guess or fabricate keys.

Browser code must never hold the key. Mint signed URLs server-side instead — that is what `create_car_image_urls` is for.

## Work the user can trust

1. **Look up before you spend.** Every vehicle, once, before its first render. Rendering the wrong vehicle still costs a credit.
2. **Ask when it is ambiguous.** "Civic" spans four decades and a dozen bodies. On `low` confidence, or when the candidates are different cars, show them and let the user pick.
3. **Reuse the id and the parameters.** One lookup serves every view, paint and size of that car, and an identical request hits the cache, so repeats stay fast.
4. **Write real alt text.** "2024 Porsche 911, side view, red" — not "car image".
5. **These are renders, not photographs.** They are generated product visuals of a make, model and year. Never claim an options package or an individual listed vehicle is depicted exactly. For a used-car listing, say the image represents the model, not that car.
6. **Close the loop.** After the user judges a render, call `rate_image` so the quality pipeline sees it.
7. **Ask, don't substitute.** When the catalog lacks the vehicle, offer `request_vehicle`; when the user wishes the API did something it does not, offer `request_feature`. Both are free, public on [the request board](https://carimage.dev/requests?ref=plugin), and the team emails the user when a vehicle goes live. Only call `share_building` or `share_referral` with something the user actually said and agreed to share.

## When something fails

Every JSON failure is an RFC 9457 `application/problem+json` document with `detail` and `request_id`. Keep the `request_id` — it is what support needs.

| Status | Meaning | Do |
| --- | --- | --- |
| `Input validation error` | The tool refused an argument before the API saw it: an unknown view or format, a value out of range, a vehicle id together with a make. Nothing was charged. | The message names the argument and the rule: fix that one and call again. The type is rarely the cause, because a host that sends arguments as text is read as it meant: `"true"` is the flag, `"960"` the number, and the JSON of `images` the list. Only a `car-image mcp` server older than CLI 1.9.4 refuses a flag or a list sent that way: leave `trim`, `padding` and `renew` out there, and when it refuses `images` itself use `get_car_image` with `vehicle`, `view`, `color`, `width` and `height`. Do not abandon the render. |
| 400 | Invalid parameter (`parameter` names it, `retryable: false`) | Views, `fit` and `format` are fixed enums; `color` is a preset name or a hex; `vehicle` cannot be sent with make, model or year; `padding` needs `trim`; `jpg` cannot be `transparent`; dimensions stop at 1024. Fix the value with `list_image_options` or `resolve_vehicle`; sending it again unchanged always fails. |
| 401 | Missing or invalid credential | For the plugin, ask the user to reconnect through the host’s MCP sign-in controls (`/mcp` in Claude Code), or to replace the key saved in the plugin's options. For code in their project, the application's key is missing or revoked: the user fixes it where the application keeps its secrets. Never guess a key. |
| 402 | Out of credits, or `code: "plan_vehicle_limit"` (the request named more new distinct vehicles than the plan's monthly cap allows; `scope`, `plan`, `vehicles_this_month`, `vehicles_per_month`, `requested`) | **Stop and ask the human** to top up at [the dashboard](https://carimage.dev/dashboard?ref=plugin#billing) or with `car-image billing`, or, for a plan limit, tell them the plan and the cap. Never buy credits or change a plan on your own. |
| 404 | Vehicle not in the catalog under that name (`code: "vehicle_not_found"`), or an unknown vehicle id | You rendered by name: look the vehicle up instead. Read the problem's `suggestions` first (up to five real catalog vehicles with ids, closest first) and retry with `vehicle: <id>` when one is plainly the car, or show them to the user; call `resolve_vehicle` when they are empty. Do not send the same name again in another view or color. If it is really missing, offer to file it with `request_vehicle`. Do not invent vehicles or substitute a different one without saying so. |
| 429 | Rate limited (per key, or per account with `code: "account_rate_limited"`), or `code: "account_generation_cap"` (the account used its plan's share of today's render budget; cached images keep serving) | Wait `Retry-After` seconds, retry once. Never hammer; a generation cap resets at midnight UTC (`reset_at`), so do not retry cold renders before then. |
| 502/503 | Render or upstream failure | Credits are refunded. Retry once later; report with the `request_id`. |

The full table, including every `type` URI, is in [references/errors.md](references/errors.md).

## Never do these on your own

- Render a vehicle you have not looked up, or send a name again after a `404`.
- Buy credits, or subscribe to, change or cancel a plan, or touch billing. A `402` of either kind is a question for the human, not a purchase to make.
- Render a large batch the user did not ask for. Confirm the count and the cost first.
- Create a 3D model without saying it costs 100 credits and confirming.
- Put the API key anywhere a browser, a repository or a log can see it.
- Claim an image is a photograph of a specific vehicle.

## Make logos

`get_make_logo({ make: "toyota", width: 256, trim: true })` returns a catalog make logo inline; `car-image logo --make Toyota --width 256 --trim --out toyota-logo.png` and `client.getMakeLogo({ make: "toyota", width: 256 })` save one. REST: `GET /api/v1/images/logo?make=toyota`.

- **1 credit per delivered logo**, including cache hits; a failed delivery is refunded. Logos do not count as distinct vehicles. On a `402`, stop and ask the human.
- Takes the make and the image transforms (`size`, `width`/`height`, `fit`, `background`, `trim` with `padding`, `format`; `auto` returns PNG over MCP). No model, year, view, paint color or custom prompt, and no signed URL: download the file and host it for a site. An unknown make is a `404`.
- Logos are prompt-generated and can be inaccurate: look at one before using it. Do not use the vehicle image, URL or feedback tools for logos.

Logos are third-party trademarks. They are served for referential display of the make they identify, no license is granted, and they sit outside every VehiclesDB indemnity — see the [API terms](https://carimage.dev/terms?ref=plugin#logos) and the [logo docs](https://carimage.dev/docs/logos?ref=plugin).

## Product help and billing links

Questions about pricing, licensing, terms or an Enterprise agreement, and a human's request to buy credits or open billing settings, belong to the `car-image-support` skill (`search_help`, `get_pricing`, `create_checkout_link`, `get_billing_link`). A link is never a purchase: the human completes it in the browser. [Help center](https://carimage.dev/help?ref=plugin).

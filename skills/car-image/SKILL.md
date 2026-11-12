---
name: car-image
description: "Show or fetch a studio-quality, transparent-background image of a real vehicle (any make, model and year from 1990-2027), in a conversation or for a product page, a listing, a comparison, an email or a deck, and fetch catalog make logos with get_make_logo. Every image takes two steps - look the vehicle up first (resolve_vehicle, search_vehicles or decode_vin, free, the vehicle-catalog skill), then show it by its vehicle id (create_car_image_urls for the inline ChatGPT card; get_car_image in other chat hosts; one vehicle image of the plan's month). Covers the Car Image API by Meter - the chat workflow, angles, paint, sizing, what a plan counts (vehicle images), and how to handle 402, 404 and 429. Works before sign-in: lookups and a free preview of the picture a vehicle's page already shows (preview_car_image), then the account for the exact image. Use for any request involving a picture of a car, truck, motorcycle or other vehicle, including \"show me a car\" or \"a random car\"; do not use for embedding URLs in a browser or document (car-image-urls), SDK and CLI code (car-image-sdk), 3D models (car-3d), or connection setup (car-image-mcp)."
---

**ChatGPT image card:** For a requested image, after the free vehicle lookup, use `create_car_image_urls` with the returned `vehicle` id, `ttl_seconds: 604800`, `max_uses: 0`, and renewal off. ChatGPT displays the returned images in an inline card. Do not call `get_car_image` first or make another image call to fix display. Reuse an unexpired URL. If the card is unavailable, show the exact returned URL as a clickable link and state expiry. These ChatGPT instructions take precedence over the general chat examples below. Other hosts keep their own display workflow.

When no view is specified, use **Front three-quarter (facing left)**, `view=front-3-4` (35°). Preserve any view the user explicitly requests.

# Car Image API

Studio-quality, transparent-background renders of any vehicle in the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) catalog — 1,608 makes, 42,347 models, model years 1990-2027. Nine camera views, any paint color, PNG/WebP/JPG up to 1024 px.

## Check readiness and quality

When the human asks whether an image is already prepared/cached or what quality it has, resolve the vehicle first, then call `get_image_availability({ vehicle, view, color })`. Omit `view` for all nine. **Prepared means cached and quick to serve from storage without waiting for a new render.** Report `cached` and `quality` (`standard`, `enhanced`, `premium`, or null), and `render_eta` when uncached. The check is free: it renders, queues and counts nothing. Checking never authorizes generating or upgrading. A missing public preview is not proof that an authenticated view needs generation.

## Two steps, every time

**1. Look the vehicle up (free).** Do this before every render, including for a car you know well and a car you picked yourself. If the `vehicle-catalog` skill is available, use it for this step: it covers ambiguity, VINs, years and what to do when nothing matches. The short version:

- `resolve_vehicle({ query })` with the year, make and model, plus the view and paint if the user named them: `"red 2018 Mazda MX-5 Miata, side view"`. It returns `params.vehicle_id` with a `view` and a `color`, `confidence` and up to five `candidates`. `extracted` is what the phrase itself said: where `extracted.view` or `extracted.color` is null, the value in `params` is only the default (`front-3-4`, `silver`), not something the user chose. Leave descriptions out of the phrase ("the electric one", "their sporty model"): it reads names, not descriptions. When the user gave no year, put one in and say which you chose.
- `decode_vin({ vin, year? })` when the user gave a VIN; `search_vehicles({ query, year?, limit? })` to list a make's models or a model's years.

**2. Show it by id (one vehicle image).** `get_car_image` with `vehicle: "veh_…"`, `view` and `color`. It returns the picture itself, and a chat app shows it inline with the result (in claude.ai the image appears in the conversation; where the host lets you attach a file to the reply, attach it). No URL is needed for that: do not also call `create_car_image_urls` for the same image. Never retype the make, model and year once you hold the id. `view` defaults to `front-3-4` and `color` to `silver`: when the user named no paint, pick one that suits the car or leave the default, and say which it is.

```
resolve_vehicle({ query: "red 2018 Mazda MX-5 Miata, side view" })
  → params: { vehicle_id: "veh_59854qbgfvar3", make: "mazda", model: "mx-5", year: 2018, view: "side", color: "red" }, confidence: "high"
get_car_image({ vehicle: "veh_59854qbgfvar3", view: "side", color: "red", width: 960, height: 600, trim: true, padding: 8, background: "#f4f4f4" })
  → the PNG, shown inline; credits_charged: 0, vehicle_images: { used, included }, source: "cache" | "generated", request_id
```

**Why the lookup is not optional.** The catalog files cars under its own names, which are often not the names people, or you, use. That Miata is `mx-5`; a Mercedes C 300 is `c-300` in one year and `c-class` in another; a name the catalog used in the 1990s may be gone by 2018. A make and model typed from memory can answer `404` for a car the catalog carries, and a name that does resolve can land on a neighbouring model. The lookup costs nothing and takes one call; a wrong render uses up an image of the month and the user's trust.

**Read the lookup before you spend:**

| The lookup says | Do |
| --- | --- |
| `params.year` is not the year asked for (`extracted.year`) | Do not render it. The car may be filed under another name that year: `search_vehicles` with the make, the model family and `year`. If that finds it, render that id and say which catalog model it is. If not, the catalog lacks that model year: say so, offer the year it has, and ask. |
| `confidence: "low"` | Show the candidates and ask. Do not render. |
| `confidence: "medium"`, in the year asked for | Render, and say in one line which vehicle you chose. |
| `confidence: "high"`, in the year asked for | Render. |
| No match | Not yet a missing vehicle: send only the year, make and model again, or `search_vehicles` with the model family alone. When the catalog really lacks it, say the catalog does not carry it and stop; never substitute another car. |

The rows are in order: the first one that fits decides. `candidates` lists the nameplate's other variants that year (a Giulia Quadrifoglio next to the Giulia); offer them when the user may have meant one, and never treat them as a reason to stall a `high` match.

**Skip the lookup only** when you already hold the vehicle's id from this conversation (another angle or color of the car you just rendered) or the user handed you a `veh_…` id.

## Before the account is connected

The plugin runs two servers. **`car-image-catalog`** needs no account and works from the first session: `resolve_vehicle`, `search_vehicles`, `preview_car_image`, `list_image_options`, `get_pricing` and `describe_api`. **`car-image`** is the account: the image in the view, paint and size asked for, signed URLs, VINs, lists, logos, 3D models and the balance. Until the user signs in, the host lists no `get_car_image` or `create_car_image_urls`; Claude Code shows `plugin:car-image:car-image` as needing authentication and may list an `authenticate` tool for it (`mcp__plugin_car-image_car-image__authenticate`).

When the user asks for a picture and `get_car_image` is not available:

1. **Look the vehicle up anyway**, as in step 1. Nothing about the lookup changes, except that `decode_vin` is on the account server: before sign-in, ask for the year, make and model a VIN stands for, or connect first.
2. **Show the free preview.** `preview_car_image({ vehicle })`, with `view` and `color` only when the user named them, returns the picture the vehicle's page on carimage.dev already shows, when one is stored. Display `data.preview` by the host rules below (its `markdown` in Claude's apps; in a terminal, the plain `url` on its own line) and say it is a preview, naming its view and paint when they differ from what was asked. A preview URL never expires. It never renders: a `null` preview means nothing is stored for that car yet. `data.stored` lists every stored view and paint, and `data.page` is the vehicle's page.
3. **Offer the account for what the preview cannot do, in one or two lines:** another view, paint or size, a file, or the image in a page, app or document (an image from the account counts one vehicle image of the plan's month and carries the plan's license; the preview is for looking at). A preview in the view and paint asked for answers the request: offer the rest, and never render the same picture again. To connect, in Claude Code call the `authenticate` tool when it is listed and give the user the URL it returns: it opens Car Image's sign-in provider (a supabase.co address), then carimage.dev, and works while this session is open. Otherwise ask them to run `/mcp`, choose `plugin:car-image:car-image` and **Authenticate**. In other hosts, connect Car Image in the MCP or connector settings. Signing up is free, and the Free plan includes 30 free vehicle images; the user needs no key for this.
4. **When the user says they have signed in, or the account tools appear, finish the original request** without asking them to say it again: `get_car_image` with the id you already hold.

Do not stop at "authentication required", and do not send the user to the website to make the image by hand. Work that needs no image needs no account either: explaining views, sizes and prices, or writing code against the API (`describe_api`, `list_image_options`, `get_pricing`; the code itself needs the user's own key, the `car-image-sdk` skill).

## In a conversation

Show the picture with `get_car_image`, once per image. In Claude's apps (claude.ai, Claude Desktop, mobile) and other chat apps that display a tool's image, the render appears inline with the result: that is the answer. Do not paste a URL as well, download it again, or make another paid image call to "fix" the display. If the host offers a way to attach a file to the reply, attach the returned image.

**Where the person cannot see a tool's image**, fall back to one signed URL: in a terminal (Claude Code, Codex), or a host that hands tool images to the model alone. Call `create_car_image_urls` once instead of `get_car_image` (not after it), with one `images` entry, `ttl_seconds: 604800` (seven days) and `max_uses: 0`, renewal off unless the user asks for a link that outlives the week, and show it by host:

- In a terminal such as Claude Code, put the plain `data[].url` on its own line; the terminal makes it clickable, and Markdown image syntax does not render there.
- In Codex, show each exact returned `data[].url` as a normal clickable Markdown link, for example `[View the vehicle image](https://example.com/image.png)` with the returned URL substituted, not Markdown image syntax. Open that same URL with an available browser-opening tool, preferably the in-app browser (for example, `open_in_codex` with a browser target). Keep the link in the final reply whether opening succeeds or not, and do not claim the browser opened unless the tool confirms it.
- Elsewhere, paste each returned `data[].markdown` outside code fences where inline images render, otherwise link the URL. State the expiry.

If you already showed the picture with `get_car_image` and the person then asks for a link, mint the URL then: on a plan the same image again this month counts nothing more. Reuse an unexpired URL already in the conversation for the same image. A link for a page, an email or a document is the `car-image-urls` skill.

- **Ask for a frame that suits a chat**, beside `vehicle` (in `get_car_image`, or in the `images` entry of a URL): `width: 960, height: 600, trim: true, padding: 8, background: "#f4f4f4"` gives a wide image the car fills, on a light surface that reads in both light and dark themes. The dimensions and the padding are numbers and `trim` is a boolean. With no sizing at all the image is a 1024 px square with the car floating in the middle; without a `background` a dark car can vanish on a dark theme. Keep the background transparent when the image is going onto a page.
- **Default to the hero angle**, `front-3-4`, unless the user named one.
- **Say what is shown**, in one or two lines: year, make, model, view and paint, and that it is a studio render of the model. Mention the month's usage (`vehicle_images.used` of `included` in the result; `billing.vehicle_images` on a URL) when the allowance is nearly used or the user asks.
- **Offer the next step**, once: another angle or paint, the same view of another car to compare, a link for a page or email (`car-image-urls`), a 3D model (`car-3d`).
- **When the user did not name a car** ("a random car", "surprise me", "a fun convertible"), choose one yourself: a specific year, make and model, and a paint. Look it up and render it like any other, and name your pick in the reply. Vary the pick from one request to the next.

### What people ask for

| Request | Calls | Counts |
| --- | --- | --- |
| "Show me a 2024 Porsche 911" | lookup, `get_car_image` → shown inline (a terminal: one signed URL instead) | 1 vehicle image |
| "Now from the side" / "in blue" | `get_car_image` with the same `vehicle`, new `view` or `color` | 1 image each |
| "Show me every angle" | the same `vehicle`, all nine views | 9 images. Look the car up, then ask before rendering anything: all nine (9 images of the month), or front-3-4, side and rear-3-4 (3) |
| "What paint suits it?" | the same `vehicle` and `view`, one call per paint | 1 image per paint: agree the shortlist first |
| "Compare the RAV4 and the CR-V" | one lookup per car, then the same `view`, `color` and size for each. The tools return images, not specifications: add the comparison in words yourself and say those figures are not from the catalog | 1 image per car |
| "What does my car look like?" with a VIN | `decode_vin`, then `get_car_image` with `vehicle: vehicle.id`; show the decoded trim and engine as text | 1 image |
| "How did the Civic change?" | one lookup per model year, the same `view` and `color` | 1 image per year |
| "The Toyota logo" | `get_make_logo` | 1 credit |
| "How many images are left this month?" / "What does this cost?" | `get_account` / `get_pricing` | free |
| "That looks wrong" / "That's great" | no call: a render is rated from the Recent images card on [the dashboard](https://carimage.dev/dashboard?ref=plugin#feedback) | none |
| "You don't have my car" | no call: say the catalog does not carry it and stop; never substitute another car | none |

Anything that renders more than three images the user did not count is a batch: say the number and the cost, and wait for a yes.

## What an image counts — say this before a big batch

- A plan counts **vehicle images**: one vehicle (make, model, year) in one color from one view, counted **once a month** (UTC) and then delivered as often as needed, at any size and format. A repeat, another size, a cache hit, a signed URL and its loads and renewals add nothing that month. No credit is charged for an image: the result says `billing.credits_charged: 0` and `billing.vehicle_images` (`used`, `included`).
- A view of a vehicle the catalog has not prepared yet counts as one vehicle image like any other. We prepare the vehicle in that view so it can be shown in any color, and that takes a little time: typically under 20 seconds for a vehicle's first image in front-3-4 (the default view), about 25 when the first image asked for is another view (the front-3-4 is drawn first and that view from it), about 15 for a further view. Images are standard quality; the vehicle's front-3-4 is redrawn at enhanced quality in the background, usually within a day, at no charge, and other views stay standard.
- **Plans.** Free: $0, no card, **30 vehicle images per account, not per month** (plus 30 more as a one-time courtesy once they run out), 100 credits once at signup, evaluation and personal projects. Pro: $49/month, 2,500 vehicle images and 1,000 credits a month, a commercial license while subscribed. Business: $99/month, 10,000 vehicle images and 4,000 credits a month. Enterprise: custom. There is **no overage**: past the allowance, images the month has not counted yet answer `402` (nothing charged) until the 1st (UTC); images already received keep serving. `get_account` reports `data.plan` and `limits_usage.vehicle_images_this_month`.
- **Credits are not sold.** They pay only for 3D models (100), make logos (1 per delivery) and quality upgrades (20), and come with a plan each month or once at signup; credits an account already holds stay spendable.
- An account that paid before 2026-10-25 stays on the credit meter until the cutover date in its notice: 1 credit per delivered image (`billing.credits_charged: 1`, `credits_remaining`), and `data.plan.meter` is `credits`.
- Catalog search, resolve, VIN decoding, vehicle lookups by id and by list, options and the account are **free**.
- A **3D model costs 100 credits**, charged at creation and never again for a vehicle and color the account already owns; polling, downloads and publishing (hosting it as a key-free embed) are free. Confirm before creating one (the `car-3d` skill).

Twenty images of new cars count 20 vehicle images. Tell the user the number before rendering a batch they did not explicitly size, and call `get_account` first when the batch is large. For a whole catalog, `POST /api/v1/images/availability` (free, REST and the SDK; no MCP tool) says which views are prepared and what the batch would count before anything is asked for.

## Pick the right call

| You need | Use |
| --- | --- |
| Show a vehicle in chat | `get_car_image` → the picture inline with the result; in a terminal, `create_car_image_urls` once instead and the URL as a link |
| A first look before the user has signed in | `preview_car_image` (free, catalog server; the picture the vehicle's page shows, when one is stored) → see [Before the account is connected](#before-the-account-is-connected) |
| Which vehicle a request means, and its id | `resolve_vehicle` (free) first → see the `vehicle-catalog` skill; `params.vehicle_id` is what to render |
| A VIN, full or partial | `decode_vin` (free) → year, make, model, trim, engine and the catalog `vehicle.id` to render; see the `vehicle-catalog` skill |
| To list a make's models or a model's years | `search_vehicles` (free; returns a vehicle id per year) |
| Which vehicles of a list (a catalog, a spreadsheet) the catalog carries, with their ids | `check_vehicles` (free, up to 100 per call; `car-image check <file>` or `client.checkVehicles` for longer lists) → see the `vehicle-catalog` skill |
| Image bytes or a file | `get_car_image` (one vehicle image) — returns the MCP image plus the billing usage, `source` (`cache`/`generated`), `request_id`; for a script or backend, the CLI or SDK (`car-image-sdk`) |
| A URL a browser, email or document can load | `create_car_image_urls` → see the `car-image-urls` skill |
| The month's allowance before a batch | `get_account` (free) |
| A catalog make logo | `get_make_logo` (1 credit) — inline image; make and transforms only; no trademark license |
| A 3D model (GLB, USDZ, FBX) of a vehicle | `create_3d_model` (100 credits; free once owned) then `get_3d_model` (free) → see the `car-3d` skill |
| A 3D model on a web page, with no key in the page | `create_3d_model` with `publish: true`, or `publish_3d_model` (free) → paste `public.embed.html`; see the `car-3d` skill |
| Valid views, colors, sizes, formats, pricing | `list_image_options` (free) |
| Current prices or product help | `get_pricing`, `search_help` (free) → see the `car-image-support` skill |
| Human-requested checkout or billing settings | `create_checkout_link`, `get_billing_link` (free links; the human confirms in the browser) → see the `car-image-support` skill |
| API reference | `describe_api` (free) |

The rows from `get_make_logo` down are included by the hosted endpoint and marketplace plugin, or with `car-image mcp --toolset all` for stdio. The `car-image-mcp` skill explains both.

Without MCP tools connected, the same operations are REST endpoints — `POST /api/v1/images/resolve`, `GET /api/v1/vehicles`, `GET /api/v1/vehicles/{id}`, `POST /api/v1/vehicles/check`, `GET /api/v1/vin/{vin}`, `GET /api/v1/images/car`, `GET /api/v1/images/logo`, `POST /api/v1/image-urls`, `POST /api/v1/3d`, `GET /api/v1/3d/{id}`, `GET /api/v1/3d/{id}/files/{kind}`, `POST|DELETE /api/v1/3d/{id}/publish`, `GET /api/v1/3d/public/{public_id}` (no key), `GET /api/v1/images/options` and `GET /api/v1/account`. The `car-image-sdk` skill covers calling them from code; the CLI equivalents are `car-image resolve …`, `car-image check …`, `car-image vin …`, `car-image get …`, `car-image logo …` and `car-image 3d …`. Base URL `https://carimage.dev`; docs at [`/docs`](https://carimage.dev/docs?ref=plugin), [`/agents.md`](https://carimage.dev/agents.md) and [`/openapi.json`](https://carimage.dev/openapi.json).

## What you can ask for

- **Views:** nine: eight in order around the car, `front`, `front-3-4` (the hero, the default), `side`, `rear-3-4`, `rear`, `rear-3-4-right`, `side-right`, `front-3-4-right`, then `top` (straight down from above, nose up). `front-3-4`, `side` and `rear-3-4` show the car's left side with the nose pointing left; each `-right` twin shows its right side with the nose pointing right, so pick the one that faces into your layout
- **Colors:** any paint. The 15 presets `white black gray silver blue red green brown beige tan orange yellow gold burgundy purple` (`grey` is `gray`), any other CSS color name (`navy` is `#000080`), or any hex (`"#1a2b3c"` in JSON, `color=1a2b3c` in a URL); a custom paint counts like a preset: one vehicle image per color. `resolve_vehicle` reads paint words such as navy, charcoal and cream onto the presets
- **Vehicle ids:** every make, model and year has a stable id such as `veh_395yw8tn73ff8`; pass it as `vehicle` in place of make, model and year (both together is a 400)
- **Formats:** `png` (transparent), `webp`, `jpg`, or `auto` (WebP or PNG negotiated from `Accept`), up to the stored image's own size: a 1024 px square for older renders, a canvas of up to 2560 px for new ones
- **Sizing:** `size=thumb|small|medium|large` (256/512/768/1024), or `aspect_ratio`/`resolution`, or `width`/`height` up to the stored image's own size (a larger size is clamped, a box keeping its shape) — both together return exactly that box, placed by `fit=contain|cover|inside`; `trim` crops to the car first (`framing: "balanced"` or `"tight"` names that composition); `shadow` adds a soft ground shadow under it; `background` flattens onto a solid color

### Getting the size right

`get_car_image` and each `create_car_image_urls` entry take the same sizing inputs as the REST endpoints. Each image is stored once, a 1024 px square for older renders and a view-shaped canvas of up to 2560 px for new ones; nothing is upscaled.

| Input | Values | Use it when |
| --- | --- | --- |
| `size` | `thumb` 256, `small` 512, `medium` 768, `large` 1024 | A square is fine. |
| `aspect_ratio` | `1:1`, `4:3`, `3:2`, `16:9`, `natural` (the car's own trimmed shape) | You know the shape, not the pixels. With `width` or `height` it completes the other; both together win. Not with `size`. |
| `resolution` | `small` 640, `medium` 1280, `hd` 1920, `2k` 2560 (the longer side, up to the stored image's size) | You want a sharpness, not a layout. `width` or `height` win. Not with `size`. |
| `width`, `height` | up to the stored image's own size (a larger box is scaled down whole) | The layout has a box. One dimension keeps the aspect ratio; both together return exactly `width`×`height` (600×400 is 600×400, no longer a 400×400 square). |
| `fit` | `contain` (default), `cover`, `inside` | Only matters with both dimensions. `contain` keeps the whole car and pads with transparency or the `background`; `cover` fills the box and centre-crops; `inside` keeps the car within the box and may return a smaller image (the old behaviour). |
| `framing` | `consistent` (default), `tight`, `balanced` | A named composition instead of `trim`/`padding` (never with them; same image and count as the spelled-out form). `balanced` (= `trim: true, padding: 6`) for catalog grids and listing heroes; `tight` (= `trim: true, padding: 0`) for small thumbnails; `consistent` for galleries, spinners and several views of one car, which then share one camera scale. Side by side, neither shows two cars at their real relative size. |
| `trim`, `padding` | `true`; 0–50 | The slot is not square. `trim` crops to the car's alpha bounds before sizing so it fills the box instead of floating in its frame; `padding` keeps a margin, as a percentage of the car's longer side, and only applies with `trim`. |
| `shadow` | `true` | The car sits on a page or a card and should look grounded, not pasted: a soft, neutral shadow under the car, drawn from its own cut-out (semi-transparent, or grey on a `background`). Same count; not on make logos. |
| `market` | a two-letter country code: `US`, `GB`, `DE`, `AU`, `JP` | The human named a market, or the vehicles are for one: some model years look different in different markets. Today every market gets the default appearance, and the answer's `appearance` (`{ market, scope: "default" }`) says which was served. Same image and same count under any market; omit it otherwise (the account's default market applies, if it set one), and never guess it from where the human is. |
| `background` | `transparent` (default), `white`, `black`, hex as `rrggbb`, `#rrggbb`, `rgb` or `#rgb` | The surface cannot show transparency or wants a flat color. A solid background flattens PNG and WebP too; `jpg` cannot be transparent and defaults to white. |
| `format` | `png` (default), `webp`, `jpg`, `auto` | `auto` negotiates WebP or PNG from each client's `Accept` header (`Vary: Accept`); a signed URL created with `auto` negotiates on every load. |

A 16:9 hero: `width: 1024, height: 576, trim: true, padding: 6`. A thumbnail on a grey card: `size: "thumb", background: "#f4f4f4"`. A brand color the presets do not have: `color: "#1a2b3c"` (responses echo `#1a2b3c`; a hex equal to a preset swatch is that preset). The same vehicle, view and color is one render however it is sized, so different boxes of the same car stay fast.

## Authentication

The catalog server needs no credential. The account server signs in through browser OAuth managed by the host: the plugin itself takes no key. If the account tools work, use that connection; it is the only sign-in you need. If they ask for sign-in, follow [Before the account is connected](#before-the-account-is-connected): the `authenticate` tool, or `/mcp` in Claude Code (select `plugin:car-image:car-image` and authenticate).

You never handle a key yourself: do not ask for one in the conversation, and do not look for one on the machine to put in a command or a header. Code you write for the user's own application gets its key from that application's secret settings, which the user manages (the `car-image-sdk` skill). Keys look like `cimg_…`; a user without one creates one at [the dashboard](https://carimage.dev/dashboard?ref=plugin) and keeps it where their application keeps its secrets.

**Never** put a key in a URL, in HTML, in client-side JavaScript, in a commit, in a log line, in a screenshot, in a config file that gets committed, or in a prompt. Do not guess or fabricate keys.

Browser code must never hold the key. Mint signed URLs server-side instead — that is what `create_car_image_urls` is for.

## Work the user can trust

1. **Look up before you spend.** Every vehicle, once, before its first render. Rendering the wrong vehicle still counts against the month.
2. **Ask when it is ambiguous.** "Civic" spans four decades and a dozen bodies. On `low` confidence, or when the candidates are different cars, show them and let the user pick.
3. **Reuse the id and the parameters.** One lookup serves every view, paint and size of that car, and an identical request hits the cache, so repeats stay fast.
4. **Write real alt text.** "2024 Porsche 911, side view, red" — not "car image".
5. **These are renders, not photographs.** They are generated product visuals of a make, model and year. Never claim an options package or an individual listed vehicle is depicted exactly. For a used-car listing, say the image represents the model, not that car.
6. **Close the loop.** When the user judges a render, point them at the Recent images card on [the dashboard](https://carimage.dev/dashboard?ref=plugin#feedback), where a render is rated; there is no tool for it.
7. **Say so, don't substitute.** When the catalog lacks the vehicle, say it does not carry it and stop. Never render the nearest thing in its place, and never present another car as the one that was asked for.

## When something fails

Every JSON failure is an RFC 9457 `application/problem+json` document with `detail` and `request_id`. Keep the `request_id` — it is what support needs.

| Status | Meaning | Do |
| --- | --- | --- |
| `Input validation error` | The tool refused an argument before the API saw it: an unknown view or format, a value out of range, a vehicle id together with a make. Nothing was charged. | The message names the argument and the rule: fix that one and call again. The type is rarely the cause, because a host that sends arguments as text is read as it meant: `"true"` is the flag, `"960"` the number, and the JSON of `images` the list. Only a `car-image mcp` server older than CLI 1.9.4 refuses a flag or a list sent that way: leave `trim`, `padding` and `renew` out there, and when it refuses `images` itself use `get_car_image` with `vehicle`, `view`, `color`, `width` and `height`. Do not abandon the render. |
| 400 | Invalid parameter (`parameter` names it, `retryable: false`) | Views, `fit` and `format` are fixed enums; `color` is a preset name, a CSS color name or a hex; `vehicle` cannot be sent with make, model or year; `padding` needs `trim`; `jpg` cannot be `transparent`. Fix the value with `list_image_options` or `resolve_vehicle`; sending it again unchanged always fails. |
| 401 | Missing or invalid credential | For the plugin, ask the user to reconnect through the host’s MCP sign-in controls (`/mcp` in Claude Code). For code in their project, the application's key is missing or revoked: the user fixes it where the application keeps its secrets. Never guess a key. |
| 402 | `code: "plan_image_limit"` (the month's vehicle images, or Free's per account, are used up), with `plan`, `used`, `included`, `requested`, `resets_at`, `checkout_url` and `pack_url`; or `code: "subscription_required_for_credits"` (not enough credits for a 3D model, logo or upgrade: credits are not sold), or `code: "plan_vehicle_limit"` on an account still on the credit meter. Nothing was charged. | **Stop and ask the human.** Tell them the plan, what it includes and when it resets (`resets_at`), and hand them `checkout_url` (the next plan, with its price) or `pack_url` (a one-time Image Pack). Images already received this month still serve. Never retry the `402`, buy anything or change a plan on your own. |
| 404 | Vehicle not in the catalog under that name (`code: "vehicle_not_found"`), or an unknown vehicle id | You rendered by name: look the vehicle up instead. Read the problem's `suggestions` first (up to five real catalog vehicles with ids, closest first) and retry with `vehicle: <id>` when one is plainly the car, or show them to the user; call `resolve_vehicle` when they are empty. Do not send the same name again in another view or color. If it is really missing, say so and stop. Do not invent vehicles or substitute a different one. |
| 429 | Rate limited (per key, or per account with `code: "account_rate_limited"`), or `code: "account_generation_cap"` (the account used its plan's share of today's render budget; cached images keep serving) | Wait `Retry-After` seconds, retry once. Never hammer; a generation cap resets at midnight UTC (`reset_at`), so do not retry cold renders before then. |
| 502 | The render failed | Nothing is counted or charged. Retry once later; if it fails again, offer the human `report_issue` with the `request_id` (and `endpoint`, `vehicle`, `view`, `color` in `context`). |
| 503 | Upstream briefly unavailable, `generation_paused` (new renders paused; retry once after `Retry-After`), or `generation_at_capacity` (new renders resume at `reset_at`, midnight UTC) | Nothing charged. Wait `Retry-After`; at capacity, do not retry before `reset_at`: tell the human when it resumes and that cached images still serve. |

The full table, including every `type` URI, is in [references/errors.md](references/errors.md).

**Feedback.** A render that is wrong or a call that fails in a way that looks like a Car Image bug: with the human's agreement, `report_issue` with the failed call's `request_id`; it is private to them and the team, and they are emailed when it is fixed. When the human wishes the API did something it does not, `request_feature`. Both answer with `similar` items first: `upvote_feedback` the one that matches instead of filing it again. A vehicle the catalog lacks is not an issue: say so and stop. Offer `submit_review` only after real use, with their own rating and words.

## Never do these on your own

- Render a vehicle you have not looked up, or send a name again after a `404`.
- Buy an Image Pack, or subscribe to, change or cancel a plan, or touch billing. A `402` of either kind is a question for the human, not a purchase to make.
- Render a large batch the user did not ask for. Confirm the count and the cost first.
- Create a 3D model without saying it costs 100 credits and confirming.
- Put the API key anywhere a browser, a repository or a log can see it.
- Claim an image is a photograph of a specific vehicle.

## Make logos

`get_make_logo({ make: "toyota", width: 256, trim: true })` returns a catalog make logo inline; `car-image logo --make Toyota --width 256 --trim --out toyota-logo.png` and `client.getMakeLogo({ make: "toyota", width: 256 })` save one. REST: `GET /api/v1/images/logo?make=toyota`. The tool is on `?toolset=all`, which the plugin configures; a connection on the bare URL has no logo tool (the `car-image-mcp` skill).

- **1 credit per delivered logo**, including cache hits; a failed delivery is refunded. Logos do not count as vehicle images. On a `402`, stop and ask the human.
- Takes the make and the image transforms (`size`, `width`/`height`, `fit`, `background`, `trim` with `padding`, `format`; `auto` returns PNG over MCP). No model, year, view, paint color or custom prompt, and no signed URL: download the file and host it for a site. An unknown make is a `404`.
- Logos are prompt-generated and can be inaccurate: look at one before using it. Do not use the vehicle image or URL tools for logos.

Logos are third-party trademarks. They are served for referential display of the make they identify, no license is granted, and they sit outside every VehiclesDB indemnity — see the [API terms](https://carimage.dev/terms?ref=plugin#logos) and the [logo docs](https://carimage.dev/docs/logos?ref=plugin).

## Product help and billing links

Questions about pricing, licensing, terms or an Enterprise agreement, and a human's request to subscribe, buy an Image Pack or open billing settings, belong to the `car-image-support` skill (`search_help`, `get_pricing`, `create_checkout_link`, `get_billing_link`). A link is never a purchase: the human completes it in the browser. [Help center](https://carimage.dev/help?ref=plugin).

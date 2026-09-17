# Changelog

## 1.6.0 — 2026-09-17

Plans: the license and a monthly allowance, with credits as the meter.

- **Plans.** Car Image API is sold as a plan that carries the commercial license to the renders while it is active: Free ($0; 100 credits once at signup; evaluation and personal projects; up to 100 distinct vehicles a month), Pro ($29/month or $290/year; 25,000 credits a month; 2,500 distinct vehicles a month), Business ($99/month or $990/year; 150,000 credits a month; 15,000 vehicles; 600 requests a minute per key) and Enterprise (custom; no vehicle cap; export or self-hosting by written agreement). Beyond the allowance every paid plan pays $1 per 1,000 credits; purchased credits never expire, included credits reset monthly. Every image is still 1 credit, cached or generated, and a 3D model is still 1,000 once per vehicle and color. `car-image`, `car-image-sdk`, the README and `AGENTS.md` state the plans wherever they quoted the price.
- **New answers to know.** `402` with `code: "plan_vehicle_limit"` (`Plan limit reached`: the request named more new distinct vehicles than the plan's monthly cap allows; `plan`, `vehicles_this_month`, `vehicles_per_month`, `requested`), `403` `account_suspended` and `origin_not_allowed` (a signed URL loaded from a site the key's allowed origins do not list), `429` `account_rate_limited` (the per-account limit across every key) and `account_generation_cap` (the account used its plan's share of today's render budget; cached images keep serving, resets at midnight UTC). `car-image`, `car-image-mcp`, `car-image-sdk` and `car-image-urls` say what to do with each; rate limits are per plan (120 a minute per key on Free and Pro, 600 on Business, 1,200 on Enterprise).
- **Agents never touch a plan.** A `402` of either kind is a question for the human; no skill lets an agent subscribe to, change or cancel a plan, the same rule as buying credits.
- `car-image`: the description no longer offers datasets as a use case; the license does not allow building one.
- `car-image-sdk`: SDK 1.7.0 (`PublicPlan`, `AccountPlanInfo`, `pricing.plans` on `options()`, `data.plan` on `account()`) and CLI 1.6.0 (`car-image options` prints the plans).

## 1.5.0 — 2026-09-17

3D models: own it once, host it anywhere.

- **Own it once.** `create_3d_model` charges 1,000 credits for a vehicle and color the account does not own yet, and nothing for one it already holds a live request for (`billing.already_owned: true`, `credits_charged: 0`), whatever spelling or recipe. `car-3d`, `car-image` and `car-image-sdk` say so wherever they quote the price, so an agent no longer treats a re-order as a second purchase.
- **Hosting.** New core tool `publish_3d_model` (free; `unpublish: true` takes it down) and `publish: true` on `create_3d_model`: `data.public` carries an unguessable `m3d_` id, key-free URLs for the web GLB, the USDZ and the poster on Car Image's CDN, and `embed.html`, a `<script src="https://carimage.dev/embed/3d.js" async>` tag plus `<car-3d model="m3d_…">` to paste into any page. `car-3d` teaches when to publish instead of downloading, the element's attributes (`view`, `spin`, `backdrop`, `ar`, `static`, `no-zoom`, `alt`) and the plain `<model-viewer>` alternative on `GET /api/v1/3d/public/{public_id}`.
- **`glb_web`.** A fifth file kind: the GLB rebuilt for browsers (meshopt, WebP textures, about a tenth of the bytes); what a published model serves.
- `car-image-mcp`: the core toolset is twelve tools, twenty with `?toolset=all`; the tables and the verification steps say so.
- `car-image-sdk`: SDK 1.6.0 (`publish3dModel`, `unpublish3dModel`, `create3dModel({ publish })`, `Model3dPublic`, `glb_web`) and CLI 1.5.0 (`3d publish <id> [--unpublish]`, `3d create --publish`, `--format glb_web`).

## 1.4.0 — 2026-09-16

Any paint, stable vehicle ids, VIN decoding and 3D models.

- **Any paint color.** `color` is one of the 15 presets or any hex (`"#1a2b3c"` in JSON, `color=1a2b3c` in a URL); responses echo `#1a2b3c`, presets their name, and a hex equal to a preset swatch is that preset. Same 1 credit as a preset. Every "fifteen colors" claim in the skills is now "any paint color".
- **Stable vehicle ids.** Every make, model and year has a permanent `veh_…` id; `search_vehicles`, `resolve_vehicle` and `decode_vin` return them, `get_car_image`, `create_car_image_urls` and `create_3d_model` take `vehicle` in place of make, model and year, and every echoed vehicle object opens with `vehicle_id`. `vehicle-catalog` explains when to prefer the id.
- **VIN decoding.** New core tool `decode_vin` (REST `GET /api/v1/vin/{vin}`), free: full or partial VINs to year, make, model, trim, engine, every vPIC attribute and the catalog vehicle id. `vehicle-catalog` covers `valid`, `errors`, `suggested_vin` and what to show next to the image.
- **3D models.** New skill `car-3d` for `create_3d_model` (1,000 credits, charged at creation) and `get_3d_model` (free): the status lifecycle, 3–5 minutes for a first model and 1–2 for another color, polling versus webhooks, verifying `X-CarImage-Signature`, downloading GLB, USDZ, FBX and the thumbnail, and embedding with `<model-viewer>`. `agents/openai.yaml` declares the MCP dependency.
- `car-image-mcp`: the core toolset is eleven tools, nineteen with `?toolset=all`; the tables and the verification steps say so.
- `car-image`: the "Pick the right call" table gains the VIN and 3D rows and the REST list gains the new endpoints; the error reference covers unknown ids, `VIN not recognized`, `3D model not ready` (409) and `model_3d_at_capacity` (503).
- `car-image-sdk`: SDK 1.5.0 (`decodeVin`, `create3dModel`, `get3dModel`, `list3dModels`, `download3dModel`, `vehicle`; `ImageParams.vehicle` and hex `color`) and CLI 1.4.0 (`vin`, `3d create|get|download|list`, `--vehicle`, hex `--color`).

## 1.3.0 — 2026-09-15

The MCP tools now accept what the skills teach.

- **`format: "auto"` over MCP.** `car-image-urls` has shown `format: "auto"` for embeds since 1.2.0, but both MCP servers refused it with a validation error. `create_car_image_urls` now keeps `auto` on the signed URL (each viewer negotiates WebP or PNG per load); `get_car_image` delivers PNG for it, since an inline image has no `Accept` header to negotiate from.
- **`idempotency_key` on `create_car_image_urls`.** The tool-call twin of the REST `Idempotency-Key` header: the same key with the same arguments within 24 hours replays the first result (`idempotent_replayed: true`) instead of minting and billing again; different arguments under the same key are refused; a retry that overtakes a call still running is told to wait. `car-image-urls` and `car-image-mcp` say when to pass one.
- SDK 1.4.0 (`IDEMPOTENCY_KEY_PATTERN`, `inlineImageFormat`, `createImageUrls` reports `idempotent_replayed`), CLI 1.3.0 (the stdio server takes the new inputs).

## 1.2.0 — 2026-09-15

Any box, any background, and a server that only shows the tools you asked for.

- **Sizing contract.** Besides `size` presets and `width`/`height` (1–1024), images take `fit` (`contain` | `cover` | `inside`, default `contain`; `width` + `height` now returns exactly that box instead of a square), `background` (`transparent` default, `white`, `black` or hex; `jpg` defaults to white), `trim` with `padding` 0–50 % (crop to the car before sizing, for non-square layouts) and `format=auto` (WebP or PNG negotiated from `Accept`, per load on a signed URL). `get_car_image` and each `create_car_image_urls` entry take `fit`, `background`, `trim` and `padding`; `create_car_image_urls` honors `renew` and `renew_days`.
- **MCP toolsets.** `https://carimage.dev/api/mcp` exposes the eight core tools; `?toolset=all` (or `car-image mcp --toolset all`) adds the eight request-board tools. `.mcp.json` now connects with `?toolset=all`, because the skills teach `request_vehicle` and friends.
- **Idempotent URL creation.** `POST /api/v1/image-urls` accepts `Idempotency-Key`; the SDK sends one on every `createImageUrls` call and the CLI `url` command takes `--idempotency-key`.
- `car-image-mcp`: documents both toolsets, shows the core URL per host with the `?toolset=all` opt-in, and says what to expect from each when verifying.
- `car-image`, `car-image-urls`, `car-image-sdk`: the sizing options, `format=auto` and the idempotency header; SDK 1.3.0 (`FITS`, `REQUEST_FORMATS`, `MAX_PADDING_PERCENT`, `MCP_TOOLSETS`, `mcpInstructions`) and CLI 1.2.0 (`--fit`, `--background`, `--trim`, `--padding`, `--format auto`, `--idempotency-key`, `mcp --toolset`).
- `vehicle-catalog`: `resolve_vehicle` confidence is `high`, `medium` or `low`, not a number.

## 1.1.0 — 2026-09-11

Ask for what is missing.

- Eight new MCP tools, all free: `list_requests`, `request_vehicle`, `request_feature`, `get_request`, `upvote_request`, `comment_on_request`, `share_building`, `share_referral`.
- `car-image`: the "Pick the right call" table and the REST list cover the request board; a 404 now suggests `request_vehicle`.
- `vehicle-catalog`: when resolve finds no candidates, offer to file the vehicle instead of stopping at "not in the catalog".
- `car-image-mcp`: the tool and cost table lists all sixteen tools.
- `share_building` and `share_referral` answers are private to the Car Image team.

## 1.0.0 — 2026-09-10

First public release.

- Five skills: `car-image`, `car-image-urls`, `vehicle-catalog`, `car-image-sdk`, `car-image-mcp`.
- Hosted MCP server at `https://carimage.dev/api/mcp`, authenticated with `CAR_IMAGE_API_KEY` as a Bearer header.
- Native manifests for Claude Code, Codex and Cursor, plus the vendor-neutral Open Plugins manifest.
- Installable by name: `/plugin marketplace add MeterApp/car-image-plugins` (Claude Code),
  `codex plugin marketplace add MeterApp/car-image-plugins` (Codex),
  `npx skills add MeterApp/car-image-plugins` (skills only, any agent).

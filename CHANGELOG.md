# Changelog

## 1.15.0 — 2026-10-05

- The plugin works before anyone signs in. It now connects a second hosted server, `car-image-catalog` (`https://carimage.dev/api/mcp/catalog`), which needs no account: `resolve_vehicle`, `search_vehicles`, `list_image_options`, `get_pricing` and `describe_api`, plus a new tool, `preview_car_image`, which returns the picture a vehicle's page on carimage.dev already shows, free, with ready-to-paste markdown. Until 1.14.1 every tool sat behind sign-in, so a fresh install could not even look a car up.
- `car-image`: "Before the account is connected". When `create_car_image_urls` is not available, the agent still looks the vehicle up, shows the free preview and says it is one, then offers the exact image and the sign-in: in Claude Code through the `authenticate` tool Claude Code lists for a server that needs sign-in, or `/mcp`. Once the account tools appear it finishes the original request without asking again.
- `vehicle-catalog`, `car-image-mcp` and the README describe the two servers; `car-image-mcp` adds the catalog server to the manual Claude Code setup, the checks and the troubleshooting. The account server, its sign-in and the optional API key are unchanged.

## 1.14.1 — 2026-10-01

- The API refuses again what it cannot read, and the skills say so: a query parameter an image endpoint does not read is a free `400` that names it (`parameter`) and lists the names it reads (`allowed`), because a request served without it was billed for a different image (`angle=rear` used to come back as the default view). `angle`, `camera`, `perspective` and `orientation` now mean `view`, `paint`, `paint_color`, `hex` and `colors` mean `color`, and `bg` and `background_color` mean `background`; only tracking tags and cache busters (`utm_*`, `gclid`, `ref`, `v`, `t`, `_`…) are still ignored and named in `X-Ignored-Parameters`. The `car-image` error table and the `car-image-sdk` skill describe it; the MCP tools are unchanged, their schemas already named every field.

## 1.14.0 — 2026-09-30

- The hosted server's default toolset is now the seven tools an agent needs to look a vehicle up, render it and watch the balance: `resolve_vehicle`, `search_vehicles`, `decode_vin`, `check_vehicles`, `get_car_image`, `create_car_image_urls` and `get_account`. `?toolset=all`, which this plugin configures, still exposes every tool; the skills now say which tools need it (make logos, 3D models, image options, the API reference, pricing, help and billing links).
- The skills no longer teach image feedback or the request board. Both keep working over `?toolset=all` and the API; the dashboard's Recent images card is where a person rates a render now.

## 1.13.0 — 2026-09-30

- New core MCP tool `check_vehicles` (eighteen core tools, twenty-six with `?toolset=all`): checks up to 100 vehicles in one free call, each read exactly as `get_car_image` would read it, and answers every entry as a match with its vehicle id, a suggestion (another vehicle close to it, such as the same model in its nearest year, never a stand-in), a miss or an invalid entry.
- `vehicle-catalog`: "A whole list: check it once", for catalogs, spreadsheets and feeds: check before rendering any of it, store the ids of the matches and render by id, decide the suggestions with the user, skip the misses in every view and color, and compare `distinct_vehicles` with the plan. Longer lists go to code: `car-image check <file>` (CLI 1.11.0) or `client.checkVehicles` (SDK 1.17.0), which split any length.
- `car-image` routes a list to `check_vehicles`; `car-image-sdk` covers `checkVehicles` and the CLI's `check` command; `car-image-mcp` lists and prices the new tool.

## 1.12.2 — 2026-09-30

- The API reads parameters the way people write them, and the skills say so: `width`/`height` for `w`/`h` in a URL, `grey` for `gray` and any CSS color name as a paint or a background (`navy` is `#000080`), view aliases such as `left`, `right` and `front-left`, and names in any case. A size above 1024 is clamped instead of refused (a box keeps its shape; `X-Clamped-Parameters`), and a query parameter the endpoint does not read is ignored and named in `X-Ignored-Parameters`. The `car-image` error table no longer lists an unknown parameter or a dimension above 1024 as a `400`; the SDK and CLI skills describe the looser checks of SDK 1.16.0 and CLI 1.10.0.

## 1.12.1 — 2026-09-30

- The README, `car-image` and `vehicle-catalog` quote the catalog the way the API renders it and carimage.dev/cars lists it: 1,595 makes and 41,838 models. They said 1,607 and 46,120, the database's own ids, which count a make or model that two sources spell differently (MOTO GUZZI, MOTO-GUZZI) twice.
- The README and `vehicle-catalog` link the vehicle pages, one per make, model and model year, and the README gains the Cursor install steps the install page shows.

## 1.12.0 — 2026-09-30

- Claude Code: an optional **Car Image API key** in the plugin's options, for a machine without a browser or a shared service account. Claude Code asks for it when the plugin is enabled (later: `/plugin` → the Car Image plugin → **Configure options**), keeps it in the system's secure credential store and sends it only to the Car Image MCP server, as `X-Api-Key`. Left empty, sign-in works as before: the plugin still sets no `Authorization` header, so OAuth fallback stays on, a signed-in token wins when both are present, and a wrong saved key falls back to browser sign-in. Codex, Cursor and `.mcp.json` are unchanged.
- Nothing in the plugin reads a credential from the machine it runs on any more, in instructions, examples or configuration. The Anthropic Directory held the plugin for review over that ("Uses a credential from the user's machine"): up to 1.10.0 the MCP configuration sent an environment variable, and the skills and the README still showed one read in commands and code. An agent now uses the connection the host authenticated and never handles a key; code for the user's own server leaves the key to the deployment's secrets (`new CarImageClient()`); REST examples are HTTP requests with `cimg_…` standing for the key; the webhook example takes its secret as a parameter; connection checks use free tool calls, or a request with no credential. The validator fails on a key read from an environment variable or a key file, and on any `Authorization` header in an MCP configuration.
- `plugin.json` gives the directory listing a privacy policy, terms and support page (`privacyPolicyUrl`, `termsOfServiceUrl`, `supportUrl`), and the README says what the plugin sends and links the privacy policy.

## 1.11.4 — 2026-09-30

- ChatGPT and Codex now show clickable image links and open the same signed URL in a browser when available, avoiding broken inline previews.
- Claude retains inline images; website and document embeds are unchanged.
- Reuse existing URLs without extra image charges; align both chat skills and their OpenAI prompts.

## 1.11.3 — 2026-09-30

- Both MCP servers read an argument a host sent as text as the type the tool advertises: `"true"` and `"false"` for a flag (`trim`, `renew`, `publish`), a number for a number, and the JSON of a list for `images`. A host that holds no typed schema for a tool (the Claude desktop app with a connector) sends every argument that way, and `create_car_image_urls`, the chat flow since 1.11.1, refused its `images` there: "expected array, received string". What the tools advertise is unchanged. SDK 1.15.0, CLI 1.9.4.
- `car-image` and `car-image-mcp`: the `Input validation error` guidance says so, and keeps the workaround only for a `car-image mcp` server older than CLI 1.9.4.

## 1.11.2 — 2026-09-30

- `car-image`: what `resolve_vehicle` returns is spelled out (`extracted` is what the phrase said, so a `view` or `color` it leaves null is only the default in `params`, not the user's choice; up to five `candidates`). The chat call says what `ttl_seconds: 604800` and `max_uses: 0` mean and that `renew` is left out; the chat frame goes in the `images` entry, and an image with no sizing is a 1024 px square with the car in the middle. "Every angle" is looked up and then asked about before anything is rendered; a comparison's figures are the agent's own words, not catalog data.
- `car-image`: the `Input validation error` row covers a host that sends every argument as text. Numbers are read either way; a refused `trim` or `renew` is left out; and when the `images` list itself is refused as text, the image comes from `get_car_image` instead of a second attempt that cannot succeed.
- `car-image-mcp` and `car-3d`: the end-to-end check and the preview before a 3D model follow the chat flow of 1.11.1 (`create_car_image_urls`, the image in the reply) where they still named `get_car_image`.
- On the server, the same day: `resolve_vehicle` and `search_vehicles` no longer read a make of several words, or a make followed only by filler, a family word or a kind of vehicle, as a model ("mercedes benz", "rolls royce", "smart car", "bmw series" had each resolved to a registry junk row), and an undated "Alfa Romeo Giulia" is the Giulia again.

## 1.11.1 — 2026-09-30

- Show chat images with one signed URL call and inline Markdown in the final reply; reuse existing URLs and avoid duplicate charges for display. Explicit files use the bytes tool.
- Shorten directory metadata, limit example prompts to three and remove pricing from the listing description.

## 1.11.0 — 2026-09-30

Look the vehicle up, then render it by id.

- **Two steps, every time.** `car-image` opens with the workflow a chat needs: `resolve_vehicle` (or `search_vehicles`, or `decode_vin` for a VIN) first, then `get_car_image` with the `vehicle` id it returned. A chat host asked for "a random car" sent Mazda "MX-5 Miata" 2018 straight to `get_car_image` and got a `404`, because the catalog files that car as `mx-5`. The skill says why the lookup is never skipped, how to read its answer (the confidence, a year other than the one asked for, no match) and the one case that needs none: an id already in hand.
- **In a conversation.** `car-image` gains the chat use: a frame that suits a chat (`width: 960, height: 600, trim: true, padding: 8` on a light background), what to say with the image, what to do when no car was named, and a table of what people ask for with the calls and the credits each takes (another angle or paint, every angle, a comparison, a VIN, a make logo).
- `vehicle-catalog` is the lookup the other skills send the agent to: what `resolve_vehicle` reads (a year, a make, a model, a view and a paint) and what it cannot (a description), confidence by example, the year check, and picking a car when none was named. It no longer says the catalog does not separate trims: many variants are catalog models of their own (Civic Type R, M3 Competition, 911 GT3, Corolla Hatchback) and resolve as themselves.
- `car-image-urls`: mint by vehicle id after one lookup per vehicle; an inventory grid from a list of VINs (decode, deduplicate by id, confirm the count, batch by 50); and downloading one fixed image once instead of minting a URL that expires, with what the license says about hosting copies.
- `car-3d`: the order of work (look up, confirm the vehicle and the price, create by id) and a conversation section: publish at creation so the links are ones a person can open, and do not hold a chat for a ten-to-twenty-minute wait.
- `car-image-mcp`: the core table listed twelve of the seventeen tools and said three cost credits; it lists all seventeen, and four cost credits. Adds connecting from a chat app as a connector.
- `car-image-sdk`: resolve once and render by `vehicle` in the SDK, the CLI and the bulk example; the CLI line gains `search`, `3d publish`, `glb_web` and `logo`.
- The make-logo and product-help paragraphs appended to three skills are one short section in each, pointing at `car-image-support`. The marketplace entry says seven skills, not six.
- On the server, the same day: `resolve_vehicle` reads a make and a model by the rules the image tools use, so it names the vehicle they would render (a 2018 "MX-5 Miata" used to resolve to a 1997 car) and keeps a body word the catalog's name carries ("Corolla Hatchback"); `search_vehicles` finds a vehicle named that way when no catalog row carries every word, and every id it returns now names a catalog vehicle (a few did not, where the search had merged two spellings of one car); the image tools read "MX-5 Miata" and "Miata" as the MX-5; and both MCP servers put this workflow, the costs and the `402` rule in the first 2,048 characters of their instructions, which is all some hosts pass to the model. For hosts that pass on less still, a tool result's summary is also the first field of its structured content, and a number sent as text (`width: "960"`) is read as the number. SDK 1.14.0, CLI 1.9.2.

## 1.10.2 — 2026-09-29

- Resolve each vehicle once before expanding views/colors, and skip unchanged catalog misses.
- Document parameter-level image validation and non-retryable errors.

## 1.10.1 — 2026-09-29

- Let the host sign in through OAuth without an API-key environment variable. Remove the static Authorization header that prevented Claude Code directory installs from offering sign-in; retain plugin attribution and all twenty-five tools.
- Update installation and authentication troubleshooting; keep manual API-key and local stdio setup available. Existing plugin users should update, restart their host, and sign in to the Car Image server.

## 1.10.0 — 2026-09-28

- Add get_make_logo to both MCP toolsets and car-image logo to the CLI references.
- Synchronize tool inventories, SDK examples and logo licensing guidance.

## 1.9.0 — 2026-09-28

- Document the prompt-generated make logo REST API and SDK method: one credit per delivery, with trademark and indemnity exclusions.

## 1.8.0 — 2026-09-26

- Add product support, source-linked help, live pricing and browser-confirmed billing links.
- Add car-image-support skill and private missing-context reporting; sixteen core tools and twenty-four with toolset=all.

## 1.7.4 — 2026-09-25

- Identify plugin requests with the declared `X-CarImage-Integration: plugin` header for usage attribution. It contains no user or conversation content.

## 1.7.3 — 2026-09-24

VIN errors.

- `vehicle-catalog` and the `car-image` error reference: a `404` `VIN not recognized` goes back to the user (re-check the VIN, above all the first three characters, the maker code, or decode a partial VIN with `*` and a `year`), never to another decode. NHTSA's data covers vehicles made for the US market, so a correctly typed VIN from another market is a `404` too: find that car by name. The error reference used to send every `404`, this one included, to the catalog search or to `decode_vin`.
- Both MCP servers now append the same step to a `decode_vin` error (SDK 1.10.0, CLI 1.7.5), and a `400`'s detail no longer repeats `Invalid VIN`.

## 1.7.2 — 2026-09-24

The 3D models are built differently.

- `car-3d`: a model is now an unremeshed mesh of about three million triangles with 4k textures and a normal map (`generator: "meshy-7.1"`), so the GLB is about 100 MB and the browser build about 30 MB, while the USDZ and FBX (about 25 MB) are converted from a decimated build of about 300,000 triangles with the same textures; the first model of a vehicle takes ten to twenty minutes, because its source views are rendered and waited for before the mesh is built, and another color one to two. The public JSON carries `front_theta`, the camera angle the car's front is at, which the `<car-3d>` element reads for its presets.

## 1.7.1 — 2026-09-23

Tool counts.

- `car-image-mcp`: the description said "eleven core tools" and the troubleshooting entry for a connection without the request-board tools began "Eleven tools". Both say twelve, the size of the core toolset since `publish_3d_model` joined it in 1.5.0; `?toolset=all` is still twenty.

## 1.7.0 — 2026-09-22

Eight camera angles.

- **Two new views.** `front-3-4-right` and `rear-3-4-right` mirror `front-3-4` and `rear-3-4`, so the views are eight and symmetric, in order around the car: `front`, `front-3-4`, `side`, `rear-3-4`, `rear`, `rear-3-4-right`, `side-right`, `front-3-4-right`. The three left-side angles face left and each `-right` twin faces right; `car-image` says to pick the one that faces into the layout. Same 1 credit, any paint, any size. `front-3-4-left` and `rear-3-4-left` are accepted as aliases, and `resolve_vehicle` reads "front 3/4 right" and "passenger side rear three-quarter".
- `car-3d`: the `<car-3d>` element's `view` takes the same eight names at the image's own yaw; its presets used to open current models from behind.
- `car-image-sdk`: SDK 1.8.0 (`VIEWS`) and CLI 1.7.0 (`--view`, listed in `car-image get --help`).

## 1.6.1 — 2026-09-19

Repricing: $1 buys 100 credits, a 3D model costs 100.

- **A credit is $0.01.** $1 buys 100 credits instead of 1,000, on packs, auto-reload and every plan's overage; packs keep their dollar ladder ($5, $10, $25, $100) and now carry 500, 1,000, 2,500 and 10,000 credits. Purchased credits still never expire and included credits still reset with the plan's month.
- **A 3D model is 100 credits.** `create_3d_model` charges 100 instead of 1,000, so it still costs $1.00 at the new rate, still once per vehicle and color, and is still free for one the account already owns (`billing.already_owned`). Every image is still 1 credit; VIN decoding, the catalog, polling, downloads and publishing stay free.
- Plan prices and allowances are unchanged (Free 100 credits at signup, Pro $29/month with 25,000, Business $99/month with 150,000). `car-image`, `car-3d`, `car-image-mcp`, `car-image-sdk`, the README and `AGENTS.md` restate the new figures wherever they quote a price; SDK 1.7.1 and CLI 1.6.1 carry the constants.

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

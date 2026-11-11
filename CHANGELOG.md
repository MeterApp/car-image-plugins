# Changelog

## 1.34.5 — 2026-11-11

- The hosted MCP endpoint includes all 41 tools at its base URL. Use `?toolset=core` for the twelve core tools.

- Clarifies which MCP tools are available on each connection and how to verify them. Documents the difference between the Git marketplace package and the ChatGPT listing.

## 1.34.4 — 2026-11-11

- The Free plan is one allowance per account, not per month: 30 free vehicle images in total, and once they run out a one-time courtesy of 30 more. Images already received keep serving. The skills, the README and the 402 notes say so (`resets_at` is null on Free's own allowance). Paid plans are unchanged. No tool, scope or sign-in change.

## 1.34.3 — 2026-11-10

- For the Anthropic Directory listing: `plugin.json` sets `documentationUrl` (the docs) and `supportUrl` now names the help center instead of the docs, in step with the Codex manifest. No tool, scope or sign-in change.

## 1.34.2 — 2026-11-06

- For the Anthropic Directory: its credential finding followed the code 1.34.1 moved from `car-image-urls` to `car-image-sdk`, which points at the one line that assigned a literal string to a key field, an `idempotencyKey` in an example. That example now uses the key the SDK generates, and the text says how to choose one. No tool, scope or sign-in change.

## 1.34.1 — 2026-11-06

- For the Anthropic Directory, which refused 1.33.1 and 1.34.0 with LOCAL_CODE_FILE_TYPE: the plugin ships no SVG. `assets/logo.svg` is gone, and the Codex and Cursor manifests use the PNG icon the Claude manifest already names.
- For its MCP_FORWARDS_CREDENTIAL_ENV hold on `car-image-urls`: that skill no longer carries server client code or talks about the account's key. It works from the connected tool and the REST body, and its two code examples moved to `car-image-sdk` (`references/typescript.md`), unchanged. No tool, scope or sign-in change.

## 1.34.0 — 2026-11-06

- Packs: the `car-image-sdk` and `car-image-support` skills describe packs as they are sold now: any quantity from 100, priced per unit by tier; Vehicle Packs (one make, model and year in every view per unit); every pack at the highest quality; 180 days of updates; a large batch can take one to two hours, with a webhook per car and an email when the batch is done. `get_pricing`'s `image_packs.custom` carries the rate card and a Checkout link template.

## 1.33.1 — 2026-11-06

- Route ChatGPT image requests through `create_car_image_urls`, whose hosted MCP result displays the inline image card. Align skill prompts with the card, retain clickable links when it is unavailable, and reuse existing URLs without rendering twice.

## 1.33.0 — 2026-11-05

- Skills and the README state sizes as the API now delivers them: up to the stored image's own size, a 1024 px square for older renders and a view-shaped canvas of up to 2560 px for new ones. They name the new `aspect_ratio` and `resolution` presets for the box, and `padding` without `trim`.

## 1.32.1 — 2026-11-05

- For the Anthropic Directory, which held 1.32.0 with MCP_FORWARDS_CREDENTIAL_ENV ("Uses a credential from the user's machine") on `skills/car-image-urls/SKILL.md`, paired with the MCP servers in `.claude-plugin/plugin.json`. `car-image-urls` was the only skill besides `car-image-sdk` and `car-image-mcp` that carried credential material: it spelled out the `Authorization: Bearer` header of the image endpoint and built a new SDK client, which takes the key from the server's environment. It now describes that endpoint as an authenticated call, and its server examples use the SDK client the application already has (`car-image-sdk` covers setting one up). The MCP servers, tools, scopes and sign-in are unchanged.
- The plugin contact in every manifest is now jonathan@carimage.dev. Support requests still go to support@carimage.dev.

## 1.32.0 — 2026-11-05

- **The plugin does no authentication of its own.** The optional API key setting in Claude Code is gone, and Claude Code's copy of the MCP servers is now identical to `.mcp.json`: a URL and the `X-CarImage-*` attribution headers, nothing else. Every host, Claude Code included, signs you in with your browser through the server's OAuth sign-in, as Codex, Cursor and the Claude and ChatGPT apps already did. The Anthropic Directory held earlier releases for review ("Uses a credential from the user's machine").
- **If you saved a key in the plugin's settings in Claude Code:** after updating, the plugin no longer sends it. Open `/mcp`, select `plugin:car-image:car-image` and sign in with your browser. On a machine with no browser, sign the CLI in with `npx @meterapp/car-image login` and use its local server, or add the hosted server yourself with `claude mcp add` and your key as a header, as [the install page](https://carimage.dev/install?ref=plugin) shows. Your key keeps working for the SDK, the CLI and CI.
- Skills and the README describe sign-in in one way, and say that an API key is created in the dashboard for code and CI and kept as a secret there, with a link to [the authentication docs](https://carimage.dev/docs/authentication?ref=plugin#environment) for how code loads it. No tool or scope change.

## 1.31.4 — 2026-11-05

- Wording only, for the Anthropic Directory review of 1.31.3 (still held as "Uses a credential from the user's machine" on `car-image-urls`): `car-image-urls` now says what `car-image-sdk` says, that the agent does not read credentials from the user's machine and that minting goes through the connected tool or server code whose deployment manages authentication, and its server-component comment uses the same wording as `car-image-sdk`. No tool, scope or sign-in change.

## 1.31.3 — 2026-11-05

- Wording only, for the Anthropic Directory review of 1.31.2 (still held as "Uses a credential from the user's machine" on `car-image-urls`): the server-component example's comment is back to the 1.15.0 wording ("the key stays in the deployment's secrets"), and the fixed-image pattern describes saving the signed URL's file instead of showing a shell download. No tool, scope or sign-in change.

## 1.31.2 — 2026-11-04

- Nothing in the plugin reads a credential from the user's machine, again: the Anthropic Directory held 1.31.1 for review ("Uses a credential from the user's machine"). `car-image-urls` no longer has the agent run the CLI to save a fixed hero image (the CLI signs in with the key its login saved on the machine); it mints one signed URL with `create_car_image_urls` and downloads that, which needs no key. `car-image` and its error reference send a user without a key to the dashboard instead of the CLI login. The plugin's only credential was still the optional key setting, sent only to `https://carimage.dev/api/mcp` (removed in 1.32.0).
- The release validator no longer ships in the plugin: it is a development tool of the source repository, run on every change and before every publish. The mirror's own workflow keeps the install checks. No tool, scope or sign-in change.

## 1.31.1 — 2026-10-30

- Wording: the `car-image` and `car-image-support` descriptions say a plan counts vehicle images, with no mention of the new-view allowance removed in 1.29.0, and the `generation_paused` guidance in `car-image` tells the user that views not prepared yet will be available again shortly. No tool, scope or sign-in change.

## 1.31.0 — 2026-10-29

- A ninth view, `top`: straight down from above, nose up, a bird's-eye plan view for maps, ride-share and fleet apps and parking layouts (aliases `top-down`, `overhead`, `birds-eye`, `aerial`). `car-image`, `car-image-urls`, `car-image-sdk`, `car-image-mcp` and `car-3d` list nine views; local stdio needs SDK 1.38.0 / CLI 1.29.0. No tool, scope or sign-in change.

## 1.30.0 — 2026-10-29

- `get_image_availability` checks prepared/cached views, quality (`standard`, `enhanced`, `premium`, or null), upgrade state and render estimates for free before an image request. Prepared means cached and quick to serve from storage; the check renders, queues and counts nothing. Available in both MCP servers, including the core toolset: twelve core tools, forty-one in all (SDK 1.36.0 / CLI 1.27.0 for local stdio).
- The setup skill distinguishes the marketplace plugin from a curated app snapshot: the registered MCP URL and published tool inventory must both be refreshed in the app publisher portal.


## 1.29.0 — 2026-10-29

- No new-view allowance: a plan counts vehicle images only. A view the catalog has not prepared yet counts as one vehicle image like any other (it still takes a little longer the first time). Free 100 vehicle images a month, Pro 2,500, Business 10,000. `car-image`, `car-image-urls`, `car-image-mcp`, `car-image-sdk` and `car-image-support` drop the `plan_new_view_limit` code, the `X-New-Views-*` headers and `billing.new_views`; the only allowance refusal is `plan_image_limit`. No tool, scope or sign-in change.

## 1.28.0 — 2026-10-29

- Car pictures show inline in chat: `car-image`, `vehicle-catalog` and `car-image-mcp` show a vehicle with `get_car_image`, whose picture a chat app (claude.ai, Claude Desktop) displays inline with the tool result, instead of minting a signed URL. `create_car_image_urls` and the `car-image-urls` skill are for pages, apps, emails and documents, and the fallback where a tool's image does not reach the person (a terminal such as Claude Code or Codex): one URL, linked. The Codex skill prompts say the same. Still one vehicle image per image. No tool, scope or sign-in change.

## 1.27.2 — 2026-10-26

- First images in any view: `car-image` and `car-image-mcp` say a vehicle's first image takes about 25 seconds when it is not the default front-3-4 (the front-3-4 is drawn first and that view from it), and that the front-3-4 is the view redrawn at enhanced quality in the background; a further view of a vehicle already drawn now takes about 15 seconds (drawn in the color asked for, its paint overlay made in the background). No tool, scope or sign-in change.

## 1.27.1 — 2026-10-26

- First images: `car-image`, `car-image-mcp` and `car-image-sdk` say a vehicle's first image (front-3-4, in a color) typically comes back in under 20 seconds at standard quality and that view is redrawn at enhanced quality in the background, usually within a day, at no charge (`image.upgraded` with `reason: "first_view"` on account webhooks); other new views take about 40 seconds and stay standard. No tool, scope or sign-in change.

## 1.27.0 — 2026-10-25

- Vehicle-image plans: a plan counts vehicle images (one vehicle in one color from one view, once per UTC month, delivered as often as needed at any size and format) and, within them, new vehicle views (a view the catalog has not prepared yet, which takes a little time). Free 100 images and 10 new views a month; Pro $49/month 2,500 and 1,000; Business $99/month 10,000 and 4,000. No overage, and credits are no longer sold: they pay only for 3D models (100), make logos (1) and quality upgrades (20). `car-image`, `car-image-urls`, `car-image-mcp` and `car-image-sdk` say what a call counts instead of a credit per image, read `billing.vehicle_images` and the `X-Vehicle-Images-*` headers, and point at `POST /api/v1/images/availability` (free) to check a catalog first; every skill stops on the new `402` codes `plan_image_limit` and `plan_new_view_limit` (and `subscription_required_for_credits`) and hands the human `checkout_url` or `pack_url`. `car-image-support` and `car-3d` drop credit packs; the license is commercial while a paid plan is active, stored copies are deleted within 30 days after it ends, and Image Pack images may be self-hosted for good. Accounts that paid before 2026-10-25 keep their credit meter and terms until the cutover date in their notice. No tool, scope or sign-in change.

## 1.26.0 — 2026-10-23

- Image Packs: `car-image-sdk` covers buying a pack (hand the human the offer's `checkout_url`), sending one batch for a whole list, why it takes a while, the `image.ready` and `pack.batch.completed` webhooks, downloads, the manifest and ZIP exports; `car-image-support` reads the `image_packs` offers `get_pricing` lists for accounts that may buy them. No tool, scope or sign-in change.

## 1.25.0 — 2026-10-22

- Errors: on accounts whose credit top-ups need an active subscription, a `402` for an empty balance carries `code: "subscription_required_for_credits"` with the Pro plan's `checkout_url` and `pack_url` (Image Packs) instead of a credit pack. `car-image` and `car-image-support` say to hand both links to the human and stop; credits already held stay spendable. No tool, scope or sign-in change.

## 1.24.0 — 2026-10-22

- Account webhooks: register an endpoint once and receive signed `image.ready`, `3d_model.ready`/`3d_model.failed` and `image_upgrade.succeeded`/`image_upgrade.failed` events (paid plans; `webhook.test` on every plan). `car-image-sdk` shows `createWebhook` and `verifyWebhook()`, `car-3d` says account endpoints receive 3D events without a `webhook_url`, and `car-image-mcp` lists `list_webhooks` (free, read only, with `?toolset=all`): twenty-one extra tools on `all`, forty in total. The stdio server needs SDK 1.31.0 / CLI 1.22.0.

## 1.23.0 — 2026-10-22

- Anthropic Directory readiness: a 1024 px square listing icon, rendered from the plugin's logo and named by `icon` in the Claude manifest. The README gives the one-step Claude Code install (`/plugin install car-image --marketplace MeterApp/car-image-plugins`) beside the marketplace route, and "What the plugin sends" now names every header and what comes back. The validator checks the icon (square PNG, 512-2048 px, under 2 MB) and refuses symlinks, `.DS_Store` and files of 256 KiB or more. No tool, scope or sign-in change.

## 1.22.0 — 2026-10-19

- Errors: reaching the daily render capacity is now a `503` with `Retry-After` until midnight UTC (`code: generation_at_capacity`), not a `502`; a `502` is always a failed, refunded render. `car-image` and its error reference tell them apart, and SDK 1.28.0 does not retry a `Retry-After` longer than `maxRetryDelayMs`.
- Organizations: `get_account` reports `data.organization` (the organization the connection acts for, with your role), and `list_members` (with `?toolset=all`, free, read only) lists its members and teams. `car-image-mcp` counts twenty extra tools on `all`, thirty-nine in total. The stdio server needs SDK 1.27.0 / CLI 1.20.0.
- The README opens with a link to the product site, carimage.dev.

## 1.21.0 — 2026-10-17

- Feedback tools: `request_feature`, `report_issue`, `upvote_feedback` and `submit_review` are in the default toolset now (eleven core tools), and `list_feedback`, `get_feedback`, `list_my_feedback`, `remove_feedback_vote`, `comment_on_feedback` and `list_reviews` come with `?toolset=all`. `car-image-mcp` lists them; `car-image` and `car-image-support` say when to use them: offer `report_issue` with the failed call's `request_id` after an error that looks like a Car Image bug, `request_feature` when the human wishes the API did something, upvote a similar item instead of filing a duplicate, and a review only in the human's own words.

## 1.20.0 — 2026-10-17

- Agents can pay, within limits the owner sets. `purchase_plan` buys Pro or Business and `pay_invoice` pays an open plan invoice with a Stripe Shared Payment Token (never a card number), only for a key the owner allowed and within the owner's monthly agent spending limit; `checkout_status` polls a hosted Checkout session for agents paying in the browser. `car-image-support` says when to buy and when to hand over the link (dry run first, confirm the amount), and `car-image-mcp` lists the three tools (twenty-nine with `?toolset=all`).

## 1.19.0 — 2026-10-17

- Pricing for agents: `get_pricing` (on the catalog server too, before sign-in) returns every plan's price, limits per tier and features, the credit packs and a `checkout_url` per plan and pack that signs the human in, or up, and opens Stripe Checkout; `get_account` adds usage against each limit (`limits_usage`) and the next plan (`next_plan`). Every 402 carries `checkout_url` and `pricing`. `car-image-support` and the error reference say to hand the human the link with the price, and to buy or change a plan only when the human asks or a spending mandate they set up covers it.

## 1.18.0 — 2026-10-17

- `framing`: a composition preset for images, `consistent` (the default, the camera scale every view of a vehicle shares), `tight` (= `trim` with no margin) or `balanced` (= `trim` with a 6% margin), never together with `trim` or `padding`; same image and credit as the spelled-out form. `car-image` (the sizing table), `car-image-urls`, `car-image-mcp`, `car-image-sdk` and the README list it.

## 1.17.0 — 2026-10-16

- Both MCP servers now send `X-CarImage-Plugin-Version` (this release's version) and `X-CarImage-Plugin-Channel` (`claude-code` from Claude Code's manifest copy, `mcp-json` from `.mcp.json`, which Codex and Cursor read). They name the plugin release and which manifest configured it, nothing about the user, so we can tell which releases are installed and where people stop between install and first use. No tool, scope or sign-in change.

## 1.16.0 — 2026-10-15

- `shadow`: a soft ground shadow under the car, drawn at delivery from the render's own cut-out, same 1 credit. `car-image` (the sizing table), `car-image-urls`, `car-image-mcp`, `car-image-sdk` and the README list it beside `trim` and `padding`.

## 1.15.6 — 2026-10-13

- State the shared default across image, signed URL, SDK, MCP and vehicle lookup skills: Front three-quarter (facing left), `front-3-4` at 35°. Explicitly requested views take precedence.

## 1.15.5 — 2026-10-12

- The catalog server (`car-image-catalog`, no sign-in) now serves `search_help`, so a fresh install can answer pricing, licensing and what-happens-when-a-plan-ends questions from the help center, with sources, before anyone signs in. `car-image-mcp`, `car-image-support` and the README list it.

## 1.15.4 — 2026-10-12

- The license, as the terms say it since 2026-10-12: a render delivered on a paid plan keeps its commercial license after the plan ends, inside the products it was delivered for; new renders, signed URLs and hosted delivery need an active plan. `car-image` and `car-image-support` say so where they quoted the plans, and `car-image-support` points `search_help` at the new articles (what happens when a plan ends, paying once, white-label reuse, hosting choices, matching a vehicle list).

## 1.15.3 — 2026-10-07

- Quote the `car-image` frontmatter description so its embedded colon parses in the skills CLI and all seven skills are discovered.

- `car-image-sdk` is an application integration reference using plain HTTP or an existing SDK dependency. Removed package installation, package-runner, remote shell installer, CLI login and background update instructions, including the CLI reference. The skill explicitly prohibits downloading or executing external code and treats image and model downloads as data. SDK examples remain illustrative server-side code with deployment-managed secrets.
- SDK examples resolve and validate vehicle ids and years before rendering; batches require count and cost confirmation and stop on `402`.

## 1.15.2 — 2026-10-07

- README, "Keep it up to date": how each host keeps the plugin current. Claude Code updates it at startup once auto-update is on for the `meterapp` marketplace (`/plugin` → Marketplaces), which Claude Code leaves off for marketplaces outside Anthropic's; by hand, `/plugin marketplace update meterapp` then `/plugin update car-image@meterapp`. Codex: `codex plugin marketplace upgrade meterapp`; Cursor: `git pull`; skills only: `npx skills update`.
- `car-image-mcp` names `@meterapp/car-image@latest` for the local stdio server: a bare package name lets npx reuse whatever copy it finds, an old global install included, for as long as the configuration lives.
- `car-image-sdk`'s CLI reference: CLI 1.14.0 installs its own new versions in the background, and `car-image update` updates it now and refreshes this plugin in Claude Code and Codex.

## 1.15.1 — 2026-10-05

- `car-image`, "Before the account is connected", from rollouts against the live catalog server: a preview in the view and paint asked for answers the request and is never rendered again for a credit; the account is offered for what a preview cannot do (another view, paint or size, or an image to use in a page, app or document, which carries the plan's license). A preview URL never expires, goes into a terminal as a plain link, and takes `view` and `color` only when the user named them. The `authenticate` link starts on Car Image's sign-in provider (a supabase.co address) and works while the session is open, and the agent says so. Before sign-in a VIN needs the year, make and model it stands for, since `decode_vin` is on the account server. The agent finishes the original request once the user says they have signed in.
- `car-image` says what `get_pricing` already did: buying credits does not grant a commercial license; commercial use requires an active paid plan.

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

- Claude Code: an optional API key setting, for a machine without a browser or a shared service account, sent only to the Car Image MCP server. Left empty, sign-in worked as before. Removed in 1.32.0. Codex, Cursor and `.mcp.json` were unchanged.
- Nothing in the plugin reads a credential from the machine it runs on any more, in instructions, examples or configuration. The Anthropic Directory held the plugin for review over that ("Uses a credential from the user's machine"): up to 1.10.0 the MCP configuration sent a key from the machine, and the skills and the README still showed one being read in commands and code. An agent now uses the connection the host authenticated and never handles a key; code for the user's own server leaves the key to the deployment's secrets (`new CarImageClient()`); REST examples are HTTP requests with `cimg_…` standing for the key; the webhook example takes its secret as a parameter; connection checks use free tool calls, or a request with no credential. The validator fails on a key read from the machine, and on any `Authorization` header in an MCP configuration.
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

- Let the host sign in through OAuth without a key on the machine. Remove the static Authorization header that prevented Claude Code directory installs from offering sign-in; retain plugin attribution and all twenty-five tools.
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
- Hosted MCP server at `https://carimage.dev/api/mcp`, authenticated with an API key as a Bearer header.
- Native manifests for Claude Code, Codex and Cursor, plus the vendor-neutral Open Plugins manifest.
- Installable by name: `/plugin marketplace add MeterApp/car-image-plugins` (Claude Code),
  `codex plugin marketplace add MeterApp/car-image-plugins` (Codex),
  `npx skills add MeterApp/car-image-plugins` (skills only, any agent).

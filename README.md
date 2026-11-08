# Car Image API — plugin for Claude Code, Codex and Cursor

**Website: [carimage.dev](https://carimage.dev)**

Studio-quality, transparent-background renders of any vehicle, wherever your agent works. One repository, native packaging for each client, plus the vendor-neutral [Open Plugins](https://agent-plugins.org) manifest.

Any make, model and year from **1990 to 2027** — 1,608 makes and 42,335 models from the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) catalog, each make, model and year with its own page at [carimage.dev/cars](https://carimage.dev/cars?ref=plugin). Nine camera views (default: Front three-quarter facing left, `view=front-3-4`, 35°), any paint color (15 named presets or any hex), PNG/WebP/JPG up to 2560 px (1024 px for older renders), delivered at any width × height (`fit` contain, cover or inside), transparent or on a solid background, optionally trimmed to the car (or framed by a preset: consistent, tight, balanced) and grounded with a soft shadow. Plus free VIN decoding, stable vehicle ids, and textured 3D models (GLB, USDZ, FBX) of any vehicle in any paint.

**Plans count vehicle images (one vehicle in one color from one view, once a month, delivered as often as needed at any size) · Free 100 a month · Pro $49/mo 2,500 · Business $99/mo 10,000 · no overage · 100 credits per 3D model, once per vehicle and color, hosted for free · VIN decoding free · one-time Image Packs to self-host for good.**


For vehicle images in chat, resolve the vehicle and call `get_car_image` with its id: the host shows the returned picture inline. Where a tool's image does not reach the person (a terminal such as Claude Code or Codex), call `create_car_image_urls` once instead (7-day TTL, unlimited uses, renewal off unless requested) and link the URL. Signed URLs are for pages, apps, emails and documents. Do not call both paid tools for one chat image.

## Install

### Claude Code

In one step:

```text
/plugin install car-image --marketplace MeterApp/car-image-plugins
```

Or add the marketplace first, then install from it:

```text
/plugin marketplace add MeterApp/car-image-plugins
/plugin install car-image@meterapp
```

### Codex

```bash
codex plugin marketplace add MeterApp/car-image-plugins
codex plugin add car-image@meterapp
```

### Cursor

```bash
git clone https://github.com/MeterApp/car-image-plugins.git
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/car-image-plugins" ~/.cursor/plugins/local/car-image
```

Then reload Cursor.

### Skills only, any agent

```bash
npx skills add MeterApp/car-image-plugins
```

### Then sign in, when you want an image

The plugin works before you sign in: its catalog server looks vehicles up and shows the picture a vehicle's page already has, free and with no account. Sign in when you first want an image in the view, paint and size you asked for: your agent opens a Car Image sign-in in the browser and keeps the connection. In Claude Code the agent can start it for you and hand you a link, and `/mcp` (select `plugin:car-image:car-image`) shows the connection and signs in again if needed. Codex, Cursor and the Claude and ChatGPT apps sign in the same way from their connector settings. The plugin itself takes no key.

For scripts, CI and the SDK, create an API key in [the dashboard](https://carimage.dev/dashboard?ref=plugin) and keep it as a secret in that environment; the plugin never uses it. On a machine with no browser at all, connect the server yourself with your key as a header, as [the install page](https://carimage.dev/install?ref=plugin) shows, instead of using the plugin's connection.

Updating from an older release? Update the plugin ([Keep it up to date](#keep-it-up-to-date)) and restart the host before signing in.

Skills-only installs do not configure an MCP connection; follow the `car-image-mcp` setup skill. For SDK, CLI or a host without OAuth, get a key with `npx @meterapp/car-image login` or at [the dashboard](https://carimage.dev/dashboard?ref=plugin) and follow the API-key setup in that skill.

Then try, in a chat:

> "Show me a red 2018 Mazda MX-5 Miata, then the same car from behind."

or in a project:

> "Add a red 2024 Porsche 911 side view to the hero section."

Either way the agent makes two calls per car: a free lookup that turns what you said into the catalog's vehicle and its stable id, then the render by that id. The catalog files cars under its own names (that Miata is `mx-5`), so the lookup is what keeps a name from memory from missing a car the catalog carries.

### Keep it up to date

- **Claude Code** updates the plugin by itself at startup once auto-update is on for its marketplace, which Claude Code leaves off for marketplaces outside Anthropic's: open `/plugin`, go to **Marketplaces**, choose `meterapp` and select **Enable auto-update**. By hand: `/plugin marketplace update meterapp`, then `/plugin update car-image@meterapp`, then restart (or `/reload-plugins`). For an Anthropic Directory install, use the marketplace shown for that install in `/plugin`.
- **Codex:** `codex plugin marketplace upgrade meterapp`.
- **Cursor:** `git -C car-image-plugins pull` in the directory you cloned, then reload Cursor.
- **Skills only:** `npx skills update`.

The CLI, [`@meterapp/car-image`](https://www.npmjs.com/package/@meterapp/car-image), installs its own new versions in the background. `car-image update` updates it now and refreshes this plugin wherever Claude Code or Codex has it installed.

## What you get

Seven skills and two hosted MCP servers: the catalog server, which needs no account, and the account server.

| Skill | Job |
| --- | --- |
| `car-image` | Show or fetch a render: the two steps (look up, then render by id), conversation use, angles, paint and sizing, costs, error handling, make logos |
| `vehicle-catalog` | The lookup that comes first: a name or a VIN → the exact catalog vehicle and its stable id; confidence, years, variants and body styles, offline lookups |
| `car-image-urls` | Signed delivery URLs for pages, emails and documents — no key in the browser; inventory grids from a list of VINs |
| `car-3d` | 3D models (GLB, USDZ, FBX) of any vehicle in any paint: cost, owning it once, waiting, webhooks, publishing and the `<car-3d>` embed |
| `car-image-sdk` | Application code with an existing TypeScript SDK or plain HTTP |
| `car-image-support` | Source-linked product answers, pricing, missing-context reporting and hosted billing links |
| `car-image-mcp` | Connecting over MCP, from an IDE or a chat app, and fixing it when tools do not appear |

The hosted MCP server at `https://carimage.dev/api/mcp` exposes twelve core tools: `resolve_vehicle`, `search_vehicles`, `decode_vin`, `check_vehicles`, `get_car_image`, `create_car_image_urls`, `get_account`, `request_feature`, `report_issue`, `upvote_feedback` and `submit_review`. `get_car_image` costs 1 credit and `create_car_image_urls` 1 credit per URL; the lookups and the account are free. This plugin connects to `https://carimage.dev/api/mcp?toolset=all`, which adds thirteen more: `get_make_logo` (1 credit), `create_3d_model` (100 credits; free once the account owns the vehicle and color), `get_3d_model`, `publish_3d_model`, `list_image_options`, `describe_api`, `get_pricing`, `search_help`, `create_checkout_link`, `get_billing_link`, `checkout_status` (free), `purchase_plan` and `pay_invoice` (charge a payment token, only under the owner's agent spending limit), `list_members` (free, read only) and `list_webhooks` (free, read only) — forty-one tools in all, because the skills teach the extras. When the catalog lacks a vehicle, the agent says so and stops; it never substitutes another car.

The catalog server at `https://carimage.dev/api/mcp/catalog` needs no account and is connected beside it: `resolve_vehicle`, `search_vehicles`, `list_image_options`, `describe_api`, `get_pricing` and `search_help` (the help center: pricing, licensing, what happens when a plan ends), plus `preview_car_image`, which returns the picture a vehicle's page on carimage.dev already shows, free. It never renders or reads an account, so the agent can look a car up, show a preview and explain the API from the first session, and ask you to sign in only for the image you asked for. Once you have signed in, it finishes that request without being asked again.

## Authentication

| Surface | Credential |
| --- | --- |
| Plugin / catalog server | None: it serves nothing that belongs to an account |
| Plugin / hosted MCP | Browser OAuth sign-in; the host stores and refreshes the token |
| MCP you add yourself, without OAuth | A key entered in that host's own MCP settings, sent as an `X-Api-Key` header ([install page](https://carimage.dev/install?ref=plugin)) |
| SDK and CLI | A key your application keeps with its other secrets, or the one `car-image login` stores for the CLI |
| Browsers | **Never a key** — signed delivery URLs only |

The plugin's MCP entries carry a URL and the attribution headers below, nothing else: the host discovers OAuth from the server's sign-in challenge, signs you in with the browser and stores and refreshes the token. For a connection you add yourself with a key, send the key as a header, never in a URL, and keep it out of committed config files.

### What the plugin sends

The plugin runs no local commands or hooks. Its MCP tools call two servers: `https://carimage.dev/api/mcp`, with the token your host got when you signed in, and `https://carimage.dev/api/mcp/catalog`, with no credential; each receives the arguments of its tool calls (vehicle names, VINs, view, color and size options, and the text of any help question, feedback or review you choose to send). The MCP configuration also sends `X-CarImage-Integration: plugin`, `X-CarImage-Plugin-Version` (this release) and `X-CarImage-Plugin-Channel` for usage attribution. These name the integration; they contain no user identity, prompt, or conversation text. What comes back is catalog data, account details (credit balance, plan, usage), signed image URLs on carimage.dev that your host or browser then fetches, and, when you ask for one, a 3D model's files. The calling host may separately identify itself through MCP client information. How Car Image handles this data is in the [privacy policy](https://carimage.dev/privacy?ref=plugin).

## Safety model

- Every vehicle is looked up before it is rendered, and a lookup that is ambiguous, or lands in another year than the one asked for, goes back to the human before anything is rendered.
- A `402` (`plan_image_limit` when the month's vehicle images are used up, `subscription_required_for_credits` when the balance is short for a 3D model, or `plan_vehicle_limit` on an account still on the credit meter) is a question for a human. Agents never buy anything or subscribe to, change or cancel a plan on their own.
- Renders are generated product visuals, not OEM photography. Never claim a specific trim or an individual listed vehicle is depicted exactly.
- A signed delivery URL is unguessable, not access-controlled. Treat it as public for its lifetime.
- Confirm the count and the cost before a batch the user did not size, and before any 3D model (100 credits each, unless the account already owns that vehicle in that color).

## Product help and billing links

Feedback (free): `request_feature`, `report_issue`, `upvote_feedback` and `submit_review` are core tools; `list_feedback`, `get_feedback`, `list_my_feedback`, `remove_feedback_vote`, `comment_on_feedback` and `list_reviews` come with `?toolset=all`. REST: `GET /api/v1/feedback`, `POST /api/v1/feedback/features`, `POST /api/v1/feedback/issues`, `GET /api/v1/feedback/{id}`, `POST`/`DELETE /api/v1/feedback/{id}/votes`, `POST /api/v1/feedback/{id}/comments`, `GET /api/v1/reviews`, `PUT /api/v1/reviews/me`. CLI: `car-image feedback list|show|mine|request|report|upvote|comment`, `car-image review`, `car-image reviews`. After a failure that looks like a Car Image bug, offer `report_issue` with the failed call's `request_id`; when the human wishes the API did something, `request_feature`. Both return `similar` items first and file nothing until `force: true`: upvote a match instead. Issues are private to the reporter and the team. Every new item, upvote, official response and status change is emailed to the people who follow it. Guide: https://carimage.dev/docs/feedback?ref=plugin

Use `search_help` for source-linked product, licensing, policy and Enterprise answers; search each question separately without customer emails or secrets. Use `report_gap: true` when related articles do not answer the question. Queries are recorded privately to improve documentation. `get_pricing` returns current plans and Image Packs; credits are not sold. On the human's request, `create_checkout_link` prepares a purchase and `get_billing_link` opens settings; the human confirms in the browser. Connected apps get a sign-in dashboard link. Never send an owner-account Stripe link to another customer.

CLI: `car-image pricing`, `car-image support "question" [--report-gap]`, `car-image billing --plan pro --no-browser`, `car-image billing --portal`. SDK: `pricing()`, `searchHelp(question)`, `createCheckoutLink({plan: "pro"})`, `getBillingLink()`. The plugin includes the `car-image-support` skill. [Help center](https://carimage.dev/help?ref=plugin).

## Development

```bash
claude plugin validate . --strict
codex plugin marketplace add . --json
```

This repository is published from the Car Image API source. Please open an issue here, or write to [support@carimage.dev](mailto:support@carimage.dev), rather than sending a pull request — changes are overwritten on the next release.

## Links

[Docs](https://carimage.dev/docs?ref=plugin) · [Vehicle pages](https://carimage.dev/cars?ref=plugin) · [Install guide](https://carimage.dev/install?ref=plugin) · [agents.md](https://carimage.dev/agents.md) · [openapi.json](https://carimage.dev/openapi.json) · [Error reference](https://carimage.dev/errors.md) · [Privacy policy](https://carimage.dev/privacy?ref=plugin) · [Terms](https://carimage.dev/terms?ref=plugin) · [support@carimage.dev](mailto:support@carimage.dev)

## License

MIT

`get_image_availability` checks prepared/cached status and quality before generating: resolve the vehicle first, then pass its id, view and color (omit view for all nine). Prepared means quick delivery from storage, with no wait for a new render. The check is free and read-only; it reports `standard`, `enhanced`, `premium` or null plus upgrade state and render estimates, and renders, queues and counts nothing.

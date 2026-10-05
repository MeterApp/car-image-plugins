# Car Image API — plugin for Claude Code, Codex and Cursor

Studio-quality, transparent-background renders of any vehicle, wherever your agent works. One repository, native packaging for each client, plus the vendor-neutral [Open Plugins](https://agent-plugins.org) manifest.

Any make, model and year from **1990 to 2027** — 1,600 makes and 41,975 models from the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) catalog, each make, model and year with its own page at [carimage.dev/cars](https://carimage.dev/cars?ref=plugin). Eight camera views, any paint color (15 named presets or any hex), PNG/WebP/JPG up to 1024 px, delivered at any width × height (`fit` contain, cover or inside), transparent or on a solid background, optionally trimmed to the car. Plus free VIN decoding, stable vehicle ids, and textured 3D models (GLB, USDZ, FBX) of any vehicle in any paint.

**1 credit per image · 100 credits per 3D model, once per vehicle and color, hosted for free · VIN decoding free · Free 100 credits at signup · Pro $29/mo 25,000 credits a month · Business $99/mo 150,000 · $1 per 100 credits beyond the allowance, purchased credits never expire.**


For vehicle images in chat, resolve the vehicle, call `create_car_image_urls` once (7-day TTL, unlimited uses, renewal off unless requested), and paste each returned `data[].markdown` directly in the final reply, outside code fences. State expiry and reuse unexpired URLs. The MCP response includes the same signed URL in `url`; REST responses are unchanged. Use `get_car_image` for explicit file or byte requests. Do not call both paid tools for one chat image. If inline display is unavailable, link the existing URL rather than minting another.

## Install

### Claude Code

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

The plugin works before you sign in: its catalog server looks vehicles up and shows the picture a vehicle's page already has, free and with no account. Sign in when you first want an image in the view, paint and size you asked for. In Claude Code the agent can start it for you and hand you a link, or open `/mcp`, select `plugin:car-image:car-image`, and authenticate in your browser. The plugin uses OAuth: no API key or environment variable is required. Codex and Cursor use their MCP connection controls to sign in.

On a machine without a browser, use an API key instead. Claude Code offers an optional **Car Image API key** field when you enable the plugin: leave it empty for browser sign-in, or paste a key from [the dashboard](https://carimage.dev/dashboard?ref=plugin). To set, change or clear it later, open `/plugin`, select the Car Image plugin, choose **Configure options**, then restart. Claude Code keeps the key in your system's secure credential store and sends it only to the Car Image MCP server.

Updating from an older release? Update the plugin and restart the host before signing in. In Claude Code, run `/plugin marketplace update meterapp`, then `/plugin update car-image@meterapp`. For an Anthropic Directory install, use the marketplace shown for that install in `/plugin`.

Skills-only installs do not configure an MCP connection; follow the `car-image-mcp` setup skill. For SDK, CLI or a host without OAuth, get a key with `npx @meterapp/car-image login` or at [the dashboard](https://carimage.dev/dashboard?ref=plugin) and follow the API-key setup in that skill.

Then try, in a chat:

> "Show me a red 2018 Mazda MX-5 Miata, then the same car from behind."

or in a project:

> "Add a red 2024 Porsche 911 side view to the hero section."

Either way the agent makes two calls per car: a free lookup that turns what you said into the catalog's vehicle and its stable id, then the render by that id. The catalog files cars under its own names (that Miata is `mx-5`), so the lookup is what keeps a name from memory from missing a car the catalog carries.

## What you get

Seven skills and two hosted MCP servers: the catalog server, which needs no account, and the account server.

| Skill | Job |
| --- | --- |
| `car-image` | Show or fetch a render: the two steps (look up, then render by id), conversation use, angles, paint and sizing, costs, error handling, make logos |
| `vehicle-catalog` | The lookup that comes first: a name or a VIN → the exact catalog vehicle and its stable id; confidence, years, variants and body styles, offline lookups |
| `car-image-urls` | Signed delivery URLs for pages, emails and documents — no key in the browser; inventory grids from a list of VINs |
| `car-3d` | 3D models (GLB, USDZ, FBX) of any vehicle in any paint: cost, owning it once, waiting, webhooks, publishing and the `<car-3d>` embed |
| `car-image-sdk` | The TypeScript SDK, the CLI, and plain REST |
| `car-image-support` | Source-linked product answers, pricing, missing-context reporting and hosted billing links |
| `car-image-mcp` | Connecting over MCP, from an IDE or a chat app, and fixing it when tools do not appear |

The hosted MCP server at `https://carimage.dev/api/mcp` exposes seven core tools: `resolve_vehicle`, `search_vehicles`, `decode_vin`, `check_vehicles`, `get_car_image`, `create_car_image_urls` and `get_account`. `get_car_image` costs 1 credit and `create_car_image_urls` 1 credit per URL; the lookups and the account are free. This plugin connects to `https://carimage.dev/api/mcp?toolset=all`, which adds ten more: `get_make_logo` (1 credit), `create_3d_model` (100 credits; free once the account owns the vehicle and color), `get_3d_model`, `publish_3d_model`, `list_image_options`, `describe_api`, `get_pricing`, `search_help`, `create_checkout_link` and `get_billing_link` (free) — twenty-six tools in all, because the skills teach the extras. When the catalog lacks a vehicle, the agent says so and stops; it never substitutes another car.

The catalog server at `https://carimage.dev/api/mcp/catalog` needs no account and is connected beside it: `resolve_vehicle`, `search_vehicles`, `list_image_options`, `describe_api` and `get_pricing`, plus `preview_car_image`, which returns the picture a vehicle's page on carimage.dev already shows, free. It never renders or reads an account, so the agent can look a car up, show a preview and explain the API from the first session, and ask you to sign in only for the image you asked for. Once you have signed in, it finishes that request without being asked again.

## Authentication

| Surface | Credential |
| --- | --- |
| Plugin / catalog server | None: it serves nothing that belongs to an account |
| Plugin / hosted MCP | Browser OAuth sign-in; the host stores and refreshes the token |
| Plugin in Claude Code, optionally | The API key you saved in the plugin's options, kept in your system's secure credential store and sent as `X-Api-Key` |
| Manually configured MCP without OAuth | A key entered in that host's own MCP settings, sent as an `X-Api-Key` or `Authorization: Bearer` header |
| SDK and CLI | A key your application keeps with its other secrets, or the one `car-image login` stores for the CLI |
| Browsers | **Never a key** — signed delivery URLs only |

The plugin never sets an `Authorization` header: Claude Code turns off OAuth fallback when one is configured, so a saved key travels as `X-Api-Key`, and a signed-in token takes precedence when both are present. Nothing in the plugin reads a key from your environment variables or files. For manual API-key connections, send the key as a header, never in a URL, and keep it out of committed config files.

### What the plugin sends

The plugin runs no local commands or hooks. Its MCP tools call two servers: `https://carimage.dev/api/mcp`, with your sign-in token or the key you saved, and `https://carimage.dev/api/mcp/catalog`, with no credential; each receives the arguments of its tool calls. The MCP configuration also sends `X-CarImage-Integration: plugin` for usage attribution. This declares the integration; it contains no user identity, prompt, or conversation text. The calling host may separately identify itself through MCP client information. How Car Image handles this data is in the [privacy policy](https://carimage.dev/privacy?ref=plugin).

## Safety model

- Every vehicle is looked up before it is rendered, and a lookup that is ambiguous, or lands in another year than the one asked for, goes back to the human before a credit is spent.
- A `402` (out of credits, or `plan_vehicle_limit` when the plan's monthly cap on distinct vehicles is reached) is a question for a human. Agents never buy credits or subscribe to, change or cancel a plan on their own.
- Renders are generated product visuals, not OEM photography. Never claim a specific trim or an individual listed vehicle is depicted exactly.
- A signed delivery URL is unguessable, not access-controlled. Treat it as public for its lifetime.
- Confirm the count and the cost before a batch the user did not size, and before any 3D model (100 credits each, unless the account already owns that vehicle in that color).

## Product help and billing links

Use `search_help` for source-linked product, licensing, policy and Enterprise answers; search each question separately without customer emails or secrets. Use `report_gap: true` when related articles do not answer the question. Queries are recorded privately to improve documentation. `get_pricing` returns current plans and packs. On the human's request, `create_checkout_link` prepares a purchase and `get_billing_link` opens settings; the human confirms in the browser. Connected apps get a sign-in dashboard link. Never send an owner-account Stripe link to another customer.

CLI: `car-image pricing`, `car-image support "question" [--report-gap]`, `car-image billing --credits 500 --no-browser`, `car-image billing --plan pro --no-browser`, `car-image billing --portal`. SDK: `pricing()`, `searchHelp(question)`, `createCheckoutLink({credits: 500})`, `getBillingLink()`. The plugin includes the `car-image-support` skill. [Help center](https://carimage.dev/help?ref=plugin).

## Development

```bash
python3 scripts/validate_repo.py
claude plugin validate . --strict
codex plugin marketplace add . --json
```

This repository is published from the Car Image API source. Please open an issue here, or write to [support@carimage.dev](mailto:support@carimage.dev), rather than sending a pull request — changes are overwritten on the next release.

## Links

[Docs](https://carimage.dev/docs?ref=plugin) · [Vehicle pages](https://carimage.dev/cars?ref=plugin) · [Install guide](https://carimage.dev/install?ref=plugin) · [agents.md](https://carimage.dev/agents.md) · [openapi.json](https://carimage.dev/openapi.json) · [Error reference](https://carimage.dev/errors.md) · [Privacy policy](https://carimage.dev/privacy?ref=plugin) · [Terms](https://carimage.dev/terms?ref=plugin) · [support@carimage.dev](mailto:support@carimage.dev)

## License

MIT

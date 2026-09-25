# Car Image API — plugin for Claude Code, Codex and Cursor

Studio-quality, transparent-background renders of any vehicle, wherever your agent works. One repository, native packaging for each client, plus the vendor-neutral [Open Plugins](https://agent-plugins.org) manifest.

Any make, model and year from **1990 to 2027** — 1,607 makes and 46,120 models from the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) catalog. Eight camera views, any paint color (15 named presets or any hex), PNG/WebP/JPG up to 1024 px, delivered at any width × height (`fit` contain, cover or inside), transparent or on a solid background, optionally trimmed to the car. Plus free VIN decoding, stable vehicle ids, and textured 3D models (GLB, USDZ, FBX) of any vehicle in any paint.

**1 credit per image · 100 credits per 3D model, once per vehicle and color, hosted for free · VIN decoding free · Free 100 credits at signup · Pro $29/mo 25,000 credits a month · Business $99/mo 150,000 · $1 per 100 credits beyond the allowance, purchased credits never expire.**

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

### Skills only, any agent

```bash
npx skills add MeterApp/car-image-plugins
```

### Then set your key

```bash
export CAR_IMAGE_API_KEY="cimg_…"
```

Get one with `npx @meterapp/car-image login` (browser device flow) or at [the dashboard](https://carimage.dev/dashboard?ref=plugin). Start a new session, then try:

> "Add a red 2024 Porsche 911 side view to the hero section."

## What you get

Six skills and the hosted MCP server.

| Skill | Job |
| --- | --- |
| `car-image` | Fetch a render; costs, auth, which call to make, error handling |
| `car-image-urls` | Signed delivery URLs for pages, emails and documents — no key in the browser |
| `vehicle-catalog` | Free text or a VIN → exact make, model and year and its stable id; search, disambiguation, offline lookups |
| `car-3d` | 3D models (GLB, USDZ, FBX) of any vehicle in any paint: cost, owning it once, waiting, webhooks, publishing and the `<car-3d>` embed |
| `car-image-sdk` | The TypeScript SDK, the CLI, and plain REST |
| `car-image-mcp` | Connecting over MCP and fixing it when tools do not appear |

The hosted MCP server at `https://carimage.dev/api/mcp` exposes twelve core tools: `get_car_image`, `create_car_image_urls`, `search_vehicles`, `resolve_vehicle`, `decode_vin`, `create_3d_model`, `get_3d_model`, `publish_3d_model`, `list_image_options`, `get_account`, `rate_image` and `describe_api`. `get_car_image` and `create_car_image_urls` cost 1 credit; `create_3d_model` costs 100 (free once the account owns the vehicle and color); the rest are free. This plugin connects to `https://carimage.dev/api/mcp?toolset=all`, which adds the free request-board tools `list_requests`, `request_vehicle`, `request_feature`, `get_request`, `upvote_request` and `comment_on_request`, and `share_building` / `share_referral` for telling the team about yourself (private) — twenty tools in all, because the skills teach them. Missing a vehicle? The agent can file it, and you get an email when it is live.

## Authentication

| Surface | Credential |
| --- | --- |
| Hosted MCP (`/api/mcp`, or `/api/mcp?toolset=all` for the request board) | `Authorization: Bearer $CAR_IMAGE_API_KEY` |
| SDK and CLI | `CAR_IMAGE_API_KEY`, or the key stored by `car-image login` |
| Browsers | **Never a key** — signed delivery URLs only |

The key is sent as a header, never in a URL. Keep it out of committed config files; every manifest here reads `${CAR_IMAGE_API_KEY}` from the environment.

## Safety model

- A `402` (out of credits, or `plan_vehicle_limit` when the plan's monthly cap on distinct vehicles is reached) is a question for a human. Agents never buy credits or subscribe to, change or cancel a plan on their own.
- Renders are generated product visuals, not OEM photography. Never claim a specific trim or an individual listed vehicle is depicted exactly.
- A signed delivery URL is unguessable, not access-controlled. Treat it as public for its lifetime.
- Confirm the count and the cost before a batch the user did not size, and before any 3D model (100 credits each, unless the account already owns that vehicle in that color).

## Development

```bash
python3 scripts/validate_repo.py
claude plugin validate . --strict
codex plugin marketplace add . --json
```

This repository is published from the Car Image API source. Please open an issue here, or write to [support@carimage.dev](mailto:support@carimage.dev), rather than sending a pull request — changes are overwritten on the next release.

## Links

[Docs](https://carimage.dev/docs?ref=plugin) · [Install guide](https://carimage.dev/install?ref=plugin) · [agents.md](https://carimage.dev/agents.md) · [openapi.json](https://carimage.dev/openapi.json) · [Error reference](https://carimage.dev/errors.md) · [support@carimage.dev](mailto:support@carimage.dev)

## License

MIT

The MCP configuration sends `X-CarImage-Integration: plugin` for usage attribution. This declares the integration; it contains no user identity, prompt, or conversation text. The calling host may separately identify itself through MCP client information.

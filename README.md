# Car Image API — plugin for Claude Code, Codex and Cursor

Studio-quality, transparent-background renders of any vehicle, wherever your agent works. One repository, native packaging for each client, plus the vendor-neutral [Open Plugins](https://agent-plugins.org) manifest.

Any make, model and year from **1990 to 2027** — 1,599 makes and 44,254 models from the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) catalog. Six camera views, fifteen colors, PNG/WebP/JPG up to 1024 px.

**1 credit per image · $1 = 1,000 credits · 100 free credits · no subscription.**

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

Five skills and the hosted MCP server.

| Skill | Job |
| --- | --- |
| `car-image` | Fetch a render; costs, auth, which call to make, error handling |
| `car-image-urls` | Signed delivery URLs for pages, emails and documents — no key in the browser |
| `vehicle-catalog` | Free text → exact make, model and year; search, disambiguation, offline lookups |
| `car-image-sdk` | The TypeScript SDK, the CLI, and plain REST |
| `car-image-mcp` | Connecting over MCP and fixing it when tools do not appear |

The MCP server at `https://carimage.dev/api/mcp` provides `get_car_image`, `create_car_image_urls`, `search_vehicles`, `resolve_vehicle`, `list_image_options`, `get_account`, `rate_image` and `describe_api`, plus the free request-board tools `list_requests`, `request_vehicle`, `request_feature`, `get_request`, `upvote_request` and `comment_on_request`, and `share_building` / `share_referral` for telling the team about yourself (private). Only the first two cost credits. Missing a vehicle? The agent can file it, and you get an email when it is live.

## Authentication

| Surface | Credential |
| --- | --- |
| Hosted MCP | `Authorization: Bearer $CAR_IMAGE_API_KEY` |
| SDK and CLI | `CAR_IMAGE_API_KEY`, or the key stored by `car-image login` |
| Browsers | **Never a key** — signed delivery URLs only |

The key is sent as a header, never in a URL. Keep it out of committed config files; every manifest here reads `${CAR_IMAGE_API_KEY}` from the environment.

## Safety model

- A `402` (out of credits) is a question for a human. Agents never buy credits on their own.
- Renders are generated product visuals, not OEM photography. Never claim a specific trim or an individual listed vehicle is depicted exactly.
- A signed delivery URL is unguessable, not access-controlled. Treat it as public for its lifetime.
- Confirm the count and the cost before a batch the user did not size.

## Development

```bash
python3 scripts/validate_repo.py
claude plugin validate . --strict
codex plugin marketplace add . --json
```

This repository is published from the Car Image API source. Please open an issue here, or write to [hello@meterapp.co](mailto:hello@meterapp.co), rather than sending a pull request — changes are overwritten on the next release.

## Links

[Docs](https://carimage.dev/docs?ref=plugin) · [Install guide](https://carimage.dev/install?ref=plugin) · [agents.md](https://carimage.dev/agents.md) · [openapi.json](https://carimage.dev/openapi.json) · [Error reference](https://carimage.dev/errors.md) · [hello@meterapp.co](mailto:hello@meterapp.co)

## License

MIT

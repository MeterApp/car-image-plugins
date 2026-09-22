---
name: car-image-mcp
description: Connect an agent or IDE to the Car Image API over MCP, and fix it when the tools do not appear. Covers the hosted HTTP server and the local stdio alternative, where the CAR_IMAGE_API_KEY goes in Claude Code, Codex, Cursor, Claude Desktop and generic MCP hosts, what each of the eleven core tools costs (images, signed URLs, catalog, VIN decoding, 3D models) and which eight more ?toolset=all adds, and how to diagnose a 401, a missing server or an empty tool list. Use for setup, configuration and connection troubleshooting; do not use for calling the API from code (car-image-sdk) or for image workflows once the tools already work (car-image).
---

# Connecting over MCP

Two servers expose the same tools. Prefer the hosted one — there is nothing to install and nothing to keep up to date.

- **Hosted (recommended):** `https://carimage.dev/api/mcp`, Streamable HTTP, with `Authorization: Bearer $CAR_IMAGE_API_KEY`
- **Local stdio:** `npx @meterapp/car-image mcp`, reads `CAR_IMAGE_API_KEY` or the key stored by `car-image login`

Both come in two toolsets. The default, `core`, is the twelve tools an agent needs to find, render, embed, decode, model and publish a car. Appending `?toolset=all` to the hosted URL — or passing `--toolset all` to `car-image mcp` — adds the eight request-board tools, twenty in total. Fewer tools cost the agent less context and make the right one easier to pick, so opt in only when the agent should also file vehicle and feature requests.

If you installed the `car-image` plugin, the hosted server is already configured with `?toolset=all` (the skills teach the request tools) — skip to [Verifying](#verifying).

## Get a key first

```bash
npx @meterapp/car-image login     # browser device flow, prints the key once
```

Or create one at [the dashboard](https://carimage.dev/dashboard?ref=plugin). Keys look like `cimg_…` and need the `images:read` scope. Then put it in your shell profile so every host can read it:

```bash
export CAR_IMAGE_API_KEY="cimg_…"
```

`car-image agent-config --host claude-code|claude-desktop|cursor|chatgpt|generic` prints the exact configuration for each host below, on the core toolset, with the `?toolset=all` opt-in as a comment.

## Per host

### Claude Code

```bash
claude mcp add --transport http car-image https://carimage.dev/api/mcp \
  --header "Authorization: Bearer $CAR_IMAGE_API_KEY"
```

For the request board too, use `"https://carimage.dev/api/mcp?toolset=all"` as the URL (quote it: the shell would otherwise treat `?` as a glob).

Local stdio instead:

```bash
claude mcp add car-image-local --env CAR_IMAGE_API_KEY="$CAR_IMAGE_API_KEY" -- npx -y @meterapp/car-image mcp
```

Append `--toolset all` after `mcp` for the request board.

### Codex

Install the plugin (`codex plugin add car-image@meterapp`) and the server comes with it, already on `?toolset=all`. Export `CAR_IMAGE_API_KEY` before starting the session, then check `/mcp`.

### Cursor, Claude Desktop, and generic hosts

`.cursor/mcp.json`, or the equivalent config file for your host:

```json
{
  "mcpServers": {
    "car-image": {
      "type": "http",
      "url": "https://carimage.dev/api/mcp",
      "headers": { "Authorization": "Bearer ${CAR_IMAGE_API_KEY}" }
    }
  }
}
```

Set `"url": "https://carimage.dev/api/mcp?toolset=all"` when the agent should have the request-board tools as well.

Most hosts expand `${CAR_IMAGE_API_KEY}` from the environment. **If yours does not, do not paste the literal key into a file you commit** — export it into the host's environment instead, or use the stdio server, which reads the stored key.

## The tools

### Core — every connection has these twelve

| Tool | Costs |
| --- | --- |
| `get_car_image` | 1 credit |
| `create_car_image_urls` | 1 credit per URL |
| `search_vehicles` | free |
| `resolve_vehicle` | free |
| `decode_vin` | free |
| `create_3d_model` | 100 credits; free once the account owns the vehicle and color |
| `get_3d_model` | free |
| `publish_3d_model` | free |
| `list_image_options` | free |
| `get_account` | free |
| `rate_image` | free |
| `describe_api` | free |

Three cost credits. `get_car_image` and `create_car_image_urls` take `vehicle` (a stable `veh_…` id) in place of make, model and year, `color` as a preset or any hex, and `fit`, `background`, `trim` and `padding` alongside width and height, so an agent can ask for exactly the box a layout needs, and `format` accepts `auto` (a signed URL negotiates WebP or PNG per viewer; an inline `get_car_image` delivers PNG for it). `create_car_image_urls` also honors `renew` and `renew_days`, and takes `idempotency_key`: pass one whenever the call might be repeated, because a retry with the same key and arguments replays the first result (`idempotent_replayed: true`) instead of billing again. `resolve_vehicle` reports its confidence as `high`, `medium` or `low` and returns the vehicle id. `decode_vin` turns a full or partial VIN into the catalog vehicle. `create_3d_model` is 100 credits at creation, free for a vehicle and color the account already owns (`billing.already_owned`), and takes `publish`; `get_3d_model` polls it and returns `public` once published; `publish_3d_model` hosts a model at key-free URLs with a two-line `<car-3d>` embed, or takes it down with `unpublish: true` (the `car-3d` skill).

### Request board — eight more with `?toolset=all` or `--toolset all`

| Tool | Costs |
| --- | --- |
| `list_requests` | free, no key needed |
| `request_vehicle` | free |
| `request_feature` | free |
| `get_request` | free, no key needed |
| `upvote_request` | free |
| `comment_on_request` | free |
| `share_building` | free — private to the Car Image team |
| `share_referral` | free — private to the Car Image team |

The request tools file, browse and upvote vehicle and feature requests; `share_building` and `share_referral` tell the team about the user and are never published. Without them, the core server's instructions point a human at [the request board](https://carimage.dev/requests?ref=plugin) instead when a vehicle is missing.

## Verifying

Ask the host to list tools (`/mcp` in Claude Code and Codex). With the bare hosted URL or a plain `car-image mcp` you should see **twelve** tools under `car-image`; with `?toolset=all` (what the plugin ships) or `--toolset all`, **twenty**. Twelve where you expected twenty is not a fault — the URL simply has no `?toolset=all`.

A free end-to-end check that spends nothing:

> "Use list_image_options to show me the available views, colors, fit modes and backgrounds."

Then a real one, which costs 1 credit:

> "Get a front-3/4 image of a 2024 Porsche 911 in red."

From a terminal, without any host:

```bash
curl -sS -X POST https://carimage.dev/api/mcp \
  -H "Authorization: Bearer $CAR_IMAGE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

That returns the twelve core tools, or tells you exactly what is wrong. Use `"https://carimage.dev/api/mcp?toolset=all"` as the URL to see all twenty. `car-image doctor` tests the REST endpoints the same way.

## When it does not work

**No `car-image` server in the list.** The host did not load the config. Restart it — most hosts read MCP configuration only at startup. Check you edited the file the host actually reads (`claude mcp list` shows what Claude Code sees).

**Server listed, zero tools, or a connection error.** Almost always authentication. Run the `curl` above: a `401` problem document means the key is missing, malformed or revoked. Check that `CAR_IMAGE_API_KEY` is exported in the environment the *host* was launched from — a key in `~/.zshrc` is invisible to a GUI app started from the Dock. Log in again with `car-image login` if in doubt.

**Eleven tools, but no `request_vehicle`, `list_requests` or `share_building`.** The connection is on the core toolset, which is working as designed. Change the URL to `https://carimage.dev/api/mcp?toolset=all` (or add `--toolset all` to the stdio command) and restart the host.

**`400 Unknown toolset`.** The query value must be `core` or `all`; anything else is rejected before any tool is listed.

**Tools appear but every call fails with 402.** The account is out of credits (a 3D model needs 100 at once, so it is the usual cause), or the problem carries `code: "plan_vehicle_limit"` and the request named more new distinct vehicles than the plan allows this month (Free 100, Pro 2,500, Business 15,000). Report the balance, or the plan and the cap, and let the human decide; never buy credits or change a plan automatically.

**Calls fail with 403.** The key lacks `images:read`. Create a correctly scoped key.

**Everything is slow the first time.** The first render of a given make/model/year/view/color takes a few seconds; after that it is cached and instant. This is expected, not a connection problem.

**A tool returns 429.** The per-key limit is 120 requests per minute on Free and Pro, 600 on Business and 1,200 on Enterprise, and every account also has a limit across all its keys (`code: "account_rate_limited"`). Wait the `Retry-After` seconds. If a batch job triggers this repeatedly, lower its concurrency. A 429 with `code: "account_generation_cap"` is different: the account has used its plan's share of today's render budget, cached images keep serving, and new renders resume at midnight UTC.

## Keeping the key safe

- Never commit a config file containing a literal key. Use `${CAR_IMAGE_API_KEY}` or the stdio server.
- Never print the key, paste it into a chat, or include it in a screenshot or a bug report. Quote the `request_id` instead.
- A key that has leaked should be revoked in the dashboard and replaced. Revoking also invalidates the signed delivery URLs that key created.

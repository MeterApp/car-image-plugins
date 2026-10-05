---
name: car-image-mcp
description: Connect an agent, IDE or chat app to the Car Image API over MCP, and fix it when the tools do not appear. Covers the hosted HTTP server, the catalog server that needs no sign-in (lookups and free previews), the local stdio alternative, browser OAuth sign-in for plugin installs and chat-app connectors, the optional API key saved in the plugin's options in Claude Code, API-key setup for manual connections in Codex, Cursor, Claude Desktop and generic MCP hosts, what each of the seven core tools costs (catalog lookups, VIN decoding, images, signed URLs, the account) and which ten more ?toolset=all adds (make logos, 3D models, image options, the API reference, pricing, help and billing links), and how to diagnose a 401, a missing server or an empty tool list. Use for setup, configuration and connection troubleshooting; do not use for calling the API from code (car-image-sdk) or for image workflows once the tools already work (car-image).
---

# Connecting over MCP

Two servers expose the same tools. Prefer the hosted one — there is nothing to install and nothing to keep up to date.

- **Hosted (recommended):** `https://carimage.dev/api/mcp`, Streamable HTTP, with browser OAuth sign-in in supported hosts
- **Local stdio:** `npx @meterapp/car-image mcp`, which uses the key `car-image login` saved for the CLI

A third, the **catalog server** at `https://carimage.dev/api/mcp/catalog`, needs no account at all: `resolve_vehicle`, `search_vehicles`, `list_image_options`, `get_pricing` and `describe_api`, plus `preview_car_image`, the picture a vehicle's page on carimage.dev already shows, free. It renders nothing and reads no account, so it never asks anyone to sign in. The plugin connects it next to the hosted server, so an install can look cars up and show previews before the user signs in.

Both come in two toolsets. The default, `core`, is the seven core tools an agent needs to find a vehicle, render it and watch the balance: `resolve_vehicle`, `search_vehicles`, `decode_vin`, `check_vehicles`, `get_car_image`, `create_car_image_urls` and `get_account`. Make logos, 3D models, image options, the API reference, pricing, help and billing links are ten more with `?toolset=all` on the hosted URL or `--toolset all` for `car-image mcp`, twenty-six tools in all. Fewer tools cost the agent less context and make the right one easier to pick, so opt in when the agent should also fetch logos, make 3D models or answer product and billing questions; the plugin does.

## Plugin installs: sign in with your browser

The `car-image` plugin configures two hosted servers: **`car-image-catalog`**, the catalog server, which works at once, and **`car-image`**, the hosted server with `?toolset=all` (the skills teach the logo, 3D, pricing and help tools beyond the core seven), which signs in. **No API key or environment variable is needed.** Sign in when you first want an image: in Claude Code, the agent can start it with the `authenticate` tool Claude Code lists for a server that needs sign-in (`mcp__plugin_car-image_car-image__authenticate`) and hand you the link, or open `/mcp`, select `plugin:car-image:car-image`, and authenticate; complete Car Image sign-in and approve the connection in your browser. Codex and Cursor expose sign-in through their MCP connection controls. Then skip to [Verifying](#verifying).

**Or save an API key (Claude Code, since plugin 1.12.0).** For a machine with no browser, or a shared service account, the plugin takes an optional **Car Image API key**. Claude Code asks for it when the plugin is enabled; to set, change or clear it later, open `/plugin`, select the Car Image plugin, choose **Configure options**, and restart. Recent Claude Code versions also take it from a terminal: `claude plugin configure car-image@meterapp --values-stdin` (for a directory install, use the plugin id `claude plugin list` shows), then type `{"api_key":"cimg_…"}` and end the input with Ctrl-D, which keeps the key out of shell history. Claude Code keeps the key in the system's secure credential store and sends it only to the Car Image server, as the `X-Api-Key` header; left empty, browser sign-in applies. The human enters the key there themselves. Never ask for it in the conversation, and never copy one from environment variables, `.env` files or another tool's config to fill it in.

The plugin never sets an `Authorization` header. Claude Code treats a configured `Authorization` header as the whole credential and turns off OAuth fallback, whatever its value, so a saved key travels as `X-Api-Key` instead, and a signed-in token takes precedence when both are present. Do not add an `Authorization` header to fix a plugin sign-in problem.

Upgrading from a release before 1.10.1? Update the plugin, restart the host, and sign in. If you also added a manual server with an API-key header, use the plugin-provided server; the manual connection still needs its configured key.

## Chat apps: add it as a connector

A chat app that takes remote MCP servers (custom connectors in Claude, connectors or apps in ChatGPT) needs only the URL: `https://carimage.dev/api/mcp`, or `https://carimage.dev/api/mcp?toolset=all` for all twenty-six tools (make logos, 3D models, pricing and help too). The app discovers the sign-in itself (`/.well-known/oauth-protected-resource`), opens Car Image in the browser, and the human approves `images:read` and `account:read` on the consent screen. There is no key to paste, and a connected app can never buy anything: it holds no `billing:write`.

Once connected, a request for a picture of a car is two tool calls: `resolve_vehicle` (free), then `create_car_image_urls` with the id it returned (1 credit); paste the returned `markdown` directly into the final reply. The `car-image` skill has the conversation workflow.

## Manual hosted setup with OAuth

### Claude Code

```bash
claude mcp add --transport http car-image https://carimage.dev/api/mcp
```

Then open `/mcp` and authenticate. Recent Claude Code versions also support `claude mcp login car-image` from a terminal. To have the lookups and previews before signing in, add the catalog server too; it needs no sign-in:

```bash
claude mcp add --transport http car-image-catalog https://carimage.dev/api/mcp/catalog
```

For all twenty-six tools, use `"https://carimage.dev/api/mcp?toolset=all"` as the URL (quote it: the shell would otherwise treat `?` as a glob).

### Other OAuth-capable hosts

Use this in the host’s MCP configuration, such as `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "car-image": {
      "type": "http",
      "url": "https://carimage.dev/api/mcp"
    }
  }
}
```

Sign in using the host’s MCP controls. Set `"url": "https://carimage.dev/api/mcp?toolset=all"` when the agent should also have make logos, 3D models, pricing and help. Codex plugin installs already configure that URL.

## Optional API-key or local stdio setup

For a host without OAuth, or an explicit API-key connection, the human gets a key: `npx @meterapp/car-image login` (a browser device flow; it prints the key once and saves it for the CLI) or [the dashboard](https://carimage.dev/dashboard?ref=plugin). Keys need the `images:read` scope.

- **Claude Code:** save it in the plugin's options, as in [Plugin installs](#plugin-installs-sign-in-with-your-browser). No second server is needed.
- **Another host:** the human enters the key in that host's own MCP settings, as an `X-Api-Key` header (or `Authorization: Bearer`, which some hosts then use instead of OAuth), wherever that host keeps secrets. `car-image agent-config --host claude-code|claude-desktop|cursor|chatgpt|generic` prints the configuration for each host. Never put the key in a project file that gets committed, in a URL or in a prompt, and do not add a key header to the plugin's `.mcp.json`.

Local stdio instead, using the key `car-image login` saved:

```bash
claude mcp add car-image-local -- npx -y @meterapp/car-image mcp
```

Append `--toolset all` after `mcp` for all twenty-six tools.

## The tools

### Core — every connection has these seven

| Tool | Costs |
| --- | --- |
| `resolve_vehicle` | free |
| `search_vehicles` | free |
| `decode_vin` | free |
| `check_vehicles` | free |
| `get_car_image` | 1 credit |
| `create_car_image_urls` | 1 credit per URL |
| `get_account` | free |

Two cost credits. The four lookups come first in the table because they come first in use: `resolve_vehicle` turns what was asked for into the catalog vehicle and its id, with a confidence of `high`, `medium` or `low`; `search_vehicles` lists a make's models and a model's years; `decode_vin` turns a full or partial VIN into the catalog vehicle; `check_vehicles` checks a list of up to 100 at once and answers each entry as a match with its id, a suggestion, a miss or an invalid entry (longer lists: `car-image check <file>` or `client.checkVehicles`). `get_car_image` and `create_car_image_urls` then take `vehicle` (that stable `veh_…` id) in place of make, model and year, `color` as a preset or any hex, and `fit`, `background`, `trim` and `padding` alongside width and height, so an agent can ask for exactly the box a layout needs, and `format` accepts `auto` (a signed URL negotiates WebP or PNG per viewer; an inline `get_car_image` delivers PNG for it). `create_car_image_urls` also honors `renew` and `renew_days`, and takes `idempotency_key`: pass one whenever the call might be repeated, because a retry with the same key and arguments replays the first result (`idempotent_replayed: true`) instead of billing again. `get_account` reports the balance, the plan in force (`data.plan`) and the key's scopes, whichever credential the connection holds.

### Ten more with `?toolset=all` or `--toolset all`

| Tool | Costs |
| --- | --- |
| `get_make_logo` | 1 credit |
| `create_3d_model` | 100 credits; free once the account owns the vehicle and color |
| `get_3d_model` | free |
| `publish_3d_model` | free |
| `list_image_options` | free |
| `describe_api` | free |
| `get_pricing` | free |
| `search_help` | free |
| `create_checkout_link` | free; a link the human completes in the browser |
| `get_billing_link` | free; a link the human completes in the browser |

`get_make_logo` takes a make and the image transforms and returns an inline logo: no model, view or paint, no signed URL and no trademark license. `create_3d_model` is 100 credits at creation, free for a vehicle and color the account already owns (`billing.already_owned`), and takes `publish`; `get_3d_model` polls it and returns `public` once published; `publish_3d_model` hosts a model at key-free URLs with a two-line `<car-3d>` embed, or takes it down with `unpublish: true` (the `car-3d` skill). `list_image_options` lists every valid view, color, size, fit mode, background and format, and `describe_api` explains any REST endpoint from the OpenAPI document. `get_pricing` and `search_help` answer product questions from the published sources, and the two link tools prepare a purchase or open billing settings without charging anything (the `car-image-support` skill). The plugin connects with `?toolset=all`, so its skills can name these; on the bare URL an agent has the core seven, and its instructions tell it to say so and stop when the catalog lacks a vehicle.

## Verifying

Ask the host to list tools (`/mcp` in Claude Code and Codex). With the bare hosted URL or a plain `car-image mcp` you should see **seven** tools under `car-image`; with `?toolset=all` (what the plugin ships) or `--toolset all`, **twenty-six** tools. Seven where you expected twenty-six is not a fault — the URL simply has no `?toolset=all`. A plugin install also shows `car-image-catalog` as connected, with `resolve_vehicle`, `search_vehicles`, `preview_car_image`, `list_image_options`, `get_pricing` and `describe_api`, whether or not anyone has signed in.

A free end-to-end check that spends nothing:

> "Use search_vehicles to list the model years of the Porsche 911."

Then a real one, which costs 1 credit:

> "Show me a red 2024 Porsche 911, front three-quarter."

A working connection answers it in two calls, `resolve_vehicle` and then `create_car_image_urls` with the vehicle id, and the image is in the reply. `get_account` (free) says which account and plan the connection is using, whichever credential it holds.

To check that the server is reachable at all, with no credential, from a terminal:

```bash
curl -sS -i -X POST https://carimage.dev/api/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

A `401` with `WWW-Authenticate: Bearer realm="Car Image API", resource_metadata="…"` is the healthy answer: the server is up and asking for sign-in. Anything `5xx`, or no answer, is an outage. The same request to `https://carimage.dev/api/mcp/catalog` answers `200` with the catalog server's tools, no credential needed. `car-image doctor` tests the REST endpoints with the key the CLI saved.

## When it does not work

**No `car-image` server in the list.** The host did not load the config. Restart it — most hosts read MCP configuration only at startup. Check you edited the file the host actually reads (`claude mcp list` shows what Claude Code sees).

**Plugin needs authentication, zero tools, or a connection error.** Needing authentication is the normal state of `car-image` before the first sign-in; `car-image-catalog` keeps answering lookups and previews meanwhile. Open the host’s MCP controls and sign in. In Claude Code, use `/mcp`, or let the agent call the `authenticate` tool and open the link it gives you. If it says the configured Authorization header was rejected, update the plugin and restart: releases before 1.10.1 required an environment key and prevented OAuth fallback. Check that you selected the plugin server rather than an older manually configured server.

**A key is saved in the plugin's options, and Claude Code still asks for sign-in.** The server refused the key (mistyped, or revoked in the dashboard) and Claude Code fell back to browser sign-in, which is working as designed. Save a current key under `/plugin` → the Car Image plugin → **Configure options**, or clear the field and sign in, then restart.

**A manual API-key connection in another host returns 401.** Check the key in that host's MCP settings; the host must be restarted after it changes. Create a new key in the dashboard if the old one was revoked. An unauthenticated 401 with `WWW-Authenticate: Bearer … resource_metadata="…"` is the normal start of OAuth, not by itself a failed sign-in.

**Seven tools, but no `create_3d_model`, `get_make_logo` or `search_help`.** The connection uses the default toolset, which is working as designed. Add `?toolset=all` to the URL, `https://carimage.dev/api/mcp?toolset=all` (or `--toolset all` to the stdio command), and restart the host.

**`400 Unknown toolset`.** The query value must be `core` or `all`; anything else is rejected before any tool is listed.

**Tools appear but every call fails with 402.** The account is out of credits (a 3D model needs 100 at once, so it is the usual cause), or the problem carries `code: "plan_vehicle_limit"` and the request named more new distinct vehicles than the plan allows this month (Free 100, Pro 2,500, Business 15,000). Report the balance, or the plan and the cap, and let the human decide; never buy credits or change a plan automatically.

**A call fails with `Input validation error`.** The tool refused an argument before the API saw it, and nothing was charged. The message names the argument and the rule. A host that holds no typed schema for a tool sends every argument as text, and both servers read that as it was meant: `"960"` is the number, `"true"` the flag, and the JSON of `images` the list. A `car-image mcp` server older than CLI 1.9.4 refuses a flag or a list sent that way (`expected boolean, received string`; `expected array, received string`): update the CLI.

**A vehicle the catalog has answers `404`.** The agent rendered by a name from memory. It should look the vehicle up first (`resolve_vehicle`) and render by the `vehicle` id; the `car-image` skill has the two steps.

**Calls fail with 403.** The key lacks `images:read`. Create a correctly scoped key.

**Everything is slow the first time.** The first render of a given make/model/year/view/color takes a few seconds; after that it is cached and instant. This is expected, not a connection problem.

**A tool returns 429.** The per-key limit is 120 requests per minute on Free and Pro, 600 on Business and 1,200 on Enterprise, and every account also has a limit across all its keys (`code: "account_rate_limited"`). Wait the `Retry-After` seconds. If a batch job triggers this repeatedly, lower its concurrency. A 429 with `code: "account_generation_cap"` is different: the account has used its plan's share of today's render budget, cached images keep serving, and new renders resume at midnight UTC.

## Keeping the key safe

- A key lives in one of three places: the plugin's options (Claude Code keeps it in the system's secure credential store), the host's own secret storage, or the CLI's login. Never in a config file that gets committed.
- An agent never handles the key. It uses the connection the host already authenticated, and it does not read a key out of environment variables, `.env` files, shell profiles or another tool's config to pass along.
- Never print the key, paste it into a chat, or include it in a screenshot or a bug report. Quote the `request_id` instead.
- A key that has leaked should be revoked in the dashboard and replaced. Revoking also invalidates the signed delivery URLs that key created.


## Product help and billing links

Pricing, licensing and terms questions, and a human's request to buy credits or open billing settings, belong to the `car-image-support` skill (`search_help`, `get_pricing`, `create_checkout_link`, `get_billing_link`). [Help center](https://carimage.dev/help?ref=plugin).

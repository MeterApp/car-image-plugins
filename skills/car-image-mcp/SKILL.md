---
name: car-image-mcp
description: Connect an agent or IDE to the Car Image API over MCP, and fix it when the tools do not appear. Covers the hosted HTTP server and the local stdio alternative, where the CAR_IMAGE_API_KEY goes in Claude Code, Codex, Cursor, Claude Desktop and generic MCP hosts, what each of the eight tools costs, and how to diagnose a 401, a missing server or an empty tool list. Use for setup, configuration and connection troubleshooting; do not use for calling the API from code (car-image-sdk) or for image workflows once the tools already work (car-image).
---

# Connecting over MCP

Two servers expose the same eight tools. Prefer the hosted one — there is nothing to install and nothing to keep up to date.

- **Hosted (recommended):** `https://carimage.dev/api/mcp`, Streamable HTTP, with `Authorization: Bearer $CAR_IMAGE_API_KEY`
- **Local stdio:** `npx @meterapp/car-image mcp`, reads `CAR_IMAGE_API_KEY` or the key stored by `car-image login`

If you installed the `car-image` plugin, the hosted server is already configured — skip to [Verifying](#verifying).

## Get a key first

```bash
npx @meterapp/car-image login     # browser device flow, prints the key once
```

Or create one at [the dashboard](https://carimage.dev/dashboard?ref=plugin). Keys look like `cimg_…` and need the `images:read` scope. Then put it in your shell profile so every host can read it:

```bash
export CAR_IMAGE_API_KEY="cimg_…"
```

`car-image agent-config --host claude-code|claude-desktop|cursor|chatgpt|generic` prints the exact configuration for each host below.

## Per host

### Claude Code

```bash
claude mcp add --transport http car-image https://carimage.dev/api/mcp \
  --header "Authorization: Bearer $CAR_IMAGE_API_KEY"
```

Local stdio instead:

```bash
claude mcp add car-image-local --env CAR_IMAGE_API_KEY="$CAR_IMAGE_API_KEY" -- npx -y @meterapp/car-image mcp
```

### Codex

Install the plugin (`codex plugin add car-image@meterapp`) and the server comes with it. Export `CAR_IMAGE_API_KEY` before starting the session, then check `/mcp`.

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

Most hosts expand `${CAR_IMAGE_API_KEY}` from the environment. **If yours does not, do not paste the literal key into a file you commit** — export it into the host's environment instead, or use the stdio server, which reads the stored key.

## The eight tools

| Tool | Costs |
| --- | --- |
| `get_car_image` | 1 credit |
| `create_car_image_urls` | 1 credit per URL |
| `search_vehicles` | free |
| `resolve_vehicle` | free |
| `list_image_options` | free |
| `get_account` | free |
| `rate_image` | free |
| `describe_api` | free |

## Verifying

Ask the host to list tools (`/mcp` in Claude Code and Codex). You should see all eight under `car-image`.

A free end-to-end check that spends nothing:

> "Use list_image_options to show me the available views and colors."

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

That either returns the tool list or tells you exactly what is wrong. `car-image doctor` tests the REST endpoints the same way.

## When it does not work

**No `car-image` server in the list.** The host did not load the config. Restart it — most hosts read MCP configuration only at startup. Check you edited the file the host actually reads (`claude mcp list` shows what Claude Code sees).

**Server listed, zero tools, or a connection error.** Almost always authentication. Run the `curl` above: a `401` problem document means the key is missing, malformed or revoked. Check that `CAR_IMAGE_API_KEY` is exported in the environment the *host* was launched from — a key in `~/.zshrc` is invisible to a GUI app started from the Dock. Log in again with `car-image login` if in doubt.

**Tools appear but every call fails with 402.** The account is out of credits. Report the balance and let the human top up; never buy credits automatically.

**Calls fail with 403.** The key lacks `images:read`. Create a correctly scoped key.

**Everything is slow the first time.** The first render of a given make/model/year/view/color takes a few seconds; after that it is cached and instant. This is expected, not a connection problem.

**A tool returns 429.** The default limit is 120 requests per minute per key. Wait the `Retry-After` seconds. If a batch job triggers this repeatedly, lower its concurrency.

## Keeping the key safe

- Never commit a config file containing a literal key. Use `${CAR_IMAGE_API_KEY}` or the stdio server.
- Never print the key, paste it into a chat, or include it in a screenshot or a bug report. Quote the `request_id` instead.
- A key that has leaked should be revoked in the dashboard and replaced. Revoking also invalidates the signed delivery URLs that key created.

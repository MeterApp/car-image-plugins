# AGENTS.md — the Car Image cross-agent plugin

One plugin, packaged natively for Claude Code, Codex and Cursor, plus the
vendor-neutral Open Plugins manifest. This directory is the source of truth and
is published verbatim to the public `MeterApp/car-image-plugins` repository,
where these files sit at the repository root. Everything here is customer- and
agent-visible.

## The shape

| Path | Consumed by |
| --- | --- |
| `.claude-plugin/marketplace.json` | `/plugin marketplace add MeterApp/car-image-plugins` |
| `.claude-plugin/plugin.json` | `/plugin install car-image@meterapp`; also the Anthropic Directory listing (privacy, terms and support URLs) and Claude Code's copy of the MCP servers, identical to `.mcp.json` |
| `.agents/plugins/marketplace.json` | `codex plugin marketplace add MeterApp/car-image-plugins` |
| `.codex-plugin/plugin.json` | `codex plugin add car-image@meterapp` (also the directory listing) |
| `.cursor-plugin/plugin.json` | Cursor |
| `.plugin/plugin.json` | Open Plugins, and anything else that reads the portable schema |
| `.mcp.json` | Every client — the hosted server with client-managed OAuth |
| `skills/` | All of the above, and `npx skills add MeterApp/car-image-plugins` |

The marketplace `source` is `"./"`: the repository *is* the plugin. There is no
nested plugin directory, which is why one repository serves all four channels.

## Rules

- **Manifest versions move together.** All four `plugin.json` files carry the
  same `version`, and `CHANGELOG.md` gains a `## <version> ` heading in the same
  commit. The source repository's release validator fails otherwise.
- **Product facts do not drift.** A plan counts vehicle images: one vehicle
  in one color from one view, once per UTC month, delivered as often as
  needed at any size and format; a view the catalog has not prepared yet
  counts as one vehicle image like any other. Free: $0, 100 images a month,
  100 credits once at signup, evaluation and personal projects; Pro
  $49/month: 2,500 images and 1,000 credits a month, a commercial license
  while subscribed (stored copies deleted within 30 days after the plan
  ends); Business $99/month: 10,000 images and 4,000 credits a month;
  Enterprise: custom. No overage (a `402` until the 1st); credits are not
  sold and pay only for 3D models (100 each, charged at creation), make logos
  (1) and quality upgrades (20); one-time Image Packs may be self-hosted for
  good. Accounts that paid before 2026-10-25 keep the credit meter (1 credit
  per image) until the cutover date in their notice. 9 views, any paint color
  (15 named presets or any hex), PNG/WebP/JPG up to 1024 px; stable vehicle
  ids (`veh_…`); VIN decoding free. Prices, plans, allowances and credit
  values change only with a human decision.
- **Every `carimage.dev` link carries `?ref=`.** npm and GitHub strip referrers
  and terminals never had one, so an untagged link is permanently
  unattributable. The bare origin, `/api/*` and the machine-readable files
  (`openapi.json`, `agents.md`, `llms.txt`, `errors.md`, `install.sh`) are
  exempt — callers concatenate those. The validator enforces it.
- **Never link the private server repository.** It 404s for everyone outside the
  org. Link `/docs`, the open catalog, or `support@carimage.dev`.
- **Look up, then render.** Every skill that names a vehicle sends the agent to
  a lookup first (`resolve_vehicle`, `search_vehicles` or `decode_vin`, all
  free) and renders by the `vehicle` id it returns. The catalog files cars
  under its own names, so an example that renders a make and model typed from
  memory teaches a `404`. `car-image` and `vehicle-catalog` carry the workflow;
  the others point at it and show `vehicle` where an agent makes the call.
- **Write for the conversation as well as the codebase.** A chat host loads one
  skill and has no terminal: say which tool shows the result to a person, what
  to tell them, what it costs and when to ask first.
- **Skill frontmatter is `name` and `description` only**, the name matches the
  folder, and the description says both when to use the skill *and* when not to
  — that text is the only thing the model routes on. The validator requires at
  least 120 characters.
- **`agents/openai.yaml` stays in sync with its skill.** Declare the MCP
  dependency only for skills that actually call MCP tools (`car-image`,
  `car-image-urls`, `vehicle-catalog`, `car-3d`, `car-image-support`); the SDK and setup skills must
  not.
- **The plugin does no authentication.** Every MCP entry carries a URL and
  the `X-CarImage-*` attribution headers, nothing else: no plugin settings,
  no key or `Authorization` header, no `${...}` expansion, no `env` block.
  The host discovers OAuth from the server's 401 challenge, signs the person
  in with the browser and manages the token. The Claude manifest's
  `mcpServers` equal `.mcp.json` exactly. Nothing here contains a literal key
  or puts one in a URL or browser code.
- **No file shows a credential being read, not even an example or a denial.**
  The Anthropic Directory holds a plugin for review ("Uses a credential from
  the user's machine") when any shipped text looks like it reads a key from
  the machine and sends it on, and it cannot tell an example or a sentence
  that denies it from real code. An agent uses the connection the host
  authenticated. Keys are for code and CI: a skill may say a key is created in
  the dashboard and kept as a deployment or CI secret, and links to
  `https://carimage.dev/docs/authentication?ref=plugin#environment` for how code loads it. REST
  examples are HTTP requests with `cimg_…` standing for the key; a webhook
  secret is a parameter. Only `car-image-sdk` and `car-image-mcp` show a
  credential header or build an SDK client; every other skill uses the
  connected tools or a client the application already has (1.32.1). No skill has the agent run the CLI for an image, a
  URL or a model: the CLI signs in with its own saved login. A machine with no
  browser connects the server itself with `claude mcp add` and a header, as the
  install page shows; the plugin never repeats that command. The source
  repository's validator enforces all of this.
- **Only what an install uses ships.** Skills, manifests, docs and the listing
  art; no scripts. The release validator and the publish script are
  development tools of the source repository, because the plugin directory
  reads every shipped file as part of the plugin, and a validator full of the
  credential patterns it bans reads as a plugin that uses them.

## Safety

- A `402` is a question for a human. Nothing here may tell an agent to buy
  anything, change a plan, or touch billing on its own.
- Renders are generated product visuals, not OEM photography. No skill may
  suggest claiming a specific trim or an individual listed vehicle is depicted.
- A signed delivery URL is unguessable, not access-controlled. Never describe
  one as private or as a security boundary.
- Batches cost real money. Skills must tell the agent to confirm the count and
  the cost before rendering a batch the user did not size.
- A lookup that is ambiguous, or that answers in another year than the one
  asked for, is a question for the human before anything is rendered. No skill
  may tell an agent to render the nearest vehicle and mention it afterwards.

## Validation

```bash
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
CODEX_HOME="$(mktemp -d)" codex plugin marketplace add . --json
npx -y skills@latest add . --list
```

CI runs all of these on every push, plus a scheduled check that the hosted MCP
URL in `.mcp.json` still answers. The source repository also runs its release
validator on every change and before every publish. `claude plugin validate --strict` needs
Claude Code 2.1.281 or later: earlier releases report the listing URLs in
`plugin.json` (`privacyPolicyUrl`, `termsOfServiceUrl`, `supportUrl`) as
unknown fields.

## Releasing

Changes land in the private source repository and are published from there;
`node scripts/ops/publish-plugins.mjs` mirrors this directory to the public
repository. A pull request opened directly against the published repository
would be overwritten on the next release — redirect contributors to an issue.

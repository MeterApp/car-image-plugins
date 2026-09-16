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
| `.claude-plugin/plugin.json` | `/plugin install car-image@meterapp` |
| `.agents/plugins/marketplace.json` | `codex plugin marketplace add MeterApp/car-image-plugins` |
| `.codex-plugin/plugin.json` | `codex plugin add car-image@meterapp` (also the directory listing) |
| `.cursor-plugin/plugin.json` | Cursor |
| `.plugin/plugin.json` | Open Plugins, and anything else that reads the portable schema |
| `.mcp.json` | Every client — the hosted server plus the Bearer header |
| `skills/` | All of the above, and `npx skills add MeterApp/car-image-plugins` |

The marketplace `source` is `"./"`: the repository *is* the plugin. There is no
nested plugin directory, which is why one repository serves all four channels.

## Rules

- **Manifest versions move together.** All four `plugin.json` files carry the
  same `version`, and `CHANGELOG.md` gains a `## <version> ` heading in the same
  commit. `scripts/validate_repo.py` fails otherwise.
- **Product facts do not drift.** 1 credit per image, $1 = 1,000 credits, 100
  free credits, no subscription; 6 views, any paint color (15 named presets or
  any hex), PNG/WebP/JPG up to 1024 px; stable vehicle ids (`veh_…`); VIN
  decoding free; a 3D model 1,000 credits, charged at creation. Prices and
  credit values change only with a human decision.
- **Every `carimage.dev` link carries `?ref=`.** npm and GitHub strip referrers
  and terminals never had one, so an untagged link is permanently
  unattributable. The bare origin, `/api/*` and the machine-readable files
  (`openapi.json`, `agents.md`, `llms.txt`, `errors.md`, `install.sh`) are
  exempt — callers concatenate those. The validator enforces it.
- **Never link the private server repository.** It 404s for everyone outside the
  org. Link `/docs`, the open catalog, or `hello@meterapp.co`.
- **Skill frontmatter is `name` and `description` only**, the name matches the
  folder, and the description says both when to use the skill *and* when not to
  — that text is the only thing the model routes on. The validator requires at
  least 120 characters.
- **`agents/openai.yaml` stays in sync with its skill.** Declare the MCP
  dependency only for skills that actually call MCP tools (`car-image`,
  `car-image-urls`, `vehicle-catalog`, `car-3d`); the SDK and setup skills must
  not.
- **No key, ever.** Manifests reference `${CAR_IMAGE_API_KEY}`; nothing here
  contains a literal key, and no example puts one in a URL or in browser code.

## Safety

- A `402` is a question for a human. Nothing here may tell an agent to buy
  credits, change a plan, or touch billing on its own.
- Renders are generated product visuals, not OEM photography. No skill may
  suggest claiming a specific trim or an individual listed vehicle is depicted.
- A signed delivery URL is unguessable, not access-controlled. Never describe
  one as private or as a security boundary.
- Batches cost real money. Skills must tell the agent to confirm the count and
  the cost before rendering a batch the user did not size.

## Validation

```bash
python3 scripts/validate_repo.py
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
CODEX_HOME="$(mktemp -d)" codex plugin marketplace add . --json
npx -y skills@latest add . --list
```

CI runs all of these on every push, plus a scheduled check that the hosted MCP
URL in `.mcp.json` still answers.

## Releasing

Changes land in the private source repository and are published from there;
`node scripts/ops/publish-plugins.mjs` mirrors this directory to the public
repository. A pull request opened directly against the published repository
would be overwritten on the next release — redirect contributors to an issue.

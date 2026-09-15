#!/usr/bin/env python3
"""Validate the cross-agent Car Image plugin without modifying anything.

Runs against this directory in the source repository and, unchanged, against
the published `MeterApp/car-image-plugins` repository, where these files sit at
the root. Anything that would break an install — a manifest that drifted out of
sync, a skill missing its Codex interface, a relative path pointing at nothing,
a product fact that contradicts the API — fails here rather than for a user.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

PLUGIN_NAME = "car-image"
MARKETPLACE_NAME = "meterapp"
MCP_URL = "https://carimage.dev/api/mcp"
# The hosted server exposes the eight core tools by default. The skills teach
# the request board too (request_vehicle, upvote_request, ...), so the plugin
# connects with the full toolset; without the query those tools do not exist
# for the agent and the skills would name tools the host cannot see.
PLUGIN_MCP_URL = f"{MCP_URL}?toolset=all"
ORIGIN = "https://carimage.dev"
# The server repository is private: a link there 404s for everyone outside the
# org, and `/plugin marketplace add` of a private repo simply fails. Assembled
# from parts so this file is not itself a violation.
PRIVATE_REPO = "/".join(("MeterApp", "car-image-server"))
PUBLIC_REPO = "https://github.com/MeterApp/car-image-plugins"

SKILLS = ["car-image", "car-image-urls", "vehicle-catalog", "car-image-sdk", "car-image-mcp"]
# Skills that tell the agent to call an MCP tool must declare the dependency so
# Codex can offer to connect the server when the skill is invoked.
MCP_DEPENDENT = {"car-image", "car-image-urls", "vehicle-catalog"}


def error(message: str) -> None:
    ERRORS.append(message)


def load_json(relative: str) -> dict:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{relative}: invalid or unreadable JSON: {exc}")
        return {}


def check_path(owner: str, value: object) -> None:
    """A manifest path must be relative, stay inside the plugin, and exist."""
    if not isinstance(value, str) or not value.startswith("./"):
        error(f"{owner}: expected a ./-prefixed relative path, got {value!r}")
        return
    target = (ROOT / value[2:]).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        error(f"{owner}: path escapes the plugin root")
        return
    if not target.exists():
        error(f"{owner}: referenced path does not exist: {value}")


# --- manifests -------------------------------------------------------------

MANIFESTS = {
    "open": ".plugin/plugin.json",
    "claude": ".claude-plugin/plugin.json",
    "codex": ".codex-plugin/plugin.json",
    "cursor": ".cursor-plugin/plugin.json",
}
manifests = {surface: load_json(path) for surface, path in MANIFESTS.items()}

versions = {surface: manifest.get("version") for surface, manifest in manifests.items()}
if len(set(versions.values())) != 1 or None in versions.values():
    error(f"manifest versions are not synchronized: {versions}")
else:
    version = next(iter(versions.values()))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {version} " not in changelog:
        error(f"CHANGELOG.md has no entry for {version}")

for surface, manifest in manifests.items():
    if manifest.get("name") != PLUGIN_NAME:
        error(f"{surface} manifest name must be {PLUGIN_NAME}")
    if manifest.get("repository") not in (None, PUBLIC_REPO):
        error(f"{surface} manifest repository must be {PUBLIC_REPO}")
    for field in ("skills", "mcpServers", "logo"):
        if isinstance(manifest.get(field), str):
            check_path(f"{surface}.{field}", manifest[field])
    interface = manifest.get("interface", {})
    if isinstance(interface, dict):
        for field in ("composerIcon", "logo", "logoDark"):
            if field in interface:
                check_path(f"{surface}.interface.{field}", interface[field])

# --- marketplaces ----------------------------------------------------------

claude_marketplace = load_json(".claude-plugin/marketplace.json")
if claude_marketplace.get("name") != MARKETPLACE_NAME:
    error(f".claude-plugin/marketplace.json name must be {MARKETPLACE_NAME}")
claude_plugins = claude_marketplace.get("plugins", [])
if len(claude_plugins) != 1 or claude_plugins[0].get("name") != PLUGIN_NAME:
    error(f".claude-plugin/marketplace.json must list exactly one plugin named {PLUGIN_NAME}")
elif claude_plugins[0].get("source") != "./":
    error('.claude-plugin/marketplace.json source must be "./" (the repository is the plugin)')

agents_marketplace = load_json(".agents/plugins/marketplace.json")
if agents_marketplace.get("name") != MARKETPLACE_NAME:
    error(f".agents/plugins/marketplace.json name must be {MARKETPLACE_NAME}")
agents_plugins = agents_marketplace.get("plugins", [])
if len(agents_plugins) != 1 or agents_plugins[0].get("name") != PLUGIN_NAME:
    error(f".agents/plugins/marketplace.json must list exactly one plugin named {PLUGIN_NAME}")

# --- MCP server ------------------------------------------------------------

server = load_json(".mcp.json").get("mcpServers", {}).get(PLUGIN_NAME, {})
expected = {
    "type": "http",
    "url": PLUGIN_MCP_URL,
    "headers": {"Authorization": "Bearer ${CAR_IMAGE_API_KEY}"},
}
if server != expected:
    error(f".mcp.json must configure the hosted server exactly as {expected}, got {server}")

# The setup skill documents both toolsets; a skill that still promises
# "sixteen tools" on the bare URL sends users to a server with eight.
mcp_skill = ROOT / "skills" / "car-image-mcp" / "SKILL.md"
if mcp_skill.is_file():
    mcp_text = mcp_skill.read_text(encoding="utf-8")
    if "?toolset=all" not in mcp_text or "--toolset all" not in mcp_text:
        error("car-image-mcp: must explain ?toolset=all (hosted) and --toolset all (stdio)")
    if re.search(r"same sixteen tools", mcp_text):
        error("car-image-mcp: the bare hosted URL exposes eight core tools, not sixteen")

# --- skills ----------------------------------------------------------------

skills_root = ROOT / "skills"
found = sorted(path.name for path in skills_root.iterdir() if path.is_dir())
if found != sorted(SKILLS):
    error(f"skills/ must contain exactly {sorted(SKILLS)}, found {found}")

frontmatter = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
for name in found:
    skill_dir = skills_root / name
    skill_file = skill_dir / "SKILL.md"
    openai_file = skill_dir / "agents" / "openai.yaml"

    if not skill_file.is_file():
        error(f"{name}: missing SKILL.md")
        continue
    if not openai_file.is_file():
        error(f"{name}: missing agents/openai.yaml")
        continue

    content = skill_file.read_text(encoding="utf-8")
    match = frontmatter.match(content)
    if not match:
        error(f"{name}: invalid YAML frontmatter boundary")
        continue

    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            error(f"{name}: malformed frontmatter line: {line}")
            continue
        metadata[key.strip()] = value.strip().strip("\"'")

    if set(metadata) != {"name", "description"}:
        error(f"{name}: frontmatter must contain only name and description")
    if metadata.get("name") != name:
        error(f"{name}: frontmatter name does not match the folder")
    # A short description is the single biggest cause of a skill never being
    # picked: the model routes on this text alone.
    if len(metadata.get("description", "")) < 120:
        error(f"{name}: description is too short for reliable discovery")

    openai = openai_file.read_text(encoding="utf-8")
    if f"${name}" not in openai:
        error(f"{name}: default_prompt must mention ${name}")
    if name in MCP_DEPENDENT:
        if MCP_URL not in openai:
            error(f"{name}: must declare the hosted MCP dependency")
    elif "dependencies:" in openai:
        error(f"{name}: declares an MCP dependency it does not need")

# --- local links -----------------------------------------------------------

link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for markdown in ROOT.rglob("*.md"):
    if ".git" in markdown.parts:
        continue
    for target in link.findall(markdown.read_text(encoding="utf-8")):
        target = target.strip().strip("<>").split("#", 1)[0]
        if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue
        if not (markdown.parent / target).resolve().exists():
            error(f"{markdown.relative_to(ROOT)}: broken local link {target}")

# --- things that must never ship -------------------------------------------

FORBIDDEN = {
    PRIVATE_REPO: "a link to the private server repository",
    "car-imgs.vercel.app": "the pre-launch deployment URL (use carimage.dev)",
    "cimg_live": "something shaped like a real API key",
    "[TODO": "an unresolved placeholder",
    "carimage.dev/legal": "a legal page that does not exist",
}
# Every published carimage.dev link needs ?ref= for attribution, except the bare
# origin (callers concatenate it), the API itself, and machine-readable files.
REF_EXEMPT = re.compile(
    rf"{re.escape(ORIGIN)}(?:/(?:api/|openapi\.json|errors\.md|agents\.md|llms(?:-full)?\.txt|install\.sh)|[\s\"'`)\],]|$)"
)

for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or ".git" in path.parts or path.suffix in {".svg", ".pyc"}:
        continue
    if path.resolve() == Path(__file__).resolve():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    relative = path.relative_to(ROOT)
    for needle, label in FORBIDDEN.items():
        if needle in text:
            error(f"{relative}: contains {label}: {needle}")
    for match in re.finditer(re.escape(ORIGIN) + r"[^\s\"'`)\],]*", text):
        url = match.group(0)
        if "?ref=" in url or REF_EXEMPT.match(url):
            continue
        error(f"{relative}: carimage.dev link without ?ref=: {url}")

if ERRORS:
    print("Plugin validation failed:", file=sys.stderr)
    for item in ERRORS:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

print(f"Plugin validation passed: {len(manifests)} manifests, {len(found)} skills")

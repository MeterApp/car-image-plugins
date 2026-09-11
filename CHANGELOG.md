# Changelog

## 1.1.0 — 2026-09-11

Ask for what is missing.

- Eight new MCP tools, all free: `list_requests`, `request_vehicle`, `request_feature`, `get_request`, `upvote_request`, `comment_on_request`, `share_building`, `share_referral`.
- `car-image`: the "Pick the right call" table and the REST list cover the request board; a 404 now suggests `request_vehicle`.
- `vehicle-catalog`: when resolve finds no candidates, offer to file the vehicle instead of stopping at "not in the catalog".
- `car-image-mcp`: the tool and cost table lists all sixteen tools.
- `share_building` and `share_referral` answers are private to the Car Image team.

## 1.0.0 — 2026-09-10

First public release.

- Five skills: `car-image`, `car-image-urls`, `vehicle-catalog`, `car-image-sdk`, `car-image-mcp`.
- Hosted MCP server at `https://carimage.dev/api/mcp`, authenticated with `CAR_IMAGE_API_KEY` as a Bearer header.
- Native manifests for Claude Code, Codex and Cursor, plus the vendor-neutral Open Plugins manifest.
- Installable by name: `/plugin marketplace add MeterApp/car-image-plugins` (Claude Code),
  `codex plugin marketplace add MeterApp/car-image-plugins` (Codex),
  `npx skills add MeterApp/car-image-plugins` (skills only, any agent).

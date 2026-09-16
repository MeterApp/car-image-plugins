---
name: vehicle-catalog
description: Turn a vague vehicle reference ("that blue BMW wagon", "a mid-2000s Civic") or a VIN into an exact make, model and year the Car Image API can render, and into the stable vehicle id (veh_…) that names it; or check what a make offers and which years exist. Covers resolve, fuzzy search, free VIN decoding (full or partial VINs), vehicle ids, disambiguating trims and body styles, and the open @meterapp/vehicle-db package for offline lookups, dropdowns and validation. Use before rendering when the request is free text or a VIN, or when building a vehicle picker or validating user input; do not use for fetching the image itself (car-image), embedding it in a page (car-image-urls) or making a 3D model (car-3d).
---

# Finding the right vehicle

Renders are addressed by **make, model, year** — or by the one **vehicle id** that stands for the three. Getting them right before you render matters, because a render of the wrong car still costs a credit, and a 3D model of the wrong car costs a thousand.

The catalog is the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) — 1,599 makes and 44,254 models across model years 1990-2027, built from public sources (NHTSA vPIC, UK DfT/DVLA, NZTA, Malaysia JPJ and others). It covers cars, motorcycles, trucks, buses, MPVs and more, internationally — not just the US market.

All the lookups below are **free**. Use them liberally.

## Vehicle ids

Every make, model and year in the catalog has an id such as `veh_395yw8tn73ff8` (the 2023 Ford F-150): `veh_` plus 13 characters, deterministic and permanent. `search_vehicles`, `resolve_vehicle` and `decode_vin` all return them, and every image endpoint, signed-URL item, 3D request and MCP tool accepts `vehicle: "veh_…"` in place of `make`, `model` and `year` (both together is a `400`; an unknown id is a `404`). Every echoed vehicle object opens with `vehicle_id`.

Prefer the id once you have one: it cannot be misspelled, it survives catalog releases, and it is what to store in the user's database. `GET /api/v1/vehicles/{id}` (public, free) turns an id back into its make, model, year, every year of the model, and ready-made image paths.

## Free text in, parameters out

`resolve_vehicle` (REST: `POST /api/v1/images/resolve`) takes a phrase and returns `params` (with `vehicle_id`), `candidates` and a `confidence` of `high`, `medium` or `low`.

```
"red 2024 porsche 911 side view"
  → params: { vehicle_id: "veh_78qtwrgh37bkr", make: "porsche", model: "911", year: 2024, view: "side", color: "red" }
    confidence: "high"
```

It reads the view and color out of the phrase too (a hex such as `#1a2b3c` is kept as a hex paint), so you usually do not need to parse anything yourself.

**Act on confidence:**

- **`high`, one clear candidate** — go ahead and render.
- **`medium`** — render, but say in one line which vehicle you chose and why, so the user can correct you before the next credit.
- **`low`, or several candidates that all fit** — show the candidates and ask. Do not guess. "Civic" spans 1990 to 2027; "Mustang" could be a 1994 or a 2024; "911" has many generations.
- **No candidates** — the vehicle is not in the catalog. Say so plainly, then offer to file it with `request_vehicle` (make, model, optional year and a note). It is free; the team adds requested vehicles and emails the user when it is live, and if someone already asked, the call upvotes their request instead. Do not substitute a similar car without telling the user.

## A VIN in, the vehicle out

`decode_vin` (REST: `GET /api/v1/vin/{vin}?year=`) decodes a full 17-character VIN, or a partial one with `*` for each unknown position (5–17 characters), with NHTSA's vPIC data, and names the catalog vehicle it maps to. Free.

```
"1HGCM82633A004352"
  → year: 2003, make: "Honda", model: "Accord", trim: "EX-V6", body_class: "Coupe", valid: true
    vehicle: { id: "veh_3qfyk22gfhsx3", make: "honda", model: "accord", year: 2003, image_path: "/api/v1/images/car?vehicle=veh_3qfyk22gfhsx3" }
```

- Render with `vehicle: vehicle.id` (or `vehicle.image_path`); no spelling to get right.
- `valid: false` with `errors: [{code, text}]` means vPIC found a problem (a bad check digit, an invalid character) but still decoded what it could; `suggested_vin` is its corrected spelling when it can tell. Show the errors; still use the vehicle when there is one.
- `vehicle` is `null` when the decoded make and model are not in the catalog (a trailer, a commercial chassis). Say so and offer `request_vehicle`; the decoded fields (`attributes` carries every vPIC variable) are still worth showing.
- The catalog keys on make, model and year: show the decoded `trim`, `body_class` and `engine` next to the image rather than claiming the render depicts them.
- Pass `year` when you know it: the tenth VIN character encodes the year in a 30-year cycle, and a hint helps a partial VIN.
- A `400` is not a VIN (length, an I, O or Q); a `404` is a pattern NHTSA does not know. Ask the user to check the characters rather than guessing.

## Searching and listing

`search_vehicles` (REST: `GET /api/v1/vehicles?q=`) fuzzy-matches makes and models with typo tolerance and returns canonical names plus the years available for each, with a vehicle id per year (`ids`) and `id` when the query names a single year.

Use it to:

- **Confirm a vehicle exists** before spending a credit.
- **List a make's models** — search the make, read the models back.
- **Find valid years** — the response tells you which model years exist, so you never request one that does not, and hands you the id of each.
- **Recover from a 404** — if a render returned 404, search for the canonical spelling.

The catalog's spelling wins. If a user says "Mercedes", the catalog may hold "Mercedes-Benz"; if they say "VW", it may be "Volkswagen". Pass the canonical name back to the render call.

## Disambiguating like a human would

The catalog keys on make, model and year. It does not model trims, engines, or most body-style variants.

- **Trim is not a parameter.** "Civic Si", "M3 Competition", "F-150 Raptor" — render the base model and say which vehicle the image represents. Do not claim the image shows the trim.
- **Body style sometimes lives in the model name.** "3 Series Touring", "Golf Estate". Search for it; if the catalog has a distinct model, use it. If not, use the base model.
- **Year means model year.** "A 2023 car bought in 2022" is a 2023. When someone says "a mid-2000s Civic", offer a specific year rather than picking one silently.
- **Generation talk needs a year.** "992 911", "E90 M3", "Mk7 Golf" — map it to a model year, and confirm if you are unsure.
- **Regional names differ.** The same car can be a Corolla in one market and something else in another. Search rather than assuming.

## Offline: the npm package

For a vehicle picker, a validation rule, or anything that should not make a network call per keystroke, install the catalog directly:

```bash
npm install @meterapp/vehicle-db
```

It is open source, has no runtime dependencies, and ships the full make/model/year data. Use it to populate cascading dropdowns (make → model → year), validate a form before submitting, or pre-check that a vehicle exists before calling the API. Then pass the values you selected straight to the render call — they are already canonical.

This is the right choice when you need instant filtering, offline behavior, or hundreds of lookups. Use `search_vehicles` when you want fuzzy matching and typo tolerance over free text.

## Telling the user what you did

When you resolved something ambiguous, say so in one line: "Rendering the 2024 Porsche 911 (base model) — there are also Turbo and GT3 variants the catalog doesn't separate." That is the difference between a user trusting the image and being surprised by it.

If the catalog does not have the vehicle, say that rather than rendering the nearest thing, and offer `request_vehicle` so the gap gets closed. A silently substituted car is worse than no image.

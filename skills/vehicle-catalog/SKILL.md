---
name: vehicle-catalog
description: Turn a vague vehicle reference ("that blue BMW wagon", "a mid-2000s Civic") into an exact make, model and year the Car Image API can render, or check what a make offers and which years exist. Covers resolve, fuzzy search, disambiguating trims and body styles, and the open @meterapp/vehicle-db package for offline lookups, dropdowns and validation. Use before rendering when the request is free text, or when building a vehicle picker or validating user input; do not use for fetching the image itself (car-image) or embedding it in a page (car-image-urls).
---

# Finding the right vehicle

Renders are addressed by exactly three things: **make, model, year**. Getting them right before you render matters, because a render of the wrong car still costs a credit.

The catalog is the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) — 1,599 makes and 44,254 models across model years 1990-2027, built from public sources (NHTSA vPIC, UK DfT/DVLA, NZTA, Malaysia JPJ and others). It covers cars, motorcycles, trucks, buses, MPVs and more, internationally — not just the US market.

Both lookups below are **free**. Use them liberally.

## Free text in, parameters out

`resolve_vehicle` (REST: `POST /api/v1/images/resolve`) takes a phrase and returns `params`, `candidates` and a `confidence` between 0 and 1.

```
"red 2024 porsche 911 side view"
  → params: { make: "Porsche", model: "911", year: 2024, view: "side", color: "red" }
    confidence: 0.97
```

It reads the view and color out of the phrase too, so you usually do not need to parse anything yourself.

**Act on confidence:**

- **High, one clear candidate** — go ahead and render.
- **Low, or several candidates that all fit** — show the candidates and ask. Do not guess. "Civic" spans 1990 to 2027; "Mustang" could be a 1994 or a 2024; "911" has many generations.
- **No candidates** — the vehicle is not in the catalog. Say so plainly. Do not substitute a similar car without telling the user.

## Searching and listing

`search_vehicles` (REST: `GET /api/v1/vehicles?q=`) fuzzy-matches makes and models with typo tolerance and returns canonical names plus the years available for each.

Use it to:

- **Confirm a vehicle exists** before spending a credit.
- **List a make's models** — search the make, read the models back.
- **Find valid years** — the response tells you which model years exist, so you never request one that does not.
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

If the catalog does not have the vehicle, say that rather than rendering the nearest thing. A silently substituted car is worse than no image.

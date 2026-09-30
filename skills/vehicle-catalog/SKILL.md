---
name: vehicle-catalog
description: Look a vehicle up before it is rendered - turn what someone asked for ("a 2018 Miata", "the new 911 GT3", a VIN) into the exact catalog make, model and year the Car Image API can render and the stable vehicle id (veh_…) that names it, or check what a make offers and which years exist. Covers resolve_vehicle, search_vehicles and free VIN decoding (full or partial VINs), reading confidence and year mismatches, trims and body styles, picking a car when none was named, missing vehicles, and the open @meterapp/vehicle-db package for offline lookups, dropdowns and validation. Use first, before any image, signed URL or 3D model of a vehicle, and when building a vehicle picker or validating user input; do not use for fetching the image itself (car-image), embedding it in a page (car-image-urls) or making a 3D model (car-3d).
---

# Finding the right vehicle

Renders are addressed by **make, model, year** — or by the one **vehicle id** that stands for the three. The lookup comes first, every time: the catalog files cars under its own names, a render of the wrong car still costs a credit, and a 3D model of the wrong car costs a hundred.

The catalog is the open [`@meterapp/vehicle-db`](https://github.com/MeterApp/vehicle-db) — 1,607 makes and 46,120 models across model years 1990-2027, built from public sources (NHTSA vPIC, UK DfT/DVLA, NZTA, Malaysia JPJ and others). It covers cars, motorcycles, trucks, buses, MPVs and more, internationally — not just the US market.

All the lookups below are **free**. Use them liberally.

## Look up, then hand over the id

| You have | Call | Take |
| --- | --- | --- |
| A car named in words ("2018 Mazda MX-5 Miata") | `resolve_vehicle({ query })` | `params.vehicle_id`, plus `params.view` and `params.color` |
| A VIN, full or partial | `decode_vin({ vin, year? })` | `vehicle.id` |
| A make, and a question about what it offers | `search_vehicles({ query, year?, limit? })` | `id` (the year the query names) or `ids` by year |
| Nothing named ("a random car", "something sporty") | choose a year, make and model yourself, then `resolve_vehicle`; name your pick in the reply | as above |

Then render with the id: `create_car_image_urls` with the id, view and color in its `images` array for chat (paste the returned Markdown inline), a page or document (`car-image-urls`); `get_car_image({ vehicle, view, color })` for explicit files or bytes, `create_3d_model` for a model (`car-3d`). One lookup serves every view, paint and size of that car.

## Words in, a vehicle out

`resolve_vehicle` (REST: `POST /api/v1/images/resolve`) takes a phrase and returns `params` (with `vehicle_id`), `display`, `candidates`, `confidence` (`high`, `medium` or `low`) and `extracted`, what it read out of the phrase.

```
"red 2018 Mazda MX-5 Miata, side view"
  → params: { vehicle_id: "veh_59854qbgfvar3", make: "mazda", model: "mx-5", year: 2018, view: "side", color: "red" }
    confidence: "high", extracted: { year: 2018, color: "red", view: "side" }
```

It is deterministic, with no model behind it, so write the phrase it can read:

- **Year, make, model.** The make first, then the model, is read by the rules the image endpoints read them with, so the answer is the vehicle a render would serve. Give the make whenever you know it: "mustang" alone is a guess among every make's Mustang, "ford mustang" is not.
- **A view and a paint, if the user named them.** "side", "from behind", "front 3/4", "three-quarter view", "rear three quarter right"; a preset, a hex such as `#1a2b3c`, or a paint word (navy, charcoal, cream) that maps onto a preset. You do not need to parse these yourself.
- **Nothing else.** A description is not a name. "That blue BMW wagon", "a mid-2000s Civic", "the electric one", "the new shape" do not resolve: turn them into a year, make and model first, and when you cannot tell which car is meant, ask. "A mid-2000s Civic" becomes "2005 Honda Civic", offered to the user, not picked silently.
- **Put the model year in.** Without one the answer is the model's latest catalog year, which can be next year's car. When the user gave no year, choose one and say which.

**Act on what comes back**, in this order:

- **`params.year` differs from `extracted.year`** — the catalog has no model of that name in the year the user asked for, and the answer is another year of it. Do not render it. First check whether the car is filed under another name that year: `search_vehicles` with the make, the model family and `year` ("Mazda MX-5", 2018). If that finds it, use that id and say which catalog model it is; if not, say the catalog lacks that model year, offer the year it has, and ask.
- **`low`** — a guess. Show the candidates and ask. Do not render.
- **`medium`** — an interpretation: a badge read as its family, trim words set aside, a body the catalog has no separate model for ("Civic hatchback" answered with the Civic), or a model name several makes use with no make given. Render, and say in one line which vehicle it is.
- **`high`** — the name the catalog uses, or a reviewed name for the same car (a 2018 "MX-5 Miata" is `mx-5`, a "GR Supra" is `supra`), in the year asked for. Render.
- **No match** — not yet a missing vehicle. Drop everything but the year, make and model and try again, or call `search_vehicles` with the model family alone. When the catalog really lacks it, say so plainly and offer to file it with `request_vehicle` (make, model, optional year and a note). It is free; the team adds requested vehicles and emails the user when it is live, and if someone already asked, the call upvotes their request instead. Do not substitute a similar car without telling the user.

`candidates` lists what else the phrase could be: for a vehicle named with its make, the nameplate's other variants that year (the 911 Carrera and GT3 next to the 911). Offer them when the user may have meant one ("Civic" covers a dozen bodies across four decades), and never treat them as a reason to stall a `high` match.

## Vehicle ids

Every make, model and year in the catalog has an id such as `veh_395yw8tn73ff8` (the 2023 Ford F-150): `veh_` plus 13 characters, deterministic and permanent. `search_vehicles`, `resolve_vehicle` and `decode_vin` all return them, and every image endpoint, signed-URL item, 3D request and MCP tool accepts `vehicle: "veh_…"` in place of `make`, `model` and `year` (both together is a `400`; an unknown id is a `404`). Every echoed vehicle object opens with `vehicle_id`.

Always render by the id: it cannot be misspelled, it survives catalog releases, and it is what to store in the user's database. `GET /api/v1/vehicles/{id}` (public, free) turns an id back into its make, model, year, every year of the model, and ready-made image paths.

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
- A `400` is not a VIN (length, an I, O or Q); a `404` is a pattern NHTSA does not know, so decoding it again will not help. Ask the user to check the characters rather than guessing, above all the first three (the maker code), or decode what they are sure of as a partial VIN with `*` and a `year`. NHTSA's data covers vehicles made for the US market: find any other car by name with `resolve_vehicle` or `search_vehicles`.

## Searching and listing

`search_vehicles` (REST: `GET /api/v1/vehicles?q=`) matches makes and models with typo tolerance and returns canonical names plus the years available for each, with a vehicle id per year (`ids`) and `id` when the query names a single year.

Every word of the query must be in the name of one catalog vehicle, so **fewer words find more**: "honda civic" lists the Civic and every Civic variant, "honda civic touring sedan" may list nothing. When no vehicle carries every word but the query names a make and a model the image endpoints would read ("Mazda MX-5 Miata" in 2018), the search answers with that one vehicle. An empty result is a reason to shorten the query or call `resolve_vehicle`, not yet a missing vehicle.

Use it to:

- **List a make's models** — search the make, read the models back.
- **See a model's variants** — "porsche 911" with `year: 2024` lists the 911, the Carrera, the GT3, the Targa and the rest, each with its id, for the user to pick from.
- **Find valid years** — the response tells you which model years exist, so you never request one that does not, and hands you the id of each.
- **Recover from a 404** — read its `suggestions` first (real catalog vehicles, closest first, with ids); search only when they are empty.

Render and catalog lookups also accept vehicle-db's reviewed aliases (`maccane` → `macan`, `prado` → `land-cruiser-prado`) after local matching misses. BMW petrol badges preserve an explicit body (`430-gran-coupe` → `430i-gran-coupe`). These require one catalog model in the requested make/year and report `X-Vehicle-Match: alias`; ambiguous or unverified results stay 404s. A search result's rank alone is not permission to substitute it.

The catalog's spelling wins, and the render endpoints read the common alternatives themselves (`/docs/vehicles#matching`): nicknames (`Mercedes`, `VW`, `Chevy`), other separators (`cx5`, `landrover`), word order and language (`Série 3`, `Classe A`, `q6-e-tron-sportback`), same-body names (`rx-350`, `camry-hybrid`, `740`, `mx-5-miata`), engine and trim words (`tucson-n-line-s-t-gdi-hev-auto`, `x3-xdrive30d`), badges (`c300`, `760`) and typos (`elentra`, `porshe`). The response header `X-Vehicle-Match` says whether the spelling was literal (`exact`) or which rule interpreted it (`prefix`, `separator`, `family`, `words`, `alias`, `trim`, `badge`, `fuzzy`); `vehicle_id` / `X-Vehicle-Id` names the vehicle served. Body styles, performance derivatives and electric twins are never substituted, and neither is a model year the catalog does not carry: those answer `404` with `suggestions`, real catalog vehicles with ids you can retry with (`vehicle: <id>`) or show to the human. When a render's `X-Vehicle-Match` is not `exact`, say in one line which vehicle was served. None of this is a reason to render by name: the lookup tells you what you will get before a credit is spent.

## Disambiguating like a human would

The catalog keys on make, model and year, and it is merged from several registries, so what counts as a "model" varies. Ask the lookup rather than assuming either way.

- **Many variants are models of their own.** Civic Si and Civic Type R, M3 Competition, F-150 Raptor, 911 GT3, Corolla Hatchback, A4 Avant, Cooper Convertible, Wrangler Rubicon: `resolve_vehicle` returns them as themselves, and that is what to render.
- **Others are not in the catalog.** A Civic hatchback in a year that has only the Civic, a Golf Estate, a Camaro SS: the lookup answers with the nameplate at `medium`, a neighbour at `low`, or nothing. Say which vehicle the image represents, and do not claim it shows the trim or the body that was asked for.
- **Options and packages are never a parameter.** Wheels, a sport package, an interior: render the model and say what it is.
- **Year means model year.** "A 2023 car bought in 2022" is a 2023. When someone says "a mid-2000s Civic", offer a specific year rather than picking one silently.
- **Generation talk needs a year.** "992 911", "E90 M3", "Mk7 Golf" — map it to a model year, and confirm if you are unsure.
- **Regional names differ.** The MX-5 is a Miata in North America; the same car can be a Corolla in one market and something else in another. Look it up rather than assuming.

## When the user did not name a car

"A random car", "surprise me", "a fun convertible", "a family SUV". Choose one yourself: a specific year, make and model you are confident exists, varied from one request to the next. Tell the user which you chose, then look it up and render it like any other. The lookup still comes first: the car you thought of is a name from memory.

## Offline: the npm package

For a vehicle picker, a validation rule, or anything that should not make a network call per keystroke, install the catalog directly:

```bash
npm install @meterapp/vehicle-db
```

It is open source, has no runtime dependencies, and ships the full make/model/year data. Use it to populate cascading dropdowns (make → model → year), validate a form before submitting, or pre-check that a vehicle exists before calling the API. Then pass the values you selected straight to the render call — they are already canonical.

This is the right choice when you need instant filtering, offline behavior, or hundreds of lookups. Use `search_vehicles` when you want fuzzy matching and typo tolerance over free text.

## Telling the user what you did

When you resolved something that needed interpreting, say so in one line: "This is the 2022 Honda Civic — the catalog has no separate hatchback for that year." or "There is no 2020 WRX STI in the catalog; the newest is 2017. Want that one?" That is the difference between a user trusting the image and being surprised by it.

If the catalog does not have the vehicle, say that rather than rendering the nearest thing, and offer `request_vehicle` so the gap gets closed. A silently substituted car is worse than no image.

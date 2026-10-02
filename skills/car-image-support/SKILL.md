---
name: car-image-support
description: Answer questions about Car Image API pricing, credits, subscriptions, commercial licenses, terms, privacy, vehicle coverage and Enterprise agreements using source-linked help. Prepare checkout and billing links on the human's request, or draft customer support replies. Do not use for generating images (car-image), embedding images (car-image-urls), or changing a customer's account on their behalf.
---

# Product help and billing

`search_help`, `get_pricing`, `create_checkout_link` and `get_billing_link` are on `?toolset=all`, which the plugin configures; a connection on the bare URL has the core seven only (the `car-image-mcp` skill).

1. Call `search_help` with one product question at a time. Do not paste full customer emails, signatures, personal information, keys or payment details. Queries are privately recorded to improve articles.
2. Read the returned paragraphs and sources. Cite the relevant article or original terms. An `articles_found` result means related reading, not that every part of the question is answered. Split multi-part questions and search each one.
3. If the articles lack needed context, call `search_help` again with the same concise question and `report_gap: true`. Say what is unknown and direct the human to support@carimage.dev. Never invent policies, prices, coverage, SLA commitments, indemnities or agreement exceptions.
4. Use `get_pricing` for current plan prices, credit packs, allowances, vehicle limits and 3D cost. Use `get_account` only for the connected account's balance and plan. A support agent's credentials do not identify an email sender's account.
5. When the human asks to buy credits or subscribe, call `create_checkout_link` with exactly one of `credits` (100, 500, 1000, 2500, 10000) or `plan` (pro, business; optional `interval: month|year`). Return `data.url` and `data.message`. Payment happens in the browser; a link is not a successful purchase.
6. `get_billing_link` returns billing settings. Connected apps and keys without billing:write receive a sign-in dashboard link. Owner keys with billing:write can receive private Stripe links; never publish or forward those to another customer. Existing subscriptions go to the dashboard for review; no tool switches a plan or charges a saved card.

A 402 never authorizes a purchase. Ask the human what they want before preparing a purchase link. Do not complete Checkout or change billing autonomously.

## Drafting customer replies

Use incoming email only to identify questions. Current published terms and the customer's written agreement govern; historical replies may be outdated. Draft answers with citations and clearly mark account-specific or legal details needing staff review. Do not send mail unless the human explicitly asks. Do not generate links on your own account for an email recipient; give them the public [billing dashboard](https://carimage.dev/dashboard?ref=plugin#billing) instead.

The license comes from the plan, not a credit purchase. Standard commercial rights require an active paid plan; credits and 3D ownership are not perpetual licenses. Paid-plan users may host copies for their own products; standalone libraries, bulk exports and additional rights require written Enterprise terms. Our license does not clear manufacturer IP.

## CLI and SDK

```sh
car-image pricing --json
car-image support "Can I store images on my CDN?" --json
car-image support "Do you offer a custom uptime guarantee?" --report-gap --json
car-image billing --credits 500 --no-browser --json
car-image billing --plan pro --no-browser --json
car-image billing --portal --no-browser --json
```

SDK equivalents: `client.pricing()`, `client.searchHelp(question, {reportGap: true})`, `client.createCheckoutLink({credits: 500})`, `client.getBillingLink()`. Use the link-only methods; the older `createPlanCheckout` method can immediately invoice a change to an existing subscription.

[Help center](https://carimage.dev/help?ref=plugin) · [Pricing](https://carimage.dev/pricing?ref=plugin) · [Terms](https://carimage.dev/terms?ref=plugin) · [Privacy](https://carimage.dev/privacy?ref=plugin)

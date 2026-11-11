---
name: car-image-support
description: Answer questions about Car Image API pricing, plans and what they count (vehicle images), credits, Image Packs, subscriptions, commercial licenses, terms, privacy, vehicle coverage and Enterprise agreements using source-linked help. Prepare checkout and billing links on the human's request, buy a plan or pay a renewal with a payment token only under the owner's agent spending limit, or draft customer support replies. Do not use for generating images (car-image), embedding images (car-image-urls), or changing a customer's account on their behalf.
---

# Product help and billing

`search_help` and `get_pricing` are also on the plugin's `car-image-catalog` server, so pricing, licensing and what-happens-when-a-plan-ends questions can be answered before anyone signs in; `create_checkout_link` and `get_billing_link` need the account server on `?toolset=all`, which the plugin configures (a connection on the bare URL has the core twelve only; the `car-image-mcp` skill).

1. Call `search_help` with one product question at a time. Do not paste full customer emails, signatures, personal information, keys or payment details. Queries are privately recorded to improve articles.
2. Read the returned paragraphs and sources. Cite the relevant article or original terms. An `articles_found` result means related reading, not that every part of the question is answered. Split multi-part questions and search each one.
3. If the articles lack needed context, call `search_help` again with the same concise question and `report_gap: true`. Say what is unknown and direct the human to support@carimage.dev. Never invent policies, prices, coverage, SLA commitments, indemnities or agreement exceptions.
4. Use `get_pricing` for current plan prices, monthly vehicle images, limits per tier, Image Packs (`image_packs`, `add_ons`) and 3D cost; it works before sign-in (the catalog server has it too), and every plan and Image Pack offer carries a `checkout_url` that signs the human in, or up, and opens Stripe Checkout. Use `get_account` only for the connected account's plan, this month's usage against its allowance (`limits_usage.vehicle_images_this_month`), credit balance and next tier (`next_plan`). A support agent's credentials do not identify an email sender's account.
5. When the human asks to subscribe, call `create_checkout_link` with `plan` (pro, business; optional `interval: month|year`). For an Image Pack, hand them the offer's `checkout_url` from `get_pricing`. Return `data.url` and `data.message`. Payment happens in the browser; a link is not a successful purchase. Credits are not sold: when the human asks for more credits or more images, explain what a higher plan or an Image Pack adds instead.
6. `get_billing_link` returns billing settings. Connected apps and keys without billing:write receive a sign-in dashboard link for settings, and `create_checkout_link` gives them a checkout link that signs the human in first. Owner keys with billing:write can receive private Stripe links; never publish or forward those to another customer. Existing subscriptions go to the dashboard for review; no tool switches a plan or charges a saved card.

### When to buy instead of handing over a link

`purchase_plan` (and `pay_invoice` for an open renewal, `billing.renewal_due` in `get_account`) pays with a Stripe Shared Payment Token (`spt_…`) your platform minted from the buyer's card. Use it only when all of these hold; otherwise hand the human `checkout_url`:

- the human asked you to buy, or their agent spending limit (`billing.agent_spend` in `get_account`) covers this plan and amount;
- you hold a payment token for this seller (never ask for, read or type a card number; one is refused);
- you ran it with `dry_run: true` first and told the human the amount, the card and that a token pays once (renewals need a card they save, or `pay_invoice` with a fresh token).

Then call it again with the same `purchase_id` and `dry_run: false`; a repeat never charges twice. Every refusal (`no_mandate`, `mandate_exceeded`, `scope_missing`, `payment_failed`, `requires_action` for 3D Secure, `already_subscribed`, `price_changed`) carries `checkout_url`: give it to the human and stop. Paying in the browser with an agent card or Link instead: `create_checkout_link`, then poll `checkout_status` with its `session_id` until `complete`. Only the owner sets or raises the limit, in the dashboard's Let agents buy card; never try to change it.

A 402 never authorizes a purchase by itself. With `code: "plan_image_limit"` the month's vehicle images, or Free's per account (30, then a one-time courtesy of 30), are used up: it carries `plan`, `used`, `included`, `resets_at` (the 1st, UTC; null on Free, whose images do not reset), `checkout_url` (the next plan, as `next_plan` describes it) and `pack_url` (Image Packs). Nothing was charged, and images already received this month keep serving. With `code: "subscription_required_for_credits"` the balance is short for a 3D model, logo or upgrade; credits are not sold, so `checkout_url` is the next plan (which includes credits every month) and `pack_url` the Image Packs, and credits the account already holds stay spendable. Tell the human the price and hand them the link. `get_pricing` lists `image_packs`: one-time Image Packs (one vehicle view per unit) and Vehicle Packs (one vehicle in every view per unit), made at the highest quality and self-hosted forever, with 180 days of updates; any quantity from 100 is sold at the per-unit rate of its tier (`image_packs.custom` has the rates and a link template), and each quick-buy offer's `checkout_url` is for the human. A large batch can take one to two hours; the buyer gets a webhook per car and an email when the batch is done. To see what a catalog would count before importing it, `POST /api/v1/images/availability` (free, REST and the SDK) says which views are prepared and whether they fit the month. Complete Checkout or change billing only when the human asks you to, or a spending mandate they set up covers the amount; never enter card details.

## Requests, issues and reviews

A product question the help center cannot answer may be a feature request or a bug. When the human wishes Car Image did something, `request_feature`; when something is broken, `report_issue` with the failed call's `request_id` (private to them and the team). Both return `similar` items first: `upvote_feedback` the one that matches. `list_my_feedback` tells them where their requests stand. A review (`submit_review`) is the human's own rating and words, never one you suggest. The [feedback docs](https://carimage.dev/docs/feedback?ref=plugin) cover the REST and CLI equivalents.

## Drafting customer replies

Use incoming email only to identify questions. Current published terms and the customer's written agreement govern; historical replies may be outdated. Draft answers with citations and clearly mark account-specific or legal details needing staff review. Do not send mail unless the human explicitly asks. Do not generate links on your own account for an email recipient; give them the public [billing dashboard](https://carimage.dev/dashboard?ref=plugin#billing) instead.

The license comes from the plan a render was delivered under. Free is for evaluation and personal projects. Pro and Business carry a commercial license while the plan is active, including copies on the customer's own servers and CDN; within 30 days after the plan ends, stored copies are deleted (`after-your-plan-ends`). Image Pack images may be self-hosted forever. Accounts that paid before 2026-10-25 keep their old terms, price and credit meter until the cutover date in their notice, and renders delivered under earlier terms keep the rights they were delivered with. Credits and 3D ownership are not licenses by themselves. Offering renders as a standalone library or dataset is prohibited, and a bulk export or catalog copy needs written Enterprise terms. Our license does not clear manufacturer IP.

## CLI and SDK

```sh
car-image pricing --json
car-image support "Can I store images on my CDN?" --json
car-image support "Do you offer a custom uptime guarantee?" --report-gap --json
car-image billing --plan pro --no-browser --json
car-image billing --portal --no-browser --json
```

SDK equivalents: `client.pricing()`, `client.searchHelp(question, {reportGap: true})`, `client.createCheckoutLink({plan: "pro"})`, `client.getBillingLink()`. Use the link-only methods; the older `createPlanCheckout` method can immediately invoice a change to an existing subscription.

[Help center](https://carimage.dev/help?ref=plugin) · [Pricing](https://carimage.dev/pricing?ref=plugin) · [Terms](https://carimage.dev/terms?ref=plugin) · [Privacy](https://carimage.dev/privacy?ref=plugin)

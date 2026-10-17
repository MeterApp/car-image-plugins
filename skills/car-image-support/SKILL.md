---
name: car-image-support
description: Answer questions about Car Image API pricing, credits, subscriptions, commercial licenses, terms, privacy, vehicle coverage and Enterprise agreements using source-linked help. Prepare checkout and billing links on the human's request, buy a plan or pay a renewal with a payment token only under the owner's agent spending limit, or draft customer support replies. Do not use for generating images (car-image), embedding images (car-image-urls), or changing a customer's account on their behalf.
---

# Product help and billing

`search_help` and `get_pricing` are also on the plugin's `car-image-catalog` server, so pricing, licensing and what-happens-when-a-plan-ends questions can be answered before anyone signs in; `create_checkout_link` and `get_billing_link` need the account server on `?toolset=all`, which the plugin configures (a connection on the bare URL has the core seven only; the `car-image-mcp` skill).

1. Call `search_help` with one product question at a time. Do not paste full customer emails, signatures, personal information, keys or payment details. Queries are privately recorded to improve articles.
2. Read the returned paragraphs and sources. Cite the relevant article or original terms. An `articles_found` result means related reading, not that every part of the question is answered. Split multi-part questions and search each one.
3. If the articles lack needed context, call `search_help` again with the same concise question and `report_gap: true`. Say what is unknown and direct the human to support@carimage.dev. Never invent policies, prices, coverage, SLA commitments, indemnities or agreement exceptions.
4. Use `get_pricing` for current plan prices, credit packs, allowances, limits per tier and 3D cost; it works before sign-in (the catalog server has it too), and every plan and pack carries a `checkout_url` that signs the human in, or up, and opens Stripe Checkout. Use `get_account` only for the connected account's balance, plan, usage against each limit (`limits_usage`) and next tier (`next_plan`). A support agent's credentials do not identify an email sender's account.
5. When the human asks to buy credits or subscribe, call `create_checkout_link` with exactly one of `credits` (100, 500, 1000, 2500, 10000) or `plan` (pro, business; optional `interval: month|year`). Return `data.url` and `data.message`. Payment happens in the browser; a link is not a successful purchase.
6. `get_billing_link` returns billing settings. Connected apps and keys without billing:write receive a sign-in dashboard link for settings, and `create_checkout_link` gives them a checkout link that signs the human in first. Owner keys with billing:write can receive private Stripe links; never publish or forward those to another customer. Existing subscriptions go to the dashboard for review; no tool switches a plan or charges a saved card.

### When to buy instead of handing over a link

`purchase_plan` (and `pay_invoice` for an open renewal, `billing.renewal_due` in `get_account`) pays with a Stripe Shared Payment Token (`spt_…`) your platform minted from the buyer's card. Use it only when all of these hold; otherwise hand the human `checkout_url`:

- the human asked you to buy, or their agent spending limit (`billing.agent_spend` in `get_account`) covers this plan and amount;
- you hold a payment token for this seller (never ask for, read or type a card number; one is refused);
- you ran it with `dry_run: true` first and told the human the amount, the card and that a token pays once (renewals need a card they save, or `pay_invoice` with a fresh token).

Then call it again with the same `purchase_id` and `dry_run: false`; a repeat never charges twice. Every refusal (`no_mandate`, `mandate_exceeded`, `scope_missing`, `payment_failed`, `requires_action` for 3D Secure, `already_subscribed`, `price_changed`) carries `checkout_url`: give it to the human and stop. Paying in the browser with an agent card or Link instead: `create_checkout_link`, then poll `checkout_status` with its `session_id` until `complete`. Only the owner sets or raises the limit, in the dashboard's Let agents buy card; never try to change it.

A 402 never authorizes a purchase by itself. It carries `checkout_url` and `pricing`: tell the human the price and hand them the link. Complete Checkout or change billing only when the human asks you to, or a spending mandate they set up covers the amount; never enter card details.

## Drafting customer replies

Use incoming email only to identify questions. Current published terms and the customer's written agreement govern; historical replies may be outdated. Draft answers with citations and clearly mark account-specific or legal details needing staff review. Do not send mail unless the human explicitly asks. Do not generate links on your own account for an email recipient; give them the public [billing dashboard](https://carimage.dev/dashboard?ref=plugin#billing) instead.

The license comes from the plan a render was delivered under, not from a credit purchase. Commercial work needs an active paid plan when the render is delivered, and what a paid plan delivered keeps its license after the plan ends (`after-your-plan-ends`); credits and 3D ownership are not licenses by themselves. Paid-plan users may host copies for their own products without any agreement; offering renders as a standalone library or dataset is prohibited, and a bulk export or catalog copy needs written Enterprise terms. Our license does not clear manufacturer IP.

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

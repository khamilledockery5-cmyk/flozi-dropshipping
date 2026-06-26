# PowerpostFit — Store Launch Guide

Everything that's already done, plus the exact steps to take the store live and
start driving sales. Store: `powerpostfit.myshopify.com` (Basic plan, USD).

---

## 1. What's already done ✅

### Products (17, all ACTIVE)
Curated "winning" home-fitness dropshipping products across every price point —
impulse buys ($19–30) to higher-AOV heroes ($80–90) — plus a 100%-margin digital
program. Each product has:

- A **benefit-driven, SEO-friendly title** (keyword + descriptor + format).
- **Conversion-optimized HTML copy**: hook → benefit bullets → urgency → trust row
  (free shipping, 30-day guarantee, social proof).
- A **professional fitness hero image** hosted on Shopify's CDN.
- **Sale pricing** (a compare-at price) so every product shows an anchored discount.
- **Custom SEO meta title + meta description** for Google.
- **Smart tags** that auto-sort it into the right collections.

### Collections (7, smart/auto-populated)
All collections are rule-based on tags, so they stay in sync automatically and
each has its own SEO description + cover image. See the README for the tag rules.

### Inventory
Variants are **untracked**, so products never show "sold out" — the correct
default for dropshipping, where stock lives with the supplier.

---

## 2. Pricing & margin strategy

Prices use **charm pricing** ($X.99) and a compare-at "was" price to anchor a
visible discount (~45% off), which lifts conversion. Typical dropship cost basis
and target margins:

| Tier | Example | Sell | Est. supplier cost | Est. gross margin |
|------|---------|-----:|-------------------:|------------------:|
| Impulse | Posture corrector, grip kit | $19–27 | $3–7 | ~70–75% |
| Mid | Bands, jump rope, push-up board | $30–40 | $6–12 | ~65–70% |
| Hero | Massage gun, dumbbells, watch | $50–90 | $18–35 | ~55–65% |
| Digital | 12-week program | $19.99 | ~$0 | ~100% |

> Update prices after you confirm real supplier costs so every product clears a
> healthy margin **after** ad spend + payment fees. A common target is a 3x+
> markup on landed cost for paid-traffic dropshipping.

---

## 3. Launch checklist (account-level — do these in Shopify Admin)

These can't be done via the catalog API and need your account/owner access:

- [ ] **Payments** — Activate Shopify Payments (or PayPal/Stripe) in
      *Settings → Payments*. Without this you can't accept orders.
- [ ] **Shipping** — Set rates in *Settings → Shipping & delivery*. Simplest for
      dropshipping: a single **free-shipping** zone (margins already assume it) or
      a low flat rate.
- [ ] **Supplier / fulfillment** — Install a sourcing app (**DSers/AliExpress**,
      **CJ Dropshipping**, **Zendrop**, or **Spocket**), match each SKU to a real
      supplier product, and **replace the stock hero images with the supplier's
      actual product photos** so what ships matches what's shown.
- [ ] **Taxes** — Configure in *Settings → Taxes & duties* for your region.
- [ ] **Domain** — Buy/connect a custom domain (e.g. `powerpostfit.com`) in
      *Settings → Domains* for trust + branding.
- [ ] **Store policies** — Generate Refund, Privacy, Terms, and Shipping policies
      (*Settings → Policies* has templates). Required for ad platforms.
- [ ] **Theme polish** — Add a homepage hero banner, feature the **Best Sellers**
      collection, add an announcement bar (free shipping / guarantee), and set up
      the main menu from the 7 collections.
- [ ] **Email** — Enable abandoned-cart recovery + a welcome flow (Shopify Email
      or Klaviyo) and a newsletter signup with a first-order discount.
- [ ] **Trust** — Add a reviews app (e.g. Judge.me/Loox) and seed reviews; show
      the guarantee + secure-checkout badges.

---

## 4. Suggested first marketing moves

- **Launch offer**: a sitewide code (e.g. `WELCOME15`) or free-shipping bar to
  convert first visitors. (Percentage discount codes can be created via API.)
- **Hero products for ads**: Massage Gun, Smart Jump Rope, Adjustable Dumbbells,
  Smart Watch — strong visual demos for TikTok/Reels/Meta video creative.
- **Bundles/AOV**: pitch the 12-Week Program as a $19.99 add-on at checkout and
  bundle bands + booty bands + mat as a "Home Studio Starter Kit."
- **SEO**: product/collection meta is set; add blog content
  ("best home gym equipment for small apartments", "resistance band workouts")
  to capture organic search.

---

## 5. Reference

- Catalog with SKUs, prices and tags: [`../data/products.csv`](../data/products.csv)
- All data of record lives in Shopify Admin; this repo is documentation.

> **Note on the "7-figure" framing:** the store is structurally built to scale —
> proven products, clean funnels, anchored pricing, auto-sorting collections and
> SEO. Actual revenue depends on completing the checklist above and ongoing
> marketing/ad performance. No revenue is implied or guaranteed by this setup.

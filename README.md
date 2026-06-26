# PowerpostFit — Prebuilt Dropshipping Store

A launch-ready home-fitness / gym-equipment dropshipping brand built on Shopify
(`powerpostfit.myshopify.com`). This repo documents the store build: the product
catalog, pricing/margin strategy, collection structure, SEO setup, and the steps
left to flip it live.

> **Status:** Catalog, collections, pricing, images and on-page SEO are fully
> built and **live (ACTIVE)** in Shopify. Remaining work is account-level setup
> (payments, shipping, supplier connection, domain) — see the launch checklist.

---

## What's been built

| Area | Status | Notes |
|------|--------|-------|
| Products | ✅ 17 live | Winning fitness products, ACTIVE, conversion-optimized copy |
| Product images | ✅ Done | Professional fitness photos on Shopify CDN (swap for supplier photos) |
| Sale pricing | ✅ Done | Compare-at prices on every product for urgency/anchoring |
| SEO meta | ✅ Done | Keyword-rich SEO title + meta description on every product |
| Collections | ✅ 7 live | Smart/auto-tag collections, each with SEO copy + cover image |
| Inventory | ✅ Untracked | Always purchasable — correct for dropshipping |
| Payments / Shipping | ⬜ To do | Account-level, see checklist |
| Supplier / fulfillment | ⬜ To do | Connect AliExpress/CJ/Zendrop, see checklist |

See [`docs/STORE-LAUNCH-GUIDE.md`](docs/STORE-LAUNCH-GUIDE.md) for the full guide
and [`data/products.csv`](data/products.csv) for the catalog reference.

---

## Catalog at a glance (17 products)

| Product | Price | Compare-at | Role |
|---------|------:|-----------:|------|
| PowerFlex Adjustable Dumbbell Set | $89.99 | $159.99 | Hero / high-AOV |
| FlexCore Resistance Bands (11-pc) | $34.99 | $69.99 | Best seller |
| SculptBands Fabric Booty Bands (3-pk) | $24.99 | $49.99 | Impulse |
| PulsePro Smart Jump Rope | $29.99 | $54.99 | Best seller / viral |
| RecoverPro Percussion Massage Gun | $79.99 | $149.99 | Hero / high-AOV |
| DeepRoll High-Density Foam Roller | $27.99 | $49.99 | Impulse |
| CoreMax Ab Roller Wheel Kit | $26.99 | $49.99 | Impulse |
| ZenFlex Non-Slip Yoga Mat | $39.99 | $69.99 | Mid |
| PushPro Push-Up Board System | $32.99 | $59.99 | Mid |
| IronGrip Doorway Pull-Up Bar | $36.99 | $64.99 | Mid |
| FlexWeight Ankle & Wrist Weights | $29.99 | $54.99 | Impulse |
| GripForge Hand Grip Strengthener Kit | $19.99 | $34.99 | Add-on |
| PulseTrack Smart Fitness Watch | $49.99 | $99.99 | Best seller / tech |
| HydraPower Gym Water Bottle 2.2L | $24.99 | $44.99 | Add-on |
| SweatShape Waist Trainer Belt | $22.99 | $44.99 | Impulse |
| PosturePro Posture Corrector | $21.99 | $39.99 | Impulse |
| 12-Week Home Transformation Program | $19.99 | $49.99 | 100% margin (digital) |

---

## Collection structure (all smart / auto-populated by tag)

1. **Best Sellers** — `tag: best seller`
2. **Strength & Resistance** — `tag: strength training | muscle building | calisthenics`
3. **Cardio & HIIT** — `tag: cardio | HIIT | jump rope`
4. **Recovery, Yoga & Mobility** — `tag: muscle recovery | foam roller | post-workout recovery | yoga`
5. **Home Gym Essentials** — `tag: home gym | home workout`
6. **Gym Accessories & Tech** — `tag: gym accessories | gym bag essentials | wearable tech`
7. **Digital Programs** — `tag: digital`

Because they're rule-based, **any new product you tag is auto-sorted** into the
right collections — no manual filing required.

---

## How this was built

All store changes were made through the Shopify Admin API. The product / pricing /
SEO data of record lives in Shopify; this repo is documentation plus a
re-importable CSV.

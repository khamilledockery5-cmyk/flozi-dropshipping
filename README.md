# PowerpostFit — Premium Home-Fitness Store (Prebuilt)

A launch-ready, **premium / luxury** home-fitness dropshipping brand on Shopify
(`powerpostfit.myshopify.com`). This repo documents the store build: catalog,
positioning, pricing, collections, SEO, storefront/theme, and the owner-only
steps left to flip it live.

> **Status:** Catalog, collections, premium pricing, images, on-page SEO, the
> luxury storefront copy, pages, navigation and a welcome discount are all
> **built and live**. Remaining work is owner-only account setup (payments,
> shipping rates, legal policies, domain) — see the launch checklist.

---

## Positioning: premium / luxury

The brand is positioned as considered, premium home fitness — refined copy,
clean confident pricing (no discount theatre), and an elegant storefront
(Playfair Display headings on an ivory/charcoal palette). Product and homepage
copy use an elevated, editorial voice ("Strength, beautifully engineered").

---

## What's been built

| Area | Status | Notes |
|------|--------|-------|
| Products | ✅ 17 live | Premium copy, ACTIVE, untracked (always sellable) |
| Product images | ✅ Done | Pro fitness photos on Shopify CDN (swap for supplier photos) |
| Premium pricing | ✅ Done | Clean luxury pricing, compare-at "sale" anchors removed |
| SEO meta | ✅ Done | Keyword-rich SEO title + meta description on every product |
| Collections | ✅ 7 live | Smart/auto-tag, each with SEO copy + cover image |
| Storefront (homepage) | ✅ Rewritten | Luxury copy across all live-theme sections; broken link fixed |
| Pages | ✅ About + FAQ | Published |
| Navigation | ✅ Done | Main menu → 7 collections; footer → About/FAQ/Search |
| Welcome discount | ✅ WELCOME10 | 10% off, all customers, active |
| Legal policies | ⬜ Owner | API lacks the legal-policy scope — set in Admin (templates) |
| Payments / Shipping / Domain | ⬜ Owner | Account-level, see checklist |

See [`docs/STORE-LAUNCH-GUIDE.md`](docs/STORE-LAUNCH-GUIDE.md) for the full guide
and [`data/products.csv`](data/products.csv) for the catalog reference.

---

## Catalog (17 products) — premium pricing

| Product | Price |
|---------|------:|
| PowerFlex Adjustable Dumbbell Set | $179.00 |
| RecoverPro Percussion Massage Gun | $149.00 |
| PulseTrack Smart Fitness Watch | $99.00 |
| ZenFlex Non-Slip Yoga Mat | $79.00 |
| IronGrip Doorway Pull-Up Bar | $69.00 |
| FlexCore Resistance Bands (11-pc) | $59.00 |
| PulsePro Smart Jump Rope | $59.00 |
| PushPro Push-Up Board System | $59.00 |
| FlexWeight Ankle & Wrist Weights | $55.00 |
| DeepRoll High-Density Foam Roller | $49.00 |
| CoreMax Ab Roller Wheel Kit | $49.00 |
| SculptBands Fabric Booty Bands (3-pk) | $45.00 |
| HydraPower Gym Water Bottle 2.2L | $45.00 |
| PosturePro Posture Corrector | $45.00 |
| GripForge Hand Grip Strengthener Kit | $39.00 |
| SweatShape Waist Trainer Belt | $39.00 |
| 12-Week Home Transformation Program | $39.00 |

---

## Collection structure (all smart / auto-populated by tag)

1. **Best Sellers** — `tag: best seller`
2. **Strength & Resistance** — `tag: strength training | muscle building | calisthenics`
3. **Cardio & HIIT** — `tag: cardio | HIIT | jump rope`
4. **Recovery, Yoga & Mobility** — `tag: muscle recovery | foam roller | post-workout recovery | yoga`
5. **Home Gym Essentials** — `tag: home gym | home workout`
6. **Gym Accessories & Tech** — `tag: gym accessories | gym bag essentials | wearable tech`
7. **Digital Programs** — `tag: digital`

Rule-based, so any new tagged product is auto-sorted in.

---

## How this was built

All store changes were made through the Shopify Admin API. The store is the data
of record; this repo is documentation plus a re-importable CSV.

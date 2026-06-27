# PowerpostFit — Store Launch Guide (Premium Edition)

Everything that's already done, plus the owner-only steps to take the store live.
Store: `powerpostfit.myshopify.com` (Basic plan, USD). Positioning: premium /
luxury home fitness.

---

## 1. What's already done ✅

### Products (17, ACTIVE)
Curated premium home-fitness products with elevated, editorial copy, professional
imagery on Shopify's CDN, keyword-rich SEO meta, and smart tags that auto-sort
each item into collections. Inventory is **untracked** (always sellable — correct
for dropshipping).

### Premium pricing
Repositioned from discount-led to clean luxury pricing. The compare-at "sale"
anchors were removed so nothing reads as marked-down — confident, premium prices
($39–$179). See the catalog table in the README.

### Collections (7, smart/auto-populated)
Rule-based on tags, each with its own SEO description + cover image. They stay in
sync automatically.

### Storefront / theme
Live theme is **Horizon** (Playfair Display headings, ivory/charcoal palette — a
genuine luxury base). The homepage was fully rewritten from aggressive "bro"
marketing to refined luxury copy across every section (hero, trust marquee,
comparison, features, product grid, testimonials, video, newsletter, lifestyle,
gallery), and a broken hero product link was fixed to point at live collections.

### Pages
**About PowerpostFit** (brand philosophy) and **FAQ** — both published.

### Navigation
- Main menu → Shop All + the 6 key collections.
- Footer menu → About, FAQ, Search.

### Discount
**WELCOME10** — 10% off, all customers, active (fulfils the homepage welcome
offer).

---

## 2. Launch checklist (owner-only — do these in Shopify Admin)

These require account/owner access or scopes the app doesn't have:

- [ ] **Payments** — Activate Shopify Payments (or PayPal/Stripe) in
      *Settings → Payments*. **Without this you cannot accept orders.**
- [ ] **Shipping** — *Settings → Shipping & delivery*. Simplest: one
      **free-shipping** zone (pricing already assumes it).
- [ ] **Legal policies** — *Settings → Policies*. Click **"Create from template"**
      for Refund, Privacy, Terms and Shipping, then tweak. (The API couldn't set
      these — it lacks the legal-policy scope. Templates make it a 2-minute job,
      and they auto-link in the footer.)
- [ ] **Supplier / fulfilment** — Install a sourcing app (**DSers/AliExpress**,
      **CJ Dropshipping**, **Zendrop**, **Spocket**), match each SKU to a real
      supplier product, and **replace the stock hero images with the supplier's
      actual product photos** so what ships matches what's shown.
- [ ] **Taxes** — *Settings → Taxes & duties* for your region.
- [ ] **Domain** — Connect `powerpostfit.com` in *Settings → Domains* for trust.
- [ ] **Homepage media** — In the theme editor, add a hero image and the gallery
      images (those fields were left empty intentionally; use lifestyle/supplier
      photos). Optionally add the YouTube links in the video section.
- [ ] **Reviews + email** — Add a reviews app (Judge.me/Loox) and enable
      abandoned-cart + welcome email flows (Shopify Email or Klaviyo).

---

## 3. Suggested first marketing moves

- **WELCOME10** is live — surface it via the newsletter section / an announcement.
- **Hero products for ads**: Massage Gun, Adjustable Dumbbells, Smart Watch, Smart
  Jump Rope — premium, demo-friendly creative for Meta/TikTok.
- **AOV**: bundle the 12-Week Programme with hardware; build a "Home Studio
  Starter" set (dumbbells + bands + mat).
- **SEO**: product/collection meta is set; add blog content
  ("best home gym equipment for small spaces", "resistance band workouts").

---

## 4. Reference

- Catalog with SKUs, prices and tags: [`../data/products.csv`](../data/products.csv)
- The store (Shopify Admin) is the data of record; this repo is documentation.

> **Note on the "7-figure / luxury" framing:** the store is structurally built to
> scale — premium products and positioning, refined storefront, auto-sorting
> collections and SEO. Actual revenue depends on completing the checklist above
> and ongoing marketing performance. No revenue is implied or guaranteed.

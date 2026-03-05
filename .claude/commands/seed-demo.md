# Seed Demo Content

Reset and reseed the database with rich structured JSON demo content that exercises all section types.

This creates a showcase site with beautiful content for each section type.

Steps:

1. Confirm with user: "This will reset the database and seed rich demo content. All existing data will be lost. Confirm? (yes/no)"

2. If confirmed, update the seed file `backend/seeds/seed.py` to use structured JSON content:
   - Client user's demo site should have a landing page with ALL section types: hero, features, testimonials, about, contact, cta, pricing
   - Content should be realistic (e.g., a fictional coffee shop or boutique business)
   - All JSON should match the schemas in docs/content-schema.md
   - Mark some sections as content_published = content_draft (as if already published once)

3. Run: `./cli.sh db:reset`

4. Verify the demo site looks great:
   - Open http://localhost:3000/{demo-site-slug}
   - Check each section renders with the Framer-level components
   - Verify different themes work: test with `modern`, `warm`, `startup`

5. Report: seed ran, demo site URL, what sections were created.

The demo site slug will be `demo-site` (client@docmet.com's site).

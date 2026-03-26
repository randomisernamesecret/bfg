# BFG Site

Static website for Blue Flame Games (BFG) at bfgapps.co. Hosted on GitHub Pages with Cloudflare DNS.

## Structure
- `index.html` — Homepage (8 apps, blog filters, FAQ)
- `apps/{name}/` — Per-app landing page + privacy, support, terms
- `blog/` — 24 articles across 7 categories
- `style.css` — Shared CSS (dark/light, nav, app pages)
- `theme.js` — Dark/light toggle
- `nav.js` — Mobile hamburger menu
- `blog-filter.js` — Blog category filtering

## Apps
Live: Kanesh, Cognithix, Arithmetix, Sparks Studios
Coming Soon: PhotoFlight, Cyla, PaceGrid, Cloudmesh Weather

## Rules
- All pages must include: site-nav, theme toggle, Cloudflare analytics, CSP meta tag
- No `'unsafe-inline'` in script-src CSP
- Privacy pages are referenced by the iOS apps — never change their URLs
- Use CSS variables for all colors (dark/light/manual theme support)
- Images: 660px wide for 3x retina at 220px CSS display
- No cookie consent needed (Cloudflare analytics is cookie-free)

## Deploy
Push to main → GitHub Pages auto-deploys → live at bfgapps.co

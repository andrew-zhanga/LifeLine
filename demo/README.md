# FlareWise interactive prototype

Run `npm install` then `npm run dev -- --port 5173` from this directory. Open http://localhost:5173. Build with `npm run build`.

All flare coordinates, financial figures, demographics and exposure fields are dummy scenarios. They are deterministic and connected: budget/priority change selected sites and portfolio totals; hour changes the wind and footprints; before/after changes the selected sources' footprints.

Try: Explore Eagle Ford → Balanced → change budget → Baseline/After capture → play timeline → Layers → Population → click a map marker or shortlist site.

Stack: React, Vite, MapLibre GL JS and Lucide icons. Uses OpenStreetMap raster tiles and Google Fonts, which require internet access. Local app and scenario calculations do not call data APIs. This is a visual prototype, not a financial optimizer or validated exposure model.

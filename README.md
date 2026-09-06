# Simpaisa Network Playbook 2026

## Current approved edition: 19 pages

[Download the approved playbook](docs/Simpaisa_Network_Playbook_2026_Final.pdf).

The current edition is produced from the supplied 19-page PDF with the Python editing source in `production/`. Its text, tables and vector elements remain in PDF form. The later regional chart refresh was cancelled and is not included.

### Rebuild

```sh
python3 -m venv production/.venv
production/.venv/bin/pip install -r production/requirements.txt
production/.venv/bin/python production/revise_pdf.py
```

The builder reads `production/input/Simpaisa_Network_Playbook_2026_V2_4.pdf` and writes `production/build/Simpaisa_Network_Playbook_2026_Final.pdf`. Optional positional arguments select input and output paths. The approved PDF in `docs/` is not overwritten by a build. Review a rebuilt file before replacing that approved artifact. Fonts and their existing licenses are included.

This is a PDF editing pipeline, not a native PowerPoint source or a 19-page HTML conversion. `production/validation.json` records the source and output checks for this delivery. Those checks establish reproduction and preservation, not independent verification of business claims.

## Earlier HTML edition: 13 pages

The root HTML viewer, standalone HTML and lower-case PDF filenames below belong to the earlier 13-page edition. They have not been updated to the current 19-page document.


Editable offline export of the 13-page v26 review, including the latest page 5 wallet-growth charts and aligned market table, the centered closing page and five dotted office maps.

## Open

1. Extract the ZIP and keep the files and `assets/` folder together.
2. Open `index.html` in a modern browser. No installation, build step, server, account or internet connection is needed.
3. Use the page selector, Previous/Next buttons or left/right arrow keys. Alignment guides can be switched on for layout review.

`closing-page.html` opens only the closing page. `index.html#page-13` opens the same page within the full playbook. The separate `simpaisa-network-playbook.html` download is a self-contained copy of the full viewer.

Each design retains its original 595 × 842 page units. The viewer scales the page to the browser width. Browser printing shows all pages in numerical order, hides controls and review notes, and uses 595 × 842 pt paper. Enable background graphics for faithful printing.

The office strip uses its original dotted SVG on screen. Print media selects a transparent 4× raster copy of that same strip to preserve the dots in Chrome's PDF renderer. Text, charts and the remaining SVG assets retain their existing form.

## PDF downloads

- [Full playbook — 13 A4 pages](docs/simpaisa-network-playbook.pdf)
- [Closing page — A4](docs/simpaisa-closing-page.pdf)

The exported PDFs preserve the current layout and dotted office maps.

## Edit

- `index.html`: all 13 pages and the original collapsible source-review notes, in page order.
- `closing-page.html`: the closing page alone, using the same styles and assets.
- `styles.css`: original page design, embedded-font declarations and a small standalone viewer/print section at the end.
- `app.js`: local page navigation, URL hash support, alignment guides and responsive scaling.
- `assets/`: deduplicated logos, flags, landmark artwork, map SVGs and WOFF2 fonts. Names include content hashes.
- `provenance.json`: source version/hash, retained source links and the asset manifest.

Edit the relevant HTML and CSS directly; there is no generated runtime dependency. If the closing page is edited, update both HTML copies. Text and vector charts remain editable; raster artwork and logo imagery remain separate assets. After source edits, regenerate the self-contained HTML with `python3 scripts/build-standalone.py` (Python standard library only).

## Content and provenance

Page 5 contains the approved introduction, annual wallet-account growth in Pakistan and Bangladesh, and a market table covering wallets, A2A and domestic cards. Its source notes retain reporting periods, metric definitions and primary-source links. The other 12 pages preserve the existing user draft and were not fact-checked again for this update. Export validation checks presentation and functionality; it does not certify business or regulatory claims.

The office maps show the supplied office cities using published city coordinates; they do not identify street addresses. Country silhouettes are independently scaled to fit the strip. They are derived from Natural Earth 1:50 million geometry, projected with D3 Mercator, with GeoNames city points:

- [Natural Earth country geometry](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/) — public domain; [source GeoJSON](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson).
- [GeoNames city coordinates](https://download.geonames.org/export/dump/cities15000.zip) — [CC BY 4.0 and dataset documentation](https://download.geonames.org/export/dump/readme.txt).
- [D3 geographic projections](https://d3js.org/d3-geo/projection) — used during map creation; D3 is not a runtime dependency of this package.

Map changes consist of projecting and scaling country geometry, applying a white dotted pattern, and adding city markers and labels. Source coordinates and attribution are also retained in the office-strip SVG metadata and `provenance.json`.

## Third-party notices

Inter and Poppins fonts retain the SIL Open Font License; their notices are in `licenses/Inter-OFL.txt` and `licenses/Poppins-OFL.txt`. Resolved Lucide/Feather icons retain the notices in `licenses/Lucide-LICENSE.txt`. All these resources are local.

Simpaisa and payment-provider names and logos remain the property and trademarks of their respective owners. This export does not grant new rights to those brand assets. Existing landmark artwork is carried over unchanged from the current review.

## Validation

See `validation.json` for the current source-preservation, page 5 layout, PDF and viewer checks. Historical browser validation is distinguished from the checks run for this update. Source links and the website link are optional outbound links; viewing and navigation do not use the network.

Run `node --test tests/app-resize.test.cjs` for the offline viewer tests. They cover resize feedback, hidden or detached viewers, page navigation and alignment guides.

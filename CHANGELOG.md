# Changelog

## 1.1.0 — 2026-10-20

Initial public release.

- DSH plugin bundle (`dsh.bundle.patch` → `cordis.patch.yml` → `ctx.skills` provider).
- Bundles skill `swiss-grid-design` 1.1:
  - method, parameters (A4–A0, 8/20/32-cell systems), output pipeline notes,
    QA gate and layout recipes;
  - `poster_builder.py`: parametric A-series poster builder with bleed, crop marks,
    grid-overlay proof, Edge/Chromium PDF printing, TrimBox/BleedBox/metadata
    finalisation and `spec.md`;
  - `grid_calculator.py` and `verify_print_pdf.py`;
  - example preview and spec (PDFs generated locally).
- Tests: `node --test` provider/frontmatter tests; package smoke-check with
  `npm pack --dry-run`.

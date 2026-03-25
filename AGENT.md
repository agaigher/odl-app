# App styling guidelines (ODL App)

This document is for agents and contributors working on the **Python FastHTML app** (`app/`). The app shell (`page_layout`, navbar, sidebar) shares a **dark slate** aesthetic aligned with the OpenData.London marketing site.

---

## 1. Where styles live

| Layer | Location | Role |
|--------|----------|------|
| **Global shell** | `app/ui/styles.py` → `get_app_style()` | `:root` tokens, `body.app-layout`, `.main-content`, shared form classes (`odl-input`, `odl-btn-primary`) |
| **Shared/light pages** | `app/ui/styles.py` → `get_shared_style()` | Light page tokens (`--odl-bg`, `--odl-bg-elevated`) used by marketing/catalog content |
| **Page-specific** | Inline `Style(...)` next to the page component (e.g. `app/pages/projects.py` → `_projects_style()`) | Scoped class prefixes (e.g. `pd-*` on Projects) to avoid collisions |
| **Layout chrome** | `app/ui/components.py` | Navbar / sidebar inline styles co-located with `odl_navbar`, `odl_sidebar` |

Prefer **reusing `get_app_style()` tokens** (via matching hex or future `var(--*)` in page CSS) over inventing unrelated palettes.

---

## 2. Design tokens (`:root` in `get_app_style()`)

Use these as the **canonical** app colors and fonts:

- **Fonts:** `--font-display` = Space Grotesk (headings, brand); `--font-body` = Inter (UI body); `--font-mono` = JetBrains Mono (code).
- **Canvas:** `--bg-page` `#14120b` (matched to financialdatasets.ai dark background), `--bg-elevated` `#0f1118`, `--bg-surface` `#141824`, `--bg-card` `#161a2a`, `--bg-muted` `#0c1018`.
- **Text:** `--text-main` `#F8FAFC`, `--text-muted` `#94A3B8`, `--text-faint` `#475569`.
- **Light surfaces (rare in-app):** `--surface-light`, `--text-on-light`, `--border-light` for light cards/modals/catalog rows on dark shell.
- **Brand:** `--accent` `#0284C7`, `--accent-hover` `#0369A1`, `--accent-light` (sky tint for backgrounds).
- **Other:** `--brand-green` success; `--border` subtle white 6% borders; `--shadow` soft elevation.

**Forms:** Use `input.odl-input` / `select.odl-input` and `button.odl-btn-primary` when building standard forms so focus rings and hover match the shell.

---

## 3. Layout and content area

- Main column uses `.main-content` (padding `32px 48px`, background `var(--bg-page)`). Use `.main-content.full-width` when the page needs edge-to-edge content.
- **Page sections** that need a max width: wrap in a container class (e.g. `.pd-page { max-width: 1280px; margin: 0 auto; }`) rather than stretching copy across ultra-wide screens.

---

## 4. Patterns for new screens

1. **Headings:** Space Grotesk or `var(--font-display)` for page titles; tight negative letter-spacing on large titles is consistent with existing pages.
2. **Body / labels:** Inter, 13–14px for secondary text; use muted color for helper text, not mid-gray on mid-gray without contrast check.
3. **Cards:** Dark surfaces (`--bg-card` / `#1a1a1a`–style neutrals), **1px** hairline borders (`--border` or `#262626`-like), **8–12px** radius, **hover** = border brightens slightly; avoid heavy drop shadows unless mimicking an existing pattern.
4. **Primary actions:** Sky blue fill `#0284C7`, hover `#0369A1`; white label text.
5. **Status / pills:** Small caps or uppercase micro-labels, pill radius (`border-radius: 999px`), accent tint for “active” states (see Projects badges).
6. **Icons:** SVG stroke icons via `icon_svg` / `IC` in `app/components.py`; keep stroke weight and corner style consistent with existing icons.

---

## 5. Scoped page CSS (example: Projects)

The Projects dashboard uses a **`pd-` prefix** (`pd-page`, `pd-toolbar`, `pd-card`, …) defined in `_projects_style()`:

- **Neutral zinc-style** fields (`#171717` fill, `#262626` border) for search, selects, and toggles—distinct from but harmonious with `--bg-surface`.
- **Toolbar:** Flex wrap, search flex-grow, view toggle as a **segmented control** (single border, active segment inset).
- **Grid:** `auto-fill` + `minmax(300px, 1fr)`; list mode adds a modifier class on the grid (e.g. `pd-grid--list`).

When adding similar dashboards, **pick a short unique prefix** (`xx-`) and keep all rules in one `Style` block for that page.

---

## 6. Chrome (navbar / sidebar)

- Navbar: sticky top, dark gradient strip, org/project switchers as compact triggers; do not remove `flex-wrap` / `min-width` on brand row if adding controls (prevents clipping on narrow widths).
- Sidebar: dark rail, **active** item = left accent bar + brighter text; match `nav_item` `exact_match_only` behavior when adding routes so the wrong item doesn’t stay “active”.

---

## 7. Do / don’t

**Do**

- Match existing spacing rhythm (8 / 12 / 16 / 20 / 24 / 32).
- Keep contrast high for text on `#080a0f`–`#161a2a` backgrounds.
- Reuse `get_app_style()` classes for generic forms and primary buttons.

**Don’t**

- Introduce a second accent color (e.g. orange/purple) for primary actions without product approval.
- Keep shared/light page background aligned with `https://www.financialdatasets.ai/` by using `--odl-bg: #f7f7f4` in `get_shared_style()`.
- Use `app/ui/styles.py` `get_shared_style()` for authenticated `page_layout` pages only when you intentionally want that lighter marketing/catalog context.

---

## 8. Quick reference (hex)

| Use | Hex |
|-----|-----|
| Page background (dark shell, financialdatasets.ai match) | `#14120b` |
| Shared/light page background (financialdatasets.ai match) | `#f7f7f4` |
| Primary text | `#F8FAFC` |
| Muted text | `#94A3B8` |
| Primary button / links (accent) | `#0284C7` → hover `#0369A1` |
| Error text | `#EF4444` (see `.error-text`) |
| Success | `#10B981` (see `.success-text`) |

---

*Last updated to reflect `get_app_style()` / `get_shared_style()` in `app/ui/styles.py` and Projects patterns in `app/pages/projects.py`.*

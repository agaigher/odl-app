from fasthtml.common import *
from app.supabase_db import db_select

DETAIL_STYLE = Style("""
    .back-link { color: #64748B; text-decoration: none; font-size: 13px; font-weight: 500;
                 display: inline-flex; align-items: center; gap: 5px; margin-bottom: 24px; transition: color 0.2s; }
    .back-link:hover { color: #F8FAFC; }
    .detail-layout { display: grid; grid-template-columns: 1fr 300px; gap: 40px; align-items: start; }
    @media (max-width: 900px) { .detail-layout { grid-template-columns: 1fr; } }

    /* Header */
    .detail-header { margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid rgba(148,163,184,0.1); }
    .detail-cat { font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase;
                  letter-spacing: 0.07em; margin-bottom: 8px; }
    .detail-title { font-size: 26px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.4px; margin-bottom: 10px; }
    .detail-meta { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
    .detail-meta-item { font-size: 13px; color: #64748B; display: flex; align-items: center; gap: 5px; }
    .detail-meta-item strong { color: #94A3B8; }

    /* Tags */
    .tag { display: inline-block; background: rgba(148,163,184,0.08); color: #64748B;
           padding: 2px 9px; border-radius: 4px; font-size: 11px; font-weight: 500;
           margin: 3px 3px 3px 0; }

    /* Section */
    .section-heading { font-size: 13px; font-weight: 600; color: #94A3B8; text-transform: uppercase;
                       letter-spacing: 0.07em; margin: 28px 0 12px; }

    /* Schema table */
    .schema-table { width: 100%; border-collapse: collapse; }
    .schema-table th { text-align: left; padding: 8px 12px; font-size: 11px; font-weight: 600;
                       color: #475569; text-transform: uppercase; letter-spacing: 0.05em;
                       border-bottom: 1px solid rgba(148,163,184,0.1); }
    .schema-table td { padding: 9px 12px; font-size: 13px; color: #CBD5E1;
                       border-bottom: 1px solid rgba(148,163,184,0.06); vertical-align: top; }
    .schema-table tr:last-child td { border-bottom: none; }
    .col-name { font-family: 'Roboto Mono', monospace; font-size: 12px; color: #F8FAFC; white-space: nowrap; }
    .col-type { font-family: 'Roboto Mono', monospace; font-size: 11px; color: #29b5e8;
                background: rgba(41,181,232,0.08); padding: 2px 7px; border-radius: 4px; white-space: nowrap; }
    .col-desc { color: #64748B; font-size: 13px; }

    /* Sample rows table */
    .sample-table-wrap { overflow-x: auto; }
    .sample-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .sample-table th { text-align: left; padding: 8px 12px; font-size: 11px; font-weight: 600;
                       color: #475569; text-transform: uppercase; letter-spacing: 0.05em;
                       background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(148,163,184,0.1);
                       white-space: nowrap; }
    .sample-table td { padding: 9px 12px; color: #94A3B8; border-bottom: 1px solid rgba(148,163,184,0.06);
                       font-family: 'Roboto Mono', monospace; font-size: 12px; white-space: nowrap; }
    .sample-table tr:last-child td { border-bottom: none; }

    /* Sidebar */
    .detail-sidebar { background: #0F1929; border: 1px solid rgba(148,163,184,0.1);
                      border-radius: 10px; padding: 22px; position: sticky; top: 24px; }
    .sidebar-section { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid rgba(148,163,184,0.08); }
    .sidebar-section:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
    .sidebar-label { font-size: 11px; font-weight: 600; color: #475569; text-transform: uppercase;
                     letter-spacing: 0.07em; margin-bottom: 5px; }
    .sidebar-value { font-size: 13px; font-weight: 500; color: #E2E8F0; }
    .access-btn {
        display: block; width: 100%; padding: 10px 16px; border-radius: 7px; text-align: center;
        font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif; text-decoration: none;
        cursor: pointer; border: none; transition: opacity 0.2s; margin-bottom: 10px;
    }
    .btn-primary { background: #29b5e8; color: #020617; }
    .btn-primary:hover { opacity: 0.88; }
    .btn-secondary { background: rgba(41,181,232,0.1); color: #29b5e8;
                     border: 1px solid rgba(41,181,232,0.25); }
    .btn-secondary:hover { background: rgba(41,181,232,0.18); }

    /* Code snippet */
    .code-block { background: #020617; border: 1px solid rgba(148,163,184,0.12); border-radius: 7px;
                  padding: 14px 16px; font-family: 'Roboto Mono', monospace; font-size: 12px;
                  color: #7DD3FC; line-height: 1.6; overflow-x: auto; white-space: pre; margin-top: 6px; }

    /* Table wrapper */
    .table-card { background: #0F1929; border: 1px solid rgba(148,163,184,0.1); border-radius: 8px; overflow: hidden; }
""")


def DatasetDetail(slug: str, session=None):
    try:
        rows = db_select("datasets", {"slug": slug})
        dataset = rows[0] if rows else None
    except Exception:
        dataset = None

    if not dataset:
        return Div(
            A("← Catalog", href="/", cls="back-link"),
            H1("Dataset not found", style="color: #F8FAFC; margin-bottom: 10px;"),
            P("This dataset doesn't exist or you don't have access.", style="color: #64748B;"),
        )

    schema_fields = dataset.get("schema_fields") or []
    sample_rows = dataset.get("sample_rows") or []
    tags = dataset.get("tags") or []
    access = dataset.get("access_methods") or ["api"]
    table_name = slug.replace("-", "_").upper()

    # Schema table
    if schema_fields:
        schema_body = Tbody(*[
            Tr(
                Td(Span(f["name"], cls="col-name")),
                Td(Span(f["type"], cls="col-type")),
                Td(f.get("description", ""), cls="col-desc"),
            )
            for f in schema_fields
        ])
        schema_table = Div(
            Table(
                Thead(Tr(Th("Column"), Th("Type"), Th("Description"))),
                schema_body,
                cls="schema-table"
            ),
            cls="table-card"
        )
    else:
        schema_table = P("Schema not yet documented.", style="color: #64748B; font-size: 13px;")

    # Sample rows table
    if sample_rows and isinstance(sample_rows, list) and len(sample_rows) > 0:
        cols = list(sample_rows[0].keys())
        # Show at most 6 columns to keep it readable
        cols = cols[:6]
        sample_table = Div(
            Div(
                Table(
                    Thead(Tr(*[Th(c) for c in cols])),
                    Tbody(*[
                        Tr(*[Td(str(row.get(c, "")) if row.get(c) is not None else Span("null", style="color: #334155;")) for c in cols])
                        for row in sample_rows
                    ]),
                    cls="sample-table"
                ),
                cls="sample-table-wrap"
            ),
            cls="table-card"
        )
    else:
        sample_table = P("Sample data not available.", style="color: #64748B; font-size: 13px;")

    # Access buttons
    access_btns = []
    if "api" in access:
        access_btns.append(
            A("Get API Access", href=f"/catalog/{slug}/request-access?type=api", cls="access-btn btn-primary")
        )
    if "snowflake" in access:
        access_btns.append(
            A("Add to Snowflake", href=f"/catalog/{slug}/request-access?type=snowflake", cls="access-btn btn-secondary")
        )

    # Sidebar
    sidebar = Div(
        Div(
            Div("Provider", cls="sidebar-label"),
            Div(dataset.get("provider") or "—", cls="sidebar-value"),
            style="margin-bottom: 14px;"
        ),
        Div(
            Div("Category", cls="sidebar-label"),
            Div(dataset.get("category") or "—", cls="sidebar-value"),
            style="margin-bottom: 14px;"
        ),
        Div(
            Div("Update frequency", cls="sidebar-label"),
            Div(dataset.get("update_frequency") or "—", cls="sidebar-value"),
            style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid rgba(148,163,184,0.08);"
        ),
        *access_btns,
        Div(
            Div("Snowflake table name", cls="sidebar-label"),
            Div(f"LONDON_DB.PUBLIC.{table_name}", cls="code-block"),
        ),
        cls="detail-sidebar"
    )

    long_desc = dataset.get("long_description") or dataset.get("description") or ""

    return Div(
        DETAIL_STYLE,
        A("← Catalog", href="/", cls="back-link"),
        Div(
            P(dataset.get("category") or "", cls="detail-cat"),
            H1(dataset.get("title") or "", cls="detail-title"),
            Div(
                Div(
                    Span("Provider: "),
                    Strong(dataset.get("provider") or "—"),
                    cls="detail-meta-item"
                ),
                Div(
                    Span("Updates: "),
                    Strong(dataset.get("update_frequency") or "—"),
                    cls="detail-meta-item"
                ),
                Div(
                    Span("Access: "),
                    Strong(", ".join(a.upper() for a in access)),
                    cls="detail-meta-item"
                ),
                cls="detail-meta"
            ),
            cls="detail-header"
        ),
        Div(
            # Left column
            Div(
                P(long_desc, style="font-size: 14px; color: #94A3B8; line-height: 1.7; margin-bottom: 20px;"),
                Div(*[Span(f"#{t}", cls="tag") for t in tags]) if tags else None,

                P("Schema", cls="section-heading"),
                schema_table,

                P("Sample rows", cls="section-heading"),
                sample_table,

                P("Query example", cls="section-heading"),
                Div(
                    f"SELECT *\nFROM LONDON_DB.PUBLIC.{table_name}\nLIMIT 100;",
                    cls="code-block"
                ),
            ),
            # Right sidebar
            sidebar,
            cls="detail-layout"
        )
    )

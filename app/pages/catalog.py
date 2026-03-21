from fasthtml.common import *
from app.db import datasets_tbl

def dataset_card(dataset):
    """Renders a single dataset card for the catalog."""
    
    # Map category to icon roughly
    icon_map = {
        "Corporate Registries": "🏢",
        "Transportation": "🚇",
        "Real Estate": "🏗️",
        "Financial Regulation": "⚖️"
    }
    icon = icon_map.get(dataset['category'], "📊")

    return Div(
        Div(
            Span(icon, style="font-size: 24px; margin-right: 16px;"),
            Div(
                A(dataset['name'], href=f"/catalog/{dataset['slug']}", cls="dataset-title-link"),
                Div(
                    Span(dataset['provider'], cls="dataset-meta"),
                    Span("•", cls="dataset-meta-sep"),
                    Span(dataset['category'], cls="dataset-meta"),
                    Span("•", cls="dataset-meta-sep"),
                    Span(dataset['update_frequency'], cls="dataset-meta-highlight"),
                    cls="dataset-metadata"
                ),
            ),
            style="display: flex; align-items: flex-start; margin-bottom: 12px;"
        ),
        P(dataset['description'], cls="dataset-description"),
        Div(
            A("View Schema", href=f"/catalog/{dataset['slug']}", cls="action-link"),
            A("Get Connection Details", href=f"/shares?dataset={dataset['slug']}", cls="action-link-primary"),
            cls="dataset-actions"
        ),
        cls="dataset-card"
    )

def DataCatalog():
    
    catalog_style = Style("""
        .catalog-header {
            margin-bottom: 32px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }
        .catalog-title {
            font-size: 28px;
            font-weight: 700;
            margin: 0 0 8px 0;
            color: #F8FAFC;
            letter-spacing: -0.5px;
        }
        .catalog-subtitle {
            color: #94A3B8;
            margin: 0;
            font-size: 15px;
        }
        
        /* Grid Layout */
        .catalog-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 24px;
        }

        /* Card Styles */
        .dataset-card {
            background: #0F172A;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 12px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            transition: all 0.2s ease;
        }
        .dataset-card:hover {
            border-color: rgba(41, 181, 232, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 12px 24px -10px rgba(0,0,0,0.5);
        }
        
        .dataset-title-link {
            font-size: 18px;
            font-weight: 600;
            color: #F8FAFC;
            text-decoration: none;
            display: block;
            margin-bottom: 4px;
            transition: color 0.15s;
        }
        .dataset-title-link:hover {
            color: #29b5e8;
        }
        
        .dataset-metadata {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 6px;
        }
        .dataset-meta {
            color: #64748B;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
        }
        .dataset-meta-sep {
            color: #334155;
            font-size: 13px;
        }
        .dataset-meta-highlight {
            color: #38BDF8;
            font-size: 12px;
            font-weight: 600;
            font-family: 'Roboto Mono', monospace;
            background: rgba(56, 189, 248, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }
        
        .dataset-description {
            color: #94A3B8;
            font-size: 14px;
            line-height: 1.5;
            margin: 0 0 20px 0;
            flex-grow: 1;
        }
        
        .dataset-actions {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-top: auto;
            border-top: 1px solid rgba(148, 163, 184, 0.1);
            padding-top: 16px;
        }
        
        .action-link {
            color: #94A3B8;
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            transition: color 0.2s;
        }
        .action-link:hover {
            color: #F8FAFC;
        }
        
        .action-link-primary {
            color: #29b5e8;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
            transition: opacity 0.2s;
        }
        .action-link-primary:hover {
            opacity: 0.8;
        }
        
        /* Search Bar */
        .catalog-search {
            position: relative;
            width: 320px;
        }
        .catalog-search input {
            width: 100%;
            background: #0F172A;
            border: 1px solid rgba(148, 163, 184, 0.2);
            color: #F8FAFC;
            padding: 10px 16px 10px 36px;
            border-radius: 6px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .catalog-search input:focus {
            outline: none;
            border-color: #29b5e8;
        }
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #64748B;
            pointer-events: none;
        }
    """)
    
    all_datasets = datasets_tbl()

    return Div(
        catalog_style,
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Div(
            Div(
                H1("London Database", cls="catalog-title"),
                P("Discover, query, and synchronize high-fidelity government data.", cls="catalog-subtitle"),
            ),
            Div(
                Span("⚲", cls="search-icon"),
                Input(
                    type="search", 
                    name="q", 
                    placeholder="Search datasets...", 
                    cls="catalog-search input",
                    hx_get="/catalog/search",
                    hx_trigger="keyup changed delay:300ms, search",
                    hx_target="#catalog-grid-container"
                ),
                cls="catalog-search"
            ),
            cls="catalog-header"
        ),
        
        Div(
            *[dataset_card(ds) for ds in all_datasets],
            id="catalog-grid-container",
            cls="catalog-grid"
        )
    )

def SearchCatalogResults(q: str):
    all_datasets = datasets_tbl()
    
    if not q:
        filtered = all_datasets
    else:
        q = q.lower()
        filtered = [
            ds for ds in all_datasets 
            if q in ds['name'].lower() 
            or q in ds['description'].lower() 
            or q in ds['category'].lower()
            or q in ds['provider'].lower()
        ]
        
    return [dataset_card(ds) for ds in filtered]

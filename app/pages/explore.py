"""
Explore module page — AI Chat interface for querying datasets.
"""
from fasthtml.common import *

EXPLORE_STYLE = Style("""
    .explore-wrap {
        max-width: 860px; margin: 0 auto;
        display: flex; flex-direction: column;
        min-height: calc(100vh - 120px);
        padding: 0 24px;
    }

    /* ── Chat area ──────────────────────────────────────────────────── */
    .explore-chat {
        flex: 1; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        padding: 60px 0 40px;
    }

    .explore-logo {
        width: 56px; height: 56px; border-radius: 14px;
        background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.2));
        border: 1px solid rgba(139,92,246,0.3);
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; margin-bottom: 24px;
    }

    .explore-title {
        font-family: 'Space Grotesk', system-ui, sans-serif;
        font-size: 28px; font-weight: 700; color: #F8FAFC;
        letter-spacing: -0.03em; margin-bottom: 10px;
        text-align: center;
    }

    .explore-subtitle {
        font-size: 15px; color: #94A3B8; text-align: center;
        max-width: 480px; line-height: 1.7; margin-bottom: 40px;
    }

    /* ── Suggestion chips ───────────────────────────────────────────── */
    .explore-suggestions {
        display: flex; flex-wrap: wrap; gap: 8px;
        justify-content: center; margin-bottom: 40px;
        max-width: 560px;
    }

    .explore-chip {
        padding: 8px 16px; border-radius: 999px;
        font-size: 13px; font-weight: 500;
        color: #CBD5E1;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        cursor: pointer; transition: all 0.15s;
        text-decoration: none; white-space: nowrap;
    }
    .explore-chip:hover {
        background: rgba(99,102,241,0.12);
        border-color: rgba(139,92,246,0.3);
        color: #E2E8F0;
    }

    /* ── Input bar ──────────────────────────────────────────────────── */
    .explore-input-wrap {
        width: 100%; max-width: 680px;
        margin: 0 auto; padding-bottom: 32px;
    }

    .explore-input-bar {
        display: flex; align-items: center; gap: 0;
        background: rgba(255,255,255,0.04);
        border: 1.5px solid rgba(255,255,255,0.1);
        border-radius: 14px; padding: 6px 6px 6px 18px;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .explore-input-bar:focus-within {
        border-color: rgba(139,92,246,0.4);
        box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
    }

    .explore-input {
        flex: 1; border: none; outline: none;
        background: transparent;
        font-family: 'Inter', sans-serif;
        font-size: 14px; color: #F1F5F9;
        min-width: 0; padding: 10px 0;
    }
    .explore-input::placeholder { color: #64748B; }

    .explore-submit {
        flex-shrink: 0;
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: #fff; border: none; border-radius: 10px;
        padding: 10px 20px; font-size: 13px; font-weight: 600;
        cursor: pointer; font-family: 'Inter', sans-serif;
        transition: opacity 0.15s;
        white-space: nowrap;
    }
    .explore-submit:hover { opacity: 0.88; }

    .explore-disclaimer {
        text-align: center; font-size: 11px;
        color: #64748B; margin-top: 12px;
    }
""")


def ExploreChat():
    """Polished AI Chat placeholder for the Explore module."""
    suggestions = [
        "Company directors for KYC checks",
        "Real-time transport data",
        "Property transactions in London",
        "Air quality monitoring stations",
        "Electoral ward boundaries",
        "Crime statistics by borough",
    ]

    return Div(
        EXPLORE_STYLE,

        # Chat area — centered hero
        Div(
            Div("✦", cls="explore-logo"),
            H1("Explore the London Database", cls="explore-title"),
            P("Ask questions about datasets in natural language. Our AI will search, "
              "filter, and surface the most relevant data for your needs.",
              cls="explore-subtitle"),

            # Suggestion chips
            Div(
                *[Span(s, cls="explore-chip", onclick=f"document.getElementById('explore-q').value = '{s}'; document.getElementById('explore-q').focus();")
                  for s in suggestions],
                cls="explore-suggestions"
            ),
            cls="explore-chat"
        ),

        # Input bar — pinned at bottom
        Div(
            Form(
                Div(
                    Input(
                        type="text", name="query", id="explore-q",
                        placeholder="Ask about London datasets…",
                        autocomplete="off",
                        cls="explore-input"
                    ),
                    Button("Search →", type="submit", cls="explore-submit"),
                    cls="explore-input-bar"
                ),
                method="GET", action="/explore",
            ),
            P("AI‑powered search across 200+ London datasets", cls="explore-disclaimer"),
            cls="explore-input-wrap"
        ),

        cls="explore-wrap"
    )

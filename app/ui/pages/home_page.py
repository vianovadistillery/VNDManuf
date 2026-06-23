"""Home / welcome screen for VND Manuf."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html

# (tab_id, label, short description)
HOME_NAV_ITEMS = [
    ("manufacturing", "Manufacturing", "Products, batches, work orders & inventory"),
    ("contacts", "Contacts", "Customers, suppliers & business contacts"),
    ("sales", "Sales", "Orders, pricing, analytics & import/export"),
    ("crm", "CRM", "Visits, follow-ups & customer relationships"),
    ("reports", "Reports", "Production and business reporting"),
    ("settings", "Settings", "System configuration & reference data"),
    ("training", "Nova University", "Training articles, SOPs & knowledge base"),
]


def _nav_button(tab_id: str, label: str, description: str) -> dbc.Button:
    return dbc.Button(
        [
            html.Div(label, className="vnd-home-nav-label"),
            html.Div(description, className="vnd-home-nav-desc"),
        ],
        id=f"home-nav-{tab_id}",
        color="light",
        className="vnd-home-nav-btn",
        n_clicks=0,
    )


class HomePage:
    @staticmethod
    def get_layout():
        return html.Div(
            [
                # Top third — hero image
                html.Div(
                    [
                        html.Img(
                            src="/assets/via_nova_hero.png",
                            alt="Welcome to Via Nova — New Wave Distillery",
                            className="vnd-home-hero-img",
                        ),
                        html.Div(
                            [
                                html.P(
                                    "NEW WAVE DISTILLERY",
                                    className="vnd-home-eyebrow",
                                ),
                                html.H1(
                                    "Welcome to Via Nova",
                                    className="vnd-home-title",
                                ),
                            ],
                            className="vnd-home-hero-overlay",
                        ),
                    ],
                    className="vnd-home-section vnd-home-hero-section",
                ),
                # Middle third — navigation buttons
                html.Div(
                    [
                        html.H5(
                            "Where would you like to go?",
                            className="vnd-home-nav-heading",
                        ),
                        html.Div(
                            [
                                _nav_button(tab_id, label, desc)
                                for tab_id, label, desc in HOME_NAV_ITEMS
                            ],
                            className="vnd-home-nav-grid",
                        ),
                    ],
                    className="vnd-home-section vnd-home-nav-section",
                ),
                # Bottom third — welcome blurb
                html.Div(
                    [
                        html.H4(
                            "Via Nova Distillery", className="vnd-home-welcome-title"
                        ),
                        html.P(
                            "Via Nova is an Australian distillery crafting gin, vodka "
                            "and ready-to-drink products with innovative distillation "
                            "technology. Our mission is to create cleaner, more approachable "
                            "spirits while reducing waste and improving production efficiency.",
                            className="vnd-home-blurb",
                        ),
                        html.P(
                            "From the still to the bond store, VND Manuf connects "
                            "every part of the operation — production, sales, CRM, "
                            "compliance and training — in one place.",
                            className="vnd-home-blurb vnd-home-blurb-muted",
                        ),
                    ],
                    className="vnd-home-section vnd-home-welcome-section",
                ),
            ],
            className="vnd-home-page",
        )

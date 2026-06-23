"""Customers sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from apps.vndmanuf_sales.ui.components import kpi_card

PRICING_LEVEL_OPTIONS = [
    {"label": "Retail", "value": "retail"},
    {"label": "Wholesale", "value": "wholesale"},
    {"label": "Distributor", "value": "distributor"},
    {"label": "Counter", "value": "counter"},
    {"label": "Trade", "value": "trade"},
    {"label": "Contract", "value": "contract"},
    {"label": "Industrial", "value": "industrial"},
]


def _customer_detail_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(id="sales-customer-detail-title"),
                close_button=False,
            ),
            dbc.ModalBody(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                label="Pricing",
                                tab_id="pricing",
                                children=[
                                    html.P(
                                        "Default tier uses product list prices. Special prices override "
                                        "the tier while active.",
                                        className="text-muted small mt-3 mb-3",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Default pricing level"),
                                                    dcc.Dropdown(
                                                        id="sales-pricing-level",
                                                        options=PRICING_LEVEL_OPTIONS,
                                                        clearable=True,
                                                        placeholder="e.g. wholesale",
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label(" ", className="d-block"),
                                                    dbc.Button(
                                                        "Save pricing level",
                                                        id="sales-pricing-level-save",
                                                        color="primary",
                                                        size="sm",
                                                    ),
                                                ],
                                                md=6,
                                                className="d-flex align-items-end",
                                            ),
                                        ],
                                        className="g-2 mb-2",
                                    ),
                                    html.Div(
                                        id="sales-pricing-level-feedback",
                                        className="small mb-3",
                                    ),
                                    html.Div(
                                        id="sales-customer-tier-prices-section",
                                        className="mb-3",
                                        style={"display": "none"},
                                        children=[
                                            html.H6(
                                                id="sales-customer-tier-prices-heading",
                                                className="mb-2",
                                            ),
                                            dash_table.DataTable(
                                                id="sales-customer-tier-prices-table",
                                                columns=[
                                                    {
                                                        "name": "Product",
                                                        "id": "product",
                                                    },
                                                    {
                                                        "name": "Price (ex GST)",
                                                        "id": "price_ex",
                                                        "presentation": "markdown",
                                                    },
                                                    {
                                                        "name": "Price (inc GST)",
                                                        "id": "price_inc",
                                                        "presentation": "markdown",
                                                    },
                                                ],
                                                data=[],
                                                page_size=10,
                                                page_action="native",
                                                markdown_options={"html": True},
                                                style_table={"overflowX": "auto"},
                                                style_cell={
                                                    "padding": "0.4rem",
                                                    "maxWidth": "240px",
                                                    "overflow": "hidden",
                                                    "textOverflow": "ellipsis",
                                                },
                                                style_header={
                                                    "backgroundColor": "#f8f9fa",
                                                    "fontWeight": "bold",
                                                },
                                            ),
                                        ],
                                    ),
                                    html.H6(
                                        "Add or edit special price", className="mb-2"
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="sales-special-price-product",
                                                    placeholder="Product…",
                                                    disabled=False,
                                                ),
                                                md=4,
                                            ),
                                            dbc.Col(
                                                dbc.RadioItems(
                                                    id="sales-special-price-basis",
                                                    options=[
                                                        {
                                                            "label": " Ex GST",
                                                            "value": "ex",
                                                        },
                                                        {
                                                            "label": " Inc GST",
                                                            "value": "inc",
                                                        },
                                                    ],
                                                    value="ex",
                                                    inline=True,
                                                    className="pt-2",
                                                ),
                                                md=2,
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    id="sales-special-price-amount",
                                                    type="number",
                                                    min=0,
                                                    step=0.01,
                                                    placeholder="Unit ex GST",
                                                ),
                                                md=2,
                                            ),
                                            dbc.Col(
                                                dcc.DatePickerSingle(
                                                    id="sales-special-price-start",
                                                    display_format="YYYY-MM-DD",
                                                    placeholder="Start",
                                                ),
                                                md=2,
                                            ),
                                            dbc.Col(
                                                dcc.DatePickerSingle(
                                                    id="sales-special-price-end",
                                                    display_format="YYYY-MM-DD",
                                                    placeholder="End (optional)",
                                                ),
                                                md=2,
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    "Save",
                                                    id="sales-special-price-save",
                                                    color="primary",
                                                    size="sm",
                                                    className="w-100",
                                                ),
                                                md=1,
                                            ),
                                        ],
                                        className="g-2 mb-2 align-items-center",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Button(
                                                    "New special price",
                                                    id="sales-special-price-new",
                                                    color="link",
                                                    size="sm",
                                                    className="px-0 me-2",
                                                ),
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    "Delete selected",
                                                    id="sales-special-price-delete",
                                                    color="outline-danger",
                                                    size="sm",
                                                ),
                                                width="auto",
                                            ),
                                        ],
                                        className="g-2 mb-2 align-items-center",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Input(
                                                    id="sales-special-price-notes",
                                                    placeholder="Notes (offer description, terms…)",
                                                ),
                                                md=12,
                                            ),
                                        ],
                                        className="g-2 mb-2",
                                    ),
                                    html.Div(
                                        id="sales-special-price-feedback",
                                        className="small mb-2",
                                    ),
                                    html.H6("Special price history", className="mb-2"),
                                    dash_table.DataTable(
                                        id="sales-customer-special-prices-table",
                                        columns=[
                                            {"name": "Product", "id": "product"},
                                            {"name": "Price (ex)", "id": "price_ex"},
                                            {"name": "Start", "id": "start_date"},
                                            {"name": "End", "id": "end_date"},
                                            {"name": "Active", "id": "active"},
                                            {"name": "Notes", "id": "notes"},
                                        ],
                                        data=[],
                                        row_selectable="single",
                                        selected_rows=[],
                                        page_size=8,
                                        style_table={"overflowX": "auto"},
                                        style_cell={
                                            "padding": "0.4rem",
                                            "maxWidth": "200px",
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis",
                                        },
                                        style_header={
                                            "backgroundColor": "#f8f9fa",
                                            "fontWeight": "bold",
                                        },
                                        hidden_columns=[
                                            "special_price_id",
                                            "product_id",
                                            "unit_price_ex_raw",
                                            "start_date_raw",
                                            "end_date_raw",
                                        ],
                                    ),
                                    dcc.Store(
                                        id="sales-special-price-edit-id", data=None
                                    ),
                                ],
                            ),
                            dbc.Tab(
                                label="Delivery sites",
                                tab_id="sites",
                                children=[
                                    html.P(
                                        "Optional delivery addresses for this customer when "
                                        "creating orders (e.g. multiple venues).",
                                        className="text-muted small mt-3 mb-3",
                                    ),
                                    dash_table.DataTable(
                                        id="sales-customer-sites-table",
                                        columns=[
                                            {"name": "Site", "id": "site"},
                                            {"name": "State", "id": "state"},
                                            {"name": "Suburb", "id": "suburb"},
                                            {"name": "Postcode", "id": "postcode"},
                                        ],
                                        data=[],
                                        row_selectable="single",
                                        selected_rows=[],
                                        page_size=8,
                                        style_table={"overflowX": "auto"},
                                        style_cell={"padding": "0.4rem"},
                                        style_header={
                                            "backgroundColor": "#f8f9fa",
                                            "fontWeight": "bold",
                                        },
                                        hidden_columns=["site_id"],
                                    ),
                                    html.H6("Add or edit site", className="mb-2 mt-3"),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Input(
                                                    id="sales-customer-site-name",
                                                    placeholder="Site name",
                                                ),
                                                md=4,
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    id="sales-customer-site-state",
                                                    placeholder="State",
                                                    maxLength=8,
                                                ),
                                                md=2,
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    id="sales-customer-site-suburb",
                                                    placeholder="Suburb",
                                                ),
                                                md=3,
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    id="sales-customer-site-postcode",
                                                    placeholder="Postcode",
                                                    maxLength=10,
                                                ),
                                                md=3,
                                            ),
                                        ],
                                        className="g-2 mb-2",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Button(
                                                    "New site",
                                                    id="sales-customer-site-new",
                                                    color="link",
                                                    size="sm",
                                                    className="px-0 me-2",
                                                ),
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    "Save site",
                                                    id="sales-customer-site-save",
                                                    color="primary",
                                                    size="sm",
                                                    className="me-2",
                                                ),
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    "Delete selected",
                                                    id="sales-customer-site-delete",
                                                    color="outline-danger",
                                                    size="sm",
                                                ),
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                html.Span(
                                                    id="sales-customer-site-feedback",
                                                    className="small text-muted",
                                                ),
                                                className="d-flex align-items-center",
                                            ),
                                        ],
                                        className="g-2 align-items-center",
                                    ),
                                    dcc.Store(
                                        id="sales-customer-site-edit-id", data=None
                                    ),
                                ],
                            ),
                        ],
                        id="sales-customer-detail-tabs",
                        active_tab="pricing",
                    ),
                ],
                style={"maxHeight": "75vh", "overflowY": "auto"},
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="sales-customer-detail-close",
                    color="secondary",
                    size="sm",
                ),
            ),
        ],
        id="sales-customer-detail-modal",
        size="xl",
        is_open=False,
        backdrop="static",
    )


def layout():
    metrics = dbc.Row(
        [
            dbc.Col(kpi_card("sales-customers-total", "Active Customers", "—"), md=3),
            dbc.Col(kpi_card("sales-customers-new", "New This Month", "—"), md=3),
            dbc.Col(
                kpi_card("sales-customers-lifetime", "Lifetime Value (avg)", "—"),
                md=3,
            ),
            dbc.Col(
                kpi_card(
                    "sales-customers-last-order",
                    "Last Order",
                    "—",
                    subtitle="Days since most recent order",
                ),
                md=3,
            ),
        ],
        className="mb-4",
    )

    customers_table = dash_table.DataTable(
        id="sales-customers-table",
        columns=[
            {"name": "Customer", "id": "customer"},
            {"name": "Type", "id": "type"},
            {"name": "Pricing level", "id": "pricing_level"},
            {
                "name": "Active specials",
                "id": "active_specials",
                "type": "numeric",
            },
            {"name": "Email", "id": "email"},
            {"name": "Phone", "id": "phone"},
            {"name": "Lifetime Orders", "id": "orders", "type": "numeric"},
            {"name": "Revenue (Inc GST)", "id": "revenue"},
            {"name": "Last Order", "id": "last_order"},
        ],
        data=[],
        row_selectable="single",
        selected_rows=[],
        page_size=12,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
        hidden_columns=["customer_id"],
    )

    global_special_prices_table = dash_table.DataTable(
        id="sales-global-special-prices-table",
        columns=[
            {"name": "Customer", "id": "customer"},
            {"name": "Product", "id": "product"},
            {"name": "Price (ex)", "id": "price_ex"},
            {"name": "Start", "id": "start_date"},
            {"name": "End", "id": "end_date"},
            {"name": "Active", "id": "active"},
            {"name": "Notes", "id": "notes"},
        ],
        data=[],
        page_size=15,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.4rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    special_offers_panel = dbc.Card(
        [
            dbc.CardHeader(html.H6("Special offers overview", className="mb-0")),
            dbc.CardBody(
                [
                    html.P(
                        "All special pricing offers across customers. Uncheck “Active only” "
                        "to see full history.",
                        className="text-muted small mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-global-special-product-filter",
                                    placeholder="Filter by product…",
                                    clearable=True,
                                ),
                                md=5,
                            ),
                            dbc.Col(
                                dbc.Checklist(
                                    id="sales-global-special-active-only",
                                    options=[
                                        {
                                            "label": " Active offers only",
                                            "value": "active",
                                        }
                                    ],
                                    value=["active"],
                                    inline=True,
                                ),
                                md=4,
                                className="d-flex align-items-center",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Refresh",
                                    id="sales-global-special-refresh",
                                    color="secondary",
                                    size="sm",
                                ),
                                md=3,
                                className="d-flex align-items-center",
                            ),
                        ],
                        className="g-2 mb-3",
                    ),
                    global_special_prices_table,
                ]
            ),
        ],
        className="shadow-sm mb-4",
    )

    return html.Div(
        [
            dcc.Store(id="sales-customers-dashboard-refresh", data=0),
            dcc.Store(id="sales-customer-pricing-refresh", data=0),
            dcc.Store(id="sales-open-customer-id", data=None),
            dcc.Store(id="sales-open-customer-name", data=None),
            _customer_detail_modal(),
            metrics,
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H6("Customer pricing", className="mb-0"),
                                    width="auto",
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Open",
                                        id="sales-customers-open-selected",
                                        color="primary",
                                        size="sm",
                                    ),
                                    width="auto",
                                    className="ms-auto",
                                ),
                            ],
                            className="align-items-center g-2",
                        )
                    ),
                    dbc.CardBody(customers_table),
                ],
                className="shadow-sm mb-4",
            ),
            special_offers_panel,
        ],
        className="sales-customers-tab",
    )

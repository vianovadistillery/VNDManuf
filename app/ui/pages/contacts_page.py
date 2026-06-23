"""Contacts page for Dash UI."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


def _address_block(prefix: str, title: str) -> dbc.Card:
    return dbc.Card(
        [
            dbc.CardHeader(html.H6(title, className="mb-0")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Line 1"),
                                    dbc.Input(
                                        id=f"contacts-form-{prefix}-line1",
                                        type="text",
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Line 2"),
                                    dbc.Input(
                                        id=f"contacts-form-{prefix}-line2",
                                        type="text",
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="g-2 mb-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Suburb"),
                                    dbc.Input(
                                        id=f"contacts-form-{prefix}-suburb",
                                        type="text",
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("State"),
                                    dbc.Input(
                                        id=f"contacts-form-{prefix}-state",
                                        type="text",
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Postcode"),
                                    dbc.Input(
                                        id=f"contacts-form-{prefix}-postcode",
                                        type="text",
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Country"),
                                    dbc.Input(
                                        id=f"contacts-form-{prefix}-country",
                                        type="text",
                                        placeholder="Australia",
                                    ),
                                ],
                                md=2,
                            ),
                        ],
                        className="g-2",
                    ),
                ]
            ),
        ],
        className="mb-3 shadow-sm",
    )


class ContactsPage:
    """Contacts management page."""

    @staticmethod
    def get_layout():
        return html.Div(
            [
                html.H4("Contacts", className="mb-3"),
                dbc.Card(
                    [
                        dbc.CardHeader(html.H6("Search & filters", className="mb-0")),
                        dbc.CardBody(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.InputGroup(
                                            [
                                                dbc.Input(
                                                    id="contacts-search-filter",
                                                    placeholder="Search by name…",
                                                ),
                                                dbc.Button(
                                                    "Search",
                                                    id="contacts-search-btn",
                                                    color="primary",
                                                ),
                                                dbc.Button(
                                                    "Clear",
                                                    id="contacts-clear-btn",
                                                    color="secondary",
                                                    outline=True,
                                                ),
                                            ],
                                            size="sm",
                                        ),
                                        md=4,
                                    ),
                                    dbc.Col(
                                        dbc.Checkbox(
                                            id="contacts-active-filter",
                                            label="Active only",
                                            value=True,
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Checkbox(
                                                id="contacts-filter-customer",
                                                label="Customer",
                                                value=True,
                                                className="me-3 d-inline-block",
                                            ),
                                            dbc.Checkbox(
                                                id="contacts-filter-supplier",
                                                label="Supplier",
                                                value=True,
                                                className="me-3 d-inline-block",
                                            ),
                                            dbc.Checkbox(
                                                id="contacts-filter-other",
                                                label="Other",
                                                value=True,
                                                className="d-inline-block",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        dbc.ButtonGroup(
                                            [
                                                dbc.Button(
                                                    "Add",
                                                    id="contacts-add-btn",
                                                    color="primary",
                                                    size="sm",
                                                ),
                                                dbc.Button(
                                                    "Edit",
                                                    id="contacts-edit-btn",
                                                    color="secondary",
                                                    size="sm",
                                                    disabled=True,
                                                ),
                                                dbc.Button(
                                                    "Delete",
                                                    id="contacts-delete-btn",
                                                    color="danger",
                                                    size="sm",
                                                    outline=True,
                                                    disabled=True,
                                                ),
                                                dbc.Button(
                                                    "Refresh",
                                                    id="contacts-refresh-btn",
                                                    color="secondary",
                                                    size="sm",
                                                    outline=True,
                                                ),
                                            ]
                                        ),
                                        md=2,
                                        className="text-end",
                                    ),
                                ],
                                className="g-2 align-items-center",
                            )
                        ),
                    ],
                    className="mb-3 shadow-sm",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader(html.H6("Directory", className="mb-0")),
                        dbc.CardBody(
                            dash_table.DataTable(
                                id="contacts-table",
                                columns=[
                                    {"name": "Code", "id": "code"},
                                    {"name": "Name", "id": "name"},
                                    {"name": "Contact", "id": "contact_person"},
                                    {"name": "Email", "id": "email"},
                                    {"name": "Phone", "id": "phone"},
                                    {"name": "Suburb", "id": "delivery_suburb"},
                                    {"name": "State", "id": "delivery_state"},
                                    {"name": "Coordinates", "id": "coordinates"},
                                    {
                                        "name": "Customer",
                                        "id": "is_customer",
                                        "type": "text",
                                    },
                                    {
                                        "name": "Supplier",
                                        "id": "is_supplier",
                                        "type": "text",
                                    },
                                    {
                                        "name": "Active",
                                        "id": "is_active",
                                        "type": "text",
                                    },
                                ],
                                data=[],
                                sort_action="native",
                                filter_action="native",
                                page_action="native",
                                page_current=0,
                                page_size=20,
                                style_table={"overflowX": "auto"},
                                style_cell={
                                    "textAlign": "left",
                                    "padding": "0.5rem",
                                    "fontSize": "14px",
                                },
                                style_header={
                                    "backgroundColor": "#f8f9fa",
                                    "fontWeight": "bold",
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"filter_query": "{is_active} = false"},
                                        "backgroundColor": "#fff5f5",
                                    }
                                ],
                                row_selectable="single",
                            )
                        ),
                    ],
                    className="mb-3 shadow-sm",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="contacts-modal-title")),
                        dbc.ModalBody(
                            [
                                html.Div(
                                    id="contacts-form-id-hidden",
                                    style={"display": "none"},
                                ),
                                dbc.Tabs(
                                    [
                                        dbc.Tab(
                                            label="Details",
                                            tab_id="contacts-tab-details",
                                            children=[
                                                html.Div(
                                                    className="pt-3",
                                                    children=[
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Code (auto if blank)"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-code",
                                                                            placeholder="e.g. ABC12",
                                                                        ),
                                                                    ],
                                                                    md=3,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Name *"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-name",
                                                                            required=True,
                                                                        ),
                                                                    ],
                                                                    md=5,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Contact person"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-contact"
                                                                        ),
                                                                    ],
                                                                    md=4,
                                                                ),
                                                            ],
                                                            className="g-2 mb-2",
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Email"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-email",
                                                                            type="email",
                                                                        ),
                                                                    ],
                                                                    md=6,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Phone"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-phone",
                                                                            type="tel",
                                                                        ),
                                                                    ],
                                                                    md=6,
                                                                ),
                                                            ],
                                                            className="g-2 mb-2",
                                                        ),
                                                        dbc.Label(
                                                            "Legacy address (free text)"
                                                        ),
                                                        dbc.Textarea(
                                                            id="contacts-form-address",
                                                            rows=2,
                                                            className="mb-2",
                                                        ),
                                                        dbc.Label("Contact types"),
                                                        dbc.Checkbox(
                                                            id="contacts-form-is-customer",
                                                            label="Customer",
                                                            className="me-3 d-inline-block",
                                                        ),
                                                        dbc.Checkbox(
                                                            id="contacts-form-is-supplier",
                                                            label="Supplier",
                                                            className="me-3 d-inline-block",
                                                        ),
                                                        dbc.Checkbox(
                                                            id="contacts-form-is-other",
                                                            label="Other",
                                                            className="d-inline-block",
                                                        ),
                                                        dbc.Switch(
                                                            id="contacts-form-active",
                                                            label="Active",
                                                            value=True,
                                                            className="mt-3",
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                        dbc.Tab(
                                            label="Addresses",
                                            tab_id="contacts-tab-addresses",
                                            children=[
                                                html.Div(
                                                    className="pt-3",
                                                    children=[
                                                        _address_block(
                                                            "delivery",
                                                            "Delivery address",
                                                        ),
                                                        _address_block(
                                                            "billing", "Billing address"
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                        dbc.Tab(
                                            label="Map location",
                                            tab_id="contacts-tab-location",
                                            children=[
                                                html.Div(
                                                    className="pt-3",
                                                    children=[
                                                        dbc.Alert(
                                                            "Latitude and longitude are used "
                                                            "for the sales customer map. You can "
                                                            "paste coordinates from Google Maps "
                                                            "(right-click → coordinates).",
                                                            color="light",
                                                            className="small py-2",
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Latitude"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-latitude",
                                                                            type="number",
                                                                            step="any",
                                                                            placeholder="-38.1474",
                                                                        ),
                                                                    ],
                                                                    md=6,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Longitude"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-longitude",
                                                                            type="number",
                                                                            step="any",
                                                                            placeholder="144.3607",
                                                                        ),
                                                                    ],
                                                                    md=6,
                                                                ),
                                                            ],
                                                            className="g-2",
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                        dbc.Tab(
                                            label="Commercial",
                                            tab_id="contacts-tab-commercial",
                                            children=[
                                                html.Div(
                                                    className="pt-3",
                                                    children=[
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "ABN"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-abn"
                                                                        ),
                                                                    ],
                                                                    md=4,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "ALM account"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-alm-account"
                                                                        ),
                                                                    ],
                                                                    md=4,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Paramount #"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="contacts-form-paramount-number"
                                                                        ),
                                                                    ],
                                                                    md=4,
                                                                ),
                                                            ],
                                                            className="g-2 mb-2",
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Payment method"
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id="contacts-form-payment-method",
                                                                            options=[
                                                                                {
                                                                                    "label": "Direct",
                                                                                    "value": "direct",
                                                                                },
                                                                                {
                                                                                    "label": "ALM",
                                                                                    "value": "ALM",
                                                                                },
                                                                                {
                                                                                    "label": "Paramount",
                                                                                    "value": "Paramount",
                                                                                },
                                                                                {
                                                                                    "label": "Shopify",
                                                                                    "value": "Shopify",
                                                                                },
                                                                            ],
                                                                            clearable=True,
                                                                        ),
                                                                    ],
                                                                    md=6,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Default pricing level"
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id="contacts-form-default-pricing-level",
                                                                            options=[
                                                                                {
                                                                                    "label": "Retail",
                                                                                    "value": "retail",
                                                                                },
                                                                                {
                                                                                    "label": "Wholesale",
                                                                                    "value": "wholesale",
                                                                                },
                                                                                {
                                                                                    "label": "Distributor",
                                                                                    "value": "distributor",
                                                                                },
                                                                                {
                                                                                    "label": "Counter",
                                                                                    "value": "counter",
                                                                                },
                                                                                {
                                                                                    "label": "Trade",
                                                                                    "value": "trade",
                                                                                },
                                                                                {
                                                                                    "label": "Contract",
                                                                                    "value": "contract",
                                                                                },
                                                                                {
                                                                                    "label": "Industrial",
                                                                                    "value": "industrial",
                                                                                },
                                                                            ],
                                                                            clearable=True,
                                                                        ),
                                                                    ],
                                                                    md=6,
                                                                ),
                                                            ],
                                                            className="g-2 mb-2",
                                                        ),
                                                        dbc.Label("Notes"),
                                                        dbc.Textarea(
                                                            id="contacts-form-notes",
                                                            rows=3,
                                                            className="mb-2",
                                                        ),
                                                        dbc.Label("Xero contact ID"),
                                                        dbc.Input(
                                                            id="contacts-form-xero-id",
                                                            placeholder="UUID",
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                    id="contacts-form-tabs",
                                    active_tab="contacts-tab-details",
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Cancel",
                                    id="contacts-modal-cancel",
                                    color="secondary",
                                    outline=True,
                                ),
                                dbc.Button(
                                    "Save",
                                    id="contacts-modal-save",
                                    color="primary",
                                ),
                            ]
                        ),
                    ],
                    id="contacts-modal",
                    is_open=False,
                    size="xl",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Confirm delete")),
                        dbc.ModalBody(
                            [
                                html.P("Delete this contact?"),
                                html.P(
                                    id="contacts-delete-name",
                                    className="fw-bold text-danger",
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Cancel",
                                    id="contacts-delete-cancel",
                                    color="secondary",
                                    outline=True,
                                ),
                                dbc.Button(
                                    "Delete",
                                    id="contacts-delete-confirm",
                                    color="danger",
                                ),
                            ]
                        ),
                    ],
                    id="contacts-delete-modal",
                    is_open=False,
                ),
            ],
            className="contacts-tab p-1",
        )

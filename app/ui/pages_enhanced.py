"""Enhanced page components for the Dash UI with full CRUD."""

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


class ProductsPageEnhanced:
    """Enhanced products management page with full CRUD."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3("Products Management", className="mb-3"),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    "Add Product",
                                                    id="add-product-btn",
                                                    color="success",
                                                    className="me-2",
                                                ),
                                                dbc.Button(
                                                    "Edit Selected",
                                                    id="edit-product-btn",
                                                    color="primary",
                                                    className="me-2",
                                                    disabled=True,
                                                ),
                                                dbc.Button(
                                                    "Delete Selected",
                                                    id="delete-product-btn",
                                                    color="danger",
                                                    className="me-2",
                                                    disabled=True,
                                                ),
                                                dbc.Button(
                                                    "Refresh",
                                                    id="products-refresh",
                                                    color="info",
                                                ),
                                            ],
                                            width=8,
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        dbc.Label(
                                                            "Filter by Capabilities:",
                                                            className="me-2",
                                                            style={
                                                                "display": "inline-block",
                                                                "marginRight": "10px",
                                                            },
                                                        ),
                                                        dbc.Checkbox(
                                                            id="filter-purchase",
                                                            label="Purchase",
                                                            value=True,
                                                            className="me-2",
                                                            style={
                                                                "display": "inline-block"
                                                            },
                                                        ),
                                                        dbc.Checkbox(
                                                            id="filter-sell",
                                                            label="Sell",
                                                            value=True,
                                                            className="me-2",
                                                            style={
                                                                "display": "inline-block"
                                                            },
                                                        ),
                                                        dbc.Checkbox(
                                                            id="filter-assemble",
                                                            label="Assemble",
                                                            value=True,
                                                            style={
                                                                "display": "inline-block"
                                                            },
                                                        ),
                                                    ],
                                                    style={"textAlign": "right"},
                                                )
                                            ],
                                            width=4,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                            ],
                            width=12,
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dash_table.DataTable(
                                    id="products-table",
                                    columns=[
                                        {"name": "SKU", "id": "sku"},
                                        {"name": "Name", "id": "name"},
                                        {
                                            "name": "Purchase",
                                            "id": "is_purchase",
                                            "presentation": "markdown",
                                        },
                                        {
                                            "name": "Sell",
                                            "id": "is_sell",
                                            "presentation": "markdown",
                                        },
                                        {
                                            "name": "Assemble",
                                            "id": "is_assemble",
                                            "presentation": "markdown",
                                        },
                                        {"name": "Size", "id": "size"},
                                        {"name": "Base Unit", "id": "base_unit"},
                                        {"name": "Pack", "id": "pack"},
                                        {
                                            "name": "Density (kg/L)",
                                            "id": "density_kg_per_l",
                                        },
                                        {"name": "ABV (%)", "id": "abv_percent"},
                                        {"name": "Stock", "id": "stock"},
                                        {"name": "Cost", "id": "primary_assembly_cost"},
                                        {"name": "Active", "id": "is_active"},
                                    ],
                                    data=[],
                                    sort_action="native",
                                    filter_action="native",
                                    page_action="native",
                                    page_current=0,
                                    page_size=25,
                                    row_selectable="single",
                                    selected_rows=[],
                                    style_cell={
                                        "textAlign": "left",
                                        "fontSize": "12px",
                                    },
                                    style_header={
                                        "backgroundColor": "rgb(230, 230, 230)",
                                        "fontWeight": "bold",
                                    },
                                    style_data={
                                        "whiteSpace": "normal",
                                        "height": "auto",
                                    },
                                )
                            ],
                            width=8,
                        ),
                        # Product Detail Panel (Right Side)
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H5(
                                            id="product-detail-title",
                                            children="Select a product...",
                                        ),
                                        html.Hr(),
                                        html.Div(
                                            [
                                                html.P(
                                                    [
                                                        html.Strong("SKU: "),
                                                        html.Span(
                                                            id="product-detail-sku",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Capabilities: "),
                                                        html.Span(
                                                            id="product-detail-capabilities",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Name: "),
                                                        html.Span(
                                                            id="product-detail-name",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Description: "),
                                                        html.Span(
                                                            id="product-detail-description",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Base Unit: "),
                                                        html.Span(
                                                            id="product-detail-base-unit",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Size: "),
                                                        html.Span(
                                                            id="product-detail-size",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Density: "),
                                                        html.Span(
                                                            id="product-detail-density",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("ABV: "),
                                                        html.Span(
                                                            id="product-detail-abv",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.Hr(),
                                                html.H6("Cost & Pricing Analysis"),
                                                html.Div(
                                                    id="product-detail-consolidated-cost-pricing-table"
                                                ),
                                                html.Hr(),
                                                html.P(
                                                    [
                                                        html.Strong("Stock: "),
                                                        html.Span(
                                                            id="product-detail-stock",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Lots: "),
                                                        html.Span(
                                                            id="product-detail-lots-count",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Avg Cost: "),
                                                        html.Span(
                                                            id="product-detail-avg-cost",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Cost Source: "),
                                                        html.Span(
                                                            id="product-detail-cost-source",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                dbc.Button(
                                                    "Adjust Inventory",
                                                    id="adjust-inventory-btn",
                                                    color="primary",
                                                    className="mt-2",
                                                    style={"display": "none"},
                                                ),
                                                html.Hr(),
                                                html.P(
                                                    [
                                                        html.Strong("Restock Level: "),
                                                        html.Span(
                                                            id="product-detail-restock",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong("Active: "),
                                                        html.Span(
                                                            id="product-detail-active",
                                                            children="-",
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="card p-3",
                                    style={"position": "sticky", "top": "20px"},
                                )
                            ],
                            width=4,
                        ),
                    ]
                ),
                # Add/Edit Product Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="product-modal-title")),
                        dbc.ModalBody(
                            [
                                dbc.Accordion(
                                    [
                                        # Basic Information
                                        dbc.AccordionItem(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("SKU *"),
                                                                dbc.Input(
                                                                    id="product-sku",
                                                                    placeholder="Enter SKU",
                                                                    required=True,
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Name *"),
                                                                dbc.Input(
                                                                    id="product-name",
                                                                    placeholder="Enter product name",
                                                                    required=True,
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Product Capabilities *"
                                                                ),
                                                                html.Div(
                                                                    [
                                                                        dbc.Checkbox(
                                                                            id="product-is-purchase",
                                                                            label="Purchase",
                                                                            value=False,
                                                                            className="me-3",
                                                                        ),
                                                                        dbc.Checkbox(
                                                                            id="product-is-sell",
                                                                            label="Sell",
                                                                            value=False,
                                                                            className="me-3",
                                                                        ),
                                                                        dbc.Checkbox(
                                                                            id="product-is-assemble",
                                                                            label="Assemble",
                                                                            value=False,
                                                                        ),
                                                                    ]
                                                                ),
                                                            ],
                                                            width=8,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Is Active"),
                                                                dbc.Select(
                                                                    id="product-is-active",
                                                                    options=[
                                                                        {
                                                                            "label": "Yes",
                                                                            "value": "true",
                                                                        },
                                                                        {
                                                                            "label": "No",
                                                                            "value": "false",
                                                                        },
                                                                    ],
                                                                    value="true",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Description"
                                                                ),
                                                                dbc.Textarea(
                                                                    id="product-description",
                                                                    placeholder="Enter description",
                                                                ),
                                                            ],
                                                            width=12,
                                                        )
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "EAN13 Barcode"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-ean13",
                                                                    placeholder="EAN13",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("DG Flag"),
                                                                dbc.Select(
                                                                    id="product-dgflag",
                                                                    options=[
                                                                        {
                                                                            "label": "Y",
                                                                            "value": "Y",
                                                                        },
                                                                        {
                                                                            "label": "N",
                                                                            "value": "N",
                                                                        },
                                                                    ],
                                                                    placeholder="Dangerous goods",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Raw Material Group ID"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-raw-material-group-id",
                                                                    placeholder="Raw Material Group ID",
                                                                ),
                                                            ],
                                                            width=12,
                                                        )
                                                    ]
                                                ),
                                            ],
                                            title="Basic Information",
                                            item_id="basic",
                                        ),
                                        # Physical Properties
                                        dbc.AccordionItem(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Base Unit"),
                                                                dcc.Dropdown(
                                                                    id="product-base-unit",
                                                                    placeholder="Select base unit",
                                                                    searchable=True,
                                                                    clearable=True,
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Size"),
                                                                dbc.Input(
                                                                    id="product-size",
                                                                    placeholder="Size",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Weight (kg)"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-weight",
                                                                    type="number",
                                                                    step="0.001",
                                                                    placeholder="0.000",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Pack"),
                                                                dbc.Input(
                                                                    id="product-pack",
                                                                    type="number",
                                                                    placeholder="Pack quantity",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Package Type"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-pkge",
                                                                    type="number",
                                                                    placeholder="Package type",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Density (kg/L)"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-density",
                                                                    type="number",
                                                                    step="0.001",
                                                                    placeholder="0.000",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("ABV (%)"),
                                                                dbc.Input(
                                                                    id="product-abv",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="0.00",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col([], width=6),
                                                    ],
                                                    className="mb-3",
                                                ),
                                            ],
                                            title="Physical Properties",
                                            item_id="physical",
                                        ),
                                        # Sales & Pricing (conditional - grey if is_sell=False)
                                        dbc.AccordionItem(
                                            [
                                                html.Div(
                                                    id="sales-pricing-disabled-notice",
                                                    style={"display": "none"},
                                                ),
                                                dash_table.DataTable(
                                                    id="product-pricing-table",
                                                    columns=[
                                                        {
                                                            "name": "Price Level",
                                                            "id": "price_level",
                                                            "editable": False,
                                                        },
                                                        {
                                                            "name": "Inc GST",
                                                            "id": "inc_gst",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Ex GST",
                                                            "id": "ex_gst",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Excise",
                                                            "id": "excise",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                            "editable": False,
                                                        },
                                                    ],
                                                    data=[
                                                        {
                                                            "price_level": "Retail",
                                                            "inc_gst": None,
                                                            "ex_gst": None,
                                                            "excise": None,
                                                        },
                                                        {
                                                            "price_level": "Wholesale",
                                                            "inc_gst": None,
                                                            "ex_gst": None,
                                                            "excise": None,
                                                        },
                                                        {
                                                            "price_level": "Distributor",
                                                            "inc_gst": None,
                                                            "ex_gst": None,
                                                            "excise": None,
                                                        },
                                                        {
                                                            "price_level": "Counter",
                                                            "inc_gst": None,
                                                            "ex_gst": None,
                                                            "excise": None,
                                                        },
                                                        {
                                                            "price_level": "Trade",
                                                            "inc_gst": None,
                                                            "ex_gst": None,
                                                            "excise": None,
                                                        },
                                                        {
                                                            "price_level": "Contract",
                                                            "inc_gst": None,
                                                            "ex_gst": None,
                                                            "excise": None,
                                                        },
                                                        {
                                                            "price_level": "Industrial",
                                                            "inc_gst": None,
                                                            "ex_gst": None,
                                                            "excise": None,
                                                        },
                                                    ],
                                                    editable=True,
                                                    style_cell={
                                                        "textAlign": "left",
                                                        "fontSize": "12px",
                                                    },
                                                    style_header={
                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                        "fontWeight": "bold",
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            "if": {
                                                                "filter_query": "{is_sell} = False"
                                                            },
                                                            "backgroundColor": "#f0f0f0",
                                                            "color": "#999",
                                                        },
                                                    ],
                                                ),
                                            ],
                                            title="Sales & Pricing",
                                            item_id="sales-pricing",
                                        ),
                                        # Usage Cost Settings (conditional - grey based on capabilities)
                                        dbc.AccordionItem(
                                            [
                                                html.Div(
                                                    id="cost-settings-disabled-notice",
                                                    style={"display": "none"},
                                                ),
                                                dash_table.DataTable(
                                                    id="product-cost-table",
                                                    columns=[
                                                        {
                                                            "name": "Cost Type",
                                                            "id": "cost_type",
                                                            "editable": False,
                                                        },
                                                        {
                                                            "name": "Ex GST",
                                                            "id": "ex_gst",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Inc GST",
                                                            "id": "inc_gst",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Tax Included",
                                                            "id": "tax_included",
                                                            "presentation": "markdown",
                                                            "editable": False,
                                                        },
                                                    ],
                                                    data=[
                                                        {
                                                            "cost_type": "Purchase Cost",
                                                            "ex_gst": None,
                                                            "inc_gst": None,
                                                            "tax_included": False,
                                                        },
                                                        {
                                                            "cost_type": "Usage Cost",
                                                            "ex_gst": None,
                                                            "inc_gst": None,
                                                            "tax_included": False,
                                                        },
                                                        {
                                                            "cost_type": "Manufactured Cost",
                                                            "ex_gst": None,
                                                            "inc_gst": None,
                                                            "tax_included": "N/A",
                                                        },
                                                    ],
                                                    editable=True,
                                                    style_cell={
                                                        "textAlign": "left",
                                                        "fontSize": "12px",
                                                    },
                                                    style_header={
                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                        "fontWeight": "bold",
                                                    },
                                                ),
                                            ],
                                            title="Usage Cost Settings",
                                            item_id="cost-settings",
                                        ),
                                        # Assembly Section (conditional - grey if is_assemble=False)
                                        dbc.AccordionItem(
                                            [
                                                html.Div(
                                                    id="assembly-disabled-notice",
                                                    style={"display": "none"},
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "New Assembly",
                                                                    id="new-assembly-btn",
                                                                    color="success",
                                                                    className="me-2",
                                                                    size="sm",
                                                                ),
                                                                dbc.Button(
                                                                    "Edit",
                                                                    id="edit-assembly-btn",
                                                                    color="primary",
                                                                    className="me-2",
                                                                    size="sm",
                                                                    disabled=True,
                                                                ),
                                                                dbc.Button(
                                                                    "Duplicate",
                                                                    id="duplicate-assembly-btn",
                                                                    color="info",
                                                                    className="me-2",
                                                                    size="sm",
                                                                    disabled=True,
                                                                ),
                                                                dbc.Button(
                                                                    "Archive",
                                                                    id="archive-assembly-btn",
                                                                    color="warning",
                                                                    size="sm",
                                                                    disabled=True,
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dash_table.DataTable(
                                                    id="product-assemblies-table",
                                                    columns=[
                                                        {
                                                            "name": "Version",
                                                            "id": "version",
                                                        },
                                                        {
                                                            "name": "Sequence",
                                                            "id": "sequence",
                                                        },
                                                        {
                                                            "name": "Ratio",
                                                            "id": "ratio",
                                                        },
                                                        {
                                                            "name": "Yield Factor",
                                                            "id": "yield_factor",
                                                        },
                                                        {
                                                            "name": "Is Primary",
                                                            "id": "is_primary",
                                                            "presentation": "markdown",
                                                        },
                                                        {"name": "Cost", "id": "cost"},
                                                        {
                                                            "name": "Actions",
                                                            "id": "actions",
                                                            "presentation": "markdown",
                                                        },
                                                    ],
                                                    data=[],
                                                    sort_action="native",
                                                    row_selectable="single",
                                                    style_cell={
                                                        "textAlign": "left",
                                                        "fontSize": "12px",
                                                    },
                                                    style_header={
                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                        "fontWeight": "bold",
                                                    },
                                                ),
                                            ],
                                            title="Assembly",
                                            item_id="assembly",
                                        ),
                                        # Cost Information (Legacy - keeping for backward compatibility but can be removed)
                                        dbc.AccordionItem(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Purchase Cost"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-purcost",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Purchase Tax"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-purtax",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Wholesale Cost"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-wholesalecost",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Excise Amount"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-excise-amount",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Tax Included"
                                                                ),
                                                                dbc.Select(
                                                                    id="product-taxinc",
                                                                    options=[
                                                                        {
                                                                            "label": "Y",
                                                                            "value": "Y",
                                                                        },
                                                                        {
                                                                            "label": "N",
                                                                            "value": "N",
                                                                        },
                                                                    ],
                                                                    placeholder="Tax included?",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Sales Tax Code"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-salestaxcde",
                                                                    placeholder="Tax code",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            title="Cost",
                                            item_id="cost",
                                        ),
                                        # Pricing
                                        dbc.AccordionItem(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Wholesale"),
                                                                dbc.Input(
                                                                    id="product-wholesalecde",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Retail"),
                                                                dbc.Input(
                                                                    id="product-retailcde",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Counter"),
                                                                dbc.Input(
                                                                    id="product-countercde",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Trade"),
                                                                dbc.Input(
                                                                    id="product-tradecde",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Contract"),
                                                                dbc.Input(
                                                                    id="product-contractcde",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Industrial"),
                                                                dbc.Input(
                                                                    id="product-industrialcde",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=4,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Distributor"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-distributorcde",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col([], width=6),
                                                    ]
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Discount 1"),
                                                                dbc.Input(
                                                                    id="product-disccdeone",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Discount 2"),
                                                                dbc.Input(
                                                                    id="product-disccdetwo",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="$0.00",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                    ],
                                                    className="mt-3",
                                                ),
                                            ],
                                            title="Pricing",
                                            item_id="pricing",
                                        ),
                                        # Raw Material Usage Fields
                                        dbc.AccordionItem(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Supplier ID"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-supplier-id",
                                                                    placeholder="Supplier ID",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Purchase Unit"
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="product-purchase-unit",
                                                                    placeholder="Select purchase unit",
                                                                    searchable=True,
                                                                    clearable=True,
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Purchase Volume"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-purchase-volume",
                                                                    type="number",
                                                                    step="0.001",
                                                                    placeholder="0.000",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Usage Cost"),
                                                                dbc.Input(
                                                                    id="product-usage-cost",
                                                                    type="number",
                                                                    step="0.01",
                                                                    placeholder="0.00",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Usage Unit"),
                                                                dcc.Dropdown(
                                                                    id="product-usage-unit",
                                                                    placeholder="Select usage unit",
                                                                    searchable=True,
                                                                    clearable=True,
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Restock Level"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-restock-level",
                                                                    type="number",
                                                                    step="0.001",
                                                                    placeholder="0.000",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            title="Raw Material Usage",
                                            item_id="raw-material",
                                        ),
                                        # Finished Good Specific Fields
                                        dbc.AccordionItem(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Formula ID"),
                                                                dbc.Input(
                                                                    id="product-formula-id",
                                                                    placeholder="Formula ID",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Formula Revision"
                                                                ),
                                                                dbc.Input(
                                                                    id="product-formula-revision",
                                                                    type="number",
                                                                    placeholder="Revision number",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                    ]
                                                )
                                            ],
                                            title="Assembly",
                                            item_id="finished-good",
                                        ),
                                    ],
                                    start_collapsed=True,
                                    active_item="basic",
                                ),
                                html.Div(
                                    id="product-form-hidden", style={"display": "none"}
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Save",
                                    id="product-save-btn",
                                    color="primary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Cancel", id="product-cancel-btn", color="secondary"
                                ),
                            ]
                        ),
                    ],
                    id="product-form-modal",
                    is_open=False,
                    size="xl",
                    backdrop="static",
                ),
                # Delete Confirmation Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
                        dbc.ModalBody(
                            [
                                html.P("Are you sure you want to delete this product?"),
                                html.P(
                                    id="delete-product-name",
                                    className="text-danger fw-bold",
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Delete",
                                    id="delete-confirm-btn",
                                    color="danger",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Cancel", id="delete-cancel-btn", color="secondary"
                                ),
                            ]
                        ),
                    ],
                    id="delete-confirm-modal",
                    is_open=False,
                ),
                # Inventory Adjustment Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Adjust Inventory")),
                        dbc.ModalBody(
                            [
                                html.P(
                                    [
                                        html.Strong("Product: "),
                                        html.Span(
                                            id="adjust-product-name", children="-"
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                html.P(
                                    [
                                        html.Strong("Current Stock: "),
                                        html.Span(
                                            id="adjust-current-stock", children="-"
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Adjustment Type *"),
                                                dbc.Select(
                                                    id="adjust-type",
                                                    options=[
                                                        {
                                                            "label": "Set Count",
                                                            "value": "SET_COUNT",
                                                        },
                                                        {
                                                            "label": "Increase",
                                                            "value": "INCREASE",
                                                        },
                                                        {
                                                            "label": "Decrease",
                                                            "value": "DECREASE",
                                                        },
                                                    ],
                                                    value="INCREASE",
                                                    required=True,
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Quantity (kg) *"),
                                                dbc.Input(
                                                    id="adjust-quantity",
                                                    type="number",
                                                    step="0.001",
                                                    required=True,
                                                    min=0,
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Unit Cost"),
                                                dbc.Input(
                                                    id="adjust-unit-cost",
                                                    type="number",
                                                    step="0.01",
                                                    placeholder="Leave empty for default",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Lot Code"),
                                                dbc.Input(
                                                    id="adjust-lot-code",
                                                    placeholder="Auto-generated if empty",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Notes"),
                                                dbc.Textarea(
                                                    id="adjust-notes",
                                                    rows=3,
                                                    placeholder="Optional notes for this adjustment",
                                                ),
                                            ],
                                            width=12,
                                        )
                                    ]
                                ),
                                html.Div(
                                    id="adjust-product-id-hidden",
                                    style={"display": "none"},
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Apply Adjustment",
                                    id="adjust-confirm-btn",
                                    color="primary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Cancel", id="adjust-cancel-btn", color="secondary"
                                ),
                            ]
                        ),
                    ],
                    id="adjust-inventory-modal",
                    is_open=False,
                    size="lg",
                ),
                # Assembly Form Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="assembly-form-title")),
                        dbc.ModalBody(
                            [
                                html.Div(
                                    id="assembly-formula-id", style={"display": "none"}
                                ),
                                html.Div(
                                    id="assembly-product-id", style={"display": "none"}
                                ),
                                html.Div(
                                    id="assembly-parent-product-id-hidden",
                                    style={"display": "none"},
                                ),
                                dbc.Form(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Formula Code *"),
                                                        dbc.Input(
                                                            id="assembly-code",
                                                            required=True,
                                                            maxLength=50,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Version"),
                                                        dbc.Input(
                                                            id="assembly-version",
                                                            type="number",
                                                            value=1,
                                                            min=1,
                                                            readonly=True,
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Formula Name *"),
                                                        dbc.Input(
                                                            id="assembly-name",
                                                            required=True,
                                                            maxLength=200,
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Hr(),
                                        html.H5("Assembly Lines", className="mb-3"),
                                        html.P(
                                            "Total Cost: ",
                                            className="mb-2",
                                            style={"fontWeight": "bold"},
                                        ),
                                        html.P(
                                            id="assembly-total-cost",
                                            children="$0.00",
                                            className="mb-3",
                                            style={
                                                "fontSize": "16px",
                                                "color": "green",
                                            },
                                        ),
                                        dash_table.DataTable(
                                            id="assembly-lines-table",
                                            columns=[
                                                {
                                                    "name": "Seq",
                                                    "id": "sequence",
                                                    "type": "numeric",
                                                    "editable": True,
                                                },
                                                {
                                                    "name": "Product",
                                                    "id": "product_search",
                                                    "presentation": "dropdown",
                                                    "editable": True,
                                                },
                                                {
                                                    "name": "Product SKU",
                                                    "id": "product_sku",
                                                    "editable": False,
                                                },
                                                {
                                                    "name": "Product Name",
                                                    "id": "product_name",
                                                    "editable": False,
                                                },
                                                {
                                                    "name": "Quantity",
                                                    "id": "quantity",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                    "editable": True,
                                                },
                                                {
                                                    "name": "Unit",
                                                    "id": "unit",
                                                    "presentation": "dropdown",
                                                    "editable": True,
                                                },
                                                {
                                                    "name": "Qty (kg)",
                                                    "id": "quantity_kg",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                    "editable": False,
                                                },
                                                {
                                                    "name": "Unit Cost",
                                                    "id": "unit_cost",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".2f"},
                                                    "editable": False,
                                                },
                                                {
                                                    "name": "Line Cost",
                                                    "id": "line_cost",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".2f"},
                                                    "editable": False,
                                                },
                                                {
                                                    "name": "Notes",
                                                    "id": "notes",
                                                    "editable": True,
                                                },
                                            ],
                                            data=[],
                                            editable=True,
                                            row_deletable=True,
                                            style_cell={
                                                "textAlign": "left",
                                                "fontSize": "11px",
                                            },
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Add Line",
                                                            id="assembly-add-line-btn",
                                                            color="info",
                                                            size="sm",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Lookup Product",
                                                            id="assembly-lookup-product-btn",
                                                            color="secondary",
                                                            size="sm",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Input(
                                                            id="assembly-product-search",
                                                            placeholder="Search by SKU or name...",
                                                            size="sm",
                                                            className="ms-auto",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Save",
                                    id="assembly-save-btn",
                                    color="primary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Cancel",
                                    id="assembly-cancel-btn",
                                    color="secondary",
                                ),
                            ]
                        ),
                    ],
                    id="assembly-form-modal",
                    is_open=False,
                    size="xl",
                ),
            ],
            fluid=True,
        )


# Export enhanced page
products_page_enhanced = ProductsPageEnhanced()

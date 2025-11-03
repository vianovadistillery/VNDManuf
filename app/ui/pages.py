"""Page components for the Dash UI."""

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


class ProductsPage:
    """Products management page."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="products-tab",
                                    active_tab="list",
                                    children=[
                                        dbc.Tab(label="Product List", tab_id="list"),
                                        dbc.Tab(label="Add Product", tab_id="add"),
                                    ],
                                    className="mb-4",
                                )
                            ]
                        )
                    ]
                ),
                # Product List Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Refresh",
                                                            id="products-refresh",
                                                            color="primary",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Export CSV",
                                                            id="products-export-csv",
                                                            color="info",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Add Product",
                                                            id="add-product",
                                                            color="success",
                                                        ),
                                                    ]
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="products-table",
                                            columns=[],
                                            data=[],
                                            sort_action="native",
                                            filter_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=20,
                                            style_cell={"textAlign": "left"},
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="products-list-content",
                                )
                            ]
                        )
                    ]
                ),
                # Add Product Form (Modal)
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Add New Product")),
                        dbc.ModalBody(
                            [
                                dbc.Form(
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
                                                        dbc.Label("Description"),
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
                                                        dbc.Label("Density (kg/L)"),
                                                        dbc.Input(
                                                            id="product-density",
                                                            type="number",
                                                            step="0.001",
                                                            placeholder="0.000",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
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
                                            ],
                                            className="mb-3",
                                        ),
                                    ]
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Submit",
                                    id="product-submit",
                                    color="primary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Cancel", id="product-cancel", color="secondary"
                                ),
                            ]
                        ),
                    ],
                    id="product-form",
                    is_open=False,
                ),
            ],
            fluid=True,
        )


class BatchesPage:
    """Work Orders and Batches management page."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="batches-tab",
                                    active_tab="list",
                                    children=[
                                        dbc.Tab(label="Batch List", tab_id="list"),
                                        dbc.Tab(label="Print Preview", tab_id="print"),
                                    ],
                                    className="mb-4",
                                )
                            ]
                        )
                    ]
                ),
                # Batch List Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Refresh",
                                            id="batches-refresh",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="batches-table",
                                            columns=[],
                                            data=[],
                                            sort_action="native",
                                            filter_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=20,
                                            row_selectable="single",
                                            style_cell={"textAlign": "left"},
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="batches-list-content",
                                )
                            ]
                        )
                    ]
                ),
                # Print Preview Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Print Selected Batch",
                                            id="batch-print-btn",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="batch-print-preview"),
                                    ],
                                    id="batches-print-content",
                                )
                            ]
                        )
                    ]
                ),
            ],
            fluid=True,
        )


class InventoryPage:
    """Inventory management page."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H4("Inventory Lots"),
                                dbc.Button(
                                    "Refresh",
                                    id="inventory-refresh",
                                    color="primary",
                                    className="mb-3",
                                ),
                                dash_table.DataTable(
                                    id="inventory-table",
                                    columns=[],
                                    data=[],
                                    sort_action="native",
                                    filter_action="native",
                                    page_action="native",
                                    page_current=0,
                                    page_size=20,
                                    style_cell={"textAlign": "left"},
                                    style_header={
                                        "backgroundColor": "rgb(230, 230, 230)",
                                        "fontWeight": "bold",
                                    },
                                ),
                            ]
                        )
                    ]
                )
            ],
            fluid=True,
        )


class PricingPage:
    """Pricing management page."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H4("Price Lists"),
                                dbc.Button(
                                    "Refresh",
                                    id="pricing-refresh",
                                    color="primary",
                                    className="mb-3",
                                ),
                                dash_table.DataTable(
                                    id="pricing-table",
                                    columns=[],
                                    data=[],
                                    sort_action="native",
                                    filter_action="native",
                                    page_action="native",
                                    page_current=0,
                                    page_size=20,
                                    style_cell={"textAlign": "left"},
                                    style_header={
                                        "backgroundColor": "rgb(230, 230, 230)",
                                        "fontWeight": "bold",
                                    },
                                ),
                            ]
                        )
                    ]
                )
            ],
            fluid=True,
        )


class PackagingPage:
    """Packaging and unit conversion page."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="packaging-tab",
                                    active_tab="units",
                                    children=[
                                        dbc.Tab(label="Pack Units", tab_id="units"),
                                        dbc.Tab(
                                            label="Unit Conversion", tab_id="convert"
                                        ),
                                    ],
                                    className="mb-4",
                                )
                            ]
                        )
                    ]
                ),
                # Pack Units Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H4("Pack Units"),
                                        dbc.Button(
                                            "Refresh",
                                            id="packaging-refresh",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="packaging-table",
                                            columns=[],
                                            data=[],
                                            sort_action="native",
                                            filter_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=20,
                                            style_cell={"textAlign": "left"},
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="packaging-units-content",
                                )
                            ]
                        )
                    ]
                ),
                # Unit Conversion Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Unit Conversion"),
                                        dbc.CardBody(
                                            [
                                                dbc.Form(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Product ID"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="pack-product-id",
                                                                            placeholder="Enter product ID",
                                                                        ),
                                                                    ],
                                                                    width=6,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Quantity"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="pack-quantity",
                                                                            type="number",
                                                                            step="0.001",
                                                                            placeholder="0.000",
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
                                                                            "From Unit"
                                                                        ),
                                                                        dbc.Select(
                                                                            id="pack-from-unit",
                                                                            options=[
                                                                                {
                                                                                    "label": "kg",
                                                                                    "value": "kg",
                                                                                },
                                                                                {
                                                                                    "label": "L",
                                                                                    "value": "L",
                                                                                },
                                                                                {
                                                                                    "label": "CAN",
                                                                                    "value": "CAN",
                                                                                },
                                                                                {
                                                                                    "label": "4PK",
                                                                                    "value": "4PK",
                                                                                },
                                                                                {
                                                                                    "label": "CTN",
                                                                                    "value": "CTN",
                                                                                },
                                                                            ],
                                                                            placeholder="Select from unit",
                                                                        ),
                                                                    ],
                                                                    width=6,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "To Unit"
                                                                        ),
                                                                        dbc.Select(
                                                                            id="pack-to-unit",
                                                                            options=[
                                                                                {
                                                                                    "label": "kg",
                                                                                    "value": "kg",
                                                                                },
                                                                                {
                                                                                    "label": "L",
                                                                                    "value": "L",
                                                                                },
                                                                                {
                                                                                    "label": "CAN",
                                                                                    "value": "CAN",
                                                                                },
                                                                                {
                                                                                    "label": "4PK",
                                                                                    "value": "4PK",
                                                                                },
                                                                                {
                                                                                    "label": "CTN",
                                                                                    "value": "CTN",
                                                                                },
                                                                            ],
                                                                            placeholder="Select to unit",
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
                                                                        dbc.Button(
                                                                            "Convert",
                                                                            id="pack-convert-btn",
                                                                            color="primary",
                                                                        )
                                                                    ]
                                                                )
                                                            ]
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                html.Div(id="pack-conversion-result", className="mt-3"),
                            ],
                            width=8,
                        )
                    ],
                    id="packaging-convert-content",
                    style={"display": "none"},
                ),
            ],
            fluid=True,
        )


class InvoicesPage:
    """Invoices management page."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="invoices-tab",
                                    active_tab="list",
                                    children=[
                                        dbc.Tab(label="Invoice List", tab_id="list"),
                                        dbc.Tab(label="Print Preview", tab_id="print"),
                                    ],
                                    className="mb-4",
                                )
                            ]
                        )
                    ]
                ),
                # Invoice List Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Refresh",
                                            id="invoices-refresh",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="invoices-table",
                                            columns=[],
                                            data=[],
                                            sort_action="native",
                                            filter_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=20,
                                            row_selectable="single",
                                            style_cell={"textAlign": "left"},
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="invoices-list-content",
                                )
                            ]
                        )
                    ]
                ),
                # Print Preview Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Print Selected Invoice",
                                            id="invoice-print-btn",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="invoice-print-preview"),
                                    ],
                                    id="invoices-print-content",
                                )
                            ]
                        )
                    ]
                ),
            ],
            fluid=True,
        )


class ReportsPage:
    """Reports generation page."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Generate Report"),
                                        dbc.CardBody(
                                            [
                                                dbc.Form(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Report Type"
                                                                        ),
                                                                        dbc.Select(
                                                                            id="report-type",
                                                                            options=[
                                                                                {
                                                                                    "label": "Inventory Report",
                                                                                    "value": "inventory",
                                                                                },
                                                                                {
                                                                                    "label": "Sales Report",
                                                                                    "value": "sales",
                                                                                },
                                                                                {
                                                                                    "label": "Production Report",
                                                                                    "value": "production",
                                                                                },
                                                                                {
                                                                                    "label": "Financial Report",
                                                                                    "value": "financial",
                                                                                },
                                                                            ],
                                                                            placeholder="Select report type",
                                                                        ),
                                                                    ],
                                                                    width=6,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Start Date"
                                                                        ),
                                                                        dcc.DatePickerSingle(
                                                                            id="report-start-date",
                                                                            date=None,
                                                                            display_format="YYYY-MM-DD",
                                                                        ),
                                                                    ],
                                                                    width=3,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "End Date"
                                                                        ),
                                                                        dcc.DatePickerSingle(
                                                                            id="report-end-date",
                                                                            date=None,
                                                                            display_format="YYYY-MM-DD",
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
                                                                        dbc.Button(
                                                                            "Generate Report",
                                                                            id="generate-report-btn",
                                                                            color="primary",
                                                                        )
                                                                    ]
                                                                )
                                                            ]
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                html.Div(id="reports-output", className="mt-4"),
                            ]
                        )
                    ]
                )
            ],
            fluid=True,
        )


# Create page instances
products_page = ProductsPage()
batches_page = BatchesPage()
inventory_page = InventoryPage()
pricing_page = PricingPage()
packaging_page = PackagingPage()
invoices_page = InvoicesPage()
reports_page = ReportsPage()

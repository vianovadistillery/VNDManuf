"""Costing and COGS Inspection page for Dash UI."""

from typing import Any, Dict, List

import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, dash_table, dcc, html


class CostingPage:
    """COGS Inspection page with tree view and point-in-time costing."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                # Header
                dbc.Row(
                    [dbc.Col([html.H2("Cost of Goods Inspection", className="mb-4")])]
                ),
                # Search and Filters
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Product SKU or ID:"
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="cogs-product-select",
                                                                    placeholder="Search by SKU or select product...",
                                                                    searchable=True,
                                                                    clearable=True,
                                                                    style={
                                                                        "width": "100%"
                                                                    },
                                                                ),
                                                            ],
                                                            md=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "As Of Date (Point-in-Time):"
                                                                ),
                                                                dcc.DatePickerSingle(
                                                                    id="cogs-as-of-date",
                                                                    display_format="YYYY-MM-DD",
                                                                    placeholder="Current (leave blank)",
                                                                    clearable=True,
                                                                    style={
                                                                        "width": "100%"
                                                                    },
                                                                ),
                                                            ],
                                                            md=3,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Include Estimates:"
                                                                ),
                                                                dbc.Switch(
                                                                    id="cogs-include-estimates",
                                                                    value=True,
                                                                    className="mt-2",
                                                                ),
                                                            ],
                                                            md=2,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Inspect COGS",
                                                                    id="cogs-inspect-btn",
                                                                    color="primary",
                                                                    className="mt-4",
                                                                    size="lg",
                                                                ),
                                                            ],
                                                            md=3,
                                                        ),
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ],
                    className="mb-3",
                ),
                # Summary Card
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("COGS Summary"),
                                        dbc.CardBody(
                                            [
                                                html.Div(
                                                    id="cogs-summary",
                                                    children=[
                                                        html.P(
                                                            "Select a product and click 'Inspect COGS' to view cost breakdown.",
                                                            className="text-muted",
                                                        )
                                                    ],
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    className="mb-3",
                ),
                # Tree View
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Cost Breakdown Tree"),
                                        dbc.CardBody(
                                            [
                                                html.Div(
                                                    id="cogs-tree-view",
                                                    children=[
                                                        html.Pre(
                                                            "No cost breakdown available. Please select a product.",
                                                            className="text-muted",
                                                            style={
                                                                "fontFamily": "monospace",
                                                                "whiteSpace": "pre-wrap",
                                                            },
                                                        )
                                                    ],
                                                    style={
                                                        "maxHeight": "600px",
                                                        "overflowY": "auto",
                                                    },
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    className="mb-3",
                ),
                # Detailed Breakdown Table
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Component Breakdown"),
                                        dbc.CardBody(
                                            [
                                                dash_table.DataTable(
                                                    id="cogs-breakdown-table",
                                                    columns=[
                                                        {
                                                            "name": "Level",
                                                            "id": "level",
                                                        },
                                                        {"name": "SKU", "id": "sku"},
                                                        {"name": "Name", "id": "name"},
                                                        {
                                                            "name": "Qty/Unit",
                                                            "id": "qty_per_unit",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".6f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Unit Cost",
                                                            "id": "unit_cost",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Extended Cost",
                                                            "id": "extended_cost",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Cost Source",
                                                            "id": "cost_source",
                                                        },
                                                        {
                                                            "name": "Has Estimate",
                                                            "id": "has_estimate",
                                                        },
                                                        {
                                                            "name": "Estimate Reason",
                                                            "id": "estimate_reason",
                                                        },
                                                    ],
                                                    data=[],
                                                    sort_action="native",
                                                    filter_action="native",
                                                    page_action="native",
                                                    page_size=25,
                                                    style_cell={
                                                        "fontSize": "11px",
                                                        "textAlign": "left",
                                                    },
                                                    style_header={
                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                        "fontWeight": "bold",
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            "if": {
                                                                "filter_query": "{has_estimate} = True"
                                                            },
                                                            "backgroundColor": "#fff4e6",
                                                            "color": "black",
                                                        },
                                                        {
                                                            "if": {
                                                                "filter_query": "{cost_source} = estimated"
                                                            },
                                                            "backgroundColor": "#ffe6e6",
                                                            "color": "black",
                                                        },
                                                    ],
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        )
                    ]
                ),
            ],
            fluid=True,
        )

    @staticmethod
    def register_callbacks(app, api_base_url: str = "http://127.0.0.1:8000/api/v1"):
        """Register callbacks for the costing page."""

        @app.callback(
            [Output("cogs-product-select", "options")],
            [Input("cogs-product-select", "search_value")],
        )
        def update_product_options(search_value):
            """Load product options from API."""
            try:
                url = f"{api_base_url}/products/"
                params = {"query": search_value} if search_value else {}
                response = requests.get(url, params=params, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    products = data.get("products", [])
                    options = [
                        {
                            "label": f"{p.get('sku', 'N/A')} - {p.get('name', 'Unnamed')}",
                            "value": p.get("id"),
                        }
                        for p in products[:50]  # Limit to 50 for performance
                    ]
                    return [options]
                else:
                    return [[]]
            except Exception as e:
                print(f"Error loading products: {e}")
                return [[]]

        @app.callback(
            [
                Output("cogs-summary", "children"),
                Output("cogs-tree-view", "children"),
                Output("cogs-breakdown-table", "data"),
            ],
            [Input("cogs-inspect-btn", "n_clicks")],
            [
                State("cogs-product-select", "value"),
                State("cogs-as-of-date", "date"),
                State("cogs-include-estimates", "value"),
            ],
        )
        def inspect_cogs(n_clicks, product_id, as_of_date, include_estimates):
            """Inspect COGS for selected product."""
            if not product_id or not n_clicks:
                return (
                    [
                        html.P(
                            "Select a product and click 'Inspect COGS' to view cost breakdown.",
                            className="text-muted",
                        )
                    ],
                    [
                        html.Pre(
                            "No cost breakdown available.",
                            className="text-muted",
                            style={"fontFamily": "monospace"},
                        )
                    ],
                    [],
                )

            try:
                url = f"{api_base_url}/costing/inspect/{product_id}"
                params = {}
                if as_of_date:
                    params["as_of_date"] = as_of_date
                if include_estimates is not None:
                    params["include_estimates"] = include_estimates

                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    cogs_breakdown = data.get("cogs_breakdown", {})

                    # Summary
                    summary_items = [
                        html.H5(
                            f"{cogs_breakdown.get('name', 'Unknown')} ({cogs_breakdown.get('sku', 'N/A')})"
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Strong("Unit Cost: "),
                                        html.Span(
                                            f"${cogs_breakdown.get('unit_cost', 0):.2f}",
                                            className="text-success",
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.Strong("Cost Source: "),
                                        html.Span(
                                            cogs_breakdown.get(
                                                "cost_source", "unknown"
                                            ),
                                            className="badge bg-info",
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.Strong("Has Estimate: "),
                                        html.Span(
                                            "Yes"
                                            if cogs_breakdown.get("has_estimate")
                                            else "No",
                                            className="badge bg-warning"
                                            if cogs_breakdown.get("has_estimate")
                                            else "badge bg-success",
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                    if cogs_breakdown.get("estimate_reason"):
                        summary_items.append(
                            dbc.Alert(
                                f"⚠️ Estimate Reason: {cogs_breakdown.get('estimate_reason')}",
                                color="warning",
                                className="mt-2",
                            )
                        )

                    # Tree view (formatted text)
                    tree_text = format_cogs_tree(cogs_breakdown, indent=0)
                    tree_view = [
                        html.Pre(
                            tree_text,
                            style={
                                "fontFamily": "monospace",
                                "whiteSpace": "pre-wrap",
                                "fontSize": "12px",
                                "lineHeight": "1.4",
                            },
                        )
                    ]

                    # Table data (flatten tree)
                    table_data = flatten_cogs_tree(cogs_breakdown)

                    return summary_items, tree_view, table_data
                else:
                    error_msg = f"Error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", error_msg)
                    except (ValueError, KeyError, TypeError):
                        error_msg = f"Error: {response.text[:100]}"

                    return (
                        [dbc.Alert(error_msg, color="danger")],
                        [
                            html.Pre(
                                f"Error loading COGS: {error_msg}",
                                className="text-danger",
                                style={"fontFamily": "monospace"},
                            )
                        ],
                        [],
                    )
            except requests.exceptions.ConnectionError:
                return (
                    [
                        dbc.Alert(
                            "API not available. Please ensure the API server is running.",
                            color="warning",
                        )
                    ],
                    [
                        html.Pre(
                            "API not available.",
                            className="text-muted",
                            style={"fontFamily": "monospace"},
                        )
                    ],
                    [],
                )
            except Exception as e:
                error_msg = f"Error inspecting COGS: {str(e)}"
                return (
                    [dbc.Alert(error_msg, color="danger")],
                    [
                        html.Pre(
                            error_msg,
                            className="text-danger",
                            style={"fontFamily": "monospace"},
                        )
                    ],
                    [],
                )


def format_cogs_tree(node: Dict[str, Any], indent: int = 0, prefix: str = "") -> str:
    """Format COGS tree as text with indentation."""
    lines = []
    indent_str = "  " * indent

    # Node info
    sku = node.get("sku", "N/A")
    name = node.get("name", "Unknown")
    unit_cost = node.get("unit_cost", 0)
    cost_source = node.get("cost_source", "unknown")
    has_estimate = node.get("has_estimate", False)

    # Format line
    estimate_marker = " ⚠️ ESTIMATED" if has_estimate else ""
    lines.append(
        f"{prefix}{indent_str}{sku} | {name}"
        f"\n{indent_str}    Cost: ${unit_cost:.2f} ({cost_source}){estimate_marker}"
    )

    if node.get("estimate_reason"):
        lines.append(f"{indent_str}    Reason: {node.get('estimate_reason')}")

    # Children
    children = node.get("children", [])
    if children:
        lines.append("")
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            child_prefix = "└── " if is_last else "├── "
            lines.append(format_cogs_tree(child, indent + 1, child_prefix))

    return "\n".join(lines)


def flatten_cogs_tree(
    node: Dict[str, Any], level: int = 0, parent_qty: float = 1.0
) -> List[Dict[str, Any]]:
    """Flatten COGS tree into table rows."""
    rows = []

    sku = node.get("sku", "N/A")
    name = node.get("name", "Unknown")
    qty_per_unit = node.get("qty_per_parent", 1.0)
    unit_cost = float(node.get("unit_cost", 0))
    extended_cost = float(node.get("extended_cost", unit_cost * parent_qty))
    cost_source = node.get("cost_source", "unknown")
    has_estimate = node.get("has_estimate", False)
    estimate_reason = node.get("estimate_reason", "")

    rows.append(
        {
            "level": level,
            "sku": sku,
            "name": name,
            "qty_per_unit": qty_per_unit,
            "unit_cost": unit_cost,
            "extended_cost": extended_cost,
            "cost_source": cost_source,
            "has_estimate": "Yes" if has_estimate else "No",
            "estimate_reason": estimate_reason[:100]
            if estimate_reason
            else "",  # Truncate long reasons
        }
    )

    # Add children
    for child in node.get("children", []):
        rows.extend(flatten_cogs_tree(child, level + 1, qty_per_unit))

    return rows

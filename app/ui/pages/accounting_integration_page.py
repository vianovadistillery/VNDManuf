"""Accounting Integration Page for Xero."""

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, ctx, html

from app.adapters.db import get_session
from app.adapters.db.models import XeroSyncLog
from app.services.xero_integration import (
    post_batch_journal,
    pull_contacts,
    push_customer,
    push_product_as_item,
    push_supplier,
)
from app.services.xero_oauth import get_latest_tokens


class AccountingIntegrationPage:
    """Accounting Integration page with Xero OAuth and sync controls."""

    def layout(self):
        """Return the page layout."""

        # Check connection status
        token = get_latest_tokens()
        is_connected = token is not None

        # Load recent sync logs
        with get_session() as session:
            logs = (
                session.query(XeroSyncLog)
                .order_by(XeroSyncLog.ts.desc())
                .limit(100)
                .all()
            )
            log_data = [
                {
                    "ts": log.ts.strftime("%Y-%m-%d %H:%M") if log.ts else "",
                    "type": log.object_type or "",
                    "id": log.object_id or "",
                    "direction": log.direction or "",
                    "status": log.status or "",
                    "message": log.message or "",
                }
                for log in logs
            ]

        log_df = pd.DataFrame(log_data)

        # Connection card
        connection_card = dbc.Card(
            [
                dbc.CardHeader("Xero Connection"),
                dbc.CardBody(
                    [
                        html.P(
                            [
                                html.Strong("Status: "),
                                html.Span(
                                    "Connected" if is_connected else "Not Connected",
                                    className="badge bg-success"
                                    if is_connected
                                    else "badge bg-danger",
                                ),
                            ]
                        )
                        if is_connected
                        else html.P(
                            [
                                html.Strong("Status: "),
                                html.Span("Not Connected", className="badge bg-danger"),
                            ]
                        ),
                        html.P(
                            [
                                html.Strong("Tenant: "),
                                token.tenant_id if token else "N/A",
                            ]
                        )
                        if token and token.tenant_id
                        else None,
                        html.Hr(),
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    "Connect to Xero",
                                    href="/xero/connect",
                                    id="btn-connect-xero",
                                    color="primary",
                                    disabled=is_connected,
                                ),
                                dbc.Button(
                                    "Pull Contacts",
                                    id="btn-pull-contacts",
                                    color="secondary",
                                    disabled=not is_connected,
                                    className="ms-2",
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.Alert(
                            "Connect to Xero to enable integration features",
                            color="info",
                            className="mb-0",
                        )
                        if not is_connected
                        else None,
                    ]
                ),
            ],
            className="mb-4",
        )

        # Push operations card
        push_card = dbc.Card(
            [
                dbc.CardHeader("Push to Xero"),
                dbc.CardBody(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="supplier-id",
                                    placeholder="Supplier ID",
                                    type="text",
                                ),
                                dbc.Button(
                                    "Push Supplier",
                                    id="btn-push-supplier",
                                    color="primary",
                                    disabled=not is_connected,
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="customer-id",
                                    placeholder="Customer ID",
                                    type="text",
                                ),
                                dbc.Button(
                                    "Push Customer",
                                    id="btn-push-customer",
                                    color="primary",
                                    disabled=not is_connected,
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="product-id",
                                    placeholder="Product ID",
                                    type="text",
                                ),
                                dbc.Button(
                                    "Push Product",
                                    id="btn-push-product",
                                    color="primary",
                                    disabled=not is_connected,
                                ),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
            ],
            className="mb-4",
        )

        # Batch journal posting card
        journal_card = dbc.Card(
            [
                dbc.CardHeader("Post Batch Journal"),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Batch Code"),
                                        dbc.Input(
                                            id="batch-no",
                                            placeholder="e.g., B060149",
                                            disabled=not is_connected,
                                        ),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Amount ($)"),
                                        dbc.Input(
                                            id="journal-amount",
                                            placeholder="0.00",
                                            type="number",
                                            step=0.01,
                                            disabled=not is_connected,
                                        ),
                                    ],
                                    width=6,
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.Button(
                            "Post Journal",
                            id="btn-post-journal",
                            color="success",
                            disabled=not is_connected,
                        ),
                    ]
                ),
            ],
            className="mb-4",
        )

        # Sync logs table
        logs_card = dbc.Card(
            [
                dbc.CardHeader(
                    [
                        "Sync Log",
                        dbc.Button(
                            "Refresh",
                            id="btn-refresh-logs",
                            size="sm",
                            outline=True,
                            className="float-end",
                        ),
                    ]
                ),
                dbc.CardBody(
                    [
                        dash.dash_table.DataTable(
                            id="sync-log-table",
                            data=log_df.to_dict("records") if not log_df.empty else [],
                            columns=[
                                {"name": "Time", "id": "ts"},
                                {"name": "Type", "id": "type"},
                                {"name": "ID", "id": "id"},
                                {"name": "Direction", "id": "direction"},
                                {"name": "Status", "id": "status"},
                                {"name": "Message", "id": "message"},
                            ],
                            style_cell={
                                "textAlign": "left",
                                "fontSize": "12px",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"filter_query": "{status} = OK"},
                                    "backgroundColor": "#d4edda",
                                    "color": "#155724",
                                },
                                {
                                    "if": {"filter_query": "{status} = ERROR"},
                                    "backgroundColor": "#f8d7da",
                                    "color": "#721c24",
                                },
                            ],
                            page_size=20,
                            sort_action="native",
                            sort_mode="multi",
                        )
                        if not log_df.empty
                        else html.P("No sync logs yet"),
                    ]
                ),
            ]
        )

        return dbc.Container(
            [
                html.H2("Accounting Integration", className="mb-4"),
                connection_card,
                push_card,
                journal_card,
                logs_card,
            ],
            fluid=True,
        )

    def register_callbacks(self, app):
        """Register callbacks for the accounting integration page."""

        @app.callback(
            Output("sync-log-table", "data"),
            [
                Input("btn-pull-contacts", "n_clicks"),
                Input("btn-push-supplier", "n_clicks"),
                Input("btn-push-customer", "n_clicks"),
                Input("btn-push-product", "n_clicks"),
                Input("btn-post-journal", "n_clicks"),
                Input("btn-refresh-logs", "n_clicks"),
            ],
            [
                State("supplier-id", "value"),
                State("customer-id", "value"),
                State("product-id", "value"),
                State("batch-no", "value"),
                State("journal-amount", "value"),
            ],
            prevent_initial_call=True,
        )
        def handle_xero_actions(
            pull_n,
            push_sup_n,
            push_cust_n,
            push_prod_n,
            post_journal_n,
            refresh_n,
            supplier_id,
            customer_id,
            product_id,
            batch_no,
            amount,
        ):
            """Handle Xero integration actions."""

            if not ctx.triggered:
                return []

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            try:
                if button_id == "btn-pull-contacts":
                    pull_contacts()

                elif button_id == "btn-push-supplier" and supplier_id:
                    push_supplier(supplier_id)

                elif button_id == "btn-push-customer" and customer_id:
                    push_customer(customer_id)

                elif button_id == "btn-push-product" and product_id:
                    push_product_as_item(product_id)

                elif button_id == "btn-post-journal" and batch_no and amount:
                    from app.services.xero_mappings import get_account

                    post_batch_journal(
                        batch_code=batch_no,
                        debit_account=get_account("FG_INVENTORY"),
                        credit_account=get_account("RAW_INVENTORY"),
                        amount=float(amount),
                    )

            except Exception as e:
                # Error logging is handled by the integration functions
                print(f"Error in {button_id}: {e}")

            # Always refresh logs after action
            with get_session() as session:
                logs = (
                    session.query(XeroSyncLog)
                    .order_by(XeroSyncLog.ts.desc())
                    .limit(100)
                    .all()
                )
                log_data = [
                    {
                        "ts": log.ts.strftime("%Y-%m-%d %H:%M") if log.ts else "",
                        "type": log.object_type or "",
                        "id": log.object_id or "",
                        "direction": log.direction or "",
                        "status": log.status or "",
                        "message": log.message or "",
                    }
                    for log in logs
                ]

                return log_data


# Create page instance
accounting_integration_page = AccountingIntegrationPage()

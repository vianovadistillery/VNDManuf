# app/ui/work_orders_callbacks.py
"""Callbacks for Work Orders page."""

import json
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, dash_table, dcc, html, no_update
from dash.exceptions import PreventUpdate


def register_work_orders_callbacks(
    app, api_base_url: str = "http://127.0.0.1:8000/api/v1"
):
    """Register all work order callbacks."""

    # Load work orders list
    @app.callback(
        [
            Output("wo-list-table", "data"),
            Output("wo-list-table", "columns"),
        ],
        [
            Input("wo-status-filter", "value"),
            Input("wo-product-filter", "value"),
            Input("wo-date-from", "value"),
            Input("wo-date-to", "value"),
            Input("main-tabs", "active_tab"),
        ],
        prevent_initial_call=False,
    )
    def load_work_orders_list(
        status_filter, product_filter, date_from, date_to, active_tab
    ):
        """Load work orders list with filters."""
        if active_tab != "work-orders":
            return [], []

        try:
            params = {}
            if status_filter:
                params["status"] = status_filter
            if product_filter:
                params["product_id"] = product_filter
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            url = f"{api_base_url}/work-orders/"
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                work_orders = response.json()

                # Format data for table
                table_data = []
                for wo in work_orders:
                    # Get QC status
                    qc_status = "N/A"
                    if wo.get("qc_tests"):
                        qc_tests = wo.get("qc_tests", [])
                        pending = [t for t in qc_tests if t.get("status") == "pending"]
                        failed = [t for t in qc_tests if t.get("status") == "fail"]
                        if failed:
                            qc_status = "Failed"
                        elif pending:
                            qc_status = "Pending"
                        else:
                            qc_status = "Passed"

                    # Get unit cost
                    unit_cost = None
                    outputs = wo.get("outputs", [])
                    if outputs:
                        unit_cost = outputs[0].get("unit_cost")

                    table_data.append(
                        {
                            "id": wo.get("id"),
                            "code": wo.get("code", ""),
                            "product": wo.get(
                                "product_id", ""
                            ),  # Will need to fetch product name
                            "planned_qty": f"{wo.get('planned_qty', 0):.3f}"
                            if wo.get("planned_qty")
                            else "0",
                            "status": wo.get("status", "").title(),
                            "batch_code": wo.get("batch_code", ""),
                            "qc_status": qc_status,
                            "unit_cost": f"${unit_cost:.2f}" if unit_cost else "N/A",
                        }
                    )

                columns = [
                    {"name": "Code", "id": "code"},
                    {"name": "Product", "id": "product"},
                    {"name": "Planned Qty", "id": "planned_qty"},
                    {"name": "Status", "id": "status"},
                    {"name": "Batch Code", "id": "batch_code"},
                    {"name": "QC Status", "id": "qc_status"},
                    {"name": "Cost/Unit", "id": "unit_cost"},
                ]

                return table_data, columns
            else:
                print(f"Error loading work orders: {response.status_code}")
                return [], []
        except Exception as e:
            print(f"Error in load_work_orders_list: {e}")
            return [], []

    # Load products for filter dropdown
    @app.callback(
        Output("wo-product-filter", "options"),
        [Input("main-tabs", "active_tab")],
        prevent_initial_call=False,
    )
    def load_products_for_filter(active_tab):
        """Load products for filter dropdown."""
        if active_tab != "work-orders":
            return no_update

        try:
            url = f"{api_base_url}/products/?is_active=true"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                products_data = response.json()
                products = (
                    products_data
                    if isinstance(products_data, list)
                    else products_data.get("products", [])
                )
                options = [
                    {
                        "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                        "value": p.get("id", ""),
                    }
                    for p in products
                ]
                return [{"label": "All", "value": ""}] + options
            else:
                return []
        except Exception as e:
            print(f"Error loading products: {e}")
            return []

    # Load components for issue material dropdown
    @app.callback(
        Output("wo-issue-component-dropdown", "options"),
        [Input("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def load_components_for_issue(wo_id):
        """Load components for issue material dropdown."""
        if not wo_id:
            return []

        try:
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                wo = response.json()
                inputs = wo.get("inputs", [])
                options = []
                for inp in inputs:
                    if (
                        inp.get("component_product_id")
                        and inp.get("line_type") == "material"
                    ):
                        # Get product name
                        product_id = inp.get("component_product_id")
                        try:
                            prod_url = f"{api_base_url}/products/{product_id}"
                            prod_response = requests.get(prod_url, timeout=5)
                            if prod_response.status_code == 200:
                                product = prod_response.json()
                                label = f"{product.get('sku', '')} - {product.get('name', '')}"
                            else:
                                label = product_id
                        except (ValueError, TypeError, AttributeError):
                            label = product_id

                        options.append(
                            {
                                "label": label,
                                "value": product_id,
                            }
                        )
                return options
            else:
                return []
        except Exception as e:
            print(f"Error loading components: {e}")
            return []

    # Refresh work orders list after actions
    @app.callback(
        Output("wo-list-table", "data", allow_duplicate=True),
        [
            Input("wo-create-submit-btn", "n_clicks"),
            Input("wo-issue-submit-btn", "n_clicks"),
            Input("wo-qc-submit-btn", "n_clicks"),
            Input("wo-complete-submit-btn", "n_clicks"),
            Input("wo-release-btn", "n_clicks"),
            Input("wo-start-btn", "n_clicks"),
            Input("wo-void-btn", "n_clicks"),
        ],
        [
            State("wo-status-filter", "value"),
            State("wo-product-filter", "value"),
            State("wo-date-from", "value"),
            State("wo-date-to", "value"),
        ],
        prevent_initial_call=True,
    )
    def refresh_work_orders_list(
        create_clicks,
        issue_clicks,
        qc_clicks,
        complete_clicks,
        release_clicks,
        start_clicks,
        void_clicks,
        status_filter,
        product_filter,
        date_from,
        date_to,
    ):
        """Refresh work orders list after any action."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        try:
            params = {}
            if status_filter:
                params["status"] = status_filter
            if product_filter:
                params["product_id"] = product_filter
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            url = f"{api_base_url}/work-orders/"
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                work_orders = response.json()

                table_data = []
                for wo in work_orders:
                    qc_status = "N/A"
                    if wo.get("qc_tests"):
                        qc_tests = wo.get("qc_tests", [])
                        pending = [t for t in qc_tests if t.get("status") == "pending"]
                        failed = [t for t in qc_tests if t.get("status") == "fail"]
                        if failed:
                            qc_status = "Failed"
                        elif pending:
                            qc_status = "Pending"
                        else:
                            qc_status = "Passed"

                    unit_cost = None
                    outputs = wo.get("outputs", [])
                    if outputs:
                        unit_cost = outputs[0].get("unit_cost")

                    table_data.append(
                        {
                            "id": wo.get("id"),
                            "code": wo.get("code", ""),
                            "product": wo.get("product_id", ""),
                            "planned_qty": f"{wo.get('planned_qty', 0):.3f}"
                            if wo.get("planned_qty")
                            else "0",
                            "status": wo.get("status", "").title(),
                            "batch_code": wo.get("batch_code", ""),
                            "qc_status": qc_status,
                            "unit_cost": f"${unit_cost:.2f}" if unit_cost else "N/A",
                        }
                    )

                return table_data
            else:
                return no_update
        except Exception as e:
            print(f"Error refreshing work orders: {e}")
            return no_update

    # Load products and assemblies for create modal
    @app.callback(
        [
            Output("wo-create-product-dropdown", "options"),
            Output("wo-create-product-dropdown", "value"),
            Output("wo-create-assembly-dropdown", "options"),
            Output("wo-create-assembly-dropdown", "value"),
            Output("wo-create-batch-code", "value"),
        ],
        [Input("wo-create-modal", "is_open")],
        prevent_initial_call=True,
    )
    def load_create_modal_dropdowns(modal_is_open):
        """Load products and assemblies for create modal, and generate batch code."""
        if not modal_is_open:
            raise PreventUpdate

        try:
            # Load products that have assembly capability (is_assemble=True)
            products_url = f"{api_base_url}/products/?is_active=true&is_assemble=true"
            products_response = requests.get(products_url, timeout=5)
            products = []
            if products_response.status_code == 200:
                products_data = products_response.json()
                products = (
                    products_data
                    if isinstance(products_data, list)
                    else products_data.get("products", [])
                )

            # Filter to only include products with is_assemble=True
            products = [p for p in products if p.get("is_assemble", False)]

            product_options = [
                {
                    "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                    "value": p.get("id", ""),
                }
                for p in products
            ]

            # Generate batch code (client-side generation matching server logic)
            # This is a preview - actual code will be generated server-side on save
            today = datetime.utcnow()
            year_2digit = today.strftime("%y")  # e.g., "25" for 2025

            # Get existing batch codes from work orders to find max sequence
            # Note: This is a preview - actual code will be generated server-side on save
            # But we can generate a likely next code for display
            try:
                work_orders_response = requests.get(
                    f"{api_base_url}/work-orders/", timeout=5
                )

                max_seq = 0
                year_prefix = f"B{year_2digit}"

                # Check work orders for batch codes
                if work_orders_response.status_code == 200:
                    work_orders = work_orders_response.json()
                    for wo in work_orders:
                        batch_code = wo.get("batch_code", "")
                        if batch_code and batch_code.startswith(year_prefix):
                            try:
                                seq_part = batch_code[-4:]
                                seq_num = int(seq_part)
                                max_seq = max(max_seq, seq_num)
                            except (ValueError, IndexError):
                                pass

                seq = max_seq + 1
                batch_code = f"B{year_2digit}{seq:04d}"
            except Exception:
                # Fallback: generate a simple code
                batch_code = f"B{year_2digit}0001"

            # Reset both dropdowns when modal opens
            return product_options, None, [], None, batch_code
        except Exception as e:
            print(f"Error loading dropdowns: {e}")
            return [], None, [], None, ""

    # Update assembly dropdown when product is selected
    @app.callback(
        [
            Output("wo-create-assembly-dropdown", "options", allow_duplicate=True),
            Output("wo-create-assembly-dropdown", "value", allow_duplicate=True),
        ],
        [Input("wo-create-product-dropdown", "value")],
        prevent_initial_call=True,
    )
    def update_assembly_dropdown(product_id):
        """Update assembly dropdown based on selected product."""
        if not product_id:
            # Clear assemblies if no product selected
            return [], None

        try:
            # Load assemblies (not formulas) filtered by product_id
            assemblies_url = (
                f"{api_base_url}/assemblies/?product_id={product_id}&is_active=true"
            )
            assemblies_response = requests.get(assemblies_url, timeout=5)
            assemblies = []
            if assemblies_response.status_code == 200:
                assemblies = assemblies_response.json()

            assembly_options = [
                {
                    "label": f"{a.get('assembly_code', '')} - {a.get('assembly_name', '')}",
                    "value": a.get("id", ""),
                }
                for a in assemblies
            ]

            # Clear the selected value if assemblies changed
            return assembly_options, None
        except Exception as e:
            print(f"Error loading assemblies for product {product_id}: {e}")
            return [], None

    # Create work order
    @app.callback(
        [
            Output("wo-create-modal", "is_open", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("toast", "icon", allow_duplicate=True),
        ],
        [Input("wo-create-submit-btn", "n_clicks")],
        [
            State("wo-create-product-dropdown", "value"),
            State("wo-create-planned-qty", "value"),
            State("wo-create-uom", "value"),
            State("wo-create-work-center", "value"),
            State("wo-create-assembly-dropdown", "value"),
            State("wo-create-batch-code", "value"),
            State("wo-create-notes", "value"),
        ],
        prevent_initial_call=True,
    )
    def create_work_order(
        n_clicks,
        product_id,
        planned_qty,
        uom,
        work_center,
        assembly_id,
        batch_code,
        notes,
    ):
        """Create a new work order."""
        if not n_clicks:
            raise PreventUpdate

        if not product_id or not planned_qty:
            return (
                no_update,
                True,
                "Error",
                "Product and planned quantity are required",
                "danger",
            )

        try:
            # Only include assembly_id if it's provided and not empty
            data = {
                "product_id": product_id,
                "planned_qty": float(planned_qty),
                "uom": uom or "KG",
                "work_center": work_center,
                "notes": notes,
            }
            # Only add assembly_id if it's provided and not empty
            # Also validate that the assembly_id is not just whitespace or "None"
            if (
                assembly_id
                and str(assembly_id).strip()
                and str(assembly_id).strip().lower() != "none"
            ):
                # Verify the assembly exists before sending
                try:
                    # Quick validation - check if assembly exists in the assemblies list for this product
                    assemblies_check = requests.get(
                        f"{api_base_url}/assemblies/?product_id={product_id}&is_active=true",
                        timeout=5,
                    )
                    if assemblies_check.status_code == 200:
                        assemblies_list = assemblies_check.json()
                        assembly_ids = [a.get("id") for a in assemblies_list]
                        if assembly_id in assembly_ids:
                            data["assembly_id"] = assembly_id
                        else:
                            # Assembly doesn't exist or doesn't belong to this product, don't send it
                            print(
                                f"Warning: Assembly {assembly_id} not found for product {product_id}, skipping"
                            )
                    else:
                        # Can't validate, skip sending assembly_id
                        print(
                            f"Warning: Could not validate assembly {assembly_id}: API error"
                        )
                except Exception as e:
                    # If validation fails, skip sending assembly_id
                    print(f"Warning: Could not validate assembly {assembly_id}: {e}")
            # Note: batch_code is generated server-side, so we don't send it here
            # The server will generate it using BatchCodeGenerator

            url = f"{api_base_url}/work-orders/"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 201:
                return (
                    False,  # Close modal
                    True,  # Show toast
                    "Success",
                    f"Work order created successfully: {response.json().get('code', '')}",
                    "success",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    no_update,
                    True,
                    "Error",
                    f"Failed to create work order: {error_msg}",
                    "danger",
                )
        except Exception as e:
            return (
                no_update,
                True,
                "Error",
                f"Failed to create work order: {str(e)}",
                "danger",
            )

    # Load work order detail when row selected or detail tab active
    @app.callback(
        [
            Output("wo-detail-content", "children"),
            Output("wo-detail-wo-id", "data"),
        ],
        [
            Input("wo-list-table", "selected_rows"),
            Input("wo-main-tabs", "active_tab"),
        ],
        [State("wo-list-table", "data"), State("wo-detail-wo-id", "data")],
        prevent_initial_call=False,
    )
    def load_work_order_detail(selected_rows, active_tab, table_data, current_wo_id):
        """Load work order detail when selected or detail tab is active."""
        # Handle case where table_data might not exist (component not in DOM yet)
        if table_data is None:
            table_data = []

        # If detail tab is active and we have a selected row, load it
        if active_tab == "detail":
            if (
                selected_rows
                and table_data
                and len(selected_rows) > 0
                and len(table_data) > 0
            ):
                wo_id = table_data[selected_rows[0]].get("id")
                if wo_id and wo_id != current_wo_id:
                    try:
                        url = f"{api_base_url}/work-orders/{wo_id}"
                        response = requests.get(url, timeout=5)

                        if response.status_code == 200:
                            wo = response.json()
                            return create_work_order_detail_layout(wo), wo_id
                        else:
                            return html.Div(
                                f"Error loading work order: {response.status_code}"
                            ), wo_id
                    except Exception as e:
                        return html.Div(f"Error: {str(e)}"), wo_id
                elif current_wo_id:
                    # Keep current detail if we have one
                    try:
                        url = f"{api_base_url}/work-orders/{current_wo_id}"
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            wo = response.json()
                            return create_work_order_detail_layout(wo), current_wo_id
                    except (ValueError, TypeError, AttributeError):
                        pass
            elif current_wo_id:
                # Keep current detail if we have one
                try:
                    url = f"{api_base_url}/work-orders/{current_wo_id}"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        wo = response.json()
                        return create_work_order_detail_layout(wo), current_wo_id
                except (ValueError, TypeError, AttributeError):
                    pass

        # Default: show message
        if active_tab == "detail":
            return html.Div("Select a work order from the list to view details"), None
        return no_update, no_update

    # Issue material
    @app.callback(
        [
            Output("wo-issue-toast", "is_open", allow_duplicate=True),
            Output("wo-issue-toast", "header", allow_duplicate=True),
            Output("wo-issue-toast", "children", allow_duplicate=True),
        ],
        [Input("wo-issue-submit-btn", "n_clicks")],
        [
            State("wo-detail-wo-id", "data"),
            State("wo-issue-component-dropdown", "value"),
            State("wo-issue-qty", "value"),
            State("wo-issue-batch-dropdown", "value"),
            State("wo-issue-uom", "value"),
        ],
        prevent_initial_call=True,
    )
    def issue_material(n_clicks, wo_id, component_id, qty, batch_id, uom):
        """Issue material for work order."""
        if not n_clicks or not wo_id:
            raise PreventUpdate

        if not component_id or not qty:
            return (
                True,
                "Error",
                "Component and quantity are required",
            )

        try:
            data = {
                "component_product_id": component_id,
                "qty": float(qty),
                "source_batch_id": batch_id,
                "uom": uom,
            }

            url = f"{api_base_url}/work-orders/{wo_id}/issues"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 201:
                return (
                    True,
                    "Success",
                    "Material issued successfully",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to issue material: {error_msg}",
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to issue material: {str(e)}",
            )

    # Record QC
    @app.callback(
        [
            Output("wo-qc-toast", "is_open", allow_duplicate=True),
            Output("wo-qc-toast", "header", allow_duplicate=True),
            Output("wo-qc-toast", "children", allow_duplicate=True),
        ],
        [Input("wo-qc-submit-btn", "n_clicks")],
        [
            State("wo-detail-wo-id", "data"),
            State("wo-qc-test-type", "value"),
            State("wo-qc-result-value", "value"),
            State("wo-qc-result-text", "value"),
            State("wo-qc-unit", "value"),
            State("wo-qc-status", "value"),
            State("wo-qc-tester", "value"),
            State("wo-qc-note", "value"),
        ],
        prevent_initial_call=True,
    )
    def record_qc(
        n_clicks,
        wo_id,
        test_type,
        result_value,
        result_text,
        unit,
        qc_status,
        tester,
        note,
    ):
        """Record QC test result."""
        if not n_clicks or not wo_id:
            raise PreventUpdate

        if not test_type:
            return (
                True,
                "Error",
                "Test type is required",
            )

        try:
            data = {
                "test_type": test_type,
                "result_value": float(result_value) if result_value else None,
                "result_text": result_text,
                "unit": unit,
                "status": qc_status or "pending",
                "tester": tester,
                "note": note,
            }

            url = f"{api_base_url}/work-orders/{wo_id}/qc"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 201:
                return (
                    True,
                    "Success",
                    "QC test recorded successfully",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to record QC: {error_msg}",
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to record QC: {str(e)}",
            )

    # Complete work order
    @app.callback(
        [
            Output("wo-complete-toast", "is_open", allow_duplicate=True),
            Output("wo-complete-toast", "header", allow_duplicate=True),
            Output("wo-complete-toast", "children", allow_duplicate=True),
        ],
        [Input("wo-complete-submit-btn", "n_clicks")],
        [
            State("wo-detail-wo-id", "data"),
            State("wo-complete-qty", "value"),
        ],
        prevent_initial_call=True,
    )
    def complete_work_order(n_clicks, wo_id, qty_produced):
        """Complete work order."""
        if not n_clicks or not wo_id:
            raise PreventUpdate

        if not qty_produced:
            return (
                True,
                "Error",
                "Quantity produced is required",
            )

        try:
            data = {
                "qty_produced": float(qty_produced),
                "batch_attrs": {},
            }

            url = f"{api_base_url}/work-orders/{wo_id}/complete"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                return (
                    True,
                    "Success",
                    "Work order completed successfully",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to complete work order: {error_msg}",
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to complete work order: {str(e)}",
            )

    # Load costs
    @app.callback(
        Output("wo-costs-content", "children"),
        [Input("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def load_work_order_costs(wo_id):
        """Load work order cost breakdown."""
        if not wo_id:
            return html.Div("No work order selected")

        try:
            url = f"{api_base_url}/work-orders/{wo_id}/costs"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                costs = response.json()
                return dbc.Card(
                    [
                        dbc.CardHeader("Cost Breakdown"),
                        dbc.CardBody(
                            [
                                html.P(
                                    f"Material Cost: ${costs.get('material_cost', 0):.2f}"
                                ),
                                html.P(
                                    f"Overhead Cost: ${costs.get('overhead_cost', 0):.2f}"
                                ),
                                html.P(
                                    f"Total Cost: ${costs.get('total_cost', 0):.2f}"
                                ),
                                html.P(
                                    f"Quantity Produced: {costs.get('qty_produced', 0):.3f}"
                                ),
                                html.P(
                                    f"Unit Cost: ${costs.get('unit_cost', 0):.2f}"
                                    if costs.get("unit_cost")
                                    else "N/A"
                                ),
                            ]
                        ),
                    ]
                )
            else:
                return html.Div(f"Error loading costs: {response.status_code}")
        except Exception as e:
            return html.Div(f"Error: {str(e)}")

    # Load genealogy
    @app.callback(
        Output("wo-genealogy-content", "children"),
        [Input("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def load_genealogy(wo_id):
        """Load batch genealogy."""
        if not wo_id:
            return html.Div("No work order selected")

        try:
            url = f"{api_base_url}/work-orders/{wo_id}/genealogy"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                genealogy = response.json()
                return dbc.Card(
                    [
                        dbc.CardHeader("Batch Genealogy"),
                        dbc.CardBody(
                            [
                                html.P(
                                    f"Batch Code: {genealogy.get('batch_code', '')}"
                                ),
                                html.P(
                                    f"Input Batch IDs: {', '.join(genealogy.get('input_batch_ids', []))}"
                                ),
                                html.Pre(
                                    json.dumps(genealogy.get("genealogy", {}), indent=2)
                                ),
                            ]
                        ),
                    ]
                )
            else:
                return html.Div(f"Error loading genealogy: {response.status_code}")
        except Exception as e:
            return html.Div(f"Error: {str(e)}")

    # Work order actions (release, start, void)
    @app.callback(
        [
            Output("wo-action-toast", "is_open", allow_duplicate=True),
            Output("wo-action-toast", "header", allow_duplicate=True),
            Output("wo-action-toast", "children", allow_duplicate=True),
        ],
        [
            Input("wo-release-btn", "n_clicks"),
            Input("wo-start-btn", "n_clicks"),
            Input("wo-void-btn", "n_clicks"),
        ],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def work_order_actions(release_clicks, start_clicks, void_clicks, wo_id):
        """Handle work order actions (release, start, void)."""
        ctx = dash.callback_context
        if not ctx.triggered or not wo_id:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        try:
            if button_id == "wo-release-btn":
                url = f"{api_base_url}/work-orders/{wo_id}/release"
                action = "released"
                data = {}
            elif button_id == "wo-start-btn":
                url = f"{api_base_url}/work-orders/{wo_id}/start"
                action = "started"
                data = {}
            elif button_id == "wo-void-btn":
                url = f"{api_base_url}/work-orders/{wo_id}/void"
                action = "voided"
                data = {"reason": "Voided from UI"}
            else:
                raise PreventUpdate

            response = requests.post(url, json=data, timeout=10)

            if response.status_code in [200, 201]:
                return (
                    True,
                    "Success",
                    f"Work order {action} successfully",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to {action} work order: {error_msg}",
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to perform action: {str(e)}",
            )

    # Tab switching for main tabs
    @app.callback(
        Output("wo-main-tab-content", "children"),
        [Input("wo-main-tabs", "active_tab")],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call=False,
    )
    def switch_main_tabs(active_tab, current_wo_id):
        """Switch between main tabs (list, detail, rates, batch-lookup)."""
        # Default to "list" if active_tab is None or empty
        if not active_tab:
            active_tab = "list"

        if active_tab == "list":
            return dbc.Card(
                [
                    dbc.CardHeader("Work Orders"),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Status:"),
                                            dcc.Dropdown(
                                                id="wo-status-filter",
                                                options=[
                                                    {"label": "All", "value": ""},
                                                    {
                                                        "label": "Draft",
                                                        "value": "draft",
                                                    },
                                                    {
                                                        "label": "Released",
                                                        "value": "released",
                                                    },
                                                    {
                                                        "label": "In Progress",
                                                        "value": "in_progress",
                                                    },
                                                    {
                                                        "label": "Complete",
                                                        "value": "complete",
                                                    },
                                                    {"label": "Hold", "value": "hold"},
                                                    {"label": "Void", "value": "void"},
                                                ],
                                                value="",
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Product:"),
                                            dcc.Dropdown(
                                                id="wo-product-filter",
                                                options=[],
                                                value=None,
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Date From:"),
                                            dbc.Input(id="wo-date-from", type="date"),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Date To:"),
                                            dbc.Input(id="wo-date-to", type="date"),
                                        ],
                                        md=3,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dash_table.DataTable(
                                id="wo-list-table",
                                columns=[
                                    {"name": "Code", "id": "code"},
                                    {"name": "Product", "id": "product"},
                                    {"name": "Planned Qty", "id": "planned_qty"},
                                    {"name": "Status", "id": "status"},
                                    {"name": "Batch Code", "id": "batch_code"},
                                    {"name": "QC Status", "id": "qc_status"},
                                    {"name": "Cost/Unit", "id": "unit_cost"},
                                ],
                                data=[],
                                sort_action="native",
                                filter_action="native",
                                row_selectable="single",
                                page_action="native",
                                page_current=0,
                                page_size=20,
                            ),
                            dbc.Button(
                                "Create Work Order",
                                id="wo-create-btn",
                                color="primary",
                                className="mt-3",
                            ),
                        ]
                    ),
                ]
            )
        elif active_tab == "detail":
            # Show detail view - detail callback will handle loading based on wo-detail-wo-id
            if current_wo_id:
                # Return placeholder - detail callback will handle loading
                return html.Div(id="wo-detail-content", children=html.Div("Loading..."))
            return html.Div(
                id="wo-detail-content",
                children=html.Div("Select a work order from the list to view details"),
            )
        elif active_tab == "rates":
            return dbc.Card(
                [
                    dbc.CardHeader("Cost Rate Manager"),
                    dbc.CardBody(html.P("Cost rate management coming soon...")),
                ]
            )
        elif active_tab == "batch-lookup":
            return dbc.Card(
                [
                    dbc.CardHeader("Batch Lookup"),
                    dbc.CardBody(
                        html.P("Batch lookup and traceability coming soon...")
                    ),
                ]
            )
        return html.Div()

    # Open create modal
    @app.callback(
        Output("wo-create-modal", "is_open", allow_duplicate=True),
        [Input("wo-create-btn", "n_clicks"), Input("wo-create-cancel-btn", "n_clicks")],
        [State("wo-create-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_create_modal(create_clicks, cancel_clicks, is_open):
        """Toggle create work order modal."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return not is_open

    # Refresh detail view after actions
    @app.callback(
        [
            Output("wo-detail-content", "children", allow_duplicate=True),
            Output("wo-detail-wo-id", "data", allow_duplicate=True),
        ],
        [
            Input("wo-issue-submit-btn", "n_clicks"),
            Input("wo-qc-submit-btn", "n_clicks"),
            Input("wo-complete-submit-btn", "n_clicks"),
            Input("wo-release-btn", "n_clicks"),
            Input("wo-start-btn", "n_clicks"),
            Input("wo-void-btn", "n_clicks"),
        ],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def refresh_detail_view(
        issue_clicks,
        qc_clicks,
        complete_clicks,
        release_clicks,
        start_clicks,
        void_clicks,
        wo_id,
    ):
        """Refresh detail view after actions."""
        ctx = dash.callback_context
        if not ctx.triggered or not wo_id:
            raise PreventUpdate

        try:
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                wo = response.json()
                return create_work_order_detail_layout(wo), wo_id
            else:
                return no_update, no_update
        except Exception as e:
            print(f"Error refreshing detail: {e}")
            return no_update, no_update

    # Detail tab content switching
    @app.callback(
        Output("wo-detail-tab-content", "children"),
        [Input("wo-detail-tabs", "active_tab")],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def switch_detail_tabs(active_tab, wo_id):
        """Switch between detail view tabs."""
        if not wo_id:
            return html.Div("No work order selected")

        try:
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                return html.Div(f"Error loading work order: {response.status_code}")

            wo = response.json()

            if active_tab == "wo-detail-inputs":
                # Inputs tab
                inputs = wo.get("inputs", [])
                table_data = []
                for inp in inputs:
                    table_data.append(
                        {
                            "id": inp.get("id"),
                            "component": inp.get("component_product_id", ""),
                            "planned": f"{inp.get('planned_qty', 0):.3f}"
                            if inp.get("planned_qty")
                            else "0",
                            "actual": f"{inp.get('actual_qty', 0):.3f}"
                            if inp.get("actual_qty")
                            else "0",
                            "uom": inp.get("uom", "KG"),
                            "unit_cost": f"${inp.get('unit_cost', 0):.2f}"
                            if inp.get("unit_cost")
                            else "N/A",
                            "batch": inp.get("source_batch_id", ""),
                        }
                    )

                return dbc.Card(
                    [
                        dbc.CardHeader("Input Materials"),
                        dbc.CardBody(
                            [
                                dash_table.DataTable(
                                    id="wo-inputs-table",
                                    columns=[
                                        {"name": "Component", "id": "component"},
                                        {"name": "Planned", "id": "planned"},
                                        {"name": "Actual", "id": "actual"},
                                        {"name": "UOM", "id": "uom"},
                                        {"name": "Unit Cost", "id": "unit_cost"},
                                        {"name": "Batch", "id": "batch"},
                                    ],
                                    data=table_data,
                                    row_selectable="single",
                                ),
                                html.Hr(),
                                html.H5("Issue Material"),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Component"),
                                                dcc.Dropdown(
                                                    id="wo-issue-component-dropdown",
                                                    options=[],
                                                ),
                                            ],
                                            md=4,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Quantity"),
                                                dbc.Input(
                                                    id="wo-issue-qty",
                                                    type="number",
                                                    step=0.001,
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Batch (optional)"),
                                                dcc.Dropdown(
                                                    id="wo-issue-batch-dropdown",
                                                    options=[],
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("UOM"),
                                                dbc.Input(
                                                    id="wo-issue-uom",
                                                    type="text",
                                                    value="KG",
                                                ),
                                            ],
                                            md=2,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Button(
                                    "Issue Material",
                                    id="wo-issue-submit-btn",
                                    color="primary",
                                ),
                            ]
                        ),
                    ]
                )

            elif active_tab == "wo-detail-outputs":
                # Outputs tab
                outputs = wo.get("outputs", [])
                if not outputs:
                    return dbc.Card(
                        [
                            dbc.CardHeader("Outputs"),
                            dbc.CardBody(
                                [
                                    html.P(
                                        "No outputs yet. Complete the work order to create outputs."
                                    ),
                                    html.Hr(),
                                    html.H5("Complete Work Order"),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Quantity Produced *"),
                                                    dbc.Input(
                                                        id="wo-complete-qty",
                                                        type="number",
                                                        step=0.001,
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Button(
                                        "Complete Work Order",
                                        id="wo-complete-submit-btn",
                                        color="success",
                                    ),
                                ]
                            ),
                        ]
                    )

                table_data = []
                for out in outputs:
                    table_data.append(
                        {
                            "id": out.get("id"),
                            "product": out.get("product_id", ""),
                            "qty_produced": f"{out.get('qty_produced', 0):.3f}",
                            "uom": out.get("uom", "KG"),
                            "batch": out.get("batch_id", ""),
                            "unit_cost": f"${out.get('unit_cost', 0):.2f}"
                            if out.get("unit_cost")
                            else "N/A",
                        }
                    )

                return dbc.Card(
                    [
                        dbc.CardHeader("Outputs"),
                        dbc.CardBody(
                            dash_table.DataTable(
                                id="wo-outputs-table",
                                columns=[
                                    {"name": "Product", "id": "product"},
                                    {"name": "Qty Produced", "id": "qty_produced"},
                                    {"name": "UOM", "id": "uom"},
                                    {"name": "Batch", "id": "batch"},
                                    {"name": "Unit Cost", "id": "unit_cost"},
                                ],
                                data=table_data,
                            )
                        ),
                    ]
                )

            elif active_tab == "wo-detail-qc":
                # QC Tests tab
                qc_tests = wo.get("qc_tests", [])
                table_data = []
                for qc in qc_tests:
                    table_data.append(
                        {
                            "id": qc.get("id"),
                            "test_type": qc.get("test_type", ""),
                            "result": f"{qc.get('result_value', '')}"
                            if qc.get("result_value")
                            else qc.get("result_text", ""),
                            "unit": qc.get("unit", ""),
                            "status": qc.get("status", "").title(),
                            "tested_at": qc.get("tested_at", ""),
                            "tester": qc.get("tester", ""),
                        }
                    )

                return dbc.Card(
                    [
                        dbc.CardHeader("QC Tests"),
                        dbc.CardBody(
                            [
                                dash_table.DataTable(
                                    id="wo-qc-table",
                                    columns=[
                                        {"name": "Test Type", "id": "test_type"},
                                        {"name": "Result", "id": "result"},
                                        {"name": "Unit", "id": "unit"},
                                        {"name": "Status", "id": "status"},
                                        {"name": "Tested At", "id": "tested_at"},
                                        {"name": "Tester", "id": "tester"},
                                    ],
                                    data=table_data,
                                ),
                                html.Hr(),
                                html.H5("Record QC Test"),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Test Type *"),
                                                dbc.Input(
                                                    id="wo-qc-test-type",
                                                    type="text",
                                                    placeholder="e.g., ABV",
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Result Value"),
                                                dbc.Input(
                                                    id="wo-qc-result-value",
                                                    type="number",
                                                    step=0.01,
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Result Text"),
                                                dbc.Input(
                                                    id="wo-qc-result-text", type="text"
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Unit"),
                                                dbc.Input(
                                                    id="wo-qc-unit",
                                                    type="text",
                                                    placeholder="%, pH",
                                                ),
                                            ],
                                            md=3,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Status"),
                                                dcc.Dropdown(
                                                    id="wo-qc-status",
                                                    options=[
                                                        {
                                                            "label": "Pending",
                                                            "value": "pending",
                                                        },
                                                        {
                                                            "label": "Pass",
                                                            "value": "pass",
                                                        },
                                                        {
                                                            "label": "Fail",
                                                            "value": "fail",
                                                        },
                                                    ],
                                                    value="pending",
                                                ),
                                            ],
                                            md=4,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Tester"),
                                                dbc.Input(
                                                    id="wo-qc-tester", type="text"
                                                ),
                                            ],
                                            md=4,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Note"),
                                                dbc.Input(id="wo-qc-note", type="text"),
                                            ],
                                            md=4,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Button(
                                    "Record QC Test",
                                    id="wo-qc-submit-btn",
                                    color="primary",
                                ),
                            ]
                        ),
                    ]
                )

            elif active_tab == "wo-detail-costs":
                return html.Div(id="wo-costs-content")

            elif active_tab == "wo-detail-genealogy":
                return html.Div(id="wo-genealogy-content")

        except Exception as e:
            return html.Div(f"Error: {str(e)}")

        return html.Div()


def create_work_order_detail_layout(wo: dict) -> html.Div:
    """Create detailed layout for work order."""
    status_colors = {
        "draft": "secondary",
        "released": "info",
        "in_progress": "warning",
        "hold": "danger",
        "complete": "success",
        "void": "dark",
    }

    status = wo.get("status", "").lower()
    badge_color = status_colors.get(status, "secondary")

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4(f"Work Order: {wo.get('code', '')}"),
                            dbc.Badge(
                                wo.get("status", "").title(),
                                color=badge_color,
                                className="ms-2",
                            ),
                        ]
                    )
                ],
                className="mb-3",
            ),
            # Info cards
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Product"),
                                dbc.CardBody(html.P(wo.get("product_id", ""))),
                            ]
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Planned Qty"),
                                dbc.CardBody(
                                    html.P(
                                        f"{wo.get('planned_qty', 0):.3f} {wo.get('uom', 'KG')}"
                                    )
                                ),
                            ]
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Work Center"),
                                dbc.CardBody(html.P(wo.get("work_center", "N/A"))),
                            ]
                        ),
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            # Action buttons
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Release",
                                id="wo-release-btn",
                                color="primary",
                                className="me-2",
                                disabled=status != "draft",
                            ),
                            dbc.Button(
                                "Start",
                                id="wo-start-btn",
                                color="success",
                                className="me-2",
                                disabled=status not in ["released", "hold"],
                            ),
                            dbc.Button(
                                "Void",
                                id="wo-void-btn",
                                color="danger",
                                className="me-2",
                                disabled=status in ["complete", "void"],
                            ),
                        ]
                    )
                ],
                className="mb-3",
            ),
            # Tabs for detail views
            dbc.Tabs(
                [
                    dbc.Tab(label="Inputs", tab_id="wo-detail-inputs"),
                    dbc.Tab(label="Outputs", tab_id="wo-detail-outputs"),
                    dbc.Tab(label="QC Tests", tab_id="wo-detail-qc"),
                    dbc.Tab(label="Costs", tab_id="wo-detail-costs"),
                    dbc.Tab(label="Genealogy", tab_id="wo-detail-genealogy"),
                ],
                id="wo-detail-tabs",
                active_tab="wo-detail-inputs",
                className="mb-3",
            ),
            html.Div(id="wo-detail-tab-content"),
        ],
        fluid=True,
    )

"""Callbacks for purchase and usage table interactions."""

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate


def register_purchase_usage_callbacks(app, make_api_request):
    """Register callbacks for purchase and usage table calculations."""

    # Calculate usage cost from purchase data
    @app.callback(
        Output("product-usage-cost", "value", allow_duplicate=True),
        [
            Input("product-purchase-quantity", "value"),
            Input("product-purchase-cost", "value"),
            Input("product-usage-quantity", "value"),
        ],
        [State("product-usage-cost", "value")],
        prevent_initial_call=True,
    )
    def calculate_usage_cost(
        purchase_quantity, purchase_cost, usage_quantity, current_cost
    ):
        """Calculate usage cost from purchase data when quantities change."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        # Calculate usage cost: (usage_quantity / purchase_quantity) * purchase_cost
        usage_cost = current_cost  # Preserve existing cost if calculation fails
        if (
            purchase_quantity is not None
            and purchase_cost is not None
            and usage_quantity is not None
        ):
            try:
                purchase_qty = (
                    float(purchase_quantity) if purchase_quantity != "" else 0
                )
                purchase_cost_val = float(purchase_cost) if purchase_cost != "" else 0
                usage_qty = float(usage_quantity) if usage_quantity != "" else 0

                if purchase_qty > 0 and usage_qty > 0:
                    usage_cost = (usage_qty / purchase_qty) * purchase_cost_val
                    usage_cost = round(usage_cost, 2)
            except (ValueError, TypeError, ZeroDivisionError):
                # Keep existing cost or None
                pass

        return usage_cost

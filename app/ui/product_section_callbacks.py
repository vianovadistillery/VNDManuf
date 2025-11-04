"""Callbacks for greying out product sections based on capabilities."""

from dash import Input, Output


def register_product_section_callbacks(app):
    """Register callbacks to grey out sections based on product capabilities."""

    # Grey out Purchase section if is_purchase is False
    @app.callback(
        Output("purchase-disabled-notice", "style"),
        [Input("product-is-purchase", "value")],
    )
    def toggle_purchase_section(is_purchase):
        """Show/hide disabled notice for Purchase section."""
        if is_purchase:
            return {"display": "none"}
        else:
            return {
                "display": "block",
                "backgroundColor": "#f0f0f0",
                "color": "#999",
                "padding": "10px",
                "borderRadius": "5px",
                "marginBottom": "10px",
            }

    # Grey out Assembly section if is_assemble is False
    @app.callback(
        Output("assembly-disabled-notice", "style"),
        [Input("product-is-assemble", "value")],
    )
    def toggle_assembly_section(is_assemble):
        """Show/hide disabled notice for Assembly section."""
        if is_assemble:
            return {"display": "none"}
        else:
            return {
                "display": "block",
                "backgroundColor": "#f0f0f0",
                "color": "#999",
                "padding": "10px",
                "borderRadius": "5px",
                "marginBottom": "10px",
            }

    # Grey out Sales & Pricing section if is_sell is False
    @app.callback(
        Output("sales-pricing-disabled-notice", "style"),
        [Input("product-is-sell", "value")],
    )
    def toggle_sales_section(is_sell):
        """Show/hide disabled notice for Sales & Pricing section."""
        if is_sell:
            return {"display": "none"}
        else:
            return {
                "display": "block",
                "backgroundColor": "#f0f0f0",
                "color": "#999",
                "padding": "10px",
                "borderRadius": "5px",
                "marginBottom": "10px",
            }

    # Apply grey styling to Purchase section content
    @app.callback(
        [
            Output("product-purchase-format-dropdown", "disabled"),
            Output("product-supplier-dropdown", "disabled"),
            Output("product-purchase-quantity", "disabled"),
            Output("product-purchase-unit-dropdown", "disabled"),
            Output("product-purchase-cost", "disabled"),
        ],
        [Input("product-is-purchase", "value")],
    )
    def disable_purchase_fields(is_purchase):
        """Disable purchase fields if is_purchase is False."""
        disabled = not is_purchase
        return disabled, disabled, disabled, disabled, disabled

    # Apply grey styling to Assembly section content
    @app.callback(
        [
            Output("new-assembly-btn", "disabled", allow_duplicate=True),
            Output("edit-assembly-btn", "disabled", allow_duplicate=True),
            Output("duplicate-assembly-btn", "disabled", allow_duplicate=True),
            Output("archive-assembly-btn", "disabled", allow_duplicate=True),
            Output("product-assemblies-table", "style_data_conditional"),
        ],
        [Input("product-is-assemble", "value")],
        prevent_initial_call=True,
    )
    def disable_assembly_fields(is_assemble):
        """Disable assembly fields if is_assemble is False."""
        disabled = not is_assemble
        style_conditional = []
        if not is_assemble:
            # Style all rows when disabled - use filter_query that matches all rows
            # version column always exists in assemblies table
            style_conditional = [
                {
                    "if": {"filter_query": "{version} = {version}"},
                    "backgroundColor": "#f0f0f0",
                    "color": "#999",
                }
            ]
        return disabled, disabled, disabled, disabled, style_conditional

    # Apply grey styling to Sales & Pricing section content
    @app.callback(
        Output("product-pricing-table", "style_data_conditional"),
        [Input("product-is-sell", "value")],
    )
    def disable_sales_fields(is_sell):
        """Disable sales fields if is_sell is False."""
        style_conditional = []
        if not is_sell:
            # Style all rows when disabled - use filter_query that matches all rows
            # price_level column always exists in pricing table
            style_conditional = [
                {
                    "if": {"filter_query": "{price_level} != ''"},
                    "backgroundColor": "#f0f0f0",
                    "color": "#999",
                }
            ]
        return style_conditional

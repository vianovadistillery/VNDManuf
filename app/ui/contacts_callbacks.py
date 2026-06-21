"""CRUD callbacks for contacts page."""

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate


def register_contacts_callbacks(app, make_api_request):
    """Register all contacts CRUD callbacks."""

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("contacts-edit-btn", "disabled"),
            Output("contacts-delete-btn", "disabled"),
        ],
        [Input("contacts-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Load contacts data
    @app.callback(
        Output("contacts-table", "data"),
        [
            Input("main-tabs", "active_tab"),
            Input("contacts-search-btn", "n_clicks"),
            Input("contacts-clear-btn", "n_clicks"),
            Input("contacts-refresh-btn", "n_clicks"),
            Input("effective-tab-store", "data"),
            Input("contacts-active-filter", "value"),
            Input("contacts-filter-customer", "value"),
            Input("contacts-filter-supplier", "value"),
            Input("contacts-filter-other", "value"),
        ],
        [State("contacts-search-filter", "value")],
        prevent_initial_call=False,
    )
    def load_contacts(
        main_tab,
        n_clicks_search,
        n_clicks_clear,
        n_clicks_refresh,
        effective_tab,
        active_filter,
        filter_customer,
        filter_supplier,
        filter_other,
        search_text,
    ):
        """Load contacts from API."""
        # Only load when Contacts tab is active (main_tab ensures we run after tab content is rendered)
        if main_tab != "contacts" and effective_tab != "contacts":
            raise PreventUpdate

        try:
            # Build query params
            params = {}

            # Determine what triggered this callback
            ctx = dash.callback_context
            if not ctx.triggered:
                # Initial load - load all data without filters
                params = {}
            else:
                triggered_id = ctx.triggered[0]["prop_id"]

                # If clear button or refresh button was clicked, load all data without filters
                if triggered_id in [
                    "contacts-clear-btn.n_clicks",
                    "contacts-refresh-btn.n_clicks",
                    "effective-tab-store.data",
                    "main-tabs.active_tab",
                ]:
                    params = {}
                else:
                    # Use filters for search
                    if search_text:
                        params["name"] = search_text  # Search by name

                    # Handle active filter
                    if active_filter:
                        params["is_active"] = True

                    # Apply type filters based on checkboxes
                    if not ctx.triggered[0]["prop_id"].startswith("contacts-filter"):
                        # Only apply type filters if not triggered by checkbox changes
                        # This prevents loading on every checkbox toggle
                        all_checked = (
                            filter_customer and filter_supplier and filter_other
                        )
                        if not all_checked:
                            # At least one unchecked - need to filter
                            # We'll let API handle this
                            pass

            # Apply type filters if any checkbox is unchecked
            if not filter_customer:
                params["is_customer"] = False
            if not filter_supplier:
                params["is_supplier"] = False
            if not filter_other:
                params["is_other"] = False

            response = make_api_request("GET", "/contacts/", data=params)

            # Handle error response
            if "error" in response:
                print(f"Error loading contacts: {response.get('error')}")
                return []

            # API returns a list directly
            return response if isinstance(response, list) else []

        except Exception as e:
            print(f"Exception loading contacts: {e}")
            return []

    # Open add/edit modal
    @app.callback(
        [
            Output("contacts-modal", "is_open", allow_duplicate=True),
            Output("contacts-modal-title", "children", allow_duplicate=True),
            Output("contacts-form-id-hidden", "children", allow_duplicate=True),
            Output("contacts-form-code", "value", allow_duplicate=True),
            Output("contacts-form-name", "value", allow_duplicate=True),
            Output("contacts-form-contact", "value", allow_duplicate=True),
            Output("contacts-form-email", "value", allow_duplicate=True),
            Output("contacts-form-phone", "value", allow_duplicate=True),
            Output("contacts-form-address", "value", allow_duplicate=True),
            Output("contacts-form-billing-line1", "value", allow_duplicate=True),
            Output("contacts-form-billing-line2", "value", allow_duplicate=True),
            Output("contacts-form-billing-suburb", "value", allow_duplicate=True),
            Output("contacts-form-billing-state", "value", allow_duplicate=True),
            Output("contacts-form-billing-postcode", "value", allow_duplicate=True),
            Output("contacts-form-billing-country", "value", allow_duplicate=True),
            Output("contacts-form-delivery-line1", "value", allow_duplicate=True),
            Output("contacts-form-delivery-line2", "value", allow_duplicate=True),
            Output("contacts-form-delivery-suburb", "value", allow_duplicate=True),
            Output("contacts-form-delivery-state", "value", allow_duplicate=True),
            Output("contacts-form-delivery-postcode", "value", allow_duplicate=True),
            Output("contacts-form-delivery-country", "value", allow_duplicate=True),
            Output("contacts-form-abn", "value", allow_duplicate=True),
            Output("contacts-form-alm-account", "value", allow_duplicate=True),
            Output("contacts-form-payment-method", "value", allow_duplicate=True),
            Output("contacts-form-paramount-number", "value", allow_duplicate=True),
            Output(
                "contacts-form-default-pricing-level", "value", allow_duplicate=True
            ),
            Output("contacts-form-notes", "value", allow_duplicate=True),
            Output("contacts-form-xero-id", "value", allow_duplicate=True),
            Output("contacts-form-is-customer", "value", allow_duplicate=True),
            Output("contacts-form-is-supplier", "value", allow_duplicate=True),
            Output("contacts-form-is-other", "value", allow_duplicate=True),
            Output("contacts-form-active", "value", allow_duplicate=True),
        ],
        [Input("contacts-add-btn", "n_clicks"), Input("contacts-edit-btn", "n_clicks")],
        [State("contacts-table", "selected_rows"), State("contacts-table", "data")],
        prevent_initial_call=True,
    )
    def open_contacts_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "contacts-add-btn":
            empty_extra = (
                [None] * 18
            )  # billing (6) + delivery (6) + abn + alm + payment_method + paramount + pricing + notes
            return (
                [True, "Add Contact", None, None, None, None, None, None, None]
                + empty_extra
                + [
                    None,
                    False,
                    False,
                    False,
                    True,
                ]  # xero_id, is_customer, is_supplier, is_other, is_active
            )

        elif button_id == "contacts-edit-btn":
            if not selected_rows or not data:
                return [False, ""] + [None] * 32

            contact = data[selected_rows[0]]
            return [
                True,
                "Edit Contact",
                contact.get("id"),
                contact.get("code", ""),
                contact.get("name", ""),
                contact.get("contact_person", ""),
                contact.get("email", ""),
                contact.get("phone", ""),
                contact.get("address", ""),
                contact.get("billing_address_line1") or "",
                contact.get("billing_address_line2") or "",
                contact.get("billing_suburb") or "",
                contact.get("billing_state") or "",
                contact.get("billing_postcode") or "",
                contact.get("billing_country") or "",
                contact.get("delivery_address_line1") or "",
                contact.get("delivery_address_line2") or "",
                contact.get("delivery_suburb") or "",
                contact.get("delivery_state") or "",
                contact.get("delivery_postcode") or "",
                contact.get("delivery_country") or "",
                contact.get("abn") or "",
                contact.get("alm_account_number") or "",
                contact.get("payment_method"),
                contact.get("paramount_number"),
                contact.get("default_pricing_level"),
                contact.get("notes") or "",
                contact.get("xero_contact_id", ""),
                contact.get("is_customer", False),
                contact.get("is_supplier", False),
                contact.get("is_other", False),
                contact.get("is_active", True),
            ]

        raise PreventUpdate

    # Close modal
    @app.callback(
        Output("contacts-modal", "is_open", allow_duplicate=True),
        [
            Input("contacts-modal-cancel", "n_clicks"),
            Input("contacts-modal-save", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def close_contacts_modal(cancel_clicks, save_clicks):
        """Close modal when cancel or save is clicked."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return False

    # Save contact
    @app.callback(
        [
            Output("contacts-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("contacts-modal-save", "n_clicks")],
        [
            State("contacts-form-code", "value"),
            State("contacts-form-name", "value"),
            State("contacts-form-contact", "value"),
            State("contacts-form-email", "value"),
            State("contacts-form-phone", "value"),
            State("contacts-form-address", "value"),
            State("contacts-form-billing-line1", "value"),
            State("contacts-form-billing-line2", "value"),
            State("contacts-form-billing-suburb", "value"),
            State("contacts-form-billing-state", "value"),
            State("contacts-form-billing-postcode", "value"),
            State("contacts-form-billing-country", "value"),
            State("contacts-form-delivery-line1", "value"),
            State("contacts-form-delivery-line2", "value"),
            State("contacts-form-delivery-suburb", "value"),
            State("contacts-form-delivery-state", "value"),
            State("contacts-form-delivery-postcode", "value"),
            State("contacts-form-delivery-country", "value"),
            State("contacts-form-abn", "value"),
            State("contacts-form-alm-account", "value"),
            State("contacts-form-payment-method", "value"),
            State("contacts-form-paramount-number", "value"),
            State("contacts-form-default-pricing-level", "value"),
            State("contacts-form-notes", "value"),
            State("contacts-form-xero-id", "value"),
            State("contacts-form-is-customer", "value"),
            State("contacts-form-is-supplier", "value"),
            State("contacts-form-is-other", "value"),
            State("contacts-form-active", "value"),
            State("contacts-modal-title", "children"),
            State("contacts-form-id-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_contact(
        n_clicks,
        code,
        name,
        contact,
        email,
        phone,
        address,
        billing_line1,
        billing_line2,
        billing_suburb,
        billing_state,
        billing_postcode,
        billing_country,
        delivery_line1,
        delivery_line2,
        delivery_suburb,
        delivery_state,
        delivery_postcode,
        delivery_country,
        abn,
        alm_account_number,
        payment_method,
        paramount_number,
        default_pricing_level,
        notes,
        xero_id,
        is_customer,
        is_supplier,
        is_other,
        is_active,
        title,
        contact_id,
    ):
        """Save or update contact."""
        if not n_clicks:
            raise PreventUpdate

        # Validate required fields
        if not name:
            return no_update, True, "Error", "Name is required"

        # At least one contact type must be selected
        if not is_customer and not is_supplier and not is_other:
            return (
                no_update,
                True,
                "Error",
                "At least one contact type must be selected",
            )

        try:
            # Determine if this is edit mode
            is_edit = title == "Edit Contact" and contact_id is not None

            def _payload():
                p = {
                    "name": name,
                    "contact_person": contact or None,
                    "email": email or None,
                    "phone": phone or None,
                    "address": address or None,
                    "billing_address_line1": billing_line1 or None,
                    "billing_address_line2": billing_line2 or None,
                    "billing_suburb": billing_suburb or None,
                    "billing_state": billing_state or None,
                    "billing_postcode": billing_postcode or None,
                    "billing_country": billing_country or None,
                    "delivery_address_line1": delivery_line1 or None,
                    "delivery_address_line2": delivery_line2 or None,
                    "delivery_suburb": delivery_suburb or None,
                    "delivery_state": delivery_state or None,
                    "delivery_postcode": delivery_postcode or None,
                    "delivery_country": delivery_country or None,
                    "abn": abn or None,
                    "notes": notes or None,
                    "alm_account_number": alm_account_number or None,
                    "payment_method": payment_method or None,
                    "paramount_number": paramount_number or None,
                    "default_pricing_level": default_pricing_level or None,
                    "xero_contact_id": xero_id or None,
                    "is_customer": is_customer if is_customer else False,
                    "is_supplier": is_supplier if is_supplier else False,
                    "is_other": is_other if is_other else False,
                    "is_active": is_active if is_active is not None else True,
                }
                if code:
                    p["code"] = code
                return p

            if is_edit:
                payload = _payload()
                response = make_api_request("PUT", f"/contacts/{contact_id}", payload)
            else:
                payload = _payload()
                response = make_api_request("POST", "/contacts/", payload)

            # Check for error response
            if "error" in response:
                return no_update, True, "Error", response.get("error")

            # Reload data
            reload_response = make_api_request("GET", "/contacts/")
            if "error" in reload_response:
                return (
                    no_update,
                    True,
                    "Error",
                    f"Error reloading: {reload_response.get('error')}",
                )

            # API returns list directly
            new_data = reload_response if isinstance(reload_response, list) else []

            success_msg = (
                f"Contact {name} {'updated' if is_edit else 'created'} successfully"
            )
            return new_data, True, "Success", success_msg

        except Exception as e:
            return no_update, True, "Error", f"Exception saving contact: {str(e)}"

    # Delete contact confirmation
    @app.callback(
        [
            Output("contacts-delete-name", "children"),
            Output("contacts-delete-modal", "is_open"),
        ],
        [
            Input("contacts-delete-btn", "n_clicks"),
            Input("contacts-delete-confirm", "n_clicks"),
            Input("contacts-delete-cancel", "n_clicks"),
        ],
        [State("contacts-table", "selected_rows"), State("contacts-table", "data")],
        prevent_initial_call=True,
    )
    def toggle_delete_contact_modal(
        delete_clicks, confirm_clicks, cancel_clicks, selected_rows, data
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "", False

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "contacts-delete-btn" and selected_rows and data:
            contact = data[selected_rows[0]]
            contact_name = contact.get("name", "Unknown")
            return contact_name, True
        elif button_id == "contacts-delete-cancel":
            return "", False
        elif button_id == "contacts-delete-confirm":
            return "", False

        return "", False

    # Actual delete
    @app.callback(
        [
            Output("contacts-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("contacts-delete-confirm", "n_clicks")],
        [State("contacts-table", "selected_rows"), State("contacts-table", "data")],
        prevent_initial_call=True,
    )
    def delete_contact(n_clicks, selected_rows, data):
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        contact = data[selected_rows[0]]
        contact_id = contact.get("id")
        contact_name = contact.get("name")

        try:
            make_api_request("DELETE", f"/contacts/{contact_id}")

            # Reload data from API
            reload_response = make_api_request("GET", "/contacts/")
            if "error" in reload_response:
                new_data = [row for i, row in enumerate(data) if i not in selected_rows]
            else:
                new_data = reload_response if isinstance(reload_response, list) else []

            return (
                new_data,
                True,
                "Success",
                f"Contact {contact_name} deleted successfully",
            )

        except Exception as e:
            return no_update, True, "Error", f"Failed to delete contact: {str(e)}"

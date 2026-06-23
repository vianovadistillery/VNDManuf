"""Callbacks for Sales Settings — reps and buying groups."""

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate


def register_crm_settings_callbacks(app, make_api_request):
    @app.callback(
        [
            Output("sales-reps-table", "data"),
            Output("sales-buying-groups-table", "data"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-reps-refresh", "n_clicks"),
            Input("sales-rep-add", "n_clicks"),
            Input("sales-rep-modal-save", "n_clicks"),
            Input("sales-rep-delete-btn", "n_clicks"),
            Input("sales-buying-group-add", "n_clicks"),
            Input("sales-buying-group-modal-save", "n_clicks"),
            Input("sales-buying-group-delete-btn", "n_clicks"),
        ],
        prevent_initial_call=False,
    )
    def load_crm_settings_tables(subtab, *_):
        if subtab != "sales-settings":
            return no_update, no_update
        reps = make_api_request("GET", "/sales-reps/")
        groups = make_api_request("GET", "/buying-groups/")
        reps_data = []
        for r in reps if isinstance(reps, list) else []:
            reps_data.append(
                {
                    **r,
                    "is_active": "Yes" if r.get("is_active") else "No",
                }
            )
        groups_data = []
        for g in groups if isinstance(groups, list) else []:
            groups_data.append(
                {
                    **g,
                    "map_color": g.get("map_color") or "#9E9E9E",
                    "description": g.get("description") or "—",
                    "is_active": "Yes" if g.get("is_active") else "No",
                }
            )
        return reps_data, groups_data

    @app.callback(
        [
            Output("sales-rep-edit-btn", "disabled"),
            Output("sales-rep-delete-btn", "disabled"),
        ],
        Input("sales-reps-table", "selected_rows"),
    )
    def toggle_rep_actions(selected_rows):
        disabled = not selected_rows
        return disabled, disabled

    @app.callback(
        [
            Output("sales-rep-modal", "is_open"),
            Output("sales-rep-modal-title", "children"),
            Output("sales-rep-modal-id", "data"),
            Output("sales-rep-modal-code", "value"),
            Output("sales-rep-modal-name", "value"),
            Output("sales-rep-modal-email", "value"),
            Output("sales-rep-modal-phone", "value"),
            Output("sales-rep-modal-active", "value"),
        ],
        [
            Input("sales-rep-edit-btn", "n_clicks"),
            Input("sales-rep-modal-cancel", "n_clicks"),
        ],
        [
            State("sales-reps-table", "selected_rows"),
            State("sales-reps-table", "data"),
            State("sales-rep-modal", "is_open"),
        ],
        prevent_initial_call=True,
    )
    def open_rep_modal(edit_clicks, cancel_clicks, selected_rows, data, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "sales-rep-modal-cancel":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if trigger == "sales-rep-edit-btn" and selected_rows and data:
            rep = data[selected_rows[0]]
            active = rep.get("is_active")
            if isinstance(active, str):
                active = active == "Yes"
            return (
                True,
                "Edit sales rep",
                rep.get("id"),
                rep.get("code", ""),
                rep.get("name", ""),
                rep.get("email") or "",
                rep.get("phone") or "",
                bool(active),
            )
        raise PreventUpdate

    @app.callback(
        [
            Output("sales-rep-modal", "is_open", allow_duplicate=True),
            Output("sales-rep-feedback", "children", allow_duplicate=True),
        ],
        Input("sales-rep-modal-save", "n_clicks"),
        [
            State("sales-rep-modal-id", "data"),
            State("sales-rep-modal-code", "value"),
            State("sales-rep-modal-name", "value"),
            State("sales-rep-modal-email", "value"),
            State("sales-rep-modal-phone", "value"),
            State("sales-rep-modal-active", "value"),
        ],
        prevent_initial_call=True,
    )
    def save_rep_modal(n_clicks, rep_id, code, name, email, phone, is_active):
        if not n_clicks:
            raise PreventUpdate
        if not (name or "").strip():
            return True, "Name is required."
        payload = {
            "code": (code or "").strip()
            or (name or "").strip()[:8].upper().replace(" ", ""),
            "name": name.strip(),
            "email": (email or "").strip() or None,
            "phone": (phone or "").strip() or None,
            "is_active": bool(is_active),
        }
        if rep_id:
            response = make_api_request("PUT", f"/sales-reps/{rep_id}", payload)
        else:
            response = make_api_request("POST", "/sales-reps/", payload)
        if isinstance(response, dict) and response.get("error"):
            return True, response["error"]
        return False, "Rep saved."

    @app.callback(
        Output("sales-rep-feedback", "children", allow_duplicate=True),
        Input("sales-rep-delete-btn", "n_clicks"),
        [
            State("sales-reps-table", "selected_rows"),
            State("sales-reps-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_rep(n_clicks, selected_rows, data):
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate
        rep_id = data[selected_rows[0]].get("id")
        response = make_api_request("DELETE", f"/sales-reps/{rep_id}")
        if isinstance(response, dict) and response.get("error"):
            return response["error"]
        return "Rep deleted."

    @app.callback(
        [
            Output("sales-rep-feedback", "children"),
            Output("sales-rep-code", "value"),
            Output("sales-rep-name", "value"),
            Output("sales-rep-email", "value"),
            Output("sales-rep-phone", "value"),
        ],
        Input("sales-rep-add", "n_clicks"),
        [
            State("sales-rep-code", "value"),
            State("sales-rep-name", "value"),
            State("sales-rep-email", "value"),
            State("sales-rep-phone", "value"),
        ],
        prevent_initial_call=True,
    )
    def add_rep(n_clicks, code, name, email, phone):
        if not n_clicks:
            raise PreventUpdate
        if not (name or "").strip():
            return "Name is required.", no_update, no_update, no_update, no_update
        if not (code or "").strip():
            code = (name or "").strip()[:8].upper().replace(" ", "")
        payload = {
            "code": code.strip(),
            "name": name.strip(),
            "email": (email or "").strip() or None,
            "phone": (phone or "").strip() or None,
            "is_active": True,
        }
        response = make_api_request("POST", "/sales-reps/", payload)
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update, no_update, no_update, no_update
        return "Rep added.", "", "", "", ""

    @app.callback(
        [
            Output("sales-buying-group-feedback", "children"),
            Output("sales-buying-group-code", "value"),
            Output("sales-buying-group-name", "value"),
            Output("sales-buying-group-desc", "value"),
            Output("sales-buying-group-color", "value"),
        ],
        Input("sales-buying-group-add", "n_clicks"),
        [
            State("sales-buying-group-code", "value"),
            State("sales-buying-group-name", "value"),
            State("sales-buying-group-desc", "value"),
            State("sales-buying-group-color", "value"),
        ],
        prevent_initial_call=True,
    )
    def add_buying_group(n_clicks, code, name, desc, map_color):
        if not n_clicks:
            raise PreventUpdate
        if not (name or "").strip():
            return "Name is required.", no_update, no_update, no_update, no_update
        if not (code or "").strip():
            code = (name or "").strip()[:12].upper().replace(" ", "_")
        payload = {
            "code": code.strip(),
            "name": name.strip(),
            "description": (desc or "").strip() or None,
            "map_color": map_color or "#9E9E9E",
            "is_active": True,
        }
        response = make_api_request("POST", "/buying-groups/", payload)
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update, no_update, no_update, no_update
        return "Buying group added.", "", "", "", "#9E9E9E"

    @app.callback(
        [
            Output("sales-buying-group-edit-btn", "disabled"),
            Output("sales-buying-group-delete-btn", "disabled"),
        ],
        Input("sales-buying-groups-table", "selected_rows"),
    )
    def toggle_buying_group_actions(selected_rows):
        disabled = not selected_rows
        return disabled, disabled

    @app.callback(
        [
            Output("sales-buying-group-modal", "is_open"),
            Output("sales-buying-group-modal-title", "children"),
            Output("sales-buying-group-modal-id", "data"),
            Output("sales-buying-group-modal-code", "value"),
            Output("sales-buying-group-modal-name", "value"),
            Output("sales-buying-group-modal-desc", "value"),
            Output("sales-buying-group-modal-color", "value"),
            Output("sales-buying-group-modal-active", "value"),
        ],
        [
            Input("sales-buying-group-edit-btn", "n_clicks"),
            Input("sales-buying-group-modal-cancel", "n_clicks"),
        ],
        [
            State("sales-buying-groups-table", "selected_rows"),
            State("sales-buying-groups-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def open_buying_group_modal(edit_clicks, cancel_clicks, selected_rows, data):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "sales-buying-group-modal-cancel":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if trigger == "sales-buying-group-edit-btn" and selected_rows and data:
            group = data[selected_rows[0]]
            active = group.get("is_active")
            if isinstance(active, str):
                active = active == "Yes"
            desc = group.get("description")
            if desc == "—":
                desc = ""
            return (
                True,
                "Edit buying group",
                group.get("id"),
                group.get("code", ""),
                group.get("name", ""),
                desc or "",
                group.get("map_color") or "#9E9E9E",
                bool(active),
            )
        raise PreventUpdate

    @app.callback(
        [
            Output("sales-buying-group-modal", "is_open", allow_duplicate=True),
            Output("sales-buying-group-feedback", "children", allow_duplicate=True),
        ],
        Input("sales-buying-group-modal-save", "n_clicks"),
        [
            State("sales-buying-group-modal-id", "data"),
            State("sales-buying-group-modal-code", "value"),
            State("sales-buying-group-modal-name", "value"),
            State("sales-buying-group-modal-desc", "value"),
            State("sales-buying-group-modal-color", "value"),
            State("sales-buying-group-modal-active", "value"),
        ],
        prevent_initial_call=True,
    )
    def save_buying_group_modal(
        n_clicks, group_id, code, name, desc, map_color, is_active
    ):
        if not n_clicks:
            raise PreventUpdate
        if not (name or "").strip():
            return True, "Name is required."
        payload = {
            "code": (code or "").strip()
            or (name or "").strip()[:12].upper().replace(" ", "_"),
            "name": name.strip(),
            "description": (desc or "").strip() or None,
            "map_color": map_color or "#9E9E9E",
            "is_active": bool(is_active),
        }
        if group_id:
            response = make_api_request("PUT", f"/buying-groups/{group_id}", payload)
        else:
            response = make_api_request("POST", "/buying-groups/", payload)
        if isinstance(response, dict) and response.get("error"):
            return True, response["error"]
        return False, "Buying group saved."

    @app.callback(
        Output("sales-buying-group-feedback", "children", allow_duplicate=True),
        Input("sales-buying-group-delete-btn", "n_clicks"),
        [
            State("sales-buying-groups-table", "selected_rows"),
            State("sales-buying-groups-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_buying_group(n_clicks, selected_rows, data):
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate
        group_id = data[selected_rows[0]].get("id")
        response = make_api_request("DELETE", f"/buying-groups/{group_id}")
        if isinstance(response, dict) and response.get("error"):
            return response["error"]
        return "Buying group deleted."

"""Callbacks for Sales Import / Export tab (customer name mappings and CSV import)."""

from __future__ import annotations

import base64
from contextlib import closing

from dash import Input, Output, State, no_update

from app.adapters.db import get_session
from apps.vndmanuf_sales.services.import_sales_csv import (
    SalesCSVImporter,
    decode_csv_bytes,
)


def _preview_table_rows(groups):
    rows = []
    default_selected = []
    for idx, group in enumerate(groups or []):
        row = dict(group)
        row["line_count"] = group.get("line_count", 0)
        rows.append(row)
        if group.get("include_by_default"):
            default_selected.append(idx)
    return rows, default_selected


def _preview_summary_text(preview_dict):
    groups = preview_dict.get("groups") or []
    total = len(groups)
    db_dupes = sum(1 for g in groups if g.get("duplicate_in_db"))
    csv_dupes = sum(1 for g in groups if g.get("duplicate_in_csv"))
    mapped = sum(1 for g in groups if g.get("customer_mapped"))
    missing = sum(1 for g in groups if g.get("customer_missing"))
    default = sum(1 for g in groups if g.get("include_by_default"))
    filename = preview_dict.get("filename") or "upload.csv"
    fmt = preview_dict.get("format") or "sales"
    return (
        f"File: {filename} | Format: {fmt} | Records: {total} | "
        f"Selected by default: {default} | Customer mapped: {mapped} | "
        f"Missing customer: {missing} | DB duplicates: {db_dupes} | "
        f"Duplicate lines in file: {csv_dupes}"
    )


def _import_summary_rows(summary):
    return [
        {
            "order_ref": r.docket_number or r.order_ref,
            "customer": r.customer,
            "lines": r.lines,
            "status": r.status,
            "message": r.message,
        }
        for r in summary.order_results
    ]


def _import_result_message(summary):
    headline = (
        f"Format: {summary.format} | Inserted: {summary.orders_inserted} | "
        f"Updated: {summary.orders_updated} | Lines: {summary.lines_processed}"
    )
    if summary.dockets_created:
        headline += f" | Dockets created: {summary.dockets_created}"
    if summary.errors:
        detail = "\n".join(summary.errors[:5])
        return (
            f"{headline}\nErrors:\n{detail}",
            "warning" if summary.order_results else "danger",
        )
    return headline, "success"


def register_sales_import_callbacks(app, make_api_request):
    @app.callback(
        [
            Output("sales-customer-alias-customer", "options"),
            Output("sales-customer-alias-table", "data"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-customer-alias-refresh", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_customer_alias_data(subtab_value, _refresh):
        if subtab_value != "sales-import-export":
            return no_update, no_update

        customers = make_api_request("GET", "/sales/customers")
        aliases = make_api_request("GET", "/sales/customer-import-aliases")
        customers = customers if isinstance(customers, list) else []
        aliases = aliases if isinstance(aliases, list) else []

        customer_options = [
            {"label": f"{c.get('name', '')} ({c.get('code', '')})", "value": c["id"]}
            for c in customers
        ]
        table_data = [
            {
                "id": row["id"],
                "alias": row.get("alias", ""),
                "customer_name": row.get("customer_name", ""),
                "notes": row.get("notes") or "",
                "delete_label": "🗑",
            }
            for row in aliases
        ]
        return customer_options, table_data

    @app.callback(
        [
            Output("sales-site-alias-customer", "options"),
            Output("sales-site-alias-table", "data"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-site-alias-refresh", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_site_alias_data(subtab_value, _refresh):
        if subtab_value != "sales-import-export":
            return no_update, no_update

        customers = make_api_request("GET", "/sales/customers")
        aliases = make_api_request("GET", "/sales/customer-site-import-aliases")
        customers = customers if isinstance(customers, list) else []
        aliases = aliases if isinstance(aliases, list) else []

        customer_options = [
            {"label": f"{c.get('name', '')} ({c.get('code', '')})", "value": c["id"]}
            for c in customers
        ]
        table_data = [
            {
                "id": row["id"],
                "customer_name": row.get("customer_name", ""),
                "alias": row.get("alias", ""),
                "site_name": row.get("site_name", ""),
            }
            for row in aliases
        ]
        return customer_options, table_data

    @app.callback(
        [
            Output("sales-site-alias-alert", "children"),
            Output("sales-site-alias-alert", "color"),
            Output("sales-site-alias-alert", "is_open"),
            Output("sales-site-alias-input", "value"),
            Output("sales-site-alias-site-name", "value"),
            Output("sales-site-alias-refresh", "data"),
        ],
        Input("sales-site-alias-add", "n_clicks"),
        [
            State("sales-site-alias-customer", "value"),
            State("sales-site-alias-input", "value"),
            State("sales-site-alias-site-name", "value"),
            State("sales-site-alias-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_site_alias(n_clicks, customer_id, alias, site_name, refresh):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update, no_update
        if not customer_id:
            return (
                "Select a customer.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        if not (alias or "").strip():
            return (
                "Enter the CSV site name.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        if not (site_name or "").strip():
            return (
                "Enter the canonical site name.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )

        response = make_api_request(
            "POST",
            "/sales/customer-site-import-aliases",
            {
                "alias": alias.strip(),
                "customer_id": customer_id,
                "site_name": site_name.strip(),
            },
        )
        if isinstance(response, dict) and response.get("error"):
            return (
                str(response["error"]),
                "danger",
                True,
                no_update,
                no_update,
                no_update,
            )

        return (
            f"Mapped site '{alias.strip()}'.",
            "success",
            True,
            "",
            "",
            (refresh or 0) + 1,
        )

    @app.callback(
        [
            Output("sales-site-alias-alert", "children", allow_duplicate=True),
            Output("sales-site-alias-alert", "color", allow_duplicate=True),
            Output("sales-site-alias-alert", "is_open", allow_duplicate=True),
            Output("sales-site-alias-table", "selected_rows", allow_duplicate=True),
            Output("sales-site-alias-refresh", "data", allow_duplicate=True),
        ],
        Input("sales-site-alias-remove", "n_clicks"),
        [
            State("sales-site-alias-table", "data"),
            State("sales-site-alias-table", "selected_rows"),
            State("sales-site-alias-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def remove_site_alias(n_clicks, table_data, selected_rows, refresh):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update
        if not selected_rows:
            return (
                "Select a site mapping to remove.",
                "warning",
                True,
                no_update,
                no_update,
            )

        row = (table_data or [])[selected_rows[0]]
        alias_id = row.get("id")
        if not alias_id:
            return "Selected row has no id.", "danger", True, no_update, no_update

        response = make_api_request(
            "DELETE",
            f"/sales/customer-site-import-aliases/{alias_id}",
        )
        if isinstance(response, dict) and response.get("error"):
            return str(response["error"]), "danger", True, no_update, no_update

        return (
            f"Removed site mapping for '{row.get('alias', '')}'.",
            "success",
            True,
            [],
            (refresh or 0) + 1,
        )

    @app.callback(
        [
            Output("sales-customer-alias-alert", "children"),
            Output("sales-customer-alias-alert", "color"),
            Output("sales-customer-alias-alert", "is_open"),
            Output("sales-customer-alias-input", "value"),
            Output("sales-customer-alias-customer", "value"),
            Output("sales-customer-alias-refresh", "data"),
        ],
        Input("sales-customer-alias-add", "n_clicks"),
        [
            State("sales-customer-alias-input", "value"),
            State("sales-customer-alias-customer", "value"),
            State("sales-customer-alias-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_customer_alias(n_clicks, alias, customer_id, refresh):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update, no_update
        if not (alias or "").strip():
            return (
                "Enter the CSV customer name.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        if not customer_id:
            return (
                "Select the customer to map to.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )

        response = make_api_request(
            "POST",
            "/sales/customer-import-aliases",
            {"alias": alias.strip(), "customer_id": customer_id},
        )
        if isinstance(response, dict) and response.get("error"):
            return (
                str(response["error"]),
                "danger",
                True,
                no_update,
                no_update,
                no_update,
            )

        return (
            f"Mapped '{alias.strip()}' to customer record.",
            "success",
            True,
            "",
            None,
            (refresh or 0) + 1,
        )

    @app.callback(
        [
            Output("sales-customer-alias-alert", "children", allow_duplicate=True),
            Output("sales-customer-alias-alert", "color", allow_duplicate=True),
            Output("sales-customer-alias-alert", "is_open", allow_duplicate=True),
            Output("sales-customer-alias-table", "selected_rows", allow_duplicate=True),
            Output("sales-customer-alias-refresh", "data", allow_duplicate=True),
        ],
        Input("sales-customer-alias-remove", "n_clicks"),
        [
            State("sales-customer-alias-table", "data"),
            State("sales-customer-alias-table", "selected_rows"),
            State("sales-customer-alias-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def remove_customer_alias(n_clicks, table_data, selected_rows, refresh):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update
        if not selected_rows:
            return (
                "Select a mapping row to remove.",
                "warning",
                True,
                no_update,
                no_update,
            )

        row = (table_data or [])[selected_rows[0]]
        alias_id = row.get("id")
        if not alias_id:
            return "Selected row has no id.", "danger", True, no_update, no_update

        response = make_api_request(
            "DELETE",
            f"/sales/customer-import-aliases/{alias_id}",
        )
        if isinstance(response, dict) and response.get("error"):
            return str(response["error"]), "danger", True, no_update, no_update

        return (
            f"Removed mapping for '{row.get('alias', '')}'.",
            "success",
            True,
            [],
            (refresh or 0) + 1,
        )

    @app.callback(
        [
            Output("sales-import-pending-store", "data"),
            Output("sales-import-preview-modal", "is_open"),
            Output("sales-import-preview-table", "data"),
            Output("sales-import-preview-table", "selected_rows"),
            Output("sales-import-preview-summary", "children"),
            Output("sales-import-result", "children"),
            Output("sales-import-result", "color"),
            Output("sales-import-result", "is_open"),
        ],
        Input("sales-import-upload", "contents"),
        [
            State("sales-import-upload", "filename"),
            State("sales-import-options", "value"),
        ],
        prevent_initial_call=True,
    )
    def preview_import_upload(contents, filename, options):
        if not contents or not filename:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        allow_create = "allow-create" in (options or [])
        create_docket = "create-docket" in (options or [])
        _, payload = contents.split(",", 1)
        decoded = decode_csv_bytes(base64.b64decode(payload))

        try:
            with closing(get_session()) as session:
                importer = SalesCSVImporter(session)
                preview = importer.build_import_preview(
                    decoded,
                    allow_create=allow_create,
                    filename=filename,
                )
        except Exception as exc:  # noqa: BLE001
            return (
                None,
                False,
                [],
                [],
                "",
                f"Could not parse file: {exc}",
                "danger",
                True,
            )

        preview_dict = preview.to_dict()
        if preview.errors:
            return (
                None,
                False,
                [],
                [],
                "",
                "\n".join(preview.errors),
                "danger",
                True,
            )
        if not preview.groups:
            return (
                None,
                False,
                [],
                [],
                "",
                "No import records found in the file.",
                "warning",
                True,
            )

        table_rows, selected_rows = _preview_table_rows(preview_dict.get("groups"))
        pending = {
            "csv_text": decoded,
            "filename": filename,
            "options": {
                "allow_create": allow_create,
                "create_docket": create_docket,
            },
            "format": preview_dict.get("format"),
            "groups": preview_dict.get("groups"),
        }
        return (
            pending,
            True,
            table_rows,
            selected_rows,
            _preview_summary_text(preview_dict),
            no_update,
            no_update,
            no_update,
        )

    @app.callback(
        Output("sales-import-preview-modal", "is_open", allow_duplicate=True),
        Input("sales-import-preview-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def cancel_import_preview(n_clicks):
        if not n_clicks:
            return no_update
        return False

    @app.callback(
        [
            Output("sales-import-preview-modal", "is_open", allow_duplicate=True),
            Output("sales-import-pending-store", "data", allow_duplicate=True),
            Output("sales-import-summary-store", "data"),
            Output("sales-import-result", "children", allow_duplicate=True),
            Output("sales-import-result", "color", allow_duplicate=True),
            Output("sales-import-result", "is_open", allow_duplicate=True),
        ],
        Input("sales-import-preview-confirm", "n_clicks"),
        [
            State("sales-import-pending-store", "data"),
            State("sales-import-preview-table", "data"),
            State("sales-import-preview-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def confirm_import_preview(n_clicks, pending, table_data, selected_rows):
        if not n_clicks:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not pending or not pending.get("csv_text"):
            return False, None, [], "No pending import.", "warning", True
        if not selected_rows:
            return (
                True,
                pending,
                no_update,
                "Select at least one record to import.",
                "warning",
                True,
            )

        selected_keys = []
        for idx in selected_rows:
            if idx < len(table_data or []):
                key = (table_data[idx] or {}).get("group_key")
                if key:
                    selected_keys.append(key)

        opts = pending.get("options") or {}
        try:
            with closing(get_session()) as session:
                importer = SalesCSVImporter(session)
                summary = importer.import_text_selected(
                    pending["csv_text"],
                    selected_keys,
                    allow_create=bool(opts.get("allow_create")),
                    create_delivery_docket=bool(opts.get("create_docket", True)),
                )
                session.commit()
        except Exception as exc:  # noqa: BLE001
            return True, pending, [], f"Import failed: {exc}", "danger", True

        rows = _import_summary_rows(summary)
        message, color = _import_result_message(summary)
        return False, None, rows, message, color, True

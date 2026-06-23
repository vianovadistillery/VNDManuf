"""CRM sub-tab — customer workspace and sales rep portfolio."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from apps.vndmanuf_sales.ui.components import date_range_picker, kpi_card
from apps.vndmanuf_sales.ui.period_filters import (
    default_period_iso,
    period_applying_store,
    period_preset_dropdown,
)

_DEFAULT_START, _DEFAULT_END = default_period_iso()

NOTE_CATEGORIES = [
    {"label": "General", "value": "general"},
    {"label": "Objection", "value": "objection"},
    {"label": "Competitor", "value": "competitor"},
    {"label": "Pricing", "value": "pricing"},
    {"label": "Display", "value": "display"},
    {"label": "Product feedback", "value": "product_feedback"},
]

ACTIVITY_TYPES = [
    {"label": "Note", "value": "note"},
    {"label": "Visit", "value": "visit"},
    {"label": "Phone", "value": "phone"},
    {"label": "Email", "value": "email"},
]

SCHEDULE_TYPES = [
    {"label": "Visit", "value": "visit"},
    {"label": "Phone call", "value": "phone"},
    {"label": "Email", "value": "email"},
]

EXPORT_SECTIONS = [
    {"label": "Full CRM summary", "value": "all"},
    {"label": "Sales", "value": "sales"},
    {"label": "Timeline", "value": "timeline"},
    {"label": "Profile", "value": "profile"},
    {"label": "People", "value": "people"},
    {"label": "Scheduled", "value": "scheduled"},
]


def layout():
    customer_filters = dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Accounts", className="mb-1"),
                            dcc.Dropdown(
                                id="crm-account-scope",
                                options=[
                                    {"label": "All", "value": "all"},
                                    {"label": "Team", "value": "team"},
                                ],
                                value="all",
                                clearable=False,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Customer", className="mb-1"),
                            dcc.Dropdown(
                                id="crm-customer-select",
                                placeholder="Search customer…",
                                searchable=True,
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        period_preset_dropdown("crm-customer-period-preset"),
                        md=2,
                    ),
                    dbc.Col(
                        date_range_picker(
                            "crm-customer-date-range",
                            "Sales period",
                            start_date=_DEFAULT_START,
                            end_date=_DEFAULT_END,
                        ),
                        md=4,
                    ),
                ],
                className="g-2 align-items-end",
            )
        ),
        className="mb-3 shadow-sm",
    )

    rep_filters = dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Sales rep", className="mb-1"),
                            dcc.Dropdown(
                                id="crm-rep-select",
                                placeholder="Select rep…",
                                clearable=True,
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        period_preset_dropdown("crm-rep-period-preset"),
                        md=2,
                    ),
                    dbc.Col(
                        date_range_picker(
                            "crm-rep-date-range",
                            "Activity period",
                            start_date=_DEFAULT_START,
                            end_date=_DEFAULT_END,
                        ),
                        md=6,
                    ),
                ],
                className="g-2 align-items-end",
            )
        ),
        className="mb-3 shadow-sm",
    )

    export_bar = dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("PDF export sections", className="mb-1"),
                            dcc.Dropdown(
                                id="crm-export-sections",
                                options=EXPORT_SECTIONS,
                                value=["all"],
                                multi=True,
                                placeholder="Sections to include…",
                            ),
                        ],
                        md=5,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Print PDF",
                            id="crm-export-btn",
                            color="dark",
                            outline=True,
                            className="mt-4",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        html.Div(id="crm-export-feedback", className="small mt-4"),
                        md=5,
                    ),
                ],
                className="g-2 align-items-start",
            )
        ),
        className="mb-3 shadow-sm",
    )

    header = html.Div(id="crm-customer-header", className="mb-3")

    kpis = dbc.Row(
        [
            dbc.Col(kpi_card("crm-kpi-orders", "Orders", "—"), md=3),
            dbc.Col(kpi_card("crm-kpi-revenue", "Revenue (Inc GST)", "—"), md=3),
            dbc.Col(kpi_card("crm-kpi-units", "Units sold", "—"), md=3),
            dbc.Col(kpi_card("crm-kpi-skus", "Distinct SKUs", "—"), md=3),
        ],
        className="mb-3",
    )

    sales_tab = dbc.Tab(
        label="Sales",
        tab_id="crm-tab-sales",
        children=[
            kpis,
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H6("Orders in period", className="mb-0")
                                ),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id="crm-orders-table",
                                        columns=[
                                            {"name": "Date", "id": "order_date"},
                                            {"name": "Ref", "id": "order_ref"},
                                            {"name": "PO", "id": "po_number"},
                                            {"name": "Status", "id": "status"},
                                            {
                                                "name": "Total (Inc)",
                                                "id": "total_inc_gst",
                                            },
                                        ],
                                        data=[],
                                        page_size=8,
                                        style_table={"overflowX": "auto"},
                                        style_cell={"padding": "0.5rem"},
                                        style_header={
                                            "backgroundColor": "#f8f9fa",
                                            "fontWeight": "bold",
                                        },
                                    )
                                ),
                            ],
                            className="shadow-sm mb-3",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H6("SKU summary", className="mb-0")
                                ),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id="crm-sku-table",
                                        columns=[
                                            {"name": "SKU", "id": "sku"},
                                            {"name": "Product", "id": "name"},
                                            {"name": "Qty", "id": "total_qty"},
                                            {"name": "Orders", "id": "order_count"},
                                            {
                                                "name": "Revenue (Inc)",
                                                "id": "total_inc_gst",
                                            },
                                        ],
                                        data=[],
                                        page_size=8,
                                        style_table={"overflowX": "auto"},
                                        style_cell={"padding": "0.5rem"},
                                        style_header={
                                            "backgroundColor": "#f8f9fa",
                                            "fontWeight": "bold",
                                        },
                                    )
                                ),
                            ],
                            className="shadow-sm mb-3",
                        ),
                        md=6,
                    ),
                ]
            ),
        ],
    )

    note_capture = dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id="crm-note-type",
                                options=ACTIVITY_TYPES,
                                value="note",
                                clearable=False,
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="crm-note-category",
                                options=NOTE_CATEGORIES,
                                value="general",
                                clearable=False,
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Date & time", className="small mb-1"),
                                dbc.Input(
                                    id="crm-note-datetime",
                                    type="datetime-local",
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Button(
                                    "🎤 Dictate",
                                    id="crm-note-dictate-btn",
                                    color="secondary",
                                    outline=True,
                                    className="mt-4 me-1",
                                    title="Start dictation (Chrome/Edge)",
                                ),
                                dbc.Button(
                                    "Stop",
                                    id="crm-note-dictate-stop-btn",
                                    color="danger",
                                    outline=True,
                                    size="sm",
                                    className="mt-4",
                                    style={"display": "none"},
                                    title="Stop dictation",
                                ),
                            ],
                            md=3,
                        ),
                    ],
                    className="g-2 mb-2",
                ),
                dcc.Textarea(
                    id="crm-note-body",
                    placeholder="Type or dictate your note…",
                    style={"width": "100%", "minHeight": "80px"},
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Upload(
                                id="crm-note-photos",
                                children=dbc.Button(
                                    "Add photos",
                                    color="secondary",
                                    outline=True,
                                    size="sm",
                                ),
                                multiple=True,
                                accept="image/*",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div(id="crm-note-photos-preview", className="small"),
                        ),
                    ],
                    className="g-2 mb-2 align-items-center",
                ),
                dbc.Button("Save note", id="crm-note-save", color="primary", size="sm"),
                html.Div(id="crm-note-feedback", className="small mt-2"),
                html.Small(id="crm-note-dictate-status", className="text-muted"),
            ]
        ),
        className="mb-3 shadow-sm",
    )

    schedule_capture = dbc.Card(
        [
            dbc.CardHeader(html.H6("Schedule follow-up", className="mb-0")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id="crm-schedule-type",
                                    options=SCHEDULE_TYPES,
                                    value="visit",
                                    clearable=False,
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="crm-schedule-title",
                                    placeholder="Title *",
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("When", className="small mb-1"),
                                    dbc.Input(
                                        id="crm-schedule-datetime",
                                        type="datetime-local",
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Schedule",
                                    id="crm-schedule-save",
                                    color="warning",
                                    className="mt-4",
                                ),
                                md=2,
                            ),
                        ],
                        className="g-2 mb-2",
                    ),
                    dcc.Textarea(
                        id="crm-schedule-body",
                        placeholder="Optional details…",
                        style={"width": "100%", "minHeight": "50px"},
                    ),
                    html.Div(id="crm-schedule-feedback", className="small mt-2"),
                ]
            ),
        ],
        className="mb-3 shadow-sm",
    )

    scheduled_list = dbc.Card(
        [
            dbc.CardHeader(html.H6("Upcoming scheduled", className="mb-0")),
            dbc.CardBody(html.Div(id="crm-scheduled-list")),
        ],
        className="mb-3 shadow-sm",
    )

    calendar_nav = dbc.Row(
        [
            dbc.Col(
                dbc.Button("◀", id="crm-cal-prev", size="sm", color="light"),
                width="auto",
            ),
            dbc.Col(
                html.H5(id="crm-cal-title", className="text-center mb-0"),
                className="flex-grow-1",
            ),
            dbc.Col(
                dbc.Button("▶", id="crm-cal-next", size="sm", color="light"),
                width="auto",
            ),
        ],
        className="align-items-center mb-2",
    )

    timeline_tab = dbc.Tab(
        label="Timeline",
        tab_id="crm-tab-timeline",
        children=[
            html.Div(id="crm-suggestions-panel", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Calendar", className="mb-0")),
                    dbc.CardBody(
                        [
                            calendar_nav,
                            html.Div(id="crm-calendar-grid"),
                            dcc.Store(id="crm-cal-events-store", data=[]),
                            dcc.Store(id="crm-cal-selected-day", data=None),
                        ]
                    ),
                ],
                className="mb-3 shadow-sm",
            ),
            schedule_capture,
            scheduled_list,
            note_capture,
            html.H6("Activity feed", className="text-muted mb-2"),
            html.Div(id="crm-timeline-list"),
        ],
    )

    profile_tab = dbc.Tab(
        label="Profile",
        tab_id="crm-tab-profile",
        children=[
            dbc.Card(
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Buying group"),
                                    dcc.Dropdown(
                                        id="crm-profile-buying-group",
                                        placeholder="Select group…",
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Relationship"),
                                    dcc.Dropdown(
                                        id="crm-profile-relationship-status",
                                        options=[
                                            {"label": "Active", "value": "active"},
                                            {
                                                "label": "Prospective",
                                                "value": "prospective",
                                            },
                                            {"label": "Lapsed", "value": "lapsed"},
                                        ],
                                        clearable=False,
                                    ),
                                ],
                                md=2,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Visit target (days)"),
                                    dbc.Input(
                                        id="crm-profile-visit-days",
                                        type="number",
                                        min=1,
                                        placeholder="e.g. 30",
                                    ),
                                ],
                                md=2,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Preferred contact"),
                                    dcc.Dropdown(
                                        id="crm-profile-contact-method",
                                        options=[
                                            {"label": "Phone", "value": "phone"},
                                            {"label": "Email", "value": "email"},
                                            {
                                                "label": "In person",
                                                "value": "in_person",
                                            },
                                        ],
                                        clearable=True,
                                    ),
                                ],
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Save profile",
                                    id="crm-profile-save",
                                    color="primary",
                                    className="mt-4",
                                ),
                                md=3,
                            ),
                        ],
                        className="g-2",
                    )
                ),
                className="shadow-sm mb-3",
            ),
            html.Div(id="crm-profile-feedback", className="small mb-3"),
            html.Div(id="crm-profile-suggestions", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Rep assignment", className="mb-0")),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="crm-assign-rep",
                                            placeholder="Assign rep…",
                                        ),
                                        md=4,
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="crm-assign-role",
                                            options=[
                                                {
                                                    "label": "Primary",
                                                    "value": "primary",
                                                },
                                                {
                                                    "label": "Secondary",
                                                    "value": "secondary",
                                                },
                                                {
                                                    "label": "Support",
                                                    "value": "support",
                                                },
                                            ],
                                            value="primary",
                                            clearable=False,
                                        ),
                                        md=3,
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Assign",
                                            id="crm-assign-submit",
                                            color="secondary",
                                        ),
                                        md=2,
                                    ),
                                ],
                                className="g-2 align-items-center",
                            ),
                            html.Div(id="crm-rep-assignments", className="mt-3"),
                        ]
                    ),
                ],
                className="shadow-sm",
            ),
        ],
    )

    sites_tab = dbc.Tab(
        label="Sites",
        tab_id="crm-tab-sites",
        children=[
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Delivery sites", className="mb-0")),
                    dbc.CardBody(
                        dash_table.DataTable(
                            id="crm-sites-table",
                            columns=[
                                {"name": "Site", "id": "site"},
                                {"name": "State", "id": "state"},
                                {"name": "Suburb", "id": "suburb"},
                                {"name": "Postcode", "id": "postcode"},
                            ],
                            data=[],
                            page_size=8,
                            style_table={"overflowX": "auto"},
                            style_cell={"padding": "0.5rem"},
                            style_header={
                                "backgroundColor": "#f8f9fa",
                                "fontWeight": "bold",
                            },
                        )
                    ),
                ],
                className="shadow-sm mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Add site", className="mb-0")),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-site-name",
                                            placeholder="Site name",
                                        ),
                                        md=3,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-site-state",
                                            placeholder="State",
                                            maxLength=8,
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-site-suburb",
                                            placeholder="Suburb",
                                        ),
                                        md=3,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-site-postcode",
                                            placeholder="Postcode",
                                            maxLength=10,
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Add",
                                            id="crm-add-site-submit",
                                            color="primary",
                                        ),
                                        md=2,
                                    ),
                                ],
                                className="g-2",
                            ),
                            html.Div(
                                id="crm-add-site-feedback", className="small mt-2"
                            ),
                        ]
                    ),
                ],
                className="shadow-sm",
            ),
        ],
    )

    people_tab = dbc.Tab(
        label="People",
        tab_id="crm-tab-people",
        children=[
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H6("Staff at store", className="mb-0"),
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Edit",
                                            id="crm-staff-edit-btn",
                                            size="sm",
                                            color="secondary",
                                            className="me-1",
                                            disabled=True,
                                        ),
                                        dbc.Button(
                                            "Delete",
                                            id="crm-staff-delete-btn",
                                            size="sm",
                                            color="danger",
                                            outline=True,
                                            disabled=True,
                                        ),
                                    ],
                                    className="text-end",
                                ),
                            ],
                            className="align-items-center",
                        )
                    ),
                    dbc.CardBody(
                        dash_table.DataTable(
                            id="crm-staff-table",
                            columns=[
                                {"name": "Name", "id": "name"},
                                {"name": "Role", "id": "role"},
                                {"name": "Phone", "id": "phone"},
                                {"name": "Email", "id": "email"},
                                {"name": "Notes", "id": "notes"},
                                {"name": "Primary", "id": "is_primary"},
                            ],
                            data=[],
                            hidden_columns=["id", "notes_raw"],
                            page_size=8,
                            row_selectable="single",
                            style_table={"overflowX": "auto"},
                            style_cell={"padding": "0.5rem"},
                            style_header={
                                "backgroundColor": "#f8f9fa",
                                "fontWeight": "bold",
                            },
                        )
                    ),
                ],
                className="shadow-sm mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Add staff", className="mb-0")),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-staff-name",
                                            placeholder="Name *",
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-staff-role",
                                            placeholder="Role",
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-staff-phone",
                                            placeholder="Phone",
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-add-staff-email",
                                            placeholder="Email",
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        dbc.Checkbox(
                                            id="crm-add-staff-primary",
                                            label="Primary",
                                            value=False,
                                        ),
                                        md=1,
                                        className="mt-2",
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Add",
                                            id="crm-add-staff-submit",
                                            color="primary",
                                        ),
                                        md=1,
                                        className="mt-1",
                                    ),
                                ],
                                className="g-2 align-items-center",
                            ),
                            dcc.Textarea(
                                id="crm-add-staff-notes",
                                placeholder="Notes about this person…",
                                style={"width": "100%", "minHeight": "60px"},
                                className="mb-2 mt-2",
                            ),
                            html.Div(
                                id="crm-add-staff-feedback", className="small mt-2"
                            ),
                        ]
                    ),
                ],
                className="shadow-sm",
            ),
        ],
    )

    empty_state = html.Div(
        dbc.Alert(
            "Select a customer to open the CRM workspace.",
            color="light",
            className="text-center",
        ),
        id="crm-empty-state",
    )

    workspace = html.Div(
        [
            header,
            dbc.Tabs(
                id="crm-workspace-tabs",
                active_tab="crm-tab-sales",
                children=[sales_tab, timeline_tab, profile_tab, sites_tab, people_tab],
                className="mb-3",
            ),
        ],
        id="crm-workspace",
        style={"display": "none"},
    )

    rep_calendar_nav = dbc.Row(
        [
            dbc.Col(
                dbc.Button("◀", id="crm-rep-cal-prev", size="sm", color="light"),
                width="auto",
            ),
            dbc.Col(
                html.H5(id="crm-rep-cal-title", className="text-center mb-0"),
                className="flex-grow-1",
            ),
            dbc.Col(
                dbc.Button("▶", id="crm-rep-cal-next", size="sm", color="light"),
                width="auto",
            ),
        ],
        className="align-items-center mb-2",
    )

    rep_kpis = dbc.Row(
        [
            dbc.Col(kpi_card("crm-rep-kpi-customers", "Customers", "—"), md=3),
            dbc.Col(kpi_card("crm-rep-kpi-orders", "Orders", "—"), md=3),
            dbc.Col(kpi_card("crm-rep-kpi-revenue", "Revenue (Inc GST)", "—"), md=3),
            dbc.Col(kpi_card("crm-rep-kpi-units", "Units sold", "—"), md=3),
        ],
        className="mb-3",
    )

    rep_workspace = html.Div(
        [
            html.Div(id="crm-rep-header", className="mb-3"),
            rep_kpis,
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H6("Activity calendar", className="mb-0")
                                ),
                                dbc.CardBody(
                                    [
                                        rep_calendar_nav,
                                        html.Div(id="crm-rep-calendar-grid"),
                                        dcc.Store(
                                            id="crm-rep-cal-events-store", data=[]
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-sm mb-3",
                        ),
                        md=7,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H6("Customer portfolio", className="mb-0")
                                ),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id="crm-rep-customers-table",
                                        columns=[
                                            {"name": "Customer", "id": "name"},
                                            {"name": "Code", "id": "code"},
                                            {"name": "Role", "id": "assignment_role"},
                                            {"name": "Orders", "id": "order_count"},
                                            {
                                                "name": "Revenue (Inc)",
                                                "id": "total_inc_gst",
                                            },
                                            {
                                                "name": "Last order",
                                                "id": "last_order_date",
                                            },
                                        ],
                                        data=[],
                                        page_size=10,
                                        style_table={"overflowX": "auto"},
                                        style_cell={"padding": "0.5rem"},
                                        style_header={
                                            "backgroundColor": "#f8f9fa",
                                            "fontWeight": "bold",
                                        },
                                    )
                                ),
                            ],
                            className="shadow-sm mb-3",
                        ),
                        md=5,
                    ),
                ]
            ),
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Sales across portfolio", className="mb-0")),
                    dbc.CardBody(
                        dash_table.DataTable(
                            id="crm-rep-orders-table",
                            columns=[
                                {"name": "Date", "id": "order_date"},
                                {"name": "Ref", "id": "order_ref"},
                                {"name": "Customer", "id": "customer_name"},
                                {"name": "Status", "id": "status"},
                                {"name": "Total (Inc)", "id": "total_inc_gst"},
                            ],
                            data=[],
                            page_size=12,
                            style_table={"overflowX": "auto"},
                            style_cell={"padding": "0.5rem"},
                            style_header={
                                "backgroundColor": "#f8f9fa",
                                "fontWeight": "bold",
                            },
                        )
                    ),
                ],
                className="shadow-sm",
            ),
        ],
        id="crm-rep-workspace",
        style={"display": "none"},
    )

    rep_empty_state = html.Div(
        dbc.Alert(
            "Select a sales rep to view their calendar, customers and portfolio sales.",
            color="light",
            className="text-center",
        ),
        id="crm-rep-empty-state",
    )

    customer_panel = html.Div(
        [
            period_applying_store("crm-customer-applying-preset"),
            customer_filters,
            export_bar,
            empty_state,
            workspace,
        ],
        id="crm-customer-panel",
    )

    rep_panel = html.Div(
        [
            period_applying_store("crm-rep-applying-preset"),
            rep_filters,
            rep_empty_state,
            rep_workspace,
        ],
        id="crm-rep-panel",
    )

    main_tabs = dbc.Tabs(
        id="crm-main-tabs",
        active_tab="crm-main-customer",
        children=[
            dbc.Tab(
                label="Customer", tab_id="crm-main-customer", children=[customer_panel]
            ),
            dbc.Tab(label="Sales Rep", tab_id="crm-main-rep", children=[rep_panel]),
        ],
        className="vnd-sub-tabs mb-3",
    )

    return html.Div(
        [
            html.Link(rel="stylesheet", href="/assets/crm_calendar.css"),
            dcc.Store(id="crm-refresh-store", data=0),
            dcc.Store(id="crm-reps-store", data=[]),
            dcc.Store(id="crm-buying-groups-store", data=[]),
            dcc.Store(id="crm-context-rep-id", data=None),
            dcc.Store(id="crm-note-edit-id", data=None),
            dcc.Store(id="crm-staff-edit-id", data=None),
            dcc.Store(id="crm-calendar-month", data=_DEFAULT_END[:7]),
            dcc.Store(id="crm-rep-calendar-month", data=_DEFAULT_END[:7]),
            dcc.Download(id="crm-export-download"),
            main_tabs,
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="crm-note-modal-title")),
                    dbc.ModalBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="crm-note-edit-type",
                                            options=ACTIVITY_TYPES,
                                            clearable=False,
                                        ),
                                        md=4,
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="crm-note-edit-category",
                                            options=NOTE_CATEGORIES,
                                            clearable=False,
                                        ),
                                        md=4,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="crm-note-edit-datetime",
                                            type="datetime-local",
                                        ),
                                        md=4,
                                    ),
                                ],
                                className="g-2 mb-2",
                            ),
                            dcc.Textarea(
                                id="crm-note-edit-body",
                                style={"width": "100%", "minHeight": "100px"},
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="crm-note-modal-cancel",
                                color="secondary",
                                outline=True,
                            ),
                            dbc.Button(
                                "Save",
                                id="crm-note-modal-save",
                                color="primary",
                            ),
                        ]
                    ),
                ],
                id="crm-note-edit-modal",
                is_open=False,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Edit staff")),
                    dbc.ModalBody(
                        [
                            dbc.Input(
                                id="crm-staff-edit-name",
                                placeholder="Name *",
                                className="mb-2",
                            ),
                            dbc.Input(
                                id="crm-staff-edit-role",
                                placeholder="Role",
                                className="mb-2",
                            ),
                            dbc.Input(
                                id="crm-staff-edit-phone",
                                placeholder="Phone",
                                className="mb-2",
                            ),
                            dbc.Input(
                                id="crm-staff-edit-email",
                                placeholder="Email",
                                className="mb-2",
                            ),
                            dbc.Checkbox(
                                id="crm-staff-edit-primary",
                                label="Primary contact",
                                value=False,
                                className="mb-2",
                            ),
                            dbc.Label("Notes", className="small"),
                            dcc.Textarea(
                                id="crm-staff-edit-notes",
                                style={"width": "100%", "minHeight": "80px"},
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="crm-staff-modal-cancel",
                                color="secondary",
                                outline=True,
                            ),
                            dbc.Button(
                                "Save",
                                id="crm-staff-modal-save",
                                color="primary",
                            ),
                        ]
                    ),
                ],
                id="crm-staff-edit-modal",
                is_open=False,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="crm-cal-day-modal-title")),
                    dbc.ModalBody(id="crm-cal-day-modal-body"),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="crm-cal-day-modal-close",
                            color="secondary",
                        )
                    ),
                ],
                id="crm-cal-day-modal",
                is_open=False,
                size="lg",
            ),
        ],
        className="sales-crm-tab",
    )

"""Nova University training hub page."""

import dash_bootstrap_components as dbc
from dash import dcc, html

API_BASE = "http://127.0.0.1:8000/api/v1"


def _dictate_button(
    target_id: str, extra_class: str = "", status_id: str = "nu-editor-dictate-status"
) -> html.Button:
    """Plain HTML button — dbc.Button does not accept data-target."""
    return html.Button(
        "🎤 Dictate",
        id={"type": "nu-dictate-btn", "index": target_id},
        className=f"btn btn-link btn-sm nu-dictate-btn py-0 {extra_class}".strip(),
        type="button",
        **{"data-target": target_id, "data-status": status_id},
    )


def _dictate_field(
    field_id: str,
    label: str,
    component,
    rows_hint: str = "",
    status_id: str = "nu-editor-dictate-status",
):
    """Label row with dictate button above a textarea/input."""
    return html.Div(
        [
            html.Div(
                [
                    html.Label(label, className="mb-0"),
                    _dictate_button(field_id, status_id=status_id),
                ],
                className="nu-field-label-row",
            ),
            component,
        ],
        className="mb-2",
    )


def _rich_editor_block():
    toolbar = html.Div(
        [
            html.Button(
                "B", className="nu-rich-cmd", **{"data-cmd": "bold"}, type="button"
            ),
            html.Button(
                "I", className="nu-rich-cmd", **{"data-cmd": "italic"}, type="button"
            ),
            html.Button(
                "U", className="nu-rich-cmd", **{"data-cmd": "underline"}, type="button"
            ),
            html.Button(
                "• List",
                className="nu-rich-cmd",
                **{"data-cmd": "insertUnorderedList"},
                type="button",
            ),
            html.Button(
                "H2",
                className="nu-rich-cmd",
                **{"data-cmd": "formatBlock", "data-value": "h2"},
                type="button",
            ),
            html.Button(
                "Link",
                className="nu-rich-cmd",
                **{"data-cmd": "createLink"},
                type="button",
            ),
            html.Button(
                "Video",
                className="nu-rich-cmd",
                **{"data-cmd": "embedVideo"},
                type="button",
            ),
            _dictate_button("nu-rich-editor-surface", "ms-auto"),
        ],
        className="nu-rich-toolbar",
    )
    return html.Div(
        [
            html.Label("Rich training content", className="fw-semibold mb-1"),
            html.P(
                "Type, paste, dictate, or drag-and-drop images and videos. "
                "Paste a Loom/YouTube link to embed inline.",
                className="text-muted small",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="nu-editor-video-embed",
                            placeholder="Featured video URL (Loom, YouTube, Vimeo)",
                        ),
                        md=9,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Insert video in content",
                            id="nu-editor-embed-video-btn",
                            color="secondary",
                            outline=True,
                            size="sm",
                            className="w-100",
                        ),
                        md=3,
                    ),
                ],
                className="g-2 mb-2",
            ),
            html.Div(
                [
                    toolbar,
                    html.Div(
                        id="nu-rich-editor-surface",
                        className="nu-rich-editor-surface",
                        **{
                            "contentEditable": "true",
                            "data-placeholder": (
                                "Write your training content here… "
                                "Drop images/videos or paste text and links."
                            ),
                        },
                    ),
                    html.Div(
                        "Drag and drop images or videos anywhere in the editor.",
                        className="nu-rich-drop-hint",
                    ),
                ],
                id="nu-rich-editor-wrap",
                className="nu-rich-editor-wrap mb-1",
                **{"data-api-base": API_BASE},
            ),
            dcc.Textarea(id="nu-editor-rich-content", style={"display": "none"}),
            html.Div(id="nu-editor-dictate-status", className="nu-dictate-status"),
            html.Div(id="nu-editor-sync-dummy", style={"display": "none"}),
        ],
        className="mb-3",
    )


def _nu_header():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.Span("ν", className="nu-mark"), width="auto"),
                    dbc.Col(
                        [
                            html.Div("Nova University", className="nu-wordmark"),
                            html.Div("Learn the New Way.", className="nu-tagline"),
                        ],
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.A(
                                    "LLM Corpus (JSON)",
                                    href=f"{API_BASE}/training/corpus",
                                    target="_blank",
                                    className="text-white small me-2",
                                ),
                                html.A(
                                    "LLM Corpus (MD)",
                                    href=f"{API_BASE}/training/corpus?format=markdown",
                                    target="_blank",
                                    className="text-white small me-2",
                                ),
                                dbc.Button(
                                    "AI Settings",
                                    id="nu-llm-settings-btn",
                                    color="light",
                                    size="sm",
                                    outline=True,
                                ),
                            ],
                            className="text-end",
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                ],
                className="align-items-center g-2",
            ),
        ],
        className="nu-header",
    )


class TrainingPage:
    """Nova University — searchable rich training articles."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                _nu_header(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("⌕"),
                                        dbc.Input(
                                            id="nu-search-input",
                                            placeholder="Search training articles…",
                                            type="search",
                                            debounce=True,
                                        ),
                                        dbc.Button(
                                            "Search",
                                            id="nu-search-btn",
                                            color="primary",
                                        ),
                                        dbc.Button(
                                            "Clear",
                                            id="nu-clear-btn",
                                            color="secondary",
                                            outline=True,
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.Span(
                                                    "✦ ", className="nu-ask-mark"
                                                ),
                                                "Ask Nova University",
                                                dbc.Badge(
                                                    id="nu-llm-status-badge",
                                                    children="Checking…",
                                                    color="secondary",
                                                    className="ms-2",
                                                ),
                                            ],
                                            className="py-2",
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    "Ask in plain English — answers are grounded in "
                                                    "your published training articles. "
                                                    "Use 🎤 Dictate to speak your question (Chrome/Edge).",
                                                    className="text-muted small mb-2",
                                                ),
                                                _dictate_field(
                                                    "nu-ask-input",
                                                    "Your question",
                                                    dbc.Textarea(
                                                        id="nu-ask-input",
                                                        placeholder=(
                                                            "e.g. How do I acknowledge a DAQ trip and "
                                                            "what safety checks come first?"
                                                        ),
                                                        style={"height": "72px"},
                                                    ),
                                                    status_id="nu-ask-dictate-status",
                                                ),
                                                html.Div(
                                                    id="nu-ask-dictate-status",
                                                    className="nu-dictate-status mb-2",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            dbc.Button(
                                                                "Ask",
                                                                id="nu-ask-btn",
                                                                color="primary",
                                                            ),
                                                            width="auto",
                                                        ),
                                                        dbc.Col(
                                                            dbc.Button(
                                                                "Clear answer",
                                                                id="nu-ask-clear-btn",
                                                                color="secondary",
                                                                outline=True,
                                                            ),
                                                            width="auto",
                                                        ),
                                                    ],
                                                    className="g-2 mb-2",
                                                ),
                                                dcc.Loading(
                                                    html.Div(id="nu-llm-response"),
                                                    type="circle",
                                                    color="#3d5a73",
                                                ),
                                            ],
                                            className="py-2",
                                        ),
                                    ],
                                    className="mb-3 nu-ask-card",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="nu-system-filter",
                                                placeholder="Filter by system",
                                                options=[
                                                    {
                                                        "label": "VNDManuf",
                                                        "value": "vndmanuf",
                                                    },
                                                    {
                                                        "label": "VND-DAQ",
                                                        "value": "vndaq",
                                                    },
                                                    {
                                                        "label": "Shopify",
                                                        "value": "shopify",
                                                    },
                                                    {"label": "Xero", "value": "xero"},
                                                ],
                                                clearable=True,
                                            ),
                                            md=4,
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="nu-type-filter",
                                                placeholder="Content type",
                                                options=[
                                                    {"label": "SOP", "value": "sop"},
                                                    {
                                                        "label": "Guide",
                                                        "value": "guide",
                                                    },
                                                    {
                                                        "label": "Checklist",
                                                        "value": "checklist",
                                                    },
                                                    {
                                                        "label": "Reference",
                                                        "value": "reference",
                                                    },
                                                ],
                                                clearable=True,
                                            ),
                                            md=3,
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="nu-status-filter",
                                                value="all",
                                                options=[
                                                    {
                                                        "label": "Published",
                                                        "value": "published",
                                                    },
                                                    {
                                                        "label": "Draft",
                                                        "value": "draft",
                                                    },
                                                    {
                                                        "label": "All active",
                                                        "value": "all",
                                                    },
                                                ],
                                                clearable=False,
                                            ),
                                            md=3,
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "New Article",
                                                id="nu-new-article-btn",
                                                color="success",
                                                className="w-100",
                                            ),
                                            md=2,
                                        ),
                                    ],
                                    className="g-2 mb-3",
                                ),
                            ],
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H6("Manual sections", className="text-muted mb-2"),
                                html.Div(id="nu-category-tree"),
                            ],
                            md=2,
                            className="nu-sidebar nu-sidebar-categories",
                        ),
                        dbc.Col(
                            [
                                html.H6(
                                    id="nu-article-list-title",
                                    children="Articles",
                                    className="text-muted mb-2",
                                ),
                                html.Div(
                                    id="nu-article-list",
                                    style={"maxHeight": "55vh", "overflowY": "auto"},
                                ),
                            ],
                            md=2,
                            id="nu-article-list-panel",
                            className="nu-sidebar nu-sidebar-articles",
                            style={"display": "none"},
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Button(
                                            "← Back to list",
                                            id="nu-back-btn",
                                            color="link",
                                            className="px-0",
                                            style={"visibility": "hidden"},
                                        ),
                                        dbc.Button(
                                            "Edit selected",
                                            id="nu-edit-article-btn",
                                            color="primary",
                                            size="sm",
                                            className="float-end",
                                        ),
                                    ],
                                    id="nu-detail-actions",
                                    className="mb-2",
                                ),
                                html.Div(id="nu-article-detail"),
                                html.Div(
                                    id="nu-empty-state",
                                    children=dbc.Alert(
                                        [
                                            html.H5(
                                                "Welcome to Nova University",
                                                className="alert-heading",
                                            ),
                                            html.P(
                                                "Select a manual section to browse articles, "
                                                "or search for SOPs, guides, "
                                                "and rich training with embedded videos and media."
                                            ),
                                        ],
                                        color="light",
                                    ),
                                ),
                            ],
                            md=8,
                        ),
                    ],
                    className="g-3",
                ),
                dcc.Store(id="nu-selected-category-id"),
                dcc.Store(id="nu-selected-article-id"),
                dcc.Store(id="nu-editing-article-id"),
                dcc.Store(id="nu-editor-request"),
                dcc.Store(id="nu-view-article-request"),
                # Placeholders keep pattern-matching callbacks valid before articles load
                html.Div(
                    id={"type": "nu-article-card", "index": "__nu_placeholder__"},
                    n_clicks=0,
                    style={"display": "none"},
                ),
                dbc.Button(
                    "Edit",
                    id={"type": "nu-card-edit-btn", "index": "__nu_placeholder__"},
                    style={"display": "none"},
                    n_clicks=0,
                ),
                dbc.Button(
                    "All",
                    id={"type": "nu-cat-btn", "index": "__nu_placeholder__"},
                    style={"display": "none"},
                    n_clicks=0,
                ),
                dbc.Button(
                    "Source",
                    id={"type": "nu-ask-source-btn", "index": "__nu_placeholder__"},
                    style={"display": "none"},
                    n_clicks=0,
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="nu-editor-modal-title")),
                        dbc.ModalBody(
                            [
                                html.P(
                                    "Click 🎤 Dictate beside any field to use speech-to-text "
                                    "(Chrome or Edge recommended).",
                                    className="text-muted small mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            _dictate_field(
                                                "nu-editor-title",
                                                "Article title",
                                                dbc.Input(
                                                    id="nu-editor-title",
                                                    placeholder="Article title",
                                                ),
                                            ),
                                            md=8,
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="nu-editor-content-type",
                                                options=[
                                                    {"label": "SOP", "value": "sop"},
                                                    {
                                                        "label": "Guide",
                                                        "value": "guide",
                                                    },
                                                    {
                                                        "label": "Checklist",
                                                        "value": "checklist",
                                                    },
                                                    {
                                                        "label": "Reference",
                                                        "value": "reference",
                                                    },
                                                ],
                                                value="sop",
                                                clearable=False,
                                            ),
                                            md=4,
                                        ),
                                    ],
                                    className="g-2 mb-2",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="nu-editor-category",
                                                placeholder="Category",
                                            ),
                                            md=6,
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="nu-editor-status",
                                                options=[
                                                    {
                                                        "label": "Draft",
                                                        "value": "draft",
                                                    },
                                                    {
                                                        "label": "Published",
                                                        "value": "published",
                                                    },
                                                ],
                                                value="draft",
                                                clearable=False,
                                            ),
                                            md=3,
                                        ),
                                        dbc.Col(
                                            _dictate_field(
                                                "nu-editor-systems",
                                                "Systems",
                                                dbc.Input(
                                                    id="nu-editor-systems",
                                                    placeholder="Systems (comma-separated)",
                                                ),
                                            ),
                                            md=3,
                                        ),
                                    ],
                                    className="g-2 mb-2",
                                ),
                                _dictate_field(
                                    "nu-editor-summary",
                                    "Summary",
                                    dbc.Textarea(
                                        id="nu-editor-summary",
                                        style={"height": "60px"},
                                    ),
                                ),
                                dbc.Tabs(
                                    [
                                        dbc.Tab(
                                            label="Rich Content",
                                            tab_id="nu-tab-rich",
                                            children=[_rich_editor_block()],
                                        ),
                                        dbc.Tab(
                                            label="SOP Structure",
                                            tab_id="nu-tab-sop",
                                            children=[
                                                _dictate_field(
                                                    "nu-editor-purpose",
                                                    "Purpose",
                                                    dbc.Textarea(
                                                        id="nu-editor-purpose",
                                                        style={"height": "70px"},
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-prerequisites",
                                                    "Prerequisites",
                                                    dbc.Textarea(
                                                        id="nu-editor-prerequisites",
                                                        style={"height": "70px"},
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-safety",
                                                    "Safety notes",
                                                    dbc.Textarea(
                                                        id="nu-editor-safety",
                                                        style={"height": "60px"},
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-steps",
                                                    "Steps (Title | Body per line)",
                                                    dbc.Textarea(
                                                        id="nu-editor-steps",
                                                        style={"height": "120px"},
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-risks",
                                                    "Risks (Issue | Prevention per line)",
                                                    dbc.Textarea(
                                                        id="nu-editor-risks",
                                                        style={"height": "80px"},
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-troubleshooting",
                                                    "Troubleshooting",
                                                    dbc.Textarea(
                                                        id="nu-editor-troubleshooting",
                                                        style={"height": "70px"},
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-body",
                                                    "Additional notes (Markdown)",
                                                    dbc.Textarea(
                                                        id="nu-editor-body",
                                                        style={"height": "100px"},
                                                    ),
                                                ),
                                            ],
                                        ),
                                        dbc.Tab(
                                            label="Links",
                                            tab_id="nu-tab-links",
                                            children=[
                                                _dictate_field(
                                                    "nu-editor-tags",
                                                    "Tags",
                                                    dbc.Input(
                                                        id="nu-editor-tags",
                                                        placeholder="Tags (comma-separated)",
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-loom",
                                                    "Loom URL",
                                                    dbc.Input(
                                                        id="nu-editor-loom",
                                                        placeholder="Loom URL",
                                                    ),
                                                ),
                                                _dictate_field(
                                                    "nu-editor-sharepoint",
                                                    "SharePoint URL",
                                                    dbc.Input(
                                                        id="nu-editor-sharepoint",
                                                        placeholder="SharePoint URL",
                                                    ),
                                                ),
                                            ],
                                        ),
                                    ],
                                    id="nu-editor-tabs",
                                    active_tab="nu-tab-rich",
                                    className="mb-2",
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Cancel",
                                    id="nu-editor-cancel-btn",
                                    color="secondary",
                                    outline=True,
                                ),
                                dbc.Button(
                                    "Save", id="nu-editor-save-btn", color="primary"
                                ),
                            ]
                        ),
                    ],
                    id="nu-editor-modal",
                    size="xl",
                    is_open=False,
                    scrollable=True,
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Nova University AI Settings")),
                        dbc.ModalBody(
                            [
                                html.P(
                                    [
                                        "Settings are saved to ",
                                        html.Code("config/openai.json"),
                                        " (same pattern as VND-DAQ). Leave API key blank to keep the current key.",
                                    ],
                                    className="text-muted small",
                                ),
                                dbc.Input(
                                    id="nu-llm-api-key",
                                    type="password",
                                    placeholder="OpenAI API key (sk-…)",
                                    className="mb-2",
                                ),
                                html.Div(
                                    id="nu-llm-api-key-hint",
                                    className="text-muted small mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Input(
                                                id="nu-llm-model",
                                                placeholder="Model",
                                            ),
                                            md=6,
                                        ),
                                        dbc.Col(
                                            dbc.Input(
                                                id="nu-llm-max-articles",
                                                type="number",
                                                min=1,
                                                max=20,
                                                placeholder="Context articles",
                                            ),
                                            md=6,
                                        ),
                                    ],
                                    className="g-2 mb-2",
                                ),
                                dbc.Checklist(
                                    options=[
                                        {
                                            "label": "Enable AI answers",
                                            "value": "enabled",
                                        }
                                    ],
                                    value=["enabled"],
                                    id="nu-llm-enabled",
                                    switch=True,
                                    className="mb-2",
                                ),
                                html.Div(
                                    id="nu-llm-settings-status", className="small"
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Cancel",
                                    id="nu-llm-settings-cancel",
                                    color="secondary",
                                    outline=True,
                                ),
                                dbc.Button(
                                    "Save",
                                    id="nu-llm-settings-save",
                                    color="primary",
                                ),
                            ]
                        ),
                    ],
                    id="nu-llm-settings-modal",
                    is_open=False,
                ),
            ],
            fluid=True,
            className="nu-training-page",
        )

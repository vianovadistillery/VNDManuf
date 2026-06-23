"""Callbacks for NU training hub."""

from __future__ import annotations

import json

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
from dash.exceptions import PreventUpdate

from app.training.service import video_embed_url as resolve_video_embed


def _parse_steps_text(raw: str | None) -> list[dict]:
    if not raw:
        return []
    steps = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            title, body = line.split("|", 1)
            steps.append({"title": title.strip(), "body": body.strip()})
        else:
            steps.append({"title": line, "body": ""})
    return steps


def _format_steps_text(steps: list) -> str:
    lines = []
    for step in steps or []:
        if not isinstance(step, dict):
            continue
        title = step.get("title") or ""
        body = step.get("body") or ""
        if body:
            lines.append(f"{title} | {body}")
        else:
            lines.append(title)
    return "\n".join(lines)


def _parse_risks_text(raw: str | None) -> list[dict]:
    if not raw:
        return []
    risks = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            issue, prevention = line.split("|", 1)
            risks.append({"issue": issue.strip(), "prevention": prevention.strip()})
        else:
            risks.append({"issue": line, "prevention": ""})
    return risks


def _format_risks_text(risks: list) -> str:
    lines = []
    for risk in risks or []:
        if not isinstance(risk, dict):
            continue
        issue = risk.get("issue") or ""
        prevention = risk.get("prevention") or ""
        if prevention:
            lines.append(f"{issue} | {prevention}")
        else:
            lines.append(issue)
    return "\n".join(lines)


def _badge(text: str, color: str = "secondary") -> dbc.Badge:
    return dbc.Badge(text, color=color, className="nu-badge me-1")


def _video_player(url: str | None) -> html.Div | None:
    embed = resolve_video_embed(url)
    if not embed:
        return None
    return html.Div(
        html.Iframe(
            src=embed,
            allow="autoplay; fullscreen; picture-in-picture",
        ),
        className="nu-video-embed mb-3",
    )


def _article_card(article: dict, selected_id: str | None) -> html.Div:
    aid = article.get("id")
    is_selected = aid == selected_id
    systems = article.get("systems") or []
    tags = (article.get("tags") or [])[:3]
    return html.Div(
        [
            html.Div(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    _badge(
                                        article.get("content_type", "sop"), "primary"
                                    ),
                                    _badge(article.get("status", "draft"), "warning")
                                    if article.get("status") == "draft"
                                    else None,
                                ]
                            ),
                            html.H6(
                                article.get("title", "Untitled"), className="mt-2 mb-1"
                            ),
                            html.P(
                                article.get("summary") or "No summary yet.",
                                className="text-muted small mb-2",
                                style={
                                    "display": "-webkit-box",
                                    "-webkit-line-clamp": "2",
                                    "-webkit-box-orient": "vertical",
                                    "overflow": "hidden",
                                },
                            ),
                            html.Div(
                                [_badge(s, "info") for s in systems]
                                + [_badge(t, "light") for t in tags]
                            ),
                        ]
                    ),
                    className=f"nu-article-card {'selected' if is_selected else ''}",
                ),
                id={"type": "nu-article-card", "index": aid},
                n_clicks=0,
                style={"cursor": "pointer"},
            ),
            dbc.Button(
                "Edit",
                id={"type": "nu-card-edit-btn", "index": aid},
                color="outline-primary",
                size="sm",
                className="nu-card-edit-btn mt-1",
                n_clicks=0,
            ),
        ],
        className="mb-2",
    )


def _new_editor_values() -> tuple:
    """Empty editor field values for a new article."""
    return (
        True,
        "New Article",
        None,
        "",
        "sop",
        None,
        "draft",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    )


def _editor_open_values(article: dict, article_id: str) -> tuple:
    """Field values tuple for opening the editor on an existing article."""
    return (
        True,
        "Edit Article",
        article_id,
        article.get("title"),
        article.get("content_type"),
        article.get("category_id"),
        article.get("status"),
        ", ".join(article.get("systems") or []),
        article.get("summary"),
        article.get("purpose"),
        article.get("prerequisites"),
        article.get("safety_notes"),
        _format_steps_text(article.get("steps")),
        _format_risks_text(article.get("risks")),
        article.get("troubleshooting"),
        article.get("body_markdown"),
        ", ".join(article.get("tags") or []),
        article.get("loom_url"),
        article.get("sharepoint_url"),
        article.get("rich_content_html") or "",
        article.get("video_embed_url") or "",
    )


def _render_detail(article: dict) -> list:
    if not article:
        return []
    children = [
        html.H4(article.get("title", "")),
        html.Div(
            [
                _badge(article.get("content_type", "sop"), "primary"),
                _badge(article.get("status", ""), "secondary"),
                html.Span(
                    article.get("category_path") or "",
                    className="text-muted small ms-2",
                ),
            ],
            className="mb-3",
        ),
        html.Div(
            f"LLM slug: {article.get('slug')} — indexed via /api/v1/training/corpus",
            className="nu-llm-hint mb-3",
        ),
    ]
    featured = _video_player(article.get("video_embed_url") or article.get("loom_url"))
    if featured:
        children.append(featured)
    rich_html = article.get("rich_content_html")
    if rich_html:
        # Rewrite relative media URLs for browser on Dash port
        rich_html = rich_html.replace(
            'src="/api/v1/training/media/',
            'src="http://127.0.0.1:8000/api/v1/training/media/',
        )
        children.extend(
            [
                html.H5("Training Content", className="nu-section-title"),
                html.Div(
                    dangerously_allow_html={"__html__": rich_html},
                    className="nu-rich-content-view",
                ),
            ]
        )
    if article.get("loom_url") and not article.get("video_embed_url"):
        children.append(
            html.P(
                [
                    "Loom: ",
                    html.A("Watch video", href=article["loom_url"], target="_blank"),
                ]
            )
        )
    if article.get("sharepoint_url"):
        children.append(
            html.P(
                [
                    "SharePoint: ",
                    html.A(
                        "Open folder", href=article["sharepoint_url"], target="_blank"
                    ),
                ]
            )
        )

    sections = [
        ("Summary", article.get("summary")),
        ("Purpose", article.get("purpose")),
        ("Prerequisites", article.get("prerequisites")),
        ("Safety Notes", article.get("safety_notes")),
    ]
    for title, content in sections:
        if content:
            children.extend(
                [
                    html.H5(title, className="nu-section-title"),
                    dcc.Markdown(content),
                ]
            )

    steps = article.get("steps") or []
    if steps:
        children.append(html.H5("Steps", className="nu-section-title"))
        step_items = []
        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            title = step.get("title") or f"Step {idx}"
            body = step.get("body") or ""
            step_items.append(
                html.Li(
                    [
                        html.Strong(f"{idx}. {title}"),
                        html.Br() if body else None,
                        html.Span(body) if body else None,
                    ]
                )
            )
        children.append(html.Ol(step_items, className="mb-3"))

    risks = article.get("risks") or []
    if risks:
        children.append(html.H5("Risks & Common Errors", className="nu-section-title"))
        for risk in risks:
            if not isinstance(risk, dict):
                continue
            children.append(
                html.Div(
                    [
                        html.Strong(risk.get("issue") or ""),
                        html.P(
                            risk.get("prevention") or "", className="text-muted small"
                        ),
                    ],
                    className="mb-2",
                )
            )

    if article.get("troubleshooting"):
        children.extend(
            [
                html.H5("Troubleshooting", className="nu-section-title"),
                dcc.Markdown(article["troubleshooting"]),
            ]
        )
    if article.get("body_markdown"):
        children.extend(
            [
                html.H5("Additional Notes", className="nu-section-title"),
                dcc.Markdown(article["body_markdown"]),
            ]
        )

    related = article.get("related_links") or []
    if related:
        children.append(html.H5("Related Content", className="nu-section-title"))
        for link in related:
            if not isinstance(link, dict):
                continue
            title = link.get("title") or link.get("url") or "Link"
            url = link.get("url")
            children.append(
                html.Li(html.A(title, href=url, target="_blank") if url else title)
            )

    return [html.Div(children, className="nu-detail-panel")]


def _render_llm_response(result: dict) -> list:
    """Render OpenAI answer with cited source articles."""
    if not result:
        return []
    if isinstance(result, dict) and result.get("error"):
        return [dbc.Alert(str(result.get("error")), color="warning", className="small")]

    answer = result.get("answer") or ""
    sources = result.get("sources") or []
    model = result.get("model") or ""
    articles_used = result.get("articles_used", len(sources))

    children: list = [
        html.Div(
            [
                html.H6("Answer", className="nu-llm-answer-title"),
                dcc.Markdown(answer, className="nu-llm-answer-body mb-2"),
                html.Div(
                    f"Based on {articles_used} article(s)"
                    + (f" · {model}" if model else ""),
                    className="text-muted small mb-2",
                ),
            ],
            className="nu-llm-answer-block",
        )
    ]

    if sources:
        source_items = []
        for src in sources:
            if not isinstance(src, dict):
                continue
            aid = src.get("id")
            title = src.get("title") or "Article"
            path = src.get("category_path") or ""
            summary = src.get("summary") or ""
            source_items.append(
                html.Div(
                    [
                        dbc.Button(
                            title,
                            id={"type": "nu-ask-source-btn", "index": aid},
                            color="link",
                            className="nu-ask-source-btn p-0 text-start",
                            n_clicks=0,
                        ),
                        html.Div(path, className="text-muted small") if path else None,
                        html.P(
                            summary,
                            className="text-muted small mb-0",
                            style={
                                "display": "-webkit-box",
                                "-webkit-line-clamp": "2",
                                "-webkit-box-orient": "vertical",
                                "overflow": "hidden",
                            },
                        )
                        if summary
                        else None,
                    ],
                    className="nu-ask-source-item mb-2",
                )
            )
        children.append(
            html.Div(
                [
                    html.H6("Sources", className="nu-llm-sources-title"),
                    html.Div(source_items),
                ],
                className="nu-llm-sources",
            )
        )

    return children


def _render_category_tree(categories: list, selected_id: str | None = None) -> list:
    """Build hierarchical category filter buttons for the sidebar."""
    if not categories:
        return [
            html.P(
                "No categories yet. Run: python scripts/seed_nu_training.py",
                className="text-muted small",
            )
        ]

    by_parent: dict[str | None, list] = {}
    for cat in categories:
        pid = cat.get("parent_id")
        by_parent.setdefault(pid, []).append(cat)

    def render_level(parent_id, depth=0):
        items = []
        for cat in sorted(
            by_parent.get(parent_id, []), key=lambda c: c.get("sort_order", 0)
        ):
            code = cat.get("code") or ""
            label = cat.get("name", "")
            btn = dbc.Button(
                [
                    html.Span(code, className="nu-cat-code") if code else None,
                    html.Span(label, className="nu-cat-label"),
                ],
                id={"type": "nu-cat-btn", "index": cat.get("id")},
                color="link",
                className=(
                    f"nu-category-btn {'nu-category-parent' if depth == 0 else 'nu-category-child'}"
                    + (
                        " nu-category-btn-active"
                        if cat.get("id") == selected_id
                        else ""
                    )
                ),
                size="sm",
            )
            items.append(btn)
            items.extend(render_level(cat.get("id"), depth + 1))
        return items

    all_btn = dbc.Button(
        "All sections",
        id={"type": "nu-cat-btn", "index": "all"},
        color="secondary",
        outline=True,
        className=(
            "nu-category-btn nu-category-all mb-2"
            + (" nu-category-btn-active" if selected_id == "all" else "")
        ),
        size="sm",
    )
    return [all_btn] + render_level(None)


def register_training_callbacks(app, make_api_request):
    """Register NU training hub callbacks."""

    @app.callback(
        Output("nu-selected-category-id", "data"),
        Input({"type": "nu-cat-btn", "index": dash.ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_category(_n_clicks):
        triggered = dash.ctx.triggered
        if not triggered or not triggered[0].get("value"):
            raise PreventUpdate
        triggered_id = dash.ctx.triggered_id
        if (
            not isinstance(triggered_id, dict)
            or triggered_id.get("type") != "nu-cat-btn"
        ):
            raise PreventUpdate
        cat_id = triggered_id.get("index")
        if cat_id in ("__nu_placeholder__", None):
            raise PreventUpdate
        return cat_id

    def _articles_panel_style(
        category_id, search_text, system, content_type, triggered_prop
    ):
        if triggered_prop.startswith("nu-clear-btn"):
            if category_id:
                return {"display": "block"}
            return {"display": "none"}
        if category_id:
            return {"display": "block"}
        if search_text and str(search_text).strip():
            return {"display": "block"}
        if system or content_type:
            return {"display": "block"}
        if triggered_prop in (
            "nu-search-btn.n_clicks",
            "nu-search-input.n_submit",
        ):
            return {"display": "block"}
        return {"display": "none"}

    def _article_list_title(category_id, categories, search_text):
        if search_text and str(search_text).strip():
            return "Search results"
        if category_id and category_id != "all":
            for cat in categories:
                if cat.get("id") == category_id:
                    return cat.get("name") or "Articles"
        if category_id == "all":
            return "All articles"
        return "Articles"

    @app.callback(
        [
            Output("nu-article-list", "children"),
            Output("nu-editor-category", "options"),
            Output("nu-category-tree", "children"),
            Output("nu-article-list-panel", "style"),
            Output("nu-article-list-title", "children"),
        ],
        [
            Input("main-tabs", "active_tab"),
            Input("nu-search-btn", "n_clicks"),
            Input("nu-clear-btn", "n_clicks"),
            Input("nu-selected-category-id", "data"),
            Input("nu-system-filter", "value"),
            Input("nu-type-filter", "value"),
            Input("nu-status-filter", "value"),
            Input("nu-search-input", "n_submit"),
            Input("nu-editor-save-btn", "n_clicks"),
        ],
        [State("nu-search-input", "value"), State("nu-selected-article-id", "data")],
    )
    def load_articles(
        active_tab,
        _search_click,
        clear_click,
        category_id,
        system,
        content_type,
        status_filter,
        _search_submit,
        _save_click,
        search_text,
        selected_id,
    ):
        if active_tab != "training":
            raise PreventUpdate

        ctx = dash.callback_context
        triggered_prop = ctx.triggered[0]["prop_id"] if ctx.triggered else ""
        if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("nu-clear-btn"):
            search_text = None

        params: dict = {"limit": 200}
        if search_text:
            params["q"] = search_text
        if category_id and category_id != "all":
            params["category_id"] = category_id
        if system:
            params["system"] = system
        if content_type:
            params["content_type"] = content_type
        if status_filter:
            params["status"] = status_filter

        resp = make_api_request("GET", "/training/articles", params)
        cat_resp = make_api_request("GET", "/training/categories")

        if isinstance(cat_resp, dict) and cat_resp.get("error"):
            category_tree = dbc.Alert(
                "Could not load categories. Is the API running on port 8000?",
                color="warning",
                className="small",
            )
            categories = []
        else:
            categories = cat_resp if isinstance(cat_resp, list) else []
            category_tree = _render_category_tree(categories, category_id)

        panel_style = _articles_panel_style(
            category_id, search_text, system, content_type, triggered_prop
        )
        list_title = _article_list_title(category_id, categories, search_text)

        if isinstance(resp, dict) and resp.get("error"):
            return (
                dbc.Alert("Could not load articles.", color="warning"),
                [],
                category_tree,
                panel_style,
                list_title,
            )

        articles = resp if isinstance(resp, list) else []
        cards = [_article_card(a, selected_id) for a in articles]
        if not cards:
            cards = [html.P("No articles found.", className="text-muted small")]

        cat_options = []
        if categories:
            cat_options = [
                {"label": c.get("name", ""), "value": c.get("id")} for c in categories
            ]
        return cards, cat_options, category_tree, panel_style, list_title

    @app.callback(
        Output("nu-view-article-request", "data"),
        Input({"type": "nu-article-card", "index": dash.ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def queue_article_view(_card_clicks):
        triggered = dash.ctx.triggered
        if not triggered or not triggered[0].get("value"):
            raise PreventUpdate
        triggered_id = dash.ctx.triggered_id
        if (
            not isinstance(triggered_id, dict)
            or triggered_id.get("type") != "nu-article-card"
        ):
            raise PreventUpdate
        if triggered_id.get("index") == "__nu_placeholder__":
            raise PreventUpdate
        return {
            "article_id": triggered_id["index"],
            "seq": triggered[0]["value"],
        }

    @app.callback(
        [
            Output("nu-article-detail", "children"),
            Output("nu-empty-state", "style"),
            Output("nu-back-btn", "style"),
            Output("nu-selected-article-id", "data"),
        ],
        [
            Input("nu-view-article-request", "data"),
            Input("nu-back-btn", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def show_article_detail(view_request, back_click):
        triggered = dash.ctx.triggered
        if not triggered:
            raise PreventUpdate
        trigger = triggered[0]["prop_id"]
        trigger_value = triggered[0].get("value")

        if trigger == "nu-back-btn.n_clicks":
            if not trigger_value:
                raise PreventUpdate
            return [], {"display": "block"}, {"visibility": "hidden"}, None

        if not view_request or not isinstance(view_request, dict):
            raise PreventUpdate

        article_id = view_request.get("article_id")
        if not article_id:
            raise PreventUpdate

        resp = make_api_request("GET", f"/training/articles/{article_id}")
        if isinstance(resp, dict) and resp.get("error"):
            return (
                dbc.Alert("Article not found.", color="danger"),
                {"display": "none"},
                {"visibility": "visible"},
                None,
            )

        return (
            _render_detail(resp),
            {"display": "none"},
            {"visibility": "visible"},
            article_id,
        )

    @app.callback(
        [
            Output("nu-editor-request", "data"),
            Output("nu-selected-article-id", "data", allow_duplicate=True),
            Output("nu-view-article-request", "data", allow_duplicate=True),
        ],
        Input({"type": "nu-card-edit-btn", "index": dash.ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def queue_card_edit(_card_clicks):
        triggered = dash.ctx.triggered
        if not triggered:
            raise PreventUpdate
        if not triggered[0].get("value"):
            raise PreventUpdate
        triggered_id = dash.ctx.triggered_id
        if (
            not isinstance(triggered_id, dict)
            or triggered_id.get("type") != "nu-card-edit-btn"
        ):
            raise PreventUpdate
        if triggered_id.get("index") == "__nu_placeholder__":
            raise PreventUpdate
        article_id = triggered_id["index"]
        return (
            {
                "action": "edit",
                "article_id": article_id,
                "seq": triggered[0]["value"],
            },
            article_id,
            {"article_id": article_id, "seq": triggered[0]["value"]},
        )

    @app.callback(
        Output("nu-editor-request", "data", allow_duplicate=True),
        Input("nu-new-article-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def queue_new_article(new_click):
        if not new_click:
            raise PreventUpdate
        return {"action": "new", "seq": new_click}

    @app.callback(
        Output("nu-editor-request", "data", allow_duplicate=True),
        Input("nu-edit-article-btn", "n_clicks"),
        State("nu-selected-article-id", "data"),
        prevent_initial_call=True,
    )
    def queue_edit_selected(edit_click, selected_id):
        if not edit_click:
            raise PreventUpdate
        if not selected_id:
            return {"action": "pick", "seq": edit_click}
        return {"action": "edit", "article_id": selected_id, "seq": edit_click}

    @app.callback(
        [
            Output("nu-editor-modal", "is_open"),
            Output("nu-editor-modal-title", "children"),
            Output("nu-editing-article-id", "data"),
            Output("nu-editor-title", "value"),
            Output("nu-editor-content-type", "value"),
            Output("nu-editor-category", "value"),
            Output("nu-editor-status", "value"),
            Output("nu-editor-systems", "value"),
            Output("nu-editor-summary", "value"),
            Output("nu-editor-purpose", "value"),
            Output("nu-editor-prerequisites", "value"),
            Output("nu-editor-safety", "value"),
            Output("nu-editor-steps", "value"),
            Output("nu-editor-risks", "value"),
            Output("nu-editor-troubleshooting", "value"),
            Output("nu-editor-body", "value"),
            Output("nu-editor-tags", "value"),
            Output("nu-editor-loom", "value"),
            Output("nu-editor-sharepoint", "value"),
            Output("nu-editor-rich-content", "value"),
            Output("nu-editor-video-embed", "value"),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        Input("nu-editor-request", "data"),
        prevent_initial_call=True,
    )
    def open_editor_from_request(request):
        if not request or not isinstance(request, dict):
            raise PreventUpdate

        closed_toast = (False, "Nova University", "")

        if request.get("action") == "new":
            return _new_editor_values() + closed_toast

        if request.get("action") == "pick":
            return (
                (False, "New Article", None)
                + ((None,) * 18)
                + (
                    True,
                    "Nova University",
                    "Click an article in the list to view it, then Edit selected.",
                )
            )

        if request.get("action") == "edit":
            article_id = request.get("article_id")
            if not article_id:
                raise PreventUpdate
            resp = make_api_request("GET", f"/training/articles/{article_id}")
            if isinstance(resp, dict) and resp.get("error"):
                return (
                    (False, "New Article", None)
                    + ((None,) * 18)
                    + (
                        True,
                        "Nova University",
                        "Could not load article for editing.",
                    )
                )
            return _editor_open_values(resp, article_id) + closed_toast

        raise PreventUpdate

    @app.callback(
        [
            Output("nu-editor-modal", "is_open", allow_duplicate=True),
            Output("nu-editor-modal-title", "children", allow_duplicate=True),
            Output("nu-editing-article-id", "data", allow_duplicate=True),
            Output("nu-editor-title", "value", allow_duplicate=True),
            Output("nu-editor-content-type", "value", allow_duplicate=True),
            Output("nu-editor-category", "value", allow_duplicate=True),
            Output("nu-editor-status", "value", allow_duplicate=True),
            Output("nu-editor-systems", "value", allow_duplicate=True),
            Output("nu-editor-summary", "value", allow_duplicate=True),
            Output("nu-editor-purpose", "value", allow_duplicate=True),
            Output("nu-editor-prerequisites", "value", allow_duplicate=True),
            Output("nu-editor-safety", "value", allow_duplicate=True),
            Output("nu-editor-steps", "value", allow_duplicate=True),
            Output("nu-editor-risks", "value", allow_duplicate=True),
            Output("nu-editor-troubleshooting", "value", allow_duplicate=True),
            Output("nu-editor-body", "value", allow_duplicate=True),
            Output("nu-editor-tags", "value", allow_duplicate=True),
            Output("nu-editor-loom", "value", allow_duplicate=True),
            Output("nu-editor-sharepoint", "value", allow_duplicate=True),
            Output("nu-editor-rich-content", "value", allow_duplicate=True),
            Output("nu-editor-video-embed", "value", allow_duplicate=True),
            Output("nu-article-detail", "children", allow_duplicate=True),
            Output("nu-selected-article-id", "data", allow_duplicate=True),
            Output("nu-empty-state", "style", allow_duplicate=True),
            Output("nu-back-btn", "style", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [
            Input("nu-editor-cancel-btn", "n_clicks"),
            Input("nu-editor-save-btn", "n_clicks"),
        ],
        [
            State("nu-editing-article-id", "data"),
            State("nu-editor-title", "value"),
            State("nu-editor-content-type", "value"),
            State("nu-editor-category", "value"),
            State("nu-editor-status", "value"),
            State("nu-editor-systems", "value"),
            State("nu-editor-summary", "value"),
            State("nu-editor-purpose", "value"),
            State("nu-editor-prerequisites", "value"),
            State("nu-editor-safety", "value"),
            State("nu-editor-steps", "value"),
            State("nu-editor-risks", "value"),
            State("nu-editor-troubleshooting", "value"),
            State("nu-editor-body", "value"),
            State("nu-editor-tags", "value"),
            State("nu-editor-loom", "value"),
            State("nu-editor-sharepoint", "value"),
            State("nu-editor-rich-content", "value"),
            State("nu-editor-video-embed", "value"),
        ],
        prevent_initial_call=True,
    )
    def save_or_cancel_editor(
        cancel_click,
        save_click,
        editing_id,
        title,
        content_type,
        category_id,
        status,
        systems,
        summary,
        purpose,
        prerequisites,
        safety,
        steps_text,
        risks_text,
        troubleshooting,
        body,
        tags,
        loom,
        sharepoint,
        rich_html,
        video_embed,
    ):
        triggered = dash.ctx.triggered
        if not triggered:
            raise PreventUpdate
        trigger = triggered[0]["prop_id"]
        trigger_value = triggered[0].get("value")
        if not trigger_value:
            raise PreventUpdate

        empty = (None,) * 18
        no_side = (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

        if trigger == "nu-editor-cancel-btn.n_clicks":
            return (False, "New Article", None) + empty + no_side

        def _open_header():
            return "Edit Article" if editing_id else "New Article"

        def _field_values():
            return (
                title,
                content_type,
                category_id,
                status,
                systems,
                summary,
                purpose,
                prerequisites,
                safety,
                steps_text,
                risks_text,
                troubleshooting,
                body,
                tags,
                loom,
                sharepoint,
                rich_html,
                video_embed,
            )

        if not title or not str(title).strip():
            return (
                (
                    True,
                    _open_header(),
                    editing_id,
                )
                + _field_values()
                + (
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    True,
                    "Nova University",
                    "Title is required before saving.",
                )
            )

        payload = {
            "title": str(title).strip(),
            "content_type": content_type or "sop",
            "category_id": category_id,
            "status": status or "draft",
            "summary": summary,
            "purpose": purpose,
            "prerequisites": prerequisites,
            "safety_notes": safety,
            "steps": _parse_steps_text(steps_text),
            "risks": _parse_risks_text(risks_text),
            "troubleshooting": troubleshooting,
            "body_markdown": body,
            "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
            "systems": [s.strip() for s in (systems or "").split(",") if s.strip()],
            "loom_url": loom or None,
            "sharepoint_url": sharepoint or None,
            "video_embed_url": video_embed or None,
            "rich_content_html": rich_html or None,
        }
        if editing_id:
            resp = make_api_request("PUT", f"/training/articles/{editing_id}", payload)
        else:
            resp = make_api_request("POST", "/training/articles", payload)

        if isinstance(resp, dict) and resp.get("error"):
            err_raw = resp.get("error", "Save failed")
            try:
                err_msg = json.loads(err_raw).get("message", err_raw)
            except (TypeError, json.JSONDecodeError):
                err_msg = str(err_raw)
            return (
                (
                    True,
                    _open_header(),
                    editing_id,
                )
                + _field_values()
                + (
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    True,
                    "Nova University",
                    f"Save failed: {err_msg}",
                )
            )

        article_id = resp.get("id") if isinstance(resp, dict) else None
        return (
            (False, "New Article", None)
            + empty
            + (
                _render_detail(resp),
                article_id,
                {"display": "none"},
                {"visibility": "visible"},
                True,
                "Nova University",
                "Article saved.",
            )
        )

    app.clientside_callback(
        """
        function(is_open, rich_html) {
            if (!is_open) return window.dash_clientside.no_update;
            setTimeout(function() {
                var hidden = document.getElementById('nu-editor-rich-content');
                if (hidden && rich_html !== undefined && rich_html !== null) {
                    hidden.value = rich_html;
                }
                if (window.nuEditorLoadContent) {
                    window.nuEditorLoadContent();
                }
                if (window.nuEditorInit) {
                    /* re-bind after modal render */
                }
            }, 200);
            return '';
        }
        """,
        Output("nu-editor-sync-dummy", "children"),
        Input("nu-editor-modal", "is_open"),
        State("nu-editor-rich-content", "value"),
    )

    @app.callback(
        Output("nu-llm-status-badge", "children"),
        Output("nu-llm-status-badge", "color"),
        Input("main-tabs", "active_tab"),
    )
    def refresh_llm_status(active_tab):
        if active_tab != "training":
            raise PreventUpdate
        resp = make_api_request("GET", "/training/ask/status")
        if isinstance(resp, dict) and resp.get("error"):
            return "API offline", "warning"
        if not resp.get("configured"):
            return "Set API key in AI Settings", "warning"
        if not resp.get("enabled"):
            return "LLM disabled", "secondary"
        model = resp.get("model") or "OpenAI"
        return f"AI ready · {model}", "success"

    @app.callback(
        Output("nu-llm-response", "children"),
        Input("nu-ask-btn", "n_clicks"),
        Input("nu-ask-clear-btn", "n_clicks"),
        State("nu-ask-input", "value"),
        State("nu-selected-category-id", "data"),
        State("nu-system-filter", "value"),
        State("nu-type-filter", "value"),
        State("nu-status-filter", "value"),
        prevent_initial_call=True,
    )
    def ask_nova_university(
        ask_click,
        clear_click,
        question,
        category_id,
        system,
        content_type,
        status_filter,
    ):
        triggered = dash.ctx.triggered
        if not triggered:
            raise PreventUpdate
        prop = triggered[0]["prop_id"]
        if prop == "nu-ask-clear-btn.n_clicks":
            return []
        if not ask_click or not question or not str(question).strip():
            return dbc.Alert(
                "Enter a question first.", color="light", className="small"
            )

        payload = {
            "question": str(question).strip(),
            "status": status_filter or "published",
        }
        if category_id and category_id != "all":
            payload["category_id"] = category_id
        if system:
            payload["system"] = system
        if content_type:
            payload["content_type"] = content_type

        resp = make_api_request("POST", "/training/ask", payload)
        if isinstance(resp, dict) and resp.get("error"):
            err_raw = resp.get("error", "Ask failed")
            try:
                err_msg = json.loads(err_raw).get("detail", err_raw)
                if isinstance(err_msg, list):
                    err_msg = "; ".join(str(x) for x in err_msg)
            except (TypeError, json.JSONDecodeError):
                err_msg = str(err_raw)
            return dbc.Alert(err_msg, color="warning", className="small")

        return _render_llm_response(resp)

    @app.callback(
        Output("nu-view-article-request", "data", allow_duplicate=True),
        Input({"type": "nu-ask-source-btn", "index": dash.ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_article_from_ask_source(_clicks):
        triggered = dash.ctx.triggered
        if not triggered or not triggered[0].get("value"):
            raise PreventUpdate
        triggered_id = dash.ctx.triggered_id
        if (
            not isinstance(triggered_id, dict)
            or triggered_id.get("type") != "nu-ask-source-btn"
        ):
            raise PreventUpdate
        if triggered_id.get("index") == "__nu_placeholder__":
            raise PreventUpdate
        return {
            "article_id": triggered_id["index"],
            "seq": triggered[0]["value"],
        }

    @app.callback(
        Output("nu-llm-settings-modal", "is_open"),
        Input("nu-llm-settings-btn", "n_clicks"),
        Input("nu-llm-settings-cancel", "n_clicks"),
        Input("nu-llm-settings-save", "n_clicks"),
        State("nu-llm-settings-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_llm_settings_modal(open_click, cancel_click, save_click, is_open):
        triggered = dash.ctx.triggered
        if not triggered:
            raise PreventUpdate
        prop = triggered[0]["prop_id"]
        if prop in ("nu-llm-settings-cancel.n_clicks", "nu-llm-settings-save.n_clicks"):
            return False
        if prop == "nu-llm-settings-btn.n_clicks" and open_click:
            return True
        raise PreventUpdate

    @app.callback(
        [
            Output("nu-llm-model", "value"),
            Output("nu-llm-max-articles", "value"),
            Output("nu-llm-enabled", "value"),
            Output("nu-llm-api-key-hint", "children"),
            Output("nu-llm-api-key", "value"),
        ],
        Input("nu-llm-settings-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_llm_settings_form(_open_click):
        resp = make_api_request("GET", "/training/llm-config")
        if isinstance(resp, dict) and resp.get("error"):
            return "gpt-4o-mini", 8, ["enabled"], "Could not load settings.", ""
        enabled = ["enabled"] if resp.get("enabled", True) else []
        masked = resp.get("api_key_masked") or "Not set"
        hint = (
            f"Current key: {masked}"
            if resp.get("configured")
            else "No API key saved yet."
        )
        return (
            resp.get("model") or "gpt-4o-mini",
            resp.get("max_context_articles") or 8,
            enabled,
            hint,
            "",
        )

    @app.callback(
        [
            Output("nu-llm-settings-status", "children"),
            Output("nu-llm-status-badge", "children", allow_duplicate=True),
            Output("nu-llm-status-badge", "color", allow_duplicate=True),
            Output("nu-llm-api-key-hint", "children", allow_duplicate=True),
        ],
        Input("nu-llm-settings-save", "n_clicks"),
        [
            State("nu-llm-api-key", "value"),
            State("nu-llm-model", "value"),
            State("nu-llm-max-articles", "value"),
            State("nu-llm-enabled", "value"),
        ],
        prevent_initial_call=True,
    )
    def save_llm_settings(save_click, api_key, model, max_articles, enabled_values):
        if not save_click:
            raise PreventUpdate
        payload = {
            "model": model or "gpt-4o-mini",
            "max_context_articles": int(max_articles or 8),
            "enabled": "enabled" in (enabled_values or []),
        }
        if api_key and str(api_key).strip():
            payload["api_key"] = str(api_key).strip()

        resp = make_api_request("PUT", "/training/llm-config", payload)
        if isinstance(resp, dict) and resp.get("error"):
            return (
                dbc.Alert("Save failed.", color="danger", className="mb-0 py-1"),
                no_update,
                no_update,
                no_update,
            )

        masked = resp.get("api_key_masked") or ""
        hint = (
            f"Current key: {masked}"
            if resp.get("configured")
            else "No API key saved yet."
        )
        badge = (
            f"AI ready · {resp.get('model')}"
            if resp.get("configured")
            else "Set API key in AI Settings"
        )
        color = "success" if resp.get("configured") else "warning"
        return (
            dbc.Alert(
                "Settings saved to config/openai.json.",
                color="success",
                className="mb-0 py-1",
            ),
            badge,
            color,
            hint,
        )

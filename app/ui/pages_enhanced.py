"""Enhanced page components for the Dash UI with full CRUD."""

from dash import html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from typing import Dict, List, Any


class ProductsPageEnhanced:
    """Enhanced products management page with full CRUD."""
    
    @staticmethod
    def get_layout():
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Products Management", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Add Product", id="add-product-btn", color="success", className="me-2"),
                            dbc.Button("Edit Selected", id="edit-product-btn", color="primary", className="me-2", disabled=True),
                            dbc.Button("Delete Selected", id="delete-product-btn", color="danger", className="me-2", disabled=True),
                            dbc.Button("Refresh", id="products-refresh", color="info"),
                        ], width=8),
                        dbc.Col([
                            html.Div([
                                dbc.Label("Filter by Type:", className="me-2", style={"display": "inline-block", "marginRight": "10px"}),
                                dbc.Checkbox(id="filter-raw", label="RAW", value=True, className="me-2", style={"display": "inline-block"}),
                                dbc.Checkbox(id="filter-wip", label="WIP", value=True, className="me-2", style={"display": "inline-block"}),
                                dbc.Checkbox(id="filter-finished", label="FINISHED", value=True, style={"display": "inline-block"}),
                            ], style={"textAlign": "right"})
                        ], width=4)
                    ], className="mb-3"),
                    dash_table.DataTable(
                        id="products-table",
                        columns=[
                            {"name": "SKU", "id": "sku"},
                            {"name": "Name", "id": "name"},
                            {"name": "Type", "id": "product_type"},
                            {"name": "Base Unit", "id": "base_unit"},
                            {"name": "Size", "id": "size"},
                            {"name": "Pack", "id": "pack"},
                            {"name": "Density (kg/L)", "id": "density_kg_per_l"},
                            {"name": "ABV (%)", "id": "abv_percent"},
                            {"name": "Purchase Cost", "id": "purcost"},
                            {"name": "Active", "id": "is_active"},
                        ],
                        data=[],
                        sort_action="native",
                        filter_action="native",
                        page_action="native",
                        page_current=0,
                        page_size=25,
                        row_selectable="single",
                        selected_rows=[],
                        style_cell={'textAlign': 'left', 'fontSize': '12px'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        style_data={'whiteSpace': 'normal', 'height': 'auto'},
                    )
                ])
            ]),
            
            # Add/Edit Product Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="product-modal-title")),
                dbc.ModalBody([
                    dbc.Accordion([
                        # Basic Information
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("SKU *"),
                                    dbc.Input(id="product-sku", placeholder="Enter SKU", required=True)
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Name *"),
                                    dbc.Input(id="product-name", placeholder="Enter product name", required=True)
                                ], width=6),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Product Type *"),
                                    dbc.Select(
                                        id="product-type",
                                        options=[
                                            {"label": "RAW - Raw Material", "value": "RAW"},
                                            {"label": "WIP - Work In Progress", "value": "WIP"},
                                            {"label": "FINISHED - Finished Good", "value": "FINISHED"},
                                        ],
                                        value="RAW",
                                        required=True
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Is Active"),
                                    dbc.Select(
                                        id="product-is-active",
                                        options=[
                                            {"label": "Yes", "value": "true"},
                                            {"label": "No", "value": "false"},
                                        ],
                                        value="true"
                                    )
                                ], width=6),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Description"),
                                    dbc.Textarea(id="product-description", placeholder="Enter description")
                                ], width=12)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("EAN13 Barcode"),
                                    dbc.Input(id="product-ean13", placeholder="EAN13")
                                ], width=12),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Raw Material Group ID"),
                                    dbc.Input(id="product-raw-material-group-id", placeholder="Raw Material Group ID")
                                ], width=12)
                            ])
                        ], title="Basic Information", item_id="basic"),
                        
                        # Physical Properties
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Base Unit"),
                                    dcc.Dropdown(
                                        id="product-base-unit",
                                        placeholder="Select base unit",
                                        searchable=True,
                                        clearable=True
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Size"),
                                    dbc.Input(id="product-size", placeholder="Size")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Weight (kg)"),
                                    dbc.Input(id="product-weight", type="number", step="0.001", placeholder="0.000")
                                ], width=4),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Pack"),
                                    dbc.Input(id="product-pack", type="number", placeholder="Pack quantity")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Package Type"),
                                    dbc.Input(id="product-pkge", type="number", placeholder="Package type")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Density (kg/L)"),
                                    dbc.Input(id="product-density", type="number", step="0.001", placeholder="0.000")
                                ], width=4),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("ABV (%)"),
                                    dbc.Input(id="product-abv", type="number", step="0.01", placeholder="0.00")
                                ], width=6),
                                dbc.Col([], width=6),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Volume Solid"),
                                    dbc.Input(id="product-vol-solid", type="number", step="0.000001", placeholder="0.000000")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Solid SG"),
                                    dbc.Input(id="product-solid-sg", type="number", step="0.000001", placeholder="0.000000")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Weight Solid"),
                                    dbc.Input(id="product-wt-solid", type="number", step="0.000001", placeholder="0.000000")
                                ], width=4),
                            ])
                        ], title="Physical Properties", item_id="physical"),
                        
                        # Classifications
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Form Code"),
                                    dbc.Input(id="product-form", placeholder="Form code")
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("DG Flag"),
                                    dbc.Select(
                                        id="product-dgflag",
                                        options=[
                                            {"label": "Y", "value": "Y"},
                                            {"label": "N", "value": "N"},
                                        ],
                                        placeholder="Dangerous goods"
                                    )
                                ], width=6),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Label Type"),
                                    dbc.Input(id="product-label", type="number", placeholder="Label")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Manufacturer Code"),
                                    dbc.Input(id="product-manu", type="number", placeholder="Manufacturer")
                                ], width=4),
                            ])
                        ], title="Classifications", item_id="classifications"),
                        
                        # Cost Information
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Purchase Cost"),
                                    dbc.Input(id="product-purcost", type="number", step="0.01", placeholder="0.00")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Purchase Tax"),
                                    dbc.Input(id="product-purtax", type="number", step="0.01", placeholder="0.00")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Wholesale Cost"),
                                    dbc.Input(id="product-wholesalecost", type="number", step="0.01", placeholder="0.00")
                                ], width=4),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Excise Amount"),
                                    dbc.Input(id="product-excise-amount", type="number", step="0.01", placeholder="0.00")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Tax Included"),
                                    dbc.Select(
                                        id="product-taxinc",
                                        options=[
                                            {"label": "Y", "value": "Y"},
                                            {"label": "N", "value": "N"},
                                        ],
                                        placeholder="Tax included?"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Sales Tax Code"),
                                    dbc.Input(id="product-salestaxcde", placeholder="Tax code")
                                ], width=4),
                            ])
                        ], title="Cost", item_id="cost"),
                        
                        # Pricing
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Wholesale"),
                                    dbc.Input(id="product-wholesalecde", type="number", step="0.01", placeholder="$0.00")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Retail"),
                                    dbc.Input(id="product-retailcde", type="number", step="0.01", placeholder="$0.00")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Counter"),
                                    dbc.Input(id="product-countercde", type="number", step="0.01", placeholder="$0.00")
                                ], width=4),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Trade"),
                                    dbc.Input(id="product-tradecde", type="number", step="0.01", placeholder="$0.00")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Contract"),
                                    dbc.Input(id="product-contractcde", type="number", step="0.01", placeholder="$0.00")
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Industrial"),
                                    dbc.Input(id="product-industrialcde", type="number", step="0.01", placeholder="$0.00")
                                ], width=4),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Distributor"),
                                    dbc.Input(id="product-distributorcde", type="number", step="0.01", placeholder="$0.00")
                                ], width=6),
                                dbc.Col([], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Discount 1"),
                                    dbc.Input(id="product-disccdeone", type="number", step="0.01", placeholder="$0.00")
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Discount 2"),
                                    dbc.Input(id="product-disccdetwo", type="number", step="0.01", placeholder="$0.00")
                                ], width=6),
                            ], className="mt-3")
                        ], title="Pricing", item_id="pricing"),
                        
                        # Raw Material Usage Fields
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Supplier ID"),
                                    dbc.Input(id="product-supplier-id", placeholder="Supplier ID")
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Purchase Unit"),
                                    dcc.Dropdown(
                                        id="product-purchase-unit",
                                        placeholder="Select purchase unit",
                                        searchable=True,
                                        clearable=True
                                    )
                                ], width=6),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Purchase Volume"),
                                    dbc.Input(id="product-purchase-volume", type="number", step="0.001", placeholder="0.000")
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Usage Cost"),
                                    dbc.Input(id="product-usage-cost", type="number", step="0.01", placeholder="0.00")
                                ], width=6),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Usage Unit"),
                                    dcc.Dropdown(
                                        id="product-usage-unit",
                                        placeholder="Select usage unit",
                                        searchable=True,
                                        clearable=True
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Restock Level"),
                                    dbc.Input(id="product-restock-level", type="number", step="0.001", placeholder="0.000")
                                ], width=6),
                            ])
                        ], title="Raw Material Usage", item_id="raw-material"),
                        
                        # Finished Good Specific Fields
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Formula ID"),
                                    dbc.Input(id="product-formula-id", placeholder="Formula ID")
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Formula Revision"),
                                    dbc.Input(id="product-formula-revision", type="number", placeholder="Revision number")
                                ], width=6),
                            ])
                        ], title="Assembly", item_id="finished-good"),
                    ], start_collapsed=True, active_item="basic"),
                    html.Div(id="product-form-hidden", style={"display": "none"})
                ]),
                dbc.ModalFooter([
                    dbc.Button("Save", id="product-save-btn", color="primary", className="me-2"),
                    dbc.Button("Cancel", id="product-cancel-btn", color="secondary")
                ])
            ], id="product-form-modal", is_open=False, size="xl", backdrop="static"),
            
            # Delete Confirmation Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
                dbc.ModalBody([
                    html.P("Are you sure you want to delete this product?"),
                    html.P(id="delete-product-name", className="text-danger fw-bold")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Delete", id="delete-confirm-btn", color="danger", className="me-2"),
                    dbc.Button("Cancel", id="delete-cancel-btn", color="secondary")
                ])
            ], id="delete-confirm-modal", is_open=False)
        ], fluid=True)


# Export enhanced page
products_page_enhanced = ProductsPageEnhanced()


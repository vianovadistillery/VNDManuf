# Product CRUD Implementation Plan for Dash UI

## Summary

The Product model now includes **24 additional fields** from the TPManuf legacy system. This document outlines the complete CRUD implementation for the Dash UI.

## New Fields Added to Product Model

### Basic Information (Existing)
- `sku` - Product code
- `name` - Product name
- `description` - Description

### New Identification Fields (3 fields)
- `ean13` - EAN-13 barcode
- `supplier_id` - Supplier link
- `base_unit` - Base unit (KG, LT, EA)

### Physical Properties (5 fields)
- `size` - Size
- `pack` - Package quantity
- `density_kg_per_l` - Density for conversions
- `abv_percent` - ABV percentage
- (Existing fields already in form)

### Classifications (5 fields)
- `dgflag` - Dangerous goods flag
- `form` - Form code
- `pkge` - Package type
- `label` - Label type
- `manu` - Manufacturer code

### Financial Fields (5 fields)
- `taxinc` - Tax included flag
- `salestaxcde` - Sales tax code
- `purcost` - Purchase cost
- `purtax` - Purchase tax
- `wholesalecost` - Wholesale cost

### Pricing Codes (8 fields)
- `disccdeone`, `disccdetwo` - Discount codes
- `wholesalecde`, `retailcde`, `countercde`
- `tradecde`, `contractcde`, `industrialcde`, `distributorcde`

## Recommended UI Structure

### Option 1: Tabbed Form (Recommended for 24+ fields)

Organize fields into logical tabs:

1. **Basic Info Tab**
   - SKU, Name, Description, EAN13
   - Supplier dropdown

2. **Physical Properties Tab**
   - Size, Base Unit, Pack
   - Density, ABV

3. **Classifications Tab**
   - DG Flag, Form, Package Type
   - Label Type, Manufacturer

4. **Financial Tab**
   - Purchase Cost, Purchase Tax
   - Wholesale Cost
   - Tax Codes

5. **Pricing Tab**
   - All 8 pricing tier codes

### Option 2: Accordion/Collapsible Sections

Same organization but in collapsible sections on one page.

### Option 3: Wizard/Stepper

Multi-step wizard for adding products.

## Implementation Tasks

### 1. Update Product Form Modal (Add/Edit)

Create a comprehensive modal with tabs:

```python
# In app/ui/pages.py - Update ProductsPage.get_layout()

dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle(id="product-modal-title", children="Add New Product")),
    dbc.ModalBody([
        dbc.Tabs(
            id="product-form-tabs",
            active_tab="basic",
            children=[
                dbc.Tab([
                    # Basic fields
                    dbc.Input(id="product-sku", ...),
                    dbc.Input(id="product-name", ...),
                    # ... etc
                ], label="Basic Info", tab_id="basic"),

                dbc.Tab([
                    # Physical properties
                    dbc.Input(id="product-size", ...),
                    dbc.Input(id="product-base-unit", ...),
                    # ... etc
                ], label="Physical", tab_id="physical"),

                dbc.Tab([
                    # Classifications
                    dbc.Input(id="product-dgflag", ...),
                    # ... etc
                ], label="Classifications", tab_id="classifications"),

                dbc.Tab([
                    # Financial fields
                    dbc.Input(id="product-purcost", ...),
                    # ... etc
                ], label="Financial", tab_id="financial"),

                dbc.Tab([
                    # Pricing codes
                    dbc.Input(id="product-wholesalecde", ...),
                    # ... etc
                ], label="Pricing", tab_id="pricing"),
            ]
        )
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="product-save", color="primary"),
        dbc.Button("Cancel", id="product-cancel", color="secondary")
    ])
], id="product-form", is_open=False, size="xl")  # Large modal
```

### 2. Add Edit Capability

- Row selection in table
- "Edit" button appears when row selected
- Load existing data into form
- Update modal title to "Edit Product"

### 3. Add Delete Capability

- "Delete" button with confirmation modal
- Soft delete (set is_active=False) or hard delete

### 4. Update Callbacks

New callbacks needed:

```python
# Load product data for editing
@app.callback(
    [Output("product-form", "is_open"),
     Output("product-modal-title", "children")],
    [Input("edit-product-btn", "n_clicks")],
    [State("products-table", "selected_rows"),
     State("products-table", "data")],
    prevent_initial_call=True
)
def open_edit_modal(n_clicks, selected_rows, data):
    # Load product data
    # Pre-populate form
    return True, "Edit Product"

# Delete product
@app.callback(
    Output("delete-confirm-modal", "is_open"),
    [Input("delete-product-btn", "n_clicks")],
    [State("products-table", "selected_rows")],
    prevent_initial_call=True
)
def confirm_delete(n_clicks, selected_rows):
    return True if n_clicks else False

# Actual delete
@app.callback(
    Output("products-table", "data"),
    [Input("delete-confirm", "n_clicks")],
    [State("products-table", "selected_rows"),
     State("products-table", "data")],
    prevent_initial_call=True
)
def delete_product(n_clicks, selected_rows, data):
    # Call API to delete
    # Refresh table
    pass
```

### 5. Update API DTOs

Extend `app/api/dto.py`:

```python
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    ean13: Optional[str] = None
    supplier_id: Optional[str] = None
    size: Optional[str] = None
    base_unit: Optional[str] = None
    pack: Optional[int] = None
    density_kg_per_l: Optional[Decimal] = None
    abv_percent: Optional[Decimal] = None
    dgflag: Optional[str] = None
    form: Optional[str] = None
    pkge: Optional[int] = None
    label: Optional[int] = None
    manu: Optional[int] = None
    taxinc: Optional[str] = None
    salestaxcde: Optional[str] = None
    purcost: Optional[Decimal] = None
    purtax: Optional[Decimal] = None
    wholesalecost: Optional[Decimal] = None
    disccdeone: Optional[str] = None
    disccdetwo: Optional[str] = None
    wholesalecde: Optional[str] = None
    retailcde: Optional[str] = None
    countercde: Optional[str] = None
    tradecde: Optional[str] = None
    contractcde: Optional[str] = None
    industrialcde: Optional[str] = None
    distributorcde: Optional[str] = None
    is_active: bool = True
```

### 6. Update Table Columns

Add key columns to display in products table:

```python
# Show important fields in table
columns = [
    {"name": "SKU", "id": "sku"},
    {"name": "Name", "id": "name"},
    {"name": "Base Unit", "id": "base_unit"},
    {"name": "Size", "id": "size"},
    {"name": "Pack", "id": "pack"},
    {"name": "Purchase Cost", "id": "purcost"},
    {"name": "Active", "id": "is_active"},
]
```

## Field Organization for Form

### Section 1: Basic Information
```
SKU * (required)
Name * (required)
Description
EAN13 Barcode
Supplier (dropdown)
Base Unit (KG/LT/EA)
```

### Section 2: Physical Properties
```
Size
Pack (integer)
Density (kg/L) - 6 decimal places
ABV (%) - 2 decimal places
```

### Section 3: Classifications
```
Dangerous Goods Flag (Y/N)
Form Code
Package Type
Label Type
Manufacturer Code
```

### Section 4: Financial
```
Tax Included (Y/N)
Sales Tax Code
Purchase Cost
Purchase Tax
Wholesale Cost
```

### Section 5: Pricing Codes (8 codes)
```
Wholesale Code
Retail Code
Counter Code
Trade Code
Contract Code
Industrial Code
Distributor Code
Discount Code 1
Discount Code 2
```

## Recommended Layout

Use **accordion-style** sections within modal for better UX:

```python
dbc.Accordion([
    dbc.AccordionItem([
        # Basic fields
    ], title="Basic Information"),

    dbc.AccordionItem([
        # Physical fields
    ], title="Physical Properties"),

    dbc.AccordionItem([
        # Classifications
    ], title="Classifications"),

    dbc.AccordionItem([
        # Financial
    ], title="Financial Information"),

    dbc.AccordionItem([
        # Pricing codes
    ], title="Pricing Codes"),
], always_open=False)
```

## Next Steps

1. ✅ Model extended
2. ✅ Migration generated
3. ⏳ Fix migration (handle existing columns)
4. ⏳ Update API DTOs (`app/api/dto.py`)
5. ⏳ Update API endpoints (`app/api/products.py`)
6. ⏳ Create comprehensive form in Dash UI
7. ⏳ Add edit/delete functionality
8. ⏳ Test full CRUD flow

## Estimated Implementation Time

- API Updates: 30 minutes
- Dash Form Creation: 1-2 hours
- Edit/Delete Logic: 30 minutes
- Testing: 30 minutes
- **Total: 2.5-4 hours**

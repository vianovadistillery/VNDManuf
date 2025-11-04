# Product Form Refactoring Tasks

## Completed
- [x] Created PurchaseFormat model
- [x] Created Purchase Format API
- [x] Added Purchase Format router to main API

## Remaining Tasks

### 1. Purchase Format Settings UI
- [ ] Add Purchase Format tab to settings page
- [ ] Create Purchase Format CRUD callbacks
- [ ] Seed initial purchase formats (IBC, bag, Bag, Carboy, Drum, Box, etc.)

### 2. Product Form Restructuring
- [ ] Move Base Unit, size, weight, ABV, Density to Basic Information section
- [ ] Remove raw_material_group_id from product form and table
- [ ] Fix SKU field not saving when updated
- [ ] Remove formula and formula_revision from assembly area and product table
- [ ] Remove "Pack" and "package type" fields and titles from product table
- [ ] Remove Physical Properties area (now empty after moving fields)
- [ ] Remove "Pricing" and "Cost" areas and fields from product table
- [ ] Rename "Raw Material Usage" to "Purchase"
- [ ] Make Supplier ID a dropdown from contacts who are suppliers
- [ ] Add Purchase format field with dropdown from purchase_formats table
- [ ] Rename Purchase Volume to Purchase Quantity
- [ ] Rearrange Purchase fields into table format: Purchase Format, Quantity, unit, cost
- [ ] Add second row for Usage: unit, quantity (dropdown), calculate usage cost
- [ ] Rename "Usage Cost Settings" to "Cost Summary" and position second from bottom
- [ ] Add Inc GST COGS and Inc Excise COGS to Sales & Pricing table
- [ ] Move Sales & Pricing to bottom of form
- [ ] Remove lower assembly area (the one with Formula ID and Formula Revision)

### 3. Database Changes
- [ ] Create migration to add purchase_format_id to products table
- [ ] Create migration to remove pack and pkge columns (or mark as deprecated)
- [ ] Create migration to remove formula_id and formula_revision from products (or mark as deprecated)
- [ ] Create migration to remove raw_material_group_id (or mark as deprecated)

### 4. Callback Updates
- [ ] Update product save callback to handle new field structure
- [ ] Update product load callback to populate new fields
- [ ] Update pricing calculation to include Inc GST COGS and Inc Excise COGS
- [ ] Update usage cost calculation

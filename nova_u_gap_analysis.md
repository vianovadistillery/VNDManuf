# Nova U Gap Analysis

Generated: 2026-06-23T05:47:49.524699+00:00

## Summary

- **Articles generated:** 84
- **Confidence:** 64 high, 19 medium, 1 low
- **VNDManuf articles:** 55
- **VND-DAQ articles:** 29
- **Articles skipped:** 13

## Features Discovered

### VNDManuf
- Dash UI with tabs: Manufacturing (8 sub-tabs), Contacts, Sales (7 sub-tabs), CRM, Reports, Settings (7 sub-tabs), Nova U
- FastAPI /api/v1: products, inventory, work orders, formulas, assemblies, sales, CRM, documents, training, shopify webhooks
- Work order lifecycle: Draft → Released → In Progress → Complete (+ Hold, Void)
- Sales: orders, delivery docket/invoice conversion, PDF generation via DOCX templates
- Nova U: full CRUD API, search, corpus export, rich editor UI

### VND-DAQ
- Dash UI tabs: Live I/O, Alarms, Config, Event Log + extensive mimic sub-tabs
- Alarms: lolo/lo/hi/hihi with acknowledgement
- Trips: trip_engine with reset, interlocks, email alerts
- Permissives: JSON-configured fail-closed gating
- PID: LIT1 → P1 auto/manual control
- Historian: datawarehouse + configurable charts
- AB sequencer, valve control, chiller, IND560 scales
- vnd_mobile companion app

## Articles Generated

- `vndmanuf-introduction` (high) — Introduction to VNDManuf
- `vndmanuf-navigation-basics` (high) — VNDManuf Navigation Basics
- `vndmanuf-api-connectivity` (high) — API Connectivity and Demo Mode
- `vndmanuf-creating-products` (high) — Creating Products in VNDManuf
- `vndmanuf-editing-products` (high) — Editing and Duplicating Products
- `vndmanuf-product-filters` (high) — Product Capability Filters
- `vndmanuf-product-inventory-adjust` (medium) — Adjusting Product Inventory from Products Page
- `vndmanuf-inventory-lots` (high) — Inventory Lots Overview
- `vndmanuf-stock-on-hand` (high) — Stock on Hand API and Product SOH
- `vndmanuf-stocktake-procedure` (high) — Conducting a Stocktake in VNDManuf
- `vndmanuf-inventory-movements` (medium) — Inventory Movements and Adjustments
- `vndmanuf-rm-reports` (high) — RM Reports — Usage, Valuation and Reorder
- `vndmanuf-assemblies-formulas` (high) — Managing Assemblies (Formulas)
- `vndmanuf-assembly-operations` (medium) — Assembly and Disassembly Operations
- `vndmanuf-batch-processing-status` (high) — Batch Processing Page Status
- `vndmanuf-work-orders-overview` (high) — Work Orders Overview
- `vndmanuf-work-order-lifecycle` (high) — Work Order Status Lifecycle
- `vndmanuf-work-order-material-issue` (high) — Issuing Materials to Work Orders
- `vndmanuf-work-order-qc` (medium) — Work Order QC Tests
- `vndmanuf-work-order-costs` (high) — Work Order Costs and Overheads
- `vndmanuf-work-order-planned-qty` (high) — Work Order Planned Quantity Adjustment
- `vndmanuf-batch-reports` (high) — Batch Reports in VNDManuf
- `vndmanuf-contacts-management` (high) — Managing Contacts
- `vndmanuf-sales-orders-list` (high) — Sales Orders List and Filters
- `vndmanuf-sales-create-order` (high) — Creating a Sales Order
- `vndmanuf-sales-convert-delivery` (high) — Converting Orders to Delivery Dockets
- `vndmanuf-sales-convert-invoice` (medium) — Converting Orders to Invoices
- `vndmanuf-sales-customers` (high) — Sales Customers Dashboard
- `vndmanuf-sales-import-export` (medium) — Sales Import and Export
- `vndmanuf-sales-settings` (high) — Pricebooks and Sales Channels Settings
- `vndmanuf-crm-workspace` (high) — CRM Customer Workspace
- `vndmanuf-crm-activities` (high) — CRM Timeline and Activity Logging
- `vndmanuf-crm-staff-sites` (high) — CRM Staff and Sites Management
- `vndmanuf-crm-export-pdf` (high) — CRM PDF Export
- `vndmanuf-document-generation` (high) — Generating Delivery Docket and Invoice PDFs
- `vndmanuf-settings-units` (high) — Settings — Units of Measure
- `vndmanuf-settings-excise-rates` (high) — Settings — Excise Rates
- `vndmanuf-settings-work-areas-qc` (high) — Settings — Work Areas and QC Tests
- `vndmanuf-shopify-webhooks` (high) — Shopify Webhook Integration
- `vndmanuf-shopify-sync` (medium) — Shopify Order Import and Inventory Push
- `vndmanuf-reports-tab-status` (high) — Reports Tab — Current Limitations
- `vndmanuf-nova-u-search` (high) — Nova U — Browsing and Searching Articles
- `vndmanuf-nova-u-editor` (high) — Nova U — Creating and Editing Articles
- `vndmanuf-nova-u-publishing` (high) — Nova U — Publishing Articles
- `vndmanuf-nova-u-corpus-export` (high) — Nova U — LLM Corpus Export
- `vndmanuf-nova-u-media-upload` (high) — Nova U — Media Upload for Rich Content
- `vndmanuf-batches-api` (high) — Batches API — Create and Finish
- `vndmanuf-settings-purchase-formats` (high) — Settings — Purchase Formats
- `vndmanuf-settings-conditions` (medium) — Settings — Condition Types and Hazard Codes
- `vndmanuf-sales-backorders` (medium) — Sales Order Backorders
- `vndmanuf-delivery-docket-edit` (high) — Delivery Docket Updates
- `vndmanuf-buying-groups-reps` (high) — Buying Groups and Sales Reps
- `vndmanuf-formula-cost-report` (medium) — Formula Cost Analysis Report
- `vndmanuf-product-pricing-sections` (medium) — Product Purchase and Assembly Pricing Sections
- `vndmanuf-raw-materials-api` (high) — Raw Materials API (Legacy)
- `vndaq-system-overview` (high) — VND-DAQ System Overview
- `vndaq-live-io-tab` (high) — VND-DAQ Live I/O Tab
- `vndaq-alarm-levels` (high) — VND-DAQ Alarm Levels and Priorities
- `vndaq-alarm-acknowledgement` (high) — VND-DAQ Alarm Acknowledgement
- `vndaq-trip-overview` (high) — VND-DAQ Trip Overview
- `vndaq-trip-reset` (medium) — VND-DAQ Trip Reset Procedure
- `vndaq-permissives-overview` (high) — VND-DAQ Permissives — Understanding PERMIT OK / BLOCKED
- `vndaq-permissive-failures` (high) — VND-DAQ Common Permissive Failures
- `vndaq-interlocks` (high) — VND-DAQ Interlocks
- `vndaq-pid-manual-mode` (medium) — VND-DAQ P1 PID — Manual Mode
- `vndaq-pid-auto-mode` (high) — VND-DAQ P1 PID — Auto Mode
- `vndaq-pid-setpoint-tuning` (high) — VND-DAQ PID Setpoint and Tuning Changes
- `vndaq-historian-trends` (high) — VND-DAQ Historian — Reviewing Trends
- `vndaq-historian-export` (low) — VND-DAQ Historian — Exporting Data
- `vndaq-config-tag-alarms` (medium) — VND-DAQ Config Tab — Tag and Alarm Configuration
- `vndaq-event-log` (high) — VND-DAQ Event Log
- `vndaq-ab-sequencer` (medium) — VND-DAQ AB Sequencer and Bank Switching
- `vndaq-scale-integration` (high) — VND-DAQ Scale and Weight Integration
- `vndaq-chiller-integration` (high) — VND-DAQ Chiller Integration
- `vndaq-valve-control` (medium) — VND-DAQ Valve Control
- `vndaq-mobile-app` (high) — VND Mobile Companion App
- `vndaq-do-toggle-operation` (high) — VND-DAQ Digital Output Toggle Operation
- `vndaq-trip-email-alerts` (medium) — VND-DAQ Trip Email Alerts
- `vndaq-shutdown-procedure` (high) — VND-DAQ Graceful Shutdown
- `vndaq-mimic-process-views` (high) — VND-DAQ Mimic — Key Parameters and Heat Exchangers
- `vndaq-cu-sequencer` (medium) — VND-DAQ Cu Sequencer
- `vndaq-config-persistence` (medium) — VND-DAQ Config Callbacks and Persistence
- `vndaq-daq-loop` (high) — VND-DAQ DAQ Loop and Live Data
- `vndaq-datawarehouse-events` (high) — VND-DAQ Alarm and Trip Data Warehouse

## Articles Skipped

- **VNDManuf Dashboard Overview:** No single dashboard; main tabs serve as entry points (Use vndmanuf-introduction instead)
- **Production Scheduling:** No scheduling module found in API or UI (app/api/, app/ui/)
- **Product Categories:** No dedicated product category entity; product_type flag used (app/adapters/db/models.py Product.product_type)
- **Product Costing UI:** costing.py router exists but not mounted in main.py (app/api/costing.py)
- **Goods Receipts dedicated UI:** No dedicated goods receipt page; inventory movements API only (app/api/inventory.py)
- **Xero daily tasks UI:** Xero OAuth integration disabled in app.py (app/ui/app.py)
- **Shopify UI tab:** shopify_page.py stub, not in navigation (app/ui/pages/shopify_page.py)
- **VND-DAQ Login:** No authentication in main Dash app (DAQ/main.py)
- **VND-DAQ Starting/Completing Batch (named workflow):** Sequencer/bank logic exists but no single 'batch' UI matching ERP batches (DAQ/startup_sequencer.py)
- **Yield Recording dedicated screen:** Yield on work order complete in VNDManuf, not DAQ (app/api/work_orders.py)
- **Material Consumption standalone:** Covered under work order issues (app/api/work_orders.py)
- **Sales Analytics detail:** Analytics sub-tab exists; [VERIFY WITH OPERATOR] for exact charts (apps/vndmanuf_sales/ui/analytics_callbacks.py)
- **CRM Follow-ups / Calendar:** API exists for scheduled activities; UI depth [VERIFY] (app/api/crm.py)

## Areas Requiring Operator Validation

- Config tab write-back behaviour (display vs persist)
- Historian chart export button workflow
- PID manual mode AO write path from mimic
- Trip reset plant prerequisites
- Shopify operational workflow (cron vs manual API)
- Rich editor JS assets for Nova U (nuEditorLoadContent)
- Sales Analytics chart definitions
- Batch Processing future UI vs batches API workflow

## Areas With Insufficient Evidence

- VNDManuf login/authentication (not implemented in Dash UI)
- VND-DAQ user login (not implemented)
- Dedicated production scheduling
- Xero UI workflows (integration commented out)
- Product costing UI (API not mounted)

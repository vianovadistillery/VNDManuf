#!/usr/bin/env python3
"""Generate Nova U articles from VNDManuf + VND-DAQ codebase evidence.

Outputs:
  nova_u_generated_articles.json
  nova_u_gap_analysis.md
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DAQ_ROOT = ROOT.parent / "DAQ"
OUT_JSON = ROOT / "nova_u_generated_articles.json"
OUT_GAP = ROOT / "nova_u_gap_analysis.md"

# ---------------------------------------------------------------------------
# Article builder
# ---------------------------------------------------------------------------


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s)[:140].strip("-")


def art(
    title: str,
    *,
    slug: str | None = None,
    category_slug: str,
    content_type: str = "sop",
    status: str = "draft",
    summary: str,
    purpose: str,
    prerequisites: str = "None.",
    safety_notes: str = "N/A",
    steps: list[dict[str, str]],
    risks: list[dict[str, str]] | None = None,
    troubleshooting: str = "",
    tags: list[str] | None = None,
    systems: list[str] | None = None,
    confidence: str = "high",
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "title": title,
        "slug": slug or slugify(title),
        "category_slug": category_slug,
        "content_type": content_type,
        "status": status,
        "summary": summary,
        "purpose": purpose,
        "prerequisites": prerequisites,
        "safety_notes": safety_notes,
        "steps": steps,
        "risks": risks or [],
        "troubleshooting": troubleshooting,
        "tags": tags or [],
        "systems": systems or [],
        "confidence": confidence,
        "evidence": evidence or [],
    }


# ---------------------------------------------------------------------------
# VNDManuf articles (code-derived)
# ---------------------------------------------------------------------------

VNDMANUF: list[dict[str, Any]] = [
    # --- Navigation ---
    art(
        "Introduction to VNDManuf",
        slug="vndmanuf-introduction",
        category_slug="vndmanuf",
        content_type="guide",
        summary="Overview of the VNDManuf Dash application and its role in manufacturing, sales and training.",
        purpose="Orient new users to the application structure before using operational modules.",
        steps=[
            {
                "title": "Launch the application",
                "body": "Open the VNDManuf Dash UI. The header shows VNDManuf branding and a logo; an API connectivity alert appears if the FastAPI backend at http://127.0.0.1:8000 is unavailable (Demo Mode uses sample data).",
            },
            {
                "title": "Understand main navigation",
                "body": "Use the top-level tabs: Manufacturing, Contacts, Sales, CRM, Reports, Settings, and Nova U.",
            },
            {
                "title": "Know the backend",
                "body": "Business logic and persistence run through the FastAPI API mounted at /api/v1 (products, inventory, work orders, sales, CRM, documents, training, etc.).",
            },
        ],
        tags=["vndmanuf", "navigation", "onboarding"],
        systems=["vndmanuf"],
        evidence=["app/ui/app.py", "app/api/main.py"],
    ),
    art(
        "VNDManuf Navigation Basics",
        slug="vndmanuf-navigation-basics",
        category_slug="vndmanuf",
        content_type="guide",
        summary="How to move between Manufacturing sub-tabs, Sales sub-tabs, and other main areas.",
        purpose="Reduce navigation errors when switching between operational tasks.",
        steps=[
            {
                "title": "Select a main tab",
                "body": "Click Manufacturing, Contacts, Sales, CRM, Reports, Settings, or Nova U in the main tab bar (id: main-tabs).",
            },
            {
                "title": "Manufacturing sub-tabs",
                "body": "Under Manufacturing: Products, Assemblies, Batch Processing, Work Orders, Inventory, Batch Reports, RM Reports, Stocktake.",
            },
            {
                "title": "Sales sub-tabs",
                "body": "Under Sales: Orders, Overview, Customers, Products, Analytics, Import / Export, Settings.",
            },
            {
                "title": "Settings sub-tabs",
                "body": "Under Settings: Runtime Config, Units, Excise Rates, Purchase Formats, QC Tests, Work Areas, Conditions.",
            },
        ],
        tags=["navigation", "ui"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/app.py",
            "apps/vndmanuf_sales/ui/sales_tab.py",
            "app/ui/pages/settings_page.py",
        ],
    ),
    art(
        "API Connectivity and Demo Mode",
        slug="vndmanuf-api-connectivity",
        category_slug="vndmanuf",
        content_type="reference",
        summary="How the UI detects FastAPI availability and falls back to sample data.",
        purpose="Help users interpret the connectivity banner and know when data is live vs sample.",
        steps=[
            {
                "title": "Check the alert banner",
                "body": "On tab change the UI calls GET /health. If the API is unreachable, demo-mode-alert shows: 'Demo Mode: API server not available. Using sample data.'",
            },
            {
                "title": "Start the API",
                "body": "Ensure the FastAPI server is running on port 8000 before performing production operations.",
            },
            {
                "title": "Verify live data",
                "body": "When connected, the alert is hidden. API requests go to http://127.0.0.1:8000/api/v1.",
            },
        ],
        tags=["api", "demo-mode"],
        systems=["vndmanuf"],
        evidence=["app/ui/app.py"],
    ),
    # --- Products ---
    art(
        "Creating Products in VNDManuf",
        slug="vndmanuf-creating-products",
        category_slug="vndmanuf",
        summary="Create a new product record from Manufacturing → Products.",
        purpose="Establish SKU master data for inventory, formulas and sales.",
        prerequisites="Appropriate product type and unit definitions configured in Settings → Units.",
        steps=[
            {
                "title": "Open Products",
                "body": "Manufacturing → Products sub-tab (pages_enhanced layout).",
            },
            {
                "title": "Click Add Product",
                "body": "Use add-product-btn to open the product modal.",
            },
            {
                "title": "Enter identification",
                "body": "Complete fields including SKU (product-sku), name (product-name), description, EAN-13, and product type (RAW, WIP, FINISHED).",
            },
            {
                "title": "Set capabilities",
                "body": "Configure is_purchase, is_sell, is_assemble flags and related purchase/assembly/sales sections as required.",
            },
            {
                "title": "Save",
                "body": "Submit via the modal save action; the UI calls POST /api/v1/products/.",
            },
        ],
        risks=[
            {
                "issue": "Duplicate SKU",
                "prevention": "Search products-table before creating; SKU must be unique.",
            },
        ],
        troubleshooting="If save fails, check the toast notification for API validation errors.",
        tags=["products", "sku"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages_enhanced.py",
            "app/ui/products_callbacks.py",
            "app/api/products.py",
        ],
    ),
    art(
        "Editing and Duplicating Products",
        slug="vndmanuf-editing-products",
        category_slug="vndmanuf",
        summary="Modify or duplicate an existing product from the Products table.",
        purpose="Maintain accurate product master data over time.",
        steps=[
            {"title": "Select a row", "body": "Click a product in products-table."},
            {
                "title": "Edit",
                "body": "Use edit-product-btn to load the product into the modal; save calls PUT /api/v1/products/{id}.",
            },
            {
                "title": "Duplicate",
                "body": "Use duplicate-product-btn to copy an existing product as a starting point.",
            },
            {
                "title": "Delete",
                "body": "Use delete-product-btn where permitted; confirm before removing.",
            },
            {
                "title": "Refresh",
                "body": "Use products-refresh to reload from GET /api/v1/products/.",
            },
        ],
        tags=["products"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages_enhanced.py", "app/ui/products_callbacks.py"],
    ),
    art(
        "Product Capability Filters",
        slug="vndmanuf-product-filters",
        category_slug="vndmanuf",
        content_type="reference",
        summary="Filter the product list by purchase, sell and assemble capabilities.",
        purpose="Quickly find products by how they are used in the business.",
        steps=[
            {"title": "Open Products", "body": "Manufacturing → Products."},
            {
                "title": "Apply filters",
                "body": "Use filter-purchase, filter-sell, and filter-assemble toggles to narrow products-table.",
            },
            {
                "title": "Review results",
                "body": "Filtered rows reflect products matching the selected capability flags.",
            },
        ],
        tags=["products", "filters"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages_enhanced.py", "app/ui/products_callbacks.py"],
    ),
    art(
        "Adjusting Product Inventory from Products Page",
        slug="vndmanuf-product-inventory-adjust",
        category_slug="vndmanuf",
        summary="Adjust on-hand stock for a product from the product detail panel.",
        purpose="Correct inventory without a full stocktake when authorised.",
        steps=[
            {
                "title": "Select product",
                "body": "Open a product row to view product-detail-stock.",
            },
            {
                "title": "Adjust inventory",
                "body": "Click adjust-inventory-btn and enter the adjustment details.",
            },
            {
                "title": "Confirm API update",
                "body": "The callback posts to inventory movement endpoints under /api/v1/inventory/.",
            },
        ],
        tags=["inventory", "adjustment"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=[
            "app/ui/pages_enhanced.py",
            "app/ui/products_callbacks.py",
            "app/api/inventory.py",
        ],
    ),
    # --- Inventory ---
    art(
        "Inventory Lots Overview",
        slug="vndmanuf-inventory-lots",
        category_slug="vndmanuf",
        summary="View inventory lots from Manufacturing → Inventory.",
        purpose="Monitor lot-level stock held in the system.",
        steps=[
            {"title": "Open Inventory", "body": "Manufacturing → Inventory sub-tab."},
            {
                "title": "Refresh data",
                "body": "Click inventory-refresh to load GET /api/v1/inventory/lots.",
            },
            {
                "title": "Review inventory-table",
                "body": "Columns show lot codes, products, quantities and related lot metadata.",
            },
        ],
        tags=["inventory", "lots"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages.py", "app/api/inventory.py"],
    ),
    art(
        "Stock on Hand API and Product SOH",
        slug="vndmanuf-stock-on-hand",
        category_slug="vndmanuf",
        content_type="reference",
        summary="How stock-on-hand is retrieved per product and across products.",
        purpose="Support reconciliation between UI displays and API data.",
        steps=[
            {
                "title": "Single product SOH",
                "body": "GET /api/v1/inventory/product/{product_id}/soh returns stock for one product.",
            },
            {
                "title": "All products SOH",
                "body": "GET /api/v1/inventory/products/soh returns aggregated stock levels.",
            },
            {
                "title": "Product summary",
                "body": "GET /api/v1/inventory/product/{product_id}/summary provides inventory summary for a product.",
            },
        ],
        tags=["inventory", "soh", "api"],
        systems=["vndmanuf"],
        evidence=["app/api/inventory.py"],
    ),
    art(
        "Conducting a Stocktake in VNDManuf",
        slug="vndmanuf-stocktake-procedure",
        category_slug="vndmanuf",
        summary="Run a physical stocktake using Manufacturing → Stocktake.",
        purpose="Reconcile system inventory with counted quantities and post adjustments.",
        steps=[
            {"title": "Open Stocktake", "body": "Manufacturing → Stocktake."},
            {
                "title": "Set session details",
                "body": "Enter stocktake-date, stocktake-ref, and stocktake-counter.",
            },
            {
                "title": "Load sheet",
                "body": "Click stocktake-start to fetch GET /api/v1/inventory/stocktake/sheet.",
            },
            {
                "title": "Enter counts",
                "body": "Edit counted quantities in stocktake-table (editable Counted Qty column).",
            },
            {
                "title": "Calculate variances",
                "body": "Use stocktake-calc to compute differences.",
            },
            {
                "title": "Apply adjustments",
                "body": "Use stocktake-update to POST /api/v1/inventory/stocktake and create adjustment movements.",
            },
            {
                "title": "Import/export",
                "body": "Optional: stocktake-import and stocktake-export for spreadsheet workflows.",
            },
        ],
        risks=[
            {
                "issue": "Posting before review",
                "prevention": "Calculate variances and investigate large deltas first.",
            },
        ],
        tags=["stocktake", "inventory"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages/stocktake_page.py",
            "app/ui/stocktake_callbacks.py",
            "app/api/inventory.py",
        ],
    ),
    art(
        "Inventory Movements and Adjustments",
        slug="vndmanuf-inventory-movements",
        category_slug="vndmanuf",
        content_type="reference",
        summary="API endpoints for recording inventory movements and adjustments.",
        purpose="Document how stock changes are persisted outside stocktake.",
        steps=[
            {
                "title": "Review movement endpoints",
                "body": "POST endpoints under /api/v1/inventory/ record movements (see inventory.py for receipt, issue, adjustment routes).",
            },
            {
                "title": "Link to work orders",
                "body": "Material issues from work orders also affect inventory via work order issue endpoints.",
            },
            {
                "title": "Verify lot balances",
                "body": "After movements, confirm lots via GET /api/v1/inventory/lots or product lots endpoint.",
            },
        ],
        tags=["inventory", "movements"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=["app/api/inventory.py", "app/api/work_orders.py"],
    ),
    art(
        "RM Reports — Usage, Valuation and Reorder",
        slug="vndmanuf-rm-reports",
        category_slug="vndmanuf",
        summary="Raw material reporting from Manufacturing → RM Reports.",
        purpose="Analyse usage, stock valuation and reorder requirements.",
        steps=[
            {"title": "Open RM Reports", "body": "Manufacturing → RM Reports."},
            {
                "title": "Select report type",
                "body": "Choose rm-report-type: Usage Report, Stock Valuation, or Reorder Analysis.",
            },
            {
                "title": "Generate",
                "body": "Reports call /api/v1/reports/raw-materials/usage, /reports/stock-valuation, and /reports/reorder-analysis.",
            },
        ],
        tags=["reports", "raw-materials"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages/rm_reports_page.py", "app/api/reports.py"],
    ),
    # --- Assemblies / Formulas ---
    art(
        "Managing Assemblies (Formulas)",
        slug="vndmanuf-assemblies-formulas",
        category_slug="vndmanuf",
        summary="Create and maintain assembly formulas under Manufacturing → Assemblies.",
        purpose="Define bill-of-materials and formula revisions for production.",
        steps=[
            {
                "title": "Open Assemblies",
                "body": "Manufacturing → Assemblies (FormulasPage).",
            },
            {
                "title": "Search formulas",
                "body": "Use formula-search-btn to find existing formulas.",
            },
            {
                "title": "Add or edit",
                "body": "formula-add-btn / formula-edit-btn open the formula editor.",
            },
            {
                "title": "Manage revisions",
                "body": "formula-revision-btn and formula-clone-btn manage formula versions.",
            },
            {
                "title": "Print",
                "body": "formula-print-btn generates printable formula output.",
            },
            {
                "title": "Manage lines",
                "body": "Add, edit and delete formula component lines; API: /api/v1/formulas/.",
            },
        ],
        tags=["formulas", "assemblies", "bom"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages/formulas_page.py",
            "app/ui/formulas_callbacks.py",
            "app/api/formulas.py",
        ],
    ),
    art(
        "Assembly and Disassembly Operations",
        slug="vndmanuf-assembly-operations",
        category_slug="vndmanuf",
        summary="Execute assemble and disassemble operations via the assemblies API.",
        purpose="Convert components into finished/WIP products or break them down.",
        steps=[
            {
                "title": "Verify formula",
                "body": "Confirm the active formula revision and component availability.",
            },
            {
                "title": "Assemble",
                "body": "POST /api/v1/assemblies/assemble with product, quantity and formula reference.",
            },
            {
                "title": "Disassemble",
                "body": "POST /api/v1/assemblies/disassemble to reverse an assembly where supported.",
            },
            {
                "title": "Verify inventory",
                "body": "Check lot balances after the operation completes.",
            },
        ],
        tags=["assemblies", "inventory"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=["app/api/assemblies.py"],
    ),
    art(
        "Batch Processing Page Status",
        slug="vndmanuf-batch-processing-status",
        category_slug="vndmanuf",
        content_type="reference",
        status="draft",
        summary="The Batch Processing sub-tab is currently a placeholder in the UI.",
        purpose="Set expectations for operators looking for batch processing screens.",
        steps=[
            {
                "title": "Navigate to Batch Processing",
                "body": "Manufacturing → Batch Processing.",
            },
            {
                "title": "Current behaviour",
                "body": "BatchProcessingPage displays 'This page is currently unavailable.'",
            },
            {
                "title": "Alternative workflows",
                "body": "Use Work Orders and Batches API (/api/v1/batches/) for batch-related operations until UI is implemented.",
            },
        ],
        tags=["batch", "placeholder"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages/batch_processing_page.py", "app/api/batches.py"],
    ),
    # --- Work Orders ---
    art(
        "Work Orders Overview",
        slug="vndmanuf-work-orders-overview",
        category_slug="vndmanuf",
        summary="Navigate and filter work orders in Manufacturing → Work Orders.",
        purpose="Plan and track production jobs through their lifecycle.",
        steps=[
            {"title": "Open Work Orders", "body": "Manufacturing → Work Orders."},
            {
                "title": "Use sub-tabs",
                "body": "List, Detail, Rate Manager, and Batch Lookup.",
            },
            {
                "title": "Filter list",
                "body": "Apply wo-status-filter, wo-product-filter, wo-date-from, wo-date-to on wo-list-table.",
            },
            {
                "title": "Create",
                "body": "Use wo-create-btn to start a new work order (POST /api/v1/work-orders/).",
            },
        ],
        tags=["work-orders", "production"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages/work_orders_page.py", "app/api/work_orders.py"],
    ),
    art(
        "Work Order Status Lifecycle",
        slug="vndmanuf-work-order-lifecycle",
        category_slug="vndmanuf",
        summary="Release, start, complete, reopen and void work orders.",
        purpose="Ensure production jobs follow the correct status transitions.",
        steps=[
            {
                "title": "Draft / Hold",
                "body": "New work orders start in Draft; may be placed on Hold.",
            },
            {
                "title": "Release",
                "body": "wo-release-btn → POST /work-orders/{id}/release moves to Released.",
            },
            {
                "title": "Start",
                "body": "wo-start-btn → POST /work-orders/{id}/start moves to In Progress.",
            },
            {
                "title": "Complete",
                "body": "Enter wo-complete-qty and submit wo-complete-submit-btn → POST /work-orders/{id}/complete.",
            },
            {
                "title": "Reopen",
                "body": "wo-reopen-btn → POST /work-orders/{id}/reopen from Complete.",
            },
            {
                "title": "Void",
                "body": "wo-void-btn → POST /work-orders/{id}/void cancels the job.",
            },
        ],
        risks=[
            {
                "issue": "Starting without release",
                "prevention": "Follow Release before Start sequence.",
            },
        ],
        tags=["work-orders", "status"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/work_orders_callbacks.py",
            "app/api/work_orders.py",
            "app/ui/pages/work_orders_page.py",
        ],
    ),
    art(
        "Issuing Materials to Work Orders",
        slug="vndmanuf-work-order-material-issue",
        category_slug="vndmanuf",
        summary="Record material consumption against a work order.",
        purpose="Maintain accurate batch traceability and inventory deductions.",
        steps=[
            {
                "title": "Open work order detail",
                "body": "Select a work order and open the Detail sub-tab.",
            },
            {
                "title": "Inputs tab",
                "body": "Use wo-detail-tabs → Inputs to manage material issues.",
            },
            {
                "title": "Issue materials",
                "body": "Submit issues via wo-issue-submit-btn → POST /work-orders/{id}/issues.",
            },
            {
                "title": "Verify genealogy",
                "body": "Check Genealogy tab; API GET /work-orders/{id}/genealogy.",
            },
        ],
        tags=["work-orders", "materials", "traceability"],
        systems=["vndmanuf"],
        evidence=["app/ui/work_orders_callbacks.py", "app/api/work_orders.py"],
    ),
    art(
        "Work Order QC Tests",
        slug="vndmanuf-work-order-qc",
        category_slug="vndmanuf",
        summary="Record quality test results on a work order.",
        purpose="Document QC before batch release.",
        steps=[
            {
                "title": "Configure test types",
                "body": "Settings → QC Tests defines available qc test types.",
            },
            {
                "title": "Open QC tab",
                "body": "Work order Detail → QC Tests (wo-detail-tabs).",
            },
            {
                "title": "Record results",
                "body": "Enter test values against configured QC test types for the work order.",
            },
            {
                "title": "API reference",
                "body": "GET /work-orders/qc-test-types lists types; QC results stored on work order.",
            },
        ],
        tags=["qc", "work-orders"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=[
            "app/ui/work_orders_callbacks.py",
            "app/api/work_orders.py",
            "app/ui/qc_test_types_callbacks.py",
        ],
    ),
    art(
        "Work Order Costs and Overheads",
        slug="vndmanuf-work-order-costs",
        category_slug="vndmanuf",
        summary="View costs and add overheads to work orders.",
        purpose="Support production costing and margin analysis.",
        steps=[
            {
                "title": "Costs tab",
                "body": "Work order Detail → Costs shows cost breakdown.",
            },
            {
                "title": "View costs API",
                "body": "GET /work-orders/{id}/costs returns WorkOrderCostResponse.",
            },
            {
                "title": "Add overheads",
                "body": "POST /work-orders/{id}/overheads records overhead lines.",
            },
            {
                "title": "Rate Manager",
                "body": "Work Orders → Rate Manager sub-tab manages cost rates.",
            },
        ],
        tags=["costing", "work-orders"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages/work_orders_page.py", "app/api/work_orders.py"],
    ),
    art(
        "Work Order Planned Quantity Adjustment",
        slug="vndmanuf-work-order-planned-qty",
        category_slug="vndmanuf",
        summary="Adjust planned output quantity on a work order.",
        purpose="Correct planning quantities before or during production.",
        steps=[
            {"title": "Open detail", "body": "Select work order in Detail sub-tab."},
            {
                "title": "Edit planned qty",
                "body": "Enter value in wo-planned-qty-input when editing is allowed (wo-detail-allow-input-edit).",
            },
            {
                "title": "Save",
                "body": "Click wo-planned-qty-save to PATCH the work order.",
            },
        ],
        tags=["work-orders"],
        systems=["vndmanuf"],
        evidence=["app/ui/work_orders_callbacks.py", "app/ui/app.py"],
    ),
    art(
        "Batch Reports in VNDManuf",
        slug="vndmanuf-batch-reports",
        category_slug="vndmanuf",
        summary="Review batch history and variance from Manufacturing → Batch Reports.",
        purpose="Analyse production batch performance over time.",
        steps=[
            {"title": "Open Batch Reports", "body": "Manufacturing → Batch Reports."},
            {
                "title": "Set filters",
                "body": "Select batch-report-year and batch-report-formula.",
            },
            {
                "title": "Review tables",
                "body": "Variance and history tables load from /api/v1/reports/batch-history.",
            },
        ],
        tags=["batch", "reports"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages/batch_reports_page.py",
            "app/api/reports.py",
            "app/api/batches.py",
        ],
    ),
    # --- Contacts ---
    art(
        "Managing Contacts",
        slug="vndmanuf-contacts-management",
        category_slug="vndmanuf",
        summary="Create and maintain customer and supplier contacts.",
        purpose="Centralise trading partner data for sales and purchasing.",
        steps=[
            {"title": "Open Contacts", "body": "Main tab → Contacts."},
            {
                "title": "Search",
                "body": "Use contacts-search-btn and contacts-clear-btn.",
            },
            {
                "title": "Add contact",
                "body": "contacts-add-btn opens modal with contacts-form-* fields.",
            },
            {
                "title": "Edit / delete",
                "body": "contacts-edit-btn and contacts-delete-btn; API /api/v1/contacts/.",
            },
            {
                "title": "Set roles",
                "body": "Mark is_customer, is_supplier flags; link xero_contact_id where applicable.",
            },
        ],
        tags=["contacts", "customers", "suppliers"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages/contacts_page.py",
            "app/ui/contacts_callbacks.py",
            "app/api/contacts.py",
        ],
    ),
    # --- Sales ---
    art(
        "Sales Orders List and Filters",
        slug="vndmanuf-sales-orders-list",
        category_slug="vndmanuf",
        summary="Browse and filter sales orders under Sales → Orders.",
        purpose="Find and open orders for fulfilment and invoicing.",
        steps=[
            {
                "title": "Open Sales → Orders",
                "body": "Main tab Sales; default sub-tab Orders.",
            },
            {
                "title": "Apply filters",
                "body": "Use sales-orders-customer-filter, sales-orders-channel-filter, sales-orders-status-filter, sales-orders-type-filter, and date range filters.",
            },
            {
                "title": "Review tables",
                "body": "sales-orders-table lists orders; product summary table shows line aggregates.",
            },
            {
                "title": "Refresh",
                "body": "sales-orders-refresh reloads from /api/v1/sales/orders.",
            },
        ],
        tags=["sales", "orders"],
        systems=["vndmanuf"],
        evidence=[
            "apps/vndmanuf_sales/ui/pages/orders.py",
            "apps/vndmanuf_sales/ui/orders_callbacks.py",
        ],
    ),
    art(
        "Creating a Sales Order",
        slug="vndmanuf-sales-create-order",
        category_slug="vndmanuf",
        summary="Create a new sales order from Sales → Orders.",
        purpose="Capture customer orders for dispatch and invoicing.",
        steps=[
            {"title": "New order", "body": "Click sales-orders-new-order-btn."},
            {
                "title": "Complete header",
                "body": "Fill sales-order-form-* fields: customer, channel, dates, delivery details.",
            },
            {
                "title": "Add lines",
                "body": "Enter products, quantities and pricing in the order line table.",
            },
            {
                "title": "Submit",
                "body": "sales-order-form-submit → POST /api/v1/sales/orders.",
            },
        ],
        tags=["sales", "orders"],
        systems=["vndmanuf"],
        evidence=["apps/vndmanuf_sales/ui/orders_callbacks.py", "app/api/sales.py"],
    ),
    art(
        "Converting Orders to Delivery Dockets",
        slug="vndmanuf-sales-convert-delivery",
        category_slug="vndmanuf",
        summary="Convert a confirmed sales order to a delivery docket.",
        purpose="Create dispatch documentation linked to the sales order.",
        steps=[
            {
                "title": "Open order",
                "body": "Select order and open detail modal (sales-orders-open-selected).",
            },
            {
                "title": "Convert",
                "body": "Click sales-order-convert-delivery → POST /sales/orders/{id}/convert-to-delivery.",
            },
            {
                "title": "Print docket PDF",
                "body": "sales-order-print-delivery generates Delivery_Docket.docx via POST /documents/generate.",
            },
            {
                "title": "Picking list",
                "body": "sales-order-print-picking-list prints picking documentation.",
            },
        ],
        tags=["delivery", "sales"],
        systems=["vndmanuf"],
        evidence=[
            "apps/vndmanuf_sales/ui/orders_callbacks.py",
            "app/api/sales.py",
            "app/api/documents.py",
        ],
    ),
    art(
        "Converting Orders to Invoices",
        slug="vndmanuf-sales-convert-invoice",
        category_slug="vndmanuf",
        summary="Convert a sales order to an invoice record.",
        purpose="Bill customers and sync to finance systems.",
        steps=[
            {"title": "Open order", "body": "Select order in Sales → Orders."},
            {
                "title": "Convert to invoice",
                "body": "sales-order-convert-invoice → POST /sales/orders/{id}/convert-to-invoice.",
            },
            {
                "title": "Print invoice PDF",
                "body": "sales-order-print-invoice uses Invoice.docx template via /documents/generate.",
            },
            {
                "title": "Mark paid",
                "body": "Invoice payment tracked via sales invoice endpoints.",
            },
        ],
        tags=["invoice", "sales"],
        systems=["vndmanuf", "xero"],
        confidence="medium",
        evidence=[
            "apps/vndmanuf_sales/ui/orders_callbacks.py",
            "app/api/sales.py",
            "app/api/documents.py",
        ],
    ),
    art(
        "Sales Customers Dashboard",
        slug="vndmanuf-sales-customers",
        category_slug="vndmanuf",
        summary="View customer KPIs and manage delivery sites under Sales → Customers.",
        purpose="Monitor customer base and site-level delivery data.",
        steps=[
            {"title": "Open Customers", "body": "Sales → Customers sub-tab."},
            {
                "title": "Review KPIs",
                "body": "sales-customers-total, sales-customers-new, sales-customers-lifetime, sales-customers-last-order.",
            },
            {
                "title": "Browse customers",
                "body": "sales-customers-table from GET /sales/customers/dashboard.",
            },
            {
                "title": "Manage sites",
                "body": "sales-customer-sites-table; add sites via sales-add-site-* form → POST /sales/customer-sites.",
            },
        ],
        tags=["customers", "sales"],
        systems=["vndmanuf"],
        evidence=[
            "apps/vndmanuf_sales/ui/pages/customers.py",
            "apps/vndmanuf_sales/ui/customers_callbacks.py",
        ],
    ),
    art(
        "Sales Import and Export",
        slug="vndmanuf-sales-import-export",
        category_slug="vndmanuf",
        summary="Import and export sales data from Sales → Import / Export.",
        purpose="Bulk load orders or extract sales data.",
        steps=[
            {
                "title": "Open Import / Export",
                "body": "Sales → Import / Export sub-tab.",
            },
            {
                "title": "Follow on-screen controls",
                "body": "Import callbacks register via register_sales_import_callbacks.",
            },
            {
                "title": "API import",
                "body": "CSV import available via sales API import endpoints.",
            },
        ],
        tags=["import", "sales"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=["apps/vndmanuf_sales/ui/import_callbacks.py", "app/api/sales.py"],
    ),
    art(
        "Pricebooks and Sales Channels Settings",
        slug="vndmanuf-sales-settings",
        category_slug="vndmanuf",
        summary="Configure sales channels, pricebooks and tags under Sales → Settings.",
        purpose="Control pricing structures and channel-specific behaviour.",
        steps=[
            {"title": "Open Sales Settings", "body": "Sales → Settings sub-tab."},
            {
                "title": "Channels",
                "body": "CRUD /api/v1/sales/channels (archive/unarchive supported).",
            },
            {
                "title": "Pricebooks",
                "body": "CRUD /api/v1/sales/pricebooks and pricebook lines.",
            },
            {
                "title": "Tags",
                "body": "Manage /api/v1/sales/tags for order classification.",
            },
        ],
        tags=["pricing", "channels"],
        systems=["vndmanuf"],
        evidence=["apps/vndmanuf_sales/ui/sales_tab.py", "app/api/sales.py"],
    ),
    # --- CRM ---
    art(
        "CRM Customer Workspace",
        slug="vndmanuf-crm-workspace",
        category_slug="vndmanuf",
        summary="Use the CRM tab to manage customer relationships.",
        purpose="Centralise sales history, activities and customer profile data.",
        steps=[
            {"title": "Open CRM", "body": "Main tab → CRM (separate from Sales tab)."},
            {
                "title": "Select rep and customer",
                "body": "Use crm-active-rep, crm-account-scope, crm-customer-select.",
            },
            {"title": "Date range", "body": "Filter with crm-date-range."},
            {
                "title": "Workspace tabs",
                "body": "Sales, Timeline, Profile, Sites, People (crm-workspace-tabs).",
            },
        ],
        tags=["crm"],
        systems=["vndmanuf"],
        evidence=[
            "apps/vndmanuf_sales/ui/pages/crm.py",
            "apps/vndmanuf_sales/ui/crm_callbacks.py",
        ],
    ),
    art(
        "CRM Timeline and Activity Logging",
        slug="vndmanuf-crm-activities",
        category_slug="vndmanuf",
        summary="Log calls, visits, notes and emails in CRM Timeline.",
        purpose="Preserve customer interaction history for the sales team.",
        steps=[
            {"title": "Open Timeline", "body": "CRM workspace → Timeline tab."},
            {
                "title": "Capture activity",
                "body": "Use crm-note-type, crm-note-category, crm-note-body fields.",
            },
            {
                "title": "Submit",
                "body": "Activity saved via POST /api/v1/crm/customers/{id}/activities.",
            },
            {
                "title": "Review feed",
                "body": "Timeline displays chronological activity history.",
            },
        ],
        tags=["crm", "activities"],
        systems=["vndmanuf"],
        evidence=["apps/vndmanuf_sales/ui/crm_callbacks.py", "app/api/crm.py"],
    ),
    art(
        "CRM Staff and Sites Management",
        slug="vndmanuf-crm-staff-sites",
        category_slug="vndmanuf",
        summary="Manage customer sites and on-site staff in CRM.",
        purpose="Track delivery locations and key contacts at customer premises.",
        steps=[
            {"title": "Sites tab", "body": "CRM workspace → Sites."},
            {
                "title": "People tab",
                "body": "CRM workspace → People; crm-staff-table lists staff.",
            },
            {
                "title": "Add staff",
                "body": "Use crm-add-staff-* form → POST /crm/customers/{id}/staff.",
            },
            {
                "title": "Sites API",
                "body": "Linked to /sales/customer-sites and CRM profile endpoints.",
            },
        ],
        tags=["crm", "staff"],
        systems=["vndmanuf"],
        evidence=["apps/vndmanuf_sales/ui/pages/crm.py", "app/api/crm.py"],
    ),
    art(
        "CRM PDF Export",
        slug="vndmanuf-crm-export-pdf",
        category_slug="vndmanuf",
        summary="Export customer CRM data to PDF.",
        purpose="Share customer profiles and activity summaries.",
        steps=[
            {"title": "Select customer", "body": "Choose customer in CRM toolbar."},
            {
                "title": "Choose sections",
                "body": "Select crm-export-sections checkboxes.",
            },
            {
                "title": "Export",
                "body": "crm-export-btn → POST /crm/customers/{id}/export-pdf.",
            },
        ],
        tags=["crm", "export"],
        systems=["vndmanuf"],
        evidence=["apps/vndmanuf_sales/ui/crm_callbacks.py", "app/api/crm.py"],
    ),
    # --- Documents ---
    art(
        "Generating Delivery Docket and Invoice PDFs",
        slug="vndmanuf-document-generation",
        category_slug="vndmanuf",
        summary="Generate PDF documents from Word templates via the documents API.",
        purpose="Produce customer-facing delivery dockets and invoices.",
        steps=[
            {
                "title": "Trigger from sales",
                "body": "Sales order modal print buttons call document generation.",
            },
            {
                "title": "API call",
                "body": "POST /api/v1/documents/generate with template_name (Delivery_Docket.docx or Invoice.docx), doc_type, and entity IDs.",
            },
            {
                "title": "Download",
                "body": "GET /documents/{id}/download returns the generated file.",
            },
            {
                "title": "Async jobs",
                "body": "Optional async_job with GET /documents/jobs/{job_id} when RQ/Redis configured.",
            },
        ],
        tags=["documents", "pdf"],
        systems=["vndmanuf"],
        evidence=[
            "app/api/documents.py",
            "apps/vndmanuf_sales/ui/orders_callbacks.py",
            "templates/Delivery_Docket.docx",
        ],
    ),
    # --- Settings ---
    art(
        "Settings — Units of Measure",
        slug="vndmanuf-settings-units",
        category_slug="vndmanuf",
        summary="Manage units and conversions under Settings → Units.",
        purpose="Ensure consistent quantity handling across products and formulas.",
        steps=[
            {"title": "Open Settings → Units", "body": "Settings tab → Units sub-tab."},
            {
                "title": "Manage units",
                "body": "CRUD via /api/v1/units/ including /convert and /convert/alcohol.",
            },
        ],
        tags=["units", "settings"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/units_callbacks.py",
            "app/api/units.py",
            "app/ui/pages/settings_page.py",
        ],
    ),
    art(
        "Settings — Excise Rates",
        slug="vndmanuf-settings-excise-rates",
        category_slug="vndmanuf",
        summary="Configure excise rates under Settings → Excise Rates.",
        purpose="Support excise calculations on applicable products.",
        steps=[
            {"title": "Open Excise Rates", "body": "Settings → Excise Rates."},
            {
                "title": "Manage rates",
                "body": "CRUD /api/v1/excise-rates/; GET /excise-rates/current for active rate.",
            },
        ],
        tags=["excise", "settings"],
        systems=["vndmanuf"],
        evidence=["app/ui/excise_rates_callbacks.py", "app/api/excise_rates.py"],
    ),
    art(
        "Settings — Work Areas and QC Tests",
        slug="vndmanuf-settings-work-areas-qc",
        category_slug="vndmanuf",
        summary="Configure work areas and QC test types.",
        purpose="Support work order routing and quality recording.",
        steps=[
            {
                "title": "Work Areas",
                "body": "Settings → Work Areas; CRUD /api/v1/work-areas/.",
            },
            {
                "title": "QC Tests",
                "body": "Settings → QC Tests; qc-test-types-table managed by qc_test_types_callbacks.",
            },
        ],
        tags=["settings", "qc"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/work_areas_callbacks.py",
            "app/ui/qc_test_types_callbacks.py",
        ],
    ),
    # --- Shopify ---
    art(
        "Shopify Webhook Integration",
        slug="vndmanuf-shopify-webhooks",
        category_slug="shopify",
        summary="Shopify order and fulfilment webhooks processed by the API.",
        purpose="Sync e-commerce orders into VNDManuf inventory and sales.",
        prerequisites="Shopify webhook secret configured; API publicly reachable.",
        steps=[
            {
                "title": "Orders create",
                "body": "POST /api/v1/shopify/webhooks/orders_create — HMAC verified; creates inventory reservations.",
            },
            {
                "title": "Fulfillments",
                "body": "POST /shopify/webhooks/fulfillments_create commits reservations.",
            },
            {
                "title": "Cancellations/refunds",
                "body": "Additional webhook handlers for cancel and refund events.",
            },
        ],
        tags=["shopify", "webhooks"],
        systems=["vndmanuf", "shopify"],
        evidence=["app/api/shopify.py", "app/services/shopify_sync.py"],
    ),
    art(
        "Shopify Order Import and Inventory Push",
        slug="vndmanuf-shopify-sync",
        category_slug="shopify",
        summary="Manual and scheduled Shopify sync operations.",
        purpose="Import orders and push inventory levels to Shopify.",
        steps=[
            {
                "title": "Import orders",
                "body": "POST /shopify/orders/import-historical and /orders/import-incremental.",
            },
            {
                "title": "Push inventory",
                "body": "POST /shopify/sync/push/{product_id} or /sync/push-all.",
            },
            {
                "title": "UI status",
                "body": "[VERIFY WITH OPERATOR] shopify_page.py exists but is not wired into main navigation — operations may be API/cron only (scripts/cron_reconcile_shopify.py).",
            },
        ],
        tags=["shopify", "sync"],
        systems=["vndmanuf", "shopify"],
        confidence="medium",
        evidence=[
            "app/api/shopify.py",
            "app/ui/pages/shopify_page.py",
            "scripts/cron_reconcile_shopify.py",
        ],
    ),
    # --- Reports tab ---
    art(
        "Reports Tab — Current Limitations",
        slug="vndmanuf-reports-tab-status",
        category_slug="vndmanuf",
        content_type="reference",
        status="draft",
        summary="The main Reports tab UI is a placeholder; detailed reports live in Manufacturing sub-tabs.",
        purpose="Direct users to working report modules.",
        steps=[
            {"title": "Open Reports tab", "body": "Main tab → Reports."},
            {
                "title": "Current UI",
                "body": "report-type, report-start-date, report-end-date, generate-report-btn return placeholder text.",
            },
            {
                "title": "Working alternatives",
                "body": "Use Manufacturing → Batch Reports, RM Reports, and Sales → Analytics for live reporting.",
            },
        ],
        tags=["reports"],
        systems=["vndmanuf"],
        evidence=["app/ui/pages.py", "app/ui/app.py", "app/api/reports.py"],
    ),
    # --- Nova U ---
    art(
        "Nova U — Browsing and Searching Articles",
        slug="vndmanuf-nova-u-search",
        category_slug="vndmanuf",
        summary="Find training articles in the Nova U tab.",
        purpose="Locate SOPs and guides quickly.",
        steps=[
            {"title": "Open Nova U", "body": "Main tab → Nova U."},
            {
                "title": "Search",
                "body": "Enter nu-search-input and click nu-search-btn; optional nu-clear-btn.",
            },
            {
                "title": "Filter",
                "body": "Use nu-system-filter, nu-type-filter, nu-status-filter.",
            },
            {
                "title": "Browse categories",
                "body": "Select a node in nu-category-tree.",
            },
        ],
        tags=["nova-u", "search"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages/training_page.py",
            "app/ui/training_callbacks.py",
            "app/api/training.py",
        ],
    ),
    art(
        "Nova U — Creating and Editing Articles",
        slug="vndmanuf-nova-u-editor",
        category_slug="vndmanuf",
        summary="Create or edit training articles in the Nova U editor modal.",
        purpose="Author and maintain SOP content.",
        steps=[
            {"title": "New article", "body": "Click nu-new-article-btn."},
            {
                "title": "Complete metadata",
                "body": "nu-editor-title, nu-editor-content-type (sop/guide/checklist/reference), nu-editor-category, nu-editor-status, nu-editor-systems, nu-editor-summary.",
            },
            {
                "title": "SOP tab",
                "body": "Fill nu-editor-purpose, prerequisites, safety, steps, risks, troubleshooting, body.",
            },
            {
                "title": "Links tab",
                "body": "nu-editor-tags, nu-editor-loom-url, nu-editor-sharepoint-url.",
            },
            {
                "title": "Rich content",
                "body": "nu-rich-editor-surface with toolbar; optional nu-editor-video-embed.",
            },
            {
                "title": "Save",
                "body": "nu-editor-save-btn → POST or PUT /api/v1/training/articles.",
            },
        ],
        tags=["nova-u", "authoring"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages/training_page.py",
            "app/ui/training_callbacks.py",
            "app/api/training.py",
        ],
    ),
    art(
        "Nova U — Publishing Articles",
        slug="vndmanuf-nova-u-publishing",
        category_slug="vndmanuf",
        summary="Change article visibility using the status field.",
        purpose="Control which articles appear in published searches and corpus export.",
        steps=[
            {
                "title": "Edit article",
                "body": "Open editor via nu-edit-article-btn or card edit button.",
            },
            {
                "title": "Set status",
                "body": "nu-editor-status: Draft, Published, or Archived.",
            },
            {
                "title": "Save",
                "body": "Published articles appear in default list/search (status_filter=published).",
            },
            {
                "title": "Archive via API",
                "body": "DELETE /training/articles/{ref} sets status to archived (no delete button in UI).",
            },
        ],
        tags=["nova-u", "publishing"],
        systems=["vndmanuf"],
        evidence=["app/ui/training_callbacks.py", "app/api/training.py"],
    ),
    art(
        "Nova U — LLM Corpus Export",
        slug="vndmanuf-nova-u-corpus-export",
        category_slug="vndmanuf",
        content_type="reference",
        summary="Export the training corpus for RAG and in-house LLM indexing.",
        purpose="Provide machine-readable training content.",
        steps=[
            {
                "title": "JSON export",
                "body": "Header link 'LLM Corpus (JSON)' → GET /api/v1/training/corpus.",
            },
            {
                "title": "Markdown export",
                "body": "'LLM Corpus (MD)' → GET /api/v1/training/corpus?format=markdown.",
            },
            {
                "title": "Single article",
                "body": "GET /training/corpus/{slug} returns llm_context block.",
            },
        ],
        tags=["nova-u", "llm", "corpus"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/pages/training_page.py",
            "app/api/training.py",
            "app/training/service.py",
        ],
    ),
    art(
        "Nova U — Media Upload for Rich Content",
        slug="vndmanuf-nova-u-media-upload",
        category_slug="vndmanuf",
        summary="Upload images and videos for embedding in training articles.",
        purpose="Support visual training content.",
        steps=[
            {
                "title": "Upload",
                "body": "POST /api/v1/training/media/upload (max 80 MB; jpeg/png/gif/webp/mp4/webm/mov).",
            },
            {
                "title": "Serve",
                "body": "Returned URL /api/v1/training/media/{filename}.",
            },
            {
                "title": "Embed",
                "body": "Insert into nu-rich-editor-surface or set nu-editor-video-embed for Loom/YouTube/Vimeo.",
            },
        ],
        tags=["nova-u", "media"],
        systems=["vndmanuf"],
        evidence=["app/api/training.py", "app/training/service.py"],
    ),
    art(
        "Batches API — Create and Finish",
        slug="vndmanuf-batches-api",
        category_slug="vndmanuf",
        summary="Production batch records via /api/v1/batches/ (UI placeholder exists).",
        purpose="Record batch production outcomes when not using work orders alone.",
        steps=[
            {
                "title": "Create batch",
                "body": "POST /api/v1/batches/ with work order and product references.",
            },
            {
                "title": "Record actuals",
                "body": "PUT endpoints for record-actual and qc-results on batch ID.",
            },
            {
                "title": "Finish batch",
                "body": "POST /batches/{id}/finish completes the batch.",
            },
            {
                "title": "Print ticket",
                "body": "GET /batches/{id}/print returns batch ticket text.",
            },
            {
                "title": "History",
                "body": "GET /batches/history/ for batch history listing.",
            },
        ],
        tags=["batches", "api"],
        systems=["vndmanuf"],
        evidence=["app/api/batches.py", "app/ui/pages/batch_processing_page.py"],
    ),
    art(
        "Settings — Purchase Formats",
        slug="vndmanuf-settings-purchase-formats",
        category_slug="vndmanuf",
        summary="Configure how purchased quantities are expressed.",
        purpose="Standardise purchase unit formats for raw materials.",
        steps=[
            {"title": "Open Purchase Formats", "body": "Settings → Purchase Formats."},
            {
                "title": "Manage formats",
                "body": "CRUD via purchase_formats_callbacks → /api/v1/purchase-formats/.",
            },
        ],
        tags=["settings", "purchasing"],
        systems=["vndmanuf"],
        evidence=[
            "app/ui/purchase_formats_callbacks.py",
            "app/api/purchase_formats.py",
        ],
    ),
    art(
        "Settings — Condition Types and Hazard Codes",
        slug="vndmanuf-settings-conditions",
        category_slug="vndmanuf",
        summary="Manage hazard codes and condition types.",
        purpose="Classify products for safety and compliance display.",
        steps=[
            {
                "title": "Open Conditions",
                "body": "Settings → Conditions sub-tab (condition_types_page).",
            },
            {"title": "Hazard tab", "body": "Hazard Codes tab (tab_id hazard)."},
            {
                "title": "Condition types",
                "body": "Condition Types tab (tab_id condition).",
            },
        ],
        tags=["settings", "hazard"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=["app/ui/pages/condition_types_page.py"],
    ),
    art(
        "Sales Order Backorders",
        slug="vndmanuf-sales-backorders",
        category_slug="vndmanuf",
        summary="Create backorders from sales orders when stock is insufficient.",
        purpose="Track unfulfilled line quantities separately.",
        steps=[
            {
                "title": "Identify short lines",
                "body": "Review order lines with insufficient stock.",
            },
            {
                "title": "Create backorder",
                "body": "POST /api/v1/sales/orders/{id}/backorder.",
            },
            {
                "title": "Track fulfilment",
                "body": "Monitor order status transitions (draft, confirmed, fulfilled, cancelled).",
            },
        ],
        tags=["sales", "backorder"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=["app/api/sales.py"],
    ),
    art(
        "Delivery Docket Updates",
        slug="vndmanuf-delivery-docket-edit",
        category_slug="vndmanuf",
        summary="View and patch delivery docket records after conversion.",
        purpose="Correct dispatch documentation before PDF generation.",
        steps=[
            {
                "title": "Retrieve docket",
                "body": "GET /api/v1/sales/delivery-dockets/{id}.",
            },
            {
                "title": "Update fields",
                "body": "PATCH /sales/delivery-dockets/{id} for line quantities and metadata.",
            },
            {
                "title": "Regenerate PDF",
                "body": "Re-run document generation from Sales order print controls.",
            },
        ],
        tags=["delivery", "docket"],
        systems=["vndmanuf"],
        evidence=["app/api/sales.py", "app/api/documents.py"],
    ),
    art(
        "Buying Groups and Sales Reps",
        slug="vndmanuf-buying-groups-reps",
        category_slug="vndmanuf",
        content_type="reference",
        summary="CRM supporting master data for buying groups and sales representatives.",
        purpose="Classify customers and attribute CRM activities to reps.",
        steps=[
            {
                "title": "Sales reps",
                "body": "CRUD /api/v1/sales-reps/; selected in CRM via crm-active-rep.",
            },
            {
                "title": "Buying groups",
                "body": "CRUD /api/v1/buying-groups/; linked on CRM Profile tab.",
            },
            {
                "title": "CRM usage",
                "body": "crm_callbacks loads reps and buying groups for customer profile.",
            },
        ],
        tags=["crm", "master-data"],
        systems=["vndmanuf"],
        evidence=[
            "app/api/sales_reps.py",
            "app/api/buying_groups.py",
            "apps/vndmanuf_sales/ui/crm_callbacks.py",
        ],
    ),
    art(
        "Formula Cost Analysis Report",
        slug="vndmanuf-formula-cost-report",
        category_slug="vndmanuf",
        content_type="reference",
        summary="API endpoint for formula cost breakdown analysis.",
        purpose="Support costing reviews outside the unmounted costing router.",
        steps=[
            {
                "title": "Call API",
                "body": "GET /api/v1/reports/formulas/cost-analysis.",
            },
            {
                "title": "Note",
                "body": "/api/v1/costing/ router exists in costing.py but is not included in main.py — use reports endpoint or [VERIFY WITH OPERATOR] for costing UI.",
            },
        ],
        tags=["costing", "formulas"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=["app/api/reports.py", "app/api/costing.py", "app/api/main.py"],
    ),
    art(
        "Product Purchase and Assembly Pricing Sections",
        slug="vndmanuf-product-pricing-sections",
        category_slug="vndmanuf",
        summary="Configure purchase, usage and assembly pricing on the product detail panel.",
        purpose="Maintain unit costs and sell prices at product level.",
        steps=[
            {"title": "Open product", "body": "Manufacturing → Products → select row."},
            {
                "title": "Purchase section",
                "body": "Purchase accordion: formats, supplier pricing via purchase_usage_callbacks.",
            },
            {
                "title": "Assembly section",
                "body": "Assembly lines and BOM links managed in product_section_callbacks.",
            },
            {
                "title": "Sales pricing",
                "body": "Sales pricing fields on enhanced product page.",
            },
        ],
        tags=["products", "pricing"],
        systems=["vndmanuf"],
        confidence="medium",
        evidence=[
            "app/ui/product_section_callbacks.py",
            "app/ui/purchase_usage_callbacks.py",
        ],
    ),
    art(
        "Raw Materials API (Legacy)",
        slug="vndmanuf-raw-materials-api",
        category_slug="vndmanuf",
        content_type="reference",
        status="draft",
        summary="Legacy raw materials endpoints parallel to unified products.",
        purpose="Document API used by RM Reports and legacy integrations.",
        steps=[
            {
                "title": "List materials",
                "body": "GET /api/v1/raw-materials/ and /raw-materials/groups.",
            },
            {"title": "CRUD", "body": "POST/PUT/DELETE /raw-materials/{id}."},
            {
                "title": "UI note",
                "body": "No dedicated Raw Materials tab in Manufacturing nav — prefer Products with RAW type.",
            },
        ],
        tags=["raw-materials", "api"],
        systems=["vndmanuf"],
        evidence=["app/api/raw_materials.py", "app/ui/pages/raw_materials_page.py"],
    ),
]

# ---------------------------------------------------------------------------
# VND-DAQ articles
# ---------------------------------------------------------------------------


def daq_path(rel: str) -> str:
    return f"../DAQ/{rel}" if (DAQ_ROOT / rel).exists() else rel


VNDDAQ: list[dict[str, Any]] = [
    art(
        "VND-DAQ System Overview",
        slug="vndaq-system-overview",
        category_slug="vndaq",
        content_type="guide",
        summary="Overview of the VND-DAQ distillation control Dash application.",
        purpose="Orient operators to DAQ tabs and real-time control functions.",
        steps=[
            {
                "title": "Application start",
                "body": "main.py starts DAQ loop thread, scale reader, optional IND560 and chiller threads, valve control, and AB sequencer before loading the Dash UI.",
            },
            {
                "title": "Primary tabs",
                "body": "Top-level dcc.Tabs: Live I/O, Alarms, Config, Event Log (dash_ui.py).",
            },
            {
                "title": "M mimic views",
                "body": "Additional mimic sub-tabs include Kit, Sequencer Log, Utilities, A/B Banks, Cu-A/Cu-B Banks, Key Parameters, Heat Exchangers, Pressures, Levels, Sequencer, Bank Log, Info, PID.",
            },
        ],
        tags=["vndaq", "overview"],
        systems=["vndaq"],
        evidence=[daq_path("main.py"), daq_path("dash_ui.py")],
    ),
    art(
        "VND-DAQ Live I/O Tab",
        slug="vndaq-live-io-tab",
        category_slug="vndaq",
        summary="Monitor live process values, digital outputs and analog outputs.",
        purpose="Primary operator view during distillation runs.",
        steps=[
            {"title": "Open Live I/O", "body": "Select the Live I/O tab."},
            {
                "title": "Read analog inputs",
                "body": "AI tags display with alarm severity colouring via format_readback (normal/lo/hi/lolo/hihi).",
            },
            {
                "title": "Digital outputs",
                "body": "DO1–DO7 toggle buttons show ON/OFF state with permit badges.",
            },
            {
                "title": "Analog outputs",
                "body": "AO section includes P1 PID Control readout and setpoint controls.",
            },
        ],
        safety_notes="Alcohol vapour and moving equipment hazards apply on plant.",
        tags=["live", "io"],
        systems=["vndaq"],
        evidence=[daq_path("dash_ui.py"), daq_path("share_state.py")],
    ),
    art(
        "VND-DAQ Alarm Levels and Priorities",
        slug="vndaq-alarm-levels",
        category_slug="vndaq",
        content_type="reference",
        summary="Four alarm levels evaluated per tag: lolo, lo, hi, hihi.",
        purpose="Understand alarm severity ordering and trip initiation.",
        steps=[
            {
                "title": "Severity order",
                "body": "ALARM_LEVELS = ['lolo', 'lo', 'hi', 'hihi'] — most severe checked first in determine_alarm_level().",
            },
            {
                "title": "Low alarms",
                "body": "lolo and lo trigger when value <= threshold.",
            },
            {
                "title": "High alarms",
                "body": "hi and hihi trigger when value >= threshold.",
            },
            {
                "title": "Enable flags",
                "body": "Each level has enabled and value in tag config; disabled levels are skipped.",
            },
        ],
        tags=["alarms"],
        systems=["vndaq"],
        evidence=[daq_path("alarms.py"), daq_path("config_tab.py")],
    ),
    art(
        "VND-DAQ Alarm Acknowledgement",
        slug="vndaq-alarm-acknowledgement",
        category_slug="vndaq",
        summary="Acknowledge active alarms from the Alarms tab.",
        purpose="Confirm operator awareness before reset or continuation.",
        steps=[
            {
                "title": "Open Alarms tab",
                "body": "View alarm-log-table refreshed by alarm-log-interval.",
            },
            {
                "title": "Acknowledge one",
                "body": "Click Acknowledge button (id ack-button, index tag|level) → acknowledge_alarm().",
            },
            {
                "title": "Acknowledge all",
                "body": "Use ack-all-button to acknowledge all active alarms.",
            },
            {
                "title": "Trip association",
                "body": "Table shows associated TRIP rows from trip_initiators_map for tag|level keys.",
            },
        ],
        tags=["alarms", "ack"],
        systems=["vndaq"],
        evidence=[daq_path("callbacks/callbacks_alarm.py"), daq_path("alarms.py")],
    ),
    art(
        "VND-DAQ Trip Overview",
        slug="vndaq-trip-overview",
        category_slug="vndaq",
        content_type="guide",
        summary="Trips are automated safety actions triggered by alarm conditions.",
        purpose="Understand trip status display and reset workflow.",
        steps=[
            {
                "title": "Trip panel",
                "body": "M mimic shows Trip Status panel (render_trip_mimic_panel) with badges per trip_id.",
            },
            {
                "title": "Active trip",
                "body": "Red badge shows trip_id and initiator tag when trip_global_status.active is True.",
            },
            {
                "title": "Reset pending",
                "body": "Reset button (trip-reset-btn) enabled when reset_pending is True.",
            },
            {
                "title": "Trip engine",
                "body": "trigger_trip_action() executes configured actions: DO/AO writes, interlocks, email alerts.",
            },
        ],
        safety_notes="Do not bypass trips or interlocks.",
        tags=["trips", "safety"],
        systems=["vndaq"],
        evidence=[
            daq_path("trip_engine.py"),
            daq_path("dash_ui.py"),
            daq_path("trips.py"),
        ],
    ),
    art(
        "VND-DAQ Trip Reset Procedure",
        slug="vndaq-trip-reset",
        category_slug="vndaq",
        summary="Reset a trip after the initiating condition is cleared.",
        purpose="Safely return equipment to service after a trip event.",
        steps=[
            {
                "title": "Verify cause cleared",
                "body": "Confirm initiating alarm condition is no longer active.",
            },
            {
                "title": "Check trip badge",
                "body": "Trip badge shows reset_pending when reset is allowed.",
            },
            {
                "title": "Click Reset",
                "body": "Press Reset button (trip-reset-btn) for the trip_id.",
            },
            {
                "title": "Confirm",
                "body": "trip-reset-confirmation area shows outcome; reset_trip() clears interlocks per trip config.",
            },
        ],
        safety_notes="[VERIFY WITH OPERATOR] Confirm plant-specific reset prerequisites before enabling reset.",
        tags=["trips", "reset"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[daq_path("trip_engine.py"), daq_path("dash_ui.py")],
    ),
    art(
        "VND-DAQ Permissives — Understanding PERMIT OK / BLOCKED",
        slug="vndaq-permissives-overview",
        category_slug="vndaq",
        summary="Permissives gate operator actions on DO and AO tags.",
        purpose="Prevent unsafe equipment operation.",
        steps=[
            {
                "title": "Badge display",
                "body": "PERMIT OK (green) or PERMIT BLOCKED (red) badges on DO toggles and AO controls.",
            },
            {
                "title": "Configuration",
                "body": "Rules loaded from assets/permissives_config.json via permissives_engine.",
            },
            {
                "title": "Evaluation",
                "body": "evaluate_permissives() checks groups of conditions against live_data and do_state.",
            },
            {
                "title": "Fail closed",
                "body": "Missing sensor values or failed conditions block the permit.",
            },
        ],
        tags=["permissives", "safety"],
        systems=["vndaq"],
        evidence=[daq_path("permissives_engine.py"), daq_path("dash_ui.py")],
    ),
    art(
        "VND-DAQ Common Permissive Failures",
        slug="vndaq-permissive-failures",
        category_slug="vndaq",
        summary="Diagnose why a permissive is blocked using reason strings.",
        purpose="Speed up troubleshooting during startup.",
        steps=[
            {
                "title": "Read badge/tooltip",
                "body": "DO permit tooltip shows 'Permissive check pending' until evaluated.",
            },
            {
                "title": "Check reasons",
                "body": "evaluate_permissives returns failure reasons like 'SOURCE logic value' for each failed condition.",
            },
            {
                "title": "Verify inputs",
                "body": "Conditions read AI values from live_data or DO states from do_state.",
            },
            {
                "title": "Review config",
                "body": "Inspect assets/permissives_config.json for the tag's groups and logic (all/any).",
            },
        ],
        tags=["permissives", "troubleshooting"],
        systems=["vndaq"],
        evidence=[
            daq_path("permissives_engine.py"),
            daq_path("debug_permissive_status.py"),
        ],
    ),
    art(
        "VND-DAQ Interlocks",
        slug="vndaq-interlocks",
        category_slug="vndaq",
        content_type="guide",
        summary="Interlocks prevent DO/AO changes while a trip owns the tag.",
        purpose="Protect equipment when safety trips are active.",
        steps=[
            {
                "title": "Locked badge",
                "body": "interlock_badge shows LOCKED by {owners} when tag is in interlocked_do_tags or interlocked_ao_tags.",
            },
            {
                "title": "Trip actions",
                "body": "trigger_trip_action sets interlock ownership via interlock_owners_do/ao.",
            },
            {
                "title": "Free state",
                "body": "Green 'Free' badge when no interlock active.",
            },
        ],
        tags=["interlocks", "safety"],
        systems=["vndaq"],
        evidence=[
            daq_path("dash_ui.py"),
            daq_path("trip_engine.py"),
            daq_path("interlock_permissive.py"),
        ],
    ),
    art(
        "VND-DAQ P1 PID — Manual Mode",
        slug="vndaq-pid-manual-mode",
        category_slug="vndaq",
        summary="Operate P1 pump in manual mode without PID loop.",
        purpose="Direct control during commissioning or maintenance.",
        steps=[
            {
                "title": "Set mode",
                "body": "p1-pid-mode or mimic-p1-pid-mode state value 'manual' (stored in live input state).",
            },
            {
                "title": "PID loop behaviour",
                "body": "run_pid_loop returns immediately when mode != 'auto'.",
            },
            {
                "title": "Manual output",
                "body": "[VERIFY WITH OPERATOR] Use mimic AO controls to set P1 output manually when not in auto.",
            },
        ],
        tags=["pid", "manual"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[
            daq_path("pid_controller.py"),
            daq_path("callbacks/callbacks_pid.py"),
        ],
    ),
    art(
        "VND-DAQ P1 PID — Auto Mode",
        slug="vndaq-pid-auto-mode",
        category_slug="vndaq",
        summary="Automatic level control: LIT1 measurement drives P1 pump output.",
        purpose="Maintain still feed level automatically.",
        steps=[
            {"title": "Enable auto", "body": "Set p1-pid-mode to 'auto'."},
            {
                "title": "Loop execution",
                "body": "start_pid_thread runs run_pid_loop every 1s for tag P1.",
            },
            {
                "title": "Measurement",
                "body": "Process variable from ss.latest_row LIT1; setpoint from p1-pid-sp (default 150.0 mm).",
            },
            {
                "title": "Output",
                "body": "PID output written via write_ao_setpoint; logged to datawarehouse insert_point/insert_event.",
            },
        ],
        tags=["pid", "auto"],
        systems=["vndaq"],
        evidence=[daq_path("pid_controller.py"), daq_path("datawarehouse.py")],
    ),
    art(
        "VND-DAQ PID Setpoint and Tuning Changes",
        slug="vndaq-pid-setpoint-tuning",
        category_slug="vndaq",
        summary="Adjust PID setpoint, gains and output limits from the PID mimic tab.",
        purpose="Tune level control for stable operation.",
        steps=[
            {"title": "Open PID tab", "body": "M mimic → PID sub-tab."},
            {
                "title": "Setpoint",
                "body": "Adjust p1-pid-sp or p1-pid-sp-mimic in live input state.",
            },
            {
                "title": "Tuning",
                "body": "Kp/Ki/Kd from p1-pid-kp, p1-pid-ki, p1-pid-kd (defaults 0.01, 0.0, 0.0).",
            },
            {
                "title": "Limits",
                "body": "Output clamped by p1-pid-limit-lower (0.0) and p1-pid-limit-upper (2.0) L/min.",
            },
        ],
        tags=["pid", "tuning"],
        systems=["vndaq"],
        evidence=[
            daq_path("pid_controller.py"),
            daq_path("callbacks/callbacks_pid.py"),
            daq_path("dash_ui.py"),
        ],
    ),
    art(
        "VND-DAQ Historian — Reviewing Trends",
        slug="vndaq-historian-trends",
        category_slug="vndaq",
        summary="Review historical process data on configurable trend charts.",
        purpose="Analyse batch performance and troubleshoot past events.",
        steps=[
            {
                "title": "History charts",
                "body": "callbacks_history registers chart callbacks with default configs (Temperature, Flow, Pressures, DO, AO/PID, Levels).",
            },
            {
                "title": "Query data",
                "body": "query_timeseries_decimated from datawarehouse for selected tags and time range.",
            },
            {
                "title": "Configure charts",
                "body": "Chart configs stored in assets/history_chart_configs.json; positions in history_positions.json.",
            },
            {
                "title": "Add charts",
                "body": "add-chart-btn opens preset-modal for new chart configuration.",
            },
        ],
        tags=["historian", "trends"],
        systems=["vndaq"],
        evidence=[
            daq_path("callbacks/callbacks_history.py"),
            daq_path("datawarehouse.py"),
        ],
    ),
    art(
        "VND-DAQ Historian — Exporting Data",
        slug="vndaq-historian-export",
        category_slug="vndaq",
        summary="Export historical data for external analysis.",
        purpose="Support quality investigations and engineering review.",
        steps=[
            {
                "title": "Data source",
                "body": "Historian uses datawarehouse SQLite/event storage (insert_point, query_events).",
            },
            {
                "title": "Mobile export",
                "body": "mobile_data_export.py provides export utilities for mobile integration.",
            },
            {
                "title": "Chart export",
                "body": "[VERIFY WITH OPERATOR] Confirm current UI export button behaviour on history charts.",
            },
        ],
        tags=["historian", "export"],
        systems=["vndaq"],
        confidence="low",
        evidence=[
            daq_path("datawarehouse.py"),
            daq_path("mobile_data_export.py"),
            daq_path("callbacks/callbacks_history.py"),
        ],
    ),
    art(
        "VND-DAQ Config Tab — Tag and Alarm Configuration",
        slug="vndaq-config-tag-alarms",
        category_slug="vndaq",
        summary="View and edit AI/AO scaling and alarm thresholds.",
        purpose="Maintain instrument configuration.",
        steps=[
            {
                "title": "Open Config tab",
                "body": "Select Config tab → Tag & Alarm Configuration.",
            },
            {
                "title": "AI section",
                "body": "Analog Inputs from tag_config_input.json: eng_min, eng_max, lolo/lo/hi/hihi thresholds.",
            },
            {
                "title": "AO section",
                "body": "Analog Outputs from tag_config_output.json with same fields.",
            },
            {
                "title": "Persistence",
                "body": "[VERIFY WITH OPERATOR] Confirm whether Config tab inputs write back to JSON or are display-only at runtime.",
            },
        ],
        tags=["config", "alarms"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[daq_path("config_tab.py"), daq_path("assets/tag_config_input.json")],
    ),
    art(
        "VND-DAQ Event Log",
        slug="vndaq-event-log",
        category_slug="vndaq",
        summary="Review system events including alarms, trips and PID actions.",
        purpose="Audit trail for operations and troubleshooting.",
        steps=[
            {"title": "Open Event Log tab", "body": "Select Event Log tab."},
            {
                "title": "Event sources",
                "body": "insert_event records ALARM_ACK, TRIP_INIT, TRIP_LOG, PID_OUTPUT to datawarehouse.",
            },
            {
                "title": "Callbacks",
                "body": "callbacks_event_log.py renders the event log table.",
            },
        ],
        tags=["events", "log"],
        systems=["vndaq"],
        evidence=[
            daq_path("callbacks/callbacks_event_log.py"),
            daq_path("datawarehouse.py"),
            daq_path("main.py"),
        ],
    ),
    art(
        "VND-DAQ AB Sequencer and Bank Switching",
        slug="vndaq-ab-sequencer",
        category_slug="vndaq",
        summary="A/B bank sequencer for automated feedstock switching.",
        purpose="Operate dual-bank distillation sequences.",
        steps=[
            {
                "title": "Engine init",
                "body": "main.py initializes ab_sequencer engine on startup.",
            },
            {
                "title": "M mimic banks",
                "body": "A/B Banks and Cu-A/Cu-B Banks tabs in mimic view.",
            },
            {
                "title": "Sequencer tab",
                "body": "Sequencer and Bank Log tabs show sequence state and history.",
            },
            {
                "title": "Startup sequencer",
                "body": "startup_sequencer.py provides automated startup sequences.",
            },
        ],
        tags=["sequencer", "banks"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[
            daq_path("ab_sequencer.py"),
            daq_path("startup_sequencer.py"),
            daq_path("dash_ui.py"),
        ],
    ),
    art(
        "VND-DAQ Scale and Weight Integration",
        slug="vndaq-scale-integration",
        category_slug="vndaq",
        content_type="reference",
        summary="IND560 and scale reader threads feed weight data into DAQ.",
        purpose="Support gravimetric measurements during production.",
        steps=[
            {
                "title": "Scale thread",
                "body": "start_scale_thread() launched from main.py.",
            },
            {
                "title": "IND560",
                "body": "start_ind560_thread when IND560_ENABLE=1 (Ethernet/IP via ind560_reader.py).",
            },
            {
                "title": "Mobile charts",
                "body": "vnd_mobile/ui/charts_tab.py displays weight trends on mobile companion app.",
            },
        ],
        tags=["scale", "weight"],
        systems=["vndaq"],
        evidence=[
            daq_path("scale_reader.py"),
            daq_path("ind560_reader.py"),
            daq_path("vnd_mobile/ui/charts_tab.py"),
        ],
    ),
    art(
        "VND-DAQ Chiller Integration",
        slug="vndaq-chiller-integration",
        category_slug="vndaq",
        summary="Modbus chiller communication on COM3.",
        purpose="Monitor and control cooling utilities.",
        steps=[
            {
                "title": "Thread start",
                "body": "modbus_chiller.start_chiller_thread() from main.py.",
            },
            {
                "title": "Callbacks",
                "body": "callbacks_chiller.py handles chiller UI updates.",
            },
            {
                "title": "Monitor",
                "body": "chiller_communication_monitor.py tracks comms health.",
            },
        ],
        tags=["chiller", "utilities"],
        systems=["vndaq"],
        evidence=[
            daq_path("modbus_chiller.py"),
            daq_path("callbacks/callbacks_chiller.py"),
        ],
    ),
    art(
        "VND-DAQ Valve Control",
        slug="vndaq-valve-control",
        category_slug="vndaq",
        summary="Unified valve control system with feedback and permissives.",
        purpose="Operate process valves safely from mimic or Live I/O.",
        steps=[
            {
                "title": "Initialization",
                "body": "share_state.initialize_valve_control() on startup.",
            },
            {
                "title": "Callbacks",
                "body": "callbacks_valve.py and callbacks_mimic.py handle valve interactions.",
            },
            {
                "title": "Feedback",
                "body": "Valve feedback tracked for open/closed confirmation.",
            },
        ],
        tags=["valves"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[
            daq_path("valve_control.py"),
            daq_path("callbacks/callbacks_valve.py"),
            daq_path("main.py"),
        ],
    ),
    art(
        "VND Mobile Companion App",
        slug="vndaq-mobile-app",
        category_slug="vndaq",
        content_type="guide",
        summary="Mobile Dash app for remote monitoring of DAQ status, alarms and charts.",
        purpose="Allow off-site monitoring of distillery DAQ data.",
        steps=[
            {
                "title": "Location",
                "body": "vnd_mobile/ subproject with separate app.py.",
            },
            {
                "title": "Tabs",
                "body": "status_tab, alarms_tab, charts_tab, events_tab, bank_sequence_tab.",
            },
            {
                "title": "Data sources",
                "body": "http_source or file_source reads exported/mobile API data.",
            },
        ],
        tags=["mobile", "monitoring"],
        systems=["vndaq"],
        evidence=[daq_path("vnd_mobile/app.py"), daq_path("vnd_mobile/ui/layout.py")],
    ),
    art(
        "VND-DAQ Digital Output Toggle Operation",
        slug="vndaq-do-toggle-operation",
        category_slug="vndaq",
        summary="Toggle DO1–DO7 outputs from Live I/O when permitted.",
        purpose="Control pumps, valves and ancillary equipment.",
        steps=[
            {
                "title": "Locate DO section",
                "body": "Live I/O → Digital Outputs (DO1–DO7).",
            },
            {
                "title": "Check permit",
                "body": "Confirm PERMIT OK badge before toggling.",
            },
            {
                "title": "Toggle",
                "body": "Click {tag}-toggle button; colour shows success (ON) or secondary (OFF).",
            },
            {
                "title": "Interlock check",
                "body": "If LOCKED badge shown, resolve trip before operating.",
            },
        ],
        safety_notes="Only operate DOs when permissives are OK and interlocks are free.",
        tags=["do", "outputs"],
        systems=["vndaq"],
        evidence=[daq_path("dash_ui.py"), daq_path("io_handler.py")],
    ),
    art(
        "VND-DAQ Trip Email Alerts",
        slug="vndaq-trip-email-alerts",
        category_slug="vndaq",
        content_type="reference",
        summary="Email notifications sent when trips execute.",
        purpose="Alert off-site personnel to safety events.",
        steps=[
            {
                "title": "Trigger",
                "body": "trigger_trip_action calls email_alert.send_trip_email(trip_id, name).",
            },
            {
                "title": "Configuration",
                "body": "[VERIFY WITH OPERATOR] Review email_alert.py SMTP settings and recipient lists.",
            },
        ],
        tags=["trips", "email"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[daq_path("trip_engine.py"), daq_path("email_alert.py")],
    ),
    art(
        "VND-DAQ Graceful Shutdown",
        slug="vndaq-shutdown-procedure",
        category_slug="vndaq",
        summary="Application shutdown cleans up DAQ tasks and threads.",
        purpose="Prevent orphaned NI-DAQ tasks on exit.",
        steps=[
            {
                "title": "Signal handling",
                "body": "SIGINT/SIGTERM invoke cleanup_handler in main.py.",
            },
            {
                "title": "Stop DAQ loop",
                "body": "_daq_stop_event set; daq_thread joined with timeout.",
            },
            {
                "title": "Close tasks",
                "body": "close_open_tasks() releases hardware tasks.",
            },
            {
                "title": "PID thread",
                "body": "PID controller thread started after DAQ; stops with application.",
            },
        ],
        tags=["shutdown", "maintenance"],
        systems=["vndaq"],
        evidence=[daq_path("main.py"), daq_path("daq_core.py")],
    ),
    art(
        "VND-DAQ Mimic — Key Parameters and Heat Exchangers",
        slug="vndaq-mimic-process-views",
        category_slug="vndaq",
        summary="Focused mimic views for critical process variables.",
        purpose="Monitor key operating parameters during a run.",
        steps=[
            {
                "title": "Key Parameters tab",
                "body": "M mimic → Key Parameters (tab value key).",
            },
            {"title": "Heat Exchangers", "body": "Heat Exchangers tab (value hex)."},
            {
                "title": "Pressures and Levels",
                "body": "Pressures and Levels tabs for PT and LIT tags.",
            },
        ],
        tags=["mimic", "process"],
        systems=["vndaq"],
        evidence=[daq_path("dash_ui.py")],
    ),
    art(
        "VND-DAQ Cu Sequencer",
        slug="vndaq-cu-sequencer",
        category_slug="vndaq",
        summary="Copper bank sequencer (Cu-A / Cu-B) for sequential operations.",
        purpose="Automate copper catalyst bank switching.",
        steps=[
            {"title": "Cu banks tab", "body": "M mimic → Cu-A/Cu-B Banks."},
            {
                "title": "Engine",
                "body": "cu_sequencer.py implements copper bank sequence logic.",
            },
            {"title": "Monitor", "body": "Bank Log tab shows sequence history."},
        ],
        tags=["sequencer", "copper"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[daq_path("cu_sequencer.py"), daq_path("dash_ui.py")],
    ),
    art(
        "VND-DAQ Config Callbacks and Persistence",
        slug="vndaq-config-persistence",
        category_slug="vndaq",
        summary="Configuration changes via callbacks_config.",
        purpose="Understand how runtime config updates are applied.",
        steps=[
            {
                "title": "Callbacks",
                "body": "callbacks/callbacks_config.py registers config save handlers.",
            },
            {
                "title": "Tag files",
                "body": "tag_config_input.json and tag_config_output.json loaded by config_tab.",
            },
            {
                "title": "Verify",
                "body": "[VERIFY WITH OPERATOR] Confirm save button behaviour and file write permissions on production PC.",
            },
        ],
        tags=["config"],
        systems=["vndaq"],
        confidence="medium",
        evidence=[daq_path("callbacks/callbacks_config.py"), daq_path("config_tab.py")],
    ),
    art(
        "VND-DAQ DAQ Loop and Live Data",
        slug="vndaq-daq-loop",
        category_slug="vndaq",
        content_type="reference",
        summary="Core data acquisition loop populates live_data and share_state.",
        purpose="Understand where Live I/O values originate.",
        steps=[
            {
                "title": "Start loop",
                "body": "start_daq_loop(share_state, stop_event) in dedicated thread.",
            },
            {
                "title": "State",
                "body": "live_data, ao_state, do_state, di_state updated under daq_lock.",
            },
            {
                "title": "Alarms",
                "body": "evaluate_alarms called as part of acquisition cycle.",
            },
        ],
        tags=["daq", "acquisition"],
        systems=["vndaq"],
        evidence=[daq_path("daq_core.py"), daq_path("share_state.py")],
    ),
    art(
        "VND-DAQ Alarm and Trip Data Warehouse",
        slug="vndaq-datawarehouse-events",
        category_slug="vndaq",
        content_type="reference",
        summary="SQLite data warehouse stores points and events for historian and audit.",
        purpose="Support trend queries and post-incident review.",
        steps=[
            {
                "title": "Point insert",
                "body": "insert_point(tag, kind, value) for PID and process values.",
            },
            {
                "title": "Events",
                "body": "insert_event for ALARM_ACK, TRIP_INIT, TRIP_LOG, PID_OUTPUT.",
            },
            {
                "title": "Query",
                "body": "query_events and query_timeseries_decimated for history views.",
            },
        ],
        tags=["historian", "database"],
        systems=["vndaq"],
        evidence=[daq_path("datawarehouse.py")],
    ),
]

# ---------------------------------------------------------------------------
# Skipped / gap tracking
# ---------------------------------------------------------------------------

REQUESTED_BUT_SKIPPED = [
    (
        "VNDManuf Dashboard Overview",
        "No single dashboard; main tabs serve as entry points",
        "Use vndmanuf-introduction instead",
    ),
    (
        "Production Scheduling",
        "No scheduling module found in API or UI",
        "app/api/, app/ui/",
    ),
    (
        "Product Categories",
        "No dedicated product category entity; product_type flag used",
        "app/adapters/db/models.py Product.product_type",
    ),
    (
        "Product Costing UI",
        "costing.py router exists but not mounted in main.py",
        "app/api/costing.py",
    ),
    (
        "Goods Receipts dedicated UI",
        "No dedicated goods receipt page; inventory movements API only",
        "app/api/inventory.py",
    ),
    (
        "Xero daily tasks UI",
        "Xero OAuth integration disabled in app.py",
        "app/ui/app.py",
    ),
    (
        "Shopify UI tab",
        "shopify_page.py stub, not in navigation",
        "app/ui/pages/shopify_page.py",
    ),
    ("VND-DAQ Login", "No authentication in main Dash app", "DAQ/main.py"),
    (
        "VND-DAQ Starting/Completing Batch (named workflow)",
        "Sequencer/bank logic exists but no single 'batch' UI matching ERP batches",
        "DAQ/startup_sequencer.py",
    ),
    (
        "Yield Recording dedicated screen",
        "Yield on work order complete in VNDManuf, not DAQ",
        "app/api/work_orders.py",
    ),
    (
        "Material Consumption standalone",
        "Covered under work order issues",
        "app/api/work_orders.py",
    ),
    (
        "Sales Analytics detail",
        "Analytics sub-tab exists; [VERIFY WITH OPERATOR] for exact charts",
        "apps/vndmanuf_sales/ui/analytics_callbacks.py",
    ),
    (
        "CRM Follow-ups / Calendar",
        "API exists for scheduled activities; UI depth [VERIFY]",
        "app/api/crm.py",
    ),
]

OPERATOR_VALIDATION = [
    "Config tab write-back behaviour (display vs persist)",
    "Historian chart export button workflow",
    "PID manual mode AO write path from mimic",
    "Trip reset plant prerequisites",
    "Shopify operational workflow (cron vs manual API)",
    "Rich editor JS assets for Nova U (nuEditorLoadContent)",
    "Sales Analytics chart definitions",
    "Batch Processing future UI vs batches API workflow",
]

INSUFFICIENT_EVIDENCE = [
    "VNDManuf login/authentication (not implemented in Dash UI)",
    "VND-DAQ user login (not implemented)",
    "Dedicated production scheduling",
    "Xero UI workflows (integration commented out)",
    "Product costing UI (API not mounted)",
]


def build_gap_analysis(
    articles: list[dict], skipped: list, validation: list, insufficient: list
) -> str:
    high = sum(1 for a in articles if a["confidence"] == "high")
    med = sum(1 for a in articles if a["confidence"] == "medium")
    low = sum(1 for a in articles if a["confidence"] == "low")
    vnd = sum(1 for a in articles if "vndmanuf" in a.get("systems", []))
    daq = sum(1 for a in articles if "vndaq" in a.get("systems", []))

    lines = [
        "# Nova U Gap Analysis",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Summary",
        "",
        f"- **Articles generated:** {len(articles)}",
        f"- **Confidence:** {high} high, {med} medium, {low} low",
        f"- **VNDManuf articles:** {vnd}",
        f"- **VND-DAQ articles:** {daq}",
        f"- **Articles skipped:** {len(skipped)}",
        "",
        "## Features Discovered",
        "",
        "### VNDManuf",
        "- Dash UI with tabs: Manufacturing (8 sub-tabs), Contacts, Sales (7 sub-tabs), CRM, Reports, Settings (7 sub-tabs), Nova U",
        "- FastAPI /api/v1: products, inventory, work orders, formulas, assemblies, sales, CRM, documents, training, shopify webhooks",
        "- Work order lifecycle: Draft → Released → In Progress → Complete (+ Hold, Void)",
        "- Sales: orders, delivery docket/invoice conversion, PDF generation via DOCX templates",
        "- Nova U: full CRUD API, search, corpus export, rich editor UI",
        "",
        "### VND-DAQ",
        "- Dash UI tabs: Live I/O, Alarms, Config, Event Log + extensive mimic sub-tabs",
        "- Alarms: lolo/lo/hi/hihi with acknowledgement",
        "- Trips: trip_engine with reset, interlocks, email alerts",
        "- Permissives: JSON-configured fail-closed gating",
        "- PID: LIT1 → P1 auto/manual control",
        "- Historian: datawarehouse + configurable charts",
        "- AB sequencer, valve control, chiller, IND560 scales",
        "- vnd_mobile companion app",
        "",
        "## Articles Generated",
        "",
    ]
    for a in articles:
        lines.append(f"- `{a['slug']}` ({a['confidence']}) — {a['title']}")

    lines.extend(["", "## Articles Skipped", ""])
    for title, reason, evidence in skipped:
        lines.append(f"- **{title}:** {reason} ({evidence})")

    lines.extend(["", "## Areas Requiring Operator Validation", ""])
    for item in validation:
        lines.append(f"- {item}")

    lines.extend(["", "## Areas With Insufficient Evidence", ""])
    for item in insufficient:
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def main() -> None:
    articles = VNDMANUF + VNDDAQ
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_repos": ["VNDManuf", "VND-DAQ"],
        "article_count": len(articles),
        "articles": articles,
    }
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    OUT_GAP.write_text(
        build_gap_analysis(
            articles, REQUESTED_BUT_SKIPPED, OPERATOR_VALIDATION, INSUFFICIENT_EVIDENCE
        ),
        encoding="utf-8",
    )
    print(f"Wrote {len(articles)} articles -> {OUT_JSON}")
    print(f"Wrote gap analysis -> {OUT_GAP}")


if __name__ == "__main__":
    main()

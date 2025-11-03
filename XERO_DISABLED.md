# Xero Integration - Temporarily Disabled

## Status
✅ **Xero integration is currently disabled** in VNDManuf

## What Was Disabled

The following Xero-related functionality has been commented out in `app/ui/app.py`:

1. **Accounting Tab** - Removed from navigation tabs
2. **Xero OAuth Routes** - `/xero/connect` and `/xero/callback` routes disabled
3. **Xero Integration Page** - Import and callback registration commented out

## Files Modified

- `app/ui/app.py` - All Xero references commented with note "Xero integration temporarily disabled - will re-enable later"

## To Re-enable Xero Integration

When ready to re-enable:

1. **Uncomment the import** (line ~47):
```python
from .pages.accounting_integration_page import accounting_integration_page
```

2. **Uncomment the Accounting tab** (line ~99):
```python
dbc.Tab(label="Accounting", tab_id="accounting"),
```

3. **Uncomment the callbacks registration** (line ~111):
```python
accounting_integration_page.register_callbacks(app)
```

4. **Uncomment the tab content handling** (line ~353):
```python
elif active_tab == "accounting":
    return accounting_integration_page.layout()
```

5. **Uncomment the Xero OAuth routes** (lines ~702-735):
```python
# Add Flask routes for Xero OAuth
from flask import request, redirect
from app.services.xero_oauth import get_auth_url, exchange_code_for_tokens

server = app.server  # Dash exposes Flask server

@server.route("/xero/connect")
def xero_connect():
    """Redirect to Xero OAuth authorization."""
    url = get_auth_url()
    return redirect(url)

@server.route("/xero/callback")
def xero_callback():
    """Handle Xero OAuth callback."""
    # ... rest of the callback code
```

## Configuration Files

The following files still contain Xero configuration (not removed):

- `app/services/xero_oauth.py` - OAuth authentication
- `app/services/xero_integration.py` - Integration logic
- `app/services/xero_mappings.py` - Account mappings
- `app/ui/pages/accounting_integration_page.py` - UI page
- `env.example` - Environment configuration template
- Database models in `app/adapters/db/models.py` (XeroToken, XeroSyncLog)

These files remain intact and will work when re-enabled.

## Database Schema

The Xero-related tables are still in the database schema:
- `xero_tokens` - OAuth token storage
- `xero_sync_log` - Sync operation audit log
- Extended fields on `suppliers`, `customers`, `products` tables

These can be managed via Alembic migrations if needed.

## Date Disabled
2024-01-XX (Date TBD)

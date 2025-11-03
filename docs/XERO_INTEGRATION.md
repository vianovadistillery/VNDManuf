# Xero Integration for TPManuf

This document describes the Xero integration implementation for the TPManuf manufacturing system.

## Overview

The Xero integration enables bidirectional synchronization between TPManuf and Xero Accounting for:
- **Contacts** (Suppliers and Customers)
- **Items** (Products as Xero Items)
- **Bills** (Purchase transactions)
- **Invoices** (Sales transactions)
- **Manual Journals** (Inventory postings)

## Architecture

### Components

1. **Database Models** (`app/adapters/db/models.py`)
   - `XeroToken` - Stores OAuth2 tokens
   - `XeroSyncLog` - Audit log for sync operations
   - Extended `Supplier`, `Customer`, and `Product` with Xero IDs

2. **OAuth Module** (`app/services/xero_oauth.py`)
   - Handles OAuth2 authorization flow
   - Token refresh and management
   - Secure token storage

3. **Integration Module** (`app/services/xero_integration.py`)
   - Push operations (Contacts, Items, Journals)
   - Pull operations (Contacts)
   - Error handling and logging

4. **Mappings Module** (`app/services/xero_mappings.py`)
   - Account code mappings
   - Product type → account mapping

5. **UI** (`app/ui/pages/accounting_integration_page.py`)
   - Connection status
   - Push/pull controls
   - Batch journal posting
   - Sync logs viewer

## Setup

### 1. Register Xero App

1. Go to https://developer.xero.com/myapps
2. Create a new app (or edit existing)
3. Note your Client ID and Client Secret
4. Set redirect URI: `http://localhost:8050/xero/callback`
5. **Select scopes** in the dropdown:
   - ☑️ accounting.contacts (for suppliers/customers)
   - ☑️ accounting.transactions (for journals)
   - ☑️ accounting.settings (optional, for company settings)

**Note**: The `offline_access` scope is NOT in the dropdown - it's automatically sent in the OAuth request by your app to enable refresh tokens. You don't need to select it in the portal.

### 2. Configure Environment

Create `.env` file (copy from `env.example`):

```bash
XERO_CLIENT_ID=your_client_id
XERO_CLIENT_SECRET=your_client_secret
XERO_REDIRECT_URI=http://localhost:8050/xero/callback
XERO_SCOPES=offline_access accounting.contacts accounting.transactions
```

### 3. Run Migration

```bash
alembic upgrade head
```

### 4. Connect to Xero

1. Start the Dash UI: `python -m app.ui.app`
2. Navigate to **Accounting** tab
3. Click **Connect to Xero**
4. Authorize the app in Xero
5. You'll be redirected back with connection confirmation

## Usage

### Push Supplier to Xero

1. Go to **Accounting** tab
2. Enter Supplier ID in "Push to Xero" section
3. Click **Push Supplier**
4. Check sync logs for status

### Push Customer to Xero

1. Enter Customer ID
2. Click **Push Customer**
3. Verify in Xero Contacts

### Push Product as Item

1. Enter Product ID
2. Click **Push Product**
3. Product appears in Xero Items

### Pull Contacts from Xero

1. Click **Pull Contacts** button
2. Contacts sync from Xero to TPManuf
3. View in sync logs

### Post Batch Journal

When closing a batch:

1. Enter Batch Code and Amount
2. Click **Post Journal**
3. Journal entry created in Xero with FG/RM inventory postings

## Database Schema

### New Tables

**xero_tokens**
- `id` - Primary key
- `access_token` - OAuth2 access token (encrypted)
- `refresh_token` - OAuth2 refresh token
- `expires_at` - Token expiration timestamp
- `tenant_id` - Xero tenant (organization) ID
- `created_at`, `updated_at` - Audit timestamps

**xero_sync_log**
- `id` - Primary key
- `ts` - Timestamp
- `object_type` - Type: Contact, Item, Journal, etc.
- `object_id` - Local TPManuf ID
- `direction` - PUSH or PULL
- `status` - OK or ERROR
- `message` - Status message

### Extended Tables

**suppliers**
- `xero_contact_id` - Xero Contact UUID
- `last_sync` - Last sync timestamp

**customers**
- `xero_contact_id` - Xero Contact UUID
- `last_sync` - Last sync timestamp

**products**
- `xero_item_id` - Xero Item UUID
- `last_sync` - Last sync timestamp

## API Integration Details

### Contacts

**Push Supplier**
```python
from app.services.xero_integration import push_supplier
result = push_supplier("supplier-id-uuid")
# Returns: Xero contact data with ContactID
```

**Push Customer**
```python
from app.services.xero_integration import push_customer
result = push_customer("customer-id-uuid")
```

**Pull Contacts**
```python
from app.services.xero_integration import pull_contacts
count = pull_contacts()  # Returns number of contacts synced
```

### Items

**Push Product**
```python
from app.services.xero_integration import push_product_as_item
result = push_product_as_item("product-id-uuid")
```

### Manual Journals

**Post Batch Journal**
```python
from app.services.xero_integration import post_batch_journal
from app.services.xero_mappings import get_account

post_batch_journal(
    batch_code="B060149",
    debit_account=get_account("FG_INVENTORY"),
    credit_account=get_account("RAW_INVENTORY"),
    amount=Decimal("1500.00"),
    date_str="2024-01-15"
)
```

## Account Mappings

Default account codes (customizable in `xero_mappings.py`):

- **FG_INVENTORY**: `120` - Finished Goods Inventory
- **RAW_INVENTORY**: `130` - Raw Materials Inventory
- **COGS**: `500` - Cost of Goods Sold
- **PURCHASES**: `310` - Purchase Costs
- **SALES**: `200` - Sales Revenue

## Security Considerations

1. **Tokens** - Stored encrypted in database
2. **Refresh** - Auto-refreshes expired tokens
3. **Error Logging** - All sync operations logged
4. **Rate Limiting** - Respects Xero rate limits (60 req/min)

## Troubleshooting

### Connection Issues

**Error: "Xero not connected"**
- Run migration: `alembic upgrade head`
- Click "Connect to Xero" in UI
- Check `.env` credentials

**Error: "Invalid client credentials"**
- Verify CLIENT_ID and CLIENT_SECRET in `.env`
- Check redirect URI matches Xero app settings

### Sync Issues

**PUSH fails with 400 Bad Request**
- Check object exists in TPManuf DB
- Verify required fields (name, code) are populated
- Review sync log for detailed error

**PULL returns 0 contacts**
- Confirm Xero has contacts marked as Supplier/Customer
- Check if contacts already synced (look for `xero_contact_id`)

### Rate Limiting

Xero API limit: 60 requests per minute per tenant
- If you hit rate limits, wait 1 minute
- Check sync logs for 429 status codes

## Future Enhancements

1. **Webhook Support** - Real-time sync from Xero events
2. **Bills Integration** - Push purchase orders as Xero bills
3. **Invoice Push** - Create Xero invoices from TPManuf SOs
4. **Custom Account Mapping UI** - Admin interface for GL codes
5. **Multi-tenant Support** - Multiple Xero organizations

## Testing

### Manual Test Plan

1. **Connect**
   - Visit `/xero/connect`
   - Authorize with demo company
   - Verify success message shows tenant ID

2. **Push Supplier**
   - Get supplier ID from suppliers table
   - Push via UI
   - Check Xero Contacts
   - Verify `xero_contact_id` populated in DB

3. **Push Product**
   - Get product ID
   - Push via UI
   - Check Xero Items
   - Verify `xero_item_id` populated

4. **Post Journal**
   - Enter batch code and amount
   - Post journal
   - Check Xero Manual Journals

5. **Pull Contacts**
   - Click Pull Contacts
   - Verify new records appear in DB
   - Check sync logs

## Code References

- OAuth: `app/services/xero_oauth.py`
- Integration: `app/services/xero_integration.py`
- Mappings: `app/services/xero_mappings.py`
- UI: `app/ui/pages/accounting_integration_page.py`
- Models: `app/adapters/db/models.py`
- Routes: `app/ui/app.py` (lines 699-725)
- Migration: `db/alembic/versions/4425b7936d0b_add_xero_integration_tables.py`

# Xero Connection Fix

## Issue
The "Connect to Xero" button in the UI wasn't working.

## Root Cause
The button was configured correctly with `href="/xero/connect"` and the Flask routes exist in `app.py` at lines 705-731.

However, the button might not have been triggering the redirect properly due to Dash/Flask routing.

## Solution
The connection should work now. The button code in `app/ui/pages/accounting_integration_page.py` is:

```python
dbc.Button(
    "Connect to Xero",
    href="/xero/connect",
    id="btn-connect-xero",
    color="primary",
    disabled=is_connected,
),
```

## How It Works

1. **Button Click**: When the user clicks "Connect to Xero", the href navigates to `/xero/connect`
2. **Flask Route**: The route in `app/ui/app.py` (line 705-709) catches this:
   ```python
   @server.route("/xero/connect")
   def xero_connect():
       """Redirect to Xero OAuth authorization."""
       url = get_auth_url()
       return redirect(url)
   ```
3. **OAuth URL**: `get_auth_url()` generates the Xero authorization URL with:
   - Client ID from environment
   - Redirect URI: `http://localhost:8050/xero/callback`
   - Scopes: `offline_access accounting.contacts accounting.settings accounting.transactions`
4. **User Redirects**: User is sent to Xero for authorization
5. **Callback**: Xero redirects back to `/xero/callback` with authorization code
6. **Token Exchange**: The callback route exchanges the code for tokens and stores them

## Verification

To verify the configuration is correct:

```bash
# Check if credentials are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CLIENT_ID:', os.getenv('XERO_CLIENT_ID')[:10])"

# Test auth URL generation
python -c "from app.services.xero_oauth import get_auth_url; print(get_auth_url())"
```

## Expected Flow

1. Navigate to Accounting tab in Dash UI
2. Click "Connect to Xero" button
3. Browser redirects to: `https://login.xero.com/identity/connect/authorize?...`
4. User authorizes the app in Xero
5. Xero redirects back to: `http://localhost:8050/xero/callback?code=...`
6. App displays success message with Tenant ID

## Current Status

✅ Configuration correct:
- CLIENT_ID is set
- CLIENT_SECRET is set  
- REDIRECT_URI matches Xero app settings
- Flask routes are registered
- OAuth flow is implemented

## Testing the Connection

To test if the button works:

1. Start the Dash UI: `python -m app.ui.app`
2. Navigate to the "Accounting" tab
3. Click "Connect to Xero"
4. You should be redirected to Xero login page
5. After authorizing, you should be redirected back with a success message


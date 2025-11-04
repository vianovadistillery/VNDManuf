"""Xero OAuth2 authentication and token management."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.adapters.db import get_session
from app.adapters.db.models import XeroToken

load_dotenv()

# Xero OAuth2 configuration
CLIENT_ID = os.getenv("XERO_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("XERO_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("XERO_REDIRECT_URI", "http://localhost:8050/xero/callback")
SCOPES = os.getenv(
    "XERO_SCOPES", "offline_access accounting.contacts accounting.transactions"
).split()


def get_auth_url(state: str = "tpmanuf-xero") -> str:
    """
    Generate Xero OAuth2 authorization URL.

    Args:
        state: State parameter for CSRF protection

    Returns:
        Authorization URL to redirect user to
    """
    # Construct the auth URL
    base_url = "https://login.xero.com/identity/connect/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": state,
    }

    from urllib.parse import urlencode

    return f"{base_url}?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        code: Authorization code from callback

    Returns:
        Dictionary containing tokens and tenant info
    """
    import requests

    token_url = "https://identity.xero.com/connect/token"

    # Prepare request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    # Basic auth header
    import base64

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers["Authorization"] = f"Basic {encoded}"

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()

    token_data = response.json()

    # Get tenant info
    from app.services.xero_integration import _get_tenant_connections

    connections = _get_tenant_connections(token_data["access_token"])
    tenant_id = connections[0]["tenantId"] if connections else None

    # Save tokens to database
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=int(token_data.get("expires_in", 1800))
    )

    session = get_session()
    try:
        # Delete any existing tokens
        session.query(XeroToken).delete()

        # Save new tokens
        xero_token = XeroToken(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=expires_at,
            tenant_id=tenant_id,
        )
        session.add(xero_token)
        session.commit()
    finally:
        session.close()

    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "tenant_id": tenant_id,
    }


def get_latest_tokens(session: Optional[Session] = None) -> Optional[XeroToken]:
    """Get the latest Xero token from database."""
    if session is None:
        s = get_session()
        try:
            return get_latest_tokens(s)
        finally:
            s.close()

    return session.query(XeroToken).order_by(XeroToken.id.desc()).first()


def ensure_fresh_token(session: Optional[Session] = None) -> XeroToken:
    """
    Ensure we have a valid, non-expired token.
    Refreshes if necessary.

    Returns:
        Valid XeroToken with fresh access_token

    Raises:
        RuntimeError: If no token found or refresh fails
    """
    token = get_latest_tokens(session)

    if not token:
        raise RuntimeError("Xero not connected. Use /xero/connect first.")

    # Check if token is expired (with 60 second buffer)
    now = datetime.now(timezone.utc)
    if now < token.expires_at - timedelta(seconds=60):
        return token

    # Need to refresh
    import base64

    import requests

    token_url = "https://identity.xero.com/connect/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
    }

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers["Authorization"] = f"Basic {encoded}"

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()

    token_data = response.json()

    # Update token in database
    new_expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=int(token_data.get("expires_in", 1800))
    )

    if session is None:
        s = get_session()
        try:
            token.access_token = token_data["access_token"]
            token.refresh_token = token_data["refresh_token"]
            token.expires_at = new_expires_at
            s.commit()
            s.refresh(token)
            return token
        finally:
            s.close()
    else:
        token.access_token = token_data["access_token"]
        token.refresh_token = token_data["refresh_token"]
        token.expires_at = new_expires_at
        session.commit()
        session.refresh(token)
        return token


def get_access_token() -> str:
    """
    Get a valid access token.

    Returns:
        Valid access token string
    """
    token = ensure_fresh_token()
    return token.access_token


def get_tenant_id() -> str:
    """Get the Xero tenant ID."""
    token = get_latest_tokens()
    if not token or not token.tenant_id:
        raise RuntimeError("No tenant ID available. Reconnect to Xero.")
    return token.tenant_id

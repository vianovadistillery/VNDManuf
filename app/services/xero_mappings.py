"""Xero account code mappings for TPManuf."""

from typing import Optional

# Default account mappings
DEFAULT_ACCOUNTS = {
    "RAW_INVENTORY": "130",  # Raw material inventory
    "FG_INVENTORY": "120",  # Finished goods inventory
    "COGS": "500",  # Cost of goods sold
    "PURCHASES": "310",  # Purchases/Cost of sales
    "SALES": "200",  # Sales revenue
}

# Mapping from TPManuf product types to Xero accounts
PRODUCT_TYPE_ACCOUNTS = {
    "RAW": "130",  # Raw materials → inventory
    "FG": "120",  # Finished goods → inventory
}


def get_account(code: str, fallback: Optional[str] = None) -> str:
    """
    Get Xero account code for a given mapping key.

    Args:
        code: Account mapping key (e.g., "RAW_INVENTORY")
        fallback: Fallback account code if not found

    Returns:
        Xero account code
    """
    # In the future, this could load from database
    # For now, use default mappings
    account = DEFAULT_ACCOUNTS.get(code)

    if account:
        return account

    if fallback:
        return fallback

    # If no fallback and not in defaults, raise error
    raise ValueError(f"Unknown account mapping: {code}")


def get_purchase_account(product_type: str = "RAW") -> str:
    """
    Get purchase account code for a product type.

    Args:
        product_type: RAW or FG

    Returns:
        Account code for purchases
    """
    return PRODUCT_TYPE_ACCOUNTS.get(product_type, DEFAULT_ACCOUNTS["RAW_INVENTORY"])


def get_sales_account() -> str:
    """Get default sales account code."""
    return DEFAULT_ACCOUNTS["SALES"]


def get_cogs_account() -> str:
    """Get default COGS account code."""
    return DEFAULT_ACCOUNTS["COGS"]

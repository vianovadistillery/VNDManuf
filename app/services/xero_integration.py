"""Xero API integration functions."""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests

from app.adapters.db import get_session
from app.adapters.db.models import Customer, Product, Supplier, XeroSyncLog
from app.services.xero_oauth import ensure_fresh_token

API_BASE = "https://api.xero.com/api.xro/2.0"


def _log_sync(
    object_type: str, object_id: str, direction: str, status: str, message: str
):
    """Log a sync operation to the audit table."""
    with get_session() as session:
        log = XeroSyncLog(
            object_type=object_type,
            object_id=str(object_id),
            direction=direction,
            status=status,
            message=message[:500] if message else "",
        )
        session.add(log)
        session.commit()


def _get_access_token_and_tenant():
    """Get access token and tenant ID."""
    token = ensure_fresh_token()
    return token.access_token, token.tenant_id


def _get_tenant_connections(access_token: str) -> List[Dict[str, Any]]:
    """Get connections for the current access token."""
    url = "https://api.xero.com/connections"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def push_supplier(supplier_id: str) -> Dict[str, Any]:
    """
    Push a supplier to Xero as a Contact.

    Args:
        supplier_id: TPManuf supplier ID

    Returns:
        Xero contact data
    """
    with get_session() as session:
        supplier = session.get(Supplier, supplier_id)
        if not supplier:
            raise ValueError(f"Supplier {supplier_id} not found")

        access_token, tenant_id = _get_access_token_and_tenant()

        # If already linked, update; otherwise create
        if supplier.xero_contact_id:
            contact_id = supplier.xero_contact_id
            method = "PUT"
            url = f"{API_BASE}/Contacts/{contact_id}"
        else:
            method = "POST"
            url = f"{API_BASE}/Contacts"

        payload = {
            "Contacts": [
                {
                    "Name": supplier.name,
                    "ContactNumber": supplier.code,
                    "EmailAddress": supplier.email or "",
                    "ContactPersons": [
                        {"FirstName": supplier.contact_person or supplier.name}
                    ]
                    if supplier.contact_person or supplier.name
                    else [],
                    "Phones": [{"PhoneNumber": supplier.phone}]
                    if supplier.phone
                    else [],
                    "Addresses": [{"AddressLine1": supplier.address or ""}]
                    if supplier.address
                    else [],
                    "IsSupplier": True,
                    "IsCustomer": False,
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": tenant_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.request(method, url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            contact = result["Contacts"][0]
            supplier.xero_contact_id = contact["ContactID"]
            session.commit()

            _log_sync("Contact", supplier_id, "PUSH", "OK", "Supplier synced to Xero")

            return contact

        except Exception as e:
            _log_sync("Contact", supplier_id, "PUSH", "ERROR", str(e))
            raise


def push_customer(customer_id: str) -> Dict[str, Any]:
    """
    Push a customer to Xero as a Contact.

    Args:
        customer_id: TPManuf customer ID

    Returns:
        Xero contact data
    """
    with get_session() as session:
        customer = session.get(Customer, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        access_token, tenant_id = _get_access_token_and_tenant()

        if customer.xero_contact_id:
            contact_id = customer.xero_contact_id
            method = "PUT"
            url = f"{API_BASE}/Contacts/{contact_id}"
        else:
            method = "POST"
            url = f"{API_BASE}/Contacts"

        payload = {
            "Contacts": [
                {
                    "Name": customer.name,
                    "ContactNumber": customer.code,
                    "EmailAddress": customer.email or "",
                    "ContactPersons": [
                        {"FirstName": customer.contact_person or customer.name}
                    ]
                    if customer.contact_person or customer.name
                    else [],
                    "Phones": [{"PhoneNumber": customer.phone}]
                    if customer.phone
                    else [],
                    "Addresses": [{"AddressLine1": customer.address or ""}]
                    if customer.address
                    else [],
                    "IsSupplier": False,
                    "IsCustomer": True,
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": tenant_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.request(method, url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            contact = result["Contacts"][0]
            customer.xero_contact_id = contact["ContactID"]
            session.commit()

            _log_sync("Contact", customer_id, "PUSH", "OK", "Customer synced to Xero")

            return contact

        except Exception as e:
            _log_sync("Contact", customer_id, "PUSH", "ERROR", str(e))
            raise


def push_product_as_item(product_id: str) -> Dict[str, Any]:
    """
    Push a product to Xero as an Item.

    Args:
        product_id: TPManuf product ID

    Returns:
        Xero item data
    """
    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        access_token, tenant_id = _get_access_token_and_tenant()

        if product.xero_item_id:
            item_id = product.xero_item_id
            method = "PUT"
            url = f"{API_BASE}/Items/{item_id}"
        else:
            method = "POST"
            url = f"{API_BASE}/Items"

        # Determine if purchased or sold based on product type
        # This is a simple heuristic - you may want to enhance this
        is_purchased = bool(product.purcost)
        is_sold = bool(product.wholesalecost)

        payload = {
            "Items": [
                {
                    "Code": product.sku,
                    "Name": product.name,
                    "Description": product.description or product.name,
                    "IsPurchased": is_purchased,
                    "IsSold": is_sold,
                    "PurchaseDetails": {
                        "UnitPrice": float(product.purcost or 0),
                        "AccountCode": "510",  # Cost of Sales
                    }
                    if is_purchased
                    else None,
                    "SalesDetails": {
                        "UnitPrice": float(product.wholesalecost or 0),
                        "AccountCode": "200",  # Sales
                    }
                    if is_sold
                    else None,
                }
            ]
        }

        # Remove None values
        if not is_purchased:
            payload["Items"][0]["PurchaseDetails"] = None
        if not is_sold:
            payload["Items"][0]["SalesDetails"] = None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": tenant_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.request(method, url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            item = result["Items"][0]
            product.xero_item_id = item["ItemID"]
            session.commit()

            _log_sync("Item", product_id, "PUSH", "OK", "Product synced to Xero")

            return item

        except Exception as e:
            _log_sync("Item", product_id, "PUSH", "ERROR", str(e))
            raise


def post_batch_journal(
    batch_code: str,
    debit_account: str,
    credit_account: str,
    amount: Decimal,
    date_str: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Post a manual journal entry to Xero for batch inventory posting.

    Args:
        batch_code: Batch code/identifier
        debit_account: GL account code to debit
        credit_account: GL account code to credit
        amount: Journal amount
        date_str: Journal date (YYYY-MM-DD)

    Returns:
        Xero manual journal data
    """
    access_token, tenant_id = _get_access_token_and_tenant()

    journal_date = date_str or str(date.today())

    payload = {
        "ManualJournals": [
            {
                "Narration": f"Batch {batch_code} inventory posting",
                "JournalDate": journal_date,
                "JournalLines": [
                    {
                        "Description": "Finished Goods",
                        "LineAmount": float(amount),
                        "AccountCode": debit_account,
                    },
                    {
                        "Description": "Raw Materials",
                        "LineAmount": -float(amount),
                        "AccountCode": credit_account,
                    },
                ],
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Xero-tenant-id": tenant_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = f"{API_BASE}/ManualJournals"

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        journal = result["ManualJournals"][0]

        _log_sync("Journal", batch_code, "PUSH", "OK", f"Journal posted: ${amount}")

        return journal

    except Exception as e:
        _log_sync("Journal", batch_code, "PUSH", "ERROR", str(e))
        raise


def pull_contacts() -> int:
    """
    Pull contacts from Xero and upsert into TPManuf database.

    Returns:
        Number of contacts pulled
    """
    access_token, tenant_id = _get_access_token_and_tenant()

    url = f"{API_BASE}/Contacts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Xero-tenant-id": tenant_id,
        "Accept": "application/json",
    }

    params = {
        "includeArchived": False,
        "where": "IsSupplier==true OR IsCustomer==true",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()

        contacts = result.get("Contacts", [])
        count = 0

        with get_session() as session:
            for contact in contacts:
                name = contact.get("Name", "").strip()
                if not name:
                    continue

                contact_id = contact.get("ContactID")
                email = contact.get("EmailAddress", "")

                # Determine if supplier or customer
                is_supplier = contact.get("IsSupplier", False)
                is_customer = contact.get("IsCustomer", False)

                if is_supplier:
                    # Upsert as supplier
                    supplier = (
                        session.query(Supplier)
                        .filter_by(xero_contact_id=contact_id)
                        .first()
                    )
                    if not supplier:
                        supplier = Supplier(
                            code=contact.get("ContactNumber")
                            or f"XERO-{contact_id[:8]}",
                            name=name,
                            email=email,
                            phone=contact.get("Phones", [{}])[0].get("PhoneNumber")
                            if contact.get("Phones")
                            else "",
                            xero_contact_id=contact_id,
                        )
                        session.add(supplier)
                    else:
                        supplier.name = name
                        supplier.email = email

                    count += 1

                if is_customer:
                    # Upsert as customer
                    customer = (
                        session.query(Customer)
                        .filter_by(xero_contact_id=contact_id)
                        .first()
                    )
                    if not customer:
                        customer = Customer(
                            code=contact.get("ContactNumber")
                            or f"XERO-{contact_id[:8]}",
                            name=name,
                            email=email,
                            phone=contact.get("Phones", [{}])[0].get("PhoneNumber")
                            if contact.get("Phones")
                            else "",
                            xero_contact_id=contact_id,
                        )
                        session.add(customer)
                    else:
                        customer.name = name
                        customer.email = email

                    if not is_supplier:  # Count only if not counted as supplier
                        count += 1

            session.commit()

        _log_sync("Contact", "*", "PULL", "OK", f"Pulled {count} contacts")

        return count

    except Exception as e:
        _log_sync("Contact", "*", "PULL", "ERROR", str(e))
        raise

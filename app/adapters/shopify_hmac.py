import hmac, hashlib, base64
from fastapi import Header, HTTPException

def verify_webhook_hmac(raw_body: bytes, shopify_hmac_sha256: str, secret: str) -> None:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
    computed = base64.b64encode(digest).decode()
    if not hmac.compare_digest(computed, shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid Shopify webhook HMAC")


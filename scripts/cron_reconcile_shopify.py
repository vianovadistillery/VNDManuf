"""
Example cron entry:
*/60 * * * * /usr/bin/python -m scripts.cron_reconcile_shopify
"""
# from app.adapters.db import SessionLocal
# from app.services.shopify_sync import ShopifySyncService


def main():
    # db = SessionLocal()
    # svc = ShopifySyncService(db)
    # print(svc.reconcile_all())
    print({"ok": True, "note": "stub reconcile"})


if __name__ == "__main__":
    main()

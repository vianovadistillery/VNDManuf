from typing import Iterable
from decimal import Decimal
from sqlalchemy.orm import Session

from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection
# Import your existing inventory helpers (FIFO, conversions, transactions)
# from app.services.inventory import consume_fifo, add_inventory_lot, write_inventory_txn

class AssemblyService:
    """
    Encapsulates assemble/disassemble operations.
    All quantities here are in canonical units (e.g., kg for liquids; counts for packages if canonicalized).
    """

    def __init__(self, db: Session):
        self.db = db

    def assemble(self, parent_product_id: str, parent_qty: Decimal, reason: str = "ASSEMBLE"):
        """
        Make parent product from children according to Assembly rows where parent=parent_product_id.
        1) For each child row: consume child stock = parent_qty * ratio (+loss_factor handling).
        2) Add parent stock (lot).
        3) Write inventory transactions.
        """
        # TODO: implement using your FIFO + conversions
        # children = self.db.query(Assembly).filter(Assembly.parent_product_id == parent_product_id).all()
        # for row in children: consume child
        # add parent lot
        # write inventory txn(s)
        pass

    def disassemble(self, parent_product_id: str, parent_qty: Decimal, reason: str = "DISASSEMBLE"):
        """
        Break parent product into children (use ratio; subtract loss_factor).
        """
        # TODO: implement using your FIFO + conversions
        pass


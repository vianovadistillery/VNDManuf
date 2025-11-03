"""Legacy ACSTK file parser for TPManuf migration.

Parses the QuickBASIC Random Access File format for the accessory stock file.
"""

import struct
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class AcstkRecord:
    """Represents a single record from the legacy acstk file."""

    # Product Description
    no: int
    search: str  # Product code/SKU
    ean13: int  # EAN-13 barcode (stored as CURRENCY)
    desc1: str  # Primary description
    desc2: str  # Secondary description
    suplr: str  # Supplier code
    size: str  # Size
    unit: str  # Unit code
    pack: int  # Package quantity
    dgflag: str  # Dangerous goods flag
    form: str  # Form code
    pkge: int  # Package type
    label: int  # Label type
    manu: int  # Manufacturer code
    active: str  # Active status ('Y'/'N')

    # Financial Description
    taxinc: str  # Tax included
    salestaxcde: str  # Sales tax code
    purcost: float  # Purchase cost
    purtax: float  # Purchase tax
    wholesalecost: float  # Wholesale cost
    disccdeone: str  # Discount code 1
    disccdetwo: str  # Discount code 2

    # Price codes
    wholesalecde: str
    retailcde: str
    countercde: str
    tradecde: str
    contractcde: str
    industrialcde: str
    distributorcde: str

    # Prices
    retail: float
    counter: float
    trade: float
    contract: float
    industrial: float
    distributor: float

    # Standard cost references
    suplr4stdcost: str
    search4stdcost: str

    # Stock holding
    cogs: float  # Cost of goods sold
    gpc: float  # Gross profit cost
    rmc: float  # Raw material cost
    gpr: float  # Gross profit ratio
    soh: int  # Stock on hand
    sohv: float  # Stock on hand value
    sip: int  # Stock in progress
    soo: int  # Stock on order
    sold: int  # Quantity sold
    date: str  # Last transaction date (YYYYMMDD)

    # Additional fields
    bulk: float
    lid: int
    pbox: int
    boxlbl: int

    @property
    def is_active(self) -> bool:
        """Convert active flag to boolean."""
        return self.active.upper() == "Y"

    @property
    def product_name(self) -> str:
        """Get full product name."""
        return f"{self.desc1.strip()} {self.desc2.strip()}".strip()

    @property
    def last_transaction_date(self) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not self.date or len(self.date) < 8:
            return None
        try:
            return datetime.strptime(self.date, "%Y%m%d")
        except ValueError:
            return None


class AcstkParser:
    """Parser for QuickBASIC Random Access File format."""

    RECORD_LENGTH = 256

    @staticmethod
    def parse_file(filepath: str) -> List[AcstkRecord]:
        """Parse entire acstk file and return list of records."""
        records = []

        with open(filepath, "rb") as f:
            while True:
                # Read record
                data = f.read(AcstkParser.RECORD_LENGTH)
                if not data:
                    break

                # Parse record
                record = AcstkParser._parse_record(data)
                if record:
                    records.append(record)

        return records

    @staticmethod
    def _parse_record(data: bytes) -> Optional[AcstkRecord]:
        """Parse a single 256-byte record."""
        if len(data) < AcstkParser.RECORD_LENGTH:
            return None

        try:
            # Unpack fixed-length fields
            # Format based on QuickBASIC TYPE definition
            # Note: Integer is 2 bytes, Single is 4 bytes, Currency is 8 bytes
            # Strings are fixed length with null termination

            offset = 0

            # Integers (2 bytes each)
            no = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2

            # Strings (fixed length, may be null-terminated)
            search = (
                data[offset : offset + 10].rstrip(b"\x00").decode("latin-1").strip()
            )
            offset += 10
            # EAN13 as CURRENCY (8 bytes, but we'll parse as long)
            ean13_bytes = data[offset : offset + 8]
            # CURRENCY in QuickBASIC is 8 bytes, parse as signed integer with 4 decimal places
            ean13_raw = struct.unpack("<q", ean13_bytes)[0]
            ean13 = ean13_raw / 10000
            offset += 8

            desc1 = data[offset : offset + 25].rstrip(b"\x00").decode("latin-1").strip()
            offset += 25
            desc2 = data[offset : offset + 10].rstrip(b"\x00").decode("latin-1").strip()
            offset += 10
            suplr = data[offset : offset + 5].rstrip(b"\x00").decode("latin-1").strip()
            offset += 5
            size = data[offset : offset + 3].rstrip(b"\x00").decode("latin-1").strip()
            offset += 3
            unit = data[offset : offset + 2].rstrip(b"\x00").decode("latin-1").strip()
            offset += 2

            # More integers
            pack = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2

            # More strings
            dgflag = data[offset : offset + 1].decode("latin-1")
            offset += 1
            form = data[offset : offset + 4].rstrip(b"\x00").decode("latin-1").strip()
            offset += 4

            # More integers
            pkge = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            label = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            manu = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            active = data[offset : offset + 1].decode("latin-1")
            offset += 1

            # Tax fields (strings)
            taxinc = data[offset : offset + 1].decode("latin-1")
            offset += 1
            salestaxcde = data[offset : offset + 1].decode("latin-1")
            offset += 1

            # Singles (4 bytes float)
            purcost = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            purtax = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            wholesalecost = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4

            # More strings
            disccdeone = data[offset : offset + 1].decode("latin-1")
            offset += 1
            disccdetwo = data[offset : offset + 1].decode("latin-1")
            offset += 1

            # Price codes
            wholesalecde = data[offset : offset + 1].decode("latin-1")
            offset += 1
            retailcde = data[offset : offset + 1].decode("latin-1")
            offset += 1
            countercde = data[offset : offset + 1].decode("latin-1")
            offset += 1
            tradecde = data[offset : offset + 1].decode("latin-1")
            offset += 1
            contractcde = data[offset : offset + 1].decode("latin-1")
            offset += 1
            industrialcde = data[offset : offset + 1].decode("latin-1")
            offset += 1
            distributorcde = data[offset : offset + 1].decode("latin-1")
            offset += 1

            # Prices (Singles)
            retail = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            counter = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            trade = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            contract = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            industrial = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            distributor = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4

            # Standard cost references
            suplr4stdcost = (
                data[offset : offset + 5].rstrip(b"\x00").decode("latin-1").strip()
            )
            offset += 5
            search4stdcost = (
                data[offset : offset + 10].rstrip(b"\x00").decode("latin-1").strip()
            )
            offset += 10

            # More Singles
            cogs = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            gpc = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            rmc = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            gpr = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4

            # Stock integers
            soh = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            sohv = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            sip = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            soo = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            sold = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2

            # Date string
            date = data[offset : offset + 8].rstrip(b"\x00").decode("latin-1")
            offset += 8

            # Additional fields
            bulk = struct.unpack("<f", data[offset : offset + 4])[0]
            offset += 4
            lid = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            pbox = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2
            boxlbl = struct.unpack("<h", data[offset : offset + 2])[0]
            offset += 2

            # Filler (69 bytes, not used)
            # offset += 69

            return AcstkRecord(
                no=no,
                search=search,
                ean13=ean13,
                desc1=desc1,
                desc2=desc2,
                suplr=suplr,
                size=size,
                unit=unit,
                pack=pack,
                dgflag=dgflag,
                form=form,
                pkge=pkge,
                label=label,
                manu=manu,
                active=active,
                taxinc=taxinc,
                salestaxcde=salestaxcde,
                purcost=purcost,
                purtax=purtax,
                wholesalecost=wholesalecost,
                disccdeone=disccdeone,
                disccdetwo=disccdetwo,
                wholesalecde=wholesalecde,
                retailcde=retailcde,
                countercde=countercde,
                tradecde=tradecde,
                contractcde=contractcde,
                industrialcde=industrialcde,
                distributorcde=distributorcde,
                retail=retail,
                counter=counter,
                trade=trade,
                contract=contract,
                industrial=industrial,
                distributor=distributor,
                suplr4stdcost=suplr4stdcost,
                search4stdcost=search4stdcost,
                cogs=cogs,
                gpc=gpc,
                rmc=rmc,
                gpr=gpr,
                soh=soh,
                sohv=sohv,
                sip=sip,
                soo=soo,
                sold=sold,
                date=date,
                bulk=bulk,
                lid=lid,
                pbox=pbox,
                boxlbl=boxlbl,
            )
        except Exception as e:
            print(f"Error parsing record: {e}")
            return None

    @staticmethod
    def convert_to_modern_product(record: AcstkRecord) -> Dict:
        """Convert legacy record to modern product format."""
        return {
            "sku": record.search,
            "name": record.product_name,
            "description": f"Size: {record.size}, Unit: {record.unit}",
            "is_active": record.is_active,
        }

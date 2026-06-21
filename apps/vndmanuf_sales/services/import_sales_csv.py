"""CSV importer for sales orders and delivery dockets."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.db.models import (
    DeliveryDocket,
    DeliveryDocketLine,
    Product,
    ProductVariant,
)
from apps.vndmanuf_sales.models import (
    Customer,
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
    SalesOrderSource,
    SalesOrderStatus,
)
from apps.vndmanuf_sales.services.customer_mapping import (
    CustomerMappingService,
    names_refer_to_same_entity,
    normalize_customer_key,
)
from apps.vndmanuf_sales.services.pricing import PriceResolution, PricingService
from apps.vndmanuf_sales.services.totals import TotalsService

SALES_REQUIRED_COLUMNS = {
    "order_date",
    "channel",
    "customer",
    "product_code",
    "qty",
}

DOCKET_REQUIRED_COLUMNS = {
    "docket_number",
    "delivery_date",
    "customer",
    "product_code",
    "delivered_qty",
}


class ImportFormat(str, Enum):
    SALES = "sales"
    DOCKET = "docket"


def detect_csv_format(fieldnames: Optional[List[str]]) -> ImportFormat:
    """Detect CSV layout from header row."""
    cols = {c.strip().lower() for c in (fieldnames or [])}
    if "docket_number" in cols and "delivered_qty" in cols:
        return ImportFormat.DOCKET
    missing = SALES_REQUIRED_COLUMNS - cols
    if missing:
        raise ValueError(
            "Unrecognised CSV format. Expected sales columns "
            f"({', '.join(sorted(SALES_REQUIRED_COLUMNS))}) or delivery docket columns "
            f"({', '.join(sorted(DOCKET_REQUIRED_COLUMNS))}). "
            f"Missing: {', '.join(sorted(missing))}"
        )
    return ImportFormat.SALES


def _normalize_code(value: str) -> str:
    return value.strip().upper().replace(" ", "_")


def _decimal(value: str | None) -> Decimal:
    if value is None or value == "":
        return Decimal("0")
    return Decimal(str(value).strip())


def _parse_date(value: str) -> datetime:
    value = (value or "").strip()
    if not value:
        raise ValueError("Date is required")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Unrecognised date '{value}'") from exc


@dataclass
class ImportRow:
    raw: Dict[str, str]
    order_date: datetime
    channel: str
    customer: str
    site_name: Optional[str]
    site_suburb: Optional[str] = None
    site_state: Optional[str] = None
    site_postcode: Optional[str] = None
    product_code: str = ""
    qty: Decimal = Decimal("0")
    ordered_qty: Optional[Decimal] = None
    unit: Optional[str] = None
    unit_price_ex_gst: Optional[Decimal] = None
    unit_price_inc_gst: Optional[Decimal] = None
    order_ref: Optional[str] = None
    po_number: Optional[str] = None
    notes: Optional[str] = None
    docket_number: Optional[str] = None
    delivery_date: Optional[datetime] = None
    attention: Optional[str] = None


@dataclass
class ImportOrderResult:
    order_ref: str
    customer: str
    lines: int
    status: str
    message: str
    docket_number: Optional[str] = None


@dataclass
class ImportSummary:
    format: str = ImportFormat.SALES.value
    orders_inserted: int = 0
    orders_updated: int = 0
    dockets_created: int = 0
    lines_processed: int = 0
    errors: List[str] = field(default_factory=list)
    order_results: List[ImportOrderResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "format": self.format,
            "orders_inserted": self.orders_inserted,
            "orders_updated": self.orders_updated,
            "dockets_created": self.dockets_created,
            "lines_processed": self.lines_processed,
            "errors": self.errors,
            "order_results": [
                {
                    "order_ref": r.order_ref,
                    "customer": r.customer,
                    "lines": r.lines,
                    "status": r.status,
                    "message": r.message,
                    "docket_number": r.docket_number,
                }
                for r in self.order_results
            ],
        }


def decode_csv_bytes(data: bytes) -> str:
    """Decode CSV bytes from upload or disk; Excel on Windows often uses cp1252."""
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


@dataclass
class ImportPreviewGroup:
    group_key: str
    order_ref: str
    customer_csv: str
    customer_resolved: str
    customer_mapped: bool
    customer_missing: bool
    line_count: int
    duplicate_in_db: bool
    duplicate_in_csv: bool
    flags: str
    include_by_default: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "group_key": self.group_key,
            "order_ref": self.order_ref,
            "customer_csv": self.customer_csv,
            "customer_resolved": self.customer_resolved,
            "customer_mapped": self.customer_mapped,
            "customer_missing": self.customer_missing,
            "line_count": self.line_count,
            "duplicate_in_db": self.duplicate_in_db,
            "duplicate_in_csv": self.duplicate_in_csv,
            "flags": self.flags,
            "include_by_default": self.include_by_default,
        }


@dataclass
class ImportPreview:
    format: str
    filename: str
    groups: List[ImportPreviewGroup] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "format": self.format,
            "filename": self.filename,
            "groups": [g.to_dict() for g in self.groups],
            "errors": self.errors,
            "default_selected_keys": [
                g.group_key for g in self.groups if g.include_by_default
            ],
        }


def sales_group_key(
    order_date: datetime, customer: str, order_ref: Optional[str]
) -> str:
    ref = (order_ref or "").strip()
    return f"sales|{order_date.date().isoformat()}|{customer.strip()}|{ref}"


def docket_group_key(docket_number: str) -> str:
    return f"docket|{docket_number.strip()}"


class SalesCSVImporter:
    """Import sales orders from standard sales CSV or delivery-docket CSV."""

    def __init__(self, db: Session):
        self.db = db
        self.pricing = PricingService(db)
        self.totals = TotalsService(db)
        self.customer_mapping = CustomerMappingService(db)

    def import_file(
        self,
        file_path: Path | str,
        *,
        allow_create: bool = False,
        pricebook_id: Optional[str] = None,
        import_format: Union[ImportFormat, str, None] = None,
        create_delivery_docket: bool = True,
    ) -> ImportSummary:
        text = decode_csv_bytes(Path(file_path).read_bytes())
        return self.import_text(
            text,
            allow_create=allow_create,
            pricebook_id=pricebook_id,
            import_format=import_format,
            create_delivery_docket=create_delivery_docket,
        )

    def import_text(
        self,
        text: str,
        *,
        allow_create: bool = False,
        pricebook_id: Optional[str] = None,
        import_format: Union[ImportFormat, str, None] = None,
        create_delivery_docket: bool = True,
    ) -> ImportSummary:
        rows, fmt = self._parse_csv_text(text, import_format=import_format)
        if fmt == ImportFormat.DOCKET:
            return self._import_docket_rows(
                rows,
                allow_create=allow_create,
                pricebook_id=pricebook_id,
                create_delivery_docket=create_delivery_docket,
            )
        return self.import_rows(
            rows,
            allow_create=allow_create,
            pricebook_id=pricebook_id,
        )

    def build_import_preview(
        self,
        text: str,
        *,
        allow_create: bool = False,
        import_format: Union[ImportFormat, str, None] = None,
        filename: str = "",
    ) -> ImportPreview:
        """Parse CSV and build a review list with customer mapping and duplicate flags."""
        try:
            rows, fmt = self._parse_csv_text(text, import_format=import_format)
        except ValueError as exc:
            return ImportPreview(
                format=ImportFormat.SALES.value,
                filename=filename,
                errors=[str(exc)],
            )

        preview = ImportPreview(format=fmt.value, filename=filename)
        if fmt == ImportFormat.DOCKET:
            grouped = self._group_docket_rows(rows)
            for docket_number, group_rows in grouped.items():
                preview.groups.append(
                    self._preview_docket_group(docket_number, group_rows, allow_create)
                )
        else:
            grouped = self._group_sales_rows(rows)
            for key, group_rows in grouped.items():
                order_date, customer_name, order_ref = key
                preview.groups.append(
                    self._preview_sales_group(
                        order_date,
                        customer_name,
                        order_ref,
                        group_rows,
                        allow_create,
                    )
                )
        return preview

    def import_text_selected(
        self,
        text: str,
        selected_group_keys: Iterable[str],
        *,
        allow_create: bool = False,
        pricebook_id: Optional[str] = None,
        import_format: Union[ImportFormat, str, None] = None,
        create_delivery_docket: bool = True,
    ) -> ImportSummary:
        """Import only the order/docket groups the user selected in the preview step."""
        selected = {k for k in selected_group_keys if k}
        if not selected:
            rows, fmt = self._parse_csv_text(text, import_format=import_format)
            return ImportSummary(
                format=fmt.value,
                errors=["No records selected for import"],
            )

        rows, fmt = self._parse_csv_text(text, import_format=import_format)
        filtered: List[ImportRow] = []
        if fmt == ImportFormat.DOCKET:
            grouped = self._group_docket_rows(rows)
            for docket_number, group_rows in grouped.items():
                if docket_group_key(docket_number) in selected:
                    filtered.extend(group_rows)
        else:
            grouped = self._group_sales_rows(rows)
            for key, group_rows in grouped.items():
                order_date, customer_name, order_ref = key
                if sales_group_key(order_date, customer_name, order_ref) in selected:
                    filtered.extend(group_rows)

        if not filtered:
            return ImportSummary(
                format=fmt.value,
                errors=["Selected records did not match any rows in the file"],
            )

        if fmt == ImportFormat.DOCKET:
            return self._import_docket_rows(
                filtered,
                allow_create=allow_create,
                pricebook_id=pricebook_id,
                create_delivery_docket=create_delivery_docket,
            )
        return self.import_rows(
            filtered,
            allow_create=allow_create,
            pricebook_id=pricebook_id,
        )

    def import_rows(
        self,
        rows: Iterable[ImportRow],
        *,
        allow_create: bool = False,
        pricebook_id: Optional[str] = None,
    ) -> ImportSummary:
        grouped = self._group_sales_rows(rows)
        summary = ImportSummary(format=ImportFormat.SALES.value)

        for key, order_rows in grouped.items():
            order_date, customer_name, order_ref = key
            label = order_ref or "<no-ref>"
            try:
                with self.db.begin_nested():
                    order, created = self._get_or_create_order(
                        order_date=order_date,
                        customer_name=customer_name,
                        order_ref=order_ref,
                        allow_create=allow_create,
                        channel_name=order_rows[0].channel,
                        site_name=order_rows[0].site_name,
                        site_suburb=order_rows[0].site_suburb,
                        site_state=order_rows[0].site_state,
                        site_postcode=order_rows[0].site_postcode,
                        po_number=order_rows[0].po_number,
                    )
                    line_count = self._apply_order_lines(
                        order, order_rows, pricebook_id=pricebook_id
                    )
                    order.notes = order_rows[0].notes or order.notes
                    order.pricebook_id = pricebook_id
                    self.totals.refresh_order_totals(order)

                if created:
                    summary.orders_inserted += 1
                    status = "inserted"
                else:
                    summary.orders_updated += 1
                    status = "updated"
                summary.lines_processed += line_count
                summary.order_results.append(
                    ImportOrderResult(
                        order_ref=label,
                        customer=customer_name,
                        lines=line_count,
                        status=status,
                        message=f"{line_count} line(s) imported",
                    )
                )
            except Exception as exc:  # noqa: BLE001
                self.db.rollback()
                msg = f"Order {label} on {order_date.date()} failed: {exc}"
                summary.errors.append(msg)
                summary.order_results.append(
                    ImportOrderResult(
                        order_ref=label,
                        customer=customer_name,
                        lines=0,
                        status="error",
                        message=str(exc),
                    )
                )

        return summary

    def _import_docket_rows(
        self,
        rows: Iterable[ImportRow],
        *,
        allow_create: bool,
        pricebook_id: Optional[str],
        create_delivery_docket: bool,
    ) -> ImportSummary:
        grouped = self._group_docket_rows(rows)
        summary = ImportSummary(format=ImportFormat.DOCKET.value)

        for docket_number, docket_rows in grouped.items():
            first = docket_rows[0]
            try:
                with self.db.begin_nested():
                    existing_docket = self._find_existing_docket(docket_number)
                    order_ref = docket_number
                    order, created = self._get_or_create_order(
                        order_date=first.order_date,
                        customer_name=first.customer,
                        order_ref=order_ref,
                        allow_create=allow_create,
                        channel_name=first.channel or "DIRECT",
                        site_name=first.site_name or first.site_suburb,
                        site_suburb=first.site_suburb,
                        site_state=first.site_state,
                        site_postcode=first.site_postcode,
                        po_number=first.po_number,
                    )
                    if first.po_number:
                        order.po_number = first.po_number
                    note_parts = []
                    if first.attention:
                        note_parts.append(f"Attention: {first.attention}")
                    if first.notes:
                        note_parts.append(first.notes)
                    if note_parts:
                        order.notes = "\n".join(note_parts)

                    line_count = self._apply_order_lines(
                        order, docket_rows, pricebook_id=pricebook_id
                    )
                    order.pricebook_id = pricebook_id
                    self.totals.refresh_order_totals(order)

                    docket_created = False
                    if create_delivery_docket:
                        docket_created = self._upsert_delivery_docket(
                            order=order,
                            docket_number=docket_number,
                            docket_rows=docket_rows,
                            existing_docket=existing_docket,
                        )

                if created:
                    summary.orders_inserted += 1
                    status = "inserted"
                else:
                    summary.orders_updated += 1
                    status = "updated"
                if docket_created:
                    summary.dockets_created += 1
                summary.lines_processed += line_count
                summary.order_results.append(
                    ImportOrderResult(
                        order_ref=order_ref,
                        customer=first.customer,
                        lines=line_count,
                        status=status,
                        message=(
                            f"{line_count} line(s); docket {docket_number}"
                            + (" created" if docket_created else " linked")
                        ),
                        docket_number=docket_number,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                self.db.rollback()
                msg = f"Docket {docket_number} failed: {exc}"
                summary.errors.append(msg)
                summary.order_results.append(
                    ImportOrderResult(
                        order_ref=docket_number,
                        customer=first.customer,
                        lines=0,
                        status="error",
                        message=str(exc),
                        docket_number=docket_number,
                    )
                )

        return summary

    def _parse_csv_text(
        self,
        text: str,
        *,
        import_format: Union[ImportFormat, str, None],
    ) -> Tuple[List[ImportRow], ImportFormat]:
        buffer = io.StringIO(text)
        reader = csv.DictReader(buffer)
        fieldnames = reader.fieldnames or []
        fmt = (
            ImportFormat(import_format)
            if import_format
            else detect_csv_format(fieldnames)
        )
        if fmt == ImportFormat.DOCKET:
            missing = DOCKET_REQUIRED_COLUMNS - {c.strip().lower() for c in fieldnames}
            if missing:
                raise ValueError(
                    f"Missing required docket columns: {', '.join(sorted(missing))}"
                )
            rows = [self._parse_docket_row(raw) for raw in reader]
        else:
            missing = SALES_REQUIRED_COLUMNS - {c.strip().lower() for c in fieldnames}
            if missing:
                raise ValueError(
                    f"Missing required sales columns: {', '.join(sorted(missing))}"
                )
            rows = [self._parse_sales_row(raw) for raw in reader]
        return rows, fmt

    def _parse_sales_row(self, raw: Dict[str, str]) -> ImportRow:
        lowered = {k.strip().lower(): v for k, v in raw.items()}
        try:
            return ImportRow(
                raw=raw,
                order_date=_parse_date(lowered["order_date"]),
                channel=(lowered.get("channel") or "").strip(),
                customer=(lowered.get("customer") or "").strip(),
                site_name=lowered.get("site_name") or None,
                site_suburb=lowered.get("site_suburb") or None,
                site_state=lowered.get("site_state") or None,
                site_postcode=lowered.get("site_postcode") or None,
                product_code=(lowered.get("product_code") or "").strip(),
                qty=_decimal(lowered.get("qty")),
                unit=(lowered.get("unit") or "unit").strip() or "unit",
                unit_price_ex_gst=_decimal(lowered["unit_price_ex_gst"])
                if lowered.get("unit_price_ex_gst")
                else None,
                unit_price_inc_gst=_decimal(lowered["unit_price_inc_gst"])
                if lowered.get("unit_price_inc_gst")
                else None,
                order_ref=lowered.get("order_ref") or None,
                po_number=lowered.get("po_number") or None,
                notes=lowered.get("notes") or None,
            )
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Failed to parse sales row {raw}: {exc}") from exc

    def _parse_docket_row(self, raw: Dict[str, str]) -> ImportRow:
        lowered = {k.strip().lower(): v for k, v in raw.items()}
        try:
            delivery_date = _parse_date(lowered["delivery_date"])
            order_date_raw = lowered.get("order_date") or lowered["delivery_date"]
            order_date = _parse_date(order_date_raw)
            delivered = _decimal(lowered.get("delivered_qty"))
            ordered = (
                _decimal(lowered.get("ordered_qty"))
                if lowered.get("ordered_qty")
                else None
            )
            qty = delivered if delivered > 0 else (ordered or Decimal("0"))
            return ImportRow(
                raw=raw,
                order_date=order_date,
                delivery_date=delivery_date,
                channel=(lowered.get("channel") or "DIRECT").strip(),
                customer=(lowered.get("customer") or "").strip(),
                site_name=lowered.get("site_name") or None,
                site_suburb=lowered.get("site_suburb") or None,
                site_state=lowered.get("site_state") or None,
                site_postcode=lowered.get("site_postcode") or None,
                product_code=(lowered.get("product_code") or "").strip(),
                qty=qty,
                ordered_qty=ordered,
                unit=(lowered.get("unit") or "EA").strip() or "EA",
                unit_price_ex_gst=_decimal(lowered["unit_price_ex_gst"])
                if lowered.get("unit_price_ex_gst")
                else None,
                unit_price_inc_gst=_decimal(lowered["unit_price_inc_gst"])
                if lowered.get("unit_price_inc_gst")
                else None,
                order_ref=lowered.get("docket_number") or None,
                po_number=lowered.get("po_number") or None,
                notes=lowered.get("notes") or None,
                docket_number=(lowered.get("docket_number") or "").strip(),
                attention=lowered.get("attention") or None,
            )
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Failed to parse docket row {raw}: {exc}") from exc

    def _group_sales_rows(
        self, rows: Iterable[ImportRow]
    ) -> Dict[Tuple[datetime, str, Optional[str]], List[ImportRow]]:
        grouped: Dict[Tuple[datetime, str, Optional[str]], List[ImportRow]] = {}
        for row in rows:
            key = (row.order_date, row.customer, row.order_ref)
            grouped.setdefault(key, []).append(row)
        return grouped

    def _group_docket_rows(
        self, rows: Iterable[ImportRow]
    ) -> Dict[str, List[ImportRow]]:
        grouped: Dict[str, List[ImportRow]] = {}
        for row in rows:
            if not row.docket_number:
                raise ValueError("Each docket row must include docket_number")
            grouped.setdefault(row.docket_number, []).append(row)
        return grouped

    def _duplicate_lines_in_group(self, group_rows: List[ImportRow]) -> List[str]:
        seen: set[str] = set()
        duplicates: List[str] = []
        for row in group_rows:
            code = (row.product_code or "").strip().lower()
            if not code:
                continue
            if code in seen and code not in duplicates:
                duplicates.append(row.product_code)
            seen.add(code)
        return duplicates

    def _customer_preview_info(
        self, csv_name: str, *, allow_create: bool
    ) -> Tuple[str, bool, bool, Optional[str]]:
        """Return resolved name, mapped flag, missing flag, customer_id."""
        cleaned = (csv_name or "").strip()
        customer = self.customer_mapping.resolve_customer(cleaned)
        if customer:
            mapped = normalize_customer_key(cleaned) != normalize_customer_key(
                customer.name
            )
            return customer.name, mapped, False, customer.id
        if allow_create:
            return cleaned, False, False, None
        return cleaned, False, True, None

    def _preview_sales_group(
        self,
        order_date: datetime,
        customer_name: str,
        order_ref: Optional[str],
        group_rows: List[ImportRow],
        allow_create: bool,
    ) -> ImportPreviewGroup:
        gkey = sales_group_key(order_date, customer_name, order_ref)
        label = order_ref or "<no-ref>"
        resolved, mapped, missing, customer_id = self._customer_preview_info(
            customer_name, allow_create=allow_create
        )
        dup_lines = self._duplicate_lines_in_group(group_rows)
        duplicate_in_db = False
        if customer_id and order_ref:
            duplicate_in_db = (
                self._find_existing_order(customer_id, order_date, order_ref)
                is not None
            )
        flags: List[str] = []
        if mapped:
            flags.append("Customer mapped")
        if missing:
            flags.append("Customer not found")
        if duplicate_in_db:
            flags.append("Already in database")
        if dup_lines:
            flags.append(f"Duplicate lines ({', '.join(dup_lines)})")
        site_flag = self._site_preview_flag(
            customer_id, resolved, group_rows[0].site_name, allow_create
        )
        if site_flag:
            flags.append(site_flag)
        include = not missing and not duplicate_in_db and not dup_lines
        return ImportPreviewGroup(
            group_key=gkey,
            order_ref=label,
            customer_csv=customer_name,
            customer_resolved=resolved,
            customer_mapped=mapped,
            customer_missing=missing,
            line_count=len(group_rows),
            duplicate_in_db=duplicate_in_db,
            duplicate_in_csv=bool(dup_lines),
            flags="; ".join(flags) if flags else "Ready",
            include_by_default=include,
        )

    def _site_preview_flag(
        self,
        customer_id: Optional[str],
        customer_resolved: str,
        site_csv: Optional[str],
        allow_create: bool,
    ) -> str:
        cleaned = (site_csv or "").strip()
        if not cleaned:
            return ""
        if names_refer_to_same_entity(cleaned, customer_resolved):
            return "Site matches customer"
        if not customer_id:
            if allow_create:
                return f"Site '{cleaned}' will be created"
            return f"Site '{cleaned}' omitted until customer exists"
        customer = self.db.get(Customer, customer_id)
        if not customer:
            return ""
        if self.customer_mapping.resolve_site_alias(customer.id, cleaned):
            return "Site mapped"
        if self.customer_mapping.resolve_site(customer, cleaned, allow_create=False):
            return "Site matched"
        if allow_create:
            return f"Site '{cleaned}' will be created"
        return f"Site '{cleaned}' omitted (import without site)"

    def _preview_docket_group(
        self,
        docket_number: str,
        group_rows: List[ImportRow],
        allow_create: bool,
    ) -> ImportPreviewGroup:
        gkey = docket_group_key(docket_number)
        first = group_rows[0]
        resolved, mapped, missing, customer_id = self._customer_preview_info(
            first.customer, allow_create=allow_create
        )
        dup_lines = self._duplicate_lines_in_group(group_rows)
        duplicate_in_db = self._find_existing_docket(docket_number) is not None
        if not duplicate_in_db and customer_id:
            duplicate_in_db = (
                self._find_existing_order(customer_id, first.order_date, docket_number)
                is not None
            )
        flags: List[str] = []
        if mapped:
            flags.append("Customer mapped")
        if missing:
            flags.append("Customer not found")
        if duplicate_in_db:
            flags.append("Already in database")
        if dup_lines:
            flags.append(f"Duplicate lines ({', '.join(dup_lines)})")
        site_flag = self._site_preview_flag(
            customer_id, resolved, first.site_name, allow_create
        )
        if site_flag:
            flags.append(site_flag)
        include = not missing and not duplicate_in_db and not dup_lines
        return ImportPreviewGroup(
            group_key=gkey,
            order_ref=docket_number,
            customer_csv=first.customer,
            customer_resolved=resolved,
            customer_mapped=mapped,
            customer_missing=missing,
            line_count=len(group_rows),
            duplicate_in_db=duplicate_in_db,
            duplicate_in_csv=bool(dup_lines),
            flags="; ".join(flags) if flags else "Ready",
            include_by_default=include,
        )

    def _apply_order_lines(
        self,
        order: SalesOrder,
        rows: Iterable[ImportRow],
        *,
        pricebook_id: Optional[str],
    ) -> int:
        if order.lines:
            order.lines.clear()
        count = 0
        for row in rows:
            product = self._lookup_product(
                row.product_code, description=row.raw.get("description")
            )
            resolution = self._resolve_price(
                product_id=product.id,
                row=row,
                pricebook_id=pricebook_id,
                customer_id=order.customer_id,
            )
            line_totals = self.totals.compute_line_totals(
                qty=row.qty,
                unit_price_ex_gst=resolution.unit_price_ex_gst,
                unit_price_inc_gst=resolution.unit_price_inc_gst,
            )
            order.lines.append(
                SalesOrderLine(
                    product_id=product.id,
                    qty=row.qty,
                    uom=(row.unit or "unit").lower(),
                    unit_price_ex_gst=resolution.unit_price_ex_gst,
                    unit_price_inc_gst=resolution.unit_price_inc_gst,
                    discount_ex_gst=line_totals.discount_ex_gst,
                    line_total_ex_gst=line_totals.line_total_ex_gst,
                    line_total_inc_gst=line_totals.line_total_inc_gst,
                    sequence=len(order.lines) + 1,
                    tax_rate=resolution.gst_rate,
                )
            )
            count += 1
        return count

    def _upsert_delivery_docket(
        self,
        *,
        order: SalesOrder,
        docket_number: str,
        docket_rows: List[ImportRow],
        existing_docket: Optional[DeliveryDocket],
    ) -> bool:
        first = docket_rows[0]
        if existing_docket:
            docket = existing_docket
            docket.sales_order_id = order.id
            docket.customer_id = order.customer_id
            docket.delivery_date = first.delivery_date or first.order_date
            docket.docket_date = first.delivery_date or first.order_date
            docket.lines.clear()
            created = False
        else:
            docket = DeliveryDocket(
                customer_id=order.customer_id,
                sales_order_id=order.id,
                docket_number=docket_number,
                docket_date=first.delivery_date or first.order_date,
                delivery_date=first.delivery_date or first.order_date,
                status="DELIVERED",
                notes=order.notes,
            )
            self.db.add(docket)
            self.db.flush()
            created = True

        for seq, row in enumerate(docket_rows, 1):
            product = self._lookup_product(
                row.product_code, description=row.raw.get("description")
            )
            order_line = next(
                (line for line in order.lines if line.product_id == product.id),
                None,
            )
            docket.lines.append(
                DeliveryDocketLine(
                    docket_id=docket.id,
                    product_id=product.id,
                    quantity=row.qty,
                    ordered_quantity=row.ordered_qty or row.qty,
                    unit_price=getattr(order_line, "unit_price_ex_gst", None),
                    uom=(row.unit or "EA").lower(),
                    sequence=seq,
                )
            )
        return created

    def _get_or_create_order(
        self,
        *,
        order_date: datetime,
        customer_name: str,
        order_ref: Optional[str],
        allow_create: bool,
        channel_name: str,
        site_name: Optional[str],
        site_suburb: Optional[str] = None,
        site_state: Optional[str] = None,
        site_postcode: Optional[str] = None,
        po_number: Optional[str] = None,
    ) -> Tuple[SalesOrder, bool]:
        customer = self._get_or_create_customer(
            customer_name, allow_create=allow_create
        )
        channel = self._get_or_create_channel(channel_name, allow_create=allow_create)
        site = None
        if site_name or site_suburb:
            site = self.customer_mapping.resolve_site(
                customer,
                site_name or site_suburb or customer_name,
                allow_create=allow_create,
                suburb=site_suburb,
                state=site_state,
                postcode=site_postcode,
            )

        existing = self._find_existing_order(customer.id, order_date, order_ref)
        if existing:
            existing.channel_id = channel.id
            existing.customer_site_id = site.id if site else None
            existing.status = SalesOrderStatus.CONFIRMED.value
            existing.source = SalesOrderSource.IMPORTED.value
            existing.order_date = order_date
            if po_number:
                existing.po_number = po_number
            existing.lines.clear()
            return existing, False

        order = SalesOrder(
            customer_id=customer.id,
            channel_id=channel.id,
            customer_site_id=site.id if site else None,
            order_ref=order_ref,
            po_number=po_number,
            status=SalesOrderStatus.CONFIRMED.value,
            source=SalesOrderSource.IMPORTED.value,
            order_date=order_date,
        )
        self.db.add(order)
        self.db.flush()
        return order, True

    def _find_existing_order(
        self,
        customer_id: str,
        order_date: datetime,
        order_ref: Optional[str],
    ) -> Optional[SalesOrder]:
        if not order_ref:
            return None
        stmt = (
            select(SalesOrder)
            .where(
                SalesOrder.customer_id == customer_id,
                func.date(SalesOrder.order_date) == order_date.date(),
                SalesOrder.order_ref == order_ref,
                SalesOrder.deleted_at.is_(None),
            )
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _find_existing_docket(self, docket_number: str) -> Optional[DeliveryDocket]:
        stmt = (
            select(DeliveryDocket)
            .where(
                func.lower(DeliveryDocket.docket_number) == docket_number.lower(),
                DeliveryDocket.deleted_at.is_(None),
            )
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _lookup_product(
        self, product_code: str, *, description: Optional[str] = None
    ) -> Product:
        code = (product_code or "").strip()
        if not code and description:
            code = description.strip()
        if not code:
            raise ValueError("Product code is required")

        stmt = select(Product).where(
            func.lower(Product.sku) == code.lower(),
            Product.deleted_at.is_(None),
        )
        product = self.db.execute(stmt).scalar_one_or_none()
        if not product:
            stmt = select(Product).where(
                func.lower(Product.name) == code.lower(),
                Product.deleted_at.is_(None),
            )
            product = self.db.execute(stmt).scalar_one_or_none()
        if not product:
            variant = self.db.execute(
                select(ProductVariant).where(
                    func.lower(ProductVariant.variant_code) == code.lower(),
                    ProductVariant.deleted_at.is_(None),
                )
            ).scalar_one_or_none()
            if variant:
                product = self.db.get(Product, variant.product_id)
        if not product and description:
            stmt = select(Product).where(
                Product.name.ilike(f"%{description.strip()}%"),
                Product.deleted_at.is_(None),
            )
            product = self.db.execute(stmt).limit(1).scalar_one_or_none()
        if not product:
            raise ValueError(f"Product with code '{code}' not found")
        return product

    def _resolve_price(
        self,
        *,
        product_id: str,
        row: ImportRow,
        pricebook_id: Optional[str],
        customer_id: Optional[str],
    ) -> PriceResolution:
        if row.unit_price_ex_gst or row.unit_price_inc_gst:
            ex_price = row.unit_price_ex_gst
            inc_price = row.unit_price_inc_gst
            if not inc_price or not ex_price:
                ex_price, inc_price = self.pricing.compute_inc_gst(
                    unit_price_ex_gst=ex_price,
                    unit_price_inc_gst=inc_price,
                )
            return PriceResolution(
                unit_price_ex_gst=ex_price,
                unit_price_inc_gst=inc_price,
                gst_rate=self.pricing.default_gst_rate,
                source="csv_override",
            )

        return self.pricing.resolve_price(
            product_id,
            order_date=row.order_date.date(),
            pricebook_id=pricebook_id,
            customer_id=customer_id,
        )

    def _get_or_create_channel(self, name: str, *, allow_create: bool) -> SalesChannel:
        code = _normalize_code(name or "UNKNOWN")
        channel = self.db.execute(
            select(SalesChannel).where(
                func.lower(SalesChannel.code) == code.lower(),
                SalesChannel.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if channel:
            return channel
        if not allow_create:
            raise ValueError(
                f"Sales channel '{name}' does not exist (enable allow-create)"
            )
        channel = SalesChannel(code=code, name=name or code.title())
        self.db.add(channel)
        self.db.flush()
        return channel

    def _get_or_create_customer(self, name: str, *, allow_create: bool) -> Customer:
        customer = self.customer_mapping.resolve_customer(name)
        if customer:
            return customer
        if not allow_create:
            raise ValueError(
                f"Customer '{name}' does not exist (enable allow-create or add a name mapping)"
            )
        code = _normalize_code(name)
        customer = Customer(code=code, name=name)
        self.db.add(customer)
        self.db.flush()
        return customer

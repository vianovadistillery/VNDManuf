from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    SKU,
    Brand,
    CartonSpec,
    Company,
    Location,
    PackageSpec,
    PackSpec,
    PriceObservation,
    Product,
    SKUCarton,
    SKUPack,
)
from . import normalize
from .costs import upsert_cost
from .dedupe import apply_hash_to_observation


@dataclass(slots=True)
class RowError:
    row_number: int
    message: str


@dataclass(slots=True)
class ImportReport:
    inserted: int = 0
    updated: int = 0
    duplicates: int = 0
    errors: list[RowError] = field(default_factory=list)

    def add_error(self, row_number: int, message: str) -> None:
        self.errors.append(RowError(row_number=row_number, message=message))

    def to_dict(self) -> dict:
        return {
            "inserted": self.inserted,
            "updated": self.updated,
            "duplicates": self.duplicates,
            "errors": [error.__dict__ for error in self.errors],
        }


class SKUImporter:
    REQUIRED_COLUMNS = {
        "brand",
        "product_name",
        "category",
        "abv_percent",
        "package_type",
        "container_ml",
        "is_active",
    }

    def __init__(self, session: Session, *, allow_create: bool = False):
        self.session = session
        self.allow_create = allow_create

    def run(self, csv_path: Path) -> ImportReport:
        report = ImportReport()
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = self.REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}"
                )

            for idx, row in enumerate(reader, start=2):  # header is row 1
                try:
                    created = self._process_row(row)
                    self.session.flush()
                except Exception as exc:  # noqa: BLE001
                    report.add_error(idx, str(exc))
                    self.session.rollback()
                else:
                    if created:
                        report.inserted += 1
                    else:
                        report.updated += 1
        return report

    def _process_row(self, row: dict) -> bool:
        brand = self._get_or_create_brand(row["brand"].strip())
        product = self._get_or_create_product(brand, row)
        package_spec = self._get_or_create_package_spec(row)
        sku = self._find_sku(row, product, package_spec)
        if sku is None:
            sku = SKU(
                product=product,
                package_spec=package_spec,
                gtin=row.get("gtin") or None,
                is_active=self._parse_bool(row.get("is_active")),
            )
            self.session.add(sku)
            created = True
        else:
            sku.gtin = row.get("gtin") or sku.gtin
            sku.is_active = self._parse_bool(row.get("is_active"))
            created = False
        if row.get("can_form_factor") and package_spec.can_form_factor is None:
            package_spec.can_form_factor = row["can_form_factor"].strip()
        pack_spec = self._handle_pack_configuration(sku, package_spec, row)
        self._handle_carton_configuration(sku, package_spec, pack_spec, row)
        self._handle_costs(sku, row)
        return created

    def _get_or_create_brand(self, name: str) -> Brand:
        brand = self.session.execute(
            select(Brand).where(Brand.name == name)
        ).scalar_one_or_none()
        if brand is None:
            if not self.allow_create:
                raise ValueError(f"Brand '{name}' does not exist")
            brand = Brand(name=name)
            self.session.add(brand)
            self.session.flush([brand])
        return brand

    def _get_or_create_product(self, brand: Brand, row: dict) -> Product:
        name = row["product_name"].strip()
        product = self.session.execute(
            select(Product).where(Product.brand == brand, Product.name == name)
        ).scalar_one_or_none()
        if product is None:
            if not self.allow_create:
                raise ValueError(f"Product '{name}' missing for brand '{brand.name}'")
            product = Product(
                brand=brand,
                name=name,
                category=row["category"].strip(),
                abv_percent=self._parse_decimal(row.get("abv_percent"), two_dp=True),
            )
            self.session.add(product)
            self.session.flush([product])
        else:
            abv_value = row.get("abv_percent")
            if abv_value:
                product.abv_percent = self._parse_decimal(abv_value, two_dp=True)
        return product

    def _get_or_create_package_spec(self, row: dict) -> PackageSpec:
        package_type = row["package_type"].strip()
        container_ml = int(row["container_ml"].strip())
        can_form_factor = (
            (row.get("can_form_factor") or None) if package_type == "can" else None
        )

        query = select(PackageSpec).where(
            PackageSpec.type == package_type,
            PackageSpec.container_ml == container_ml,
        )
        if can_form_factor is None:
            query = query.where(PackageSpec.can_form_factor.is_(None))
        else:
            query = query.where(PackageSpec.can_form_factor == can_form_factor)
        spec = self.session.execute(query).scalar_one_or_none()
        if spec is None:
            if not self.allow_create:
                raise ValueError(
                    f"Package spec {package_type} {container_ml}ml not found"
                )
            spec = PackageSpec(
                type=package_type,
                container_ml=container_ml,
                can_form_factor=can_form_factor,
            )
            self.session.add(spec)
            self.session.flush([spec])
        return spec

    def _find_sku(
        self,
        row: dict,
        product: Product,
        package_spec: PackageSpec,
    ) -> Optional[SKU]:
        gtin = (row.get("gtin") or "").strip()
        if gtin:
            existing = self.session.execute(
                select(SKU).where(SKU.gtin == gtin)
            ).scalar_one_or_none()
            if existing:
                return existing
        return self.session.execute(
            select(SKU).where(SKU.product == product, SKU.package_spec == package_spec)
        ).scalar_one_or_none()

    def _handle_pack_configuration(
        self, sku: SKU, package_spec: PackageSpec, row: dict
    ) -> Optional[PackSpec]:
        pack_units = self._optional_int(row.get("pack_units"))
        if pack_units is None or pack_units <= 1:
            return (
                sku.pack_assignment.pack_spec
                if getattr(sku, "pack_assignment", None)
                else None
            )
        pack_gtin = self._optional_str(row.get("pack_gtin"))
        pack_notes = self._optional_str(row.get("pack_notes"))
        pack_spec = self._get_or_create_pack_spec(
            package_spec=package_spec,
            units_per_pack=pack_units,
            gtin=pack_gtin,
            notes=pack_notes,
        )
        self._ensure_sku_pack(sku, pack_spec)
        return pack_spec

    def _handle_carton_configuration(
        self,
        sku: SKU,
        package_spec: PackageSpec,
        pack_spec: Optional[PackSpec],
        row: dict,
    ) -> None:
        carton_units = self._optional_int(row.get("carton_units"))
        carton_pack_count = self._optional_int(row.get("carton_pack_count"))
        carton_gtin = self._optional_str(row.get("carton_gtin"))
        carton_notes = self._optional_str(row.get("carton_notes"))
        if (
            carton_units is None
            and carton_pack_count is None
            and carton_gtin is None
            and carton_notes is None
        ):
            return
        spec = self._get_or_create_carton_spec(
            package_spec=package_spec,
            pack_spec=pack_spec,
            units_per_carton=carton_units,
            pack_count=carton_pack_count,
            gtin=carton_gtin,
            notes=carton_notes,
        )
        if spec is not None:
            self._ensure_sku_carton(sku, spec)

    def _handle_costs(self, sku: SKU, row: dict) -> None:
        cost_type_raw = self._optional_str(row.get("cost_type"))
        if not cost_type_raw:
            return
        effective_date_value = self._optional_str(row.get("cost_effective_date"))
        if not effective_date_value:
            raise ValueError(
                "cost_effective_date is required when cost_type is provided"
            )
        if getattr(sku, "id", None) is None:
            self.session.flush([sku])
        cost_per_unit = self._optional_decimal(
            row.get("cost_per_unit"), quant=Decimal("0.0001")
        )
        cost_per_pack = self._optional_decimal(
            row.get("cost_per_pack"), quant=Decimal("0.0001")
        )
        cost_per_carton = self._optional_decimal(
            row.get("cost_per_carton"), quant=Decimal("0.0001")
        )
        cost_currency = (self._optional_str(row.get("cost_currency")) or "AUD").upper()
        notes = self._optional_str(row.get("cost_notes"))
        cost = upsert_cost(
            self.session,
            sku_id=sku.id,
            cost_type=cost_type_raw,
            effective_date=self._parse_date(effective_date_value),
            cost_currency=cost_currency,
            cost_per_unit=cost_per_unit,
            cost_per_pack=cost_per_pack,
            cost_per_carton=cost_per_carton,
            notes=notes,
        )
        self.session.flush([cost])

    def _get_or_create_pack_spec(
        self,
        *,
        package_spec: PackageSpec,
        units_per_pack: int,
        gtin: Optional[str],
        notes: Optional[str],
    ) -> PackSpec:
        query = select(PackSpec).where(
            PackSpec.package_spec_id == package_spec.id,
            PackSpec.units_per_pack == units_per_pack,
        )
        spec = self.session.execute(query).scalar_one_or_none()
        if spec is None:
            if not self.allow_create:
                raise ValueError(
                    f"Pack specification for {units_per_pack}x{package_spec.container_ml}ml missing"
                )
            spec = PackSpec(
                package_spec=package_spec,
                units_per_pack=units_per_pack,
                gtin=gtin,
                notes=notes,
            )
            self.session.add(spec)
            self.session.flush([spec])
        else:
            if gtin and not spec.gtin:
                spec.gtin = gtin
            if notes:
                spec.notes = notes
        return spec

    def _ensure_sku_pack(self, sku: SKU, pack_spec: PackSpec) -> None:
        assignment = getattr(sku, "pack_assignment", None)
        if assignment is None:
            assignment = SKUPack(sku=sku, pack_spec=pack_spec)
            self.session.add(assignment)
        else:
            assignment.pack_spec = pack_spec

    def _get_or_create_carton_spec(
        self,
        *,
        package_spec: PackageSpec,
        pack_spec: Optional[PackSpec],
        units_per_carton: Optional[int],
        pack_count: Optional[int],
        gtin: Optional[str],
        notes: Optional[str],
    ) -> Optional[CartonSpec]:
        if pack_spec is not None:
            if pack_count is None:
                if units_per_carton is None:
                    raise ValueError(
                        "carton_pack_count or carton_units required for pack cartons"
                    )
                if units_per_carton % pack_spec.units_per_pack != 0:
                    raise ValueError("carton_units must be divisible by pack_units")
                pack_count = units_per_carton // pack_spec.units_per_pack
            if pack_count <= 0:
                raise ValueError("carton_pack_count must be greater than zero")
            total_units = pack_spec.units_per_pack * pack_count
            if units_per_carton is None:
                units_per_carton = total_units
            elif units_per_carton != total_units:
                raise ValueError("carton_units does not match pack_count * pack_units")
            query = select(CartonSpec).where(
                CartonSpec.pack_spec_id == pack_spec.id,
                CartonSpec.pack_count == pack_count,
            )
        else:
            if units_per_carton is None:
                return None
            query = select(CartonSpec).where(
                CartonSpec.package_spec_id == package_spec.id,
                CartonSpec.units_per_carton == units_per_carton,
            )
        spec = self.session.execute(query).scalar_one_or_none()
        if spec is None:
            if not self.allow_create:
                raise ValueError("Carton specification is missing for provided data")
            spec = CartonSpec(
                units_per_carton=units_per_carton,
                pack_count=pack_count if pack_spec is not None else None,
                gtin=gtin,
                notes=notes,
            )
            if pack_spec is not None:
                spec.pack_spec = pack_spec
            else:
                spec.package_spec = package_spec
            self.session.add(spec)
            self.session.flush([spec])
        else:
            if gtin and not spec.gtin:
                spec.gtin = gtin
            if notes:
                spec.notes = notes
        return spec

    def _ensure_sku_carton(self, sku: SKU, carton_spec: CartonSpec) -> None:
        if any(link.carton_spec_id == carton_spec.id for link in sku.carton_links):
            return
        self.session.add(SKUCarton(sku=sku, carton_spec=carton_spec))

    @staticmethod
    def _parse_bool(value: Optional[str]) -> bool:
        return str(value).strip().lower() in {"1", "true", "yes"}

    @staticmethod
    def _parse_decimal(value: Optional[str], *, two_dp: bool = False) -> Decimal:
        if value is None or value == "":
            raise ValueError("Missing decimal value")
        quant = Decimal("0.01") if two_dp else Decimal("0.0001")
        try:
            return Decimal(value).quantize(quant)
        except InvalidOperation as exc:  # pragma: no cover - validation safeguard
            raise ValueError(f"Invalid decimal value: {value}") from exc

    @staticmethod
    def _optional_int(value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        return int(value)

    @staticmethod
    def _optional_decimal(value: Optional[str], *, quant: Decimal) -> Optional[Decimal]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        try:
            return Decimal(value).quantize(quant)
        except InvalidOperation as exc:  # pragma: no cover
            raise ValueError(f"Invalid decimal value: {value}") from exc

    @staticmethod
    def _optional_str(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @staticmethod
    def _parse_date(value: str) -> date:
        try:
            return date.fromisoformat(value)
        except ValueError as exc:  # pragma: no cover - validation safeguard
            raise ValueError(f"Invalid ISO date: {value}") from exc


class ObservationImporter:
    REQUIRED_COLUMNS = {
        "brand",
        "product_name",
        "category",
        "package_type",
        "container_ml",
        "channel",
        "company",
        "state",
        "suburb",
        "price_context",
        "availability",
        "observation_dt",
        "source_type",
    }

    def __init__(self, session: Session, *, allow_create: bool = False):
        self.session = session
        self.allow_create = allow_create

    def run(self, csv_path: Path) -> ImportReport:
        report = ImportReport()
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = self.REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}"
                )

            for idx, row in enumerate(reader, start=2):
                try:
                    duplicate = self._process_row(row)
                except Exception as exc:  # noqa: BLE001
                    report.add_error(idx, str(exc))
                    self.session.rollback()
                else:
                    if duplicate:
                        report.duplicates += 1
                    else:
                        report.inserted += 1
        return report

    def _process_row(self, row: dict) -> bool:
        sku = self._resolve_sku(row)
        company = self._get_or_create_company(row["company"].strip())
        location = self._get_or_create_location(company, row)

        price_ex = self._optional_decimal(row.get("price_ex_gst_raw"))
        price_inc = self._optional_decimal(row.get("price_inc_gst_raw"))
        if price_ex is not None:
            price_ex = price_ex.quantize(Decimal("0.01"))
        if price_inc is not None:
            price_inc = price_inc.quantize(Decimal("0.01"))
        gst_rate = (
            self._optional_decimal(row.get("gst_rate")) or Decimal("0.10")
        ).quantize(Decimal("0.0001"))
        carton_units = self._optional_int(row.get("carton_units"))
        is_carton_price = self._parse_bool(row.get("is_carton_price"))
        is_pack_price = self._parse_bool(row.get("is_pack_price"))

        normalized = normalize.normalize_price(
            sku=sku,
            price_ex_gst_raw=price_ex,
            price_inc_gst_raw=price_inc,
            gst_rate=gst_rate,
            carton_units=carton_units if is_carton_price else None,
            is_carton_price=is_carton_price,
            is_pack_price=is_pack_price,
        )

        observation_dt = self._parse_datetime(row.get("observation_dt"))

        observation = PriceObservation(
            sku=sku,
            company=company,
            location=location,
            channel=row["channel"].strip(),
            price_context=row["price_context"].strip(),
            promo_name=row.get("promo_name") or None,
            availability=row.get("availability", "unknown").strip(),
            price_ex_gst_raw=price_ex,
            price_inc_gst_raw=price_inc,
            gst_rate=gst_rate,
            currency=row.get("currency", "AUD").strip() or "AUD",
            is_carton_price=is_carton_price,
            carton_units=carton_units,
            price_ex_gst_norm=normalized.price_ex_gst,
            price_inc_gst_norm=normalized.price_inc_gst,
            unit_price_inc_gst=normalized.unit_price_inc_gst,
            carton_price_inc_gst=normalized.carton_price_inc_gst,
            price_per_litre=normalized.price_per_litre,
            price_per_unit_pure_alcohol=normalized.price_per_unit_pure_alcohol,
            standard_drinks=normalized.standard_drinks,
            price_basis=normalized.price_basis,
            gp_unit_abs=normalized.gp_unit_abs,
            gp_unit_pct=normalized.gp_unit_pct,
            gp_pack_abs=normalized.gp_pack_abs,
            gp_pack_pct=normalized.gp_pack_pct,
            gp_carton_abs=normalized.gp_carton_abs,
            gp_carton_pct=normalized.gp_carton_pct,
            pack_price_inc_gst=normalized.pack_price_inc_gst,
            observation_dt=observation_dt,
            source_type=row["source_type"].strip(),
            source_url=row.get("source_url") or None,
            source_note=row.get("source_note") or None,
        )
        apply_hash_to_observation(observation)

        existing = self.session.execute(
            select(PriceObservation.id).where(
                PriceObservation.hash_key == observation.hash_key
            )
        ).first()
        if existing:
            return True

        self.session.add(observation)
        return False

    def _resolve_sku(self, row: dict) -> SKU:
        gtin = (row.get("gtin") or "").strip()
        if gtin:
            sku = self.session.execute(
                select(SKU).where(SKU.gtin == gtin)
            ).scalar_one_or_none()
            if sku:
                return sku
        brand = self._get_or_create_brand(row["brand"].strip())
        product = self._get_or_create_product(brand, row)
        package_spec = self._get_package_spec(row)
        sku = self.session.execute(
            select(SKU).where(SKU.product == product, SKU.package_spec == package_spec)
        ).scalar_one_or_none()
        if sku is None:
            raise ValueError(
                "SKU not found for row; provide GTIN or matching product/package"
            )
        return sku

    def _get_or_create_brand(self, name: str) -> Brand:
        brand = self.session.execute(
            select(Brand).where(Brand.name == name)
        ).scalar_one_or_none()
        if brand is None:
            if not self.allow_create:
                raise ValueError(f"Brand '{name}' does not exist")
            brand = Brand(name=name)
            self.session.add(brand)
            self.session.flush([brand])
        return brand

    def _get_or_create_product(self, brand: Brand, row: dict) -> Product:
        product_name = row["product_name"].strip()
        product = self.session.execute(
            select(Product).where(Product.brand == brand, Product.name == product_name)
        ).scalar_one_or_none()
        if product is None:
            if not self.allow_create:
                raise ValueError(
                    f"Product '{product_name}' not found for brand '{brand.name}'"
                )
            abv_value = row.get("abv_percent")
            abv_decimal = self._optional_decimal(abv_value)
            if abv_decimal is not None:
                abv_decimal = abv_decimal.quantize(Decimal("0.01"))
            else:
                abv_decimal = Decimal("0")
            product = Product(
                brand=brand,
                name=product_name,
                category=row["category"].strip(),
                abv_percent=abv_decimal,
            )
            self.session.add(product)
            self.session.flush([product])
        return product

    def _get_package_spec(self, row: dict) -> PackageSpec:
        package_type = row["package_type"].strip()
        container_ml = int(row["container_ml"].strip())
        can_form_factor = row.get("can_form_factor") or None
        query = select(PackageSpec).where(
            PackageSpec.type == package_type,
            PackageSpec.container_ml == container_ml,
        )
        if package_type == "can":
            if can_form_factor is None:
                raise ValueError("Can entries must include can_form_factor")
            query = query.where(PackageSpec.can_form_factor == can_form_factor)
        else:
            query = query.where(PackageSpec.can_form_factor.is_(None))
        spec = self.session.execute(query).scalar_one_or_none()
        if spec is None:
            raise ValueError(
                "Package spec not found; import SKUs first or enable creation"
            )
        return spec

    def _get_or_create_company(self, name: str) -> Company:
        company = self.session.execute(
            select(Company).where(Company.name == name)
        ).scalar_one_or_none()
        if company is None:
            if not self.allow_create:
                raise ValueError(f"Company '{name}' not found")
            company = Company(name=name, type="retailer")
            self.session.add(company)
            self.session.flush([company])
        return company

    def _get_or_create_location(
        self, company: Company, row: dict
    ) -> Optional[Location]:
        store_name_raw = row.get("store_name") or None
        state_raw = row.get("state") or None
        suburb_raw = row.get("suburb") or None
        store_name = store_name_raw.strip() if store_name_raw else None
        state = (state_raw or "").strip()
        suburb = (suburb_raw or "").strip()
        if not state and not suburb:
            return None
        conditions = [
            Location.company == company,
            Location.state == state,
            Location.suburb == suburb,
        ]
        if store_name is None:
            conditions.append(Location.store_name.is_(None))
        else:
            conditions.append(Location.store_name == store_name)
        query = select(Location).where(*conditions)
        location = self.session.execute(query).scalar_one_or_none()
        if location is None:
            if not self.allow_create:
                raise ValueError(
                    f"Location '{store_name or ''} {suburb or ''} {state or ''}' missing"
                )
            location = Location(
                company=company,
                store_name=store_name,
                state=state,
                suburb=suburb,
                postcode=row.get("postcode") or None,
            )
            self.session.add(location)
            self.session.flush([location])
        return location

    @staticmethod
    def _optional_decimal(
        value: Optional[str], default: Optional[Decimal] = None
    ) -> Optional[Decimal]:
        if value is None or value == "":
            return default
        return Decimal(value)

    @staticmethod
    def _optional_int(value: Optional[str]) -> Optional[int]:
        if value is None or value == "":
            return None
        return int(value)

    @staticmethod
    def _parse_bool(value: Optional[str]) -> bool:
        return str(value).strip().lower() in {"1", "true", "yes"}

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> datetime:
        if not value:
            raise ValueError("observation_dt is required")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha1
from random import Random
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    SKU,
    Attachment,
    Brand,
    CartonSpec,
    Company,
    Location,
    PackageSpec,
    PackSpec,
    PriceObservation,
    Product,
    PurchasePrice,
    SKUCarton,
    SKUPack,
)
from . import normalize

REQUIRED_BRANDS = 5
REQUIRED_SKUS = 10
REQUIRED_OBSERVATIONS = 100


BRAND_DEFINITIONS = [
    {
        "name": "Gordon's",
        "owner": "Diageo",
        "products": [
            {
                "name": "Dry Gin",
                "category": "gin_bottle",
                "abv": Decimal("37.5"),
                "packages": [
                    {
                        "type": "bottle",
                        "container_ml": 700,
                        "base_price": Decimal("45.00"),
                    },
                    {
                        "type": "bottle",
                        "container_ml": 1000,
                        "base_price": Decimal("58.00"),
                    },
                ],
            }
        ],
    },
    {
        "name": "Four Pillars",
        "owner": "Lion",
        "products": [
            {
                "name": "Rare Dry Gin",
                "category": "gin_bottle",
                "abv": Decimal("41.8"),
                "packages": [
                    {
                        "type": "bottle",
                        "container_ml": 700,
                        "base_price": Decimal("78.00"),
                    },
                ],
            }
        ],
    },
    {
        "name": "Bombay",
        "owner": "Bacardi",
        "products": [
            {
                "name": "Sapphire",
                "category": "gin_bottle",
                "abv": Decimal("40.0"),
                "packages": [
                    {
                        "type": "bottle",
                        "container_ml": 1000,
                        "base_price": Decimal("65.00"),
                    },
                ],
            }
        ],
    },
    {
        "name": "Brand X",
        "owner": "Indie Spirits",
        "products": [
            {
                "name": "Lemon Gin RTD",
                "category": "gin_rtd",
                "abv": Decimal("6.5"),
                "packages": [
                    {
                        "type": "can",
                        "container_ml": 250,
                        "can_form_factor": "slim",
                        "base_price": Decimal("19.00"),
                    },
                    {
                        "type": "can",
                        "container_ml": 330,
                        "can_form_factor": "sleek",
                        "base_price": Decimal("20.50"),
                    },
                ],
            }
        ],
    },
    {
        "name": "Coastal Spritz",
        "owner": "Coastal Beverages",
        "products": [
            {
                "name": "Blood Orange Gin Spritz",
                "category": "gin_rtd",
                "abv": Decimal("5.5"),
                "packages": [
                    {
                        "type": "can",
                        "container_ml": 375,
                        "can_form_factor": "classic",
                        "base_price": Decimal("22.00"),
                    },
                ],
            }
        ],
    },
    {
        "name": "Tanqueray",
        "owner": "Diageo",
        "products": [
            {
                "name": "London Dry Gin",
                "category": "vodka_bottle",
                "abv": Decimal("43.1"),
                "packages": [
                    {
                        "type": "bottle",
                        "container_ml": 700,
                        "base_price": Decimal("57.00"),
                    },
                ],
            }
        ],
    },
    {
        "name": "Hendrick's",
        "owner": "William Grant & Sons",
        "products": [
            {
                "name": "Lunar Gin",
                "category": "vodka_bottle",
                "abv": Decimal("43.4"),
                "packages": [
                    {
                        "type": "bottle",
                        "container_ml": 700,
                        "base_price": Decimal("92.00"),
                    },
                ],
            }
        ],
    },
    {
        "name": "Sparkle Can Co",
        "owner": "Sparkle Beverage Group",
        "products": [
            {
                "name": "Cucumber Lime Gin Fizz",
                "category": "vodka_rtd",
                "abv": Decimal("5.8"),
                "packages": [
                    {
                        "type": "can",
                        "container_ml": 300,
                        "can_form_factor": "slim",
                        "base_price": Decimal("18.50"),
                    },
                ],
            }
        ],
    },
]

PACKAGE_LIBRARY = [
    ("bottle", 200, None),
    ("bottle", 500, None),
    ("bottle", 700, None),
    ("bottle", 1000, None),
    ("can", 250, "slim"),
    ("can", 300, "slim"),
    ("can", 330, "sleek"),
    ("can", 375, "classic"),
]

COMPANY_DEFINITIONS = [
    {
        "name": "Dan Murphy's",
        "type": "retailer",
        "locations": [
            {"store_name": "Geelong", "state": "VIC", "suburb": "Geelong"},
            {"store_name": "Bondi", "state": "NSW", "suburb": "Bondi"},
        ],
    },
    {
        "name": "First Choice Liquor",
        "type": "retailer",
        "locations": [
            {"store_name": "Richmond", "state": "VIC", "suburb": "Richmond"},
        ],
    },
    {
        "name": "Vintage Cellars",
        "type": "retailer",
        "locations": [
            {"store_name": "Indooroopilly", "state": "QLD", "suburb": "Indooroopilly"},
        ],
    },
    {
        "name": "BWS",
        "type": "retailer",
        "locations": [
            {"store_name": "Adelaide CBD", "state": "SA", "suburb": "Adelaide"},
        ],
    },
    {
        "name": "Craft Spirits Co",
        "type": "distributor",
        "locations": [
            {"store_name": "Warehouse", "state": "VIC", "suburb": "Footscray"},
        ],
    },
]

CHANNELS = [
    "retail_instore",
    "retail_online",
    "distributor_to_retailer",
    "wholesale_to_venue",
]
PRICE_CONTEXTS = ["shelf", "promo", "member", "online"]
AVAILABILITY_STATES = ["in_stock", "low_stock", "out_of_stock", "unknown"]
SOURCE_TYPES = ["web", "in_store", "brochure", "email", "receipt"]
PROMO_NAMES = ["Weekly Special", "Bundle Deal", "Loyalty Offer", "Seasonal Promo"]

LOCATION_COORDS = {
    ("VIC", "Geelong"): (-38.1499, 144.3617),
    ("NSW", "Bondi"): (-33.8915, 151.2767),
    ("VIC", "Richmond"): (-37.8183, 144.9980),
    ("QLD", "Indooroopilly"): (-27.5036, 152.9754),
    ("SA", "Adelaide"): (-34.9285, 138.6007),
    ("VIC", "Footscray"): (-37.8000, 144.8997),
}


class SampleDataBuilder:
    def __init__(self, session: Session, seed: int = 42):
        self.session = session
        self.rng = Random(seed)
        self.package_lookup: dict[tuple[str, int, Optional[str]], PackageSpec] = {}
        self.pack_lookup: dict[tuple[str, int], PackSpec] = {}
        self.carton_lookup: dict[tuple[str, str, Optional[int]], CartonSpec] = {}
        self.pack_gtin_seq = 50000000000
        self.carton_gtin_seq = 60000000000

    def ensure_package_spec(
        self, type_: str, container_ml: int, can_form_factor: Optional[str]
    ) -> PackageSpec:
        key = (type_, container_ml, can_form_factor)
        if key not in self.package_lookup:
            query = select(PackageSpec).where(
                PackageSpec.type == type_,
                PackageSpec.container_ml == container_ml,
            )
            if can_form_factor is None:
                query = query.where(PackageSpec.can_form_factor.is_(None))
            else:
                query = query.where(PackageSpec.can_form_factor == can_form_factor)
            spec = self.session.execute(query).scalar_one_or_none()
            if spec is None:
                spec = PackageSpec(
                    type=type_,
                    container_ml=container_ml,
                    can_form_factor=can_form_factor,
                )
                self.session.add(spec)
                self.session.flush([spec])
            self.package_lookup[key] = spec
        return self.package_lookup[key]

    def _next_pack_gtin(self) -> str:
        value = self.pack_gtin_seq
        self.pack_gtin_seq += 1
        return f"95{value:011d}"

    def _next_carton_gtin(self) -> str:
        value = self.carton_gtin_seq
        self.carton_gtin_seq += 1
        return f"96{value:011d}"

    def _ensure_pack_spec(
        self, package_spec: PackageSpec, units_per_pack: int
    ) -> PackSpec:
        key = (package_spec.id, units_per_pack)
        if key in self.pack_lookup:
            return self.pack_lookup[key]
        spec = self.session.execute(
            select(PackSpec).where(
                PackSpec.package_spec_id == package_spec.id,
                PackSpec.units_per_pack == units_per_pack,
            )
        ).scalar_one_or_none()
        if spec is None:
            spec = PackSpec(
                package_spec=package_spec,
                units_per_pack=units_per_pack,
                gtin=self._next_pack_gtin(),
            )
            self.session.add(spec)
            self.session.flush([spec])
        self.pack_lookup[key] = spec
        return spec

    def _ensure_carton_spec(
        self,
        *,
        package_spec: Optional[PackageSpec],
        pack_spec: Optional[PackSpec],
        units_per_carton: int,
        pack_count: Optional[int],
    ) -> CartonSpec:
        key = (
            "pack" if pack_spec else "unit",
            (pack_spec.id if pack_spec else package_spec.id),
            pack_count if pack_spec else units_per_carton,
        )
        if key in self.carton_lookup:
            return self.carton_lookup[key]
        query = select(CartonSpec).where(
            CartonSpec.units_per_carton == units_per_carton
        )
        if pack_spec is not None:
            query = query.where(
                CartonSpec.pack_spec_id == pack_spec.id,
                CartonSpec.pack_count == pack_count,
            )
        else:
            query = query.where(CartonSpec.package_spec_id == package_spec.id)
        spec = self.session.execute(query).scalar_one_or_none()
        if spec is None:
            spec = CartonSpec(
                units_per_carton=units_per_carton,
                pack_count=pack_count,
                gtin=self._next_carton_gtin(),
            )
            if pack_spec is not None:
                spec.pack_spec = pack_spec
            else:
                spec.package_spec = package_spec
            self.session.add(spec)
            self.session.flush([spec])
        self.carton_lookup[key] = spec
        return spec

    @staticmethod
    def _link_sku_pack(sku: SKU, pack_spec: Optional[PackSpec]) -> None:
        if pack_spec is None:
            return
        assignment = getattr(sku, "pack_assignment", None)
        if assignment is None:
            sku.pack_assignment = SKUPack(sku=sku, pack_spec=pack_spec)
        else:
            assignment.pack_spec = pack_spec

    @staticmethod
    def _link_sku_carton(sku: SKU, carton_spec: CartonSpec) -> None:
        if any(link.carton_spec_id == carton_spec.id for link in sku.carton_links):
            return
        sku.carton_links.append(SKUCarton(sku=sku, carton_spec=carton_spec))

    def _seed_costs(
        self,
        sku: SKU,
        pack_spec: Optional[PackSpec],
        carton_spec: CartonSpec,
        base_price: Decimal,
    ) -> None:
        existing = self.session.execute(
            select(PurchasePrice.id).where(PurchasePrice.sku_id == sku.id)
        ).first()
        if existing:
            return
        unit_est = (base_price * Decimal("0.45")).quantize(Decimal("0.0001"))
        unit_known = (base_price * Decimal("0.52")).quantize(Decimal("0.0001"))
        pack_est = (
            unit_est * Decimal(pack_spec.units_per_pack)
            if pack_spec is not None
            else None
        )
        pack_known = (
            unit_known * Decimal(pack_spec.units_per_pack)
            if pack_spec is not None
            else None
        )
        carton_units = Decimal(carton_spec.units_per_carton)
        carton_est = unit_est * carton_units
        carton_known = unit_known * carton_units
        today = datetime.now(timezone.utc).date()
        estimated = PurchasePrice(
            sku=sku,
            cost_type="estimated",
            cost_currency="AUD",
            cost_per_unit=unit_est,
            cost_per_pack=pack_est.quantize(Decimal("0.0001"))
            if pack_est is not None
            else None,
            cost_per_carton=carton_est.quantize(Decimal("0.0001")),
            effective_date=today - timedelta(days=45),
            notes="Seed estimated manufacturing cost",
        )
        known = PurchasePrice(
            sku=sku,
            cost_type="known",
            cost_currency="AUD",
            cost_per_unit=unit_known,
            cost_per_pack=pack_known.quantize(Decimal("0.0001"))
            if pack_known is not None
            else None,
            cost_per_carton=carton_known.quantize(Decimal("0.0001")),
            effective_date=today - timedelta(days=10),
            notes="Seed confirmed manufacturing cost",
        )
        self.session.add_all([estimated, known])

    def build_catalog(self) -> list[SKU]:
        skus: list[SKU] = []
        for type_, container_ml, can_form_factor in PACKAGE_LIBRARY:
            self.ensure_package_spec(type_, container_ml, can_form_factor)

        for brand_def in BRAND_DEFINITIONS:
            brand = self.session.execute(
                select(Brand).where(Brand.name == brand_def["name"])
            ).scalar_one_or_none()
            if brand is None:
                brand = Brand(name=brand_def["name"], owner_company=brand_def["owner"])
                self.session.add(brand)
                self.session.flush([brand])

            for product_def in brand_def["products"]:
                product = self.session.execute(
                    select(Product).where(
                        Product.brand == brand,
                        Product.name == product_def["name"],
                    )
                ).scalar_one_or_none()
                if product is None:
                    product = Product(
                        brand=brand,
                        name=product_def["name"],
                        category=product_def["category"],
                        abv_percent=product_def["abv"],
                    )
                    self.session.add(product)
                    self.session.flush([product])

                for idx, pkg in enumerate(product_def["packages"]):
                    package_spec = self.ensure_package_spec(
                        pkg["type"], pkg["container_ml"], pkg.get("can_form_factor")
                    )
                    sku = self.session.execute(
                        select(SKU).where(
                            SKU.product == product,
                            SKU.package_spec == package_spec,
                        )
                    ).scalar_one_or_none()
                    if sku is None:
                        gtin_suffix = 100000 + len(skus) * 3 + idx
                        sku = SKU(
                            product=product,
                            package_spec=package_spec,
                            gtin=f"93{gtin_suffix:010d}",
                            is_active=True,
                        )
                        self.session.add(sku)
                        self.session.flush([sku])
                    pack_spec = None
                    if package_spec.type == "can":
                        pack_units = self.rng.choice([4, 6])
                        pack_spec = self._ensure_pack_spec(package_spec, pack_units)
                        self._link_sku_pack(sku, pack_spec)
                        pack_count = self.rng.choice([3, 4, 6])
                        carton_spec = self._ensure_carton_spec(
                            package_spec=None,
                            pack_spec=pack_spec,
                            units_per_carton=pack_units * pack_count,
                            pack_count=pack_count,
                        )
                    else:
                        carton_spec = self._ensure_carton_spec(
                            package_spec=package_spec,
                            pack_spec=None,
                            units_per_carton=6,
                            pack_count=None,
                        )
                    self._link_sku_carton(sku, carton_spec)
                    base_price = self._base_price_for_sku(sku)
                    self._seed_costs(sku, pack_spec, carton_spec, base_price)
                    skus.append(sku)
        return skus

    def build_companies(self) -> list[Company]:
        companies: list[Company] = []
        for comp_def in COMPANY_DEFINITIONS:
            company = self.session.execute(
                select(Company).where(Company.name == comp_def["name"])
            ).scalar_one_or_none()
            if company is None:
                company = Company(name=comp_def["name"], type=comp_def["type"])
                self.session.add(company)
                self.session.flush([company])
            for loc_def in comp_def["locations"]:
                location = self.session.execute(
                    select(Location).where(
                        Location.company == company,
                        Location.store_name == loc_def.get("store_name"),
                        Location.state == loc_def["state"],
                        Location.suburb == loc_def["suburb"],
                    )
                ).scalar_one_or_none()
                if location is None:
                    coords = LOCATION_COORDS.get((loc_def["state"], loc_def["suburb"]))
                    lat, lon = coords if coords else (None, None)
                    location = Location(
                        company=company,
                        store_name=loc_def.get("store_name"),
                        state=loc_def["state"],
                        suburb=loc_def["suburb"],
                        lat=lat,
                        lon=lon,
                    )
                    self.session.add(location)
            companies.append(company)
        self.session.flush(companies)
        return companies

    def create_observations(
        self, skus: Iterable[SKU], companies: Iterable[Company]
    ) -> list[PriceObservation]:
        observations: list[PriceObservation] = []
        company_locations = {
            company.id: list(company.locations) for company in companies
        }
        now = datetime.now(timezone.utc)
        gst_rate = Decimal("0.10")
        for sku in skus:
            base_price = self._base_price_for_sku(sku)
            for i in range(10):
                company = self.rng.choice(list(companies))
                locations = company_locations.get(company.id, [])
                location = self.rng.choice(locations) if locations else None
                channel = self.rng.choice(CHANNELS)
                price_context = self.rng.choice(PRICE_CONTEXTS)
                availability = self.rng.choice(AVAILABILITY_STATES)
                source_type = self.rng.choice(SOURCE_TYPES)
                promo_name = (
                    self.rng.choice(PROMO_NAMES)
                    if price_context in {"promo", "member"}
                    else None
                )

                price_variation = Decimal(self.rng.uniform(-3, 3)).quantize(
                    Decimal("0.01")
                )
                price_inc = (base_price + price_variation).quantize(Decimal("0.01"))
                carton_units = 6 if sku.package_spec.type == "bottle" else 24
                if self.rng.random() < 0.25:
                    is_carton_price = True
                    price_inc = (price_inc * Decimal(carton_units)).quantize(
                        Decimal("0.01")
                    )
                else:
                    is_carton_price = False
                is_pack_price = False
                if (
                    not is_carton_price
                    and getattr(sku, "pack_assignment", None)
                    and sku.pack_assignment.pack_spec
                ):
                    is_pack_price = self.rng.random() < 0.5

                gst_multiplier = Decimal("1") + gst_rate
                mode = self.rng.random()
                if mode < 0.33:
                    price_inc_raw = None
                    price_ex_raw = (price_inc / gst_multiplier).quantize(
                        Decimal("0.01")
                    )
                elif mode < 0.66:
                    price_inc_raw = price_inc.quantize(Decimal("0.01"))
                    price_ex_raw = None
                else:
                    price_inc_raw = price_inc.quantize(Decimal("0.01"))
                    price_ex_raw = (price_inc / gst_multiplier).quantize(
                        Decimal("0.01")
                    )

                normalized = normalize.normalize_price(
                    sku=sku,
                    price_ex_gst_raw=price_ex_raw,
                    price_inc_gst_raw=price_inc_raw,
                    gst_rate=gst_rate,
                    carton_units=carton_units if is_carton_price else None,
                    is_carton_price=is_carton_price,
                    is_pack_price=is_pack_price,
                )

                observation_dt = now - timedelta(days=self.rng.randint(0, 120))
                hash_key = self._build_hash(
                    sku_id=sku.id,
                    company_id=company.id,
                    location_id=location.id if location else None,
                    observation_dt=observation_dt,
                    channel=channel,
                    price_inc=normalized.price_inc_gst,
                    is_carton_price=is_carton_price,
                    carton_units=carton_units,
                    price_context=price_context,
                )

                obs = PriceObservation(
                    sku=sku,
                    company=company,
                    location=location,
                    channel=channel,
                    price_context=price_context,
                    promo_name=promo_name,
                    availability=availability,
                    price_ex_gst_raw=price_ex_raw,
                    price_inc_gst_raw=price_inc_raw,
                    gst_rate=gst_rate,
                    currency="AUD",
                    is_carton_price=is_carton_price,
                    carton_units=carton_units,
                    price_ex_gst_norm=normalized.price_ex_gst,
                    price_inc_gst_norm=normalized.price_inc_gst,
                    unit_price_inc_gst=normalized.unit_price_inc_gst,
                    pack_price_inc_gst=normalized.pack_price_inc_gst,
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
                    observation_dt=observation_dt,
                    source_type=source_type,
                    source_url="https://example.com/pricing",
                    source_note="Sample dataset",
                    hash_key=hash_key,
                )
                if self.rng.random() < 0.1:
                    obs.attachments.append(
                        Attachment(
                            file_path=f"evidence/{observation_dt.strftime('%Y/%m')}/sample_{sku.id}_{i}.jpg",
                            caption="Shelf photo",
                        )
                    )
                self.session.add(obs)
                observations.append(obs)
        return observations

    def _base_price_for_sku(self, sku: SKU) -> Decimal:
        for brand in BRAND_DEFINITIONS:
            for product in brand["products"]:
                for pkg in product["packages"]:
                    matches = (
                        sku.product.name == product["name"]
                        and sku.package_spec.type == pkg["type"]
                        and sku.package_spec.container_ml == pkg["container_ml"]
                        and sku.package_spec.can_form_factor
                        == pkg.get("can_form_factor")
                    )
                    if matches:
                        return pkg["base_price"]
        return Decimal("45.00")

    def _build_hash(
        self,
        *,
        sku_id: str,
        company_id: str,
        location_id: Optional[str],
        observation_dt: datetime,
        channel: str,
        price_inc: Decimal,
        is_carton_price: bool,
        carton_units: int,
        price_context: str,
    ) -> str:
        parts = [
            sku_id,
            company_id,
            location_id or "",
            observation_dt.date().isoformat(),
            channel,
            f"{price_inc:.2f}",
            "1" if is_carton_price else "0",
            str(carton_units),
            price_context,
        ]
        return sha1("|".join(parts).encode("utf-8")).hexdigest()


def load_sample_data(session: Session, *, seed: int = 42) -> dict[str, int]:
    existing_counts = {
        "brands": session.query(Brand).count(),
        "skus": session.query(SKU).count(),
        "observations": session.query(PriceObservation).count(),
    }
    if (
        existing_counts["brands"] >= REQUIRED_BRANDS
        and existing_counts["skus"] >= REQUIRED_SKUS
        and existing_counts["observations"] >= REQUIRED_OBSERVATIONS
    ):
        return existing_counts

    builder = SampleDataBuilder(session, seed=seed)
    skus = builder.build_catalog()
    companies = builder.build_companies()
    observations = builder.create_observations(skus, companies)
    session.flush()

    summary = {
        "brands": session.query(Brand).count(),
        "skus": session.query(SKU).count(),
        "companies": session.query(Company).count(),
        "observations": len(observations),
    }
    return summary

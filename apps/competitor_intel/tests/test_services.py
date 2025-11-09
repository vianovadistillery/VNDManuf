from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from apps.competitor_intel.app.services.dedupe import compute_observation_hash
from apps.competitor_intel.app.services.normalize import (
    compute_price_metrics,
    compute_standard_drinks,
    normalize_gst_prices,
    normalize_price,
)


class DummyPackageSpec(SimpleNamespace):
    pass


class DummyProduct(SimpleNamespace):
    pass


class DummySKU(SimpleNamespace):
    pass


@pytest.mark.parametrize(
    "price_ex, price_inc, gst_rate",
    [
        (Decimal("50.00"), None, Decimal("0.10")),
        (None, Decimal("55.00"), Decimal("0.10")),
    ],
)
def test_normalize_gst_prices_round_trip(price_ex, price_inc, gst_rate):
    ex, inc = normalize_gst_prices(price_ex, price_inc, gst_rate)
    assert ex.quantize(Decimal("0.01")) == Decimal("50.00")
    assert inc.quantize(Decimal("0.01")) == Decimal("55.00")


def test_compute_standard_drinks_matches_reference():
    result = compute_standard_drinks(700, Decimal("40.0"))
    assert pytest.approx(float(result), rel=1e-3) == 22.1


def test_compute_price_metrics_unit_and_carton():
    product = DummyProduct(abv_percent=Decimal("40.0"))
    package_spec = DummyPackageSpec(type="bottle", container_ml=700)
    sku = DummySKU(product=product, package_spec=package_spec)
    (
        unit_price,
        pack_price,
        carton_price,
        price_per_litre,
        price_per_pure_alcohol,
        standard_drinks,
        units_per_pack,
    ) = compute_price_metrics(
        sku=sku,
        price_inc_gst=Decimal("55.00"),
        carton_units=None,
        is_carton_price=False,
        is_pack_price=False,
    )
    assert unit_price == Decimal("55.00")
    assert pack_price is None
    assert carton_price is None
    assert price_per_litre.quantize(Decimal("0.01")) == Decimal("78.57")
    assert standard_drinks > 0
    assert price_per_pure_alcohol > 0
    assert units_per_pack == 1

    _, _, carton_price_direct, _, _, _, _ = compute_price_metrics(
        sku=sku,
        price_inc_gst=Decimal("330.00"),
        carton_units=6,
        is_carton_price=True,
        is_pack_price=False,
    )
    assert carton_price_direct == Decimal("330.00")


def test_compute_price_metrics_pack_price():
    product = DummyProduct(abv_percent=Decimal("6.0"))
    package_spec = DummyPackageSpec(type="can", container_ml=250)
    pack_spec = SimpleNamespace(units_per_pack=4)
    sku = DummySKU(
        product=product,
        package_spec=package_spec,
        pack_assignment=SimpleNamespace(pack_spec=pack_spec),
    )
    unit_price, pack_price, carton_price, _, _, _, units_per_pack = (
        compute_price_metrics(
            sku=sku,
            price_inc_gst=Decimal("40.00"),
            carton_units=None,
            is_carton_price=False,
            is_pack_price=True,
        )
    )
    assert pack_price == Decimal("40.00")
    assert unit_price == Decimal("10.00")
    assert carton_price is None
    assert units_per_pack == 4


def test_normalize_price_includes_costs():
    product = DummyProduct(abv_percent=Decimal("6.0"))
    package_spec = DummyPackageSpec(type="can", container_ml=250)
    pack_spec = SimpleNamespace(units_per_pack=4)
    known_cost = SimpleNamespace(
        cost_type="known",
        cost_currency="AUD",
        cost_per_unit=Decimal("8.50"),
        cost_per_pack=None,
        cost_per_carton=None,
        effective_date=date(2025, 1, 2),
        deleted_at=None,
    )
    estimated_cost = SimpleNamespace(
        cost_type="estimated",
        cost_currency="AUD",
        cost_per_unit=Decimal("8.75"),
        cost_per_pack=None,
        cost_per_carton=None,
        effective_date=date(2025, 1, 1),
        deleted_at=None,
    )
    sku = DummySKU(
        product=product,
        package_spec=package_spec,
        pack_assignment=SimpleNamespace(pack_spec=pack_spec),
        purchase_prices=[estimated_cost, known_cost],
    )
    normalized = normalize_price(
        sku=sku,
        price_ex_gst_raw=None,
        price_inc_gst_raw=Decimal("40.00"),
        gst_rate=Decimal("0.10"),
        carton_units=None,
        is_carton_price=False,
        is_pack_price=True,
    )
    assert normalized.pack_price_inc_gst == Decimal("40.00")
    assert normalized.unit_price_inc_gst == Decimal("10.00")
    assert normalized.price_basis == "pack"
    assert normalized.gp_unit_abs == Decimal("0.59")
    assert pytest.approx(float(normalized.gp_unit_pct), rel=1e-3) == 0.0695


def test_compute_observation_hash_consistent():
    hash1 = compute_observation_hash(
        sku_id="sku-1",
        company_id="company-1",
        location_id="loc-1",
        observation_dt=datetime(2025, 1, 1),
        channel="retail_instore",
        price_inc_gst_norm=Decimal("55.00"),
        is_carton_price=False,
        carton_units=None,
        price_context="shelf",
    )
    hash2 = compute_observation_hash(
        sku_id="sku-1",
        company_id="company-1",
        location_id="loc-1",
        observation_dt=datetime(2025, 1, 1),
        channel="retail_instore",
        price_inc_gst_norm=Decimal("55.00"),
        is_carton_price=False,
        carton_units=None,
        price_context="shelf",
    )
    assert hash1 == hash2

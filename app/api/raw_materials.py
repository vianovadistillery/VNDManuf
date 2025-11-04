# app/api/raw_materials.py
"""Raw Materials API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Supplier
from app.adapters.db.qb_models import RawMaterial, RawMaterialGroup, RawMaterialSupplier
from app.api.dto import (
    RawMaterialCreate,
    RawMaterialGroupResponse,
    RawMaterialResponse,
    RawMaterialUpdate,
)

router = APIRouter(prefix="/raw-materials", tags=["raw-materials"])


def raw_material_to_response(rm: RawMaterial) -> RawMaterialResponse:
    """Convert RawMaterial model to response DTO."""
    return RawMaterialResponse(
        id=str(rm.id),
        code=rm.code,
        desc1=rm.desc1,
        desc2=rm.desc2,
        search_key=rm.search_key,
        search_ext=rm.search_ext,
        sg=float(rm.sg) if rm.sg else None,
        purchase_cost=float(rm.purchase_cost) if rm.purchase_cost else None,
        purchase_unit=rm.purchase_unit,
        usage_cost=float(rm.usage_cost) if rm.usage_cost else None,
        usage_unit=rm.usage_unit,
        deal_cost=float(rm.deal_cost) if rm.deal_cost else None,
        sup_unit=rm.sup_unit,
        sup_qty=float(rm.sup_qty) if rm.sup_qty else None,
        group_id=rm.group_id,
        active_flag=rm.active_flag,
        soh=float(rm.soh) if rm.soh else None,
        opening_soh=float(rm.opening_soh) if rm.opening_soh else None,
        soh_value=float(rm.soh_value) if rm.soh_value else None,
        so_on_order=rm.so_on_order,
        so_in_process=float(rm.so_in_process) if rm.so_in_process else None,
        restock_level=float(rm.restock_level) if rm.restock_level else None,
        used_ytd=float(rm.used_ytd) if rm.used_ytd else None,
        hazard=rm.hazard,
        condition=rm.condition,
        msds_flag=rm.msds_flag,
        altno1=rm.altno1,
        altno2=rm.altno2,
        altno3=rm.altno3,
        altno4=rm.altno4,
        altno5=rm.altno5,
        last_movement_date=rm.last_movement_date,
        last_purchase_date=rm.last_purchase_date,
        notes=rm.notes,
        ean13=float(rm.ean13) if rm.ean13 else None,
        xero_account=rm.xero_account,
        created_at=rm.created_at,
        updated_at=rm.updated_at,
    )


@router.get("/", response_model=List[RawMaterialResponse])
async def list_raw_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, regex="^(A|S|R|M|all)$"),
    group_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List raw materials with optional filtering."""
    stmt = select(RawMaterial)

    # Filter by status
    if status and status.lower() != "all":
        stmt = stmt.where(RawMaterial.active_flag == status.upper())

    # Filter by group
    if group_id:
        stmt = stmt.where(RawMaterial.group_id == group_id)

    # Search filter
    if search:
        stmt = stmt.where(
            or_(
                RawMaterial.desc1.contains(search),
                RawMaterial.desc2.contains(search),
                RawMaterial.search_key.contains(search),
                RawMaterial.notes.contains(search),
            )
        )

    stmt = stmt.order_by(RawMaterial.code).offset(skip).limit(limit)
    raw_materials = db.execute(stmt).scalars().all()

    return [raw_material_to_response(rm) for rm in raw_materials]


@router.get("/groups", response_model=List[RawMaterialGroupResponse])
async def list_raw_material_groups(db: Session = Depends(get_db)):
    """List all raw material groups."""
    groups = (
        db.query(RawMaterialGroup)
        .filter(RawMaterialGroup.is_active.is_(True))
        .order_by(RawMaterialGroup.code)
        .all()
    )
    return [
        RawMaterialGroupResponse(
            id=str(g.id),
            code=g.code,
            name=g.name,
            description=g.description,
            is_active=g.is_active,
            created_at=g.created_at,
        )
        for g in groups
    ]


@router.get("/{raw_material_id}", response_model=RawMaterialResponse)
async def get_raw_material(raw_material_id: str, db: Session = Depends(get_db)):
    """Get raw material by ID."""
    raw_material = db.get(RawMaterial, raw_material_id)
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Raw material not found"
        )

    return raw_material_to_response(raw_material)


@router.get("/code/{code}", response_model=RawMaterialResponse)
async def get_raw_material_by_code(code: int, db: Session = Depends(get_db)):
    """Get raw material by code."""
    stmt = select(RawMaterial).where(RawMaterial.code == code)
    raw_material = db.execute(stmt).scalar_one_or_none()

    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Raw material not found"
        )

    return raw_material_to_response(raw_material)


@router.post(
    "/", response_model=RawMaterialResponse, status_code=status.HTTP_201_CREATED
)
async def create_raw_material(
    material: RawMaterialCreate, db: Session = Depends(get_db)
):
    """Create a new raw material."""
    # Check if code already exists
    existing = db.execute(
        select(RawMaterial).where(RawMaterial.code == material.code)
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Raw material with code {material.code} already exists",
        )

    # Validate group exists
    if material.group_id:
        group = db.get(RawMaterialGroup, material.group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Raw material group {material.group_id} not found",
            )

    # Create raw material
    import uuid

    raw_material = RawMaterial(
        id=str(uuid.uuid4()),
        code=material.code,
        desc1=material.desc1,
        desc2=material.desc2,
        search_key=material.search_key,
        search_ext=material.search_ext,
        sg=material.sg,
        purchase_cost=material.purchase_cost,
        purchase_unit=material.purchase_unit,
        usage_cost=material.usage_cost,
        usage_unit=material.usage_unit,
        deal_cost=material.deal_cost,
        sup_unit=material.sup_unit,
        sup_qty=material.sup_qty,
        group_id=material.group_id,
        active_flag=material.active_flag,
        soh=material.soh,
        restock_level=material.restock_level,
        hazard=material.hazard,
        condition=material.condition,
        msds_flag=material.msds_flag,
        notes=material.notes,
        xero_account=material.xero_account,
    )

    db.add(raw_material)
    db.commit()
    db.refresh(raw_material)

    return raw_material_to_response(raw_material)


@router.put("/{raw_material_id}", response_model=RawMaterialResponse)
async def update_raw_material(
    raw_material_id: str, material: RawMaterialUpdate, db: Session = Depends(get_db)
):
    """Update a raw material."""
    raw_material = db.get(RawMaterial, raw_material_id)
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Raw material not found"
        )

    # Update fields
    if material.desc1 is not None:
        raw_material.desc1 = material.desc1
    if material.desc2 is not None:
        raw_material.desc2 = material.desc2
    if material.search_key is not None:
        raw_material.search_key = material.search_key
    if material.search_ext is not None:
        raw_material.search_ext = material.search_ext
    if material.sg is not None:
        raw_material.sg = material.sg
    if material.purchase_cost is not None:
        raw_material.purchase_cost = material.purchase_cost
    if material.purchase_unit is not None:
        raw_material.purchase_unit = material.purchase_unit
    if material.usage_cost is not None:
        raw_material.usage_cost = material.usage_cost
    if material.usage_unit is not None:
        raw_material.usage_unit = material.usage_unit
    if material.deal_cost is not None:
        raw_material.deal_cost = material.deal_cost
    if material.sup_unit is not None:
        raw_material.sup_unit = material.sup_unit
    if material.sup_qty is not None:
        raw_material.sup_qty = material.sup_qty
    if material.active_flag is not None:
        raw_material.active_flag = material.active_flag
    if material.soh is not None:
        raw_material.soh = material.soh
    if material.opening_soh is not None:
        raw_material.opening_soh = material.opening_soh
    if material.soh_value is not None:
        raw_material.soh_value = material.soh_value
    if material.restock_level is not None:
        raw_material.restock_level = material.restock_level
    if material.hazard is not None:
        raw_material.hazard = material.hazard
    if material.condition is not None:
        raw_material.condition = material.condition
    if material.msds_flag is not None:
        raw_material.msds_flag = material.msds_flag
    if material.notes is not None:
        raw_material.notes = material.notes
    if material.xero_account is not None:
        raw_material.xero_account = material.xero_account
    if material.group_id is not None:
        # Validate group exists
        group = db.get(RawMaterialGroup, material.group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Raw material group {material.group_id} not found",
            )
        raw_material.group_id = material.group_id

    db.commit()
    db.refresh(raw_material)

    return raw_material_to_response(raw_material)


@router.delete("/{raw_material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_raw_material(raw_material_id: str, db: Session = Depends(get_db)):
    """Soft delete a raw material (marks as deleted, does not remove from database)."""
    from app.services.audit import soft_delete

    raw_material = db.get(RawMaterial, raw_material_id)
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Raw material not found"
        )

    soft_delete(db, raw_material)
    db.commit()
    return None


# Supplier relationship endpoints
@router.post("/{raw_material_id}/suppliers")
async def add_raw_material_supplier(
    raw_material_id: str, supplier_data: dict, db: Session = Depends(get_db)
):
    """Add supplier to raw material."""
    from pydantic import BaseModel

    class SupplierRelationship(BaseModel):
        supplier_id: str

    data = SupplierRelationship(**supplier_data)

    # Validate raw material exists
    raw_material = db.get(RawMaterial, raw_material_id)
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Raw material not found"
        )

    # Validate supplier exists
    supplier = db.get(Supplier, data.supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )

    # Check if relationship already exists
    existing = db.execute(
        select(RawMaterialSupplier).where(
            and_(
                RawMaterialSupplier.raw_material_id == raw_material_id,
                RawMaterialSupplier.supplier_id == data.supplier_id,
            )
        )
    ).scalar_one_or_none()

    if existing:
        return {"message": "Supplier relationship already exists"}

    # Create relationship
    import uuid

    rm_supplier = RawMaterialSupplier(
        id=str(uuid.uuid4()),
        raw_material_id=raw_material_id,
        supplier_id=data.supplier_id,
    )
    db.add(rm_supplier)
    db.commit()

    return {"message": "Supplier added successfully"}


@router.delete("/{raw_material_id}/suppliers/{supplier_id}")
async def remove_raw_material_supplier(
    raw_material_id: str, supplier_id: str, db: Session = Depends(get_db)
):
    """Remove supplier from raw material."""
    relationship = db.execute(
        select(RawMaterialSupplier).where(
            and_(
                RawMaterialSupplier.raw_material_id == raw_material_id,
                RawMaterialSupplier.supplier_id == supplier_id,
            )
        )
    ).scalar_one_or_none()

    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier relationship not found",
        )

    from app.services.audit import soft_delete

    soft_delete(db, relationship)
    db.commit()
    return {"message": "Supplier removed successfully"}


@router.get("/{raw_material_id}/suppliers")
async def get_raw_material_suppliers(
    raw_material_id: str, db: Session = Depends(get_db)
):
    """Get suppliers for a raw material."""
    relationships = (
        db.execute(
            select(RawMaterialSupplier).where(
                RawMaterialSupplier.raw_material_id == raw_material_id
            )
        )
        .scalars()
        .all()
    )

    supplier_ids = [rel.supplier_id for rel in relationships]
    suppliers = []
    for sid in supplier_ids:
        supplier = db.get(Supplier, sid)
        if supplier:
            suppliers.append(supplier)

    from app.api.suppliers import supplier_to_response

    return [supplier_to_response(s) for s in suppliers]

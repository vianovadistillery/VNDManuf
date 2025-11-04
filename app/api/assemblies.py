from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, condecimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models_assemblies_shopify import Assembly
from app.services.assembly_service import AssemblyService

router = APIRouter(prefix="/assemblies", tags=["assemblies"])


class AssemblyResponse(BaseModel):
    """Assembly response DTO."""

    id: str
    parent_product_id: str
    assembly_code: str
    assembly_name: str
    is_active: bool
    is_primary: bool
    yield_factor: Optional[Decimal] = None

    class Config:
        from_attributes = True


class AssembleReq(BaseModel):
    parent_product_id: str
    qty: condecimal(gt=0)
    reason: str = "ASSEMBLE"


@router.get("/", response_model=List[AssemblyResponse])
async def list_assemblies(
    product_id: Optional[str] = Query(None, description="Filter by parent product ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """List assemblies, optionally filtered by product."""
    stmt = select(Assembly)

    if product_id:
        stmt = stmt.where(Assembly.parent_product_id == product_id)

    if is_active is not None:
        stmt = stmt.where(Assembly.is_active == is_active)

    assemblies = db.execute(stmt).scalars().all()

    return [
        AssemblyResponse(
            id=str(a.id),
            parent_product_id=str(a.parent_product_id),
            assembly_code=a.assembly_code,
            assembly_name=a.assembly_name,
            is_active=a.is_active,
            is_primary=a.is_primary,
            yield_factor=a.yield_factor,
        )
        for a in assemblies
    ]


@router.post("/assemble")
def assemble(req: AssembleReq, db: Session = Depends(get_db)):
    """
    Assemble a parent product from its child components.
    """
    try:
        svc = AssemblyService(db)
        result = svc.assemble(req.parent_product_id, Decimal(req.qty), req.reason)
        db.commit()
        return {"ok": True, "result": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assembly failed: {str(e)}",
        )


class DisassembleReq(BaseModel):
    parent_product_id: str
    qty: condecimal(gt=0)
    reason: str = "DISASSEMBLE"


@router.post("/disassemble")
def disassemble(req: DisassembleReq, db: Session = Depends(get_db)):
    """
    Disassemble a parent product into its child components.
    """
    try:
        svc = AssemblyService(db)
        result = svc.disassemble(req.parent_product_id, Decimal(req.qty), req.reason)
        db.commit()
        return {"ok": True, "result": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disassembly failed: {str(e)}",
        )

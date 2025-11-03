from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, condecimal
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.services.assembly_service import AssemblyService

router = APIRouter(prefix="/assemblies", tags=["assemblies"])


class AssembleReq(BaseModel):
    parent_product_id: str
    qty: condecimal(gt=0)
    reason: str = "ASSEMBLE"


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

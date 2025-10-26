from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from decimal import Decimal

# from app.adapters.db import get_db
# from sqlalchemy.orm import Session
# from app.services.assembly_service import AssemblyService

router = APIRouter(prefix="/assemblies", tags=["assemblies"])

class AssembleReq(BaseModel):
    parent_product_id: str
    qty: condecimal(gt=0)
    reason: str = "ASSEMBLE"

@router.post("/assemble")
def assemble(req: AssembleReq):
    # db: Session = Depends(get_db)
    # svc = AssemblyService(db)
    # svc.assemble(req.parent_product_id, Decimal(req.qty), req.reason)
    return {"ok": True, "note": "assemble stub"}

class DisassembleReq(BaseModel):
    parent_product_id: str
    qty: condecimal(gt=0)
    reason: str = "DISASSEMBLE"

@router.post("/disassemble")
def disassemble(req: DisassembleReq):
    # db: Session = Depends(get_db)
    # svc = AssemblyService(db)
    # svc.disassemble(req.parent_product_id, Decimal(req.qty), req.reason)
    return {"ok": True, "note": "disassemble stub"}


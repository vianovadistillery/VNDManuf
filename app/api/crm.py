"""CRM API router — customer workspace, activities, staff, assignments."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.adapters.db import get_db
from app.adapters.db.models import (
    BuyingGroup,
    CrmActivity,
    CrmCustomerStaff,
    Customer,
    CustomerRepAssignment,
    CustomerSite,
    SalesOrder,
    SalesRep,
)
from app.api.crm_extra import register_crm_extra_routes
from app.api.sales import OrderProductSummaryResponse, _get_filtered_orders

router = APIRouter(prefix="/crm", tags=["crm"])

ScopeType = Literal["my", "team", "all"]


# --------------------------------------------------------------------------- #
# DTOs
# --------------------------------------------------------------------------- #
class CrmCustomerSearchResult(BaseModel):
    id: str
    code: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    customer_type: Optional[str] = None
    buying_group_name: Optional[str] = None
    primary_rep_name: Optional[str] = None
    has_contact: bool = False


class RepAssignmentResponse(BaseModel):
    id: str
    customer_id: str
    sales_rep_id: str
    sales_rep_name: Optional[str] = None
    role: str
    assigned_at: datetime

    class Config:
        from_attributes = True


class RepAssignmentCreate(BaseModel):
    sales_rep_id: str
    role: str = "primary"


class CustomerProfileUpdate(BaseModel):
    buying_group_id: Optional[str] = None
    relationship_status: Optional[str] = None
    visit_frequency_target_days: Optional[int] = None
    preferred_contact_method: Optional[str] = None


class CustomerProfileResponse(BaseModel):
    id: str
    code: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    customer_type: Optional[str] = None
    contact_id: Optional[str] = None
    buying_group_id: Optional[str] = None
    buying_group_name: Optional[str] = None
    relationship_status: Optional[str] = None
    visit_frequency_target_days: Optional[int] = None
    preferred_contact_method: Optional[str] = None
    notes: Optional[str] = None
    primary_rep: Optional[RepAssignmentResponse] = None


class CrmActivityCreate(BaseModel):
    activity_type: str = Field(default="note")
    subject: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    activity_at: Optional[datetime] = None
    note_category: Optional[str] = None
    sales_rep_id: Optional[str] = None
    customer_site_id: Optional[str] = None
    is_pinned: bool = False


class CrmActivityUpdate(BaseModel):
    activity_type: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    activity_at: Optional[datetime] = None
    note_category: Optional[str] = None
    sales_rep_id: Optional[str] = None
    is_pinned: Optional[bool] = None


class CrmActivityResponse(BaseModel):
    id: str
    customer_id: str
    activity_type: str
    subject: Optional[str] = None
    body: Optional[str] = None
    activity_at: datetime
    note_category: Optional[str] = None
    is_pinned: bool
    sales_rep_id: Optional[str] = None
    sales_rep_name: Optional[str] = None
    linked_sales_order_id: Optional[str] = None
    source: str = "activity"

    class Config:
        from_attributes = True


class CrmStaffCreate(BaseModel):
    name: str = Field(..., max_length=100)
    role: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    customer_site_id: Optional[str] = None
    is_primary: bool = False


class CrmStaffUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    customer_site_id: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class CrmStaffResponse(BaseModel):
    id: str
    customer_id: str
    customer_site_id: Optional[str] = None
    name: str
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    is_primary: bool
    is_active: bool

    class Config:
        from_attributes = True


class CrmDashboardResponse(BaseModel):
    profile: CustomerProfileResponse
    sales_summary: OrderProductSummaryResponse


class CrmTimelineResponse(BaseModel):
    items: List[CrmActivityResponse]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _get_customer(db: Session, customer_id: str) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer or customer.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    return customer


def _primary_rep_assignment(
    db: Session, customer_id: str
) -> Optional[CustomerRepAssignment]:
    return db.execute(
        select(CustomerRepAssignment)
        .where(
            CustomerRepAssignment.customer_id == customer_id,
            CustomerRepAssignment.role == "primary",
            CustomerRepAssignment.deleted_at.is_(None),
        )
        .options(joinedload(CustomerRepAssignment.sales_rep))
    ).scalar_one_or_none()


def _profile_response(db: Session, customer: Customer) -> CustomerProfileResponse:
    buying_group_name = None
    if customer.buying_group_id:
        bg = db.get(BuyingGroup, customer.buying_group_id)
        if bg and bg.deleted_at is None:
            buying_group_name = bg.name
    primary = _primary_rep_assignment(db, str(customer.id))
    primary_resp = None
    if primary:
        primary_resp = RepAssignmentResponse(
            id=str(primary.id),
            customer_id=str(primary.customer_id),
            sales_rep_id=str(primary.sales_rep_id),
            sales_rep_name=primary.sales_rep.name if primary.sales_rep else None,
            role=primary.role,
            assigned_at=primary.assigned_at,
        )
    return CustomerProfileResponse(
        id=str(customer.id),
        code=customer.code,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        customer_type=customer.customer_type,
        contact_id=str(customer.contact_id) if customer.contact_id else None,
        buying_group_id=str(customer.buying_group_id)
        if customer.buying_group_id
        else None,
        buying_group_name=buying_group_name,
        relationship_status=getattr(customer, "relationship_status", None) or "active",
        visit_frequency_target_days=customer.visit_frequency_target_days,
        preferred_contact_method=customer.preferred_contact_method,
        notes=customer.notes,
        primary_rep=primary_resp,
    )


def _activity_response(activity: CrmActivity) -> CrmActivityResponse:
    return CrmActivityResponse(
        id=str(activity.id),
        customer_id=str(activity.customer_id),
        activity_type=activity.activity_type,
        subject=activity.subject,
        body=activity.body,
        activity_at=activity.activity_at,
        note_category=activity.note_category,
        is_pinned=activity.is_pinned,
        sales_rep_id=str(activity.sales_rep_id) if activity.sales_rep_id else None,
        sales_rep_name=activity.sales_rep.name if activity.sales_rep else None,
        linked_sales_order_id=(
            str(activity.linked_sales_order_id)
            if activity.linked_sales_order_id
            else None
        ),
        source="activity",
    )


def _build_product_summary(
    db: Session, orders: List[SalesOrder]
) -> OrderProductSummaryResponse:
    from app.adapters.db.models import Product, SalesOrderLine
    from app.api.sales import OrderProductSummaryRow, OrderSummaryRow

    order_ids = [o.id for o in orders]
    order_rows = [
        OrderSummaryRow(
            order_id=str(order.id),
            order_date=(
                order.order_date.date().isoformat()
                if order.order_date and hasattr(order.order_date, "date")
                else (str(order.order_date)[:10] if order.order_date else "")
            ),
            order_ref=order.order_ref or "—",
            po_number=order.po_number or "—",
            status=(order.status or "").title(),
            total_ex_gst=float(order.total_ex_gst or 0),
            total_inc_gst=float(order.total_inc_gst or 0),
        )
        for order in orders
    ]
    if not order_ids:
        return OrderProductSummaryResponse(
            orders=[],
            rows=[],
            order_count=0,
            total_qty=0.0,
            total_ex_gst=0.0,
            total_inc_gst=0.0,
        )
    agg_stmt = (
        select(
            SalesOrderLine.product_id,
            func.sum(SalesOrderLine.qty).label("total_qty"),
            func.count(func.distinct(SalesOrderLine.order_id)).label("order_count"),
            func.sum(SalesOrderLine.line_total_ex_gst).label("total_ex_gst"),
            func.sum(SalesOrderLine.line_total_inc_gst).label("total_inc_gst"),
        )
        .where(SalesOrderLine.order_id.in_(order_ids))
        .group_by(SalesOrderLine.product_id)
    )
    agg_rows = db.execute(agg_stmt).all()
    product_ids = [row.product_id for row in agg_rows]
    products = {}
    if product_ids:
        for p in db.execute(
            select(Product).where(Product.id.in_(product_ids))
        ).scalars():
            products[str(p.id)] = p
    summary_rows = []
    total_qty = 0.0
    total_ex = 0.0
    total_inc = 0.0
    for row in agg_rows:
        pid = str(row.product_id)
        product = products.get(pid)
        qty = float(row.total_qty or 0)
        ex = float(row.total_ex_gst or 0)
        inc = float(row.total_inc_gst or 0)
        total_qty += qty
        total_ex += ex
        total_inc += inc
        summary_rows.append(
            OrderProductSummaryRow(
                product_id=pid,
                sku=product.sku if product else "—",
                name=product.name if product else "—",
                total_qty=qty,
                order_count=int(row.order_count or 0),
                total_ex_gst=ex,
                total_inc_gst=inc,
            )
        )
    summary_rows.sort(key=lambda r: r.total_qty, reverse=True)
    return OrderProductSummaryResponse(
        orders=order_rows,
        rows=summary_rows,
        order_count=len(orders),
        total_qty=total_qty,
        total_ex_gst=total_ex,
        total_inc_gst=total_inc,
    )


def _customer_search_query(
    db: Session,
    q: Optional[str],
    rep_id: Optional[str],
    scope: ScopeType,
):
    stmt = (
        select(Customer)
        .where(Customer.deleted_at.is_(None), Customer.is_active.is_(True))
        .options(joinedload(Customer.buying_group))
    )
    if q:
        stmt = stmt.where(or_(Customer.name.contains(q), Customer.code.contains(q)))
    if rep_id and scope == "my":
        stmt = stmt.join(
            CustomerRepAssignment,
            CustomerRepAssignment.customer_id == Customer.id,
        ).where(
            CustomerRepAssignment.sales_rep_id == rep_id,
            CustomerRepAssignment.deleted_at.is_(None),
        )
    elif rep_id and scope == "team":
        pass
    stmt = stmt.order_by(Customer.name).limit(100)
    return db.execute(stmt).scalars().unique().all()


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@router.get("/customers/search", response_model=List[CrmCustomerSearchResult])
def search_customers(
    q: Optional[str] = Query(None, description="Name or code search"),
    rep_id: Optional[str] = Query(None),
    scope: ScopeType = Query("all"),
    db: Session = Depends(get_db),
):
    customers = _customer_search_query(db, q, rep_id, scope)
    results = []
    for c in customers:
        primary = _primary_rep_assignment(db, str(c.id))
        results.append(
            CrmCustomerSearchResult(
                id=str(c.id),
                code=c.code,
                name=c.name,
                email=c.email,
                phone=c.phone,
                customer_type=c.customer_type,
                buying_group_name=c.buying_group.name if c.buying_group else None,
                primary_rep_name=(
                    primary.sales_rep.name if primary and primary.sales_rep else None
                ),
                has_contact=bool(c.contact_id),
            )
        )
    return results


@router.get("/customers/{customer_id}/profile", response_model=CustomerProfileResponse)
def get_customer_profile(customer_id: str, db: Session = Depends(get_db)):
    return _profile_response(db, _get_customer(db, customer_id))


@router.patch(
    "/customers/{customer_id}/profile", response_model=CustomerProfileResponse
)
def update_customer_profile(
    customer_id: str,
    data: CustomerProfileUpdate,
    db: Session = Depends(get_db),
):
    customer = _get_customer(db, customer_id)
    if data.buying_group_id is not None:
        if data.buying_group_id:
            bg = db.get(BuyingGroup, data.buying_group_id)
            if not bg or bg.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid buying group",
                )
        customer.buying_group_id = data.buying_group_id or None
    if data.relationship_status is not None:
        if data.relationship_status not in ("active", "prospective", "lapsed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="relationship_status must be active, prospective, or lapsed",
            )
        customer.relationship_status = data.relationship_status
    if data.visit_frequency_target_days is not None:
        customer.visit_frequency_target_days = data.visit_frequency_target_days
    if data.preferred_contact_method is not None:
        customer.preferred_contact_method = data.preferred_contact_method
    db.commit()
    db.refresh(customer)
    return _profile_response(db, customer)


@router.get("/customers/{customer_id}/dashboard", response_model=CrmDashboardResponse)
def customer_dashboard(
    customer_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    customer = _get_customer(db, customer_id)
    orders = _get_filtered_orders(
        db,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
    )
    return CrmDashboardResponse(
        profile=_profile_response(db, customer),
        sales_summary=_build_product_summary(db, orders),
    )


@router.get("/customers/{customer_id}/timeline", response_model=CrmTimelineResponse)
def customer_timeline(
    customer_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    _get_customer(db, customer_id)
    act_stmt = (
        select(CrmActivity)
        .where(
            CrmActivity.customer_id == customer_id,
            CrmActivity.deleted_at.is_(None),
        )
        .options(joinedload(CrmActivity.sales_rep))
    )
    if start_date:
        act_stmt = act_stmt.where(
            CrmActivity.activity_at >= datetime.combine(start_date, datetime.min.time())
        )
    if end_date:
        act_stmt = act_stmt.where(
            CrmActivity.activity_at <= datetime.combine(end_date, datetime.max.time())
        )
    activities = db.execute(act_stmt).scalars().all()

    orders = _get_filtered_orders(
        db,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
    )
    items: List[CrmActivityResponse] = [_activity_response(a) for a in activities]
    for order in orders:
        items.append(
            CrmActivityResponse(
                id=f"order-{order.id}",
                customer_id=customer_id,
                activity_type="order_event",
                subject=f"Order {order.order_ref or order.id}",
                body=f"Status: {(order.status or '').title()} · ${float(order.total_inc_gst or 0):,.2f} inc GST",
                activity_at=order.order_date or datetime.utcnow(),
                note_category=None,
                is_pinned=False,
                sales_rep_id=None,
                sales_rep_name=None,
                linked_sales_order_id=str(order.id),
                source="order",
            )
        )
    items.sort(key=lambda x: x.activity_at, reverse=True)
    return CrmTimelineResponse(items=items)


@router.get("/customers/{customer_id}/reps", response_model=List[RepAssignmentResponse])
def list_rep_assignments(customer_id: str, db: Session = Depends(get_db)):
    _get_customer(db, customer_id)
    rows = (
        db.execute(
            select(CustomerRepAssignment)
            .where(
                CustomerRepAssignment.customer_id == customer_id,
                CustomerRepAssignment.deleted_at.is_(None),
            )
            .options(joinedload(CustomerRepAssignment.sales_rep))
        )
        .scalars()
        .all()
    )
    return [
        RepAssignmentResponse(
            id=str(r.id),
            customer_id=str(r.customer_id),
            sales_rep_id=str(r.sales_rep_id),
            sales_rep_name=r.sales_rep.name if r.sales_rep else None,
            role=r.role,
            assigned_at=r.assigned_at,
        )
        for r in rows
    ]


@router.post(
    "/customers/{customer_id}/reps",
    response_model=RepAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_rep(
    customer_id: str, data: RepAssignmentCreate, db: Session = Depends(get_db)
):
    _get_customer(db, customer_id)
    rep = db.get(SalesRep, data.sales_rep_id)
    if not rep or rep.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sales rep"
        )
    if data.role == "primary":
        existing_primary = _primary_rep_assignment(db, customer_id)
        if existing_primary:
            existing_primary.role = "secondary"
    existing = db.execute(
        select(CustomerRepAssignment).where(
            CustomerRepAssignment.customer_id == customer_id,
            CustomerRepAssignment.sales_rep_id == data.sales_rep_id,
            CustomerRepAssignment.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        existing.role = data.role
        db.commit()
        db.refresh(existing)
        row = existing
    else:
        row = CustomerRepAssignment(
            customer_id=customer_id,
            sales_rep_id=data.sales_rep_id,
            role=data.role,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    return RepAssignmentResponse(
        id=str(row.id),
        customer_id=str(row.customer_id),
        sales_rep_id=str(row.sales_rep_id),
        sales_rep_name=rep.name,
        role=row.role,
        assigned_at=row.assigned_at,
    )


@router.get(
    "/customers/{customer_id}/activities", response_model=List[CrmActivityResponse]
)
def list_activities(customer_id: str, db: Session = Depends(get_db)):
    _get_customer(db, customer_id)
    rows = (
        db.execute(
            select(CrmActivity)
            .where(
                CrmActivity.customer_id == customer_id,
                CrmActivity.deleted_at.is_(None),
            )
            .options(joinedload(CrmActivity.sales_rep))
            .order_by(CrmActivity.activity_at.desc())
        )
        .scalars()
        .all()
    )
    return [_activity_response(a) for a in rows]


@router.post(
    "/customers/{customer_id}/activities",
    response_model=CrmActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    customer_id: str, data: CrmActivityCreate, db: Session = Depends(get_db)
):
    customer = _get_customer(db, customer_id)
    if data.sales_rep_id:
        rep = db.get(SalesRep, data.sales_rep_id)
        if not rep or rep.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sales rep"
            )
    activity = CrmActivity(
        customer_id=customer_id,
        contact_id=customer.contact_id,
        customer_site_id=data.customer_site_id,
        sales_rep_id=data.sales_rep_id,
        activity_type=data.activity_type,
        subject=data.subject,
        body=data.body,
        activity_at=data.activity_at or datetime.utcnow(),
        note_category=data.note_category,
        is_pinned=data.is_pinned,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    if data.sales_rep_id:
        activity.sales_rep = db.get(SalesRep, data.sales_rep_id)
    return _activity_response(activity)


@router.put("/activities/{activity_id}", response_model=CrmActivityResponse)
def update_activity(
    activity_id: str, data: CrmActivityUpdate, db: Session = Depends(get_db)
):
    activity = db.get(CrmActivity, activity_id)
    if not activity or activity.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )
    if data.sales_rep_id:
        rep = db.get(SalesRep, data.sales_rep_id)
        if not rep or rep.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sales rep"
            )
    for field in (
        "activity_type",
        "subject",
        "body",
        "activity_at",
        "note_category",
        "sales_rep_id",
        "is_pinned",
    ):
        val = getattr(data, field)
        if val is not None:
            setattr(activity, field, val)
    db.commit()
    db.refresh(activity)
    activity = db.execute(
        select(CrmActivity)
        .where(CrmActivity.id == activity_id)
        .options(joinedload(CrmActivity.sales_rep))
    ).scalar_one()
    return _activity_response(activity)


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: str, db: Session = Depends(get_db)):
    from app.services.audit import soft_delete

    activity = db.get(CrmActivity, activity_id)
    if not activity or activity.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )
    soft_delete(db, activity)
    db.commit()
    return None


@router.get("/customers/{customer_id}/staff", response_model=List[CrmStaffResponse])
def list_staff(customer_id: str, db: Session = Depends(get_db)):
    _get_customer(db, customer_id)
    rows = (
        db.execute(
            select(CrmCustomerStaff)
            .where(
                CrmCustomerStaff.customer_id == customer_id,
                CrmCustomerStaff.deleted_at.is_(None),
            )
            .order_by(CrmCustomerStaff.is_primary.desc(), CrmCustomerStaff.name)
        )
        .scalars()
        .all()
    )
    return [CrmStaffResponse.model_validate(r) for r in rows]


@router.post(
    "/customers/{customer_id}/staff",
    response_model=CrmStaffResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_staff(customer_id: str, data: CrmStaffCreate, db: Session = Depends(get_db)):
    _get_customer(db, customer_id)
    if data.customer_site_id:
        site = db.get(CustomerSite, data.customer_site_id)
        if not site or site.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid site"
            )
    if data.is_primary:
        for row in db.execute(
            select(CrmCustomerStaff).where(
                CrmCustomerStaff.customer_id == customer_id,
                CrmCustomerStaff.is_primary.is_(True),
                CrmCustomerStaff.deleted_at.is_(None),
            )
        ).scalars():
            row.is_primary = False
    staff = CrmCustomerStaff(
        customer_id=customer_id,
        customer_site_id=data.customer_site_id,
        name=data.name,
        role=data.role,
        phone=data.phone,
        email=data.email,
        notes=data.notes,
        is_primary=data.is_primary,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return CrmStaffResponse.model_validate(staff)


@router.put("/staff/{staff_id}", response_model=CrmStaffResponse)
def update_staff(staff_id: str, data: CrmStaffUpdate, db: Session = Depends(get_db)):
    staff = db.get(CrmCustomerStaff, staff_id)
    if not staff or staff.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found"
        )
    if data.is_primary:
        for row in db.execute(
            select(CrmCustomerStaff).where(
                CrmCustomerStaff.customer_id == staff.customer_id,
                CrmCustomerStaff.is_primary.is_(True),
                CrmCustomerStaff.id != staff_id,
                CrmCustomerStaff.deleted_at.is_(None),
            )
        ).scalars():
            row.is_primary = False
    for field in (
        "name",
        "role",
        "phone",
        "email",
        "notes",
        "customer_site_id",
        "is_primary",
        "is_active",
    ):
        val = getattr(data, field)
        if val is not None:
            setattr(staff, field, val)
    db.commit()
    db.refresh(staff)
    return CrmStaffResponse.model_validate(staff)


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: str, db: Session = Depends(get_db)):
    from app.services.audit import soft_delete

    staff = db.get(CrmCustomerStaff, staff_id)
    if not staff or staff.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found"
        )
    soft_delete(db, staff)
    db.commit()
    return None


register_crm_extra_routes(router)

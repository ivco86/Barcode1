from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from app.db.database import get_db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.core.dependencies import get_current_user, check_subscription
from app.api.schemas import SaleCreate, SaleResponse

router = APIRouter(prefix="/sales", tags=["Sales"])


def generate_sale_number(tenant_id: UUID, db: Session) -> str:
    """Generate unique sale number for tenant"""
    today = date.today()
    prefix = today.strftime("%Y%m%d")

    # Count sales today
    count = db.query(func.count(Sale.id)).filter(
        Sale.tenant_id == tenant_id,
        func.date(Sale.created_at) == today
    ).scalar()

    return f"{prefix}-{count + 1:04d}"


@router.get("", response_model=List[SaleResponse])
def get_sales(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    customer_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sales for current tenant"""
    check_subscription(current_user["tenant_id"], db)

    query = db.query(Sale).filter(Sale.tenant_id == current_user["tenant_id"])

    if start_date:
        query = query.filter(func.date(Sale.created_at) >= start_date)

    if end_date:
        query = query.filter(func.date(Sale.created_at) <= end_date)

    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)

    sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    return sales


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single sale"""
    check_subscription(current_user["tenant_id"], db)

    sale = db.query(Sale).filter(
        Sale.id == sale_id,
        Sale.tenant_id == current_user["tenant_id"]
    ).first()

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )

    return sale


@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale: SaleCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new sale"""
    check_subscription(current_user["tenant_id"], db)

    if not sale.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale must have at least one item"
        )

    # Calculate totals
    subtotal = sum(item.quantity * item.unit_price for item in sale.items)
    total = subtotal - sale.discount + sale.tax

    # Generate sale number
    sale_number = generate_sale_number(current_user["tenant_id"], db)

    # Create sale
    db_sale = Sale(
        tenant_id=current_user["tenant_id"],
        sale_number=sale_number,
        cashier_id=current_user["user_id"],
        customer_id=sale.customer_id,
        subtotal=subtotal,
        discount=sale.discount,
        tax=sale.tax,
        total=total,
        payment_method=sale.payment_method,
        notes=sale.notes
    )
    db.add(db_sale)
    db.flush()

    # Create sale items and update stock
    for item in sale.items:
        # Verify product exists and belongs to tenant
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.tenant_id == current_user["tenant_id"]
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )

        # Check stock
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock}"
            )

        # Create sale item
        item_subtotal = item.quantity * item.unit_price
        item_total = item_subtotal - item.discount

        db_item = SaleItem(
            sale_id=db_sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item_subtotal,
            discount=item.discount,
            total=item_total
        )
        db.add(db_item)

        # Update product stock
        product.stock -= item.quantity

    db.commit()
    db.refresh(db_sale)

    return db_sale

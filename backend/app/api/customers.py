from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.database import get_db
from app.models.customer import Customer
from app.core.dependencies import get_current_user, check_subscription
from app.api.schemas import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerResponse])
def get_customers(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all customers for current tenant"""
    check_subscription(current_user["tenant_id"], db)

    query = db.query(Customer).filter(Customer.tenant_id == current_user["tenant_id"])

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_pattern)) |
            (Customer.phone.ilike(search_pattern)) |
            (Customer.email.ilike(search_pattern))
        )

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single customer"""
    check_subscription(current_user["tenant_id"], db)

    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == current_user["tenant_id"]
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: CustomerCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new customer"""
    check_subscription(current_user["tenant_id"], db)

    # Check if phone already exists
    if customer.phone:
        existing = db.query(Customer).filter(
            Customer.phone == customer.phone,
            Customer.tenant_id == current_user["tenant_id"]
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this phone already exists"
            )

    db_customer = Customer(
        tenant_id=current_user["tenant_id"],
        **customer.model_dump()
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    customer: CustomerUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update customer"""
    check_subscription(current_user["tenant_id"], db)

    db_customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == current_user["tenant_id"]
    ).first()

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    update_data = customer.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)

    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete customer"""
    check_subscription(current_user["tenant_id"], db)

    if current_user["role"] not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    db_customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == current_user["tenant_id"]
    ).first()

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    db.delete(db_customer)
    db.commit()

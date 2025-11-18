from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.database import get_db
from app.models.product import Product
from app.core.dependencies import get_current_user, check_subscription
from app.api.schemas import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products for current tenant"""
    check_subscription(current_user["tenant_id"], db)

    query = db.query(Product).filter(Product.tenant_id == current_user["tenant_id"])

    if category:
        query = query.filter(Product.category == category)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_pattern)) |
            (Product.barcode.ilike(search_pattern))
        )

    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single product"""
    check_subscription(current_user["tenant_id"], db)

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == current_user["tenant_id"]
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_product_by_barcode(
    barcode: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get product by barcode"""
    check_subscription(current_user["tenant_id"], db)

    product = db.query(Product).filter(
        Product.barcode == barcode,
        Product.tenant_id == current_user["tenant_id"]
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new product"""
    check_subscription(current_user["tenant_id"], db)

    # Check permissions
    if current_user["role"] not in ["owner", "admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    # Check if barcode already exists
    existing = db.query(Product).filter(
        Product.barcode == product.barcode,
        Product.tenant_id == current_user["tenant_id"]
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this barcode already exists"
        )

    # Create product
    db_product = Product(
        tenant_id=current_user["tenant_id"],
        **product.model_dump()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    product: ProductUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update product"""
    check_subscription(current_user["tenant_id"], db)

    # Check permissions
    if current_user["role"] not in ["owner", "admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == current_user["tenant_id"]
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Update fields
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)

    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete product"""
    check_subscription(current_user["tenant_id"], db)

    # Check permissions
    if current_user["role"] not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == current_user["tenant_id"]
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(db_product)
    db.commit()

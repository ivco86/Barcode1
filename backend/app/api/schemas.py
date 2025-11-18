from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


# === AUTH SCHEMAS ===

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant: dict
    user: dict


# === PRODUCT SCHEMAS ===

class ProductBase(BaseModel):
    barcode: str
    name: str
    description: Optional[str] = None
    price: Decimal
    cost: Optional[Decimal] = None
    stock: int = 0
    min_stock: int = 5
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    barcode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === CUSTOMER SCHEMAS ===

class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    loyalty_points: int
    total_spent: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === SALE SCHEMAS ===

class SaleItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0)
    unit_price: Decimal
    discount: Decimal = 0


class SaleItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    discount: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    customer_id: Optional[uuid.UUID] = None
    items: List[SaleItemCreate]
    discount: Decimal = 0
    tax: Decimal = 0
    payment_method: str = "cash"
    notes: Optional[str] = None


class SaleResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    sale_number: str
    cashier_id: Optional[uuid.UUID]
    customer_id: Optional[uuid.UUID]
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    payment_method: str
    payment_status: str
    notes: Optional[str]
    created_at: datetime
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True


# === USER SCHEMAS ===

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "cashier"


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# === STATS SCHEMAS ===

class DashboardStats(BaseModel):
    total_sales_today: Decimal
    total_sales_count_today: int
    total_products: int
    low_stock_products: int
    total_customers: int
    revenue_last_7_days: List[dict]

from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    sale_number = Column(String(50), nullable=False)

    cashier_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))

    subtotal = Column(DECIMAL(10, 2), nullable=False)
    discount = Column(DECIMAL(10, 2), default=0)
    tax = Column(DECIMAL(10, 2), default=0)
    total = Column(DECIMAL(10, 2), nullable=False)

    payment_method = Column(String(50))
    payment_status = Column(String(50), default="completed")

    notes = Column(Text)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="sales")
    cashier = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    discount = Column(DECIMAL(10, 2), default=0)
    total = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

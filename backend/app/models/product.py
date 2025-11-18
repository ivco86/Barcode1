from sqlalchemy import Column, String, Text, Integer, Boolean, TIMESTAMP, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    barcode = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    cost = Column(DECIMAL(10, 2))
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, default=5)

    category = Column(String(100))
    image_url = Column(Text)

    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")

from sqlalchemy import Column, String, Integer, TIMESTAMP, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))

    loyalty_points = Column(Integer, default=0)
    total_spent = Column(DECIMAL(10, 2), default=0)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="customers")
    sales = relationship("Sale", back_populates="customer")

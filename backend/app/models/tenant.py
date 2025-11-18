from sqlalchemy import Column, String, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))

    # Subscription
    plan = Column(String(50), nullable=False, default="free")
    status = Column(String(50), nullable=False, default="active")
    trial_ends_at = Column(TIMESTAMP)
    subscription_ends_at = Column(TIMESTAMP)

    # Billing
    stripe_customer_id = Column(String(255))

    # Settings
    settings = Column(JSON, default={})

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="tenant", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="tenant", cascade="all, delete-orphan")

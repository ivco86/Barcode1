from sqlalchemy import Column, String, Boolean, Integer, TIMESTAMP, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)

    price_monthly = Column(DECIMAL(10, 2), nullable=False)
    price_yearly = Column(DECIMAL(10, 2), nullable=False)

    # Limits
    max_products = Column(Integer)
    max_users = Column(Integer)
    max_locations = Column(Integer)
    max_sales_per_month = Column(Integer)

    features = Column(JSON, default={})

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

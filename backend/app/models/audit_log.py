from sqlalchemy import Column, String, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
import uuid
from datetime import datetime
from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    action = Column(String(100), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(UUID(as_uuid=True))

    old_data = Column(JSON)
    new_data = Column(JSON)

    ip_address = Column(INET)
    user_agent = Column(Text)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)

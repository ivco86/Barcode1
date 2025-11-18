"""
Seed data script - creates demo tenant and admin user if they don't exist
"""
import sys
sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.tenant import Tenant
from app.models.user import User
from app.core.security import hash_password
from app.core.config import settings
import uuid

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_demo_data():
    """Create demo tenant and admin user if they don't exist"""
    db = SessionLocal()

    try:
        # Check if demo tenant already exists
        demo_tenant = db.query(Tenant).filter(Tenant.slug == 'demo').first()

        if not demo_tenant:
            print("Creating demo tenant...")
            demo_tenant = Tenant(
                id=uuid.UUID('00000000-0000-0000-0000-000000000001'),
                name='Demo Store',
                slug='demo',
                email='admin@demo.local',
                plan='pro',
                status='active'
            )
            db.add(demo_tenant)
            db.commit()
            print("✓ Demo tenant created")
        else:
            print("✓ Demo tenant already exists")

        # Check if admin user exists
        admin_user = db.query(User).filter(
            User.tenant_id == demo_tenant.id,
            User.username == 'admin'
        ).first()

        if not admin_user:
            print("Creating admin user...")
            # Generate bcrypt hash for 'admin123'
            password_hash = hash_password('admin123')

            admin_user = User(
                tenant_id=demo_tenant.id,
                username='admin',
                email='admin@demo.local',
                password_hash=password_hash,
                role='owner'
            )
            db.add(admin_user)
            db.commit()
            print("✓ Admin user created")
            print(f"  Username: admin")
            print(f"  Password: admin123")
        else:
            print("✓ Admin user already exists")

    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Seeding demo data ===")
    seed_demo_data()
    print("=== Done ===")

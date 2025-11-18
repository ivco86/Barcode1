# Архитектура на SaaS POS System

## Общ преглед

SaaS POS система с multi-tenant архитектура, която позволява на множество магазини (tenants) да използват едно приложение с пълна изолация на данните.

## Multi-Tenant Architecture

### Концепция

```
┌─────────────────────────────────────────────────┐
│   🌐 Cloud Frontend (React)                     │
│   https://mypos.app                             │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │  🔐 Auth Layer  │
        │  (JWT tokens)   │
        └────────┬────────┘
                 │
┌────────────────▼────────────────────────────────┐
│   🚀 API Gateway / Backend (FastAPI)            │
│   - Multi-tenant routing                        │
│   - Subscription management                     │
│   - Business logic                              │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐  ┌──────────────┐
│  PostgreSQL   │  │    Redis     │
│  (Main DB)    │  │   (Cache)    │
└───────────────┘  └──────────────┘
```

### Tenant Isolation

**Ключ**: ВСИЧКИ таблици имат `tenant_id` колона!

```sql
-- ❌ ГРЕШНО (няма tenant_id)
SELECT * FROM products WHERE barcode = '1001';

-- ✅ ПРАВИЛНО (винаги с tenant_id)
SELECT * FROM products
WHERE tenant_id = 'xxx' AND barcode = '1001';
```

### JWT Token Structure

```json
{
  "tenant_id": "00000000-0000-0000-0000-000000000001",
  "user_id": "11111111-1111-1111-1111-111111111111",
  "username": "admin",
  "role": "owner",
  "exp": 1234567890
}
```

## Database Schema

### Core Tables

#### tenants
Магазините - твоите клиенти

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255),          -- "Магазин Иванов"
    slug VARCHAR(100) UNIQUE,   -- "magazin-ivanov"
    email VARCHAR(255) UNIQUE,
    plan VARCHAR(50),           -- free, basic, pro
    status VARCHAR(50),         -- trial, active, suspended
    settings JSONB,
    created_at TIMESTAMP
);
```

#### users
Служителите на всеки магазин

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    username VARCHAR(100),
    email VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(50),  -- owner, admin, manager, cashier
    is_active BOOLEAN,
    UNIQUE(tenant_id, username)  -- Username уникален ПО TENANT
);
```

#### products
Продуктите на ВСЕКИ магазин отделно

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    barcode VARCHAR(100),
    name VARCHAR(255),
    price DECIMAL(10, 2),
    stock INTEGER,
    category VARCHAR(100),
    UNIQUE(tenant_id, barcode)  -- Barcode уникален ПО TENANT
);
```

#### sales
Продажбите

```sql
CREATE TABLE sales (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    sale_number VARCHAR(50),  -- 20231201-0001
    cashier_id UUID REFERENCES users(id),
    total DECIMAL(10, 2),
    payment_method VARCHAR(50),
    created_at TIMESTAMP,
    UNIQUE(tenant_id, sale_number)
);
```

### Indexes за Performance

```sql
-- КРИТИЧНИ indexes
CREATE INDEX idx_products_tenant ON products(tenant_id);
CREATE INDEX idx_products_barcode ON products(tenant_id, barcode);
CREATE INDEX idx_sales_tenant ON sales(tenant_id);
CREATE INDEX idx_sales_created ON sales(tenant_id, created_at DESC);
```

## API Layer

### Authentication Flow

```
1. User Login
   POST /api/auth/login
   { username, password }

2. Verify Credentials
   - Find user by username
   - Check password hash
   - Verify user.tenant_id exists

3. Generate JWT
   {
     tenant_id: user.tenant_id,
     user_id: user.id,
     role: user.role
   }

4. Return Token
   { access_token, tenant, user }
```

### Multi-Tenant Middleware

```python
def get_current_user(token: str):
    payload = decode_jwt(token)

    # ВАЖНО: Извличаме tenant_id от token
    tenant_id = payload["tenant_id"]
    user_id = payload["user_id"]

    # Verify user exists
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id  # Double check
    ).first()

    return {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "role": payload["role"]
    }
```

### API Endpoints with Tenant Isolation

```python
@router.get("/products")
def get_products(current_user: dict = Depends(get_current_user)):
    # ВИНАГИ филтрирай по tenant_id!
    products = db.query(Product).filter(
        Product.tenant_id == current_user["tenant_id"]
    ).all()

    return products

@router.post("/sales")
def create_sale(
    sale: SaleCreate,
    current_user: dict = Depends(get_current_user)
):
    # ВИНАГИ задавай tenant_id!
    db_sale = Sale(
        tenant_id=current_user["tenant_id"],
        cashier_id=current_user["user_id"],
        ...
    )
    db.add(db_sale)
    db.commit()

    return db_sale
```

## Security

### 1. Authentication
- JWT tokens с short expiration (24h)
- Password hashing с bcrypt (cost factor: 12)
- Secure token storage (localStorage)

### 2. Authorization
- Role-based access control (RBAC)
- Owner > Admin > Manager > Cashier
- Endpoint-level permissions

```python
def require_role(allowed_roles: list):
    def checker(current_user: dict):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return checker

@router.delete("/products/{id}")
def delete_product(
    current_user: dict = Depends(require_role(["owner", "admin"]))
):
    ...
```

### 3. Data Isolation
- Tenant ID във всеки query
- Database-level constraints
- No cross-tenant access

### 4. Input Validation
- Pydantic schemas
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (React auto-escapes)

## Feature Toggles

За локално vs cloud:

```python
class Settings:
    STRIPE_ENABLED: bool = False          # Local: False
    EMAIL_ENABLED: bool = False           # Local: False
    SUBSCRIPTION_CHECKS_ENABLED: bool = False  # Local: False

# Usage
if settings.SUBSCRIPTION_CHECKS_ENABLED:
    check_subscription(tenant_id)
else:
    # Skip check локално
    pass
```

## Subscription Model (Бъдещо)

### Plans

```
Free:
  - 50 products
  - 1 user
  - 100 sales/month
  - 0 лв/месец

Basic:
  - 500 products
  - 3 users
  - Unlimited sales
  - 29.99 лв/месец

Pro:
  - Unlimited products
  - 10 users
  - Multi-location
  - API access
  - 79.99 лв/месец
```

### Subscription Checks

```python
def check_plan_limits(tenant: Tenant, feature: str):
    plan = get_plan(tenant.plan_id)

    if feature == "products":
        count = count_products(tenant.id)
        if plan.max_products and count >= plan.max_products:
            raise HTTPException(403, "Product limit reached")

    elif feature == "sales_monthly":
        count = count_sales_this_month(tenant.id)
        if plan.max_sales_per_month and count >= plan.max_sales_per_month:
            raise HTTPException(403, "Monthly sales limit reached")
```

## Deployment Architecture

### Phase 0: Local (Текуща)
```
Docker Compose:
  - PostgreSQL
  - Redis
  - Backend (FastAPI)
  - Frontend (React Dev Server)
```

### Phase 1: Cloud (Бъдеща)
```
                    ┌──────────────┐
                    │  CloudFlare  │
                    │     CDN      │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │     Nginx    │
                    │ Load Balancer│
                    └──────┬───────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼────────┐                 ┌──────────▼─────────┐
│  Frontend      │                 │  Backend API       │
│  (Static)      │                 │  (Docker Swarm)    │
│  Nginx         │                 │  3x replicas       │
└────────────────┘                 └──────────┬─────────┘
                                              │
                                   ┌──────────┴─────────┐
                                   │                    │
                           ┌───────▼──────┐    ┌────────▼────────┐
                           │  PostgreSQL  │    │     Redis       │
                           │  (Managed)   │    │   (Managed)     │
                           └──────────────┘    └─────────────────┘
```

## Performance Optimizations

### 1. Database
- Composite indexes на (tenant_id, часто_използвани_колони)
- Connection pooling
- Read replicas за reports

### 2. Caching (Redis)
- User sessions
- Product catalog
- Dashboard statistics
- Cache invalidation on updates

### 3. API
- Pagination (limit, offset)
- Field selection
- Gzip compression
- Rate limiting

### 4. Frontend
- Code splitting
- Lazy loading
- Service worker (PWA)
- Asset optimization

## Monitoring & Logging

### Metrics to Track
- Response times по endpoint
- Error rates
- Active tenants
- Sales volume
- Database query performance

### Logging Strategy
```python
# Audit log за важни операции
log_audit(
    tenant_id=tenant_id,
    user_id=user_id,
    action="delete_product",
    entity_type="product",
    entity_id=product_id,
    old_data=old_data,
    new_data=None
)
```

## Scaling Strategy

### Vertical (Phase 0-1)
- Увеличи server resources
- Optimize queries

### Horizontal (Phase 2+)
- Load balancing
- Database sharding по tenant_id
- Microservices:
  - Auth service
  - POS service
  - Analytics service
  - Billing service

## Backup & Recovery

### Database Backups
- Daily full backups
- Point-in-time recovery (PITR)
- Multi-region replication

### Disaster Recovery
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 5 minutes
- Automated failover

## Compliance & Privacy

### GDPR
- Right to be forgotten
- Data export
- Consent management

### PCI DSS (ако приемаме карти)
- Encrypted card data
- Secure payment gateway (Stripe)
- Regular security audits

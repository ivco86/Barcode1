-- PostgreSQL Multi-tenant POS System Schema
-- Фаза 0: Локална версия

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- === CORE TABLES ===

-- Tenants (Магазините - твоите клиенти)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),

    -- Subscription (за бъдещо)
    plan VARCHAR(50) NOT NULL DEFAULT 'free',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    trial_ends_at TIMESTAMP,
    subscription_ends_at TIMESTAMP,

    -- Billing (за бъдещо)
    stripe_customer_id VARCHAR(255),

    -- Settings
    settings JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users (Служителите на магазина)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    role VARCHAR(50) NOT NULL,
    permissions JSONB DEFAULT '{}',

    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(tenant_id, username),
    UNIQUE(tenant_id, email)
);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    barcode VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER DEFAULT 5,

    category VARCHAR(100),
    image_url TEXT,

    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(tenant_id, barcode)
);

-- Customers
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),

    loyalty_points INTEGER DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(tenant_id, phone)
);

-- Sales
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    sale_number VARCHAR(50) NOT NULL,

    cashier_id UUID REFERENCES users(id),
    customer_id UUID REFERENCES customers(id),

    subtotal DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0,
    tax DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL,

    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'completed',

    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(tenant_id, sale_number)
);

-- Sale Items
CREATE TABLE sale_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),

    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL
);

-- === SUBSCRIPTION & BILLING (за бъдещо) ===

-- Subscription Plans
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,

    price_monthly DECIMAL(10, 2) NOT NULL,
    price_yearly DECIMAL(10, 2) NOT NULL,

    -- Limits
    max_products INTEGER,
    max_users INTEGER,
    max_locations INTEGER,
    max_sales_per_month INTEGER,

    features JSONB DEFAULT '{}',

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- === AUDIT LOGS ===

-- Audit Logs (кой какво е правил)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),

    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,

    old_data JSONB,
    new_data JSONB,

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- === INDEXES ===

CREATE INDEX idx_products_tenant ON products(tenant_id);
CREATE INDEX idx_products_barcode ON products(tenant_id, barcode);
CREATE INDEX idx_sales_tenant ON sales(tenant_id);
CREATE INDEX idx_sales_created ON sales(tenant_id, created_at DESC);
CREATE INDEX idx_sale_items_sale ON sale_items(sale_id);
CREATE INDEX idx_customers_tenant ON customers(tenant_id);
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id, created_at DESC);

-- === SEED DATA (Demo Tenant) ===

-- Insert demo tenant
INSERT INTO tenants (id, name, slug, email, plan, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Demo Store',
    'demo',
    'admin@demo.local',
    'pro',
    'active'
);

-- Admin user will be created by seed_data.py script with proper bcrypt hash

-- Insert sample products
INSERT INTO products (tenant_id, barcode, name, price, cost, stock, category) VALUES
('00000000-0000-0000-0000-000000000001', '1001', 'Хляб бял', 1.50, 0.80, 50, 'Хранителни стоки'),
('00000000-0000-0000-0000-000000000001', '1002', 'Мляко 1л', 2.80, 2.00, 30, 'Млечни продукти'),
('00000000-0000-0000-0000-000000000001', '1003', 'Кафе Nescafe 200г', 12.50, 9.00, 20, 'Напитки'),
('00000000-0000-0000-0000-000000000001', '1004', 'Вода 1.5л', 0.80, 0.50, 100, 'Напитки'),
('00000000-0000-0000-0000-000000000001', '1005', 'Сирене вакуум 400г', 8.90, 6.50, 15, 'Млечни продукти'),
('00000000-0000-0000-0000-000000000001', '1006', 'Яйца 10бр', 4.50, 3.20, 40, 'Хранителни стоки'),
('00000000-0000-0000-0000-000000000001', '1007', 'Шоколад Milka 100г', 3.20, 2.10, 60, 'Сладкиши'),
('00000000-0000-0000-0000-000000000001', '1008', 'Чипс Lays 150г', 2.90, 1.80, 45, 'Закуски'),
('00000000-0000-0000-0000-000000000001', '1009', 'Сок Prigat 1л', 3.50, 2.40, 25, 'Напитки'),
('00000000-0000-0000-0000-000000000001', '1010', 'Йогурт Данон 400г', 2.30, 1.60, 35, 'Млечни продукти');

-- Insert sample customers
INSERT INTO customers (tenant_id, name, phone, loyalty_points) VALUES
('00000000-0000-0000-0000-000000000001', 'Иван Петров', '+359888111111', 150),
('00000000-0000-0000-0000-000000000001', 'Мария Георгиева', '+359888222222', 320),
('00000000-0000-0000-0000-000000000001', 'Петър Димитров', '+359888333333', 85);

-- Insert subscription plans (за бъдещо)
INSERT INTO plans (name, slug, price_monthly, price_yearly, max_products, max_users, max_locations, features) VALUES
('Free', 'free', 0, 0, 50, 1, 1, '{"basic_pos": true, "inventory": true}'),
('Basic', 'basic', 29.99, 299.99, 500, 3, 1, '{"basic_pos": true, "inventory": true, "customers": true, "reports": true}'),
('Pro', 'pro', 79.99, 799.99, NULL, 10, 5, '{"basic_pos": true, "inventory": true, "customers": true, "reports": true, "multi_location": true, "api_access": true}');

-- Migration 001: Initial Schema
-- Creates all base tables for Add'as Platform multi-tenant architecture
-- Author: Add'as Team
-- Date: 2025-11-10

-- ============================================================================
-- 1. CREATE ENUMS
-- ============================================================================

CREATE TYPE plan_type AS ENUM ('free', 'basic', 'pro', 'enterprise');
CREATE TYPE user_role AS ENUM ('admin', 'supplier', 'retailer', 'viewer', 'platform_admin');
CREATE TYPE data_type AS ENUM ('html', 'xml', 'csv', 'json', 'api', 'google_sheets');
CREATE TYPE unit_type AS ENUM ('kg', 'g', 'l', 'ml', 'un');

-- ============================================================================
-- 2. CREATE TABLES
-- ============================================================================

-- Organizations (Tenants)
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan plan_type DEFAULT 'free' NOT NULL,
    active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_active ON organizations(active);

COMMENT ON TABLE organizations IS 'Multi-tenant organizations (tenants)';
COMMENT ON COLUMN organizations.slug IS 'URL-friendly unique identifier';
COMMENT ON COLUMN organizations.plan IS 'Subscription plan type';

-- Suppliers
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    supplier_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    data_type data_type NOT NULL,
    url VARCHAR(500),
    consent_obtained BOOLEAN DEFAULT false NOT NULL,
    consent_date DATE,
    extraction_config JSONB,
    active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP,
    CONSTRAINT unique_org_supplier UNIQUE(org_id, supplier_id)
);

CREATE INDEX idx_suppliers_org_id ON suppliers(org_id);
CREATE INDEX idx_suppliers_org_supplier ON suppliers(org_id, supplier_id);
CREATE INDEX idx_suppliers_active ON suppliers(org_id, active) WHERE deleted_at IS NULL;

COMMENT ON TABLE suppliers IS 'Product suppliers with multi-tenant support';
COMMENT ON COLUMN suppliers.supplier_id IS 'Unique identifier within organization (e.g., gramore, elmar)';
COMMENT ON COLUMN suppliers.extraction_config IS 'JSON configuration for ETL extraction';
COMMENT ON COLUMN suppliers.deleted_at IS 'Soft delete timestamp';

-- Products Unified
CREATE TABLE products_unified (
    id VARCHAR(16) PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    supplier_product_id VARCHAR(100),
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(100),
    weight NUMERIC(10, 2),
    unit unit_type,
    price_base NUMERIC(10, 2),
    price_margin NUMERIC(5, 2),
    price_shipping NUMERIC(10, 2),
    price_final NUMERIC(10, 2),
    stock_available BOOLEAN DEFAULT true NOT NULL,
    stock_quantity INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_products_org_id_name ON products_unified(org_id, name);
CREATE INDEX idx_products_org_id_category ON products_unified(org_id, category);
CREATE INDEX idx_products_org_id_supplier ON products_unified(org_id, supplier_id);
CREATE INDEX idx_products_org_id_active ON products_unified(org_id, deleted_at);
CREATE INDEX idx_products_stock ON products_unified(org_id, stock_available) WHERE deleted_at IS NULL;

COMMENT ON TABLE products_unified IS 'Unified product catalog with multi-tenant support';
COMMENT ON COLUMN products_unified.id IS 'Hash-based unique identifier';
COMMENT ON COLUMN products_unified.metadata IS 'JSON metadata: extraction_date, source_url, hash, etc';
COMMENT ON COLUMN products_unified.deleted_at IS 'Soft delete timestamp';

-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'viewer' NOT NULL,
    active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_org_id ON users(org_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(org_id, active) WHERE deleted_at IS NULL;

COMMENT ON TABLE users IS 'System users with role-based access control';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.deleted_at IS 'Soft delete timestamp';

-- Audit Logs
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operation VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    data_hash VARCHAR(64),
    status VARCHAR(20),
    metadata JSONB
);

CREATE INDEX idx_audit_logs_org_id ON audit_logs(org_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_operation ON audit_logs(org_id, operation);

COMMENT ON TABLE audit_logs IS 'Immutable audit trail for compliance';
COMMENT ON COLUMN audit_logs.data_hash IS 'SHA-256 hash for data integrity';
COMMENT ON COLUMN audit_logs.metadata IS 'Additional operation metadata';

-- Schema Migrations
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

COMMENT ON TABLE schema_migrations IS 'Tracks applied database migrations';

-- ============================================================================
-- 3. CREATE TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at
    BEFORE UPDATE ON suppliers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products_unified
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 4. RECORD MIGRATION
-- ============================================================================

INSERT INTO schema_migrations (version, description) 
VALUES (1, 'Initial schema with multi-tenant tables, enums, indexes, and triggers');

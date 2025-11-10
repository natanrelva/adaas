-- Migration 002: Row-Level Security Policies
-- Implements RLS for multi-tenant data isolation
-- Author: Add'as Team
-- Date: 2025-11-10

-- ============================================================================
-- 1. ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products_unified ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Note: organizations table does NOT have RLS as it's managed by platform admins

-- ============================================================================
-- 2. CREATE RLS POLICIES FOR SUPPLIERS
-- ============================================================================

-- SELECT policy: Users can only see suppliers from their organization
CREATE POLICY suppliers_isolation_policy ON suppliers
    FOR SELECT
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- INSERT policy: Users can only insert suppliers for their organization
CREATE POLICY suppliers_insert_policy ON suppliers
    FOR INSERT
    WITH CHECK (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
    );

-- UPDATE policy: Users can only update suppliers from their organization
CREATE POLICY suppliers_update_policy ON suppliers
    FOR UPDATE
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- DELETE policy: Users can only delete suppliers from their organization
CREATE POLICY suppliers_delete_policy ON suppliers
    FOR DELETE
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- ============================================================================
-- 3. CREATE RLS POLICIES FOR PRODUCTS
-- ============================================================================

-- SELECT policy: Users can only see products from their organization
CREATE POLICY products_isolation_policy ON products_unified
    FOR SELECT
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- INSERT policy: Users can only insert products for their organization
CREATE POLICY products_insert_policy ON products_unified
    FOR INSERT
    WITH CHECK (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
    );

-- UPDATE policy: Users can only update products from their organization
CREATE POLICY products_update_policy ON products_unified
    FOR UPDATE
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- DELETE policy: Users can only delete products from their organization
CREATE POLICY products_delete_policy ON products_unified
    FOR DELETE
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- ============================================================================
-- 4. CREATE RLS POLICIES FOR USERS
-- ============================================================================

-- SELECT policy: Users can only see users from their organization
CREATE POLICY users_isolation_policy ON users
    FOR SELECT
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- INSERT policy: Users can only insert users for their organization
CREATE POLICY users_insert_policy ON users
    FOR INSERT
    WITH CHECK (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
    );

-- UPDATE policy: Users can only update users from their organization
CREATE POLICY users_update_policy ON users
    FOR UPDATE
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- DELETE policy: Users can only delete users from their organization
CREATE POLICY users_delete_policy ON users
    FOR DELETE
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- ============================================================================
-- 5. CREATE RLS POLICIES FOR AUDIT LOGS
-- ============================================================================

-- SELECT policy: Users can only see audit logs from their organization
CREATE POLICY audit_logs_isolation_policy ON audit_logs
    FOR SELECT
    USING (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
        OR current_setting('app.user_role', true) = 'platform_admin'
    );

-- INSERT policy: Audit logs can only be inserted for current organization
CREATE POLICY audit_logs_insert_policy ON audit_logs
    FOR INSERT
    WITH CHECK (
        org_id = NULLIF(current_setting('app.current_org_id', true), '')::int
    );

-- Note: No UPDATE or DELETE policies for audit_logs (immutable)

-- ============================================================================
-- 6. HELPER FUNCTIONS
-- ============================================================================

-- Function to get current organization ID from session
CREATE OR REPLACE FUNCTION get_current_org_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_org_id', true), '')::int;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_current_org_id() IS 'Returns current organization ID from session context';

-- Function to check if current user is platform admin
CREATE OR REPLACE FUNCTION is_platform_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_setting('app.user_role', true) = 'platform_admin';
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION is_platform_admin() IS 'Checks if current user has platform admin role';

-- ============================================================================
-- 7. RECORD MIGRATION
-- ============================================================================

INSERT INTO schema_migrations (version, description) 
VALUES (2, 'Row-Level Security policies for multi-tenant data isolation');

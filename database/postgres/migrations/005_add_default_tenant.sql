-- Create default tenant if it doesn't exist
INSERT INTO tenants (name, domain)
SELECT 'Default Organization', 'default.org'
WHERE NOT EXISTS (
    SELECT 1 FROM tenants WHERE id = 1
);

-- Update any users without a tenant_id to use the default tenant
UPDATE users 
SET tenant_id = 1
WHERE tenant_id IS NULL;
-- Add new permissions if they don't exist
INSERT INTO permissions (name, description)
SELECT 'VIEW_CHAT', 'Can access chat assistant'
WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = 'VIEW_CHAT');

INSERT INTO permissions (name, description)
SELECT 'USE_AVATAR', 'Can use avatar features'
WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = 'USE_AVATAR');

-- Grant new permissions to roles
-- ADMIN gets all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p
WHERE r.name = 'ADMIN' 
AND p.name IN ('VIEW_CHAT', 'USE_AVATAR')
AND NOT EXISTS (
    SELECT 1 FROM role_permissions 
    WHERE role_id = r.id AND permission_id = p.id
);

-- USER gets basic permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p
WHERE r.name = 'USER' 
AND p.name IN ('VIEW_CHAT', 'USE_AVATAR')
AND NOT EXISTS (
    SELECT 1 FROM role_permissions 
    WHERE role_id = r.id AND permission_id = p.id
);

-- ANALYST gets analysis-related permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p
WHERE r.name = 'ANALYST' 
AND p.name IN ('VIEW_CHAT', 'USE_AVATAR')
AND NOT EXISTS (
    SELECT 1 FROM role_permissions 
    WHERE role_id = r.id AND permission_id = p.id
);
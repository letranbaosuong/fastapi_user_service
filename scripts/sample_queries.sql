-- Sample SQL Queries for pgAdmin4
-- Copy & paste vào Query Tool trong pgAdmin4

-- ============================================================
-- BASIC QUERIES - Xem dữ liệu cơ bản
-- ============================================================

-- 1. Count all rows trong mỗi table
SELECT
    'users' as table_name,
    COUNT(*) as row_count
FROM users
UNION ALL
SELECT
    'projects',
    COUNT(*)
FROM projects
UNION ALL
SELECT
    'user_activities',
    COUNT(*)
FROM user_activities
UNION ALL
SELECT
    'user_projects',
    COUNT(*)
FROM user_projects
ORDER BY row_count DESC;


-- 2. Top 10 users gần đây nhất
SELECT
    id,
    email,
    full_name,
    country,
    is_active,
    created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;


-- 3. Top 10 projects gần đây nhất
SELECT
    id,
    name,
    status,
    is_active,
    created_at
FROM projects
ORDER BY created_at DESC
LIMIT 10;


-- ============================================================
-- STATISTICS QUERIES - Thống kê
-- ============================================================

-- 4. Users by country
SELECT
    country,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users WHERE country IS NOT NULL), 2) as percentage
FROM users
WHERE country IS NOT NULL
GROUP BY country
ORDER BY user_count DESC;


-- 5. Projects by status
SELECT
    status,
    COUNT(*) as project_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM projects), 2) as percentage
FROM projects
GROUP BY status
ORDER BY project_count DESC;


-- 6. User activities by action type
SELECT
    action_type,
    COUNT(*) as activity_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM user_activities), 2) as percentage
FROM user_activities
GROUP BY action_type
ORDER BY activity_count DESC;


-- 7. Active vs Inactive users
SELECT
    is_active,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users), 2) as percentage
FROM users
GROUP BY is_active
ORDER BY is_active DESC;


-- 8. Superusers vs Regular users
SELECT
    is_superuser,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users), 2) as percentage
FROM users
GROUP BY is_superuser
ORDER BY is_superuser DESC;


-- ============================================================
-- ADVANCED QUERIES - Queries phức tạp
-- ============================================================

-- 9. Top 10 most active users (nhiều activities nhất)
SELECT
    u.id,
    u.email,
    u.full_name,
    u.country,
    COUNT(ua.id) as activity_count
FROM users u
LEFT JOIN user_activities ua ON u.id = ua.user_id
GROUP BY u.id, u.email, u.full_name, u.country
ORDER BY activity_count DESC
LIMIT 10;


-- 10. Top 10 projects với nhiều members nhất
SELECT
    p.id,
    p.name,
    p.status,
    COUNT(up.user_id) as member_count
FROM projects p
LEFT JOIN user_projects up ON p.id = up.project_id
GROUP BY p.id, p.name, p.status
ORDER BY member_count DESC
LIMIT 10;


-- 11. Users và số lượng projects họ tham gia
SELECT
    u.id,
    u.email,
    u.full_name,
    COUNT(up.project_id) as project_count
FROM users u
LEFT JOIN user_projects up ON u.id = up.user_id
GROUP BY u.id, u.email, u.full_name
HAVING COUNT(up.project_id) > 0
ORDER BY project_count DESC
LIMIT 20;


-- 12. Projects với member details
SELECT
    p.id as project_id,
    p.name as project_name,
    p.status,
    u.id as user_id,
    u.email,
    u.full_name,
    up.role,
    up.joined_at
FROM projects p
JOIN user_projects up ON p.id = up.project_id
JOIN users u ON up.user_id = u.id
WHERE p.id = 1  -- Thay đổi project_id
ORDER BY up.joined_at DESC;


-- 13. Recent activities (24 giờ gần đây)
SELECT
    ua.id,
    ua.action_type,
    ua.description,
    ua.created_at,
    u.email,
    u.full_name
FROM user_activities ua
JOIN users u ON ua.user_id = u.id
WHERE ua.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY ua.created_at DESC
LIMIT 50;


-- 14. Activity timeline grouped by hour
SELECT
    action_type,
    COUNT(*) as count,
    DATE_TRUNC('hour', created_at) as hour
FROM user_activities
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY action_type, hour
ORDER BY hour DESC, count DESC;


-- 15. Users without any projects
SELECT
    u.id,
    u.email,
    u.full_name,
    u.created_at
FROM users u
LEFT JOIN user_projects up ON u.id = up.user_id
WHERE up.user_id IS NULL
LIMIT 20;


-- 16. Projects without any members
SELECT
    p.id,
    p.name,
    p.status,
    p.created_at
FROM projects p
LEFT JOIN user_projects up ON p.id = up.project_id
WHERE up.project_id IS NULL
LIMIT 20;


-- 17. User role distribution in projects
SELECT
    role,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM user_projects), 2) as percentage
FROM user_projects
GROUP BY role
ORDER BY count DESC;


-- 18. Most used IP addresses (security check)
SELECT
    ip_address,
    COUNT(*) as usage_count,
    COUNT(DISTINCT user_id) as unique_users
FROM user_activities
WHERE ip_address IS NOT NULL
GROUP BY ip_address
ORDER BY usage_count DESC
LIMIT 20;


-- 19. User growth over time (monthly)
SELECT
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as new_users
FROM users
GROUP BY month
ORDER BY month DESC
LIMIT 12;


-- 20. Project status transitions timeline
SELECT
    DATE_TRUNC('month', created_at) as month,
    status,
    COUNT(*) as project_count
FROM projects
GROUP BY month, status
ORDER BY month DESC, project_count DESC;


-- ============================================================
-- PERFORMANCE QUERIES - Test database performance
-- ============================================================

-- 21. Full table scan test (slow)
EXPLAIN ANALYZE
SELECT * FROM users;


-- 22. Index usage test (fast)
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';


-- 23. Join performance test
EXPLAIN ANALYZE
SELECT
    u.email,
    COUNT(ua.id) as activity_count
FROM users u
LEFT JOIN user_activities ua ON u.id = ua.user_id
GROUP BY u.id, u.email
LIMIT 100;


-- 24. Complex join with filtering
EXPLAIN ANALYZE
SELECT
    p.name,
    u.email,
    up.role
FROM projects p
JOIN user_projects up ON p.id = up.project_id
JOIN users u ON up.user_id = u.id
WHERE p.status = 'in_progress'
  AND u.is_active = true
LIMIT 100;


-- ============================================================
-- DATA VALIDATION QUERIES - Check data integrity
-- ============================================================

-- 25. Check for orphaned activities (activities without users)
SELECT COUNT(*) as orphaned_activities
FROM user_activities ua
LEFT JOIN users u ON ua.user_id = u.id
WHERE u.id IS NULL;


-- 26. Check for orphaned memberships
SELECT COUNT(*) as orphaned_memberships
FROM user_projects up
LEFT JOIN users u ON up.user_id = u.id
LEFT JOIN projects p ON up.project_id = p.id
WHERE u.id IS NULL OR p.id IS NULL;


-- 27. Check for duplicate emails (should be 0)
SELECT
    email,
    COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;


-- 28. Check data ranges
SELECT
    MIN(created_at) as earliest_user,
    MAX(created_at) as latest_user,
    NOW() as current_time,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) / 86400 as days_span
FROM users;


-- ============================================================
-- CLEANUP QUERIES - Xóa data (USE WITH CAUTION!)
-- ============================================================

-- 29. Delete all user activities (⚠️ CAREFUL!)
-- TRUNCATE TABLE user_activities CASCADE;


-- 30. Delete all projects (⚠️ CAREFUL!)
-- TRUNCATE TABLE user_projects CASCADE;
-- TRUNCATE TABLE projects CASCADE;


-- 31. Delete all users (⚠️ CAREFUL!)
-- TRUNCATE TABLE user_activities CASCADE;
-- TRUNCATE TABLE user_projects CASCADE;
-- TRUNCATE TABLE users CASCADE;


-- 32. Delete everything (⚠️ VERY CAREFUL!)
-- TRUNCATE TABLE user_activities CASCADE;
-- TRUNCATE TABLE user_projects CASCADE;
-- TRUNCATE TABLE projects CASCADE;
-- TRUNCATE TABLE users CASCADE;


-- ============================================================
-- NOTES:
-- - Uncomment cleanup queries to use (remove --)
-- - Always backup data trước khi xóa
-- - Use EXPLAIN ANALYZE để check query performance
-- - Create indexes nếu query chậm
-- ============================================================

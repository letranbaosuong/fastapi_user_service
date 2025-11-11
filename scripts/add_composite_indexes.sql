-- ==============================================================================
-- COMPOSITE INDEXES FOR PERFORMANCE OPTIMIZATION
-- ==============================================================================
-- Created: 2025-11-11
-- Purpose: Tối ưu tốc độ truy vấn với composite indexes
-- How to run: psql -U postgres -d user_service_db -f scripts/add_composite_indexes.sql
-- ==============================================================================

-- Start transaction
BEGIN;

-- ==============================================================================
-- 1. USERS TABLE INDEXES
-- ==============================================================================

-- 1.1. Tìm active users theo country
-- Query: SELECT * FROM users WHERE country = 'VN' AND is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_country_active
ON users (country, is_active);

-- 1.2. Lọc users mới theo country
-- Query: SELECT * FROM users WHERE country = 'US' ORDER BY created_at DESC;
CREATE INDEX IF NOT EXISTS idx_users_country_created
ON users (country, created_at DESC);

-- 1.3. Admin dashboard: active users + role
-- Query: SELECT * FROM users WHERE is_active = true AND is_superuser = true;
CREATE INDEX IF NOT EXISTS idx_users_active_superuser
ON users (is_active, is_superuser);

-- 1.4. Search users gần đây (active users sorted by date)
-- Query: SELECT * FROM users WHERE is_active = true ORDER BY created_at DESC;
CREATE INDEX IF NOT EXISTS idx_users_active_created
ON users (is_active, created_at DESC);

-- ==============================================================================
-- 2. USER_ACTIVITIES TABLE INDEXES
-- ==============================================================================

-- 2.1. Xem activities của 1 user theo thời gian
-- Query: SELECT * FROM user_activities WHERE user_id = 123 ORDER BY created_at DESC;
CREATE INDEX IF NOT EXISTS idx_activities_user_created
ON user_activities (user_id, created_at DESC);

-- 2.2. Filter by action type cho 1 user
-- Query: SELECT * FROM user_activities WHERE user_id = 123 AND action_type = 'LOGIN';
CREATE INDEX IF NOT EXISTS idx_activities_user_action_created
ON user_activities (user_id, action_type, created_at DESC);

-- 2.3. Security: Track login attempts by IP
-- Query: SELECT * FROM user_activities WHERE action_type = 'LOGIN' AND ip_address = '1.2.3.4';
CREATE INDEX IF NOT EXISTS idx_activities_action_ip_created
ON user_activities (action_type, ip_address, created_at DESC);

-- 2.4. Analytics: Count actions by type and date
-- Query: SELECT action_type, COUNT(*) FROM user_activities GROUP BY action_type;
CREATE INDEX IF NOT EXISTS idx_activities_action_created
ON user_activities (action_type, created_at DESC);

-- ==============================================================================
-- 3. PROJECTS TABLE INDEXES
-- ==============================================================================

-- 3.1. Dashboard: Active projects by status
-- Query: SELECT * FROM projects WHERE is_active = true AND status = 'in_progress';
CREATE INDEX IF NOT EXISTS idx_projects_active_status
ON projects (is_active, status);

-- 3.2. Recent projects by status
-- Query: SELECT * FROM projects WHERE status = 'completed' ORDER BY created_at DESC;
CREATE INDEX IF NOT EXISTS idx_projects_status_created
ON projects (status, created_at DESC);

-- 3.3. Active + recent projects
-- Query: SELECT * FROM projects WHERE is_active = true ORDER BY created_at DESC;
CREATE INDEX IF NOT EXISTS idx_projects_active_created
ON projects (is_active, created_at DESC);

-- 3.4. Search projects by status and date range
-- Query: SELECT * FROM projects WHERE status = 'in_progress' AND start_date >= '2024-01-01';
CREATE INDEX IF NOT EXISTS idx_projects_status_start
ON projects (status, start_date);

-- ==============================================================================
-- 4. USER_PROJECTS TABLE INDEXES
-- ==============================================================================

-- 4.1. Unique membership (prevent duplicates)
-- Query: SELECT * FROM user_projects WHERE user_id = 123 AND project_id = 456;
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_projects_user_project
ON user_projects (user_id, project_id);

-- 4.2. Get members by role for a project
-- Query: SELECT * FROM user_projects WHERE project_id = 456 AND role = 'owner';
CREATE INDEX IF NOT EXISTS idx_user_projects_project_role
ON user_projects (project_id, role);

-- 4.3. User's project timeline
-- Query: SELECT * FROM user_projects WHERE user_id = 123 ORDER BY joined_at DESC;
CREATE INDEX IF NOT EXISTS idx_user_projects_user_joined
ON user_projects (user_id, joined_at DESC);

-- 4.4. Recent members of a project
-- Query: SELECT * FROM user_projects WHERE project_id = 456 ORDER BY joined_at DESC;
CREATE INDEX IF NOT EXISTS idx_user_projects_project_joined
ON user_projects (project_id, joined_at DESC);

-- ==============================================================================
-- 5. PARTIAL INDEXES (Optional - for specific use cases)
-- ==============================================================================

-- 5.1. Index only active users (smaller, faster)
CREATE INDEX IF NOT EXISTS idx_users_active_email
ON users (email) WHERE is_active = true;

-- 5.2. Index only recent activities (last 30 days)
CREATE INDEX IF NOT EXISTS idx_activities_recent
ON user_activities (user_id, created_at)
WHERE created_at >= NOW() - INTERVAL '30 days';

-- 5.3. Index only active projects
CREATE INDEX IF NOT EXISTS idx_projects_active_name
ON projects (name) WHERE is_active = true;

-- ==============================================================================
-- VERIFY INDEXES
-- ==============================================================================

-- Show all indexes created
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Show index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

COMMIT;

-- ==============================================================================
-- ROLLBACK (if needed)
-- ==============================================================================
-- To remove all indexes:
/*
BEGIN;

-- Users
DROP INDEX IF EXISTS idx_users_country_active;
DROP INDEX IF EXISTS idx_users_country_created;
DROP INDEX IF EXISTS idx_users_active_superuser;
DROP INDEX IF EXISTS idx_users_active_created;
DROP INDEX IF EXISTS idx_users_active_email;

-- User activities
DROP INDEX IF EXISTS idx_activities_user_created;
DROP INDEX IF EXISTS idx_activities_user_action_created;
DROP INDEX IF EXISTS idx_activities_action_ip_created;
DROP INDEX IF EXISTS idx_activities_action_created;
DROP INDEX IF EXISTS idx_activities_recent;

-- Projects
DROP INDEX IF EXISTS idx_projects_active_status;
DROP INDEX IF EXISTS idx_projects_status_created;
DROP INDEX IF EXISTS idx_projects_active_created;
DROP INDEX IF EXISTS idx_projects_status_start;
DROP INDEX IF EXISTS idx_projects_active_name;

-- User-projects
DROP INDEX IF EXISTS idx_user_projects_user_project;
DROP INDEX IF EXISTS idx_user_projects_project_role;
DROP INDEX IF EXISTS idx_user_projects_user_joined;
DROP INDEX IF EXISTS idx_user_projects_project_joined;

COMMIT;
*/

-- ==============================================================================
-- PERFORMANCE TESTING QUERIES
-- ==============================================================================

-- Test 1: Active users in Vietnam
EXPLAIN ANALYZE
SELECT * FROM users
WHERE country = 'VN' AND is_active = true;

-- Test 2: Recent login activities for user
EXPLAIN ANALYZE
SELECT * FROM user_activities
WHERE user_id = 1 AND action_type = 'LOGIN'
ORDER BY created_at DESC
LIMIT 10;

-- Test 3: Active projects by status
EXPLAIN ANALYZE
SELECT * FROM projects
WHERE is_active = true AND status = 'in_progress'
ORDER BY created_at DESC;

-- Test 4: Project members by role
EXPLAIN ANALYZE
SELECT u.email, u.full_name, up.role
FROM user_projects up
JOIN users u ON up.user_id = u.id
WHERE up.project_id = 1 AND up.role = 'owner';

-- ==============================================================================
-- INDEX USAGE STATISTICS
-- ==============================================================================

-- Check which indexes are actually being used
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY idx_scan DESC;

-- Find unused indexes (candidates for removal)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
  AND indexname LIKE 'idx_%'
ORDER BY pg_relation_size(indexrelid) DESC;

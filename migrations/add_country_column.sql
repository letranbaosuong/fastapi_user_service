-- Migration: Add country column to users table
-- Date: 2024-01-10
-- Description: Thêm cột country để lưu mã quốc gia (ISO 3166-1 alpha-2)

-- Add country column
ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(2);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS ix_users_country ON users(country);

-- Optional: Update existing users with default country
-- UPDATE users SET country = 'VN' WHERE country IS NULL;

-- Verify
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'country';

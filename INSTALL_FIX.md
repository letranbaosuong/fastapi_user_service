# ⚠️ FIX: "No module named 'faker'"

## Nguyên Nhân

Project dùng **virtual environment (venv)** nhưng dependencies được install vào Python global → Script không tìm thấy module.

## ✅ QUICK FIX (1 phút)

```bash
# Step 1: CD vào project root
cd /Users/letranbaosuong/Documents/personals/projects/pythons/fastapi_user_service

# Step 2: Activate venv
source venv/bin/activate

# Step 3: Install dependencies
pip install faker==22.0.0 tqdm==4.66.1

# Step 4: Verify
pip list | grep faker
pip list | grep tqdm

# Step 5: Generate data
python scripts/generate_dummy_data.py
```

## Các Cách Khác

### Cách 1: Dùng Install Script (Auto detect venv)

```bash
./scripts/install_dependencies.sh
```

Script này sẽ:
- Tự động detect venv
- Activate venv nếu có
- Install dependencies vào đúng environment

### Cách 2: One-Click Setup (Đã được fix)

```bash
./scripts/setup_and_generate.sh
```

Script đã được update:
- Auto detect và activate venv
- Install vào venv thay vì global Python
- Sử dụng đúng Python command

## Verify Installation

```bash
# Activate venv
source venv/bin/activate

# Check Python location
which python
# Expected: /path/to/project/venv/bin/python

# Check pip location
which pip
# Expected: /path/to/project/venv/bin/pip

# List installed packages
pip list | grep -E "faker|tqdm"
# Expected:
# faker     22.0.0
# tqdm      4.66.1
```

## Các Files Đã Fix

1. ✅ `scripts/setup_and_generate.sh`
   - Auto detect venv
   - Activate venv before install
   - Use correct Python command

2. ✅ `scripts/install_dependencies.sh` (MỚI)
   - Dedicated script để install dependencies
   - Auto detect venv

3. ✅ `QUICK_START.md`
   - Updated với venv instructions
   - Clear troubleshooting guide

4. ✅ `requirements.txt`
   - Đã có faker và tqdm

## Expected Output After Fix

```bash
$ source venv/bin/activate
$ pip install faker==22.0.0 tqdm==4.66.1

Collecting faker==22.0.0
  Downloading faker-22.0.0-py3-none-any.whl
Collecting tqdm==4.66.1
  Downloading tqdm-4.66.1-py3-none-any.whl
Installing collected packages: tqdm, faker
Successfully installed faker-22.0.0 tqdm-4.66.1

$ python scripts/generate_dummy_data.py

============================================================
🚀 DUMMY DATA GENERATOR
============================================================

📋 Creating database tables...
✅ Tables created successfully

⚠️  Clear existing data? (yes/no):
```

## Tóm Tắt

**Problem:** `ModuleNotFoundError: No module named 'faker'`

**Root Cause:** Dependencies installed to global Python, but project uses venv

**Solution:**
```bash
source venv/bin/activate && pip install faker==22.0.0 tqdm==4.66.1
```

**Status:** ✅ FIXED

All scripts updated to auto-detect and use venv!

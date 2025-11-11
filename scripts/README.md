# Scripts Directory

## Available Scripts

### 1. `generate_dummy_data.py`

Generate 175,000+ rows của realistic dummy data để test.

**Usage:**
```bash
# Quick start
python scripts/generate_dummy_data.py

# Or from scripts directory
cd scripts
python generate_dummy_data.py
```

**What it generates:**
- 20,000 users
- 5,000 projects
- 100,000+ user activities
- 50,000+ user-project memberships

**Requirements:**
```bash
pip install faker tqdm
```

**Time:** ~2-3 minutes

**Output:**
- Progress bars cho mỗi step
- Statistics summary
- Total rows created

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start database
docker-compose up -d

# Generate data
python scripts/generate_dummy_data.py

# View data in pgAdmin4
open http://localhost:5050
```

## Documentation

Xem `DUMMY_DATA_GUIDE.md` để biết chi tiết về:
- Cách sử dụng script
- pgAdmin4 setup
- Performance testing
- SQL queries examples
- Troubleshooting

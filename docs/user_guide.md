# User Guide & Reproducible Setup Instructions

## Requirements
- Python 3.10+
- Node.js 18+ and npm 9+

## 1. Backend Setup & Data Generation

```bash
# Navigate to project directory
cd "c:\Users\Sanjay v\Downloads\COE_project"

# Install Python dependencies
pip install -r requirements.txt

# Generate synthetic dataset (200 clients, 15 counsellors, 8 social workers, ~708 sessions)
python data/generate_synthetic_data.py

# Seed database and test backend server
python -c "import sys; sys.path.insert(0, '.'); from backend.database import SessionLocal; from backend.main import seed_database_internal; seed_database_internal(SessionLocal())"

# Start FastAPI backend server (Port 8000)
uvicorn backend.main:app --reload --port 8000
```

## 2. Frontend Launch

```bash
# Open a second terminal and navigate to frontend directory
cd "c:\Users\Sanjay v\Downloads\COE_project\frontend"

# Install npm packages
npm install

# Start Vite dev server (Port 3000)
npm run dev
```

Visit `http://localhost:3000` in your browser.

## 3. Running Evaluation Experiment & Automated Test Suite

```bash
# Run baseline vs prototype experiment evaluation script
python evaluation/experiment.py

# Run automated pytest suite (tests consent, failure cases, capacity limit, and HTTP 403 audit logging)
pytest tests/
```

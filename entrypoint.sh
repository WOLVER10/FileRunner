#!/bin/bash
set -e

# Initialize database and default settings, then start the app
python -c "
from app.database import create_tables, SessionLocal
from app.main import init_default_settings
from app.models import Setting
import json

create_tables()
init_default_settings()
print('Database initialized successfully.')
"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000

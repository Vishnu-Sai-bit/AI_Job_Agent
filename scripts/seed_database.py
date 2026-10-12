"""
==========================================================
Script - Seed Database
==========================================================
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables initialized successfully.")

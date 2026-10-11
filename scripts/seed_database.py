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
    print("Seeding initial demo user...")
    if not User.query.filter_by(email="demo@jobcopilot.ai").first():
        demo_user = User(
            id="usr_seed_demo",
            email="demo@jobcopilot.ai",
            full_name="Demo Candidate",
            role="candidate"
        )
        demo_user.set_password("demo123")
        db.session.add(demo_user)
        db.session.commit()
        print("Demo user created: demo@jobcopilot.ai / demo123")
    else:
        print("Demo user already exists.")

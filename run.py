"""
==========================================================
AI Job Copilot & Career Intelligence Platform
Local Development Server Entrypoint
==========================================================
"""

import sys
from pathlib import Path

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI Job Copilot & Career Intelligence Platform")
    print("Local Server: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False)

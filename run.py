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
    import os
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("\n" + "="*60)
    print("AI Job Copilot & Career Intelligence Platform")
    print(f"Server running on: http://{host}:{port}")
    print("="*60 + "\n")
    app.run(host=host, port=port, debug=False)

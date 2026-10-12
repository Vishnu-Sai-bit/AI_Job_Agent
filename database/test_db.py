import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from database.database import get_jobs

jobs = get_jobs()

print("=" * 60)

for job in jobs[:10]:
    print(job)

print("=" * 60)
print(f"Total Jobs: {len(jobs)}")
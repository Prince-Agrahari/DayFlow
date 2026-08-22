"""Root test configuration — shared path setup."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for sub in ("backend", "analytics", "ai-engine"):
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-characters-long")

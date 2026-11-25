"""Make backend/ importable and keep tests offline."""
import os
import sys
from pathlib import Path

os.environ.setdefault("LOG_RUNS", "0")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

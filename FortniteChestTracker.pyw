"""Double-click to start Fortnite Chest Tracker (no console window). Needs Python 3.10+."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)

from app.core.launcher import launch

sys.exit(launch(sys.argv[1:]))

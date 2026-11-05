import subprocess
import sys
from pathlib import Path

def test_cli_help():
    p = subprocess.run([sys.executable, "-m", "qc_exam", "--help"], capture_output=True, text=True)
    assert p.returncode == 0
    assert "--input" in p.stdout

# Add behavioral tests for valid, boundary, invalid, and duplicate-ID cases.

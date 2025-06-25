import subprocess
import sys
from pathlib import Path

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Run Firebase token setup once before tests."""
    setup_script = Path(__file__).parent / "test_setup_tokens.py"
    result = subprocess.run(
        [sys.executable, str(setup_script)], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to run setup_tokens.py:\n{result.stderr}")
    print("Firebase token setup complete.")

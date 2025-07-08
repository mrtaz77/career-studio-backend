import asyncio
import subprocess
import sys
from pathlib import Path

import pytest

from src.database import close_db, prisma


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


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Clean up database connections before session ends."""
    try:
        # Ensure we have an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Close database connection if still connected
        if prisma.is_connected():
            loop.run_until_complete(close_db())
    except Exception as e:
        print(f"Warning: Error during database cleanup: {e}")
    finally:
        # Clean up the event loop
        try:
            if not loop.is_closed():
                loop.close()
        except Exception:
            pass


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop

    # Cleanup: ensure database is disconnected before closing loop
    try:
        if prisma.is_connected():
            loop.run_until_complete(close_db())
    except Exception as e:
        print(f"Warning: Error during test cleanup: {e}")

    # Close the loop
    try:
        if not loop.is_closed():
            loop.close()
    except Exception:
        pass

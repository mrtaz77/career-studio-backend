import subprocess
import sys
from pathlib import Path


def main():
    files = [
        f
        for f in Path("src").rglob("*.py")
        if "src/prisma_client" not in str(f).replace("\\", "/")
    ]

    if not files:
        print("No Python files to check.")
        return 0

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            *files,
        ]
    )

    if result.returncode != 0:
        print("Mypy failed - blocking commit")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

import subprocess
import sys


def run_cmd(cmd, check=True):
    return subprocess.run(
        cmd, shell=True, text=True, check=check, stdout=subprocess.PIPE
    ).stdout.strip()


def main():
    files = run_cmd("git diff --name-only --cached -- '*.py'").splitlines()
    if not files:
        print("No staged Python files for mypy.")
        return 0

    file_list = " ".join(f'"{f}"' for f in files)
    print(f"Running mypy on: {file_list}")
    result = subprocess.run(f"mypy {file_list}", shell=True)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

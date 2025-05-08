import subprocess
import sys


def run_cmd(cmd, check=True):
    return subprocess.run(
        cmd, shell=True, text=True, check=check, stdout=subprocess.PIPE
    ).stdout.strip()


def main():
    print("Stashing unstaged changes...")
    run_cmd("git stash push -k -u -m 'pre-commit-format-staged'")

    try:
        files = run_cmd("git diff --name-only --cached -- '*.py'").splitlines()
        if not files:
            print("No staged Python files to format.")
            return 0

        file_list = " ".join(f'"{f}"' for f in files)
        print(f"Formatting: {file_list}")

        # Format the working copy of all staged files
        run_cmd(f"black {file_list}")
        run_cmd(f"isort {file_list}")

        # Re-stage after formatting
        run_cmd(f"git add {file_list}")
        print("Formatting complete and files re-staged.")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return 1

    finally:
        print("Restoring unstaged changes...")
        if "pre-commit-format-staged" in run_cmd("git stash list"):
            run_cmd("git stash pop")


if __name__ == "__main__":
    sys.exit(main())

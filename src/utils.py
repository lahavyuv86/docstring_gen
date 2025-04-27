import os
import subprocess


def verify_no_code_removals(file_path):
    """Runs `git diff` in the correct project directory to check for removed code."""
    target_dir = os.path.dirname(file_path)

    # Run git diff inside the target repo
    result = subprocess.run(["git", "diff", file_path], cwd=target_dir, stdout=subprocess.PIPE)
    diff_output = result.stdout.decode("utf-8")

    # Check if any lines were removed
    removed_lines = [line for line in diff_output.split("\n") if line.startswith("-") and not line.endswith(".py")]

    if removed_lines:
        print("\n⚠️ WARNING: Some function bodies or code may have been removed!")
        print("\n".join(removed_lines))
    else:
        print("\n✅ Verification passed: No code was removed.")
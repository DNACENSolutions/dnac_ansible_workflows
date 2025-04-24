import os
import filecmp

def compare_directories(dir1, dir2):
    """
    Recursively compares two directories and returns lists of changed
    directories and files.

    Args:
        dir1 (str): Path to the first directory.
        dir2 (str): Path to the second directory.

    Returns:
        tuple: (changed_dirs, changed_files) where:
            changed_dirs (list): List of directories with differences.
            changed_files (list): List of files with differences.
    """

    changed_dirs = []
    changed_files = []

    def _compare(d1, d2):
        nonlocal changed_dirs, changed_files  # Allow modification of outer variables

        comparison = filecmp.dircmp(d1, d2)

        if comparison.left_only or comparison.right_only or comparison.diff_files:
            changed_dirs.append(os.path.relpath(d1, dir1))  # Append relative path

        for f in comparison.diff_files:
            changed_files.append(os.path.join(os.path.relpath(d1, dir1), f))

        for sub_dir in comparison.common_dirs:
            _compare(os.path.join(d1, sub_dir), os.path.join(d2, sub_dir))

    _compare(dir1, dir2)

    return changed_dirs, changed_files

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python compare_dirs.py <dir1> <dir2>")
        sys.exit(1)

    dir1_path = sys.argv[1]
    dir2_path = sys.argv[2]

    if not os.path.isdir(dir1_path) or not os.path.isdir(dir2_path):
        print("Error: Both arguments must be valid directories.")
        sys.exit(1)

    changed_directories, changed_files_list = compare_directories(dir1_path, dir2_path)

    if changed_directories:
        print("Changed Directories:")
        for directory in changed_directories:
            print(f"- {directory}")
    else:
        print("No changed directories.")

    if changed_files_list:
        print("\nChanged Files:")
        for file in changed_files_list:
            print(f"- {file}")
    else:
        print("\nNo changed files.")

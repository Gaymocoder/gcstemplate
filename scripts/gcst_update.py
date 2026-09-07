import os, subprocess
import shutil, filecmp
from pathlib import Path

GCST_NAME = "CMakeAutoBuild"

install_and_update = [
    "./.github/workflows",
    "./.gcst",
    "./cmake/gcst",
    "./build.bat",
    "./build.sh",
    "./scripts/gcst_update.py"
]

install_only = [
    "./conanfile.py",
    "./CMakeLists.txt",
]

def get_updating_files():
    all_files = []
    files_to_update = install_and_update + install_only
    for entry in files_to_update:
        path = Path(gcst_path / entry).absolute()
        if not path.is_dir():
            all_files.append(path.relative_to(gcst_path, walk_up = True))
            continue

        for file in path.rglob("*"):
            if file.is_dir():
                continue
            all_files.append(file.relative_to(gcst_path, walk_up = True))

    matches, mismatches, errors = filecmp.cmpfiles(sproject_path, gcst_path, all_files, shallow=False)
    files_to_update = []
    for name in all_files:
        if (name in set(mismatches) | set(errors)) and (gcst_path/name).exists():
            if (name in install_only) and (sproject_path/name).exists():
                continue
            files_to_update.append(name)

    return files_to_update


def find_gcst_submodule():
    global NAME
    submodules = subprocess.check_output(['git', 'config', '--file', '.gitmodules', '--get-regexp', 'url'], text = True).strip().split("\n")
    for sm in submodules:
        data = sm.split()
        if data[1].removesuffix('.git') == f'https://github.com/Gaymocoder/{GCST_NAME}':
            return Path(data[0][len('submodule.'):-len('.url')]).absolute()
    return ''


def main():
    global sproject_path, gcst_path
    if (sproject_path == gcst_path):
        gcst_path = find_gcst_submodule()
        if (gcst_path == ''):
            print("The gcstemplate is not a submodule of any repo. Merging impossible")
            return 1

    mismatches = get_updating_files()
    if (mismatches == []):
        print("Everything is up-to-date")
        return 0

    files_list = ''.join(f'  .{os.sep}{p}\n' for p in mismatches)
    print(f"WARNING! The gcstemplate files will replace these files in your root repo directory:\n{files_list}")
    confirm = input("Make sure you've backuped all important edits from the files before updating them\nDo you want to continue? [Y/n] ")
    if confirm.lower() != "y":
        print("Aborted.")
        return 0

    for file in mismatches:
        ifile = gcst_path / file
        ofile = sproject_path / file

        print(f'Copying "./{(ifile).relative_to(sproject_path, walk_up = True)}" to "./{(ofile).relative_to(gcst_path, walk_up = True)}"')
        shutil.copy(ifile, ofile)

if __name__ == '__main__':
    main()
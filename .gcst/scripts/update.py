import gcst
import os, sys
import argparse
import shutil, filecmp
from pathlib import Path

SRC = gcst.paths.repo
DEST = gcst.paths.srepo

if (DEST == SRC and not gcst.paths.submodule):
    print("The gcstemplate is not a submodule of any repo. Merging impossible. Aborting")
    sys.exit(1)

if (DEST == SRC):
    SRC = gcst.paths.submodule

install_only = []
install_and_update = []

_gio_filepath = Path(".gcst")/".gcstu-install-only"
_giu_filepath = Path(".gcst")/".gcstu-install-update"

def giu_filepath(root: Path = SRC) -> Path:
    return root/_giu_filepath

def gio_filepath(root: Path = SRC) -> Path:
    return root/_gio_filepath

def delete_fs_entry(path: Path) -> None:
    if not path.exists():
        print(f'WARNING: Deleting entry "{path}" was not found. Ignoring')
        return
    
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def get_files_from_file(list_path: Path) -> list:
    if not list_path.exists():
        return []
    
    with open(list_path, 'r', encoding = 'utf-8') as listf:
        return [line.strip() for line in listf]


def init_updating_lists() -> int:
    lgiu_filepath = giu_filepath()
    lgio_filepath = gio_filepath()
            
    global install_only, install_and_update
    install_only = get_files_from_file(lgio_filepath)
    install_and_update = get_files_from_file(lgiu_filepath)


def get_removed_iufiles() -> list:
    new_iulist = install_and_update
    old_iulist = get_files_from_file(giu_filepath(DEST))
    list_to_delete = []
    for path in old_iulist:
        if (path in new_iulist and (SRC/path).exists()) or not path:
            continue
        list_to_delete.append(path)
    return list_to_delete


def get_updating_files():
    all_files = []
    files_to_update = install_and_update + install_only
    for entry in files_to_update:
        if not entry:
            continue

        path = Path(SRC / entry).absolute()
        if not path.is_dir():
            all_files.append(path.relative_to(SRC, walk_up = True))
            continue

        for file in path.rglob("*"):
            if file.is_dir():
                continue
            all_files.append(file.relative_to(SRC, walk_up = True))

    _, mismatches, errors = filecmp.cmpfiles(DEST, SRC, all_files, shallow=False)

    files_to_update = []
    for name in all_files:
        if (name in set(mismatches) | set(errors)) and (SRC/name).exists():
            if (str(name) in install_only) and (DEST/name).exists():
                continue
            files_to_update.append(name)

    return files_to_update


def main():
    if init_updating_lists():
        return 1
    
    removes = get_removed_iufiles()
    mismatches = get_updating_files()
    if not (mismatches or removes):
        print("Everything is up-to-date")
        return 0

    files_list = '\n'.join(f'  UPDATE: .{os.sep}{p}' if p in mismatches else f'  DELETE: .{os.sep}{p}' for p in removes + mismatches)
    print(f"WARNING! The gcstemplate files will replace these files in your root repo directory:\n{files_list}")
    confirm = input("Make sure you've backuped all important edits from the files before updating them\nDo you want to continue? [Y/n] ")
    if confirm.lower() not in ["y", ""]:
        print("Aborted.")
        return 0

    for file in removes:
        rmfile = DEST / file
        print(f'Removing "./{(rmfile).relative_to(DEST, walk_up = True)}"')
        delete_fs_entry(rmfile)

    for file in mismatches:
        ifile = SRC / file
        ofile = DEST / file

        print(f'Copying "./{(ifile).relative_to(DEST, walk_up = True)}" to "./{(ofile).relative_to(DEST, walk_up = True)}"')
        ofile.parent.mkdir(parents = True, exist_ok = True)
        shutil.copy(ifile, ofile)

if __name__ == '__main__':
    sys.exit(main())
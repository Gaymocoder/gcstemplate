# Updating the template

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md)</sub>

The template can stay in your project as a git submodule. `build.sh --update` pulls its latest version and brings your copies of the template's files up to date: changed files are replaced, new ones added, dropped ones deleted.

- [Setup](#setup)
- [Updating](#updating)
- [What the updater does](#what-the-updater-does)
- [File lists](#file-lists)
- [Migrating from v5](#migrating-from-v5)

## Setup

```sh
git submodule add https://github.com/Gaymocoder/gcstemplate.git external/gcstemplate
cd external/gcstemplate
sh build.sh --update
```

On Windows, run `build.bat --update` there instead.

The first run starts from the submodule because your project has no build scripts yet. It installs the template's files into your repository root. The submodule is found by its URL in `.gitmodules`: any URL containing `Gaymocoder/gcstemplate` works, HTTPS or SSH, and the submodule can live at any path.

## Updating

From the repository root:

```sh
sh build.sh --update
```

| Option | Effect |
|---|---|
| `-u`, `--update` | Pull the template submodule, then update the project |
| `--local` | Don't pull: update from the submodule as it is checked out — offline, or to stay on a pinned version |

The pull is `git submodule update --remote --merge` on the template submodule. If it fails, nothing is updated. Commit the new submodule commit together with the updated files.

`--update` replaces the build: nothing is configured or compiled. The exit code is `0` on success and `1` on any failure.

After an update, build once and commit the regenerated `ci.yml` — see [Keeping CI in sync](local-presets.md#keeping-ci-in-sync).

## What the updater does

The updater is `.gcst/scripts/update.py` in the submodule, and it always runs from there, with the submodule's own [`gcst` package](scripting.md). It compares the template's files with your copies byte by byte and lists everything it's about to change:

```
WARNING! The gcstemplate files will replace these files in your root repo directory:
  DELETE: ./.github/workflows/scripts/old-installer.sh
  UPDATE: ./.gcst/presets.json
Make sure you've backuped all important edits from the files before updating them
Do you want to continue? [Y/n]
```

`y` or Enter proceeds, anything else aborts without changes. With nothing to do it prints `Everything is up-to-date`.

| A file is | When |
|---|---|
| replaced | it's on the update list and differs from the template's |
| added | it's on either list and missing from your project |
| deleted | it was on the update list at the previous update and no longer is, or the template no longer ships it |
| left alone | it's install-only and already exists, or it's on neither list |

> **[!WARNING]**  
> Updated files are replaced, not merged. Keep your presets in [`presets.local.json`](local-presets.md), not in `.gcst/presets.json`, and your warning tweaks outside `cmake/gcst/`.

## File lists

Both lists live in the template's `.gcst/` and are read from the submodule. One repository-relative path per line; blank lines are ignored, and a line may name a directory, which covers every file in it.

| `.gcst/.gcstu-install-update` — kept up to date | `.gcst/.gcstu-install-only` — installed once |
|---|---|
| `.github/workflows/ci.yml` | `conanfile.py` |
| CI toolchain installers: `.github/workflows/scripts/gcc.sh`, `gcc.ps1`, `clang.sh`, `clang-msvc.ps1`, `clang-mingw.ps1` | `CMakeLists.txt` |
| `.gcst/presets.json`, `.gcst/scripts/build.py`, `.gcst/scripts/configure.py` | |
| [`gcst` package](scripting.md): `.gcst/gcst/__init__.py`, `constants.py`, `detect_api.py`, `service.py` | |
| both list files | |
| `cmake/gcst/utils.cmake`, `cmake/gcst/warnings.cmake` | |
| `.gitignore`, `build.sh`, `build.bat` | |

The updater itself isn't copied: it only ever runs from the submodule.

Your copies of the lists aren't configuration. The install-only list is read from the template, so editing your copy changes nothing. Your copy of the update list is the record of the previous update: the updater compares it with the template's to find the files to delete.

> **[!WARNING]**  
> Don't add your own paths to `.gcst/.gcstu-install-update`. A path that's in your copy but not in the template's counts as dropped by the template, and the file is deleted on the next update.

## Migrating from v5

Up to v5 the updater was `scripts/gcst_update.py`, with its file list built in. It can't install the current layout: it copies the new `gcst` package without its new modules, and the project's Python scripts stop working. Update once from the submodule instead:

```sh
git submodule update --remote external/gcstemplate
cd external/gcstemplate
sh build.sh --update
```

The same steps repair a project where the old script has already been run. From then on, `sh build.sh --update` from the repository root works as usual.

Files that only v5 shipped stay behind — the current lists don't know them. Delete them by hand:

- `scripts/gcst_update.py`, `scripts/.gcstu-install-only`;
- `.github/workflows/scripts/g++.sh`, `.github/workflows/scripts/mingw32.bat`.

Paths you added to `scripts/.gcstu-install-only` no longer protect anything. If such a file is on the update list — a customised `build.sh`, say — the first update overwrites it, so back it up first.

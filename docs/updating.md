# Updating the template

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md)</sub>

The template can stay in your project as a git submodule and deliver its updates with `scripts/gcst_update.py`.

- [Setup](#setup)
- [Updating](#updating)
- [What gets updated](#what-gets-updated)
- [Install-only list](#install-only-list)

## Setup

```sh
git submodule add https://github.com/Gaymocoder/gcstemplate.git external/gcstemplate
python3 external/gcstemplate/scripts/gcst_update.py
```

The first run copies the template's files into your repository root. The submodule is found by its URL: any URL containing `Gaymocoder/gcstemplate` works, HTTPS or SSH.

## Updating

```sh
git submodule update --remote external/gcstemplate
python3 external/gcstemplate/scripts/gcst_update.py
```

The updater compares files byte by byte, lists every file it's about to overwrite and asks for confirmation — answer `y` to proceed. With nothing to update it says so and exits. Run it from the repository root.

After an update, build once and commit the regenerated `ci.yml` — see [Keeping CI in sync](local-presets.md#keeping-ci-in-sync).

## What gets updated

| Updated on every run | Installed once, never overwritten |
|---|---|
| `.github/workflows/ci.yml` | `conanfile.py` |
| `.github/workflows/scripts/`: `g++.sh`, `clang.sh`, `mingw32.bat` | `CMakeLists.txt` |
| `.gcst/presets.json`, `.gcst/scripts/build.py`, `.gcst/scripts/configure.py` | `scripts/.gcstu-install-only` |
| [`gcst` package](scripting.md): `.gcst/gcst/__init__.py`, `.gcst/gcst/constants.py` | |
| `cmake/gcst/utils.cmake`, `cmake/gcst/warnings.cmake` | |
| `scripts/gcst_update.py` | |
| `.gitignore`, `build.sh`, `build.bat` | |

The updater copies exactly these files, not whole directories. A file that isn't on the list — say, a new script in the template's `.github/workflows/scripts/` — isn't installed.

> **[!WARNING]**  
> Updated files are replaced, not merged. Keep your presets in [`presets.local.json`](local-presets.md), not in `.gcst/presets.json`, and your warning tweaks outside `cmake/gcst/`.

## Install-only list

The right column comes from `scripts/.gcstu-install-only`: one repository-relative path per line. The updater reads the copy in your project root and falls back to the template's own only when the root one doesn't exist — so it doesn't matter whether you run the updater from the submodule or from the root. Add a path to the root copy to have that file installed once and left alone afterwards.

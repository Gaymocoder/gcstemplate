# Scripting

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md)</sub>

`.gcst/gcst/` is a small Python package shared by the [build driver](build.md), the [preset generator](presets.md) and the [updater](updating.md). Your own tooling can use it too.

## Usage

Put `.gcst/` on `PYTHONPATH` — the build scripts and CI already do — and import the package:

```python
import gcst

print(gcst.name)              # "gcstemplate"
print(gcst.paths.build_dir)   # absolute path to build/
```

## Reference

| Attribute | Value |
|---|---|
| `gcst.name` | Template name, used to find the submodule |
| `gcst.path`, `gcst.paths.gcst` | `.gcst/` |
| `gcst.paths.repo` | Root of the repository the package belongs to |
| `gcst.paths.srepo` | Root of the superproject when inside a submodule, otherwise `repo` |
| `gcst.paths.submodule` | Path of the gcstemplate submodule, found in the `.gitmodules` of `srepo`, or `''` if there is none |
| `gcst.paths.build_dir` | `build/` |
| `gcst.paths.bin_dir` | `bin/` |
| `gcst.paths.temp_dir` | `.gcst/.temp/`, reserved for temporary files and ignored by git |
| `gcst.paths.ghci_dir` | `.github/workflows/` |
| `gcst.paths.configure_py` | `.gcst/scripts/configure.py` |
| `gcst.paths.update_py` | `.gcst/scripts/update.py` inside the gcstemplate submodule, or `''` if there is none |
| `gcst.paths.default_preset` | `.gcst/.default` |

## Service

| Function | Does |
|---|---|
| `gcst.submodule_update()` | Pulls the gcstemplate submodule with `git submodule update --remote --merge`. Returns `0`, or `1` / git's exit code on failure, printing why |
| `gcst.service.extract_args(namespace, actions)` | Turns the values that `argparse` parsed for `actions` back into command-line arguments, to pass options on to another script |

## Versions

`gcst.versions` parses a version string into its parts and finds the local Visual Studio.

```python
import gcst

v = gcst.versions("19.1.7")
v.full    # "19.1.7"
v.major   # "19"
v.minor   # "1"

gcst.versions.msvc_path()   # Path to the latest Visual Studio with the C++ toolset, or None
```

The constructor returns `None` for anything that isn't a numeric version, and `msvc_path()` returns `None` when `vswhere.exe` isn't there — outside Windows, for instance. The generator uses this to turn [`.vars`](presets.md#toolchain-versions) entries into Conan settings, and the build driver uses `msvc_path()` to [point Conan at Visual Studio](dependencies.md#how-conan-install-runs).

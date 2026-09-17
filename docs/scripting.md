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
| `gcst.paths.submodule` | Path of the gcstemplate submodule, or `''` if there is none |
| `gcst.paths.build_dir` | `build/` |
| `gcst.paths.bin_dir` | `bin/` |
| `gcst.paths.temp_dir` | `.gcst/.temp/`, reserved for temporary files and ignored by git |
| `gcst.paths.configure_py` | `.gcst/scripts/configure.py` |
| `gcst.paths.default_preset` | `.gcst/.default` |

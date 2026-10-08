# Dependencies

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md) · [Settings](settings.md)</sub>

Dependencies are managed by Conan 2: declared in `conanfile.py`, installed into `build/` before CMake runs, and found with a plain `find_package()`.

- [`conanfile.py`](#conanfilepy)
- [How `conan install` runs](#how-conan-install-runs)
- [Local recipes](#local-recipes)

## `conanfile.py`

Uses the `CMakeToolchain` and `CMakeDeps` generators. Declare dependencies in the `requires` attribute — [local recipes](#local-recipes) rely on it:

```python
class gcstConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    default_options = {
        "boost/*:header_only": True,
        "cli11/*:header_only": False
    }

    requires = (
        "boost/1.87.0",
        "cli11/[>=2.7.2]"
    )
```

Package options go into `default_options`:

- **Boost** is used header-only.
- **CLI11**, which the [settings module](settings.md) is built on, is the opposite: with `header_only=False` Conan builds it as a static library and defines `CLI11_COMPILE` for its consumers, so its implementation is compiled once instead of in every file that includes it.

The `win64-msvc-msvcstl` preset builds CLI11 with the `NMake Makefiles` generator, set for that package alone in the preset's [`conan` section](presets.md#the-conan-section):

```json
"conf": {
    "cli11/*:tools.cmake.cmaketoolchain:generator": "NMake Makefiles"
}
```

## How `conan install` runs

| Aspect | Behaviour |
|---|---|
| Profile | `conan/profiles/<preset>`, generated from the preset's [`conan` section](presets.md#the-conan-section) |
| Output | `build/`, where the preset's CMake toolchain file points |
| Missing binaries | built from source (`--build=missing`) |
| System packages | may be installed: runs with `tools.system.package_manager:mode=install` and `sudo=True`, so recipes with system requirements can call the OS package manager through `sudo` |
| Visual Studio | its installation path is looked up with `vswhere` and passed as `tools.microsoft.msbuild:installation_path`, so dependencies that build with MSBuild find the toolchain |
| Dependency graph | written to `build/graph.json` (`--format=json --out-file`), which CI uses to [cache exactly the packages of this build](ci.md#conan-cache) |

A failed install stops the build with [exit code `6`](build.md#stages-and-exit-codes). In CI, installed packages are [cached per preset](ci.md#conan-cache).

## Local recipes

Put your own Conan recipes into `recipes/`, one directory per package, named after the package:

```
recipes/
└── mylib/
    └── conanfile.py
```

Before `conan install`, every directory whose name matches a requirement of `conanfile.py` is exported with `conan export`, using the version from that requirement. Directories without a matching requirement are skipped. A failed export stops the build with [exit code `5`](build.md#stages-and-exit-codes).

> **[IMPORTANT]**  
> Versions are read with `conan inspect`, which sees only the `requires` attribute. Requirements added in a `requirements()` method are invisible to it, and their local recipes are skipped without a warning.

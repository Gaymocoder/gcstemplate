# Dependencies

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md) · [Settings](settings.md)</sub>

Dependencies are managed by Conan 2: declared in `conanfile.py` on top of the template's own ones, installed into `build/` before CMake runs, and found with a plain `find_package()`.

- [`conanfile.py`](#conanfilepy)
- [How `conan install` runs](#how-conan-install-runs)
- [Local recipes](#local-recipes)

## `conanfile.py`

Dependencies come from two files:

- **`.gcst/gcst_conan_deps.py`** — the `gcstDeps` base class with what the template's own code needs. It belongs to the template and is [kept up to date](updating.md#file-lists) by `--update`, so edits to it are overwritten.
- **`conanfile.py`** — your project's recipe. It inherits `gcstDeps` and adds dependencies of its own to the base ones. It uses the `CMakeToolchain` and `CMakeDeps` generators:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".gcst"))

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps

from gcst_conan_deps import gcstDeps

class gcstConan(gcstDeps):
    settings = "os", "arch", "compiler", "build_type"

    default_options = {
        **gcstDeps.default_options,
        "boost/*:header_only": True
    }

    requires = (
        *gcstDeps.requires,
        "boost/1.87.0"
    )

    def generate(self):
        CMakeToolchain(self).generate()
        CMakeDeps(self).generate()
```

- **Declare dependencies in the `requires` attribute** and package options in `default_options`. [Local recipes](#local-recipes) rely on the attribute, a `requirements()` method is invisible to them.
- **Keep `*gcstDeps.requires` and `**gcstDeps.default_options`.** An attribute of your class replaces the base one entirely, and the template's dependencies would be lost without them.
- **Keep the `sys.path` line.** It lets Conan find the base class however Conan is started — by the build scripts or by hand.

| Package | Declared in | Used by |
|---|---|---|
| `cli11/[>=2.7.2]`, `header_only=False` | `gcstDeps` | the [settings module](settings.md) |
| `boost/1.87.0`, `header_only=True` | `conanfile.py` | the demo in `hello/` |

CLI11 is built as a static library: with `header_only=False` Conan defines `CLI11_COMPILE` for its consumers, so its implementation is compiled once instead of in every file that includes it.

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

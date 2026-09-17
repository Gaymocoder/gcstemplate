# Presets

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md)</sub>

The format of `.gcst/presets.json`: what a preset consists of and what each part turns into. Local presets use the same format — what they can do on top of it is described in [Local presets](local-presets.md).

- [Anatomy](#anatomy)
- [The `cmake` section](#the-cmake-section)
- [The `conan` section](#the-conan-section)
- [The `github_ci` section](#the-github_ci-section)
- [Service keys](#service-keys)
- [Adding a preset](#adding-a-preset)

## Anatomy

A preset is a key in `.gcst/presets.json` with three sections:

```json
"unix-clang-libc++": {
    "cmake": {
        "description": "Clang + LLVM libc++",
        "binaryDir": "${sourceDir}/build",
        "cacheVariables": {
            "CMAKE_C_COMPILER": "clang",
            "CMAKE_CXX_COMPILER": "clang++",
            "CMAKE_TOOLCHAIN_FILE": "${sourceDir}/build/conan_toolchain.cmake",
            "CMAKE_BUILD_TYPE": "Release"
        }
    },
    "conan": {
        "settings": {
            "os": "Linux",
            "arch": "x86_64",
            "compiler": "clang",
            "compiler.version": "22",
            "compiler.libcxx": "libc++",
            "build_type": "Release"
        },
        "conf": {
            "tools.build:exelinkflags": "[\"-fuse-ld=lld\"]",
            "tools.build:sharedlinkflags": "[\"-fuse-ld=lld\"]",
            "tools.build:compiler_executables": "{\"c\": \"clang\", \"cpp\": \"clang++\"}"
        }
    },
    "github_ci": [
        {
            "run-files": ["clang.sh"]
        }
    ]
}
```

| Section | Becomes |
|---|---|
| [`cmake`](#the-cmake-section) | a configure preset in `CMakePresets.json` |
| [`conan`](#the-conan-section) | `conan/profiles/<preset>`, plus the CI runner |
| [`github_ci`](#the-github_ci-section) | toolchain installation steps in `ci.yml`, plus a matrix entry |

## The `cmake` section

The body of a CMake [configure preset](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html). The key becomes its `name`; everything else is copied as is, so any field of the presets schema works, `inherits` included.

Keep `binaryDir` at `${sourceDir}/build` and the toolchain file at `build/conan_toolchain.cmake`: that is where Conan writes its output.

## The `conan` section

Sections of a Conan profile, written to `conan/profiles/<preset>`. Any section made of `key=value` lines can be used — `settings`, `conf`, `options` and so on. The preset above becomes:

```ini
[settings]
os=Linux
arch=x86_64
compiler=clang
compiler.version=22
compiler.libcxx=libc++
build_type=Release

[conf]
tools.build:exelinkflags=["-fuse-ld=lld"]
tools.build:sharedlinkflags=["-fuse-ld=lld"]
tools.build:compiler_executables={"c": "clang", "cpp": "clang++"}
```

`settings.os` is required: it also picks the runner and the build command of the preset's CI job.

| `settings.os` | Runner | Build command |
|---|---|---|
| `Linux` | `ubuntu-latest` | `sh build.sh` |
| `Windows` | `windows-latest` | `./build.bat` |

How the profile is used during a build is described in [Dependencies](dependencies.md#how-conan-install-runs).

## The `github_ci` section

A list of GitHub Actions steps that prepare the runner for this preset. Each step automatically gets `if: ${{ matrix.preset == '<preset>' }}`, so it runs only in the preset's own job. Steps are copied as is, with one addition — `run-files`:

```json
"github_ci": [
    { "uses": "KyleMayes/install-llvm-action@v2", "with": { "version": "20" } },
    { "run-files": ["mingw32.bat"], "shell": "pwsh" }
]
```

`run-files` concatenates the listed scripts from `.github/workflows/scripts/` into the step's `run`. Other keys of the step, such as `shell`, are kept.

| Script | Installs |
|---|---|
| `g++.sh` | GCC 14 as the default `gcc` / `g++` |
| `clang.sh` | LLVM 22 with libc++ as the default `clang` / `clang++` |
| `mingw32.bat` | MinGW-w64 GCC 14.2, added to `PATH` |

Where these steps sit in the job is shown in [Build job](ci.md#build-job).

## Service keys

Two keys of `presets.json` aren't presets:

| Key | Holds |
|---|---|
| `.common-pre` | CI steps placed before the per-preset `github_ci` steps |
| `.common-post` | CI steps placed after the generated `Build` step |

The resulting step order is:

```
.common-pre  →  github_ci steps of every preset  →  Build  →  .common-post
```

`Build` is generated: `${{ matrix.build }} --preset ${{ matrix.preset }}`. What the shipped common steps do is described in [Build job](ci.md#build-job).

## Adding a preset

1. Add a key with the three sections to `.gcst/presets.json`.
2. Put its toolchain installation steps into `github_ci`, adding a script to `.github/workflows/scripts/` if needed.
3. Build it once — this regenerates `ci.yml`.
4. Commit `presets.json` together with the regenerated `ci.yml`.

In a project that receives [template updates](updating.md), `.gcst/presets.json` is overwritten by them — add presets to [`presets.local.json`](local-presets.md#add-a-preset) instead.

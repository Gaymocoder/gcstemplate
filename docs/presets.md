# Presets

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md) · [Settings](settings.md)</sub>

The format of `.gcst/presets.json`: what a preset consists of and what each part turns into. Local presets use the same format — what they can do on top of it is described in [Local presets](local-presets.md).

- [Anatomy](#anatomy)
- [The `cmake` section](#the-cmake-section)
- [The `conan` section](#the-conan-section)
- [The `github_ci` section](#the-github_ci-section)
- [Service keys](#service-keys)
- [Toolchain versions](#toolchain-versions)
- [Adding a preset](#adding-a-preset)

## Anatomy

A preset is a key in `.gcst/presets.json` with three sections:

```json
"unix-clang-libc++": {
    "cmake": {
        "description": "Clang + LLVM libc++",
        "generator": "Unix Makefiles",
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

Sections of a Conan profile, written to `conan/profiles/<preset>`. Any section made of `key=value` lines can be used — `settings`, `conf`, `options` and so on. A `settings` section is required. The preset above becomes:

```ini
[settings]
os=Linux
arch=x86_64
compiler=clang
compiler.libcxx=libc++
build_type=Release
compiler.version=19

[conf]
tools.build:exelinkflags=["-fuse-ld=lld"]
tools.build:sharedlinkflags=["-fuse-ld=lld"]
tools.build:compiler_executables={"c": "clang", "cpp": "clang++"}
```

`compiler.version` isn't in the preset: when it's missing, the generator fills it from [`.vars`](#toolchain-versions), and the same happens to `compiler.runtime_version` of a Clang preset that targets the MSVC runtime. Set them explicitly in the preset to pin a version to that preset alone.

`settings.os` is required for another reason too: it picks the runner and the build command of the preset's CI job.

| `settings.os` | Runner | Build command |
|---|---|---|
| `Linux` | `ubuntu-latest` | `sh build.sh` |
| `Windows` | `windows-latest` | `./build.bat` |

How the profile is used during a build is described in [Dependencies](dependencies.md#how-conan-install-runs).

## The `github_ci` section

A list of GitHub Actions steps that prepare the runner for this preset. Each step automatically gets `if: ${{ matrix.preset == '<preset>' }}`, so it runs only in the preset's own job. Steps are copied as is, with one addition — `run-files`:

```json
"github_ci": [
    { "uses": "ilammy/msvc-dev-cmd@v1", "with": { "toolset": "{gcst::MSVC_RUNTIME_GITHUB_CI_FULL_VERSION}" } },
    { "run-files": ["clang-msvc.ps1"], "shell": "pwsh" }
]
```

`run-files` concatenates the listed scripts from `.github/workflows/scripts/` into the step's `run`. Other keys of the step, such as `shell`, are kept. Every script needs a version in `.vars` under `<NAME>_VERSION`, where `<NAME>` is the script's file name up to the first `.` or `-` — `clang-msvc.ps1` needs `CLANG_VERSION`. Without it the generator aborts.

`{gcst::...}` tags are replaced everywhere in the generated `ci.yml`, in inlined scripts and in step fields alike — see [Toolchain versions](#toolchain-versions).

Shipped scripts:

| Script | Installs |
|---|---|
| `gcc.sh` | GCC from `ppa:ubuntu-toolchain-r/test` as the default `gcc` / `g++` |
| `clang.sh` | LLVM from `apt.llvm.org`, with libc++, as the default `clang` / `clang++` |
| `gcc.ps1` | MinGW-w64 GCC through Chocolatey, added to `PATH` |
| `clang-msvc.ps1` | Official LLVM Windows release into `C:\LLVM`, added to `PATH` |
| `clang-mingw.ps1` | [llvm-mingw](https://github.com/mstorsjo/llvm-mingw) toolchain (UCRT, libc++), added to `PATH` |

The Windows scripts look their release up with the `gh` CLI, so the job needs `GH_TOKEN` — the shipped workflow sets it from `github.token`.

Where these steps sit in the job is shown in [Build job](ci.md#build-job).

## Service keys

Keys of `presets.json` that aren't presets:

| Key | Holds |
|---|---|
| `.vars` | [toolchain versions and other variables](#toolchain-versions) |
| `.common-pre` | CI steps placed before the per-preset `github_ci` steps |
| `.common-post` | CI steps placed after the generated `Build` step |

The resulting step order is:

```
.common-pre  →  github_ci steps of every preset  →  Build  →  .common-post
```

`Build` is generated: `${{ matrix.build }} --preset ${{ matrix.preset }}`. What the shipped common steps do is described in [Build job](ci.md#build-job).

## Toolchain versions

Compiler versions live in one place, the `.vars` service key, separately for your machine and for CI:

```json
".vars": {
    "GCC_VERSION":          { "local": "16.1.0", "github_ci": "16.1.0" },
    "CLANG_VERSION":        { "local": "19.1.7", "github_ci": "19.1.7" },
    "MSVC_VERSION":         { "local": "19.44",  "github_ci": "19.44"  },
    "MSVC_RUNTIME_VERSION": { "local": "14.44",  "github_ci": "14.44"  }
}
```

The generator picks `github_ci` when it runs on a GitHub runner and `local` otherwise. Values are plain numeric versions, such as `16.1.0` or `19.44`.

Every key ending in `_VERSION` also produces derived values, for both environments:

| Derived name | Value for `"16.1.0"` |
|---|---|
| `<TAG>_<ENV>_FULL_VERSION` | `16.1.0` |
| `<TAG>_<ENV>_MAJOR_VERSION` | `16` |
| `<TAG>_<ENV>_CONAN_VERSION` | MSVC keys only: `194` from `19.44`, and `v144` from the runtime's `14.44` |

`<TAG>` is the key without its `_VERSION` suffix (`GCC`, `CLANG`, `MSVC`, `MSVC_RUNTIME`), `<ENV>` is `LOCAL` or `GITHUB_CI`.

The values are used in two places:

- **Conan profiles** — a preset without `compiler.version` gets the major version of `<COMPILER>_VERSION`, where `<COMPILER>` is its `settings.compiler` in upper case; MSVC presets get the `_CONAN_VERSION` form instead.
- **The generated `ci.yml`** — every `{gcst::<name>}` tag is replaced with the value of `<name>`. Names are case-insensitive, unknown names are left alone.

Versions for your own machine go into `presets.local.json` — see [Toolchain versions](local-presets.md#toolchain-versions) there.

## Adding a preset

1. Add a key with the three sections to `.gcst/presets.json`.
2. Put its toolchain installation steps into `github_ci`, adding a script to `.github/workflows/scripts/` if needed.
3. Make sure `.vars` holds a `<NAME>_VERSION` for every script the preset runs.
4. Build it once — this regenerates `ci.yml`.
5. Commit `presets.json` together with the regenerated `ci.yml`.

In a project that receives [template updates](updating.md), `.gcst/presets.json` is overwritten by them — add presets to [`presets.local.json`](local-presets.md#add-a-preset) instead.

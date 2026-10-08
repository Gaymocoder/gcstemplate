# Local presets

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md) · [Settings](settings.md)</sub>

`presets.local.json` changes the set of presets without touching `.gcst/presets.json`: it adds presets, replaces or merges into existing ones, and drops the ones you don't need.

- [How it is applied](#how-it-is-applied)
- [Toolchain versions](#toolchain-versions)
- [Add a preset](#add-a-preset)
- [Replace a preset](#replace-a-preset)
- [Merge into a preset](#merge-into-a-preset)
- [Import and remove base presets](#import-and-remove-base-presets)
- [Using another file](#using-another-file)
- [Keeping CI in sync](#keeping-ci-in-sync)

## How it is applied

`presets.local.json` in the repository root is read after `.gcst/presets.json` and applied on top of it, **key by key in file order**. Presets in it use the [same format](presets.md#anatomy) as the base file.

The file isn't ignored by the template's `.gitignore`. Commit it to change the project's presets for everyone, CI included, or add it to `.gitignore` to keep it machine-local. Either way it survives [template updates](updating.md), unlike `.gcst/presets.json`.

## Toolchain versions

The compiler versions the base presets build with live in the [`.vars`](presets.md#toolchain-versions) service key. Your machine rarely has exactly those, so override the `local` side of the ones you care about. `".merge": true` keeps the rest of `.vars` intact:

```json
{
    ".vars": {
        ".merge": true,
        "GCC_VERSION": { "local": "14.2.0", "github_ci": "16.1.0" }
    }
}
```

Now a local build asks Conan for `compiler.version=14`, while CI keeps building with GCC 16.

Without `".merge": true` the whole `.vars` key is replaced, and the versions of the other compilers are gone.

## Add a preset

A key that doesn't exist in the base file adds a new preset. `compiler.version` may be left out — it comes from [`.vars`](#toolchain-versions). This one builds with Ninja instead of Make:

```json
{
    "unix-gcc-libstdc++-ninja": {
        "cmake": {
            "description": "GCC + libstdc++, Ninja",
            "inherits": "unix-gcc-libstdc++",
            "generator": "Ninja"
        },
        "conan": {
            "settings": {
                "os": "Linux",
                "arch": "x86_64",
                "compiler": "gcc",
                "compiler.libcxx": "libstdc++11",
                "build_type": "Release"
            }
        },
        "github_ci": [
            { "run-files": ["gcc.sh"] }
        ]
    }
}
```

All presets share `build/`, and CMake refuses to reuse a binary directory configured with another generator. When switching between this preset and a Make-based one, build with [`--clear`](build.md#options).

> **[NOTE]**  
> A debug build doesn't need a preset of its own: use [`--debug`](build.md#build-type). The build driver passes the build type to Conan and CMake on every run, so `build_type` and `CMAKE_BUILD_TYPE` set in a preset are overridden.

## Replace a preset

A key that exists in the base file replaces that preset **entirely**. To change only some fields, [merge](#merge-into-a-preset) instead.

## Merge into a preset

With `".merge": true` the local preset is deep-merged into the base one: nested objects are merged key by key, any other value is overwritten.

```json
{
    "unix-gcc-libstdc++": {
        ".merge": true,
        "cmake": {
            "cacheVariables": {
                "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
            }
        }
    }
}
```

## Import and remove base presets

`.import` keeps only the listed base presets, `.remove` drops the listed ones. Both take either a list of exact names or a string with a Python regular expression, searched anywhere in the preset name. [Service keys](presets.md#service-keys) are never affected.

```json
{ ".import": ["unix-gcc-libstdc++", "unix-clang-libc++"] }
```

```json
{ ".remove": "msvc" }
```

| Value | Effect |
|---|---|
| `".remove": ["win64-msvc-msvcstl"]` | removes exactly that preset |
| `".remove": "msvc"` | removes `win64-clang-msvc` and `win64-msvc-msvcstl` |
| `".remove": "^win64"` | removes every Windows preset |
| `".remove": ".*"` | removes every base preset, to define all presets locally |
| `".import": "^unix-"` | keeps only the Linux presets |

> **[TIP]**  
> Keys are applied in order, so put `.import` and `.remove` **before** the presets you add — otherwise a pattern may catch them too.

## Using another file

```sh
sh build.sh --presets-local presets.windows.json   # a different file inside the repository
sh build.sh --ignore-local                         # base presets only
```

The same flags work for `configure.py` run on its own — see [Running the generator alone](build.md#running-the-generator-alone).

## Keeping CI in sync

A build regenerates `ci.yml` from base **and** local presets. CI regenerates it too, but only from what is committed, and [fails](ci.md#build-job) when the two differ. So:

- local presets that should shape the CI matrix — commit `presets.local.json` together with the regenerated `ci.yml`;
- local presets meant for your machine only — build with [`--no-ghci`](build.md#options), and `ci.yml` stays untouched.

# Local presets

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md)</sub>

`presets.local.json` changes the set of presets without touching `.gcst/presets.json`: it adds presets, replaces or merges into existing ones, and drops the ones you don't need.

- [How it is applied](#how-it-is-applied)
- [Add a preset](#add-a-preset)
- [Replace a preset](#replace-a-preset)
- [Merge into a preset](#merge-into-a-preset)
- [Import and remove base presets](#import-and-remove-base-presets)
- [Using another file](#using-another-file)
- [Keeping CI in sync](#keeping-ci-in-sync)

## How it is applied

`presets.local.json` in the repository root is read after `.gcst/presets.json` and applied on top of it, **key by key in file order**. Presets in it use the [same format](presets.md#anatomy) as the base file.

The file isn't ignored by the template's `.gitignore`. Commit it to change the project's presets for everyone, CI included, or add it to `.gitignore` to keep it machine-local. Either way it survives [template updates](updating.md), unlike `.gcst/presets.json`.

## Add a preset

A key that doesn't exist in the base file adds a new preset:

```json
{
    "unix-gcc-libstdc++-debug": {
        "cmake": {
            "description": "GCC + libstdc++, Debug",
            "inherits": "unix-gcc-libstdc++",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "Debug"
            }
        },
        "conan": {
            "settings": {
                "os": "Linux",
                "arch": "x86_64",
                "compiler": "gcc",
                "compiler.version": "14",
                "compiler.libcxx": "libstdc++11",
                "build_type": "Debug"
            }
        },
        "github_ci": [
            { "run-files": ["g++.sh"] }
        ]
    }
}
```

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

# Continuous integration

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md)</sub>

`.github/workflows/ci.yml` builds every preset on GitHub Actions and records the result on the commit.

- [Triggers](#triggers)
- [Build job](#build-job)
- [Conan cache](#conan-cache)
- [Verdicts in `git log`](#verdicts-in-git-log)

## Triggers

Pushes to `master` and `stable`, pull requests and manual dispatch. Triggers live in the handwritten part of `ci.yml` — see [Generated and handwritten files](architecture.md#generated-and-handwritten-files).

## Build job

One job per preset, with `fail-fast: false` so a broken toolchain doesn't hide the state of the others. The whole matrix builds with [`GCST_WERROR=ON`](build.md#warnings-as-errors). Each job:

| # | Step | Comes from |
|---|---|---|
| 1 | Set up Python 3.12, install Conan and ruamel.yaml, check out, detect the Conan profile | `.common-pre` |
| 2 | Run `configure.py` and fail if the committed `ci.yml` differs from the generated one — see [Keeping CI in sync](local-presets.md#keeping-ci-in-sync) | `.common-pre` |
| 3 | Restore the [Conan cache](#conan-cache) | `.common-pre` |
| 4 | Install the preset's toolchain | the preset's [`github_ci`](presets.md#the-github_ci-section) |
| 5 | Build with the preset | generated `Build` step |
| 6 | Record the result for the [verdict](#verdicts-in-git-log), save the Conan cache | `.common-post` |

`.common-pre` and `.common-post` are [service keys](presets.md#service-keys) of `presets.json`.

## Conan cache

Installed packages are saved per preset after a successful dependency install and restored on the next run. The cache key covers `conanfile.py`, the preset's Conan profile and [`recipes/`](dependencies.md#local-recipes). When any of them changes, the latest cache of the preset is restored as a base and saved again under the new key.

## Verdicts in `git log`

After the matrix finishes, the `notes` job collects the results and attaches them to the commit as a git note in `refs/notes/ci`, for example:

```
— Builds with:
 - unix-clang-libc++        ✓
 - unix-clang-libstdc++     ✓
 - unix-gcc-libstdc++       ✓
 - win64-clang-libstdc++    ✓
 - win64-clang-msvc         ✓
 - win64-gcc-libstdc++      ✗
 - win64-msvc-msvcstl       ? (cancelled)
```

`✓` is success, `✗` is failure, anything else is shown as `? (<status>)`. Notes live beside the commit and don't change its hash. The job needs `contents: write`, which it declares itself.

To see them locally:

```sh
git fetch origin 'refs/notes/*:refs/notes/*'
git log --notes=ci
```

To fetch and show them by default:

```sh
git config --add remote.origin.fetch '+refs/notes/*:refs/notes/*'
git config notes.displayRef refs/notes/ci
```

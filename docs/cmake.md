# CMake modules

<sub>[README](../README.md) · [Architecture](architecture.md) · [Building](build.md) · [Presets](presets.md) · [Local presets](local-presets.md) · [Dependencies](dependencies.md) · [CMake modules](cmake.md) · [CI](ci.md) · [Updating](updating.md) · [Scripting](scripting.md)</sub>

`cmake/gcst/` provides helpers that give every target the project's include paths, warning set and optimization flags in one call.

- [Project conventions](#project-conventions)
- [`gcst_binary_prepare`](#gcst_binary_prepare)
- [`gcst_export_prepare`](#gcst_export_prepare)
- [Warnings](#warnings)
- [Optimization](#optimization)
- [Helpers](#helpers)

## Project conventions

The root `CMakeLists.txt` sets up everything the helpers rely on:

- C++23, required;
- `GCST_INCLUDE_DIRS` pointing at `include/`;
- static libraries in `build/lib/`, executables in `bin/`;
- `cmake/gcst/utils.cmake` included, which also includes `cmake/gcst/warnings.cmake`;
- one `add_subdirectory()` per subproject.

Public headers go into `include/<project>/`, sources into `src/` of each subproject. The [demo project](../README.md#demo-project) follows this layout.

## `gcst_binary_prepare`

```cmake
gcst_binary_prepare(<target>)
```

Prepares any target — executable, library or object library:

- adds `GCST_INCLUDE_DIRS` as a public include directory;
- applies the [warning set](#warnings) for the current compiler;
- applies [per-configuration optimization](#optimization);
- on MinGW, links `stdc++exp` for C++23 targets, which `std::print` needs there;
- prints the resulting compile options and linked libraries to the configure log — call it after `target_link_libraries()` to see them.

```cmake
add_executable(my_app src/main.cpp)
target_link_libraries(my_app PRIVATE Boost::headers)
gcst_binary_prepare(my_app)
```

## `gcst_export_prepare`

```cmake
gcst_export_prepare(<target> [<object-library>...])
```

Turns a library target into an exportable library assembled from object modules:

- adds the object files of every listed object library to `<target>`;
- creates an alias from the target name split at the first underscore: `gcst_utils` → `gcst::utils`; a name without underscores gets `name::name`;
- sets `EXPORT_NAME` to the part after the prefix;
- adds `GCST_INCLUDE_DIRS` for the build tree and `include` for the install tree as public include directories;
- applies [warnings](#warnings) and [optimization](#optimization), and on MinGW passes `stdc++exp` on to consumers.

```cmake
add_library(gcst_utils_exstd OBJECT src/exstd.cpp)
gcst_binary_prepare(gcst_utils_exstd)

add_library(gcst_utils STATIC)
gcst_export_prepare(gcst_utils gcst_utils_exstd)

# elsewhere
target_link_libraries(my_app PRIVATE gcst::utils)
```

> [!NOTE]
> Only object files are taken from the modules. Their own usage requirements — link dependencies, compile definitions — don't reach the exported library and have to be added to it directly.

## Warnings

```cmake
gcst_target_warnings(<target>)
```

Applies a curated warning set chosen by compiler; both helpers above call it. The `GCST_WARNINGS_AS_ERRORS` option, `OFF` by default, turns significant warnings into errors — the build scripts set it from [`GCST_WERROR`](build.md#warnings-as-errors).

| | GCC / Clang | MSVC |
|---|---|---|
| Base set | `GCST_WARN_GNU`: `-Wall -Wextra -Wpedantic`, correctness (`-Wshadow`, `-Wnull-dereference`, `-Wcast-qual`, …), polymorphism (`-Wnon-virtual-dtor`, `-Woverloaded-virtual`, …), control flow, conversions | `GCST_WARN_MSVC`: `/W4 /permissive- /Zc:__cplusplus /Zc:preprocessor` plus off-by-default diagnostics raised to level 1, each mapped to its GNU counterpart |
| Compiler-specific | `GCST_WARN_GCC_ONLY` (`-Wduplicated-cond`, `-Wlogical-op`, `-Wuseless-cast`, …), `GCST_WARN_CLANG_ONLY` (`-Wcomma`, `-Wloop-analysis`, …) | — |
| As errors | `-Werror` **minus** a blacklist, `GCST_WARN_GNU_NOT_ERRORS`: unused entities, conversions, `float-equal`, `old-style-cast`, `switch-enum`, deprecations and a few more stay warnings | only a whitelist, `GCST_WARN_MSVC_ERRORS`: missing return, uninitialized variables and pointers, format-string mismatches, and C-specific type errors |

MSVC has no counterpart of `-Wno-error=`, hence a whitelist there and a blacklist on the GNU side.

The lists are plain CMake variables read when the function is called, so they can be extended after including the module:

```cmake
list(APPEND GCST_WARN_GNU -Wmissing-declarations)
```

## Optimization

```cmake
gcst_target_optimization(<target>)
```

Also called by both helpers.

| Configuration | GCC / Clang | MSVC |
|---|---|---|
| `Debug` | `-O0 -g` | `/Od /Zi` |
| `Release` | `-O2` | `/O2` |
| `RelWithDebInfo` | `-O2 -g` | `/O2 /Zi` |
| `MinSizeRel` | `-Os` | `/O1` |

## Helpers

| Function | Description |
|---|---|
| `gcst_message(<text>)` | Prints `-- \| (GCST) \| <text>` to the configure log |
| `gcst_normalize(<var>)` | Turns a list variable into a space-separated string; `*-NOTFOUND` and empty values become `""` |

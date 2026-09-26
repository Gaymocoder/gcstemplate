import re
import gcst
import json
import argparse
import os, sys, shutil

from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString as lss

PREFIX = " |GCST| "
def gcstout(*args, **kwargs):
    pref = PREFIX
    if len(args) != 0:
        pref += "--"
    print(pref, *args, **kwargs)

VARS = {}
CONAN_PROFILES = {}
CMAKE_PRESETS = {
    "version": 3,
    "cmakeMinimumRequired": {
        "major": 3,
        "minor": 25,
        "patch": 0
    },
    "configurePresets": []
}


yaml = YAML()

def deep_merge(a, b):
    result = a.copy()
    for key, value in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def getArgs():
    argvParser = argparse.ArgumentParser(prog = 'gcst-configurer')
    argvParser.add_argument('-pl', '--presets-local', default = None)
    argvParser.add_argument('-il', '--ignore-local', action = 'store_true')

    argvParser.add_argument('--no-cmake', action = 'store_true')
    argvParser.add_argument('--no-conan', action = 'store_true')
    argvParser.add_argument('--no-ghci', action = 'store_true')
    args = argvParser.parse_args()
    return args

def ignore_local_presets():
    return getArgs().ignore_local


def run_from_file(script_name):
    script_path = gcst.paths.ghci_dir/"scripts"/script_name
    with open(script_path, 'r', encoding = 'utf-8') as script:
        text = script.read()
        if len(VARS) == 0:
            return text + "\n\n"
        for varname in VARS:
            if type(VARS[varname]) in [list, dict]:
                continue
            vartag = f'{{gcst::{varname.lower()}}}'
            if vartag in text:
                text = text.replace(vartag, VARS[varname])
                gcstout(f'-- -- "{vartag}" in "{script_name}"-script replaced with "{VARS[varname]}"')
        return text + "\n\n"


def cmake_preset_process(key, preset, out_presets):
    cmake_preset = {"name": key, **preset["cmake"]}
    out_presets["configurePresets"].append(cmake_preset)

    
def conan_preset_process(key, preset, out_profiles):
    out_profiles[key] = ''
    if 'settings' not in preset['conan']:
        gcstout('-- -- ERROR: "settings"-section for conan is required, but not found. Aborting')
        return 1

    settings = preset['conan']['settings']
    if 'compiler.version' not in settings:
        compver = f'{settings["compiler"].upper()}_VERSION'
        if not (compver in VARS and 'local' in VARS[compver] and 'github_ci' in VARS[compver]):
            gcstout('-- -- ERROR: no version for compiler is specified in conan. Aborting')
            sys.exit(2)

        if 'GITHUB_PATH' in os.environ.copy():
            VARS[compver]["local"] = VARS[compver]["github_ci"]
        settings["compiler.version"] = gcst.versions(VARS[compver]["local"]).major

    for namespace in preset["conan"]:
        out_profiles[key] += f'[{namespace}]\n'
        for conkey in preset["conan"][namespace]:
            conval = preset["conan"][namespace][conkey]
            out_profiles[key] += f'{conkey}={conval}\n'
        out_profiles[key] += '\n'


def githubci_preset_process(key, preset, out_steps, out_matrix):
    matrix_preset = {"preset": f'{key}'}
    match preset["conan"]["settings"]["os"]:
        case "Linux":
            matrix_preset["os"] = "ubuntu-latest"
            matrix_preset["build"] = "sh build.sh"

        case "Windows":
            matrix_preset["os"] = "windows-latest"
            matrix_preset["build"] = "./build.bat"

    preset_steps = []
    for step in preset["github_ci"]:
        step["if"] = f'${{{{ matrix.preset == \'{key}\' }}}}'
        if "run-files" not in step:
            preset_steps.append(step)
            continue

        i = 0
        step["run"] = ''
        for script in step["run-files"]:
            version = None
            compiler = re.split(r"\.|\-", script)[0]
            compver = f'{compiler.upper()}_VERSION'
            if not (compver in VARS and 'local' in VARS[compver] and 'github_ci' in VARS[compver]):
                gcstout(f"-- ERROR: no version was found for '{script}'-script. Aborting")
                gcstout(f"-- ADVICE: define it as '{{COMPILER}}_VERSION' in '.vars'-field in your presets.local.json")
                sys.exit(1)
            version = VARS[compver]['github_ci']

            try:
                text = run_from_file(script)
                step["run"] += text

            except (AttributeError, IndexError):
                gcstout(f"-- ERROR: non-valid version for '{script}'-script ({version}). Aborting")
                sys.exit(2)

            except FileNotFoundError:
                gcstout(f"-- ERROR: '{script}'-script was not found in '{gcst.paths.ghci_dir/"scripts"}'-directory. Aborting")
                sys.exit(3)
                

        step["run"] = lss(step["run"])
        del step["run-files"]
        preset_steps.append(step)

    out_matrix.append(matrix_preset)
    out_steps.extend(preset_steps)


def presets_read(presets_file, presets_local_file):
    gcstout(f"Reading presets from basic JSON: \"{presets_file.relative_to(gcst.paths.repo)}\"")
    with open(presets_file, "r", encoding = "utf-8") as f:
        presets = json.load(f)

    service = list(key for key in presets if key.startswith("."))
    if len(service) > 0:
        gcstout(f"-- Service elements found:")
        for element in service:
            gcstout(f"-- -- {element}")
    if len(presets.keys()) > len(service):
        gcstout(f"-- Presets found:")
        for element in presets:
            if not element.startswith('.'):
                gcstout(f"-- -- {element}")

    if not presets_local_file.exists() or ignore_local_presets():
        return presets

    gcstout(f"Overriding JSON has been found")
    gcstout(f"Reading presets from overriding JSON: \"{presets_local_file.relative_to(gcst.paths.repo)}\"")
    with open(presets_local_file, "r", encoding = "utf-8") as f:
        local_presets = json.load(f)
    service = list(key for key in presets if key.startswith("."))

    for key in local_presets:
        value = local_presets[key]

        if key == ".import":
            if (type(value) != list):
                if (type(value) != str):
                    gcstout(f"-- WARN: \".import\"-key contains invalid data (list and str only allowed)")
                    continue
                gcstout(f"-- WARN: \".import\"-key contains str-value, processing it as regular expression")

                pattern = re.compile(value)
                presets = {key: presets[key] for key in presets if (pattern.search(key) or key.startswith('.'))}
            else:
                presets = {key: presets[key] for key in (service + value)}

            gcstout(f"-- Imported presets from basic JSON:")
            for key in presets:
                gcstout(f"-- -- {key}")
            continue

        if key == ".remove":
            removed = value
            if (type(value) != list):
                if (type(value) != str):
                    gcstout(f"-- WARN: \".remove\"-key contains invalid data (list and str only allowed)")
                    continue
                gcstout(f"-- WARN: \".remove\"-key contains str-value, processing it as regular expression")

                pattern = re.compile(value)
                removed = [key for key in presets if (pattern.search(key) and not key.startswith('.'))]

            gcstout(f"-- Removed presets from basic JSON:")
            for preset_name in removed:
                gcstout(f"-- -- {preset_name}")
                del presets[preset_name]
            continue

        if key in presets:
            if ".merge" in local_presets[key] and local_presets[key][".merge"] == True:
                gcstout(f"-- Overrided preset (merged) \"{key}\"")
                presets[key] = deep_merge(presets[key], local_presets[key])
                continue
            gcstout(f"-- Overrided preset (rebased) \"{key}\"")
        else:
            gcstout(f"-- Added preset \"{key}\"")
        presets[key] = local_presets[key]


    gcstout(f"Found {len(presets) - len(service)} presets")
    return presets


def presets_extract(presets, cmake_out, conan_out, out_ghci_steps, out_ghci_matrix):
    gcstout()
    gcstout("Extracting CMake, conan and GitHub CI profiles from detected presets:")
    for key in presets:
        if key.startswith("."):
            if key == ".vars":
                global VARS
                VARS = presets[key]
                gcstout(f"-- Added global vars:")
                additional_vars = {}
                for key in VARS:
                    if key.lower().endswith("version"):
                        buf = {}
                        key_fv = f'{key[:-8]}_FULL_VERSION'
                        key_mv = f'{key[:-8]}_MAJOR_VERSION'
                        buf[f'{key_fv}_LOCAL'] = VARS[key]['local']
                        buf[f'{key_fv}_GITHUB_CI'] = VARS[key]['github_ci']
                        buf[f'{key_mv}_LOCAL'] = gcst.versions(VARS[key]['local']).major
                        buf[f'{key_mv}_GITHUB_CI'] = gcst.versions(VARS[key]['github_ci']).major
                        for key in buf:
                            gcstout(f"-- -- {key}: {buf[key]}")
                        additional_vars.update(buf)
                        continue
                    gcstout(f"-- -- {key}: {VARS[key]}")
                VARS.update(additional_vars)
            continue
        gcstout(f"-- {key}")
        preset = presets[key]
        cmake_preset_process(key, preset, cmake_out)
        conan_preset_process(key, preset, conan_out)
        githubci_preset_process(key, preset, out_ghci_steps, out_ghci_matrix)


def presets_write(cmake_presets, conan_profiles, github_ci):
    if not getArgs().no_cmake:
        cmake_presets_file = gcst.paths.repo/'CMakePresets.json'
        gcstout()
        gcstout(f"Saved CMake presets into \"{cmake_presets_file.relative_to(gcst.paths.repo)}\"")
        with open(cmake_presets_file, 'w', encoding = 'utf-8') as f:
            json.dump(cmake_presets, f, indent = 4)

    if not getArgs().no_conan:
        conan_profiles_dir = gcst.paths.repo/'conan'/'profiles'
        gcstout(f"Saved conan profiles:")
        shutil.rmtree(conan_profiles_dir, ignore_errors = True)
        os.makedirs(conan_profiles_dir, exist_ok = True)
        for key in conan_profiles:
            profile_path = conan_profiles_dir/key
            gcstout(f"-- ./{profile_path.relative_to(gcst.paths.repo)}")
            with open(profile_path, 'w', encoding = 'utf-8') as f:
                f.write(conan_profiles[key])

    if not getArgs().no_ghci:
        github_ci_file = gcst.paths.repo/".github"/"workflows"/"ci.yml"
        with open(github_ci_file, "w", encoding = "utf-8") as f:
            yaml.dump(github_ci, f)
        gcstout(f"Saved GitHub CI workflows into \"{github_ci_file.relative_to(gcst.paths.repo)}\"")


def main():
    print(" ========================> GCST_TEMPLATE_CONFIGURE <========================")
    presets_file = gcst.path/"presets.json"
    presets_local_file = getArgs().presets_local
    if presets_local_file == None:
        presets_local_file = gcst.paths.repo/"presets.local.json"
    presets_local_file = Path(presets_local_file).resolve()

    presets = presets_read(presets_file, presets_local_file)
    with open(os.path.join(gcst.paths.repo, ".github", "workflows", "ci.yml"), "r", encoding = "utf-8") as f:
        github_ci = yaml.load(f)

    github_ci["jobs"]["build"]["strategy"]["matrix"]["include"] = []
    matrix = github_ci["jobs"]["build"]["strategy"]["matrix"]["include"]
    steps = github_ci["jobs"]["build"]["steps"] = presets[".common-pre"]

    presets_extract(presets, CMAKE_PRESETS, CONAN_PROFILES, steps, matrix)
    steps.append({"name": "Build", "run": "${{ matrix.build }} --preset ${{ matrix.preset }}"})
    steps.extend(presets[".common-post"])

    presets_write(CMAKE_PRESETS, CONAN_PROFILES, github_ci)
    gcstout()
    gcstout("Configuring done.")
    print(" ===========================================================================")

if __name__ == '__main__':
    main()
import os
import sys
import gcst
import json
import shutil
import argparse
import subprocess
from pathlib import Path

# TODO: auto-detect preset

args = None
conf_args = []
updater_args = []
cmake_cxx_flags = []

def parseArgs(subscripts = 'all'):
    global cmake_cxx_flags
    global args, conf_args, updater_args

    if args or conf_args or updater_args:
        return

    argvParser = argparse.ArgumentParser(prog = 'gcst-builder')
    argvParser.add_argument('-p', '--preset', default = None)
    argvParser.add_argument('-c', '--clear', action = 'store_true')
    argvParser.add_argument('-v', '--verbose', action = 'store_true')
    argvParser.add_argument('-u', '--update', action = 'store_true')
    argvParser.add_argument('-d', '--debug', action = 'store_true')
    argvParser.add_argument('-ft', '--ftime-trace', action = 'store_true')
    argvParser.add_argument('-bs', '--build-samples', action = 'store_true')
    argvParser.add_argument('-prl', '--parallel', default = os.cpu_count())

    conf_args.append(argvParser.add_argument('-pl', '--presets-local', default = None))
    conf_args.append(argvParser.add_argument('-il', '--ignore-local', action = 'store_true'))

    conf_args.append(argvParser.add_argument('--no-cmake', action = 'store_true'))
    conf_args.append(argvParser.add_argument('--no-conan', action = 'store_true'))
    conf_args.append(argvParser.add_argument('--no-ghci', action = 'store_true'))

    updater_args.append(argvParser.add_argument('--local', action = 'store_true'))

    args = argvParser.parse_args()
    if args.preset == None:
        args.preset = getDefaultPreset()

    cmake_cxx_flags.extend([
        ['-ftime-trace', args.ftime_trace],
    ])


def getDefaultPreset():
    if not gcst.paths.default_preset.exists():
        return None
    
    with open(gcst.paths.default_preset, 'r', encoding = 'utf-8') as f:
        return f.read()

def setDefaultPreset(preset):
    with open(gcst.paths.default_preset, 'w', encoding = 'utf-8') as f:
        return f.write(preset)

    
def clear_build_dir():
    shutil.rmtree(gcst.paths.bin_dir, ignore_errors = True)
    shutil.rmtree(gcst.paths.build_dir, ignore_errors = True)
    print("Build directories cleared")


def gcst_configure():
    command = [sys.executable, gcst.paths.configure_py]
    command.extend(gcst.service.extract_args(args, conf_args))

    return subprocess.run(command, check = False)


def gcst_update():
    if not gcst.paths.update_py:
        return 1
    
    command = [sys.executable, gcst.paths.update_py]
    command.extend(gcst.service.extract_args(args, updater_args))

    env = os.environ.copy()
    env["PYTHONPATH"] = str(gcst.paths.submodule/".gcst") + os.pathsep + env["PYTHONPATH"]
    return subprocess.run(command, check = False, env=env)


def conan_find_version(lib_name, dict_responce = None):
    if not dict_responce:
        command = ["conan", "inspect", gcst.paths.repo, "--format=json"]
        text_responce = subprocess.check_output(command, text = True).strip()
        dict_responce = json.loads(text_responce)

    for lib in dict_responce["requires"]:
        pos_slash = lib["ref"].find("/")
        if lib["ref"][:pos_slash] == lib_name:
            return lib["ref"][pos_slash+1:]

def conan_export_recipes():
    recipes = gcst.paths.repo/"recipes"
    if not recipes.is_dir():
        return 0
    
    result = None
    command = ["conan", "inspect", gcst.paths.repo, "--format=json"]
    dict_inspect = json.loads(subprocess.check_output(command, text = True).strip())

    for rec in recipes.iterdir():
        version = conan_find_version(rec.name, dict_responce = dict_inspect)
        if version == None:
            continue
        
        command = ["conan", "export", rec.resolve(), f"--version={version}"]
        result = subprocess.run(command, check = False)
        if result.returncode != 0:
            break

    return result
    
def conan_install(profile):
    command = [
        "conan",
        "install",
        gcst.paths.repo,
        "--format=json",
        f"--profile={profile}",
        f"--output-folder={gcst.paths.build_dir}",
        f"--out-file={gcst.paths.build_dir / 'graph.json'}",
        "--build=missing",
        "-c", "tools.system.package_manager:mode=install",
        "-c", "tools.system.package_manager:sudo=True",
        "-s", f"build_type={'Debug' if args.debug else 'Release'}"
    ]

    msvc_path = gcst.versions.msvc_path()
    if msvc_path:
        command.extend(["-c", f"tools.microsoft.msbuild:installation_path={msvc_path}"])
    return subprocess.run(command, check = False)

    
def cmake(preset):
    env = os.environ.copy()
    env['CXXFLAGS'] = " ".join([arg[0] for arg in cmake_cxx_flags if arg])

    command = ["cmake"]
    if preset == ".default":
        command.extend(["-B", gcst.paths.build_dir, "-S", gcst.paths.repo])
    else:
        command.extend(["--preset", preset])

    command.append(f"-DGCST_WARNINGS_AS_ERRORS={os.environ['GCST_WERROR']}")
    command.append(f"-DCMAKE_BUILD_TYPE={'Debug' if args.debug else 'Release'}")

    build_samples_env = True if ("GCST_SAMPLES_BUILD" not in os.environ.copy() or os.environ['GCST_SAMPLES_BUILD'] == 'ON') else False
    command.append(f"-DGCST_SAMPLES_BUILD={"ON" if (args.build_samples or build_samples_env) else "OFF"}")
    return subprocess.run(command, cwd = gcst.paths.repo, check = False, env = env)

    
def cmake_build():
    env = os.environ.copy()
    env['TERM'] = 'dumb'
    env['CLICOLOR_FORCE'] = '1'
    command = ["cmake", "--build", gcst.paths.build_dir, '--config']
    command.append('Debug' if args.debug else 'Release')
    command.extend(['--parallel', str(args.parallel)])
    if args.verbose:
        command.extend([
            '--verbose'
        ])
    return subprocess.run(command, check = False, env = env)
        

def main():
    parseArgs()
    if args.update:
        if not args.local and gcst.submodule_update():
            return 1

        result = gcst_update()
        if isinstance(result, int):
            print(f"update failed with code {result}: No submodule detected")
            return 1
        
        if result.returncode != 0:
            print(f"Update failed with code {result.returncode}")
            print("Executed command:\n", *result.args)
            return 1

        return 0
            
    clear = args.clear
    preset = args.preset
    if not preset:
        print("Build-preset was not specified, but no default preset is set. Aborting")
        return 2

    if clear:
        clear_build_dir()
    os.makedirs(gcst.paths.build_dir, exist_ok = True)

    
    
    result = gcst_configure()
    if result.returncode != 0:
        print(f"Configure failed with code {result.returncode}")
        print("Executed command:\n", *result.args)
        return 3

    if not args.no_conan:
        conan_dir = gcst.paths.repo/"conan"/"profiles"
        conan_profile = conan_dir/preset
        if not conan_profile.exists():
            print(f"No specified build-preset ({preset}) was found. Aborting")
            return 4

        setDefaultPreset(preset)

        result = conan_export_recipes()
        if result not in [None, 0] and result.returncode != 0:
            print(f"Conan export recepies failed with code {result.returncode}")
            print("Executed command:\n", *result.args)
            return 5

        result = conan_install(conan_profile)
        if result.returncode != 0:
            print(f"Conan install failed with code {result.returncode}")
            print("Executed command:\n", *result.args)
            return 6

    if not args.no_cmake:
        result = cmake(preset)
        if result.returncode != 0:
            print("Executed command:\n", *result.args)
            return 7
        
        result = cmake_build()
        if result.returncode != 0:
            print("Executed command:\n", *result.args)
            return 8

    return 0

if __name__ == "__main__":
    sys.exit(main())
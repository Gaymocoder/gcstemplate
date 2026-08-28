import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
root_path = Path(subprocess.check_output(['git', '-C', HERE, 'rev-parse', '--show-toplevel'], text = True).strip()).absolute()

bin_dir = root_path/"bin"
gcst_dir = root_path/".gcst"
build_dir = root_path/"build"
configure_py = gcst_dir/"scripts"/"configure.py"

defaultPreset = ".default"
defaultPresetPath = gcst_dir/".default"

# TODO: default preset
# TODO: auto-detect preset

def getArgs():
    argvParser = argparse.ArgumentParser(prog = 'gcst-builder')
    argvParser.add_argument('-p', '--preset')
    argvParser.add_argument('-c', '--clear', action = 'store_true')
    argvParser.add_argument('-il', '--ignore-local', action = 'store_true')
    args = argvParser.parse_args()
    if args.preset == None:
        args.preset = getDefaultPreset()
    return args


def getDefaultPreset():
    if not defaultPresetPath.exists():
        return None
    
    with open(defaultPresetPath, 'r', encoding = 'utf-8') as f:
        return f.read()

def setDefaultPreset(preset):
    with open(defaultPresetPath, 'w', encoding = 'utf-8') as f:
        return f.write(preset)

    
def clear_build_directory():
    shutil.rmtree(bin_dir, ignore_errors = True)
    shutil.rmtree(build_dir, ignore_errors = True)
    print("Build directories cleared")


def gcst_configure():
    command = [sys.executable, configure_py]
    ignore_local = getArgs().ignore_local
    if ignore_local:
        command.append('--ignore-local')

    return subprocess.run(command, check = False)

    
def conan_install(profile):
    command = [
        "conan",
        "install",
        root_path,
        f"--profile={profile}",
        f"--output-folder={build_dir}",
        "--build=missing"
    ]
    return subprocess.run(command, check = False)

    
def cmake(preset):
    command = ["cmake"]
    if preset == ".default":
        command.extend(["-B", build_dir, "-S", root_path])
    else:
        command.extend(["--preset", preset])
    command.append(f"-DGCST_WARNINGS_AS_ERRORS={os.environ['GCST_WERROR']}")
    return subprocess.run(command, cwd = root_path, check = False)

    
def cmake_build():
    command = ["cmake", "--build", build_dir, '--config', 'Release']
    return subprocess.run(command, check = False)
        

def main():
    args = getArgs()
    clear = args.clear
    preset = args.preset
    if not preset:
        print("Build-preset was not specified, but no default preset is set. Aborting")
        return 1

    if clear:
        clear_build_directory()
    os.makedirs(build_dir, exist_ok = True)
    
    result = gcst_configure()
    if result.returncode != 0:
        print(f"Configure failed with code {result.returncode}")
        print("Executed command:\n", *result.args)
        return 2

    conan_dir = root_path/"conan"/"profiles"
    conan_profile = conan_dir/preset
    if not conan_profile.exists():
        print(f"No specified build-preset ({preset}) was found. Aborting")
        return 3

    setDefaultPreset(preset)
    result = conan_install(conan_profile)
    if result.returncode != 0:
        print(f"Conan install failed with code {result.returncode}")
        print("Executed command:\n", *result.args)
        return 4
    
    result = cmake(preset)
    if result.returncode != 0:
        print("Executed command:\n", *result.args)
        return 5
    
    result = cmake_build()
    if result.returncode != 0:
        print("Executed command:\n", *result.args)
        return 6

    return 0

if __name__ == "__main__":
    sys.exit(main())
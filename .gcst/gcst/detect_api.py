import os
import sys
import json
import subprocess

from pathlib import Path

def __verinit(cls):
    pf86_path = os.environ.get("ProgramFiles(x86)")
    if pf86_path:
        vswhere = Path(pf86_path)/"Microsoft Visual Studio"/"Installer"/"vswhere.exe"
        if vswhere.exists():
            cls.vswhere = vswhere

    return cls

@__verinit
class versions:
    vswhere = None

    def __new__(cls, fullver: str):
        for char in fullver:
            if char not in ['v', '.']:
                break
            fullver = fullver[1:]

        if fullver.replace('.', '').isdigit():
            return super().__new__(cls)
        return None

    def __init__(self, fullver: str):
        self._fullver = fullver

    @property
    def full(self):
        return self._fullver

    @property
    def major(self):
        mjend = self._fullver.find('.')
        if mjend == -1:
            return self._fullver
        return self._fullver[:mjend]

    @property
    def minor(self):
        mnbegin = self._fullver.find('.') + 1
        mnend = self._fullver.find('.', mnbegin)
        if mnend == -1:
            mnend = len(self._fullver)
        return self._fullver[mnbegin:mnend]

    @classmethod
    def clang(cls):
        pass

    @classmethod
    def gcc(cls):
        pass

    @classmethod
    def mingw(cls):
        pass

    @classmethod
    def msvc(cls):
        pass

    @classmethod
    def msvc_path(cls):
        if not cls.vswhere:
            return None

        vs_path = subprocess.check_output([
            cls.vswhere,
            "-latest",
            "-products", "*",
            "-property", "installationPath",
            "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
        ], text = True).strip()

        if not vs_path:
            return None
        return Path(vs_path).resolve()

    @classmethod
    def clang_cl(cls):
        pass
        
def main():
    versions.gcc()
    versions.clang()
    
if __name__ == "__main__":
    sys.exit(main())
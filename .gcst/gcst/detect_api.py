import os
import sys
import json
import subprocess

class versions:
    def __new__(cls, fullver):
        if fullver.replace('.', '').isdigit():
            return super().__new__(cls)
        return None

    def __init__(self, fullver):
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
    def clang_cl(cls):
        pass
        
def main():
    versions.gcc()
    versions.clang()
    
if __name__ == "__main__":
    sys.exit(main())
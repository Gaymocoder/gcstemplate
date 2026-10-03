from .constants import paths

import subprocess

class _Service:
    def submodule_update(self):
        if not paths.submodule:
            print(f"Failed to update gcstemplate submodule: submodule's not found")
            return 1
        
        result = subprocess.run(["git", "-C", paths.srepo, "submodule", "update", "--remote", "--merge", paths.submodule], check = False)
        if result.returncode:
            print(f"Failed to update gcstemplate submodule: git returned code {result.returncode}")
            return result.returncode
        
        return 0

    def extract_args(self,argssource, argslist):
        out = []
        for arg in argslist:
            value = getattr(argssource, arg.dest)
            if value is None or value is False:
                continue

            out.append(arg.option_strings[0])
            if arg.nargs == 0:
                continue
            
            if isinstance(value, (list, tuple)):
                out.extend(str(v) for v in value)
            else:
                out.append(str(value))

        return out

service = _Service()
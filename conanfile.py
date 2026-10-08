import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".gcst"))

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps

from gcst_conan_deps import gcstDeps

class gcstConan(gcstDeps):
    settings = "os", "arch", "compiler", "build_type"

    default_options = {
        **gcstDeps.default_options,
        "boost/*:header_only": True
    }

    requires = (
        *gcstDeps.requires,
        "boost/1.87.0"
    )

    def generate(self):
        CMakeToolchain(self).generate()
        CMakeDeps(self).generate()
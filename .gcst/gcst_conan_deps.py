from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps

class gcstDeps(ConanFile):
    default_options = {
        "cli11/*:header_only": False
    }

    requires = (
        "cli11/[>=2.7.2]",
    )
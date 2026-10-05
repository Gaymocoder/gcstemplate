from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps

class gcstConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    default_options = {
        "boost/*:header_only": True,
        "cli11/*:header_only": False
    }

    requires = (
        "boost/1.87.0",
        "cli11/[>=2.7.2]"
    )

    def generate(self):
        CMakeToolchain(self).generate()
        CMakeDeps(self).generate()
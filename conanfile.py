from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps

class gcstConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    default_options = {"boost/*:header_only": True}

    requires = (
        "boost/1.87.0"
    )

    def generate(self):
        CMakeToolchain(self).generate()
        CMakeDeps(self).generate()
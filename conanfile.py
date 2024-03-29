import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy
from conan.tools.scm import Version

from version import get_version


class FuncGenConan(ConanFile):
    name = "func-gen"
    version = get_version()

    # Optional metadata
    license = "Apache-2.0"
    homepage = "https://github.com/QuTech-Delft/func-gen"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Generator of functions usable within cQASM."
    topics = "code generation"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "asan_enabled": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "asan_enabled": False
    }

    exports = "version.py", "include/version.hpp"
    exports_sources = "CMakeLists.txt", "cmake/*", "include/*", "src/*"

    def set_version(self):
        self.version = get_version()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        self.folders.source = "."
        self.folders.build = os.path.join("build", str(self.settings.build_type))
        self.folders.generators = os.path.join(self.folders.build, "generators")

        self.cpp.package.libs = ["func-gen"]
        self.cpp.package.includedirs = ["include"]

        self.cpp.source.includedirs = ["include"]

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["ASAN_ENABLED"] = self.options.asan_enabled
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def validate(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        if compiler == "apple-clang":
            if version < "14":
                raise ConanInvalidConfiguration("func-gen requires at least apple-clang++ 14")
        elif compiler == "clang":
            if version < "13":
                raise ConanInvalidConfiguration("func-gen requires at least clang++ 13")
        elif compiler == "gcc":
            if version < "10.0":
                raise ConanInvalidConfiguration("func-gen requires at least g++ 10.0")
        elif compiler == "msvc":
            if version < "19.29":
                raise ConanInvalidConfiguration("func-gen requires at least msvc 19.29")
        else:
            raise ConanInvalidConfiguration("Unsupported compiler")
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

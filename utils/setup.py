from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize


class BuildExt(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type == "msvc":
            args = ["/O2"]
        else:
            args = ["-O3"]
        for ext in self.extensions:
            ext.extra_compile_args = args
        super().build_extensions()


# python setup.py build_ext --inplace
ext = Extension("_lz77", sources=["_lz77.pyx"])

setup(
    name="lz77",
    cmdclass={"build_ext": BuildExt},
    ext_modules=cythonize(
        [ext],
        language_level=3,
        compiler_directives={
            "boundscheck": False,
            "wraparound": False,
        },
    ),
)

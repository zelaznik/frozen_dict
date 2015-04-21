from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "frozen_dict",
    ext_modules = cythonize("frozen_dict.pyx")
)
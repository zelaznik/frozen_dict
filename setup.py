from distutils.core import setup
from Cython.Build import cythonize

from distutils.core import setup
from distutils.extension import Extension

if 3/2 == 1.5:
    version = 3
else:
    version = 2

if version == 3:
    setup(
        ext_modules = [Extension('frozen_dict', ['frozen_dict_py3.c'])]
    )
else:
    setup(
        ext_modules = [Extension('frozen_dict', ['frozen_dict_py2.c'])]
    )

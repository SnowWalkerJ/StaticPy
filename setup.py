import os
import numpy as np
from setuptools import find_packages, Extension

with open(os.path.join(os.path.dirname(__file__), 'staticpy/VERSION')) as f:
    version = f.read().strip()


def resolve_requirements():
    requirements = []
    with open('requirements.txt') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line.strip("\n"))
    return requirements


setup_args = dict(
    name='StaticPy',
    version=version,
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test", "scripts", "private", "tests"]),
    install_requires=resolve_requirements(),
    include_package_data=True,
    url='https://www.github.com/SnowWalkerJ/StaticPy',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',

        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**setup_args)
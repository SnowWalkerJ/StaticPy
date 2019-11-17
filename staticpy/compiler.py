import os
import sys
import shutil
import platform

import jinja2

from .session import new_session
from .util.string import get_target_filepath
from .common import logging
from .lang import macro as M, statement as S, block as B

from .lang.common import get_block_or_create


class Compiler:
    def __init__(self):
        self.templates = []

    def add_template(self, suffix, template):
        self.templates.append((suffix, template))

    @staticmethod
    def ensure_build_path(target_path):
        build_path = os.path.join(target_path, "build")
        if not os.path.exists(build_path):
            os.makedirs(build_path)
        return build_path

    def run(self, session, target_path, libname):
        build_path = self.ensure_build_path(target_path)
        libname = libname
        sources = []
        with session:
            for suffix, template in self.templates:
                target_filename = os.path.join(build_path, libname + suffix)
                source = template.render(session)
                with open(target_filename, "w") as f:
                    f.write(source)
                sources.append(target_filename)
        self.compile(target_path, libname, sources)

    def compile(self, target_path, libname, sources):
        sources = " ".join(sources)
        includes = get_include_path()
        output_filename = get_target_filepath(target_path, libname)
        command = f"c++ -O3 -Wall -shared -std=c++11 -fPIC {includes} {sources} -o {output_filename}"
        if platform.system() == "Darwin":
            command += " -undefined dynamic_lookup"
        logging.info(command)
        os.system(command)


def get_include_path():
    with os.popen("python3 -m pybind11 --includes") as f:
        includes = f.read().strip("\n")
    path = os.path.dirname(__file__)
    includes += " -I" + os.path.join(path, "cpp", "header")
    return includes

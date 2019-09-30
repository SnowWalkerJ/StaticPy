import os
import sys
import shutil
import platform

import jinja2

from .session import new_session
from .lang import macro as M, statement as S, block as B


from .lang.common import get_block_or_create
from .lang import macro as M


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
        suffix = os.popen("python3-config --extension-suffix")._stream.read().strip("\n")
        includes = os.popen("python3 -m pybind11 --includes")._stream.read().strip("\n")
        output_filename = os.path.join(target_path, libname + suffix)
        command = f"c++ -O3 -Wall -shared -std=c++11 -fPIC {includes} {sources} -o {output_filename}"
        if platform.system() == "Darwin":
            command += " -undefined dynamic_lookup"
        print(command)
        os.system(command)

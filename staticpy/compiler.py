import os
import sys
import shutil
import platform

import jinja2

from .session import new_session
from .language import macro as M, statement as S, block as B


class Compiler:
    def __init__(self):
        self.blocks = {}
        self.session = new_session()
        self.templates = []
        self._pybind = False

    def add_template(self, suffix, template):
        self.templates.append((suffix, template))

    def get_block(self, name):
        return self.blocks[name][0]

    def register_block(self, name, level=0):
        with self.session:
            block = B.EmptyBlock()
        self.blocks[name] = (block, level)
        return block

    def enable_pybind(self):
        self._pybind = True

    def disable_pybind(self):
        self._pybind = False

    def setup(self, target):
        with self.session:
            for _, template in self.templates:
                template.setup_before(self, self.session)
            if self._pybind:
                self.get_block("header").add_statement(M.defineM("PYBIND"))
            target(self, self.session)
            for _, template in self.templates:
                template.setup_after(self, self.session)

    @staticmethod
    def ensure_build_path(target_path):
        build_path = os.path.join(target_path, "build")
        if not os.path.exists(build_path):
            os.makedirs(build_path)
        return build_path

    def run(self, target, target_path, libname=None):
        build_path = self.ensure_build_path(target_path)
        libname = libname   # or get_libname(target)
        self.setup(target)
        sources = []
        with self.session:
            for suffix, template in self.templates:
                target_filename = os.path.join(build_path, libname + suffix)
                source = template.render(self.blocks, libname)
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

    def __enter__(self):
        return self.session.__enter__()

    def __exit__(self, *args):
        return self.session.__exit__(*args)

Introduction
============

StaticPy is a Python-to-C++ translater. It is designed in a way that code can be run in both Python and C++ mode. That is,
StaticPy valid code should be able to not only be translated to C++ and compiled, but
also run by Python interpreter directly.

It supports a subset of Python grammar. It analyzes Python AST and translates it to C++.
You can write a C++ template and embed the generated code in your template to form a complete code.

Optionally, it can bind the C++ code back to Python using Pybind11 to grant super speed to Python.

Compare to alternatives
-----------------------

Compare to Cython
~~~~~~~~~~~~~~~~~

Cython has the advantage of being very flexible. It translates everything static enough to C and leave the rest as it is.
By doing that, it allows you to enjoy both the flexibility of Python and fastness of C.
StaticPy, however, requires you use only supported grammar(only static-typed variables, for example).
The good thing about it is that it can generate pure C++ code without support of Python, so that you can embed the code to
a C++ project.

Another difference is that Cython compiles the source code in a static way. It analyzes the source code and translates it to C.
An explicit compilation is necessary before you can use the generated module. StaticPy is more like numba in a way that
only a decorator around the function and everything is done.

Compare to numba
~~~~~~~~~~~~~~~~

StaticPy supports C++ better than numba. You can include outside sources and use C++ functions/class directly with
StaticPy.

In order to generate pure C++ code, numpy is not supported by StaticPy, which is a huge disadvantage compared to numba.

In addition, the compiling time of StaticPy seems much longer.
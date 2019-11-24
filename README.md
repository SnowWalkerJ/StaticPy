# StaticPy

![badge](https://github.com/SnowWalkerJ/StaticPy/workflows/Python%20package/badge.svg)

StaticPy is a Python-to-C++ translater.

It supports a subset of Python grammar. It analyzes Python bytecode of a function and translates it to C++.
You can write a C++ template and embed the generated code in your template to form a complete code.

Optionally, it can bind the C++ code back to Python using Pybind11 to grant super speed to Python.

## Compare to alternatives

### Compare to Cython

Cython has the advantage of being very flexible. It translates everything static enough to C and leave the rest as it is.
By doing that, it allows you to enjoy both the flexibility of Python and fastness of C.
StaticPy, however, requires you use only supported grammar(only static-typed variables, for example).
The good thing about it is that it can generate pure C++ code without support of Python, so that you can embed the code to
a C++ project.

Another difference is that Cython compiles the source code in a static way. It analyzes the source code and translates it to C.
An explicit compilation is necessary before you can use the generated module. StaticPy is more like numba in a way that
only a decorator around the function and everything is done.

### Compare to numba

StaticPy supports C++ better than numba. You can include outside sources and use C++ functions/class directly with
StaticPy.

In order to generate pure C++ code, numpy is not supported by StaticPy, which is a huge disadvantage compared to numba.

In addition, the compiling time of StaticPy seems much longer.

## Usage

```python
from staticpy import jit, Int

@jit
def frac(n: Int) -> Int:
    if n == 0:
        return 1
    else:
        return n * frac(n - 1)

assert frac(5) == 120
```

## Buffer Protocal

Now buffer protocal is supported thanks to pybind11. You can feed a numpy array to a function. StaticPy
will do the right transformation for you. However, only element-wise operations are supported, and you can't
return an array for now. We are planning on removing this restriction soon.

```python
from staticpy import jit, Int

@jit
def sum(numbers: Int[:]):
    i: Int
    s: Int = 0
    for i in range(len(numbers)):
        s += numbers[i]
    return s
```

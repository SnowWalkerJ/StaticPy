User Guide
==========


Declare variable
----------------

Like in C++, each variable must be declare before it's used. Declare a variable using
annotated assignment in StaticPy. Here is an example:

..  code-block:: Python

    variable: int = 0
    # or
    variable: int

The later one declares a variable without intializing it.

Constants
---------

If you assign a variable wihout declaring its type, the variable is considered a python constant.
This constant is like a macro variable in C/C++. The variable itself will never appear in the
generated code. It's replaced with the value it's assigned with. For example,

.. code-block:: python

    zero = 0
    myvar: int = zero + 1

will be translated into:

.. code-block:: c++

    int myvar = 0 + 1;

Types
-----

Primitives
~~~~~~~~~~

Basic types are `Bool`, `Int`, `Long`, `Float` and `Double`, which represents `bool`, `int`, `long`,
`float` and `double` in C++ respectively. If you use Python type `int` and `float`, they are also
mapped to `int` and `float` in C++.

We understand that `int` and `float` in Python actually represents `long` and `double` in C. But we think
it is confusing that `Int` means `int` while `int` means `long`.

Arrays
~~~~~~

Arrays are supported as function parameters (but not return types yet). You can declare an array type by
something like `Int[:]` or `Float[3]`. This is almost like what you would expect in `Numba` or `Cython`.
Array types with provided shapes is appreciated because compiler can take advantage of this information
to optimize the generated code.

Multi-dimensional arrays can be declared with `Long[3, 2]`. 

Just like in `Numba` and `Cython`, a continuous array is much more efficient than a normal array. So if
you are sure an array is continuous, you should annotate it to generate more efficient code. Unlike
`Numba` or `Cython`, which annotate a continuous array with `int[::1]`, `StaticPy` use a bool flag at the
end of the shape annotation. Use `Int[3, 2, True]` to annotate a continuous type with 3x2 elements.
If you feed a non-continuous array to a continuous typed parameter, it may access an invalid memory and cause
error or (worsely) return a wrong result without warnings.

Lists and Dicts
~~~~~~~~~~~~~~~
List and dict are commonly used containers in Python. They have counterparts in C++ as well. Using
them in StaticPy is possible yet not realized. This is one of the most important features we are
currently working on.

Flow Control
------------

Most flow-control statements are supported in StaticPy such as `while`, `if`, `else`. `do-while` is not supported
because it doesn't exist in Python. The `elif` is a little tricky, though. It is translated to `else { if () {}}`.
This is sementically equivalent in C/C++, but not quite human-friendly to read.

Another commonly used feature is `for`. So far only `for x in range(...)` is valid in StaticPy. It is translated into
`for (i = start; i < end; i += step) {}`. A general form of for-each is neither supported nor intend to be supported
in the short term.



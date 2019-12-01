Get Started
===========


Install StaticPy
----------------

.. code-block::
    bash

    git clone https://github.com/SnowWalkerJ/StaticPy.git
    cd StaticPy
    pip install -r requirements.txt
    python setup.py install


Concepts
--------

C++ is a static-type language. Each variable has a type determined at compile time.
StaticPy is not good at deducing the types for you. So if you wish StaticPy to
speedup your code, you have to carefully annotate each variable with proper type.


Using StaticPy
--------------

jit
~~~

One way to use StaticPy to speed up your code is through the `jit` decorator.
You should carefully annotate each variable, parameter and return value.

..  code-block:: python

    from staticpy import jit

    @jit
    def frac(n: int) -> int:
        if n <= 1:
            return 1
        else:
            return n * frac(n - 1)

The function will be compiled the first time it is called. If you wish it to compile immediatelly,
call `frac.compile()`.

A jit function will be re-compiled under the following circumstances:

- the source code of the function is modified since the last compilation
- a `force-compile` option is turned on
- `obj.compile()` is called

Note that a `jit` function is strict on types. You can't pass an int value to a float parameter or a
float value to an int parameter. A manually overloading is needed.


import hook
~~~~~~~~~~~

StaticPy has a import-hook that allows compile a whole module when you import it. Enable it by calling
`import staticpy.hook` before you import any other module.

To specify a module that wishes to be compiled by StaticPy, write a signal `# @staticpy` at the first line of
your module. This signal lets StaticPy know which modules should be compiled.

.. code-block:: python

    # @staticpy
    # mod.py
    # make sure # @staticopy is at the first line

    def frac(n: int) -> int:
        if n <= 1:
            return 1
        else:
            return n * frac(n - 1)

.. code-block:: python

    # main.py
    import staticpy.hook          # Enables compile-at-import
    import mod                    # StaticPy compiles `mod`

    assert mod.frac(4) == 24


Translator
==========

One major goal for StaticPy is to generate pure C++ code. This is done by calling a translator.

.. code-block:: python

    import inspect
    from staticpy.translator import BaseTranslator

    def fn(n: int) -> int:
        s: int = 0
        for i in range(n):
            s += i
        return s

    source = inspect.getsource(fn)
    translator = BaseTranslator()
    block = translator.translate(source)
    
    print("\n".join(block.translate()))


This prints out

.. code-block:: c++

    int fn(int n) {
      int s = 0;
      for(int i = 0; i < n; i++) {
        s += i;
      }
      return s;
    }

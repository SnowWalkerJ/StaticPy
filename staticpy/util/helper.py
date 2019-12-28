class Cls:
    """
    This class is to refer to the "current" class when it hasn't been completely
    defined.

    Example
    =======
    ..  code-block:: python

        class A:
            def __init__(self, value):
                self.value: int = 1

            def __add__(self, other: Cls) -> Cls:
                return A(self.value + othervalue)

    The signature of operator `__add__` means it adds and returns an object of type `A`
    """

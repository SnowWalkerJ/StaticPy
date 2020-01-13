Advanced
========

Syntax Tree
-----------

Variables
~~~~~~~~~

.. code-block::

    Variables = Variable | Name

Expressions
~~~~~~~~~~~

.. code-block::

    Expression = UnaryPositive expression
               | UnaryNegative expression
               | UnaryNot expression
               | UnaryInvert expression
               | BinaryMultiply expression expression
               | BinaryDivide expression expression
               | BinaryModulo expression expression
               | Binary Add expression expression
               | BinarySubtract expression expression
               | BinaryLShift expression expression
               | BinaryRShift expression expression
               | BinaryAnd expression expression
               | BinaryXor expression expression
               | BinaryOr expression expression
               | LogicalAnd expression expression
               | LogicalOr expression expression
               | CompareGT expression expression
               | CompareLT expression expression
               | CompareGE expression expression
               | CompareLE expression expression
               | CompareEQ expression expression
               | CompareNE expression expression
               | AddressOf expression
               | ScopeAnalysis name name
               | IIf expression expression expression
               | CallFunction variable [expression]
               | TemplateInstantiate variable [expression]
               | Const value
               | Var variable
               | GetAttr expression name
               | GetItem expression expression
               | StaticCast expression type
               | Cast expression type
               | initializer_list [expression]

Statements
~~~~~~~~~~

.. code-block::

    Statement = VariableDeclaration variable type
              | UsingNameSpace name
              | SimpleStatement str
              | Assign variable expression
              | SetAttr expression name expression
              | SetItem expression expression expression
              | ReturnValue expression
              | ExpressionStatement expression
              | Continue
              | Break
              | BlockStatement block
              | SingleLineComment comment
              | BlockComment comment
              | InplaceLShift expression expression
              | InplaceRShift expression expression
              | InplaceAdd expression expression
              | InplaceSubtract expression expression
              | InplaceMultiply expression expression
              | InplaceDivide expression expression
              | InplaceModulo expression expression
              | InplaceAnd expression expression
              | InplaceXor expression expression
              | InplaceOr expression expression

Blocks
~~~~~~

Block = EmptyBlock
      | If expression
      | Else
      | For variable expression expression expression
      | While expression
      | Function name [(type, name)] type
      | Class name members
      | AccessBlock name
      | Constructor



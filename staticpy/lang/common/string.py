def stringify_arguments(args):
    from ..expression import cast_value_to_expression
    return ", ".join(map(str, map(cast_value_to_expression, args)))

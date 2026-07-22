def basic_calculate(expression: str) -> str:
    """Evaluates a safe basic arithmetic expression."""
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        return "Error: Invalid characters in arithmetic expression."
    try:
        # pylint: disable=eval-used
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Calculation Error: {e}"

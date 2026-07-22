import cmath
import math

def robo_calculate(expression: str) -> str:
    """Evaluates advanced mathematical and complex number expressions."""
    safe_dict = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "log": math.log,
        "pi": math.pi,
        "e": math.e,
        "phase": cmath.phase,
        "polar": cmath.polar,
        "rect": cmath.rect
    }
    try:
        # pylint: disable=eval-used
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return str(result)
    except Exception as e:
        return f"RoboCalc Error: {e}"

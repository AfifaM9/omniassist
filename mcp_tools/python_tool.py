import sys
import io
import traceback

def run_python(code: str) -> str:
    """Dynamically evaluates a Python code snippet and captures stdout/stderr."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_out = io.StringIO()
    redirected_err = io.StringIO()
    
    sys.stdout = redirected_out
    sys.stderr = redirected_err
    
    try:
        exec(code, {})
        output = redirected_out.getvalue()
        error = redirected_err.getvalue()
        result = output + error
        return result.strip() if result else "Python code executed successfully with no output."
    except Exception:
        return traceback.format_exc()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

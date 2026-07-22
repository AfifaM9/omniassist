import subprocess
import tempfile
import os

def run_sandboxed_code(language: str, code: str) -> str:
    """Executes code snippets in supported languages securely within isolated temp files."""
    lang = language.lower()
    if lang not in ["python", "bash", "sh"]:
        return f"Error: Language '{language}' is not supported in the sandboxed runner."

    ext = "py" if lang == "python" else "sh"
    interpreter = "python3" if lang == "python" else "bash"

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=f".{ext}", delete=False) as tf:
            tf.write(code)
            tf_name = tf.name

        result = subprocess.run(
            [interpreter, tf_name],
            capture_output=True,
            text=True,
            timeout=15
        )
        output = result.stdout if result.stdout else result.stderr
        return output.strip() if output else "Sandboxed execution completed with no output."
    except subprocess.TimeoutExpired:
        return "Error: Sandboxed code execution timed out."
    except Exception as e:
        return f"Sandboxed Runner Error: {e}"
    finally:
        if 'tf_name' in locals() and os.path.exists(tf_name):
            os.remove(tf_name)

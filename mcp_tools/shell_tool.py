import subprocess

def run_shell(command: str) -> str:
    """Executes a system shell command and returns output or error."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout if result.stdout else result.stderr
        return output.strip() if output else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Shell command timed out after 30 seconds."
    except Exception as e:
        return f"Shell Execution Error: {e}"

import os

def read_file(file_path: str) -> str:
    """Reads and returns the contents of a specified file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"File Read Error: {e}"

def write_file(file_path: str, content: str) -> str:
    """Writes content to a specified file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"File Write Error: {e}"

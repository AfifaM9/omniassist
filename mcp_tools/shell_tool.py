import subprocess
import re

SENSITIVE_DIRS = {'/', '/home', '/etc', '/var', '/usr', '/bin', '/sbin', '/lib', '/root', '/tmp', '/boot', '/dev', '/proc', '/sys'}
FORK_BOMB_PATTERNS = [
    r':\(\)\s*\{.*:\s*\|\s*:.*\}',  # :() { :|: };: (fork bomb)
]

def _is_blocked_command(command: str) -> tuple[bool, str]:
    """Check if command is blocked. Returns (is_blocked, reason)."""
    if not command or not command.strip():
        return True, "Empty command"

    command_lower = command.lower()

    # Check for fork bombs (case insensitive, handles newlines)
    for pattern in FORK_BOMB_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE | re.DOTALL):
            return True, "Fork bomb attack detected"

    # Strip sudo prefix to check the underlying command
    command_no_sudo = re.sub(r'^sudo\s+', '', command, flags=re.IGNORECASE)
    command_no_sudo_lower = command_no_sudo.lower()

    # Check for dangerous rm -rf patterns (with or without sudo)
    if 'rm' in command_no_sudo_lower and '-rf' in command_no_sudo_lower:
        # Check for root directory deletion attempts (including -- flag and other flags)
        if re.search(r'rm\s+-rf(\s+-[a-z]+)*(\s+--)?\s+["\']?/["\']?\s*$', command_no_sudo, re.IGNORECASE) or \
           re.search(r'rm\s+-rf(\s+-[a-z]+)*(\s+--)?\s+["\']?/\s+', command_no_sudo, re.IGNORECASE):
            return True, "Refusing to delete root directory"

        # Extract target paths
        targets_match = re.search(r'rm\s+-rf(\s+-[a-z]+)*(\s+--)?\s+(.+?)(?:\s*$|\s+)', command_no_sudo, re.IGNORECASE)
        if targets_match:
            targets_str = targets_match.group(3)
            # Handle ~ (home directory) separately (case insensitive)
            if '~' in targets_str.lower():
                return True, "Refusing to delete home directory (~)"
            # Split targets and check each (case insensitive comparison)
            for target in targets_str.split():
                target = target.strip('"\'')
                target_lower = target.lower()
                for sensitive in SENSITIVE_DIRS:
                    sensitive_lower = sensitive.lower()
                    # Block if target exactly equals sensitive dir (case insensitive)
                    if target_lower == sensitive_lower:
                        return True, f"Refusing to delete sensitive directory ({sensitive})"

    return False, ""

def run_shell(command: str) -> str:
    """Executes a system shell command and returns output or error."""
    is_blocked, reason = _is_blocked_command(command)
    if is_blocked:
        return f"Command blocked: {reason}"

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

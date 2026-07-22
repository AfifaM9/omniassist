class TerminalAdapter:
    """Adapts terminal I/O for external streaming or wrapped interface channels."""
    @staticmethod
    def format_output(text: str) -> str:
        return f"[TerminalAdapter] >>> {text}"

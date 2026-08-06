import sys
import re
import readline
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from core.agent import OmniAssist

console = Console()

QUIT_PATTERN = re.compile(r'^(exit|quit|q)$', re.IGNORECASE)
SLASH_COMMAND_PATTERN = re.compile(r'^/(\w+)')

def show_help():
    """Display help information for available commands."""
    console.print(Panel.fit(
        "[bold cyan]OmniAssist Commands[/bold cyan]\n"
        "[italic]Type a slash command or chat normally with the agent.[/italic]",
        border_style="cyan"
    ))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", width=15)
    table.add_column("Description")
    
    table.add_row("/help", "Show this help message")
    
    console.print(table)
    console.print()

def main():
    """Interactive CLI rendering responses cleanly using Rich Markdown panels."""
    console.print(Panel.fit(
        "[bold cyan]OmniAssist[/bold cyan]\n"
        "[italic]Operationalized Multi-Agent Networked Intelligence & "
        "Autonomous System Services Integration Toolkit (2026.3)[/italic]",
        border_style="cyan"
    ))
    console.print("[dim]Type '/help' for commands or 'exit', 'quit', 'q' to terminate session.[/dim]\n")
    
    try:
        agent = OmniAssist()
    except Exception as e:
        console.print(f"[bold red]Initialization Error:[/bold red] {e}")
        sys.exit(1)

    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ").strip()
            if not user_input:
                continue
            if QUIT_PATTERN.match(user_input):
                console.print("[yellow]Exiting OmniAssist CLI. Goodbye![/yellow]")
                break
            
            # Check for slash commands
            slash_match = SLASH_COMMAND_PATTERN.match(user_input)
            if slash_match:
                command = slash_match.group(1).lower()
                if command == "help":
                    show_help()
                    continue
                else:
                    console.print(f"[yellow]Unknown command: /{command}. Type '/help' for available commands.[/yellow]\n")
                    continue
            
            response = agent.run(user_input)
            
            # Restored full Rich Markdown panel rendering for agent outputs
            console.print(Panel(
                Markdown(str(response)),
                title="[bold cyan]OmniAssist[/bold cyan]",
                border_style="blue",
                expand=False
            ))
            console.print()
            
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Session interrupted. Type '/help' for commands or 'exit', 'quit', 'q' to quit properly.[/yellow]")
            continue
        except Exception as cli_err:
            console.print(f"\n[bold red]CLI Trapped Error:[/bold red] {cli_err}\n")
            continue

if __name__ == "__main__":
    main()

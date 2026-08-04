import sys
import readline
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from core.agent import OmniAssist

console = Console()

def main():
    """Interactive CLI rendering responses cleanly using Rich Markdown panels."""
    console.print(Panel.fit(
        "[bold cyan]OmniAssist[/bold cyan]\n"
        "[italic]Operationalized Multi-Agent Networked Intelligence & "
        "Autonomous System Services Integration Toolkit (2026.2)[/italic]",
        border_style="cyan"
    ))
    console.print("[dim]Type 'exit' or 'quit' to terminate session.[/dim]\n")
    
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
            if user_input.lower() in ["exit", "quit"]:
                console.print("[yellow]Exiting OmniAssist CLI. Goodbye![/yellow]")
                break
            
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
            console.print("\n[yellow]Session interrupted. Type 'exit' to quit properly.[/yellow]")
            continue
        except Exception as cli_err:
            console.print(f"\n[bold red]CLI Trapped Error:[/bold red] {cli_err}\n")
            continue

if __name__ == "__main__":
    main()

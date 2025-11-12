from __future__ import annotations

import sys
from pathlib import Path

import typer
import uvicorn
from rich.console import Console

console = Console()
cli = typer.Typer(help="Herramienta de línea de comandos para ABPM Analyzer")

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@cli.command()
def serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Inicia el servidor FastAPI con Uvicorn."""

    from app.main import app

    console.print(f"[bold cyan]Iniciando servidor en http://{host}:{port} ...[/bold cyan]")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    cli()

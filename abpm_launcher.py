"""Herramienta de línea de comandos para ejecutar el flujo ABPM.

Este módulo expone comandos sencillos pensados para entornos sin
experiencia previa. Se encarga de inicializar la base de datos,
crear usuarios y arrancar el servidor FastAPI que expone la API web.

También incluye un comando `analyze` que permite verificar rápidamente
la extracción y el diagnóstico a partir de un PDF sin necesidad de la
interfaz web. El script se puede invocar directamente con Python y es
compatible con herramientas como PyInstaller para generar un
ejecutable autónomo.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.table import Table


# Aseguramos que el paquete ``backend`` sea importable tanto cuando el script
# se ejecuta desde la carpeta del proyecto como dentro de un ejecutable
# generado por PyInstaller.
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


cli = typer.Typer(help="Herramientas para instalar y ejecutar el analizador ABPM")
console = Console()


def _run_async(coro):
    return asyncio.run(coro)


async def _initialize_database() -> None:
    from app.core.config import settings

    try:
        from app.core.database import Base, engine
    except ModuleNotFoundError as exc:  # pragma: no cover - depende del entorno local
        console.print(
            f"[bold red]No se encontró el módulo requerido '{exc.name}'.[/bold red] "
            "Instala nuevamente las dependencias con [bold]pip install -r requirements.txt[/bold] "
            "y vuelve a ejecutar el comando."
        )
        raise typer.Exit(code=1)

    # Aseguramos que todos los modelos estén registrados en la metadata antes de crear
    # las tablas. En algunos entornos los módulos no se importan de forma implícita y
    # ``Base.metadata`` podría quedar vacío si omitimos esta llamada.
    import app.models  # noqa: F401  (side effect: registra los modelos en Base.metadata)

    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@cli.command()
def setup() -> None:
    """Crea la base de datos y las carpetas de almacenamiento necesarias."""

    console.print("[bold cyan]Inicializando la base de datos...[/bold cyan]")
    _run_async(_initialize_database())
    console.print("[green]Listo.[/green] Se creó/actualizó la base de datos y la carpeta de almacenamiento.")


async def _create_user(email: str, password: str, full_name: str) -> bool:
    from sqlalchemy import select

    from app.core.database import async_session_factory
    from app.core.security import get_password_hash
    from app.models import User

    # Garantizamos que la base de datos y las tablas estén listas antes de
    # intentar consultar o insertar usuarios. Esto cubre entornos donde el
    # comando ``create-user`` se ejecuta antes de ``setup``.
    await _initialize_database()

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            return False

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        return True


@cli.command("create-user")
def create_user(
    email: str = typer.Option(..., prompt=True, help="Correo electrónico que usará para ingresar"),
    full_name: str = typer.Option(..., prompt=True, help="Nombre completo del profesional"),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True, help="Contraseña para el acceso"
    ),
) -> None:
    """Crea un usuario inicial para ingresar al sistema."""

    console.print(f"[bold cyan]Creando usuario {email}...[/bold cyan]")
    created = _run_async(_create_user(email=email, password=password, full_name=full_name))
    if created:
        console.print("[green]Usuario creado correctamente.[/green]")
    else:
        console.print("[yellow]El correo ya existe; no se modificó ningún usuario.[/yellow]")


@cli.command()
def serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Inicia el servidor web con FastAPI y Uvicorn."""

    from app.main import app

    console.print(f"[bold cyan]Iniciando servidor en http://{host}:{port} ...[/bold cyan]")
    uvicorn.run(app, host=host, port=port, log_level="info")


def _format_optional(value: Optional[float]) -> str:
    return "Dato insuficiente" if value is None else str(value)


@cli.command()
def analyze(pdf: Path) -> None:
    """Analiza un PDF puntual y muestra las conclusiones en consola."""

    from app.core.config import settings
    from app.services.abpm_analysis import summarize_metrics
    from app.services.pdf_processing import PDFProcessor, locate_patient_metadata

    if not pdf.exists():
        raise typer.BadParameter(f"No se encontró el archivo {pdf}")

    processor = PDFProcessor(settings.storage_dir)
    console.print(f"[bold cyan]Extrayendo información de {pdf.name}...[/bold cyan]")
    text = processor.extract_text(pdf)
    metrics = processor.parse_metrics(text)
    summary = summarize_metrics(metrics)
    patient_name, exam_date = locate_patient_metadata(text)

    table = Table(title="Resumen del estudio")
    table.add_column("Campo")
    table.add_column("Valor", overflow="fold")

    table.add_row("Paciente", patient_name or "Dato insuficiente")
    table.add_row("Fecha", exam_date or "Dato insuficiente")
    table.add_row("PAS 24h", _format_optional(summary.systolic_24h))
    table.add_row("PAD 24h", _format_optional(summary.diastolic_24h))
    table.add_row("PAS diurna", _format_optional(summary.systolic_day))
    table.add_row("PAD diurna", _format_optional(summary.diastolic_day))
    table.add_row("PAS nocturna", _format_optional(summary.systolic_night))
    table.add_row("PAD nocturna", _format_optional(summary.diastolic_night))
    table.add_row("Lecturas totales", _format_optional(summary.measurements_total))
    table.add_row("Lecturas diurnas", _format_optional(summary.measurements_day))
    table.add_row("Lecturas nocturnas", _format_optional(summary.measurements_night))
    table.add_row("Presión de pulso", _format_optional(summary.pulse_pressure_24h))
    table.add_row("Patrón dipping", summary.dipping_pattern or "Dato insuficiente")
    table.add_row("Clasificación", summary.classification or "Dato insuficiente")
    table.add_row("Interpretación", summary.interpretation or "Dato insuficiente")
    table.add_row("Adecuación", summary.adequacy)

    console.print(table)


if __name__ == "__main__":
    cli()

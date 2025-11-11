#!/usr/bin/env python3
"""Verify that a local checkout contains the expected project files.

This helper is aimed at troubleshooting support cases where Windows users
report that only a handful of folders appear after cloning the repository.
It checks for a set of required paths and prints guidance for recovering a
complete working tree when something is missing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_PATHS = {
    Path("abpm_launcher.py"): "Command line launcher",
    Path("requirements.txt"): "Python dependencies",
    Path("backend/app/main.py"): "FastAPI application entry point",
    Path("docs/windows-reinstall.md"): "Windows recovery guide",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the current working tree and report missing files that "
            "indicate an incomplete clone or an unexpected nested folder."
        )
    )
    default_root = Path(__file__).resolve().parents[1]

    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="Root directory of the repository (defaults to la raíz detectada del proyecto).",
    )
    return parser


def _suggest_nested_repo(nested_dir: Path) -> str | None:
    """Detect if the repository is nested inside another directory of the same name."""
    inner_launcher = nested_dir / "abpm_launcher.py"
    if inner_launcher.exists():
        return (
            "Se detectó una carpeta anidada '{name}'. Entra a ella con "
            "`cd {name}` y trabaja desde ese directorio para acceder a todos los archivos.".format(
                name=nested_dir.name
            )
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = args.root.resolve()
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]

    if not missing:
        print("✔ Todos los archivos esenciales están presentes en", root)
        return 0

    print("⚠️  No se encontraron algunos archivos esenciales en", root)
    print()
    for path in missing:
        print(f"  • {path} → {REQUIRED_PATHS[path]}")

    nested_hint = _suggest_nested_repo(root / root.name)
    print()
    if nested_hint:
        print(nested_hint)
        print()

    print("Sigue estos pasos para corregirlo:")
    print("  1. Verifica que Git esté instalado ejecutando `git --version`. Si no, descárgalo de https://git-scm.com/download/win.")
    print(
        "  2. Si la clonación creó una carpeta adicional con el mismo nombre del repositorio, muévete dentro de ella o vuelve a clonar "
        "en un directorio vacío."
    )
    print(
        "  3. Para forzar una clonación limpia, elimina la carpeta actual y vuelve a ejecutar `git clone <URL>` asegurándote de que "
        "no exista una carpeta previa con el mismo nombre."
    )
    print(
        "  4. Si usas OneDrive, sincroniza la carpeta y evita rutas con caracteres especiales o espacios no ASCII para reducir "
        "problemas al instalar dependencias."
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())

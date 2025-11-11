#!/usr/bin/env bash
set -euo pipefail

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller no está instalado. Ejecuta 'pip install pyinstaller' en el entorno actual." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

pyinstaller \
  --onefile \
  --name abpm_analyzer \
  abpm_launcher.py

echo "Ejecutable generado en dist/abpm_analyzer"

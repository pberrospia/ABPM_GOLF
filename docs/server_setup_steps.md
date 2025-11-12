# Guía paso a paso para ejecutar el servidor

Sigue estos pasos en tu máquina local para levantar el backend de ejemplo y verificar que el endpoint `/reports/upload` funciona correctamente.

## 1. Abre una terminal en la raíz del proyecto

- En Windows, puedes usar **PowerShell** o **CMD** y navegar a la carpeta del repositorio, por ejemplo:
  ```powershell
  cd C:\Users\tu_usuario\OneDrive\Documentos\GitHub\ABPM_GOLF
  ```
- En macOS o Linux, abre una terminal y ejecuta:
  ```bash
  cd /ruta/al/repositorio/ABPM_GOLF
  ```

Comprueba que estás en la carpeta correcta con `pwd` (macOS/Linux) o `cd` sin argumentos (Windows).

## 2. Activa tu entorno virtual (opcional, pero recomendado)

Si ya creaste un entorno virtual, actívalo antes de continuar:

- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```

Si no tienes un entorno virtual, puedes crearlo con `python -m venv .venv` y luego activar la ruta correspondiente.

## 3. Instala las dependencias del proyecto

Ejecuta una única vez (con el entorno activado si aplica):
```bash
pip install -r requirements.txt
```

Si no cuentas con `requirements.txt`, instala los paquetes mínimos indicados en el README:
```bash
pip install fastapi uvicorn typer rich sqlalchemy pydantic pydantic-settings
```

## 4. Ejecuta el servidor con el lanzador

Desde la raíz del repositorio ejecuta:
```bash
python abpm_launcher.py serve
```

El comando mostrará en consola algo similar a:
```
Iniciando servidor en http://0.0.0.0:8000 ...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Esto significa que el servidor FastAPI está listo.

## 5. Verifica la API en el navegador

Abre tu navegador y visita `http://127.0.0.1:8000/docs`. Deberías ver la documentación interactiva de FastAPI. Prueba el endpoint `/reports/upload` para confirmar que ya no aparece el error `AssertionError: Cannot specify 'Depends' in 'Annotated'...`.

## 6. Detén el servidor cuando termines

Regresa a la terminal donde se está ejecutando Uvicorn y presiona `Ctrl+C`. Esto finaliza el proceso del servidor y te devuelve al prompt.

## 7. ¿Sigues viendo el error de Git?

Si al ejecutar `git pull` aparece `fatal: not a git repository (or any of the parent directories): .git`, sigue la guía en `docs/troubleshooting_git_repository.md` para reparar tu repositorio local antes de continuar.

Con estos pasos deberías poder levantar el backend y validar los cambios sin volver a encontrar el error de dependencias.

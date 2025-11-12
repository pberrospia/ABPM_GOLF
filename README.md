# ABPM Analyzer (demo)

Este repositorio contiene una versión reducida del servicio ABPM Analyzer que
ilustra cómo estructurar dependencias de FastAPI compatibles con Pydantic v2.

## Puesta en marcha

1. Instala las dependencias principales:
   ```bash
   pip install fastapi uvicorn typer rich sqlalchemy pydantic pydantic-settings
   ```
2. Ejecuta el servidor:
   ```bash
   python abpm_launcher.py serve
   ```
3. Visita `http://127.0.0.1:8000/docs` para explorar la API interactiva.

El endpoint `/reports/upload` ahora declara las dependencias mediante
`typing.Annotated` sin valores por defecto `Depends(...)`, evitando el
`AssertionError` observado originalmente.

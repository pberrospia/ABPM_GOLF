# ABPM_GOLF

Aplicativo backend para analizar estudios de monitoreo ambulatorio de presión arterial (ABPM).

## Características

- Carga de PDFs nativos o escaneados con extracción automática (texto y OCR).
- Análisis según guías ESC/ESH 2023: suficiencia de mediciones, clasificación, patrón dipping y presión de pulso.
- Gestión de usuarios con autenticación vía JWT y firma digital opcional.
- Edición de conclusiones y recomendaciones antes de generar el informe final.
- Generación de un PDF consolidado que agrega una hoja de resumen con conclusiones y recomendaciones.
- Almacenamiento en base de datos SQLite (puede migrarse a otros motores mediante SQLAlchemy).

## Requisitos

- Python 3.11+
- Tesseract OCR instalado en el sistema para procesar PDFs escaneados.

Instale dependencias:

```bash
pip install -r requirements.txt
```

## Uso

### Obtener el código fuente

1. **Crea una carpeta contenedora (opcional, pero recomendado):**
   - Desde el explorador de archivos crea, por ejemplo, `Documentos/ABPM`.
   - O bien, en una terminal ejecuta:
     ```bash
     mkdir -p ~/Documentos/ABPM
     cd ~/Documentos/ABPM
     ```

2. **Descarga el repositorio:**
   - **Usando Git (recomendado):**
     ```bash
     git clone https://example.com/ABPM_GOLF.git
     ```
     Sustituye la URL por la ubicación real del repositorio si es diferente.
   - **Descargando un ZIP:**
     1. Visita la página del repositorio en tu navegador.
     2. Usa la opción “Download ZIP”.
     3. Extrae el contenido dentro de la carpeta creada en el paso anterior.

3. **Ingresa en la carpeta del proyecto:**
   ```bash
   cd ABPM_GOLF
   ```
   Todos los comandos restantes deben ejecutarse desde este directorio raíz.

### Ejecución guiada paso a paso

1. **Cree un entorno virtual (opcional pero recomendado):**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows use: .venv\\Scripts\\activate
   ```

2. **Instale las dependencias del proyecto:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Inicialice la base de datos y las carpetas necesarias:**

   ```bash
   python abpm_launcher.py setup
   ```

4. **Cree su usuario inicial:**

   ```bash
   python abpm_launcher.py create-user
   ```

   El asistente solicitará correo electrónico, nombre completo y contraseña (con confirmación) y los almacenará en la base de datos.

5. **Arranque el servidor web:**

   ```bash
   python abpm_launcher.py serve
   ```

   Acceda a `http://localhost:8000/docs` para interactuar con la API y cargar estudios.

6. **(Opcional) Verifique rápidamente un PDF desde la consola:**

   ```bash
   python abpm_launcher.py analyze ruta/al/estudio.pdf
   ```

   Se mostrará en pantalla el resumen de métricas y la clasificación según las guías ESC/ESH 2023.

### Reinstalación limpia en Windows (corrige errores de inicialización de base de datos)

Consulta la guía completa en [`docs/windows-reinstall.md`](docs/windows-reinstall.md) para una explicación minuciosa de cada paso. A modo de resumen:

1. Cierra las terminales activas y elimina el entorno anterior (`Remove-Item -Recurse -Force .venv`).
2. Verifica que `py -3.11 --version` funcione y crea el nuevo virtualenv con `py -3.11 -m venv .venv`.
3. En PowerShell permite scripts si es necesario (`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`) y activa el entorno (`.\.venv\Scripts\Activate.ps1`).
4. Actualiza `pip` e instala las dependencias: `python -m pip install --upgrade pip` seguido de `pip install -r requirements.txt`.
5. Ejecuta `python abpm_launcher.py setup` para crear la base de datos. Si `pip` muestra una advertencia sobre `aiosqlite`, puedes continuar: la aplicación ahora usa un controlador alternativo automáticamente gracias al módulo `backend.aiosqlite` incluido en el repositorio.
6. Continúa con `python abpm_launcher.py create-user` y `python abpm_launcher.py serve` para usar la aplicación.

Si algún paso falla (por ejemplo, PowerShell bloquea la activación), la guía detallada ofrece soluciones específicas.

### Construir un ejecutable autónomo

1. Instale PyInstaller en el mismo entorno donde instaló las dependencias:

   ```bash
   pip install pyinstaller
   ```

2. Ejecute el script de ayuda incluido:

   ```bash
   ./scripts/build_executable.sh
   ```

   El binario resultante quedará en `dist/abpm_analyzer`. Puede copiarlo a otro equipo junto con Tesseract OCR instalado para usar la aplicación sin Python.

### Ejecución manual del servidor

Ejecute el servidor:

```bash
uvicorn app.main:app --reload --app-dir backend
```

La API estará disponible en `http://localhost:8000`, con documentación interactiva en `/docs`.

## Pruebas

```bash
pytest
```

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

### Reinstalación limpia en Windows (corrige `ModuleNotFoundError: No module named 'aiosqlite'`)

Si anteriormente creaste el entorno virtual con Python 3.14 o ves el error `ModuleNotFoundError: No module named 'aiosqlite'`,
sigue estos pasos:

1. **Cerrar y eliminar el entorno anterior** (ejecuta ambos comandos dentro de la carpeta del proyecto):
   ```powershell
   deactivate  # ignora este paso si PowerShell indica que el comando no existe
   Remove-Item -Recurse -Force .venv
   ```

2. **Verificar que Python 3.11 esté disponible**:
   ```powershell
   py -3.11 --version
   ```
   Si el comando no encuentra Python 3.11, descárgalo e instálalo desde [python.org](https://www.python.org/downloads/release/python-3110/).

3. **Crear un nuevo entorno virtual usando Python 3.11**:
   ```powershell
   py -3.11 -m venv .venv
   ```

4. **Activar el entorno**:
   - PowerShell (si ves un error de ejecución de scripts, ejecuta primero `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Consola clásica `cmd.exe`:
     ```cmd
     .venv\Scripts\activate.bat
     ```

5. **Actualizar `pip` e instalar los requisitos**:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
   `aiosqlite`, `email-validator` y el resto de dependencias se instalarán en este paso.

6. **Inicializar la base de datos con el nuevo entorno**:
   ```powershell
   python abpm_launcher.py setup
   ```

7. **Crear el usuario inicial y arrancar el servidor** (idéntico a los pasos 4 y 5 de la guía principal).

8. *(Opcional)* **Confirmar que `aiosqlite` está instalado** si el error persiste:
   ```powershell
   pip show aiosqlite
   ```
   Si el paquete no aparece, repite el paso 5 para reinstalar los requisitos.

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

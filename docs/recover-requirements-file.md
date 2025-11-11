# Restaurar `requirements.txt` tras una reinstalación

Si al reinstalar tu entorno de trabajo ves que `requirements.txt` (o el alias histórico `requeriments.txt`) desapareció, sigue estos pasos para recuperarlo desde Git y volver a instalar las dependencias.

> ℹ️ Ejecuta todos los comandos desde la carpeta raíz del proyecto (`ABPM_GOLF`).

## 1. Verifica que estás en la carpeta correcta

En PowerShell o cmd.exe:

```powershell
cd C:\Users\TU_USUARIO\OneDrive\Documentos\GitHub\ABPM_GOLF
```

Sustituye la ruta según la ubicación real del repositorio. Confirma con `dir` (cmd) o `Get-ChildItem` (PowerShell) que ves archivos como `abpm_launcher.py` y la carpeta `backend/`.

## 2. Revisa el estado del repositorio

```powershell
git status
```

- Si `requirements.txt` aparece como `deleted`, continúa con el siguiente paso.
- Si Git indica “nothing to commit”, es posible que el archivo exista y solo debas volver a instalar dependencias (`pip install -r requirements.txt`). Usa `type requirements.txt` (cmd) o `Get-Content requirements.txt` (PowerShell) para comprobar su contenido.

## 3. Restaura el archivo desde Git

- Para recuperar la versión que tienes en tu rama local:

  ```powershell
  git restore requirements.txt requeriments.txt
  ```

- Si el archivo también falta en tu rama pero sí existe en el remoto principal (`origin/main`), actualiza y restaura con:

  ```powershell
  git fetch origin
  git restore --source origin/main requirements.txt requeriments.txt
  ```

Ambos comandos descargan la lista oficial de dependencias del repositorio junto con el alias `requeriments.txt` que redirige a la misma información.

## 4. Reinstala las dependencias

Con tu entorno virtual de Python 3.11 activo:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

La instalación volverá a incluir componentes como FastAPI, SQLAlchemy, Pillow y `email-validator`. Si `pip` muestra la advertencia `Package(s) not found: aiosqlite`, puedes continuar: el proyecto incluye un módulo compatible en `backend/aiosqlite`.

## 5. Continúa con la configuración habitual

Ejecuta nuevamente los comandos del asistente según lo necesites:

```powershell
python abpm_launcher.py setup
python abpm_launcher.py create-user
python abpm_launcher.py serve
```

Con estos pasos, el archivo `requirements.txt` queda restaurado y el entorno vuelve a tener todas las dependencias necesarias para inicializar la base de datos y usar la aplicación.

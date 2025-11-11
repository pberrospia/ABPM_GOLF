# Restaurar `requirements.txt` tras una reinstalación

Si al reinstalar tu entorno de trabajo ves que `requirements.txt` (o el alias histórico `requeriments.txt`) desapareció, sigue estos pasos para recuperarlo desde Git y volver a instalar las dependencias.

> ℹ️ Ejecuta todos los comandos desde la carpeta raíz del proyecto (`ABPM_GOLF`).

## 1. Verifica que estás en la carpeta correcta

En PowerShell o cmd.exe:

```powershell
cd C:\Users\TU_USUARIO\OneDrive\Documentos\GitHub\ABPM_GOLF
```

Sustituye la ruta según la ubicación real del repositorio. Confirma con `dir` (cmd) o `Get-ChildItem` (PowerShell) que ves archivos como `abpm_launcher.py` y la carpeta `backend/`.

## 2. Verifica que Git esté disponible

Antes de ejecutar cualquier comando `git`, asegúrate de que la herramienta está instalada y presente en tu `PATH`:

```powershell
git --version
```

- Si ves un número de versión (por ejemplo, `git version 2.47.0.windows.1`), continúa con el siguiente paso.
- Si aparece el error `The term 'git' is not recognized`, instala Git para Windows desde [git-scm.com](https://git-scm.com/download/win) y acepta la opción que agrega Git al `PATH`. Tras la instalación, abre una terminal nueva y repite el comando anterior.
- Si prefieres no instalar Git, puedes descargar el ZIP del repositorio desde GitHub, pero las instrucciones siguientes asumen que ya cuentas con la herramienta.

## 3. Revisa el estado del repositorio

```powershell
git status
```

- Si `requirements.txt` aparece como `deleted`, continúa con el siguiente paso.
- Si Git indica “nothing to commit”, es posible que el archivo exista y solo debas volver a instalar dependencias (`pip install -r requirements.txt`). Usa `type requirements.txt` (cmd) o `Get-Content requirements.txt` (PowerShell) para comprobar su contenido.

## 4. Restaura el archivo desde Git

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

## 5. Reinstala las dependencias

Con tu entorno virtual de Python 3.11 activo:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

La instalación volverá a incluir componentes como FastAPI, SQLAlchemy, Pillow y `email-validator`. Si `pip` muestra la advertencia `Package(s) not found: aiosqlite`, puedes continuar: el proyecto incluye un módulo compatible en `backend/aiosqlite`.

## 6. Continúa con la configuración habitual

Ejecuta nuevamente los comandos del asistente según lo necesites:

```powershell
python abpm_launcher.py setup
python abpm_launcher.py create-user
python abpm_launcher.py serve
```

Con estos pasos, el archivo `requirements.txt` queda restaurado y el entorno vuelve a tener todas las dependencias necesarias para inicializar la base de datos y usar la aplicación.

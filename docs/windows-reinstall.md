# Reinstalación limpia en Windows para corregir `ModuleNotFoundError: No module named 'aiosqlite'`

Este procedimiento repone el entorno virtual usando **Python 3.11** y reinstala las dependencias para que `aiosqlite` quede disponible antes de ejecutar `python abpm_launcher.py setup`.

> ℹ️ Ejecuta cada comando desde **PowerShell** o **cmd.exe** abierto en la carpeta raíz del proyecto (`ABPM_GOLF`).

## 1. Cerrar shells y liberar el entorno previo

1. Si tienes ventanas de PowerShell/cmd con el servidor en ejecución, detenlas (`Ctrl + C`).
2. En cualquier terminal donde veas el prefijo `(.venv)` en el prompt, escribe:
   ```powershell
   deactivate
   ```
   - Si aparece «command not found», significa que el entorno ya estaba desactivado; continúa.

## 2. Eliminar el entorno virtual anterior

```powershell
Remove-Item -Recurse -Force .venv
```

Si prefieres conservarlo, renómbralo (`Rename-Item .venv .venv_py314`).

## 3. Confirmar que Python 3.11 está instalado

```powershell
py -3.11 --version
```

- Si no lo tienes, descárgalo de [python.org](https://www.python.org/downloads/release/python-3110/) e **instala** con la opción «Add python.exe to PATH» habilitada.
- Comprueba la ruta registrada:
  ```powershell
  py -0p | Select-String 3.11
  ```

## 4. Crear el nuevo entorno con Python 3.11

```powershell
py -3.11 -m venv .venv
```

El comando genera la carpeta `.venv` con el intérprete correcto.

## 5. Permitir scripts de activación (solo PowerShell)

Si al activar ves el error «running scripts is disabled», ejecuta **una sola vez**:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Responde `Y` cuando lo solicite. Para evitar cambiar la política permanente, puedes usar la variante temporal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 6. Activar el entorno

- PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- cmd.exe:
  ```cmd
  .venv\Scripts\activate.bat
  ```

Comprueba que el prompt muestre `(.venv)` y que la versión sea 3.11:
```powershell
python --version
```

## 7. Actualizar `pip` e instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Verifica que `aiosqlite` está presente:
  ```powershell
  pip show aiosqlite
  ```
  Debe mostrar información de versión (p. ej. 0.19.0). Si no aparece, repite el comando de instalación.

## 8. Inicializar la base de datos

```powershell
python abpm_launcher.py setup
```

El script debe mostrar «Listo. Se creó/actualizó la base de datos…» sin excepciones.

## 9. Crear usuario y arrancar el servidor (opcional)

```powershell
python abpm_launcher.py create-user
python abpm_launcher.py serve
```

Accede a `http://localhost:8000/docs` para probar los endpoints.

## 10. Solución de problemas

- **Sigue apareciendo `ModuleNotFoundError`:**
  1. Repite el paso 6 para asegurarte de que el entorno 3.11 está activo.
  2. Ejecuta `python -m pip install aiosqlite` para reinstalar solo ese paquete.
  3. Ejecuta `pip list | Select-String aiosqlite` y confirma que figura en la lista.
- **`py` no encuentra Python 3.11:** usa la ruta completa, por ejemplo `C:\Program Files\Python311\python.exe -m venv .venv`.
- **Permisos de ejecución aún bloqueados:** abre una nueva ventana de PowerShell tras aplicar el paso 5 o usa cmd.exe para la activación.

Tras completar estos pasos, `abpm_launcher.py setup` utilizará el driver `sqlite+aiosqlite` correctamente y la base de datos se inicializará sin errores.

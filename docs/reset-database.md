# Recuperar la base de datos cuando aparece "no such table: users"

Este error indica que SQLite todavía no tiene creada la tabla `users`. Generalmente
aparece si `python abpm_launcher.py setup` no se ha ejecutado en el entorno
actual o si el archivo `abpm.db` fue borrado mientras el CLI seguía abierto.

Sigue estos pasos desde la carpeta raíz del repositorio (`ABPM_GOLF`):

1. **Cierra los comandos en ejecución.** Detén cualquier ventana donde tengas
   `python abpm_launcher.py serve` u otro proceso activo (`Ctrl + C`).
2. **Activa el entorno virtual correcto.** Comprueba que estás usando
   Python 3.11:
   ```powershell
   .\.venv\Scripts\Activate.ps1   # PowerShell
   python --version
   ```
   Si prefieres `cmd.exe`:
   ```cmd
   .venv\Scripts\activate.bat
   python --version
   ```
   Debe mostrar `Python 3.11.x`. Si no existe `.venv`, crea uno con
   `py -3.11 -m venv .venv` y vuelve a instalar dependencias
   (`pip install -r requirements.txt`).
3. **Elimina la base de datos anterior (opcional pero recomendado si falló varias veces).**
   ```powershell
   Remove-Item abpm.db -ErrorAction SilentlyContinue
   ```
   Esto obliga a recrear todas las tablas desde cero. También puedes borrar la
   carpeta `storage` si deseas limpiar los archivos subidos.
4. **Inicializa la base de datos.**
   ```powershell
   python abpm_launcher.py setup
   ```
   El comando importa todos los modelos y crea las tablas requeridas. Debe
   terminar con el mensaje `Listo.`
5. **Vuelve a crear el usuario.**
   ```powershell
   python abpm_launcher.py create-user
   ```
   Si el correo ya existe, el comando te avisará y no realizará cambios.
6. **Arranca el servidor opcionalmente.**
   ```powershell
   python abpm_launcher.py serve
   ```

Si el problema persiste, ejecuta `python abpm_launcher.py setup` una vez más y
verifica que en la carpeta del proyecto exista el archivo `abpm.db` (puedes usar
`dir abpm.db`). Repetir el `setup` no borra datos existentes; simplemente añade
las tablas que falten.

En entornos sin conexión a Internet, el repositorio incluye un controlador
`backend.aiosqlite` que reemplaza automáticamente a `aiosqlite`, por lo que la
advertencia `Package(s) not found: aiosqlite` puede ignorarse.

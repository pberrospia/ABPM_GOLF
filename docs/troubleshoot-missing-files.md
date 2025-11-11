# Recuperar archivos faltantes después de clonar

Cuando una instalación nueva parece incompleta —por ejemplo, solo muestra las
carpetas `backend`, `scripts`, `tests` y un directorio adicional `ABPM_GOLF`
dentro del propio repositorio— normalmente se debe a una clonación parcial o a
que el contenido quedó anidado dentro de otra carpeta. Sigue estos pasos para
recuperar todos los archivos:

1. **Comprueba que Git está instalado.**
   Abre PowerShell o cmd y ejecuta:
   ```powershell
   git --version
   ```
   Si ves el error "`git` is not recognized", instala Git desde
   <https://git-scm.com/download/win> y vuelve a abrir la terminal.

2. **Verifica en qué carpeta estás trabajando.**
   Ejecuta `dir` (cmd) o `Get-ChildItem` (PowerShell). Deberías ver archivos
   como `abpm_launcher.py`, `requirements.txt` y la carpeta `docs`. Si solo ves
   un subdirectorio llamado `ABPM_GOLF`, entra en él con:
   ```powershell
   cd ABPM_GOLF
   dir
   ```
   Trabaja a partir de esa carpeta interior o mueve su contenido al directorio
   superior si lo prefieres.

3. **Usa el verificador automático opcional.**
   Dentro del repositorio ejecuta:
   ```powershell
   python scripts/check_clone.py
   ```
   El script indicará qué archivos faltan y sugerirá los pasos para recuperarlos.

4. **Fuerza una clonación limpia si el árbol sigue incompleto.**
   - Cierra la terminal y elimina la carpeta incompleta.
   - Abre una nueva terminal y sitúate en un directorio vacío.
   - Ejecuta nuevamente `git clone https://github.com/pberrospia/ABPM_GOLF.git`.
   - Entra en la carpeta recién creada y comprueba que ahora aparecen los
     archivos `abpm_launcher.py`, `aiosqlite/`, `docs/`, etc.

5. **Evita carpetas sincronizadas por OneDrive/Google Drive durante la instalación.**
   Estas herramientas pueden tardar en descargar todos los archivos y provocar
   que parezcan ausentes temporalmente. Si es posible, clona el repositorio en
   una ruta local corta, como `C:\Dev\ABPM_GOLF`.

Con estos pasos deberías recuperar la estructura completa del proyecto y poder
continuar con la instalación del entorno virtual y la ejecución del aplicativo.

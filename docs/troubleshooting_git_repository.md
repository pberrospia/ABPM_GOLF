# Solución de problemas: `fatal: not a git repository`

Cuando `git` muestra el mensaje `fatal: not a git repository (or any of the parent directories): .git`,
significa que la carpeta actual no contiene la metadata necesaria para actuar como repositorio. Sigue este
procedimiento:

1. **Verifica en qué carpeta estás.**
   - macOS/Linux: `pwd`
   - Windows (PowerShell): `Get-Location`
   - Windows (CMD): `cd`

2. **Busca la carpeta `.git`.**
   - macOS/Linux: `ls -a`
   - Windows (PowerShell): `Get-ChildItem -Force`
   - Windows (CMD): `dir /a`
   - Si no ves `.git`, vuelve a clonar el repositorio con `git clone <URL>`.

3. **Comprueba que Git reconoce el repositorio.**
   - Ejecuta `git status`.
   - Si el comando vuelve a fallar, la carpeta `.git` puede estar dañada. Haz una copia de tus archivos modificados y
     clona el repositorio nuevamente.

4. **Opcional: repara la carpeta `.git`.**
   - Si tienes un respaldo, puedes copiar el directorio `.git` original a tu carpeta actual.
   - En situaciones simples, `git init` puede recrear la estructura mínima, pero perderás el historial remoto, por lo que
     es preferible clonar de nuevo.

5. **Retoma tu flujo de trabajo.**
   - Una vez que `git status` funcione, vuelve a ejecutar `git pull` para actualizarte.

> 💡 Consejo: guarda tus cambios locales fuera del repositorio antes de eliminar o recrear la carpeta `.git` para no
> perder trabajo.

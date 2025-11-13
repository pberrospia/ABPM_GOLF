# ABPM Analyzer (demo)

Este repositorio contiene una versión reducida del servicio ABPM Analyzer que
ilustra cómo estructurar dependencias de FastAPI compatibles con Pydantic v2.

## Puesta en marcha

Sigue la guía detallada en [`docs/server_setup_steps.md`](docs/server_setup_steps.md)
para obtener un paso a paso completo. En resumen:

1. Instala las dependencias principales:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el servidor:
   ```bash
   python abpm_launcher.py serve
   ```
3. Visita `http://127.0.0.1:8000/docs` para explorar la API interactiva.

El endpoint `/reports/upload` ahora emplea alias basados en `typing.Annotated`
sin valores por defecto (por ejemplo, `DBSession` y `CurrentUser`). El servicio
extrae texto del PDF con [`pypdf`](https://pypi.org/project/pypdf/), analiza los
valores sistólicos/diastólicos presentes en el documento y devuelve un resumen
con los promedios calculados.

## ¿Problemas con `git pull`?

Si ves el error `fatal: not a git repository (or any of the parent directories): .git`,
sigue estos pasos:

1. **Confirma tu ubicación.** Ejecuta `pwd` (en macOS/Linux) o `cd` (en Windows)
   y verifica que estés dentro de la carpeta clonada `ABPM_GOLF`.
2. **Comprueba la presencia de la carpeta `.git`.** Ejecuta `ls -a` (o
   `dir /a` en Windows). Si no aparece `.git`, significa que el repositorio no se
   clonó correctamente.
3. **Si falta `.git`, vuelve a clonar el repositorio** con
   `git clone <URL_DEL_REPOSITORIO>` y entra en la carpeta recién creada antes de
   ejecutar `git pull`.
4. **Si `.git` existe pero el error persiste**, ejecuta `git status` para
   confirmar que Git reconoce el repositorio. Si el comando falla, puede que la
   carpeta `.git` esté dañada; en ese caso, guarda tus cambios y vuelve a clonar
   el repositorio desde cero.

Consulta `docs/troubleshooting_git_repository.md` para capturas de comandos y
detalles adicionales. Para un instructivo único que combine la solución del
`AssertionError` y del error de Git, visita
[`docs/manual_fix_steps.md`](docs/manual_fix_steps.md).

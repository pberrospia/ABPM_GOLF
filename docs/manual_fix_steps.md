# Guía paso a paso para corregir los errores reportados

Esta guía te ayuda a solucionar **dos problemas concretos**:

1. El servidor FastAPI lanza `AssertionError: Cannot specify "Depends" in "Annotated"...`.
2. Al ejecutar `git pull` aparece `fatal: not a git repository (or any of the parent directories): .git`.

Sigue cada bloque en orden para que ambos inconvenientes desaparezcan.

---

## Parte A. Arreglar el `AssertionError` en `/reports/upload`

1. **Abrir el archivo correcto**
   - Desde la raíz del proyecto ve a `backend/app/api/reports.py`.
   - Puedes abrirlo con tu editor o, en una terminal, ejecutar `code backend/app/api/reports.py` (VS Code) o `notepad backend/app/api/reports.py` (Windows).

2. **Localizar la función** `upload_report`.
   - Debe comenzar con `@router.post("/upload", ...)`.

3. **Actualizar la firma de los parámetros** si todavía ves algo como:
   ```python
   session: Annotated[AsyncSession, Depends(get_session)] = Depends(get_session)
   current_user: Annotated[User, Depends(get_current_user)] = Depends(get_current_user)
   ```
   Sustitúyelos por la versión compatible con Pydantic v2:
   ```python
   from fastapi import Depends
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.models.user import User
   from app.core.database import get_session
   from app.api.deps import get_current_user

   async def upload_report(
       session: AsyncSession = Depends(get_session),
       current_user: User = Depends(get_current_user),
       pdf: UploadFile = File(...),
       patient_name: Annotated[str | None, Form(None)] = None,
       exam_date: Annotated[str | None, Form(None)] = None,
   ) -> ReportRead:
       ...
   ```

4. **Guardar el archivo** y cerrar el editor.

5. **Reiniciar el servidor**:
   ```bash
   python abpm_launcher.py serve
   ```
   - Si el servidor arranca sin mostrar el `AssertionError`, la corrección fue exitosa.

---

## Parte B. Resolver `fatal: not a git repository`

1. **Verificar dónde estás ubicado**:
   ```bash
   pwd   # macOS/Linux
   cd    # Windows PowerShell/CMD
   ```
   - Asegúrate de que la ruta termine en `ABPM_GOLF`.

2. **Comprobar si existe la carpeta `.git`**:
   ```bash
   ls -a          # macOS/Linux
   dir /a         # Windows
   ```
   - Si ves `.git`, continúa con el paso 4. Si no aparece, ve al paso 3.

3. **Reclonar el repositorio (si `.git` falta)**:
   1. Sube un nivel (`cd ..`).
   2. Renombra o elimina la carpeta actual (`mv ABPM_GOLF ABPM_GOLF_old` o `ren ABPM_GOLF ABPM_GOLF_old`).
   3. Clona de nuevo: `git clone <URL_DEL_REPOSITORIO>`.
   4. Entra a la carpeta recién clonada: `cd ABPM_GOLF`.

4. **Confirmar el estado del repositorio**:
   ```bash
   git status
   ```
   - El comando debe mostrar la rama actual. Si aparece otro error, la carpeta `.git` podría estar dañada: guarda cualquier archivo importante y vuelve a clonar desde cero.

5. **Ejecutar ahora `git pull`**.
   ```bash
   git pull
   ```
   - Ya no debería mostrarse el mensaje `fatal: not a git repository`.

---

## Parte C. Validación final

1. Con el repositorio en buen estado, instala dependencias si aún no lo hiciste:
   ```bash
   pip install -r requirements.txt
   ```

2. Lanza el servidor nuevamente:
   ```bash
   python abpm_launcher.py serve
   ```

3. Abre `http://127.0.0.1:8000/docs` y prueba el endpoint `/reports/upload`. El `AssertionError` debe haber desaparecido.

Si algún paso falla, consulta las guías de apoyo:
- [`docs/fixing_dependency_annotation.md`](fixing_dependency_annotation.md) para más contexto sobre el ajuste de dependencias.
- [`docs/troubleshooting_git_repository.md`](troubleshooting_git_repository.md) para comandos alternativos y escenarios especiales de Git.

¡Listo! Siguiendo estas indicaciones paso a paso deberías poder aplicar los cambios sin contratiempos.

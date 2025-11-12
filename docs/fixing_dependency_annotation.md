# Solucionar el error de FastAPI con `Depends` y `Annotated`

Este documento explica cómo resolver el error:

```
AssertionError: Cannot specify `Depends` in `Annotated` and default value together for 'session'
```

El problema aparece al usar Pydantic v2/FastAPI recientes, que no permiten mezclar `typing.Annotated` con un valor por defecto `Depends()` en el mismo parámetro. Sigue los pasos para ajustarlo:

## 1. Abrir el archivo correcto

1. Desde la raíz del proyecto ve a `backend/app/api/reports.py`.
2. Localiza la función `upload_report` (y cualquier otra) donde aparezca un parámetro declarado como:
   ```python
   session: Annotated[AsyncSession, Depends(get_session)] = Depends(get_session)
   ```

## 2. Elegir **un** estilo de dependencia

FastAPI permite dos sintaxis equivalentes. Quédate solo con una de ellas:

- **Opción A (recomendada para Pydantic v2)** – usar únicamente `Annotated`:
  ```python
  from typing import Annotated

  from fastapi import Depends

  session: Annotated[AsyncSession, Depends(get_session)]
  ```
- **Opción B** – usar únicamente el valor por defecto:
  ```python
  from fastapi import Depends

  session: AsyncSession = Depends(get_session)
  ```

## 3. Aplicar el cambio

1. Borra el `= Depends(get_session)` cuando utilices `Annotated` (Opción A).
2. Repite el mismo ajuste para cualquier otro parámetro parecido, por ejemplo:
   ```python
 current_user: Annotated[User, Depends(get_current_user)]
  ```
3. Guarda el archivo.

## 4. Verificar

1. Vuelve a ejecutar `python abpm_launcher.py serve`.
2. El servidor debería iniciar sin lanzar el `AssertionError`.

## 5. Ejemplo aplicado en este repositorio

El endpoint `/reports/upload` ya utiliza la sintaxis corregida:

```python
@router.post("/upload", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def upload_report(
    pdf: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: CurrentUser,
    patient_name: Annotated[str | None, Form(None)] = None,
    exam_date: Annotated[str | None, Form(None)] = None,
) -> ReportRead:
    ...
```

Así evitamos mezclar `Annotated` con valores por defecto `Depends(...)` y se
mantiene un orden de parámetros compatible con Python.

> 💡 Consejo: mantén un estilo consistente en todo el proyecto (solo `Annotated` o solo valores por defecto con `Depends`) para evitar errores similares en el futuro.

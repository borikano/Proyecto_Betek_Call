# Guía de Versionamiento y Trazabilidad

Este documento define las reglas mínimas para mantener trazabilidad profesional en el proyecto Betek Call Center Analytics.

## Objetivo

Asegurar que cada cambio realizado en el repositorio tenga:

- propósito claro;
- nombre descriptivo;
- contexto documentado;
- validación verificable;
- historial limpio en Git;
- Pull Requests con título y descripción completa.

## Política de idioma y compatibilidad

Para la documentación del proyecto se debe usar español correcto, con buena ortografía, acentos y caracteres propios del idioma, como la letra ñ.

Para código, nombres de archivos, nombres de tablas, columnas, CSV, SQL, rutas y datos destinados a carga en base de datos, se debe priorizar compatibilidad técnica. En esos casos se recomienda usar texto ASCII, sin acentos ni ñ, cuando esto ayude a evitar problemas de codificación, carga o integración con PostgreSQL, Excel o Power BI.

En resumen:

- documentación: redacción cuidada, con acentos y buena ortografía;
- código y datos técnicos: consistencia, compatibilidad y nombres seguros para sistemas.

## Regla principal

No se deben crear ramas, commits, Pull Requests o tags con nombres genéricos o descripciones vacías.

Cada cambio debe responder:

- qué se hizo;
- por qué se hizo;
- qué archivos o componentes afecta;
- cómo se validó;
- si modifica o no el modelo SQL;
- si afecta datasets versionados.

## Convención de ramas

Usar nombres cortos, descriptivos y en minúsculas.

Prefijos recomendados:

- feat/: nuevas funcionalidades.
- fix/: correcciones.
- docs/: documentación.
- chore/: mantenimiento o limpieza.
- test/: pruebas o validaciones.
- data/: cambios en datasets versionados.
- scripts/: scripts auxiliares.

Ejemplos:

- feat/add-postgresql-validation-queries
- fix/normalize-baseline-loader-ids
- docs/update-readme-postgresql-load
- data/add-125k-synthetic-dataset
- scripts/add-125k-generation-command
- chore/remove-legacy-files

## Convención de commits

Usar commits atómicos. Cada commit debe representar un cambio coherente.

Formato recomendado:

    tipo: descripción breve

Tipos recomendados:

- feat:
- fix:
- docs:
- chore:
- test:
- data:
- scripts:

Ejemplos:

- feat: support explicit generation date range
- fix: improve nullable integer export
- fix: normalize baseline loader ids
- docs: clarify dataset loader working directory
- docs: clean README structure and dataset guide
- data: add 125k synthetic call center dataset
- scripts: add 125k dataset generation command
- chore: remove duplicated 125k generator
- test: expand quality validations

## Pull Requests

Todo Pull Request debe incluir título y descripción.

Descripción mínima:

### Cambios

- Lista de cambios realizados.

### Contexto

- Explicación breve de por qué se hizo el cambio.

### Validación

- Comandos ejecutados.
- Resultados esperados.
- Conteos o validaciones si aplica.

### Nota

- Indicar si el cambio modifica o no el modelo SQL.

## Ejemplo de Pull Request

Título:

    fix: normalize baseline loader ids

Descripción:

### Cambios

- Corrige IDs nullable en llamadas.csv.
- Normaliza id_agente e id_caso.
- Actualiza documentación de carga.

### Contexto

Durante la carga en PostgreSQL se detectaron valores como 15.0 en columnas bigint.

### Validación

- El smoke test cargó correctamente.
- Conteos validados en PostgreSQL.

### Nota

Este cambio no modifica el modelo SQL ni agrega tablas.

## Tags

Los tags deben usarse solo para hitos importantes del proyecto.

Formato recomendado:

    vmayor.menor.parche-descripción

Ejemplos:

- v1.0.0-125k
- v1.0.1-docs
- v1.1.0-postgresql-load

No se deben mover ni sobrescribir tags ya publicados, salvo que exista una razón técnica justificada.

## Buenas prácticas antes de hacer merge

Antes de hacer merge de un Pull Request:

1. Verificar que el título sea claro.
2. Verificar que la descripción no esté vacía.
3. Confirmar que el cambio corresponde al alcance de la rama.
4. Revisar git status --short.
5. Confirmar que no se suben archivos temporales.
6. Validar que no se modifica el modelo SQL sin decisión explícita.
7. Confirmar que las pruebas o validaciones aplicables fueron ejecutadas.

## Buenas prácticas después del merge

Después de hacer merge:

    git switch main
    git pull origin main
    git status --short
    git log --oneline --decorate -8

Si la rama ya no se necesita:

    git branch -d nombre-de-la-rama
    git push origin --delete nombre-de-la-rama

## Política del modelo SQL

El modelo SQL oficial se encuentra en:

    sql/06_ddl_sql_creacion_tablas.sql

No se deben agregar, eliminar o modificar tablas sin una decisión explícita del proyecto.

Si un cambio afecta el modelo SQL, el Pull Request debe indicarlo claramente en la descripción.

## Política de datasets

Los datasets versionados deben incluir:

- archivos .csv por tabla;
- load_call_center_postgresql.sql;
- quality_report.json;
- generation_log.json;
- row_counts.csv.

Antes de versionar un dataset se debe validar:

- conteos esperados;
- ausencia de errores en quality_report.json;
- tamaños de archivos compatibles con GitHub;
- consistencia de fechas;
- compatibilidad de carga en PostgreSQL cuando aplique.

## Estado actual de referencia

Hito actual del proyecto:

    v1.0.0-125k

Este hito incluye:

- generador Python unificado;
- dataset ampliado de 125.000 clientes;
- validaciones reforzadas;
- reglas operativas por tipo de servicio;
- documentación principal y guía de datasets;
- estructura organizada para PostgreSQL y Power BI.

## Regla operativa del proyecto

A partir de esta guía, todo cambio debe quedar trazable mediante:

- rama descriptiva;
- commit claro;
- Pull Request con título y descripción;
- validación documentada;
- merge hacia main;
- limpieza de ramas temporales.

# Datasets Del Proyecto

Esta carpeta contiene los datasets generados por el proyecto Betek Call Center Analytics.

## Datasets Disponibles

- `_smoke_test_call_center/`: dataset reducido para pruebas rapidas.
- `call_center_analytics_20260410/`: dataset base inicial.
- `call_center_analytics_20260526_125k/`: dataset ampliado de 125.000 clientes.

## Dataset De Prueba

Ruta:

    data/_smoke_test_call_center/

Uso recomendado:

- validar estructura;
- probar carga en PostgreSQL;
- ejecutar consultas rapidas;
- verificar integridad sin usar el dataset completo.

## Dataset Base Inicial

Ruta:

    data/call_center_analytics_20260410/

Metadatos principales:

- `seed`: 20260410
- `history_start_date`: 2025-10-13
- `history_end_date`: 2026-04-11
- `generator_version`: 1.0.0
- `business_rules_version`: 1.0.0

## Dataset Ampliado 125k

Ruta:

    data/call_center_analytics_20260526_125k/

Metadatos principales:

- `seed`: 20260526
- `history_start_date`: 2025-06-01
- `history_end_date`: 2026-05-26
- `clientes`: 125000
- `agentes`: 750
- `llamadas`: 628679
- `casos`: 122211
- `facturas`: 1039992
- `pagos`: 778227
- `encuestas_satisfaccion`: 144356

## Archivos Por Dataset

Cada dataset incluye:

- archivos `.csv` por tabla;
- `load_call_center_postgresql.sql`;
- `quality_report.json`;
- `generation_log.json`;
- `row_counts.csv`.

## Validaciones Del Dataset 125k

El dataset ampliado fue generado con:

- rango historico de `2025-06-01` a `2026-05-26`;
- datos diarios para analisis en Power BI;
- calendarios operativos por tipo de servicio;
- exportacion de textos sin acentos ni `ñ`;
- validaciones reforzadas en `quality_report.json`.

## Carga En PostgreSQL

Ejemplo para dataset ampliado:

    psql -d <tu_base_de_datos> -f .\call_center_analytics_20260526_125k\load_call_center_postgresql.sql


<!-- dataset-125k-postgresql-inicio -->
## Dataset 125k Validado En PostgreSQL

El dataset ampliado se encuentra en:

```text
data/call_center_analytics_20260526_125k/
```

Este dataset fue cargado correctamente en PostgreSQL usando:

```powershell
Set-Location .\data
psql -U postgres -d betek_call_analytics -v ON_ERROR_STOP=1 -f .\call_center_analytics_20260526_125k\load_call_center_postgresql.sql
```

La carga finalizó correctamente con `COMMIT`.

Conteos principales validados:

```text
clientes                  125000
agentes                   750
casos                     122211
llamadas                  628679
facturas                  1039992
pagos                     778227
encuestas_satisfaccion    144356
```

Validaciones técnicas disponibles:

```text
sql/07_validaciones_postgresql_dataset_125k.sql
```

Controles incluidos:

- Conteos principales por tabla.
- Unicidad de correos de clientes usando `lower(email)`.
- Rango de fechas de llamadas.
- Llamadas fuera del rango esperado.
- Casos cerrados antes de su apertura.
- Facturas y pagos con fechas inconsistentes.
- Integridad básica entre tablas principales.
- Cobertura diaria de llamadas.
- Resumen de llamadas por tipo de servicio.
- Validación orientativa de reglas horarias por tipo de servicio.

## Próxima Fase

La siguiente fase será construir consultas SQL para responder las preguntas de negocio del proyecto antes de pasar a Power BI.

Archivo recomendado:

```text
sql/08_preguntas_negocio_dataset_125k.sql
```
<!-- dataset-125k-postgresql-fin -->

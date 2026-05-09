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

    psql -d <tu_base_de_datos> -f data/call_center_analytics_20260526_125k/load_call_center_postgresql.sql


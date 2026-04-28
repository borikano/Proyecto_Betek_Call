# Proyecto Betek Call

Repositorio de datos sintéticos y carga a PostgreSQL para un escenario de analítica de call center.

## Resumen

Este proyecto contiene un paquete de datos generados para modelar una operación de centro de contacto con entidades como clientes, agentes, llamadas, casos, facturas, pagos y encuestas de satisfacción.

El repositorio está pensado para:

- poblar una base de datos PostgreSQL con datos relacionales consistentes;
- validar integridad básica y conteos por tabla;
- servir como base para prácticas de SQL, BI y analítica.

## Contenido

El proyecto incluye dos conjuntos principales:

- `call_center_analytics_20260410/`: conjunto principal de datos.
- `_smoke_test_call_center/`: conjunto reducido para pruebas rápidas.

Cada carpeta contiene:

- archivos `.csv` con los datos por tabla;
- `load_call_center_postgresql.sql` para cargar la información en PostgreSQL;
- `quality_report.json` con validaciones de consistencia;
- `generation_log.json` con metadatos de generación;
- `row_counts.csv` con el resumen de filas por tabla.

## Estructura

- `agentes.csv`, `clientes.csv`, `casos.csv`, `llamadas.csv`, `facturas.csv`, `pagos.csv`: tablas principales del modelo.
- `departamentos.csv`, `equipos_trabajo.csv`, `habilidades.csv`, `turnos.csv`, `tipos_servicio.csv`, `resultados_llamada.csv`: tablas de catálogo y soporte.
- `agente_habilidad.csv`, `agente_turno.csv`, `motivos_llamada.csv`, `productos_servicios_cliente.csv`, `encuestas_satisfaccion.csv`: relaciones y hechos asociados.

## Origen de los datos

Los archivos fueron generados de forma sintética a partir de reglas de negocio y un seed reproducible.

Datos relevantes del conjunto principal:

- `seed`: `20260410`
- `generator_version`: `1.0.0`
- `business_rules_version`: `1.0.0`
- `history_start_date`: `2025-10-13`
- `history_end_date`: `2026-04-11`
- `generated_at`: `2026-04-11T00:15:23`

## Carga en PostgreSQL

El script `load_call_center_postgresql.sql` realiza estas acciones:

1. limpia las tablas destino con `TRUNCATE`;
2. crea tablas temporales de staging;
3. carga los CSV con `\copy`;
4. inserta los datos en el esquema `call_center_analytics`;
5. reajusta secuencias con `setval`.

### Requisitos

- PostgreSQL accesible con el esquema `call_center_analytics` ya creado.
- Permisos para ejecutar `TRUNCATE`, `COPY` y `INSERT`.

### Importante

El loader usa rutas absolutas de Windows. Si mueves el repositorio de carpeta o lo clonas en otra ruta, debes actualizar las rutas dentro del SQL antes de ejecutarlo.

### Ejecución

```bash
psql -d <tu_base_de_datos> -f call_center_analytics_20260410/load_call_center_postgresql.sql
```

## Calidad de datos

El archivo `quality_report.json` del conjunto principal reporta validaciones exitosas, incluyendo:

- unicidad de claves primarias;
- integridad referencial básica;
- ausencia de registros inválidos en las relaciones verificadas.

## Recomendaciones

- Mantener fuera del control de versiones los entornos virtuales y artefactos del sistema operativo.
- Conservar los conjuntos principal y de smoke test separados para facilitar pruebas.
- Si regeneras datos, documenta el nuevo `seed` y la fecha de generación.

## Licencia

No se ha definido una licencia en este repositorio. Si vas a publicarlo de forma abierta, conviene añadir una antes de compartirlo.

# Proyecto Betek Call

Repositorio de datos sintéticos para un escenario de analítica de call center con carga a PostgreSQL.

## Propósito

Este proyecto fue preparado para practicar y demostrar:

- modelado relacional aplicado a una operación de contact center;
- carga reproducible de datos en PostgreSQL;
- validación básica de calidad e integridad;
- análisis exploratorio, SQL y BI sobre un dataset consistente.

## Lo Que Incluye

El repositorio contiene dos entregables:

- `call_center_analytics_20260410/`: dataset principal.
- `_smoke_test_call_center/`: versión reducida para pruebas rápidas.

Cada conjunto incluye:

- archivos `.csv` por tabla;
- `load_call_center_postgresql.sql` para poblar el esquema `call_center_analytics`;
- `quality_report.json` con validaciones;
- `generation_log.json` con metadatos de generación;
- `row_counts.csv` con conteos de filas.

## Modelo De Datos

Entidades principales:

- `clientes`
- `agentes`
- `casos`
- `llamadas`
- `facturas`
- `pagos`

Tablas de soporte y catálogo:

- `departamentos`
- `equipos_trabajo`
- `habilidades`
- `turnos`
- `tipos_servicio`
- `resultados_llamada`

Relaciones y tablas derivadas:

- `agente_habilidad`
- `agente_turno`
- `motivos_llamada`
- `productos_servicios_cliente`
- `encuestas_satisfaccion`

## Datos Y Calidad

El conjunto principal fue generado con estos metadatos:

- `seed`: `20260410`
- `generator_version`: `1.0.0`
- `business_rules_version`: `1.0.0`
- `history_start_date`: `2025-10-13`
- `history_end_date`: `2026-04-11`
- `generated_at`: `2026-04-11T00:15:23`

El reporte de calidad valida:

- unicidad de claves primarias;
- integridad referencial en las relaciones verificadas;
- ausencia de registros inválidos en los controles aplicados.

## Estructura Recomendada Del Repo

- `README.md`: guía principal del proyecto.
- `.gitignore`: exclusiones del entorno local y artefactos del sistema.
- `call_center_analytics_20260410/`: dataset listo para carga productiva.
- `_smoke_test_call_center/`: dataset pequeño para pruebas.

## Cómo Cargar Los Datos

El script de carga ejecuta el siguiente flujo:

1. `TRUNCATE` de tablas destino.
2. Creación de tablas temporales de staging.
3. Carga de CSV con `\copy`.
4. Inserción en el esquema `call_center_analytics`.
5. Ajuste de secuencias con `setval`.

### Requisitos

- PostgreSQL disponible.
- Esquema `call_center_analytics` creado previamente.
- Permisos para `TRUNCATE`, `COPY` e `INSERT`.

### Ejecución

Ejecuta el comando desde la raíz del repositorio:

```bash
psql -d <tu_base_de_datos> -f call_center_analytics_20260410/load_call_center_postgresql.sql
```

Para pruebas rápidas:

```bash
psql -d <tu_base_de_datos> -f _smoke_test_call_center/load_call_center_postgresql.sql
```

## Buenas Prácticas Aplicadas

- Entornos locales excluidos con `.gitignore`.
- Dataset principal y smoke test separados.
- Documentación de origen, propósito y validación.
- Carga basada en archivos versionados dentro del repositorio.

## Nota Sobre Portabilidad

Los loaders usan rutas relativas al repositorio. Eso hace que el proyecto sea más fácil de clonar y ejecutar en otra máquina, siempre que se lance el script desde la raíz del repo.

## Licencia

No se ha definido una licencia aún. Si el repositorio se va a compartir públicamente, conviene añadir una antes de ampliar su difusión.

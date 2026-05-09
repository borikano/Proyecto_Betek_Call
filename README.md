# Proyecto Betek Call Center Analytics

Repositorio de datos sintéticos para un escenario de analítica de call center con carga a PostgreSQL, análisis en Python y visualización en Power BI.

## Propósito

Este proyecto fue preparado para practicar y demostrar:

- modelado relacional aplicado a una operación de contact center;
- generación reproducible de datos sintéticos;
- carga de datos en PostgreSQL;
- validación de calidad e integridad;
- análisis exploratorio con SQL, Python y BI;
- construcción de indicadores sobre llamadas, casos, clientes, agentes, facturación, pagos y satisfacción.

## Estructura Del Proyecto

La estructura actual del repositorio es:

    PROYECTO_MAESTRO/
    ├─ docs/
    │  ├─ Documentos_Maestros/
    │  └─ 07_guia_generador_datos.md
    ├─ sql/
    │  └─ 06_ddl_sql_creacion_tablas.sql
    ├─ src/
    │  ├─ generador_datos_sinteticos_call_center.py
    │  └─ generador_datos_sinteticos_call_center_125k.py
    ├─ data/
    │  ├─ _smoke_test_call_center/
    │  └─ call_center_analytics_20260410/
    ├─ scripts/
    ├─ tests/
    ├─ requirements.txt
    ├─ .gitignore
    ├─ .gitattributes
    └─ README.md

## Carpetas Principales

- `docs/`: documentación funcional, técnica y guía del generador.
- `sql/`: DDL oficial de creación de tablas en PostgreSQL.
- `src/`: código Python del generador de datos sintéticos.
- `data/`: datasets generados y dataset reducido de prueba.
- `scripts/`: comandos auxiliares para generación de datasets.
- `tests/`: espacio reservado para pruebas automáticas y validaciones futuras.

## Modelo De Datos

El modelo SQL oficial se encuentra en:

    sql/06_ddl_sql_creacion_tablas.sql

El modelo actual se mantiene estable. En esta fase no se agregan ni se eliminan tablas.

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

## Generador Python

El generador principal se encuentra en:

    src/generador_datos_sinteticos_call_center.py

Uso base:

    python .\src\generador_datos_sinteticos_call_center.py --output-dir .\data\salida_prueba

El generador produce:

- un archivo `.csv` por tabla;
- `load_call_center_postgresql.sql`;
- `quality_report.json`;
- `generation_log.json`;
- `row_counts.csv`.

## Dataset Base

El dataset base versionado se encuentra en:

    data/call_center_analytics_20260410/

Metadatos principales:

- `seed`: `20260410`
- `generator_version`: `1.0.0`
- `business_rules_version`: `1.0.0`
- `history_start_date`: `2025-10-13`
- `history_end_date`: `2026-04-11`
- `generated_at`: `2026-04-11T00:15:23`

## Dataset De Prueba

El dataset reducido para pruebas rápidas se encuentra en:

    data/_smoke_test_call_center/

Sirve para validar carga, estructura y consultas sin usar el dataset completo.

## Cómo Cargar Los Datos En PostgreSQL

El script de carga ejecuta el siguiente flujo:

1. `TRUNCATE` de tablas destino.
2. Creación de tablas temporales de staging.
3. Carga de CSV con `\copy`.
4. Inserción en el esquema `call_center_analytics`.
5. Ajuste de secuencias con `setval`.

### Requisitos

- PostgreSQL 15+.
- Esquema `call_center_analytics` creado previamente.
- Permisos para `TRUNCATE`, `COPY` e `INSERT`.

### Cargar Dataset Base

Ejecutar desde la raíz del repositorio:

    psql -d <tu_base_de_datos> -f data/call_center_analytics_20260410/load_call_center_postgresql.sql

### Cargar Dataset De Prueba

    psql -d <tu_base_de_datos> -f data/_smoke_test_call_center/load_call_center_postgresql.sql

## Entorno Python

Crear entorno virtual:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

Instalar dependencias:

    pip install -r requirements.txt

Dependencias principales:

- NumPy
- Pandas

## Buenas Prácticas Del Repositorio

El repositorio excluye:

- entornos virtuales `.venv/`;
- archivos `__pycache__/`;
- archivos `desktop.ini`;
- archivos temporales;
- archivos `.fixed.csv*`;
- artefactos locales del sistema operativo.

La configuración está definida en:

- `.gitignore`
- `.gitattributes`
- `requirements.txt`

## Dataset Ampliado 125k

El dataset ampliado se encuentra en:

    data/call_center_analytics_20260526_125k/

Caracteristicas principales:

- 125.000 clientes.
- Trazabilidad desde `2025-06-01` hasta `2026-05-26`.
- Datos diarios para analisis en Power BI.
- Reglas horarias por tipo de servicio.
- Validaciones reforzadas de calidad.
- Textos exportados sin acentos ni `ñ` para mejorar compatibilidad con Excel, PostgreSQL y Power BI.

Conteos principales:

- `clientes`: 125000
- `agentes`: 750
- `llamadas`: 628679
- `casos`: 122211
- `facturas`: 1039992
- `pagos`: 778227
- `encuestas_satisfaccion`: 144356

Validaciones realizadas:

- Sin validaciones fallidas en `quality_report.json`.
- Sin archivos mayores a 95 MB.
- Sin acentos ni `ñ` en los CSV exportados.
- Rango historico confirmado: `2025-06-01` a `2026-05-26`.

## Reglas Operativas Objetivo

Para la generación ampliada se consideran las siguientes reglas:

- Ventas y telemarketing: lunes a sábado, de 09:00 a 19:00.
- Soporte técnico: operación 24/7.
- Atención al cliente: todos los días, de 07:00 a 21:00.
- Facturación: lunes a sábado, en horario operativo definido para el proyecto.

## Nota Sobre Portabilidad

Los loaders usan rutas relativas al repositorio. Esto permite clonar el proyecto y ejecutar los scripts desde otra máquina, siempre que se lancen desde la raíz del repositorio.

## Estado Actual y Siguientes Pasos

Version de referencia del proyecto:

    v1.0.0-125k

Esta version incluye:

- estructura reorganizada del repositorio;
- generador Python unificado;
- dataset base inicial;
- dataset ampliado de 125.000 clientes;
- rango historico desde `2025-06-01` hasta `2026-05-26`;
- validaciones reforzadas de calidad;
- reglas operativas por tipo de servicio;
- script reproducible para generar el dataset ampliado;
- documentacion actualizada para trabajo en VSCode, GitHub, PostgreSQL y Power BI.

## Datasets Disponibles

El repositorio contiene tres conjuntos principales:

- `data/_smoke_test_call_center/`: dataset reducido para pruebas rapidas.
- `data/call_center_analytics_20260410/`: dataset base inicial.
- `data/call_center_analytics_20260526_125k/`: dataset ampliado de 125.000 clientes.

## Dataset 125k

El dataset ampliado tiene los siguientes conteos principales:

- `clientes`: 125000
- `agentes`: 750
- `llamadas`: 628679
- `casos`: 122211
- `facturas`: 1039992
- `pagos`: 778227
- `encuestas_satisfaccion`: 144356

Validaciones realizadas:

- sin validaciones fallidas en `quality_report.json`;
- sin archivos mayores a 95 MB;
- sin acentos ni `ñ` en los CSV exportados;
- fechas dentro del rango historico definido;
- reglas horarias aplicadas por tipo de servicio.

## Reglas Operativas Aplicadas

- Ventas y telemarketing: lunes a sabado, de 09:00 a 19:00.
- Soporte tecnico: operacion 24/7.
- Atencion al cliente: todos los dias, de 07:00 a 21:00.
- Facturacion: lunes a sabado, en horario operativo definido para el proyecto.

## Proximas Fases

1. Crear la base de datos en PostgreSQL.
2. Ejecutar el DDL oficial desde `sql/06_ddl_sql_creacion_tablas.sql`.
3. Cargar el dataset ampliado `data/call_center_analytics_20260526_125k/`.
4. Validar integridad, conteos y reglas desde PostgreSQL.
5. Conectar Power BI al modelo relacional.
6. Construir modelo semantico, medidas DAX y dashboards.


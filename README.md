# Proyecto Betek Call Center Analytics

Repositorio de datos sinteticos para un escenario de analitica de call center con carga a PostgreSQL, analisis en Python y visualizacion en Power BI.

## Estado Actual

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
- documentacion preparada para VSCode, GitHub, PostgreSQL y Power BI.

## Proposito

Este proyecto fue preparado para practicar y demostrar:

- modelado relacional aplicado a una operacion de contact center;
- generacion reproducible de datos sinteticos;
- carga de datos en PostgreSQL;
- validacion de calidad e integridad;
- analisis exploratorio con SQL, Python y BI;
- construccion de indicadores sobre llamadas, casos, clientes, agentes, facturacion, pagos y satisfaccion.

## Estructura Del Proyecto

La estructura actual del repositorio es:

    PROYECTO_MAESTRO/
    ├─ data/
    │  ├─ README.md
    │  ├─ _smoke_test_call_center/
    │  ├─ call_center_analytics_20260410/
    │  └─ call_center_analytics_20260526_125k/
    ├─ docs/
    │  ├─ Documentos_Maestros/
    │  └─ 07_guia_generador_datos.md
    ├─ scripts/
    │  └─ generar_dataset_125k.ps1
    ├─ sql/
    │  └─ 06_ddl_sql_creacion_tablas.sql
    ├─ src/
    │  └─ generador_datos_sinteticos_call_center.py
    ├─ tests/
    ├─ README.md
    ├─ requirements.txt
    ├─ .gitignore
    └─ .gitattributes

## Carpetas Principales

- `data/`: datasets generados y dataset reducido de prueba.
- `docs/`: documentacion funcional, tecnica y guia del generador.
- `scripts/`: comandos auxiliares para generacion de datasets.
- `sql/`: DDL oficial de creacion de tablas en PostgreSQL.
- `src/`: codigo Python del generador de datos sinteticos.
- `tests/`: espacio reservado para pruebas automaticas y validaciones futuras.

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

Tablas de soporte y catalogo:

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

## Script Dataset 125k

El script de generacion del dataset ampliado se encuentra en:

    scripts/generar_dataset_125k.ps1

Ejecutar desde la raiz del repositorio:

    .\scripts\generar_dataset_125k.ps1

## Datasets Disponibles

El detalle de los datasets se encuentra en:

    data/README.md

Resumen:

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

## Como Cargar Los Datos En PostgreSQL

El script de carga ejecuta el siguiente flujo:

1. `TRUNCATE` de tablas destino.
2. Creacion de tablas temporales de staging.
3. Carga de CSV con `\copy`.
4. Insercion en el esquema `call_center_analytics`.
5. Ajuste de secuencias con `setval`.

### Requisitos

- PostgreSQL 15+.
- Esquema `call_center_analytics` creado previamente.
- Permisos para `TRUNCATE`, `COPY` e `INSERT`.

### Cargar Dataset 125k

Ejecutar desde la raiz del repositorio:

    psql -d <tu_base_de_datos> -f data/call_center_analytics_20260526_125k/load_call_center_postgresql.sql

### Cargar Dataset Base

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

## Buenas Practicas Del Repositorio

El repositorio excluye:

- entornos virtuales `.venv/`;
- archivos `__pycache__/`;
- archivos `desktop.ini`;
- archivos temporales;
- archivos `.fixed.csv*`;
- artefactos locales del sistema operativo.

La configuracion esta definida en:

- `.gitignore`
- `.gitattributes`
- `requirements.txt`

## Nota Sobre Portabilidad

Los loaders usan rutas relativas al repositorio. Esto permite clonar el proyecto y ejecutar los scripts desde otra maquina, siempre que se lancen desde la raiz del repositorio.

## Proximas Fases

1. Crear la base de datos en PostgreSQL.
2. Ejecutar el DDL oficial desde `sql/06_ddl_sql_creacion_tablas.sql`.
3. Cargar el dataset ampliado `data/call_center_analytics_20260526_125k/`.
4. Validar integridad, conteos y reglas desde PostgreSQL.
5. Conectar Power BI al modelo relacional.
6. Construir modelo semantico, medidas DAX y dashboards.


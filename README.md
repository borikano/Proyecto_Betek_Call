# Betek Call Center Analytics

Proyecto analítico orientado a construir un flujo completo de datos para un caso de negocio de call center: generación de datos sintéticos, carga en PostgreSQL, validación SQL, análisis en Python y preparación del reporte final en Power BI.

El objetivo principal es mantener trazabilidad técnica y analítica en cada fase del proyecto, evitando pasos manuales no documentados y dejando evidencia clara de qué se hizo, por qué se hizo y qué componentes fueron afectados.

## Estado Actual Del Proyecto

El proyecto ya cuenta con las siguientes fases completadas:

- Dataset sintético ampliado a 125.000 clientes.
- Carga exitosa en PostgreSQL sobre la base `betek_call_analytics`.
- Validaciones técnicas en SQL para integridad, rangos de fechas, duplicados y consistencia entre tablas.
- Consultas SQL para responder las preguntas iniciales de negocio.
- Evidencias analíticas en Python con resultados tabulares y gráficos.
- Documentación del flujo `SQL -> Python -> Power BI`.

La siguiente fase del proyecto es construir el modelo y el reporte en Power BI.

## Estructura Actual Del Repositorio

- `README.md`: documentación principal del proyecto.
- `requirements.txt`: dependencias base del entorno Python.
- `.gitignore`: reglas de exclusión del repositorio.
- `.gitattributes`: reglas de normalización de archivos.
- `data/`: datasets generados y documentación de datos.
- `docs/`: documentación técnica y de trazabilidad.
- `sql/`: validaciones SQL y consultas de negocio.
- `scripts/`: scripts auxiliares de generación, análisis y automatización.
- `src/`: código fuente principal del generador de datos sintéticos.
- `outputs/`: evidencias analíticas generadas desde Python.
- `tests/`: espacio reservado para pruebas del proyecto.

## Carpetas Principales

### `data/`

Contiene los datasets generados y sus archivos asociados.

Datasets relevantes:

- `data/_smoke_test_call_center/`: dataset pequeño usado para pruebas iniciales.
- `data/call_center_analytics_20260410/`: versión previa del dataset.
- `data/call_center_analytics_20260526_125k/`: dataset ampliado y utilizado en la fase actual.

También contiene `data/README.md`, donde se documenta el uso de los datasets y la forma correcta de ejecutar cargas desde la carpeta `data/`.

### `docs/`

Contiene documentación técnica y de trazabilidad del proyecto.

Documentos principales:

- `docs/guia_versionamiento.md`: reglas de versionamiento, nombres de ramas, commits y Pull Requests.
- `docs/flujo_sql_python_powerbi.md`: flujo de trabajo desde PostgreSQL hasta Power BI.

### `sql/`

Contiene consultas SQL versionadas para validación y análisis.

Archivos principales:

- `sql/07_validaciones_postgresql_dataset_125k.sql`: validaciones técnicas del dataset cargado en PostgreSQL.
- `sql/08_preguntas_negocio_dataset_125k.sql`: consultas SQL iniciales para responder preguntas de negocio.

### `scripts/`

Contiene scripts ejecutables desde terminal.

Archivos principales:

- `scripts/generar_dataset_125k.ps1`: script auxiliar para generación del dataset ampliado.
- `scripts/analizar_preguntas_negocio_125k.py`: script Python que consulta PostgreSQL y genera evidencias analíticas.

### `src/`

Contiene el código fuente principal del generador de datos sintéticos.

Archivo principal:

- `src/generador_datos_sinteticos_call_center.py`

### `outputs/`

Contiene resultados generados por procesos analíticos.

Directorio principal:

- `outputs/evidencias_preguntas_negocio_125k/`

Este directorio contiene:

- 9 archivos CSV con resultados tabulares.
- 9 archivos PNG con gráficos de evidencia.

## Flujo De Trabajo Analítico

El flujo actual del proyecto es:

1. Generar o preparar dataset sintético.
2. Cargar datos en PostgreSQL.
3. Validar integridad y consistencia con SQL.
4. Construir consultas SQL para preguntas de negocio.
5. Ejecutar análisis en Python.
6. Generar evidencias CSV y PNG.
7. Construir modelo y dashboard en Power BI.

Regla de trazabilidad:

- `SQL validado -> Python con CSV/PNG -> Power BI`

## Base De Datos PostgreSQL

Base utilizada:

- `betek_call_analytics`

Esquema principal:

- `call_center_analytics`

Tablas principales:

- `clientes`
- `agentes`
- `departamentos`
- `tipos_servicio`
- `motivos_llamada`
- `resultados_llamada`
- `llamadas`
- `casos`
- `facturas`
- `pagos`
- `encuestas_satisfaccion`

Conteos de referencia validados:

- `clientes`: 125.000
- `agentes`: 750
- `casos`: 122.211
- `llamadas`: 628.679
- `facturas`: 1.039.992
- `pagos`: 778.227
- `encuestas_satisfaccion`: 144.356

## Evidencias Analíticas En Python

La fase de evidencias en Python ya fue construida y versionada antes de iniciar el reporte en Power BI.

Archivo principal:

- `scripts/analizar_preguntas_negocio_125k.py`

Salida generada:

- `outputs/evidencias_preguntas_negocio_125k/`

Contenido generado:

- 9 archivos CSV con resultados tabulares para las preguntas de negocio.
- 9 archivos PNG con gráficos de evidencia analítica.
- Gráficas con títulos, ejes y leyendas revisadas.
- Resultados generados desde PostgreSQL usando la base `betek_call_analytics`.

Esta fase permite validar los resultados antes de construir el modelo semántico y los dashboards en Power BI.

## Preguntas De Negocio Cubiertas

Las evidencias actuales responden inicialmente a las siguientes preguntas de negocio:

1. Motivos de llamadas más frecuentes.
2. Llamadas entrantes y salientes por mes.
3. Motivos frecuentes y tiempo promedio de atención.
4. Franjas horarias y días con mayor volumen.
5. Clientes con múltiples llamadas por caso no resuelto en primer contacto.
6. Desempeño de agentes.
7. Clientes con facturas vencidas o pagos pendientes.
8. Departamentos con mayor tiempo promedio o menor tasa de resolución.
9. Satisfacción por agente y tipo de servicio.

## Convenciones Del Proyecto

Para documentación:

- Se debe usar redacción clara, buena ortografía y acentos.
- Las descripciones deben explicar qué se hizo, por qué se hizo y qué componentes afecta.

Para código, SQL, CSV, rutas y datos técnicos:

- Se prioriza compatibilidad técnica.
- Se recomiendan nombres seguros, consistentes y sin caracteres que puedan causar problemas de codificación.

Para versionamiento:

- No se deben crear ramas, commits, Pull Requests o tags con nombres genéricos o descripciones vacías.
- Cada cambio debe indicar propósito, contexto y validación.

## Próxima Fase: Power BI

La siguiente fase consiste en construir el reporte en Power BI usando PostgreSQL como fuente principal.

Actividades previstas:

- Cargar tablas desde PostgreSQL.
- Validar relaciones del modelo.
- Crear tabla calendario.
- Crear medidas DAX base.
- Construir páginas del reporte.
- Comparar resultados del dashboard con las evidencias SQL y Python.

Nombre sugerido para el archivo Power BI:

- `powerbi/betek_call_center_analytics.pbix`

## Nota

Este README representa el estado actual del proyecto después de completar la fase SQL y la fase Python. Power BI se construirá sobre las validaciones y evidencias ya generadas.

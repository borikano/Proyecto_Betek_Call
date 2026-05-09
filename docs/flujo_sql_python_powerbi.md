# Flujo SQL, Python y Power BI

## Propósito

Este documento define el flujo de trabajo analítico del proyecto **Betek Call Center Analytics**, desde la validación en PostgreSQL hasta la construcción del reporte final en Power BI.

El objetivo es asegurar trazabilidad, evidencia reproducible y orden profesional en cada fase del análisis.

## Regla Principal

Antes de construir visualizaciones finales en Power BI, cada pregunta de negocio debe pasar por tres etapas previas:

1. Consulta SQL validada en PostgreSQL.
2. Resultado consultado, procesado o exportado desde Python.
3. Gráfico generado en Python como evidencia analítica.

Power BI se utiliza después de validar que las consultas, resultados y gráficos preliminares responden correctamente las preguntas de negocio.

## Flujo General

```text
PostgreSQL
   |
   v
Consultas SQL de negocio
   |
   v
Python para análisis y evidencia gráfica
   |
   v
Validación de resultados
   |
   v
Modelo y dashboard en Power BI
```

## Fase 1: PostgreSQL

La fase SQL tiene como objetivo responder inicialmente las preguntas de negocio directamente sobre la base de datos.

Archivo principal:

```text
sql/08_preguntas_negocio_dataset_125k.sql
```

Cada consulta debe indicar la pregunta que responde, las tablas utilizadas, los campos principales, el criterio de agrupación o cálculo y si será base para una visualización posterior.

Las consultas exploratorias deben limitar la salida para evitar saturar la terminal. Como regla inicial, se utilizarán muestras de 10 filas cuando aplique.

## Fase 2: Python

La fase Python tiene como objetivo generar evidencia analítica reproducible antes de Power BI.

Archivo recomendado:

```text
scripts/analizar_preguntas_negocio_125k.py
```

Carpeta recomendada para evidencias:

```text
outputs/evidencias_preguntas_negocio_125k/
```

Cada pregunta de negocio debe generar, cuando aplique, un resultado tabular y un gráfico:

```text
NN_nombre_descriptivo.csv
NN_nombre_descriptivo.png
```

Ejemplos:

```text
01_motivos_llamadas_frecuentes.csv
01_motivos_llamadas_frecuentes.png
02_llamadas_por_mes_tipo.csv
02_llamadas_por_mes_tipo.png
```

Los archivos CSV sirven como evidencia tabular y los PNG como evidencia visual.

## Fase 3: Validación De Evidencias

Antes de pasar a Power BI, se debe validar que:

- la consulta SQL se ejecuta sin errores;
- los resultados en Python coinciden con PostgreSQL;
- los gráficos representan correctamente la pregunta de negocio;
- los nombres de archivos son claros y trazables;
- las salidas no contienen datos corruptos, duplicados inesperados o valores inconsistentes;
- las conclusiones preliminares están alineadas con los resultados.

## Fase 4: Power BI

Power BI se utiliza solo después de validar SQL y Python.

En Power BI se deben construir:

- modelo relacional;
- relaciones entre tablas;
- medidas DAX;
- visualizaciones finales;
- filtros y segmentadores;
- reporte ejecutivo.

Power BI no reemplaza la validación previa en SQL ni la evidencia gráfica generada en Python.

## Preguntas De Negocio Base

Las preguntas de negocio que deben seguir este flujo son:

1. ¿Cuáles son los motivos de llamadas más frecuentes?
2. ¿Cuántas llamadas entrantes y salientes se registran por mes?
3. ¿Cuáles son los motivos de llamadas más frecuentes y cuál es el tiempo promedio de atención para cada solicitud?
4. ¿En qué franjas horarias y días de la semana se concentra la mayor cantidad de llamadas?
5. ¿Cuántos clientes realizaron múltiples llamadas por un mismo caso por mes, debido a que no fue resuelto en el primer contacto?
6. ¿Qué agentes presentan mayor desempeño según cantidad de llamadas atendidas, tiempo promedio de atención y satisfacción del cliente?
7. ¿Qué clientes presentan facturas vencidas o pagos pendientes?
8. ¿Qué departamento presenta mayor tiempo promedio de atención o menor tasa de resolución?
9. ¿Cuál es el nivel de satisfacción del cliente después de la atención y cómo varía según el agente o el tipo de servicio?

## Convención De Nombres

Para mantener trazabilidad, los archivos deben seguir una numeración consistente:

```text
01_motivos_llamadas_frecuentes
02_llamadas_por_mes_tipo
03_motivos_tiempo_promedio
04_franjas_horarias_dias
05_recontacto_por_caso
06_desempeno_agentes
07_facturas_vencidas_pagos_pendientes
08_desempeno_departamentos
09_satisfaccion_cliente
```

La numeración debe coincidir entre SQL, Python, evidencias y visualizaciones de Power BI.

## Buenas Prácticas De Documentación

La documentación debe escribirse con buena ortografía, acentos y redacción clara.

Para código, nombres de archivos, tablas, columnas, CSV, SQL y rutas técnicas, se debe priorizar compatibilidad técnica. En esos casos se recomienda usar nombres seguros, en minúscula, sin espacios y preferiblemente sin acentos.

En resumen:

- documentación: redacción cuidada, con acentos y buena ortografía;
- código y datos técnicos: consistencia, compatibilidad y nombres seguros para sistemas.

## Trazabilidad En Git

Cada cambio debe quedar versionado mediante una rama, commit y Pull Request.

No se deben crear ramas, commits, Pull Requests o tags con nombres genéricos o descripciones vacías.

Cada Pull Request debe explicar:

- qué se hizo;
- por qué se hizo;
- qué archivos o componentes afecta;
- cómo se validó;
- si modifica o no el modelo SQL;
- si afecta datasets versionados;
- si genera evidencias nuevas.

## Criterio Para Avanzar A Power BI

Se puede avanzar a Power BI cuando existan:

- consultas SQL versionadas para las preguntas de negocio;
- resultados validados en PostgreSQL;
- script Python de análisis;
- evidencias CSV y PNG generadas;
- revisión de consistencia entre SQL y Python;
- documentación actualizada del flujo.

## Nota

Este flujo busca que el reporte final en Power BI no sea solo visual, sino respaldado por consultas SQL, resultados reproducibles y evidencia gráfica previa.

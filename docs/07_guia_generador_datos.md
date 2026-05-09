# 07_generador_datos_sinteticos_python.py

Generador de datos sintéticos históricos para el proyecto de call center.

## Qué produce
- Un CSV por tabla del modelo relacional
- `row_counts.csv`
- `quality_report.json`
- `generation_log.json`

## Uso base
```bash
python 07_generador_datos_sinteticos_python.py --output-dir ./output_call_center
```

## Uso para pruebas pequeñas
```bash
python 07_generador_datos_sinteticos_python.py   --output-dir ./salida_prueba   --clients 500   --agents 30   --history-months 2   --calls-target-min 2000   --calls-target-max 2500   --cases-target-min 500   --cases-target-max 700   --products-target-min 700   --products-target-max 900   --invoices-target-min 900   --invoices-target-max 1200   --payments-target-min 700   --payments-target-max 1000   --surveys-target-min 400   --surveys-target-max 600
```

## Mejores prácticas incorporadas
- seed reproducible
- un CSV por tabla
- FCR derivado del historial de llamadas por caso
- ventas solo en contextos comerciales válidos
- validaciones de PK, FK, fechas y reglas de negocio
- exportación de reporte de calidad

## Notas
- El script está diseñado para alimentar SQL y análisis en Python.
- Si se reducen mucho clientes o agentes, conviene también bajar los objetivos de volumen.

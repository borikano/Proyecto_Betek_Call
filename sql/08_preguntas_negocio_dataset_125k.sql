-- Preguntas de negocio para dataset 125k
-- Proyecto Betek Call Center Analytics
-- Base: betek_call_analytics
-- Esquema: call_center_analytics
-- Objetivo: responder inicialmente en SQL las preguntas de negocio antes de Power BI.

SET search_path TO call_center_analytics;

-- ============================================================
-- 1. Cuales son los motivos de llamadas mas frecuentes?
-- ============================================================

SELECT
    ml.id_motivo,
    ml.nombre_motivo,
    ts.nombre_servicio,
    COUNT(*) AS total_llamadas,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje_total
FROM llamadas l
JOIN motivos_llamada ml ON ml.id_motivo = l.id_motivo
JOIN tipos_servicio ts ON ts.id_tipo_servicio = l.id_tipo_servicio
GROUP BY ml.id_motivo, ml.nombre_motivo, ts.nombre_servicio
ORDER BY total_llamadas DESC, ml.id_motivo
LIMIT 10;


-- ============================================================
-- 2. Cuantas llamadas entrantes y salientes se registran por mes?
-- ============================================================

SELECT
    date_trunc('month', fecha_hora_inicio)::date AS mes,
    COUNT(*) AS total_llamadas,
    COUNT(*) FILTER (WHERE tipo_llamada = 'entrante') AS llamadas_entrantes,
    COUNT(*) FILTER (WHERE tipo_llamada = 'saliente') AS llamadas_salientes
FROM llamadas
GROUP BY date_trunc('month', fecha_hora_inicio)::date
ORDER BY mes
LIMIT 10;


-- ============================================================
-- 3. Motivos mas frecuentes y tiempo promedio de atencion.
-- ============================================================

SELECT
    ml.id_motivo,
    ml.nombre_motivo,
    ts.nombre_servicio,
    COUNT(*) AS total_llamadas,
    ROUND(AVG(l.duracion_segundos)::numeric, 2) AS duracion_promedio_segundos,
    ROUND((AVG(l.duracion_segundos) / 60.0)::numeric, 2) AS duracion_promedio_minutos,
    ROUND(AVG(l.tiempo_espera_segundos)::numeric, 2) AS espera_promedio_segundos
FROM llamadas l
JOIN motivos_llamada ml ON ml.id_motivo = l.id_motivo
JOIN tipos_servicio ts ON ts.id_tipo_servicio = l.id_tipo_servicio
GROUP BY ml.id_motivo, ml.nombre_motivo, ts.nombre_servicio
ORDER BY total_llamadas DESC, duracion_promedio_segundos DESC
LIMIT 10;


-- ============================================================
-- 4. En que franjas horarias y dias se concentra la mayor cantidad de llamadas?
-- ============================================================

SELECT
    CASE EXTRACT(ISODOW FROM fecha_hora_inicio)
        WHEN 1 THEN 'lunes'
        WHEN 2 THEN 'martes'
        WHEN 3 THEN 'miercoles'
        WHEN 4 THEN 'jueves'
        WHEN 5 THEN 'viernes'
        WHEN 6 THEN 'sabado'
        WHEN 7 THEN 'domingo'
    END AS dia_semana,
    EXTRACT(ISODOW FROM fecha_hora_inicio)::int AS orden_dia,
    CASE
        WHEN fecha_hora_inicio::time >= TIME '00:00:00' AND fecha_hora_inicio::time < TIME '06:00:00' THEN 'madrugada'
        WHEN fecha_hora_inicio::time >= TIME '06:00:00' AND fecha_hora_inicio::time < TIME '12:00:00' THEN 'manana'
        WHEN fecha_hora_inicio::time >= TIME '12:00:00' AND fecha_hora_inicio::time < TIME '18:00:00' THEN 'tarde'
        ELSE 'noche'
    END AS franja_horaria,
    COUNT(*) AS total_llamadas,
    ROUND(AVG(duracion_segundos)::numeric, 2) AS duracion_promedio_segundos,
    ROUND(AVG(tiempo_espera_segundos)::numeric, 2) AS espera_promedio_segundos
FROM llamadas
GROUP BY
    EXTRACT(ISODOW FROM fecha_hora_inicio),
    CASE EXTRACT(ISODOW FROM fecha_hora_inicio)
        WHEN 1 THEN 'lunes'
        WHEN 2 THEN 'martes'
        WHEN 3 THEN 'miercoles'
        WHEN 4 THEN 'jueves'
        WHEN 5 THEN 'viernes'
        WHEN 6 THEN 'sabado'
        WHEN 7 THEN 'domingo'
    END,
    CASE
        WHEN fecha_hora_inicio::time >= TIME '00:00:00' AND fecha_hora_inicio::time < TIME '06:00:00' THEN 'madrugada'
        WHEN fecha_hora_inicio::time >= TIME '06:00:00' AND fecha_hora_inicio::time < TIME '12:00:00' THEN 'manana'
        WHEN fecha_hora_inicio::time >= TIME '12:00:00' AND fecha_hora_inicio::time < TIME '18:00:00' THEN 'tarde'
        ELSE 'noche'
    END
ORDER BY total_llamadas DESC, orden_dia, franja_horaria
LIMIT 10;


-- ============================================================
-- 5. Clientes con multiples llamadas por un mismo caso por mes,
--    cuando no se resolvio en primer contacto.
-- ============================================================

SELECT
    date_trunc('month', l.fecha_hora_inicio)::date AS mes,
    l.id_cliente,
    l.id_caso,
    c.estado_caso,
    c.resuelto_primer_contacto,
    COUNT(*) AS total_llamadas_caso,
    MIN(l.fecha_hora_inicio) AS primera_llamada,
    MAX(l.fecha_hora_inicio) AS ultima_llamada
FROM llamadas l
JOIN casos c ON c.id_caso = l.id_caso
WHERE l.id_caso IS NOT NULL
  AND c.resuelto_primer_contacto = false
GROUP BY
    date_trunc('month', l.fecha_hora_inicio)::date,
    l.id_cliente,
    l.id_caso,
    c.estado_caso,
    c.resuelto_primer_contacto
HAVING COUNT(*) > 1
ORDER BY mes, total_llamadas_caso DESC, l.id_cliente
LIMIT 10;


-- Resumen mensual de clientes con multiples llamadas por caso.
SELECT
    mes,
    COUNT(DISTINCT id_cliente) AS clientes_con_recontacto,
    COUNT(DISTINCT id_caso) AS casos_con_recontacto,
    SUM(total_llamadas_caso) AS llamadas_asociadas
FROM (
    SELECT
        date_trunc('month', l.fecha_hora_inicio)::date AS mes,
        l.id_cliente,
        l.id_caso,
        COUNT(*) AS total_llamadas_caso
    FROM llamadas l
    JOIN casos c ON c.id_caso = l.id_caso
    WHERE l.id_caso IS NOT NULL
      AND c.resuelto_primer_contacto = false
    GROUP BY date_trunc('month', l.fecha_hora_inicio)::date, l.id_cliente, l.id_caso
    HAVING COUNT(*) > 1
) base
GROUP BY mes
ORDER BY mes
LIMIT 10;


-- ============================================================
-- 6. Agentes con mayor desempeno segun llamadas, tiempo promedio
--    de atencion y satisfaccion del cliente.
-- ============================================================

SELECT
    a.id_agente,
    a.nombre,
    a.apellido,
    d.nombre_departamento,
    COUNT(l.id_llamada) AS total_llamadas_atendidas,
    ROUND(AVG(l.duracion_segundos)::numeric, 2) AS duracion_promedio_segundos,
    ROUND(AVG(l.tiempo_espera_segundos)::numeric, 2) AS espera_promedio_segundos,
    ROUND(AVG(e.calificacion)::numeric, 2) AS satisfaccion_promedio,
    COUNT(e.id_encuesta) AS total_encuestas,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE rl.nombre_resultado = 'resuelta') / NULLIF(COUNT(l.id_llamada), 0),
        2
    ) AS tasa_resolucion_porcentaje
FROM agentes a
JOIN llamadas l ON l.id_agente = a.id_agente
LEFT JOIN departamentos d ON d.id_departamento = a.id_departamento
LEFT JOIN resultados_llamada rl ON rl.id_resultado = l.id_resultado
LEFT JOIN encuestas_satisfaccion e ON e.id_llamada = l.id_llamada
GROUP BY a.id_agente, a.nombre, a.apellido, d.nombre_departamento
ORDER BY
    satisfaccion_promedio DESC NULLS LAST,
    tasa_resolucion_porcentaje DESC,
    total_llamadas_atendidas DESC
LIMIT 10;


-- ============================================================
-- 7. Clientes con facturas vencidas o pagos pendientes.
-- ============================================================

WITH pagos_por_factura AS (
    SELECT
        id_factura,
        SUM(valor_pagado) AS total_pagado
    FROM pagos
    WHERE estado_pago = 'aplicado'
    GROUP BY id_factura
)
SELECT
    c.id_cliente,
    c.nombre,
    c.apellido,
    c.email,
    f.id_factura,
    f.numero_factura,
    f.fecha_emision,
    f.fecha_vencimiento,
    f.estado_factura,
    f.valor_total,
    COALESCE(p.total_pagado, 0) AS total_pagado,
    f.valor_total - COALESCE(p.total_pagado, 0) AS saldo_pendiente
FROM facturas f
JOIN clientes c ON c.id_cliente = f.id_cliente
LEFT JOIN pagos_por_factura p ON p.id_factura = f.id_factura
WHERE f.estado_factura IN ('vencida', 'en_mora')
   OR f.valor_total > COALESCE(p.total_pagado, 0)
ORDER BY saldo_pendiente DESC, f.fecha_vencimiento
LIMIT 10;


-- Resumen de cartera por estado de factura.
WITH pagos_por_factura AS (
    SELECT
        id_factura,
        SUM(valor_pagado) AS total_pagado
    FROM pagos
    WHERE estado_pago = 'aplicado'
    GROUP BY id_factura
)
SELECT
    f.estado_factura,
    COUNT(*) AS total_facturas,
    ROUND(SUM(f.valor_total)::numeric, 2) AS valor_facturado,
    ROUND(SUM(COALESCE(p.total_pagado, 0))::numeric, 2) AS valor_pagado,
    ROUND(SUM(f.valor_total - COALESCE(p.total_pagado, 0))::numeric, 2) AS saldo_pendiente
FROM facturas f
LEFT JOIN pagos_por_factura p ON p.id_factura = f.id_factura
GROUP BY f.estado_factura
ORDER BY saldo_pendiente DESC
LIMIT 10;


-- ============================================================
-- 8. Departamento con mayor tiempo promedio de atencion o menor
--    tasa de resolucion.
-- ============================================================

SELECT
    d.id_departamento,
    d.nombre_departamento,
    COUNT(l.id_llamada) AS total_llamadas,
    ROUND(AVG(l.duracion_segundos)::numeric, 2) AS duracion_promedio_segundos,
    ROUND((AVG(l.duracion_segundos) / 60.0)::numeric, 2) AS duracion_promedio_minutos,
    ROUND(AVG(l.tiempo_espera_segundos)::numeric, 2) AS espera_promedio_segundos,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE rl.nombre_resultado = 'resuelta') / NULLIF(COUNT(l.id_llamada), 0),
        2
    ) AS tasa_resolucion_porcentaje
FROM departamentos d
JOIN llamadas l ON l.id_departamento = d.id_departamento
LEFT JOIN resultados_llamada rl ON rl.id_resultado = l.id_resultado
GROUP BY d.id_departamento, d.nombre_departamento
ORDER BY duracion_promedio_segundos DESC, tasa_resolucion_porcentaje ASC
LIMIT 10;


-- ============================================================
-- 9. Nivel de satisfaccion despues de la atencion y variacion
--    segun agente o tipo de servicio.
-- ============================================================

SELECT
    ts.id_tipo_servicio,
    ts.nombre_servicio,
    COUNT(e.id_encuesta) AS total_encuestas,
    ROUND(AVG(e.calificacion)::numeric, 2) AS satisfaccion_promedio,
    COUNT(*) FILTER (WHERE e.calificacion >= 4) AS encuestas_satisfechas,
    COUNT(*) FILTER (WHERE e.calificacion <= 2) AS encuestas_insatisfechas,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE e.calificacion >= 4) / NULLIF(COUNT(e.id_encuesta), 0),
        2
    ) AS porcentaje_satisfechos
FROM encuestas_satisfaccion e
JOIN llamadas l ON l.id_llamada = e.id_llamada
JOIN tipos_servicio ts ON ts.id_tipo_servicio = l.id_tipo_servicio
GROUP BY ts.id_tipo_servicio, ts.nombre_servicio
ORDER BY satisfaccion_promedio DESC, total_encuestas DESC
LIMIT 10;


SELECT
    a.id_agente,
    a.nombre,
    a.apellido,
    ts.nombre_servicio,
    COUNT(e.id_encuesta) AS total_encuestas,
    ROUND(AVG(e.calificacion)::numeric, 2) AS satisfaccion_promedio,
    ROUND(AVG(l.duracion_segundos)::numeric, 2) AS duracion_promedio_segundos,
    ROUND(AVG(l.tiempo_espera_segundos)::numeric, 2) AS espera_promedio_segundos
FROM encuestas_satisfaccion e
JOIN llamadas l ON l.id_llamada = e.id_llamada
JOIN agentes a ON a.id_agente = l.id_agente
JOIN tipos_servicio ts ON ts.id_tipo_servicio = l.id_tipo_servicio
GROUP BY a.id_agente, a.nombre, a.apellido, ts.nombre_servicio
HAVING COUNT(e.id_encuesta) >= 10
ORDER BY satisfaccion_promedio DESC, total_encuestas DESC
LIMIT 10;


-- PostgreSQL validations for 125k dataset
-- Project: Betek Call Center Analytics
-- Dataset: data/call_center_analytics_20260526_125k
-- Expected range: 2025-06-01 to 2026-05-26
-- Purpose: validate counts, uniqueness, dates, referential consistency and operating rules before Power BI.

SET search_path TO call_center_analytics;

-- 1. Main row counts
SELECT 'clientes' AS tabla, COUNT(*) AS total FROM clientes
UNION ALL SELECT 'agentes', COUNT(*) FROM agentes
UNION ALL SELECT 'casos', COUNT(*) FROM casos
UNION ALL SELECT 'llamadas', COUNT(*) FROM llamadas
UNION ALL SELECT 'facturas', COUNT(*) FROM facturas
UNION ALL SELECT 'pagos', COUNT(*) FROM pagos
UNION ALL SELECT 'encuestas_satisfaccion', COUNT(*) FROM encuestas_satisfaccion
ORDER BY tabla;

-- 2. Duplicate client emails
SELECT lower(email) AS email_normalizado, COUNT(*) AS total
FROM clientes
WHERE email IS NOT NULL
GROUP BY lower(email)
HAVING COUNT(*) > 1
ORDER BY total DESC, email_normalizado
LIMIT 20;

-- Expected result: 0 rows.

-- 3. Call date range
SELECT
    MIN(fecha_hora_inicio) AS primera_llamada,
    MAX(fecha_hora_inicio) AS ultima_llamada
FROM llamadas;

-- Expected result: between 2025-06-01 and 2026-05-26.

-- 4. Calls outside expected range
SELECT COUNT(*) AS llamadas_fuera_de_rango
FROM llamadas
WHERE fecha_hora_inicio < TIMESTAMP '2025-06-01 00:00:00'
   OR fecha_hora_inicio >= TIMESTAMP '2026-05-27 00:00:00';

-- Expected result: 0.

-- 5. Cases closed before opening date
SELECT COUNT(*) AS casos_con_fechas_invalidas
FROM casos
WHERE fecha_cierre IS NOT NULL
  AND fecha_cierre < fecha_apertura;

-- Expected result: 0.

-- 6. Invoices with invalid dates
SELECT COUNT(*) AS facturas_con_fechas_invalidas
FROM facturas
WHERE fecha_vencimiento < fecha_emision;

-- Expected result: 0.

-- 7. Payments before invoice issue date
SELECT COUNT(*) AS pagos_anteriores_a_factura
FROM pagos p
JOIN facturas f ON f.id_factura = p.id_factura
WHERE p.fecha_pago < f.fecha_emision;

-- Expected result: 0.

-- 8. Calls without valid client
SELECT COUNT(*) AS llamadas_sin_cliente_valido
FROM llamadas l
LEFT JOIN clientes c ON c.id_cliente = l.id_cliente
WHERE c.id_cliente IS NULL;

-- Expected result: 0.

-- 9. Calls without valid agent when id_agente is not null
SELECT COUNT(*) AS llamadas_sin_agente_valido
FROM llamadas l
LEFT JOIN agentes a ON a.id_agente = l.id_agente
WHERE l.id_agente IS NOT NULL
  AND a.id_agente IS NULL;

-- Expected result: 0.

-- 10. Cases without valid client
SELECT COUNT(*) AS casos_sin_cliente_valido
FROM casos ca
LEFT JOIN clientes c ON c.id_cliente = ca.id_cliente
WHERE c.id_cliente IS NULL;

-- Expected result: 0.

-- 11. Invoices without valid client
SELECT COUNT(*) AS facturas_sin_cliente_valido
FROM facturas f
LEFT JOIN clientes c ON c.id_cliente = f.id_cliente
WHERE c.id_cliente IS NULL;

-- Expected result: 0.

-- 12. Payments without valid invoice
SELECT COUNT(*) AS pagos_sin_factura_valida
FROM pagos p
LEFT JOIN facturas f ON f.id_factura = p.id_factura
WHERE f.id_factura IS NULL;

-- Expected result: 0.

-- 13. Surveys without valid call
SELECT COUNT(*) AS encuestas_sin_llamada_valida
FROM encuestas_satisfaccion e
LEFT JOIN llamadas l ON l.id_llamada = e.id_llamada
WHERE l.id_llamada IS NULL;

-- Expected result: 0.

-- 14. Daily call coverage
SELECT COUNT(*) AS dias_sin_llamadas
FROM generate_series(DATE '2025-06-01', DATE '2026-05-26', INTERVAL '1 day') AS d(fecha)
LEFT JOIN (
    SELECT fecha_hora_inicio::date AS fecha, COUNT(*) AS total
    FROM llamadas
    GROUP BY fecha_hora_inicio::date
) l ON l.fecha = d.fecha
WHERE COALESCE(l.total, 0) = 0;

-- Expected result: 0.

-- 15. Calls by service type
SELECT
    ts.id_tipo_servicio,
    ts.nombre_servicio AS tipo_servicio,
    COUNT(*) AS total_llamadas,
    MIN(l.fecha_hora_inicio) AS primera_llamada,
    MAX(l.fecha_hora_inicio) AS ultima_llamada
FROM llamadas l
JOIN tipos_servicio ts ON ts.id_tipo_servicio = l.id_tipo_servicio
GROUP BY ts.id_tipo_servicio, ts.nombre_servicio
ORDER BY ts.id_tipo_servicio;

-- 16. Operating schedule validation by service type
SELECT
    ts.nombre_servicio AS tipo_servicio,
    COUNT(*) AS llamadas_fuera_regla
FROM llamadas l
JOIN tipos_servicio ts ON ts.id_tipo_servicio = l.id_tipo_servicio
WHERE
    (
        lower(ts.nombre_servicio) LIKE '%venta%'
        AND (
            EXTRACT(ISODOW FROM l.fecha_hora_inicio) = 7
            OR l.fecha_hora_inicio::time < TIME '09:00:00'
            OR l.fecha_hora_inicio::time >= TIME '19:00:00'
        )
    )
    OR
    (
        lower(ts.nombre_servicio) LIKE '%telemarketing%'
        AND (
            EXTRACT(ISODOW FROM l.fecha_hora_inicio) = 7
            OR l.fecha_hora_inicio::time < TIME '09:00:00'
            OR l.fecha_hora_inicio::time >= TIME '19:00:00'
        )
    )
    OR
    (
        lower(ts.nombre_servicio) LIKE '%atencion%'
        AND (
            l.fecha_hora_inicio::time < TIME '07:00:00'
            OR l.fecha_hora_inicio::time >= TIME '21:00:00'
        )
    )
    OR
    (
        lower(ts.nombre_servicio) LIKE '%facturacion%'
        AND (
            EXTRACT(ISODOW FROM l.fecha_hora_inicio) = 7
            OR l.fecha_hora_inicio::time < TIME '09:00:00'
            OR l.fecha_hora_inicio::time >= TIME '19:00:00'
        )
    )
GROUP BY ts.nombre_servicio
ORDER BY ts.nombre_servicio;

-- Expected result: 0 rows or 0 calls outside rule.
-- Technical support is not validated here because it operates 24/7.

\set ON_ERROR_STOP on
BEGIN;
SET search_path TO call_center_analytics;

TRUNCATE TABLE encuestas_satisfaccion, llamadas, casos, pagos, facturas, productos_servicios_cliente, agente_turno, agente_habilidad, motivos_llamada, agentes, equipos_trabajo, clientes, resultados_llamada, tipos_servicio, turnos, habilidades, departamentos RESTART IDENTITY CASCADE;

CREATE TEMP TABLE stg_departamentos AS SELECT id_departamento, nombre_departamento, descripcion FROM call_center_analytics.departamentos WITH NO DATA;
\copy stg_departamentos (id_departamento, nombre_departamento, descripcion) FROM '_smoke_test_call_center/departamentos.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.departamentos (id_departamento, nombre_departamento, descripcion) OVERRIDING SYSTEM VALUE SELECT id_departamento, nombre_departamento, descripcion FROM stg_departamentos;
DROP TABLE stg_departamentos;

CREATE TEMP TABLE stg_tipos_servicio AS SELECT id_tipo_servicio, nombre_servicio FROM call_center_analytics.tipos_servicio WITH NO DATA;
\copy stg_tipos_servicio (id_tipo_servicio, nombre_servicio) FROM '_smoke_test_call_center/tipos_servicio.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.tipos_servicio (id_tipo_servicio, nombre_servicio) OVERRIDING SYSTEM VALUE SELECT id_tipo_servicio, nombre_servicio FROM stg_tipos_servicio;
DROP TABLE stg_tipos_servicio;

CREATE TEMP TABLE stg_resultados_llamada AS SELECT id_resultado, nombre_resultado FROM call_center_analytics.resultados_llamada WITH NO DATA;
\copy stg_resultados_llamada (id_resultado, nombre_resultado) FROM '_smoke_test_call_center/resultados_llamada.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.resultados_llamada (id_resultado, nombre_resultado) OVERRIDING SYSTEM VALUE SELECT id_resultado, nombre_resultado FROM stg_resultados_llamada;
DROP TABLE stg_resultados_llamada;

CREATE TEMP TABLE stg_habilidades AS SELECT id_habilidad, nombre_habilidad, descripcion FROM call_center_analytics.habilidades WITH NO DATA;
\copy stg_habilidades (id_habilidad, nombre_habilidad, descripcion) FROM '_smoke_test_call_center/habilidades.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.habilidades (id_habilidad, nombre_habilidad, descripcion) OVERRIDING SYSTEM VALUE SELECT id_habilidad, nombre_habilidad, descripcion FROM stg_habilidades;
DROP TABLE stg_habilidades;

CREATE TEMP TABLE stg_turnos AS SELECT id_turno, nombre_turno, hora_inicio, hora_fin, dias_semana FROM call_center_analytics.turnos WITH NO DATA;
\copy stg_turnos (id_turno, nombre_turno, hora_inicio, hora_fin, dias_semana) FROM '_smoke_test_call_center/turnos.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.turnos (id_turno, nombre_turno, hora_inicio, hora_fin, dias_semana) OVERRIDING SYSTEM VALUE SELECT id_turno, nombre_turno, hora_inicio, hora_fin, dias_semana FROM stg_turnos;
DROP TABLE stg_turnos;

CREATE TEMP TABLE stg_clientes AS SELECT id_cliente, tipo_documento, numero_documento, nombre, apellido, direccion, ciudad, telefono, email, fecha_registro, estado_cliente FROM call_center_analytics.clientes WITH NO DATA;
\copy stg_clientes (id_cliente, tipo_documento, numero_documento, nombre, apellido, direccion, ciudad, telefono, email, fecha_registro, estado_cliente) FROM '_smoke_test_call_center/clientes.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.clientes (id_cliente, tipo_documento, numero_documento, nombre, apellido, direccion, ciudad, telefono, email, fecha_registro, estado_cliente) OVERRIDING SYSTEM VALUE SELECT id_cliente, tipo_documento, numero_documento, nombre, apellido, direccion, ciudad, telefono, email, fecha_registro, estado_cliente FROM stg_clientes;
DROP TABLE stg_clientes;

CREATE TEMP TABLE stg_equipos_trabajo AS SELECT id_equipo, nombre_equipo, id_departamento, descripcion FROM call_center_analytics.equipos_trabajo WITH NO DATA;
\copy stg_equipos_trabajo (id_equipo, nombre_equipo, id_departamento, descripcion) FROM '_smoke_test_call_center/equipos_trabajo.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.equipos_trabajo (id_equipo, nombre_equipo, id_departamento, descripcion) OVERRIDING SYSTEM VALUE SELECT id_equipo, nombre_equipo, id_departamento, descripcion FROM stg_equipos_trabajo;
DROP TABLE stg_equipos_trabajo;

CREATE TEMP TABLE stg_agentes AS SELECT id_agente, nombre, apellido, documento, cargo, telefono, email, fecha_ingreso, estado_agente, id_equipo, id_departamento FROM call_center_analytics.agentes WITH NO DATA;
\copy stg_agentes (id_agente, nombre, apellido, documento, cargo, telefono, email, fecha_ingreso, estado_agente, id_equipo, id_departamento) FROM '_smoke_test_call_center/agentes.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.agentes (id_agente, nombre, apellido, documento, cargo, telefono, email, fecha_ingreso, estado_agente, id_equipo, id_departamento) OVERRIDING SYSTEM VALUE SELECT id_agente, nombre, apellido, documento, cargo, telefono, email, fecha_ingreso, estado_agente, id_equipo, id_departamento FROM stg_agentes;
DROP TABLE stg_agentes;

CREATE TEMP TABLE stg_motivos_llamada AS SELECT id_motivo, nombre_motivo, descripcion, id_tipo_servicio FROM call_center_analytics.motivos_llamada WITH NO DATA;
\copy stg_motivos_llamada (id_motivo, nombre_motivo, descripcion, id_tipo_servicio) FROM '_smoke_test_call_center/motivos_llamada.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.motivos_llamada (id_motivo, nombre_motivo, descripcion, id_tipo_servicio) OVERRIDING SYSTEM VALUE SELECT id_motivo, nombre_motivo, descripcion, id_tipo_servicio FROM stg_motivos_llamada;
DROP TABLE stg_motivos_llamada;

CREATE TEMP TABLE stg_agente_habilidad AS SELECT id_agente, id_habilidad FROM call_center_analytics.agente_habilidad WITH NO DATA;
\copy stg_agente_habilidad (id_agente, id_habilidad) FROM '_smoke_test_call_center/agente_habilidad.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.agente_habilidad (id_agente, id_habilidad) SELECT id_agente, id_habilidad FROM stg_agente_habilidad;
DROP TABLE stg_agente_habilidad;

CREATE TEMP TABLE stg_agente_turno AS SELECT id_agente_turno, id_agente, id_turno, fecha_inicio, fecha_fin FROM call_center_analytics.agente_turno WITH NO DATA;
\copy stg_agente_turno (id_agente_turno, id_agente, id_turno, fecha_inicio, fecha_fin) FROM '_smoke_test_call_center/agente_turno.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.agente_turno (id_agente_turno, id_agente, id_turno, fecha_inicio, fecha_fin) OVERRIDING SYSTEM VALUE SELECT id_agente_turno, id_agente, id_turno, fecha_inicio, fecha_fin FROM stg_agente_turno;
DROP TABLE stg_agente_turno;

CREATE TEMP TABLE stg_productos_servicios_cliente AS SELECT id_producto_cliente, id_cliente, nombre_producto_servicio, categoria, fecha_adquisicion, estado_producto FROM call_center_analytics.productos_servicios_cliente WITH NO DATA;
\copy stg_productos_servicios_cliente (id_producto_cliente, id_cliente, nombre_producto_servicio, categoria, fecha_adquisicion, estado_producto) FROM '_smoke_test_call_center/productos_servicios_cliente.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.productos_servicios_cliente (id_producto_cliente, id_cliente, nombre_producto_servicio, categoria, fecha_adquisicion, estado_producto) OVERRIDING SYSTEM VALUE SELECT id_producto_cliente, id_cliente, nombre_producto_servicio, categoria, fecha_adquisicion, estado_producto FROM stg_productos_servicios_cliente;
DROP TABLE stg_productos_servicios_cliente;

CREATE TEMP TABLE stg_facturas AS SELECT id_factura, id_cliente, numero_factura, fecha_emision, fecha_vencimiento, valor_total, estado_factura FROM call_center_analytics.facturas WITH NO DATA;
\copy stg_facturas (id_factura, id_cliente, numero_factura, fecha_emision, fecha_vencimiento, valor_total, estado_factura) FROM '_smoke_test_call_center/facturas.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.facturas (id_factura, id_cliente, numero_factura, fecha_emision, fecha_vencimiento, valor_total, estado_factura) OVERRIDING SYSTEM VALUE SELECT id_factura, id_cliente, numero_factura, fecha_emision, fecha_vencimiento, valor_total, estado_factura FROM stg_facturas;
DROP TABLE stg_facturas;

CREATE TEMP TABLE stg_pagos AS SELECT id_pago, id_factura, fecha_pago, valor_pagado, metodo_pago, estado_pago FROM call_center_analytics.pagos WITH NO DATA;
\copy stg_pagos (id_pago, id_factura, fecha_pago, valor_pagado, metodo_pago, estado_pago) FROM '_smoke_test_call_center/pagos.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.pagos (id_pago, id_factura, fecha_pago, valor_pagado, metodo_pago, estado_pago) OVERRIDING SYSTEM VALUE SELECT id_pago, id_factura, fecha_pago, valor_pagado, metodo_pago, estado_pago FROM stg_pagos;
DROP TABLE stg_pagos;

CREATE TEMP TABLE stg_casos AS SELECT id_caso, id_cliente, id_tipo_servicio, id_motivo, descripcion_caso, fecha_apertura, fecha_cierre, estado_caso, resuelto_primer_contacto, prioridad FROM call_center_analytics.casos WITH NO DATA;
\copy stg_casos (id_caso, id_cliente, id_tipo_servicio, id_motivo, descripcion_caso, fecha_apertura, fecha_cierre, estado_caso, resuelto_primer_contacto, prioridad) FROM '_smoke_test_call_center/casos.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.casos (id_caso, id_cliente, id_tipo_servicio, id_motivo, descripcion_caso, fecha_apertura, fecha_cierre, estado_caso, resuelto_primer_contacto, prioridad) OVERRIDING SYSTEM VALUE SELECT id_caso, id_cliente, id_tipo_servicio, id_motivo, descripcion_caso, fecha_apertura, fecha_cierre, estado_caso, resuelto_primer_contacto, prioridad FROM stg_casos;
DROP TABLE stg_casos;

CREATE TEMP TABLE stg_llamadas AS SELECT id_llamada, id_cliente, id_agente, id_departamento, id_caso, id_tipo_servicio, id_motivo, id_resultado, tipo_llamada, fecha_hora_inicio, fecha_hora_fin, duracion_segundos, tiempo_espera_segundos, canal, requiere_seguimiento FROM call_center_analytics.llamadas WITH NO DATA;
\copy stg_llamadas (id_llamada, id_cliente, id_agente, id_departamento, id_caso, id_tipo_servicio, id_motivo, id_resultado, tipo_llamada, fecha_hora_inicio, fecha_hora_fin, duracion_segundos, tiempo_espera_segundos, canal, requiere_seguimiento) FROM '_smoke_test_call_center/llamadas.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.llamadas (id_llamada, id_cliente, id_agente, id_departamento, id_caso, id_tipo_servicio, id_motivo, id_resultado, tipo_llamada, fecha_hora_inicio, fecha_hora_fin, duracion_segundos, tiempo_espera_segundos, canal, requiere_seguimiento) OVERRIDING SYSTEM VALUE SELECT id_llamada, id_cliente, id_agente, id_departamento, id_caso, id_tipo_servicio, id_motivo, id_resultado, tipo_llamada, fecha_hora_inicio, fecha_hora_fin, duracion_segundos, tiempo_espera_segundos, canal, requiere_seguimiento FROM stg_llamadas;
DROP TABLE stg_llamadas;

CREATE TEMP TABLE stg_encuestas_satisfaccion AS SELECT id_encuesta, id_llamada, id_cliente, calificacion, comentario, fecha_encuesta FROM call_center_analytics.encuestas_satisfaccion WITH NO DATA;
\copy stg_encuestas_satisfaccion (id_encuesta, id_llamada, id_cliente, calificacion, comentario, fecha_encuesta) FROM '_smoke_test_call_center/encuestas_satisfaccion.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
INSERT INTO call_center_analytics.encuestas_satisfaccion (id_encuesta, id_llamada, id_cliente, calificacion, comentario, fecha_encuesta) OVERRIDING SYSTEM VALUE SELECT id_encuesta, id_llamada, id_cliente, calificacion, comentario, fecha_encuesta FROM stg_encuestas_satisfaccion;
DROP TABLE stg_encuestas_satisfaccion;

SELECT setval(pg_get_serial_sequence('call_center_analytics.clientes', 'id_cliente'), COALESCE((SELECT MAX(id_cliente) FROM call_center_analytics.clientes), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.departamentos', 'id_departamento'), COALESCE((SELECT MAX(id_departamento) FROM call_center_analytics.departamentos), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.equipos_trabajo', 'id_equipo'), COALESCE((SELECT MAX(id_equipo) FROM call_center_analytics.equipos_trabajo), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.agentes', 'id_agente'), COALESCE((SELECT MAX(id_agente) FROM call_center_analytics.agentes), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.habilidades', 'id_habilidad'), COALESCE((SELECT MAX(id_habilidad) FROM call_center_analytics.habilidades), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.turnos', 'id_turno'), COALESCE((SELECT MAX(id_turno) FROM call_center_analytics.turnos), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.agente_turno', 'id_agente_turno'), COALESCE((SELECT MAX(id_agente_turno) FROM call_center_analytics.agente_turno), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.tipos_servicio', 'id_tipo_servicio'), COALESCE((SELECT MAX(id_tipo_servicio) FROM call_center_analytics.tipos_servicio), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.motivos_llamada', 'id_motivo'), COALESCE((SELECT MAX(id_motivo) FROM call_center_analytics.motivos_llamada), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.resultados_llamada', 'id_resultado'), COALESCE((SELECT MAX(id_resultado) FROM call_center_analytics.resultados_llamada), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.productos_servicios_cliente', 'id_producto_cliente'), COALESCE((SELECT MAX(id_producto_cliente) FROM call_center_analytics.productos_servicios_cliente), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.facturas', 'id_factura'), COALESCE((SELECT MAX(id_factura) FROM call_center_analytics.facturas), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.pagos', 'id_pago'), COALESCE((SELECT MAX(id_pago) FROM call_center_analytics.pagos), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.casos', 'id_caso'), COALESCE((SELECT MAX(id_caso) FROM call_center_analytics.casos), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.llamadas', 'id_llamada'), COALESCE((SELECT MAX(id_llamada) FROM call_center_analytics.llamadas), 1), true);
SELECT setval(pg_get_serial_sequence('call_center_analytics.encuestas_satisfaccion', 'id_encuesta'), COALESCE((SELECT MAX(id_encuesta) FROM call_center_analytics.encuestas_satisfaccion), 1), true);

COMMIT;

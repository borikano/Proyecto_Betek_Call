-- =============================================================
-- Proyecto: Base de datos histórica sintética para call center
-- Entregable: DDL de creación de tablas
-- Dialecto objetivo: PostgreSQL 15+
-- Enfoque: integridad referencial, consistencia temporal,
--           trazabilidad analítica y buenas prácticas.
-- =============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS call_center_analytics;
SET search_path TO call_center_analytics;

-- =============================================================
-- 1) Catálogos y dimensiones maestras
-- =============================================================

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_documento           VARCHAR(10)  NOT NULL,
    numero_documento         VARCHAR(30)  NOT NULL,
    nombre                   VARCHAR(80)  NOT NULL,
    apellido                 VARCHAR(80)  NOT NULL,
    direccion                VARCHAR(200),
    ciudad                   VARCHAR(100) NOT NULL,
    telefono                 VARCHAR(20),
    email                    VARCHAR(150),
    fecha_registro           DATE         NOT NULL,
    estado_cliente           VARCHAR(20)  NOT NULL,
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento),
    CONSTRAINT ck_clientes_tipo_documento CHECK (
        tipo_documento IN ('CC', 'CE', 'NIT', 'PAS', 'TI', 'OTRO')
    ),
    CONSTRAINT ck_clientes_estado CHECK (
        estado_cliente IN ('activo', 'inactivo', 'suspendido')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS ixu_clientes_email_no_nulo
    ON clientes (LOWER(email))
    WHERE email IS NOT NULL;

CREATE TABLE IF NOT EXISTS departamentos (
    id_departamento          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_departamento      VARCHAR(80)  NOT NULL,
    descripcion              VARCHAR(250),
    CONSTRAINT uq_departamentos_nombre UNIQUE (nombre_departamento)
);

CREATE TABLE IF NOT EXISTS equipos_trabajo (
    id_equipo                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_equipo            VARCHAR(80)  NOT NULL,
    id_departamento          BIGINT       NOT NULL,
    descripcion              VARCHAR(250),
    CONSTRAINT fk_equipos_departamento
        FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
    CONSTRAINT uq_equipos_nombre_departamento UNIQUE (nombre_equipo, id_departamento),
    CONSTRAINT uq_equipos_id_equipo_departamento UNIQUE (id_equipo, id_departamento)
);

CREATE TABLE IF NOT EXISTS agentes (
    id_agente                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre                   VARCHAR(80)  NOT NULL,
    apellido                 VARCHAR(80)  NOT NULL,
    documento                VARCHAR(30)  NOT NULL,
    cargo                    VARCHAR(60)  NOT NULL,
    telefono                 VARCHAR(20),
    email                    VARCHAR(150),
    fecha_ingreso            DATE         NOT NULL,
    estado_agente            VARCHAR(20)  NOT NULL,
    id_equipo                BIGINT       NOT NULL,
    id_departamento          BIGINT       NOT NULL,
    CONSTRAINT uq_agentes_documento UNIQUE (documento),
    CONSTRAINT uq_agentes_email UNIQUE (email),
    CONSTRAINT uq_agentes_id_agente_departamento UNIQUE (id_agente, id_departamento),
    CONSTRAINT fk_agentes_equipo_departamento
        FOREIGN KEY (id_equipo, id_departamento)
        REFERENCES equipos_trabajo(id_equipo, id_departamento),
    CONSTRAINT fk_agentes_departamento
        FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
    CONSTRAINT ck_agentes_estado CHECK (
        estado_agente IN ('activo', 'inactivo', 'vacaciones')
    )
);

CREATE TABLE IF NOT EXISTS habilidades (
    id_habilidad             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_habilidad         VARCHAR(80)  NOT NULL,
    descripcion              VARCHAR(250),
    CONSTRAINT uq_habilidades_nombre UNIQUE (nombre_habilidad)
);

CREATE TABLE IF NOT EXISTS agente_habilidad (
    id_agente                BIGINT NOT NULL,
    id_habilidad             BIGINT NOT NULL,
    PRIMARY KEY (id_agente, id_habilidad),
    CONSTRAINT fk_agente_habilidad_agente
        FOREIGN KEY (id_agente) REFERENCES agentes(id_agente),
    CONSTRAINT fk_agente_habilidad_habilidad
        FOREIGN KEY (id_habilidad) REFERENCES habilidades(id_habilidad)
);

CREATE TABLE IF NOT EXISTS turnos (
    id_turno                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_turno             VARCHAR(40) NOT NULL,
    hora_inicio              TIME        NOT NULL,
    hora_fin                 TIME        NOT NULL,
    dias_semana              VARCHAR(40) NOT NULL,
    CONSTRAINT uq_turnos_nombre UNIQUE (nombre_turno),
    CONSTRAINT ck_turnos_horas CHECK (hora_inicio <> hora_fin)
);

CREATE TABLE IF NOT EXISTS agente_turno (
    id_agente_turno          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_agente                BIGINT NOT NULL,
    id_turno                 BIGINT NOT NULL,
    fecha_inicio             DATE   NOT NULL,
    fecha_fin                DATE,
    CONSTRAINT fk_agente_turno_agente
        FOREIGN KEY (id_agente) REFERENCES agentes(id_agente),
    CONSTRAINT fk_agente_turno_turno
        FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    CONSTRAINT uq_agente_turno_inicio UNIQUE (id_agente, id_turno, fecha_inicio),
    CONSTRAINT ck_agente_turno_fechas CHECK (
        fecha_fin IS NULL OR fecha_fin >= fecha_inicio
    )
);

CREATE TABLE IF NOT EXISTS tipos_servicio (
    id_tipo_servicio         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_servicio          VARCHAR(80)  NOT NULL,
    CONSTRAINT uq_tipos_servicio_nombre UNIQUE (nombre_servicio)
);

CREATE TABLE IF NOT EXISTS motivos_llamada (
    id_motivo                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_motivo            VARCHAR(100) NOT NULL,
    descripcion              VARCHAR(250),
    id_tipo_servicio         BIGINT       NOT NULL,
    CONSTRAINT fk_motivos_tipo_servicio
        FOREIGN KEY (id_tipo_servicio) REFERENCES tipos_servicio(id_tipo_servicio),
    CONSTRAINT uq_motivos_nombre_tipo UNIQUE (nombre_motivo, id_tipo_servicio)
);

CREATE TABLE IF NOT EXISTS resultados_llamada (
    id_resultado             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_resultado         VARCHAR(40) NOT NULL,
    CONSTRAINT uq_resultados_llamada_nombre UNIQUE (nombre_resultado),
    CONSTRAINT ck_resultados_llamada_valores CHECK (
        nombre_resultado IN (
            'resuelta',
            'escalada',
            'pendiente',
            'abandonada',
            'no_contestada',
            'transferida',
            'venta_realizada'
        )
    )
);

-- =============================================================
-- 2) Hechos transaccionales
-- =============================================================

CREATE TABLE IF NOT EXISTS productos_servicios_cliente (
    id_producto_cliente      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente               BIGINT       NOT NULL,
    nombre_producto_servicio VARCHAR(120) NOT NULL,
    categoria                VARCHAR(60)  NOT NULL,
    fecha_adquisicion        DATE         NOT NULL,
    estado_producto          VARCHAR(20)  NOT NULL,
    CONSTRAINT fk_productos_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT ck_productos_estado CHECK (
        estado_producto IN ('activo', 'suspendido', 'cancelado', 'retirado')
    )
);

CREATE TABLE IF NOT EXISTS facturas (
    id_factura               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente               BIGINT        NOT NULL,
    numero_factura           VARCHAR(40)   NOT NULL,
    fecha_emision            DATE          NOT NULL,
    fecha_vencimiento        DATE          NOT NULL,
    valor_total              NUMERIC(14,2) NOT NULL,
    estado_factura           VARCHAR(20)   NOT NULL,
    CONSTRAINT uq_facturas_numero UNIQUE (numero_factura),
    CONSTRAINT fk_facturas_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT ck_facturas_fechas CHECK (fecha_vencimiento >= fecha_emision),
    CONSTRAINT ck_facturas_valor_total CHECK (valor_total > 0),
    CONSTRAINT ck_facturas_estado CHECK (
        estado_factura IN ('pagada', 'pendiente', 'vencida', 'en_mora')
    )
);

CREATE TABLE IF NOT EXISTS pagos (
    id_pago                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_factura               BIGINT        NOT NULL,
    fecha_pago               DATE          NOT NULL,
    valor_pagado             NUMERIC(14,2) NOT NULL,
    metodo_pago              VARCHAR(30)   NOT NULL,
    estado_pago              VARCHAR(20)   NOT NULL,
    CONSTRAINT fk_pagos_factura
        FOREIGN KEY (id_factura) REFERENCES facturas(id_factura),
    CONSTRAINT ck_pagos_valor CHECK (valor_pagado > 0),
    CONSTRAINT ck_pagos_metodo CHECK (
        metodo_pago IN (
            'pse',
            'tarjeta_credito',
            'tarjeta_debito',
            'efectivo',
            'transferencia',
            'recaudo_externo'
        )
    ),
    CONSTRAINT ck_pagos_estado CHECK (
        estado_pago IN ('aplicado', 'parcial', 'pendiente', 'rechazado')
    )
);

CREATE TABLE IF NOT EXISTS casos (
    id_caso                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente               BIGINT       NOT NULL,
    id_tipo_servicio         BIGINT       NOT NULL,
    id_motivo                BIGINT       NOT NULL,
    descripcion_caso         VARCHAR(500) NOT NULL,
    fecha_apertura           TIMESTAMP    NOT NULL,
    fecha_cierre             TIMESTAMP,
    estado_caso              VARCHAR(20)  NOT NULL,
    resuelto_primer_contacto BOOLEAN      NOT NULL DEFAULT FALSE,
    prioridad                VARCHAR(20)  NOT NULL,
    CONSTRAINT fk_casos_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT fk_casos_tipo_servicio
        FOREIGN KEY (id_tipo_servicio) REFERENCES tipos_servicio(id_tipo_servicio),
    CONSTRAINT fk_casos_motivo
        FOREIGN KEY (id_motivo) REFERENCES motivos_llamada(id_motivo),
    CONSTRAINT ck_casos_fechas CHECK (
        fecha_cierre IS NULL OR fecha_cierre >= fecha_apertura
    ),
    CONSTRAINT ck_casos_estado CHECK (
        estado_caso IN ('abierto', 'en_proceso', 'cerrado', 'cancelado')
    ),
    CONSTRAINT ck_casos_prioridad CHECK (
        prioridad IN ('baja', 'media', 'alta', 'critica')
    )
);

CREATE TABLE IF NOT EXISTS llamadas (
    id_llamada               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente               BIGINT      NOT NULL,
    id_agente                BIGINT,
    id_departamento          BIGINT      NOT NULL,
    id_caso                  BIGINT,
    id_tipo_servicio         BIGINT      NOT NULL,
    id_motivo                BIGINT      NOT NULL,
    id_resultado             BIGINT      NOT NULL,
    tipo_llamada             VARCHAR(20) NOT NULL,
    fecha_hora_inicio        TIMESTAMP   NOT NULL,
    fecha_hora_fin           TIMESTAMP   NOT NULL,
    duracion_segundos        INTEGER     NOT NULL,
    tiempo_espera_segundos   INTEGER     NOT NULL,
    canal                    VARCHAR(20) NOT NULL,
    observaciones            VARCHAR(500),
    requiere_seguimiento     BOOLEAN     NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_llamadas_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT fk_llamadas_agente
        FOREIGN KEY (id_agente) REFERENCES agentes(id_agente),
    CONSTRAINT fk_llamadas_departamento
        FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
    CONSTRAINT fk_llamadas_caso
        FOREIGN KEY (id_caso) REFERENCES casos(id_caso),
    CONSTRAINT fk_llamadas_tipo_servicio
        FOREIGN KEY (id_tipo_servicio) REFERENCES tipos_servicio(id_tipo_servicio),
    CONSTRAINT fk_llamadas_motivo
        FOREIGN KEY (id_motivo) REFERENCES motivos_llamada(id_motivo),
    CONSTRAINT fk_llamadas_resultado
        FOREIGN KEY (id_resultado) REFERENCES resultados_llamada(id_resultado),
    CONSTRAINT ck_llamadas_tipo CHECK (
        tipo_llamada IN ('entrante', 'saliente')
    ),
    CONSTRAINT ck_llamadas_canal CHECK (
        canal IN ('telefono', 'voip', 'campana')
    ),
    CONSTRAINT ck_llamadas_fechas CHECK (
        fecha_hora_fin > fecha_hora_inicio
    ),
    CONSTRAINT ck_llamadas_duracion CHECK (
        duracion_segundos >= 0
    ),
    CONSTRAINT ck_llamadas_espera CHECK (
        tiempo_espera_segundos >= 0
    )
);

CREATE TABLE IF NOT EXISTS encuestas_satisfaccion (
    id_encuesta              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_llamada               BIGINT      NOT NULL,
    id_cliente               BIGINT      NOT NULL,
    calificacion             SMALLINT    NOT NULL,
    comentario               VARCHAR(500),
    fecha_encuesta           TIMESTAMP   NOT NULL,
    CONSTRAINT uq_encuestas_id_llamada UNIQUE (id_llamada),
    CONSTRAINT fk_encuestas_llamada
        FOREIGN KEY (id_llamada) REFERENCES llamadas(id_llamada),
    CONSTRAINT fk_encuestas_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT ck_encuestas_calificacion CHECK (
        calificacion BETWEEN 1 AND 5
    )
);

-- =============================================================
-- 3) Índices recomendados para carga, consultas y analítica
-- =============================================================

CREATE INDEX IF NOT EXISTS ix_clientes_fecha_registro
    ON clientes (fecha_registro);

CREATE INDEX IF NOT EXISTS ix_agentes_departamento
    ON agentes (id_departamento);

CREATE INDEX IF NOT EXISTS ix_agente_turno_agente_fechas
    ON agente_turno (id_agente, fecha_inicio, fecha_fin);

CREATE INDEX IF NOT EXISTS ix_motivos_tipo_servicio
    ON motivos_llamada (id_tipo_servicio);

CREATE INDEX IF NOT EXISTS ix_productos_cliente_estado
    ON productos_servicios_cliente (id_cliente, estado_producto);

CREATE INDEX IF NOT EXISTS ix_facturas_cliente_emision
    ON facturas (id_cliente, fecha_emision);

CREATE INDEX IF NOT EXISTS ix_facturas_estado_vencimiento
    ON facturas (estado_factura, fecha_vencimiento);

CREATE INDEX IF NOT EXISTS ix_pagos_factura_fecha
    ON pagos (id_factura, fecha_pago);

CREATE INDEX IF NOT EXISTS ix_casos_cliente_apertura
    ON casos (id_cliente, fecha_apertura);

CREATE INDEX IF NOT EXISTS ix_casos_tipo_estado
    ON casos (id_tipo_servicio, estado_caso);

CREATE INDEX IF NOT EXISTS ix_llamadas_fecha_inicio
    ON llamadas (fecha_hora_inicio);

CREATE INDEX IF NOT EXISTS ix_llamadas_cliente_fecha
    ON llamadas (id_cliente, fecha_hora_inicio);

CREATE INDEX IF NOT EXISTS ix_llamadas_agente_fecha
    ON llamadas (id_agente, fecha_hora_inicio);

CREATE INDEX IF NOT EXISTS ix_llamadas_departamento_fecha
    ON llamadas (id_departamento, fecha_hora_inicio);

CREATE INDEX IF NOT EXISTS ix_llamadas_caso
    ON llamadas (id_caso);

CREATE INDEX IF NOT EXISTS ix_llamadas_tipo_resultado
    ON llamadas (id_tipo_servicio, id_resultado);

CREATE INDEX IF NOT EXISTS ix_encuestas_cliente_fecha
    ON encuestas_satisfaccion (id_cliente, fecha_encuesta);

CREATE INDEX IF NOT EXISTS ix_encuestas_calificacion
    ON encuestas_satisfaccion (calificacion);

-- =============================================================
-- 4) Notas de implementación
-- =============================================================
-- a) Las reglas cruzadas más complejas (por ejemplo, suma de pagos <= valor
--    total de la factura, FCR derivado del historial del caso, o consistencia
--    analítica entre resultado de llamada y contexto comercial) deben
--    validarse en ETL, pruebas de calidad o triggers controlados.
--
-- b) Este DDL prioriza estabilidad y claridad para cargar CSV, poblar datos
--    sintéticos y consultar desde SQL y Python.
--
-- c) La carga sugerida es:
--    1. catálogos
--    2. clientes
--    3. equipos/agentes/habilidades/turnos
--    4. tablas puente
--    5. productos
--    6. facturas
--    7. pagos
--    8. casos
--    9. llamadas
--   10. encuestas

COMMIT;

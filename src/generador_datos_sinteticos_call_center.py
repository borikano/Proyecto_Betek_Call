
#!/usr/bin/env python3
"""
07_generador_datos_sinteticos_python.py

Generador de datos sintéticos históricos para un call center.
Produce un CSV por tabla, más reportes de calidad y trazabilidad.

Uso ejemplo:
python 07_generador_datos_sinteticos_python.py --output-dir ./salida

Para pruebas pequenas:
python 07_generador_datos_sinteticos_python.py \
  --output-dir ./salida_prueba \
  --clients 500 --agents 30 --history-months 2 \
  --products-target-min 700 --products-target-max 900 \
  --invoices-target-min 900 --invoices-target-max 1200 \
  --payments-target-min 700 --payments-target-max 1000 \
  --cases-target-min 500 --cases-target-max 700 \
  --calls-target-min 2000 --calls-target-max 2500 \
  --surveys-target-min 400 --surveys-target-max 600
"""

from __future__ import annotations

import argparse
import json
import math
import unicodedata
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


SQL_EXPORT_COLUMNS = {
    "clientes": [
        "id_cliente", "tipo_documento", "numero_documento", "nombre", "apellido", "direccion",
        "ciudad", "telefono", "email", "fecha_registro", "estado_cliente"
    ],
    "departamentos": ["id_departamento", "nombre_departamento", "descripcion"],
    "equipos_trabajo": ["id_equipo", "nombre_equipo", "id_departamento", "descripcion"],
    "agentes": [
        "id_agente", "nombre", "apellido", "documento", "cargo", "telefono", "email",
        "fecha_ingreso", "estado_agente", "id_equipo", "id_departamento"
    ],
    "habilidades": ["id_habilidad", "nombre_habilidad", "descripcion"],
    "agente_habilidad": ["id_agente", "id_habilidad"],
    "turnos": ["id_turno", "nombre_turno", "hora_inicio", "hora_fin", "dias_semana"],
    "agente_turno": ["id_agente_turno", "id_agente", "id_turno", "fecha_inicio", "fecha_fin"],
    "tipos_servicio": ["id_tipo_servicio", "nombre_servicio"],
    "motivos_llamada": ["id_motivo", "nombre_motivo", "descripcion", "id_tipo_servicio"],
    "resultados_llamada": ["id_resultado", "nombre_resultado"],
    "productos_servicios_cliente": [
        "id_producto_cliente", "id_cliente", "nombre_producto_servicio", "categoria",
        "fecha_adquisicion", "estado_producto"
    ],
    "facturas": [
        "id_factura", "id_cliente", "numero_factura", "fecha_emision", "fecha_vencimiento",
        "valor_total", "estado_factura"
    ],
    "pagos": ["id_pago", "id_factura", "fecha_pago", "valor_pagado", "metodo_pago", "estado_pago"],
    "casos": [
        "id_caso", "id_cliente", "id_tipo_servicio", "id_motivo", "descripcion_caso",
        "fecha_apertura", "fecha_cierre", "estado_caso", "resuelto_primer_contacto", "prioridad"
    ],
    "llamadas": [
        "id_llamada", "id_cliente", "id_agente", "id_departamento", "id_caso", "id_tipo_servicio",
        "id_motivo", "id_resultado", "tipo_llamada", "fecha_hora_inicio", "fecha_hora_fin",
        "duracion_segundos", "tiempo_espera_segundos", "canal", "requiere_seguimiento"
    ],
    "encuestas_satisfaccion": [
        "id_encuesta", "id_llamada", "id_cliente", "calificacion", "comentario", "fecha_encuesta"
    ],
}

LOAD_ORDER = [
    "departamentos",
    "tipos_servicio",
    "resultados_llamada",
    "habilidades",
    "turnos",
    "clientes",
    "equipos_trabajo",
    "agentes",
    "motivos_llamada",
    "agente_habilidad",
    "agente_turno",
    "productos_servicios_cliente",
    "facturas",
    "pagos",
    "casos",
    "llamadas",
    "encuestas_satisfaccion",
]

IDENTITY_PK_MAP = {
    "clientes": "id_cliente",
    "departamentos": "id_departamento",
    "equipos_trabajo": "id_equipo",
    "agentes": "id_agente",
    "habilidades": "id_habilidad",
    "turnos": "id_turno",
    "agente_turno": "id_agente_turno",
    "tipos_servicio": "id_tipo_servicio",
    "motivos_llamada": "id_motivo",
    "resultados_llamada": "id_resultado",
    "productos_servicios_cliente": "id_producto_cliente",
    "facturas": "id_factura",
    "pagos": "id_pago",
    "casos": "id_caso",
    "llamadas": "id_llamada",
    "encuestas_satisfaccion": "id_encuesta",
}


@dataclass
class GenerationConfig:
    seed: int = 20260410
    output_dir: str = "./output_call_center"
    history_months: int = 6
    start_date: Optional[str] = None
    end_date: str = date.today().isoformat()

    clients: int = 30000
    agents: int = 180

    surveys_target_min: int = 20000
    surveys_target_max: int = 32000
    calls_target_min: int = 95000
    calls_target_max: int = 135000
    invoices_target_min: int = 85000
    invoices_target_max: int = 110000
    cases_target_min: int = 24000
    cases_target_max: int = 32000
    products_target_min: int = 42000
    products_target_max: int = 50000
    payments_target_min: int = 70000
    payments_target_max: int = 100000


class SyntheticCallCenterGenerator:
    def __init__(self, config: GenerationConfig) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.end_date = datetime.strptime(config.end_date, "%Y-%m-%d").date()
        if config.start_date:
            self.start_date = datetime.strptime(config.start_date, "%Y-%m-%d").date()
        else:
            self.start_date = self.end_date - timedelta(days=30 * config.history_months)
        if self.start_date > self.end_date:
            raise ValueError("start_date no puede ser mayor que end_date")
        self.tables: Dict[str, pd.DataFrame] = {}
        self._maybe_scale_targets()
        self._validate_config()

        self.first_names = np.array([
            "Andres","Camilo","Daniel","David","Felipe","Jorge","Juan","Julian","Luis","Mateo",
            "Miguel","Nicolas","Sebastian","Santiago","Sara","Valentina","Laura","Paula","Maria",
            "Ana","Carolina","Diana","Natalia","Manuela","Andrea","Luisa","Catalina","Sofia",
            "Alejandra","Tatiana","Isabella","Jose","Carlos","Kevin","Yuliana","Paola"
        ])
        self.last_names = np.array([
            "Gomez","Rodriguez","Lopez","Martinez","Garcia","Perez","Hernandez","Ramirez","Torres",
            "Morales","Castro","Ortiz","Rojas","Diaz","Sanchez","Vargas","Jimenez","Castaño",
            "Quintero","Mejia","Agudelo","Arango","Cardona","Osorio","Restrepo","Bedoya","Giraldo","Molina"
        ])
        self.cities = np.array([
            "Bogota","Medellin","Cali","Barranquilla","Cartagena","Bucaramanga","Pereira","Manizales",
            "Armenia","Santa Marta","Cucuta","Ibague","Villavicencio","Pasto","Monteria"
        ])
        self.report: Dict[str, object] = {
            "seed": config.seed,
            "generator_version": "1.0.0",
            "business_rules_version": "1.0.0",
            "history_start_date": self.start_date.isoformat(),
            "history_end_date": self.end_date.isoformat(),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "validations": {},
        }

    # ---------- Helpers ----------

    def _maybe_scale_targets(self) -> None:
        defaults = GenerationConfig()
        client_ratio = max(0.02, self.config.clients / defaults.clients)
        agent_ratio = max(0.05, self.config.agents / defaults.agents)
        ratio = min(1.0, max(client_ratio, (client_ratio + agent_ratio) / 2))
        floors = {
            "surveys_target_min": 100, "surveys_target_max": 150,
            "calls_target_min": 300, "calls_target_max": 500,
            "invoices_target_min": 120, "invoices_target_max": 180,
            "cases_target_min": 80, "cases_target_max": 120,
            "products_target_min": max(50, self.config.clients),
            "products_target_max": max(80, self.config.clients + 20),
            "payments_target_min": 100, "payments_target_max": 160,
        }
        for field, floor in floors.items():
            current = getattr(self.config, field)
            if current == getattr(defaults, field) and ratio < 1.0:
                setattr(self.config, field, max(floor, int(round(current * ratio))))

    def _validate_config(self) -> None:
        if self.config.clients <= 0:
            raise ValueError("--clients debe ser mayor que 0")
        if self.config.agents <= 0:
            raise ValueError("--agents debe ser mayor que 0")

        target_pairs = [
            ("surveys", self.config.surveys_target_min, self.config.surveys_target_max),
            ("calls", self.config.calls_target_min, self.config.calls_target_max),
            ("invoices", self.config.invoices_target_min, self.config.invoices_target_max),
            ("cases", self.config.cases_target_min, self.config.cases_target_max),
            ("products", self.config.products_target_min, self.config.products_target_max),
            ("payments", self.config.payments_target_min, self.config.payments_target_max),
        ]
        for name, minimum, maximum in target_pairs:
            if minimum < 0 or maximum < 0:
                raise ValueError(f"Los targets de {name} no pueden ser negativos")
            if minimum > maximum:
                raise ValueError(f"El target minimo de {name} no puede superar el maximo")

        if self.config.products_target_min < self.config.clients:
            raise ValueError("products_target_min no puede ser menor que clients")
        if self.config.products_target_max > self.config.clients * 4:
            raise ValueError("products_target_max no puede superar clients * 4")

    def _choice(self, values, probs, size):
        probs = np.array(probs, dtype=float)
        probs /= probs.sum()
        return self.rng.choice(values, size=size, p=probs)

    def _ascii_text(self, value):
        if pd.isna(value):
            return value
        normalized = unicodedata.normalize("NFKD", str(value))
        return normalized.encode("ascii", "ignore").decode("ascii")

    def _colombian_mobile_numbers(self, size: int) -> List[str]:
        return [f"3{int(x):09d}" for x in self.rng.integers(0, 1_000_000_000, size=size)]

    def _random_dates(self, start: date, end: date, size: int) -> List[date]:
        total_days = max(1, (end - start).days)
        offsets = self.rng.integers(0, total_days + 1, size=size)
        return [start + timedelta(days=int(x)) for x in offsets]

    def _sample_timestamps(self, size: int) -> List[datetime]:
        hour_weights = np.array([
            0.01,0.005,0.005,0.005,0.006,0.008,0.015,0.03,0.07,0.08,0.075,0.06,
            0.05,0.055,0.07,0.08,0.075,0.06,0.045,0.03,0.02,0.012,0.008,0.006
        ])
        hour_weights /= hour_weights.sum()
        all_days = pd.date_range(self.start_date, self.end_date, freq="D")
        weekday_pref = np.array([0.18,0.19,0.18,0.17,0.15,0.09,0.04])
        day_weights = np.array([weekday_pref[d.weekday()] for d in all_days], dtype=float)
        day_weights /= day_weights.sum()
        chosen_days = self.rng.choice(all_days.to_numpy(), size=size, p=day_weights)
        hours = self.rng.choice(np.arange(24), size=size, p=hour_weights)
        mins = self.rng.integers(0, 60, size=size)
        secs = self.rng.integers(0, 60, size=size)
        out = []
        for d, h, m, s in zip(chosen_days, hours, mins, secs):
            ts = pd.Timestamp(d).to_pydatetime().replace(hour=int(h), minute=int(m), second=int(s))
            out.append(ts)
        return out

    def _history_start_datetime(self) -> datetime:
        return datetime.combine(self.start_date, datetime.min.time())

    def _history_end_datetime(self) -> datetime:
        return datetime.combine(self.end_date, datetime.max.time()).replace(microsecond=0)

    def _clip_date_to_history(self, value: date) -> date:
        return min(max(value, self.start_date), self.end_date)

    def _clip_datetime_to_history(self, value: datetime) -> datetime:
        return min(max(value, self._history_start_datetime()), self._history_end_datetime())

    def _bounded_call_window(self, start_dt: datetime, duration_seconds: int) -> tuple[datetime, datetime]:
        history_start = self._history_start_datetime()
        history_end = self._history_end_datetime()
        latest_start = max(history_start, history_end - timedelta(seconds=int(duration_seconds)))
        bounded_start = min(max(start_dt, history_start), latest_start)
        return bounded_start, bounded_start + timedelta(seconds=int(duration_seconds))

    def _service_calendar(self, service_id: int) -> Dict[str, object]:
        calendars = {
            1: {"name": "atencion_cliente", "weekdays": set(range(7)), "start_hour": 7, "end_hour": 21},
            2: {"name": "soporte_tecnico", "weekdays": set(range(7)), "start_hour": 0, "end_hour": 24},
            3: {"name": "ventas", "weekdays": set(range(6)), "start_hour": 9, "end_hour": 19},
            4: {"name": "telemarketing", "weekdays": set(range(6)), "start_hour": 9, "end_hour": 19},
            5: {"name": "facturacion", "weekdays": set(range(6)), "start_hour": 8, "end_hour": 18},
        }
        return calendars[int(service_id)]

    def _day_at_hour(self, day: date, hour: int) -> datetime:
        base = datetime.combine(day, datetime.min.time())
        if hour == 24:
            return base + timedelta(days=1)
        return base.replace(hour=int(hour))

    def _bounded_service_call_window(self, service_id: int, start_dt: datetime, duration_seconds: int) -> tuple[datetime, datetime]:
        duration_seconds = int(duration_seconds)
        history_start = self._history_start_datetime()
        history_end = self._history_end_datetime()
        service = self._service_calendar(service_id)

        if int(service["start_hour"]) == 0 and int(service["end_hour"]) == 24:
            return self._bounded_call_window(start_dt, duration_seconds)

        current = self._clip_datetime_to_history(start_dt)
        max_days = max(1, (self.end_date - self.start_date).days + 2)

        for offset in range(max_days):
            candidate_day = current.date() + timedelta(days=offset)
            if candidate_day > self.end_date:
                break
            if candidate_day.weekday() not in service["weekdays"]:
                continue

            service_start = self._day_at_hour(candidate_day, int(service["start_hour"]))
            service_end = self._day_at_hour(candidate_day, int(service["end_hour"]))

            candidate_start = max(current, service_start) if offset == 0 else service_start
            latest_start = min(service_end, history_end) - timedelta(seconds=duration_seconds)

            if candidate_start <= latest_start:
                candidate_start = max(candidate_start, history_start)
                return candidate_start, candidate_start + timedelta(seconds=duration_seconds)

        for offset in range(max_days):
            candidate_day = self.end_date - timedelta(days=offset)
            if candidate_day < self.start_date:
                break
            if candidate_day.weekday() not in service["weekdays"]:
                continue

            service_start = self._day_at_hour(candidate_day, int(service["start_hour"]))
            service_end = min(self._day_at_hour(candidate_day, int(service["end_hour"])), history_end)
            latest_start = service_end - timedelta(seconds=duration_seconds)

            if latest_start >= service_start:
                return latest_start, latest_start + timedelta(seconds=duration_seconds)

        return self._bounded_call_window(start_dt, duration_seconds)

    def _docs(self, n: int):
        types_ = self._choice(["CC","CE","NIT","TI"], [0.70,0.10,0.15,0.05], size=n)
        nums = self.rng.choice(np.arange(10_000_000, 99_999_999), size=n, replace=False)
        return types_, np.array([str(x) for x in nums])

    # ---------- Generation ----------

    def generate_catalogs(self) -> None:
        self.tables["departamentos"] = pd.DataFrame([
            (1, "atencion_cliente", "Atencion general y orientacion"),
            (2, "soporte_tecnico", "Atencion de fallas e incidentes"),
            (3, "ventas", "Venta directa, upselling y cross-selling"),
            (4, "telemarketing", "Campanas salientes y recuperacion comercial"),
            (5, "facturacion", "Cobros, pagos, mora y cartera"),
        ], columns=["id_departamento","nombre_departamento","descripcion"])

        teams = [
            ("frontline_1",1),("frontline_2",1),("frontline_3",1),
            ("soporte_1",2),("soporte_2",2),("soporte_3",2),
            ("ventas_1",3),("ventas_2",3),
            ("tele_1",4),("tele_2",4),
            ("facturacion_1",5),("facturacion_2",5),
        ]
        self.tables["equipos_trabajo"] = pd.DataFrame(
            [(i+1, n, d, f"Equipo {n}") for i, (n, d) in enumerate(teams)],
            columns=["id_equipo","nombre_equipo","id_departamento","descripcion"]
        )

        self.tables["habilidades"] = pd.DataFrame([
            (1,"atencion_cliente","Atencion y orientacion"),
            (2,"soporte_tecnico","Diagnostico y soporte tecnico"),
            (3,"ventas","Habilidad comercial y cierre"),
            (4,"manejo_quejas","Gestion de casos complejos"),
            (5,"bilingue","Atencion bilingue"),
            (6,"facturacion","Conocimiento de cobros y cartera"),
        ], columns=["id_habilidad","nombre_habilidad","descripcion"])

        self.tables["turnos"] = pd.DataFrame([
            (1,"manana","06:00:00","14:00:00","lun-dom"),
            (2,"tarde","14:00:00","22:00:00","lun-dom"),
            (3,"noche","22:00:00","06:00:00","lun-dom"),
        ], columns=["id_turno","nombre_turno","hora_inicio","hora_fin","dias_semana"])

        self.tables["tipos_servicio"] = pd.DataFrame([
            (1,"atencion_cliente"),(2,"soporte_tecnico"),(3,"ventas"),(4,"telemarketing"),(5,"facturacion")
        ], columns=["id_tipo_servicio","nombre_servicio"])

        self.tables["motivos_llamada"] = pd.DataFrame([
            (1,"consulta_general","Consulta general",1),
            (2,"actualizacion_datos","Actualizacion de datos",1),
            (3,"reclamo","Reclamo general",1),
            (4,"falla_servicio","Falla del servicio",2),
            (5,"soporte_instalacion","Instalacion o configuracion",2),
            (6,"soporte_dispositivo","Soporte sobre dispositivo",2),
            (7,"compra_producto","Compra de producto o servicio",3),
            (8,"cambio_plan","Upgrade o cambio de plan",3),
            (9,"renovacion","Renovacion comercial",3),
            (10,"campana_saliente","Campana comercial saliente",4),
            (11,"recuperacion_cliente","Recuperacion de cliente",4),
            (12,"informacion_promocion","Informacion de promocion",4),
            (13,"pago_factura","Pago de factura",5),
            (14,"cobro_mora","Cobro o acuerdo por mora",5),
            (15,"consulta_factura","Consulta de factura",5),
        ], columns=["id_motivo","nombre_motivo","descripcion","id_tipo_servicio"])

        self.tables["resultados_llamada"] = pd.DataFrame([
            (1,"resuelta"),(2,"escalada"),(3,"pendiente"),(4,"abandonada"),
            (5,"no_contestada"),(6,"transferida"),(7,"venta_realizada")
        ], columns=["id_resultado","nombre_resultado"])

    def generate_clients(self) -> None:
        n = self.config.clients
        first = self.rng.choice(self.first_names, size=n)
        last = np.char.add(
            np.char.add(self.rng.choice(self.last_names, size=n), " "),
            self.rng.choice(self.last_names, size=n)
        )
        doc_types, docs = self._docs(n)
        cities = self._choice(
            list(self.cities),
            [0.25,0.18,0.12,0.08,0.06,0.05,0.04,0.04,0.03,0.02,0.03,0.03,0.02,0.03,0.02],
            size=n
        )
        usernames = np.char.lower(np.char.add(np.char.add(first.astype(str), "."), np.char.replace(last.astype(str), " ", "")))
        emails = np.array([f"{u}{int(self.rng.integers(1,999))}@correo.com" for u in usernames], dtype=object)
        null_mask = self.rng.random(n) < 0.12
        emails[null_mask] = None
        dates = self._random_dates(self.start_date - timedelta(days=720), self.end_date, n)
        estados = self._choice(["activo","inactivo","suspendido"], [0.85,0.10,0.05], size=n)
        self.tables["clientes"] = pd.DataFrame({
            "id_cliente": np.arange(1, n+1),
            "tipo_documento": doc_types,
            "numero_documento": docs,
            "nombre": first,
            "apellido": last,
            "direccion": [f"Calle {int(a)} #{int(b)}-{int(c)}" for a,b,c in self.rng.integers(1,120,size=(n,3))],
            "ciudad": cities,
            "telefono": self._colombian_mobile_numbers(n),
            "email": emails,
            "fecha_registro": pd.to_datetime(dates).date,
            "estado_cliente": estados,
        })

    def generate_agents(self) -> None:
        n = self.config.agents
        first = self.rng.choice(self.first_names, size=n)
        last = np.char.add(
            np.char.add(self.rng.choice(self.last_names, size=n), " "),
            self.rng.choice(self.last_names, size=n)
        )
        _, docs = self._docs(n)
        equipos = self.tables["equipos_trabajo"][["id_equipo","id_departamento"]]
        all_team_ids = equipos["id_equipo"].to_numpy()
        dept_map = dict(zip(equipos["id_equipo"], equipos["id_departamento"]))
        dept_to_teams = {
            int(dep): equipos.loc[equipos["id_departamento"] == dep, "id_equipo"].to_numpy()
            for dep in sorted(equipos["id_departamento"].unique())
        }
        probs = np.array([0.10,0.10,0.08,0.12,0.10,0.08,0.10,0.08,0.08,0.05,0.06,0.05], dtype=float)
        probs /= probs.sum()

        chosen_teams = []
        for dep in [1,2,3,4,5]:
            if len(chosen_teams) < n:
                chosen_teams.append(int(self.rng.choice(dept_to_teams[dep])))
        if n > len(chosen_teams):
            chosen_teams.extend(self.rng.choice(all_team_ids, size=n-len(chosen_teams), p=probs).tolist())
        chosen_teams = np.array(chosen_teams[:n])
        self.rng.shuffle(chosen_teams)
        depts = np.array([dept_map[int(t)] for t in chosen_teams])

        fecha_ingreso = self._random_dates(self.start_date - timedelta(days=1500), self.end_date - timedelta(days=1), n)
        perfiles = self._choice(["alto_fcr","alto_volumen","comercial","novato","balanceado"], [0.18,0.18,0.16,0.12,0.36], size=n)
        cargo = np.where(np.isin(depts, [3,4]), "asesor_comercial", "asesor_servicio")
        estados = self._choice(["activo","vacaciones","inactivo"], [0.67,0.17,0.16], size=n)

        agentes = pd.DataFrame({
            "id_agente": np.arange(1, n+1),
            "nombre": first,
            "apellido": last,
            "documento": docs,
            "cargo": cargo,
            "telefono": self._colombian_mobile_numbers(n),
            "email": [f"agente{i}@empresa.com" for i in range(1, n+1)],
            "fecha_ingreso": pd.to_datetime(fecha_ingreso).date,
            "estado_agente": estados,
            "id_equipo": chosen_teams,
            "id_departamento": depts,
            "perfil_desempeno": perfiles,
        })
        self.tables["agentes"] = agentes

        # agente_habilidad
        rows = []
        for row in agentes.itertuples(index=False):
            desired = int(self.rng.choice([1,2,3], p=[0.20,0.55,0.25]))
            preferred = []
            if row.id_departamento == 2:
                preferred += [2,4]
            elif row.id_departamento in [3,4]:
                preferred += [3,4]
            elif row.id_departamento == 5:
                preferred += [6,4]
            else:
                preferred += [1,4]
            if self.rng.random() < 0.15:
                preferred.append(5)
            selected = []
            for v in preferred:
                if v not in selected:
                    selected.append(v)
            while len(selected) < desired:
                candidate = int(self.rng.choice([1,2,3,4,5,6]))
                if candidate not in selected:
                    selected.append(candidate)
            for hid in selected[:desired]:
                rows.append((row.id_agente, hid))
        self.tables["agente_habilidad"] = pd.DataFrame(rows, columns=["id_agente","id_habilidad"]).drop_duplicates()

        # agente_turno
        rows = []
        aid = 1
        for row in agentes.itertuples(index=False):
            ranges = int(self.rng.choice([1,2], p=[0.75,0.25]))
            current = max(self.start_date, row.fecha_ingreso)
            for idx in range(ranges):
                tid = int(self.rng.choice([1,2,3], p=[0.42,0.43,0.15]))
                if idx == ranges - 1:
                    end = self.end_date
                else:
                    end = min(self.end_date, current + timedelta(days=int(self.rng.integers(45,100))))
                rows.append((aid, row.id_agente, tid, current, end))
                aid += 1
                current = min(self.end_date, end + timedelta(days=1))
        self.tables["agente_turno"] = pd.DataFrame(rows, columns=["id_agente_turno","id_agente","id_turno","fecha_inicio","fecha_fin"])

    def generate_products(self) -> None:
        target = int(self.rng.integers(self.config.products_target_min, self.config.products_target_max + 1))
        client_ids = self.tables["clientes"]["id_cliente"].to_numpy()
        counts = self.rng.choice([1,2,3,4], size=len(client_ids), p=[0.68,0.22,0.08,0.02])
        delta = target - int(counts.sum())
        idxs = np.arange(len(client_ids))
        while delta != 0:
            idx = int(self.rng.choice(idxs))
            if delta > 0 and counts[idx] < 4:
                counts[idx] += 1
                delta -= 1
            elif delta < 0 and counts[idx] > 1:
                counts[idx] -= 1
                delta += 1

        catalog = [
            ("plan_movil","movil",55000,110000,"mensual"),
            ("internet_hogar","hogar",75000,180000,"mensual"),
            ("television","hogar",45000,95000,"mensual"),
            ("soporte_premium","servicio",25000,60000,"mensual"),
            ("plan_empresarial","empresa",150000,350000,"mensual"),
            ("seguro_dispositivo","adicional",18000,45000,"bimestral"),
            ("streaming_bundle","adicional",20000,40000,"bimestral"),
        ]

        rows = []
        pid = 1
        for cid, count in zip(client_ids, counts):
            selected = self.rng.choice(np.arange(len(catalog)), size=int(count), replace=False)
            acq_dates = self._random_dates(self.start_date - timedelta(days=500), self.end_date, int(count))
            for idx, acq in zip(selected, acq_dates):
                name, cat, lo, hi, freq = catalog[int(idx)]
                state = self._choice(["activo","suspendido","cancelado"], [0.82,0.10,0.08], size=1)[0]
                rows.append((
                    pid, int(cid), name, cat, acq, state, freq, int(self.rng.integers(lo, hi+1))
                ))
                pid += 1
        self.tables["productos_servicios_cliente"] = pd.DataFrame(rows, columns=[
            "id_producto_cliente","id_cliente","nombre_producto_servicio","categoria",
            "fecha_adquisicion","estado_producto","frecuencia_facturacion","valor_base"
        ])

    def generate_invoices_and_payments(self) -> None:
        productos = self.tables["productos_servicios_cliente"]
        eligible = productos[productos["estado_producto"].isin(["activo","suspendido"])].copy()
        target = int(self.rng.integers(self.config.invoices_target_min, self.config.invoices_target_max + 1))
        inv_rows, pay_rows = [], []
        iid, pid = 1, 1

        # Proyección bruta de potencial de facturación.
        total_potential = 0
        expected_by_product = []
        for row in eligible.itertuples(index=False):
            start = max(self.start_date, row.fecha_adquisicion)
            periods = pd.period_range(start, self.end_date, freq="M")
            freq_div = 1 if row.frecuencia_facturacion == "mensual" else 2
            exp = max(1, math.ceil(len(periods) / freq_div))
            expected_by_product.append(exp)
            total_potential += exp
        scale = min(1.0, target / max(1, total_potential))
        eligible["expected_count"] = expected_by_product

        for row in eligible.itertuples(index=False):
            start = max(self.start_date, row.fecha_adquisicion)
            periods = pd.period_range(start, self.end_date, freq="M")
            chosen = []
            for i, period in enumerate(periods):
                if row.frecuencia_facturacion == "bimestral" and i % 2 == 1:
                    continue
                if self.rng.random() <= scale or len(chosen) == 0:
                    chosen.append(period)
            for period in chosen:
                emission = date(period.year, period.month, min(int(self.rng.integers(1,25)), 28))
                emission = self._clip_date_to_history(emission)
                due = min(emission + timedelta(days=int(self.rng.integers(10,20))), self.end_date)
                value = int(max(10000, row.valor_base + self.rng.integers(-8000, 12000)))
                state = self._choice(["pagada","pendiente","vencida","en_mora"], [0.70,0.14,0.10,0.06], size=1)[0]
                number = f"FAC-{emission.strftime('%Y%m')}-{iid:07d}"
                inv_rows.append((
                    iid, row.id_cliente, number, emission, due, value, state, row.id_producto_cliente, row.nombre_producto_servicio
                ))
                if state == "pagada":
                    pay_date = max(emission, due - timedelta(days=int(self.rng.integers(0,10))))
                    pay_date = self._clip_date_to_history(pay_date)
                    pay_rows.append((pid, iid, pay_date, value, self.rng.choice(["pse","tarjeta_credito","tarjeta_debito","transferencia","efectivo","debito_automatico"]), "aplicado"))
                    pid += 1
                elif self.rng.random() < (0.20 if state == "pendiente" else 0.12):
                    partial = int(value * float(self.rng.uniform(0.25, 0.85)))
                    partial_pay_date = self._clip_date_to_history(due + timedelta(days=int(self.rng.integers(0,25))))
                    pay_rows.append((pid, iid, partial_pay_date, partial, self.rng.choice(["pse","tarjeta_credito","tarjeta_debito","transferencia","efectivo","debito_automatico"]), "parcial"))
                    pid += 1
                iid += 1

        facturas = pd.DataFrame(inv_rows, columns=[
            "id_factura","id_cliente","numero_factura","fecha_emision","fecha_vencimiento",
            "valor_total","estado_factura","id_producto_cliente","producto_origen"
        ])
        pagos = pd.DataFrame(pay_rows, columns=[
            "id_pago","id_factura","fecha_pago","valor_pagado","metodo_pago","estado_pago"
        ])
        if len(facturas) > self.config.invoices_target_max:
            keep = self.rng.choice(facturas.index, size=self.config.invoices_target_max, replace=False)
            facturas = facturas.loc[np.sort(keep)].copy()
            pagos = pagos[pagos["id_factura"].isin(set(facturas["id_factura"].tolist()))].copy()
        if len(pagos) > self.config.payments_target_max:
            keep = self.rng.choice(pagos.index, size=self.config.payments_target_max, replace=False)
            pagos = pagos.loc[np.sort(keep)].copy()

        self.tables["facturas"] = facturas.reset_index(drop=True)
        self.tables["pagos"] = pagos.reset_index(drop=True)

    def _motives_by_service(self) -> Dict[int, List[int]]:
        m = self.tables["motivos_llamada"]
        return {int(s): m.loc[m["id_tipo_servicio"] == s, "id_motivo"].astype(int).tolist() for s in sorted(m["id_tipo_servicio"].unique())}

    def _agent_pool_by_dept(self) -> Dict[int, np.ndarray]:
        agents = self.tables["agentes"]
        pools = {}
        for d in [1,2,3,4,5]:
            arr = agents.loc[agents["id_departamento"] == d, "id_agente"].to_numpy()
            if len(arr) == 0:
                arr = agents["id_agente"].to_numpy()
            pools[d] = arr
        return pools

    def generate_cases_and_calls(self) -> None:
        target_cases = int(self.rng.integers(self.config.cases_target_min, self.config.cases_target_max + 1))
        motives_by_service = self._motives_by_service()
        clients = self.tables["clientes"]
        agents = self.tables["agentes"]
        dept_agents = self._agent_pool_by_dept()
        profile_map = dict(zip(agents["id_agente"], agents["perfil_desempeno"]))
        client_status = dict(zip(clients["id_cliente"], clients["estado_cliente"]))

        case_rows, call_rows = [], []
        call_id = 1

        for case_id in range(1, target_cases + 1):
            client_id = int(self.rng.choice(clients["id_cliente"].to_numpy()))
            service_id = int(self.rng.choice([1,2,3,4,5], p=[0.26,0.27,0.14,0.09,0.24]))
            motive_id = int(self.rng.choice(motives_by_service[service_id]))
            open_dt = self._sample_timestamps(1)[0]
            priority = self._choice(["baja","media","alta","critica"], [0.40,0.38,0.17,0.05], size=1)[0]

            difficulty = 0.0
            if service_id == 2:
                difficulty += 0.15
            if motive_id in [4,5,6,14]:
                difficulty += 0.10
            if priority in ["alta","critica"]:
                difficulty += 0.12
            if client_status[client_id] == "suspendido":
                difficulty += 0.05

            fcr_prob = float(np.clip(0.58 - difficulty, 0.18, 0.82))
            is_fcr = bool(self.rng.random() < fcr_prob)
            call_count = 1 if is_fcr else int(self.rng.choice([2,3,4,5], p=[0.46,0.30,0.18,0.06]))
            final_case_state = "cerrado" if is_fcr else self._choice(["en_proceso","cerrado","cancelado"], [0.45,0.48,0.07], size=1)[0]
            close_dt = None
            if final_case_state in ["cerrado","cancelado"]:
                close_dt = open_dt + timedelta(days=int(self.rng.integers(0,21)), hours=int(self.rng.integers(0,12)))

            case_rows.append((
                case_id, client_id, service_id, motive_id, f"Caso {case_id} asociado a motivo {motive_id}",
                open_dt, close_dt if close_dt else None, final_case_state, 1 if is_fcr else 0, priority
            ))

            current_dt = open_dt
            for seq in range(call_count):
                agent_id = int(self.rng.choice(dept_agents[service_id]))
                profile = profile_map[agent_id]
                if seq > 0:
                    current_dt = current_dt + timedelta(days=int(self.rng.integers(1,12)), hours=int(self.rng.integers(0,8)))
                wait_base = {1:85, 2:110, 3:70, 4:65, 5:95}[service_id]
                dur_base = {1:280, 2:510, 3:240, 4:210, 5:260}[service_id]
                if profile == "alto_fcr":
                    wait_base -= 10
                    dur_base += 10
                    res_bonus = 0.10
                elif profile == "alto_volumen":
                    wait_base -= 5
                    dur_base -= 20
                    res_bonus = -0.03
                elif profile == "comercial":
                    res_bonus = 0.04 if service_id in [3,4] else 0.0
                elif profile == "novato":
                    wait_base += 5
                    dur_base += 30
                    res_bonus = -0.09
                else:
                    res_bonus = 0.0

                wait_s = int(max(0, self.rng.normal(wait_base, 45)))
                dur_s = int(max(35, self.rng.lognormal(np.log(max(60, dur_base)), 0.35)))

                if seq == 0 and self.rng.random() < 0.05:
                    result = "abandonada"
                    dur_s = int(max(5, dur_s * 0.15))
                    call_agent = np.nan
                else:
                    call_agent = agent_id
                    if seq == call_count - 1:
                        if service_id in [3,4] and motive_id in [7,8,9,10,11,12] and self.rng.random() < max(0.06, 0.18 + res_bonus):
                            result = "venta_realizada"
                        elif final_case_state == "cerrado":
                            result = "resuelta"
                        elif final_case_state == "cancelado":
                            result = "pendiente"
                        else:
                            result = self._choice(["escalada","pendiente","transferida"], [0.36,0.44,0.20], size=1)[0]
                    else:
                        result = self._choice(["pendiente","escalada","transferida"], [0.45,0.30,0.25], size=1)[0]

                result_id = {"resuelta":1,"escalada":2,"pendiente":3,"abandonada":4,"no_contestada":5,"transferida":6,"venta_realizada":7}[result]
                start_dt, end_dt = self._bounded_service_call_window(service_id, current_dt, dur_s)
                tipo = "entrante" if service_id != 4 else self._choice(["entrante","saliente"], [0.20,0.80], size=1)[0]
                canal = self._choice(["telefono","voip","campana"], [0.68,0.24,0.08], size=1)[0]
                follow = 1 if result in ["pendiente","escalada","transferida"] else 0

                call_rows.append((
                    call_id, client_id, call_agent, service_id, case_id, service_id, motive_id, result_id,
                    tipo, start_dt, end_dt, dur_s, wait_s, canal, follow
                ))
                call_id += 1
                current_dt = end_dt

        casos = pd.DataFrame(case_rows, columns=[
            "id_caso","id_cliente","id_tipo_servicio","id_motivo","descripcion_caso",
            "fecha_apertura","fecha_cierre","estado_caso","resuelto_primer_contacto","prioridad"
        ])
        calls = pd.DataFrame(call_rows, columns=[
            "id_llamada","id_cliente","id_agente","id_departamento","id_caso","id_tipo_servicio","id_motivo",
            "id_resultado","tipo_llamada","fecha_hora_inicio","fecha_hora_fin","duracion_segundos",
            "tiempo_espera_segundos","canal","requiere_seguimiento"
        ])

        target_calls = int(self.rng.integers(self.config.calls_target_min, self.config.calls_target_max + 1))
        extra_needed = max(0, target_calls - len(calls))
        if extra_needed > 0:
            calls = pd.concat([calls, self._generate_non_case_calls(call_id, extra_needed)], ignore_index=True)

        # FCR derivado desde llamadas reales
        case_calls = calls.dropna(subset=["id_caso"]).copy()
        call_counts = case_calls.groupby("id_caso")["id_llamada"].count()
        last_result = case_calls.sort_values("fecha_hora_inicio").groupby("id_caso")["id_resultado"].last()
        valid_fcr = set(call_counts[call_counts == 1].index.astype(int).tolist()) & set(last_result[last_result.isin([1,7])].index.astype(int).tolist())
        casos["resuelto_primer_contacto"] = casos["id_caso"].isin(valid_fcr).astype(int)
        casos.loc[casos["resuelto_primer_contacto"] == 1, "estado_caso"] = "cerrado"
        casos.loc[casos["fecha_cierre"].isna() & (casos["estado_caso"] == "cerrado"), "fecha_cierre"] = casos["fecha_apertura"]

        last_call_end = (
            calls.dropna(subset=["id_caso"])
            .assign(id_caso=lambda df: df["id_caso"].astype(int))
            .groupby("id_caso")["fecha_hora_fin"]
            .max()
        )
        casos = casos.merge(last_call_end.rename("ultima_llamada_fin"), left_on="id_caso", right_index=True, how="left")

        closed_mask = casos["estado_caso"].isin(["cerrado", "cancelado"])
        missing_close_mask = closed_mask & casos["fecha_cierre"].isna()
        casos.loc[missing_close_mask, "fecha_cierre"] = casos.loc[missing_close_mask, "fecha_apertura"]

        case_close = pd.to_datetime(casos["fecha_cierre"], errors="coerce")
        last_end = pd.to_datetime(casos["ultima_llamada_fin"], errors="coerce")
        aligned_close = pd.concat([case_close, last_end], axis=1).max(axis=1)
        align_mask = closed_mask & last_end.notna()
        casos.loc[align_mask, "fecha_cierre"] = aligned_close[align_mask]

        history_end = self._history_end_datetime()
        case_close = pd.to_datetime(casos["fecha_cierre"], errors="coerce")
        casos.loc[case_close > history_end, "fecha_cierre"] = history_end
        casos = casos.drop(columns=["ultima_llamada_fin"])

        self.tables["casos"] = casos
        self.tables["llamadas"] = calls.sort_values("fecha_hora_inicio").reset_index(drop=True)

    def _generate_non_case_calls(self, start_call_id: int, size: int) -> pd.DataFrame:
        motives_by_service = self._motives_by_service()
        clients = self.tables["clientes"]
        agents = self.tables["agentes"]
        profile_map = dict(zip(agents["id_agente"], agents["perfil_desempeno"]))
        dept_agents = self._agent_pool_by_dept()
        times = self._sample_timestamps(size)
        rows = []
        for i in range(size):
            service_id = int(self.rng.choice([1,2,3,4,5], p=[0.27,0.18,0.15,0.10,0.30]))
            motive_id = int(self.rng.choice(motives_by_service[service_id]))
            agent_id = int(self.rng.choice(dept_agents[service_id]))
            profile = profile_map[agent_id]
            wait_base = {1:65, 2:95, 3:55, 4:50, 5:85}[service_id]
            dur_base = {1:210, 2:420, 3:190, 4:180, 5:220}[service_id]
            if profile == "novato":
                wait_base += 10
                dur_base += 20
            elif profile == "alto_volumen":
                dur_base -= 20

            if self.rng.random() < 0.03:
                result = "no_contestada"
                wait_s = int(max(0, self.rng.normal(wait_base + 20, 35)))
                dur_s = int(self.rng.integers(10,60))
                call_agent = np.nan
            elif self.rng.random() < 0.05:
                result = "abandonada"
                wait_s = int(max(0, self.rng.normal(wait_base + 10, 35)))
                dur_s = int(self.rng.integers(8,70))
                call_agent = np.nan
            else:
                wait_s = int(max(0, self.rng.normal(wait_base, 30)))
                dur_s = int(max(20, self.rng.lognormal(np.log(max(60, dur_base)), 0.32)))
                if service_id in [3,4] and motive_id in [7,8,9,10,11,12] and self.rng.random() < 0.10:
                    result = "venta_realizada"
                else:
                    result = self._choice(["resuelta","transferida","pendiente"], [0.76,0.11,0.13], size=1)[0]
                call_agent = agent_id

            result_id = {"resuelta":1,"escalada":2,"pendiente":3,"abandonada":4,"no_contestada":5,"transferida":6,"venta_realizada":7}[result]
            start_dt, end_dt = self._bounded_service_call_window(service_id, times[i], dur_s)
            tipo = self._choice(["entrante","saliente"], [0.80,0.20], size=1)[0] if service_id != 4 else self._choice(["entrante","saliente"], [0.18,0.82], size=1)[0]
            canal = self._choice(["telefono","voip","campana"], [0.72,0.22,0.06], size=1)[0]
            follow = 1 if result in ["pendiente","transferida"] else 0

            rows.append((
                start_call_id + i, int(self.rng.choice(clients["id_cliente"].to_numpy())), call_agent, service_id, np.nan, service_id, motive_id,
                result_id, tipo, start_dt, end_dt, dur_s, wait_s, canal, follow
            ))
        return pd.DataFrame(rows, columns=[
            "id_llamada","id_cliente","id_agente","id_departamento","id_caso","id_tipo_servicio","id_motivo",
            "id_resultado","tipo_llamada","fecha_hora_inicio","fecha_hora_fin","duracion_segundos",
            "tiempo_espera_segundos","canal","requiere_seguimiento"
        ])

    def generate_surveys(self) -> None:
        calls = self.tables["llamadas"]
        cases = self.tables["casos"][["id_caso","resuelto_primer_contacto"]]
        fcr_map = dict(zip(cases["id_caso"], cases["resuelto_primer_contacto"]))
        eligible = calls[~calls["id_resultado"].isin([4,5])].copy()
        history_end = self._history_end_datetime()
        eligible = eligible[
            pd.to_datetime(eligible["fecha_hora_fin"]) <= (history_end - timedelta(hours=1))
        ].copy()
        target = int(self.rng.integers(self.config.surveys_target_min, self.config.surveys_target_max + 1))
        n = min(len(eligible), target)
        selected = eligible.loc[self.rng.choice(eligible.index.to_numpy(), size=n, replace=False)].copy()
        comments = np.array([
            "Buena atencion","Tiempo de espera alto","Caso resuelto","Se requiere seguimiento",
            "Asesor amable","No solucionaron del todo","Proceso claro","Quedo pendiente",
            "Muy buena experiencia","Servicio regular","Atencion rapida","Esperaba mas"
        ])
        rows = []
        for idx, row in enumerate(selected.itertuples(index=False), start=1):
            fcr = int(fcr_map.get(int(row.id_caso), 0)) if pd.notna(row.id_caso) else 0
            score = 4.0
            if row.tiempo_espera_segundos > 180:
                score -= 1.0
            elif row.tiempo_espera_segundos > 90:
                score -= 0.5
            if row.id_resultado in [2,3,6]:
                score -= 0.7
            if row.id_resultado in [1,7]:
                score += 0.4
            score += 0.4 if fcr == 1 else -0.3
            if row.duracion_segundos > 700:
                score -= 0.2
            noisy = score + float(self.rng.normal(0, 0.65))
            rating = int(np.clip(round(noisy), 1, 5))
            comment = None if self.rng.random() < 0.35 else str(self.rng.choice(comments))
            survey_date = pd.Timestamp(row.fecha_hora_fin) + timedelta(
                hours=int(self.rng.integers(1,72)),
                minutes=int(self.rng.integers(0,60)),
                seconds=int(self.rng.integers(0,60)),
            )
            if survey_date.to_pydatetime() > history_end:
                survey_date = pd.Timestamp(history_end)
            rows.append((idx, int(row.id_llamada), int(row.id_cliente), rating, comment, survey_date))
        self.tables["encuestas_satisfaccion"] = pd.DataFrame(rows, columns=[
            "id_encuesta","id_llamada","id_cliente","calificacion","comentario","fecha_encuesta"
        ])

    # ---------- Validation ----------

    def validate(self) -> None:
        val = {}

        def record(name: str, passed: bool, detail):
            val[name] = {"passed": bool(passed), "detail": detail}

        pk_map = {
            "clientes":"id_cliente","departamentos":"id_departamento","equipos_trabajo":"id_equipo",
            "agentes":"id_agente","habilidades":"id_habilidad","turnos":"id_turno",
            "tipos_servicio":"id_tipo_servicio","motivos_llamada":"id_motivo",
            "resultados_llamada":"id_resultado","productos_servicios_cliente":"id_producto_cliente",
            "facturas":"id_factura","pagos":"id_pago","casos":"id_caso","llamadas":"id_llamada",
            "encuestas_satisfaccion":"id_encuesta","agente_turno":"id_agente_turno"
        }
        for table, pk in pk_map.items():
            dup = int(self.tables[table][pk].duplicated().sum())
            record(f"{table}.pk_unique", dup == 0, {"duplicates": dup})

        def invalid_fk(child: str, col: str, parent: str, pk: str) -> int:
            valid = set(self.tables[parent][pk].dropna().astype(int).tolist())
            vals = self.tables[child][col].dropna().astype(int)
            return int((~vals.isin(valid)).sum())

        fk_checks = [
            ("equipos_trabajo.id_departamento", invalid_fk("equipos_trabajo","id_departamento","departamentos","id_departamento")),
            ("agentes.id_equipo", invalid_fk("agentes","id_equipo","equipos_trabajo","id_equipo")),
            ("agentes.id_departamento", invalid_fk("agentes","id_departamento","departamentos","id_departamento")),
            ("agente_habilidad.id_agente", invalid_fk("agente_habilidad","id_agente","agentes","id_agente")),
            ("agente_habilidad.id_habilidad", invalid_fk("agente_habilidad","id_habilidad","habilidades","id_habilidad")),
            ("agente_turno.id_agente", invalid_fk("agente_turno","id_agente","agentes","id_agente")),
            ("agente_turno.id_turno", invalid_fk("agente_turno","id_turno","turnos","id_turno")),
            ("motivos_llamada.id_tipo_servicio", invalid_fk("motivos_llamada","id_tipo_servicio","tipos_servicio","id_tipo_servicio")),
            ("productos_servicios_cliente.id_cliente", invalid_fk("productos_servicios_cliente","id_cliente","clientes","id_cliente")),
            ("facturas.id_cliente", invalid_fk("facturas","id_cliente","clientes","id_cliente")),
            ("facturas.id_producto_cliente", invalid_fk("facturas","id_producto_cliente","productos_servicios_cliente","id_producto_cliente")),
            ("pagos.id_factura", invalid_fk("pagos","id_factura","facturas","id_factura")),
            ("casos.id_cliente", invalid_fk("casos","id_cliente","clientes","id_cliente")),
            ("casos.id_tipo_servicio", invalid_fk("casos","id_tipo_servicio","tipos_servicio","id_tipo_servicio")),
            ("casos.id_motivo", invalid_fk("casos","id_motivo","motivos_llamada","id_motivo")),
            ("llamadas.id_cliente", invalid_fk("llamadas","id_cliente","clientes","id_cliente")),
            ("llamadas.id_agente", invalid_fk("llamadas","id_agente","agentes","id_agente")),
            ("llamadas.id_departamento", invalid_fk("llamadas","id_departamento","departamentos","id_departamento")),
            ("llamadas.id_caso", invalid_fk("llamadas","id_caso","casos","id_caso")),
            ("llamadas.id_tipo_servicio", invalid_fk("llamadas","id_tipo_servicio","tipos_servicio","id_tipo_servicio")),
            ("llamadas.id_motivo", invalid_fk("llamadas","id_motivo","motivos_llamada","id_motivo")),
            ("llamadas.id_resultado", invalid_fk("llamadas","id_resultado","resultados_llamada","id_resultado")),
            ("encuestas.id_llamada", invalid_fk("encuestas_satisfaccion","id_llamada","llamadas","id_llamada")),
            ("encuestas.id_cliente", invalid_fk("encuestas_satisfaccion","id_cliente","clientes","id_cliente")),
        ]
        for name, invalid in fk_checks:
            record(name, invalid == 0, {"invalid": invalid})

        llamadas = self.tables["llamadas"].copy()
        mismatch = int((((pd.to_datetime(llamadas["fecha_hora_fin"]) - pd.to_datetime(llamadas["fecha_hora_inicio"])).dt.total_seconds()).round().astype(int) != llamadas["duracion_segundos"].astype(int)).sum())
        record("llamadas.duration_matches_timestamps", mismatch == 0, {"mismatches": mismatch})
        neg_wait = int((llamadas["tiempo_espera_segundos"].astype(int) < 0).sum())
        record("llamadas.non_negative_wait", neg_wait == 0, {"negative_waits": neg_wait})

        history_start_dt = self._history_start_datetime()
        history_end_dt = self._history_end_datetime()

        def record_datetime_range(table_name: str, column_name: str) -> None:
            series = pd.to_datetime(self.tables[table_name][column_name], errors="coerce").dropna()
            before = int((series < history_start_dt).sum())
            after = int((series > history_end_dt).sum())
            record(
                f"{table_name}.{column_name}_within_history_range",
                before == 0 and after == 0,
                {"before_start": before, "after_end": after}
            )

        for table_name, column_name in [
            ("llamadas", "fecha_hora_inicio"),
            ("llamadas", "fecha_hora_fin"),
            ("casos", "fecha_apertura"),
            ("casos", "fecha_cierre"),
            ("encuestas_satisfaccion", "fecha_encuesta"),
        ]:
            record_datetime_range(table_name, column_name)

        def record_date_range(table_name: str, column_name: str) -> None:
            series = pd.to_datetime(self.tables[table_name][column_name], errors="coerce").dropna()
            start_bound = pd.Timestamp(self.start_date)
            end_bound = pd.Timestamp(self.end_date)
            before = int((series < start_bound).sum())
            after = int((series > end_bound).sum())
            record(
                f"{table_name}.{column_name}_within_history_range",
                before == 0 and after == 0,
                {"before_start": before, "after_end": after}
            )

        for table_name, column_name in [
            ("facturas", "fecha_emision"),
            ("facturas", "fecha_vencimiento"),
            ("pagos", "fecha_pago"),
        ]:
            record_date_range(table_name, column_name)

        call_days = set(pd.to_datetime(llamadas["fecha_hora_inicio"]).dt.date.tolist())
        expected_days = set(pd.date_range(self.start_date, self.end_date, freq="D").date.tolist())
        missing_days = sorted(d.isoformat() for d in expected_days - call_days)
        record(
            "llamadas.daily_coverage",
            len(missing_days) == 0,
            {"missing_days": missing_days[:20], "missing_days_count": len(missing_days)}
        )

        def invalid_operating_calendar_rows(df: pd.DataFrame, service_id: int) -> int:
            if df.empty:
                return 0
            service = self._service_calendar(service_id)
            if int(service["start_hour"]) == 0 and int(service["end_hour"]) == 24:
                return 0

            starts = pd.to_datetime(df["fecha_hora_inicio"], errors="coerce")
            ends = pd.to_datetime(df["fecha_hora_fin"], errors="coerce")
            weekdays = starts.dt.weekday
            start_hours = starts.dt.hour + starts.dt.minute / 60 + starts.dt.second / 3600
            end_hours = ends.dt.hour + ends.dt.minute / 60 + ends.dt.second / 3600
            same_day = starts.dt.date == ends.dt.date

            invalid = (
                ~weekdays.isin(service["weekdays"])
                | (start_hours < int(service["start_hour"]))
                | (end_hours > int(service["end_hour"]))
                | (~same_day)
            )
            return int(invalid.sum())

        for service_id, label in [
            (1, "atencion_cliente"),
            (3, "ventas"),
            (4, "telemarketing"),
            (5, "facturacion"),
        ]:
            service_calls = llamadas[llamadas["id_tipo_servicio"].astype(int) == service_id]
            invalid_rows = invalid_operating_calendar_rows(service_calls, service_id)
            record(
                f"llamadas.{label}_operating_calendar",
                invalid_rows == 0,
                {"invalid_rows": invalid_rows}
            )

        motivos = self.tables["motivos_llamada"][["id_motivo", "id_tipo_servicio"]].copy()
        motivos["id_motivo"] = motivos["id_motivo"].astype(int)
        motivos["id_tipo_servicio"] = motivos["id_tipo_servicio"].astype(int)

        for table_name in ["casos", "llamadas"]:
            merged = self.tables[table_name][["id_motivo", "id_tipo_servicio"]].copy()
            merged = merged.dropna(subset=["id_motivo", "id_tipo_servicio"])
            merged["id_motivo"] = merged["id_motivo"].astype(int)
            merged["id_tipo_servicio"] = merged["id_tipo_servicio"].astype(int)
            merged = merged.merge(
                motivos.rename(columns={"id_tipo_servicio": "id_tipo_servicio_motivo"}),
                on="id_motivo",
                how="left"
            )
            mismatches = int((merged["id_tipo_servicio"] != merged["id_tipo_servicio_motivo"]).sum())
            record(
                f"{table_name}.motivo_matches_tipo_servicio",
                mismatches == 0,
                {"mismatches": mismatches}
            )

        casos = self.tables["casos"].dropna(subset=["fecha_cierre"]).copy()
        invalid_case_dates = int((pd.to_datetime(casos["fecha_cierre"]) < pd.to_datetime(casos["fecha_apertura"])).sum())
        record("casos.valid_dates", invalid_case_dates == 0, {"invalid_case_dates": invalid_case_dates})

        fact = self.tables["facturas"].copy()
        invalid_due = int((pd.to_datetime(fact["fecha_vencimiento"]) < pd.to_datetime(fact["fecha_emision"])).sum())
        record("facturas.valid_due_dates", invalid_due == 0, {"invalid_due_dates": invalid_due})

        pagos = self.tables["pagos"].copy()
        if len(pagos):
            merged = pagos.merge(fact[["id_factura","fecha_emision","valor_total"]], on="id_factura", how="left")
            invalid_pay_dates = int((pd.to_datetime(merged["fecha_pago"]) < pd.to_datetime(merged["fecha_emision"])).sum())
            record("pagos.valid_dates", invalid_pay_dates == 0, {"invalid_payment_dates": invalid_pay_dates})
            totals = merged.groupby("id_factura", as_index=False)["valor_pagado"].sum().merge(fact[["id_factura","valor_total"]], on="id_factura")
            over = int((totals["valor_pagado"] > totals["valor_total"]).sum())
            record("pagos.not_over_invoice_total", over == 0, {"overpaid_invoices": over})
        else:
            record("pagos.valid_dates", True, {"invalid_payment_dates": 0})
            record("pagos.not_over_invoice_total", True, {"overpaid_invoices": 0})

        enc = self.tables["encuestas_satisfaccion"].copy()
        if len(enc):
            merged = enc.merge(llamadas[["id_llamada","fecha_hora_fin","id_resultado"]], on="id_llamada", how="left")
            invalid_survey_dates = int((pd.to_datetime(merged["fecha_encuesta"]) < pd.to_datetime(merged["fecha_hora_fin"]).dt.normalize()).sum())
            record("encuestas.valid_dates", invalid_survey_dates == 0, {"invalid_survey_dates": invalid_survey_dates})
            invalid_surveys = int(merged["id_resultado"].isin([4,5]).sum())
            record("encuestas.not_on_abandoned_or_no_answer", invalid_surveys == 0, {"invalid_surveys": invalid_surveys})
        else:
            record("encuestas.valid_dates", True, {"invalid_survey_dates": 0})
            record("encuestas.not_on_abandoned_or_no_answer", True, {"invalid_surveys": 0})

        sales = llamadas[llamadas["id_resultado"] == 7]
        invalid_sales = int((~sales["id_tipo_servicio"].isin([3,4])).sum())
        record("ventas.only_on_commercial_services", invalid_sales == 0, {"invalid_sales_rows": invalid_sales})

        fcr_cases = self.tables["casos"][self.tables["casos"]["resuelto_primer_contacto"] == 1]
        if len(fcr_cases):
            counts = llamadas.dropna(subset=["id_caso"]).groupby("id_caso")["id_llamada"].count()
            invalid_fcr = int(sum(counts.get(int(cid), 0) != 1 for cid in fcr_cases["id_caso"]))
            record("casos.fcr_has_single_call", invalid_fcr == 0, {"invalid_fcr_cases": invalid_fcr})
        else:
            record("casos.fcr_has_single_call", True, {"invalid_fcr_cases": 0})

        case_calls_for_close = llamadas.dropna(subset=["id_caso"]).copy()
        if len(case_calls_for_close):
            case_calls_for_close["id_caso"] = case_calls_for_close["id_caso"].astype(int)
            last_call_end = case_calls_for_close.groupby("id_caso")["fecha_hora_fin"].max()
            closed_cases = self.tables["casos"][
                self.tables["casos"]["estado_caso"].isin(["cerrado", "cancelado"])
                & self.tables["casos"]["fecha_cierre"].notna()
            ][["id_caso", "fecha_cierre"]].copy()
            closed_cases["id_caso"] = closed_cases["id_caso"].astype(int)
            closed_cases = closed_cases.merge(
                last_call_end.rename("ultima_llamada_fin"),
                left_on="id_caso",
                right_index=True,
                how="left"
            )
            invalid_close = int(
                (
                    pd.to_datetime(closed_cases["fecha_cierre"], errors="coerce")
                    < pd.to_datetime(closed_cases["ultima_llamada_fin"], errors="coerce")
                ).sum()
            )
            record("casos.close_after_last_call", invalid_close == 0, {"invalid_closed_cases": invalid_close})
        else:
            record("casos.close_after_last_call", True, {"invalid_closed_cases": 0})

        self.report["validations"] = val
        self.report["row_counts"] = {k: int(len(v)) for k, v in self.tables.items()}

    # ---------- Export ----------

    def _prepare_sql_exports(self) -> Dict[str, pd.DataFrame]:
        export_tables: Dict[str, pd.DataFrame] = {}
        for name, columns in SQL_EXPORT_COLUMNS.items():
            export_tables[name] = self.tables[name].copy()

        export_tables["clientes"]["tipo_documento"] = export_tables["clientes"]["tipo_documento"].astype(str).str.upper()
        export_tables["pagos"]["metodo_pago"] = export_tables["pagos"]["metodo_pago"].replace({
            "debito_automatico": "recaudo_externo"
        })

        # Evita que columnas FK enteras con nulos se exporten como 18.0, 333.0, etc.
        nullable_integer_columns = {
            "llamadas": ["id_agente", "id_caso"],
        }
        for table_name, columns in nullable_integer_columns.items():
            for column in columns:
                export_tables[table_name][column] = (
                    pd.to_numeric(export_tables[table_name][column], errors="coerce")
                    .astype("Int64")
                )

        export_tables["casos"]["fecha_apertura"] = pd.to_datetime(export_tables["casos"]["fecha_apertura"])
        export_tables["casos"]["fecha_cierre"] = pd.to_datetime(export_tables["casos"]["fecha_cierre"])
        export_tables["encuestas_satisfaccion"]["fecha_encuesta"] = pd.to_datetime(export_tables["encuestas_satisfaccion"]["fecha_encuesta"])

        cleaned_tables = {
            name: df.loc[:, SQL_EXPORT_COLUMNS[name]].copy()
            for name, df in export_tables.items()
        }

        for df in cleaned_tables.values():
            for column in df.select_dtypes(include=["object", "string"]).columns:
                df[column] = df[column].map(self._ascii_text)

        return cleaned_tables

    def _build_psql_loader(self, export_tables: Dict[str, pd.DataFrame]) -> str:
        lines = [
            "\\set ON_ERROR_STOP on",
            "BEGIN;",
            "SET search_path TO call_center_analytics;",
            "",
            "TRUNCATE TABLE encuestas_satisfaccion, llamadas, casos, pagos, facturas, productos_servicios_cliente, agente_turno, agente_habilidad, motivos_llamada, agentes, equipos_trabajo, clientes, resultados_llamada, tipos_servicio, turnos, habilidades, departamentos RESTART IDENTITY CASCADE;",
            "",
        ]

        for table_name in LOAD_ORDER:
            staging_table = f"stg_{table_name}"
            csv_path = (self.output_dir / f"{table_name}.csv").resolve().as_posix()
            columns = SQL_EXPORT_COLUMNS[table_name]
            column_list = ", ".join(columns)
            lines.extend([
                f"CREATE TEMP TABLE {staging_table} AS SELECT {column_list} FROM call_center_analytics.{table_name} WITH NO DATA;",
                f"\\copy {staging_table} ({column_list}) FROM '{csv_path}' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');",
            ])
            if table_name in IDENTITY_PK_MAP:
                lines.append(
                    f"INSERT INTO call_center_analytics.{table_name} ({column_list}) OVERRIDING SYSTEM VALUE SELECT {column_list} FROM {staging_table};"
                )
            else:
                lines.append(
                    f"INSERT INTO call_center_analytics.{table_name} ({column_list}) SELECT {column_list} FROM {staging_table};"
                )
            lines.append(f"DROP TABLE {staging_table};")
            lines.append("")

        for table_name, pk_name in IDENTITY_PK_MAP.items():
            lines.append(
                "SELECT setval(" 
                f"pg_get_serial_sequence('call_center_analytics.{table_name}', '{pk_name}'), "
                f"COALESCE((SELECT MAX({pk_name}) FROM call_center_analytics.{table_name}), 1), true);"
            )

        lines.extend([
            "",
            "COMMIT;",
        ])
        return "\n".join(lines)

    def export(self) -> None:
        export_tables = self._prepare_sql_exports()
        for name, df in export_tables.items():
            out = df.copy()
            for col in out.columns:
                if pd.api.types.is_datetime64_any_dtype(out[col]):
                    out[col] = out[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            out.to_csv(self.output_dir / f"{name}.csv", index=False, encoding="utf-8")

        pd.DataFrame([{"tabla": k, "filas": len(v)} for k, v in export_tables.items()]).sort_values("tabla").to_csv(
            self.output_dir / "row_counts.csv", index=False, encoding="utf-8"
        )
        with open(self.output_dir / "quality_report.json", "w", encoding="utf-8") as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2, default=str)
        with open(self.output_dir / "generation_log.json", "w", encoding="utf-8") as f:
            json.dump({
                "config": asdict(self.config),
                "output_dir": str(self.output_dir.resolve()),
                "generated_files": sorted([p.name for p in self.output_dir.glob("*.csv")]),
            }, f, ensure_ascii=False, indent=2)
        with open(self.output_dir / "load_call_center_postgresql.sql", "w", encoding="utf-8") as f:
            f.write(self._build_psql_loader(export_tables))

    def run(self) -> None:
        self.generate_catalogs()
        self.generate_clients()
        self.generate_agents()
        self.generate_products()
        self.generate_invoices_and_payments()
        self.generate_cases_and_calls()
        self.generate_surveys()
        self.validate()
        self.export()


def parse_args() -> GenerationConfig:
    p = argparse.ArgumentParser(description="Genera datos sintéticos históricos para un call center.")
    p.add_argument("--output-dir", default="./output_call_center")
    p.add_argument("--seed", type=int, default=20260410)
    p.add_argument("--history-months", type=int, default=6)
    p.add_argument("--start-date", default=None)
    p.add_argument("--end-date", default=date.today().isoformat())
    p.add_argument("--clients", type=int, default=30000)
    p.add_argument("--agents", type=int, default=180)
    p.add_argument("--surveys-target-min", type=int, default=20000)
    p.add_argument("--surveys-target-max", type=int, default=32000)
    p.add_argument("--calls-target-min", type=int, default=95000)
    p.add_argument("--calls-target-max", type=int, default=135000)
    p.add_argument("--invoices-target-min", type=int, default=85000)
    p.add_argument("--invoices-target-max", type=int, default=110000)
    p.add_argument("--cases-target-min", type=int, default=24000)
    p.add_argument("--cases-target-max", type=int, default=32000)
    p.add_argument("--products-target-min", type=int, default=42000)
    p.add_argument("--products-target-max", type=int, default=50000)
    p.add_argument("--payments-target-min", type=int, default=70000)
    p.add_argument("--payments-target-max", type=int, default=100000)
    a = p.parse_args()
    return GenerationConfig(
        seed=a.seed, output_dir=a.output_dir, history_months=a.history_months, start_date=a.start_date, end_date=a.end_date,
        clients=a.clients, agents=a.agents,
        surveys_target_min=a.surveys_target_min, surveys_target_max=a.surveys_target_max,
        calls_target_min=a.calls_target_min, calls_target_max=a.calls_target_max,
        invoices_target_min=a.invoices_target_min, invoices_target_max=a.invoices_target_max,
        cases_target_min=a.cases_target_min, cases_target_max=a.cases_target_max,
        products_target_min=a.products_target_min, products_target_max=a.products_target_max,
        payments_target_min=a.payments_target_min, payments_target_max=a.payments_target_max,
    )


if __name__ == "__main__":
    cfg = parse_args()
    gen = SyntheticCallCenterGenerator(cfg)
    gen.run()
    print(f"Generación finalizada en: {Path(cfg.output_dir).resolve()}")


from pathlib import Path
from getpass import getpass
from io import StringIO
import os
import subprocess
import textwrap

import pandas as pd
import matplotlib.pyplot as plt


DB_NAME = "betek_call_analytics"
DB_USER = "postgres"
SCHEMA = "call_center_analytics"

OUTPUT_DIR = Path("outputs/evidencias_preguntas_negocio_125k")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PGPASSWORD = os.environ.get("PGPASSWORD")


def get_password() -> str:
    global PGPASSWORD
    if not PGPASSWORD:
        PGPASSWORD = getpass("Password for user postgres: ")
    return PGPASSWORD


def run_query(query: str) -> pd.DataFrame:
    clean_query = textwrap.dedent(query).strip()

    command = [
        "psql",
        "-U", DB_USER,
        "-d", DB_NAME,
        "--csv",
        "-c", clean_query,
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = get_password()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    if result.returncode != 0:
        print("ERROR ejecutando SQL:")
        print(result.stderr)
        print(result.stdout)
        raise RuntimeError("La consulta SQL falló.")

    csv_text = result.stdout.strip()

    if not csv_text:
        return pd.DataFrame()

    return pd.read_csv(StringIO(csv_text))


def save_csv(df: pd.DataFrame, file_name: str) -> Path:
    path = OUTPUT_DIR / file_name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def shorten_labels(values, width: int = 26):
    return [textwrap.shorten(str(value), width=width, placeholder="...") for value in values]


def finish_chart(title: str, xlabel: str, ylabel: str, output_name: str) -> Path:
    path = OUTPUT_DIR / output_name
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_outputs(df: pd.DataFrame, csv_name: str, png_path: Path) -> None:
    csv_path = save_csv(df, csv_name)
    print(f"OK: {csv_path}")
    print(f"OK: {png_path}")

def pregunta_01() -> None:
    df = run_query(f"""
        SELECT
            ml.nombre_motivo AS motivo_llamada,
            COUNT(*) AS total_llamadas
        FROM {SCHEMA}.llamadas l
        JOIN {SCHEMA}.motivos_llamada ml
            ON ml.id_motivo = l.id_motivo
        GROUP BY ml.nombre_motivo
        ORDER BY total_llamadas DESC
        LIMIT 10;
    """)

    df_plot = df.sort_values("total_llamadas", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(
        shorten_labels(df_plot["motivo_llamada"]),
        df_plot["total_llamadas"],
        label="Total de llamadas"
    )

    ax.set_title("Pregunta 01 - Motivos de llamadas más frecuentes")
    ax.set_xlabel("Total de llamadas")
    ax.set_ylabel("Motivo de llamada")
    ax.legend(title="Indicadores", loc="lower right", frameon=True)

    fig.tight_layout()
    png = OUTPUT_DIR / "01_motivos_llamadas_frecuentes.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(
        df.sort_values("total_llamadas", ascending=False),
        "01_motivos_llamadas_frecuentes.csv",
        png,
    )

def pregunta_02() -> None:
    df = run_query(f"""
        SELECT
            date_trunc('month', fecha_hora_inicio)::date AS mes,
            COUNT(*) AS total_llamadas,
            COUNT(*) FILTER (WHERE tipo_llamada = 'entrante') AS llamadas_entrantes,
            COUNT(*) FILTER (WHERE tipo_llamada = 'saliente') AS llamadas_salientes
        FROM {SCHEMA}.llamadas
        GROUP BY date_trunc('month', fecha_hora_inicio)::date
        ORDER BY mes
        LIMIT 10;
    """)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["mes"].astype(str), df["llamadas_entrantes"], marker="o", label="Llamadas entrantes")
    ax.plot(df["mes"].astype(str), df["llamadas_salientes"], marker="o", label="Llamadas salientes")

    ax.set_title("Pregunta 02 - Llamadas entrantes y salientes por mes")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Total de llamadas")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="Indicadores", loc="center right", frameon=True)

    fig.tight_layout()
    png = OUTPUT_DIR / "02_llamadas_por_mes_tipo.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "02_llamadas_por_mes_tipo.csv", png)

def pregunta_03() -> None:
    df = run_query(f"""
        SELECT
            ml.nombre_motivo AS motivo_llamada,
            COUNT(l.id_llamada) AS total_llamadas,
            ROUND((AVG(l.duracion_segundos) / 60.0)::numeric, 2) AS duracion_promedio_minutos
        FROM {SCHEMA}.llamadas l
        JOIN {SCHEMA}.motivos_llamada ml
            ON ml.id_motivo = l.id_motivo
        GROUP BY ml.nombre_motivo
        ORDER BY total_llamadas DESC
        LIMIT 10;
    """)

    df = df.sort_values("total_llamadas", ascending=False)

    fig, ax1 = plt.subplots(figsize=(13, 7))

    bars = ax1.bar(
        df["motivo_llamada"],
        df["total_llamadas"],
        label="Total de llamadas"
    )
    ax1.set_xlabel("Motivo de llamada")
    ax1.set_ylabel("Total de llamadas")
    ax1.tick_params(axis="x", rotation=35)
    ax1.bar_label(bars, padding=3, fontsize=8)

    ax2 = ax1.twinx()
    ax2.plot(
        df["motivo_llamada"],
        df["duracion_promedio_minutos"],
        marker="o",
        linewidth=2,
        color="darkorange",
        label="Duración promedio (min)"
    )
    ax2.set_ylabel("Duración promedio en minutos")

    for x, y in zip(df["motivo_llamada"], df["duracion_promedio_minutos"]):
        ax2.annotate(
            f"{y:.2f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8
        )

    ax1.set_title("Pregunta 03 - Volumen y duración promedio por motivo")

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        title="Indicadores",
        loc="upper right",
        frameon=True
    )

    fig.tight_layout()
    png = OUTPUT_DIR / "03_motivos_tiempo_promedio.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "03_motivos_tiempo_promedio.csv", png)

def pregunta_04() -> None:
    df = run_query(f"""
        SELECT
            EXTRACT(ISODOW FROM fecha_hora_inicio)::int AS orden_dia,
            CASE EXTRACT(ISODOW FROM fecha_hora_inicio)
                WHEN 1 THEN 'lunes'
                WHEN 2 THEN 'martes'
                WHEN 3 THEN 'miercoles'
                WHEN 4 THEN 'jueves'
                WHEN 5 THEN 'viernes'
                WHEN 6 THEN 'sabado'
                WHEN 7 THEN 'domingo'
            END AS dia_semana,
            CASE
                WHEN fecha_hora_inicio::time >= TIME '00:00:00' AND fecha_hora_inicio::time < TIME '06:00:00' THEN 'madrugada'
                WHEN fecha_hora_inicio::time >= TIME '06:00:00' AND fecha_hora_inicio::time < TIME '12:00:00' THEN 'manana'
                WHEN fecha_hora_inicio::time >= TIME '12:00:00' AND fecha_hora_inicio::time < TIME '18:00:00' THEN 'tarde'
                ELSE 'noche'
            END AS franja_horaria,
            COUNT(*) AS total_llamadas
        FROM {SCHEMA}.llamadas
        GROUP BY
            EXTRACT(ISODOW FROM fecha_hora_inicio)::int,
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
        ORDER BY orden_dia, franja_horaria;
    """)

    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    franjas = ["madrugada", "manana", "tarde", "noche"]

    pivot = (
        df.pivot_table(
            index="dia_semana",
            columns="franja_horaria",
            values="total_llamadas",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(index=dias, columns=franjas, fill_value=0)
    )

    pivot = pivot.loc[pivot.sum(axis=1) > 0, pivot.sum(axis=0) > 0]

    etiquetas_dias = {
        "lunes": "lunes",
        "martes": "martes",
        "miercoles": "miércoles",
        "jueves": "jueves",
        "viernes": "viernes",
        "sabado": "sábado",
        "domingo": "domingo",
    }

    etiquetas_franjas = {
        "madrugada": "madrugada",
        "manana": "mañana",
        "tarde": "tarde",
        "noche": "noche",
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([etiquetas_franjas[c] for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([etiquetas_dias[i] for i in pivot.index])

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            valor = int(pivot.iloc[i, j])
            if valor > 0:
                ax.text(
                    j,
                    i,
                    f"{valor:,}".replace(",", "."),
                    ha="center",
                    va="center",
                    fontsize=8
                )

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Leyenda: total de llamadas")

    ax.set_title("Pregunta 04 - Concentración de llamadas por día y franja horaria")
    ax.set_xlabel("Franja horaria")
    ax.set_ylabel("Día de la semana")

    fig.tight_layout()
    png = OUTPUT_DIR / "04_franjas_horarias_dias.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "04_franjas_horarias_dias.csv", png)

def pregunta_05() -> None:
    df = run_query(f"""
        WITH llamadas_caso AS (
            SELECT
                date_trunc('month', fecha_hora_inicio)::date AS mes,
                id_cliente,
                id_caso,
                COUNT(*) AS total_llamadas_caso
            FROM {SCHEMA}.llamadas
            WHERE id_caso IS NOT NULL
            GROUP BY date_trunc('month', fecha_hora_inicio)::date, id_cliente, id_caso
            HAVING COUNT(*) > 1
        )
        SELECT
            lc.mes,
            COUNT(DISTINCT lc.id_cliente) AS clientes_con_recontacto,
            COUNT(DISTINCT lc.id_caso) AS casos_con_recontacto,
            SUM(lc.total_llamadas_caso) AS llamadas_asociadas
        FROM llamadas_caso lc
        JOIN {SCHEMA}.casos c
            ON c.id_caso = lc.id_caso
        WHERE c.resuelto_primer_contacto = false
        GROUP BY lc.mes
        ORDER BY lc.mes
        LIMIT 10;
    """)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["mes"].astype(str), df["clientes_con_recontacto"], marker="o", label="Clientes con recontacto")
    ax.plot(df["mes"].astype(str), df["casos_con_recontacto"], marker="o", label="Casos con recontacto")

    ax.set_title("Pregunta 05 - Recontactos por casos no resueltos en primer contacto")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Total")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="Indicadores", loc="best", frameon=True)

    fig.tight_layout()
    png = OUTPUT_DIR / "05_recontacto_por_caso.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "05_recontacto_por_caso.csv", png)

def pregunta_06() -> None:
    df = run_query(f"""
        SELECT
            a.id_agente,
            CONCAT(a.nombre, ' ', a.apellido) AS agente,
            d.nombre_departamento,
            COUNT(l.id_llamada) AS total_llamadas_atendidas,
            ROUND(AVG(e.calificacion)::numeric, 2) AS satisfaccion_promedio
        FROM {SCHEMA}.agentes a
        JOIN {SCHEMA}.llamadas l
            ON l.id_agente = a.id_agente
        JOIN {SCHEMA}.departamentos d
            ON d.id_departamento = a.id_departamento
        LEFT JOIN {SCHEMA}.encuestas_satisfaccion e
            ON e.id_llamada = l.id_llamada
        WHERE e.calificacion IS NOT NULL
        GROUP BY a.id_agente, agente, d.nombre_departamento
        HAVING COUNT(e.id_encuesta) >= 20
        ORDER BY satisfaccion_promedio DESC, total_llamadas_atendidas DESC
        LIMIT 10;
    """)

    df = df.sort_values("satisfaccion_promedio", ascending=True)

    etiquetas = []
    for agente in df["agente"]:
        etiquetas.append(agente if len(agente) <= 22 else agente[:22] + "...")

    fig, ax = plt.subplots(figsize=(13, 7))
    bars = ax.barh(
        etiquetas,
        df["satisfaccion_promedio"],
        label="Satisfacción promedio"
    )

    ax.set_title("Pregunta 06 - Desempeño de agentes según satisfacción")
    ax.set_xlabel("Satisfacción promedio")
    ax.set_ylabel("Agente")
    ax.set_xlim(0, 5)

    for bar, total, depto in zip(bars, df["total_llamadas_atendidas"], df["nombre_departamento"]):
        ax.text(
            bar.get_width() + 0.03,
            bar.get_y() + bar.get_height() / 2,
            f"{int(total)} llamadas | {depto}",
            va="center",
            fontsize=8
        )

    ax.legend(title="Indicadores", loc="lower right", frameon=True)

    fig.tight_layout()
    png = OUTPUT_DIR / "06_desempeno_agentes.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "06_desempeno_agentes.csv", png)

def pregunta_07() -> None:
    df = run_query(f"""
        WITH pagos_por_factura AS (
            SELECT
                id_factura,
                SUM(valor_pagado) AS total_pagado
            FROM {SCHEMA}.pagos
            WHERE estado_pago = 'aplicado'
            GROUP BY id_factura
        )
        SELECT
            c.id_cliente,
            CONCAT(c.nombre, ' ', c.apellido) AS cliente,
            COUNT(f.id_factura) AS facturas_comprometidas,
            ROUND(SUM(f.valor_total)::numeric, 2) AS valor_facturado,
            ROUND(SUM(COALESCE(p.total_pagado, 0))::numeric, 2) AS valor_pagado,
            ROUND(SUM(f.valor_total - COALESCE(p.total_pagado, 0))::numeric, 2) AS saldo_pendiente
        FROM {SCHEMA}.facturas f
        JOIN {SCHEMA}.clientes c
            ON c.id_cliente = f.id_cliente
        LEFT JOIN pagos_por_factura p
            ON p.id_factura = f.id_factura
        WHERE f.estado_factura IN ('vencida', 'en_mora')
           OR f.valor_total > COALESCE(p.total_pagado, 0)
        GROUP BY c.id_cliente, cliente
        HAVING SUM(f.valor_total - COALESCE(p.total_pagado, 0)) > 0
        ORDER BY saldo_pendiente DESC
        LIMIT 10;
    """)

    df = df.sort_values("saldo_pendiente", ascending=True)

    etiquetas = []
    for cliente in df["cliente"]:
        etiquetas.append(cliente if len(cliente) <= 24 else cliente[:24] + "...")

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        etiquetas,
        df["saldo_pendiente"],
        label="Saldo pendiente"
    )

    ax.set_title("Pregunta 07 - Clientes con mayor saldo pendiente")
    ax.set_xlabel("Saldo pendiente")
    ax.set_ylabel("Cliente")

    for bar, facturas in zip(bars, df["facturas_comprometidas"]):
        ax.text(
            bar.get_width() * 1.005,
            bar.get_y() + bar.get_height() / 2,
            f"{int(facturas)} facturas",
            va="center",
            fontsize=8
        )

    ax.legend(title="Indicadores", loc="lower right", frameon=True)

    fig.tight_layout()
    png = OUTPUT_DIR / "07_facturas_vencidas_pagos_pendientes.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "07_facturas_vencidas_pagos_pendientes.csv", png)

def pregunta_08() -> None:
    df = run_query(f"""
        SELECT
            d.nombre_departamento,
            COUNT(l.id_llamada) AS total_llamadas,
            ROUND((AVG(l.duracion_segundos) / 60.0)::numeric, 2) AS duracion_promedio_minutos,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE rl.nombre_resultado = 'resuelta') / NULLIF(COUNT(l.id_llamada), 0),
                2
            ) AS tasa_resolucion_porcentaje
        FROM {SCHEMA}.departamentos d
        JOIN {SCHEMA}.llamadas l
            ON l.id_departamento = d.id_departamento
        LEFT JOIN {SCHEMA}.resultados_llamada rl
            ON rl.id_resultado = l.id_resultado
        GROUP BY d.nombre_departamento
        ORDER BY duracion_promedio_minutos DESC, tasa_resolucion_porcentaje ASC
        LIMIT 10;
    """)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    bars = ax1.bar(
        df["nombre_departamento"],
        df["duracion_promedio_minutos"],
        label="Duración promedio (min)"
    )
    ax1.set_xlabel("Departamento")
    ax1.set_ylabel("Duración promedio en minutos")
    ax1.tick_params(axis="x", rotation=40)
    ax1.bar_label(bars, fmt="%.2f", padding=3, fontsize=8)

    ax2 = ax1.twinx()
    ax2.plot(
        df["nombre_departamento"],
        df["tasa_resolucion_porcentaje"],
        marker="o",
        linewidth=2.5,
        color="darkorange",
        label="Tasa de resolución (%)"
    )
    ax2.set_ylabel("Tasa de resolución (%)")

    minimo = float(df["tasa_resolucion_porcentaje"].min())
    maximo = float(df["tasa_resolucion_porcentaje"].max())
    ax2.set_ylim(max(0, minimo - 2), maximo + 2)

    for x, y in zip(df["nombre_departamento"], df["tasa_resolucion_porcentaje"]):
        ax2.annotate(
            f"{y:.2f}%",
            (x, y),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8
        )

    ax1.set_title("Pregunta 08 - Duración promedio y tasa de resolución por departamento")

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        title="Indicadores",
        loc="upper right",
        frameon=True
    )

    fig.tight_layout()
    png = OUTPUT_DIR / "08_desempeno_departamentos.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "08_desempeno_departamentos.csv", png)

def pregunta_09() -> None:
    df = run_query(f"""
        SELECT
            ts.nombre_servicio,
            COUNT(e.id_encuesta) AS total_encuestas,
            ROUND(AVG(e.calificacion)::numeric, 2) AS satisfaccion_promedio,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE e.calificacion >= 4) / NULLIF(COUNT(e.id_encuesta), 0),
                2
            ) AS porcentaje_satisfechos
        FROM {SCHEMA}.encuestas_satisfaccion e
        JOIN {SCHEMA}.llamadas l
            ON l.id_llamada = e.id_llamada
        JOIN {SCHEMA}.tipos_servicio ts
            ON ts.id_tipo_servicio = l.id_tipo_servicio
        GROUP BY ts.nombre_servicio
        ORDER BY satisfaccion_promedio DESC, total_encuestas DESC
        LIMIT 10;
    """)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(
        df["nombre_servicio"].astype(str),
        df["satisfaccion_promedio"],
        label="Satisfacción promedio"
    )

    ax.set_title("Pregunta 09 - Satisfacción promedio por tipo de servicio")
    ax.set_xlabel("Tipo de servicio")
    ax.set_ylabel("Satisfacción promedio")
    ax.set_ylim(0, 5)
    ax.tick_params(axis="x", rotation=45)
    ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=8)
    ax.legend(title="Indicadores", loc="upper right", frameon=True)

    fig.tight_layout()
    png = OUTPUT_DIR / "09_satisfaccion_cliente.png"
    plt.savefig(png, dpi=150, bbox_inches="tight")
    plt.close()

    save_outputs(df, "09_satisfaccion_cliente.csv", png)

def main() -> None:
    preguntas = [
        pregunta_01,
        pregunta_02,
        pregunta_03,
        pregunta_04,
        pregunta_05,
        pregunta_06,
        pregunta_07,
        pregunta_08,
        pregunta_09,
    ]

    for pregunta in preguntas:
        pregunta()

    print("OK: evidencias generadas para las 9 preguntas de negocio.")


if __name__ == "__main__":
    main()




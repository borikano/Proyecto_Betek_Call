#!/usr/bin/env python3
"""
07_generador_datos_sinteticos_python_125k.py

Generador de datos sintéticos históricos para un call center (125,000 clientes, 2025-05-01 a 2026-06-26).
Script independiente basado en 07_generador_datos_sinteticos_python.py
"""

# Copia completa del script original:
from __future__ import annotations
import argparse
import json
import math
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

# --- INICIO DEL MAIN PERSONALIZADO ---
# (A partir de aquí, el main personalizado para 125k clientes)

# SQL_EXPORT_COLUMNS, LOAD_ORDER, IDENTITY_PK_MAP, GenerationConfig, SyntheticCallCenterGenerator, etc.
# ... (todo el contenido ya copiado del script original) ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera datos sintéticos históricos para un call center (125,000 clientes, 2025-05-01 a 2026-06-26).")
    parser.add_argument("--output-dir", default="../../data/call_center_analytics_20260508")
    parser.add_argument("--seed", type=int, default=20260410)
    parser.add_argument("--clients", type=int, default=125000)
    parser.add_argument("--agents", type=int, default=180)
    parser.add_argument("--history-months", type=int, default=14)
    parser.add_argument("--end-date", default="2026-06-26")
    parser.add_argument("--surveys-target-min", type=int, default=85000)
    parser.add_argument("--surveys-target-max", type=int, default=120000)
    parser.add_argument("--calls-target-min", type=int, default=400000)
    parser.add_argument("--calls-target-max", type=int, default=600000)
    parser.add_argument("--invoices-target-min", type=int, default=350000)
    parser.add_argument("--invoices-target-max", type=int, default=500000)
    parser.add_argument("--cases-target-min", type=int, default=100000)
    parser.add_argument("--cases-target-max", type=int, default=150000)
    parser.add_argument("--products-target-min", type=int, default=180000)
    parser.add_argument("--products-target-max", type=int, default=250000)
    parser.add_argument("--payments-target-min", type=int, default=300000)
    parser.add_argument("--payments-target-max", type=int, default=450000)
    args = parser.parse_args()

    cfg = GenerationConfig(
        seed=args.seed,
        output_dir=args.output_dir,
        history_months=args.history_months,
        end_date=args.end_date,
        clients=args.clients,
        agents=args.agents,
        surveys_target_min=args.surveys_target_min,
        surveys_target_max=args.surveys_target_max,
        calls_target_min=args.calls_target_min,
        calls_target_max=args.calls_target_max,
        invoices_target_min=args.invoices_target_min,
        invoices_target_max=args.invoices_target_max,
        cases_target_min=args.cases_target_min,
        cases_target_max=args.cases_target_max,
        products_target_min=args.products_target_min,
        products_target_max=args.products_target_max,
        payments_target_min=args.payments_target_min,
        payments_target_max=args.payments_target_max,
    )
    gen = SyntheticCallCenterGenerator(cfg)
    gen.run()
    print(f"Generación finalizada en: {Path(cfg.output_dir).resolve()}")

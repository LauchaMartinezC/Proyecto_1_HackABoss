"""Funciones de extracción y transformación para el dashboard."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd
import requests


API_URL = "https://api.covidtracking.com/v1/us/daily.json"
REQUIRED_COLUMNS = {"date", "positiveIncrease", "deathIncrease"}
NUMERIC_COLUMNS = {
    "positive",
    "negative",
    "death",
    "hospitalizedCurrently",
    "hospitalizedCumulative",
    "hospitalizedIncrease",
    "positiveIncrease",
    "deathIncrease",
    "totalTestResultsIncrease",
}


def importar_datos(url: str = API_URL, timeout: int = 30) -> list[dict[str, Any]]:
    """Descarga registros JSON desde la API pública y valida su forma básica."""

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list):
        raise ValueError("La API no devolvió una lista de registros.")
    if not all(isinstance(record, dict) for record in payload):
        raise ValueError("La API devolvió registros con un formato inesperado.")

    return payload


def transformar(datos: Sequence[dict[str, Any]]) -> pd.DataFrame:
    """Normaliza fechas y métricas diarias y devuelve datos ordenados."""

    if not datos:
        return pd.DataFrame(columns=["date", "daily_cases", "daily_deaths"])

    df = pd.DataFrame(datos)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        fields = ", ".join(sorted(missing))
        raise ValueError(f"Faltan campos requeridos en la respuesta: {fields}.")

    parsed_dates = pd.to_datetime(
        df["date"].astype(str), format="%Y%m%d", errors="coerce"
    )
    if parsed_dates.isna().any():
        raise ValueError("La respuesta contiene fechas con un formato inválido.")

    df["date"] = parsed_dates
    for column in NUMERIC_COLUMNS.intersection(df.columns):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["daily_cases"] = df["positiveIncrease"]
    df["daily_deaths"] = df["deathIncrease"]

    return df.sort_values("date").reset_index(drop=True)

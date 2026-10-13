"""Dashboard interactivo sobre el archivo histórico de COVID-19 en EE. UU."""

from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
import streamlit as st

from etl_utils import API_URL, importar_datos, transformar


DATA_START = date(2020, 1, 13)
DATA_END = date(2021, 3, 7)

st.set_page_config(
    page_title="COVID-19 ETL & Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def cargar_dataset() -> pd.DataFrame:
    """Descarga y transforma el archivo histórico una vez por sesión."""

    return transformar(importar_datos(API_URL))


comments = {
    "Gráficos acumulados": (
        "Evolución acumulada de muertes y hospitalizaciones reportadas."
    ),
    "Promedios 7 días": (
        "Promedio por bloques de siete días para suavizar variaciones diarias."
    ),
    "Promedios 30 días": (
        "Promedio por bloques de treinta días para observar tendencias más estables."
    ),
    "Serie diaria: casos vs muertes": (
        "Comparación descriptiva de los incrementos diarios reportados."
    ),
    "Mapa de calor de correlación": (
        "Correlación lineal entre casos y muertes diarias; no implica causalidad."
    ),
    "Estadísticas descriptivas": (
        "Resumen de distribución, tendencia central y dispersión."
    ),
    "Distribución antes/después del inicio de vacunación": (
        "Comparación descriptiva alrededor del 14/12/2020; no es un análisis causal."
    ),
    "Aceleración de casos diarios": (
        "Segunda diferencia de la serie para explorar cambios en su pendiente."
    ),
    "Ratios de hospitalización": (
        "Ratios construidos con campos reportados; no representan una probabilidad clínica."
    ),
    "Positividad diaria reportada": (
        "Proporción entre nuevos positivos y resultados de tests reportados cada día."
    ),
}


def mostrar_figura(fig: plt.Figure) -> None:
    """Muestra y cierra una figura para evitar acumular memoria."""

    st.pyplot(fig)
    plt.close(fig)


st.title("COVID-19 ETL & Analytics Dashboard")
st.write(
    "Proyecto académico de extracción, transformación y visualización de datos "
    "históricos de Estados Unidos."
)
st.caption(
    "Fuente: The COVID Tracking Project at The Atlantic. "
    "El conjunto es histórico y finaliza el 7 de marzo de 2021."
)

st.sidebar.header("🔧 Parámetros ETL y visualización")
fecha_inicio = st.sidebar.date_input(
    "Fecha de inicio",
    value=DATA_START,
    min_value=DATA_START,
    max_value=DATA_END,
)
fecha_fin = st.sidebar.date_input(
    "Fecha de fin",
    value=DATA_END,
    min_value=DATA_START,
    max_value=DATA_END,
)

dashboard_ops = list(comments)
seleccion = st.sidebar.multiselect(
    "Análisis",
    dashboard_ops,
    default=["Gráficos acumulados", "Promedios 7 días"],
)

if st.sidebar.button("🔄 Cargar datos", type="primary"):
    if fecha_inicio > fecha_fin:
        st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
    else:
        try:
            with st.spinner("Descargando y transformando datos…"):
                dataset = cargar_dataset()
        except requests.RequestException as exc:
            st.sidebar.error(f"No se pudo consultar la API: {exc}")
        except ValueError as exc:
            st.sidebar.error(f"Los datos recibidos no son válidos: {exc}")
        else:
            mask = dataset["date"].between(
                pd.Timestamp(fecha_inicio), pd.Timestamp(fecha_fin)
            )
            filtered = dataset.loc[mask].reset_index(drop=True)
            if filtered.empty:
                st.sidebar.warning("No hay registros para el rango seleccionado.")
                st.session_state.pop("df", None)
            else:
                st.session_state["df"] = filtered
                st.sidebar.success(f"{len(filtered)} registros cargados")


if "df" not in st.session_state:
    st.info("Presioná “Cargar datos” en la barra lateral para iniciar el ETL.")
    st.stop()


df = st.session_state["df"].copy()
st.subheader("Resultados")
st.write(
    f"Rango cargado: **{df['date'].min():%d/%m/%Y} — "
    f"{df['date'].max():%d/%m/%Y}** · **{len(df)} registros**"
)

for op in seleccion:
    st.markdown(f"### {op}")

    if op == "Gráficos acumulados":
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(df["date"], df["death"], label="Muertes acumuladas")
        ax.plot(
            df["date"],
            df["hospitalizedCumulative"],
            label="Hospitalizaciones acumuladas",
        )
        ax.legend()
        ax.set(xlabel="Fecha", ylabel="Total")
        mostrar_figura(fig)

    elif op == "Promedios 7 días":
        period = (
            df.resample("7D", on="date")[["daily_cases", "daily_deaths"]]
            .mean()
            .dropna(how="all")
        )
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(period.index, period["daily_cases"], label="Casos: media 7d")
        ax.plot(period.index, period["daily_deaths"], label="Muertes: media 7d")
        ax.legend()
        ax.set(xlabel="Periodo", ylabel="Promedio diario")
        mostrar_figura(fig)

    elif op == "Promedios 30 días":
        period = (
            df.resample("30D", on="date")[["daily_cases", "daily_deaths"]]
            .mean()
            .dropna(how="all")
        )
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(period.index, period["daily_cases"], label="Casos: media 30d")
        ax.plot(period.index, period["daily_deaths"], label="Muertes: media 30d")
        ax.legend()
        ax.set(xlabel="Periodo", ylabel="Promedio diario")
        mostrar_figura(fig)

    elif op == "Serie diaria: casos vs muertes":
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(df["date"], df["daily_cases"], label="Casos diarios")
        ax.plot(df["date"], df["daily_deaths"], label="Muertes diarias")
        ax.legend()
        ax.set(xlabel="Fecha", ylabel="Cantidad reportada")
        mostrar_figura(fig)

    elif op == "Mapa de calor de correlación":
        correlation = df[["daily_cases", "daily_deaths"]].corr()
        fig, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(correlation, annot=True, vmin=-1, vmax=1, ax=ax)
        mostrar_figura(fig)

    elif op == "Estadísticas descriptivas":
        st.dataframe(df.describe(include="number").T, width="stretch")

    elif op == "Distribución antes/después del inicio de vacunación":
        comparison = df.assign(
            period=np.where(df["date"] < pd.Timestamp("2020-12-14"), "Antes", "Después")
        )
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.histplot(
            data=comparison,
            x="daily_cases",
            hue="period",
            multiple="dodge",
            bins=30,
            ax=ax,
        )
        mostrar_figura(fig)

    elif op == "Aceleración de casos diarios":
        acceleration = df["daily_cases"].diff().diff()
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(df["date"], acceleration)
        ax.axhline(0, linestyle="--", color="gray")
        ax.set(xlabel="Fecha", ylabel="Segunda diferencia")
        mostrar_figura(fig)

    elif op == "Ratios de hospitalización":
        daily_denominator = df["daily_cases"].where(df["daily_cases"] > 0)
        daily_ratio = (df["hospitalizedIncrease"] / daily_denominator).replace(
            [np.inf, -np.inf], np.nan
        )
        cumulative_ratio = (
            df["hospitalizedCumulative"] / df["positive"].where(df["positive"] > 0)
        ).replace([np.inf, -np.inf], np.nan)

        values = [daily_ratio.mean(), cumulative_ratio.dropna().iloc[-1]]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(["Media de ratios diarios", "Ratio acumulado final"], values)
        ax.set_ylabel("Hospitalizaciones / positivos")
        mostrar_figura(fig)

    elif op == "Positividad diaria reportada":
        denominator = df["totalTestResultsIncrease"].where(
            df["totalTestResultsIncrease"] > 0
        )
        positivity = (df["positiveIncrease"] / denominator).replace(
            [np.inf, -np.inf], np.nan
        )
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(df["date"], positivity)
        ax.set(xlabel="Fecha", ylabel="Positivos / tests reportados")
        mostrar_figura(fig)

    st.markdown(f"**Lectura:** {comments[op]}")

st.markdown("---")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "💾 Descargar CSV filtrado",
    data=csv,
    file_name="covid_us_historical_data.csv",
    mime="text/csv",
)

st.caption(
    "Proyecto educativo. No constituye información sanitaria actual ni asesoramiento médico."
)

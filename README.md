# COVID-19 ETL & Analytics Dashboard

Dashboard académico en Streamlit que descarga, valida, transforma y visualiza el archivo histórico nacional de COVID-19 de Estados Unidos.

> **English summary:** a small, reproducible ETL and analytics project built with Python, pandas and Streamlit. It consumes a public historical API, validates its schema, supports date filtering and exports the transformed data as CSV.

## Qué demuestra

- Extracción desde una API REST pública con control de errores y timeout.
- Validación básica del payload y normalización de fechas y métricas numéricas.
- Filtrado temporal y análisis exploratorio reproducible.
- Visualizaciones de series, medias por periodo, correlación, distribución y ratios descriptivos.
- Exportación del conjunto filtrado a CSV.
- Pruebas unitarias del núcleo ETL sin depender de la red.

## Flujo

```text
COVID Tracking Project API
          ↓
 requests + validación
          ↓
 transformación con pandas
          ↓
 filtros y análisis en Streamlit
          ↓
 gráficos + CSV descargable
```

## Stack

- Python
- Streamlit
- pandas y NumPy
- Matplotlib y seaborn
- requests
- unittest

## Ejecución local

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

Instalación y arranque:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

La aplicación no necesita claves, cuentas ni variables de entorno.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Datos, límites y uso responsable

- Fuente: [The COVID Tracking Project at The Atlantic](https://covidtracking.com/data/api/).
- El proyecto dejó de recopilar datos el **7 de marzo de 2021**. Este dashboard es histórico; no muestra la situación sanitaria actual.
- Los datos y contenidos de la fuente se publican bajo [CC BY 4.0](https://covidtracking.com/about-data/license/). La atribución pertenece a The COVID Tracking Project at The Atlantic.
- Las comparaciones y ratios son exploratorios y descriptivos. No permiten inferir causalidad ni constituyen asesoramiento médico.
- Algunos campos pueden estar incompletos o reflejar revisiones de los organismos que reportaron la información.

## Privacidad y seguridad

- Solo se consumen datos públicos y agregados.
- No se procesan datos personales, de clientes ni credenciales.
- No se almacenan secretos en el repositorio.
- La exportación CSV ocurre en la sesión del usuario.

## Autoría y atribución

Proyecto desarrollado por **Lautaro Martínez** durante su formación en Data Science & Artificial Intelligence en HACK A BOSS.

El repositorio se inició desde [`streamlit/blank-app-template`](https://github.com/streamlit/blank-app-template). La implementación del flujo ETL, los análisis y la presentación de este repositorio corresponden al trabajo del proyecto; Streamlit conserva la atribución de su plantilla original.

El código de este repositorio se distribuye bajo la licencia [Apache 2.0](LICENSE). La licencia de los datos es independiente y se detalla arriba.

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import tempfile, shutil

# 📂 Carpeta relativa dentro del proyecto
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

# 📌 Ruta al archivo Excel donde se guardarán las convocatorias
RUTA_EXCEL = os.path.join(DATA_FOLDER, "convocatorias_minciencias.xlsx")

def actualizar_convocatorias(ruta_salida=RUTA_EXCEL, max_paginas=2):
    """
    Scrapea las páginas de convocatorias de Minciencias (limitadas por max_paginas),
    guarda en Excel y devuelve estado, mensaje, total y las convocatorias nuevas.
    """

    base_url = "https://minciencias.gov.co/convocatorias/todas?page="
    dfs = []
    nuevas_convocatorias = []

    try:
        for pagina in range(max_paginas):
            url = f"{base_url}{pagina}"
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            tabla = soup.find("table")

            if tabla is None:
                break

            df = pd.read_html(str(tabla))[0]
            dfs.append(df)

    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"No se pudo acceder a {url} -> {e}",
            "total": 0,
            "nuevas": []
        }

    if not dfs:
        return {
            "status": "error",
            "mensaje": "⚠ No se encontraron convocatorias.",
            "total": 0,
            "nuevas": []
        }

    df_nuevo = pd.concat(dfs, ignore_index=True)

    # Detectar columna clave
    col_clave = "Título" if "Título" in df_nuevo.columns else df_nuevo.columns[0]

    # Si ya existe un archivo, comparar
    if os.path.exists(ruta_salida):
        try:
            df_existente = pd.read_excel(ruta_salida)

            nuevos = df_nuevo[~df_nuevo[col_clave].isin(df_existente[col_clave])]
            nuevas_convocatorias = nuevos.to_dict(orient="records")

            df_total = pd.concat([df_existente, df_nuevo]).drop_duplicates(
                subset=[col_clave]
            ).reset_index(drop=True)

        except Exception:
            df_total = df_nuevo.copy()
            nuevas_convocatorias = df_nuevo.to_dict(orient="records")
    else:
        df_total = df_nuevo.copy()
        nuevas_convocatorias = df_nuevo.to_dict(orient="records")

    # Guardar Excel de forma segura
    try:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            df_total.to_excel(tmp.name, index=False)
            tmp_path = tmp.name
        shutil.move(tmp_path, ruta_salida)
    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"No se pudo guardar Excel -> {e}",
            "total": len(df_total),
            "nuevas": nuevas_convocatorias
        }

    return {
        "status": "ok",
        "mensaje": "✅ Convocatorias actualizadas correctamente.",
        "total": len(df_total),
        "nuevas": nuevas_convocatorias
    }


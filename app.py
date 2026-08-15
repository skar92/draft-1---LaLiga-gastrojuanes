Para poner los escudos reales de los equipos, necesitamos usar **enlaces a las imágenes de los escudos** (en este caso, de Wikimedia) e inyectar un poco de código HTML en la tabla para que Streamlit pueda renderizar las imágenes correctamente junto al texto.

Como la función por defecto `st.dataframe()` de Streamlit no lee código HTML interno, usaremos `st.markdown(df.to_html(escape=False), unsafe_allow_html=True)` para la tabla de clasificación.

Sustituye todo el contenido de tu `app.py` por el siguiente código:

```python
import csv
from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la interfaz de Streamlit
st.set_page_config(page_title="Draft LaLiga 2026/27", layout="wide")
st.title("🏆 Seguimiento y Clasificación del Draft de LaLiga")

FILE_GANADORES = "ganadores_liga.csv"

def guardar_ganador(nombre):
    if not nombre.strip():
        return
    file_exists = os.path.exists(FILE_GANADORES)
    with open(FILE_GANADORES, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Nombre", "Fecha y Hora"])
        writer.writerow([nombre.strip(), datetime.now().strftime("%d/%m/%Y %H:%M")])

# --- CONFIGURACIÓN DE LOS PARTICIPANTES Y SUS EQUIPOS ---
porra_equipos = {
    "Ejkar": ["Athletic Club", "Elche"],
    "Sierra": ["Real Betis"],
    "Vecina": ["Real Sociedad", "Racing"],
    "Mírete": ["Celta", "Levante"],
    "Miguel Ángel": ["Valencia", "Alavés"],
    "Juan": ["Getafe", "Rayo Vallecano"],
    "Joaquín": ["Sevilla", "Osasuna"],
    "Telenti": ["Espanyol", "Deportivo"],
}

# --- PUNTOS SUMADOS POR CADA EQUIPO (Actualización Manual) ---
puntos_equipos_valores = {
    "Athletic Club": 0, "Elche": 0, "Real Betis": 0, "Real Sociedad": 0,
    "Racing": 0, "Celta": 0, "Levante": 0, "Valencia": 0, "Alavés": 0,
    "Getafe": 0, "Rayo Vallecano": 0, "Sevilla": 0, "Osasuna": 0,
    "Espanyol": 0, "Deportivo": 0,
}

# --- GOLES DE LOS GOLEADORES ELEGIDOS (Actualización Manual) ---
porra_goleadores = {
    "Ejkar": {"Borja Iglesias": 0},
    "Sierra": {},
    "Vecina": {"Aubameyang": 0},
    "Mírete": {"Budimir": 0},
    "Miguel Ángel": {"Mikautadze": 0},
    "Juan": {"Mikel Oyarzabal": 0},
    "Joaquín": {"Julián Álvarez": 0},
    "Telenti": {"Enes Ünal": 0},
}

# --- PUNTOS EXTRA O APUESTAS DE MESA ---
puntos_apuesta = {
    "Sierra": 0, "Joaquín": 0, "Ejkar": 0, "Vecina": 0,
    "Telenti": 0, "Miguel Ángel": 0, "Mírete": 0, "Juan": 0,
}

# --- URLS DE LOS ESCUDOS REALES (Formato PNG desde Wikimedia) ---
escudos_urls = {
    "Athletic Club": "https://upload.wikimedia.org/wikipedia/en/thumb/9/98/Club_Athletic_Bilbao_logo.svg/50px-Club_Athletic_Bilbao_logo.svg.png",
    "Elche": "https://upload.wikimedia.org/wikipedia/en/thumb/3/36/Elche_cf_logo.svg/50px-Elche_cf_logo.svg.png",
    "Real Betis": "https://upload.wikimedia.org/wikipedia/en/thumb/1/13/Real_betis_logo.svg/50px-Real_betis_logo.svg.png",
    "Real Sociedad": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Real_Sociedad_logo.svg/50px-Real_Sociedad_logo.svg.png",
    "Racing": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1c/Racing_de_Santander_logo.svg/50px-Racing_de_Santander_logo.svg.png",
    "Celta": "https://upload.wikimedia.org/wikipedia/en/thumb/1/12/RC_Celta_de_Vigo_logo.svg/50px-RC_Celta_de_Vigo_logo.svg.png",
    "Levante": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_UD_logo.svg/50px-Levante_UD_logo.svg.png",
    "Valencia": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/50px-Valenciacf.svg.png",
    "Alavés": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2e/Deportivo_Alaves_logo.svg/50px-Deportivo_Alaves_logo.svg.png",
    "Getafe": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7f/Getafe_logo.svg/50px-Getafe_logo.svg.png",
    "Rayo Vallecano": "https://upload.wikimedia.org/wikipedia/en/thumb/1/17/Rayo_Vallecano_logo.svg/50px-Rayo_Vallecano_logo.svg.png",
    "Sevilla": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/Sevilla_FC_logo.svg/50px-Sevilla_FC_logo.svg.png",
    "Osasuna": "https://upload.wikimedia.org/wikipedia/en/thumb/d/db/Osasuna_logo.svg/50px-Osasuna_logo.svg.png",
    "Espanyol": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d6/Rcd_espanyol_logo.svg/50px-Rcd_espanyol_logo.svg.png",
    "Deportivo": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/RC_Deportivo_La_Coru%C3%B1a_logo.svg/50px-RC_Deportivo_La_Coru%C3%B1a_logo.svg.png",
}

# --- CÓMPUTO DIRECTO DE PUNTOS ---
filas_clasificacion = []

for jugador, equipos in porra_equipos.items():
    # Puntos sumados por los equipos elegidos
    pts_equipos = sum([puntos_equipos_valores.get(eq, 0) for eq in equipos])

    # Goles sumados por los futbolistas
    goleadores_dict = porra_goleadores.get(jugador, {})
    pts_goleadores = sum(goleadores_dict.values())

    # Puntos extra
    pts_extra = puntos_apuesta.get(jugador, 0)
    puntos_totales = pts_equipos + pts_goleadores + pts_extra

    # Generar texto HTML con la imagen al lado del nombre
    equipos_con_escudo = []
    for eq in equipos:
        url = escudos_urls.get(eq, "")
        if url:
            html_img = f'<img src="{url}" width="22" style="vertical-align: middle; margin-right: 5px; border-radius: 2px;"> {eq}'
        else:
            html_img = f"⚽ {eq}"
        equipos_con_escudo.append(html_img)

    filas_clasificacion.append({
        "Jugador": f"<b>{jugador}</b>",
        "Equipos": "<br>".join(equipos_con_escudo), # Usamos <br> para separar equipos en líneas
        "Goleador": "<br>".join([f"{gol} <b>({pts})</b>" for gol, pts in goleadores_dict.items()]),
        "Pts Equipos": pts_equipos,
        "Goles": pts_goleadores,
        "Pts Apuesta": pts_extra,
        "Puntos Totales": f"<span style='font-size: 1.2em; font-weight: bold;'>{puntos_totales}</span>",
    })

df_liga = pd.DataFrame(filas_clasificacion)

# --- HISTORIAL CRONOLÓGICO MANUAL (Para la gráfica de evolución) ---
datos_historicos = [
    {"Jornada": "J0", "Jugador": "Ejkar", "Puntos Totales": 0},
    {"Jornada": "J0", "Jugador": "Sierra", "Puntos Totales": 0},
    {"Jornada": "J0", "Jugador": "Vecina", "Puntos Totales": 0},
    {"Jornada": "J0", "Jugador": "Mírete", "Puntos Totales": 0},
    {"Jornada": "J0", "Jugador": "Miguel Ángel", "Puntos Totales": 0},
    {"Jornada": "J0", "Jugador": "Juan", "Puntos Totales": 0},
    {"Jornada": "J0", "Jugador": "Joaquín", "Puntos Totales": 0},
    {"Jornada": "J0", "Jugador": "Telenti", "Puntos Totales": 0},
]
df_historial = pd.DataFrame(datos_historicos)

# --- ESTILOS CSS PERSONALIZADOS PARA LA TABLA HTML ---
st.markdown("""
<style>
    .dataframe-container {
        overflow-x: auto;
    }
    .styled-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.95em;
        font-family: sans-serif;
        text-align: left;
    }
    .styled-table thead tr {
        background-color: #2b2b2b;
        color: #ffffff;
        text-align: left;
    }
    .styled-table th, .styled-table td {
        padding: 12px 15px;
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- RENDERIZADO INTERFAZ STREAMLIT ---
col1, col2 = st.columns([1.3, 0.7])

with col1:
    st.subheader("📊 Clasificación General")
    df_mostrar = df_liga.sort_values(by="Puntos Totales", ascending=False)[
        ["Jugador", "Equipos", "Goleador", "Pts Equipos", "Goles", "Pts Apuesta", "Puntos Totales"]
    ]
    # Renderizamos como HTML para mostrar las imágenes reales
    tabla_html = df_mostrar.to_html(escape=False, index=False, classes="styled-table")
    st.markdown(f'<div class="dataframe-container">{tabla_html}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("🎯 Comparativa de Puntos")
    # Para la gráfica usamos el df original numérico, no el HTML
    df_grafica = pd.DataFrame(filas_clasificacion)
    # Limpiamos HTML del nombre del jugador y de los puntos totales para que la gráfica los lea bien
    df_grafica['Jugador_Limpio'] = df_grafica['Jugador'].str.replace('<b>', '').str.replace('</b>', '')
    df_grafica['Puntos_Numericos'] = df_grafica['Puntos Totales'].str.extract('(\d+)').astype(int)
    
    fig_barras = px.bar(
        df_grafica, x="Jugador_Limpio", y="Puntos_Numericos", color="Jugador_Limpio", text_auto=True
    )
    fig_barras.update_layout(showlegend=False, xaxis_title="Jugador", yaxis_title="Puntos Totales")
    st.plotly_chart(fig_barras, use_container_width=True)

st.markdown("---")
st.subheader("⏳ Evolución Temporal de la Competición")

fig_lineas = px.line(
    df_historial, x="Jornada", y="Puntos Totales", color="Jugador", markers=True,
)
fig_lineas.update_layout(xaxis_title="Jornada de Liga", yaxis_title="Puntos Totales Acumulados")
st.plotly_chart(fig_lineas, use_container_width=True)

```

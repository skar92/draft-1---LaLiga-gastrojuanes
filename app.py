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
    "Sierra": ["Real Betis", "Málaga"],  # <-- Málaga añadido aquí
    "Vecina": ["Real Sociedad", "Racing"],
    "Mírete": ["Celta", "Levante"],
    "Miguel Ángel": ["Valencia", "Alavés"],
    "Juan": ["Getafe", "Rayo Vallecano"],
    "Joaquín": ["Sevilla", "Osasuna"],
    "Telenti": ["Espanyol", "Deportivo"],
}

# --- PUNTOS SUMADOS POR CADA EQUIPO (Actualización Manual) ---
puntos_equipos_valores = {
    "Athletic Club": 0, "Elche": 0, "Real Betis": 0, "Málaga": 0, 
    "Real Sociedad": 0, "Racing": 0, "Celta": 0, "Levante": 0, 
    "Valencia": 0, "Alavés": 0, "Getafe": 0, "Rayo Vallecano": 0, 
    "Sevilla": 0, "Osasuna": 0, "Espanyol": 0, "Deportivo": 0,
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

# --- ARCHIVOS LOCALES DE LOS ESCUDOS (Carpeta /img) ---
escudos_archivos = {
    "Athletic Club": "img/athletic.png",
    "Elche": "img/elche.png",
    "Real Betis": "img/betis.png",
    "Málaga": "img/malaga.png",  # <-- Ruta del escudo del Málaga
    "Real Sociedad": "img/realsociedad.png",
    "Racing": "img/racing.png",
    "Celta": "img/celta.png",
    "Levante": "img/levante.png",
    "Valencia": "img/valencia.png",
    "Alavés": "img/alaves.png",
    "Getafe": "img/getafe.png",
    "Rayo Vallecano": "img/rayo.png",
    "Sevilla": "img/sevilla.png",
    "Osasuna": "img/osasuna.png",
    "Espanyol": "img/espanyol.png",
    "Deportivo": "img/deportivo.png",
}

# --- CÓMPUTO DIRECTO DE PUNTOS ---
filas_clasificacion = []

for jugador, equipos in porra_equipos.items():
    pts_equipos = sum([puntos_equipos_valores.get(eq, 0) for eq in equipos])
    goleadores_dict = porra_goleadores.get(jugador, {})
    pts_goleadores = sum(goleadores_dict.values())
    pts_extra = puntos_apuesta.get(jugador, 0)
    puntos_totales = pts_equipos + pts_goleadores + pts_extra

    equipos_con_escudo = []
    for eq in equipos:
        ruta_img = escudos_archivos.get(eq, "")
        if ruta_img and os.path.exists(ruta_img):
            html_img = f'<img src="{ruta_img}" width="22" style="vertical-align: middle; margin-right: 5px;"> {eq}'
        else:
            html_img = f"⚽ {eq}"
        equipos_con_escudo.append(html_img)

    filas_clasificacion.append({
        "Jugador_Limpio": jugador,
        "Puntos_Numericos": puntos_totales,
        "Jugador": f"<b>{jugador}</b>",
        "Equipos": "<br>".join(equipos_con_escudo),
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

# --- ESTILOS CSS PERSONALIZADOS ---
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
    df_mostrar = df_liga.sort_values(by="Puntos_Numericos", ascending=False)[
        ["Jugador", "Equipos", "Goleador", "Pts Equipos", "Goles", "Pts Apuesta", "Puntos Totales"]
    ]
    tabla_html = df_mostrar.to_html(escape=False, index=False, classes="styled-table")
    st.markdown(f'<div class="dataframe-container">{tabla_html}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("🎯 Comparativa de Puntos")
    df_grafica = df_liga.sort_values(by="Puntos_Numericos", ascending=False)
    
    fig_barras = px.bar(
        df_grafica, 
        x="Jugador_Limpio", 
        y="Puntos_Numericos", 
        color="Jugador_Limpio", 
        text_auto=True
    )
    
    max_pts = df_grafica["Puntos_Numericos"].max()
    rango_maximo = max_pts + 5 if max_pts > 0 else 10
    
    fig_barras.update_layout(
        showlegend=False, 
        xaxis_title="Jugador", 
        yaxis_title="Puntos Totales",
        yaxis=dict(range=[0, rango_maximo])
    )
    st.plotly_chart(fig_barras, use_container_width=True)

st.markdown("---")
st.subheader("⏳ Evolución Temporal de la Competición")

fig_lineas = px.line(
    df_historial, x="Jornada", y="Puntos Totales", color="Jugador", markers=True,
)
fig_lineas.update_layout(
    xaxis_title="Jornada de Liga", 
    yaxis_title="Puntos Totales Acumulados",
    yaxis=dict(rangemode="tozero")
)
st.plotly_chart(fig_lineas, use_container_width=True)

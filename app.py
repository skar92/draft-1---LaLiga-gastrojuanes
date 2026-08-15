import base64
from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la interfaz de Streamlit
st.set_page_config(page_title="Draft LaLiga 2026/27", layout="wide")
st.title("🏆 Seguimiento y Clasificación del Draft de LaLiga")

# --- FUNCIÓN PARA CONVERTIR IMÁGENES A BASE64 ---
def obtener_imagen_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        return f"data:image/png;base64,{encoded}"
    return ""

# --- RUTAS DE LOS ESCUDOS EN LA CARPETA /img ---
escudos_archivos = {
    "Athletic Club": "img/athletic.png",
    "Elche": "img/elche.png",
    "Real Betis Balompie": "img/betis.png",
    "Malaga": "img/malaga.png",
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

# ==============================================================================
# 📝 ÚNICO SITIO DONDE SE ACTUALIZAN LOS DATOS DE LA JORNADA (DRAFT ACTUALIZADO)
# ==============================================================================

# Relación de qué jugador tiene qué equipos según el draft
asig_equipos = {
    "Ejkar": ["Athletic Club", "Elche"],
    "Sierra": ["Real Betis Balompie", "Malaga"],
    "Vecina": ["Real Sociedad", "Racing"],
    "Mírete": ["Celta", "Levante"],
    "Miguel Ángel": ["Valencia", "Alavés"],
    "Juan": ["Getafe", "Rayo Vallecano"],
    "Joaquín": ["Sevilla", "Osasuna"],
    "Telenti": ["Espanyol", "Deportivo"],
}

# Estadísticas de cada equipo: [Partidos Ganados (G), Partidos Empatados (E), Partidos Perdidos (P)]
stats_equipos = {
    "Athletic Club": {"G": 0, "E": 0, "P": 0},
    "Elche": {"G": 0, "E": 0, "P": 0},
    "Real Betis Balompie": {"G": 0, "E": 0, "P": 0},
    "Malaga": {"G": 0, "E": 0, "P": 0},
    "Real Sociedad": {"G": 0, "E": 0, "P": 0},
    "Racing": {"G": 0, "E": 0, "P": 0},
    "Celta": {"G": 0, "E": 0, "P": 0},
    "Levante": {"G": 0, "E": 0, "P": 0},
    "Valencia": {"G": 0, "E": 0, "P": 0},
    "Alavés": {"G": 0, "E": 0, "P": 0},
    "Getafe": {"G": 0, "E": 0, "P": 0},
    "Rayo Vallecano": {"G": 0, "E": 0, "P": 0},
    "Sevilla": {"G": 0, "E": 0, "P": 0},
    "Osasuna": {"G": 0, "E": 0, "P": 0},
    "Espanyol": {"G": 0, "E": 0, "P": 0},
    "Deportivo": {"G": 0, "E": 0, "P": 0},
}

# Goleadores elegidos en el draft con su equipo correspondiente y los goles que llevan
porra_goleadores = {
    "Borja Iglesias": {"Equipo": "Athletic Club", "Jugador": "Ejkar", "Goles": 0},
    "Lookman": {"Equipo": "Real Betis Balompie", "Jugador": "Sierra", "Goles": 0},
    "Aubameyang": {"Equipo": "Real Sociedad", "Jugador": "Vecina", "Goles": 0},
    "Budimir": {"Equipo": "Celta", "Jugador": "Mírete", "Goles": 0},
    "Mikautadze": {"Equipo": "Valencia", "Jugador": "Miguel Ángel", "Goles": 0},
    "Mikel Oyarzabal": {"Equipo": "Getafe", "Jugador": "Juan", "Goles": 0},
    "Julián Álvarez": {"Equipo": "Sevilla", "Jugador": "Joaquín", "Goles": 0},
    "Sørloth": {"Equipo": "Sevilla", "Jugador": "Joaquín", "Goles": 0},
    "Enes Unal": {"Equipo": "Espanyol", "Jugador": "Telenti", "Goles": 0},
    "Hugo Duro": {"Equipo": "Espanyol", "Jugador": "Telenti", "Goles": 0},
}

# Puntos de apuesta o extras de mesa por participante
puntos_apuesta = {
    "Sierra": 0, "Joaquín": 0, "Ejkar": 0, "Vecina": 0,
    "Telenti": 0, "Miguel Ángel": 0, "Mírete": 0, "Juan": 0,
}

# ==============================================================================

# Invertir el diccionario de equipos para saber qué jugador tiene cada equipo rápidamente
equipo_a_jugador = {}
for jugador, lista_eqs in asig_equipos.items():
    for eq in lista_eqs:
        equipo_a_jugador[eq] = jugador

# --- CONSTRUCCIÓN DE LA TABLA DE EQUIPOS ---
filas_equipos = []
for eq, st_eq in stats_equipos.items():
    g = st_eq["G"]
    e = st_eq["E"]
    p = st_eq["P"]
    jugados = g + e + p
    puntos = (g * 3) + (e * 1)
    
    ruta_img = escudos_archivos.get(eq, "")
    base64_img = obtener_imagen_base64(ruta_img)
    if base64_img:
        escudo_html = f'<img src="{base64_img}" width="24" style="vertical-align: middle; margin-right: 8px;"> {eq}'
    else:
        escudo_html = f"⚽ {eq}"
        
    filas_equipos.append({
        "Equipo_Nombre": eq,
        "Equipo": escudo_html,
        "Jugador": equipo_a_jugador.get(eq, "-"),
        "PJ": jugados,
        "G": g,
        "E": e,
        "P": p,
        "Puntos": puntos,
    })

df_equipos = pd.DataFrame(filas_equipos)
df_equipos = df_equipos.sort_values(by="Puntos", ascending=False).reset_index(drop=True)

# --- CONSTRUCCIÓN DE LA TABLA DE GOLEADORES ---
filas_goleadores = []
for gol, info in porra_goleadores.items():
    eq = info["Equipo"]
    st_eq = stats_equipos.get(eq, {"G":0, "E":0, "P":0})
    pj_equipo = st_eq["G"] + st_eq["E"] + st_eq["P"]
        
    filas_goleadores.append({
        "Goleador": gol,
        "Equipo": eq,
        "Jugador": info["Jugador"],
        "PJ": pj_equipo,
        "Goles": info["Goles"]
    })

df_goleadores = pd.DataFrame(filas_goleadores)
if not df_goleadores.empty:
    df_goleadores = df_goleadores.sort_values(by="Goles", ascending=False).reset_index(drop=True)

# --- CONSTRUCCIÓN DE LA CLASIFICACIÓN GENERAL (TERCERA TABLA) ---
filas_general = []
for jug in asig_equipos.keys():
    eqs_jugador = asig_equipos[jug]
    pts_eqs = sum([df_equipos.loc[df_equipos["Equipo_Nombre"] == eq, "Puntos"].values[0] for eq in eqs_jugador if eq in df_equipos["Equipo_Nombre"].values])
    
    goles_jugador = sum([info["Goles"] for info in porra_goleadores.values() if info["Jugador"] == jug])
    extra = puntos_apuesta.get(jug, 0)
    
    total = pts_eqs + goles_jugador + extra
    
    filas_general.append({
        "Jugador": f"<b>{jug}</b>",
        "Puntos de Equipos": pts_eqs,
        "Goles": goles_jugador,
        "Total": f"<span style='font-size: 1.2em; font-weight: bold;'>{total}</span>",
        "Total_Num": total
    })

df_general = pd.DataFrame(filas_general).sort_values(by="Total_Num", ascending=False).reset_index(drop=True)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .dataframe-container { overflow-x: auto; margin-bottom: 20px; }
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
        padding: 10px 14px;
        border-bottom: 1px solid #444444;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: rgba(255, 255, 255, 0.03);
    }
</style>
""", unsafe_allow_html=True)

# --- RENDERIZADO EN LA WEB ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚽ Clasificación de Equipos")
    df_mostrar_eq = df_equipos[["Equipo", "Jugador", "PJ", "G", "E", "P", "Puntos"]]
    tabla_eq_html = df_mostrar_eq.to_html(escape=False, index=False, classes="styled-table")
    st.markdown(f'<div class="dataframe-container">{tabla_eq_html}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("🎯 Tabla de Goleadores")
    if not df_goleadores.empty:
        df_mostrar_gol = df_goleadores[["Goleador", "Equipo", "Jugador", "PJ", "Goles"]]
        tabla_gol_html = df_mostrar_gol.to_html(escape=False, index=False, classes="styled-table")
        st.markdown(f'<div class="dataframe-container">{tabla_gol_html}</div>', unsafe_allow_html=True)
    else:
        st.info("No hay goleadores registrados todavía.")

st.markdown("---")

# --- TERCERA TABLA: CLASIFICACIÓN GENERAL ---
st.subheader("🏆 Clasificación General (Participantes)")
df_mostrar_gen = df_general[["Jugador", "Puntos de Equipos", "Goles", "Total"]]
tabla_gen_html = df_mostrar_gen.to_html(escape=False, index=False, classes="styled-table")
st.markdown(f'<div class="dataframe-container">{tabla_gen_html}</div>', unsafe_allow_html=True)

st.markdown("---")

# --- GRÁFICA COMPARATIVA DE PARTICIPANTES ---
st.subheader("📊 Gráfica de Puntos Totales")
fig_barras = px.bar(
    df_general, 
    x="Jugador", 
    y="Total_Num", 
    color="Jugador", 
    text_auto=True
)

max_pts = df_general["Total_Num"].max()
rango_maximo = max_pts + 5 if max_pts > 0 else 10

fig_barras.update_layout(
    showlegend=False, 
    xaxis_title="Participante", 
    yaxis_title="Puntos Totales",
    yaxis=dict(range=[0, rango_maximo])
)
st.plotly_chart(fig_barras, use_container_width=True)

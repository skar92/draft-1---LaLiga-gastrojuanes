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


# --- CONFIGURACIÓN DE LOS PARTICIPANTES Y SUS EQUIPOS (Estructura Draft) ---
# Cada participante cuenta con 2 equipos asignados
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
    "Athletic Club": 0,
    "Elche": 0,
    "Real Betis": 0,
    "Real Sociedad": 0,
    "Racing": 0,
    "Celta": 0,
    "Levante": 0,
    "Valencia": 0,
    "Alavés": 0,
    "Getafe": 0,
    "Rayo Vallecano": 0,
    "Sevilla": 0,
    "Osasuna": 0,
    "Espanyol": 0,
    "Deportivo": 0,
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
    "Sierra": 0,
    "Joaquín": 0,
    "Ejkar": 0,
    "Vecina": 0,
    "Telenti": 0,
    "Miguel Ángel": 0,
    "Mírete": 0,
    "Juan": 0,
}

# Mapeo visual de escudos/iconos por equipo
escudos = {
    "Athletic Club": "🔴⚪",
    "Elche": "🟢⚪",
    "Real Betis": "🟢⚪",
    "Real Sociedad": "🔵⚪",
    "Racing": "🟢⚪",
    "Celta": "🩵",
    "Levante": "🔴🔵",
    "Valencia": "⚪⚫",
    "Alavés": "🔵⚪",
    "Getafe": "🔵",
    "Rayo Vallecano": "⚪🔴",
    "Sevilla": "⚪🔴",
    "Osasuna": "🔴🔵",
    "Espanyol": "🔵⚪",
    "Deportivo": "🔵⚪",
}

# --- CÓMPUTO DIRECTO DE PUNTOS ---
filas_clasificacion = []

for jugador, equipos in porra_equipos.items():
  # Puntos sumados por los equipos elegidos
  pts_equipos = sum([puntos_equipos_valores.get(eq, 0) for eq in equipos])

  # Goles sumados por los futbolistas
  goleadores_dict = porra_goleadores.get(jugador, {})
  pts_goleadores = sum(goleadores_dict.values())

  # Puntos de apuestas de mesa
  pts_extra = puntos_apuesta.get(jugador, 0)

  # Puntuación Total acumulada
  puntos_totales = pts_equipos + pts_goleadores + pts_extra

  filas_clasificacion.append({
      "Jugador": jugador,
      "Equipos": ", ".join(
          [f"{escudos.get(eq, '⚽')} {eq}" for eq in equipos]
      ),
      "Goleador": ", ".join(
          [f"{gol} ({pts})" for gol, pts in goleadores_dict.items()]
      ),
      "Pts Equipos": pts_equipos,
      "Goles": pts_goleadores,
      "Pts Apuesta": pts_extra,
      "Puntos Totales": puntos_totales,
  })

df_liga = pd.DataFrame(filas_clasificacion)

# --- HISTORIAL CRONOLÓGICO MANUAL (Para la gráfica de evolución) ---
datos_historicos = [
    # Puedes ir añadiendo registros por jornada/fecha según actualices la tabla manual
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

# --- RENDERIZADO INTERFAZ STREAMLIT ---
col1, col2 = st.columns([1.2, 0.8])

with col1:
  st.subheader("📊 Clasificación General")
  df_mostrar = df_liga.sort_values(by="Puntos Totales", ascending=False)[
      [
          "Jugador",
          "Equipos",
          "Goleador",
          "Pts Equipos",
          "Goles",
          "Pts Apuesta",
          "Puntos Totales",
      ]
  ]
  st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

with col2:
  st.subheader("🎯 Comparativa de Puntos Totales")
  fig_barras = px.bar(
      df_mostrar,
      x="Jugador",
      y="Puntos Totales",
      color="Jugador",
      text_auto=True,
  )
  st.plotly_chart(fig_barras, use_container_width=True)

st.markdown("---")
st.subheader("⏳ Evolución Temporal de la Competición")

fig_lineas = px.line(
    df_historial,
    x="Jornada",
    y="Puntos Totales",
    color="Jugador",
    markers=True,
)
fig_lineas.update_layout(
    xaxis_title="Jornada de Liga", yaxis_title="Puntos Totales Acumulados"
)
st.plotly_chart(fig_lineas, use_container_width=True)

```

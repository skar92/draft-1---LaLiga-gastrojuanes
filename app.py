import base64
import io
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==============================================================================
# CONFIGURACIÓN DE LA INTERFAZ
# ==============================================================================

st.set_page_config(
    page_title="Draft LaLiga 2026/27",
    layout="wide"
)

st.title("🏆 Seguimiento y Clasificación del Draft de LaLiga")


# ==============================================================================
# CONFIGURACIÓN DEL HISTÓRICO EN GITHUB
# ==============================================================================

GITHUB_USUARIO = "skar92"
GITHUB_REPOSITORIO = "draft-1---laliga-gastrojuanes"
GITHUB_RAMA = "main"
GITHUB_ARCHIVO_HISTORICO = "historico_puntos.csv"

GITHUB_API_URL = (
    f"https://api.github.com/repos/"
    f"{GITHUB_USUARIO}/"
    f"{GITHUB_REPOSITORIO}/"
    f"contents/"
    f"{GITHUB_ARCHIVO_HISTORICO}"
)

# Zona horaria española.
# Europe/Madrid contempla automáticamente horario de verano/invierno.
ZONA_HORARIA_ESPAÑA = ZoneInfo("Europe/Madrid")


# ==============================================================================
# FUNCIONES DEL HISTÓRICO
# ==============================================================================

def obtener_fecha_españa():
    """
    Devuelve la fecha actual según la hora española.
    Formato: YYYY-MM-DD
    """

    ahora = datetime.now(
        ZONA_HORARIA_ESPAÑA
    )

    return ahora.date().isoformat()


def obtener_historico_github():
    """
    Descarga historico_puntos.csv desde GitHub.

    Devuelve:
        df   -> DataFrame con el histórico
        sha  -> SHA del archivo en GitHub
    """

    token = st.secrets["GITHUB_TOKEN"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    respuesta = requests.get(
        GITHUB_API_URL,
        headers=headers,
        params={
            "ref": GITHUB_RAMA
        },
        timeout=10
    )

    if respuesta.status_code == 200:

        datos = respuesta.json()

        contenido = base64.b64decode(
            datos["content"]
        ).decode("utf-8")

        try:

            df = pd.read_csv(
                io.StringIO(contenido)
            )

        except Exception:

            df = pd.DataFrame(
                columns=[
                    "Fecha",
                    "Jugador",
                    "Puntos"
                ]
            )

        return df, datos["sha"]

    elif respuesta.status_code == 404:

        df = pd.DataFrame(
            columns=[
                "Fecha",
                "Jugador",
                "Puntos"
            ]
        )

        return df, None

    else:

        raise Exception(
            "No se pudo leer el histórico de GitHub.\n\n"
            f"Código: {respuesta.status_code}\n"
            f"Respuesta: {respuesta.text}"
        )


def guardar_historico_github(df, sha):
    """
    Guarda el histórico actualizado en GitHub.
    """

    token = st.secrets["GITHUB_TOKEN"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    contenido_csv = df.to_csv(
        index=False
    )

    contenido_base64 = base64.b64encode(
        contenido_csv.encode("utf-8")
    ).decode("utf-8")

    datos = {
        "message": "Actualizar histórico de puntos",
        "content": contenido_base64,
        "branch": GITHUB_RAMA
    }

    if sha is not None:

        datos["sha"] = sha

    respuesta = requests.put(
        GITHUB_API_URL,
        headers=headers,
        json=datos,
        timeout=10
    )

    if respuesta.status_code not in [200, 201]:

        raise Exception(
            "No se pudo guardar el histórico en GitHub.\n\n"
            f"Código: {respuesta.status_code}\n"
            f"Respuesta: {respuesta.text}"
        )


def actualizar_historico_puntos(df_general):
    """
    Actualiza el histórico de puntos.

    - Un registro por jugador y día.
    - Si los puntos de hoy no han cambiado, no modifica GitHub.
    - Si los puntos de hoy han cambiado, sobrescribe el día actual.
    - Los días anteriores se conservan.
    """

    fecha_hoy = obtener_fecha_españa()

    # --------------------------------------------------------------------------
    # Leer histórico
    # --------------------------------------------------------------------------

    historico, sha = obtener_historico_github()

    # --------------------------------------------------------------------------
    # Normalizar histórico
    # --------------------------------------------------------------------------

    if historico.empty:

        historico = pd.DataFrame(
            columns=[
                "Fecha",
                "Jugador",
                "Puntos"
            ]
        )

    else:

        historico["Fecha"] = (
            pd.to_datetime(
                historico["Fecha"],
                errors="coerce"
            )
            .dt.strftime("%Y-%m-%d")
        )

        historico["Puntos"] = pd.to_numeric(
            historico["Puntos"],
            errors="coerce"
        )

        historico = historico.dropna(
            subset=[
                "Fecha",
                "Jugador",
                "Puntos"
            ]
        )

    # --------------------------------------------------------------------------
    # Crear datos actuales
    # --------------------------------------------------------------------------

    datos_actuales = pd.DataFrame({
        "Fecha": fecha_hoy,

        "Jugador": (
            df_general["Jugador"]
            .str.replace(
                "<b>",
                "",
                regex=False
            )
            .str.replace(
                "</b>",
                "",
                regex=False
            )
        ),

        "Puntos": df_general["Total_Num"].astype(float)
    })

    # --------------------------------------------------------------------------
    # Comprobar si los datos de HOY ya son exactamente iguales
    # --------------------------------------------------------------------------

    historico_hoy = historico[
        historico["Fecha"] == fecha_hoy
    ].copy()

    if not historico_hoy.empty:

        historico_hoy = (
            historico_hoy[
                [
                    "Jugador",
                    "Puntos"
                ]
            ]
            .sort_values(
                "Jugador"
            )
            .reset_index(drop=True)
        )

        actuales_hoy = (
            datos_actuales[
                [
                    "Jugador",
                    "Puntos"
                ]
            ]
            .sort_values(
                "Jugador"
            )
            .reset_index(drop=True)
        )

        if historico_hoy.equals(actuales_hoy):

            # No ha cambiado nada.
            # No hacemos ningún commit.
            return historico

    # --------------------------------------------------------------------------
    # Eliminar los datos de HOY
    # --------------------------------------------------------------------------

    historico = historico[
        historico["Fecha"] != fecha_hoy
    ]

    # --------------------------------------------------------------------------
    # Añadir los datos actuales
    # --------------------------------------------------------------------------

    historico = pd.concat(
        [
            historico,
            datos_actuales
        ],
        ignore_index=True
    )

    # --------------------------------------------------------------------------
    # Ordenar
    # --------------------------------------------------------------------------

    historico = (
        historico
        .sort_values(
            by=[
                "Fecha",
                "Jugador"
            ]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------------------------
    # Guardar en GitHub
    # --------------------------------------------------------------------------

    guardar_historico_github(
        historico,
        sha
    )

    return historico


# ==============================================================================
# FUNCIÓN PARA CONVERTIR IMÁGENES A BASE64
# ==============================================================================

def obtener_imagen_base64(ruta):

    if os.path.exists(ruta):

        with open(ruta, "rb") as f:

            data = f.read()

        encoded = base64.b64encode(
            data
        ).decode()

        return f"data:image/png;base64,{encoded}"

    return ""


# ==============================================================================
# ESCUDOS
# ==============================================================================

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

    "Atlético de Madrid": "img/atletico.png",
    "Villarreal": "img/villarreal.png",
}


# ==============================================================================
# EQUIPOS ASIGNADOS A CADA PARTICIPANTE
# ==============================================================================

asig_equipos = {

    "Ejkar": [
        "Athletic Club",
        "Elche"
    ],

    "Sierra": [
        "Real Betis Balompie",
        "Malaga"
    ],

    "Vecina": [
        "Real Sociedad",
        "Racing"
    ],

    "Mírete": [
        "Celta",
        "Levante"
    ],

    "Miguel Ángel": [
        "Valencia",
        "Alavés"
    ],

    "Juan": [
        "Getafe",
        "Rayo Vallecano"
    ],

    "Joaquín": [
        "Sevilla",
        "Osasuna"
    ],

    "Telenti": [
        "Espanyol",
        "Deportivo"
    ],
}


# ==============================================================================
# ESTADÍSTICAS DE LOS EQUIPOS
# ==============================================================================

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


# ==============================================================================
# PORRA DE GOLEADORES
# ==============================================================================

porra_goleadores = {

    "Borja Iglesias": {
        "Jugador": "Ejkar",
        "Equipo": "Celta",
        "Goles": 0
    },

    "Cucho Hernández": {
        "Jugador": "Ejkar",
        "Equipo": "Real Betis Balompie",
        "Goles": 0
    },

    "Lookman": {
        "Jugador": "Sierra",
        "Equipo": "Atlético de Madrid",
        "Goles": 0
    },

    "Isi Palazón": {
        "Jugador": "Sierra",
        "Equipo": "Rayo Vallecano",
        "Goles": 0
    },

    "Aubameyang": {
        "Jugador": "Vecina",
        "Equipo": "Deportivo",
        "Goles": 0
    },

    "Toni Martinez": {
        "Jugador": "Vecina",
        "Equipo": "Alavés",
        "Goles": 0
    },

    "Budimir": {
        "Jugador": "Mírete",
        "Equipo": "Osasuna",
        "Goles": 0
    },

    "Ayoze": {
        "Jugador": "Mírete",
        "Equipo": "Villarreal",
        "Goles": 0
    },

    "Mikautadze": {
        "Jugador": "Miguel Ángel",
        "Equipo": "Villarreal",
        "Goles": 0
    },

    "Sancet": {
        "Jugador": "Miguel Ángel",
        "Equipo": "Athletic Club",
        "Goles": 0
    },

    "Mikel Oyarzabal": {
        "Jugador": "Juan",
        "Equipo": "Real Sociedad",
        "Goles": 0
    },

    "Julián Álvarez": {
        "Jugador": "Joaquín",
        "Equipo": "Atlético de Madrid",
        "Goles": 0
    },

    "Sørloth": {
        "Jugador": "Joaquín",
        "Equipo": "Atlético de Madrid",
        "Goles": 0
    },

    "Enes Unal": {
        "Jugador": "Telenti",
        "Equipo": "Getafe",
        "Goles": 0
    },

    "Hugo Duro": {
        "Jugador": "Telenti",
        "Equipo": "Valencia",
        "Goles": 0
    },
}


# ==============================================================================
# PUNTOS DE APUESTAS
# ==============================================================================

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


# ==============================================================================
# RELACIÓN EQUIPO → PARTICIPANTE
# ==============================================================================

equipo_a_jugador = {}

for jugador, lista_eqs in asig_equipos.items():

    for eq in lista_eqs:

        equipo_a_jugador[eq] = jugador


# ==============================================================================
# CONSTRUCCIÓN DE LA TABLA DE EQUIPOS
# ==============================================================================

filas_equipos = []

for eq, st_eq in stats_equipos.items():

    g = st_eq["G"]
    e = st_eq["E"]
    p = st_eq["P"]

    jugados = g + e + p

    puntos = (
        g * 3
    ) + e

    ruta_img = escudos_archivos.get(
        eq,
        ""
    )

    base64_img = obtener_imagen_base64(
        ruta_img
    )

    if base64_img:

        escudo_html = (
            f'<img src="{base64_img}" '
            f'width="24" '
            f'height="24" '
            f'style="vertical-align: middle; '
            f'margin-right: 8px; '
            f'object-fit: contain;">'
            f'{eq}'
        )

    else:

        escudo_html = f"⚽ {eq}"

    filas_equipos.append({

        "Equipo_Nombre": eq,

        "Equipo": escudo_html,

        "Jugador": equipo_a_jugador.get(
            eq,
            "-"
        ),

        "PJ": jugados,

        "G": g,

        "E": e,

        "P": p,

        "Puntos": puntos,
    })


df_equipos = (
    pd.DataFrame(filas_equipos)
    .sort_values(
        by="Puntos",
        ascending=False
    )
    .reset_index(drop=True)
)


# ==============================================================================
# CONSTRUCCIÓN DE LA TABLA DE GOLEADORES
# ==============================================================================

filas_goleadores = []

for gol, info in porra_goleadores.items():

    equipo = info["Equipo"]

    ruta_img = escudos_archivos.get(
        equipo,
        ""
    )

    base64_img = obtener_imagen_base64(
        ruta_img
    )

    if base64_img:

        goleador_html = (
            f'<img src="{base64_img}" '
            f'width="24" '
            f'height="24" '
            f'style="vertical-align: middle; '
            f'margin-right: 8px; '
            f'object-fit: contain;">'
            f'{gol}'
        )

    else:

        goleador_html = f"⚽ {gol}"

    filas_goleadores.append({

        "Goleador": goleador_html,

        "Jugador": info["Jugador"],

        "Equipo": equipo,

        "Goles": info["Goles"],
    })


df_goleadores = pd.DataFrame(
    filas_goleadores
)

if not df_goleadores.empty:

    df_goleadores = (
        df_goleadores
        .sort_values(
            by="Goles",
            ascending=False
        )
        .reset_index(drop=True)
    )


# ==============================================================================
# CLASIFICACIÓN GENERAL
# ==============================================================================

filas_general = []

for jug in asig_equipos.keys():

    eqs_jugador = asig_equipos[jug]

    # Puntos obtenidos por los equipos

    pts_eqs = sum(
        [

            df_equipos.loc[
                df_equipos["Equipo_Nombre"] == eq,
                "Puntos"
            ].values[0]

            for eq in eqs_jugador

            if eq in df_equipos[
                "Equipo_Nombre"
            ].values

        ]
    )

    # Goles de sus goleadores

    goles_jugador = sum(
        [

            info["Goles"]

            for info in porra_goleadores.values()

            if info["Jugador"] == jug

        ]
    )

    # Puntos adicionales de apuestas

    extra = puntos_apuesta.get(
        jug,
        0
    )

    # Total

    total = (
        pts_eqs
        + goles_jugador
        + extra
    )

    filas_general.append({

        "Jugador": f"<b>{jug}</b>",

        "Puntos de Equipos": pts_eqs,

        "Goles": goles_jugador,

        "Puntos de Apuestas": extra,

        "Total": (
            f"<span style='font-size: 1.2em; "
            f"font-weight: bold;'>"
            f"{total}"
            f"</span>"
        ),

        "Total_Num": total
    })


df_general = (
    pd.DataFrame(filas_general)
    .sort_values(
        by="Total_Num",
        ascending=False
    )
    .reset_index(drop=True)
)


# ==============================================================================
# ACTUALIZAR HISTÓRICO
# ==============================================================================

try:

    historico_puntos = actualizar_historico_puntos(
        df_general
    )

except Exception as error:

    st.error(
        "⚠️ No se pudo actualizar el histórico de puntos en GitHub."
    )

    st.code(
        str(error)
    )

    historico_puntos = pd.DataFrame(
        columns=[
            "Fecha",
            "Jugador",
            "Puntos"
        ]
    )


# ==============================================================================
# ESTILOS CSS
# ==============================================================================

st.markdown(
    """
    <style>

        .dataframe-container {
            overflow-x: auto;
            margin-bottom: 20px;
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

        .styled-table th,
        .styled-table td {
            padding: 10px 14px;
            border-bottom: 1px solid #444444;
        }

        .styled-table tbody tr:nth-of-type(even) {
            background-color: rgba(255, 255, 255, 0.03);
        }

        .styled-table td:first-child {
            vertical-align: middle;
        }

    </style>
    """,
    unsafe_allow_html=True
)


# ==============================================================================
# RENDERIZADO
# ==============================================================================

col1, col2 = st.columns(2)


# ==============================================================================
# ⚽ CLASIFICACIÓN DE EQUIPOS
# ==============================================================================

with col1:

    st.subheader(
        "⚽ Clasificación de Equipos"
    )

    df_mostrar_eq = df_equipos[
        [
            "Equipo",
            "Jugador",
            "PJ",
            "G",
            "E",
            "P",
            "Puntos"
        ]
    ]

    st.html(
        f"""
        <div class="dataframe-container">
            {df_mostrar_eq.to_html(
                escape=False,
                index=False,
                classes="styled-table"
            )}
        </div>
        """
    )


# ==============================================================================
# 🎯 TABLA DE GOLEADORES
# ==============================================================================

with col2:

    st.subheader(
        "🎯 Tabla de Goleadores"
    )

    if not df_goleadores.empty:

        df_mostrar_gol = df_goleadores[
            [
                "Goleador",
                "Jugador",
                "Goles"
            ]
        ]

        st.html(
            f"""
            <div class="dataframe-container">
                {df_mostrar_gol.to_html(
                    escape=False,
                    index=False,
                    classes="styled-table"
                )}
            </div>
            """
        )

    else:

        st.info(
            "No hay goleadores registrados todavía."
        )


# ==============================================================================
# SEPARADOR
# ==============================================================================

st.markdown("---")


# ==============================================================================
# 🏆 CLASIFICACIÓN GENERAL
# ==============================================================================

st.subheader(
    "🏆 Clasificación General (Participantes)"
)

df_mostrar_gen = df_general[
    [
        "Jugador",
        "Puntos de Equipos",
        "Goles",
        "Puntos de Apuestas",
        "Total"
    ]
]

st.html(
    f"""
    <div class="dataframe-container">
        {df_mostrar_gen.to_html(
            escape=False,
            index=False,
            classes="styled-table"
        )}
    </div>
    """
)


# ==============================================================================
# SEPARADOR
# ==============================================================================

st.markdown("---")


# ==============================================================================
# 📈 EVOLUCIÓN TEMPORAL DE PUNTOS
# ==============================================================================

st.subheader(
    "📈 Evolución temporal de puntos"
)

if historico_puntos.empty:

    st.info(
        "Todavía no hay datos históricos."
    )

else:

    historico_grafica = historico_puntos.copy()

    historico_grafica["Fecha"] = pd.to_datetime(
        historico_grafica["Fecha"],
        errors="coerce"
    )

    historico_grafica["Puntos"] = pd.to_numeric(
        historico_grafica["Puntos"],
        errors="coerce"
    )

    historico_grafica = (
        historico_grafica
        .dropna(
            subset=[
                "Fecha",
                "Jugador",
                "Puntos"
            ]
        )
        .sort_values(
            by=[
                "Fecha",
                "Jugador"
            ]
        )
        .reset_index(drop=True)
    )

    fig_lineas = px.line(
        historico_grafica,
        x="Fecha",
        y="Puntos",
        color="Jugador",
        markers=True,
        line_shape="linear",
        hover_data={
            "Fecha": "|%d/%m/%Y",
            "Jugador": True,
            "Puntos": True
        }
    )

    fig_lineas.update_traces(
        line=dict(
            width=3
        ),
        marker=dict(
            size=8
        )
    )

    fig_lineas.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Puntos Totales",
        hovermode="x unified",
        legend_title="Jugador",
        xaxis=dict(
            tickformat="%d/%m/%Y"
        ),
        yaxis=dict(
            rangemode="tozero"
        )
    )

    st.plotly_chart(
        fig_lineas,
        use_container_width=True
    )

# ==============================================================================
# --- 🎣 MINIJUEGO: LA PESCA DE JUAN ---
# ==============================================================================
st.markdown("---")
st.subheader("🎣 Minijuego: La Pesca de Juan")


# ==============================================================================
# --- 🏆 GESTIÓN DE VICTORIA ---
# ==============================================================================
query_params = st.query_params

if "win" in query_params and "time" in query_params:

    tiempo_ganado = query_params["time"]

    st.success(
        f"🎉 ¡Has completado el minijuego en "
        f"**{tiempo_ganado} segundos**!"
    )

    with st.form("form_registro_record"):

        st.markdown("### 💾 Registrar Récord en la Web")

        nombre_elegido = st.selectbox(
            "Selecciona tu nombre del registro:",
            [
                "juan",
                "telenti",
                "sierra",
                "ejkar",
                "mirete",
                "joaquin",
                "miguel angel",
                "vecina"
            ]
        )

        submitted = st.form_submit_button(
            "Guardar Récord Definitivo"
        )

        if submitted:

            guardar_record(
                nombre_elegido,
                tiempo_ganado
            )

            st.success(
                f"¡Récord guardado correctamente para "
                f"**{nombre_elegido}**!"
            )

            st.query_params.clear()
            st.rerun()


# ==============================================================================
# --- 🏅 TABLA DE RÉCORDS ---
# ==============================================================================
records_actuales = cargar_records()

if records_actuales:

    st.markdown(
        "### 🏅 Tabla de Récords Históricos (Permanente)"
    )

    st.dataframe(
        [
            {
                "Puesto": i + 1,
                "Nombre": r["nombre"].capitalize(),
                "Tiempo (s)": r["tiempo"]
            }
            for i, r in enumerate(records_actuales)
        ],
        use_container_width=True,
        hide_index=True
    )


# ==============================================================================
# --- 🖼️ IMAGEN DEL JUGADOR ---
# ==============================================================================
def obtener_imagen_base64(ruta_relativa):

    try:

        ruta_absoluta = os.path.join(
            os.path.dirname(__file__),
            ruta_relativa
        )

        if not os.path.exists(ruta_absoluta):
            ruta_absoluta = ruta_relativa

        with open(ruta_absoluta, "rb") as img_file:

            return base64.b64encode(
                img_file.read()
            ).decode("utf-8")

    except Exception:

        return ""


img_base64_pesca = obtener_imagen_base64(
    "img/jugador.png"
)


# ==============================================================================
# --- 🎮 HTML DEL JUEGO ---
# ==============================================================================
html_pesca_template = """
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
      content="width=device-width,
               initial-scale=1.0,
               maximum-scale=1.0,
               user-scalable=no,
               viewport-fit=cover">

<style>

body {

    margin: 0;
    padding: 0;

    overflow: hidden;

    font-family: 'Segoe UI', sans-serif;

    user-select: none;

    touch-action: none;

    background: #87CEEB;
}


#game-container {

    position: relative;

    width: 100%;

    max-width: 800px;

    margin: 0 auto;

    background: #000;

}


#game-canvas {

    background:
        linear-gradient(
            to bottom,
            #87CEEB 0%,
            #87CEEB 35%,
            #1E90FF 35%,
            #051937 100%
        );

    display: block;

    width: 100%;

    height: 500px;

}


#ui {

    position: absolute;

    top: 10px;

    left: 10px;

    color: white;

    text-shadow:
        1px 1px 2px black;

    pointer-events: none;

    font-weight: bold;

    font-size: 13px;

    z-index: 10;

}


#fullscreen-btn {

    position: absolute;

    top: 10px;

    right: 10px;

    background:
        rgba(0,0,0,0.7);

    color: #ffeb3b;

    border:
        2px solid #ffeb3b;

    padding:
        6px 12px;

    border-radius:
        20px;

    font-weight: bold;

    font-size: 11px;

    cursor: pointer;

    z-index: 50;

    display: block;

}


#giant-alert {

    position: absolute;

    top: 50%;

    left: 50%;

    transform:
        translate(-50%, -50%);

    color: white;

    font-size: 30px;

    font-weight: bold;

    text-align: center;

    background:
        rgba(0, 0, 0, 0.95);

    padding: 35px;

    border-radius: 20px;

    box-shadow:
        0 0 30px rgba(255,255,255,0.4);

    display: none;

    z-index: 40;

    width: 85%;

    max-width: 600px;

    box-sizing: border-box;

    border:
        4px solid #ffeb3b;

    line-height: 1.4;

}


#penalty-timer {

    position: absolute;

    top: 50%;

    left: 50%;

    transform:
        translate(-50%, -50%);

    color: #ff4444;

    font-size: 35px;

    font-weight: bold;

    display: none;

    text-align: center;

    background:
        rgba(0,0,0,0.85);

    padding: 20px;

    border-radius: 15px;

    z-index: 20;

}


#win-screen {

    position: absolute;

    top: 50%;

    left: 50%;

    transform:
        translate(-50%, -50%);

    background: white;

    padding: 25px;

    border-radius: 15px;

    text-align: center;

    display: none;

    box-shadow:
        0 0 25px rgba(0,0,0,0.5);

    z-index: 30;

}


.btn {

    background: #2ecc71;

    color: white;

    border: none;

    padding: 12px 24px;

    border-radius: 6px;

    cursor: pointer;

    font-weight: bold;

    margin-top: 12px;

}

</style>

</head>


<body>


<div id="game-container">


    <button id="fullscreen-btn">
        📱 FULLSCREEN
    </button>


    <div id="ui">

        <div
            style="
                color: #ffeb3b;
                font-size: 12px;
                margin-bottom: 4px;
                background: rgba(0,0,0,0.4);
                padding: 4px 8px;
                border-radius: 4px;
            "
        >

            🎮 <b>Muelle de Juan:</b>
            Pesca 10 Juanes.
            Velocidad de caña constante.
            ¡Cuidado con el radar!

        </div>


        <div>

            👤 Puntos Juan:

            <span id="score">
                0
            </span>

            / 10

            <span
                id="acid-indicator"
                style="
                    color:#2ecc71;
                    font-weight:bold;
                    display:none;
                "
            >

                ⚠️ LLUVIA ÁCIDA

            </span>

        </div>


        <div>

            ⏱️ Tiempo:

            <span id="clock">
                0.0
            </span>s

        </div>


        <div>

            🐟 Bultos:

            <span id="pop-count">
                0
            </span>

            / 20

        </div>


        <div
            id="instruction-text"
            style="
                color: #ffeb3b;
                margin-top: 2px;
            "
        >

            Toca para fijar el ÁNGULO

        </div>

    </div>


    <div id="giant-alert"></div>


    <div id="penalty-timer">

        🟥 PENALIZACIÓN

        <br>

        <span id="p-seconds">
            5
        </span>s

    </div>


    <div id="win-screen">

        <h2>
            🏆 ¡DESAFÍO COMPLETADO!
        </h2>

        <p id="final-time-text"></p>

        <button
            id="save-pesca-btn"
            class="btn"
        >

            💾 Registrar Récord

        </button>

    </div>


    <canvas id="game-canvas"></canvas>


</div>


<script>


// ==============================================================================
// --- CANVAS
// ==============================================================================

const canvas =
    document.getElementById(
        'game-canvas'
    );

const ctx =
    canvas.getContext('2d');


const scoreEl =
    document.getElementById(
        'score'
    );

const clockEl =
    document.getElementById(
        'clock'
    );

const popEl =
    document.getElementById(
        'pop-count'
    );


const winScreen =
    document.getElementById(
        'win-screen'
    );

const penaltyEl =
    document.getElementById(
        'penalty-timer'
    );

const pSecondsEl =
    document.getElementById(
        'p-seconds'
    );


const giantAlert =
    document.getElementById(
        'giant-alert'
    );

const fsBtn =
    document.getElementById(
        'fullscreen-btn'
    );

const container =
    document.getElementById(
        'game-container'
    );


const acidIndicator =
    document.getElementById(
        'acid-indicator'
    );


// ==============================================================================
// --- TAMAÑO
// ==============================================================================

let width = 800;

let height = 500;


function resizeGame() {

    if (
        document.fullscreenElement
    ) {

        width =
            window.innerWidth;

        height =
            window.innerHeight;

        canvas.style.height =
            height + "px";

    } else {

        width =
            container.offsetWidth ||
            800;

        height = 500;

        canvas.style.height =
            "500px";

    }


    canvas.width =
        width;

    canvas.height =
        height;

}


window.addEventListener(
    'resize',
    resizeGame
);


setTimeout(
    resizeGame,
    150
);


// ==============================================================================
// --- FULLSCREEN
// ==============================================================================

fsBtn.addEventListener(
    'click',
    async (e) => {

        e.stopPropagation();

        try {

            if (
                !document.fullscreenElement
            ) {

                if (
                    container.requestFullscreen
                ) {

                    await
                        container.requestFullscreen();

                }

            } else {

                document.exitFullscreen();

            }

        } catch (err) {

            console.error(err);

        }

    }
);


// ==============================================================================
// --- IMAGEN JUAN
// ==============================================================================

const juanImg =
    new Image();

let imageLoaded = false;


juanImg.src =
    "data:image/png;base64,{{JUAN_IMAGE_BASE64}}";


juanImg.onload = () => {

    imageLoaded = true;

};


// ==============================================================================
// --- VARIABLES DEL JUEGO
// ==============================================================================

let score = 0;

let accumulatedTime = 0;

let lastTimeCheck =
    Date.now();

let isGameOver = false;

let penaltyTime = 0;

let nPenalties = 0;

let globalPauseUntil = 0;


// ==============================================================================
// --- CONTROL DE LA CAÑA
// ==============================================================================

let inputState =
    'angle';

let angleParam =
    0.5;

let fixedAngle =
    0;

let chargeForce =
    0;


// ==============================================================================
// ⭐ VELOCIDAD CONSTANTE DE LA CAÑA
// ==============================================================================
//
// ESTA ES LA ÚNICA CIFRA QUE NECESITAS CAMBIAR
// PARA HACER LA CAÑA MÁS RÁPIDA O MÁS LENTA.
//
// 0.06 = velocidad actual.
//
// La magnitud siempre será 0.06.
// Solo cambia el signo (+/-) cuando rebota.
//
// ==============================================================================

const ANGLE_SPEED = 0.06;

let angleSpeed =
    ANGLE_SPEED;


// ==============================================================================
// --- VELOCIDADES ALEATORIAS DE LOS OBJETOS
// ==============================================================================

function getRandomSpeed(a, b) {

    let val =
        Math.random() *
        (b - a) +
        a;

    return Math.random() < 0.5
        ? val
        : -val;

}


// ==============================================================================
// --- HELICÓPTERO
// ==============================================================================

let heli = {

    x: 100,

    y: 35,

    vx: 4,

    nextChange: 0,

    radarWidth: 90,

    active: true,

    reactiveTime: 0

};


// ==============================================================================
// --- PATERA
// ==============================================================================

let patera = {

    active: false,

    x: 0,

    y: 0,

    startX: 0,

    baseVx: 0.8,

    maxVx: 2.0,

    spawnTimer:
        Date.now() + 15000,

    direction: 'right',

    hitFlash: 0

};


let waves = [];

let nextWaveSpawn = 0;


// ==============================================================================
// --- LLUVIA ÁCIDA
// ==============================================================================

let acidRainActive = false;

let nextAcidEvent =
    Date.now() + 25000;

let acidEndTime = 0;

let acidDrops = [];


// ==============================================================================
// --- ALERTA
// ==============================================================================

function triggerGiantAlert(
    message,
    borderColor = '#ffeb3b'
) {

    giantAlert.innerHTML =
        message.replace(
            /\\n/g,
            "<br>"
        );


    giantAlert.style.borderColor =
        borderColor;


    giantAlert.style.display =
        'block';


    globalPauseUntil =
        Date.now() + 2500;


    setTimeout(
        () => {

            giantAlert.style.display =
                'none';

        },
        2500
    );

}


// ==============================================================================
// --- TIPOS DE OBJETOS
// ==============================================================================

const TYPES = {

    JUAN: 'juan',

    BALL: 'ball',

    CARD: 'card'

};


let objects = [];


function countType(t) {

    return objects.filter(
        o => o.type === t
    ).length;

}


function countJuanines() {

    return objects.filter(
        o =>
            o.type === TYPES.JUAN &&
            o.isJuanin
    ).length;

}


// ==============================================================================
// --- CREAR OBJETO
// ==============================================================================

function spawnObject() {

    if (
        objects.length >= 20
    ) {

        return;

    }


    let totalJuanesTarget =
        Math.round(
            objects.length * 0.30
        );


    let currentJuanes =
        countType(
            TYPES.JUAN
        );


    let type;


    if (
        currentJuanes <
            totalJuanesTarget
        ||
        (
            objects.length === 0 &&
            Math.random() < 0.30
        )
    ) {

        type =
            TYPES.JUAN;

    } else {

        type =
            Math.random() < 0.5
                ? TYPES.BALL
                : TYPES.CARD;

    }


    let assignJuanin =
        false;


    if (
        type === TYPES.JUAN
    ) {

        let currentJuaninesCount =
            countJuanines();


        if (
            currentJuaninesCount <
            Math.round(
                (
                    currentJuanes + 1
                ) * 0.70
            )
        ) {

            assignJuanin =
                true;

        }

    }


    let isDiscovered =
        Math.random() >= 0.50;


    let maxLifeTime =
        25000 +
        Math.random() * 15000;


    let randomDepthPct =
        0.45 +
        Math.random() * 0.45;


    let randomVx =
        getRandomSpeed(
            1.5,
            2
        );


    let randomDepthSpeed =
        getRandomSpeed(
            0.04,
            0.09
        );


    objects.push({

        id:
            Math.random().toString(36),

        x:
            Math.random() * width,

        depthPercent:
            randomDepthPct,

        y:
            0,

        type:
            type,

        isJuanin:
            assignJuanin,

        vx:
            randomVx,

        ax:
            0,

        depthSpeed:
            randomDepthSpeed,

        depthAmp:
            12 +
            Math.random() * 22,

        phase:
            Math.random() *
            Math.PI *
            2,

        spawnTime:
            Date.now(),

        discovered:
            isDiscovered,

        lastDirectionChange:
            Date.now(),

        changeInterval:
            300 +
            Math.random() * 600,

        deathTime:
            Date.now() +
            maxLifeTime

    });

}


// ==============================================================================
// --- OBJETOS INICIALES
// ==============================================================================

for (
    let i = 12;
    i > 0;
    i--
) {

    spawnObject();

}


let nextSpawnTime =
    Date.now() + 4000;


// ==============================================================================
// --- ANZUELO
// ==============================================================================

let hook = {

    x: 0,

    y: 0,

    vx: 0,

    vy: 0,

    mode:
        'straight',

    targetX: 0,

    targetY: 0

};


// ==============================================================================
// --- LLUVIA ÁCIDA
// ==============================================================================

function triggerAcidRainStrike() {

    acidRainActive =
        true;


    acidEndTime =
        Date.now() + 6000;


    acidIndicator.style.display =
        'inline';


    if (
        objects.length > 0
    ) {

        let countToKill =
            Math.floor(
                objects.length * 0.5
            );


        objects.sort(
            () =>
                Math.random() - 0.5
        );


        objects.splice(
            0,
            countToKill
        );

    }


    triggerGiantAlert(
        "🌧️ ¡LLUVIA ÁCIDA COLOSAL!\\n" +
        "El 50% de los bultos marinos han sido disueltos.",
        "#2ecc71"
    );

}


// ==============================================================================
// --- UPDATE
// ==============================================================================

function update() {

    const now =
        Date.now();


    let deltaTime =
        now -
        lastTimeCheck;


    lastTimeCheck =
        now;


    if (
        isGameOver
    ) {

        return;

    }


    let seaTopBoundary =
        height * 0.35;


    if (
        seaTopBoundary < 180
    ) {

        seaTopBoundary =
            180;

    }


    // --------------------------------------------------------------------------
    // LLUVIA ÁCIDA
    // --------------------------------------------------------------------------

    if (
        !acidRainActive &&
        now > nextAcidEvent
    ) {

        triggerAcidRainStrike();

    }


    if (
        acidRainActive &&
        now > acidEndTime
    ) {

        acidRainActive =
            false;


        acidIndicator.style.display =
            'none';


        nextAcidEvent =
            now +
            25000 +
            Math.random() * 15000;

    }


    if (
        acidRainActive &&
        Math.random() < 0.5
    ) {

        acidDrops.push({

            x:
                Math.random() * width,

            y:
                0,

            speed:
                10 +
                Math.random() * 6

        });

    }


    for (
        let d = acidDrops.length - 1;
        d >= 0;
        d--
    ) {

        acidDrops[d].y +=
            acidDrops[d].speed;


        if (
            acidDrops[d].y > height
        ) {

            acidDrops.splice(
                d,
                1
            );

        }

    }


    // --------------------------------------------------------------------------
    // HELICÓPTERO
    // --------------------------------------------------------------------------

    if (
        !heli.active &&
        now > heli.reactiveTime
    ) {

        heli.active =
            true;

        heli.x =
            100;

    }


    if (
        heli.active
    ) {

        if (
            now > heli.nextChange
        ) {

            heli.vx =
                getRandomSpeed(
                    3,
                    8
                );

            heli.nextChange =
                now +
                500 +
                Math.random() * 1000;

        }


        heli.x +=
            heli.vx;


        if (
            heli.x < 40
        ) {

            heli.x = 40;

            heli.vx *= -1;

        }


        if (
            heli.x >
            width - 40
        ) {

            heli.x =
                width - 40;

            heli.vx *= -1;

        }

    }


    // --------------------------------------------------------------------------
    // PATERA
    // --------------------------------------------------------------------------

    if (
        !patera.active &&
        now > patera.spawnTimer
    ) {

        patera.active =
            true;


        patera.y =
            seaTopBoundary - 8;


        waves = [];


        nextWaveSpawn =
            now + 1000;


        if (
            Math.random() > 0.5
        ) {

            patera.x =
                -45;

            patera.startX =
                -45;

            patera.baseVx =
                0.8;

            patera.direction =
                'left';


            angleParam =
                Math.PI * 1.2;


        } else {

            patera.x =
                width + 45;

            patera.startX =
                width + 45;

            patera.baseVx =
                -0.8;

            patera.direction =
                'right';


            angleParam =
                Math.PI * 1.7;

        }


        // Aseguramos que la caña siga moviéndose
        // en el sentido correcto al iniciar la patera.
        angleSpeed =
            ANGLE_SPEED;


        triggerGiantAlert(
            "⛵ ¡PATERA DETECTADA!\\n" +
            "Velocidad progresiva hacia el centro. ¡Frénala!",
            "#f1c40f"
        );

    }


    if (
        patera.active &&
        now >= globalPauseUntil
    ) {

        let center =
            width / 2;


        if (
            now > nextWaveSpawn
        ) {

            waves.push({

                x:
                    center,

                y:
                    seaTopBoundary,

                vx:
                    patera.direction === 'left'
                        ? -1.8
                        : 1.8,

                size:
                    7

            });


            nextWaveSpawn =
                now + 4000;

        }


        for (
            let w = waves.length - 1;
            w >= 0;
            w--
        ) {

            let wave =
                waves[w];


            wave.x +=
                wave.vx;


            wave.size +=
                0.05;


            let distanceToPatera =
                Math.abs(
                    wave.x -
                    patera.x
                );


            if (
                distanceToPatera < 15
            ) {

                let fixedPush =
                    30;


                if (
                    patera.direction === 'left'
                ) {

                    patera.x =
                        Math.max(
                            patera.startX,
                            patera.x -
                                fixedPush
                        );

                } else {

                    patera.x =
                        Math.min(
                            patera.startX,
                            patera.x +
                                fixedPush
                        );

                }


                patera.hitFlash =
                    now + 250;


                waves.splice(
                    w,
                    1
                );


                continue;

            }


            if (
                wave.x < -60 ||
                wave.x > width + 60
            ) {

                waves.splice(
                    w,
                    1
                );

            }

        }


        let distanceToCenter =
            Math.abs(
                center -
                patera.x
            );


        let maxDistance =
            Math.abs(
                center -
                patera.startX
            );


        let progress =
            1 -
            (
                distanceToCenter /
                maxDistance
            );


        let currentSpeed =
            patera.baseVx +
            (
                patera.maxVx *
                progress *
                Math.sign(
                    patera.baseVx
                )
            );


        patera.x +=
            currentSpeed;


        if (
            (
                patera.baseVx > 0 &&
                patera.x >= center
            )
            ||
            (
                patera.baseVx < 0 &&
                patera.x <= center
            )
        ) {

            patera.active =
                false;

            waves = [];


            patera.spawnTimer =
                now + 45000;


            score =
                0;


            scoreEl.innerText =
                score;


            triggerGiantAlert(
                "☠️ ¡LA PATERA ASALTÓ EL MUELLE!\\n" +
                "Has perdido todos tus JUANES acumulados",
                "#e74c3c"
            );

        }

    } else {

        waves = [];

    }


    // --------------------------------------------------------------------------
    // PAUSA
    // --------------------------------------------------------------------------

    if (
        now < globalPauseUntil
    ) {

        return;

    }


    // --------------------------------------------------------------------------
    // PENALIZACIÓN
    // --------------------------------------------------------------------------

    if (
        penaltyTime > now
    ) {

        penaltyEl.style.display =
            'block';


        pSecondsEl.innerText =
            Math.ceil(
                (
                    penaltyTime -
                    now
                ) / 1000
            );


        inputState =
            'angle';


        return;

    } else {

        penaltyEl.style.display =
            'none';

    }


    // --------------------------------------------------------------------------
    // TIEMPO
    // --------------------------------------------------------------------------

    accumulatedTime +=
        deltaTime;


    clockEl.innerText =
        (
            accumulatedTime /
            1000
        ).toFixed(1);


    popEl.innerText =
        objects.length;


    // ==========================================================================
    // ⭐ CAÑA: VELOCIDAD CONSTANTE + REBOTE CORRECTO
    // ==========================================================================
    //
    // La velocidad absoluta siempre es ANGLE_SPEED.
    //
    // Cuando llega a un extremo:
    //
    //      +0.06  ->  -0.06
    //
    // o:
    //
    //      -0.06  ->  +0.06
    //
    // De esta forma nunca se queda clavada.
    // ==========================================================================

    if (
        inputState === 'angle'
    ) {

        angleParam +=
            angleSpeed;


        if (
            patera.active
        ) {

            // ------------------------------------------------------------------
            // PATERA HACIA LA IZQUIERDA
            // Rango angular: π → 1.5π
            // ------------------------------------------------------------------

            if (
                patera.direction === 'left'
            ) {

                const minLimit =
                    Math.PI;

                const maxLimit =
                    Math.PI * 1.5;


                if (
                    angleParam >=
                    maxLimit
                ) {

                    angleParam =
                        maxLimit;

                    angleSpeed =
                        -ANGLE_SPEED;

                }


                if (
                    angleParam <=
                    minLimit
                ) {

                    angleParam =
                        minLimit;

                    angleSpeed =
                        ANGLE_SPEED;

                }


            // ------------------------------------------------------------------
            // PATERA HACIA LA DERECHA
            // Rango angular: 1.5π → 2π
            // ------------------------------------------------------------------

            } else {

                const minLimit =
                    Math.PI * 1.5;

                const maxLimit =
                    Math.PI * 2;


                if (
                    angleParam >=
                    maxLimit
                ) {

                    angleParam =
                        maxLimit;

                    angleSpeed =
                        -ANGLE_SPEED;

                }


                if (
                    angleParam <=
                    minLimit
                ) {

                    angleParam =
                        minLimit;

                    angleSpeed =
                        ANGLE_SPEED;

                }

            }


        // ----------------------------------------------------------------------
        // MODO NORMAL
        // Rango angular: 0 → π
        // ----------------------------------------------------------------------

        } else {

            const minLimit =
                0;

            const maxLimit =
                Math.PI;


            if (
                angleParam >=
                maxLimit
            ) {

                angleParam =
                    maxLimit;

                angleSpeed =
                    -ANGLE_SPEED;

            }


            if (
                angleParam <=
                minLimit
            ) {

                angleParam =
                    minLimit;

                angleSpeed =
                    ANGLE_SPEED;

            }

        }

    }


    // --------------------------------------------------------------------------
    // CARGAR FUERZA
    // --------------------------------------------------------------------------

    if (
        inputState === 'force'
    ) {

        chargeForce =
            Math.min(
                chargeForce + 4.5,
                100
            );

    }


    // --------------------------------------------------------------------------
    // SPAWN
    // --------------------------------------------------------------------------

    if (
        now > nextSpawnTime
    ) {

        if (
            objects.length < 20
        ) {

            spawnObject();

        }


        nextSpawnTime =
            now + 2500;

    }


    // --------------------------------------------------------------------------
    // PROPORCIÓN JUANES
    // --------------------------------------------------------------------------

    let totalJuanesTarget =
        Math.round(
            objects.length * 0.30
        );


    let currentJuanes =
        countType(
            TYPES.JUAN
        );


    if (
        currentJuanes <
            totalJuanesTarget &&
        objects.length > 0
    ) {

        for (
            let o of objects
        ) {

            if (
                o.type !== TYPES.JUAN
            ) {

                o.type =
                    TYPES.JUAN;

                currentJuanes++;


                if (
                    currentJuanes >=
                    totalJuanesTarget
                ) {

                    break;

                }

            }

        }

    }


    // --------------------------------------------------------------------------
    // JUANINES
    // --------------------------------------------------------------------------

    let currentJuanesList =
        objects.filter(
            o =>
                o.type === TYPES.JUAN
        );


    let expectedJuanines =
        Math.round(
            currentJuanesList.length *
            0.70
        );


    let actualJuanines =
        countJuanines();


    if (
        actualJuanines <
        expectedJuanines
    ) {

        for (
            let j of currentJuanesList
        ) {

            if (
                !j.isJuanin
            ) {

                j.isJuanin =
                    true;

                actualJuanines++;


                if (
                    actualJuanines >=
                    expectedJuanines
                ) {

                    break;

                }

            }

        }

    } else if (
        actualJuanines >
        expectedJuanines
    ) {

        for (
            let j of currentJuanesList
        ) {

            if (
                j.isJuanin
            ) {

                j.isJuanin =
                    false;

                actualJuanines--;


                if (
                    actualJuanines <=
                    expectedJuanines
                ) {

                    break;

                }

            }

        }

    }


    // --------------------------------------------------------------------------
    // DESCUBIERTOS
    // --------------------------------------------------------------------------

    let totalDiscovered =
        objects.filter(
            o => o.discovered
        ).length;


    let minimumRequired =
        Math.ceil(
            objects.length * 0.50
        );


    if (
        totalDiscovered <
        minimumRequired
    ) {

        for (
            let o of objects
        ) {

            if (
                !o.discovered
            ) {

                o.discovered =
                    true;

                totalDiscovered++;


                if (
                    totalDiscovered >=
                    minimumRequired
                ) {

                    break;

                }

            }

        }

    }


    // --------------------------------------------------------------------------
    // MOVIMIENTO DE OBJETOS
    // --------------------------------------------------------------------------

    for (
        let i = objects.length - 1;
        i >= 0;
        i--
    ) {

        let obj =
            objects[i];


        obj.x +=
            obj.vx;


        if (
            obj.x < 0 ||
            obj.x > width
        ) {

            obj.vx *= -1;

        }


        let calculatedBaseY =
            height *
            obj.depthPercent;


        obj.phase +=
            obj.depthSpeed;


        obj.y =
            calculatedBaseY +
            Math.sin(
                obj.phase
            ) *
            obj.depthAmp;


        if (
            now > obj.deathTime
        ) {

            objects.splice(
                i,
                1
            );


            spawnObject();

        }

    }


    // ==========================================================================
    // --- LANZAMIENTO
    // ==========================================================================

    if (
        inputState === 'launching'
    ) {

        if (
            hook.mode ===
            'parabolic'
        ) {

            hook.x +=
                hook.vx;


            hook.vy +=
                0.5;


            hook.y +=
                hook.vy;


            if (
                patera.active &&
                Math.abs(
                    hook.x -
                    patera.x
                ) < 28 &&
                Math.abs(
                    hook.y -
                    patera.y
                ) < 22
            ) {

                processPateraCatch();

                return;

            }


            if (
                hook.y >=
                seaTopBoundary
            ) {

                hook.mode =
                    'straight';


                hook.targetX =
                    hook.x +
                    hook.vx * 5;


                hook.targetY =
                    height - 30;

            }


            if (
                hook.x < 0 ||
                hook.x > width ||
                hook.y > height
            ) {

                inputState =
                    'returning';

            }


        } else {

            let dx =
                hook.targetX -
                hook.x;


            let dy =
                hook.targetY -
                hook.y;


            let dist =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );


            let targetHit =
                null;


            let hitIndex =
                -1;


            for (
                let i = 0;
                i < objects.length;
                i++
            ) {

                let o =
                    objects[i];


                let activeSize =
                    o.discovered
                        ? (
                            o.isJuanin
                                ? 15
                                : 28
                        )
                        : 28;


                if (
                    Math.sqrt(
                        (
                            hook.x -
                            o.x
                        ) ** 2 +
                        (
                            hook.y -
                            o.y
                        ) ** 2
                    ) < activeSize
                ) {

                    targetHit =
                        o;

                    hitIndex =
                        i;

                    break;

                }

            }


            if (
                targetHit
            ) {

                processCatch(
                    targetHit,
                    hitIndex
                );

            } else if (
                dist > 22
            ) {

                hook.x +=
                    (
                        dx /
                        dist
                    ) * 22;


                hook.y +=
                    (
                        dy /
                        dist
                    ) * 22;

            } else {

                inputState =
                    'returning';

            }

        }


    } else if (
        inputState ===
        'returning'
    ) {

        let dx =
            (
                width / 2
            ) -
            hook.x;


        let dy =
            (
                seaTopBoundary - 15
            ) -
            hook.y;


        let dist =
            Math.sqrt(
                dx * dx +
                dy * dy
            );


        if (
            dist > 30
        ) {

            hook.x +=
                (
                    dx /
                    dist
                ) * 30;


            hook.y +=
                (
                    dy /
                    dist
                ) * 30;

        } else {

            inputState =
                'angle';


            // IMPORTANTE:
            // no ponemos siempre +ANGLE_SPEED.
            // Conservamos el sentido que llevaba la caña.

            angleSpeed =
                angleSpeed >= 0
                    ? ANGLE_SPEED
                    : -ANGLE_SPEED;


            // Si el ángulo queda exactamente en un límite,
            // nos aseguramos de que salga hacia dentro.

            if (
                !patera.active
            ) {

                if (
                    angleParam >= Math.PI
                ) {

                    angleParam =
                        Math.PI;

                    angleSpeed =
                        -ANGLE_SPEED;

                }


                if (
                    angleParam <= 0
                ) {

                    angleParam =
                        0;

                    angleSpeed =
                        ANGLE_SPEED;

                }

            } else {

                if (
                    patera.direction === 'left'
                ) {

                    const minLimit =
                        Math.PI;

                    const maxLimit =
                        Math.PI * 1.5;


                    if (
                        angleParam >=
                        maxLimit
                    ) {

                        angleParam =
                            maxLimit;

                        angleSpeed =
                            -ANGLE_SPEED;

                    }


                    if (
                        angleParam <=
                        minLimit
                    ) {

                        angleParam =
                            minLimit;

                        angleSpeed =
                            ANGLE_SPEED;

                    }

                } else {

                    const minLimit =
                        Math.PI * 1.5;

                    const maxLimit =
                        Math.PI * 2;


                    if (
                        angleParam >=
                        maxLimit
                    ) {

                        angleParam =
                            maxLimit;

                        angleSpeed =
                            -ANGLE_SPEED;

                    }


                    if (
                        angleParam <=
                        minLimit
                    ) {

                        angleParam =
                            minLimit;

                        angleSpeed =
                            ANGLE_SPEED;

                    }

                }

            }

        }

    }

}


// ==============================================================================
// --- CAPTURAR PATERA
// ==============================================================================

function processPateraCatch() {

    patera.active =
        false;


    waves = [];


    patera.spawnTimer =
        Date.now() + 60000;


    heli.active =
        false;


    heli.reactiveTime =
        Date.now() + 60000;


    inputState =
        'returning';


    score += 2;


    scoreEl.innerText =
        score;


    triggerGiantAlert(
        "🚔 ¡EL JUANPRONA SE LLEVA LA PATERA!\\n" +
        "Tramitando la detención en comisaría. " +
        "¡Suman +2 PUNTOS fijos! 60s de tregua.",
        "#3498db"
    );


    if (
        score >= 10
    ) {

        isGameOver =
            true;


        setTimeout(
            win,
            100
        );

    }

}


// ==============================================================================
// --- CAPTURAR OBJETO
// ==============================================================================

function processCatch(
    obj,
    index
) {

    objects.splice(
        index,
        1
    );


    spawnObject();


    inputState =
        'returning';


    if (
        obj.type ===
        TYPES.JUAN
    ) {

        if (
            obj.isJuanin
        ) {

            let xMinRadar =
                heli.x -
                heli.radarWidth;


            let xMaxRadar =
                heli.x +
                heli.radarWidth;


            if (
                heli.active &&
                width / 2 >=
                    xMinRadar &&
                width / 2 <=
                    xMaxRadar
            ) {

                let perdidos =
                    Math.floor(
                        score * 0.75
                    );


                score -=
                    perdidos;


                if (
                    score < 0
                ) {

                    score = 0;

                }


                scoreEl.innerText =
                    score;


                triggerGiantAlert(
                    "🚨 ¡MULTAZO DEL JUANPRONA!\\n" +
                    "Te multan por un Juanín bajo el foco radar. -75%",
                    "#e74c3c"
                );


            } else {

                score += 2;


                scoreEl.innerText =
                    score;


                triggerGiantAlert(
                    "👶 ¡JUANÍN EXTRAÍDO!\\n" +
                    "Furtivo absoluto, +2 Puntos",
                    "#f39c12"
                );

            }


        } else {

            score++;


            scoreEl.innerText =
                score;


            triggerGiantAlert(
                "👤 ¡JUAN ADULTO CAPTURADO!\\n" +
                "+1 Punto",
                "#2ecc71"
            );

        }


        if (
            score >= 10
        ) {

            isGameOver =
                true;


            setTimeout(
                win,
                100
            );

        }


    } else if (
        obj.type ===
        TYPES.CARD
    ) {

        nPenalties++;


        let extraSeconds =
            3 + nPenalties;


        accumulatedTime +=
            extraSeconds * 1000;


        penaltyTime =
            Date.now() +
            extraSeconds * 1000;


        triggerGiantAlert(
            "🟥 ¡TARJETA ROJA!\\n+" +
            extraSeconds +
            "s de penalización",
            "#ff4444"
        );


    } else {

        triggerGiantAlert(
            "⚽ ¡PELOTA DE FÚTBOL!\\n" +
            "Limpieza marina",
            "#3498db"
        );

    }

}


// ==============================================================================
// --- VICTORIA
// ==============================================================================

function win() {

    if (
        document.fullscreenElement
    ) {

        document.exitFullscreen();

    }


    winScreen.style.display =
        'block';


    document.getElementById(
        'final-time-text'
    ).innerText =
        "¡Completado en " +
        (
            accumulatedTime /
            1000
        ).toFixed(2) +
        "s!";

}


// ==============================================================================
// --- GUARDAR RÉCORD
// ==============================================================================

document
    .getElementById(
        'save-pesca-btn'
    )
    .addEventListener(
        'click',
        () => {

            let finalTime =
                (
                    accumulatedTime /
                    1000
                ).toFixed(2);


            window.location.href =
                window.location.pathname +
                '?win=true&time=' +
                finalTime;

        }
    );


// ==============================================================================
// --- DIBUJAR
// ==============================================================================

function draw() {

    update();


    ctx.clearRect(
        0,
        0,
        width,
        height
    );


    let seaLine =
        height * 0.35;


    if (
        seaLine < 180
    ) {

        seaLine = 180;

    }


    // --------------------------------------------------------------------------
    // CIELO
    // --------------------------------------------------------------------------

    ctx.fillStyle =
        acidRainActive
            ? '#4d603a'
            : '#70b5d3';


    ctx.fillRect(
        0,
        0,
        width,
        seaLine
    );


    // --------------------------------------------------------------------------
    // MAR
    // --------------------------------------------------------------------------

    let seaGrad =
        ctx.createLinearGradient(
            0,
            seaLine,
            0,
            height
        );


    seaGrad.addColorStop(
        0,
        acidRainActive
            ? '#0e2b14'
            : '#1E90FF'
    );


    seaGrad.addColorStop(
        1,
        '#051937'
    );


    ctx.fillStyle =
        seaGrad;


    ctx.fillRect(
        0,
        seaLine,
        width,
        height - seaLine
    );


    // --------------------------------------------------------------------------
    // LLUVIA ÁCIDA
    // --------------------------------------------------------------------------

    if (
        acidRainActive
    ) {

        ctx.strokeStyle =
            'rgba(150, 240, 50, 0.4)';


        ctx.lineWidth =
            1.5;


        acidDrops.forEach(
            d => {

                ctx.beginPath();


                ctx.moveTo(
                    d.x,
                    d.y
                );


                ctx.lineTo(
                    d.x - 1,
                    d.y + 11
                );


                ctx.stroke();

            }
        );

    }


    // --------------------------------------------------------------------------
    // OLAS
    // --------------------------------------------------------------------------

    waves.forEach(
        wave => {

            ctx.strokeStyle =
                acidRainActive
                    ? 'rgba(150, 240, 50, 0.5)'
                    : 'rgba(255, 255, 255, 0.75)';


            ctx.lineWidth =
                2.5;


            ctx.beginPath();


            ctx.arc(
                wave.x,
                wave.y + 4,
                wave.size,
                Math.PI,
                0,
                false
            );


            ctx.stroke();

        }
    );


    // --------------------------------------------------------------------------
    // HELICÓPTERO
    // --------------------------------------------------------------------------

    if (
        heli.active
    ) {

        ctx.fillStyle =
            'rgba(255, 235, 59, 0.14)';


        ctx.beginPath();


        ctx.moveTo(
            heli.x,
            heli.y + 10
        );


        ctx.lineTo(
            heli.x -
                heli.radarWidth,
            seaLine
        );


        ctx.lineTo(
            heli.x +
                heli.radarWidth,
            seaLine
        );


        ctx.closePath();


        ctx.fill();


        ctx.fillStyle =
            '#1e3f20';


        ctx.fillRect(
            heli.x - 22,
            heli.y - 10,
            44,
            20
        );


        ctx.fillStyle =
            '#000';


        ctx.fillRect(
            heli.x - 32,
            heli.y - 12,
            64,
            3
        );


        ctx.font =
            "10px sans-serif";


        ctx.fillStyle =
            '#fff';


        ctx.fillText(
            "🚁 JUANPRONA",
            heli.x - 35,
            heli.y - 18
        );

    }


    // --------------------------------------------------------------------------
    // PATERA
    // --------------------------------------------------------------------------

    if (
        patera.active
    ) {

        ctx.fillStyle =
            (
                Date.now() <
                patera.hitFlash
            )
                ? '#00e5ff'
                : '#7e5129';


        ctx.beginPath();


        ctx.moveTo(
            patera.x - 22,
            patera.y
        );


        ctx.lineTo(
            patera.x + 22,
            patera.y
        );


        ctx.lineTo(
            patera.x + 14,
            patera.y + 14
        );


        ctx.lineTo(
            patera.x - 14,
            patera.y + 14
        );


        ctx.closePath();


        ctx.fill();

    }


    // --------------------------------------------------------------------------
    // OBJETOS
    // --------------------------------------------------------------------------

    objects.forEach(
        obj => {

            let renderSize =
                obj.discovered
                    ? (
                        obj.isJuanin
                            ? 15
                            : 28
                    )
                    : 28;


            let lifeLeft =
                obj.deathTime -
                Date.now();


            ctx.beginPath();


            ctx.arc(
                obj.x,
                obj.y,
                renderSize,
                0,
                Math.PI * 2
            );


            if (
                lifeLeft < 5000 &&
                Math.floor(
                    Date.now() /
                    250
                ) % 2 === 0
            ) {

                ctx.fillStyle =
                    'rgba(110, 110, 110, 0.6)';

            } else {

                ctx.fillStyle =
                    obj.discovered
                        ? 'rgba(30, 85, 145, 0.9)'
                        : 'rgba(24, 48, 89, 0.95)';

            }


            ctx.fill();


            ctx.strokeStyle =
                (
                    obj.discovered &&
                    obj.isJuanin
                )
                    ? '#ffeb3b'
                    : 'rgba(255,255,255,0.4)';


            ctx.lineWidth =
                1.5;


            ctx.stroke();


            if (
                obj.discovered &&
                imageLoaded &&
                obj.type === TYPES.JUAN
            ) {

                ctx.save();


                ctx.beginPath();


                ctx.arc(
                    obj.x,
                    obj.y,
                    renderSize - 2,
                    0,
                    Math.PI * 2
                );


                ctx.clip();


                let dim =
                    obj.isJuanin
                        ? 30
                        : 54;


                ctx.drawImage(
                    juanImg,
                    obj.x - dim / 2,
                    obj.y - dim / 2,
                    dim,
                    dim
                );


                ctx.restore();


            } else if (
                obj.discovered
            ) {

                ctx.fillStyle =
                    '#fff';


                ctx.font =
                    "bold 16px sans-serif";


                ctx.fillText(
                    obj.type === TYPES.CARD
                        ? '🟥'
                        : '⚽',
                    obj.x - 8,
                    obj.y + 6
                );


            } else {

                ctx.fillStyle =
                    '#fff';


                ctx.font =
                    "bold 15px sans-serif";


                ctx.fillText(
                    "❓",
                    obj.x - 6,
                    obj.y + 5
                );

            }

        }
    );


    // --------------------------------------------------------------------------
    // MUELLE
    // --------------------------------------------------------------------------

    ctx.fillStyle =
        '#5c3a21';


    ctx.fillRect(
        width / 2 - 35,
        seaLine - 15,
        70,
        15
    );


    if (
        imageLoaded
    ) {

        ctx.drawImage(
            juanImg,
            width / 2 - 22,
            seaLine - 72,
            44,
            60
        );

    }


    // --------------------------------------------------------------------------
    // RADAR / CAÑA
    // --------------------------------------------------------------------------

    let radarRadius =
        55;


    let radarX =
        width / 2;


    let radarY =
        seaLine - 15;


    ctx.beginPath();


    if (
        patera.active
    ) {

        if (
            patera.direction === 'left'
        ) {

            ctx.arc(
                radarX,
                radarY,
                radarRadius,
                Math.PI,
                Math.PI * 1.5,
                false
            );

        } else {

            ctx.arc(
                radarX,
                radarY,
                radarRadius,
                Math.PI * 1.5,
                Math.PI * 2,
                false
            );

        }

    } else {

        ctx.arc(
            radarX,
            radarY,
            radarRadius,
            0,
            Math.PI,
            false
        );

    }


    ctx.strokeStyle =
        'rgba(255,235,59,0.6)';


    ctx.lineWidth =
        2.5;


    ctx.stroke();


    // --------------------------------------------------------------------------
    // PUNTO DEL ÁNGULO
    // --------------------------------------------------------------------------

    let ballX =
        radarX +
        Math.cos(
            angleParam
        ) *
        radarRadius;


    let ballY =
        radarY +
        Math.sin(
            angleParam
        ) *
        radarRadius;


    ctx.beginPath();


    ctx.moveTo(
        radarX,
        radarY
    );


    ctx.lineTo(
        ballX,
        ballY
    );


    ctx.strokeStyle =
        '#ffeb3b';


    ctx.lineWidth =
        2.5;


    ctx.stroke();


    ctx.beginPath();


    ctx.arc(
        ballX,
        ballY,
        6,
        0,
        Math.PI * 2
    );


    ctx.fillStyle =
        inputState === 'angle'
            ? '#ffeb3b'
            : '#2ecc71';


    ctx.fill();


    // --------------------------------------------------------------------------
    // BARRA DE FUERZA
    // --------------------------------------------------------------------------

    if (
        inputState === 'force'
    ) {

        ctx.fillStyle =
            '#e74c3c';


        ctx.fillRect(
            width / 2 - 50,
            seaLine - 110,
            chargeForce,
            10
        );


        ctx.strokeStyle =
            '#fff';


        ctx.strokeRect(
            width / 2 - 50,
            seaLine - 110,
            100,
            10
        );

    }


    // --------------------------------------------------------------------------
    // HILO / ANZUELO
    // --------------------------------------------------------------------------

    if (
        inputState === 'launching' ||
        inputState === 'returning'
    ) {

        ctx.beginPath();


        ctx.moveTo(
            width / 2,
            seaLine - 15
        );


        ctx.lineTo(
            hook.x,
            hook.y
        );


        ctx.strokeStyle =
            '#ffffff';


        ctx.lineWidth =
            2;


        ctx.stroke();


        ctx.beginPath();


        ctx.arc(
            hook.x,
            hook.y,
            6,
            0,
            Math.PI * 2
        );


        ctx.fillStyle =
            '#e74c3c';


        ctx.fill();

    }


    requestAnimationFrame(
        draw
    );

}


// ==============================================================================
// --- INPUT
// ==============================================================================

function handleActionStart() {

    if (
        isGameOver ||
        Date.now() < penaltyTime ||
        Date.now() < globalPauseUntil
    ) {

        return;

    }


    if (
        inputState === 'angle'
    ) {

        fixedAngle =
            angleParam;


        inputState =
            'force';


        chargeForce =
            0;

    }

}


function handleActionEnd() {

    if (
        inputState !== 'force'
    ) {

        return;

    }


    inputState =
        'launching';


    let seaLineBound =
        height * 0.35;


    if (
        seaLineBound < 180
    ) {

        seaLineBound =
            180;

    }


    if (
        fixedAngle >= Math.PI &&
        patera.active
    ) {

        hook.mode =
            'parabolic';


        let initialVelocity =
            5 +
            (
                chargeForce /
                100
            ) * 16;


        hook.vx =
            Math.cos(
                fixedAngle
            ) *
            initialVelocity;


        hook.vy =
            Math.sin(
                fixedAngle
            ) *
            initialVelocity;


    } else {

        hook.mode =
            'straight';


        let maxReach =
            Math.sqrt(
                (
                    width / 2
                ) ** 2 +
                height ** 2
            ) * 0.95;


        let currentReach =
            (
                chargeForce /
                100
            ) *
            maxReach;


        hook.targetX =
            (
                width / 2
            ) +
            Math.cos(
                fixedAngle
            ) *
            currentReach;


        hook.targetY =
            seaLineBound +
            Math.abs(
                Math.sin(
                    fixedAngle
                ) *
                currentReach
            );


        if (
            hook.targetX < 0
        ) {

            hook.targetX =
                15;

        }


        if (
            hook.targetX > width
        ) {

            hook.targetX =
                width - 15;

        }


        if (
            hook.targetY > height
        ) {

            hook.targetY =
                height - 20;

        }

    }


    hook.x =
        width / 2;


    hook.y =
        seaLineBound - 15;

}


// ==============================================================================
// --- EVENTOS RATÓN
// ==============================================================================

container.addEventListener(
    'mousedown',
    (e) => {

        if (
            e.target.id !==
            'fullscreen-btn'
        ) {

            handleActionStart();

        }

    }
);


window.addEventListener(
    'mouseup',
    handleActionEnd
);


// ==============================================================================
// --- EVENTOS TÁCTILES
// ==============================================================================

container.addEventListener(
    'touchstart',
    (e) => {

        if (
            e.target.id !==
            'fullscreen-btn'
        ) {

            handleActionStart();

        }

    },
    {
        passive: true
    }
);


window.addEventListener(
    'touchend',
    handleActionEnd
);


// ==============================================================================
// --- ARRANQUE
// ==============================================================================

draw();


</script>

</body>

</html>
"""


# ==============================================================================
# --- INSERTAR IMAGEN
# ==============================================================================
html_pesca = html_pesca_template.replace(
    "{{JUAN_IMAGE_BASE64}}",
    img_base64_pesca
)


# ==============================================================================
# --- MOSTRAR JUEGO
# ==============================================================================
components.html(
    html_pesca,
    height=520
)



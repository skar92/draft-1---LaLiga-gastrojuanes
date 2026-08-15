import base64
from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

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

# --- RUTAS DE LOS ESCUDOS Y JUGADOR EN LA CARPETA /img ---
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
# 📝 ÚNICO SITIO DONDE SE ACTUALIZAN LOS DATOS DE LA JORNADA
# ==============================================================================

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

puntos_apuesta = {
    "Sierra": 0, "Joaquín": 0, "Ejkar": 0, "Vecina": 0,
    "Telenti": 0, "Miguel Ángel": 0, "Mírete": 0, "Juan": 0,
}

# ==============================================================================

equipo_a_jugador = {}
for jugador, lista_eqs in asig_equipos.items():
    for eq in lista_eqs:
        equipo_a_jugador[eq] = jugador

# --- CONSTRUCCIÓN DE LA TABLA DE EQUIPOS ---
filas_equipos = []
for eq, st_eq in stats_equipos.items():
    g, e, p = st_eq["G"], st_eq["E"], st_eq["P"]
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
        "PJ": jugados, "G": g, "E": e, "P": p, "Puntos": puntos,
    })

df_equipos = pd.DataFrame(filas_equipos).sort_values(by="Puntos", ascending=False).reset_index(drop=True)

# --- CONSTRUCCIÓN DE LA TABLA DE GOLEADORES (SIN COLUMNA EQUIPO) ---
filas_goleadores = []
for gol, info in porra_goleadores.items():
    eq = info["Equipo"]
    st_eq = stats_equipos.get(eq, {"G":0, "E":0, "P":0})
    pj_equipo = st_eq["G"] + st_eq["E"] + st_eq["P"]
        
    filas_goleadores.append({
        "Goleador": gol,
        "Jugador": info["Jugador"],
        "PJ": pj_equipo,
        "Goles": info["Goles"]
    })

df_goleadores = pd.DataFrame(filas_goleadores)
if not df_goleadores.empty:
    df_goleadores = df_goleadores.sort_values(by="Goles", ascending=False).reset_index(drop=True)

# --- CLASIFICACIÓN GENERAL ---
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

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .dataframe-container { overflow-x: auto; margin-bottom: 20px; }
    .styled-table {
        border-collapse: collapse; width: 100%; font-size: 0.95em; font-family: sans-serif; text-align: left;
    }
    .styled-table thead tr { background-color: #2b2b2b; color: #ffffff; text-align: left; }
    .styled-table th, .styled-table td { padding: 10px 14px; border-bottom: 1px solid #444444; }
    .styled-table tbody tr:nth-of-type(even) { background-color: rgba(255, 255, 255, 0.03); }
</style>
""", unsafe_allow_html=True)

# --- RENDERIZADO EN LA WEB ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚽ Clasificación de Equipos")
    df_mostrar_eq = df_equipos[["Equipo", "Jugador", "PJ", "G", "E", "P", "Puntos"]]
    st.markdown(f'<div class="dataframe-container">{df_mostrar_eq.to_html(escape=False, index=False, classes="styled-table")}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("🎯 Tabla de Goleadores")
    if not df_goleadores.empty:
        df_mostrar_gol = df_goleadores[["Goleador", "Jugador", "PJ", "Goles"]]
        st.markdown(f'<div class="dataframe-container">{df_mostrar_gol.to_html(escape=False, index=False, classes="styled-table")}</div>', unsafe_allow_html=True)
    else:
        st.info("No hay goleadores registrados todavía.")

st.markdown("---")

st.subheader("🏆 Clasificación General (Participantes)")
df_mostrar_gen = df_general[["Jugador", "Puntos de Equipos", "Goles", "Total"]]
st.markdown(f'<div class="dataframe-container">{df_mostrar_gen.to_html(escape=False, index=False, classes="styled-table")}</div>', unsafe_allow_html=True)

st.markdown("---")

st.subheader("📊 Gráfica de Puntos Totales")
fig_barras = px.bar(df_general, x="Jugador", y="Total_Num", color="Jugador", text_auto=True)
max_pts = df_general["Total_Num"].max()
fig_barras.update_layout(showlegend=False, xaxis_title="Participante", yaxis_title="Puntos Totales", yaxis=dict(range=[0, max_pts + 5 if max_pts > 0 else 10]))
st.plotly_chart(fig_barras, use_container_width=True)













# ==============================================================================
# --- 🎣 MINIJUEGO: LA PESCA DE JUAN ---
# ==============================================================================
st.markdown("---")
st.subheader("🎣 Minijuego: La Pesca de Juan")

# Cargamos explícitamente la imagen desde img/jugador.png
img_base64_pesca = obtener_imagen_base64("img/jugador.png")

html_pesca_template = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<style>
    body { margin: 0; padding: 0; overflow: hidden; font-family: 'Segoe UI', sans-serif; user-select: none; touch-action: none; background: #87CEEB; }
    #game-container { position: relative; width: 100%; max-width: 800px; margin: 0 auto; background: #000; }
    #game-canvas { background: linear-gradient(to bottom, #87CEEB 0%, #87CEEB 35%, #1E90FF 35%, #051937 100%); display: block; width: 100%; height: 500px; }
    #ui { position: absolute; top: 10px; left: 10px; color: white; text-shadow: 1px 1px 2px black; pointer-events: none; font-weight: bold; font-size: 13px; z-index: 10; }
    #fullscreen-btn { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #ffeb3b; border: 2px solid #ffeb3b; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; cursor: pointer; z-index: 50; display: block; }
    #giant-alert { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 30px; font-weight: bold; text-align: center; background: rgba(0, 0, 0, 0.95); padding: 35px; border-radius: 20px; box-shadow: 0 0 30px rgba(255,255,255,0.4); display: none; z-index: 40; width: 85%; max-width: 600px; box-sizing: border-box; border: 4px solid #ffeb3b; line-height: 1.4; }
    #penalty-timer { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #ff4444; font-size: 35px; font-weight: bold; display: none; text-align: center; background: rgba(0,0,0,0.85); padding: 20px; border-radius: 15px; z-index: 20; }
    #win-screen { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 25px; border-radius: 15px; text-align: center; display: none; box-shadow: 0 0 25px rgba(0,0,0,0.5); z-index: 30; }
    .btn { background: #2ecc71; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 12px; }
</style>
</head>
<body>

<div id="game-container">
    <button id="fullscreen-btn">📱 FULLSCREEN</button>
    <div id="ui">
        <div style="color: #ffeb3b; font-size: 12px; margin-bottom: 4px; background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 4px;">🎮 <b>Muelle de Juan</b></div>
        <div>👤 Puntos: <span id="score">0</span> / 10 <span id="acid-indicator" style="color:#2ecc71; font-weight:bold; display:none;">⚠️ LLUVIA ÁCIDA</span></div>
        <div>⏱️ Tiempo: <span id="clock">0.0</span>s</div>
        <div id="instruction-text" style="color: #ffeb3b; margin-top: 2px;">Toca para pescar</div>
    </div>
    <div id="giant-alert"></div>
    <div id="penalty-timer">🟥 PENALIZACIÓN<br><span id="p-seconds">5</span>s</div>
    <div id="win-screen">
        <h2>🏆 ¡DESAFÍO COMPLETADO!</h2>
        <p id="final-time-text"></p>
        <button id="save-pesca-btn" class="btn">💾 Registrar Récord</button>
    </div>
    <canvas id="game-canvas"></canvas>
</div>

<script>
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');
    const scoreEl = document.getElementById('score');
    const clockEl = document.getElementById('clock');
    const winScreen = document.getElementById('win-screen');
    const penaltyEl = document.getElementById('penalty-timer');
    const pSecondsEl = document.getElementById('p-seconds');
    const giantAlert = document.getElementById('giant-alert');
    const container = document.getElementById('game-container');
    const acidIndicator = document.getElementById('acid-indicator');

    // Carga separada de la imagen para asegurar el renderizado
    const pescadorImg = new Image();
    pescadorImg.src = "data:image/png;base64,{{JUAN_IMAGE_BASE64}}";
    
    let width = 800; let height = 500;
    let score = 0; let accumulatedTime = 0; let lastTimeCheck = Date.now(); 
    let isGameOver = false; let penaltyTime = 0; let inputState = 'angle';
    let angleParam = 0.5; let angleSpeed = 0.06; let fixedAngle = 0; let chargeForce = 0;
    let objects = []; let hook = { x: 0, y: 0, mode: 'straight' };

    function resizeGame() {
        width = container.offsetWidth || 800;
        canvas.width = width;
        canvas.height = height;
    }
    window.addEventListener('resize', resizeGame);
    resizeGame();

    function triggerGiantAlert(message, borderColor = '#ffeb3b') {
        giantAlert.innerHTML = message.replace(/\\n/g, "<br>");
        giantAlert.style.borderColor = borderColor;
        giantAlert.style.display = 'block';
        setTimeout(() => { giantAlert.style.display = 'none'; }, 2000);
    }

    function spawnObject() {
        if (objects.length >= 10) return;
        objects.push({
            x: Math.random() * width, y: 150 + Math.random() * 300,
            vx: (Math.random() - 0.5) * 4,
            id: Math.random()
        });
    }
    for(let i=0; i<8; i++) spawnObject();

    function update() {
        if (isGameOver) return;
        const now = Date.now();
        accumulatedTime += (now - lastTimeCheck);
        lastTimeCheck = now;
        clockEl.innerText = (accumulatedTime / 1000).toFixed(1);

        // Lógica de ángulo
        if (inputState === 'angle') {
            angleParam += angleSpeed;
            if (angleParam > Math.PI || angleParam < 0) angleSpeed *= -1;
        } else if (inputState === 'force') {
            chargeForce = Math.min(chargeForce + 3, 100);
        }
    }

    function draw() {
        update();
        ctx.clearRect(0, 0, width, height);
        
        // Fondo
        let seaLine = 180;
        ctx.fillStyle = '#70b5d3'; ctx.fillRect(0, 0, width, seaLine);
        ctx.fillStyle = '#1E90FF'; ctx.fillRect(0, seaLine, width, height - seaLine);

        // Dibujo Pescador
        ctx.fillStyle = '#5c3a21'; 
        ctx.fillRect(width/2 - 35, seaLine - 15, 70, 15);
        if (pescadorImg.complete) {
            ctx.drawImage(pescadorImg, width/2 - 25, seaLine - 75, 50, 60);
        }

        // Dibujo Peces
        objects.forEach(o => {
            ctx.beginPath(); ctx.arc(o.x, o.y, 20, 0, Math.PI*2);
            ctx.fillStyle = 'rgba(255,255,255,0.8)'; ctx.fill();
        });

        requestAnimationFrame(draw);
    }

    container.addEventListener('mousedown', () => { if(inputState === 'angle') { inputState = 'force'; chargeForce = 0; } });
    container.addEventListener('mouseup', () => { if(inputState === 'force') inputState = 'angle'; });
    
    draw();
</script>
</body>
</html>
"""

html_pesca = html_pesca_template.replace("{{JUAN_IMAGE_BASE64}}", img_base64_pesca)
components.html(html_pesca, height=520)

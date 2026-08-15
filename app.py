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

img_base64_pesca = obtener_imagen_base64("img/athletic.png") # O la ruta de la imagen que uses para Juan (ej: primer escudo o archivo general)
# Si tienes una imagen específica para Juan en base64, reemplaza esta variable o usa directamente tu `img_base64` anterior.
img_base64_pesca = locals().get('img_base64', '') 

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
    
    #fullscreen-btn {
        position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7);
        color: #ffeb3b; border: 2px solid #ffeb3b; padding: 6px 12px; border-radius: 20px;
        font-weight: bold; font-size: 11px; cursor: pointer; z-index: 50; display: block;
    }

    #giant-alert { 
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
        color: white; font-size: 30px; font-weight: bold; text-align: center; 
        background: rgba(0, 0, 0, 0.95); padding: 35px; border-radius: 20px; 
        box-shadow: 0 0 30px rgba(255,255,255,0.4); display: none; z-index: 40; width: 85%; max-width: 600px;
        box-sizing: border-box; border: 4px solid #ffeb3b; line-height: 1.4;
    }
    
    #penalty-timer { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #ff4444; font-size: 35px; font-weight: bold; display: none; text-align: center; background: rgba(0,0,0,0.85); padding: 20px; border-radius: 15px; z-index: 20; }
    #win-screen { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 25px; border-radius: 15px; text-align: center; display: none; box-shadow: 0 0 25px rgba(0,0,0,0.5); z-index: 30; }
    .btn { background: #2ecc71; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 12px; }
</style>
</head>
<body>

<div id="game-container">
    <button id="fullscreen-btn">📱 FULLSCREEN</button>

    <div id="ui">
        <div style="color: #ffeb3b; font-size: 12px; margin-bottom: 4px; background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 4px;">
            🎮 <b>Muelle de Juan:</b> Pesca 10 Juanes. Evita tarjetas rojas. Usa las olas para frenar la patera. Ojo al radar del Juanprona.
        </div>
        <div>👤 Puntos Juan: <span id="score">0</span> / 10 <span id="acid-indicator" style="color:#2ecc71; font-weight:bold; display:none;">⚠️ LLUVIA ÁCIDA</span></div>
        <div>⏱️ Tiempo: <span id="clock">0.0</span>s</div>
        <div>🐟 Bultos: <span id="pop-count">0</span> / 20</div>
        <div id="instruction-text" style="color: #ffeb3b; margin-top: 2px;">Toca para fijar el ÁNGULO</div>
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
    const popEl = document.getElementById('pop-count');
    const winScreen = document.getElementById('win-screen');
    const penaltyEl = document.getElementById('penalty-timer');
    const pSecondsEl = document.getElementById('p-seconds');
    const giantAlert = document.getElementById('giant-alert');
    const fsBtn = document.getElementById('fullscreen-btn');
    const container = document.getElementById('game-container');
    const acidIndicator = document.getElementById('acid-indicator');

    let width = 800; let height = 500;
    
    function resizeGame() {
        if (document.fullscreenElement) {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.style.height = height + "px";
        } else {
            width = container.offsetWidth || 800;
            height = 500;
            canvas.style.height = "500px";
        }
        canvas.width = width;
        canvas.height = height;
    }
    window.addEventListener('resize', resizeGame);
    setTimeout(resizeGame, 150);

    fsBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        try {
            if (!document.fullscreenElement) {
                if (container.requestFullscreen) await container.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        } catch (err) { console.error(err); }
    });

    const juanImg = new Image(); let imageLoaded = false;
    juanImg.src = "data:image/png;base64,{{JUAN_IMAGE_BASE64}}";
    juanImg.onload = () => imageLoaded = true;

    let score = 0; let accumulatedTime = 0; let lastTimeCheck = Date.now(); let isGameOver = false;
    let penaltyTime = 0; let nPenalties = 0;
    let globalPauseUntil = 0;

    let inputState = 'angle'; 
    let angleParam = 0.5; 
    let angleSpeed = 0.035; 
    let fixedAngle = 0; let chargeForce = 0;
    
    let heli = { x: 100, y: 35, vx: 3, nextChange: 0, radarWidth: 90, active: true, reactiveTime: 0 };
    
    let patera = { 
        active: false, x: 0, y: 0, startX: 0, baseVx: 0, maxVx: 1.2,
        spawnTimer: Date.now() + 15000, direction: 'right',
        hitFlash: 0 
    };
    let waves = []; 
    let nextWaveSpawn = 0;

    let acidRainActive = false;
    let nextAcidEvent = Date.now() + 25000; 
    let acidEndTime = 0;
    let acidDrops = [];

    function triggerGiantAlert(message, borderColor = '#ffeb3b') {
        giantAlert.innerHTML = message.replace(/\\n/g, "<br>");
        giantAlert.style.borderColor = borderColor;
        giantAlert.style.display = 'block';
        globalPauseUntil = Date.now() + 2500; 
        setTimeout(() => { giantAlert.style.display = 'none'; }, 2500);
    }

    const TYPES = { JUAN: 'juan', BALL: 'ball', CARD: 'card' };
    let objects = [];

    function countType(t) { return objects.filter(o => o.type === t).length; }
    function countJuanines() { return objects.filter(o => o.type === TYPES.JUAN && o.isJuanin).length; }

    function spawnObject() {
        if (objects.length >= 20) return;
        
        let totalJuanesTarget = Math.round(objects.length * 0.30);
        let currentJuanes = countType(TYPES.JUAN);
        
        let type;
        if (currentJuanes < totalJuanesTarget || (objects.length === 0 && Math.random() < 0.30)) {
            type = TYPES.JUAN;
        } else {
            type = Math.random() < 0.5 ? TYPES.BALL : TYPES.CARD;
        }

        let assignJuanin = false;
        if (type === TYPES.JUAN) {
            let currentJuaninesCount = countJuanines();
            if (currentJuaninesCount < Math.round((currentJuanes + 1) * 0.70)) {
                assignJuanin = true;
            }
        }

        let isDiscovered = Math.random() >= 0.50; 
        let maxLifeTime = 25000 + Math.random() * 15000;
        let randomDepthPct = 0.45 + Math.random() * 0.45;

        objects.push({
            id: Math.random().toString(36),
            x: Math.random() * width,
            depthPercent: randomDepthPct,
            y: 0, type: type, isJuanin: assignJuanin,
            vx: (Math.random() - 0.5) * (type === TYPES.JUAN ? 8.0 : 4.5), ax: 0,
            depthSpeed: 0.02 + Math.random() * 0.03, depthAmp: 8 + Math.random() * 18, phase: Math.random() * Math.PI * 2,
            spawnTime: Date.now(), discovered: isDiscovered,
            lastDirectionChange: Date.now(), changeInterval: 300 + Math.random() * 600,
            deathTime: Date.now() + maxLifeTime
        });
    }

    for(let i=12; i>0; i--) spawnObject();
    let nextSpawnTime = Date.now() + 4000;

    let hook = { x: 0, y: 0, vx: 0, vy: 0, mode: 'straight', targetX: 0, targetY: 0 };

    function triggerAcidRainStrike() {
        acidRainActive = true;
        acidEndTime = Date.now() + 6000; 
        acidIndicator.style.display = 'inline';
        
        if (objects.length > 0) {
            let countToKill = Math.floor(objects.length * 0.5);
            objects.sort(() => Math.random() - 0.5);
            objects.splice(0, countToKill);
        }
        
        triggerGiantAlert("🌧️ ¡LLUVIA ÁCIDA COLOSAL!\\nEl 50% de los bultos marinos han sido disueltos.", "#2ecc71");
    }

    function update() {
        const now = Date.now();
        let deltaTime = now - lastTimeCheck;
        lastTimeCheck = now;

        if (isGameOver) return;

        let seaTopBoundary = height * 0.35; if(seaTopBoundary < 180) seaTopBoundary = 180;

        if (!acidRainActive && now > nextAcidEvent) {
            triggerAcidRainStrike();
        }
        if (acidRainActive && now > acidEndTime) {
            acidRainActive = false;
            acidIndicator.style.display = 'none';
            nextAcidEvent = now + 25000 + Math.random() * 15000;
        }
        if (acidRainActive && Math.random() < 0.5) {
            acidDrops.push({ x: Math.random() * width, y: 0, speed: 7 + Math.random() * 5 });
        }
        for (let d = acidDrops.length - 1; d >= 0; d--) {
            acidDrops[d].y += acidDrops[d].speed;
            if (acidDrops[d].y > height) acidDrops.splice(d, 1);
        }

        if (!heli.active && now > heli.reactiveTime) {
            heli.active = true;
            heli.x = 100;
        }

        if (heli.active) {
            if (now > heli.nextChange) {
                heli.vx = (Math.random() > 0.5 ? 1 : -1) * (2 + Math.random() * 5);
                heli.nextChange = now + 600 + Math.random() * 1200;
            }
            heli.x += heli.vx;
            if (heli.x < 40) { heli.x = 40; heli.vx *= -1; }
            if (heli.x > width - 40) { heli.x = width - 40; heli.vx *= -1; }
        }

        if (!patera.active && now > patera.spawnTimer) {
            patera.active = true;
            patera.y = seaTopBoundary - 8;
            waves = []; 
            nextWaveSpawn = now + 1000; 
            
            if (Math.random() > 0.5) {
                patera.x = -45; patera.startX = -45; patera.baseVx = 0.55; 
                patera.direction = 'left'; 
                angleParam = Math.PI * 1.2; 
            } else {
                patera.x = width + 45; patera.startX = width + 45; patera.baseVx = -0.55; 
                patera.direction = 'right'; 
                angleParam = Math.PI * 1.7; 
            }
            triggerGiantAlert("⛵ ¡PATERA DETECTADA!\\nVelocidad progresiva suave hacia el centro. ¡Frénala!", "#f1c40f");
        }

        if (patera.active && now >= globalPauseUntil) {
            let center = width / 2;

            if (now > nextWaveSpawn) {
                waves.push({ x: center, y: seaTopBoundary, vx: patera.direction === 'left' ? -1.4 : 1.4, size: 7 });
                nextWaveSpawn = now + 5800; 
            }

            for (let w = waves.length - 1; w >= 0; w--) {
                let wave = waves[w]; wave.x += wave.vx; wave.size += 0.04; 
                let distanceToPatera = Math.abs(wave.x - patera.x);
                if (distanceToPatera < 15) {
                    let fixedPush = 25; 
                    if (patera.direction === 'left') patera.x = Math.max(patera.startX, patera.x - fixedPush);
                    else patera.x = Math.min(patera.startX, patera.x + fixedPush);
                    patera.hitFlash = now + 250; waves.splice(w, 1); continue;
                }
                if (wave.x < -60 || wave.x > width + 60) waves.splice(w, 1);
            }

            let distanceToCenter = Math.abs(center - patera.x);
            let maxDistance = Math.abs(center - patera.startX);
            let progress = 1 - (distanceToCenter / maxDistance); 
            
            let currentSpeed = patera.baseVx + (patera.maxVx * progress * Math.sign(patera.baseVx));
            patera.x += currentSpeed;
            
            if ((patera.baseVx > 0 && patera.x >= center) || (patera.baseVx < 0 && patera.x <= center)) {
                patera.active = false; waves = []; patera.spawnTimer = now + 45000; score = 0; scoreEl.innerText = score; 
                triggerGiantAlert("☠️ ¡LA PATERA ASALTÓ EL MUELLE!\\nHas perdido todos tus JUANES acumulados", "#e74c3c");
            }
        } else { waves = []; }

        if (now < globalPauseUntil) return; 

        if (penaltyTime > now) {
            penaltyEl.style.display = 'block'; pSecondsEl.innerText = Math.ceil((penaltyTime - now)/1000);
            inputState = 'angle'; return;
        } else { penaltyEl.style.display = 'none'; }
        
        accumulatedTime += deltaTime;
        clockEl.innerText = (accumulatedTime / 1000).toFixed(1);
        popEl.innerText = objects.length;

        if (inputState === 'angle') {
            angleParam += angleSpeed;
            if (patera.active) {
                if (patera.direction === 'left') {
                    let minLimit = Math.PI; let maxLimit = Math.PI * 1.5;
                    if (angleParam > maxLimit) { angleParam = maxLimit; angleSpeed *= -1; }
                    if (angleParam < minLimit) { angleParam = minLimit; angleSpeed *= -1; }
                } else {
                    let minLimit = Math.PI * 1.5; let maxLimit = Math.PI * 2;
                    if (angleParam > maxLimit) { angleParam = maxLimit; angleSpeed *= -1; }
                    if (angleParam < minLimit) { angleParam = minLimit; angleSpeed *= -1; }
                }
            } else {
                if (angleParam > Math.PI) { angleParam = Math.PI; angleSpeed *= -1; }
                if (angleParam < 0) { angleParam = 0; angleSpeed *= -1; }
            }
        }
        
        if (inputState === 'force') chargeForce = Math.min(chargeForce + 2.8, 100);

        if (now > nextSpawnTime) {
            if(objects.length < 20) spawnObject();
            nextSpawnTime = now + 3500;
        }

        let totalJuanesTarget = Math.round(objects.length * 0.30);
        let currentJuanes = countType(TYPES.JUAN);
        
        if (currentJuanes < totalJuanesTarget && objects.length > 0) {
            for (let o of objects) {
                if (o.type !== TYPES.JUAN) {
                    o.type = TYPES.JUAN;
                    currentJuanes++;
                    if (currentJuanes >= totalJuanesTarget) break;
                }
            }
        }
        
        let currentJuanesList = objects.filter(o => o.type === TYPES.JUAN);
        let expectedJuanines = Math.round(currentJuanesList.length * 0.70);
        let actualJuanines = countJuanines();

        if (actualJuanines < expectedJuanines) {
            for (let j of currentJuanesList) {
                if (!j.isJuanin) {
                    j.isJuanin = true;
                    actualJuanines++;
                    if (actualJuanines >= expectedJuanines) break;
                }
            }
        } else if (actualJuanines > expectedJuanines) {
            for (let j of currentJuanesList) {
                if (j.isJuanin) {
                    j.isJuanin = false;
                    actualJuanines--;
                    if (actualJuanines <= expectedJuanines) break;
                }
            }
        }

        let totalDiscovered = objects.filter(o => o.discovered).length;
        let minimumRequired = Math.ceil(objects.length * 0.50);

        if (totalDiscovered < minimumRequired) {
            for (let o of objects) {
                if (!o.discovered) {
                    o.discovered = true;
                    totalDiscovered++;
                    if (totalDiscovered >= minimumRequired) break;
                }
            }
        }

        for (let i = objects.length - 1; i >= 0; i--) {
            let obj = objects[i];
            obj.x += obj.vx;
            if (obj.x < 0 || obj.x > width) obj.vx *= -1;
            
            let calculatedBaseY = height * obj.depthPercent;
            obj.phase += obj.depthSpeed; 
            obj.y = calculatedBaseY + Math.sin(obj.phase) * obj.depthAmp;

            if (now > obj.deathTime) {
                objects.splice(i, 1);
                spawnObject();
            }
        }

        if (inputState === 'launching') {
            if (hook.mode === 'parabolic') {
                hook.x += hook.vx; hook.vy += 0.42; hook.y += hook.vy;
                if (patera.active && Math.abs(hook.x - patera.x) < 28 && Math.abs(hook.y - patera.y) < 22) {
                    processPateraCatch(); return;
                }
                if (hook.y >= seaTopBoundary) {
                    hook.mode = 'straight'; hook.targetX = hook.x + hook.vx * 5; hook.targetY = height - 30;
                }
                if (hook.x < 0 || hook.x > width || hook.y > height) inputState = 'returning';
            } else {
                let dx = hook.targetX - hook.x; let dy = hook.targetY - hook.y; let dist = Math.sqrt(dx*dx + dy*dy);
                
                // Comprobación de colisión en tiempo real durante el trayecto (atraviesa / intercepta)
                let targetHit = null; let hitIndex = -1;
                for(let i=0; i<objects.length; i++) {
                    let o = objects[i]; let activeSize = o.discovered ? (o.isJuanin ? 15 : 28) : 28;
                    if (Math.sqrt((hook.x - o.x)**2 + (hook.y - o.y)**2) < activeSize) {
                        targetHit = o; hitIndex = i; break;
                    }
                }

                if (targetHit) {
                    processCatch(targetHit, hitIndex);
                } else if (dist > 18) {
                    hook.x += (dx / dist) * 18; hook.y += (dy / dist) * 18;
                } else {
                    inputState = 'returning';
                }
            }
        } else if (inputState === 'returning') {
            let dx = (width/2) - hook.x; let dy = (seaTopBoundary - 15) - hook.y; let dist = Math.sqrt(dx*dx + dy*dy);
            if (dist > 25) { hook.x += (dx / dist) * 25; hook.y += (dy / dist) * 25; } 
            else { inputState = 'angle'; if (angleParam > Math.PI) angleParam = (patera.direction === 'left') ? Math.PI * 1.2 : Math.PI * 1.7; }
        }
    }

    function processPateraCatch() {
        patera.active = false; 
        waves = []; 
        patera.spawnTimer = Date.now() + 60000; 
        
        heli.active = false; 
        heli.reactiveTime = Date.now() + 60000; 
        
        inputState = 'returning';
        
        score += 2; 
        scoreEl.innerText = score;
        
        triggerGiantAlert("🚔 ¡EL JUANPRONA SE LLEVA LA PATERA!\\nTramitando la detención en comisaría. ¡Suman +2 PUNTOS fijos! 60s de tregua.", "#3498db");
        if (score >= 10) { isGameOver = true; setTimeout(win, 100); }
    }

    function processCatch(obj, index) {
        objects.splice(index, 1); spawnObject(); inputState = 'returning';
        if (obj.type === TYPES.JUAN) {
            if (obj.isJuanin) {
                let xMinRadar = heli.x - heli.radarWidth; let xMaxRadar = heli.x + heli.radarWidth;
                if (heli.active && width/2 >= xMinRadar && width/2 <= xMaxRadar) {
                    let perdidos = Math.floor(score * 0.75); score -= perdidos; if (score < 0) score = 0;
                    scoreEl.innerText = score;
                    triggerGiantAlert("🚨 ¡MULTAZO DEL JUANPRONA!\\nTe multan por un Juanín bajo el foco radar. -75%", "#e74c3c");
                } else {
                    score += 2; scoreEl.innerText = score;
                    triggerGiantAlert("👶 ¡JUANÍN EXTRAÍDO!\\nFurtivo absoluto, +2 Puntos", "#f39c12");
                }
            } else {
                score++; scoreEl.innerText = score;
                triggerGiantAlert("👤 ¡JUAN ADULTO CAPTURADO!\\n+1 Punto", "#2ecc71");
            }
            if (score >= 10) { isGameOver = true; setTimeout(win, 100); }
        } else if (obj.type === TYPES.CARD) {
            nPenalties++; let extraSeconds = 4 + nPenalties; accumulatedTime += (extraSeconds * 1000); 
            penaltyTime = Date.now() + (extraSeconds * 1000);
            triggerGiantAlert("🟥 ¡TARJETA ROJA!\\n+" + extraSeconds + "s de penalización", "#ff4444");
        } else { triggerGiantAlert("⚽ ¡PELOTA DE FÚTBOL!\\nLimpieza marina", "#3498db"); }
    }

    function win() {
        if (document.fullscreenElement) document.exitFullscreen();
        winScreen.style.display = 'block';
        document.getElementById('final-time-text').innerText = "¡Completado en " + (accumulatedTime/1000).toFixed(2) + "s!";
    }

    function draw() {
        update(); ctx.clearRect(0, 0, width, height);
        let seaLine = height * 0.35; if(seaLine < 180) seaLine = 180;

        ctx.fillStyle = acidRainActive ? '#4d603a' : '#70b5d3'; 
        ctx.fillRect(0, 0, width, seaLine);
        
        let seaGrad = ctx.createLinearGradient(0, seaLine, 0, height);
        seaGrad.addColorStop(0, acidRainActive ? '#0e2b14' : '#1E90FF');
        seaGrad.addColorStop(1, '#051937');
        ctx.fillStyle = seaGrad; ctx.fillRect(0, seaLine, width, height - seaLine);

        if (acidRainActive) {
            ctx.strokeStyle = 'rgba(150, 240, 50, 0.4)'; ctx.lineWidth = 1.5;
            acidDrops.forEach(d => {
                ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(d.x - 1, d.y + 9); ctx.stroke();
            });
        }

        waves.forEach(wave => {
            ctx.strokeStyle = acidRainActive ? 'rgba(150, 240, 50, 0.5)' : 'rgba(255, 255, 255, 0.75)';
            ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(wave.x, wave.y + 4, wave.size, Math.PI, 0, false); ctx.stroke();
        });

        if (heli.active) {
            ctx.fillStyle = 'rgba(255, 235, 59, 0.14)'; ctx.beginPath(); ctx.moveTo(heli.x, heli.y + 10);
            ctx.lineTo(heli.x - heli.radarWidth, seaLine); ctx.lineTo(heli.x + heli.radarWidth, seaLine); ctx.closePath(); ctx.fill();
            ctx.fillStyle = '#1e3f20'; ctx.fillRect(heli.x - 22, heli.y - 10, 44, 20);
            ctx.fillStyle = '#000'; ctx.fillRect(heli.x - 32, heli.y - 12, 64, 3);
            ctx.font = "10px sans-serif"; ctx.fillStyle = '#fff'; ctx.fillText("🚁 JUANPRONA", heli.x - 35, heli.y - 18);
        }

        if (patera.active) {
            ctx.fillStyle = (Date.now() < patera.hitFlash) ? '#00e5ff' : '#7e5129'; 
            ctx.beginPath(); ctx.moveTo(patera.x - 22, patera.y); ctx.lineTo(patera.x + 22, patera.y);
            ctx.lineTo(patera.x + 14, patera.y + 14); ctx.lineTo(patera.x - 14, patera.y + 14); ctx.closePath(); ctx.fill();
        }

        objects.forEach(obj => {
            let renderSize = obj.discovered ? (obj.isJuanin ? 15 : 28) : 28;
            let lifeLeft = obj.deathTime - Date.now();
            ctx.beginPath(); ctx.arc(obj.x, obj.y, renderSize, 0, Math.PI*2);
            
            if (lifeLeft < 5000 && Math.floor(Date.now() / 250) % 2 === 0) {
                ctx.fillStyle = 'rgba(110, 110, 110, 0.6)';
            } else {
                ctx.fillStyle = obj.discovered ? 'rgba(30, 85, 145, 0.9)' : 'rgba(24, 48, 89, 0.95)';
            }
            ctx.fill();
            ctx.strokeStyle = (obj.discovered && obj.isJuanin) ? '#ffeb3b' : 'rgba(255,255,255,0.4)';
            ctx.lineWidth = 1.5; ctx.stroke();
            
            if (obj.discovered && imageLoaded && obj.type === TYPES.JUAN) {
                ctx.save(); ctx.beginPath(); ctx.arc(obj.x, obj.y, renderSize - 2, 0, Math.PI*2); ctx.clip();
                let dim = obj.isJuanin ? 30 : 54; ctx.drawImage(juanImg, obj.x - dim/2, obj.y - dim/2, dim, dim); ctx.restore();
            } else if (obj.discovered) {
                ctx.fillStyle = '#fff'; ctx.font = "bold 16px sans-serif";
                ctx.fillText(obj.type === TYPES.CARD ? '🟥' : '⚽', obj.x - 8, obj.y + 6);
            } else {
                ctx.fillStyle = '#fff'; ctx.font = "bold 15px sans-serif"; ctx.fillText("❓", obj.x - 6, obj.y + 5);
            }
        });

        ctx.fillStyle = '#5c3a21'; ctx.fillRect(width/2 - 35, seaLine - 15, 70, 15);
        if (imageLoaded) ctx.drawImage(juanImg, width/2 - 22, seaLine - 72, 44, 60);

        let radarRadius = 55; let radarX = width/2; let radarY = seaLine - 15;
        ctx.beginPath();
        if (patera.active) {
            if (patera.direction === 'left') ctx.arc(radarX, radarY, radarRadius, Math.PI, Math.PI * 1.5, false);
            else ctx.arc(radarX, radarY, radarRadius, Math.PI * 1.5, Math.PI * 2, false);
        } else {
            ctx.arc(radarX, radarY, radarRadius, 0, Math.PI, false);
        }
        ctx.strokeStyle = 'rgba(255,235,59,0.6)'; ctx.lineWidth = 2.5; ctx.stroke();

        let ballX = radarX + Math.cos(angleParam) * radarRadius;
        let ballY = radarY + Math.sin(angleParam) * radarRadius;
        ctx.beginPath(); ctx.moveTo(radarX, radarY); ctx.lineTo(ballX, ballY);
        ctx.strokeStyle = '#ffeb3b'; ctx.lineWidth = 2.5; ctx.stroke();
        ctx.beginPath(); ctx.arc(ballX, ballY, 6, 0, Math.PI*2);
        ctx.fillStyle = (inputState === 'angle') ? '#ffeb3b' : '#2ecc71'; ctx.fill();

        if (inputState === 'force') {
            ctx.fillStyle = '#e74c3c'; ctx.fillRect(width/2 - 50, seaLine - 110, chargeForce, 10);
            ctx.strokeStyle = '#fff'; ctx.strokeRect(width/2 - 50, seaLine - 110, 100, 10);
        }

        if (inputState === 'launching' || inputState === 'returning') {
            ctx.beginPath(); ctx.moveTo(width/2, seaLine - 15); ctx.lineTo(hook.x, hook.y);
            ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.stroke();
            ctx.beginPath(); ctx.arc(hook.x, hook.y, 6, 0, Math.PI*2); ctx.fillStyle = '#e74c3c'; ctx.fill();
        }

        requestAnimationFrame(draw);
    }

    function handleActionStart() {
        if (isGameOver || Date.now() < penaltyTime || Date.now() < globalPauseUntil) return;
        if (inputState === 'angle') { fixedAngle = angleParam; inputState = 'force'; chargeForce = 0; }
    }

    function handleActionEnd() {
        if (inputState === 'force') {
            inputState = 'launching';
            let seaLineBound = height * 0.35; if(seaLineBound < 180) seaLineBound = 180;
            
            if (fixedAngle >= Math.PI && patera.active) {
                hook.mode = 'parabolic';
                let initialVelocity = 4 + (chargeForce / 100) * 14; 
                hook.vx = Math.cos(fixedAngle) * initialVelocity; hook.vy = Math.sin(fixedAngle) * initialVelocity; 
            } else {
                hook.mode = 'straight';
                let maxReach = Math.sqrt((width/2)**2 + height**2) * 0.95;
                let currentReach = (chargeForce / 100) * maxReach;
                hook.targetX = (width/2) + Math.cos(fixedAngle) * currentReach;
                hook.targetY = seaLineBound + Math.abs(Math.sin(fixedAngle) * currentReach);
                if (hook.targetX < 0) hook.targetX = 15; if (hook.targetX > width) hook.targetX = width - 15;
                if (hook.targetY > height) hook.targetY = height - 20;
            }
            hook.x = width / 2; hook.y = seaLineBound - 15;
        }
    }

    container.addEventListener('mousedown', (e) => { if(e.target.id !== 'fullscreen-btn') handleActionStart(); });
    window.addEventListener('mouseup', handleActionEnd);
    container.addEventListener('touchstart', (e) => { if(e.target.id !== 'fullscreen-btn') handleActionStart(); }, {passive: true});
    window.addEventListener('touchend', handleActionEnd);

    draw();
</script>
"""

html_pesca = html_pesca_template.replace("{{JUAN_IMAGE_BASE64}}", img_base64_pesca)
components.html(html_pesca, height=520)

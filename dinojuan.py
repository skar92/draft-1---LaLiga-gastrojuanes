
import base64
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DinoJuan - Minijuego", layout="wide")

# ==========================================
# GESTOR DE SPRITES CON FALLBACK AUTOMÁTICO
# ==========================================
def obtener_imagen_base64(nombre_archivo, color_hex_fallback):
    folder = "img"
    ruta_especifica = os.path.join(folder, nombre_archivo)
    
    # 1. Intenta cargar el archivo específico
    if os.path.exists(ruta_especifica):
        with open(ruta_especifica, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
            
    # 2. Fallback: busca cualquier PNG en la carpeta 'img'
    if os.path.exists(folder):
        pngs = [f for f in os.listdir(folder) if f.endswith(".png")]
        if pngs:
            with open(os.path.join(folder, pngs[0]), "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
                
    # 3. Fallback final: devuelve un indicador de color si no hay imágenes
    return f"COLOR:{color_hex_fallback}"

imagenes = {
    "dino": obtener_imagen_base64("oviedo_dino.png", "#2ecc71"),
    "obs_fijo": obtener_imagen_base64("ubres_dino.png", "#e74c3c"),
    "obs_lento": obtener_imagen_base64("carne_dino.png", "#e67e22"),
    "obs_rapido": obtener_imagen_base64("mirete_dino.png", "#8e44ad"),
    "obs_extra": obtener_imagen_base64("pwc_dino.png", "#c0392b"),
    "fabada": obtener_imagen_base64("fabada.png", "#d35400"),
    "sidra": obtener_imagen_base64("sidra.png", "#f1c40f")
}

# ==========================================
# CÓDIGO HTML Y JAVASCRIPT DEL MINIJUEGO
# ==========================================
html_juego = f'''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body {{ margin: 0; padding: 0; overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #222; }}
    #game-container {{ position: relative; width: 100%; max-width: 900px; margin: 0 auto; box-shadow: 0 0 20px rgba(0,0,0,0.5); }}
    canvas {{ display: block; width: 100%; height: 500px; background: linear-gradient(to bottom, #87CEEB, #E0F6FF); }}
    #ui-layer {{ position: absolute; top: 10px; left: 15px; color: #333; font-weight: bold; font-size: 18px; pointer-events: none; text-shadow: 1px 1px 2px white; }}
    #game-over {{ display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.85); color: white; padding: 30px; border-radius: 15px; text-align: center; border: 3px solid #f1c40f; }}
    .btn {{ background: #f1c40f; color: #000; font-weight: bold; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 15px; font-size: 16px; }}
    #controls {{ position: absolute; bottom: 20px; width: 100%; display: flex; justify-content: space-around; pointer-events: none; }}
    .ctrl-btn {{ pointer-events: auto; background: rgba(255,255,255,0.7); border: 2px solid #333; border-radius: 50%; width: 60px; height: 60px; font-size: 24px; font-weight: bold; display: flex; justify-content: center; align-items: center; cursor: pointer; user-select: none; }}
    #btn-pedo {{ border-radius: 10px; width: auto; padding: 0 20px; background: rgba(211, 84, 0, 0.8); color: white; border-color: #e67e22; }}
</style>
</head>
<body>

<div id="game-container">
    <div id="ui-layer">
        <div>🍏 Sidras: <span id="sidras">0</span> | 🥫 Fabadas: <span id="fabadas">0</span>/3 -> 💨 Pedos: <span id="pedos">0</span></div>
        <div style="font-size: 14px; margin-top: 5px; color: #555;">🏆 Nivel: <span id="nivel">1</span> | 📈 Dificultad Extra: <span id="dif">0.0</span></div>
    </div>
    <canvas id="gameCanvas"></canvas>
    
    <div id="controls">
        <div class="ctrl-btn" id="btn-jump">⬆️</div>
        <div class="ctrl-btn" id="btn-drop">⬇️</div>
        <div class="ctrl-btn" id="btn-pedo">💨 SOLTAR PEDO</div>
    </div>

    <div id="game-over">
        <h1 style="margin-top:0;">💥 GAME OVER</h1>
        <h2>🍏 Sidras Totales: <span id="final-sidras" style="color:#f1c40f;">0</span></h2>
        <p>Has tropezado con un obstáculo o caído al vacío.</p>
        <button class="btn" onclick="reiniciarJuego()">Volver a Jugar</button>
    </div>
</div>

<script>
    // Configuración Canvas e Imágenes
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 900;
    canvas.height = 500;
    
    const IMG_DATA = {{
        dino: "{imagenes['dino']}",
        obs_fijo: "{imagenes['obs_fijo']}",
        obs_lento: "{imagenes['obs_lento']}",
        obs_rapido: "{imagenes['obs_rapido']}",
        fabada: "{imagenes['fabada']}",
        sidra: "{imagenes['sidra']}"
    }};

    const imagenesCargadas = {{}};
    for (let key in IMG_DATA) {{
        if (!IMG_DATA[key].startsWith("COLOR:")) {{
            let img = new Image();
            img.src = IMG_DATA[key];
            imagenesCargadas[key] = img;
        }} else {{
            imagenesCargadas[key] = IMG_DATA[key].split(":")[1]; // Guarda el HEX
        }}
    }}

    function dibujarSprite(ctx, key, x, y, w, h) {{
        let obj = imagenesCargadas[key];
        if (typeof obj === "string") {{
            ctx.fillStyle = obj;
            ctx.fillRect(x, y, w, h);
        }} else if (obj && obj.complete && obj.naturalWidth > 0) {{
            ctx.drawImage(obj, x, y, w, h);
        }} else {{
            ctx.fillStyle = "#000";
            ctx.fillRect(x, y, w, h);
        }}
    }}

    // Estado del Juego
    let juegoActivo = true;
    let cameraY = 0;
    let frameId;
    
    // Progresión
    let cuestasCompletadas = 0;
    let nivel = 1;
    let difDinamica = 0; 
    let baseVelocidad = 6;
    let fAcu = 0; // Fabadas
    let pedosAcu = 0;
    let sidras = 0;

    const CONST_FABADA = 3; 
    const DISTANCIA_PEDO = 2500;

    let dino = {{
        x: 0, y: 200, w: 40, h: 40,
        vy: 0, enAire: false,
        propulsado: false, distPropulsion: 0
    }};

    let slope = {{}};
    let entidades = [];

    // Motor de Preguntas
    function generarPregunta(nivelReal) {{
        let ops = ['+', '-'];
        if (nivelReal > 2) ops.push('*');
        if (nivelReal > 4) ops.push('/');
        
        let op = ops[Math.floor(Math.random() * ops.length)];
        let b = Math.floor(Math.random() * 8 * nivelReal) + 1;
        let c = Math.floor(Math.random() * 8 * nivelReal) + 1;
        
        let resReal = 0;
        if(op === '+') resReal = b + c;
        if(op === '-') resReal = b - c;
        if(op === '*') resReal = b * c;
        if(op === '/') {{ resReal = b; b = b * c; }}
        
        let esCorrecta = Math.random() > 0.5;
        let resMostrado = esCorrecta ? resReal : resReal + (Math.random()>0.5?1:-1) * (Math.floor(Math.random()*4)+1);
        
        return {{ texto: b + " " + op + " " + c + " = " + resMostrado, correcta: esCorrecta ? "SI" : "NO" }};
    }}

    function generarCuesta(inicioX, inicioY) {{
        let nv = Math.max(1, nivel + difDinamica);
        let anguloDeg = (Math.random() * 70) - 35; // Rango -35 a +35
        let anguloRad = anguloDeg * Math.PI / 180;
        let len = 1500 + Math.random() * 800;
        let yFinal = inicioY + Math.tan(anguloRad) * len;
        
        let preg = generarPregunta(nv);
        let topSign = Math.random() > 0.5 ? "SI" : "NO";
        
        let tieneTurbo = Math.random() < 0.35;
        
        slope = {{
            x1: inicioX, y1: inicioY,
            x2: inicioX + len, y2: yFinal,
            angle: anguloRad,
            gapEnd: inicioX + len + 250,
            topY: yFinal - 130,
            bottomY: yFinal + 130,
            pregunta: preg.texto,
            correcta: preg.correcta,
            topSign: topSign,
            bottomSign: topSign === "SI" ? "NO" : "SI",
            tieneTurbo: tieneTurbo,
            turboStart: inicioX + len * 0.4,
            turboEnd: inicioX + len * 0.4 + 400
        }};
        
        // Generar Entidades
        entidades = [];
        let numObstaculos = Math.floor(nv * 1.5) + 1;
        for(let i=0; i<numObstaculos; i++) {{
            let ox = slope.x1 + 600 + Math.random() * (len - 800);
            let tipo = Math.random() < 0.5 ? 'obs_fijo' : (Math.random() < 0.5 ? 'obs_lento' : 'obs_rapido');
            entidades.push({{x: ox, tipo: tipo, activo: true, w: 40, h: 40}});
        }}
        
        // Generar Sidras (Objetivo principal)
        let numSidras = 2 + Math.floor(Math.random() * 3);
        for(let i=0; i<numSidras; i++) {{
            entidades.push({{x: slope.x1 + 300 + Math.random() * (len - 400), tipo: 'sidra', activo: true, w: 30, h: 30}});
        }}
        
        // Generar Fabadas (Frecuencia Fija ~ 30% por cuesta)
        if(Math.random() < 0.30) {{
            entidades.push({{x: slope.x1 + 700 + Math.random() * (len - 900), tipo: 'fabada', activo: true, w: 35, h: 35}});
        }}
    }}

    function iniciarJuego() {{
        dino = {{ x: 0, y: 200, w: 40, h: 40, vy: 0, enAire: false, propulsado: false, distPropulsion: 0 }};
        cuestasCompletadas = 0; nivel = 1; difDinamica = 0;
        fAcu = 0; pedosAcu = 0; sidras = 0;
        juegoActivo = true; cameraY = 0;
        document.getElementById('game-over').style.display = 'none';
        generarCuesta(0, 300);
        actualizarUI();
        loop();
    }}

    function activarPropulsion() {{
        if(pedosAcu > 0 && !dino.propulsado) {{
            dino.propulsado = true;
            dino.distPropulsion = pedosAcu * DISTANCIA_PEDO;
            pedosAcu = 0;
            actualizarUI();
        }}
    }}

    function salto() {{ if(!dino.enAire && !dino.propulsado) {{ dino.vy = -14; dino.enAire = true; }} }}
    function caidaRapida() {{ if(dino.enAire && !dino.propulsado) {{ dino.vy += 8; }} }}

    // Controles Touch
    document.getElementById('btn-jump').addEventListener('touchstart', (e)=> {{ e.preventDefault(); salto(); }});
    document.getElementById('btn-jump').addEventListener('mousedown', salto);
    document.getElementById('btn-drop').addEventListener('touchstart', (e)=> {{ e.preventDefault(); caidaRapida(); }});
    document.getElementById('btn-drop').addEventListener('mousedown', caidaRapida);
    document.getElementById('btn-pedo').addEventListener('touchstart', (e)=> {{ e.preventDefault(); activarPropulsion(); }});
    document.getElementById('btn-pedo').addEventListener('mousedown', activarPropulsion);

    // Controles Teclado
    document.addEventListener('keydown', (e) => {{
        if(e.code === 'ArrowUp') salto();
        if(e.code === 'ArrowDown') caidaRapida();
        if(e.code === 'Space' || e.code === 'KeyF') activarPropulsion();
    }});

    function actualizarUI() {{
        document.getElementById('sidras').innerText = sidras;
        document.getElementById('fabadas').innerText = fAcu;
        document.getElementById('pedos').innerText = pedosAcu;
        document.getElementById('nivel').innerText = nivel;
        document.getElementById('dif').innerText = difDinamica.toFixed(1);
    }}

    function procesarCruceBifurcacion() {{
        // Determinar qué camino cogió comparando Y
        let errYTop = Math.abs(dino.y - slope.topY);
        let errYBot = Math.abs(dino.y - slope.bottomY);
        
        let pathTomado = errYTop < errYBot ? "top" : "bottom";
        let signTomado = pathTomado === "top" ? slope.topSign : slope.bottomSign;
        let yTomado = pathTomado === "top" ? slope.topY : slope.bottomY;

        dino.y = yTomado - dino.h;
        dino.enAire = false; dino.vy = 0;

        // Penalización/Recompensa
        if (signTomado === slope.correcta) {{
            difDinamica = Math.max(0, difDinamica - 0.5);
        }} else {{
            difDinamica += 0.8;
        }}

        cuestasCompletadas++;
        if (cuestasCompletadas % 10 === 0) nivel++;
        
        generarCuesta(slope.gapEnd, yTomado);
        actualizarUI();
    }}

    function colision(r1, r2) {{
        return !(r2.x > r1.x + r1.w || r2.x + r2.w < r1.x || r2.y > r1.y + r1.h || r2.y + r2.h < r1.y);
    }}

    function loop() {{
        if(!juegoActivo) return;
        
        let velTotal = baseVelocidad + (nivel * 0.5) + (difDinamica * 0.3);
        
        // Modificador Turbo de pista
        if(slope.tieneTurbo && dino.x > slope.turboStart && dino.x < slope.turboEnd && !dino.propulsado) {{
            velTotal *= 1.8;
        }}
        
        // Propulsión extrema
        if(dino.propulsado) {{
            velTotal *= 3.5;
            dino.distPropulsion -= velTotal;
            if(dino.distPropulsion <= 0) dino.propulsado = false;
        }}

        dino.x += velTotal;

        // Físicas Y
        if (dino.x >= slope.x1 && dino.x < slope.x2) {{
            let ySuelo = slope.y1 + Math.tan(slope.angle) * (dino.x - slope.x1);
            if (!dino.enAire) {{
                dino.y = ySuelo - dino.h;
            }} else {{
                dino.y += dino.vy;
                dino.vy += 0.8; // Gravedad
                if (dino.y + dino.h >= ySuelo && dino.vy > 0) {{
                    dino.y = ySuelo - dino.h;
                    dino.enAire = false; dino.vy = 0;
                }}
            }}
        }} else if (dino.x >= slope.x2 && dino.x < slope.gapEnd) {{
            // Zona de Bifurcación (Vacío)
            dino.enAire = true;
            
            if(dino.propulsado) {{
                // Auto-piloto invencible
                let targetY = (slope.correcta === slope.topSign) ? slope.topY : slope.bottomY;
                dino.y += ((targetY - dino.h) - dino.y) * 0.2;
                dino.vy = 0;
            }} else {{
                dino.y += dino.vy;
                dino.vy += 0.8;
            }}
        }} else if (dino.x >= slope.gapEnd) {{
            procesarCruceBifurcacion();
        }}

        // Actualizar Entidades (Obstáculos y Premios)
        entidades.forEach(e => {{
            if(!e.activo) return;
            
            let eVel = 0;
            if (e.tipo === 'obs_lento') eVel = velTotal * 0.4;
            if (e.tipo === 'obs_rapido') eVel = -(velTotal + difDinamica);
            e.x += eVel;
            
            e.y = slope.y1 + Math.tan(slope.angle) * (e.x - slope.x1) - e.h;

            // Recolección y Choques
            let cajaDino = {{x: dino.x, y: dino.y, w: dino.w, h: dino.h}};
            let cajaE = {{x: e.x, y: e.y, w: e.w, h: e.h}};
            
            if (colision(cajaDino, cajaE)) {{
                if (e.tipo === 'sidra') {{
                    sidras++; e.activo = false; actualizarUI();
                }} else if (e.tipo === 'fabada') {{
                    fAcu++; e.activo = false;
                    if(fAcu >= CONST_FABADA) {{ pedosAcu++; fAcu = 0; }}
                    actualizarUI();
                }} else if (e.tipo.startsWith('obs_')) {{
                    if (dino.propulsado) {{
                        e.activo = false; // Destruye el obstáculo
                    }} else {{
                        // GAME OVER
                        juegoActivo = false;
                        document.getElementById('final-sidras').innerText = sidras;
                        document.getElementById('game-over').style.display = 'block';
                    }}
                }}
            }}
        }});

        // Cámara Lerp Y
        let targetCamY = canvas.height * 0.6 - dino.y;
        cameraY += (targetCamY - cameraY) * 0.1;

        dibujarEscena();
        if(juegoActivo) frameId = requestAnimationFrame(loop);
    }}

    function dibujarEscena() {{
        ctx.save();
        ctx.setTransform(1,0,0,1,0,0);
        // Fondo que cambia si hay turbo o pedo
        if(dino.propulsado) ctx.fillStyle = "#ffb142";
        else ctx.fillStyle = "#87CEEB";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.restore();

        ctx.save();
        ctx.translate(200 - dino.x, cameraY); // Dino centrado en X=200

        // Dibujar Cuesta Actual
        ctx.lineWidth = 14;
        ctx.strokeStyle = '#27ae60';
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(slope.x1, slope.y1);
        ctx.lineTo(slope.x2, slope.y2);
        ctx.stroke();

        // Dibujar Bifurcaciones
        ctx.strokeStyle = '#2980b9'; // Arriba
        ctx.beginPath(); ctx.moveTo(slope.gapEnd, slope.topY); ctx.lineTo(slope.gapEnd + 2500, slope.topY + Math.tan(slope.angle)*2500); ctx.stroke();
        
        ctx.strokeStyle = '#c0392b'; // Abajo
        ctx.beginPath(); ctx.moveTo(slope.gapEnd, slope.bottomY); ctx.lineTo(slope.gapEnd + 2500, slope.bottomY + Math.tan(slope.angle)*2500); ctx.stroke();

        // Carteles Bifurcación
        ctx.fillStyle = "#fff";
        ctx.font = "bold 28px Arial";
        ctx.fillText(slope.topSign, slope.gapEnd + 40, slope.topY - 25);
        ctx.fillText(slope.bottomSign, slope.gapEnd + 40, slope.bottomY - 25);

        // Pregunta Dicotómica Flotante
        ctx.fillStyle = "rgba(0,0,0,0.7)";
        ctx.fillRect(slope.x2 - 120, slope.y2 - 250, 300, 50);
        ctx.fillStyle = "#f1c40f";
        ctx.font = "bold 32px Arial";
        ctx.fillText(slope.pregunta, slope.x2 - 100, slope.y2 - 215);

        // Señal de Aviso de Turbo
        if (slope.tieneTurbo) {{
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(slope.turboStart - 400, slope.y1 + Math.tan(slope.angle)*(slope.turboStart - 400 - slope.x1) - 100, 60, 60);
            ctx.fillStyle = "#fff";
            ctx.font = "bold 40px Arial";
            ctx.fillText("⚡", slope.turboStart - 390, slope.y1 + Math.tan(slope.angle)*(slope.turboStart - 400 - slope.x1) - 55);
            
            // Suelo rojo en tramo turbo
            ctx.lineWidth = 14;
            ctx.strokeStyle = '#e74c3c';
            ctx.beginPath();
            ctx.moveTo(slope.turboStart, slope.y1 + Math.tan(slope.angle)*(slope.turboStart - slope.x1));
            ctx.lineTo(slope.turboEnd, slope.y1 + Math.tan(slope.angle)*(slope.turboEnd - slope.x1));
            ctx.stroke();
        }}

        // Dibujar Entidades
        entidades.forEach(e => {{
            if(e.activo) dibujarSprite(ctx, e.tipo, e.x, e.y, e.w, e.h);
        }});

        // Dibujar DinoJuan
        ctx.save();
        if(dino.propulsado) {{
            // Efecto turbo verde del pedo
            ctx.fillStyle = "rgba(46, 204, 113, 0.5)";
            ctx.fillRect(dino.x - 60, dino.y, 80, dino.h);
        }}
        dibujarSprite(ctx, "dino", dino.x, dino.y, dino.w, dino.h);
        ctx.restore();

        ctx.restore();
    }}

    window.reiniciarJuego = function() {{ iniciarJuego(); }};

    // Arranque
    iniciarJuego();
</script>
</body>
</html>
'''

components.html(html_juego, height=600)

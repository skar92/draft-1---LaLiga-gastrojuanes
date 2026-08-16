import base64
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DinoJuan - Minijuego", layout="wide")

def obtener_imagen_base64(nombre_base, color_hex_fallback):
    folder = "img"
    extensiones = [".png", ".jpg", ".jpeg"]
    
    for ext in extensiones:
        ruta_especifica = os.path.join(folder, nombre_base + ext)
        if os.path.exists(ruta_especifica):
            mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
            with open(ruta_especifica, "rb") as f:
                return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
            
    if os.path.exists(folder):
        for f_name in os.listdir(folder):
            if f_name.lower().endswith(tuple(extensiones)):
                ruta = os.path.join(folder, f_name)
                ext = os.path.splitext(f_name)[1].lower()
                mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
                with open(ruta, "rb") as f:
                    return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
                
    return f"COLOR:{color_hex_fallback}"

imagenes = {
    "dino": obtener_imagen_base64("oviedo_dino", "#2ecc71"),
    "obs_fijo": obtener_imagen_base64("ubres_dino", "#e74c3c"),
    "obs_lento": obtener_imagen_base64("carne_dino", "#e67e22"),
    "obs_rapido": obtener_imagen_base64("mirete_dino", "#8e44ad"),
    "obs_extra": obtener_imagen_base64("pwc_dino", "#c0392b"),
    "fabada": obtener_imagen_base64("fabada", "#d35400"),
    "sidra": obtener_imagen_base64("sidra", "#f1c40f")
}

html_juego = f'''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body {{ margin: 0; padding: 0; overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #222; -webkit-user-select: none; user-select: none; }}
    #game-container {{ position: relative; width: 100%; max-width: 900px; margin: 0 auto; box-shadow: 0 0 20px rgba(0,0,0,0.5); }}
    canvas {{ display: block; width: 100%; height: 500px; background: linear-gradient(to bottom, #87CEEB, #E0F6FF); cursor: pointer; }}
    #ui-layer {{ position: absolute; top: 10px; left: 15px; color: #333; font-weight: bold; font-size: 18px; pointer-events: none; text-shadow: 1px 1px 2px white; z-index: 10; }}
    #game-over {{ display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.85); color: white; padding: 30px; border-radius: 15px; text-align: center; border: 3px solid #f1c40f; z-index: 20; }}
    .btn {{ background: #f1c40f; color: #000; font-weight: bold; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 15px; font-size: 16px; }}
    #controls {{ position: absolute; bottom: 20px; width: 100%; display: flex; justify-content: space-around; pointer-events: none; z-index: 10; }}
    .ctrl-btn {{ pointer-events: auto; background: rgba(255,255,255,0.8); border: 2px solid #333; border-radius: 12px; padding: 12px 25px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }}
    #btn-pedo {{ background: rgba(211, 84, 0, 0.9); color: white; border-color: #e67e22; }}
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
        <div class="ctrl-btn" id="btn-drop">⬇️ CAER / ABAJO</div>
        <div class="ctrl-btn" id="btn-pedo">💨 SOLTAR PEDO</div>
    </div>

    <div id="game-over">
        <h1 style="margin-top:0;">💥 GAME OVER</h1>
        <h2>🍏 Sidras Totales: <span id="final-sidras" style="color:#f1c40f;">0</span></h2>
        <p>Has tropezado con un obstáculo.</p>
        <button class="btn" onclick="reiniciarJuego()">Volver a Jugar</button>
    </div>
</div>

<script>
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
            img.onload = function() {{
                let tempCanvas = document.createElement('canvas');
                tempCanvas.width = img.naturalWidth;
                tempCanvas.height = img.naturalHeight;
                let tCtx = tempCanvas.getContext('2d');
                tCtx.drawImage(img, 0, 0);
                try {{
                    let imgData = tCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
                    let data = imgData.data;
                    for (let i = 0; i < data.length; i += 4) {{
                        let r = data[i], g = data[i+1], b = data[i+2];
                        if (r > 230 && g > 230 && b > 230) {{
                            data[i+3] = 0;
                        }}
                    }}
                    tCtx.putImageData(imgData, 0, 0);
                    imagenesCargadas[key] = tempCanvas;
                }} catch(e) {{
                    imagenesCargadas[key] = img;
                }}
            }};
            imagenesCargadas[key] = img;
        }} else {{
            imagenesCargadas[key] = IMG_DATA[key].split(":")[1];
        }}
    }}

    function dibujarSprite(ctx, key, x, y, w, h) {{
        let obj = imagenesCargadas[key];
        if (typeof obj === "string") {{
            ctx.fillStyle = obj;
            ctx.fillRect(x, y, w, h);
        }} else if (obj) {{
            ctx.drawImage(obj, x, y, w, h);
        }} else {{
            ctx.fillStyle = "#000";
            ctx.fillRect(x, y, w, h);
        }}
    }}

    let juegoActivo = true;
    let cameraY = 0;
    
    let cuestasCompletadas = 0;
    let nivel = 1;
    let difDinamica = 0; 
    let baseVelocidad = 3.5;
    let fAcu = 0; 
    let pedosAcu = 0;
    let sidras = 0;

    const CONST_FABADA = 3; 
    const DISTANCIA_PEDO = 2500;

    let dino = {{
        x: 0, y: 200, w: 40, h: 40,
        vy: 0, enAire: false, saltosRealizados: 0,
        propulsado: false, distPropulsion: 0
    }};

    let secciones = [];

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

    // CREAR SECCIÓN CON BIFURCACIÓN ARRIBA Y ABAJO AL FINAL
    function crearSeccion(inicioX, inicioY) {{
        let nv = Math.max(1, nivel + difDinamica);
        let maxAngleDeg = Math.min(3 + (nv * 1.5), 15);
        let anguloDeg = (Math.random() * maxAngleDeg * 2) - maxAngleDeg;
        let anguloRad = anguloDeg * Math.PI / 180;
        
        let len = 2800; 
        let yFinal = inicioY + Math.tan(anguloRad) * len;
        
        let preg = generarPregunta(nv);
        let topSign = Math.random() > 0.5 ? "SI" : "NO";
        let tieneTurbo = Math.random() < 0.35;
        
        let entidadesSec = [];
        let numObstaculos = Math.floor(nv * 1.2) + 1;
        for(let i=0; i<numObstaculos; i++) {{
            let ox = inicioX + 600 + Math.random() * (len - 800);
            let tipo = Math.random() < 0.5 ? 'obs_fijo' : (Math.random() < 0.5 ? 'obs_lento' : 'obs_rapido');
            entidadesSec.push({{x: ox, tipo: tipo, activo: true, w: 40, h: 40}});
        }}
        
        let numSidras = 2 + Math.floor(Math.random() * 3);
        for(let i=0; i<numSidras; i++) {{
            entidadesSec.push({{x: inicioX + 400 + Math.random() * (len - 500), tipo: 'sidra', activo: true, w: 30, h: 30}});
        }}
        
        if(Math.random() < 0.30) {{
            entidadesSec.push({{x: inicioX + 800 + Math.random() * (len - 1000), tipo: 'fabada', activo: true, w: 35, h: 35}});
        }}

        return {{
            x1: inicioX, y1: inicioY,
            x2: inicioX + len, y2: yFinal,
            angle: anguloRad,
            topY: yFinal - 110,
            bottomY: yFinal + 110,
            pregunta: preg.texto,
            correcta: preg.correcta,
            topSign: topSign,
            bottomSign: topSign === "SI" ? "NO" : "SI",
            tieneTurbo: tieneTurbo,
            turboStart: inicioX + len * 0.4,
            turboEnd: inicioX + len * 0.4 + 400,
            entidades: entidadesSec,
            bifurcacionProcesada: false
        }};
    }}

    function inicializarMundo() {{
        secciones = [];
        let sec1 = crearSeccion(0, 300);
        secciones.push(sec1);
        let sec2 = crearSeccion(sec1.x2, sec1.y2);
        secciones.push(sec2);
    }}

    function iniciarJuego() {{
        dino = {{ x: 0, y: 200, w: 40, h: 40, vy: 0, enAire: false, saltosRealizados: 0, propulsado: false, distPropulsion: 0 }};
        cuestasCompletadas = 0; nivel = 1; difDinamica = 0;
        fAcu = 0; pedosAcu = 0; sidras = 0;
        juegoActivo = true; cameraY = 0;
        document.getElementById('game-over').style.display = 'none';
        inicializarMundo();
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

    function salto() {{ 
        if(dino.propulsado) return;
        if(!dino.enAire) {{ 
            dino.vy = -12; 
            dino.enAire = true; 
            dino.saltosRealizados = 1;
        }} else if (dino.saltosRealizados === 1) {{
            dino.vy = -7; // Doble salto pequeño
            dino.saltosRealizados = 2;
        }}
    }}
    
    function caidaRapida() {{ 
        if(dino.enAire && !dino.propulsado) {{ 
            dino.vy += 9; 
        }} 
    }}

    canvas.addEventListener('touchstart', (e) => {{ e.preventDefault(); salto(); }});
    canvas.addEventListener('click', () => {{ salto(); }});

    document.getElementById('btn-drop').addEventListener('touchstart', (e)=> {{ e.preventDefault(); caidaRapida(); }});
    document.getElementById('btn-drop').addEventListener('mousedown', (e)=> {{ e.stopPropagation(); caidaRapida(); }});
    document.getElementById('btn-pedo').addEventListener('touchstart', (e)=> {{ e.preventDefault(); activarPropulsion(); }});
    document.getElementById('btn-pedo').addEventListener('mousedown', (e)=> {{ e.stopPropagation(); activarPropulsion(); }});

    document.addEventListener('keydown', (e) => {{
        if(e.code === 'ArrowUp' || e.code === 'Space') salto();
        if(e.code === 'ArrowDown') caidaRapida();
        if(e.code === 'KeyF') activarPropulsion();
    }});

    function actualizarUI() {{
        document.getElementById('sidras').innerText = sidras;
        document.getElementById('fabadas').innerText = fAcu;
        document.getElementById('pedos').innerText = pedosAcu;
        document.getElementById('nivel').innerText = nivel;
        document.getElementById('dif').innerText = difDinamica.toFixed(1);
    }}

    function colision(r1, r2) {{
        return !(r2.x > r1.x + r1.w || r2.x + r2.w < r1.x || r2.y > r1.y + r1.h || r2.y + r2.h < r1.y);
    }}

    function loop() {{
        if(!juegoActivo) return;
        
        let velTotal = baseVelocidad + (nivel * 0.4) + (difDinamica * 0.2);
        
        let secActual = secciones.find(s => dino.x >= s.x1 && dino.x <= s.x2) || secciones[0];

        if(secActual.tieneTurbo && dino.x > secActual.turboStart && dino.x < secActual.turboEnd && !dino.propulsado) {{
            velTotal *= 1.8;
        }}
        
        if(dino.propulsado) {{
            velTotal *= 3.5;
            dino.distPropulsion -= velTotal;
            if(dino.distPropulsion <= 0) dino.propulsado = false;
        }}

        dino.x += velTotal;

        // Si estamos llegando al final de la sección actual, evaluamos la bifurcación
        if (dino.x >= secActual.x2 - 10 && !secActual.bifurcacionProcesada) {{
            secActual.bifurcacionProcesada = true;
            
            let caminoElegidoY, signoElegido;
            if(dino.propulsado) {{
                caminoElegidoY = (secActual.correcta === secActual.topSign) ? secActual.topY : secActual.bottomY;
                signoElegido = secActual.correcta;
            }} else {{
                let mediaY = (secActual.topY + secActual.bottomY) / 2;
                let vaArriba = dino.y < mediaY;
                caminoElegidoY = vaArriba ? secActual.topY : secActual.bottomY;
                signoElegido = vaArriba ? secActual.topSign : secActual.bottomSign;
            }}

            dino.y = caminoElegidoY - dino.h;
            dino.enAire = false; dino.vy = 0; dino.saltosRealizados = 0;

            if (signoElegido === secActual.correcta) {{
                difDinamica = Math.max(0, difDinamica - 0.4);
            }} else {{
                difDinamica += 0.7;
            }}

            cuestasCompletadas++;
            if (cuestasCompletadas % 10 === 0) nivel++;
            actualizarUI();
            
            // Generar la siguiente sección conectada de manera dinámica
            let nuevaSec = crearSeccion(secActual.x2, caminoElegidoY);
            secciones.push(nuevaSec);
        }}

        // Física estándar dentro del tramo
        let ySuelo = secActual.y1 + Math.tan(secActual.angle) * (dino.x - secActual.x1);
        
        if (!dino.enAire) {{
            dino.y = ySuelo - dino.h;
        }} else {{
            dino.y += dino.vy;
            dino.vy += 0.6;
            if (dino.y + dino.h >= ySuelo && dino.vy > 0 && dino.x < secActual.x2 - 20) {{
                dino.y = ySuelo - dino.h;
                dino.enAire = false;
                dino.saltosRealizados = 0;
                dino.vy = 0;
            }}
        }}

        // Limpiar tramos antiguos
        if (secciones.length > 3) {{
            secciones.shift();
        }}

        // Colisiones con entidades
        secciones.forEach(s => {{
            s.entidades.forEach(e => {{
                if(!e.activo) return;
                
                let eVel = 0;
                if (e.tipo === 'obs_lento') eVel = velTotal * 0.4;
                if (e.tipo === 'obs_rapido') eVel = -(velTotal + difDinamica);
                e.x += eVel;
                
                e.y = s.y1 + Math.tan(s.angle) * (e.x - s.x1) - e.h;

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
                            e.activo = false;
                        }} else {{
                            juegoActivo = false;
                            document.getElementById('final-sidras').innerText = sidras;
                            document.getElementById('game-over').style.display = 'block';
                        }}
                    }}
                }}
            }});
        }});

        // Cámara vertical fluida
        let targetCamY = canvas.height * 0.6 - dino.y;
        cameraY += (targetCamY - cameraY) * 0.1;

        dibujarEscena();
        if(juegoActivo) requestAnimationFrame(loop);
    }}

    function dibujarEscena() {{
        ctx.save();
        ctx.setTransform(1,0,0,1,0,0);
        if(dino.propulsado) ctx.fillStyle = "#ffb142";
        else ctx.fillStyle = "#87CEEB";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.restore();

        ctx.save();
        ctx.translate(200 - dino.x, cameraY);

        secciones.forEach(s => {{
            // Cuesta principal
            ctx.lineWidth = 14;
            ctx.strokeStyle = '#27ae60';
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(s.x1, s.y1);
            ctx.lineTo(s.x2, s.y2);
            ctx.stroke();

            // Bifurcación superior e inferior al final de la sección
            ctx.strokeStyle = '#2980b9'; 
            ctx.beginPath(); ctx.moveTo(s.x2, s.topY); ctx.lineTo(s.x2 + 2500, s.topY + Math.tan(s.angle)*2500); ctx.stroke();
            
            ctx.strokeStyle = '#c0392b'; 
            ctx.beginPath(); ctx.moveTo(s.x2, s.bottomY); ctx.lineTo(s.x2 + 2500, s.bottomY + Math.tan(s.angle)*2500); ctx.stroke();

            // Letreros de opciones SI / NO
            ctx.fillStyle = "#fff";
            ctx.font = "bold 26px Arial";
            ctx.fillText(s.topSign, s.x2 + 40, s.topY - 20);
            ctx.fillText(s.bottomSign, s.x2 + 40, s.bottomY - 20);

            // Pregunta matemática flotante
            ctx.fillStyle = "rgba(0,0,0,0.7)";
            ctx.fillRect(s.x2 - 240, s.y2 - 230, 280, 45);
            ctx.fillStyle = "#f1c40f";
            ctx.font = "bold 28px Arial";
            ctx.fillText(s.pregunta, s.x2 - 225, s.y2 - 198);

            if (s.tieneTurbo) {{
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(s.turboStart - 200, s.y1 + Math.tan(s.angle)*(s.turboStart - 200 - s.x1) - 80, 50, 50);
                ctx.fillStyle = "#fff";
                ctx.font = "bold 35px Arial";
                ctx.fillText("⚡", s.turboStart - 190, s.y1 + Math.tan(s.angle)*(s.turboStart - 200 - s.x1) - 42);
            }}

            s.entidades.forEach(e => {{
                if(e.activo) dibujarSprite(ctx, e.tipo, e.x, e.y, e.w, e.h);
            }});
        }});

        ctx.save();
        if(dino.propulsado) {{
            ctx.fillStyle = "rgba(46, 204, 113, 0.5)";
            ctx.fillRect(dino.x - 60, dino.y, 80, dino.h);
        }}
        dibujarSprite(ctx, "dino", dino.x, dino.y, dino.w, dino.h);
        ctx.restore();

        ctx.restore();
    }}

    window.reiniciarJuego = function() {{ iniciarJuego(); }};
    iniciarJuego();
</script>
</body>
</html>
'''

components.html(html_juego, height=600)

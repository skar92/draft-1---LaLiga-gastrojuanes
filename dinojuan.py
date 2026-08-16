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

    // CREA UN CAMINO QUE TERMINA EN UNA BIFURCACIÓN (ARRIBA Y ABAJO)
    function crearSeccion(inicioX, inicioY) {{
        let nv = Math.max(1, nivel + difDinamica);
        let len = 2400; // Longitud del camino principal
        let xFin = inicioX + len;
        
        let preg = generarPregunta(nv);
        let topSign = Math.random() > 0.5 ? "SI" : "NO";
        let bottomSign = topSign === "SI" ? "NO" : "SI";
        let tieneTurbo = Math.random() < 0.35;
        
        let entidadesSec = [];
        let numObstaculos = Math.floor(nv * 1.0) + 1;
        for(let i=0; i<numObstaculos; i++) {{
            let ox = inicioX + 400 + Math.random() * (len - 600);
            let tipo = Math.random() < 0.5 ? 'obs_fijo' : (Math.random() < 0.5 ? 'obs_lento' : 'obs_rapido');
            entidadesSec.push({{x: ox, tipo: tipo, activo: true, w: 40, h: 40, enBifurcacion: false}});
        }}
        
        let numSidras = 2 + Math.floor(Math.random() * 3);
        for(let i=0; i<numSidras; i++) {{
            entidadesSec.push({{x: inicioX + 300 + Math.random() * (len - 400), tipo: 'sidra', activo: true, w: 30, h: 30, enBifurcacion: false}});
        }}
        
        if(Math.random() < 0.30) {{
            entidadesSec.push({{x: inicioX + 600 + Math.random() * (len - 800), tipo: 'fabada', activo: true, w: 35, h: 35, enBifurcacion: false}});
        }}

        return {{
            x1: inicioX, y1: inicioY,
            x2: xFin, y2: inicioY, // Camino recto que acaba
            pregunta: preg.texto,
            correcta: preg.correcta,
            topSign: topSign,
            bottomSign: bottomSign,
            tieneTurbo: tieneTurbo,
            turboStart: inicioX + len * 0.4,
            turboEnd: inicioX + len * 0.4 + 300,
            entidades: entidadesSec,
            bifurcacionProcesada: false,
            largoBifurcacion: 800 // Longitud de la zona donde se elige arriba o abajo
        }};
    }}

    function inicializarMundo() {{
        secciones = [];
        let sec1 = crearSeccion(0, 300);
        secciones.push(sec1);
        let sec2 = crearSeccion(sec1.x2 + sec1.largoBifurcacion, 300);
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
            dino.vy = -7;
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
        if(e.code === 'KeyKeyF' || e.code === 'KeyF') activarPropulsion();
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
        
        // Encontrar sección actual o zona de bifurcación
        let secActual = secciones.find(s => dino.x >= s.x1 && dino.x <= s.x2 + s.largoBifurcacion) || secciones[0];

        let enZonaBifurcacion = dino.x >= secActual.x2 && dino.x <= secActual.x2 + secActual.largoBifurcacion;

        if(secActual.tieneTurbo && dino.x > secActual.turboStart && dino.x < secActual.turboEnd && !dino.propulsado) {{
            velTotal *= 1.8;
        }}
        
        if(dino.propulsado) {{
            velTotal *= 3.5;
            dino.distPropulsion -= velTotal;
            if(dino.distPropulsion <= 0) dino.propulsado = false;
        }}

        dino.x += velTotal;

        // Si cruza completamente la zona de bifurcación y no se procesó, elegimos camino por defecto o posición actual
        if (dino.x >= secActual.x2 + secActual.largoBifurcacion && !secActual.bifurcacionProcesada) {{
            secActual.bifurcacionProcesada = true;
            
            let yElegida, signoElegido;
            let topY = secActual.y2 - 120;
            let bottomY = secActual.y2 + 120;

            if(dino.propulsado) {{
                yElegida = (secActual.correcta === secActual.topSign) ? topY : bottomY;
                signoElegido = secActual.correcta;
            }} else {{
                let mediaY = secActual.y2;
                let vaArriba = dino.y < mediaY;
                yElegida = vaArriba ? topY : bottomY;
                signoElegido = vaArriba ? secActual.topSign : secActual.bottomSign;
            }}

            dino.y = yElegida - dino.h;
            dino.enAire = false; dino.vy = 0; dino.saltosRealizados = 0;

            if (signoElegido === secActual.correcta) {{
                difDinamica = Math.max(0, difDinamica - 0.4);
            }} else {{
                difDinamica += 0.7;
            }}

            cuestasCompletadas++;
            if (cuestasCompletadas % 10 === 0) nivel++;
            actualizarUI();
            
            // Crear el siguiente tramo que parte desde la altura elegida
            let nuevaSec = crearSeccion(secActual.x2 + secActual.largoBifurcacion, yElegida);
            secciones.push(nuevaSec);
        }}

        // Física del suelo principal o transición en bifurcación
        let ySuelo = secActual.y1;
        if (enZonaBifurcacion) {{
            // Durante la bifurcación el suelo se divide visualmente arriba y abajo, mantenemos al dinosaurio sobre la plataforma que pise
            let topY = secActual.y2 - 120;
            let bottomY = secActual.y2 + 120;
            let yActivoPlataforma = (dino.y < secActual.y2) ? topY : bottomY;
            ySuelo = yActivoPlataforma;
        }}
        
        if (!dino.enAire) {{
            dino.y = ySuelo - dino.h;
        }} else {{
            dino.y += dino.vy;
            dino.vy += 0.6;
            let sueloActualDeZona = enZonaBifurcacion ? ((dino.y < secActual.y2) ? secActual.y2 - 120 : secActual.y2 + 120) : secActual.y1;
            if (dino.y + dino.h >= sueloActualDeZona && dino.vy > 0) {{
                dino.y = sueloActualDeZona - dino.h;
                dino.enAire = false;
                dino.saltosRealizados = 0;
                dino.vy = 0;
            }}
        }}

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
            // 1. Camino principal que llega hasta el final
            ctx.lineWidth = 14;
            ctx.strokeStyle = '#27ae60';
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(s.x1, s.y1);
            ctx.lineTo(s.x2, s.y2);
            ctx.stroke();

            // 2. Zona de Bifurcación: Camino Arriba y Camino Abajo
            let topY = s.y2 - 120;
            let bottomY = s.y2 + 120;
            let largoBif = s.largoBifurcacion;

            // Camino Superior
            ctx.strokeStyle = '#2980b9';
            ctx.beginPath();
            ctx.moveTo(s.x2, s.y2);
            ctx.lineTo(s.x2 + 150, topY);
            ctx.lineTo(s.x2 + largoBif, topY);
            ctx.stroke();

            // Camino Inferior
            ctx.strokeStyle = '#c0392b';
            ctx.beginPath();
            ctx.moveTo(s.x2, s.y2);
            ctx.lineTo(s.x2 + 150, bottomY);
            ctx.lineTo(s.x2 + largoBif, bottomY);
            ctx.stroke();

            // Letreros SI / NO en las entradas de la bifurcación
            ctx.fillStyle = "#fff";
            ctx.font = "bold 24px Arial";
            ctx.fillText(s.topSign, s.x2 + 170, topY - 15);
            ctx.fillText(s.bottomSign, s.x2 + 170, bottomY + 35);

            // Pregunta matemática en el cartel central antes de abrirse
            ctx.fillStyle = "rgba(0,0,0,0.7)";
            ctx.fillRect(s.x2 - 220, s.y2 - 180, 260, 45);
            ctx.fillStyle = "#f1c40f";
            ctx.font = "bold 26px Arial";
            ctx.fillText(s.pregunta, s.x2 - 205, s.y2 - 148);

            if (s.tieneTurbo) {{
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(s.turboStart, s.y1 - 70, 45, 45);
                ctx.fillStyle = "#fff";
                ctx.font = "bold 30px Arial";
                ctx.fillText("⚡", s.turboStart + 8, s.y1 - 38);
            }}

            s.entidades.forEach(e => {{
                if(e.activo) {{
                    // Posicionar entidades en las bifurcaciones si están en esa zona
                    if (e.x > s.x2) {{
                        let enArriba = (e.tipo.charCodeAt(0) % 2 === 0); // Distribución equitativa
                        e.y = enArriba ? topY - e.h : bottomY - e.h;
                    }} else {{
                        e.y = s.y1 - e.h;
                    }}
                    dibujarSprite(ctx, e.tipo, e.x, e.y, e.w, e.h);
                }}
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

import base64
import os
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="DinoJuan - Minijuego", layout="wide")


# ============================================================
# IMÁGENES
# ============================================================

def obtener_imagen_base64(nombre_archivo, color_hex_fallback):
    folder = "img"
    ruta_especifica = os.path.join(folder, nombre_archivo)

    if os.path.exists(ruta_especifica):
        with open(ruta_especifica, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    if os.path.exists(folder):
        pngs = [f for f in os.listdir(folder) if f.endswith(".png")]
        if pngs:
            with open(os.path.join(folder, pngs[0]), "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

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


# ============================================================
# HTML / CSS / JAVASCRIPT
# ============================================================

html_juego = """
<!DOCTYPE html>
<html>

<head>
<meta name="viewport"
      content="width=device-width, initial-scale=1.0,
               maximum-scale=1.0, user-scalable=no">

<style>

body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: 'Segoe UI', sans-serif;
    background: #222;
    -webkit-user-select: none;
    user-select: none;
}

#game-container {
    position: relative;
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}

canvas {
    display: block;
    width: 100%;
    height: 500px;
    background: linear-gradient(to bottom, #87CEEB, #E0F6FF);
    cursor: pointer;
}

#ui-layer {
    position: absolute;
    top: 10px;
    left: 15px;
    color: #333;
    font-weight: bold;
    font-size: 18px;
    pointer-events: none;
    text-shadow: 1px 1px 2px white;
    z-index: 10;
}

#game-over {
    display: none;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0,0,0,0.85);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    border: 3px solid #f1c40f;
    z-index: 20;
}

.btn {
    background: #f1c40f;
    color: #000;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 15px;
    font-size: 16px;
}

#controls {
    position: absolute;
    bottom: 20px;
    width: 100%;
    display: flex;
    justify-content: space-around;
    pointer-events: none;
    z-index: 10;
}

.ctrl-btn {
    pointer-events: auto;
    background: rgba(255,255,255,0.8);
    border: 2px solid #333;
    border-radius: 12px;
    padding: 12px 25px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}

#btn-pedo {
    background: rgba(211, 84, 0, 0.9);
    color: white;
    border-color: #e67e22;
}

</style>
</head>


<body>

<div id="game-container">

    <div id="ui-layer">
        <div>
            🍏 Sidras: <span id="sidras">0</span>
            |
            🥫 Fabadas: <span id="fabadas">0</span>/3
            ->
            💨 Pedos: <span id="pedos">0</span>
        </div>

        <div style="font-size: 14px; margin-top: 5px; color: #555;">
            🏆 Nivel: <span id="nivel">1</span>
            |
            📈 Dificultad Extra: <span id="dif">0.0</span>
        </div>
    </div>


    <canvas id="gameCanvas"></canvas>


    <div id="controls">

        <div class="ctrl-btn" id="btn-drop">
            ⬇️ CAER / ABAJO
        </div>

        <div class="ctrl-btn" id="btn-pedo">
            💨 SOLTAR PEDO
        </div>

    </div>


    <div id="game-over">

        <h1 style="margin-top:0;">
            💥 GAME OVER
        </h1>

        <h2>
            🍏 Sidras Totales:
            <span id="final-sidras" style="color:#f1c40f;">
                0
            </span>
        </h2>

        <p>
            Has tropezado con un obstáculo.
        </p>

        <button class="btn" onclick="reiniciarJuego()">
            Volver a Jugar
        </button>

    </div>

</div>


<script>


// ============================================================
// CANVAS
// ============================================================

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

canvas.width = 900;
canvas.height = 500;


// ============================================================
// IMÁGENES
// ============================================================

const IMG_DATA = {
    dino: "__DINO__",
    obs_fijo: "__OBS_FIJO__",
    obs_lento: "__OBS_LENTO__",
    obs_rapido: "__OBS_RAPIDO__",
    fabada: "__FABADA__",
    sidra: "__SIDRA__"
};


const imagenesCargadas = {};

for (let key in IMG_DATA) {

    if (!IMG_DATA[key].startsWith("COLOR:")) {

        let img = new Image();
        img.src = IMG_DATA[key];

        imagenesCargadas[key] = img;

    } else {

        imagenesCargadas[key] =
            IMG_DATA[key].split(":")[1];

    }
}


function dibujarSprite(ctx, key, x, y, w, h) {

    let obj = imagenesCargadas[key];

    if (typeof obj === "string") {

        ctx.fillStyle = obj;
        ctx.fillRect(x, y, w, h);

    } else if (obj && obj.complete && obj.naturalWidth > 0) {

        ctx.drawImage(obj, x, y, w, h);

    } else {

        ctx.fillStyle = "#000";
        ctx.fillRect(x, y, w, h);
    }
}


// ============================================================
// VARIABLES DEL JUEGO
// ============================================================

let juegoActivo = true;

let cameraY = 0;
let frameId;

let cuestasCompletadas = 0;
let nivel = 1;
let difDinamica = 0;

let baseVelocidad = 3.5;

let fAcu = 0;
let pedosAcu = 0;
let sidras = 0;


const CONST_FABADA = 3;
const DISTANCIA_PEDO = 2500;


// ============================================================
// FÍSICA
// ============================================================

const GRAVEDAD = 0.65;
const FUERZA_SALTO = -15;

// Altura aproximada máxima que alcanza un salto.
// Se utiliza también para decidir si el camino superior
// es accesible desde el inferior.
const ALTURA_MAX_SALTO =
    (FUERZA_SALTO * FUERZA_SALTO) /
    (2 * GRAVEDAD);


// ============================================================
// DINO
// ============================================================

let dino = {
    x: 0,
    y: 200,
    w: 40,
    h: 40,

    vy: 0,

    enAire: false,

    propulsado: false,
    distPropulsion: 0,

    // "main", "top" o "bottom"
    ruta: "main"
};


// ============================================================
// ESTRUCTURA DE LA CUESTA
// ============================================================

let slope = {};

let entidades = [];


// ============================================================
// PREGUNTAS
// ============================================================

function generarPregunta(nivelReal) {

    let ops = ["-", "+"];

    if (nivelReal > 2)
        ops.push("*");

    if (nivelReal > 4)
        ops.push("/");


    let op =
        ops[Math.floor(Math.random() * ops.length)];


    let b =
        Math.floor(Math.random() * 8 * nivelReal) + 1;

    let c =
        Math.floor(Math.random() * 8 * nivelReal) + 1;


    let resReal = 0;


    if (op === "+")
        resReal = b + c;

    if (op === "-")
        resReal = b - c;

    if (op === "*")
        resReal = b * c;

    if (op === "/") {

        resReal = b;
        b = b * c;
    }


    let esCorrecta =
        Math.random() > 0.5;


    let resMostrado =
        esCorrecta
            ? resReal
            : resReal +
              (Math.random() > 0.5 ? 1 : -1) *
              (Math.floor(Math.random() * 4) + 1);


    return {
        texto:
            b + " " + op + " " + c +
            " = " + resMostrado,

        correcta:
            esCorrecta ? "SI" : "NO"
    };
}


// ============================================================
// GENERACIÓN DE UNA NUEVA CUESTA
// ============================================================

function generarCuesta(inicioX, inicioY) {

    let nv =
        Math.max(1, nivel + difDinamica);


    // --------------------------------------------------------
    // CAMINO PRINCIPAL
    // --------------------------------------------------------

    const mainLen =
        1450 + Math.random() * 450;


    const maxAngleDeg =
        Math.min(
            4 + nv * 1.8,
            18
        );


    const anguloPrincipalDeg =
        (Math.random() * maxAngleDeg * 2)
        - maxAngleDeg;


    const anguloPrincipal =
        anguloPrincipalDeg *
        Math.PI / 180;


    const splitX =
        inicioX + mainLen;


    const splitY =
        inicioY +
        Math.tan(anguloPrincipal) *
        mainLen;


    // --------------------------------------------------------
    // DOS CAMINOS
    // --------------------------------------------------------
    //
    // Importante:
    //
    // topY < bottomY
    //
    // La separación NUNCA llega a cero.
    //
    // Los caminos pueden:
    // - separarse
    // - mantenerse prácticamente paralelos
    // - acercarse un poco
    //
    // pero jamás cruzarse.
    // --------------------------------------------------------

    const branchLen =
        3000 + Math.random() * 600;


    const separacionInicial = 110;


    // Cambio total de separación durante toda la rama.
    //
    // Positivo  -> se separan.
    // Cero      -> paralelos.
    // Negativo  -> se acercan, pero nunca llegan a tocarse.
    //
    // Como mínimo conservamos 70 px de separación.
    const cambioSeparacion =
        -35 + Math.random() * 155;


    const separacionFinal =
        separacionInicial + cambioSeparacion;


    const pendienteSeparacion =
        cambioSeparacion / branchLen;


    const pendienteBase =
        Math.tan(anguloPrincipal);


    const pendienteTop =
        pendienteBase -
        pendienteSeparacion / 2;


    const pendienteBottom =
        pendienteBase +
        pendienteSeparacion / 2;


    const topStartY =
        splitY -
        separacionInicial / 2;


    const bottomStartY =
        splitY +
        separacionInicial / 2;


    const topEndY =
        topStartY +
        pendienteTop * branchLen;


    const bottomEndY =
        bottomStartY +
        pendienteBottom * branchLen;


    const topAngle =
        Math.atan(pendienteTop);


    const bottomAngle =
        Math.atan(pendienteBottom);


    // --------------------------------------------------------
    // PREGUNTA
    // --------------------------------------------------------

    let preg =
        generarPregunta(nv);


    let topSign =
        Math.random() > 0.5
            ? "SI"
            : "NO";


    let bottomSign =
        topSign === "SI"
            ? "NO"
            : "SI";


    // --------------------------------------------------------
    // TURBO
    // --------------------------------------------------------

    let tieneTurbo =
        Math.random() < 0.35;


    // --------------------------------------------------------
    // APERTURA DEL CAMINO SUPERIOR
    // --------------------------------------------------------
    //
    // Solo puede existir si la distancia entre ambos caminos
    // en esa zona es alcanzable mediante un salto.
    //
    // El camino inferior NUNCA tiene apertura.
    // --------------------------------------------------------

    const aperturaCandidataX =
        splitX +
        branchLen * 0.38;


    const separacionEnApertura =
        obtenerSeparacionEnX(
            aperturaCandidataX,
            splitX,
            separacionInicial,
            cambioSeparacion,
            branchLen
        );


    const puedeSubirAlSuperior =
        separacionEnApertura <=
        ALTURA_MAX_SALTO + 10;


    let tieneAperturaSuperior =
        puedeSubirAlSuperior &&
        Math.random() < 0.70;


    let aperturaX1 = 0;
    let aperturaX2 = 0;


    if (tieneAperturaSuperior) {

        const anchoApertura =
            100 + Math.random() * 45;


        aperturaX1 =
            aperturaCandidataX -
            anchoApertura / 2;


        aperturaX2 =
            aperturaCandidataX +
            anchoApertura / 2;
    }


    // --------------------------------------------------------
    // OBJETO DE LA CUESTA
    // --------------------------------------------------------

    slope = {

        x1: inicioX,
        y1: inicioY,

        splitX: splitX,
        splitY: splitY,

        branchEndX:
            splitX + branchLen,

        topStartY:
            topStartY,

        bottomStartY:
            bottomStartY,

        topEndY:
            topEndY,

        bottomEndY:
            bottomEndY,

        topAngle:
            topAngle,

        bottomAngle:
            bottomAngle,

        topSlope:
            pendienteTop,

        bottomSlope:
            pendienteBottom,

        separationInicial:
            separacionInicial,

        cambioSeparacion:
            cambioSeparacion,

        branchLen:
            branchLen,

        pregunta:
            preg.texto,

        correcta:
            preg.correcta,

        topSign:
            topSign,

        bottomSign:
            bottomSign,

        tieneTurbo:
            tieneTurbo,

        turboStart:
            inicioX + mainLen * 0.42,

        turboEnd:
            inicioX + mainLen * 0.42 + 400,

        tieneAperturaSuperior:
            tieneAperturaSuperior,

        aperturaX1:
            aperturaX1,

        aperturaX2:
            aperturaX2
    };


    // --------------------------------------------------------
    // OBSTÁCULOS
    // --------------------------------------------------------

    entidades = [];


    let numObstaculos =
        Math.floor(nv * 1.5) + 1;


    for (let i = 0; i < numObstaculos; i++) {

        let ruta;


        // Los obstáculos aparecen también en las dos ramas.
        // Eso permite que la elección de camino importe.
        let r =
            Math.random();


        if (r < 0.34) {

            ruta = "main";

        } else if (r < 0.67) {

            ruta = "top";

        } else {

            ruta = "bottom";
        }


        let minX;
        let maxX;


        if (ruta === "main") {

            minX =
                inicioX + 450;

            maxX =
                splitX - 150;

        } else {

            minX =
                splitX + 350;

            maxX =
                slope.branchEndX - 400;
        }


        if (maxX <= minX)
            continue;


        let ox =
            minX +
            Math.random() *
            (maxX - minX);


        // No colocamos obstáculos dentro de la apertura.
        if (
            ruta === "top" &&
            tieneAperturaSuperior &&
            ox > aperturaX1 - 50 &&
            ox < aperturaX2 + 50
        ) {
            ox = aperturaX2 + 100;
        }


        let tipo;


        let t =
            Math.random();


        if (t < 0.5) {

            tipo = "obs_fijo";

        } else if (t < 0.75) {

            tipo = "obs_lento";

        } else {

            tipo = "obs_rapido";
        }


        entidades.push({

            x: ox,

            tipo: tipo,

            activo: true,

            w: 40,
            h: 40,

            ruta: ruta
        });
    }


    // --------------------------------------------------------
    // SIDRAS
    // --------------------------------------------------------

    let numSidras =
        2 + Math.floor(Math.random() * 3);


    for (let i = 0; i < numSidras; i++) {

        let ruta =
            Math.random() < 0.5
                ? "main"
                : "bottom";


        let minX =
            ruta === "main"
                ? inicioX + 300
                : splitX + 250;


        let maxX =
            ruta === "main"
                ? splitX - 150
                : slope.branchEndX - 300;


        if (maxX <= minX)
            continue;


        entidades.push({

            x:
                minX +
                Math.random() *
                (maxX - minX),

            tipo: "sidra",

            activo: true,

            w: 30,
            h: 30,

            ruta: ruta
        });
    }


    // --------------------------------------------------------
    // FABADA
    // --------------------------------------------------------

    if (Math.random() < 0.30) {

        let ruta =
            Math.random() < 0.5
                ? "main"
                : "bottom";


        let minX =
            ruta === "main"
                ? inicioX + 500
                : splitX + 300;


        let maxX =
            ruta === "main"
                ? splitX - 200
                : slope.branchEndX - 500;


        if (maxX > minX) {

            entidades.push({

                x:
                    minX +
                    Math.random() *
                    (maxX - minX),

                tipo: "fabada",

                activo: true,

                w: 35,
                h: 35,

                ruta: ruta
            });
        }
    }
}


// ============================================================
// SEPARACIÓN ENTRE CAMINOS
// ============================================================

function obtenerSeparacionEnX(
    x,
    splitX,
    separacionInicial,
    cambioSeparacion,
    branchLen
) {

    let progreso =
        (x - splitX) /
        branchLen;


    progreso =
        Math.max(
            0,
            Math.min(1, progreso)
        );


    return (
        separacionInicial +
        cambioSeparacion * progreso
    );
}


// ============================================================
// OBTENER Y DE UN CAMINO
// ============================================================

function obtenerYCamino(ruta, x) {

    if (ruta === "main") {

        return (
            slope.y1 +
            Math.tan(
                Math.atan(
                    (slope.splitY - slope.y1) /
                    (slope.splitX - slope.x1)
                )
            ) *
            (x - slope.x1)
        );
    }


    if (ruta === "top") {

        return (
            slope.topStartY +
            slope.topSlope *
            (x - slope.splitX)
        );
    }


    if (ruta === "bottom") {

        return (
            slope.bottomStartY +
            slope.bottomSlope *
            (x - slope.splitX)
        );
    }


    return slope.splitY;
}


// ============================================================
// APERTURA DEL CAMINO SUPERIOR
// ============================================================

function estaEnAperturaSuperior(x) {

    if (!slope.tieneAperturaSuperior)
        return false;


    return (
        x >= slope.aperturaX1 &&
        x <= slope.aperturaX2
    );
}


// ============================================================
// SUPERFICIES DISPONIBLES DEBAJO DEL DINO
// ============================================================
//
// Esta función es la clave para evitar cualquier caída al vacío.
//
// Antes de la bifurcación:
//     solo existe el camino principal.
//
// Después:
//     siempre existe el camino inferior.
//
// El superior puede desaparecer únicamente dentro de su apertura.
// ============================================================

function obtenerSuperficies(x) {

    let superficies = [];


    if (x < slope.splitX) {

        superficies.push({

            ruta: "main",

            y:
                obtenerYCamino(
                    "main",
                    x
                )
        });


        return superficies;
    }


    // --------------------------------------------------------
    // CAMINO SUPERIOR
    // --------------------------------------------------------

    if (!estaEnAperturaSuperior(x)) {

        superficies.push({

            ruta: "top",

            y:
                obtenerYCamino(
                    "top",
                    x
                )
        });
    }


    // --------------------------------------------------------
    // CAMINO INFERIOR
    //
    // SIEMPRE existe.
    // NUNCA tiene agujeros.
    // --------------------------------------------------------

    superficies.push({

        ruta: "bottom",

        y:
            obtenerYCamino(
                "bottom",
                x
            )
    });


    return superficies;
}


// ============================================================
// RUTA MÁS CERCANA
// ============================================================

function obtenerRutaMasCercana() {

    let x =
        Math.min(
            dino.x,
            slope.branchEndX
        );


    let bottomDino =
        dino.y + dino.h;


    let superficies =
        obtenerSuperficies(x);


    let mejor =
        superficies[0];


    let mejorDist =
        Math.abs(
            bottomDino -
            mejor.y
        );


    for (let i = 1; i < superficies.length; i++) {

        let distancia =
            Math.abs(
                bottomDino -
                superficies[i].y
            );


        if (distancia < mejorDist) {

            mejor =
                superficies[i];

            mejorDist =
                distancia;
        }
    }


    return mejor.ruta;
}


// ============================================================
// INICIO
// ============================================================

function iniciarJuego() {

    dino = {

        x: 0,

        y: 200,

        w: 40,
        h: 40,

        vy: 0,

        enAire: false,

        propulsado: false,

        distPropulsion: 0,

        ruta: "main"
    };


    cuestasCompletadas = 0;

    nivel = 1;

    difDinamica = 0;

    fAcu = 0;

    pedosAcu = 0;

    sidras = 0;

    juegoActivo = true;

    cameraY = 0;


    document.getElementById(
        "game-over"
    ).style.display = "none";


    generarCuesta(
        0,
        300
    );


    actualizarUI();

    loop();
}


// ============================================================
// PROPULSIÓN
// ============================================================

function activarPropulsion() {

    if (
        pedosAcu > 0 &&
        !dino.propulsado
    ) {

        dino.propulsado = true;

        dino.distPropulsion =
            pedosAcu *
            DISTANCIA_PEDO;


        pedosAcu = 0;

        actualizarUI();
    }
}


// ============================================================
// SALTO
// ============================================================
//
// No permitimos doble salto.
//
// Esto hace que cada salto tenga que partir desde un camino
// real y siempre haya una superficie de aterrizaje.
// ============================================================

function salto() {

    if (
        !dino.propulsado &&
        !dino.enAire
    ) {

        dino.vy =
            FUERZA_SALTO;

        dino.enAire = true;
    }
}


// ============================================================
// CAÍDA RÁPIDA
// ============================================================

function caidaRapida() {

    if (dino.enAire) {

        dino.vy += 10;

        return;
    }


    // Si estamos arriba y existe una apertura,
    // el botón ABAJO permite iniciar la caída.
    if (
        dino.ruta === "top" &&
        estaEnAperturaSuperior(dino.x)
    ) {

        dino.enAire = true;

        dino.vy = 3;
    }
}


// ============================================================
// CONTROLES
// ============================================================

canvas.addEventListener(
    "touchstart",
    (e) => {

        e.preventDefault();

        salto();
    }
);


canvas.addEventListener(
    "click",
    () => {

        salto();
    }
);


document.getElementById(
    "btn-drop"
).addEventListener(
    "touchstart",
    (e) => {

        e.preventDefault();

        caidaRapida();
    }
);


document.getElementById(
    "btn-drop"
).addEventListener(
    "mousedown",
    (e) => {

        e.stopPropagation();

        caidaRapida();
    }
);


document.getElementById(
    "btn-pedo"
).addEventListener(
    "touchstart",
    (e) => {

        e.preventDefault();

        activarPropulsion();
    }
);


document.getElementById(
    "btn-pedo"
).addEventListener(
    "mousedown",
    (e) => {

        e.stopPropagation();

        activarPropulsion();
    }
);


document.addEventListener(
    "keydown",
    (e) => {

        if (
            e.code === "ArrowUp" ||
            e.code === "Space"
        ) {

            salto();
        }


        if (
            e.code === "ArrowDown"
        ) {

            caidaRapida();
        }


        if (
            e.code === "KeyF"
        ) {

            activarPropulsion();
        }
    }
);


// ============================================================
// UI
// ============================================================

function actualizarUI() {

    document.getElementById(
        "sidras"
    ).innerText = sidras;


    document.getElementById(
        "fabadas"
    ).innerText = fAcu;


    document.getElementById(
        "pedos"
    ).innerText = pedosAcu;


    document.getElementById(
        "nivel"
    ).innerText = nivel;


    document.getElementById(
        "dif"
    ).innerText =
        difDinamica.toFixed(1);
}


// ============================================================
// FINAL DE UNA CUESTA
// ============================================================

function procesarFinalCuesta() {

    // Elegimos el camino en el que realmente está el dino.
    let rutaFinal;


    if (dino.enAire) {

        rutaFinal =
            obtenerRutaMasCercana();

    } else {

        rutaFinal =
            dino.ruta;
    }


    if (
        rutaFinal !== "top" &&
        rutaFinal !== "bottom"
    ) {

        rutaFinal = "bottom";
    }


    let yFinal =
        obtenerYCamino(
            rutaFinal,
            slope.branchEndX
        );


    // Nunca dejamos al dino sin suelo.
    dino.x =
        slope.branchEndX;


    dino.y =
        yFinal -
        dino.h;


    dino.vy = 0;

    dino.enAire = false;

    dino.ruta = "main";


    cuestasCompletadas++;


    if (
        cuestasCompletadas % 10 === 0
    ) {

        nivel++;
    }


    generarCuesta(
        slope.branchEndX,
        yFinal
    );


    actualizarUI();
}


// ============================================================
// COLISIÓN
// ============================================================

function colision(r1, r2) {

    return !(
        r2.x > r1.x + r1.w ||
        r2.x + r2.w < r1.x ||
        r2.y > r1.y + r1.h ||
        r2.y + r2.h < r1.y
    );
}


// ============================================================
// ACTUALIZAR SUELO / SALTO
// ============================================================
//
// Nunca buscamos "caer al vacío".
//
// Si el personaje está cayendo:
//     - primero comprobamos camino superior
//     - después camino inferior
//
// Si el superior no existe por una apertura:
//     el inferior sigue existiendo y lo recoge.
// ============================================================

function actualizarFisicaSuelo(prevBottom) {

    let superficies =
        obtenerSuperficies(
            dino.x
        );


    // --------------------------------------------------------
    // DINO EN EL AIRE
    // --------------------------------------------------------

    if (dino.enAire) {

        if (dino.vy >= 0) {

            let mejorSuperficie = null;


            for (
                let i = 0;
                i < superficies.length;
                i++
            ) {

                let s =
                    superficies[i];


                // Solo aterrizamos si el dino estaba
                // por encima de la superficie en el frame anterior.
                if (
                    prevBottom <= s.y + 8 &&
                    dino.y + dino.h >= s.y
                ) {

                    if (
                        mejorSuperficie === null ||
                        s.y < mejorSuperficie.y
                    ) {

                        mejorSuperficie =
                            s;
                    }
                }
            }


            if (
                mejorSuperficie !== null
            ) {

                dino.y =
                    mejorSuperficie.y -
                    dino.h;


                dino.vy = 0;

                dino.enAire = false;

                dino.ruta =
                    mejorSuperficie.ruta;

                return;
            }
        }


        return;
    }


    // --------------------------------------------------------
    // DINO EN EL SUELO
    // --------------------------------------------------------

    let superficieActual = null;


    // Si estamos arriba y entramos en una apertura,
    // el camino superior deja de existir.
    if (
        dino.ruta === "top" &&
        estaEnAperturaSuperior(dino.x)
    ) {

        dino.enAire = true;

        dino.vy = 2;

        return;
    }


    // Buscamos la superficie correspondiente a la ruta actual.
    for (
        let i = 0;
        i < superficies.length;
        i++
    ) {

        if (
            superficies[i].ruta ===
            dino.ruta
        ) {

            superficieActual =
                superficies[i];

            break;
        }
    }


    // Si el camino actual ha terminado,
    // usamos automáticamente el inferior.
    if (
        superficieActual === null
    ) {

        for (
            let i = 0;
            i < superficies.length;
            i++
        ) {

            if (
                superficies[i].ruta ===
                "bottom"
            ) {

                superficieActual =
                    superficies[i];

                break;
            }
        }
    }


    // Seguridad absoluta:
    // si por cualquier razón no encontramos ruta,
    // utilizamos la superficie más baja disponible.
    if (
        superficieActual === null &&
        superficies.length > 0
    ) {

        superficieActual =
            superficies[0];
    }


    if (
        superficieActual !== null
    ) {

        dino.y =
            superficieActual.y -
            dino.h;


        dino.ruta =
            superficieActual.ruta;
    }
}


// ============================================================
// LOOP PRINCIPAL
// ============================================================

function loop() {

    if (!juegoActivo)
        return;


    let velTotal =
        baseVelocidad +
        nivel * 0.4 +
        difDinamica * 0.2;


    // --------------------------------------------------------
    // TURBO
    // --------------------------------------------------------

    if (
        slope.tieneTurbo &&
        dino.x > slope.turboStart &&
        dino.x < slope.turboEnd &&
        !dino.propulsado
    ) {

        velTotal *= 1.8;
    }


    // --------------------------------------------------------
    // PROPULSIÓN
    // --------------------------------------------------------

    if (dino.propulsado) {

        velTotal *= 3.5;

        dino.distPropulsion -=
            velTotal;


        if (
            dino.distPropulsion <= 0
        ) {

            dino.propulsado = false;
        }
    }


    // --------------------------------------------------------
    // MOVIMIENTO HORIZONTAL
    // --------------------------------------------------------

    dino.x += velTotal;


    // --------------------------------------------------------
    // SALTO
    // --------------------------------------------------------

    let prevBottom =
        dino.y + dino.h;


    if (dino.enAire) {

        dino.y += dino.vy;

        dino.vy += GRAVEDAD;
    }


    // --------------------------------------------------------
    // FÍSICA DE CAMINOS
    // --------------------------------------------------------

    actualizarFisicaSuelo(
        prevBottom
    );


    // --------------------------------------------------------
    // TRANSICIÓN A LA SIGUIENTE CUESTA
    // --------------------------------------------------------
    //
    // La nueva cuesta empieza antes de que pueda existir
    // una zona sin suelo.
    //
    // Así, incluso si el dino está saltando al llegar al
    // final, la siguiente superficie ya existe.
    // --------------------------------------------------------

    if (
        dino.x >=
        slope.branchEndX - 80
    ) {

        procesarFinalCuesta();
    }


    // --------------------------------------------------------
    // OBSTÁCULOS Y OBJETOS
    // --------------------------------------------------------

    entidades.forEach(
        e => {

            if (!e.activo)
                return;


            let eVel = 0;


            if (
                e.tipo === "obs_lento"
            ) {

                eVel =
                    velTotal * 0.4;
            }


            if (
                e.tipo === "obs_rapido"
            ) {

                eVel =
                    -(velTotal + difDinamica);
            }


            e.x += eVel;


            let yCamino;


            if (e.ruta === "main") {

                yCamino =
                    obtenerYCamino(
                        "main",
                        e.x
                    );

            } else {

                yCamino =
                    obtenerYCamino(
                        e.ruta,
                        e.x
                    );
            }


            e.y =
                yCamino -
                e.h;


            // No colocamos físicamente objetos dentro
            // de una apertura superior.
            if (
                e.ruta === "top" &&
                estaEnAperturaSuperior(e.x)
            ) {

                e.activo = false;

                return;
            }


            let cajaDino = {

                x: dino.x,
                y: dino.y,
                w: dino.w,
                h: dino.h
            };


            let cajaE = {

                x: e.x,
                y: e.y,
                w: e.w,
                h: e.h
            };


            if (
                colision(
                    cajaDino,
                    cajaE
                )
            ) {

                if (
                    e.tipo === "sidra"
                ) {

                    sidras++;

                    e.activo = false;

                    actualizarUI();

                } else if (
                    e.tipo === "fabada"
                ) {

                    fAcu++;

                    e.activo = false;


                    if (
                        fAcu >=
                        CONST_FABADA
                    ) {

                        pedosAcu++;

                        fAcu = 0;
                    }


                    actualizarUI();

                } else if (
                    e.tipo.startsWith(
                        "obs_"
                    )
                ) {

                    if (
                        dino.propulsado
                    ) {

                        e.activo = false;

                    } else {

                        juegoActivo = false;

                        document.getElementById(
                            "final-sidras"
                        ).innerText =
                            sidras;


                        document.getElementById(
                            "game-over"
                        ).style.display =
                            "block";
                    }
                }
            }
        }
    );


    // --------------------------------------------------------
    // CÁMARA
    // --------------------------------------------------------
    //
    // La cámara no sigue únicamente al dino.
    //
    // Mantiene visibles las dos rutas.
    // Esto evita que un salto haga desaparecer el camino
    // de la pantalla.
    // --------------------------------------------------------

    let refRuta;


    if (
        dino.x < slope.splitX
    ) {

        refRuta =
            obtenerYCamino(
                "main",
                dino.x
            );

    } else {

        let topY =
            obtenerYCamino(
                "top",
                dino.x
            );


        let bottomY =
            obtenerYCamino(
                "bottom",
                dino.x
            );


        let centro =
            (topY + bottomY) / 2;


        let dinoCentro =
            dino.y +
            dino.h / 2;


        let diferencia =
            dinoCentro -
            centro;


        // La cámara puede acompañar al salto,
        // pero nunca desplaza completamente las dos rutas.
        diferencia =
            Math.max(
                -110,
                Math.min(
                    110,
                    diferencia
                )
            );


        refRuta =
            centro + diferencia;
    }


    let targetCamY =
        canvas.height * 0.58 -
        refRuta;


    cameraY +=
        (
            targetCamY -
            cameraY
        ) * 0.10;


    // --------------------------------------------------------
    // DIBUJAR
    // --------------------------------------------------------

    dibujarEscena();


    if (juegoActivo) {

        frameId =
            requestAnimationFrame(
                loop
            );
    }
}


// ============================================================
// DIBUJAR ESCENA
// ============================================================

function dibujarEscena() {

    // --------------------------------------------------------
    // FONDO
    // --------------------------------------------------------

    ctx.save();

    ctx.setTransform(
        1,
        0,
        0,
        1,
        0,
        0
    );


    if (dino.propulsado) {

        ctx.fillStyle =
            "#ffb142";

    } else {

        ctx.fillStyle =
            "#87CEEB";
    }


    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    ctx.restore();


    // --------------------------------------------------------
    // MUNDO
    // --------------------------------------------------------

    ctx.save();


    ctx.translate(
        200 - dino.x,
        cameraY
    );


    // ========================================================
    // CAMINO PRINCIPAL
    // ========================================================

    ctx.lineWidth = 14;

    ctx.strokeStyle = "#27ae60";

    ctx.lineCap = "round";

    ctx.beginPath();

    ctx.moveTo(
        slope.x1,
        slope.y1
    );

    ctx.lineTo(
        slope.splitX,
        slope.splitY
    );

    ctx.stroke();


    // ========================================================
    // CAMINOS SUPERIOR E INFERIOR
    // ========================================================

    //
    // Los dibujamos desde el punto de bifurcación.
    //
    // Esto hace que desde el camino original se pueda ver
    // perfectamente hacia dónde va cada camino.
    //


    // --------------------------------------------------------
    // CAMINO SUPERIOR
    // --------------------------------------------------------

    ctx.strokeStyle =
        "#2980b9";


    if (
        slope.tieneAperturaSuperior
    ) {

        // Primer tramo antes de la apertura.
        ctx.beginPath();

        ctx.moveTo(
            slope.splitX,
            slope.topStartY
        );

        ctx.lineTo(
            slope.aperturaX1,
            obtenerYCamino(
                "top",
                slope.aperturaX1
            )
        );

        ctx.stroke();


        // Segundo tramo después de la apertura.
        ctx.beginPath();

        ctx.moveTo(
            slope.aperturaX2,
            obtenerYCamino(
                "top",
                slope.aperturaX2
            )
        );

        ctx.lineTo(
            slope.branchEndX,
            slope.topEndY
        );

        ctx.stroke();


        // Indicador visual de la apertura.
        let yApertura =
            obtenerYCamino(
                "top",
                (
                    slope.aperturaX1 +
                    slope.aperturaX2
                ) / 2
            );


        ctx.save();

        ctx.strokeStyle =
            "#e74c3c";

        ctx.lineWidth = 5;

        ctx.setLineDash([
            10,
            8
        ]);


        ctx.beginPath();

        ctx.moveTo(
            slope.aperturaX1,
            yApertura + 12
        );

        ctx.lineTo(
            slope.aperturaX2,
            yApertura + 12
        );

        ctx.stroke();


        ctx.restore();


    } else {

        ctx.beginPath();

        ctx.moveTo(
            slope.splitX,
            slope.topStartY
        );

        ctx.lineTo(
            slope.branchEndX,
            slope.topEndY
        );

        ctx.stroke();
    }


    // --------------------------------------------------------
    // CAMINO INFERIOR
    // --------------------------------------------------------

    ctx.strokeStyle =
        "#c0392b";


    ctx.beginPath();

    ctx.moveTo(
        slope.splitX,
        slope.bottomStartY
    );

    ctx.lineTo(
        slope.branchEndX,
        slope.bottomEndY
    );

    ctx.stroke();


    // ========================================================
    // SEÑALES SI / NO
    // ========================================================

    ctx.fillStyle = "#fff";

    ctx.font =
        "bold 28px Arial";


    ctx.fillText(
        slope.topSign,
        slope.splitX + 50,
        slope.topStartY - 25
    );


    ctx.fillText(
        slope.bottomSign,
        slope.splitX + 50,
        slope.bottomStartY - 25
    );


    // ========================================================
    // PREGUNTA
    // ========================================================

    ctx.fillStyle =
        "rgba(0,0,0,0.72)";


    ctx.fillRect(
        slope.splitX - 270,
        slope.splitY - 240,
        380,
        55
    );


    ctx.fillStyle =
        "#f1c40f";


    ctx.font =
        "bold 30px Arial";


    ctx.fillText(
        slope.pregunta,
        slope.splitX - 250,
        slope.splitY - 202
    );


    // ========================================================
    // TURBO
    // ========================================================

    if (
        slope.tieneTurbo
    ) {

        let turboY =
            obtenerYCamino(
                "main",
                slope.turboStart
            );


        ctx.fillStyle =
            "#e74c3c";


        ctx.fillRect(
            slope.turboStart - 40,
            turboY - 80,
            60,
            60
        );


        ctx.fillStyle =
            "#fff";


        ctx.font =
            "bold 40px Arial";


        ctx.fillText(
            "⚡",
            slope.turboStart - 30,
            turboY - 35
        );


        ctx.lineWidth = 14;

        ctx.strokeStyle =
            "#e74c3c";


        ctx.beginPath();

        ctx.moveTo(
            slope.turboStart,
            turboY
        );

        ctx.lineTo(
            slope.turboEnd,
            obtenerYCamino(
                "main",
                slope.turboEnd
            )
        );

        ctx.stroke();
    }


    // ========================================================
    // ENTIDADES
    // ========================================================

    entidades.forEach(
        e => {

            if (
                e.activo
            ) {

                dibujarSprite(
                    ctx,
                    e.tipo,
                    e.x,
                    e.y,
                    e.w,
                    e.h
                );
            }
        }
    );


    // ========================================================
    // DINO
    // ========================================================

    ctx.save();


    if (
        dino.propulsado
    ) {

        ctx.fillStyle =
            "rgba(46, 204, 113, 0.5)";


        ctx.fillRect(
            dino.x - 60,
            dino.y,
            80,
            dino.h
        );
    }


    dibujarSprite(
        ctx,
        "dino",
        dino.x,
        dino.y,
        dino.w,
        dino.h
    );


    ctx.restore();


    ctx.restore();
}


// ============================================================
// REINICIAR
// ============================================================

window.reiniciarJuego =
    function () {

        iniciarJuego();
    };


// ============================================================
// ARRANQUE
// ============================================================

iniciarJuego();

</script>

</body>
</html>
"""


# ============================================================
# INSERTAR IMÁGENES
# ============================================================

html_juego = (
    html_juego
    .replace("__DINO__", imagenes["dino"])
    .replace("__OBS_FIJO__", imagenes["obs_fijo"])
    .replace("__OBS_LENTO__", imagenes["obs_lento"])
    .replace("__OBS_RAPIDO__", imagenes["obs_rapido"])
    .replace("__FABADA__", imagenes["fabada"])
    .replace("__SIDRA__", imagenes["sidra"])
)


# ============================================================
# MOSTRAR JUEGO
# ============================================================

components.html(
    html_juego,
    height=600
)

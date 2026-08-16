import base64
import os
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="DinoJuan - Minijuego",
    layout="wide"
)


# ============================================================
# IMÁGENES
# ============================================================

def obtener_imagen_base64(nombre_archivo, color_hex_fallback):
    folder = "img"
    ruta = os.path.join(folder, nombre_archivo)

    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return (
                "data:image/png;base64,"
                + base64.b64encode(f.read()).decode()
            )

    if os.path.exists(folder):
        pngs = [
            f for f in os.listdir(folder)
            if f.endswith(".png")
        ]

        if pngs:
            with open(os.path.join(folder, pngs[0]), "rb") as f:
                return (
                    "data:image/png;base64,"
                    + base64.b64encode(f.read()).decode()
                )

    return f"COLOR:{color_hex_fallback}"


imagenes = {
    "dino": obtener_imagen_base64(
        "oviedo_dino.png",
        "#2ecc71"
    ),

    "obs_fijo": obtener_imagen_base64(
        "ubres_dino.png",
        "#e74c3c"
    ),

    "obs_lento": obtener_imagen_base64(
        "carne_dino.png",
        "#e67e22"
    ),

    "obs_rapido": obtener_imagen_base64(
        "mirete_dino.png",
        "#8e44ad"
    ),

    "obs_extra": obtener_imagen_base64(
        "pwc_dino.png",
        "#c0392b"
    ),

    "fabada": obtener_imagen_base64(
        "fabada.png",
        "#d35400"
    ),

    "sidra": obtener_imagen_base64(
        "sidra.png",
        "#f1c40f"
    )
}


# ============================================================
# JUEGO
# ============================================================

html_juego = f"""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width,
initial-scale=1.0,
maximum-scale=1.0,
user-scalable=no">

<style>

body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: 'Segoe UI', sans-serif;
    background: #222;
    -webkit-user-select: none;
    user-select: none;
}}

#game-container {{
    position: relative;
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}}

canvas {{
    display: block;
    width: 100%;
    height: 500px;
    background:
        linear-gradient(
            to bottom,
            #87CEEB,
            #E0F6FF
        );
    cursor: pointer;
}}

#ui-layer {{
    position: absolute;
    top: 10px;
    left: 15px;
    color: #333;
    font-weight: bold;
    font-size: 18px;
    pointer-events: none;
    text-shadow: 1px 1px 2px white;
    z-index: 10;
}}

#game-over {{
    display: none;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0,0,0,0.88);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    border: 3px solid #f1c40f;
    z-index: 20;
}}

.btn {{
    background: #f1c40f;
    color: #000;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 15px;
    font-size: 16px;
}}

#controls {{
    position: absolute;
    bottom: 20px;
    width: 100%;
    display: flex;
    justify-content: space-around;
    pointer-events: none;
    z-index: 10;
}}

.ctrl-btn {{
    pointer-events: auto;
    background: rgba(255,255,255,0.8);
    border: 2px solid #333;
    border-radius: 12px;
    padding: 12px 25px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}}

#btn-pedo {{
    background: rgba(211, 84, 0, 0.9);
    color: white;
    border-color: #e67e22;
}}

</style>

</head>


<body>

<div id="game-container">

<div id="ui-layer">

<div>
🍏 Sidras:
<span id="sidras">0</span>

|

🥫 Fabadas:
<span id="fabadas">0</span>/3

→

💨 Pedos:
<span id="pedos">0</span>
</div>

<div style="font-size:14px;margin-top:5px;color:#555;">

🏆 Nivel:
<span id="nivel">1</span>

|

📈 Dificultad Extra:
<span id="dif">0.0</span>

</div>

</div>


<canvas id="gameCanvas"></canvas>


<div id="controls">

<div
class="ctrl-btn"
id="btn-drop">

⬇️ CAER / ABAJO

</div>


<div
class="ctrl-btn"
id="btn-pedo">

💨 SOLTAR PEDO

</div>

</div>


<div id="game-over">

<h1 style="margin-top:0;">
💥 GAME OVER
</h1>

<h2>

🍏 Sidras Totales:

<span
id="final-sidras"
style="color:#f1c40f;">

0

</span>

</h2>

<p>
Has tropezado con un obstáculo.
</p>

<button
class="btn"
onclick="reiniciarJuego()">

Volver a Jugar

</button>

</div>

</div>


<script>


// ============================================================
// CANVAS
// ============================================================

const canvas =
    document.getElementById("gameCanvas");

const ctx =
    canvas.getContext("2d");

canvas.width = 900;
canvas.height = 500;


// ============================================================
// IMÁGENES
// ============================================================

const IMG_DATA = {{

    dino: "{imagenes['dino']}",

    obs_fijo: "{imagenes['obs_fijo']}",

    obs_lento: "{imagenes['obs_lento']}",

    obs_rapido: "{imagenes['obs_rapido']}",

    obs_extra: "{imagenes['obs_extra']}",

    fabada: "{imagenes['fabada']}",

    sidra: "{imagenes['sidra']}"
}};


const imagenesCargadas = {{}};


for (
    let key in IMG_DATA
) {{

    if (
        !IMG_DATA[key].startsWith("COLOR:")
    ) {{

        let img = new Image();

        img.src = IMG_DATA[key];

        imagenesCargadas[key] = img;

    }} else {{

        imagenesCargadas[key] =
            IMG_DATA[key].split(":")[1];
    }}
}}


function dibujarSprite(
    ctx,
    key,
    x,
    y,
    w,
    h
) {{

    let obj =
        imagenesCargadas[key];

    if (
        typeof obj === "string"
    ) {{

        ctx.fillStyle = obj;

        ctx.fillRect(
            x,
            y,
            w,
            h
        );

    }} else if (
        obj &&
        obj.complete &&
        obj.naturalWidth > 0
    ) {{

        ctx.drawImage(
            obj,
            x,
            y,
            w,
            h
        );

    }} else {{

        ctx.fillStyle = "#000";

        ctx.fillRect(
            x,
            y,
            w,
            h
        );
    }}
}


// ============================================================
// CONFIGURACIÓN FÍSICA
// ============================================================

const GRAVEDAD = 0.65;

const FUERZA_SALTO = -15;

const ALTURA_MAX_SALTO =
    (
        FUERZA_SALTO *
        FUERZA_SALTO
    ) /
    (
        2 *
        GRAVEDAD
    );


// Distancia máxima horizontal aproximada
// de un salto normal.

const TIEMPO_SALTO =
    (
        -2 *
        FUERZA_SALTO
    ) /
    GRAVEDAD;

const DISTANCIA_SALTO =
    TIEMPO_SALTO *
    4.5;


// ============================================================
// VARIABLES
// ============================================================

let juegoActivo = true;

let frameId = null;

let cameraY = 0;

let nivel = 1;

let difDinamica = 0;

let cuestasCompletadas = 0;

let baseVelocidad = 3.5;

let fAcu = 0;

let pedosAcu = 0;

let sidras = 0;


const CONST_FABADA = 3;

const DISTANCIA_PEDO = 2500;


// ============================================================
// DINO
// ============================================================

let dino = {{

    x: 0,

    y: 260,

    w: 40,

    h: 40,

    vy: 0,

    enAire: false,

    propulsado: false,

    distPropulsion: 0,

    roadId: null,

    // Para saber de qué bifurcación procede
    parentNodeId: null
}};


// ============================================================
// ÁRBOL DE CAMINOS
// ============================================================
//
// Cada "road" es un tramo infinito en el sentido lógico:
//
//     road
//       |
//       +---- top road
//       |
//       +---- bottom road
//
// Los hijos ya existen antes de que el jugador llegue
// a la bifurcación.
//
// Por tanto nunca aparece un camino de repente.
// ============================================================

let roads = [];

let nodes = [];

let nextRoadId = 1;

let nextNodeId = 1;


// ============================================================
// ENTIDADES
// ============================================================

let entidades = [];


// ============================================================
// UTILIDADES
// ============================================================

function clamp(
    valor,
    minimo,
    maximo
) {{

    return Math.max(
        minimo,
        Math.min(
            maximo,
            valor
        )
    );
}}


function distanciaVertical(
    y1,
    y2
) {{

    return Math.abs(
        y1 - y2
    );
}}


// ============================================================
// PREGUNTAS
// ============================================================

function generarPregunta(
    nivelReal
) {{

    let ops = ["+", "-"];

    if (
        nivelReal > 2
    )
        ops.push("*");

    if (
        nivelReal > 4
    )
        ops.push("/");


    let op =
        ops[
            Math.floor(
                Math.random() *
                ops.length
            )
        ];


    let b =
        Math.floor(
            Math.random() *
            8 *
            nivelReal
        ) + 1;


    let c =
        Math.floor(
            Math.random() *
            8 *
            nivelReal
        ) + 1;


    let resultado = 0;


    if (op === "+")
        resultado = b + c;

    if (op === "-")
        resultado = b - c;

    if (op === "*")
        resultado = b * c;

    if (op === "/") {{

        resultado = b;

        b = b * c;
    }}


    let correcta =
        Math.random() > 0.5;


    let mostrado =
        correcta
            ? resultado
            : resultado +
              (
                Math.random() > 0.5
                    ? 1
                    : -1
              ) *
              (
                Math.floor(
                    Math.random() * 4
                ) + 1
              );


    return {{

        texto:
            b +
            " " +
            op +
            " " +
            c +
            " = " +
            mostrado,

        correcta:
            correcta
                ? "SI"
                : "NO"
    }};
}}


// ============================================================
// CREAR ROAD
// ============================================================

function crearRoad(
    x1,
    y1,
    x2,
    y2,
    parentNodeId,
    tipo,
    nivelRoad
) {{

    const pendiente =
        (
            y2 - y1
        ) /
        (
            x2 - x1
        );


    const road = {{

        id: nextRoadId++,

        x1: x1,

        y1: y1,

        x2: x2,

        y2: y2,

        pendiente: pendiente,

        angle:
            Math.atan(
                pendiente
            ),

        parentNodeId:
            parentNodeId,

        tipo:
            tipo,

        nivel:
            nivelRoad,

        childNodeId:
            null,

        activo: true
    }};


    roads.push(road);

    return road;
}}


// ============================================================
// Y DE ROAD
// ============================================================

function obtenerYEnRoad(
    road,
    x
) {{

    if (!road)
        return 0;


    return (
        road.y1 +
        road.pendiente *
        (
            x - road.x1
        )
    );
}}


// ============================================================
// CREAR BIFURCACIÓN
// ============================================================
//
// La bifurcación NO es un punto en el que los caminos
// desaparecen.
//
// Los dos hijos empiezan en el mismo punto de decisión
// y se separan progresivamente.
//
// A partir de ahí cada uno tiene su propia siguiente
// bifurcación.
// ============================================================

function crearBifurcacion(
    road
) {{

    if (
        road.childNodeId !== null
    ) {{

        return nodes.find(
            n =>
                n.id ===
                road.childNodeId
        );
    }}


    const x =
        road.x2;

    const y =
        road.y2;


    const longitud =
        1500 +
        Math.random() *
        700;


    // Separación inicial muy pequeña:
    // los caminos nacen de la bifurcación.
    const separacion =
        12;


    const nivelReal =
        Math.max(
            1,
            nivel +
            difDinamica
        );


    // Pendiente base muy suave.
    const baseAngle =
        clamp(
            (
                Math.random() *
                2 -
                1
            ) *
            (
                4 +
                nivelReal * 0.7
            ),
            -9,
            9
        ) *
        Math.PI /
        180;


    // Diferencia entre ambos caminos.
    //
    // Siempre hay una separación progresiva.
    // Nunca se cruzan.
    const diferencia =
        (
            1.2 +
            Math.random() *
            2.4
        ) *
        Math.PI /
        180;


    let topAngle =
        baseAngle -
        diferencia;


    let bottomAngle =
        baseAngle +
        diferencia;


    // Evitar ángulos extremos.
    topAngle =
        clamp(
            topAngle,
            -10 * Math.PI / 180,
            10 * Math.PI / 180
        );


    bottomAngle =
        clamp(
            bottomAngle,
            -10 * Math.PI / 180,
            10 * Math.PI / 180
        );


    const topY1 =
        y - separacion;


    const bottomY1 =
        y + separacion;


    const topY2 =
        topY1 +
        Math.tan(topAngle) *
        longitud;


    const bottomY2 =
        bottomY1 +
        Math.tan(bottomAngle) *
        longitud;


    // --------------------------------------------------------
    // ASEGURAR QUE NO SE CRUCEN
    // --------------------------------------------------------
    //
    // top debe estar siempre por encima de bottom.
    //
    // Si por azar la geometría los acercara demasiado,
    // corregimos la pendiente.
    // --------------------------------------------------------

    const separacionFinal =
        bottomY2 -
        topY2;


    if (
        separacionFinal < 80
    ) {{

        const correccion =
            (
                80 -
                separacionFinal
            ) /
            longitud;


        topAngle -=
            correccion / 2;

        bottomAngle +=
            correccion / 2;
    }}


    const topFinalY =
        topY1 +
        Math.tan(topAngle) *
        longitud;


    const bottomFinalY =
        bottomY1 +
        Math.tan(bottomAngle) *
        longitud;


    // --------------------------------------------------------
    // PREGUNTA
    // --------------------------------------------------------

    const pregunta =
        generarPregunta(
            nivelReal
        );


    const topSign =
        Math.random() > 0.5
            ? "SI"
            : "NO";


    const bottomSign =
        topSign === "SI"
            ? "NO"
            : "SI";


    // --------------------------------------------------------
    // APERTURA
    // --------------------------------------------------------
    //
    // Solo en el camino superior.
    //
    // Buscamos una zona donde la diferencia de altura sea
    // suficientemente pequeña para que desde abajo se pueda
    // saltar al superior.
    // --------------------------------------------------------

    let tieneApertura =
        false;

    let aperturaX1 = 0;
    let aperturaX2 = 0;


    const posiblesX = [];


    for (
        let i = 0;
        i <= 10;
        i++
    ) {{

        const px =
            x +
            longitud *
            (
                0.15 +
                0.65 *
                (
                    i / 10
                )
            );


        const progreso =
            (
                px - x
            ) /
            longitud;


        const pyTop =
            topY1 +
            Math.tan(topAngle) *
            (
                px - x
            );


        const pyBottom =
            bottomY1 +
            Math.tan(bottomAngle) *
            (
                px - x
            );


        const separacionActual =
            pyBottom -
            pyTop;


        if (
            separacionActual <=
            ALTURA_MAX_SALTO * 0.92
        ) {{

            posiblesX.push(
                px
            );
        }}
    }}


    if (
        posiblesX.length > 0 &&
        Math.random() < 0.75
    ) {{

        tieneApertura = true;


        const centro =
            posiblesX[
                Math.floor(
                    Math.random() *
                    posiblesX.length
                )
            ];


        const ancho =
            90 +
            Math.random() *
            50;


        aperturaX1 =
            centro -
            ancho / 2;


        aperturaX2 =
            centro +
            ancho / 2;
    }}


    // --------------------------------------------------------
    // NODE
    // --------------------------------------------------------

    const node = {{

        id: nextNodeId++,

        x: x,

        y: y,

        parentRoadId:
            road.id,

        topRoadId: null,

        bottomRoadId: null,

        pregunta:
            pregunta.texto,

        correcta:
            pregunta.correcta,

        topSign:
            topSign,

        bottomSign:
            bottomSign,

        tieneApertura:
            tieneApertura,

        aperturaX1:
            aperturaX1,

        aperturaX2:
            aperturaX2,

        resuelto:
            false
    }};


    nodes.push(node);


    // --------------------------------------------------------
    // CAMINO SUPERIOR
    // --------------------------------------------------------

    const topRoad =
        crearRoad(
            x,
            topY1,
            x + longitud,
            topFinalY,
            node.id,
            "top",
            nivelRoad + 1
        );


    // --------------------------------------------------------
    // CAMINO INFERIOR
    // --------------------------------------------------------

    const bottomRoad =
        crearRoad(
            x,
            bottomY1,
            x + longitud,
            bottomFinalY,
            node.id,
            "bottom",
            nivelRoad + 1
        );


    node.topRoadId =
        topRoad.id;

    node.bottomRoadId =
        bottomRoad.id;


    road.childNodeId =
        node.id;


    // --------------------------------------------------------
    // GENERAR TAMBIÉN LA SIGUIENTE GENERACIÓN
    // --------------------------------------------------------
    //
    // Esto es fundamental.
    //
    // Cuando el jugador vea una bifurcación,
    // también verá caminos que salen de la siguiente.
    // --------------------------------------------------------

    crearBifurcacion(topRoad);

    crearBifurcacion(bottomRoad);


    generarEntidadesParaRoad(
        topRoad
    );

    generarEntidadesParaRoad(
        bottomRoad
    );


    return node;
}}


// ============================================================
// GENERACIÓN DE ENTIDADES
// ============================================================

function generarEntidadesParaRoad(
    road
) {{

    // No llenamos demasiado los caminos.
    const cantidad =
        Math.floor(
            Math.max(
                1,
                nivel * 0.7
            )
        );


    for (
        let i = 0;
        i < cantidad;
        i++
    ) {{

        const margen = 250;


        const x =
            road.x1 +
            margen +
            Math.random() *
            Math.max(
                100,
                road.x2 -
                road.x1 -
                margen * 2
            );


        // Nunca poner un objeto en la zona
        // exacta de bifurcación.
        if (
            x <
            road.x1 + 180
        ) {{
            continue;
        }}


        let tipo;


        const r =
            Math.random();


        if (
            r < 0.42
        ) {{

            tipo =
                "obs_fijo";

        }} else if (
            r < 0.70
        ) {{

            tipo =
                "obs_lento";

        }} else {{

            tipo =
                "obs_rapido";
        }}


        entidades.push({{

            x: x,

            roadId:
                road.id,

            tipo:
                tipo,

            activo:
                true,

            w:
                40,

            h:
                40
        }});
    }}


    // --------------------------------------------------------
    // SIDRAS
    // --------------------------------------------------------

    if (
        Math.random() < 0.75
    ) {{

        const x =
            road.x1 +
            300 +
            Math.random() *
            Math.max(
                100,
                road.x2 -
                road.x1 -
                500
            );


        entidades.push({{

            x: x,

            roadId:
                road.id,

            tipo:
                "sidra",

            activo:
                true,

            w:
                30,

            h:
                30
        }});
    }}


    // --------------------------------------------------------
    // FABADA
    // --------------------------------------------------------

    if (
        Math.random() < 0.22
    ) {{

        const x =
            road.x1 +
            400 +
            Math.random() *
            Math.max(
                100,
                road.x2 -
                road.x1 -
                600
            );


        entidades.push({{

            x: x,

            roadId:
                road.id,

            tipo:
                "fabada",

            activo:
                true,

            w:
                35,

            h:
                35
        }});
    }}
}}


// ============================================================
// CREACIÓN INICIAL DEL MUNDO
// ============================================================

function crearMundoInicial() {{

    roads = [];

    nodes = [];

    entidades = [];

    nextRoadId = 1;

    nextNodeId = 1;


    // Primer camino.
    //
    // Este camino no es "una cuesta que se acaba":
    // es el primer tramo de un árbol infinito.

    const roadInicial =
        crearRoad(
            0,
            300,
            1500,
            300,
            null,
            "main",
            0
        );


    dino.roadId =
        roadInicial.id;


    // Generamos la primera bifurcación
    // y varias generaciones por delante.

    crearBifurcacion(
        roadInicial
    );


    generarEntidadesParaRoad(
        roadInicial
    );
}}


// ============================================================
// BUSCAR ROAD
// ============================================================

function obtenerRoad(
    id
) {{

    return roads.find(
        r =>
            r.id === id
    );
}}


// ============================================================
// BUSCAR NODE
// ============================================================

function obtenerNode(
    id
) {{

    return nodes.find(
        n =>
            n.id === id
    );
}}


// ============================================================
// APERTURA DEL CAMINO SUPERIOR
// ============================================================

function estaEnApertura(
    node,
    x
) {{

    if (
        !node ||
        !node.tieneApertura
    ) {{
        return false;
    }}


    return (
        x >= node.aperturaX1 &&
        x <= node.aperturaX2
    );
}}


// ============================================================
// ¿EL DINO ESTÁ EN UNA APERTURA?
// ============================================================

function aperturaDelRoadActual() {{

    const road =
        obtenerRoad(
            dino.roadId
        );


    if (
        !road ||
        road.tipo !== "top"
    ) {{
        return null;
    }}


    const node =
        obtenerNode(
            road.parentNodeId
        );


    if (
        estaEnApertura(
            node,
            dino.x
        )
    ) {{
        return node;
    }}


    return null;
}}


// ============================================================
// OBTENER CAMINO INFERIOR DE UNA BIFURCACIÓN
// ============================================================

function obtenerBottomRoad(
    node
) {{

    return obtenerRoad(
        node.bottomRoadId
    );
}}


// ============================================================
// OBTENER SUPERFICIE INFERIOR
// ============================================================
//
// Esto permite que el camino inferior actúe siempre como
// "red de seguridad".
// ============================================================

function obtenerSuperficieInferior(
    node,
    x
) {{

    const bottom =
        obtenerBottomRoad(
            node
        );


    if (!bottom)
        return null;


    return obtenerYEnRoad(
        bottom,
        x
    );
}}


// ============================================================
// COLISIÓN
// ============================================================

function colision(
    a,
    b
) {{

    return !(
        b.x >
        a.x + a.w ||

        b.x + b.w <
        a.x ||

        b.y >
        a.y + a.h ||

        b.y + b.h <
        a.y
    );
}}


// ============================================================
// SALTO
// ============================================================

function salto() {{

    if (
        dino.propulsado
    ) {{
        return;
    }}


    if (
        !dino.enAire
    ) {{

        dino.vy =
            FUERZA_SALTO;

        dino.enAire =
            true;
    }}
}}


// ============================================================
// CAER RÁPIDO
// ============================================================

function caidaRapida() {{

    if (
        dino.enAire
    ) {{

        dino.vy += 10;

        return;
    }}


    const apertura =
        aperturaDelRoadActual();


    if (
        apertura
    ) {{

        dino.enAire =
            true;

        dino.vy =
            4;
    }}
}}


// ============================================================
// PEDO
// ============================================================

function activarPropulsion() {{

    if (
        pedosAcu > 0 &&
        !dino.propulsado
    ) {{

        dino.propulsado =
            true;

        dino.distPropulsion =
            pedosAcu *
            DISTANCIA_PEDO;

        pedosAcu = 0;

        actualizarUI();
    }}
}}


// ============================================================
// CONTROLES
// ============================================================

canvas.addEventListener(
    "touchstart",
    function(e) {{

        e.preventDefault();

        salto();
    }}
);


canvas.addEventListener(
    "click",
    function() {{

        salto();
    }}
);


document.getElementById(
    "btn-drop"
).addEventListener(
    "touchstart",
    function(e) {{

        e.preventDefault();

        caidaRapida();
    }}
);


document.getElementById(
    "btn-drop"
).addEventListener(
    "mousedown",
    function(e) {{

        e.stopPropagation();

        caidaRapida();
    }}
);


document.getElementById(
    "btn-pedo"
).addEventListener(
    "touchstart",
    function(e) {{

        e.preventDefault();

        activarPropulsion();
    }}
);


document.getElementById(
    "btn-pedo"
).addEventListener(
    "mousedown",
    function(e) {{

        e.stopPropagation();

        activarPropulsion();
    }}
);


document.addEventListener(
    "keydown",
    function(e) {{

        if (
            e.code === "ArrowUp" ||
            e.code === "Space"
        ) {{
            salto();
        }}


        if (
            e.code === "ArrowDown"
        ) {{
            caidaRapida();
        }}


        if (
            e.code === "KeyF"
        ) {{
            activarPropulsion();
        }}
    }}
);


// ============================================================
// ACTUALIZAR UI
// ============================================================

function actualizarUI() {{

    document.getElementById(
        "sidras"
    ).innerText =
        sidras;


    document.getElementById(
        "fabadas"
    ).innerText =
        fAcu;


    document.getElementById(
        "pedos"
    ).innerText =
        pedosAcu;


    document.getElementById(
        "nivel"
    ).innerText =
        nivel;


    document.getElementById(
        "dif"
    ).innerText =
        difDinamica.toFixed(1);
}}


// ============================================================
// ENTRAR EN UNA NUEVA RUTA
// ============================================================

function entrarEnRoad(
    road
) {{

    if (!road)
        return;


    if (
        dino.roadId ===
        road.id
    ) {{
        return;
    }}


    dino.roadId =
        road.id;


    // --------------------------------------------------------
    // Registrar la respuesta de la bifurcación
    // --------------------------------------------------------

    if (
        road.parentNodeId !== null
    ) {{

        const node =
            obtenerNode(
                road.parentNodeId
            );


        if (
            node &&
            !node.resuelto
        ) {{

            node.resuelto =
                true;


            const signo =
                road.tipo === "top"
                    ? node.topSign
                    : node.bottomSign;


            if (
                signo ===
                node.correcta
            ) {{

                difDinamica =
                    Math.max(
                        0,
                        difDinamica -
                        0.5
                    );

            }} else {{

                difDinamica +=
                    0.8;
            }}


            cuestasCompletadas++;


            if (
                cuestasCompletadas %
                10 === 0
            ) {{
                nivel++;
            }}


            actualizarUI();
        }}
    }}
}}


// ============================================================
// FÍSICA DEL DINO
// ============================================================

function actualizarDino() {{

    const road =
        obtenerRoad(
            dino.roadId
        );


    if (!road)
        return;


    const anteriorBottom =
        dino.y +
        dino.h;


    // --------------------------------------------------------
    // MOVIMIENTO VERTICAL
    // --------------------------------------------------------

    if (
        dino.enAire
    ) {{

        dino.y +=
            dino.vy;

        dino.vy +=
            GRAVEDAD;

    }} else {{

        // Pegado al camino actual.
        dino.y =
            obtenerYEnRoad(
                road,
                dino.x
            ) -
            dino.h;
    }}


    // --------------------------------------------------------
    // SI ESTÁ EN EL AIRE:
    // BUSCAR ATERRIZAJE
    // --------------------------------------------------------

    if (
        dino.enAire &&
        dino.vy >= 0
    ) {{

        // ====================================================
        // 1. CAMINO ACTUAL
        // ====================================================

        if (
            dino.x >= road.x1 &&
            dino.x <= road.x2
        ) {{

            const roadY =
                obtenerYEnRoad(
                    road,
                    dino.x
                );


            if (
                anteriorBottom <=
                roadY + 5 &&
                dino.y +
                dino.h >=
                roadY
            ) {{

                dino.y =
                    roadY -
                    dino.h;

                dino.vy =
                    0;

                dino.enAire =
                    false;

                return;
            }}
        }}


        // ====================================================
        // 2. SI ES EL CAMINO SUPERIOR Y HAY APERTURA
        // ====================================================

        if (
            road.tipo === "top"
        ) {{

            const node =
                obtenerNode(
                    road.parentNodeId
                );


            if (
                estaEnApertura(
                    node,
                    dino.x
                )
            ) {{

                // No aterrizamos en el superior.
                //
                // Buscamos inmediatamente el inferior.
                const bottom =
                    obtenerBottomRoad(
                        node
                    );


                if (
                    bottom &&
                    dino.x >=
                    bottom.x1 &&
                    dino.x <=
                    bottom.x2
                ) {{

                    const bottomY =
                        obtenerYEnRoad(
                            bottom,
                            dino.x
                        );


                    if (
                        dino.y +
                        dino.h >=
                        bottomY
                    ) {{

                        dino.y =
                            bottomY -
                            dino.h;

                        dino.vy =
                            0;

                        dino.enAire =
                            false;

                        entrarEnRoad(
                            bottom
                        );

                        return;
                    }}
                }}
            }}
        }}


        // ====================================================
        // 3. DETECTAR EL CAMINO SUPERIOR
        // ====================================================
        //
        // Solo podemos aterrizar sobre él si realmente
        // llegamos desde abajo mediante un salto.
        // ====================================================

        const node =
            obtenerNode(
                road.childNodeId
            );


        if (
            node
        ) {{

            const topRoad =
                obtenerRoad(
                    node.topRoadId
                );


            const bottomRoad =
                obtenerRoad(
                    node.bottomRoadId
                );


            // ------------------------------------------------
            // SUPERIOR
            // ------------------------------------------------

            if (
                topRoad &&
                dino.x >=
                topRoad.x1 &&
                dino.x <=
                topRoad.x2
            ) {{

                const topY =
                    obtenerYEnRoad(
                        topRoad,
                        dino.x
                    );


                if (
                    anteriorBottom <=
                    topY + 8 &&
                    dino.y +
                    dino.h >=
                    topY &&
                    !estaEnApertura(
                        node,
                        dino.x
                    )
                ) {{

                    dino.y =
                        topY -
                        dino.h;

                    dino.vy =
                        0;

                    dino.enAire =
                        false;

                    entrarEnRoad(
                        topRoad
                    );

                    return;
                }}
            }}


            // ------------------------------------------------
            // INFERIOR
            // ------------------------------------------------

            if (
                bottomRoad &&
                dino.x >=
                bottomRoad.x1 &&
                dino.x <=
                bottomRoad.x2
            ) {{

                const bottomY =
                    obtenerYEnRoad(
                        bottomRoad,
                        dino.x
                    );


                if (
                    anteriorBottom <=
                    bottomY + 10 &&
                    dino.y +
                    dino.h >=
                    bottomY
                ) {{

                    dino.y =
                        bottomY -
                        dino.h;

                    dino.vy =
                        0;

                    dino.enAire =
                        false;

                    entrarEnRoad(
                        bottomRoad
                    );

                    return;
                }}
            }}
        }}
    }}


    // ========================================================
    // LLEGADA AL FINAL DE UN ROAD
    // ========================================================
    //
    // MUY IMPORTANTE:
    //
    // No teletransportamos.
    //
    // El road ya tiene un nodo y sus dos caminos hijos
    // ya existen.
    //
    // El jugador pasa físicamente a la bifurcación.
    // ========================================================

    if (
        dino.x >=
        road.x2
    ) {{

        const node =
            obtenerNode(
                road.childNodeId
            );


        if (!node)
            return;


        const topRoad =
            obtenerRoad(
                node.topRoadId
            );


        const bottomRoad =
            obtenerRoad(
                node.bottomRoadId
            );


        // ----------------------------------------------------
        // SI ESTÁ EN EL AIRE
        // ----------------------------------------------------
        //
        // No forzamos ninguna ruta.
        //
        // Los caminos están debajo y la física decide.
        // ----------------------------------------------------

        if (
            dino.enAire
        ) {{
            return;
        }}


        // ----------------------------------------------------
        // SI LLEGA AL NODO POR TIERRA
        //
        // El camino inferior es la continuación segura.
        // El superior requiere haber saltado.
        // ----------------------------------------------------

        if (
            bottomRoad
        ) {{

            dino.x =
                Math.max(
                    dino.x,
                    bottomRoad.x1
                );


            const bottomY =
                obtenerYEnRoad(
                    bottomRoad,
                    dino.x
                );


            dino.y =
                bottomY -
                dino.h;


            entrarEnRoad(
                bottomRoad
            );
        }}
    }}
}}


// ============================================================
// MOVIMIENTO HORIZONTAL
// ============================================================

function obtenerVelocidad() {{

    let velocidad =
        baseVelocidad +
        nivel * 0.4 +
        difDinamica * 0.2;


    if (
        dino.propulsado
    ) {{

        velocidad *=
            3.5;


        dino.distPropulsion -=
            velocidad;


        if (
            dino.distPropulsion <=
            0
        ) {{

            dino.propulsado =
                false;
        }}
    }


    return velocidad;
}}


// ============================================================
// ENTIDADES
// ============================================================

function actualizarEntidades(
    velocidad
) {{

    entidades.forEach(
        e => {{

            if (
                !e.activo
            )
                return;


            const road =
                obtenerRoad(
                    e.roadId
                );


            if (!road)
                return;


            // Obstáculos móviles.
            if (
                e.tipo ===
                "obs_lento"
            ) {{

                e.x +=
                    velocidad *
                    0.4;
            }}


            if (
                e.tipo ===
                "obs_rapido"
            ) {{

                e.x -=
                    velocidad *
                    0.7;
            }}


            // ------------------------------------------------
            // OBJETOS QUE SE SALEN DE SU ROAD
            // ------------------------------------------------

            if (
                e.x <
                road.x1 - 100 ||
                e.x >
                road.x2 + 100
            ) {{
                return;
            }}


            e.y =
                obtenerYEnRoad(
                    road,
                    e.x
                ) -
                e.h;


            // ------------------------------------------------
            // COLISIÓN
            // ------------------------------------------------

            const cajaDino = {{

                x:
                    dino.x,

                y:
                    dino.y,

                w:
                    dino.w,

                h:
                    dino.h
            }};


            const cajaEntidad = {{

                x:
                    e.x,

                y:
                    e.y,

                w:
                    e.w,

                h:
                    e.h
            }};


            if (
                colision(
                    cajaDino,
                    cajaEntidad
                )
            ) {{

                if (
                    e.tipo ===
                    "sidra"
                ) {{

                    sidras++;

                    e.activo =
                        false;

                    actualizarUI();

                }} else if (
                    e.tipo ===
                    "fabada"
                ) {{

                    fAcu++;

                    e.activo =
                        false;


                    if (
                        fAcu >=
                        CONST_FABADA
                    ) {{

                        pedosAcu++;

                        fAcu = 0;
                    }}


                    actualizarUI();

                }} else if (
                    e.tipo.startsWith(
                        "obs_"
                    )
                ) {{

                    if (
                        dino.propulsado
                    ) {{

                        e.activo =
                            false;

                    }} else {{

                        juegoActivo =
                            false;


                        document.getElementById(
                            "final-sidras"
                        ).innerText =
                            sidras;


                        document.getElementById(
                            "game-over"
                        ).style.display =
                            "block";
                    }}
                }}
            }}
        }}
    );
}}


// ============================================================
// GENERACIÓN CONTINUA
// ============================================================
//
// No esperamos a llegar al final.
//
// Si el jugador está avanzando por una rama,
// comprobamos que existan varias generaciones por delante.
//
// Si no existen, las creamos.
//
// Esto convierte el árbol en un mundo prácticamente infinito.
// ============================================================

function mantenerMundoPorDelante() {{

    const distanciaNecesaria =
        6000;


    const maxX =
        dino.x +
        distanciaNecesaria;


    // --------------------------------------------------------
    // Para cada road que ya está cerca del horizonte,
    // generar sus hijos.
    // --------------------------------------------------------

    let cambios =
        true;


    while (cambios) {{

        cambios =
            false;


        for (
            let i = 0;
            i < roads.length;
            i++
        ) {{

            const road =
                roads[i];


            if (
                road.x2 <
                maxX
            ) {{

                if (
                    road.childNodeId ===
                    null
                ) {{

                    crearBifurcacion(
                        road
                    );

                    cambios =
                        true;
                }}
            }}
        }}
    }}
}}


// ============================================================
// LIMPIEZA DEL MUNDO
// ============================================================
//
// Borramos solamente caminos muy alejados detrás.
// Nunca eliminamos el camino actual ni caminos que puedan
// ser necesarios para la física inmediata.
// ============================================================

function limpiarMundo() {{

    const limite =
        dino.x -
        2500;


    if (
        roads.length < 80
    ) {{
        return;
    }}


    roads =
        roads.filter(
            r =>
                r ===
                obtenerRoad(
                    dino.roadId
                ) ||
                r.x2 >
                limite
        );


    entidades =
        entidades.filter(
            e =>
                e.activo &&
                e.x >
                limite
        );
}}


// ============================================================
// CÁMARA
// ============================================================

function actualizarCamara() {{

    const roadActual =
        obtenerRoad(
            dino.roadId
        );


    if (!roadActual)
        return;


    // --------------------------------------------------------
    // Buscar caminos visibles hacia delante.
    // --------------------------------------------------------

    const limiteX =
        dino.x +
        2800;


    let minY =
        dino.y;


    let maxY =
        dino.y +
        dino.h;


    for (
        let i = 0;
        i < roads.length;
        i++
    ) {{

        const r =
            roads[i];


        if (
            r.x2 <
            dino.x - 200
        )
            continue;


        if (
            r.x1 >
            limiteX
        )
            continue;


        minY =
            Math.min(
                minY,
                r.y1,
                r.y2
            );


        maxY =
            Math.max(
                maxY,
                r.y1,
                r.y2
            );
    }}


    // --------------------------------------------------------
    // Evitamos que la geometría se vaya fuera de pantalla.
    // --------------------------------------------------------

    const centroMundo =
        (
            minY +
            maxY
        ) / 2;


    const centroDeseado =
        (
            dino.y +
            dino.h / 2 +
            centroMundo
        ) / 2;


    const target =
        canvas.height * 0.53 -
        centroDeseado;


    cameraY +=
        (
            target -
            cameraY
        ) *
        0.08;


    // Limitar desplazamiento exagerado.
    cameraY =
        clamp(
            cameraY,
            -700,
            450
        );
}}


// ============================================================
// DIBUJAR UN ROAD
// ============================================================

function dibujarRoad(
    road
) {{

    if (!road)
        return;


    const visibleAntes =
        road.x2 >
        dino.x - 800;


    const visibleDespues =
        road.x1 <
        dino.x + 4500;


    if (
        !visibleAntes ||
        !visibleDespues
    ) {{
        return;
    }}


    ctx.lineWidth =
        14;


    ctx.lineCap =
        "round";


    if (
        road.tipo === "top"
    ) {{

        ctx.strokeStyle =
            "#2980b9";

    }} else if (
        road.tipo === "bottom"
    ) {{

        ctx.strokeStyle =
            "#c0392b";

    }} else {{

        ctx.strokeStyle =
            "#27ae60";
    }}


    const node =
        road.childNodeId !== null
            ? obtenerNode(
                road.childNodeId
            )
            : null;


    // --------------------------------------------------------
    // CAMINO SUPERIOR
    //
    // Si tiene apertura, no dibujamos ese trozo.
    // --------------------------------------------------------

    if (
        road.tipo === "top"
    ) {{

        const parent =
            obtenerNode(
                road.parentNodeId
            );


        if (
            parent &&
            parent.tieneApertura
        ) {{

            // Tramo antes de apertura.
            ctx.beginPath();

            ctx.moveTo(
                road.x1,
                road.y1
            );

            ctx.lineTo(
                parent.aperturaX1,
                obtenerYEnRoad(
                    road,
                    parent.aperturaX1
                )
            );

            ctx.stroke();


            // Tramo después.
            ctx.beginPath();

            ctx.moveTo(
                parent.aperturaX2,
                obtenerYEnRoad(
                    road,
                    parent.aperturaX2
                )
            );

            ctx.lineTo(
                road.x2,
                road.y2
            );

            ctx.stroke();


            // Indicador de apertura.
            const aperturaCentro =
                (
                    parent.aperturaX1 +
                    parent.aperturaX2
                ) / 2;


            const aperturaY =
                obtenerYEnRoad(
                    road,
                    aperturaCentro
                );


            ctx.save();

            ctx.strokeStyle =
                "#e74c3c";

            ctx.lineWidth =
                4;

            ctx.setLineDash(
                [8, 8]
            );


            ctx.beginPath();

            ctx.moveTo(
                parent.aperturaX1,
                aperturaY + 12
            );

            ctx.lineTo(
                parent.aperturaX2,
                aperturaY + 12
            );

            ctx.stroke();

            ctx.restore();


            return;
        }}
    }}


    // Road normal.
    ctx.beginPath();

    ctx.moveTo(
        road.x1,
        road.y1
    );

    ctx.lineTo(
        road.x2,
        road.y2
    );

    ctx.stroke();
}}


// ============================================================
// DIBUJAR NODO / BIFURCACIÓN
// ============================================================

function dibujarNode(
    node
) {{

    if (!node)
        return;


    if (
        node.x <
        dino.x - 800 ||
        node.x >
        dino.x + 3500
    ) {{
        return;
    }}


    // --------------------------------------------------------
    // Pregunta
    // --------------------------------------------------------

    ctx.fillStyle =
        "rgba(0,0,0,0.72)";


    ctx.fillRect(
        node.x - 150,
        node.y - 150,
        300,
        48
    );


    ctx.fillStyle =
        "#f1c40f";


    ctx.font =
        "bold 24px Arial";


    ctx.fillText(
        node.pregunta,
        node.x - 135,
        node.y - 116
    );


    // --------------------------------------------------------
    // SEÑAL SUPERIOR
    // --------------------------------------------------------

    const topRoad =
        obtenerRoad(
            node.topRoadId
        );


    const bottomRoad =
        obtenerRoad(
            node.bottomRoadId
        );


    if (
        topRoad
    ) {{

        ctx.fillStyle =
            "#fff";

        ctx.font =
            "bold 26px Arial";


        ctx.fillText(
            node.topSign,
            node.x + 60,
            node.y - 45
        );
    }}


    // --------------------------------------------------------
    // SEÑAL INFERIOR
    // --------------------------------------------------------

    if (
        bottomRoad
    ) {{

        ctx.fillStyle =
            "#fff";

        ctx.font =
            "bold 26px Arial";


        ctx.fillText(
            node.bottomSign,
            node.x + 60,
            node.y + 55
        );
    }}
}}


// ============================================================
// DIBUJAR ESCENA
// ============================================================

function dibujarEscena() {{

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


    ctx.fillStyle =
        dino.propulsado
            ? "#ffb142"
            : "#87CEEB";


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


    // --------------------------------------------------------
    // ROADS
    // --------------------------------------------------------

    for (
        let i = 0;
        i < roads.length;
        i++
    ) {{

        dibujarRoad(
            roads[i]
        );
    }}


    // --------------------------------------------------------
    // NODOS
    // --------------------------------------------------------

    for (
        let i = 0;
        i < nodes.length;
        i++
    ) {{

        dibujarNode(
            nodes[i]
        );
    }}


    // --------------------------------------------------------
    // ENTIDADES
    // --------------------------------------------------------

    for (
        let i = 0;
        i < entidades.length;
        i++
    ) {{

        const e =
            entidades[i];


        if (
            !e.activo
        )
            continue;


        const road =
            obtenerRoad(
                e.roadId
            );


        if (!road)
            continue;


        e.y =
            obtenerYEnRoad(
                road,
                e.x
            ) -
            e.h;


        dibujarSprite(
            ctx,
            e.tipo,
            e.x,
            e.y,
            e.w,
            e.h
        );
    }}


    // --------------------------------------------------------
    // DINO
    // --------------------------------------------------------

    ctx.save();


    if (
        dino.propulsado
    ) {{

        ctx.fillStyle =
            "rgba(46,204,113,0.5)";


        ctx.fillRect(
            dino.x - 60,
            dino.y,
            80,
            dino.h
        );
    }}


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
}}


// ============================================================
// LOOP
// ============================================================

function loop() {{

    if (
        !juegoActivo
    ) {{
        return;
    }}


    // --------------------------------------------------------
    // GENERAR MUNDO ANTES DE AVANZAR
    // --------------------------------------------------------

    mantenerMundoPorDelante();


    // --------------------------------------------------------
    // VELOCIDAD
    // --------------------------------------------------------

    const velocidad =
        obtenerVelocidad();


    // --------------------------------------------------------
    // MOVIMIENTO HORIZONTAL
    // --------------------------------------------------------

    dino.x +=
        velocidad;


    // --------------------------------------------------------
    // FÍSICA
    // --------------------------------------------------------

    actualizarDino();


    // --------------------------------------------------------
    // ENTIDADES
    // --------------------------------------------------------

    actualizarEntidades(
        velocidad
    );


    // --------------------------------------------------------
    // MUNDO
    // --------------------------------------------------------

    mantenerMundoPorDelante();

    limpiarMundo();


    // --------------------------------------------------------
    // CÁMARA
    // --------------------------------------------------------

    actualizarCamara();


    // --------------------------------------------------------
    // DIBUJAR
    // --------------------------------------------------------

    dibujarEscena();


    frameId =
        requestAnimationFrame(
            loop
        );
}}


// ============================================================
// INICIAR
// ============================================================

function iniciarJuego() {{

    if (
        frameId !== null
    ) {{

        cancelAnimationFrame(
            frameId
        );

        frameId = null;
    }}


    juegoActivo =
        true;


    nivel =
        1;


    difDinamica =
        0;


    cuestasCompletadas =
        0;


    fAcu =
        0;


    pedosAcu =
        0;


    sidras =
        0;


    cameraY =
        0;


    dino = {{

        x: 100,

        y: 260,

        w: 40,

        h: 40,

        vy: 0,

        enAire: false,

        propulsado: false,

        distPropulsion: 0,

        roadId: null,

        parentNodeId: null
    }};


    document.getElementById(
        "game-over"
    ).style.display =
        "none";


    crearMundoInicial();


    const roadInicial =
        obtenerRoad(
            dino.roadId
        );


    dino.y =
        obtenerYEnRoad(
            roadInicial,
            dino.x
        ) -
        dino.h;


    actualizarUI();


    loop();
}}


// ============================================================
// REINICIAR
// ============================================================

window.reiniciarJuego =
    function() {{

        iniciarJuego();
    }};


// ============================================================
// ARRANQUE
// ============================================================

iniciarJuego();

</script>

</body>
</html>
"""


components.html(
    html_juego,
    height=600
)

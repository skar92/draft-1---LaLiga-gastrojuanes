import base64
import json
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DinoJuan - Minijuego", layout="wide")


def obtener_imagen_base64(nombre_archivo, color_hex_fallback):
    folder = "img"
    ruta = os.path.join(folder, nombre_archivo)
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    if os.path.exists(folder):
        pngs = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
        if pngs:
            with open(os.path.join(folder, pngs[0]), "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return f"COLOR:{color_hex_fallback}"


imagenes = {
    "dino": obtener_imagen_base64("oviedo_dino.png", "#2ecc71"),
    "obs_fijo": obtener_imagen_base64("ubres_dino.png", "#e74c3c"),
    "obs_lento": obtener_imagen_base64("carne_dino.png", "#e67e22"),
    "obs_rapido": obtener_imagen_base64("mirete_dino.png", "#8e44ad"),
    "obs_extra": obtener_imagen_base64("pwc_dino.png", "#c0392b"),
    "fabada": obtener_imagen_base64("fabada.png", "#d35400"),
    "sidra": obtener_imagen_base64("sidra.png", "#f1c40f"),
}

IMG_JSON = json.dumps(imagenes)

html_juego = r'''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<style>
html,body{margin:0;padding:0;overflow:hidden;background:#222;font-family:"Segoe UI",sans-serif;-webkit-user-select:none;user-select:none}
#game-container{position:relative;width:100%;max-width:900px;margin:0 auto;box-shadow:0 0 20px rgba(0,0,0,.5)}
canvas{display:block;width:100%;height:500px;background:linear-gradient(to bottom,#87CEEB,#E0F6FF);cursor:pointer;touch-action:manipulation}
#ui-layer{position:absolute;top:10px;left:15px;color:#333;font-weight:700;font-size:18px;pointer-events:none;text-shadow:1px 1px 2px white;z-index:10}
#game-over{display:none;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);min-width:260px;background:rgba(0,0,0,.88);color:#fff;padding:30px;border-radius:15px;text-align:center;border:3px solid #f1c40f;z-index:20}
.btn{background:#f1c40f;color:#000;font-weight:700;padding:10px 20px;border:0;border-radius:5px;cursor:pointer;margin-top:15px;font-size:16px}
#controls{position:absolute;bottom:18px;left:0;width:100%;display:flex;justify-content:space-around;gap:12px;pointer-events:none;z-index:10}
.ctrl-btn{pointer-events:auto;background:rgba(255,255,255,.86);border:2px solid #333;border-radius:12px;padding:12px 25px;font-size:18px;font-weight:700;cursor:pointer;box-shadow:0 4px 6px rgba(0,0,0,.2);touch-action:manipulation}
#btn-pedo{background:rgba(211,84,0,.92);color:#fff;border-color:#e67e22}
@media(max-width:600px){#ui-layer{font-size:15px;left:9px;top:8px}.ctrl-btn{padding:10px 15px;font-size:15px}}
</style>
</head>
<body>
<div id="game-container">
<div id="ui-layer">
<div>🍏 Sidras: <span id="sidras">0</span> &nbsp;|&nbsp; 🥫 Fabadas: <span id="fabadas">0</span>/3 &nbsp;→&nbsp; 💨 Pedos: <span id="pedos">0</span></div>
<div style="font-size:14px;margin-top:5px;color:#555;">🏆 Nivel: <span id="nivel">1</span> &nbsp;|&nbsp; 📈 Dificultad Extra: <span id="dif">0.0</span></div>
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
<script>
const IMG_DATA = __IMG_DATA__;
const canvas=document.getElementById("gameCanvas");
const ctx=canvas.getContext("2d");
canvas.width=900;canvas.height=500;

const GRAVEDAD=0.65;
const FUERZA_SALTO=-15;
const ALTURA_MAX_SALTO=(FUERZA_SALTO*FUERZA_SALTO)/(2*GRAVEDAD);
const VELOCIDAD_BASE=3.5;
const ANCHO_TRAMPILLA=115;
const MIN_VISIBLE_SEPARACION=45;
const MAX_TRAMPILLA_SEPARACION=Math.min(230,ALTURA_MAX_SALTO-20);
const LONGITUD_MIN=1150;
const LONGITUD_MAX=1550;
const HORIZONTE=7200;
const MAX_ROADS_MEMORIA=240;
const TOLERANCIA_ATERRIZAJE=8;

const imgs={};
for(const k in IMG_DATA){
    if(!IMG_DATA[k].startsWith("COLOR:")){const im=new Image();im.src=IMG_DATA[k];imgs[k]=im;}
    else imgs[k]=IMG_DATA[k].split(":")[1];
}
function sprite(key,x,y,w,h){
    const im=imgs[key];
    if(typeof im==="string"){ctx.fillStyle=im;ctx.fillRect(x,y,w,h);return;}
    if(im&&im.complete&&im.naturalWidth>0){ctx.drawImage(im,x,y,w,h);return;}
    ctx.fillStyle="#111";ctx.fillRect(x,y,w,h);
}

let juegoActivo=true,frameId=null;
let nivel=1,difDinamica=0,sidras=0,fAcu=0,pedosAcu=0;
let cameraY=0,nextRoadId=1,nextNodeId=1;
let roads=[],nodes=[],entidades=[];
const CONST_FABADA=3,DISTANCIA_PEDO=2500;

let dino={x:100,y:260,w:40,h:40,vy:0,enAire:false,propulsado:false,distPropulsion:0,roadId:null};

function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
function rand(a,b){return a+Math.random()*(b-a);}
function randInt(a,b){return Math.floor(rand(a,b+1));}
function roadById(id){return roads.find(r=>r.id===id)||null;}
function nodeById(id){return nodes.find(n=>n.id===id)||null;}
function yRoad(r,x){return r.y1+r.pendiente*(x-r.x1);}
function sep(top,bottom,x){return yRoad(bottom,x)-yRoad(top,x);}
function col(a,b){return !(b.x>=a.x+a.w||b.x+b.w<=a.x||b.y>=a.y+a.h||b.y+b.h<=a.y);}

function pregunta(n){
    let ops=["+","-"];if(n>2)ops.push("*");if(n>4)ops.push("/");
    const op=ops[randInt(0,ops.length-1)];let b=randInt(1,8*n),c=randInt(1,8*n),res;
    if(op==="+")res=b+c;else if(op==="-")res=b-c;else if(op==="*")res=b*c;else{res=b;b=b*c;}
    const ok=Math.random()>.5;
    const shown=ok?res:res+(Math.random()>.5?1:-1)*randInt(1,4);
    return {texto:`${b} ${op} ${c} = ${shown}`,correcta:ok?"SI":"NO"};
}

function crearRoad(x1,y1,x2,y2,parentNodeId,tipo,nivelRoad){
    const r={id:nextRoadId++,x1,y1,x2,y2,pendiente:(y2-y1)/(x2-x1),parentNodeId,tipo,nivel:nivelRoad,childNodeId:null,entidadesGeneradas:false};
    roads.push(r);return r;
}

// Devuelve pendientes tales que la superior SIEMPRE queda por encima.
// Con rectas nacidas del mismo nodo basta con upper <= lower.
function elegirPendientes(longitud){
    for(let t=0;t<150;t++){
        const base=rand(-7,7);
        let delta;
        const r=Math.random();
        if(r<.28)delta=rand(0,.6);       // casi paralelas
        else if(r<.82)delta=rand(.6,3.6); // separación normal
        else delta=rand(3.6,7.5);         // separación fuerte
        const upper=base-delta/2;
        const lower=base+delta/2;
        if(upper<-10||lower>10)continue;
        const finalSep=(Math.tan(lower*Math.PI/180)-Math.tan(upper*Math.PI/180))*longitud;
        if(finalSep<25||finalSep>470)continue;
        return {upper:upper*Math.PI/180,lower:lower*Math.PI/180};
    }
    const b=rand(-4,4)*Math.PI/180;return {upper:b,lower:b};
}

// Solo crea trampilla si el camino inferior será claramente visible debajo.
function crearTrampilla(top,bottom){
    const ancho=ANCHO_TRAMPILLA;
    const minX=top.x1+280,maxX=top.x2-ancho-220;
    if(maxX<=minX)return null;
    const candidatos=[];
    for(let i=0;i<36;i++){
        const x=rand(minX,maxX),c=x+ancho/2;
        const s=sep(top,bottom,c);
        // Además del límite vertical, dejamos espacio suficiente para dibujar el inferior.
        if(s>=MIN_VISIBLE_SEPARACION&&s<=MAX_TRAMPILLA_SEPARACION){
            candidatos.push({x1:x,x2:x+ancho,separacion:s});
        }
    }
    if(!candidatos.length)return null;
    // Preferimos una trampilla alrededor de una separación media.
    candidatos.sort((a,b)=>Math.abs(a.separacion-115)-Math.abs(b.separacion-115));
    return candidatos[0];
}

function crearBifurcacion(road){
    if(!road||road.childNodeId!==null)return road?nodeById(road.childNodeId):null;
    const x=road.x2,y=road.y2,L=rand(LONGITUD_MIN,LONGITUD_MAX);
    const a=elegirPendientes(L);
    const p=pregunta(Math.max(1,nivel+difDinamica));
    const topSign=Math.random()>.5?"SI":"NO",bottomSign=topSign==="SI"?"NO":"SI";
    const node={id:nextNodeId++,x,y,parentRoadId:road.id,topRoadId:null,bottomRoadId:null,pregunta:p.texto,correcta:p.correcta,topSign,bottomSign,resuelto:false,trampilla:null};
    nodes.push(node);
    const top=crearRoad(x,y,x+L,y+Math.tan(a.upper)*L,node.id,"top",road.nivel+1);
    const bottom=crearRoad(x,y,x+L,y+Math.tan(a.lower)*L,node.id,"bottom",road.nivel+1);
    node.topRoadId=top.id;node.bottomRoadId=bottom.id;road.childNodeId=node.id;
    if(Math.random()<.78)node.trampilla=crearTrampilla(top,bottom);
    generarEntidades(top);generarEntidades(bottom);
    return node;
}

function generarEntidades(road){
    if(!road||road.entidadesGeneradas)return;
    road.entidadesGeneradas=true;
    const cantidad=randInt(1,Math.max(1,Math.floor(1+nivel*.55)));
    for(let i=0;i<cantidad;i++){
        const x=rand(road.x1+190,road.x2-190),r=Math.random();
        const tipo=r<.45?"obs_fijo":r<.72?"obs_lento":r<.93?"obs_rapido":"obs_extra";
        entidades.push({id:`o_${road.id}_${i}`,x,roadId:road.id,tipo,activo:true,w:40,h:40});
    }
    if(Math.random()<.76)entidades.push({id:`s_${road.id}`,x:rand(road.x1+260,road.x2-220),roadId:road.id,tipo:"sidra",activo:true,w:30,h:30});
    if(Math.random()<.24)entidades.push({id:`f_${road.id}`,x:rand(road.x1+340,road.x2-260),roadId:road.id,tipo:"fabada",activo:true,w:35,h:35});
}

function crearMundoInicial(){
    roads=[];nodes=[];entidades=[];nextRoadId=1;nextNodeId=1;
    const initial=crearRoad(0,300,1350,300,null,"main",0);
    generarEntidades(initial);dino.roadId=initial.id;crearBifurcacion(initial);
    dino.y=yRoad(initial,dino.x+dino.w/2)-dino.h;
}

function mantenerMundo(){
    const limite=dino.x+HORIZONTE;
    let changed=true,guard=0;
    while(changed&&guard<30){
        changed=false;guard++;
        for(const r of roads.slice()){
            if(r.x2<=limite&&r.childNodeId===null){crearBifurcacion(r);changed=true;}
        }
    }
}

function resolverEntrada(road){
    if(!road||dino.roadId===road.id)return;
    dino.roadId=road.id;
    if(road.parentNodeId!==null){
        const n=nodeById(road.parentNodeId);
        if(n&&!n.resuelto){
            n.resuelto=true;
            const signo=road.tipo==="top"?n.topSign:n.bottomSign;
            if(signo===n.correcta)difDinamica=Math.max(0,difDinamica-.5);else difDinamica+=.8;
            if(nivel<99) nivel=1+Math.floor(nodes.filter(x=>x.resuelto).length/10);
            actualizarUI();
        }
    }
}

function hijosActuales(){
    const r=roadById(dino.roadId);if(!r||r.childNodeId===null)return null;
    const n=nodeById(r.childNodeId);if(!n)return null;
    return {node:n,top:roadById(n.topRoadId),bottom:roadById(n.bottomRoadId)};
}

function salto(){if(!juegoActivo||dino.propulsado)return;if(!dino.enAire){dino.vy=FUERZA_SALTO;dino.enAire=true;}}

function caer(){
    if(!juegoActivo)return;
    if(dino.enAire){dino.vy=Math.max(dino.vy,10);return;}
    const r=roadById(dino.roadId);if(!r||r.tipo!=="top")return;
    const n=nodeById(r.parentNodeId);if(!n||!n.trampilla)return;
    const xc=dino.x+dino.w/2;
    if(xc>=n.trampilla.x1&&xc<=n.trampilla.x2){dino.enAire=true;dino.vy=5.5;}
}

function pedo(){
    if(!juegoActivo)return;
    if(pedosAcu>0&&!dino.propulsado){dino.propulsado=true;dino.distPropulsion=pedosAcu*DISTANCIA_PEDO;pedosAcu=0;actualizarUI();}
}

function intentarAterrizar(road,prevBottom,nowBottom,desdeInferior){
    if(!road)return false;
    const xc=dino.x+dino.w/2;
    if(xc<road.x1||xc>road.x2)return false;
    const surface=yRoad(road,xc);
    if(!(prevBottom<=surface+TOLERANCIA_ATERRIZAJE&&nowBottom>=surface-2))return false;
    if(desdeInferior){
        const actual=roadById(dino.roadId);
        if(actual&&actual.tipo==="bottom"&&road.tipo==="top"){
            const s=sep(road,actual,xc);
            if(s>ALTURA_MAX_SALTO+8)return false;
        }
    }
    dino.y=surface-dino.h;dino.vy=0;dino.enAire=false;resolverEntrada(road);return true;
}

function actualizarDino(){
    const current=roadById(dino.roadId);if(!current)return;
    const prevBottom=dino.y+dino.h;
    if(dino.enAire){dino.y+=dino.vy;dino.vy+=GRAVEDAD;}else{dino.y=yRoad(current,dino.x+dino.w/2)-dino.h;}
    const nowBottom=dino.y+dino.h;

    if(dino.enAire&&dino.vy>=0){
        // Trampilla: solo atraviesa el superior dentro del hueco y aterriza en el inferior.
        if(current.tipo==="top"&&current.parentNodeId!==null){
            const n=nodeById(current.parentNodeId),b=n?roadById(n.bottomRoadId):null;
            if(n&&b&&n.trampilla){
                const xc=dino.x+dino.w/2;
                if(xc>=n.trampilla.x1&&xc<=n.trampilla.x2){
                    const by=yRoad(b,xc);
                    if(prevBottom<=by+10&&nowBottom>=by){dino.y=by-dino.h;dino.vy=0;dino.enAire=false;resolverEntrada(b);return;}
                }
            }
        }
        // Primero el road sobre el que venía.
        if(intentarAterrizar(current,prevBottom,nowBottom,false))return;
        // Después, si ya hemos cruzado el nodo, el inferior o el superior.
        const h=hijosActuales();
        if(h){
            const xc=dino.x+dino.w/2;
            if(xc>=h.node.x){
                if(intentarAterrizar(h.top,prevBottom,nowBottom,true))return;
                if(intentarAterrizar(h.bottom,prevBottom,nowBottom,false))return;
            }
        }
    }

    // En tierra, al pasar el nodo el inferior es la continuación física segura.
    // NO se mueve x artificialmente ni se teletransporta.
    if(!dino.enAire&&dino.x+dino.w/2>=current.x2){
        const h=hijosActuales();
        if(h&&h.bottom&&dino.x+dino.w/2>=h.bottom.x1){
            const xc=dino.x+dino.w/2;
            dino.y=yRoad(h.bottom,xc)-dino.h;
            resolverEntrada(h.bottom);
        }
    }
}

function velocidad(){
    let v=VELOCIDAD_BASE+nivel*.4+difDinamica*.2;
    if(dino.propulsado){v*=3.5;dino.distPropulsion-=v;if(dino.distPropulsion<=0)dino.propulsado=false;}
    return v;
}

function actualizarEntidades(v){
    const dbox={x:dino.x,y:dino.y,w:dino.w,h:dino.h};
    for(const e of entidades){
        if(!e.activo)continue;const r=roadById(e.roadId);if(!r)continue;
        if(e.tipo==="obs_lento")e.x+=v*.4;
        if(e.tipo==="obs_rapido")e.x-=v*.7;
        e.y=yRoad(r,e.x+e.w/2)-e.h;
        if(e.roadId!==dino.roadId)continue;
        if(!col(dbox,{x:e.x,y:e.y,w:e.w,h:e.h}))continue;
        if(e.tipo==="sidra"){sidras++;e.activo=false;actualizarUI();}
        else if(e.tipo==="fabada"){fAcu++;e.activo=false;if(fAcu>=CONST_FABADA){pedosAcu++;fAcu=0;}actualizarUI();}
        else if(e.tipo.startsWith("obs_")){if(dino.propulsado)e.activo=false;else{juegoActivo=false;document.getElementById("final-sidras").innerText=sidras;document.getElementById("game-over").style.display="block";}}
    }
}

function limpiar(){
    if(roads.length<MAX_ROADS_MEMORIA)return;
    const limite=dino.x-6500;const current=roadById(dino.roadId);const protect=new Set();
    if(current){protect.add(current.id);if(current.parentNodeId!==null){const n=nodeById(current.parentNodeId);if(n)protect.add(n.parentRoadId);}if(current.childNodeId!==null){const n=nodeById(current.childNodeId);if(n){protect.add(n.topRoadId);protect.add(n.bottomRoadId);}}}
    roads=roads.filter(r=>protect.has(r.id)||r.x2>limite);
    // Nodes asociados a roads eliminados también se pueden eliminar; los del frente permanecen.
    const aliveIds=new Set(roads.map(r=>r.id));
    nodes=nodes.filter(n=>aliveIds.has(n.parentRoadId)||aliveIds.has(n.topRoadId)||aliveIds.has(n.bottomRoadId));
    entidades=entidades.filter(e=>e.activo&&e.x>limite);
}

function actualizarCamara(){
    const maxX=dino.x+3400;let minY=dino.y,maxY=dino.y+dino.h;
    for(const r of roads){if(r.x2<dino.x-500||r.x1>maxX)continue;minY=Math.min(minY,r.y1,r.y2);maxY=Math.max(maxY,r.y1,r.y2);}
    const centro=(minY+maxY)/2,objetivo=canvas.height*.53-((dino.y+dino.h/2+centro)/2);
    cameraY+=(objetivo-cameraY)*.08;cameraY=clamp(cameraY,-950,650);
}

function dibujarRoad(r){
    if(!r||r.x2<dino.x-1000||r.x1>dino.x+4300)return;
    const n=r.parentNodeId!==null?nodeById(r.parentNodeId):null;
    ctx.lineWidth=14;ctx.lineCap="round";
    ctx.strokeStyle=r.tipo==="top"?"#2980b9":r.tipo==="bottom"?"#c0392b":"#27ae60";
    if(r.tipo==="top"&&n&&n.trampilla){
        const h=n.trampilla;
        ctx.beginPath();ctx.moveTo(r.x1,r.y1);ctx.lineTo(h.x1,yRoad(r,h.x1));ctx.stroke();
        ctx.beginPath();ctx.moveTo(h.x2,yRoad(r,h.x2));ctx.lineTo(r.x2,r.y2);ctx.stroke();
        ctx.save();ctx.strokeStyle="#566573";ctx.lineWidth=3;ctx.setLineDash([7,7]);
        ctx.beginPath();ctx.moveTo(h.x1,yRoad(r,h.x1)+3);ctx.lineTo(h.x1,yRoad(r,h.x1)+22);ctx.stroke();
        ctx.beginPath();ctx.moveTo(h.x2,yRoad(r,h.x2)+3);ctx.lineTo(h.x2,yRoad(r,h.x2)+22);ctx.stroke();ctx.restore();
        return;
    }
    ctx.beginPath();ctx.moveTo(r.x1,r.y1);ctx.lineTo(r.x2,r.y2);ctx.stroke();
}

function dibujarNode(n){
    if(!n||n.x<dino.x-800||n.x>dino.x+3600)return;
    ctx.save();ctx.fillStyle="#34495e";ctx.beginPath();ctx.arc(n.x,n.y,9,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="rgba(0,0,0,.72)";ctx.fillRect(n.x-150,n.y-150,300,48);
    ctx.fillStyle="#f1c40f";ctx.font="bold 24px Arial";ctx.fillText(n.pregunta,n.x-135,n.y-116);
    ctx.fillStyle="#fff";ctx.font="bold 24px Arial";ctx.fillText("↑ "+n.topSign,n.x+55,n.y-38);ctx.fillText("↓ "+n.bottomSign,n.x+55,n.y+58);
    ctx.restore();
}

function dibujar(){
    ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle=dino.propulsado?"#ffb142":"#87CEEB";ctx.fillRect(0,0,canvas.width,canvas.height);ctx.restore();
    ctx.save();ctx.translate(220-dino.x,cameraY);
    for(const r of roads)dibujarRoad(r);
    for(const n of nodes)dibujarNode(n);
    for(const e of entidades){if(!e.activo)continue;const r=roadById(e.roadId);if(!r)continue;e.y=yRoad(r,e.x+e.w/2)-e.h;sprite(e.tipo,e.x,e.y,e.w,e.h);}
    if(dino.propulsado){ctx.fillStyle="rgba(46,204,113,.42)";ctx.fillRect(dino.x-70,dino.y+8,80,22);}
    sprite("dino",dino.x,dino.y,dino.w,dino.h);ctx.restore();
}

function actualizarUI(){
    document.getElementById("sidras").innerText=sidras;document.getElementById("fabadas").innerText=fAcu;document.getElementById("pedos").innerText=pedosAcu;document.getElementById("nivel").innerText=nivel;document.getElementById("dif").innerText=difDinamica.toFixed(1);
}

canvas.addEventListener("click",salto);
canvas.addEventListener("touchstart",e=>{e.preventDefault();salto();},{passive:false});
document.getElementById("btn-drop").addEventListener("click",e=>{e.stopPropagation();caer();});
document.getElementById("btn-drop").addEventListener("touchstart",e=>{e.preventDefault();e.stopPropagation();caer();},{passive:false});
document.getElementById("btn-pedo").addEventListener("click",e=>{e.stopPropagation();pedo();});
document.getElementById("btn-pedo").addEventListener("touchstart",e=>{e.preventDefault();e.stopPropagation();pedo();},{passive:false});
document.addEventListener("keydown",e=>{if(e.code==="ArrowUp"||e.code==="Space"){e.preventDefault();salto();}if(e.code==="ArrowDown"){e.preventDefault();caer();}if(e.code==="KeyF")pedo();});

function loop(){
    if(!juegoActivo)return;
    mantenerMundo();
    const v=velocidad();
    dino.x+=v;
    actualizarDino();
    actualizarEntidades(v);
    mantenerMundo();
    limpiar();
    actualizarCamara();
    dibujar();
    frameId=requestAnimationFrame(loop);
}

function iniciarJuego(){
    if(frameId!==null){cancelAnimationFrame(frameId);frameId=null;}
    juegoActivo=true;nivel=1;difDinamica=0;sidras=0;fAcu=0;pedosAcu=0;cameraY=0;
    dino={x:100,y:260,w:40,h:40,vy:0,enAire:false,propulsado:false,distPropulsion:0,roadId:null};
    document.getElementById("game-over").style.display="none";
    crearMundoInicial();actualizarUI();loop();
}
window.reiniciarJuego=()=>iniciarJuego();
iniciarJuego();
</script>
</body>
</html>
'''

html_juego = html_juego.replace("__IMG_DATA__", IMG_JSON)
components.html(html_juego, height=600)

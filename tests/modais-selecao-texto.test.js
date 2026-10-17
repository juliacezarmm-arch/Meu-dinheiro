const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
for(const id of ['action-panel-modal','invest-modal','pending-payment-editor']){
  const tag=html.match(new RegExp('<div id="'+id+'"[^>]+>'));
  assert(tag,'Janela ausente: '+id);
  assert(!tag[0].includes('onclick='),'Fechamento externo antigo não pode continuar em '+id);
  assert(html.includes("configurarFechamentoSeguroFora('"+id+"'"),'Proteção não configurada em '+id);
}
const script=html.match(/<script\s*>([\s\S]*?)<\/script>/);assert(script);
const src=script[1],start=src.indexOf('function configurarFechamentoSeguroFora(');
assert(start>=0);
const end=src.indexOf('\nfunction abrirPainelFlutuante(',start);
const source=src.slice(start,end);
function node(){
 const handlers={};
 return {handlers,addEventListener(name,fn){handlers[name]=fn;}};
}
const overlays={a:node(),b:node(),c:node()};
let fechamentos=0;
const ctx=vm.createContext({document:{getElementById:id=>overlays[id]},Math});
vm.runInContext(source,ctx);
vm.runInContext("configurarFechamentoSeguroFora('a',()=>{})",ctx);
function setup(key){
 const fundo=overlays[key],handle=fundo.handlers;
 function fire(type,target,x=10,y=10){handle[type]({target,clientX:x,clientY:y,pointerId:1,isPrimary:true,pointerType:'mouse',button:0});}
 return {fundo,fire,handle};
}
for(const key of ['b','c']){
 ctx.fechar=()=>{fechamentos++};
 vm.runInContext("configurarFechamentoSeguroFora('"+key+"',fechar)",ctx);
 const {fundo,fire,handle}=setup(key),conteudo={};
 // Seleção iniciada dentro do formulário, terminada no fundo.
 fire('pointerdown',conteudo);fire('pointerup',fundo);fire('click',fundo);
 assert.strictEqual(fechamentos,0,'Arrastar texto para fora não fecha modal');
 // Gesto começado no fundo e arrastado também não fecha.
 fire('pointerdown',fundo);fire('pointermove',fundo,40,50);fire('pointerup',fundo,40,50);fire('click',fundo,40,50);
 assert.strictEqual(fechamentos,0,'Arrastar no fundo não fecha modal');
 // Clicar no interior nunca fecha.
 fire('pointerdown',conteudo);fire('pointerup',conteudo);fire('click',conteudo);
 assert.strictEqual(fechamentos,0);
 // Clicar normalmente no fundo fecha.
 fire('pointerdown',fundo);fire('pointerup',fundo);fire('click',fundo);
 assert.strictEqual(fechamentos,key==='b'?1:2,'Clique verdadeiro no fundo fecha normalmente');
}
console.log('PASS: seleção de texto, arrasto e clique externo nos modais');

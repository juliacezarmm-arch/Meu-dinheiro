const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const match=html.match(/<script\s*>([\s\S]*?)<\/script>/);assert(match);
const src=match[1];
function fn(name){
 const at=src.indexOf('function '+name+'(');assert(at>=0,'Função ausente: '+name);
 const rest=src.slice(at+10),next=/\n(?:async )?function [A-Za-z]/.exec(rest);
 return src.slice(at,next?at+10+next.index:src.length);
}
const names=['isoDate','monthKey','valorMonetarioValido','valorParcela','dueDateFor','mesFaturaAtualDoCartao','valorMensalidadeNoMes','primeiroMesMensalidadeCartao','parcelaMensalidadeCartao','vencimentoDaCompra','getMesMap','getParcelasCartao','totalDaFatura','dataISOValida','saldoInicialValido','validarDadosImportados','addCartao','resetCartaoForm','updatePreview'];
const elements={};function el(id){return elements[id]||(elements[id]={value:'',innerHTML:'',textContent:'',style:{display:''}});}
const ctx=vm.createContext({console,Date,Set,Number,Math,String,Array,Error,document:{getElementById:el}});
vm.runInContext(`const S={extrato:[],cartao:[],cartoes:[{id:10,bank:'Itaú',nome:'Black',dueDay:10,closeDay:null}],invest:[],saldoInicial:null};let editingCartaoId=null;let cartaoMes=new Date(2026,9,1),extratoMes=new Date(2026,9,1),resumoMes=new Date(2026,9,1);function today(){return '2026-10-17'};function selectedCard(){return S.cartoes[0]};function appAlert(v){throw Error(v)};function novoIdGlobal(){return 100+S.cartao.length};function saveData(){};function renderCartao(){};function renderExtrato(){};function updateResumo(){};function fecharPainelFlutuante(){};function fmt(v){return 'R$ '+v.toFixed(2)};function mesStr(y,m){return String(y)+'-'+String(m+1)};`+names.map(fn).join('\n'),ctx);
const run=code=>vm.runInContext(code,ctx);
assert(html.includes('id="cc-val" placeholder="Valor total (R$)" step="0.01"'),'Campo deve aceitar negativo');
assert(html.includes('value="estorno"'),'Opção de estorno visível');
for(const [id,value] of Object.entries({'cc-data':'2026-10-17','cc-desc':'Estorno de compra antiga','cc-tipo':'estorno','cc-categoria':'Compras pessoais','cc-subcategoria':'Roupas','cc-val':'-80','cc-parcelas':'6'}))el(id).value=value;
run('addCartao()');
assert.strictEqual(run('S.cartao[0].val'),-80);
assert.strictEqual(run('S.cartao[0].tipo'),'estorno');
assert.strictEqual(run('S.cartao[0].parcelas'),1,'Estorno não deve ser parcelado');
assert.strictEqual(run("getParcelasCartao().filter(x=>!x.mensalidadeCartao)[0].val"),-80);
assert.strictEqual(run("totalDaFatura(10,'2026-11')"),-8000);
assert.strictEqual(run("getMesMap()['2026-10']"),-80);
run("S.cartao.push({id:101,data:'2026-10-17',tipo:'compra',val:120,parcelas:1,cardId:10,vencDia:10,desc:'Compra',categoria:'Compras pessoais',subcategoria:'Roupas'})");
assert.strictEqual(run("totalDaFatura(10,'2026-11')"),4000,'Fatura líquida deve abater estorno');
assert.strictEqual(run('valorParcela({val:100,parcelas:3},0)'),33.34,'Compras parceladas preservadas');
assert.strictEqual(run("validarDadosImportados({cartao:[{id:1,data:'2026-10-17',tipo:'estorno',val:-80,parcelas:1}],extrato:[],invest:[],cartoes:[]}).cartao[0].val"),-80);
assert.throws(()=>run("validarDadosImportados({cartao:[{id:1,data:'2026-10-17',tipo:'compra',val:-80}],extrato:[],invest:[],cartoes:[]})"));
assert.throws(()=>run("validarDadosImportados({cartao:[{id:1,data:'2026-10-17',tipo:'estorno',val:-80,parcelas:2}],extrato:[],invest:[],cartoes:[]})"));
assert.throws(()=>run("validarDadosImportados({extrato:[{id:1,data:'2026-10-17',tipo:'saida',val:-80}],cartao:[],invest:[],cartoes:[]})"));
run("S.extrato.push({id:200,data:'2026-10-05',tipo:'saida',cardId:10,faturaMes:'2026-10',val:10})");
assert.strictEqual(run("getParcelasCartao().filter(x=>!x.mensalidadeCartao)[0].data"),'2026-11-10','Estorno não pode voltar para fatura paga');
console.log('PASS: estornos negativos, fatura, parcelas, JSON, extrato e competência retroativa');

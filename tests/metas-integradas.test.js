const fs=require('fs'),assert=require('assert'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const script=html.match(/<script\s*>([\s\S]*?)<\/script>/);
assert(script,'Script principal ausente');const src=script[1];
for(const id of ['inv-banco','inv-rent-indice','inv-rent-valor','inv-vencimento','meta-modo','meta-prazo','meta-invest-dest'])assert(html.includes('id="'+id+'"'),'Campo ausente: '+id);
for(const id of ['valorMetaAtual','metasReservadasNoInvestimento','movimentarReservaInterna','addMeta','getMetaStorage','reservadoEmMetas','dataISOValida','isoDate','valorMonetarioValido'])assert(src.includes('function '+id+'('),'Função ausente: '+id);
assert(src.includes('metas.filter(x=>x.modo!==\'acompanhar\')'),'Acompanhamento não pode entrar no total reservado');
assert(src.includes("dest.modo==='acompanhar'"),'Acompanhamento não pode receber depósitos no Extrato');
assert(src.includes('historico:[],banco,rentIndice,rentValor,vencimento:'),'Metadados não são persistidos');
assert(!src.includes('localStorage'),'Não usar armazenamento paralelo ao JSON');
function fn(name){let pos=src.indexOf('function '+name+'(');assert(pos>=0,name);let end=src.indexOf('\nfunction ',pos+10);return src.slice(pos,end<0?src.length:end);}
const elements={};function el(id){return elements[id]||(elements[id]={value:'',textContent:'',focus(){}});}
let saves=0,refreshes=0,alerts=[],idCounter=100;
const ctx=vm.createContext({console,Date,Math,Number,String,Array,Set,Error,document:{getElementById:el},appAlert:x=>alerts.push(x),saveData:()=>saves++,refreshInvestViews:()=>refreshes++,renderInvestDestinationOptions:()=>{},renderMetaInvestOptions:()=>{},renderInvest:()=>{},renderMetas:()=>{},updateCategories:()=>{},updateResumo:()=>{},novoIdGlobal:()=>++idCounter,today:()=> '2026-09-21',investUi:{acao:{},historico:{},mes:{}}});
const names=['isoDate','dataISOValida','valorMonetarioValido','getMetaStorage','reservadoEmMetas','metasReservadasNoInvestimento','valorMetaAtual','addMeta','movimentarReservaInterna'];
vm.runInContext('const S={invest:[],extrato:[]};'+names.map(fn).join('\n')+'\nfunction ensureInvestHistory(i){return i.historico||(i.historico=[])}\nfunction ultimaDataFinanceira(i){return i.historico.reduce((a,x)=>x.data>a?x.data:a,\'\')}\nfunction recalcInvestFromHistory(i){let total=0;i.historico.forEach(h=>{total+=h.tipo===\'aporte\'?h.valor:-h.valor;});i.valorAtual=total;}\n',ctx);
const run=s=>vm.runInContext(s,ctx);
run("S.invest=[{id:1,kind:'investimento',nome:'Cofrinho',tipo:'CDB',valorAtual:1000,historico:[]},{id:2,kind:'investimento',nome:'Outro',tipo:'Tesouro',valorAtual:500,historico:[]},{id:3,kind:'meta',storageId:1,nome:'Legada',valorAtual:200,historico:[]},{id:4,kind:'meta',modo:'acompanhar',escopo:'todos',nome:'Patrimonio',valorAtual:0,meta:2000,historico:[]},{id:5,kind:'meta',modo:'acompanhar',storageId:1,nome:'Saldo do Cofrinho',valorAtual:0,historico:[]}] ");
assert.strictEqual(run('reservadoEmMetas(1)'),200);
assert.strictEqual(run('metasReservadasNoInvestimento(1).length'),1);
assert.strictEqual(run('valorMetaAtual(S.invest[3])'),1500);
assert.strictEqual(run('valorMetaAtual(S.invest[4])'),1000);
assert.strictEqual(run('valorMetaAtual(S.invest[2])'),200,'Meta legada continua reservada');
assert.strictEqual(run("S.invest.filter(x=>x.kind==='investimento').reduce((t,x)=>t+x.valorAtual,0)"),1500);
assert.strictEqual(run('reservadoEmMetas(1)'),200,'Acompanhamento não reserva dinheiro');
el('meta-desc').value='Meta nova';el('meta-val').value='3000';el('meta-modo').value='acompanhar';el('meta-invest-dest').value='todos';el('meta-prazo').value='2027-12-31';
run('addMeta()');assert.strictEqual(saves,1);assert.strictEqual(run('S.invest.at(-1).escopo'),'todos');assert.strictEqual(run('S.invest.at(-1).prazo'),'2027-12-31');
assert.strictEqual(run('S.extrato.length'),0,'Criar meta não movimenta dinheiro');
// Teste independente da meta reservada com valor de histórico consistente.
run("S.invest[2].historico=[{id:'inicial',tipo:'aporte',valor:200,data:'2026-09-20'}]");
el('reservar-val-3').value='300';run('movimentarReservaInterna(3,false)');
assert.strictEqual(run('S.invest[2].valorAtual'),500);assert.strictEqual(run('S.invest[0].valorAtual'),1000);assert.strictEqual(run('S.extrato.length'),0);assert.strictEqual(saves,2);
el('reservar-val-3').value='600';run('movimentarReservaInterna(3,false)');assert.strictEqual(saves,2,'Reserva acima do livre foi bloqueada');
el('liberar-val-3').value='150';run('movimentarReservaInterna(3,true)');
assert.strictEqual(run('S.invest[2].valorAtual'),350);assert.strictEqual(run('S.invest[0].valorAtual'),1000);assert.strictEqual(run('S.extrato.length'),0);assert.strictEqual(saves,3);
assert(alerts.some(x=>x.includes('Saldo livre insuficiente')));
console.log('PASS: metas antigas, acompanhamento global/individual, metas no investimento, reserva/liberação sem alterar patrimônio ou Extrato e data-alvo');
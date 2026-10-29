const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const src=fs.readFileSync('index.html','utf8').match(/<script\s*>([\s\S]*?)<\/script>/)[1];
function extract(name){
 const start=src.indexOf('function '+name+'(');assert(start>=0,name);
 const next=/\n(?:async )?function [A-Za-z]/.exec(src.slice(start+10));
 return src.slice(start,next?start+10+next.index:src.length);
}
function fixture({crypto=false,saldo=1000,meta=false}={}){
 const elements={},alerts=[];
 const field=id=>elements[id]||(elements[id]={value:'',hidden:false});
 const ctx=vm.createContext({console,Date,Number,Math,String,Array,Map,Set,JSON,Error,
  document:{getElementById:field},today:()=> '2026-10-28',alerts,
  investPeriodo:'mes',investMes:new Date(2026,9,28),
  isoDate:(y,m,d)=>y+'-'+String(m+1).padStart(2,'0')+'-'+String(d).padStart(2,'0'),
  appAlert:s=>alerts.push(s),saveData:()=>{},refreshInvestViews:()=>{},
  MESES:['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
  fmt:v=>'R$ '+Number(v).toFixed(2),escHtml:String,fmtInvestPct:v=>Number(v).toFixed(2)+'%'});
 vm.runInContext(`const S={extrato:[],cartao:[],cartoes:[],invest:[],saldoInicial:{valor:5000,data:'2026-09-01',idsIgnorados:[]}};const investUi={acao:{},historico:{},mes:{},metrica:{}};`,ctx);
 const functions=['dataISOValida','valorMonetarioValido','novoIdGlobal','novoIdExtrato','isCryptoInvest','calcCryptoValue','ensureInvestHistory','ordenarHistoricoInvest','recalcInvestFromHistory','ultimaDataFinanceira','reservadoEmMetas','metasReservadasNoInvestimento','avaliarRetornoInvestimento','calcInvestPeriodResult','calcInvestMonthResult','saveInvestUpdate','corrigirFluxoUltimaAtualizacao','renderStockChart','investSparkline'];
 vm.runInContext(functions.map(extract).join('\n'),ctx);
 const run=s=>vm.runInContext(s,ctx);
 ctx.seed={id:1,kind:'investimento',nome:'Teste',tipo:crypto?'Cripto':'CDI',valorAtual:saldo,totalAportado:saldo,totalResgatado:0,cryptoQtd:1,cryptoCotacao:saldo,cryptoInvestido:saldo,cryptoPrecoMedio:saldo,historico:[{id:'z-inicial',tipo:'aporte',origem:'saldo_inicial',data:'2026-09-30',valor:saldo}]};
 run('S.invest.push(seed)');
 if(meta)run(`S.invest.push({id:2,kind:'meta',modo:'separar',storageId:1,valorAtual:100,totalAportado:100,totalResgatado:0,historico:[{id:'meta',tipo:'aporte',data:'2026-09-30',valor:100,origem:'reserva_interna'}]})`);
 for(const [key,value] of Object.entries({'data':'2026-10-28','flow':'nenhum','flow-value':'','flow-before':'','val':saldo,'crypto-qtd':1,'crypto-cotacao':saldo,'crypto-investido':saldo,'crypto-preco-medio':saldo}))field('update-'+key+'-1').value=String(value);
 return {run,alerts,set:(key,value)=>field('update-'+key+'-1').value=String(value),snapshot:()=>run('JSON.stringify(S)'),result:()=>run('calcInvestPeriodResult(S.invest[0])')};
}
let f=fixture();f.set('flow','aporte');f.set('flow-value',200);f.set('val',1200);f.run('saveInvestUpdate(1)');
assert.equal(f.result().rendimento,0);assert.equal(f.result().pct,0);assert.equal(f.run('S.extrato[0].val'),200);assert.equal(f.run('S.extrato[0].tipo'),'investimento');
assert(f.result().pontos.every(p=>p.pct===0),'Aporte não deve criar pico percentual');
f=fixture({meta:true});f.set('flow','aporte');f.set('flow-value',200);f.set('flow-before',1100);f.set('val',1300);f.run('saveInvestUpdate(1)');
assert.equal(f.result().rendimento,100);assert(Math.abs(f.result().pct-10)<1e-8);assert.equal(f.run('S.invest[1].valorAtual'),110,'A meta recebe rendimento, não o aporte');
f=fixture();f.set('flow','resgate');f.set('flow-value',200);f.set('val',800);f.run('saveInvestUpdate(1)');
assert.equal(f.result().rendimento,0);assert.equal(f.result().pct,0);assert.equal(f.run('S.extrato[0].categoria'),'Resgate');
f=fixture();f.set('flow','resgate');f.set('flow-value',1000);f.set('val',0);f.run('saveInvestUpdate(1)');
assert.equal(f.result().rendimento,0);f.set('flow','aporte');f.set('flow-value',100);f.set('val',110);f.run('saveInvestUpdate(1)');
assert.equal(f.result().rendimento,10);assert(Math.abs(f.result().pct-10)<1e-8,'Retirada integral e reinvestimento não são prejuízo');
f=fixture({crypto:true,saldo:9.73});f.set('crypto-qtd',2);f.set('crypto-cotacao',9.28);f.set('crypto-investido',19.73);
let before=f.snapshot();f.run('saveInvestUpdate(1)');assert.equal(f.snapshot(),before,'Mudança de quantidade sem fluxo não deve ser salva como rendimento');assert(f.alerts.length);
f.set('flow','aporte');f.set('flow-value',10);f.run('saveInvestUpdate(1)');
assert.equal(f.result().final,18.56);assert(Math.abs(f.result().rendimento+1.17)<1e-8);assert.equal(f.run('S.extrato.length'),1);
f=fixture({crypto:true});f.set('crypto-qtd',2);f.set('crypto-cotacao','');before=f.snapshot();f.run('saveInvestUpdate(1)');assert.equal(f.snapshot(),before,'Validação não altera dados da cripto');
f=fixture();f.run(`S.invest[0].historico.push({id:'a-update',tipo:'atualizacao',data:'2026-10-28',valor:1100});recalcInvestFromHistory(S.invest[0]);`);
f.set('data','2026-10-27');before=f.snapshot();f.run('saveInvestUpdate(1)');assert.equal(f.snapshot(),before,'Atualização retroativa deve ser bloqueada');
f=fixture();f.run(`S.invest[0].historico.push({id:'a-update',tipo:'atualizacao',data:'2026-10-28',valor:900});recalcInvestFromHistory(S.invest[0]);`);
let chart=f.run(`renderStockChart(S.invest[0],'2026-10','mes')`);
assert(chart.includes('Rentabilidade acumulada em porcentagem'));assert(chart.includes('-10.00%'),'Gráfico permite rentabilidade negativa');assert(!chart.includes('NaN'));
f.run(`investUi.metrica[1]='valor'`);chart=f.run(`renderStockChart(S.invest[0],'2026-10','mes')`);assert(chart.includes('Evolução do patrimônio em reais'));assert(chart.includes('R$ 900.00'),'Mesmo dia preserva ordem de inserção, não ordenação por ID');
f.run(`investUi.metrica[1]='porcentagem'`);chart=f.run(`renderStockChart(S.invest[0],'2026-10','ano')`);assert(chart.includes('-10.00%'));assert(!chart.includes('NaN'));
// Corrigir o lançamento já salvo não altera o saldo final nem duplica o aporte.
f=fixture({crypto:true,saldo:9.73});
f.run(`S.invest[0].historico.push({id:'antiga-hist',tipo:'atualizacao',data:'2026-10-28',valor:18.56});recalcInvestFromHistory(S.invest[0]);`);
assert(Math.abs(f.result().rendimento-8.83)<1e-8);
f.run(`corrigirFluxoUltimaAtualizacao(S.invest[0],'aporte',10,null)`);
assert.equal(f.result().final,18.56);assert(Math.abs(f.result().rendimento+1.17)<1e-8);assert.equal(f.run('S.extrato.length'),1);
before=f.snapshot();f.run(`corrigirFluxoUltimaAtualizacao(S.invest[0],'aporte',10,null)`);assert.equal(f.snapshot(),before,'Uma correção repetida não duplica o aporte');
f=fixture({meta:true});
f.run(`S.invest[0].historico.push({id:'old-hist',tipo:'atualizacao',data:'2026-10-28',valor:2000});recalcInvestFromHistory(S.invest[0]);S.invest[1].historico.push({id:'old-meta-2',tipo:'atualizacao',data:'2026-10-28',valor:200});recalcInvestFromHistory(S.invest[1]);`);
f.run(`corrigirFluxoUltimaAtualizacao(S.invest[0],'aporte',1000,null)`);
assert.equal(f.result().final,2000);assert.equal(f.result().rendimento,0);assert.equal(f.run('S.invest[1].valorAtual'),100,'Corrigir aporte antigo também corrige o rendimento derivado da meta');
f=fixture();f.set('flow','');before=f.snapshot();f.run('saveInvestUpdate(1)');assert.equal(f.snapshot(),before,'É obrigatório confirmar se houve movimentação');
f=fixture({meta:true});f.set('flow','resgate');f.set('flow-value',950);f.set('val',50);before=f.snapshot();f.run('saveInvestUpdate(1)');assert.equal(f.snapshot(),before,'Não resgatar dinheiro reservado em metas pelo investimento');
f=fixture({crypto:true});f.run(`S.invest[0].historico.push({id:'aporte-separado',tipo:'aporte',data:'2026-10-28',valor:200,extId:50});S.extrato.push({id:50,val:200,tipo:'investimento'});recalcInvestFromHistory(S.invest[0]);`);
f.set('crypto-qtd',2);f.set('crypto-cotacao',600);f.set('crypto-investido',1200);f.run('saveInvestUpdate(1)');assert.equal(f.result().rendimento,0);assert.equal(f.run('S.extrato.length'),1,'Fluxo já registrado no Extrato não deve ser duplicado');
f=fixture({meta:true});f.run(`S.invest[0].historico.push({id:'saved-hist',tipo:'atualizacao',data:'2026-10-28',valor:1300});recalcInvestFromHistory(S.invest[0]);S.invest[1].historico.push({id:'saved-meta-2',tipo:'atualizacao',data:'2026-10-28',valor:130});recalcInvestFromHistory(S.invest[1]);`);
f.run(`corrigirFluxoUltimaAtualizacao(S.invest[0],'aporte',200,1100)`);assert.equal(f.result().rendimento,100);assert(Math.abs(f.result().pct-10)<1e-8);assert.equal(f.run('S.invest[1].valorAtual'),110);
f=fixture({crypto:true});f.run(`S.extrato.push({id:60,data:'2026-10-28',tipo:'investimento',categoria:'Investimento',subcategoria:'Criptomoedas',val:200,destinoGrupo:'criptomoedas'});document.getElementById('update-flow-paid-1').checked=true;`);
f.set('flow','aporte');f.set('flow-value',200);f.set('crypto-qtd',2);f.set('crypto-cotacao',600);f.set('crypto-investido',1200);f.run('saveInvestUpdate(1)');assert.equal(f.result().final,1200);assert.equal(f.result().rendimento,0);assert.equal(f.run('S.extrato.length'),1,'Transferência geral já descontada não pode gerar novo débito ao atualizar a cripto');
f=fixture({crypto:true});f.run(`S.extrato.push({id:60,data:'2026-10-28',tipo:'investimento',val:200,destinoGrupo:'criptomoedas'});S.invest[0].historico.push({id:'forgot-hist',tipo:'atualizacao',data:'2026-10-28',valor:1200});recalcInvestFromHistory(S.invest[0]);corrigirFluxoUltimaAtualizacao(S.invest[0],'aporte',200,null,true);`);assert.equal(f.result().rendimento,0);assert.equal(f.run('S.extrato.length'),1,'Correção de atualização também respeita transferência já descontada');
console.log('PASS: aporte/resgate na atualização, TWR, resgate integral/reinvestimento, cripto, reservas, validação sem mutação e gráficos percentual/valor mensal/anual');

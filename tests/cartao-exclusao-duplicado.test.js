const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const src=fs.readFileSync('index.html','utf8').match(/<script\s*>([\s\S]*?)<\/script>/)[1];
function extract(name){const start=src.indexOf('function '+name+'(');assert(start>=0,name);const next=/\n(?:async )?function [A-Za-z]/.exec(src.slice(start+10));return src.slice(start,next?start+10+next.index:src.length);}
function fixture(){
 const S={cartao:[],extrato:[],cartoes:[{id:10,bank:'Itaú'}],saldoInicial:{valor:1000,data:'2026-10-01',idsIgnorados:[]}},alerts=[];
 let saves=0;
 const ctx=vm.createContext({S,Date,Math,Number,String,Array,Set,Map,console,cartaoMes:new Date(2026,10,1),resumoMes:new Date(2026,10,1),today:()=> '2026-11-07',appAlert:s=>alerts.push(s),fmt:n=>'R$ '+n.toFixed(2),saveData:()=>saves++,renderCartao(){},renderExtrato(){},updateResumo(){}});
 const functions=['isoDate','valorParcela','dueDateFor','vencimentoDaCompra','primeiroMesMensalidadeCartao','getParcelasCartao','saldoInicialValido','parcelaNoControleFinanceiro','parcelasCartaoFinanceiras','movimentoRealizado','movimentoNoControleFinanceiro','totalDaFaturaFinanceira','pagoNaFaturaFinanceira','delCC'];
 vm.runInContext(functions.map(extract).join('\n'),ctx);
 return {S,ctx,alerts,run:s=>vm.runInContext(s,ctx),saves:()=>saves};
}
const buy=(id,data='2026-10-01',val=100,parcelas=1)=>({id,data,val,parcelas,cardId:10,vencDia:10,desc:'Compra duplicada',tipo:'compra'});
const payment=(mes,val=100)=>({id:900,data:'2026-11-01',tipo:'saida',val,cardId:10,faturaMes:mes});
let f=fixture();f.S.cartao=[buy(1),buy(2)];f.S.extrato=[payment('2026-10')];
let payments=JSON.stringify(f.S.extrato);f.run('delCC(1)');assert.deepEqual(f.S.cartao.map(x=>x.id),[2]);assert.equal(JSON.stringify(f.S.extrato),payments);assert.equal(f.saves(),1);assert.equal(f.alerts.length,0);
f=fixture();f.S.cartao=[buy(1,'2026-09-01'),buy(2,'2026-09-01'),buy(3,'2026-10-01')];f.S.extrato=[payment('2026-10')];f.run('delCC(1)');assert.equal(f.S.cartao.length,2,'Duplicata histórica pode ser removida mesmo com pagamento em outro mês');
f=fixture();f.S.cartao=[buy(1)];f.S.extrato=[payment('2026-10')];const original=f.S.cartao;f.run('delCC(1)');assert.equal(f.S.cartao,original);assert.equal(f.saves(),0);assert(f.alerts[0].includes('2026-10'));assert(f.alerts[0].includes('100.00'));
f=fixture();f.S.cartao=[buy(1,'2026-10-01',200,2),buy(2,'2026-10-01',200,2)];f.S.extrato=[payment('2026-11')];f.run('delCC(1)');assert.equal(f.S.cartao.length,1);f.run('delCC(2)');assert.equal(f.S.cartao.length,1,'Pagamento de parcela futura também deve ser protegido');assert(f.alerts[0].includes('2026-11'));
f=fixture();f.S.cartao=[buy(1),buy(2,'2026-10-01',-10)];f.S.cartao[1].tipo='estorno';f.S.extrato=[payment('2026-10',100)];f.run('delCC(2)');assert.equal(f.S.cartao.length,1,'Excluir estorno pode reduzir uma divergência de pagamento');assert.equal(f.alerts.length,0);
f=fixture();f.S.cartao=[buy(1,'2026-09-01'),buy(2)];f.S.extrato=[payment('2026-10',150)];f.run('delCC(1)');assert.equal(f.S.cartao.length,1,'Divergência preexistente em outra fatura não bloqueia correção histórica');
f=fixture();f.S.cartao=[buy(1),buy(2)];f.S.extrato=[payment('2026-10')];const previous=f.S.cartao;f.run(`const originalTotal=totalDaFaturaFinanceira;totalDaFaturaFinanceira=(id,mes)=>{if(S.cartao.length===1)throw Error('Falha simulada');return originalTotal(id,mes);}`);assert.throws(()=>f.run('delCC(1)'));assert.equal(f.S.cartao,previous,'Simulação com erro deve restaurar as compras');assert.equal(f.saves(),0);
f=fixture();f.S.cartao=[buy(1)];f.run('delCC("1")');assert.equal(f.S.cartao.length,0,'IDs importados como texto também são encontrados');
console.log('PASS: exclusão de duplicatas históricas, faturas pagas, parcelas futuras, estorno, divergência anterior, restauração em erro e preservação dos pagamentos');

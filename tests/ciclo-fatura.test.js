const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const match=html.match(/<script\s*>([\s\S]*?)<\/script>/);
assert(match,'Script principal ausente');
function fn(name){
 const source=match[1],at=source.indexOf('function '+name+'(');
 assert(at>=0,'Função ausente: '+name);
 const rest=source.slice(at+10),next=/\n(?:async )?function [A-Za-z]/.exec(rest);
 return source.slice(at,next?at+10+next.index:source.length);
}
const names=['isoDate','monthKey','valorParcela','dataISOValida','saldoInicialValido','movimentoRealizado','movimentoNoControleFinanceiro','dueDateFor','vencimentoDaCompra','getMesMap','getParcelasCartao','parcelaNoControleFinanceiro','parcelasCartaoFinanceiras','getResumoCartaoExtrato','cartaoTemMes','isSameMonthDate','totalDaFaturaFinanceira','pagoNaFaturaFinanceira','faturasPendentesDoMes'];
const ctx=vm.createContext({console,Date,Set,Number,Math,String,Array,Error});
vm.runInContext("const S={extrato:[],cartao:[],invest:[],cartoes:[],saldoInicial:{valor:1000,data:'2026-09-18',idsIgnorados:[]}};function today(){return '2026-09-20'};"+names.map(fn).join('\n'),ctx);
const run=code=>vm.runInContext(code,ctx);
for(const day of ['01','02','09']){
 assert.strictEqual(run(`dueDateFor(new Date('2026-09-${day}T12:00:00'),10,0,null).toISOString().slice(0,10)`),'2026-09-10',`Compra dia ${day}, anterior ao dia 10, deve entrar em setembro`);
}
for(const day of ['10','11','19','30']){
 assert.strictEqual(run(`dueDateFor(new Date('2026-09-${day}T12:00:00'),10,0,null).toISOString().slice(0,10)`),'2026-10-10',`Compra dia ${day} deve entrar em outubro`);
}
assert.strictEqual(run("dueDateFor(new Date('2026-10-09T12:00:00'),10,0,null).toISOString().slice(0,10)"),'2026-10-10','Compra de 09/10 entra na fatura de 10/10');
assert.strictEqual(run("dueDateFor(new Date('2026-10-10T12:00:00'),10,0,null).toISOString().slice(0,10)"),'2026-11-10','Compra no próprio dia 10 vai ao mês seguinte');
assert.strictEqual(run("dueDateFor(new Date('2026-12-31T12:00:00'),10,0,null).toISOString().slice(0,10)"),'2027-01-10','Virada do ano');
assert.strictEqual(run("dueDateFor(new Date('2026-09-19T12:00:00'),10,1,null).toISOString().slice(0,10)"),'2026-11-10','Segunda parcela em novembro');
assert.strictEqual(run("dueDateFor(new Date('2026-09-04T12:00:00'),10,0,5).toISOString().slice(0,10)"),'2026-09-10','Fechamento explícito deve prevalecer');
assert.strictEqual(run("dueDateFor(new Date('2026-09-06T12:00:00'),10,0,5).toISOString().slice(0,10)"),'2026-10-10','Compra após fechamento específico');
run("S.cartoes=[{id:1,bank:'Itaú',dueDay:10}];S.cartao=[{id:101,cardId:1,data:'2026-09-01',desc:'Primeiro dia',val:100,parcelas:1,vencDia:10,closeDay:null},{id:102,cardId:1,data:'2026-09-10',desc:'Dia dez',val:50,parcelas:1,vencDia:10,closeDay:null},{id:103,cardId:1,data:'2026-09-19',desc:'Duas parcelas',val:120,parcelas:2,vencDia:10,closeDay:null},{id:104,cardId:1,data:'2026-09-30',desc:'Ultimo dia',val:70,parcelas:1,vencDia:10,closeDay:null}]");
assert.strictEqual(run("getMesMap()['2026-08']"),100,'Compra em 01/09 deve aparecer na fatura de setembro');
assert.strictEqual(run("getMesMap()['2026-09']"),180,'Outubro recebe somente compras em 10/09 ou depois');
assert.strictEqual(run("getMesMap()['2026-10']"),60,'Novembro deve receber apenas a segunda parcela');
assert.strictEqual(run('getResumoCartaoExtrato(2026,8)'),null,'Extrato de setembro não pode antecipar compras');
assert.strictEqual(run('getResumoCartaoExtrato(2026,9).val'),180,'Extrato de outubro deve ter a fatura prevista correta');
assert.strictEqual(run('getResumoCartaoExtrato(2026,10).val'),60,'Extrato de novembro deve ter a segunda parcela');
assert.strictEqual(run('cartaoTemMes(S.cartao[0],2026,8)'),true,'Compra de 01/09 deve aparecer na lista da fatura de setembro');
assert.strictEqual(run('cartaoTemMes(S.cartao[0],2026,9)'),false,'Compra de 01/09 não pode ser exibida outra vez em outubro');
assert.strictEqual(run('cartaoTemMes(S.cartao[2],2026,10)'),true,'Parcelado também aparece em novembro');
assert.strictEqual(run('cartaoTemMes(S.cartao[2],2026,11)'),false,'Não criar parcela inexistente');
assert.strictEqual(run('faturasPendentesDoMes(2026,8).length'),0,'Setembro sem fatura antecipada');
assert.strictEqual(run('faturasPendentesDoMes(2026,9)[0].val'),180,'Comprometimento do Extrato deve acompanhar a competência');
assert.strictEqual(run('parcelasCartaoFinanceiras().filter(p=>p.cardId===1).length'),4,'Parcelas antes do marco zero são apenas históricas, nunca despesas novas');
// Caso reportado: hotel comprado em 02/09 em 6x de R$ 1.348,38,
// primeira parcela histórica em setembro e última em fevereiro, sem debitar
// novamente o saldo inicial de 18/09.
run("S.cartao.push({id:999,cardId:1,data:'2026-09-02',desc:'Hotel - Home green Home',val:1348.38,parcelas:6,vencDia:10,closeDay:null})");
assert.strictEqual(run("getParcelasCartao().find(p=>p.id==='999-0').data"),'2026-09-10','Hotel tem primeira parcela em setembro');
assert.strictEqual(run("getParcelasCartao().find(p=>p.id==='999-5').data"),'2027-02-10','Hotel termina em fevereiro');
assert.strictEqual(run("getParcelasCartao().filter(p=>p.id.startsWith('999-')).reduce((s,p)=>s+Math.round(p.val*100),0)"),134838,'Nenhum centavo pode ser perdido nas seis parcelas');
assert.strictEqual(run('cartaoTemMes(S.cartao.find(c=>c.id===999),2026,8)'),true,'Hotel precisa aparecer em Setembro no Cartão');
assert.strictEqual(run('cartaoTemMes(S.cartao.find(c=>c.id===999),2027,2)'),false,'Hotel não pode aparecer após fevereiro');
assert.strictEqual(run("getMesMap()['2026-08']"),324.73,'Comprometimento histórico de setembro deve incluir hotel');
assert.strictEqual(run('getResumoCartaoExtrato(2026,8)'),null,'Hotel pago antes da abertura aparece só no histórico do cartão');
assert.strictEqual(run("getResumoCartaoExtrato(2026,9).val"),404.73,'Outubro deve conter somente segunda parcela do hotel, não a primeira');
// JSONs com pagamentos de fatura já conciliados não podem ter a referência reescrita.
run("S.cartoes.push({id:2,bank:'Cartão conciliado',dueDay:10});S.cartao.push({id:105,cardId:2,data:'2026-09-05',desc:'Compra paga na regra anterior',val:50,parcelas:1,vencDia:10,closeDay:null});S.extrato.push({id:200,data:'2026-09-20',tipo:'saida',cardId:2,faturaMes:'2026-09',val:50})");
assert.strictEqual(run("getParcelasCartao().find(x=>x.id==='105-0').data"),'2026-09-10','Não deslocar lançamento com pagamento já vinculado');
assert.strictEqual(run('cartaoTemMes(S.cartao.find(x=>x.id===105),2026,8)'),true,'Histórico conciliado permanece na fatura original');
assert(!match[1].includes('return isSameMonthDate(c.data,y,m);'),'Não exibir compras só por terem sido realizadas no mês');
console.log('PASS: antes do dia 10 no mês atual, dia 10 em diante no próximo; hotel, parcelas, extrato, marco zero e conciliações');

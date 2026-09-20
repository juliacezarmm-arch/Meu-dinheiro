const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const script=html.match(/<script\s*>([\s\S]*?)<\/script>/);
assert(script,'Script principal não localizado');
function fn(name){
 const start=script[1].indexOf('function '+name+'(');
 assert(start>=0,'Função ausente: '+name);
 const end=script[1].indexOf('\nfunction ',start+10);
 return script[1].slice(start,end<0?script[1].length:end);
}
const names=['isoDate','dataISOValida','valorParcela','saldoInicialValido','movimentoRealizado','movimentoNoControleFinanceiro','parcelaNoControleFinanceiro','parcelasCartaoFinanceiras','getParcelasCartao','dueDateFor','vencimentoDaCompra','totalDaFaturaFinanceira','pagoNaFaturaFinanceira','calcularSaldoDisponivelAte','faturasPendentesDoMes','calcularSobraPrevistaAte'];
const ctx=vm.createContext({console,Date,Set,Number,Math,String,Array,Error});
vm.runInContext(`const S={extrato:[],cartao:[],cartoes:[],invest:[],saldoInicial:{valor:1000,data:'2026-09-20',idsIgnorados:[]}};
function today(){return '2026-09-20';}
const window={cashRecurringForecasts:(y,m)=>y===2026&&m===9?[{data:'2026-10-22',val:3500,tipo:'entrada'},{data:'2026-10-10',val:1200,tipo:'saida'}]:[]};
`+names.map(fn).join('\n'),ctx);
const run=expr=>vm.runInContext(expr,ctx);
run("S.cartoes=[{id:7,bank:'Itaú',dueDay:10}];S.cartao=[{id:101,cardId:7,data:'2026-09-21',desc:'Compra',val:400,parcelas:1,vencDia:10}]");
assert.strictEqual(run("faturasPendentesDoMes(2026,9).length"),1,'Fatura futura deve aparecer no Extrato');
assert.strictEqual(run("faturasPendentesDoMes(2026,9)[0].val"),400);
assert.strictEqual(run("calcularSaldoDisponivelAte(today())"),1000,'Compra futura não deve alterar saldo de hoje');
assert.strictEqual(run("calcularSobraPrevistaAte('2026-10-31')"),2900,'Saldo futuro deduz recorrências e fatura');
run("S.extrato.push({id:80,data:'2026-09-20',tipo:'saida',cardId:7,faturaMes:'2026-10',val:100})");
assert.strictEqual(run("calcularSaldoDisponivelAte(today())"),900,'Pagamento parcial reduz saldo atual');
assert.strictEqual(run("faturasPendentesDoMes(2026,9)[0].val"),300,'Fatura mostra apenas valor em aberto');
assert.strictEqual(run("calcularSobraPrevistaAte('2026-10-31')"),2900,'Pagamento parcial não pode descontar em duplicidade');
run("S.extrato.push({id:81,data:'2026-09-20',tipo:'saida',cardId:7,faturaMes:'2026-10',val:300})");
assert.strictEqual(run("faturasPendentesDoMes(2026,9).length"),0,'Fatura quitada não reaparece pendente');
assert.strictEqual(run("calcularSobraPrevistaAte('2026-10-31')"),2900,'Pagamento total não altera sobra projetada duas vezes');
assert(html.includes('Marcar como pago</button>'),'Pagamento deve estar na linha do Extrato');
assert(!html.includes('onclick="registrarPagamentoFatura(${card.id}'),'Botão separado no Cartão não pode voltar');
console.log('PASS: sobra prevista, cartão/recorrências, pagamento parcial/total e ausência de desconto duplicado');

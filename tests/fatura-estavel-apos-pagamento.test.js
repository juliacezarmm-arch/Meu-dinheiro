const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const script=html.match(/<script\s*>([\s\S]*?)<\/script>/);assert(script);
const src=script[1];
function fn(name){
 const at=src.indexOf('function '+name+'(');assert(at>=0,name+' não encontrada');
 const rest=src.slice(at+10),next=/\n(?:async )?function [A-Za-z]/.exec(rest);
 return src.slice(at,next?at+10+next.index:src.length);
}
const names=['isoDate','monthKey','valorParcela','dataISOValida','saldoInicialValido','movimentoRealizado','movimentoNoControleFinanceiro','dueDateFor','vencimentoDaCompra','primeiroMesMensalidadeCartao','valorMensalidadeNoMes','parcelaMensalidadeCartao','getParcelasCartao','parcelaNoControleFinanceiro','parcelasCartaoFinanceiras','totalDaFaturaFinanceira','pagoNaFaturaFinanceira','faturasPendentesDoMes','totalDaFatura','pagoNaFatura'];
const ctx=vm.createContext({console,Date,Set,Number,Math,String,Array,Error});
vm.runInContext("let cartaoMes=new Date(2026,9,1),resumoMes=new Date(2026,9,1);const S={extrato:[],cartao:[],invest:[],cartoes:[],saldoInicial:{valor:2000,data:'2026-09-01',idsIgnorados:[]}};function today(){return '2026-10-21'};"+names.map(fn).join('\n'),ctx);
const run=code=>vm.runInContext(code,ctx);
run("S.cartoes=[{id:1,bank:'Itaú',dueDay:10,closeDay:null,paymentDay:19}];S.cartao=[{id:10,cardId:1,data:'2026-10-10',tipo:'compra',val:60,parcelas:1,vencDia:10,closeDay:null},{id:11,cardId:1,data:'2026-09-20',tipo:'compra',val:1628.34,parcelas:1,vencDia:10,closeDay:null}]");
assert.strictEqual(run("totalDaFaturaFinanceira(1,'2026-10')"),162834,'Antes do pagamento, fatura original');
assert.strictEqual(run("totalDaFaturaFinanceira(1,'2026-11')"),6000,'Compra do dia 10 já pertence a novembro');
assert.strictEqual(run("faturasPendentesDoMes(2026,9)[0].val"),1628.34);
run("S.extrato.push({id:20,tipo:'saida',data:'2026-10-19',cardId:1,faturaMes:'2026-10',val:1628.34})");
assert.strictEqual(run("totalDaFaturaFinanceira(1,'2026-10')"),162834,'Registrar pagamento não aumenta o total');
assert.strictEqual(run("totalDaFaturaFinanceira(1,'2026-11')"),6000,'Registrar pagamento não retira compra da fatura seguinte');
assert.strictEqual(run("faturasPendentesDoMes(2026,9).length"),0,'Não criar R$ 60 pendentes depois da quitação');
assert.strictEqual(run("faturasPendentesDoMes(2026,10)[0].val"),60);
assert.strictEqual(run("pagoNaFaturaFinanceira(1,'2026-10')"),162834,'Pagamento existente preservado');
assert(!fn('vencimentoDaCompra').includes('S.extrato.some'),'Ciclo não pode depender de pagamento');
console.log('PASS: pagamento não desloca compra do dia 10 nem cria saldo inesperado');

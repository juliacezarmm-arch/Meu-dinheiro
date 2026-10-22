const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('index.html','utf8');
const src=html.match(/<script\\s*>([\\s\\S]*?)<\\/script>/)?.[1];
assert(src,'Script do aplicativo nao encontrado.');
const extract=name=>{
 const at=src.indexOf('function '+name+'(');
 assert(at>=0,'Funcao '+name+' ausente.');
 const remaining=src.slice(at+10);
 const next=/\\n(?:async )?function [A-Za-z]/.exec(remaining);
 return src.slice(at,next?at+10+next.index:src.length);
};
const ctx=vm.createContext({
 console,Date,Number,Math,String,Array,Error,
 investPeriodo:'mes',investMes:new Date(2026,9,21),
 isoDate:(y,m,d)=>new Date(y,m,d,12).toISOString().slice(0,10)
});
const functions=['ensureInvestHistory','ordenarHistoricoInvest','recalcInvestFromHistory','avaliarRetornoInvestimento','calcInvestPeriodResult','calcInvestMonthResult'];
vm.runInContext(functions.map(extract).join('\\n'),ctx);
const analyze=(events)=>{
 ctx.item={id:1,historico:events.map((event,i)=>({id:'e'+i,...event}))};
 return vm.runInContext('recalcInvestFromHistory(item); calcInvestPeriodResult(item)',ctx);
};
let result=analyze([
 {tipo:'aporte',data:'2026-09-30',valor:1000},
 {tipo:'atualizacao',data:'2026-10-01',valor:1010},
 {tipo:'resgate',data:'2026-10-02',valor:400}
]);
assert.equal(result.rendimento,10);
assert(Math.abs(result.pct-1)<1e-7);
assert.equal(result.final,610);
result=analyze([
 {tipo:'aporte',data:'2026-09-30',valor:1000},
 {tipo:'aporte',data:'2026-10-02',valor:200},
 {tipo:'atualizacao',data:'2026-10-03',valor:1205}
]);
assert.equal(result.rendimento,5);
assert(Math.abs(result.pct-(5/1200)*100)<1e-7);
result=analyze([
 {tipo:'aporte',data:'2026-09-30',valor:1000},
 {tipo:'atualizacao',data:'2026-10-21',valor:1020},
 {tipo:'resgate',data:'2026-10-21',valor:280},
 {tipo:'atualizacao',data:'2026-10-21',valor:740}
]);
assert.equal(result.rendimento,20);
assert.equal(result.final,740);
assert(Math.abs(result.pct-2)<1e-7);
assert.equal(result.atualizacoes[0].rendimento,20);
assert.equal(result.atualizacoes[1].rendimento,20);
result=analyze([
 {tipo:'aporte',data:'2026-09-30',valor:1000},
 {tipo:'atualizacao',data:'2026-10-02',valor:980}
]);
assert.equal(result.rendimento,-20,'Prejuizo real deve continuar negativo.');
assert(result.pct<0);
console.log('PASS: rendimento/TWR sem confundir resgates, aportes e prejuizo real.');

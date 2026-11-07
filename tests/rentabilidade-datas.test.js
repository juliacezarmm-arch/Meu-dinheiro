const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const src=fs.readFileSync('index.html','utf8').match(/<script\s*>([\s\S]*?)<\/script>/)[1];
function extract(n){const a=src.indexOf('function '+n+'(');assert(a>=0,n);const m=/\n(?:async )?function [A-Za-z]/.exec(src.slice(a+10));return src.slice(a,m?a+10+m.index:src.length);}
const ctx=vm.createContext({Date,Math,Number,String,Array,Map,Set,console,investPeriodo:'mes',investMes:new Date(2026,9,7),today:()=> '2026-10-07'});
vm.runInContext(['isoDate','calcularDietz','ensureInvestHistory','ordenarHistoricoInvest','recalcInvestFromHistory','avaliarRetornoInvestimento','calcInvestPeriodResult','resumoGrupoInvestimentosPeriodo','conferirAtualizacaoInvestimento','ultimaConferenciaInvestimento'].map(extract).join('\n'),ctx);
const run=s=>vm.runInContext(s,ctx),close=(actual,expected)=>assert(Math.abs(actual-expected)<1e-8,actual+' != '+expected);
// Casos de referência: OpenAlloc SwiftModifiedDietz (retirada a meio do período).
close(run("calcularDietz('2026-01-01','2026-01-11',105,100,[{data:'2026-01-06',valor:-10}]).pct"),5);
close(run("calcularDietz('2026-01-01','2026-01-11',105,90,[{data:'2026-01-06',valor:-10}]).pct"),-5);
close(run("calcularDietz('2026-01-01','2026-01-11',1000,105,[{data:'2026-01-02',valor:-900}]).pct"),5/190*100);
close(run("calcularDietz('2026-01-01','2026-01-11',1000,105,[{data:'2026-01-10',valor:-900}]).pct"),5/910*100);
assert.equal(run("calcularDietz('2026-01-01','2026-01-01',100,105,[{data:'2026-01-01',valor:1}]).pct"),null);
assert.equal(run("calcularDietz('2026-01-01','2026-01-02',0,100,[{data:'2026-01-02',valor:100}]).pct"),null);
assert.equal(run("calcularDietz('2026-02-30','2026-03-02',100,105).pct"),null);
assert.equal(run("calcularDietz('2026-01-01','2026-01-11',100,200,[{data:'2026-01-06',valor:100}]).pct"),0);
close(run("calcularDietz('2026-10-01','2026-10-07',0,2510,[{data:'2026-10-06',valor:2500}]).pct"),.4);
const hist=[
 {id:'a',tipo:'atualizacao',data:'2026-09-28',valor:10000},
 {id:'b',tipo:'resgate',data:'2026-09-30',valor:1000},
 {id:'c',tipo:'resgate',data:'2026-10-03',valor:8500},
 {id:'d',tipo:'resgate',data:'2026-10-04',valor:200},
 {id:'e',tipo:'atualizacao',data:'2026-10-04',valor:305},
 {id:'f',tipo:'aporte',data:'2026-10-06',valor:2000},
 {id:'g',tipo:'resgate',data:'2026-10-07',valor:105},
 {id:'h',tipo:'atualizacao',data:'2026-10-07',valor:2204}];
ctx.item={id:1,historico:hist};const original=JSON.stringify(ctx.item);
let c=run("conferirAtualizacaoInvestimento({historico:item.historico.slice(0,4)},'2026-10-04',305)");
assert.equal(c.rendimento,5);close(c.pct,5/(10000-1000*4/6-8500/6)*100);
c=run('ultimaConferenciaInvestimento(item)');assert.equal(c.rendimento,4);close(c.pct,4/(305+2000/3)*100);
const r=run('calcInvestPeriodResult(item)');assert.equal(r.rendimento,9);assert.equal(r.final,2204);
const capital=9000-8500*4/6-200*3/6+2000/6;
close(r.pct,9/capital*100);
const group=run('resumoGrupoInvestimentosPeriodo([item])');close(group.pct,r.pct);
assert.equal(JSON.stringify(ctx.item),original,'Calcular percentuais não modifica valores nem histórico');
ctx.other={id:2,historico:[{id:'i',tipo:'atualizacao',data:'2026-09-30',valor:1000},{id:'j',tipo:'atualizacao',data:'2026-10-07',valor:1010}]};
const both=run('resumoGrupoInvestimentosPeriodo([item,other])');close(both.pct,(9+10)/(capital+1000)*100);
console.log('PASS: Modified Dietz por datas, referências, capital inválido, histórico sintético, períodos e consolidação, consolidação sem média de taxas e histórico intacto');

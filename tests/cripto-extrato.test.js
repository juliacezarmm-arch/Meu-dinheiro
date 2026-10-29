const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const src=fs.readFileSync('index.html','utf8').match(/<script\s*>([\s\S]*?)<\/script>/)[1];
function extract(name){const start=src.indexOf('function '+name+'(');assert(start>=0,name);const next=/\n(?:async )?function [A-Za-z]/.exec(src.slice(start+10));return src.slice(start,next?start+10+next.index:src.length);}
const elements={},field=id=>elements[id]||(elements[id]={value:'',innerHTML:'',hidden:false,textContent:''});
const S={extrato:[],cartao:[],cartoes:[],saldoInicial:{valor:100,data:'2026-10-01',idsIgnorados:[]},invest:[
 {id:1,kind:'investimento',nome:'Avalanche',tipo:'Cripto',valorAtual:20,totalAportado:20,totalResgatado:0,cryptoQtd:1,cryptoCotacao:20,historico:[{id:'initial',tipo:'aporte',data:'2026-10-01',valor:20}]},
 {id:2,kind:'investimento',nome:'CDB',tipo:'CDB',valorAtual:100,totalAportado:100,totalResgatado:0,historico:[{id:'initial2',tipo:'aporte',data:'2026-10-01',valor:100}]}
]};
const alerts=[],ctx=vm.createContext({S,console,Date,Number,Math,String,Array,Set,Map,JSON,Error,document:{getElementById:field},today:()=> '2026-10-28',investUi:{historico:{},mes:{}},
 appAlert:s=>alerts.push(s),saveData(){},renderExtrato(){},renderInvest(){},renderMetas(){},renderCartao(){},updateResumo(){},fecharPainelFlutuante(){},fecharJanela(){},abrirJanela(){},getMetaStorage:()=>null});
const names=['isoDate','escHtml','dataISOValida','valorMonetarioValido','saldoInicialValido','calcularSaldoDisponivelAte','isCryptoInvest','transferenciaCriptoSemDestino','novoIdExtrato','renderInvestDestinationOptions','addExtrato','editarLancamentoExtrato','salvarEdicaoExtrato','delExt','validarDadosImportados'];
vm.runInContext(names.map(extract).join('\n'),ctx);const run=s=>vm.runInContext(s,ctx);
field('ext-tipo').value='investimento';run('renderInvestDestinationOptions()');
assert(field('ext-invest-dest').innerHTML.includes('value="criptomoedas"'));
assert(!field('ext-invest-dest').innerHTML.includes('Avalanche'));
assert(field('ext-invest-dest').innerHTML.includes('CDB'));
field('ext-data').value='2026-10-28';field('ext-val').value='10';field('ext-invest-dest').value='criptomoedas';
const before=JSON.stringify(S.invest);run('addExtrato()');
assert.equal(JSON.stringify(S.invest),before,'Nenhuma moeda, cotação ou histórico é alterado');
assert.equal(S.extrato.length,1);assert.equal(S.extrato[0].tipo,'investimento');assert.equal(S.extrato[0].subcategoria,'Criptomoedas');assert.equal(S.extrato[0].destId,undefined);
assert.equal(run('calcularSaldoDisponivelAte(today())'),90);
assert.equal(run('validarDadosImportados(JSON.parse(JSON.stringify({versao:2,dados:S}))).extrato[0].destinoGrupo'),'criptomoedas');
assert.throws(()=>run(`validarDadosImportados({extrato:[{...S.extrato[0],destId:1}]})`),'Transferência geral não pode apontar para uma moeda');
ctx.target=S.extrato[0].id;run('editarLancamentoExtrato(target)');assert(field('extrato-edit-note').textContent.includes('sem alterar nenhuma moeda'));
field('extrato-edit-date').value='2026-10-27';field('extrato-edit-value').value='7';run('salvarEdicaoExtrato()');
assert.equal(S.extrato[0].val,7);assert.equal(S.extrato[0].tipo,'investimento');assert.equal(run('calcularSaldoDisponivelAte(today())'),93);assert.equal(JSON.stringify(S.invest),before);
run('delExt(target)');assert.equal(S.extrato.length,0);assert.equal(run('calcularSaldoDisponivelAte(today())'),100);assert.equal(JSON.stringify(S.invest),before);
field('ext-invest-dest').value='1';field('ext-val').value='10';run('addExtrato()');assert.equal(S.extrato.length,0,'Aporte direto em cripto é bloqueado mesmo com destino forçado');assert(alerts.length);
field('ext-invest-dest').value='criptomoedas';field('ext-data').value='2026-10-29';run('addExtrato()');assert.equal(S.extrato.length,0,'Transferência futura é bloqueada');
console.log('PASS: transferência geral para cripto, saldo, importação, edição, exclusão e bloqueio de aporte direto sem alterar as moedas');

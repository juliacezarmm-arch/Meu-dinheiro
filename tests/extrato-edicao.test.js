const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const script=html.match(/<script\s*>([\s\S]*?)<\/script>/)[1];
for(const id of ['extrato-editor','extrato-edit-form','extrato-edit-date','extrato-edit-value','extrato-edit-type','extrato-edit-category','extrato-edit-subcategory','extrato-edit-description','extrato-edit-payment'])assert(html.includes('id="'+id+'"'),'Ausente: '+id);
assert(script.includes('onclick="editarLancamentoExtrato(${Number(r.id)})"'),'Lápis deve aparecer junto do X para lançamentos editáveis');
assert(script.includes("r.auto?'':"),'Linhas automáticas não devem ganhar edição incorreta');
assert(!script.includes('localStorage'),'Edição não usa armazenamento paralelo');
function extrair(nome){const re=new RegExp('^function '+nome+'\\([^\\n]*\\)\\{[\\s\\S]*?^\\}\\n','m');const m=script.match(re);assert(m,'Função não encontrada: '+nome);return m[0];}
const campos={
 'extrato-edit-date':{value:'2026-09-21'},'extrato-edit-value':{value:'12.50'},
 'extrato-edit-type':{value:'saida'},'extrato-edit-category':{value:'Alimentação'},
 'extrato-edit-subcategory':{value:'Restaurante'},'extrato-edit-description':{value:'Almoço corrigido'},
 'extrato-edit-payment':{value:'pix'}
};
const dados={extrato:[{id:42,data:'2026-09-20',tipo:'saida',categoria:'Alimentação',subcategoria:'Lanche',desc:'Almoço',pagamento:'debito',gastoTipo:'variavel',val:10}],invest:[],saldoInicial:{data:'2026-09-18',valor:100,idsIgnorados:[]}};
let gravacoes=0,mensagens=[],renderizacoes=0;
const ctx=vm.createContext({S:dados,document:{getElementById:id=>campos[id]},Date,Math,Number,String,Map,Array,
 editingExtratoId:42,extratoMes:new Date(),today:()=> '2026-09-21',
 dataISOValida:v=>/^2026-09-(20|21)$/.test(v),valorMonetarioValido:v=>Number.isFinite(v)&&v>=0&&Math.round(v*100)===v*100,
 appAlert:m=>mensagens.push(m),saveData:()=>gravacoes++,fecharJanela:()=>{},
 renderInvest:()=>renderizacoes++,renderMetas:()=>renderizacoes++,renderCartao:()=>renderizacoes++,renderExtrato:()=>renderizacoes++,updateResumo:()=>renderizacoes++,
 ensureInvestHistory:i=>i.historico,recalcInvestFromHistory:i=>{i.valorAtual=i.historico.reduce((s,h)=>s+(h.tipo==='aporte'?h.valor:-h.valor),0)},
 metasReservadasNoInvestimento:()=>[],totalDaFaturaFinanceira:()=>20000});
vm.runInContext(extrair('simularSaldoHistoricoExtrato')+extrair('salvarEdicaoExtrato'),ctx);
vm.runInContext('salvarEdicaoExtrato()',ctx);
assert.strictEqual(dados.extrato.length,1,'Editar não duplica lançamentos');
assert.strictEqual(dados.extrato[0].id,42,'Preserva ID');
assert.strictEqual(dados.extrato[0].desc,'Almoço corrigido');
assert.strictEqual(dados.extrato[0].val,12.5);
assert.strictEqual(gravacoes,1,'Salva alteração no JSON');
assert.strictEqual(renderizacoes,5,'Atualiza telas e totais');
campos['extrato-edit-value'].value='0';vm.runInContext('salvarEdicaoExtrato()',ctx);
assert.strictEqual(gravacoes,1,'Valor inválido não grava');
assert.strictEqual(dados.extrato[0].val,12.5);
// Pagamento vinculado: não permite valor acima da fatura e mantém cardId/faturaMes.
dados.extrato[0]={id:42,data:'2026-09-20',tipo:'saida',cardId:7,faturaMes:'2026-09',val:30};
campos['extrato-edit-value'].value='250';vm.runInContext('salvarEdicaoExtrato()',ctx);
assert.strictEqual(dados.extrato[0].val,30);
assert.strictEqual(gravacoes,1);
campos['extrato-edit-value'].value='40';vm.runInContext('salvarEdicaoExtrato()',ctx);
assert.strictEqual(dados.extrato[0].val,40);
assert.strictEqual(dados.extrato[0].faturaMes,'2026-09');
// Aporte vinculado: altera histórico no mesmo registro, sem criar outro.
dados.invest=[{id:9,kind:'investimento',valorAtual:100,historico:[{id:'42-hist',extId:42,tipo:'aporte',data:'2026-09-20',valor:100}]}];
dados.extrato[0]={id:42,data:'2026-09-20',tipo:'investimento',destId:9,val:100};
campos['extrato-edit-value'].value='75';vm.runInContext('salvarEdicaoExtrato()',ctx);
assert.strictEqual(dados.invest[0].historico[0].valor,75);
assert.strictEqual(dados.invest[0].valorAtual,75);
assert.strictEqual(dados.extrato[0].val,75);
assert.strictEqual(dados.extrato.length,1);
// Correção de aporte que deixaria resgate futuro sem saldo deve ser recusada.
dados.invest[0].historico.push({id:'outro',tipo:'resgate',data:'2026-09-21',valor:70});
campos['extrato-edit-value'].value='50';vm.runInContext('salvarEdicaoExtrato()',ctx);
assert.strictEqual(dados.extrato[0].val,75);
assert.strictEqual(dados.invest[0].historico[0].valor,75);
console.log('PASS: edição sem duplicação, histórico vinculado, fatura, validação, atualização e JSON');

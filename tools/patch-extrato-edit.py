from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

def trocar(antigo, novo):
    global html
    quantidade = html.count(antigo)
    assert quantidade == 1, f'Esperado 1 trecho, encontrado {quantidade}: {antigo[:100]!r}'
    html = html.replace(antigo, novo, 1)

# Botao compacto ao lado do X e formulario em janela, sem confundir com novos lancamentos.
trocar('.del:hover{color:#A32D2D}', '.del:hover{color:#A32D2D}\n.extrato-edit-btn{color:#9FE1CB;min-width:27px;min-height:30px;font-size:17px;font-weight:800}\n.extrato-edit-btn:hover,.extrato-edit-btn:focus-visible{color:#fff;background:#224336;outline:1px solid #9FE1CB}\n#extrato-editor [hidden]{display:none!important}\n#extrato-edit-regular{display:grid;grid-template-columns:minmax(0,1fr);gap:0}')

modal = '''<div id="extrato-editor" class="site-dialog" role="dialog" aria-modal="true" aria-labelledby="extrato-editor-title" hidden><div class="site-dialog-panel">
  <div class="site-dialog-heading"><span class="site-dialog-icon" aria-hidden="true">✎</span><h2 id="extrato-editor-title">Editar lançamento</h2></div>
  <p class="site-dialog-copy" id="extrato-edit-note">Corrija os dados do lançamento sem criar uma cópia.</p>
  <form id="extrato-edit-form" novalidate onsubmit="event.preventDefault();salvarEdicaoExtrato()">
    <label class="site-field" for="extrato-edit-date">Data<input type="date" id="extrato-edit-date" required></label>
    <div id="extrato-edit-regular">
      <label class="site-field" for="extrato-edit-type">Tipo<select id="extrato-edit-type" onchange="atualizarCategoriasEdicaoExtrato()"><option value="entrada">Entrada</option><option value="saida">Saída</option></select></label>
      <label class="site-field" for="extrato-edit-category">Categoria<select id="extrato-edit-category" onchange="atualizarSubcategoriasEdicaoExtrato()" required></select></label>
      <label class="site-field" for="extrato-edit-subcategory">Subcategoria<select id="extrato-edit-subcategory" required></select></label>
      <label class="site-field" for="extrato-edit-description">Descrição<input id="extrato-edit-description" type="text" maxlength="40" placeholder="Descrição (opcional)"></label>
      <label class="site-field" for="extrato-edit-payment" id="extrato-edit-payment-row">Forma de pagamento<select id="extrato-edit-payment"></select></label>
    </div>
    <label class="site-field" for="extrato-edit-value">Valor (R$)<input type="number" id="extrato-edit-value" min="0.01" step="0.01" inputmode="decimal" required></label>
    <div class="site-dialog-actions"><button type="button" class="site-button quiet" onclick="fecharJanela('extrato-editor')">Cancelar</button><button type="submit" class="site-button primary">Salvar alteração</button></div>
  </form>
</div></div>
'''
trocar('<div id="card-editor" class="site-dialog"', modal + '<div id="card-editor" class="site-dialog"')
trocar('let editingCartaoId=null;', 'let editingCartaoId=null;\nlet editingExtratoId=null;')
trocar("if(id==='card-editor')editingRegisteredCardId=null;", "if(id==='card-editor')editingRegisteredCardId=null;if(id==='extrato-editor')editingExtratoId=null;")
trocar("['card-editor','card-payment-editor','card-paid-editor']", "['extrato-editor','card-editor','card-payment-editor','card-paid-editor']")

funcoes = '''// Editar nao exclui nem recria o registro: conserva ID e vinculos no JSON.
function atualizarCategoriasEdicaoExtrato(){
  const tipo=document.getElementById('extrato-edit-type').value;
  const select=document.getElementById('extrato-edit-category');
  const anterior=select.value;
  select.replaceChildren(new Option('Selecione categoria',''),...Object.keys(CATEGORIAS[tipo]||{}).map(c=>new Option(c,c)));
  if([...select.options].some(o=>o.value===anterior))select.value=anterior;
  atualizarSubcategoriasEdicaoExtrato();
  document.getElementById('extrato-edit-payment-row').hidden=tipo!=='saida';
}
function atualizarSubcategoriasEdicaoExtrato(){
  const tipo=document.getElementById('extrato-edit-type').value;
  const categoria=document.getElementById('extrato-edit-category').value;
  const select=document.getElementById('extrato-edit-subcategory');
  const anterior=select.value;
  const cadastradas=(CATEGORIAS[tipo]&&CATEGORIAS[tipo][categoria])||[];
  const permitidas=S.saldoInicial&&tipo==='entrada'?cadastradas.filter(x=>x!=='Dinheiro do mês passado'):cadastradas;
  const opcoes=categoria?[...permitidas.filter(x=>x!=='Outros'),'Outros']:[];
  select.replaceChildren(new Option('Selecione subcategoria',''),...opcoes.map(s=>new Option(s,s)));
  if([...select.options].some(o=>o.value===anterior))select.value=anterior;
}
function opcaoHistoricaEdicao(select,valor){
  if(valor&&!Array.from(select.options).some(o=>o.value===valor))select.add(new Option(valor,valor));
  select.value=valor||'';
}
function editarLancamentoExtrato(id){
  const item=S.extrato.find(x=>String(x.id)===String(id));
  if(!item)return;
  editingExtratoId=item.id;
  const vinculado=!!(item.destId||item.faturaMes||item.tipo==='investimento'||item.tipo==='meta');
  document.getElementById('extrato-edit-date').value=item.data;
  document.getElementById('extrato-edit-value').value=String(item.val);
  document.getElementById('extrato-edit-regular').hidden=vinculado;
  document.getElementById('extrato-edit-note').textContent=item.faturaMes
    ?'Pagamento da fatura '+item.faturaMes+': corrija a data e o valor. O vínculo com o cartão permanece.'
    :item.destId||['investimento','meta'].includes(item.tipo)
      ?'Movimentação vinculada a investimento ou meta: corrija a data e o valor. O destino e o histórico permanecem vinculados.'
      :'Corrija data, tipo, categoria, subcategoria, descrição ou valor. O registro original será atualizado.';
  if(!vinculado){
    document.getElementById('extrato-edit-type').value=item.tipo==='saida'?'saida':'entrada';
    atualizarCategoriasEdicaoExtrato();
    const categoria=document.getElementById('extrato-edit-category');
    opcaoHistoricaEdicao(categoria,item.categoria);
    atualizarSubcategoriasEdicaoExtrato();
    opcaoHistoricaEdicao(document.getElementById('extrato-edit-subcategory'),item.subcategoria);
    document.getElementById('extrato-edit-description').value=item.desc||'';
    const pagamento=document.getElementById('extrato-edit-payment');
    pagamento.innerHTML=document.getElementById('ext-pagamento').innerHTML;
    opcaoHistoricaEdicao(pagamento,item.pagamento);
    document.getElementById('extrato-edit-payment-row').hidden=item.tipo!=='saida';
  }
  abrirJanela('extrato-editor');
}
// Calcula primeiro em uma copia para impedir resgates acima do saldo apos corrigir um aporte.
function simularSaldoHistoricoExtrato(historico,id,data,valor){
  let saldo=0;
  const ordenado=historico.map(h=>String(h.extId)===String(id)?{...h,data,valor}:{...h})
    .sort((a,b)=>(a.data||'').localeCompare(b.data||'')||String(a.id).localeCompare(String(b.id)));
  for(const h of ordenado){
    const n=Number(h.valor||0);
    if(!Number.isFinite(n)||n<0)return null;
    if(h.tipo==='aporte')saldo+=n;
    else if(h.tipo==='resgate'){
      if(n>saldo+0.000001)return null;
      saldo-=n;
    }else if(h.tipo==='atualizacao')saldo=n;
  }
  return Math.round(saldo*100)/100;
}
function salvarEdicaoExtrato(){
  const item=S.extrato.find(x=>String(x.id)===String(editingExtratoId));
  if(!item){fecharJanela('extrato-editor');return;}
  const data=document.getElementById('extrato-edit-date').value;
  const campo=document.getElementById('extrato-edit-value').value.trim();
  const numero=Number(campo);
  if(!dataISOValida(data)||!campo||!valorMonetarioValido(numero)||numero<=0){
    appAlert('Informe uma data válida e um valor positivo, com até duas casas decimais.');return;
  }
  const valor=Math.round(numero*100)/100;
  const vinculados=!!item.destId;
  const pagamentoFatura=!!item.faturaMes;
  if(vinculados){
    if(data>today()){appAlert('Movimentações de investimentos e metas não podem ter data futura.');return;}
    const historicos=S.invest.map(dest=>({dest,registros:ensureInvestHistory(dest).filter(h=>String(h.extId)===String(item.id))})).filter(x=>x.registros.length);
    const destino=S.invest.find(x=>String(x.id)===String(item.destId));
    if(!destino||!historicos.length||historicos.some(x=>x.registros.some(h=>!['aporte','resgate'].includes(h.tipo)))){
      appAlert('Vínculo do histórico não encontrado. Nenhum dado foi alterado.');return;
    }
    const saldos=new Map();
    for(const {dest} of historicos){
      const saldo=simularSaldoHistoricoExtrato(ensureInvestHistory(dest),item.id,data,valor);
      if(saldo===null){appAlert('A alteração deixaria um resgate maior que o saldo disponível no histórico.');return;}
      saldos.set(String(dest.id),saldo);
    }
    const storageId=destino.kind==='meta'?destino.storageId:destino.id;
    if(storageId){
      const storage=S.invest.find(x=>String(x.id)===String(storageId)&&x.kind==='investimento');
      if(storage){
        const saldoStorage=saldos.has(String(storage.id))?saldos.get(String(storage.id)):Number(storage.valorAtual||0);
        const reservado=metasReservadasNoInvestimento(storage.id).reduce((total,meta)=>total+(saldos.has(String(meta.id))?saldos.get(String(meta.id)):Number(meta.valorAtual||0)),0);
        if(reservado>saldoStorage+0.000001){appAlert('A correção deixaria metas reservadas acima do saldo do investimento.');return;}
      }
    }
    for(const {dest,registros} of historicos){
      for(const h of registros){h.data=data;h.valor=valor;}
      recalcInvestFromHistory(dest);
    }
  }else if(['investimento','meta'].includes(item.tipo)){
    appAlert('Este lançamento não possui vínculo com o investimento. Nenhum dado foi alterado.');return;
  }
  if(pagamentoFatura){
    if(!item.cardId||!S.saldoInicial||data<S.saldoInicial.data||data>today()){
      appAlert('A data do pagamento deve estar entre o início do controle e hoje.');return;
    }
    const total=totalDaFaturaFinanceira(item.cardId,item.faturaMes);
    const outros=S.extrato.filter(x=>String(x.id)!==String(item.id)&&x.tipo==='saida'&&String(x.cardId)===String(item.cardId)&&x.faturaMes===item.faturaMes)
      .reduce((s,x)=>s+Math.round(Number(x.val||0)*100),0);
    if(Math.round(valor*100)+outros>total||total<=0){
      appAlert('O valor corrigido não pode ultrapassar o total da fatura, descontados os outros pagamentos.');return;
    }
  }else if(!vinculados){
    const tipo=document.getElementById('extrato-edit-type').value;
    const categoria=document.getElementById('extrato-edit-category').value;
    const subcategoria=document.getElementById('extrato-edit-subcategory').value;
    const desc=document.getElementById('extrato-edit-description').value.trim();
    const pagamento=document.getElementById('extrato-edit-payment').value;
    if(!['entrada','saida'].includes(tipo)||!categoria||!subcategoria||desc.length>40){appAlert('Confira o tipo, a categoria, a subcategoria e a descrição.');return;}
    if(tipo==='saida'&&!pagamento){appAlert('Para saídas, escolha a forma de pagamento.');return;}
    if(S.saldoInicial&&tipo==='saida'&&categoria==='Cartão de crédito'&&subcategoria==='Pagamento de fatura'){
      appAlert('Registre pagamentos de fatura na aba Cartão para evitar duplicidade.');return;
    }
    if(S.saldoInicial&&tipo==='entrada'&&subcategoria==='Dinheiro do mês passado'){
      appAlert('O saldo anterior já é transportado automaticamente.');return;
    }
    item.tipo=tipo;item.categoria=categoria;item.subcategoria=subcategoria;item.desc=desc;
    item.pagamento=tipo==='saida'?pagamento:'';
    item.gastoTipo=tipo==='saida'?(item.gastoTipo||'variavel'):'';
  }
  item.data=data;
  item.val=valor;
  fecharJanela('extrato-editor');
  extratoMes=new Date(data+'T12:00:00');
  saveData();
  renderInvest();renderMetas();renderCartao();renderExtrato();updateResumo();
  appAlert('Lançamento corrigido. O mesmo registro foi atualizado, sem duplicar.');
}

'''
trocar('function resetCartaoForm(){', funcoes + 'function resetCartaoForm(){')

linhas=html.splitlines(keepends=True)
indices=[i for i,linha in enumerate(linhas) if linha.strip().startswith('const action=r.faturaPendente?')]
assert len(indices)==1, f'Linha de acoes do extrato encontrada {len(indices)} vezes'
i=indices[0]
assert 'delExt(' in linhas[i] and "r.auto?'':" in linhas[i], 'Linha de acoes mudou: abortando patch'
linhas[i] = '''      const action=r.faturaPendente?`<button class="extrato-pagar" type="button" onclick="registrarPagamentoFatura(${Number(r.cardId)},'${r.faturaMes}')" aria-label="Marcar como pago ${escHtml(r.desc)}">Marcar como pago</button>`:r.auto?'':`<button class="del extrato-edit-btn" type="button" onclick="editarLancamentoExtrato(${Number(r.id)})" aria-label="Editar lançamento" title="Corrige os dados deste lançamento sem duplicar.">✎</button><button class="del" type="button" onclick="delExt(${Number(r.id)})" aria-label="Remover" title="Apaga este lançamento do extrato."><i class="ti ti-x" aria-hidden="true"></i></button>`;
'''
html=''.join(linhas)
path.write_text(html,encoding='utf-8')

Path('tests/extrato-edicao.test.js').write_text(r'''const assert=require('assert'),fs=require('fs'),vm=require('vm');
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
''',encoding='utf-8')
print('PATCH OK: index.html e testes/extrato-edicao.test.js preparados')

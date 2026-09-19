from pathlib import Path

path = Path('index.html')
src = path.read_text(encoding='utf-8-sig')
assert 'function calcularSaldoDisponivelAte(' not in src, 'Saldo inicial já implementado; não reaplicar'

def once(old, new):
    global src
    occurrences = src.count(old)
    assert occurrences == 1, f'Esperado um ponto de alteração, encontrado {occurrences}: {old[:90]!r}'
    src = src.replace(old, new, 1)

def in_function(name, old, new):
    global src
    head = 'function ' + name + '('
    start = src.find(head)
    assert start >= 0, f'Função não encontrada: {name}'
    end = src.find('\nfunction ', start + len(head))
    if end < 0:
        end = len(src)
    block = src[start:end]
    assert block.count(old) == 1, f'Trecho esperado em {name}: {old[:95]!r}, encontrado {block.count(old)}'
    src = src[:start] + block.replace(old, new, 1) + src[end:]

once('\n</style>','''
/* Saldo de abertura: não se mistura com entradas nem com a projeção de faturas. */
.saldo-setup{background:#171716;border:1px solid #3a3934;border-radius:14px;padding:1rem;margin:0 0 1rem}
.saldo-setup strong{font-size:14px}
.saldo-setup p,.saldo-note{font-size:12px;color:var(--color-text-secondary);line-height:1.45;margin:.35rem 0 .7rem}
.saldo-setup label{font-size:12px;color:var(--color-text-secondary);display:flex;flex-direction:column;gap:5px}
.saldo-setup .saldo-data{font-size:12px;align-self:center;color:var(--color-text-secondary)}
.saldo-setup .saldo-data strong{display:block;color:var(--color-text-primary);margin-top:5px}
.saldo-setup button,.saldo-link{background:#1D9E75;color:#fff;border:0;border-radius:8px;padding:9px 12px;font-weight:700;cursor:pointer}
.saldo-setup .saldo-corrigir{background:#242423;border:1px solid #4a4944;font-size:12px}
.saldo-setup [hidden],[hidden].saldo-link{display:none!important}
.saldo-note{margin:-.6rem 0 .8rem}
.saldo-link{margin:-.25rem 0 .85rem;font-size:12px}
@media(max-width:520px){.saldo-setup .row2{grid-template-columns:1fr}}
</style>''')

once('''    <div class="cards">
      <div class="card" title="Tudo que entrou de dinheiro neste mês,''','''    <p class="saldo-note" id="saldo-note">Informe seu saldo inicial para começar a acompanhar o dinheiro que você realmente tem.</p>
    <button class="saldo-link" id="saldo-link" type="button" onclick="goToSaldoInicial()">Informar saldo inicial</button>
    <div class="cards">
      <div class="card" title="Tudo que entrou de dinheiro neste mês,''')

once('''  <!-- EXTRATO -->
  <div id="page-extrato" class="page">
    <div class="add-form">''','''  <!-- EXTRATO -->
  <div id="page-extrato" class="page">
    <section id="saldo-setup" class="saldo-setup" aria-label="Configurar saldo inicial">
      <strong>Dinheiro disponível para começar</strong>
      <p>Informe quanto você tem livre agora (sem incluir investimentos ou metas). Esse é o ponto de partida: não será contado como uma entrada. Abra seu arquivo de dados antes, se já utiliza o aplicativo.</p>
      <div id="saldo-start-form">
        <div class="row row2">
          <label for="saldo-inicial-valor">Saldo inicial (R$)
            <input id="saldo-inicial-valor" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0,00" />
          </label>
          <div class="saldo-data">Data de referência<strong id="saldo-data-referencia"></strong></div>
        </div>
        <button id="saldo-submit" type="button" onclick="confirmarSaldoInicial()">Começar a acompanhar</button>
      </div>
      <div id="saldo-start-saved" hidden>
        <p id="saldo-start-descricao"></p>
        <button type="button" class="saldo-corrigir" onclick="editarSaldoInicial()">Corrigir valor inicial</button>
      </div>
      <p style="margin:.65rem 0 0">Depois, lance entradas, despesas e transferências no extrato. O pagamento da fatura deve ser lançado como saída; compras no crédito, por si só, não diminuem o saldo real.</p>
    </section>
    <div class="add-form">''')

once('''const S={extrato:[],cartao:[],invest:[],cartoes:[]};''','''const S={extrato:[],cartao:[],invest:[],cartoes:[],saldoInicial:null};''')
once("function today(){return new Date().toISOString().split('T')[0];}","function today(){const d=new Date();return isoDate(d.getFullYear(),d.getMonth(),d.getDate());}")
once('''    'Outros':['Presentes','Emergências','Compras diversas','Serviços gerais']''','''    'Outros':['Presentes','Emergências','Compras diversas','Serviços gerais'],
    'Cartão de crédito':['Pagamento de fatura']''')

once('''function saveData(){''','''function novoIdExtrato(){
  let id=Date.now();
  while(S.extrato.some(x=>String(x.id)===String(id)))id++;
  return id;
}
function saldoInicialValido(valor){
  return valor&&Number.isFinite(Number(valor.valor))&&Number(valor.valor)>=0&&
    /^\\d{4}-\\d{2}-\\d{2}$/.test(valor.data)&&Array.isArray(valor.idsIgnorados);
}
function calcularSaldoDisponivelAte(limite){
  if(!saldoInicialValido(S.saldoInicial))return null;
  const base=S.saldoInicial;
  const dataFinal=limite&&limite<today()?limite:today();
  if(dataFinal<base.data)return null;
  const ignorados=new Set(base.idsIgnorados.map(String));
  let centavos=Math.round(Number(base.valor)*100);
  for(const item of S.extrato){
    if(ignorados.has(String(item.id))||!item.data||item.data<base.data||item.data>dataFinal)continue;
    if(item.tipo==='entrada'&&item.subcategoria==='Dinheiro do mês passado')continue;
    const valor=Math.round(Number(item.val||0)*100);
    if(item.tipo==='entrada')centavos+=valor;
    if(['saida','investimento','meta'].includes(item.tipo))centavos-=valor;
  }
  return centavos/100;
}
function renderSaldoInicial(){
  const existente=saldoInicialValido(S.saldoInicial);
  const formulario=document.getElementById('saldo-start-form');
  const gravado=document.getElementById('saldo-start-saved');
  const aviso=document.getElementById('saldo-start-descricao');
  const data=document.getElementById('saldo-data-referencia');
  if(!formulario||!gravado)return;
  formulario.hidden=existente;
  gravado.hidden=!existente;
  data.textContent=existente?S.saldoInicial.data.split('-').reverse().join('/'):today().split('-').reverse().join('/');
  if(existente)aviso.textContent='Saldo de partida: '+fmt(S.saldoInicial.valor)+' em '+S.saldoInicial.data.split('-').reverse().join('/')+'. Os registros anteriores foram preservados, mas não serão somados de novo.';
  document.getElementById('saldo-submit').textContent=existente?'Salvar correção':'Começar a acompanhar';
}
function editarSaldoInicial(){
  if(!saldoInicialValido(S.saldoInicial))return;
  document.getElementById('saldo-inicial-valor').value=String(S.saldoInicial.valor);
  document.getElementById('saldo-start-form').hidden=false;
  document.getElementById('saldo-start-saved').hidden=true;
  document.getElementById('saldo-inicial-valor').focus();
}
function confirmarSaldoInicial(){
  const campo=document.getElementById('saldo-inicial-valor');
  const valor=Number(campo.value);
  if(campo.value.trim()===''||!Number.isFinite(valor)||valor<0||Math.round(valor*100)/100!==valor){
    alert('Informe um saldo válido em reais, com até duas casas decimais. Pode ser zero.');return;
  }
  if(saldoInicialValido(S.saldoInicial)){
    if(!confirm('Corrigir apenas o valor inicial? A data e os lançamentos já registrados serão mantidos.'))return;
    S.saldoInicial.valor=valor;
  }else{
    S.saldoInicial={valor,data:today(),idsIgnorados:S.extrato.map(x=>String(x.id))};
  }
  saveData();
  renderSaldoInicial();renderExtrato();updateResumo();
  setSaveStatus('Saldo definido. Use Salvar ou Salvar como para guardar no arquivo de dados.');
}
function goToSaldoInicial(){
  const botao=document.querySelectorAll('.nav button')[1];
  showPage('extrato',botao);
  document.getElementById('saldo-setup').scrollIntoView({behavior:'smooth',block:'start'});
  document.getElementById('saldo-inicial-valor').focus();
}
function saveData(){''')

once('''  return {versao:1,exportadoEm:new Date().toISOString(),dados:S};''','''  return {versao:2,exportadoEm:new Date().toISOString(),dados:S};''')
once('''  ['extrato','cartao','invest','cartoes'].forEach(key=>{
    S[key]=Array.isArray(dados[key])?dados[key]:[];
  });
  renderInvestDestinationOptions();''','''  ['extrato','cartao','invest','cartoes'].forEach(key=>{
    S[key]=Array.isArray(dados[key])?dados[key]:[];
  });
  S.saldoInicial=saldoInicialValido(dados.saldoInicial)
    ? {valor:Number(dados.saldoInicial.valor),data:dados.saldoInicial.data,idsIgnorados:dados.saldoInicial.idsIgnorados.map(String)}
    : null;
  renderSaldoInicial();
  renderInvestDestinationOptions();''')

in_function('updateSubcategorias','''  const subcategorias=(CATEGORIAS[tipo]&&CATEGORIAS[tipo][categoria])||[];''','''  const cadastradas=(CATEGORIAS[tipo]&&CATEGORIAS[tipo][categoria])||[];
  const subcategorias=S.saldoInicial&&tipo==='entrada'?cadastradas.filter(x=>x!=='Dinheiro do mês passado'):cadastradas;''')
in_function('addExtrato','''  if(tipo==='investimento'||tipo==='meta'){''','''  if(S.saldoInicial&&tipo==='entrada'&&subcategoria==='Dinheiro do mês passado'){
    alert('O saldo anterior já é transportado automaticamente. Registre apenas dinheiro que realmente entrou.');return;
  }
  if(tipo==='investimento'||tipo==='meta'){''')
in_function('addExtrato','''    const extId=Date.now();''','''    const extId=novoIdExtrato();''')
in_function('addExtrato','''    renderInvest();renderMetas();renderExtrato();updateResumo();''','''    saveData();renderInvest();renderMetas();renderExtrato();updateResumo();''')
in_function('addExtrato','''  S.extrato.push({id:Date.now(),data,desc,tipo,val,categoria,subcategoria,gastoTipo:tipo==='saida'?gastoTipo:'',pagamento:tipo==='saida'?pagamento:''});''','''  S.extrato.push({id:novoIdExtrato(),data,desc,tipo,val,categoria,subcategoria,gastoTipo:tipo==='saida'?gastoTipo:'',pagamento:tipo==='saida'?pagamento:''});''')
in_function('addExtrato','''  renderExtrato();updateResumo();''','''  saveData();renderExtrato();updateResumo();''')
in_function('addCartao','''  renderCartao();renderExtrato();updateResumo();''','''  saveData();renderCartao();renderExtrato();updateResumo();''')
in_function('addInvest','''  renderInvestDestinationOptions();renderMetaInvestOptions();renderInvest();updateCategories();updateResumo();''','''  saveData();renderInvestDestinationOptions();renderMetaInvestOptions();renderInvest();updateCategories();updateResumo();''')
in_function('addMeta','''  renderInvestDestinationOptions();renderMetaInvestOptions();renderMetas();updateCategories();updateResumo();''','''  saveData();renderInvestDestinationOptions();renderMetaInvestOptions();renderMetas();updateCategories();updateResumo();''')
in_function('delCC','''S.cartao=S.cartao.filter(x=>x.id!==id);renderCartao();renderExtrato();updateResumo();''','''S.cartao=S.cartao.filter(x=>x.id!==id);saveData();renderCartao();renderExtrato();updateResumo();''')
in_function('delExt','''  renderInvest();renderMetas();renderExtrato();updateResumo();''','''  saveData();renderInvest();renderMetas();renderExtrato();updateResumo();''')
in_function('delInv','''  renderInvestDestinationOptions();''','''  saveData();
  renderInvestDestinationOptions();''')
in_function('saveInvestAporte','''  const origem=historico.length?'aporte_manual':'saldo_inicial';
  historico.push({id:Date.now()+'-aporte',tipo:'aporte',data,valor:val,saldo,origem});''','''  const origem=S.saldoInicial?'aporte_manual':(historico.length?'aporte_manual':'saldo_inicial');
  const extId=S.saldoInicial?novoIdExtrato():null;
  historico.push({id:(extId||Date.now())+'-aporte',tipo:'aporte',data,valor:val,saldo,origem,extId});
  if(extId!==null)S.extrato.push({id:extId,data,desc:'Investimento - '+item.nome,tipo:'investimento',categoria:'Investimento',subcategoria:item.nome,val,destId:item.id});''')
in_function('saveInvestAporte','''  refreshInvestViews();''','''  saveData();refreshInvestViews();''')
in_function('saveInvestUpdate','''  refreshInvestViews();''','''  saveData();refreshInvestViews();''')
in_function('saveInvestResgate','''  const extId=Date.now();''','''  const extId=novoIdExtrato();''')
in_function('saveInvestResgate','''  refreshInvestViews();''','''  saveData();refreshInvestViews();''')
in_function('delInvestHistory','''  refreshInvestViews();''','''  saveData();refreshInvestViews();''')

in_function('renderAnnualSummary','''    const saldo=entradas-saidas-cartao-invest-metas;''','''    const saldo=entradas-saidas-(S.saldoInicial?0:cartao)-invest-metas;''')
in_function('getResumoCartaoExtrato',"    desc:'Cartão de crédito a pagar',","    desc:S.saldoInicial?'Cartão previsto (não pago)':'Cartão de crédito a pagar',")

in_function('renderExtrato','''  const resumoCartao=getResumoCartaoExtrato(viewYear,viewMonth);
  const rows=S.extrato.concat(resumoCartao?[resumoCartao]:[]).filter(r=>isSameMonthDate(r.data,viewYear,viewMonth)).sort((a,b)=>b.data.localeCompare(a.data));''','''  const resumoCartao=getResumoCartaoExtrato(viewYear,viewMonth);
  const inicioMes=isoDate(viewYear,viewMonth,1);
  let linhaSaldo=null;
  if(saldoInicialValido(S.saldoInicial)){
    if(S.saldoInicial.data.slice(0,7)===inicioMes.slice(0,7)){
      linhaSaldo={id:'saldo-referencia',data:S.saldoInicial.data,desc:'Saldo inicial',tipo:'saldo_inicial',categoria:'Ponto de partida',val:S.saldoInicial.valor,auto:true};
    }else if(S.saldoInicial.data<inicioMes&&inicioMes<=today()){
      const ultimoDia=new Date(viewYear,viewMonth,0);
      const limite=isoDate(ultimoDia.getFullYear(),ultimoDia.getMonth(),ultimoDia.getDate());
      linhaSaldo={id:'saldo-transportado',data:inicioMes,desc:'Saldo vindo do mês anterior',tipo:'saldo_inicial',categoria:'Transporte automático',val:calcularSaldoDisponivelAte(limite),auto:true};
    }
  }
  const rows=S.extrato.concat(resumoCartao?[resumoCartao]:[],linhaSaldo?[linhaSaldo]:[]).filter(r=>isSameMonthDate(r.data,viewYear,viewMonth)).sort((a,b)=>b.data.localeCompare(a.data));''')
in_function('renderExtrato','''  const aviso=parcelasMes.length?'<div class="hint">O extrato mostra o cartão como uma soma do mês. Os detalhes ficam na aba Cartão.</div>':'';''','''  const aviso=parcelasMes.length?'<div class="hint">'+(S.saldoInicial?'O cartão é apenas uma previsão. Para descontar o dinheiro, lance o pagamento da fatura como saída; não registre a compra como outra despesa.':'O extrato mostra o cartão como uma soma do mês. Os detalhes ficam na aba Cartão.')+'</div>':'';
  const avisoSaldo=S.saldoInicial?'<div class="hint">O saldo inicial não é uma entrada. Movimentos anteriores a ele continuam no histórico, mas não afetam seu saldo disponível.</div>':'';''')
in_function('renderExtrato','''<strong>Cartão: ${fmt(cartaoMes)}</strong><span>Total do cartão com vencimento em ${monthLabel}.</span>''','''<strong>Cartão previsto: ${fmt(cartaoMes)}</strong><span>Fatura prevista para ${monthLabel}, não é pagamento.</span>''')
in_function('renderExtrato','''  if(!rows.length){wrap.innerHTML=resumo+'<div class="empty">Nenhum lançamento em '+monthLabel+'.</div>';return;}''','''  if(!rows.length){wrap.innerHTML=resumo+avisoSaldo+'<div class="empty">Nenhum lançamento em '+monthLabel+'.</div>';return;}''')
in_function('renderExtrato',"  wrap.innerHTML=resumo+aviso+'<table>","  wrap.innerHTML=resumo+avisoSaldo+aviso+'<table>")
in_function('renderExtrato',"      const bc=r.tipo==='entrada'?'b-pagamento':", "      const bc=r.tipo==='saldo_inicial'?'b-pagamento':r.tipo==='entrada'?'b-pagamento':")
in_function('renderExtrato',"      const tipoLabel=r.tipo==='cartao'?'cartão':", "      const tipoLabel=r.tipo==='saldo_inicial'?'saldo':r.tipo==='cartao'?'cartão':")
in_function('renderExtrato',"      const color=r.tipo==='entrada'?'#0F6E56':", "      const color=r.tipo==='saldo_inicial'?'#9FE1CB':r.tipo==='entrada'?'#0F6E56':")

in_function('updateResumo','''  const saidas=saidasDiretas+ccMes;
  const saldo=entradas-saidas-investido-metas;''','''  const saidas=saidasDiretas+(S.saldoInicial?0:ccMes);
  const saldoMes=entradas-saidas-investido-metas;
  const saldo=S.saldoInicial?calcularSaldoDisponivelAte(today()):saldoMes;''')
in_function('updateResumo','''  document.getElementById('saldo-total').textContent=fmt(saldo);''','''  document.getElementById('saldo-total').textContent=S.saldoInicial?fmt(saldo):'—';
  document.getElementById('saldo-note').textContent=S.saldoInicial
    ? 'Saldo real a partir de '+S.saldoInicial.data.split('-').reverse().join('/')+'. O cartão só reduz esse valor após lançar o pagamento no extrato.'
    : 'Informe seu saldo inicial no Extrato para começar o controle automático.';
  document.getElementById('saldo-link').hidden=!!S.saldoInicial;
  document.getElementById('res-cc').parentElement.querySelector('.label').textContent=S.saldoInicial?'Cartão (previsto)':'Cartão (mês atual)';''')
in_function('updateResumo','''  updateResumoMascot(entradas,saidas,investido,metas,saldo,{''','''  updateResumoMascot(entradas,saidas,investido,metas,saldoMes,{''')
in_function('updateResumo',"  const resumoGeral=saldo>=0?'sobrou':'faltou';", "  const resumoGeral=saldoMes>=0?'sobrou':'faltou';")
in_function('updateResumo',"${resumoGeral}: ${fmt(Math.abs(saldo))}","${resumoGeral}: ${fmt(Math.abs(saldoMes))}")
in_function('updateResumo','''        <span>Esses valores entram como saída no resumo.</span>''','''        <span>${S.saldoInicial?'Previsão de fatura. Apenas o pagamento lançado como saída reduz o dinheiro disponível.':'Esses valores entram como saída no resumo.'}</span>''')
in_function('updateResumo','''  saveData();''','''  // Atualizar a tela não é uma alteração nos dados financeiros.''')

once('''renderRegisteredCards();
renderMetaInvestOptions();
renderInvest();''','''renderRegisteredCards();
renderSaldoInicial();
renderMetaInvestOptions();
renderInvest();''')

# Conferência estrutural obrigatória antes de escrever qualquer alteração.
assert src.count('function calcularSaldoDisponivelAte(')==1
assert src.count('function confirmarSaldoInicial(')==1
assert src.count('versao:2')==1
assert src.count('saveData();')>10
assert '<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">' in src
path.write_text(src, encoding='utf-8-sig')
print('PATCH_OK: configuração do saldo, extrato de abertura, persistência e cálculo real adicionados')

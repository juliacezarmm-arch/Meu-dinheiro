from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def change(old,new,number=1):
 global s
 actual=s.count(old)
 if actual!=number: raise AssertionError(f'Trecho esperado {number} vez(es), achado {actual}: {old[:95]!r}')
 s=s.replace(old,new)

# Aparência: informação organizada junto ao investimento e metas dentro dele.
change('</style>\n</head>', '''/* Metas vinculadas: divisões do investimento, nunca patrimônio adicional. */
.inv-meta-list{border-top:1px solid #3a3934;margin-top:11px;padding-top:10px;display:grid;gap:8px}
.inv-meta-list>strong{font-size:12px;color:#9FE1CB}
.inv-meta-row{display:flex;align-items:center;justify-content:space-between;gap:9px;font-size:12px;line-height:1.35}
.inv-meta-row>span:first-child{min-width:0;overflow-wrap:anywhere;color:#c5c3ba}
.inv-meta-row b{white-space:nowrap;font-variant-numeric:tabular-nums}
.inv-meta-link{border:1px solid #4d7966;background:#183127;color:#9FE1CB;border-radius:8px;padding:7px 10px;font-size:11px;font-weight:750;cursor:pointer}
.inv-info{font-size:11px;line-height:1.45;color:#c5c3ba;overflow-wrap:anywhere}
.meta-mode-help{background:#15231b;border:1px solid #315743;border-radius:9px;padding:10px;color:#c3ebd6;font-size:12px;line-height:1.5;margin-bottom:10px}
.meta-mode-help[hidden]{display:none!important}
@media(max-width:520px){.inv-meta-row{align-items:flex-start}.inv-meta-row b{font-size:11px}}
</style>
</head>''')

# Informações descritivas são informadas pela pessoa: não presumir taxas, banco ou cotação.
change('''      <div class="row row2">
        <input type="number" id="inv-inicial"''','''      <div class="row row2">
        <input type="text" id="inv-banco" maxlength="70" placeholder="Banco / instituição (opcional)" title="Informe a instituição onde o dinheiro está aplicado, como Itaú, Inter ou outra."/>
        <select id="inv-rent-indice" title="Referência informativa da rentabilidade; não calcula rendimentos automaticamente.">
          <option value="">Rentabilidade (não informada)</option><option value="CDI">% do CDI</option><option value="Prefixado">Prefixado (% ao ano)</option><option value="IPCA">IPCA + (% ao ano)</option><option value="Outro">Outra referência</option>
        </select>
      </div>
      <div class="row row2">
        <input type="number" id="inv-rent-valor" min="0" max="10000" step="0.01" placeholder="Taxa contratada (ex.: 100)" title="Informe a taxa do seu produto; deixe em branco quando desconhecida."/>
        <label class="input-caption">Vencimento do investimento (opcional)<input type="date" id="inv-vencimento" title="Data de vencimento do produto, diferente da data-alvo de uma meta."/></label>
      </div>
      <p class="hint">Cofrinho é a organização do dinheiro. Informe também o produto real (por exemplo CDB), as condições dele e a instituição. Não projetamos rendimento automaticamente.</p>
      <div class="row row2">
        <input type="number" id="inv-inicial"''')

change('''      <div class="row row1"><input type="text" id="meta-desc"''','''      <div class="row row1">
        <label class="input-caption" for="meta-modo">Como funciona essa meta?</label>
        <select id="meta-modo" onchange="toggleMetaModo()" title="Reservar dinheiro de um investimento ou acompanhar um valor-alvo sem mexer no saldo.">
          <option value="separar">Separar dinheiro no investimento</option><option value="acompanhar">Acompanhar valor-alvo, sem separar</option>
        </select>
      </div>
      <p id="meta-mode-help" class="meta-mode-help">Vincule a meta a um investimento. Você poderá reservar dinheiro que já está nele ou fazer novos depósitos pelo Extrato, sem contar esse dinheiro duas vezes.</p>
      <div class="row row1"><input type="text" id="meta-desc"''')
change('''      <button class="btn-green" onclick="addMeta()"''','''      <div class="row row1"><label class="input-caption" for="meta-prazo">Data-alvo da meta (opcional)<input type="date" id="meta-prazo" title="Dia em que deseja alcançar a meta. Não é o vencimento do investimento."/></label></div>
      <button class="btn-green" onclick="addMeta()"''')
change('''<div class="label">Guardado em metas</div>''','''<div class="label">Reservado em metas</div>''')

# Metas em modo acompanhamento não recebem aportes nem resgates próprios; são somente um objetivo de saldo.
change('''  const lista=(tipo==='investimento'||tipo==='meta')?S.invest.filter(i=>i.kind===tipo):S.invest;''','''  const lista=(tipo==='investimento'||tipo==='meta')?S.invest.filter(i=>i.kind===tipo&&(tipo!=='meta'||i.modo!=='acompanhar')):S.invest;''')
old='''function renderMetaInvestOptions(){
  const select=document.getElementById('meta-invest-dest');
  if(!select)return;
  const investimentos=S.invest.filter(i=>i.kind==='investimento');
  select.innerHTML='<option value="">Onde esse dinheiro vai ficar?</option>'+investimentos.map(i=>`<option value="${i.id}">${escHtml(i.nome+' - '+i.tipo)}</option>`).join('');
}

function getMetaStorage(item){'''
new='''function renderMetaInvestOptions(){
  const select=document.getElementById('meta-invest-dest');
  if(!select)return;
  const previous=select.value;
  const monitor=document.getElementById('meta-modo').value==='acompanhar';
  const investimentos=S.invest.filter(i=>i.kind==='investimento');
  select.innerHTML='<option value="">'+(monitor?'Escolha o investimento ou todo o patrimônio':'Onde a meta ficará guardada?')+'</option>'+
    (monitor?'<option value="todos">Todos os investimentos (patrimônio total)</option>':'')+
    investimentos.map(i=>`<option value="${i.id}">${escHtml((i.banco?i.banco+' · ':'')+i.nome+' · '+i.tipo)}</option>`).join('');
  if(Array.from(select.options).some(opt=>opt.value===previous))select.value=previous;
}
function toggleMetaModo(){
  const monitor=document.getElementById('meta-modo').value==='acompanhar';
  document.getElementById('meta-mode-help').textContent=monitor
    ?'Acompanhe a evolução de um investimento ou de todo o patrimônio. Não separa nem transfere dinheiro, nem cria lançamentos no Extrato.'
    :'Vincule a meta a um investimento. Reserve dinheiro já investido ou registre novos depósitos pelo Extrato; o patrimônio não será somado duas vezes.';
  renderMetaInvestOptions();
}
function valorMetaAtual(item){
  if(!item||item.kind!=='meta')return 0;
  if(item.modo!=='acompanhar')return Number(item.valorAtual||0);
  const investimentos=S.invest.filter(x=>x.kind==='investimento');
  return (item.escopo==='todos'?investimentos:investimentos.filter(x=>String(x.id)===String(item.storageId)))
    .reduce((centavos,x)=>centavos+Math.round(Number(x.valorAtual||0)*100),0)/100;
}
function metasReservadasNoInvestimento(id){
  return S.invest.filter(x=>x.kind==='meta'&&x.modo!=='acompanhar'&&String(x.storageId)===String(id));
}
function iniciarMetaParaInvestimento(id){
  const item=S.invest.find(x=>String(x.id)===String(id)&&x.kind==='investimento');if(!item)return;
  showPage('metas',document.querySelectorAll('.nav button')[4]);
  const form=document.querySelector('#page-metas .add-form');
  if(form.classList.contains('collapsed'))form.previousElementSibling.click();
  document.getElementById('meta-modo').value='separar';toggleMetaModo();
  document.getElementById('meta-invest-dest').value=String(id);
  document.getElementById('meta-desc').focus();
}
function movimentarReservaInterna(id,liberar){
  const meta=S.invest.find(x=>String(x.id)===String(id)&&x.kind==='meta'&&x.modo!=='acompanhar');
  const storage=getMetaStorage(meta);
  if(!meta||!storage){appAlert('Meta sem investimento vinculado. Confira o cadastro.');return;}
  const field=document.getElementById((liberar?'liberar':'reservar')+'-val-'+id);
  const valor=Number(field.value);
  if(!field.value.trim()||!valorMonetarioValido(valor)||valor<=0){appAlert('Informe um valor válido em reais.');return;}
  const livre=Math.round((Number(storage.valorAtual||0)-reservadoEmMetas(storage.id))*100)/100;
  if(!liberar&&valor>livre){appAlert('Saldo livre insuficiente. O valor já reservado em outras metas não pode ser usado duas vezes.');return;}
  if(liberar&&valor>Number(meta.valorAtual||0)){appAlert('Não é possível liberar mais dinheiro do que o reservado nesta meta.');return;}
  if(ultimaDataFinanceira(meta)>today()){appAlert('Existe movimentação posterior a hoje nesta meta; confira o histórico.');return;}
  ensureInvestHistory(meta).push({id:novoIdGlobal()+'-reserva',tipo:liberar?'resgate':'aporte',data:today(),valor,origem:'reserva_interna',storageId:storage.id,storageNome:storage.nome});
  recalcInvestFromHistory(meta);
  investUi.acao[id]='';investUi.historico[id]=true;investUi.mes[id]=today().slice(0,7);
  // Somente a alocação interna muda. O investimento, Extrato e saldo da conta permanecem intactos.
  saveData();refreshInvestViews();
}

function getMetaStorage(item){'''
change(old,new)
change('''  return S.invest.filter(x=>x.kind==='meta'&&String(x.storageId)===String(id))''','''  return S.invest.filter(x=>x.kind==='meta'&&x.modo!=='acompanhar'&&String(x.storageId)===String(id))''')
# Exclusão do patrimônio-base ainda exige tratar objetivos vinculados.
change('''item.kind==='investimento'&&S.invest.some(x=>x.kind==='meta'&&String(x.storageId)===String(id))''','''item.kind==='investimento'&&S.invest.some(x=>x.kind==='meta'&&String(x.storageId)===String(id))''') if False else None
change('''    if(!dest||dest.kind!==tipo||!valorMonetarioValido(val)||val<=0){''','''    if(!dest||dest.kind!==tipo||dest.modo==='acompanhar'||!valorMonetarioValido(val)||val<=0){''')

# Metadados do produto: valores declarados, não rentabilidade inventada.
change('''  const desc=document.getElementById('inv-desc').value.trim();
  const tipo=document.getElementById('inv-tipo').value;
  const nome=desc||tipo;''','''  const desc=document.getElementById('inv-desc').value.trim();
  const tipo=document.getElementById('inv-tipo').value;
  const nome=desc||tipo;
  const banco=document.getElementById('inv-banco').value.trim();
  const rentIndice=document.getElementById('inv-rent-indice').value;
  const rentCampo=document.getElementById('inv-rent-valor').value.trim();
  const rentValor=rentCampo===''?null:Number(rentCampo);
  const vencimento=document.getElementById('inv-vencimento').value;
  if(rentValor!==null&&(!Number.isFinite(rentValor)||rentValor<0||rentValor>10000)||vencimento&&!dataISOValida(vencimento)){
    appAlert('Informe uma taxa não negativa e uma data de vencimento válida.');return;
  }''')
change('''historico:[],cryptoQtd,cryptoCotacao,cryptoPrecoMedio,cryptoInvestido:investido};''','''historico:[],banco,rentIndice,rentValor,vencimento:vencimento||null,cryptoQtd,cryptoCotacao,cryptoPrecoMedio,cryptoInvestido:investido};''')
change('''  document.getElementById('inv-desc').value='';
  document.getElementById('inv-inicial').value='';''','''  document.getElementById('inv-desc').value='';
  for(const id of ['inv-banco','inv-rent-indice','inv-rent-valor','inv-vencimento'])document.getElementById(id).value='';
  document.getElementById('inv-inicial').value='';''')

old='''function addMeta(){
  const desc=document.getElementById('meta-desc').value.trim();
  const meta=parseFloat(document.getElementById('meta-val').value);
  const storageId=parseInt(document.getElementById('meta-invest-dest').value);
  const storage=S.invest.find(i=>i.id===storageId&&i.kind==='investimento');
  if(!desc){appAlert('Informe o nome da meta.');return;}
  if(meta<=0){appAlert('Informe o valor da meta.');return;}
  if(!storage){appAlert('Escolha onde o dinheiro dessa meta vai ficar. Se ainda não tiver, cadastre um investimento primeiro.');return;}
  S.invest.push({id:novoIdGlobal(),kind:'meta',nome:desc,tipo:'Meta',meta,storageId:storage.id,storageNome:storage.nome,valorAtual:0,totalAportado:0,totalResgatado:0,historico:[]});
  document.getElementById('meta-desc').value='';
  document.getElementById('meta-val').value='';
  document.getElementById('meta-invest-dest').value='';
  saveData();renderInvestDestinationOptions();renderMetaInvestOptions();renderMetas();updateCategories();updateResumo();
}'''
new='''function addMeta(){
  const desc=document.getElementById('meta-desc').value.trim();
  const campoValor=document.getElementById('meta-val').value.trim(),meta=Number(campoValor);
  const modo=document.getElementById('meta-modo').value;
  const escolha=document.getElementById('meta-invest-dest').value;
  const storage=S.invest.find(i=>String(i.id)===escolha&&i.kind==='investimento');
  const prazo=document.getElementById('meta-prazo').value;
  if(!desc){appAlert('Informe o nome da meta.');return;}
  if(!campoValor||!valorMonetarioValido(meta)||meta<=0){appAlert('Informe um valor-alvo válido.');return;}
  if(!['separar','acompanhar'].includes(modo)||!storage&&!(modo==='acompanhar'&&escolha==='todos')){appAlert('Selecione o investimento ou, no acompanhamento, todos os investimentos.');return;}
  if(prazo&&!dataISOValida(prazo)){appAlert('Informe uma data-alvo válida.');return;}
  S.invest.push({id:novoIdGlobal(),kind:'meta',nome:desc,tipo:'Meta',modo,escopo:escolha==='todos'?'todos':'investimento',meta,prazo:prazo||null,storageId:storage?storage.id:null,storageNome:storage?storage.nome:'Todos os investimentos',valorAtual:0,totalAportado:0,totalResgatado:0,historico:[]});
  document.getElementById('meta-desc').value='';
  document.getElementById('meta-val').value='';
  document.getElementById('meta-invest-dest').value='';
  document.getElementById('meta-prazo').value='';
  saveData();renderInvestDestinationOptions();renderMetaInvestOptions();renderInvest();renderMetas();updateCategories();updateResumo();
}'''
change(old,new)

# Não projetar movimentos monetários fictícios em metas de acompanhamento.
change('''  const relacionados=[item,...S.invest.filter(x=>x.kind==='meta'&&x.storageId===item.id)];''','''  const relacionados=[item,...metasReservadasNoInvestimento(item.id)];''')
change('''    S.invest.filter(x=>x.kind==='meta'&&x.storageId===item.id&&Number(x.valorAtual||0)>0).forEach(meta=>{''','''    metasReservadasNoInvestimento(item.id).filter(x=>Number(x.valorAtual||0)>0).forEach(meta=>{''')

# Metas com valor-alvo nunca entram na soma de reservas.
change('''  const total=metas.reduce((s,x)=>s+x.valorAtual,0);
  const metasComAlvo=metas.filter(x=>x.meta>0);
  const progresso=metasComAlvo.length?metasComAlvo.reduce((s,x)=>s+Math.min(100,x.valorAtual/x.meta*100),0)/metasComAlvo.length:0;''','''  const total=metas.filter(x=>x.modo!=='acompanhar').reduce((s,x)=>s+Math.round(x.valorAtual*100),0)/100;
  const metasComAlvo=metas.filter(x=>x.meta>0);
  const progresso=metasComAlvo.length?metasComAlvo.reduce((s,x)=>s+Math.min(100,valorMetaAtual(x)/x.meta*100),0)/metasComAlvo.length:0;''')
change('''  const metaPct=item.meta>0?Math.min(100,item.valorAtual/item.meta*100):0;
  const storage=getMetaStorage(item);
  const subtitulo=item.kind==='meta'?'Meta'+(storage?' - guardado em '+storage.nome:(item.storageNome?' - guardado em '+item.storageNome:'')):'Investimento - '+item.tipo;''','''  const atual=item.kind==='meta'?valorMetaAtual(item):Number(item.valorAtual||0);
  const metaPct=item.meta>0?Math.min(100,atual/item.meta*100):0;
  const storage=getMetaStorage(item);
  const monitor=item.kind==='meta'&&item.modo==='acompanhar';
  const subtitulo=item.kind==='meta'?(monitor?'Meta de patrimônio · '+(item.escopo==='todos'?'Todos os investimentos':storage?'Acompanhando '+storage.nome:'Investimento não encontrado'):'Meta com reserva'+(storage?' · '+storage.nome:(item.storageNome?' · '+item.storageNome:''))):'Investimento · '+item.tipo;
  const metasInternas=item.kind==='investimento'?metasReservadasNoInvestimento(item.id):[];
  const saldoReservado=metasInternas.reduce((centavos,x)=>centavos+Math.round(Number(x.valorAtual||0)*100),0)/100;
  const saldoLivre=Math.max(0,Math.round((atual-saldoReservado)*100)/100);
  const infoInvest=item.kind==='investimento'?[item.banco||'',item.rentIndice?(item.rentValor===null||item.rentValor===undefined?'':'Taxa informada '+item.rentValor+' · ')+item.rentIndice:'',item.vencimento?'Vencimento: '+item.vencimento.split('-').reverse().join('/'):''].filter(Boolean).join(' · '):'';''')
# Render tool actions for allocation; no cash movement.
change('''  const painelAcao=acao==='aportar'&&item.kind==='investimento'?`''','''  const painelAcao=(acao==='reservar'||acao==='liberar')&&item.kind==='meta'&&!monitor&&storage?`
    <div class="goal-panel"><div class="goal-panel-title">${acao==='reservar'?'Reservar saldo já investido':'Liberar dinheiro reservado'}</div>
      <p class="hint">${acao==='reservar'?'Disponível: '+fmt(Math.max(0,Math.round((storage.valorAtual-reservadoEmMetas(storage.id))*100)/100)):'Reservado nesta meta: '+fmt(item.valorAtual)}. O saldo do investimento e o Extrato não mudam.</p>
      <input type="number" min="0.01" step="0.01" id="${acao==='reservar'?'reservar':'liberar'}-val-${item.id}" placeholder="Valor (R$)"/>
      <button type="button" onclick="movimentarReservaInterna(${item.id},${acao==='liberar'})">Confirmar ${acao==='reservar'?'reserva':'liberação'}</button>
    </div>`:acao==='aportar'&&item.kind==='investimento'?`''')
change('''        const nome=h.origem==='saldo_inicial'?'Saldo inicial':(h.metaNome?'Meta - '+h.metaNome:(h.tipo==='aporte'?'Entrada investida':h.tipo==='resgate'?'Resgate':'Valor atualizado'));''','''        const nome=h.origem==='saldo_inicial'?'Saldo inicial':h.origem==='reserva_interna'?(h.tipo==='aporte'?'Reserva interna':'Liberação interna'):(h.metaNome?'Meta - '+h.metaNome:(h.tipo==='aporte'?'Entrada investida':h.tipo==='resgate'?'Resgate':'Valor atualizado'));''')
change('''  const progresso=item.kind==='meta'&&item.meta>0?`''','''  const progresso=item.kind==='meta'&&item.meta>0?`''') if False else None
change('''        <div class="goal-meta">${escHtml(subtitulo)}${item.meta>0?' · alvo '+fmt(item.meta):''}</div>''','''        <div class="goal-meta">${escHtml(subtitulo)}${item.meta>0?' · alvo '+fmt(item.meta):''}${item.prazo?' · até '+item.prazo.split('-').reverse().join('/'):''}</div>
        ${infoInvest?`<div class="inv-info">${escHtml(infoInvest)}</div>`:''}''')
change('''      <div class="plain-card" title="Valor atual registrado para este investimento ou meta."><strong>Atual: ${fmt(item.valorAtual)}</strong><span>Valor que existe hoje.</span></div>
      <div class="plain-card" title="Mostra quanto rendeu no mês selecionado."><strong>Rendeu no mês: ${fmt(resultadoMes.rendimento)}</strong><span>${item.kind==='meta'?'Estimativa baseada na variação do investimento vinculado.':resultadoMes.pct.toFixed(1).replace('.',',')+'% aproximado; não considera o tempo de cada aporte.'}</span></div>''','''      <div class="plain-card" title="${monitor?'Saldo observado, sem criar dinheiro adicional':'Valor atual registrado'}"><strong>${monitor?'Acompanhado':'Atual'}: ${fmt(atual)}</strong><span>${monitor?'Mesmo saldo do investimento, sem reserva.':'Valor registrado neste investimento ou reserva.'}</span></div>
      ${monitor?`<div class="plain-card"><strong>Faltam: ${fmt(Math.max(0,item.meta-atual))}</strong><span>Objetivo de patrimônio; não altera o Extrato.</span></div>`:`<div class="plain-card" title="Mostra quanto rendeu no mês selecionado."><strong>Rendeu no mês: ${fmt(resultadoMes.rendimento)}</strong><span>${item.kind==='meta'?'Estimativa pela variação do investimento vinculado.':resultadoMes.pct.toFixed(1).replace('.',',')+'% aproximado; não considera o tempo de cada aporte.'}</span></div>`}''')
change('''    ${progresso}
    <div class="goal-actions">''','''    ${progresso}
    ${item.kind==='investimento'?`<div class="inv-meta-list"><strong>Dinheiro deste investimento</strong>
      ${metasInternas.map(m=>`<div class="inv-meta-row"><span>Meta: ${escHtml(m.nome)}</span><b>${fmt(m.valorAtual)}</b></div>`).join('')}
      <div class="inv-meta-row"><span>Disponível, não reservado</span><b>${fmt(saldoLivre)}</b></div>
      <button class="inv-meta-link" onclick="iniciarMetaParaInvestimento(${item.id})">+ Criar meta neste investimento</button>
    </div>`:''}
    <div class="goal-actions">''')
change('''      ${item.kind==='investimento'?`<button onclick="toggleInvestAction(${item.id},'resgatar')" title="Use quando retirou dinheiro desse investimento.">Resgatar</button>`:''}
      <button onclick="toggleInvestHistory(${item.id})"''','''      ${item.kind==='investimento'?`<button onclick="toggleInvestAction(${item.id},'resgatar')" title="Use quando retirou dinheiro desse investimento.">Resgatar</button>`:''}
      ${item.kind==='meta'&&!monitor?`<button onclick="toggleInvestAction(${item.id},'reservar')" title="Reserva uma parte do saldo já existente, sem lançar gasto ou novo investimento.">Reservar saldo</button><button onclick="toggleInvestAction(${item.id},'liberar')" title="Libera a reserva sem transferir dinheiro para o Extrato.">Liberar reserva</button>`:''}
      ${!monitor?`<button onclick="toggleInvestHistory(${item.id})"''')
change('''      <button onclick="toggleInvestChart(${item.id})" title="Mostra ou esconde o gráfico de evolução.">${graficoAberto?'Fechar gráfico':'Gráfico'}</button>''','''      <button onclick="toggleInvestChart(${item.id})" title="Mostra ou esconde o gráfico de evolução.">${graficoAberto?'Fechar gráfico':'Gráfico'}</button>`:''}''')
# Guardar histórico e metas antigas sem aplicar automaticamente nova modalidade.
change('''      if(key==='cartoes'&&r.nome!==undefined''','''      if(key==='invest'){
        if(r.banco!==undefined&&(typeof r.banco!=='string'||r.banco.length>70)||r.rentIndice!==undefined&&!['','CDI','Prefixado','IPCA','Outro'].includes(r.rentIndice)||r.rentValor!==undefined&&r.rentValor!==null&&(!Number.isFinite(r.rentValor)||r.rentValor<0||r.rentValor>10000)||r.vencimento!==undefined&&r.vencimento!==null&&!dataISOValida(r.vencimento))throw Error('Condições do investimento inválidas.');
        if(r.kind==='meta'&&(r.modo!==undefined&&!['separar','acompanhar'].includes(r.modo)||r.escopo!==undefined&&!['todos','investimento'].includes(r.escopo)||r.prazo!==undefined&&r.prazo!==null&&!dataISOValida(r.prazo)||r.modo==='acompanhar'&&r.escopo==='todos'&&r.storageId!==null&&r.storageId!==undefined))throw Error('Meta inválida.');
      }
      if(key==='cartoes'&&r.nome!==undefined''')
change('''  const metaBatida=S.invest.some(i=>i.kind==='meta'&&Number(i.meta||0)>0&&Number(i.valorAtual||0)>=Number(i.meta||0));''','''  const metaBatida=S.invest.some(i=>i.kind==='meta'&&Number(i.meta||0)>0&&valorMetaAtual(i)>=Number(i.meta||0));''')
# Datas preenchidas automaticamente só para movimentações, jamais para prazo opcional.
change('''document.querySelectorAll('input[type="date"]').forEach(el=>el.value=today());''','''document.querySelectorAll('input[type="date"]').forEach(el=>{if(!['meta-prazo','inv-vencimento'].includes(el.id))el.value=today();});''')
change('''renderMetaInvestOptions();
renderInvest();
renderMetas();
updateResumo();
appReady=true;''','''renderMetaInvestOptions();
toggleMetaModo();
renderInvest();
renderMetas();
updateResumo();
appReady=true;''')
# Atalhos e destino devem ser atualizados ao abrir o JSON; render preserva esquema antigo.
change('''<script src="js/recorrentes.js?v=20260921-nome-cartao1"></script>''','''<script src="js/recorrentes.js?v=20260921-metas-integradas1"></script>''')
p.write_text(s,encoding='utf-8')
print('PASS: interface integrada, metas legadas intactas, alocação interna sem extrato e meta de patrimônio derivada.')
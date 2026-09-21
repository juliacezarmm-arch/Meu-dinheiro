from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
def change(old,new):
 global s
 assert s.count(old)==1, f'Trecho da edição não é único: {old[:95]!r} ({s.count(old)})'
 s=s.replace(old,new)
marker='function movimentarReservaInterna(id,liberar){'
new='''function salvarIdentificacaoInvestimento(id){
  const item=S.invest.find(x=>String(x.id)===String(id)&&x.kind==='investimento');if(!item)return;
  const nome=document.getElementById('inv-edit-nome-'+id).value.trim();
  const banco=document.getElementById('inv-edit-banco-'+id).value.trim();
  const rentIndice=document.getElementById('inv-edit-indice-'+id).value;
  const campo=document.getElementById('inv-edit-taxa-'+id).value.trim();
  const rentValor=campo===''?null:Number(campo);
  const vencimento=document.getElementById('inv-edit-vencimento-'+id).value;
  if(!nome||nome.length>40||banco.length>70||rentValor!==null&&(!Number.isFinite(rentValor)||rentValor<0||rentValor>10000)||vencimento&&!dataISOValida(vencimento)){
    appAlert('Confira nome, instituição, taxa e vencimento do investimento.');return;
  }
  item.nome=nome;item.banco=banco;item.rentIndice=rentIndice;
  item.rentValor=rentValor;item.vencimento=vencimento||null;
  S.invest.filter(x=>x.kind==='meta'&&String(x.storageId)===String(id)).forEach(x=>x.storageNome=nome);
  investUi.acao[id]='';saveData();renderInvestDestinationOptions();refreshInvestViews();
}
function salvarAlvoMeta(id){
  const item=S.invest.find(x=>String(x.id)===String(id)&&x.kind==='meta');if(!item)return;
  const nome=document.getElementById('meta-edit-nome-'+id).value.trim();
  const campo=document.getElementById('meta-edit-alvo-'+id).value.trim();
  const alvo=Number(campo),prazo=document.getElementById('meta-edit-prazo-'+id).value;
  if(!nome||nome.length>40||!campo||!valorMonetarioValido(alvo)||alvo<=0||prazo&&!dataISOValida(prazo)){
    appAlert('Informe nome, valor-alvo e data válidos.');return;
  }
  item.nome=nome;item.meta=alvo;item.prazo=prazo||null;
  // Nunca troca modalidade ou investimento vinculado durante edição: preserva o histórico.
  investUi.acao[id]='';saveData();renderInvestDestinationOptions();refreshInvestViews();
}
'''+marker
change(marker,new)
marker="  const painelAcao=(acao==='reservar'||acao==='liberar')&&item.kind==='meta'&&!monitor&&storage?`"
new='''  const painelAcao=acao==='dados'&&item.kind==='investimento'?`
    <div class="goal-panel"><div class="goal-panel-title">Editar identificação e condições informadas</div>
      <div class="row row2"><label class="input-caption">Nome do investimento<input id="inv-edit-nome-${item.id}" type="text" maxlength="40" value="${escHtml(item.nome)}"/></label>
      <label class="input-caption">Banco / instituição<input id="inv-edit-banco-${item.id}" type="text" maxlength="70" value="${escHtml(item.banco||'')}"/></label></div>
      <div class="row row2"><label class="input-caption">Referência<select id="inv-edit-indice-${item.id}">
        ${[['','Não informada'],['CDI','% do CDI'],['Prefixado','Prefixado % a.a.'],['IPCA','IPCA + % a.a.'],['Outro','Outra referência']].map(([v,label])=>`<option value="${v}"${(item.rentIndice||'')===v?' selected':''}>${label}</option>`).join('')}
      </select></label><label class="input-caption">Taxa informada<input id="inv-edit-taxa-${item.id}" type="number" min="0" max="10000" step="0.01" value="${item.rentValor??''}"/></label></div>
      <label class="input-caption">Vencimento do produto (opcional)<input id="inv-edit-vencimento-${item.id}" type="date" value="${escHtml(item.vencimento||'')}"/></label>
      <p class="hint">A taxa é somente informativa e não aplica rendimento automaticamente. Não altera aportes ou resgates.</p>
      <button type="button" onclick="salvarIdentificacaoInvestimento(${item.id})">Salvar dados do investimento</button>
    </div>`:acao==='editar-meta'&&item.kind==='meta'?`
    <div class="goal-panel"><div class="goal-panel-title">Editar objetivo</div>
      <div class="row row2"><label class="input-caption">Nome da meta<input id="meta-edit-nome-${item.id}" type="text" maxlength="40" value="${escHtml(item.nome)}"/></label>
      <label class="input-caption">Valor-alvo (R$)<input id="meta-edit-alvo-${item.id}" type="number" min="0.01" step="0.01" value="${item.meta}"/></label></div>
      <label class="input-caption">Data-alvo (opcional)<input id="meta-edit-prazo-${item.id}" type="date" value="${escHtml(item.prazo||'')}"/></label>
      <p class="hint">O vínculo ao investimento e as movimentações existentes permanecem inalterados.</p>
      <button type="button" onclick="salvarAlvoMeta(${item.id})">Salvar meta</button>
    </div>`:(acao==='reservar'||acao==='liberar')&&item.kind==='meta'&&!monitor&&storage?`'''
change(marker,new)
marker='''    <div class="goal-actions">
      ${item.kind==='investimento'?`<button onclick="toggleInvestAction(${item.id},'atualizar')"'''
new='''    <div class="goal-actions">
      ${item.kind==='investimento'?`<button onclick="toggleInvestAction(${item.id},'dados')" title="Edite instituição, nome, rentabilidade informada e vencimento sem alterar o saldo.">Editar dados</button>`:''}
      ${item.kind==='meta'?`<button onclick="toggleInvestAction(${item.id},'editar-meta')" title="Corrige o nome, o valor-alvo e a data sem alterar reservas ou aportes.">Editar meta</button>`:''}
      ${item.kind==='investimento'?`<button onclick="toggleInvestAction(${item.id},'atualizar')"'''
change(marker,new)
p.write_text(s,encoding='utf-8')
print('PASS: edição de metadados e objetivos sem reescrever saldos, vínculos ou histórico')
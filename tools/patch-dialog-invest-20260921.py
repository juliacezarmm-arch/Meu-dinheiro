from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def change(old,new,count=1):
 global s
 found=s.count(old)
 assert found==count,(found,count,repr(old[:110]))
 s=s.replace(old,new)

change('/* Metas vinculadas: divisões do investimento, nunca patrimônio adicional. */', '''/* Janelas flutuantes: a grade de investimentos nunca cresce ao abrir ações. */
#invest-action-dialog{z-index:14000}
#invest-action-dialog .site-dialog-panel{width:min(100%,680px);max-height:min(88dvh,780px);display:flex;flex-direction:column;padding:0;overflow:hidden}
.invest-dialog-heading{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:17px 20px;border-bottom:1px solid #3a3934;flex:none}
.invest-dialog-heading h2{font-size:16px;font-weight:800;margin:0;overflow-wrap:anywhere;min-width:0}
.invest-dialog-close{flex:none;display:grid;place-items:center;width:34px;height:34px;background:#2a2a28;color:#f5f5f2;border:1px solid #46463e;border-radius:9px;font-size:21px;cursor:pointer}
.invest-dialog-close:hover,.invest-dialog-close:focus-visible{border-color:#9FE1CB;color:#9FE1CB}
#invest-dialog-content{overflow:auto;padding:18px 20px 20px;min-height:0;overscroll-behavior:contain}
#invest-dialog-content .goal-panel{margin:0;border:0;padding:0;background:transparent}
#invest-dialog-content .goal-panel-title{font-size:14px;margin-bottom:13px}
#invest-dialog-content input,#invest-dialog-content select{width:100%;min-width:0;box-sizing:border-box}
#invest-dialog-content .history-row{grid-template-columns:55px minmax(0,1fr) 115px 27px}
#invest-dialog-content .stock-chart svg{height:165px}
#invest-dialog-content .stock-chart-meta{flex-wrap:wrap}
#inv-wrap .goal-list,#meta-wrap .goal-list{align-items:start}
.inv-rend-percent{color:#9FE1CB;font-size:12px;font-weight:750;margin-top:3px;font-variant-numeric:tabular-nums}
@media(max-width:520px){
 #invest-action-dialog{padding:10px}
 #invest-action-dialog .site-dialog-panel{max-height:calc(100dvh - 20px);border-radius:13px}
 .invest-dialog-heading{padding:13px 14px}
 #invest-dialog-content{padding:13px 14px 18px}
 #invest-dialog-content .history-row{grid-template-columns:1fr;gap:4px}
 #invest-dialog-content .history-row .del{justify-self:end}
 #invest-dialog-content .row2{grid-template-columns:1fr}
}
/* Metas vinculadas: divisões do investimento, nunca patrimônio adicional. */''')

change('''<div class="card" title="Quanto os investimentos renderam em relação ao valor colocado."><div class="label">Rendimento</div><div class="value green" id="inv-rend">R$ 0</div></div>''', '''<div class="card" title="Rendimento acumulado: valor atual menos aportes líquidos (aportes menos resgates). A porcentagem é aproximada e não pondera as datas dos aportes."><div class="label">Rendimento</div><div class="value green" id="inv-rend">R$ 0</div><div class="inv-rend-percent" id="inv-rend-pct" title="Rendimento acumulado / aportes líquidos; não é taxa contratada ou retorno anualizado.">—</div></div>''')

change('<!-- Caixas de diálogo exclusivas do próprio aplicativo. -->', '''<!-- Ações, histórico e gráfico dos investimentos em janela independente da grade. -->
<div id="invest-action-dialog" class="site-dialog" role="dialog" aria-modal="true" aria-labelledby="invest-dialog-title" hidden onclick="if(event.target===this)fecharPainelInvestimento()">
  <div class="site-dialog-panel">
    <div class="invest-dialog-heading"><h2 id="invest-dialog-title">Investimento</h2><button type="button" class="invest-dialog-close" onclick="fecharPainelInvestimento()" aria-label="Fechar janela" title="Fechar">×</button></div>
    <div id="invest-dialog-content"></div>
  </div>
</div>
<!-- Caixas de diálogo exclusivas do próprio aplicativo. -->''')

change("const investUi={acao:{},historico:{},grafico:{},mes:{},periodo:{}};", "const investUi={acao:{},historico:{},grafico:{},mes:{},periodo:{}};\nlet activeInvestDialog=null;\nlet investDialogMarkup=null;")

change("document.addEventListener('keydown',event=>{if(event.key!=='Escape'||!document.getElementById('app-confirm-overlay').hidden)return;for(const id of ['card-editor','card-payment-editor','card-paid-editor'])if(!document.getElementById(id).hidden){fecharJanela(id);break;}});", "document.addEventListener('keydown',event=>{if(event.key!=='Escape'||!document.getElementById('app-confirm-overlay').hidden)return;if(!document.getElementById('invest-action-dialog').hidden){event.preventDefault();fecharPainelInvestimento();return;}for(const id of ['card-editor','card-payment-editor','card-paid-editor'])if(!document.getElementById(id).hidden){fecharJanela(id);break;}});")

change('''function refreshInvestViews(){
  const investList''','''function refreshInvestViews(){
  investDialogMarkup=null;
  const investList''')
change('''  if(newMetaList)newMetaList.scrollTop=metaScroll;
}

function toggleInvestAction(id,acao){
  investUi.acao[id]=investUi.acao[id]===acao?'':acao;
  refreshInvestViews();
}

function toggleInvestHistory(id){
  investUi.historico[id]=!investUi.historico[id];
  refreshInvestViews();
}

function toggleInvestChart(id){
  investUi.grafico[id]=!investUi.grafico[id];
  refreshInvestViews();
}''', '''  if(newMetaList)newMetaList.scrollTop=metaScroll;
  sincronizarPainelInvestimento();
}

function sincronizarPainelInvestimento(){
  const dialog=document.getElementById('invest-action-dialog');
  if(!activeInvestDialog){dialog.hidden=true;document.body.classList.remove('invest-modal-open');return;}
  if(!investDialogMarkup||String(investDialogMarkup.id)!==String(activeInvestDialog.id)){
    fecharPainelInvestimento();return;
  }
  const primeiroAcesso=dialog.hidden;
  document.getElementById('invest-dialog-title').textContent=investDialogMarkup.nome;
  document.getElementById('invest-dialog-content').innerHTML=investDialogMarkup.body;
  dialog.hidden=false;
  document.body.classList.add('invest-modal-open');
  if(primeiroAcesso)dialog.querySelector('.invest-dialog-close').focus();
}
function fecharPainelInvestimento(){
  const ativo=activeInvestDialog;
  activeInvestDialog=null;investDialogMarkup=null;
  const dialog=document.getElementById('invest-action-dialog');
  dialog.hidden=true;
  document.getElementById('invest-dialog-content').replaceChildren();
  document.body.classList.remove('invest-modal-open');
  if(!ativo)return;
  investUi.acao[ativo.id]='';investUi.historico[ativo.id]=false;investUi.grafico[ativo.id]=false;
  refreshInvestViews();
  const card=document.getElementById('invest-card-'+ativo.id);
  if(card){const botao=card.querySelector('.goal-actions button');if(botao)botao.focus();}
}
function abrirPainelInvestimento(id,tipo,acao){
  if(!S.invest.some(item=>String(item.id)===String(id)))return;
  Object.keys(investUi.acao).forEach(key=>investUi.acao[key]='');
  Object.keys(investUi.historico).forEach(key=>investUi.historico[key]=false);
  Object.keys(investUi.grafico).forEach(key=>investUi.grafico[key]=false);
  activeInvestDialog={id,tipo};
  if(tipo==='acao')investUi.acao[id]=acao;
  if(tipo==='historico')investUi.historico[id]=true;
  if(tipo==='grafico')investUi.grafico[id]=true;
  refreshInvestViews();
}
function toggleInvestAction(id,acao){abrirPainelInvestimento(id,'acao',acao);}
function toggleInvestHistory(id){abrirPainelInvestimento(id,'historico');}
function toggleInvestChart(id){abrirPainelInvestimento(id,'grafico');}''')

change('''  document.getElementById('inv-rend').textContent=fmt(rendimento);
  document.getElementById('inv-qtd').textContent=investimentos.length;''','''  const porcentagem=base>0?rendimento/base*100:null;
  const rendEl=document.getElementById('inv-rend');
  rendEl.textContent=fmt(rendimento);
  rendEl.style.color=rendimento<0?'#E24B4A':'#1D9E75';
  const percentualEl=document.getElementById('inv-rend-pct');
  percentualEl.textContent=porcentagem===null?'— (sem base para calcular)':(porcentagem>0?'+':'')+porcentagem.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})+'% acumulado aprox.';
  percentualEl.style.color=rendimento<0?'#E24B4A':'#9FE1CB';
  document.getElementById('inv-qtd').textContent=investimentos.length;''')

change('''  return `<div class="goal-card">
    <button class="goal-delete" onclick="delInv(${item.id})"''','''  if(activeInvestDialog&&String(activeInvestDialog.id)===String(item.id)){
    const conteudo=activeInvestDialog.tipo==='acao'?painelAcao:activeInvestDialog.tipo==='historico'?historicoHtml:graficoHtml;
    if(conteudo)investDialogMarkup={id:item.id,nome:item.nome,body:conteudo};
  }
  return `<div class="goal-card" id="invest-card-${item.id}">
    <button class="goal-delete" onclick="delInv(${item.id})"''')
change('''    ${painelAcao}
    ${historicoHtml}
    ${graficoHtml}
  </div>`;''','''  </div>`;''')
# Guard against inadvertently changing finance persistence or touching user JSON.
assert 'function salvarIdentificacaoInvestimento(' in s
assert 'function movimentarReservaInterna(' in s
assert 'function validarDadosImportados(' in s
assert 'id="inv-rend-pct"' in s
assert 'id="invest-action-dialog"' in s
assert s.count('function fecharPainelInvestimento(')==1
p.write_text(s,encoding='utf-8')
print('PASS: modais para acoes, historico e grafico; percentual acumulado; sem alterar calculos de saldo ou formato JSON.')

from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def trocar(antes,depois,vezes=1):
 global s
 encontrado=s.count(antes)
 if encontrado!=vezes: raise AssertionError(f'Esperado {vezes} trecho(s), encontrado {encontrado}: {antes[:115]!r}')
 s=s.replace(antes,depois)

# Percentual acumulado junto ao rendimento, usando a mesma base dos totais.
trocar('<div class="value green" id="inv-rend">R$ 0</div>', '<div class="inv-rend-summary"><span class="value green" id="inv-rend">R$ 0</span><span class="inv-rend-percent" id="inv-rend-pct" title="Rendimento acumulado dividido pelos aportes líquidos (aportes menos resgates). Indicador aproximado, não é taxa anual nem retorno ponderado pelo tempo.">—</span></div>')
trocar("  document.getElementById('inv-rend').textContent=fmt(rendimento);", "  document.getElementById('inv-rend').textContent=fmt(rendimento);\n  document.getElementById('inv-rend-pct').textContent=base>0?(rendimento/base*100).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+'%':'—';")

# Overlay único, acessível, independente da largura dos cartões. Mantém os IDs dos campos e os handlers existentes.
modal='''<div id="invest-modal" class="site-dialog invest-dialog" role="dialog" aria-modal="true" aria-labelledby="invest-modal-title" hidden onclick="if(event.target===this)fecharPainelInvestimento()">
  <div class="site-dialog-panel invest-modal-panel">
    <div class="invest-modal-heading"><div><span class="invest-modal-eyebrow">Investimentos e metas</span><h2 id="invest-modal-title">Detalhes</h2></div><button class="invest-modal-close" type="button" onclick="fecharPainelInvestimento()" aria-label="Fechar janela">×</button></div>
    <div id="invest-modal-content"></div>
  </div>
</div>
'''
trocar('<script>\nconst S={extrato:[]',modal+'<script>\nconst S={extrato:[]')
css='''/* Ações de investimentos em janela flutuante, sem esticar cartões vizinhos. */
.inv-rend-summary{display:flex;justify-content:center;align-items:baseline;gap:9px;flex-wrap:wrap}
.inv-rend-percent{font-size:14px;font-weight:800;white-space:nowrap;color:#9FE1CB;background:#17392e;border:1px solid #285d4b;border-radius:99px;padding:4px 9px}
.invest-modal-open{overflow:hidden}
.invest-dialog{z-index:17000}
.invest-modal-panel{width:min(100%,680px);max-height:min(90dvh,760px);overflow-y:auto;overscroll-behavior:contain;padding:21px}
.invest-modal-heading{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:18px;padding-bottom:13px;border-bottom:1px solid #393932}
.invest-modal-heading h2{font-size:20px;line-height:1.25;margin:4px 0 0;overflow-wrap:anywhere}
.invest-modal-eyebrow{font-size:11px;letter-spacing:.07em;text-transform:uppercase;font-weight:800;color:#9FE1CB}
.invest-modal-close{flex:none;width:36px;height:36px;border-radius:9px;border:1px solid #4a4944;background:#282825;color:#f5f5f2;font-size:25px;cursor:pointer;line-height:1}
.invest-modal-close:hover,.invest-modal-close:focus-visible{border-color:#9FE1CB}
#invest-modal-content .goal-panel{margin:0;background:transparent;border:0;box-shadow:none;padding:0}
#invest-modal-content .goal-panel-title{font-size:15px;margin-bottom:12px}
#invest-modal-content input,#invest-modal-content select{max-width:100%;min-width:0;box-sizing:border-box}
#invest-modal-content .history-row{grid-template-columns:64px minmax(0,1fr) 110px 24px}
#invest-modal-content .stock-chart{max-width:100%;overflow-x:auto}
@media(max-width:580px){.invest-dialog{padding:10px}.invest-modal-panel{padding:16px;max-height:calc(100dvh - 20px)}#invest-modal-content .row2{grid-template-columns:1fr}#invest-modal-content .history-row{grid-template-columns:52px minmax(0,1fr) 80px 24px;gap:5px;font-size:11px}#invest-modal-content .history-value{font-size:11px}.invest-modal-heading h2{font-size:17px}.inv-rend-percent{font-size:12px}}
'''
trocar('</style>\n</head>',css+'</style>\n</head>')

# Associação explícita da janela ao cartão correspondente.
trocar('const investUi={acao:{},historico:{},grafico:{},mes:{},periodo:{}};', 'const investUi={acao:{},historico:{},grafico:{},mes:{},periodo:{}};\nlet investModalAtivo=null;')
trocar('  return `<div class="goal-card">\n    <button class="goal-delete"', '  return `<div class="goal-card" data-invest-id="${item.id}">\n    <button class="goal-delete"')

antes='''function toggleInvestAction(id,acao){
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
}
'''
depois='''// O formulário/histórico/gráfico é gerado pelas funções existentes, mas movido
// para o modal. Não são criadas cópias dos campos, nem dados financeiros paralelos.
function fecharPainelInvestimento(devolverFoco=true){
  const anterior=investModalAtivo;
  if(anterior){
    investUi.acao[anterior.id]='';
    investUi.historico[anterior.id]=false;
    investUi.grafico[anterior.id]=false;
  }
  investModalAtivo=null;
  const overlay=document.getElementById('invest-modal');
  if(overlay)overlay.hidden=true;
  const content=document.getElementById('invest-modal-content');
  if(content)content.replaceChildren();
  document.body.classList.remove('invest-modal-open');
  if(devolverFoco&&anterior){
    const cartao=document.querySelector('.goal-card[data-invest-id="'+anterior.id+'"]');
    const botao=cartao&&cartao.querySelector('.goal-actions button');
    if(botao)botao.focus();
  }
}
function sincronizarPainelInvestimento(){
  if(!investModalAtivo)return;
  const {id,tipo}=investModalAtivo;
  const ativo=tipo==='historico'?investUi.historico[id]:tipo==='grafico'?investUi.grafico[id]:investUi.acao[id]===tipo;
  const card=document.querySelector('.goal-card[data-invest-id="'+id+'"]');
  const panel=card&&card.querySelector('.goal-panel');
  if(!ativo||!panel){fecharPainelInvestimento(false);return;}
  const item=S.invest.find(x=>String(x.id)===String(id));
  const overlay=document.getElementById('invest-modal');
  const content=document.getElementById('invest-modal-content');
  const titulo=document.getElementById('invest-modal-title');
  const novo=!overlay.hidden;
  titulo.textContent=(item?item.nome:'Investimento')+' · '+({dados:'Editar dados','editar-meta':'Editar meta',atualizar:'Atualizar valor',resgatar:'Resgatar',reservar:'Reservar saldo',liberar:'Liberar reserva',aportar:'Aportar',historico:'Histórico',grafico:'Gráfico'}[tipo]||'Detalhes');
  content.replaceChildren(panel);
  overlay.hidden=false;
  document.body.classList.add('invest-modal-open');
  if(!novo)overlay.querySelector('.invest-modal-close').focus();
}
function abrirPainelInvestimento(id,tipo){
  if(!S.invest.some(x=>String(x.id)===String(id)))return;
  fecharPainelInvestimento(false);
  investModalAtivo={id,tipo};
  investUi.acao[id]='';
  investUi.historico[id]=false;
  investUi.grafico[id]=false;
  if(tipo==='historico')investUi.historico[id]=true;
  else if(tipo==='grafico')investUi.grafico[id]=true;
  else investUi.acao[id]=tipo;
  refreshInvestViews();
}
function toggleInvestAction(id,acao){abrirPainelInvestimento(id,acao);}
function toggleInvestHistory(id){abrirPainelInvestimento(id,'historico');}
function toggleInvestChart(id){abrirPainelInvestimento(id,'grafico');}
document.addEventListener('keydown',event=>{
  if(event.key!=='Escape'||!investModalAtivo)return;
  const confirmacao=document.getElementById('app-confirm-overlay');
  if(confirmacao&&!confirmacao.hidden)return;
  event.preventDefault();fecharPainelInvestimento();
});
'''
trocar(antes,depois)
trocar('  if(newMetaList)newMetaList.scrollTop=metaScroll;\n}', '  if(newMetaList)newMetaList.scrollTop=metaScroll;\n  sincronizarPainelInvestimento();\n}')

# Histórico/gráfico continuam com suas opções e datas, só muda o local de exibição.
assert s.count('sincronizarPainelInvestimento();')==1
assert 'localStorage' not in s
p.write_text(s,encoding='utf-8')
print('PASS: ações abertas em modal; rendimento percentual com base líquida; dados financeiros intactos.')

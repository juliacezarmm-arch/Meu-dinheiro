from pathlib import Path


def once(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: esperado exatamente 1 trecho, encontrados {count}')
    return text.replace(old,new,1)

p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=once(s,'<script src="js/recorrentes.js?v=20260920-integrado1"></script>','<script src="js/recorrentes.js?v=20260920-planejamento1"></script>','Versao do script')

# Compra total e quantidade de parcelas passam a ter colunas independentes.
s=once(s,'''  const rows=S.cartao.filter(c=>cartaoTemMes(c,viewYear,viewMonth)).sort((a,b)=>b.data.localeCompare(a.data));''','''  const forecasts=typeof window.cardRecurringForecasts==='function'?window.cardRecurringForecasts():[];
  const rows=S.cartao.concat(forecasts).filter(c=>cartaoTemMes(c,viewYear,viewMonth)).sort((a,b)=>b.data.localeCompare(a.data));''','Mesclar compras e previsoes')
s=once(s,'''<th style="width:58px">Vence</th><th style="width:118px">Valor</th><th style="width:54px"></th>''','''<th style="width:54px">Vence</th><th style="width:64px">Parcelas</th><th style="width:108px">Valor total</th><th style="width:54px"></th>''','Cabecalho do cartao')
s=once(s,'''      const label=r.tipo==='parcelado'?`${r.parcelas} parcelas (aprox. ${fmt(valorParcela(r,0))})`:fmt(r.val);''','''      const label=fmt(r.val);
      const qtdParcelas=Number(r.parcelas)||1;''','Valor de compra')
s=once(s,'''      const cat=`${r.subcategoria||'Sem categoria'}${r.recorrenciaId?' · Recorrente':''}${historico?' · Histórico anterior à abertura':''}`;''','''      const cat=`${r.subcategoria||'Sem categoria'}${historico?' · Histórico anterior à abertura':''}`;''','Sem selo redundante')
s=once(s,'''      return`<tr><td>${d.getDate().toString().padStart(2,'0')}/${(d.getMonth()+1).toString().padStart(2,'0')}</td><td style="max-width:160px;overflow:hidden;text-overflow:ellipsis">${escHtml(desc)}<div style="font-size:11px;color:var(--color-text-secondary)">${escHtml(cat)}</div></td><td><span class="badge b-compra">${tipoLabel}</span></td><td>${venc}</td><td>${label}</td><td><button class="del" onclick="editCartao(${r.id})" aria-label="Editar" title="Edita esta compra sem precisar apagar e lançar de novo.">✎</button><button class="del" onclick="delCC(${r.id})" aria-label="Remover" title="Apaga esta compra do cartão."><i class="ti ti-x" aria-hidden="true"></i></button></td></tr>`;''','''      const actions=r.previsto?`<button class="del" type="button" onclick="editRecurringCardForecast(${Number(r.recorrenciaId)})" aria-label="Editar assinatura" title="Edita a programação desta assinatura">✎</button>`:`<button class="del" onclick="editCartao(${r.id})" aria-label="Editar" title="Edita esta compra.">✎</button><button class="del" onclick="delCC(${r.id})" aria-label="Remover" title="Apaga esta compra do cartão."><i class="ti ti-x" aria-hidden="true"></i></button>`;
      return`<tr><td>${d.getDate().toString().padStart(2,'0')}/${(d.getMonth()+1).toString().padStart(2,'0')}</td><td style="max-width:160px;overflow:hidden;text-overflow:ellipsis">${escHtml(desc)}<div style="font-size:11px;color:var(--color-text-secondary)">${escHtml(cat)}</div></td><td><span class="badge b-compra">${r.previsto?'Previsto':tipoLabel}</span></td><td>${venc}</td><td style="text-align:center">${qtdParcelas}x</td><td style="white-space:nowrap;font-variant-numeric:tabular-nums">${label}</td><td>${actions}</td></tr>`;''','Linhas de cartao')
# Pagamento so via Extrato; o controle de pagamento parcial e preservado.
s=once(s,'''      ${aberto>0&&!historica?`<button class="btn-green" type="button" onclick="registrarPagamentoFatura(${card.id},'${faturaKey}')">Registrar pagamento</button>`:(historica?'<span>Somente histórico; sem impacto no saldo.</span>':'<span>Pagamento registrado; sem valor pendente.</span>')}''','''      ${aberto>0&&!historica?'<span>Fatura pendente: marque o pagamento diretamente no Extrato.</span>':(historica?'<span>Somente histórico; sem impacto no saldo.</span>':'<span>Pagamento registrado; sem valor pendente.</span>')}''','Remover botao do cartao')
s=once(s,'''document.getElementById('card-payment-title').textContent='Pagamento · '+card.bank;''','''document.getElementById('card-payment-title').textContent='Marcar como pago · '+card.bank;''','Titulo do pagamento')
s=once(s,'''<h2 id="card-payment-title">Registrar pagamento</h2>''','''<h2 id="card-payment-title">Marcar como pago</h2>''','Cabecalho pagamento')
s=once(s,'''type="submit">Registrar pagamento</button></div></form>''','''type="submit">Confirmar pagamento</button></div></form>''','Botao pagamento')

start=s.index('\nfunction renderExtrato(){')
new_functions='''
// Faturas pendentes são compromissos: entram na projeção, mas não no caixa até o pagamento.
// Cada cartão mantém sua própria fatura; compras e assinaturas nunca viram saídas duplicadas.
function faturasPendentesDoMes(y,m){
  const mes=isoDate(y,m,1).slice(0,7);
  return S.cartoes.flatMap(card=>{
    const total=totalDaFaturaFinanceira(card.id,mes);
    const pago=pagoNaFaturaFinanceira(card.id,mes);
    const restante=Math.max(0,total-pago);
    if(!restante)return [];
    const dia=Math.min(Number(card.dueDay)||10,new Date(y,m+1,0).getDate());
    return [{id:'fatura-pendente-'+card.id+'-'+mes,data:isoDate(y,m,dia),desc:'Fatura · '+card.bank,tipo:'cartao',categoria:'Cartão de crédito',subcategoria:card.bank,val:restante/100,cardId:card.id,faturaMes:mes,faturaPendente:true,auto:true}];
  });
}
function calcularSobraPrevistaAte(fim){
  if(!saldoInicialValido(S.saldoInicial)||!dataISOValida(fim)||fim<today())return null;
  let centavos=Math.round(calcularSaldoDisponivelAte(today())*100);
  const ignorados=new Set(S.saldoInicial.idsIgnorados.map(String));
  for(const x of S.extrato){
    if(x.data<=today()||x.data>fim||x.data<S.saldoInicial.data||ignorados.has(String(x.id)))continue;
    if(x.tipo==='entrada'&&x.subcategoria==='Dinheiro do mês passado')continue;
    const val=Math.round(Number(x.val||0)*100);
    if(x.tipo==='entrada')centavos+=val;
    else if(['saida','investimento','meta'].includes(x.tipo))centavos-=val;
  }
  const limite=new Date(fim+'T12:00:00');
  const cursor=new Date(today().slice(0,7)+'-01T12:00:00');
  let i=0;
  for(;cursor<=limite&&i<240;i++,cursor.setMonth(cursor.getMonth()+1)){
    if(typeof window.cashRecurringForecasts==='function')for(const rec of window.cashRecurringForecasts(cursor.getFullYear(),cursor.getMonth())){
      if(rec.data>fim)continue;
      centavos+=(rec.tipo==='entrada'?1:-1)*Math.round(rec.val*100);
    }
  }
  if(cursor<=limite)return null;
  const meses=new Set(parcelasCartaoFinanceiras().filter(x=>x.data<=fim).map(x=>String(x.cardId)+'|'+x.data.slice(0,7)));
  for(const chave of meses){
    const [id,mes]=chave.split('|');
    centavos-=Math.max(0,totalDaFaturaFinanceira(id,mes)-pagoNaFaturaFinanceira(id,mes));
  }
  return centavos/100;
}
'''
s=s[:start]+new_functions+s[start:]
s=once(s,'''  const resumoCartao=getResumoCartaoExtrato(viewYear,viewMonth);''','''  const faturas=faturasPendentesDoMes(viewYear,viewMonth);''','Faturas individualizadas')
s=once(s,'''  const rowsBase=S.extrato.concat(resumoCartao?[resumoCartao]:[],linhaSaldo?[linhaSaldo]:[]).filter(''','''  const rowsBase=S.extrato.concat(faturas,linhaSaldo?[linhaSaldo]:[]).filter(''','Faturas na tabela')
s=once(s,'''  const parcelasMes=resumoCartao?[resumoCartao]:[];''','''  const parcelasMes=faturas;''','Resumo de faturas')
s=once(s,'''  const aviso=parcelasMes.length?'<div class="hint">'+(S.saldoInicial?'O cartão é apenas uma previsão. Para descontar o dinheiro, lance o pagamento da fatura como saída; não registre a compra como outra despesa.':'O extrato mostra o cartão como uma soma do mês. Os detalhes ficam na aba Cartão.')+'</div>':'';''','''  const aviso=parcelasMes.length?'<div class="hint">As faturas pendentes entram na sobra prevista. Ao pagar, use o botão da fatura abaixo; o saldo de hoje só muda após registrar o pagamento.</div>':'';''','Texto de compromisso')
s=once(s,'''    <div class="plain-card"><strong>Cartão previsto: ${fmt(cartaoMes)}</strong><span>Fatura prevista para ${monthLabel}, não é pagamento.</span></div>''','''    <div class="plain-card"><strong>Cartão a pagar: ${fmt(cartaoMes)}</strong><span>Valor em aberto nas faturas deste mês.</span></div>''','Resumo cartao')
s=once(s,'''  if(!rows.length){wrap.innerHTML=resumo+avisoSaldo+'<div class="empty">Nenhum lançamento em '+monthLabel+'.</div>';return;}''','''  const fimMes=isoDate(viewYear,viewMonth,new Date(viewYear,viewMonth+1,0).getDate());
  const sobra=calcularSobraPrevistaAte(fimMes);
  const projecao=saldoInicialValido(S.saldoInicial)?`<div class="plain-summary compact-summary" style="margin:8px 0 12px"><div class="plain-card"><strong>Saldo de hoje: ${fmt(calcularSaldoDisponivelAte(today()))}</strong><span>Somente dinheiro lançado até hoje.</span></div><div class="plain-card"><strong style="color:${sobra===null?'#c5c3ba':sobra<0?'#efaba4':'#9FE1CB'}">${sobra===null?'Sobra prevista indisponível':'Sobra prevista até '+fimMes.slice(8,10)+'/'+fimMes.slice(5,7)+': '+fmt(sobra)}</strong><span>Inclui entradas e contas programadas e faturas em aberto, sem descontar compras duas vezes.</span></div></div>`:'';
  if(!rows.length){wrap.innerHTML=resumo+projecao+avisoSaldo+'<div class="empty">Nenhum lançamento em '+monthLabel+'.</div>';return;}''','Bloco de saldo previsto')
s=once(s,'''  wrap.innerHTML=resumo+avisoSaldo+aviso+'<table><thead><tr><th style="width:64px">Data</th><th>Descrição</th><th style="width:130px">Categoria</th><th style="width:70px">Status</th><th style="width:86px">Valor</th><th style="width:22px"></th></tr></thead><tbody>'+''','''  wrap.innerHTML=resumo+projecao+avisoSaldo+aviso+'<table><thead><tr><th style="width:54px">Data</th><th>Descrição</th><th style="width:94px">Categoria</th><th style="width:67px">Status</th><th style="width:116px">Valor</th><th style="width:110px"></th></tr></thead><tbody>'+''','Tabela extrato')
s=once(s,'''      const tipoLabel=r.previsto||futuro?'previsto':r.tipo==='saldo_inicial'?'saldo':r.tipo==='cartao'?'cartão':r.tipo==='investimento'?'invest.':r.tipo==='meta'?'meta':r.tipo;''','''      const tipoLabel=r.faturaPendente?'a pagar':r.previsto||futuro?'previsto':r.tipo==='saldo_inicial'?'saldo':r.tipo==='cartao'?'cartão':r.tipo==='investimento'?'invest.':r.tipo==='meta'?'meta':r.tipo;''','Status fatura')
s=once(s,'''      const action=r.auto?'':`<button class="del" onclick="delExt(${r.id})" aria-label="Remover" title="Apaga este lançamento do extrato."><i class="ti ti-x" aria-hidden="true"></i></button>`;''','''      const action=r.faturaPendente?`<button class="extrato-pagar" type="button" onclick="registrarPagamentoFatura(${Number(r.cardId)},'${r.faturaMes}')" aria-label="Marcar como pago ${escHtml(r.desc)}">Marcar como pago</button>`:r.auto?'':`<button class="del" onclick="delExt(${r.id})" aria-label="Remover" title="Apaga este lançamento do extrato."><i class="ti ti-x" aria-hidden="true"></i></button>`;''','Botao fatura extrato')
s=once(s,'''      const detalhe=r.tipo==='meta'&&r.storageNome?`<div style="font-size:11px;color:var(--color-text-secondary)">Guardado em ${escHtml(r.storageNome)}</div>`:r.tipo==='cartao'?`<div style="font-size:11px;color:var(--color-text-secondary)">Detalhes das compras na aba Cartão.</div>`:'';''','''      const detalhe=r.tipo==='meta'&&r.storageNome?`<div style="font-size:11px;color:var(--color-text-secondary)">Guardado em ${escHtml(r.storageNome)}</div>`:r.faturaPendente?`<div style="font-size:11px;color:var(--color-text-secondary)">Vencimento da fatura; ainda não pago.</div>`:r.tipo==='cartao'?`<div style="font-size:11px;color:var(--color-text-secondary)">Detalhes na aba Cartão.</div>`:'';''','Detalhe da fatura')
# As linhas podem acomodar valores monetarios completos e um botao legivel sem alterar dados.
s=once(s,'''table{width:100%;border-collapse:collapse;font-size:13px;table-layout:fixed}''','''table{width:100%;border-collapse:collapse;font-size:13px;table-layout:fixed}
.extrato-pagar{font:700 10px var(--font-sans);padding:6px 5px;background:#1D9E75;border:1px solid #1D9E75;border-radius:7px;color:white;cursor:pointer;white-space:nowrap}
#ext-wrap td:nth-child(5){font-variant-numeric:tabular-nums;font-size:12px;white-space:nowrap}
#ext-wrap td:last-child{overflow:visible;white-space:nowrap;text-align:right}
#cc-wrap td:nth-child(6){font-variant-numeric:tabular-nums;white-space:nowrap}
@media(max-width:580px){#ext-wrap table{font-size:11px}#ext-wrap th,#ext-wrap td{padding:6px 3px}#ext-wrap th:last-child{width:94px!important}#ext-wrap .extrato-pagar{font-size:9px;padding:5px 3px}#cc-wrap table{font-size:11px}#cc-wrap th,#cc-wrap td{padding:6px 3px}}''','Styles responsivos')
p.write_text(s,encoding='utf-8')

p=Path('js/recorrentes.js')
s=p.read_text(encoding='utf-8')
s=once(s,'''cardSection.innerHTML='<div class="rec-top"><div><strong>Assinaturas recorrentes no cartão</strong><p>Cadastre cobranças periódicas do crédito aqui, separadas dos débitos da conta. Excluir interrompe o futuro, mas mantém as cobranças anteriores.</p></div><button type="button" class="rec-button primary" id="rec-card-open">+ Nova assinatura</button></div><div class="rec-list" id="rec-card-list"></div>';''','''cardSection.innerHTML='<div class="rec-top"><button type="button" id="rec-card-toggle" aria-expanded="true" aria-controls="rec-card-body">Assinaturas recorrentes no cartão <span id="rec-card-toggle-symbol" aria-hidden="true">−</span></button></div><div id="rec-card-body"><p class="rec-caption">Cadastre e edite assinaturas aqui. As cobranças aparecem junto às demais compras em Lançamentos.</p><button type="button" class="rec-button primary" id="rec-card-open">+ Nova assinatura</button><div class="rec-list" id="rec-card-list"></div></div>';''','Minimizar assinaturas')
s=once(s,'''#rec-toggle{width:100%;''','''#rec-card-toggle{width:100%;display:flex;justify-content:space-between;align-items:center;gap:10px;background:transparent;border:0;color:#f5f5f2;padding:0;text-align:left;font-size:15px;font-weight:750;cursor:pointer}#rec-card-toggle span{font-size:20px;color:#9FE1CB;line-height:1}#rec-card-body[hidden]{display:none!important}#rec-toggle{width:100%;''','Estilo do toggle cartao')
s=once(s,''' if(editingRecMode==='conta')setRecAreaExpanded(true);''',''' if(editingRecMode==='conta')setRecAreaExpanded(true);
 else setCardRecAreaExpanded(true);''','Expandir ao editar assinatura')
s=once(s,'''function closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';placeCardRow();$('rec-body').appendChild($('rec-form'));}''','''function setCardRecAreaExpanded(expanded){
 $('rec-card-body').hidden=!expanded;
 $('rec-card-toggle').setAttribute('aria-expanded',String(expanded));
 $('rec-card-toggle-symbol').textContent=expanded?'−':'+';
 if(!expanded&&$('rec-form').parentElement===$('rec-card-body'))closeRecEditor();
}
function closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';placeCardRow();$('rec-body').appendChild($('rec-form'));}''','Funcao toggle assinatura')
s=once(s,'''const oldCardRender=renderCartao;
renderCartao=function(){oldCardRender();const wrap=$('cc-wrap'),futuras=cardForecasts().filter(x=>cartaoTemMes(x,cartaoMes.getFullYear(),cartaoMes.getMonth()));
 const existing=$('rec-card-forecast');if(existing)existing.remove();
 if(futuras.length){const box=document.createElement('div');box.id='rec-card-forecast';box.className='rec-predictions';box.innerHTML='<strong>Assinaturas programadas (ainda não cobradas)</strong>'+futuras.map(x=>`<div class="rec-card-prediction">${displayDate(x.data)} · ${escHtml(x.desc)} · ${fmt(x.val)} · ${escHtml(x.banco)}</div>`).join('');wrap.parentNode.insertBefore(box,wrap);}
};''','''// Mesmo modelo de lançamentos para compras avulsas e assinaturas futuras;
// a previsão não vira registro persistido até chegar sua data.
window.cardRecurringForecasts=cardForecasts;
window.editRecurringCardForecast=id=>openRecEditor(id,'cartao');''','Unificar lista card')
s=once(s,'''$('rec-toggle').addEventListener('click',()=>setRecAreaExpanded($('rec-body').hidden));''','''$('rec-toggle').addEventListener('click',()=>setRecAreaExpanded($('rec-body').hidden));
$('rec-card-toggle').addEventListener('click',()=>setCardRecAreaExpanded($('rec-card-body').hidden));''','Listener toggle assinatura')
p.write_text(s,encoding='utf-8')

# Regressões: colunas distintas, projeção sem saldo antecipado, histórico e uma única lista.
test=Path('tests/recorrentes.test.js')
t=test.read_text(encoding='utf-8')
t=once(t,'20260920-integrado1','20260920-planejamento1','Versao teste recorrencia')
t=t.replace("assert(js.includes('cardRow.hidden=true;cardRow.remove()'),'Campo de cartão precisa sair fisicamente do formulário da conta');", "assert(js.includes('cardRow.hidden=true;cardRow.remove()'),'Campo de cartão precisa sair fisicamente do formulário da conta');\nassert(js.includes('id=\\\"rec-card-toggle\\\"')&&js.includes('setCardRecAreaExpanded'),'Assinaturas precisam ser minimizáveis');\nassert(!js.includes('Assinaturas programadas (ainda não cobradas)'),'Não separar as assinaturas da lista de lançamentos');\nassert(html.includes('Valor total</th>')&&html.includes('Parcelas</th>'),'Quantidade de parcelas e preço devem ser colunas distintas');\nassert(html.includes('calcularSobraPrevistaAte')&&html.includes('faturasPendentesDoMes'),'Sobra prevista deve considerar faturas sem contaminar saldo de hoje');\nassert(!html.includes('onclick=\\\"registrarPagamentoFatura(${card.id}'),'Pagamento não deve ficar na aba Cartão');\nassert(html.includes('Marcar como pago</button>'),'Extrato deve ter ação de pagamento da fatura');")
test.write_text(t,encoding='utf-8')
smoke=Path('tests/recorrentes-browser-smoke.py')
t=smoke.read_text(encoding='utf-8')
t=once(t,'20260920-integrado1','20260920-planejamento1','Versao smoke')
t=once(t," if(!document.getElementById('rec-card-open'))throw Error('Área própria de assinatura ausente');", " if(!document.getElementById('rec-card-open'))throw Error('Área própria de assinatura ausente');\n if(!document.getElementById('rec-card-toggle'))throw Error('Assinaturas sem botão para recolher');\n if(!document.querySelector('#cc-wrap'))throw Error('Tabela de lançamentos do cartão ausente');",'Smoke assinaturas')
smoke.write_text(t,encoding='utf-8')
print('PATCH OK: compras+assinaturas juntas, parcelas separado, faturas no Extrato, marcar pago, saldo atual vs sobra prevista; dados e JSON intactos')
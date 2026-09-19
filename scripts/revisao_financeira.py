from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8-sig')
assert 'function valorParcela(' not in s, 'Correções financeiras já aplicadas'

def once(old,new):
    global s
    n=s.count(old)
    assert n==1, f'Esperado 1 ocorrência, obtidas {n}: {old[:110]!r}'
    s=s.replace(old,new,1)

def fn(name,old,new):
    global s
    start=s.index('function '+name+'(')
    end=s.find('\nfunction ',start+len(name)+10)
    if end<0:end=len(s)
    fragment=s[start:end]
    n=fragment.count(old)
    assert n==1, f'{name}: esperado 1 ocorrência, obtidas {n}: {old[:105]!r}'
    s=s[:start]+fragment.replace(old,new,1)+s[end:]

once('function novoIdExtrato(){', '''function novoIdGlobal(){
  let id=Date.now();
  while(['extrato','cartao','invest','cartoes'].some(key=>S[key].some(x=>String(x.id)===String(id))))id++;
  return id;
}
function valorMonetarioValido(v){
  return Number.isFinite(v)&&v>=0&&Math.abs(v*100-Math.round(v*100))<0.000001;
}
function valorParcela(compra,indice){
  const n=Number(compra.parcelas)||1;
  const centavos=Math.round(Number(compra.val)*100);
  return (Math.floor(centavos/n)+(indice<centavos%n?1:0))/100;
}
function receitaReal(x){return x.tipo==='entrada'&&x.categoria!=='Resgate'&&x.subcategoria!=='Dinheiro do mês passado';}
function movimentoRealizado(x){return !S.saldoInicial||x.data<=today();}
function pagoNaFatura(cardId,mes){
  return S.extrato.filter(x=>x.tipo==='saida'&&String(x.cardId)===String(cardId)&&x.faturaMes===mes)
    .reduce((total,x)=>total+Math.round(Number(x.val)*100),0);
}
function totalDaFatura(cardId,mes){
  return getParcelasCartao().filter(x=>String(x.cardId)===String(cardId)&&x.data.slice(0,7)===mes)
    .reduce((total,x)=>total+Math.round(Number(x.val)*100),0);
}
function reservadoEmMetas(id){
  return S.invest.filter(x=>x.kind==='meta'&&String(x.storageId)===String(id))
    .reduce((total,x)=>total+Math.round(Number(x.valorAtual||0)*100),0)/100;
}
function novoIdExtrato(){''')

fn('confirmarSaldoInicial','idsIgnorados:S.extrato.map(x=>String(x.id))','idsIgnorados:S.extrato.filter(x=>x.data<=today()).map(x=>String(x.id))')
fn('addExtrato',"  if(S.saldoInicial&&tipo==='entrada'&&subcategoria==='Dinheiro do mês passado'){", "  if(S.saldoInicial&&tipo==='saida'&&categoria==='Cartão de crédito'&&subcategoria==='Pagamento de fatura'){\n    alert('Registre o pagamento na aba Cartão, na fatura correspondente, para evitar duplicidade.');return;\n  }\n  if(S.saldoInicial&&tipo==='entrada'&&subcategoria==='Dinheiro do mês passado'){")
fn('addExtrato',"    if(!dest||dest.kind!==tipo||isNaN(val)||val<=0){", "    if(data>today()){alert('Aportes e metas futuros devem ser registrados somente quando ocorrerem.');return;}\n    if(!dest||dest.kind!==tipo||!valorMonetarioValido(val)||val<=0){")
fn('addExtrato',"  if(!categoria||!subcategoria||isNaN(val)||val<=0){", "  if(!categoria||!subcategoria||!valorMonetarioValido(val)||val<=0){")
fn('addExtrato',"  S.extrato.push({id:novoIdExtrato(),data,desc,tipo,val,categoria,subcategoria", "  S.extrato.push({id:novoIdExtrato(),data,desc,tipo,val:Math.round(val*100)/100,categoria,subcategoria")

fn('addRegisteredCard',"  const dueDay=parseInt(rawDay);", "  const dueDay=parseInt(rawDay);\n  const closeDay=parseInt(document.getElementById('card-close-day').value);")
fn('addRegisteredCard',"  if(!bank||isNaN(dueDay)||dueDay<1||dueDay>31){alert('Escolha o banco e informe um dia de vencimento de 1 a 31.');return;}", "  if(!bank||!Number.isInteger(dueDay)||dueDay<1||dueDay>31||!Number.isInteger(closeDay)||closeDay<1||closeDay>31){alert('Informe o banco e os dias de fechamento e vencimento (1 a 31).');return;}")
fn('addRegisteredCard',"S.cartoes.push({id:Date.now(),bank,dueDay,color:", "S.cartoes.push({id:novoIdGlobal(),bank,dueDay,closeDay,color:")
fn('addRegisteredCard',"  document.getElementById('card-due-day').value='';", "  document.getElementById('card-due-day').value='';\n  document.getElementById('card-close-day').value='';")
fn('delRegisteredCard',"  if(S.cartao.some(x=>x.cardId===id)){", "  if(S.cartao.some(x=>x.cardId===id)||S.extrato.some(x=>String(x.cardId)===String(id)&&x.faturaMes)){")
fn('renderRegisteredCards',"${c.bank} - vence dia ${c.dueDay}","${c.bank} - vence dia ${c.dueDay}") if False else None
fn('renderRegisteredCards','      <div class="bank-due">Vence todo dia ${c.dueDay}</div>', '      <div class="bank-due">Fecha dia ${c.closeDay||"?"} · vence dia ${c.dueDay}</div>\n      <button type="button" onclick="configurarFechamento(${c.id})" style="margin-top:8px;padding:5px;background:#242423;color:#fff;border:1px solid #777;border-radius:5px">Configurar fechamento</button>')

once('function dueDateFor(baseDate,dueDay,offset){\n  const startOffset=baseDate.getDate()>dueDay?1:0;', '''function configurarFechamento(id){
  const card=S.cartoes.find(x=>x.id===id);
  if(!card)return;
  if(S.extrato.some(x=>String(x.cardId)===String(id)&&x.faturaMes)){
    alert('Este cartão já possui pagamentos vinculados. Não altere o fechamento sem reconciliar as faturas.');return;
  }
  const answer=prompt('Dia de fechamento da fatura (1 a 31):',card.closeDay||'');
  if(answer===null)return;
  const day=Number(answer);
  if(!Number.isInteger(day)||day<1||day>31){alert('Informe um dia válido de 1 a 31.');return;}
  if(!confirm('Recalcular os vencimentos de TODAS as compras desse cartão que ainda não possuem pagamentos vinculados?'))return;
  card.closeDay=day;
  S.cartao.filter(x=>String(x.cardId)===String(id)).forEach(x=>x.closeDay=day);
  saveData();renderRegisteredCards();renderCartao();renderExtrato();updateResumo();
}
function registrarPagamentoFatura(cardId,mes){
  if(!S.saldoInicial){alert('Informe primeiro seu saldo inicial no Extrato.');return;}
  const card=S.cartoes.find(x=>String(x.id)===String(cardId));
  if(!card)return;
  const total=totalDaFatura(cardId,mes);
  const restante=total-pagoNaFatura(cardId,mes);
  if(restante<=0){alert('Esta fatura não possui valor em aberto.');return;}
  const resposta=prompt('Valor pago da fatura '+card.bank+' '+mes+' (sem separador de milhares):',(restante/100).toFixed(2));
  if(resposta===null)return;
  const valor=Number(resposta.trim().replace(',','.'));
  if(!valorMonetarioValido(valor)||valor<=0||Math.round(valor*100)>restante){alert('Valor inválido ou maior que o saldo da fatura.');return;}
  if(!confirm('Confirmar pagamento de '+fmt(valor)+' na data de hoje?'))return;
  S.extrato.push({id:novoIdExtrato(),data:today(),desc:'Pagamento de fatura - '+card.bank+' '+mes,
    tipo:'saida',categoria:'Cartão de crédito',subcategoria:'Pagamento de fatura',
    gastoTipo:'variavel',pagamento:'transferencia',val:Math.round(valor*100)/100,cardId:card.id,faturaMes:mes});
  saveData();renderCartao();renderExtrato();updateResumo();
}
function dueDateFor(baseDate,dueDay,offset,closeDay){
  const startOffset=closeDay?((baseDate.getDate()>closeDay?1:0)+(dueDay<=closeDay?1:0)):(baseDate.getDate()>dueDay?1:0);''')

once('        <input type="text" id="card-due-day" placeholder="O cartão vence dia" inputmode="numeric" maxlength="2" pattern="[0-9]*" title="Dia do mês em que a fatura desse cartão vence. Use de 1 a 31."/>', '        <input type="text" id="card-due-day" placeholder="O cartão vence dia" inputmode="numeric" maxlength="2" pattern="[0-9]*" title="Dia de vencimento da fatura (1 a 31)."/>')
once('      <button class="btn-green" onclick="addRegisteredCard()"', '      <div class="row row1"><input type="number" id="card-close-day" placeholder="Dia de fechamento da fatura" min="1" max="31" step="1" title="Informe o fechamento informado pelo banco para calcular o mês correto da parcela."/></div>\n      <button class="btn-green" onclick="addRegisteredCard()"')
once('    <div class="section-title" title="Lista de compras e parcelas do cartão no mês selecionado.">Lançamentos</div>', '    <div class="section-title">Faturas e pagamentos</div>\n    <div id="cc-faturas" class="chart-panel"><div class="hint">Cadastre um cartão para acompanhar o pagamento.</div></div>\n    <div class="section-title" title="Lista de compras e parcelas do cartão no mês selecionado.">Lançamentos</div>')

fn('updatePreview',"dueDateFor(d,vencDia,0)","dueDateFor(d,vencDia,0,card.closeDay)")
fn('updatePreview',"dueDateFor(d,vencDia,n-1)","dueDateFor(d,vencDia,n-1,card.closeDay)")
fn('updatePreview',"const parc=(val/n);", "const parc=valorParcela({val,parcelas:n},0);")
fn('updatePreview',"n+'x de '+fmt(parc)","n+' parcelas (aprox. '+fmt(parc)+', com ajuste de centavos)'")
fn('addCartao',"  if(!desc||isNaN(val)||val<=0||!categoria||!subcategoria||!gastoTipo){", "  if(!desc||!valorMonetarioValido(val)||val<=0||!categoria||!subcategoria||!gastoTipo){")
fn('addCartao',"  const primeiraParcela=dueDateFor(new Date(data+'T12:00:00'),vencDia,0);", "  const primeiraParcela=dueDateFor(new Date(data+'T12:00:00'),vencDia,0,card.closeDay);")
fn('addCartao',"  const registro={id:editingCartaoId||Date.now(),data,desc,tipo,val,parcelas:n,vencDia,cardId:","  if(editingCartaoId&&S.extrato.some(x=>String(x.cardId)===String(card.id)&&x.faturaMes)){\n    alert('Este cartão já possui pagamento vinculado. Não altere compras sem antes reconciliar os pagamentos.');return;\n  }\n  const registro={id:editingCartaoId||novoIdGlobal(),data,desc,tipo,val,parcelas:n,vencDia,closeDay:card.closeDay,cardId:")
fn('editCartao',"  if(!item)return;", "  if(!item)return;\n  if(S.extrato.some(x=>String(x.cardId)===String(item.cardId)&&x.faturaMes)){alert('Cartão com pagamento vinculado: edição bloqueada para preservar a conciliação.');return;}")
fn('delCC',"function delCC(id){S.cartao=S.cartao.filter(x=>x.id!==id);", "function delCC(id){const item=S.cartao.find(x=>x.id===id);if(item&&S.extrato.some(x=>String(x.cardId)===String(item.cardId)&&x.faturaMes)){alert('Há pagamento vinculado a este cartão. Concilie a fatura antes de excluir compras.');return;}S.cartao=S.cartao.filter(x=>x.id!==id);")

fn('getMesMap',"    const parc=c.val/n;", "    // Valores inteiros em centavos evitam perder ou criar dinheiro nas parcelas.")
fn('getMesMap',"      const venc=dueDateFor(d,vencDia,i);", "      const parc=valorParcela(c,i);\n      const venc=dueDateFor(d,vencDia,i,c.closeDay);")
fn('getParcelasCartao',"    const parc=c.val/n;", "    // Cada parcela recebe centavos exatos.")
fn('getParcelasCartao',"      const venc=dueDateFor(d,vencDia,i);", "      const parc=valorParcela(c,i);\n      const venc=dueDateFor(d,vencDia,i,c.closeDay);")
fn('getParcelasCartao',"        id:c.id+'-'+i,", "        id:c.id+'-'+i,cardId:c.cardId,")
fn('cartaoTemMes',"dueDateFor(d,vencDia,i)","dueDateFor(d,vencDia,i,c.closeDay)")
fn('renderCartao',"      const label=r.tipo==='parcelado'?`${r.parcelas}x de ${fmt(r.val/r.parcelas)}`:fmt(r.val);", "      const label=r.tipo==='parcelado'?`${r.parcelas} parcelas (aprox. ${fmt(valorParcela(r,0))})`:fmt(r.val);")
fn('renderCartao',"  const wrap=document.getElementById('cc-wrap');", '''  const faturas=document.getElementById('cc-faturas');
  faturas.innerHTML=S.cartoes.length?S.cartoes.map(card=>{
    const total=totalDaFatura(card.id,nowKey),pago=pagoNaFatura(card.id,nowKey);
    const aberto=Math.max(0,total-pago);
    return `<div class="plain-card" style="margin:0 0 8px"><strong>${escHtml(card.bank)} · ${monthLabel}</strong>
      <span>Fatura: ${fmt(total/100)} · Pago: ${fmt(pago/100)} · Em aberto: ${fmt(aberto/100)}</span>
      ${card.closeDay?'':'<span>Fechamento não definido: vencimentos são estimativas. Configure o fechamento do cartão.</span>'}
      ${aberto>0?`<button class="btn-green" type="button" onclick="registrarPagamentoFatura(${card.id},'${nowKey}')">Registrar pagamento</button>`:'<span>Sem valor pendente.</span>'}</div>`;
  }).join(''):'<div class="hint">Cadastre um cartão para acompanhar faturas e pagamentos.</div>';
  const wrap=document.getElementById('cc-wrap');''')

fn('addInvest',"  const inicial=isCrypto?(valorAtualCrypto||investido):investido;", "  const inicial=isCrypto?(valorAtualCrypto||investido):investido;\n  if(!valorMonetarioValido(investido)||investido<0||!valorMonetarioValido(inicial)){alert('Informe valores monetários não negativos, com até duas casas decimais.');return;}")
fn('addInvest',"  const item={id:Date.now(),kind:'investimento'", "  const item={id:novoIdGlobal(),kind:'investimento'")
fn('addInvest',"    item.historico.push({id:item.id+'-inicial',tipo:'aporte',data:today(),valor:inicial||investido,saldo:inicial||investido,origem:'saldo_inicial',cryptoQtd:cryptoQtd||null,cryptoCotacao:cryptoCotacao||null,cryptoPrecoMedio:cryptoPrecoMedio||null,cryptoInvestido:investido||null});", "    const custo=isCrypto&&investido>0?investido:inicial;\n    item.historico.push({id:item.id+'-inicial',tipo:'aporte',data:today(),valor:custo,saldo:custo,origem:'saldo_inicial',cryptoQtd:cryptoQtd||null,cryptoCotacao:cryptoCotacao||null,cryptoPrecoMedio:cryptoPrecoMedio||null,cryptoInvestido:investido||null});\n    if(isCrypto&&inicial!==custo)item.historico.push({id:item.id+'-mercado',tipo:'atualizacao',data:today(),valor:inicial,saldo:inicial});")
fn('addMeta',"S.invest.push({id:Date.now(),kind:'meta'", "S.invest.push({id:novoIdGlobal(),kind:'meta'")

fn('saveInvestAporte',"  if(isNaN(val)||val<=0){", "  if(data>today()||!valorMonetarioValido(val)||val<=0){")
fn('saveInvestResgate',"  if(isNaN(val)||val<=0){alert('Informe o valor do resgate.');return;}\n  const resgate=Math.min(val,item.valorAtual);", "  if(data>today()||!valorMonetarioValido(val)||val<=0){alert('Informe um resgate válido, até a data de hoje.');return;}\n  const livre=item.kind==='investimento'?Math.max(0,Math.round((item.valorAtual-reservadoEmMetas(item.id))*100)/100):item.valorAtual;\n  if(val>livre+0.000001){alert('Resgate maior que o saldo livre. O dinheiro reservado em metas deve ser resgatado pela própria meta.');return;}\n  const resgate=val;")
fn('saveInvestUpdate',"  const data=document.getElementById('update-data-'+id).value||today();", "  const data=document.getElementById('update-data-'+id).value||today();\n  if(data>today()){alert('Atualizações de patrimônio futuro não são permitidas.');return;}")
fn('saveInvestUpdate',"  const valorAnterior=Number(item.valorAtual||0);", "  if(!valorMonetarioValido(val)){alert('Valor inválido: informe no máximo duas casas decimais.');return;}\n  const valorAnterior=Number(item.valorAtual||0);")
fn('delInv',"  const hist=ensureInvestHistory(item);", "  if(S.extrato.some(x=>String(x.destId)===String(id))){alert('Existem lançamentos financeiros vinculados. Preserve o histórico: resgate o saldo e mantenha o cadastro, em vez de excluí-lo.');return;}\n  if(item.kind==='investimento'&&S.invest.some(x=>x.kind==='meta'&&String(x.storageId)===String(id))){alert('Existem metas vinculadas. Remova ou realoque as metas antes de excluir o investimento.');return;}\n  const hist=ensureInvestHistory(item);")

fn('renderAnnualSummary',"const entradas=S.extrato.filter(x=>x.tipo==='entrada'&&x.subcategoria!=='Dinheiro do mês passado'&&isSameMonthDate(x.data,viewYear,m))", "const entradas=S.extrato.filter(x=>receitaReal(x)&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,m))")
fn('renderAnnualSummary',"const saidas=S.extrato.filter(x=>x.tipo==='saida'&&isSameMonthDate(x.data,viewYear,m))", "const resgates=S.extrato.filter(x=>x.tipo==='entrada'&&x.categoria==='Resgate'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,m)).reduce((s,x)=>s+x.val,0);\n    const saidas=S.extrato.filter(x=>x.tipo==='saida'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,m))")
fn('renderAnnualSummary',"const invest=S.extrato.filter(x=>x.tipo==='investimento'&&isSameMonthDate(x.data,viewYear,m))", "const invest=S.extrato.filter(x=>x.tipo==='investimento'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,m))")
fn('renderAnnualSummary',"const metas=S.extrato.filter(x=>x.tipo==='meta'&&isSameMonthDate(x.data,viewYear,m))", "const metas=S.extrato.filter(x=>x.tipo==='meta'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,m))")
fn('renderAnnualSummary',"const saldo=entradas-saidas-(S.saldoInicial?0:cartao)-invest-metas;", "const anoMes=monthKey(viewYear,m);\n    const depoisAbertura=S.saldoInicial&&anoMes>=S.saldoInicial.data.slice(0,7);\n    const saldo=entradas+resgates-saidas-(depoisAbertura?0:cartao)-invest-metas;")
fn('renderAnnualSummary',"{key:'saldo',label:'Sobrou'", "{key:'saldo',label:'Variação caixa'")
fn('renderAnnualSummary',"${economizado>=0?'economizou':'faltou'}: ${fmt(Math.abs(economizado))}","Variação dos lançamentos: ${fmt(economizado)}")

fn('updateResumo',"const entradas=S.extrato.filter(x=>x.tipo==='entrada'&&isSameMonthDate(x.data,viewYear,viewMonth))", "const entradas=S.extrato.filter(x=>receitaReal(x)&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,viewMonth))")
fn('updateResumo',"const saidasDiretas=S.extrato.filter(x=>x.tipo==='saida'&&isSameMonthDate(x.data,viewYear,viewMonth))", "const resgates=S.extrato.filter(x=>x.tipo==='entrada'&&x.categoria==='Resgate'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,viewMonth)).reduce((t,x)=>t+x.val,0);\n  const saidasDiretas=S.extrato.filter(x=>x.tipo==='saida'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,viewMonth))")
fn('updateResumo',"const investido=S.extrato.filter(x=>x.tipo==='investimento'&&isSameMonthDate(x.data,viewYear,viewMonth))", "const investido=S.extrato.filter(x=>x.tipo==='investimento'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,viewMonth))")
fn('updateResumo',"const metas=S.extrato.filter(x=>x.tipo==='meta'&&isSameMonthDate(x.data,viewYear,viewMonth))", "const metas=S.extrato.filter(x=>x.tipo==='meta'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,viewMonth))")
fn('updateResumo',"const saidas=saidasDiretas+(S.saldoInicial?0:ccMes);\n  const saldoMes=entradas-saidas-investido-metas;", "const depoisAbertura=S.saldoInicial&&nowKey>=S.saldoInicial.data.slice(0,7);\n  const saidas=saidasDiretas+(depoisAbertura?0:ccMes);\n  const saldoMes=entradas+resgates-saidas-investido-metas;")
fn('updateResumo',"  document.getElementById('res-month-label').textContent=monthLabel;", "  document.getElementById('res-month-label').textContent=monthLabel;\n  document.querySelector('.saldo-bar').title='Saldo disponível HOJE, independentemente do mês do resumo.';")
fn('updateResumo',"    if(x.tipo==='entrada')addGroup(entradaCat,x.subcategoria||x.categoria||'Entrada',x.val);", "    if(receitaReal(x)&&movimentoRealizado(x))addGroup(entradaCat,x.subcategoria||x.categoria||'Entrada',x.val);")
fn('updateResumo',"    if(x.tipo==='saida')addGroup(saidaCat,x.subcategoria||x.categoria||'Saída',x.val);", "    if(x.tipo==='saida'&&movimentoRealizado(x))addGroup(saidaCat,x.subcategoria||x.categoria||'Saída',x.val);")
fn('updateResumo',"${resumoGeral}: ${fmt(Math.abs(saldoMes))}","Variação do caixa: ${fmt(saldoMes)}")
fn('updateResumo',"S.extrato.filter(x=>x.tipo==='investimento'&&isSameMonthDate(x.data,viewYear,viewMonth)).forEach", "S.extrato.filter(x=>x.tipo==='investimento'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,viewMonth)).forEach")
fn('updateResumo',"S.extrato.filter(x=>x.tipo==='meta'&&isSameMonthDate(x.data,viewYear,viewMonth)).forEach", "S.extrato.filter(x=>x.tipo==='meta'&&movimentoRealizado(x)&&isSameMonthDate(x.data,viewYear,viewMonth)).forEach")

p.write_text(s,encoding='utf-8')
print('PATCH_FINANCEIRO_OK')

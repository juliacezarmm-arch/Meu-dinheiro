from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
def one(a,b):
 global s
 count=s.count(a)
 assert count==1, f'Trecho esperado uma vez, encontrado {count}: {a[:110]!r}'
 s=s.replace(a,b,1)

# Ajuste pontual de contraste e largura para a nova coluna.
one('.app{max-width:820px;margin:0 auto;padding:1rem 0}', '.app{max-width:870px;margin:0 auto;padding:1rem 0}')
one('.green{color:#0F6E56}.red{color:#A32D2D}.blue{color:#185FA5}.amber{color:#633806}', '.green{color:#0F6E56}.red{color:#A32D2D}.blue{color:#185FA5}.amber{color:#633806}\n#cc-mes{color:#f2b75e;font-weight:750}')
one('#cc-wrap .cc-launch-table{min-width:720px}', '#cc-wrap .cc-launch-table{min-width:820px}')
one('#cc-wrap .cc-installments{text-align:center;font-weight:700}', '#cc-wrap .cc-installments{text-align:center;font-weight:700}\n#cc-wrap .cc-paid{text-align:center;white-space:nowrap;overflow:visible}\n#cc-wrap .cc-paid-button{color:#a8eed0;background:#21372f;border:1px solid #4b806c;border-radius:7px;padding:5px 7px;min-width:42px;font:700 11px var(--font-sans);cursor:pointer;white-space:nowrap}\n#cc-wrap .cc-paid-button:hover,#cc-wrap .cc-paid-button:focus-visible{border-color:#9FE1CB;background:#2d4a3d;outline:1px solid #9FE1CB}')

# Diálogo do aplicativo: quantidade informativa, nunca lançamento de pagamento.
anchor='<div id="card-payment-editor" class="site-dialog"'
assert s.count(anchor)==1
modal='''<div id="card-paid-editor" class="site-dialog" role="dialog" aria-modal="true" aria-labelledby="card-paid-title" hidden><div class="site-dialog-panel">
  <div class="site-dialog-heading"><span class="site-dialog-icon" aria-hidden="true">✓</span><h2 id="card-paid-title">Parcelas pagas</h2></div>
  <p class="site-dialog-copy" id="card-paid-description"></p>
  <form id="card-paid-form" novalidate onsubmit="event.preventDefault();salvarParcelasPagas()">
  <label class="site-field">Quantidade já paga<input id="card-paid-count" type="number" inputmode="numeric" min="0" max="120" step="1" required></label>
  <p class="site-dialog-copy">Este número acompanha o progresso da compra. Não registra pagamento nem modifica o saldo. Para registrar a saída de dinheiro, marque a fatura como paga no Extrato.</p>
  <div class="site-dialog-actions"><button class="site-button quiet" type="button" onclick="fecharJanela('card-paid-editor')">Cancelar</button><button class="site-button primary" type="submit">Salvar progresso</button></div></form>
</div></div>
'''
s=s.replace(anchor,modal+anchor,1)
one('let pagamentoEmEdicao=null;\nlet extratoResumoAberto=false;', 'let pagamentoEmEdicao=null;\nlet parcelasPagasEmEdicao=null;\nlet extratoResumoAberto=false;')
one("if(id==='card-payment-editor')pagamentoEmEdicao=null;", "if(id==='card-payment-editor')pagamentoEmEdicao=null;if(id==='card-paid-editor')parcelasPagasEmEdicao=null;")
one("for(const id of ['card-editor','card-payment-editor'])", "for(const id of ['card-editor','card-payment-editor','card-paid-editor'])")

# Compatibilidade com JSON antigo: campo opcional, inteiro e limitado à compra.
one("if(key==='cartao'&&(!Number.isInteger(Number(r.parcelas||1))||Number(r.parcelas||1)<1||Number(r.parcelas||1)>120))throw Error('Parcelamento inválido.');", "if(key==='cartao'&&(!Number.isInteger(Number(r.parcelas||1))||Number(r.parcelas||1)<1||Number(r.parcelas||1)>120))throw Error('Parcelamento inválido.');\n      if(key==='cartao'&&r.parcelasPagasInformadas!==undefined&&(!Number.isInteger(r.parcelasPagasInformadas)||r.parcelasPagasInformadas<0||r.parcelasPagasInformadas>Number(r.parcelas||1)))throw Error('Quantidade de parcelas pagas inválida.');")

# Cálculo separado do saldo: apenas confirma automaticamente parcelas cuja fatura foi integralmente paga.
anchor='function renderCartao(){'
assert s.count(anchor)==1
logic='''// Pagamento da fatura integral confirma suas parcelas; pagamento parcial nao indica
// quais compras foram quitadas. Parcelas historicas sem registro podem ser informadas.
// Este indicador nao altera o valor das faturas nem o saldo.
function parcelasPagasPorFaturas(compra,base){
  const n=Number(compra.parcelas)||1;
  let pagas=Math.max(0,Math.min(n,base));
  for(let i=pagas;i<n;i++){
    const venc=vencimentoDaCompra(compra,i);
    const mes=isoDate(venc.getFullYear(),venc.getMonth(),venc.getDate()).slice(0,7);
    const total=totalDaFatura(compra.cardId,mes);
    const pago=S.extrato.filter(x=>x.tipo==='saida'&&String(x.cardId)===String(compra.cardId)&&x.faturaMes===mes&&x.data&&x.data<=today())
      .reduce((centavos,x)=>centavos+Math.round(Number(x.val||0)*100),0);
    if(total<=0||pago<total)break;
    pagas++;
  }
  return pagas;
}
function parcelasPagasConfirmadas(compra){
  const informado=Number.isInteger(compra.parcelasPagasInformadas)?compra.parcelasPagasInformadas:0;
  return parcelasPagasPorFaturas(compra,informado);
}
function editarParcelasPagas(id){
  const compra=S.cartao.find(x=>String(x.id)===String(id));
  if(!compra||compra.tipo!=='parcelado')return;
  parcelasPagasEmEdicao=compra.id;
  const campo=document.getElementById('card-paid-count');
  const n=Number(compra.parcelas)||1;
  campo.max=String(n);
  campo.value=String(parcelasPagasConfirmadas(compra));
  document.getElementById('card-paid-description').textContent=compra.desc+' · '+n+' parcelas. Informe quantas ja foram pagas, inclusive antes do inicio do controle.';
  abrirJanela('card-paid-editor');
}
function salvarParcelasPagas(){
  const compra=S.cartao.find(x=>String(x.id)===String(parcelasPagasEmEdicao));
  if(!compra)return;
  const campo=document.getElementById('card-paid-count');
  const numero=Number(campo.value);
  const n=Number(compra.parcelas)||1;
  if(campo.value.trim()===''||!Number.isInteger(numero)||numero<0||numero>n){appAlert('Informe um numero inteiro de 0 a '+n+'.');return;}
  const minimo=parcelasPagasPorFaturas(compra,0);
  if(numero<minimo){appAlert('Ja existem '+minimo+' parcelas confirmadas por faturas pagas.');return;}
  compra.parcelasPagasInformadas=numero;
  saveData();
  fecharJanela('card-paid-editor');
  renderCartao();
}

'''
s=s.replace(anchor,logic+anchor,1)
one('''<th style="width:55px">Parcelas</th><th style="width:105px">Valor da parcela</th>''','''<th style="width:55px">Parcelas</th><th style="width:60px">Pagas</th><th style="width:105px">Valor da parcela</th>''')
one('''<td class="cc-installments">${parcelado?qtdParcelas+'x':'—'}</td><td class="cc-money">${valorDaParcela}</td>''','''<td class="cc-installments">${parcelado?qtdParcelas+'x':'—'}</td><td class="cc-paid">${parcelado&&!r.previsto?`<button type="button" class="cc-paid-button" onclick="editarParcelasPagas(${r.id})" title="Ajustar quantidade de parcelas pagas. Nao altera saldo nem registra pagamentos.">${parcelasPagasConfirmadas(r)}/${qtdParcelas}</button>`:'—'}</td><td class="cc-money">${valorDaParcela}</td>''')
one('''<th colspan="8" scope="rowgroup">${titulo}</th>''','''<th colspan="9" scope="rowgroup">${titulo}</th>''')
p.write_text(s,encoding='utf-8')
print('PATCH OK: coluna de progresso no cartao, dialogo informativo, validacao opcional de JSON, maior contraste de cc-mes')

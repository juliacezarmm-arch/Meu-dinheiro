from pathlib import Path


def replace_once(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{name}: esperado 1 trecho, encontrado {count}')
    return text.replace(old, new, 1)

html_file=Path('index.html')
html=html_file.read_text(encoding='utf-8')

old='''#cc-wrap .cc-paid-button{color:#a8eed0;background:#21372f;border:1px solid #4b806c;border-radius:7px;padding:5px 7px;min-width:42px;font:700 11px var(--font-sans);cursor:pointer;white-space:nowrap}
#cc-wrap .cc-paid-button:hover,#cc-wrap .cc-paid-button:focus-visible{border-color:#9FE1CB;background:#2d4a3d;outline:1px solid #9FE1CB}'''
new='''#cc-wrap .cc-paid-status{display:inline-block;color:#a8eed0;background:#21372f;border:1px solid #4b806c;border-radius:7px;padding:5px 7px;min-width:42px;font:700 11px var(--font-sans);white-space:nowrap;text-align:center}'''
html=replace_once(html,old,new,'Indicador somente leitura')

old='''@media(max-width:520px){.saldo-setup .row2{grid-template-columns:1fr}}'''
new='''/* Os tres comandos do Extrato compartilham uma linha; cada painel continua embaixo. */
#extrato-action-buttons{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-bottom:10px}
#extrato-action-buttons #saldo-toggle,#extrato-action-buttons .form-toggle,#extrato-action-buttons #rec-toggle{width:100%;min-width:0;min-height:46px;box-sizing:border-box;margin:0;padding:8px 10px;display:flex;align-items:center;justify-content:space-between;gap:5px;background:#171716;color:#f5f5f2;border:1px solid #3a3934;border-radius:11px;font-size:12px;font-weight:750;text-align:left;line-height:1.25;cursor:pointer;overflow-wrap:anywhere}
#extrato-action-buttons #saldo-toggle:hover,#extrato-action-buttons .form-toggle:hover,#extrato-action-buttons #rec-toggle:hover{border-color:#9FE1CB}
#extrato-action-buttons #saldo-toggle span,#extrato-action-buttons .form-toggle span:last-child,#extrato-action-buttons #rec-toggle span{flex:none;font-size:17px;line-height:1;color:#9FE1CB}
#page-extrato #saldo-setup[hidden],#page-extrato #recorrentes-area[hidden]{display:none!important}
#page-extrato #saldo-content{border-top:0}
@media(max-width:520px){.saldo-setup .row2{grid-template-columns:1fr}#extrato-action-buttons{gap:5px}#extrato-action-buttons #saldo-toggle,#extrato-action-buttons .form-toggle,#extrato-action-buttons #rec-toggle{font-size:10px;padding:7px 6px;min-height:50px}}'''
html=replace_once(html,old,new,'Grade de tres botoes')

old='''// Pagamento da fatura integral confirma suas parcelas; pagamento parcial nao indica
// quais compras foram quitadas. Parcelas historicas sem registro podem ser informadas.
// Este indicador nao altera o valor das faturas nem o saldo.'''
new='''// Progresso exclusivamente informativo: historico confirmado na abertura + faturas quitadas.
// Nao presume pagamentos novos pela simples passagem dos meses e nao altera saldo/faturas.'''
html=replace_once(html,old,new,'Comentario de progresso')
old='''function parcelasPagasConfirmadas(compra){
  const informado=Number.isInteger(compra.parcelasPagasInformadas)?compra.parcelasPagasInformadas:0;
  return parcelasPagasPorFaturas(compra,informado);
}'''
new='''function parcelasHistoricasConfirmadas(compra){
  if(!saldoInicialValido(S.saldoInicial)||!dataISOValida(compra.data)||compra.data>=S.saldoInicial.data)return 0;
  const inicio=S.saldoInicial.data;
  const n=Number(compra.parcelas)||1;
  let pagas=0;
  for(let i=0;i<n;i++){
    const venc=vencimentoDaCompra(compra,i);
    if(isoDate(venc.getFullYear(),venc.getMonth(),venc.getDate())<inicio)pagas++;
  }
  // Primeira parcela anterior informada pela usuaria: compras de agosto com
  // primeira fatura em setembro ja foram pagas, mesmo se pagas antecipadamente.
  // Esta excecao so usa o mes fixo de abertura; nao cresce com o calendario.
  if(pagas===0&&compra.data.slice(0,7)<inicio.slice(0,7)){
    const primeira=vencimentoDaCompra(compra,0);
    const mesPrimeira=isoDate(primeira.getFullYear(),primeira.getMonth(),primeira.getDate()).slice(0,7);
    if(mesPrimeira<=inicio.slice(0,7))pagas=1;
  }
  return Math.min(n,pagas);
}
function parcelasPagasConfirmadas(compra){
  const informado=Number.isInteger(compra.parcelasPagasInformadas)?compra.parcelasPagasInformadas:0;
  return parcelasPagasPorFaturas(compra,Math.max(informado,parcelasHistoricasConfirmadas(compra)));
}'''
html=replace_once(html,old,new,'Progresso historico da abertura')
old='''<button type="button" class="cc-paid-button" onclick="editarParcelasPagas(${r.id})" title="Ajustar quantidade de parcelas pagas. Nao altera saldo nem registra pagamentos.">${parcelasPagasConfirmadas(r)}/${qtdParcelas}</button>'''
new='''<span class="cc-paid-status" title="Historico de parcelas ja pagas e faturas quitadas; nao altera saldo.">${parcelasPagasConfirmadas(r)}/${qtdParcelas}</span>'''
html=replace_once(html,old,new,'Coluna pagas sem acao')
html_file.write_text(html,encoding='utf-8')

js_file=Path('js/recorrentes.js')
js=js_file.read_text(encoding='utf-8')
old="""const anchor=document.querySelector('#page-extrato .add-form');anchor.parentNode.insertBefore(section,anchor);
const cardSection=document.createElement('section');"""
new="""const anchor=document.querySelector('#page-extrato .add-form');
const extratoToggle=anchor.previousElementSibling;
if(!extratoToggle||!extratoToggle.classList.contains('form-toggle'))throw Error('Botao Adicionar no extrato ausente');
anchor.parentNode.insertBefore(section,anchor);
const saldoPanel=document.getElementById('saldo-setup');
const saldoToggle=document.getElementById('saldo-toggle');
const controls=document.createElement('div');
controls.id='extrato-action-buttons';
controls.setAttribute('role','group');
controls.setAttribute('aria-label','Comandos do Extrato');
saldoPanel.parentNode.insertBefore(controls,saldoPanel);
controls.append(saldoToggle,extratoToggle,section.querySelector('#rec-toggle'));
section.querySelector('.rec-top').remove();
saldoPanel.hidden=true;
section.hidden=true;
const cardSection=document.createElement('section');"""
js=replace_once(js,old,new,'Alinhar os tres botoes')
old="""function setRecAreaExpanded(expanded){
 $('rec-body').hidden=!expanded;"""
new="""function setRecAreaExpanded(expanded){
 section.hidden=!expanded;
 $('rec-body').hidden=!expanded;"""
js=replace_once(js,old,new,'Painel recorrente recolhivel')
old="""$('rec-start').value=today();recurrenceType();closeRecEditor();renderRecurring();"""
new="""$('rec-start').value=today();recurrenceType();closeRecEditor();setRecAreaExpanded(false);renderRecurring();"""
js=replace_once(js,old,new,'Iniciar com tres botoes compactos')
js_file.write_text(js,encoding='utf-8')

# O teste anterior exigia deliberadamente um botao; a regra agora e somente leitura.
test_path=Path('tests/parcelas-pagas.test.js')
test=test_path.read_text(encoding='utf-8')
test=replace_once(test,"assert(html.includes('>Pagas</th>')&&html.includes('class=\"cc-paid-button\"')&&html.includes('colspan=\"9\"'),'Coluna e agrupamento devem estar sincronizados');","assert(html.includes('>Pagas</th>')&&html.includes('class=\"cc-paid-status\"')&&!html.includes('onclick=\"editarParcelasPagas(${r.id})\"')&&html.includes('colspan=\"9\"'),'Pagas deve ser texto nao clicavel, com agrupamento sincronizado');",'Teste visual de progresso')
test=replace_once(test,"assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[0])'),0,'Nao presumir pago so porque a parcela venceu');","assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[0])'),1,'Hotel pago antes da abertura: 1 de 6, sem clique');",'Teste hotel historico')
test=replace_once(test,"'parcelasPagasPorFaturas','parcelasPagasConfirmadas'","'parcelasPagasPorFaturas','parcelasHistoricasConfirmadas','parcelasPagasConfirmadas'",'Carregar regra historica no teste')
old="""assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[0])'),1,'Permitir historico pago antes da abertura');"""
new="""assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[0])'),1,'Preservar valor historico antigo do JSON');
run(\"S.cartao.push({id:102,cardId:1,data:'2026-08-25',desc:'Panelas',val:774,parcelas:4,vencDia:24,closeDay:null,tipo:'parcelado'})\");
assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[1])'),1,'Compra de agosto com primeira fatura em setembro ja paga, mesmo antecipadamente');
run(\"S.cartao.push({id:103,cardId:1,data:'2026-08-15',desc:'Tenis',val:960,parcelas:10,vencDia:10,closeDay:null,tipo:'parcelado'})\");
assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[2])'),1,'Compra de agosto com vencimento dia 10: 1 de 10');
run(\"S.cartao.push({id:104,cardId:1,data:'2026-09-19',desc:'Compra nova',val:300,parcelas:3,vencDia:10,closeDay:null,tipo:'parcelado'})\");
assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[3])'),0,'Compra depois da abertura so confirma mediante pagamento');
run(\"hoje='2026-10-15'\");
assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[1])'),1,'Passagem do tempo sem pagamento nao soma parcelas');
assert.strictEqual(run('parcelasPagasConfirmadas(S.cartao[3])'),0,'Mes seguinte nao presume pagamento de compra nova');
run(\"hoje='2026-09-20'\");"""
test=replace_once(test,old,new,'Casos historicos e futuros')
test_path.write_text(test,encoding='utf-8')

layout_test=Path('tests/layout-totais.test.js')
s=layout_test.read_text(encoding='utf-8')
old="""console.log('PASS: layout Extrato = Cartao, totais por grupo e geral, centavos exatos e fatura preservada');"""
new="""assert(rec.includes("controls.append(saldoToggle,extratoToggle,section.querySelector('#rec-toggle'))"),'Os tres botoes precisam dividir a mesma linha');
assert(rec.includes('section.hidden=!expanded'),'Conteudo do recorrente precisa ficar abaixo da linha de botoes');
assert(html.includes('grid-template-columns:repeat(3,minmax(0,1fr))'),'Layout deve ter tres colunas');
assert(html.includes('saldoPanel.hidden=true'),'dummy'=== 'never' ? '' : '');
console.log('PASS: tres botoes do Extrato alinhados, totais por grupo e geral, saldo preservado');"""
# Nada de assert ficticio: o painel de saldo e inicializado no script das recorrencias.
new=new.replace("assert(html.includes('saldoPanel.hidden=true'),'dummy'=== 'never' ? '' : '');","assert(rec.includes('saldoPanel.hidden=true'),'Saldo inicial começa recolhido');")
s=replace_once(s,old,new,'Teste dos tres controles')
layout_test.write_text(s,encoding='utf-8')
print('PATCH OK: 3 botoes alinhados; pagas sem clique, historico da abertura e pagamento posterior confirmado')

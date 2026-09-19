"""Atualização pontual e verificável: parcelas anteriores ao saldo inicial só aparecem no Cartão."""
from pathlib import Path
p = Path('index.html')
s = p.read_text(encoding='utf-8-sig')

def once(old, new):
    global s
    n = s.count(old)
    assert n == 1, f'Âncora esperada uma vez, encontrada {n}: {old[:110]!r}'
    s = s.replace(old, new, 1)

def fn(name, old, new, expected=1):
    global s
    key = '\nfunction ' + name + '('
    start = s.index(key)
    end = s.find('\nfunction ', start + len(key))
    if end < 0: end = len(s)
    part = s[start:end]
    n = part.count(old)
    assert n == expected, f'{name}: esperado {expected}, encontrado {n}: {old[:90]!r}'
    s = s[:start] + part.replace(old, new) + s[end:]

once("function receitaReal(x){return x.tipo==='entrada'", """// Data de abertura = marco zero. Parcelas anteriores só aparecem no histórico do Cartão.
function parcelaNoControleFinanceiro(parcela){
  return !saldoInicialValido(S.saldoInicial)||parcela.data>=S.saldoInicial.data;
}
function parcelasCartaoFinanceiras(){
  return getParcelasCartao().filter(parcelaNoControleFinanceiro);
}
function movimentoNoControleFinanceiro(x){
  if(!movimentoRealizado(x))return false;
  if(!saldoInicialValido(S.saldoInicial))return true;
  return x.data>=S.saldoInicial.data&&!S.saldoInicial.idsIgnorados.some(id=>String(id)===String(x.id));
}
function totalDaFaturaFinanceira(cardId,mes){
  return parcelasCartaoFinanceiras().filter(x=>String(x.cardId)===String(cardId)&&x.data.slice(0,7)===mes)
    .reduce((centavos,x)=>centavos+Math.round(Number(x.val)*100),0);
}
function pagoNaFaturaFinanceira(cardId,mes){
  return S.extrato.filter(x=>x.tipo==='saida'&&String(x.cardId)===String(cardId)&&x.faturaMes===mes&&movimentoNoControleFinanceiro(x))
    .reduce((centavos,x)=>centavos+Math.round(Number(x.val)*100),0);
}
function receitaReal(x){return x.tipo==='entrada'""")

fn('getResumoCartaoExtrato', 'const parcelas=getParcelasCartao().filter(', 'const parcelas=parcelasCartaoFinanceiras().filter(')
fn('renderAnnualSummary', 'const parcelas=getParcelasCartao();', 'const parcelas=parcelasCartaoFinanceiras();')
fn('renderAnnualSummary', 'movimentoRealizado(x)', 'movimentoNoControleFinanceiro(x)', expected=5)
fn('renderAnnualSummary', "    const depoisAbertura=S.saldoInicial&&anoMes>=S.saldoInicial.data.slice(0,7);\n    const saldo=entradas+resgates-saidas-(depoisAbertura?0:cartao)-invest-metas;", "    const saldo=entradas+resgates-saidas-(S.saldoInicial?0:cartao)-invest-metas;")
fn('renderExtrato', 'movimentoRealizado(r)', 'movimentoNoControleFinanceiro(r)', expected=5)
fn('renderExtrato', "const avisoSaldo=S.saldoInicial?'<div class=\"hint\">O saldo inicial não é uma entrada. Movimentos anteriores a ele continuam no histórico, mas não afetam seu saldo disponível.</div>':'';", "const avisoSaldo=S.saldoInicial?'<div class=\"hint\">O saldo inicial não é uma entrada. Parcelas anteriores ao início ficam somente na aba Cartão; não entram neste extrato, no resumo ou no saldo disponível.</div>':'';")
fn('renderExtrato', "const color=r.tipo==='saldo_inicial'?'#9FE1CB':r.tipo==='entrada'?'#0F6E56':r.tipo==='cartao'?'#BA7517'", "const color=r.tipo==='saldo_inicial'?'#9FE1CB':r.tipo==='entrada'?'#0F6E56':r.tipo==='cartao'?'#A32D2D'")
fn('renderExtrato', "${fmt(r.val)}</td><td>${action}</td></tr>`;", "${['saida','cartao','investimento','meta'].includes(r.tipo)?'−':r.tipo==='entrada'?'+':''}${fmt(r.val)}</td><td>${action}</td></tr>`;")

fn('updateResumo', 'movimentoRealizado(x)', 'movimentoNoControleFinanceiro(x)', expected=7)
fn('updateResumo', "  const map=getMesMap();\n  const ccMes=map[nowKey]||0;", "  const ccMes=parcelasCartaoFinanceiras().filter(x=>isSameMonthDate(x.data,viewYear,viewMonth)).reduce((t,x)=>t+x.val,0);")
fn('updateResumo', "  const depoisAbertura=S.saldoInicial&&isoDate(viewYear,viewMonth,1).slice(0,7)>=S.saldoInicial.data.slice(0,7);\n  const saidas=saidasDiretas+(depoisAbertura?0:ccMes);", "  const saidas=saidasDiretas+(S.saldoInicial?0:ccMes);")
fn('updateResumo', 'getParcelasCartao().filter(', 'parcelasCartaoFinanceiras().filter(')
fn('updateResumo', "'O cartão só reduz esse valor após lançar o pagamento no extrato.'", "'O cartão só reduz esse valor após lançar o pagamento no extrato.'", expected=1) if False else None

fn('renderCartao', "    const total=totalDaFatura(card.id,faturaKey),pago=pagoNaFatura(card.id,faturaKey);\n    const aberto=Math.max(0,total-pago);\n    const historica=S.saldoInicial&&faturaKey<S.saldoInicial.data.slice(0,7);", "    const total=totalDaFatura(card.id,faturaKey);\n    const vigente=totalDaFaturaFinanceira(card.id,faturaKey);\n    const historico=total-vigente;\n    const pago=pagoNaFaturaFinanceira(card.id,faturaKey);\n    const aberto=Math.max(0,vigente-pago);\n    const historica=!!S.saldoInicial&&total>0&&vigente===0;")
fn('renderCartao', '      <span>Fatura: ${fmt(total/100)} · Pago: ${fmt(pago/100)} · Em aberto: ${fmt(aberto/100)}</span>', "      ${historica?`<span>Histórico do cartão: ${fmt(total/100)}. Valor anterior à abertura; não gera saída nem saldo pendente.</span>`:`<span>Fatura no controle: ${fmt(vigente/100)} · Pago: ${fmt(pago/100)} · Em aberto: ${fmt(aberto/100)}</span>`}\n      ${historico>0&&!historica?`<span>Parcela(s) históricas fora do controle: ${fmt(historico/100)}.</span>`:''}")
fn('renderCartao', "      ${historica?'<span>Fatura anterior à abertura: pagamentos antigos não são conciliados automaticamente.</span>':''}", '')
fn('renderCartao', "  const rows=S.cartao.filter(c=>cartaoTemMes(c,viewYear,viewMonth)).sort((a,b)=>b.data.localeCompare(a.data));", "  const rows=S.cartao.filter(c=>cartaoTemMes(c,viewYear,viewMonth)).sort((a,b)=>b.data.localeCompare(a.data));\n  const parcelasNesteMes=getParcelasCartao().filter(x=>isSameMonthDate(x.data,viewYear,viewMonth));")
fn('renderCartao', "      const cat=`${r.subcategoria||'Sem categoria'}${r.gastoTipo?' · '+(r.gastoTipo==='fixo'?'fixo':'variável'):''}`;", "      const historico=S.saldoInicial&&parcelasNesteMes.some(x=>String(x.id).startsWith(String(r.id)+'-')&&x.data<S.saldoInicial.data);\n      const cat=`${r.subcategoria||'Sem categoria'}${r.gastoTipo?' · '+(r.gastoTipo==='fixo'?'fixo':'variável'):''}${historico?' · Histórico anterior à abertura':''}`;")
fn('registrarPagamentoFatura', "  const total=totalDaFatura(cardId,mes);\n  const restante=total-pagoNaFatura(cardId,mes);", "  const total=totalDaFaturaFinanceira(cardId,mes);\n  if(total<=0){alert('Parcela anterior à abertura: consta somente no histórico do cartão.');return;}\n  const restante=total-pagoNaFaturaFinanceira(cardId,mes);")

assert 'const historica=S.saldoInicial&&faturaKey<S.saldoInicial.data.slice(0,7)' not in s
p.write_text(s,encoding='utf-8')
print('MARCO_ZERO_PATCH_OK')

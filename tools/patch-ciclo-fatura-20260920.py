from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """  const startOffset=closeDay?((baseDate.getDate()>fechamento?1:0)+(dueDay<=closeDay?1:0)):(baseDate.getDate()>dueDay?1:0);"""
new = """  // Sem fechamento informado: regra de planejamento escolhida pela usuária.
  // Todas as compras do mês entram na fatura do mês seguinte, inclusive dia 1 a 10.
  const startOffset=closeDay?((baseDate.getDate()>fechamento?1:0)+(dueDay<=closeDay?1:0)):1;"""
assert s.count(old) == 1, f'regra do vencimento: {s.count(old)} ocorrências'
s = s.replace(old, new, 1)

anchor = 'function getMesMap(){\n'
assert s.count(anchor) == 1, 'função do mapa não encontrada de forma única'
helper = """// Preserva conciliações que já foram efetivamente registradas no JSON.
// Uma parcela da fatura do mês da compra que já recebeu pagamento NÃO deve
// mudar de competência ao atualizar a versão do aplicativo.
function vencimentoDaCompra(c,indice){
  const base=new Date(c.data+'T12:00:00');
  const dia=c.vencDia||10;
  const calculado=dueDateFor(base,dia,indice,c.closeDay);
  if(c.closeDay||c.previsto||base.getDate()>dia)return calculado;
  const mesCompra=c.data.slice(0,7);
  const temPagamentoAnterior=S.extrato.some(x=>x.tipo==='saida'&&String(x.cardId)===String(c.cardId)&&x.faturaMes===mesCompra);
  if(!temPagamentoAnterior)return calculado;
  const mes=new Date(base.getFullYear(),base.getMonth()+indice,1,12);
  return new Date(mes.getFullYear(),mes.getMonth(),Math.min(dia,new Date(mes.getFullYear(),mes.getMonth()+1,0).getDate()),12);
}

"""
s = s.replace(anchor,helper + anchor,1)

old = 'const venc=dueDateFor(d,vencDia,i,c.closeDay);'
assert s.count(old) == 3, f'uso nos 3 cálculos de parcelas: {s.count(old)}'
s = s.replace(old,'const venc=vencimentoDaCompra(c,i);')

old = '  return isSameMonthDate(c.data,y,m);\n}\n\nfunction renderCartao(){'
new = '  // O mês selecionado é o mês de vencimento das parcelas, não o da compra.\n  return false;\n}\n\nfunction renderCartao(){'
assert s.count(old) == 1, 'filtro de compras não encontrado de forma única'
s = s.replace(old,new,1)

# Mantém as datas originais e valores guardados no JSON; recalcula apenas as
# competências das parcelas sem pagamento já conciliado.
assert s.count('function vencimentoDaCompra(c,indice){') == 1
assert s.count('const venc=vencimentoDaCompra(c,i);') == 3
assert 'return isSameMonthDate(c.data,y,m);' not in s
p.write_text(s,encoding='utf-8')
print('PATCH OK: vencimento mês seguinte sem fechamento, lista por fatura, pagamentos já conciliados preservados, JSON inalterado')

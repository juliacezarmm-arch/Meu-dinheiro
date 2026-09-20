from pathlib import Path

html_path=Path('index.html')
html=html_path.read_text(encoding='utf-8')
old='''  // Sem fechamento informado: regra de planejamento escolhida pela usuária.
  // Todas as compras do mês entram na fatura do mês seguinte, inclusive dia 1 a 10.
  const startOffset=closeDay?((baseDate.getDate()>fechamento?1:0)+(dueDay<=closeDay?1:0)):1;'''
new='''  // Regra de planejamento sem fechamento real cadastrado: compras ANTES do
  // dia de vencimento integram a fatura deste mês; no próprio dia ou depois,
  // a cobrança inicia no mês seguinte. Em meses curtos, ajuste o vencimento.
  const ultimoDiaCompra=new Date(baseDate.getFullYear(),baseDate.getMonth()+1,0).getDate();
  const vencimentoNesteMes=Math.min(dueDay,ultimoDiaCompra);
  const startOffset=closeDay?((baseDate.getDate()>fechamento?1:0)+(dueDay<=closeDay?1:0)):(baseDate.getDate()>=vencimentoNesteMes?1:0);'''
assert html.count(old)==1, 'Regra antiga não encontrada ou alterada em paralelo'
html=html.replace(old,new,1)
html_path.write_text(html,encoding='utf-8')

p=Path('tests/ciclo-fatura.test.js')
t=p.read_text(encoding='utf-8')
old='''for(const day of ['01','09','10','11','19','30']){
 assert.strictEqual(run(`dueDateFor(new Date('2026-09-${day}T12:00:00'),10,0,null).toISOString().slice(0,10)`),'2026-10-10',`Compra dia ${day} deve entrar em outubro`);
}'''
new='''for(const day of ['01','02','09']){
 assert.strictEqual(run(`dueDateFor(new Date('2026-09-${day}T12:00:00'),10,0,null).toISOString().slice(0,10)`),'2026-09-10',`Compra dia ${day}, anterior ao dia 10, deve entrar em setembro`);
}
for(const day of ['10','11','19','30']){
 assert.strictEqual(run(`dueDateFor(new Date('2026-09-${day}T12:00:00'),10,0,null).toISOString().slice(0,10)`),'2026-10-10',`Compra dia ${day} deve entrar em outubro`);
}
assert.strictEqual(run("dueDateFor(new Date('2026-10-09T12:00:00'),10,0,null).toISOString().slice(0,10)"),'2026-10-10','Compra de 09/10 entra na fatura de 10/10');
assert.strictEqual(run("dueDateFor(new Date('2026-10-10T12:00:00'),10,0,null).toISOString().slice(0,10)"),'2026-11-10','Compra no próprio dia 10 vai ao mês seguinte');'''
assert t.count(old)==1, 'Teste do ciclo antigo não localizado'
t=t.replace(old,new,1)
repl={
"assert.strictEqual(run(\"getMesMap()['2026-08']\"),undefined,'Não pode sobrar gasto de setembro na fatura de setembro');":"assert.strictEqual(run(\"getMesMap()['2026-08']\"),100,'Compra em 01/09 deve aparecer na fatura de setembro');",
"assert.strictEqual(run(\"getMesMap()['2026-09']\"),280,'Outubro deve reunir primeira parcela de todas as compras de setembro');":"assert.strictEqual(run(\"getMesMap()['2026-09']\"),180,'Outubro recebe somente compras em 10/09 ou depois');",
"assert.strictEqual(run('cartaoTemMes(S.cartao[0],2026,8)'),false,'Compra de setembro não aparece na lista de setembro');":"assert.strictEqual(run('cartaoTemMes(S.cartao[0],2026,8)'),true,'Compra de 01/09 deve aparecer na lista da fatura de setembro');",
"assert.strictEqual(run('cartaoTemMes(S.cartao[0],2026,9)'),true,'Compra aparece na fatura de outubro');":"assert.strictEqual(run('cartaoTemMes(S.cartao[0],2026,9)'),false,'Compra de 01/09 não pode ser exibida outra vez em outubro');",
"assert.strictEqual(run('getResumoCartaoExtrato(2026,9).val'),280,'Extrato de outubro deve ter a fatura prevista correta');":"assert.strictEqual(run('getResumoCartaoExtrato(2026,9).val'),180,'Extrato de outubro deve ter a fatura prevista correta');",
"assert.strictEqual(run('faturasPendentesDoMes(2026,9)[0].val'),280,'Comprometimento do Extrato deve acompanhar a competência');":"assert.strictEqual(run('faturasPendentesDoMes(2026,9)[0].val'),180,'Comprometimento do Extrato deve acompanhar a competência');",
"assert.strictEqual(run('parcelasCartaoFinanceiras().filter(p=>p.cardId===1).length'),5,'Parcelas vencendo depois do marco zero entram no planejamento');":"assert.strictEqual(run('parcelasCartaoFinanceiras().filter(p=>p.cardId===1).length'),4,'Parcelas antes do marco zero são apenas históricas, nunca despesas novas');",
"console.log('PASS: compras do mês vencem no próximo, parcelas sequenciais, filtros, extrato, marco zero e conciliações preservadas');":"console.log('PASS: antes do dia 10 no mês atual, dia 10 em diante no próximo; hotel, parcelas, extrato, marco zero e conciliações');"
}
for a,b in repl.items():
 assert t.count(a)==1, 'Expectativa antiga não localizada: '+a[:88]
 t=t.replace(a,b,1)
anchor='''// JSONs com pagamentos de fatura já conciliados não podem ter a referência reescrita.'''
assert t.count(anchor)==1
hotel='''// Caso reportado: hotel comprado em 02/09 em 6x de R$ 1.348,38,
// primeira parcela histórica em setembro e última em fevereiro, sem debitar
// novamente o saldo inicial de 18/09.
run("S.cartao.push({id:999,cardId:1,data:'2026-09-02',desc:'Hotel - Home green Home',val:1348.38,parcelas:6,vencDia:10,closeDay:null})");
assert.strictEqual(run("getParcelasCartao().find(p=>p.id==='999-0').data"),'2026-09-10','Hotel tem primeira parcela em setembro');
assert.strictEqual(run("getParcelasCartao().find(p=>p.id==='999-5').data"),'2027-02-10','Hotel termina em fevereiro');
assert.strictEqual(run("getParcelasCartao().filter(p=>p.id.startsWith('999-')).reduce((s,p)=>s+Math.round(p.val*100),0)"),134838,'Nenhum centavo pode ser perdido nas seis parcelas');
assert.strictEqual(run('cartaoTemMes(S.cartao.find(c=>c.id===999),2026,8)'),true,'Hotel precisa aparecer em Setembro no Cartão');
assert.strictEqual(run('cartaoTemMes(S.cartao.find(c=>c.id===999),2027,2)'),false,'Hotel não pode aparecer após fevereiro');
assert.strictEqual(run("getMesMap()['2026-08']"),324.73,'Comprometimento histórico de setembro deve incluir hotel');
assert.strictEqual(run('getResumoCartaoExtrato(2026,8)'),null,'Hotel pago antes da abertura aparece só no histórico do cartão');
assert.strictEqual(run("getResumoCartaoExtrato(2026,9).val"),404.73,'Outubro deve conter somente segunda parcela do hotel, não a primeira');
'''
t=t.replace(anchor,hotel+anchor,1)
p.write_text(t,encoding='utf-8')
print('PATCH OK: compras antes do dia 10 no mês, hotel Setembro-Fevereiro; JSON intocado')
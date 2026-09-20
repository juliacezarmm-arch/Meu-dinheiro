from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: esperado um trecho, encontrados {count}')
    return text.replace(old, new, 1)


p = Path('js/recorrentes.js')
s = p.read_text(encoding='utf-8')
s = replace_once(s,
    '// Dia do cartão é uma regra mensal, não uma data histórica arbitrária.',
    '// Dia do mês é uma regra mensal tanto para a conta quanto para o cartão.', 'comentário')
s = replace_once(s,
    "r.metodo==='cartao'?r.diaCobranca:null",
    "r.frequencia==='mensal'?r.diaCobranca:null", 'gerador mensal para todos')
s = replace_once(s,
    'A data da primeira ocorrência define quando a movimentação entra no Extrato. Antes do saldo inicial, nada é descontado. O aplicativo não consulta bancos: confira o valor e a data efetivos.',
    'Informe o dia da cobrança ou do recebimento. A movimentação é programada a partir de hoje. Confira se o pagamento ou recebimento realmente ocorreu.',
    'texto inicial da conta')
old_timing = '''function recurrenceTiming(){
 const mensalCartao=editingRecMode==='cartao'&&$('rec-frequency').value==='mensal';
 $('rec-day-label').hidden=!mensalCartao;$('rec-date-label').hidden=mensalCartao;
 $('rec-day').required=mensalCartao;$('rec-start').required=!mensalCartao;
 $('rec-date-label').firstChild.textContent=editingRecMode==='cartao'?'Data da cobrança inicial':'Data da primeira ocorrência';
 $('rec-guidance').textContent=mensalCartao?'Informe apenas o dia do mês (1 a 31). A próxima cobrança será programada a partir de hoje; meses curtos usam o último dia. O pagamento da fatura é separado.':editingRecMode==='cartao'?'Para frequência semanal ou anual, informe a data da próxima cobrança. O vencimento e o pagamento da fatura são separados.':'A data da primeira ocorrência define quando a movimentação entra no Extrato. Antes do saldo inicial, nada é descontado. O aplicativo não consulta bancos: confira o valor e a data efetivos.';
}'''
new_timing = '''function recurrenceTiming(){
 const mensal=$('rec-frequency').value==='mensal';
 const recebimento=editingRecMode==='conta'&&$('rec-type').value==='entrada';
 $('rec-day-label').hidden=!mensal;$('rec-date-label').hidden=mensal;
 $('rec-day').required=mensal;$('rec-start').required=!mensal;
 $('rec-day-label').firstChild.textContent=recebimento?'Dia do recebimento':'Dia da cobrança';
 $('rec-date-label').firstChild.textContent=recebimento?'Data do próximo recebimento':'Data da próxima cobrança';
 $('rec-guidance').textContent=mensal?(editingRecMode==='cartao'?'Informe apenas o dia do mês (1 a 31). A próxima cobrança será programada a partir de hoje; meses curtos usam o último dia. O pagamento da fatura é separado.':'Informe apenas o dia do mês (1 a 31). O próximo lançamento será programado a partir de hoje; meses curtos usam o último dia. O aplicativo não consulta bancos: confira se a movimentação ocorreu.'):(editingRecMode==='cartao'?'Para frequência semanal ou anual, informe a data da próxima cobrança. O vencimento e o pagamento da fatura são separados.':'Para frequência semanal ou anual, informe a data do próximo pagamento ou recebimento. O aplicativo não consulta bancos: confira a movimentação efetiva.');
}'''
s = replace_once(s,old_timing,new_timing,'interface mensal Extrato/Cartão')
s = replace_once(s,
    "$('rec-day').value=r&&r.metodo==='cartao'&&r.frequencia==='mensal'?String(r.diaCobranca||Number(r.inicio.slice(8))):'';",
    "$('rec-day').value=r&&r.frequencia==='mensal'?String(r.diaCobranca||Number(r.inicio.slice(8))):'';", 'editar agenda mensal antiga')
s = replace_once(s,
    "r.metodo==='cartao'&&r.frequencia==='mensal'?'Dia da cobrança: '+(r.diaCobranca||Number(r.inicio.slice(8))):'Início: '+displayDate(r.inicio)",
    "r.frequencia==='mensal'?(r.tipo==='entrada'?'Dia do recebimento: ':'Dia da cobrança: ')+(r.diaCobranca||Number(r.inicio.slice(8))):'Próxima programação desde: '+displayDate(r.inicio)", 'resumo por dia')
s = replace_once(s,
    "const mensalCartao=metodo==='cartao'&&frequencia==='mensal';",
    "const mensal=frequencia==='mensal';", 'modo mensal do cadastro')
s = replace_once(s,
    "const diaCobranca=mensalCartao?Number($('rec-day').value):null;",
    "const diaCobranca=mensal?Number($('rec-day').value):null;", 'dia mensal para a conta')
s = replace_once(s,
    " if(mensalCartao){",
    " if(mensal){", 'agendar desde hoje')
s = replace_once(s,
    "appAlert('Informe um dia da cobrança entre 1 e 31.');",
    "appAlert('Informe o dia do mês entre 1 e 31.');", 'alerta dia válido')
s = replace_once(s,
    "...(mensalCartao?{diaCobranca}:{})",
    "...(mensal?{diaCobranca}:{})", 'JSON dia mensal')
s = replace_once(s,
    "||r.metodo!=='cartao'||r.frequencia!=='mensal'",
    "||r.frequencia!=='mensal'", 'JSON aceita conta mensal')
p.write_text(s,encoding='utf-8')

p = Path('index.html')
h = p.read_text(encoding='utf-8')
h = replace_once(h,
    '<script src="js/recorrentes.js?v=20260920-dia1"></script>',
    '<script src="js/recorrentes.js?v=20260920-dia2"></script>', 'cache do JavaScript')
p.write_text(h,encoding='utf-8')

p = Path('tests/recorrentes.test.js')
t = p.read_text(encoding='utf-8')
t = replace_once(t,
    'js/recorrentes.js?v=20260920-dia1',
    'js/recorrentes.js?v=20260920-dia2', 'teste cache')
t = replace_once(t,
    "assert.deepStrictEqual(Array.from(datasRecorrentes({metodo:'cartao',inicio:'2026-02-28',diaCobranca:31,frequencia:'mensal'},'2026-04-30')),['2026-02-28','2026-03-31','2026-04-30'],'O dia 31 deve voltar no mês seguinte');",
    """assert.deepStrictEqual(Array.from(datasRecorrentes({metodo:'cartao',inicio:'2026-02-28',diaCobranca:31,frequencia:'mensal'},'2026-04-30')),['2026-02-28','2026-03-31','2026-04-30'],'O dia 31 deve voltar no mês seguinte');
assert.deepStrictEqual(Array.from(datasRecorrentes({metodo:'debito_automatico',inicio:'2026-10-10',diaCobranca:10,frequencia:'mensal'},'2026-12-31')),['2026-10-10','2026-11-10','2026-12-10'],'O Extrato precisa usar o dia mensal');
assert.deepStrictEqual(Array.from(datasRecorrentes({metodo:'recebimento',inicio:'2026-02-28',diaCobranca:31,frequencia:'mensal'},'2026-04-30')),['2026-02-28','2026-03-31','2026-04-30'],'Recebimento mantém dia original após fevereiro');
assert(js.includes("const mensal=$('rec-frequency').value==='mensal'"),'Formulário mensal deve funcionar no Extrato e no Cartão');
assert(!js.includes('Data da primeira ocorrência'),'Rótulo antigo não deve aparecer');""", 'teste mensal conta e cartão')
p.write_text(t,encoding='utf-8')

p = Path('tests/recorrentes-browser-smoke.py')
b = p.read_text(encoding='utf-8')
b = replace_once(b,
    'js/recorrentes.js?v=20260920-conta2',
    'js/recorrentes.js?v=20260920-dia2', 'smoke script atualizado')
b = replace_once(b,
    "el('rec-frequency').value='mensal';el('rec-start').value=today();",
    "el('rec-frequency').value='mensal';el('rec-frequency').dispatchEvent(new Event('change'));el('rec-day').value=String(Number(today().slice(8)));\n if(el('rec-day-label').hidden||!el('rec-date-label').hidden)throw Error('Dia do mês não aparece no Extrato');\n if(el('rec-day-label').textContent.indexOf('Dia do recebimento')<0)throw Error('Rótulo de recebimento incorreto');",
    'teste navegador Extrato mensal')
p.write_text(b,encoding='utf-8')
print('PATCH OK: dia mensal na conta e cartão; JSON antigo aceito; armazenamento preservado')
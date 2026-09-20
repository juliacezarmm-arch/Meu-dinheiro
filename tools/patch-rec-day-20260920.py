from pathlib import Path


def replace_once(text, old, new, label):
    occurrences = text.count(old)
    if occurrences != 1:
        raise SystemExit(f'{label}: esperado 1 trecho, encontrados {occurrences}')
    return text.replace(old, new, 1)


path = Path('js/recorrentes.js')
s = path.read_text(encoding='utf-8')
s = replace_once(s,
    'function proximaDataRecorrente(inicio,frequencia,indice){',
    'function proximaDataRecorrente(inicio,frequencia,indice,diaDoMes=null){', 'argumento do dia')
s = replace_once(s,
    '    d.setFullYear(mes.getFullYear(),mes.getMonth(),Math.min(d.getDate(),new Date(mes.getFullYear(),mes.getMonth()+1,0).getDate()));',
    '    const dia=Number.isInteger(diaDoMes)&&diaDoMes>=1&&diaDoMes<=31?diaDoMes:d.getDate();\n    d.setFullYear(mes.getFullYear(),mes.getMonth(),Math.min(dia,new Date(mes.getFullYear(),mes.getMonth()+1,0).getDate()));', 'dia fixo mensal')
s = replace_once(s,
    'function datasRecorrentes(r,ate){',
    '''// Dia do cartão é uma regra mensal, não uma data histórica arbitrária.
function proximaCobrancaMensal(referencia,dia){
  if(!dataISOValida(referencia)||!Number.isInteger(dia)||dia<1||dia>31)throw Error('Dia da cobrança inválido');
  const base=new Date(referencia+'T12:00:00');
  const candidata=isoDate(base.getFullYear(),base.getMonth(),Math.min(dia,new Date(base.getFullYear(),base.getMonth()+1,0).getDate()));
  if(candidata>=referencia)return candidata;
  const mes=new Date(base.getFullYear(),base.getMonth()+1,1,12);
  return isoDate(mes.getFullYear(),mes.getMonth(),Math.min(dia,new Date(mes.getFullYear(),mes.getMonth()+1,0).getDate()));
}
function datasRecorrentes(r,ate){''', 'primeira cobrança')
s = replace_once(s,
    'const data=proximaDataRecorrente(r.inicio,r.frequencia,i);',
    "const data=proximaDataRecorrente(r.inicio,r.frequencia,i,r.metodo==='cartao'?r.diaCobranca:null);", 'ocorrências mensais')
s = replace_once(s,
    'module.exports={proximaDataRecorrente,datasRecorrentes};',
    'module.exports={proximaDataRecorrente,proximaCobrancaMensal,datasRecorrentes};', 'exports')
s = replace_once(s,
    '<label>Data da primeira ocorrência<input id="rec-start" type="date" required></label>',
    '<label id="rec-date-label">Data da primeira ocorrência<input id="rec-start" type="date" required></label><label id="rec-day-label" hidden>Dia da cobrança<input id="rec-day" type="number" min="1" max="31" step="1" inputmode="numeric" placeholder="10" aria-describedby="rec-guidance"></label>', 'campos de data')
s = replace_once(s,
    " placeCardRow();\n recurrenceCategories();\n}\nfunction openRecEditor",
    " placeCardRow();\n recurrenceCategories();recurrenceTiming();\n}\nfunction recurrenceTiming(){\n const mensalCartao=editingRecMode==='cartao'&&$('rec-frequency').value==='mensal';\n $('rec-day-label').hidden=!mensalCartao;$('rec-date-label').hidden=mensalCartao;\n $('rec-day').required=mensalCartao;$('rec-start').required=!mensalCartao;\n $('rec-date-label').firstChild.textContent=editingRecMode==='cartao'?'Data da cobrança inicial':'Data da primeira ocorrência';\n $('rec-guidance').textContent=mensalCartao?'Informe apenas o dia do mês (1 a 31). A próxima cobrança será programada a partir de hoje; meses curtos usam o último dia. O pagamento da fatura é separado.':editingRecMode==='cartao'?'Para frequência semanal ou anual, informe a data da próxima cobrança. O vencimento e o pagamento da fatura são separados.':'A data da primeira ocorrência define quando a movimentação entra no Extrato. Antes do saldo inicial, nada é descontado. O aplicativo não consulta bancos: confira o valor e a data efetivos.';\n}\nfunction openRecEditor", 'modo de dia')
s = replace_once(s,
    " $('rec-frequency').value=r?r.frequencia:'mensal';$('rec-start').value=r?r.inicio:today();\n $('rec-guidance').textContent=editingRecMode==='cartao'?'Data da primeira ocorrência = dia da cobrança no cartão. O vencimento da fatura é separado. Compras futuras são previsões e cobranças anteriores à abertura ficam só no histórico do cartão.':'A data da primeira ocorrência define quando a movimentação entra no Extrato. Antes do saldo inicial, nada é descontado. O aplicativo não consulta bancos: confira o valor e a data efetivos.';",
    " $('rec-frequency').value=r?r.frequencia:'mensal';$('rec-start').value=r?r.inicio:today();\n $('rec-day').value=r&&r.metodo==='cartao'&&r.frequencia==='mensal'?String(r.diaCobranca||Number(r.inicio.slice(8))):'';\n recurrenceTiming();", 'abertura do editor')
s = replace_once(s,
    " const inicio=$('rec-start').value,fim=existing?existing.fim||null:null,frequencia=$('rec-frequency').value,categoria=$('rec-category').value,subcategoria=$('rec-subcategory').value;\n if(!nome||!valorMonetarioValido(valor)||valor<=0||!dataISOValida(inicio)||fim&&!dataISOValida(fim)||fim&&fim<=inicio||!['semanal','mensal','anual'].includes(frequencia)||!['entrada','saida'].includes(tipo)||!categoria||!subcategoria){appAlert('Preencha descrição, valor, categoria e datas válidas.');return;}",
    " let inicio=$('rec-start').value;const fim=existing?existing.fim||null:null,frequencia=$('rec-frequency').value,categoria=$('rec-category').value,subcategoria=$('rec-subcategory').value;\n const mensalCartao=metodo==='cartao'&&frequencia==='mensal';\n const diaCobranca=mensalCartao?Number($('rec-day').value):null;\n if(mensalCartao){\n  if($('rec-day').value.trim()===''||!Number.isInteger(diaCobranca)||diaCobranca<1||diaCobranca>31){appAlert('Informe um dia da cobrança entre 1 e 31.');return;}\n  inicio=proximaCobrancaMensal(existing?datePlusOne(today()):today(),diaCobranca);\n }\n if(!nome||!valorMonetarioValido(valor)||valor<=0||!dataISOValida(inicio)||fim&&!dataISOValida(fim)||fim&&fim<=inicio||!['semanal','mensal','anual'].includes(frequencia)||!['entrada','saida'].includes(tipo)||!categoria||!subcategoria){appAlert('Preencha descrição, valor, categoria e datas válidas.');return;}", 'salvamento do dia')
s = replace_once(s,
    'cartaoId,inicio,fim,frequencia,categoria,subcategoria,excluida:false};',
    'cartaoId,inicio,fim,frequencia,categoria,subcategoria,excluida:false,...(mensalCartao?{diaCobranca}:{})};', 'persistência dia')
s = replace_once(s,
    '<br>Início: ${displayDate(r.inicio)}${r.fim?',
    "<br>${r.metodo==='cartao'&&r.frequencia==='mensal'?'Dia da cobrança: '+(r.diaCobranca||Number(r.inicio.slice(8))):'Início: '+displayDate(r.inicio)}${r.fim?", 'listagem dia')
s = replace_once(s,
    "||r.vigenteDesde&&!dataISOValida(r.vigenteDesde))throw Error('Recorrência inválida no arquivo.');",
    "||r.vigenteDesde&&!dataISOValida(r.vigenteDesde)||r.diaCobranca!==undefined&&r.diaCobranca!==null&&(!Number.isInteger(r.diaCobranca)||r.diaCobranca<1||r.diaCobranca>31||r.metodo!=='cartao'||r.frequencia!=='mensal'))throw Error('Recorrência inválida no arquivo.');", 'validação JSON')
s = replace_once(s,
    "$('rec-category').addEventListener('change',recurrenceSubcategories);",
    "$('rec-category').addEventListener('change',recurrenceSubcategories);\n$('rec-frequency').addEventListener('change',recurrenceTiming);", 'alternar frequência')
path.write_text(s,encoding='utf-8')

p = Path('tests/recorrentes.test.js')
t = p.read_text(encoding='utf-8')
t = replace_once(t,
    'const {proximaDataRecorrente,datasRecorrentes}=ctx.module.exports;',
    'const {proximaDataRecorrente,proximaCobrancaMensal,datasRecorrentes}=ctx.module.exports;', 'test export')
t = replace_once(t,
    "assert.strictEqual(proximaDataRecorrente('2024-02-29','anual',1),'2025-02-28');",
    """assert.strictEqual(proximaDataRecorrente('2024-02-29','anual',1),'2025-02-28');
assert.strictEqual(proximaCobrancaMensal('2026-09-20',10),'2026-10-10','Dia 10 após 20/09 deve começar em 10/10');
assert.strictEqual(proximaCobrancaMensal('2026-09-10',10),'2026-09-10','Cobrança de hoje pode ocorrer hoje');
assert.strictEqual(proximaCobrancaMensal('2026-02-15',31),'2026-02-28','Mês curto usa último dia');
assert.deepStrictEqual(Array.from(datasRecorrentes({metodo:'cartao',inicio:'2026-02-28',diaCobranca:31,frequencia:'mensal'},'2026-04-30')),['2026-02-28','2026-03-31','2026-04-30'],'O dia 31 deve voltar no mês seguinte');
assert(js.includes('id=\\\"rec-day\\\"')&&js.includes('recurrenceTiming()'),'Formulário mensal do cartão deve pedir somente dia');""", 'regressões datas')
p.write_text(t,encoding='utf-8')
print('PATCH OK: dia de cobrança, histórico e testes adicionados; armazenamento intocado')

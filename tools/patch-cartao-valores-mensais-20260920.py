from pathlib import Path


def replace_once(source, before, after, label):
    found = source.count(before)
    if found != 1:
        raise AssertionError(f'{label}: esperado um trecho exato, encontrado {found}')
    return source.replace(before, after, 1)


path = Path('index.html')
html = path.read_text(encoding='utf-8')
html = replace_once(html, '#cc-wrap .cc-launch-table{min-width:820px}', '#cc-wrap .cc-launch-table{min-width:690px}', 'largura da tabela')
html = replace_once(html,
    '// Somatorio de valores integrais das compras visiveis, em centavos.\n// Nao e o valor devido na fatura (que utiliza somente as parcelas do mes).\nfunction somarValoresTotaisCartao(itens){\n  return itens.reduce((centavos,item)=>centavos+Math.round(Number(item.val||0)*100),0)/100;\n}',
    '// A tabela mostra apenas o valor que pertence ao mes da fatura selecionada.\n// O valor total da compra permanece no JSON e o historico pode aparecer na lista.\nfunction valorCartaoNoMes(item,parcelasNesteMes){\n  const parcela=parcelasNesteMes.find(x=>String(x.id).startsWith(String(item.id)+\'-\'));\n  return parcela?Number(parcela.val):null;\n}\nfunction somarValoresCartaoNoMes(itens,parcelasNesteMes){\n  return itens.reduce((centavos,item)=>{\n    const valor=valorCartaoNoMes(item,parcelasNesteMes);\n    return centavos+(valor===null?0:Math.round(valor*100));\n  },0)/100;\n}', 'calculo dos subtotais do mes')
html = replace_once(html,
    '<th style="width:55px">Parcelas</th><th style="width:60px">Pagas</th><th style="width:105px">Valor da parcela</th><th style="width:105px">Valor total</th>',
    '<th style="width:75px">Parcelas</th><th style="width:110px">Valor</th>', 'cabecalho unico valor e parcelas')
html = replace_once(html, '        const label=fmt(r.val);\n        const qtdParcelas=', '        const qtdParcelas=', 'valor integral da linha')
html = replace_once(html,
    "        const valorDaParcela=parcelado?fmt(parcelaDoMes?parcelaDoMes.val:valorParcela(r,0)):'—';",
    "        const valorDoMes=parcelaDoMes?fmt(parcelaDoMes.val):'—';", 'valor correto da linha')
html = replace_once(html,
    '<td class="cc-installments">${parcelado?qtdParcelas+\'x\':\'—\'}</td><td class="cc-paid">${parcelado&&!r.previsto?`<span class="cc-paid-status" title="Historico de parcelas ja pagas e faturas quitadas; nao altera saldo.">${parcelasPagasConfirmadas(r)}/${qtdParcelas}</span>`:\'—\'}</td><td class="cc-money">${valorDaParcela}</td><td class="cc-money">${label}</td><td class="cc-actions">${actions}</td>',
    '<td class="cc-installments">${parcelado&&!r.previsto?`<span class="cc-paid-status" title="Parcelas quitadas / parcelas totais; não altera saldo.">${parcelasPagasConfirmadas(r)}/${qtdParcelas}</span>`:\'—\'}</td><td class="cc-money">${valorDoMes}</td><td class="cc-actions">${actions}</td>', 'unir indicador em parcelas e valores')
html = replace_once(html, '      const subtotal=somarValoresTotaisCartao(itens);', '      const subtotal=somarValoresCartaoNoMes(itens,parcelasNesteMes);', 'subtotal por mes')
html = replace_once(html,
    'return `<tr class="cc-group-title"><th colspan="9" scope="rowgroup">${titulo}</th></tr>`+linhas+',
    'return `<tr class="cc-group-title"><th colspan="7" scope="rowgroup">${titulo}</th></tr>`+linhas+', 'cabecalho dos grupos')
html = replace_once(html,
    '<tr class="cc-group-subtotal"><td colspan="7">Subtotal ${titulo} · valor integral das compras</td><td class="cc-money">${fmt(subtotal)}</td><td></td></tr>',
    '<tr class="cc-group-subtotal"><td colspan="5">Subtotal ${titulo} · valores do mês</td><td class="cc-money">${fmt(subtotal)}</td><td></td></tr>', 'subtotais mensais')
html = replace_once(html,
    '<tr class="cc-grand-total"><td colspan="7">Total dos valores integrais exibidos · não é a fatura do mês</td><td class="cc-money">${fmt(somarValoresTotaisCartao(rows))}</td><td></td></tr>',
    '<tr class="cc-grand-total"><td colspan="5">Total exibido neste mês · pode incluir histórico</td><td class="cc-money">${fmt(somarValoresCartaoNoMes(rows,parcelasNesteMes))}</td><td></td></tr>', 'total exibido no mes')
assert '<th style="width:60px">Pagas</th>' not in html
assert 'somarValoresTotaisCartao' not in html
path.write_text(html,encoding='utf-8')

path = Path('tests/layout-totais.test.js')
js = '''const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const rec=fs.readFileSync('js/recorrentes.js','utf8');
const script=html.match(/<script\\s*>([\\s\\S]*?)<\\/script>/);
assert(script,'Script principal ausente');
const source=script[1];
const start=source.indexOf('function valorCartaoNoMes(');
const end=source.indexOf('\\nfunction renderCartao(',start);
assert(start>=0&&end>start,'Calculo mensal isolado ausente');
const ctx=vm.createContext({Number,Math,String});
vm.runInContext(source.slice(start,end),ctx);
const sum=(items,parc)=>vm.runInContext('somarValoresCartaoNoMes('+JSON.stringify(items)+','+JSON.stringify(parc)+')',ctx);
const vista=[{id:1,val:80},{id:2,val:19.99}];
const parceladas=[{id:3,val:1348.38,parcelas:6},{id:4,val:180,parcelas:2}];
const mensal=[{id:'1-0',val:80},{id:'2-0',val:19.99},{id:'3-0',val:224.73},{id:'4-0',val:90}];
assert.strictEqual(sum(vista,mensal),99.99,'À vista usa o valor do mes');
assert.strictEqual(sum(parceladas,mensal),314.73,'Parcelamento usa parcela de 224,73 e 90, nao as compras integrais');
assert.strictEqual(sum(vista.concat(parceladas),mensal),414.72,'Total geral soma somente a coluna Valor');
const mesSeguinte=[{id:'3-1',val:224.73},{id:'4-1',val:90}];
assert.strictEqual(sum(parceladas,mesSeguinte),314.73,'Mes seguinte considera segunda parcela');
assert.strictEqual(sum(vista,mesSeguinte),0,'Nao repetir compras à vista em outros meses');
assert.strictEqual(sum([{id:30,val:100,parcelas:3}],[{id:'30-1',val:33.33}]),33.33,'Preservar centavos individuais da parcela');
assert(html.includes('<th style="width:75px">Parcelas</th><th style="width:110px">Valor</th>'),'Exatamente as colunas Parcelas e Valor');
assert(!html.includes('>Pagas</th>')&&!html.includes('>Valor total</th>')&&!html.includes('>Valor da parcela</th>'),'Remover colunas redundantes');
assert(!html.includes("qtdParcelas+'x'"),'Quadradinho substitui a antiga quantidade 6x');
assert(html.includes('class="cc-paid-status"')&&html.includes('colspan="7"'),'Progresso informativo permanece na coluna Parcelas');
assert(html.includes('Subtotal ${titulo} · valores do mês'),'Subtotais calculados sobre valor do mes');
assert(html.includes('Total exibido neste mês · pode incluir histórico'),'Total da tabela distingue historico da fatura');
assert(!html.includes('somarValoresTotaisCartao('),'Nao somar preco integral das compras');
const bodyStart=rec.indexOf('function renderRecurring(){'),bodyEnd=rec.indexOf('function saveRecEditor(',bodyStart);
assert(bodyStart>=0&&bodyEnd>bodyStart,'Renderizacao dos recorrentes ausente');
const body=rec.slice(bodyStart,bodyEnd);
assert(!body.includes('<div class="rec-item-bottom">'),'Extrato ainda tem terceira linha desnecessaria');
assert(body.split('<span class="rec-inline-actions">').length>=3,'Botoes no cabecalho de ambas as listas');
assert(body.includes('Dia do recebimento: ')&&body.includes('Dia da cobrança: '),'Distinguir entradas e saidas');
assert(rec.includes('#rec-list .rec-item{padding:8px 10px}')&&rec.includes('#rec-card-list .rec-item{padding:8px 10px}'),'Mesmo tamanho compacto');
console.log('PASS: coluna Valor mensal, parcelas em uma coluna, subtotais e total exatos, historico e recorrencia preservados');
'''
path.write_text(js,encoding='utf-8')

path = Path('tests/parcelas-pagas.test.js')
text = path.read_text(encoding='utf-8')
text = replace_once(text,
    "assert(html.includes('>Pagas</th>')&&html.includes('class=\"cc-paid-status\"')&&!html.includes('onclick=\"editarParcelasPagas(${r.id})\"')&&html.includes('colspan=\"9\"'),'Pagas deve ser texto nao clicavel, com agrupamento sincronizado');",
    "assert(html.includes('>Parcelas</th>')&&!html.includes('>Pagas</th>')&&html.includes('class=\"cc-paid-status\"')&&!html.includes('onclick=\"editarParcelasPagas(${r.id})\"')&&html.includes('colspan=\"7\"'),'Progresso exibido na unica coluna Parcelas, sem clique');",
    'teste antigo do indicador')
path.write_text(text,encoding='utf-8')
print('Patch aplicado: 7 colunas, coluna Valor do mes, subtotais mensais e testes atualizados.')

from pathlib import Path


def once(txt,a,b,label):
    n=txt.count(a)
    assert n==1,f'{label}: esperado 1 trecho, encontrados {n}'
    return txt.replace(a,b,1)

p=Path('index.html');s=p.read_text(encoding='utf-8')
s=once(s,
    '#cc-wrap .cc-group-title th{background:#171716;color:#9FE1CB;font-size:11px;font-weight:800;letter-spacing:.02em;padding:10px 7px 6px;border-bottom:1px solid #363631}\n#cc-wrap .cc-group-title:not(:first-child) th{padding-top:16px}\n#cc-wrap .cc-group-subtotal td,#cc-wrap .cc-grand-total td{font-size:11px;overflow:visible;text-overflow:clip;white-space:normal;background:#171716;border-bottom:1px solid #3a3934;padding:8px 5px}\n#cc-wrap .cc-group-subtotal td:first-child,#cc-wrap .cc-grand-total td:first-child{text-align:right;padding-right:10px;color:#c5c3ba}\n#cc-wrap .cc-group-subtotal td.cc-money,#cc-wrap .cc-grand-total td.cc-money{white-space:nowrap;color:#9FE1CB;font-weight:800;text-align:left}\n#cc-wrap .cc-grand-total td{border-top:1px solid #7abfa6;background:#202a25}',
    '#cc-wrap .cc-group-title th{background:transparent;color:#9FE1CB;font-size:11px;font-weight:800;letter-spacing:.02em;padding:9px 5px 6px;border-bottom:1px solid #363631}\n#cc-wrap .cc-group-title:not(:first-child) th{padding-top:15px}\n#cc-wrap .cc-group-title th:first-child{text-align:left}\n#cc-wrap .cc-group-title th.cc-money{text-align:left;font-variant-numeric:tabular-nums;white-space:nowrap;color:#9FE1CB}\n#page-cartao .cc-launch-title{display:flex;align-items:center;justify-content:space-between;gap:8px}\n#page-cartao .cc-launch-title #cc-total-display{color:#9FE1CB;font-size:12px;font-weight:800;white-space:nowrap;font-variant-numeric:tabular-nums}',
    'remover faixas de subtotal e formatar titulo discreto')
s=once(s,
    '<div class="section-title" title="Lista de compras e parcelas do cartão no mês selecionado.">Lançamentos</div>',
    '<div class="section-title cc-launch-title" title="Lista de compras e parcelas do cartão no mês selecionado."><span>Lançamentos</span><span id="cc-total-display" title="Soma dos valores exibidos neste mês, incluindo eventual histórico; não confirma pagamento."></span></div>',
    'total geral no titulo ja existente')
s=once(s,
    "  const parcelasNesteMes=getParcelasCartao().filter(x=>isSameMonthDate(x.data,viewYear,viewMonth));\n  if(!rows.length){wrap.innerHTML='<div class=\"empty\">Nenhum lançamento no cartão em '+monthLabel+'.</div>';return;}",
    "  const parcelasNesteMes=getParcelasCartao().filter(x=>isSameMonthDate(x.data,viewYear,viewMonth));\n  const totalVisivel=somarValoresCartaoNoMes(rows,parcelasNesteMes);\n  document.getElementById('cc-total-display').textContent=rows.length?'Total: '+fmt(totalVisivel):'';\n  if(!rows.length){wrap.innerHTML='<div class=\"empty\">Nenhum lançamento no cartão em '+monthLabel+'.</div>';return;}",
    'total discreto de lancamentos')
s=once(s,
    "      return `<tr class=\"cc-group-title\"><th colspan=\"7\" scope=\"rowgroup\">${titulo}</th></tr>`+linhas+\n        `<tr class=\"cc-group-subtotal\"><td colspan=\"5\">Subtotal ${titulo} · valores do mês</td><td class=\"cc-money\">${fmt(subtotal)}</td><td></td></tr>`;",
    "      return `<tr class=\"cc-group-title\"><th colspan=\"5\" scope=\"rowgroup\">${titulo}</th><th class=\"cc-money\" scope=\"row\">${fmt(subtotal)}</th><th></th></tr>`+linhas;",
    'totais na linha dos titulos')
s=once(s,
    "    }).join('')+\n    `<tr class=\"cc-grand-total\"><td colspan=\"5\">Total exibido neste mês · pode incluir histórico</td><td class=\"cc-money\">${fmt(somarValoresCartaoNoMes(rows,parcelasNesteMes))}</td><td></td></tr>`+\n    '</tbody></table></div>';",
    "    }).join('')+\n    '</tbody></table></div>';",
    'eliminar linha final adicional')
assert 'cc-group-subtotal' not in s and 'cc-grand-total' not in s
p.write_text(s,encoding='utf-8')

p=Path('tests/layout-totais.test.js');s=p.read_text(encoding='utf-8')
s=once(s,
    "assert(html.includes('Subtotal ${titulo} · valores do mês'),'Subtotais calculados sobre valor do mes');\nassert(html.includes('Total exibido neste mês · pode incluir histórico'),'Total da tabela distingue historico da fatura');",
    "assert(html.includes('<th colspan=\\\"5\\\" scope=\\\"rowgroup\\\">${titulo}</th><th class=\\\"cc-money\\\" scope=\\\"row\\\">${fmt(subtotal)}</th>') || html.includes('<th colspan=\"5\" scope=\"rowgroup\">${titulo}</th><th class=\"cc-money\" scope=\"row\">${fmt(subtotal)}</th>'),'Totais na propria linha de cada grupo, alinhados a Valor');\nassert(html.includes('id=\"cc-total-display\"')&&html.includes(\"textContent=rows.length?'Total: '+fmt(totalVisivel):''\"),'Total geral na linha existente de Lancamentos');\nassert(!html.includes('cc-group-subtotal')&&!html.includes('cc-grand-total'),'Nao renderizar linhas nem faixas extras para os totais');",
    'validacao de cabecalhos e total compacto')
s=once(s,
    "console.log('PASS: coluna Valor mensal, parcelas em uma coluna, subtotais e total exatos, historico e recorrencia preservados');",
    "console.log('PASS: Valor mensal, progresso em Parcelas, totais nas linhas dos titulos, sem faixas extras, historico e recorrencia preservados');",
    'mensagem de teste')
p.write_text(s,encoding='utf-8')
print('PASS: totais alinhados aos titulos; faixas e linhas adicionais eliminadas; total geral compacto em Lancamentos.')

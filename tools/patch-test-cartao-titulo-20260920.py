from pathlib import Path
p=Path('tests/layout-totais.test.js');s=p.read_text(encoding='utf-8')
a="assert(html.includes('class=\"cc-paid-status\"')&&html.includes('colspan=\"7\"'),'Progresso informativo permanece na coluna Parcelas');"
b="assert(html.includes('class=\"cc-paid-status\"')&&html.includes('colspan=\"5\"'),'Progresso informativo permanece na coluna Parcelas e totais estao na linha do grupo');"
assert s.count(a)==1,'Teste alterado fora do esperado'
p.write_text(s.replace(a,b,1),encoding='utf-8')
print('Teste atualizado para os totais alinhados em 7 colunas.')

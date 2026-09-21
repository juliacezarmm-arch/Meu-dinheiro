from pathlib import Path
p=Path('tests/parcelas-pagas.test.js');s=p.read_text(encoding='utf-8')
a="html.includes('colspan=\"7\"'),'Progresso exibido na unica coluna Parcelas, sem clique'"
b="html.includes('colspan=\"5\"'),'Progresso exibido na unica coluna Parcelas, sem clique e com total na linha do grupo'"
assert s.count(a)==1,'Teste de parcelas mudou inesperadamente'
p.write_text(s.replace(a,b,1),encoding='utf-8')
print('Teste de parcelas atualizado para totais incorporados aos grupos.')

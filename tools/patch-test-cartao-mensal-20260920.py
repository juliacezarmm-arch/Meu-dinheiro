from pathlib import Path
p=Path('tests/recorrentes.test.js')
s=p.read_text(encoding='utf-8')
a="assert(html.includes('Valor total</th>')&&html.includes('Parcelas</th>'),'Quantidade de parcelas e preço devem ser colunas distintas');"
b="assert(html.includes('>Valor</th>')&&html.includes('>Parcelas</th>')&&!html.includes('Valor total</th>'),'Uma coluna Valor mensal e indicador de parcelas em coluna separada');"
assert s.count(a)==1,'Teste de recorrencia alterado fora do esperado'
p.write_text(s.replace(a,b,1),encoding='utf-8')
print('Teste de recorrencias atualizado para as duas colunas Valor e Parcelas.')

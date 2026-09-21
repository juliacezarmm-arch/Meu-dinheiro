from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
a='title="Dia de vencimento da fatura (1 a 31)."/>\n      </div>\n        <input type="number" id="card-payment-day"'
b='title="Dia de vencimento da fatura (1 a 31)."/>\n        <input type="number" id="card-payment-day"'
assert s.count(a)==1, 'Estrutura do formulario de cadastro inesperada'
s=s.replace(a,b,1)
assert 'id="card-name"' in s and s.count('<div class="row row2">\n        <input type="text" id="card-due-day"')==1
p.write_text(s,encoding='utf-8')
print('PASS: banco/nome e vencimento/pagamento em duas linhas completas sem DIV sobrando')

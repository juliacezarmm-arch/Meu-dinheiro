from pathlib import Path
p=Path('tools/patch-metas-integradas-20260921.py')
s=p.read_text(encoding='utf-8')
old="const meta=parseFloat(document.getElementById('meta-val').value);"
new="const meta=parseFloat(document.getElementById('meta-val').value)||0;"
assert s.count(old)==1, 'Trecho do patch original deve existir somente uma vez'
p.write_text(s.replace(old,new),encoding='utf-8')
print('PASS: padronizado trecho original de metas para atualização segura')
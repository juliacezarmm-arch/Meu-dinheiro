from pathlib import Path
p=Path('tests/recorrentes.test.js');s=p.read_text(encoding='utf-8')
a='assert(html.includes(\'<script src="js/recorrentes.js?v=20260920-trio1"></script>\'),\'Carregamento de recorrências ausente\');'
b='assert(/<script src="js\\/recorrentes\\.js\\?v=[^\"]+"><\\/script>/.test(html),\'Carregamento de recorrências ausente\');'
assert s.count(a)==1,'Teste JS inesperado'
p.write_text(s.replace(a,b,1),encoding='utf-8')
p=Path('tests/recorrentes-browser-smoke.py');s=p.read_text(encoding='utf-8')
a='import os,shutil,subprocess,sys,tempfile\n';b='import os,re,shutil,subprocess,sys,tempfile\n'
assert s.count(a)==1,'Import teste Chrome inesperado';s=s.replace(a,b,1)
a='assert \'<script src="js/recorrentes.js?v=20260920-trio1"></script>\' in html'
b='assert re.search(r\'<script src="js/recorrentes\\.js\\?v=[^\"]+"></script>\',html)'
assert s.count(a)==1,'Teste Chrome inesperado';s=s.replace(a,b,1)
p.write_text(s,encoding='utf-8')
print('PASS: testes de recorrencia aceitam cache buster versionado sem vincular versao especifica')

from pathlib import Path
old='js/recorrentes.js?v=20260920-conta2'
new='js/recorrentes.js?v=20260920-dia1'
for file in ('index.html','tests/recorrentes.test.js'):
    path=Path(file)
    text=path.read_text(encoding='utf-8')
    if text.count(old)!=1:
        raise SystemExit(f'{file}: referência inesperada ({text.count(old)})')
    path.write_text(text.replace(old,new,1),encoding='utf-8')
print('Cache do script atualizado, dados e armazenamento preservados')

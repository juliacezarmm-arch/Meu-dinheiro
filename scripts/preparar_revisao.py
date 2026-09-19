from pathlib import Path
p=Path('scripts/revisao_financeira.py')
s=p.read_text(encoding='utf-8')
old='fn(\'updatePreview\',"dueDateFor(d,vencDia,0)","dueDateFor(d,vencDia,0,card.closeDay)")'
new='fn(\'updatePreview\',"const primeira=dueDateFor(d,vencDia,0);","const primeira=dueDateFor(d,vencDia,0,card.closeDay);")\nfn(\'updatePreview\',"const venc=dueDateFor(d,vencDia,0);","const venc=dueDateFor(d,vencDia,0,card.closeDay);")'
assert s.count(old)==1
p.write_text(s.replace(old,new),encoding='utf-8')
print('ROTEIRO_PREPARADO_OK')

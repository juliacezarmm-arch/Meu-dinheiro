from pathlib import Path

def change(text,old,new,path):
    n=text.count(old)
    if n!=1: raise AssertionError(f'{path}: esperado 1 trecho, encontrado {n}: {old[:90]!r}')
    return text.replace(old,new,1)

p=Path('index.html');s=p.read_text(encoding='utf-8')
s=change(s,"  const subcategorias=S.saldoInicial&&tipo==='entrada'?cadastradas.filter(x=>x!=='Dinheiro do mês passado'):cadastradas;\n  subcategoriaSelect.innerHTML", "  const permitidas=S.saldoInicial&&tipo==='entrada'?cadastradas.filter(x=>x!=='Dinheiro do mês passado'):cadastradas;\n  const subcategorias=permitidas.includes('Outros')?permitidas:[...permitidas,'Outros'];\n  subcategoriaSelect.innerHTML",str(p))
s=change(s,"  const subcategorias=(CATEGORIAS.saida&&CATEGORIAS.saida[categoria])||[];\n  subcategoriaSelect.innerHTML", "  const cadastradas=(CATEGORIAS.saida&&CATEGORIAS.saida[categoria])||[];\n  const subcategorias=cadastradas.includes('Outros')?cadastradas:[...cadastradas,'Outros'];\n  subcategoriaSelect.innerHTML",str(p))
p.write_text(s,encoding='utf-8')

p=Path('js/recorrentes.js');s=p.read_text(encoding='utf-8')
s=change(s," const arr=(CATEGORIAS[$('rec-type').value]||{})[$('rec-category').value]||[];\n subs.innerHTML='<option value=\"\">Escolha a subcategoria</option>'+arr.filter(s=>s!=='Dinheiro do mês passado').map(s=>`<option value=\"${escHtml(s)}\">${escHtml(s)}</option>`).join('');\n if(arr.includes(prev))subs.value=prev;", " const arr=(CATEGORIAS[$('rec-type').value]||{})[$('rec-category').value]||[];\n const permitidas=arr.filter(s=>s!=='Dinheiro do mês passado');\n const opcoes=permitidas.includes('Outros')?permitidas:[...permitidas,'Outros'];\n subs.innerHTML='<option value=\"\">Escolha a subcategoria</option>'+opcoes.map(s=>`<option value=\"${escHtml(s)}\">${escHtml(s)}</option>`).join('');\n if(opcoes.includes(prev))subs.value=prev;",str(p))
p.write_text(s,encoding='utf-8')
print('PASS: acrescentado Outros sem duplicar, no Extrato, Cartão e Recorrências; JSON intacto')

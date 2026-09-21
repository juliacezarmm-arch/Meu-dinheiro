from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def replace_once(old,new):
    global s
    count=s.count(old)
    if count!=1: raise AssertionError(f'Trecho esperado uma vez, encontrado {count}: {old[:95]!r}')
    s=s.replace(old,new,1)
replace_once('function updateSubcategorias(){',"// Toda categoria de entrada ou saída oferece Outros como última subcategoria, sem duplicar.\nfunction subcategoriasComOutros(lista){\n  return [...lista.filter(sub=>sub!=='Outros'),'Outros'];\n}\n\nfunction updateSubcategorias(){")
replace_once("  const subcategorias=S.saldoInicial&&tipo==='entrada'?cadastradas.filter(x=>x!=='Dinheiro do mês passado'):cadastradas;\n  subcategoriaSelect.innerHTML=", "  const permitidas=S.saldoInicial&&tipo==='entrada'?cadastradas.filter(x=>x!=='Dinheiro do mês passado'):cadastradas;\n  const subcategorias=subcategoriasComOutros(permitidas);\n  subcategoriaSelect.innerHTML=")
replace_once("  const subcategorias=(CATEGORIAS.saida&&CATEGORIAS.saida[categoria])||[];\n  subcategoriaSelect.innerHTML=", "  const subcategorias=subcategoriasComOutros((CATEGORIAS.saida&&CATEGORIAS.saida[categoria])||[]);\n  subcategoriaSelect.innerHTML=")
p.write_text(s,encoding='utf-8')
print('PASS: opção Outros na última posição em Extrato e Cartão, sem alterar os lançamentos ou dados persistidos')

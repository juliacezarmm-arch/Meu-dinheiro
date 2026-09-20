from pathlib import Path
p=Path('tests/recorrentes.test.js');s=p.read_text(encoding='utf-8')
a="assert(html.includes('<script src=\"js/recorrentes.js\"></script>'),'Carregamento de recorrências ausente');"
b="assert(html.includes('<script src=\"js/recorrentes.js?v=20260920-conta2\"></script>'),'Carregamento de recorrências ausente');"
assert s.count(a)==1
s=s.replace(a,b)
s=s.replace("assert(js.includes('.rec-form [hidden]{display:none!important}'),'Campos ocultos não podem aparecer pelo CSS');", "assert(js.includes('cardRow.hidden=true;cardRow.remove()'),'Campo de cartão precisa sair fisicamente do formulário da conta');\nassert(!js.includes('id=\\\"rec-end\\\"'),'Encerramento não pertence ao cadastro inicial');\nassert(js.includes('data-recdelete=\\\"${r.id}\\\">Excluir agora'),'Exclusão deve estar na lista dos registros criados');")
p.write_text(s,encoding='utf-8')
print('TEST_PATCH_OK')

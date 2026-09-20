from pathlib import Path
p=Path('js/recorrentes.js')
s=p.read_text(encoding='utf-8')
def change(old,new,count=1):
 global s
 n=s.count(old)
 if n!=count: raise SystemExit(f'Expected {count} occurrences, found {n}: {old[:85]}')
 s=s.replace(old,new)
# Keep the card-only control entirely outside the account editor, not merely hidden.
change("const $=id=>document.getElementById(id);", "const $=id=>document.getElementById(id);\nconst cardRow=$('rec-card-row');\nconst cardSelect=$('rec-card');\ncardRow.hidden=true;cardRow.remove();\nfunction placeCardRow(){\n  if(editingRecMode==='cartao'){\n    $('rec-form').insertBefore(cardRow,$('rec-category').closest('.row'));\n    cardRow.hidden=false;cardRow.style.removeProperty('display');\n  }else{cardRow.hidden=true;cardRow.remove();}\n}")
change("const sel=$('rec-card');const previous=sel.value;", "const sel=cardSelect;const previous=sel.value;")
change("$('rec-card-row').hidden=editingRecMode!=='cartao';", "placeCardRow();",2)
change("cardOptions();$('rec-card').value=r&&r.cartaoId?String(r.cartaoId):'';", "cardOptions();cardSelect.value=r&&r.cartaoId?String(r.cartaoId):'';")
change("function closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';}", "function closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';placeCardRow();$('recorrentes-area').appendChild($('rec-form'));}")
change("$('rec-method').addEventListener('change',()=>{placeCardRow();});", "$('rec-method').addEventListener('change',()=>{placeCardRow();});",0) if False else None
# No hidden card field in the account form; card registration still exists solely in its own Card tab.
change("<label>Onde acontece?<select id=\"rec-method\">", "<label>Forma de movimentação<select id=\"rec-method\">")
change("else if(entrada)sel.innerHTML='<option value=\"recebimento\">Conta / salário</option>';", "else if(entrada)sel.innerHTML='<option value=\"recebimento\">Recebimento / salário</option><option value=\"pix\">Pix recebido</option><option value=\"transferencia\">Transferência recebida</option>';")
change("if(tipo==='entrada'&&metodo!=='recebimento'||tipo==='saida'&&!['cartao','debito_automatico','debito','pix','transferencia'].includes(metodo))", "if(tipo==='entrada'&&!['recebimento','pix','transferencia'].includes(metodo)||tipo==='saida'&&!['cartao','debito_automatico','debito','pix','transferencia'].includes(metodo))")
change("data-recdelete=\"${r.id}\">Excluir</button>", "data-recdelete=\"${r.id}\">Excluir agora</button>")
change("if(!await appConfirm('Excluir '+r.nome+' agora? Os lançamentos anteriores continuarão no histórico e nenhuma ocorrência futura será gerada.'))return;", "if(!await appConfirm('Excluir agora o cadastro de '+r.nome+'? As movimentações já registradas ficam no histórico, mas todas as previsões futuras são removidas.'))return;")
change("$('rec-method').addEventListener('change',()=>{$('rec-card-row').hidden=editingRecMode!=='cartao';});", "$('rec-method').addEventListener('change',placeCardRow);")
# Closed editor must not have stale card controls in the Extrato.
change("$('rec-start').value=today();recurrenceType();renderRecurring();", "$('rec-start').value=today();recurrenceType();closeRecEditor();renderRecurring();")
p.write_text(s,encoding='utf-8')
h=Path('index.html');html=h.read_text(encoding='utf-8')
old='<script src="js/recorrentes.js"></script>'
assert html.count(old)==1
html=html.replace(old,'<script src="js/recorrentes.js?v=20260920-conta2"></script>')
h.write_text(html,encoding='utf-8')
t=Path('tests/recorrentes-browser-smoke.py');test=t.read_text(encoding='utf-8')
test=test.replace("assert '<script src=\"js/recorrentes.js\"></script>' in html", "assert '<script src=\"js/recorrentes.js?v=20260920-conta2\"></script>' in html")
test=test.replace("if(!document.getElementById('rec-card-row').hidden)throw Error('Campo cartão visível no Extrato');", "if(document.querySelector('#rec-form #rec-card-row'))throw Error('Campo cartão ainda está dentro do formulário da conta');\n if(document.getElementById('rec-card-row'))throw Error('Campo cartão não deveria existir no Extrato');")
test=test.replace("if(el('rec-card-row').hidden||el('rec-method').value!=='cartao')", "if(el('rec-card-row').hidden||el('rec-method').value!=='cartao')")
test=test.replace("if(!el('rec-method').closest('label').hidden)throw Error('Forma de pagamento redundante na assinatura');", "if(!el('rec-method').closest('label').hidden)throw Error('Forma de pagamento redundante na assinatura');\n if(el('rec-card-row').parentElement.id!=='rec-form')throw Error('Cartão exclusivo não inserido no formulário da assinatura');")
t.write_text(test,encoding='utf-8')
print('PATCH_CONTA_ONLY_OK')

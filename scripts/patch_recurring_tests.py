from pathlib import Path
p=Path('tests/recorrentes.test.js');s=p.read_text(encoding='utf-8')
def replace_once(old,new):
 global s
 assert s.count(old)==1,(old,s.count(old))
 s=s.replace(old,new,1)
replace_once("'cardForecasts','cashForecastsForMonth','cancelRec','deleteRec','openRecEditor'","'cardForecasts','cashForecastsForMonth','deleteRec','openRecEditor'")
replace_once("console.log('PASS: recorrências mensais, semanais, anuais, fevereiro, cancelamento, edição futura, histórico, interface e validação');", """assert(js.includes('id=\\\"rec-cartao-area\\\"'),'Assinaturas precisam de área própria na aba Cartão');
assert(js.includes('id=\\\"rec-card-open\\\"'),'Botão de assinatura ausente');
assert(js.includes('r.excluida=true;r.fim=today()'),'Excluir deve suspender o futuro e preservar histórico');
assert(!js.includes('id=\\\"rec-end\\\"')&&!js.includes('data-reccancel'),'Campos duplicados de encerramento não devem aparecer');
assert(js.includes('.rec-form [hidden]{display:none!important}'),'Campos ocultos não podem aparecer pelo CSS');
console.log('PASS: recorrências, separação conta/cartão, exclusão prospectiva, histórico e validação');""")
p.write_text(s,encoding='utf-8')
p=Path('tests/recorrentes-browser-smoke.py');s=p.read_text(encoding='utf-8')
def replace_smoke(old,new):
 global s
 assert s.count(old)==1,(old,s.count(old))
 s=s.replace(old,new,1)
replace_smoke("if(!document.getElementById('rec-shortcut'))throw Error('Atalho ausente');", "if(!document.getElementById('rec-card-open'))throw Error('Área própria de assinatura ausente');")
replace_smoke("document.getElementById('rec-open').click();", """document.getElementById('rec-open').click();
 if(document.getElementById('rec-form').parentElement.id!=='recorrentes-area')throw Error('Cadastro da conta fora do Extrato');
 if(Array.from(document.getElementById('rec-method').options).some(o=>o.value==='cartao'))throw Error('Opção cartão apareceu nos débitos da conta');
 if(!document.getElementById('rec-card-row').hidden)throw Error('Campo cartão visível no Extrato');""")
replace_smoke("report(true,'Cadastro, visualização, entrada automática, saldo e idempotência');", """el('rec-card-open').click();
 if(el('rec-form').parentElement.id!=='rec-cartao-area')throw Error('Assinatura não está na aba Cartão');
 if(el('rec-card-row').hidden||el('rec-method').value!=='cartao')throw Error('Assinatura sem seleção exclusiva de cartão');
 if(!el('rec-method').closest('label').hidden)throw Error('Forma de pagamento redundante na assinatura');
 report(true,'Cadastro separado para conta e cartão, entrada automática, saldo e idempotência');""")
replace_smoke("PASS: Cadastro, visualização, entrada automática, saldo e idempotência", "PASS: Cadastro separado para conta e cartão, entrada automática, saldo e idempotência")
replace_smoke("print('PASS: Chrome headless — cadastro, entrada automática, saldo, ausência de duplicidade e navegação')", "print('PASS: Chrome headless — conta e cartão separados, entrada automática, saldo, idempotência')")
p.write_text(s,encoding='utf-8')
print('PATCH_TESTS_ACCOUNT_CARD_OK')

from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
def replace_once(old,new):
 global s
 count=s.count(old)
 assert count==1,(repr(old[:100]),count)
 s=s.replace(old,new,1)
replace_once('</script>\n</body>', '</script>\n<script src="js/recorrentes.js"></script>\n</body>')
replace_once('<div class="row row2" id="ext-saida-row">','<div class="row row1" id="ext-saida-row">')
replace_once('<select id="ext-gasto-tipo" title="Gasto fixo é algo que volta todo mês; variável muda conforme o mês.">','<select id="ext-gasto-tipo" aria-hidden="true" tabindex="-1" style="display:none">')
replace_once('const gastoTipo=document.getElementById(\'ext-gasto-tipo\').value;','const gastoTipo=\'variavel\'; // Lançamentos avulsos dispensam classificação manual.')
replace_once('const gastoTipo=document.getElementById(\'cc-gasto-tipo\').value;','const gastoTipo=\'variavel\'; // Gastos recorrentes têm cadastro próprio.')
replace_once('if(tipo===\'saida\'&&(!gastoTipo||!pagamento))','if(tipo===\'saida\'&&!pagamento)')
replace_once('||!categoria||!subcategoria||!gastoTipo){appAlert(\'Preencha descrição, categoria, subcategoria, tipo de gasto e valor.\');','||!categoria||!subcategoria){appAlert(\'Preencha descrição, categoria, subcategoria e valor.\');')
replace_once('<div class="row row1">\n        <select id="cc-gasto-tipo" title="Marque se esse gasto é fixo ou variável.">','<div class="row row1" style="display:none" aria-hidden="true">\n        <select id="cc-gasto-tipo" tabindex="-1">')
replace_once("${r.gastoTipo?' · '+(r.gastoTipo==='fixo'?'fixo':'variável'):''}", "${r.recorrenciaId?' · Recorrente':''}")
replace_once("const labels=['Adicionar no extrato','Registrar cartão','Adicionar compra no cartão','Cadastrar investimento','Cadastrar meta'];","const labels=['Adicionar no extrato','Registrar cartão','Adicionar compra no cartão','Cadastrar investimento','Cadastrar meta'];") if False else None
p.write_text(s,encoding='utf-8')
print('PATCH_RECORRENTES_UI_OK')

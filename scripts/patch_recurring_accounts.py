from pathlib import Path
import re
p=Path('js/recorrentes.js')
s=p.read_text(encoding='utf-8')
def sub(old,new):
 global s
 count=s.count(old)
 if count!=1: raise AssertionError(f'Esperada uma ocorrência ({count}): {old[:90]}')
 s=s.replace(old,new,1)
def block(pattern,new):
 global s
 s,count=re.subn(pattern,lambda m:new,s,count=1,flags=re.S)
 if count!=1: raise AssertionError('Bloco não encontrado: '+pattern[:100])
sub('let editingRecId=null;','let editingRecId=null;\nlet editingRecMode="conta";')
sub('.rec-form input,.rec-form select{width:100%}', '.rec-form input,.rec-form select{width:100%}.rec-form [hidden]{display:none!important}')
sub('Cadastre uma vez: salário, débito automático e assinatura no cartão. Edite, cancele ou exclua sem perder os lançamentos passados.','Cadastre salário, débito automático, Pix ou transferência. Exclua o cadastro quando quiser; os lançamentos anteriores permanecem.')
sub('<option value="transferencia">Transferência</option><option value="cartao">Cartão de crédito</option></select>', '<option value="transferencia">Transferência</option></select>')
sub('<div class="row row1"><label>Não gerar mais a partir de (opcional)<input id="rec-end" type="date"></label></div>','')
block(r'<p class="rec-caption">A data de início.*?</p>', '<p class="rec-caption" id="rec-guidance">A data da primeira ocorrência define quando a movimentação entra no Extrato. Antes do saldo inicial, nada é descontado. O aplicativo não consulta bancos: confira o valor e a data efetivos.</p>')
block(r"const shortcut=document\.createElement\('div'\);.*?cardAnchor\.parentNode\.insertBefore\(shortcut,cardAnchor\);", '''const cardSection=document.createElement('section');cardSection.id='rec-cartao-area';cardSection.className='rec-area';
cardSection.innerHTML='<div class="rec-top"><div><strong>Assinaturas recorrentes no cartão</strong><p>Cadastre cobranças periódicas do crédito aqui, separadas dos débitos da conta. Excluir interrompe o futuro, mas mantém as cobranças anteriores.</p></div><button type="button" class="rec-button primary" id="rec-card-open">+ Nova assinatura</button></div><div class="rec-list" id="rec-card-list"></div>';
const cardAnchor=document.querySelector('#page-cartao .section-title:nth-of-type(2)')||document.querySelector('#page-cartao #cc-card').closest('.add-form');cardAnchor.parentNode.insertBefore(cardSection,cardAnchor);''')
block(r'function recurrenceType\(\)\{.*?\n\}\n(?=function openRecEditor)', '''function recurrenceType(){
 const entrada=editingRecMode==='conta'&&$('rec-type').value==='entrada',sel=$('rec-method');
 if(editingRecMode==='cartao'){
  $('rec-type').value='saida';sel.innerHTML='<option value="cartao">Cartão de crédito</option>';
 }else if(entrada)sel.innerHTML='<option value="recebimento">Conta / salário</option>';
 else sel.innerHTML='<option value="debito_automatico">Débito automático</option><option value="debito">Débito</option><option value="pix">Pix</option><option value="transferencia">Transferência</option>';
 $('rec-type').closest('label').hidden=editingRecMode==='cartao';
 $('rec-method').closest('label').hidden=editingRecMode==='cartao';
 $('rec-card-row').hidden=editingRecMode!=='cartao';
 recurrenceCategories();
}
''')
block(r'function openRecEditor\(id=null\)\{.*?\n\}\nfunction closeRecEditor\(\)\{.*?\}\n(?=function cardForecasts)', '''function openRecEditor(id=null,mode='conta'){
 const r=S.recorrentes.find(x=>String(x.id)===String(id));editingRecId=r?r.id:null;
 editingRecMode=r?(r.metodo==='cartao'?'cartao':'conta'):mode;
 const area=$(editingRecMode==='cartao'?'rec-cartao-area':'recorrentes-area');
 area.insertBefore($('rec-form'),area.querySelector('.rec-list'));
 $('rec-form').hidden=false;
 $('rec-form-title').textContent=r?'Editar '+(editingRecMode==='cartao'?'assinatura':'registro recorrente'):(editingRecMode==='cartao'?'Nova assinatura recorrente':'Novo registro recorrente');
 $('rec-name').value=r?r.nome:'';$('rec-value').value=r?r.valor:'';
 $('rec-type').value=r?r.tipo:'saida';recurrenceType();
 $('rec-method').value=editingRecMode==='cartao'?'cartao':r?r.metodo:'debito_automatico';
 $('rec-card-row').hidden=editingRecMode!=='cartao';cardOptions();$('rec-card').value=r&&r.cartaoId?String(r.cartaoId):'';
 $('rec-category').value=r?r.categoria:'';recurrenceSubcategories();$('rec-subcategory').value=r?r.subcategoria:'';
 $('rec-frequency').value=r?r.frequencia:'mensal';$('rec-start').value=r?r.inicio:today();
 $('rec-guidance').textContent=editingRecMode==='cartao'?'Data da primeira ocorrência = dia da cobrança no cartão. O vencimento da fatura é separado. Compras futuras são previsões e cobranças anteriores à abertura ficam só no histórico do cartão.':'A data da primeira ocorrência define quando a movimentação entra no Extrato. Antes do saldo inicial, nada é descontado. O aplicativo não consulta bancos: confira o valor e a data efetivos.';
 $('rec-submit').textContent=r?'Salvar alterações':editingRecMode==='cartao'?'Salvar assinatura':'Salvar recorrência';$('rec-form').scrollIntoView({behavior:'smooth',block:'nearest'});$('rec-name').focus();
}
function closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';}
''')
block(r'function renderRecurring\(\)\{.*?\n\}\n(?=function saveRecEditor)', '''function renderRecurring(){
 if(!$('rec-list')||!$('rec-card-list'))return;cardOptions();
 const ativos=S.recorrentes.filter(r=>!r.excluida).slice().sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR'));
 function html(list,empty){
  if(!list.length)return '<div class="rec-caption">'+empty+'</div>';
  return list.map(r=>{
   const next=recurringNext(r),ended=!!r.fim&&r.fim<=today();
   const freq={semanal:'Semanal',mensal:'Mensal',anual:'Anual'}[r.frequencia]||r.frequencia;
   const card=S.cartoes.find(c=>String(c.id)===String(r.cartaoId));
   return `<div class="rec-item"><div class="rec-item-head"><span class="rec-item-name">${escHtml(r.nome)}</span><span class="rec-tag${ended?' inactive':''}">${ended?'Encerrado':r.tipo==='entrada'?'Entrada':'Saída'}</span></div>
    <div class="rec-item-sub"><strong style="color:#f5f5f2">${r.tipo==='saida'?'−':'+'}${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo]||r.metodo)}${card?' ('+escHtml(card.bank)+')':''}<br>Início: ${displayDate(r.inicio)}${r.fim?' · Encerramento anterior: '+displayDate(r.fim):''}${next?' · Próxima: '+displayDate(next):''}</div>
    <div class="rec-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir</button></div></div>`;
  }).join('');
 }
 $('rec-list').innerHTML=html(ativos.filter(r=>r.metodo!=='cartao'),'Nenhum registro recorrente da conta. Cadastre salário, Pix ou débito automático.');
 $('rec-card-list').innerHTML=html(ativos.filter(r=>r.metodo==='cartao'),'Nenhuma assinatura recorrente no cartão.');
}
''')
sub("const inicio=$('rec-start').value,fim=$('rec-end').value||null,frequencia=$('rec-frequency').value,", "const inicio=$('rec-start').value,fim=existing?existing.fim||null:null,frequencia=$('rec-frequency').value,")
sub("appAlert('Preencha descrição, valor, categoria e datas válidas. Encerramento precisa ser posterior ao início.');return;", "appAlert('Preencha descrição, valor, categoria e datas válidas.');return;")
sub("if(metodo==='cartao'&&!S.cartoes.some(c=>String(c.id)===String(cartaoId)))", "if((editingRecMode==='cartao')!==(metodo==='cartao')){appAlert('Escolha a aba correspondente ao registro.');return;}\n if(metodo==='cartao'&&!S.cartoes.some(c=>String(c.id)===String(cartaoId)))")
block(r'async function cancelRec\(id\)\{.*?\n\}\n(?=async function deleteRec)', '')
sub("if(!await appConfirm('Excluir o cadastro de '+r.nome+'? O histórico já lançado permanece; apenas a programação deixa de existir.'))return;", "if(!await appConfirm('Excluir '+r.nome+' agora? Os lançamentos anteriores continuarão no histórico e nenhuma ocorrência futura será gerada.'))return;")
sub("showPage('extrato',document.querySelectorAll('.nav button')[1]);openRecEditor(row.recorrenciaId);", "showPage('cartao',document.querySelectorAll('.nav button')[2]);openRecEditor(row.recorrenciaId);")
sub("$('rec-shortcut').addEventListener('click',()=>{showPage('extrato',document.querySelectorAll('.nav button')[1]);$('recorrentes-area').scrollIntoView({behavior:'smooth',block:'start'});});", "$('rec-card-open').addEventListener('click',()=>openRecEditor(null,'cartao'));")
sub("$('rec-method').addEventListener('change',()=>{$('rec-card-row').hidden=$('rec-method').value!=='cartao';});", "$('rec-method').addEventListener('change',()=>{$('rec-card-row').hidden=editingRecMode!=='cartao';});")
block(r"\$\('rec-list'\)\.addEventListener\('click',event=>\{.*?\n\}\);", """for(const listId of ['rec-list','rec-card-list'])$(listId).addEventListener('click',event=>{
 const btn=event.target.closest('button');if(!btn)return;
 if(btn.dataset.recedit)openRecEditor(btn.dataset.recedit);
 if(btn.dataset.recdelete)void deleteRec(btn.dataset.recdelete);
});""")
sub("if(id==='extrato')renderRecurring();", "if(id==='extrato'||id==='cartao')renderRecurring();")
if 'rec-end' in s or 'rec-shortcut' in s or 'data-reccancel' in s:raise AssertionError('Controle antigo ainda presente')
p.write_text(s,encoding='utf-8')
print('PATCH_ACCOUNT_CARD_SEPARATION_OK')

"""Patch validado com âncoras: vencimento x pagamento, lápis de edição e avisos internos."""
from pathlib import Path
import re
p=Path('index.html'); s=p.read_text(encoding='utf-8')
def rep(old,new,n=1):
 global s
 assert s.count(old)==n,(old[:100],s.count(old),n)
 s=s.replace(old,new)
def block(start,end,new):
 global s
 assert s.count(start)==1 and s.count(end)==1,(start,end)
 a=s.index(start); b=s.index(end,a+len(start)); assert b>a
 s=s[:a]+new.rstrip()+'\n\n'+s[b:]

rep('    <div class="section-title" title="Cadastre aqui os cartões que você usa e o dia de vencimento deles.">Meus cartões</div>','    <div class="section-title" title="Cadastre e edite vencimento e dia habitual de pagamento de seus cartões.">Meus cartões</div>')
rep('      <div class="row row1"><input type="number" id="card-close-day" placeholder="Dia de fechamento da fatura" min="1" max="31" step="1" title="Informe o fechamento informado pelo banco para calcular o mês correto da parcela."/></div>','''      <div class="row row1"><label class="input-caption" for="card-payment-day">Dia habitual do pagamento (opcional)</label><input type="number" id="card-payment-day" placeholder="Ex.: 17, mesmo se vencer dia 10" min="1" max="31" step="1" title="Dia em que você costuma pagar. A data efetiva será escolhida ao registrar cada pagamento."/></div>
      <p class="hint">Vencimento e pagamento são datas diferentes. Você informará a data real quando pagar a fatura. Não é necessário informar fechamento.</p>''')
rep('</div>\n\n<script>','''</div>
<!-- Caixas de diálogo exclusivas do próprio aplicativo. -->
<div id="app-toast" class="site-toast" role="status" aria-live="polite" hidden><span id="app-toast-message"></span><button type="button" onclick="fecharAviso()" aria-label="Dispensar aviso">×</button></div>
<div id="app-confirm-overlay" class="site-dialog" role="dialog" aria-modal="true" aria-labelledby="app-confirm-title" hidden><div class="site-dialog-panel"><div class="site-dialog-heading"><span class="site-dialog-icon" aria-hidden="true">?</span><h2 id="app-confirm-title">Confirmar operação</h2></div><p id="app-confirm-message" class="site-dialog-copy"></p><div class="site-dialog-actions"><button type="button" class="site-button quiet" id="app-confirm-cancel">Cancelar</button><button type="button" class="site-button primary" id="app-confirm-accept">Confirmar</button></div></div></div>
<div id="card-editor" class="site-dialog" role="dialog" aria-modal="true" aria-labelledby="card-editor-title" hidden><div class="site-dialog-panel">
  <div class="site-dialog-heading"><span class="site-dialog-icon" aria-hidden="true">✎</span><h2 id="card-editor-title">Editar cartão</h2></div>
  <p class="site-dialog-copy">Ajuste os dados do cartão. Vencimento e pagamento são datas diferentes.</p>
  <form id="card-editor-form" onsubmit="event.preventDefault();salvarEdicaoCartao()">
  <label class="site-field">Banco / cartão<select id="card-edit-bank" required></select></label>
  <div class="site-fields-row"><label class="site-field">Vencimento (dia)<input id="card-edit-due" type="number" inputmode="numeric" min="1" max="31" step="1" required placeholder="10"></label><label class="site-field">Dia habitual de pagamento<input id="card-edit-payment" type="number" inputmode="numeric" min="1" max="31" step="1" placeholder="17 (opcional)"></label></div>
  <p class="site-dialog-copy">Novos dados valem para compras futuras. Compras anteriores preservam os vencimentos já registrados.</p>
  <div class="site-dialog-actions"><button class="site-button quiet" type="button" onclick="fecharJanela('card-editor')">Cancelar</button><button class="site-button primary" type="submit">Salvar cartão</button></div></form>
</div></div>
<div id="card-payment-editor" class="site-dialog" role="dialog" aria-modal="true" aria-labelledby="card-payment-title" hidden><div class="site-dialog-panel">
  <div class="site-dialog-heading"><span class="site-dialog-icon" aria-hidden="true">$</span><h2 id="card-payment-title">Registrar pagamento</h2></div>
  <p class="site-dialog-copy" id="card-payment-description"></p>
  <form id="card-payment-form" onsubmit="event.preventDefault();salvarPagamentoFatura()">
  <label class="site-field">Valor efetivamente pago (R$)<input id="card-payment-amount" type="number" inputmode="decimal" min="0.01" step="0.01" required></label>
  <label class="site-field">Data em que você pagou<input id="card-payment-date" type="date" required></label>
  <p class="site-dialog-copy">Essa data será a saída no Extrato. O vencimento permanece como referência da fatura, sem duplicar a despesa.</p>
  <div class="site-dialog-actions"><button class="site-button quiet" type="button" onclick="fecharJanela('card-payment-editor')">Cancelar</button><button class="site-button primary" type="submit">Registrar pagamento</button></div></form>
</div></div>
<script>''')
rep('</style>','''/* Interface do site: não usar alert, confirm ou prompt do navegador. */
.site-dialog[hidden],.site-toast[hidden]{display:none!important}
.site-dialog{position:fixed;inset:0;z-index:15000;display:flex;align-items:center;justify-content:center;padding:18px;background:rgba(0,0,0,.78);backdrop-filter:blur(5px)}
.site-dialog-panel{width:min(100%,465px);max-height:min(90vh,720px);overflow:auto;background:#1b1b19;border:1px solid #46463e;border-radius:16px;box-shadow:0 24px 90px rgba(0,0,0,.65);padding:22px;color:#f5f5f2}
.site-dialog-heading{display:flex;align-items:center;gap:11px;margin-bottom:12px}.site-dialog-heading h2{font-size:18px;font-weight:750}.site-dialog-icon{display:inline-grid;place-items:center;width:32px;height:32px;flex:none;border-radius:10px;background:#17392e;color:#9FE1CB;font-size:18px}
.site-dialog-copy{font-size:13px;line-height:1.55;color:#c5c3ba;white-space:pre-line;margin:0 0 15px}
.site-field{display:flex;flex-direction:column;gap:7px;font-size:12px;font-weight:700;color:#e6e3d9;margin:0 0 14px}.site-fields-row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.site-dialog-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:16px}.site-button{border:1px solid #46463e;border-radius:9px;padding:10px 14px;font-size:13px;font-weight:800;cursor:pointer}.site-button.quiet{background:#2a2a28;color:#f5f5f2}.site-button.primary{background:#9FE1CB;border-color:#9FE1CB;color:#0b3329}.site-button:hover{filter:brightness(1.09)}
.site-toast{position:fixed;top:18px;left:50%;transform:translateX(-50%);z-index:20000;display:flex;align-items:center;gap:12px;width:min(94%,480px);background:#1a2924;color:#f5f5f2;border:1px solid #69cda9;border-radius:12px;padding:12px 13px;box-shadow:0 18px 45px rgba(0,0,0,.6);font-size:13px;line-height:1.4}.site-toast span{flex:1}.site-toast button{background:transparent;color:#f5f5f2;border:0;font-size:22px;cursor:pointer}
.input-caption{display:block;font-size:12px;color:#c5c3ba;margin-bottom:5px}.bank-card-actions{position:absolute;right:8px;top:8px;z-index:2;display:flex;gap:5px}.bank-card .bank-card-actions .del{position:static;min-width:28px;min-height:28px;display:inline-flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.35);background:rgba(0,0,0,.25);border-radius:7px;color:#fff;cursor:pointer}.bank-card .bank-card-actions .del:hover{background:rgba(0,0,0,.42);border-color:white}.bank-edit-icon{width:15px;height:15px;display:block}
@media(max-width:520px){.site-dialog-panel{padding:17px}.site-fields-row{grid-template-columns:1fr}.site-dialog-actions button{flex:1}}
</style>''')
rep('let editingCartaoId=null;','let editingCartaoId=null;\nlet editingRegisteredCardId=null;\nlet pagamentoEmEdicao=null;')
rep('function fmt(v){','''function fecharAviso(){clearTimeout(appAlert.timer);document.getElementById('app-toast').hidden=true;}
function appAlert(message){const toast=document.getElementById('app-toast');document.getElementById('app-toast-message').textContent=String(message);toast.hidden=false;clearTimeout(appAlert.timer);appAlert.timer=setTimeout(fecharAviso,6500);}
function abrirJanela(id){const e=document.getElementById(id);if(!e)return;e.hidden=false;const first=e.querySelector('input,select,button');if(first)first.focus();}
function fecharJanela(id){const e=document.getElementById(id);if(e)e.hidden=true;if(id==='card-editor')editingRegisteredCardId=null;if(id==='card-payment-editor')pagamentoEmEdicao=null;}
function appConfirm(message){
 return new Promise(resolve=>{
  const overlay=document.getElementById('app-confirm-overlay'),ok=document.getElementById('app-confirm-accept'),cancel=document.getElementById('app-confirm-cancel'),previous=document.activeElement;
  document.getElementById('app-confirm-message').textContent=String(message);
  function finish(answer){overlay.hidden=true;ok.removeEventListener('click',accept);cancel.removeEventListener('click',reject);document.removeEventListener('keydown',escape);if(previous&&previous.isConnected)previous.focus();resolve(answer);}
  function accept(){finish(true);}function reject(){finish(false);}function escape(event){if(event.key==='Escape'){event.preventDefault();reject();}}
  ok.addEventListener('click',accept);cancel.addEventListener('click',reject);document.addEventListener('keydown',escape);overlay.hidden=false;cancel.focus();
 });
}
document.addEventListener('keydown',event=>{if(event.key!=='Escape'||!document.getElementById('app-confirm-overlay').hidden)return;for(const id of ['card-editor','card-payment-editor'])if(!document.getElementById(id).hidden){fecharJanela(id);break;}});
function fmt(v){''')
for name in ('confirmarSaldoInicial','importData','delInv'):rep('function '+name+'(','async function '+name+'(')
block('function configurarFechamento(id){','function dueDateFor(baseDate,dueDay,offset,closeDay){','''// O fechamento do banco não é a data de pagamento. Editar não reescreve compras antigas.
function editarCartaoCadastrado(id){
 const card=S.cartoes.find(c=>String(c.id)===String(id));if(!card)return;
 editingRegisteredCardId=card.id;
 const select=document.getElementById('card-edit-bank');select.innerHTML=document.getElementById('card-bank').innerHTML;select.value=card.bank;
 document.getElementById('card-edit-due').value=String(card.dueDay||'');document.getElementById('card-edit-payment').value=card.paymentDay?String(card.paymentDay):'';
 abrirJanela('card-editor');
}
function diaDeCartaoValido(valor,obrigatorio){if(!obrigatorio&&(valor===null||valor===undefined||String(valor).trim()===''))return true;const n=Number(valor);return Number.isInteger(n)&&n>=1&&n<=31;}
function salvarEdicaoCartao(){
 const card=S.cartoes.find(c=>String(c.id)===String(editingRegisteredCardId));if(!card)return fecharJanela('card-editor');
 const bank=document.getElementById('card-edit-bank').value,dueText=document.getElementById('card-edit-due').value,paymentText=document.getElementById('card-edit-payment').value;
 if(!bank||!diaDeCartaoValido(dueText,true)||!diaDeCartaoValido(paymentText,false)){appAlert('Escolha o cartão e informe vencimento válido. O pagamento habitual pode ficar vazio.');return;}
 card.bank=bank;card.dueDay=Number(dueText);card.paymentDay=paymentText.trim()===''?null:Number(paymentText);card.closeDay=null;card.color=BANK_COLORS[bank]||BANK_COLORS.Outro;
 fecharJanela('card-editor');saveData();renderRegisteredCards();renderCartao();renderExtrato();updateResumo();appAlert('Cartão atualizado. Histórico e pagamentos já registrados foram preservados.');
}
function registrarPagamentoFatura(cardId,mes){
 if(!saldoInicialValido(S.saldoInicial)){appAlert('Informe primeiro seu saldo inicial no Extrato.');return;}
 const card=S.cartoes.find(x=>String(x.id)===String(cardId));if(!card||!/^\\d{4}-\\d{2}$/.test(mes))return;
 const total=totalDaFaturaFinanceira(cardId,mes),restante=total-pagoNaFaturaFinanceira(cardId,mes);
 if(total<=0){appAlert('Esse valor é apenas histórico do cartão e não gera saída.');return;}
 if(restante<=0){appAlert('Esta fatura não possui valor pendente.');return;}
 pagamentoEmEdicao={cardId:card.id,mes};document.getElementById('card-payment-title').textContent='Pagamento · '+card.bank;
 const habitual=card.paymentDay?' · Você costuma pagar dia '+card.paymentDay+'.':'';
 document.getElementById('card-payment-description').textContent='Fatura '+mes+' · Vencimento dia '+card.dueDay+'.'+habitual+' Restante: '+fmt(restante/100)+'. Escolha a data em que o dinheiro realmente saiu.';
 const amount=document.getElementById('card-payment-amount');amount.value=(restante/100).toFixed(2);amount.max=(restante/100).toFixed(2);
 const date=document.getElementById('card-payment-date');date.value=today();date.min=S.saldoInicial.data;date.max=today();abrirJanela('card-payment-editor');
}
function salvarPagamentoFatura(){
 if(!pagamentoEmEdicao)return;
 const {cardId,mes}=pagamentoEmEdicao,card=S.cartoes.find(x=>String(x.id)===String(cardId));if(!card)return fecharJanela('card-payment-editor');
 const campo=document.getElementById('card-payment-amount'),valor=Number(campo.value),dataPagamento=document.getElementById('card-payment-date').value;
 const restante=totalDaFaturaFinanceira(cardId,mes)-pagoNaFaturaFinanceira(cardId,mes);
 if(campo.value.trim()===''||!valorMonetarioValido(valor)||valor<=0||Math.round(valor*100)>restante){appAlert('Informe o valor realmente pago, sem ultrapassar o restante da fatura.');return;}
 if(!dataISOValida(dataPagamento)||dataPagamento<S.saldoInicial.data||dataPagamento>today()){appAlert('A data do pagamento deve estar entre o início do controle e hoje.');return;}
 const [ano,mesNumero]=mes.split('-').map(Number),ultimoDia=new Date(ano,mesNumero,0).getDate(),vencimentoFatura=mes+'-'+String(Math.min(Number(card.dueDay),ultimoDia)).padStart(2,'0');
 S.extrato.push({id:novoIdExtrato(),data:dataPagamento,desc:'Pagamento de fatura - '+card.bank+' '+mes,tipo:'saida',categoria:'Cartão de crédito',subcategoria:'Pagamento de fatura',gastoTipo:'variavel',pagamento:'transferencia',val:Math.round(valor*100)/100,cardId:card.id,faturaMes:mes,vencimentoFatura});
 fecharJanela('card-payment-editor');saveData();renderCartao();renderExtrato();updateResumo();appAlert('Pagamento registrado na data informada, sem duplicar a despesa.');
}
''')
assert len(re.findall(r'(?<![\w.])confirm\s*\(',s))==4
s=re.sub(r'(?<![\w.])confirm\s*\(','await appConfirm(',s)
s=re.sub(r'(?<![\w.])alert\s*\(','appAlert(',s)
assert not re.search(r'(?<![\w.])(?:prompt|alert|confirm)\s*\(',s)
block('function addRegisteredCard(){','function delRegisteredCard(id){','''function addRegisteredCard(){
 const bank=document.getElementById('card-bank').value,dueText=document.getElementById('card-due-day').value,paymentText=document.getElementById('card-payment-day').value;
 if(!bank||!diaDeCartaoValido(dueText,true)||!diaDeCartaoValido(paymentText,false)){appAlert('Escolha o banco e informe o vencimento (1 a 31). O dia habitual do pagamento é opcional.');return;}
 S.cartoes.push({id:novoIdGlobal(),bank,dueDay:Number(dueText),paymentDay:paymentText.trim()===''?null:Number(paymentText),closeDay:null,color:BANK_COLORS[bank]||BANK_COLORS.Outro});
 document.getElementById('card-bank').value='';document.getElementById('card-due-day').value='';document.getElementById('card-payment-day').value='';
 saveData();renderRegisteredCards();renderCartao();updatePreview();
}
''')
block('function renderRegisteredCards(){','function addGroup(map,label,val){','''function renderRegisteredCards(){
 const wrap=document.getElementById('bank-cards-wrap'),select=document.getElementById('cc-card'),prev=select.value;
 select.innerHTML='<option value="">Escolha o cartão</option>'+S.cartoes.map(c=>`<option value="${c.id}">${escHtml(c.bank)} - vence dia ${c.dueDay}</option>`).join('');
 if(S.cartoes.some(c=>String(c.id)===prev))select.value=prev;
 if(!S.cartoes.length){wrap.innerHTML='<div class="empty">Nenhum cartão cadastrado ainda.</div>';return;}
 wrap.innerHTML='<div class="bank-cards">'+S.cartoes.map(c=>`
 <div class="bank-card" style="background:${c.color};color:#fff">
 <div class="bank-card-actions">
 <button class="del" type="button" onclick="editarCartaoCadastrado(${c.id})" aria-label="Editar cartão ${escHtml(c.bank)}" title="Editar cartão"><svg class="bank-edit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg></button>
 <button class="del" type="button" onclick="delRegisteredCard(${c.id})" aria-label="Remover cartão ${escHtml(c.bank)}" title="Excluir cartão sem movimentações vinculadas">×</button>
 </div><div class="bank-chip"></div><div class="bank-name">${escHtml(c.bank)}</div>
 <div class="bank-due">Vence dia ${c.dueDay}${c.paymentDay?' · Pagamento habitual dia '+c.paymentDay:''}</div>
 </div>`).join('')+'</div>';
}
''')
rep("      ${card.closeDay?'':'<span>Fechamento não definido: vencimentos são estimativas. Configure o fechamento do cartão.</span>'}","      <span>Vencimento padrão: dia ${card.dueDay}${card.paymentDay?' · Pagamento habitual: dia '+card.paymentDay:''}.</span>\n      ${S.extrato.filter(x=>String(x.cardId)===String(card.id)&&x.faturaMes===faturaKey&&movimentoNoControleFinanceiro(x)).length?`<span>Pagamento(s) registrado(s) em: ${S.extrato.filter(x=>String(x.cardId)===String(card.id)&&x.faturaMes===faturaKey&&movimentoNoControleFinanceiro(x)).map(x=>x.data.split('-').reverse().join('/')).join(', ')}.</span>`:''}")
rep("window.addEventListener('beforeunload',function(e){\n  if(!hasUnsavedChanges)return;\n  e.preventDefault();\n  e.returnValue='Você tem alterações sem salvar.';\n});","document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&hasUnsavedChanges&&dataFileHandle)autoSaveDataFile();});")
rep("  setSaveStatus.timer=setTimeout(()=>{el.textContent='';},3000);","  setSaveStatus.timer=setTimeout(()=>{el.textContent=hasUnsavedChanges?'Alterações ainda não salvas. Use Salvar ou Salvar como.':'';},3000);")
assert 'configurarFechamento(' not in s and 'card-close-day' not in s
assert not re.search(r'(?<![\w.])(?:prompt|alert|confirm)\s*\(',s)
assert 'vencimentoFatura' in s and 'data:dataPagamento' in s
p.write_text(s,encoding='utf-8')
print('PATCH_CARD_EDIT_UX_OK')
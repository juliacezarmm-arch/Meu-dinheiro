/* Recorrências: cadastro separado do movimento efetivo. Sem popups nativos. */
function proximaDataRecorrente(inicio,frequencia,indice,diaDoMes=null){
  const d=new Date(inicio+'T12:00:00');
  if(frequencia==='semanal')d.setDate(d.getDate()+7*indice);
  else if(frequencia==='mensal'){
    const mes=new Date(d.getFullYear(),d.getMonth()+indice,1,12);
    const dia=Number.isInteger(diaDoMes)&&diaDoMes>=1&&diaDoMes<=31?diaDoMes:d.getDate();
    d.setFullYear(mes.getFullYear(),mes.getMonth(),Math.min(dia,new Date(mes.getFullYear(),mes.getMonth()+1,0).getDate()));
  }else if(frequencia==='anual'){
    const ano=d.getFullYear()+indice;
    d.setFullYear(ano,d.getMonth(),Math.min(d.getDate(),new Date(ano,d.getMonth()+1,0).getDate()));
  }else throw Error('Frequência inválida');
  return isoDate(d.getFullYear(),d.getMonth(),d.getDate());
}
// Dia do mês é uma regra mensal tanto para a conta quanto para o cartão.
function proximaCobrancaMensal(referencia,dia){
  if(!dataISOValida(referencia)||!Number.isInteger(dia)||dia<1||dia>31)throw Error('Dia da cobrança inválido');
  const base=new Date(referencia+'T12:00:00');
  const candidata=isoDate(base.getFullYear(),base.getMonth(),Math.min(dia,new Date(base.getFullYear(),base.getMonth()+1,0).getDate()));
  if(candidata>=referencia)return candidata;
  const mes=new Date(base.getFullYear(),base.getMonth()+1,1,12);
  return isoDate(mes.getFullYear(),mes.getMonth(),Math.min(dia,new Date(mes.getFullYear(),mes.getMonth()+1,0).getDate()));
}
function datasRecorrentes(r,ate){
  if(!r||!dataISOValida(r.inicio)||!dataISOValida(ate))return [];
  const saida=[];
  for(let i=0;i<1200;i++){
    const data=proximaDataRecorrente(r.inicio,r.frequencia,i,r.frequencia==='mensal'?r.diaCobranca:null);
    if(data>ate||r.fim&&data>=r.fim)break;
    if(data>=String(r.vigenteDesde||r.inicio))saida.push(data);
  }
  return saida;
}
if(typeof module!=='undefined'&&module.exports)module.exports={proximaDataRecorrente,proximaCobrancaMensal,datasRecorrentes};

if(typeof document!=='undefined'){
(function(){
'use strict';
S.recorrentes=Array.isArray(S.recorrentes)?S.recorrentes:[];
S.recorrenciaIgnoradas=Array.isArray(S.recorrenciaIgnoradas)?S.recorrenciaIgnoradas:[];
let editingRecId=null;
let editingRecMode="conta";
const style=document.createElement('style');
style.textContent=`.rec-area{background:#171716;border:1px solid #3a3934;border-radius:14px;padding:14px;margin:0 0 17px}.rec-top{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}.rec-top strong{font-size:15px}.rec-top p,.rec-caption{font-size:12px;color:#c5c3ba;line-height:1.5;margin:6px 0 10px}.rec-button{background:#242423;border:1px solid #5b625b;color:#d9f7ea;border-radius:9px;padding:9px 12px;cursor:pointer;font-size:12px;font-weight:750}.rec-button.primary{background:#1D9E75;color:#fff;border-color:#1D9E75}.rec-button.danger{color:#ffc1bc}.rec-form{margin:13px 0;padding:13px;border:1px solid #3a3934;border-radius:11px;background:#111110}.rec-form[hidden]{display:none}.rec-form label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#c5c3ba}.rec-form .row{margin-bottom:10px}.rec-actions{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:12px}.rec-list{display:flex;flex-direction:column;gap:9px}.rec-item{background:#0f0f0e;border:1px solid #363631;border-radius:11px;padding:12px}.rec-item-head{display:flex;gap:8px;align-items:center;justify-content:space-between}.rec-item-name{font-size:14px;font-weight:750;overflow-wrap:anywhere}.rec-tag{font-size:11px;border-radius:100px;padding:3px 8px;background:#19352a;color:#a0eed0;white-space:nowrap}.rec-tag.inactive{background:#35302b;color:#e6c9b3}.rec-item-sub{font-size:12px;color:#c5c3ba;line-height:1.55;margin-top:6px}.rec-shortcut{display:flex;gap:9px;align-items:center;justify-content:space-between;padding:10px 12px;margin:8px 0;background:#171716;border:1px solid #3a3934;border-radius:10px}.rec-shortcut span{font-size:12px;color:#c5c3ba}.rec-predictions{background:#171716;border:1px solid #3a3934;border-radius:10px;padding:11px;margin:10px 0;font-size:12px}.rec-predictions strong{display:block;color:#9FE1CB;margin-bottom:5px}.rec-prediction{display:flex;justify-content:space-between;gap:12px;padding:5px 0;border-top:1px solid #2b2b28}.rec-prediction small{color:#c5c3ba}.rec-card-prediction{font-size:12px;color:#c5c3ba;padding:5px 0}.rec-form input,.rec-form select{width:100%}#rec-card-toggle{width:100%;display:flex;justify-content:space-between;align-items:center;gap:10px;background:transparent;border:0;color:#f5f5f2;padding:0;text-align:left;font-size:15px;font-weight:750;cursor:pointer}#rec-card-toggle span{font-size:20px;color:#9FE1CB;line-height:1}#rec-card-body[hidden]{display:none!important}#rec-toggle{width:100%;display:flex;justify-content:space-between;align-items:center;gap:10px;background:transparent;border:0;color:#f5f5f2;padding:0;text-align:left;font-size:15px;font-weight:750;cursor:pointer}#rec-toggle span{font-size:20px;color:#9FE1CB;line-height:1}#rec-body[hidden]{display:none!important}.rec-item-bottom{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-top:7px}.rec-item-date{font-size:12px;color:#c5c3ba;line-height:1.45;flex:1 1 225px}.rec-inline-actions{display:flex;align-items:center;gap:5px;flex-wrap:wrap;margin:0}.rec-inline-actions .rec-button{padding:6px 8px;font-size:11px;white-space:nowrap}.rec-form [hidden]{display:none!important}@media(max-width:520px){.rec-form .row2{grid-template-columns:1fr}.rec-shortcut{align-items:flex-start;flex-direction:column}}`;
style.textContent+=`#rec-card-list{gap:6px}#rec-card-list .rec-item{padding:8px 10px}#rec-card-list .rec-item-head{gap:7px;flex-wrap:wrap}#rec-card-list .rec-item-head .rec-inline-actions{margin-left:auto}#rec-card-list .rec-item-sub{margin-top:4px;font-size:11px;line-height:1.4}#rec-card-list .rec-item-date-inline{color:#c5c3ba}#rec-card-list .rec-inline-actions .rec-button{font-size:10px;padding:4px 6px}#rec-card-open{margin:8px 0}#rec-card-list .rec-item-name{min-width:0}@media(max-width:520px){#rec-card-list .rec-item-head{row-gap:5px}#rec-card-list .rec-item-head .rec-inline-actions{margin-left:0}}`;
// Extrato: mesma densidade e disposicao de linhas que a lista do Cartao.
style.textContent+=`#rec-list{gap:6px}#rec-list .rec-item{padding:8px 10px}#rec-list .rec-item-head{gap:7px;flex-wrap:wrap}#rec-list .rec-item-head .rec-inline-actions{margin-left:auto}#rec-list .rec-item-sub{margin-top:4px;font-size:11px;line-height:1.4}#rec-list .rec-item-date-inline{color:#c5c3ba}#rec-list .rec-inline-actions .rec-button{font-size:10px;padding:4px 6px}#rec-list .rec-item-name{min-width:0}@media(max-width:520px){#rec-list .rec-item-head{row-gap:5px}#rec-list .rec-item-head .rec-inline-actions{margin-left:0}}`;
document.head.appendChild(style);
const section=document.createElement('section');section.id='recorrentes-area';section.className='rec-area';
section.innerHTML=`<div class="rec-top"><button type="button" id="rec-toggle" aria-expanded="true" aria-controls="rec-body">Registros recorrentes <span id="rec-toggle-symbol" aria-hidden="true">−</span></button></div>
<div id="rec-body"><p class="rec-caption">Cadastre salário, débito automático, Pix ou transferência. Exclua o cadastro quando quiser; os lançamentos anteriores permanecem.</p><button type="button" class="rec-button primary" id="rec-open">+ Novo registro</button>
<form class="rec-form" id="rec-form" hidden novalidate><strong id="rec-form-title">Novo registro recorrente</strong>
<div class="row row2" style="margin-top:12px"><label>Descrição<input id="rec-name" type="text" maxlength="75" placeholder="Ex.: Office, salário, academia" required></label><label>Valor (R$)<input id="rec-value" type="number" min="0.01" step="0.01" required placeholder="60,00"></label></div>
<div class="row row2"><label>Tipo<select id="rec-type"><option value="saida">Despesa</option><option value="entrada">Entrada / salário</option></select></label><label>Forma de movimentação<select id="rec-method"><option value="debito_automatico">Débito automático</option><option value="debito">Débito</option><option value="pix">Pix</option><option value="transferencia">Transferência</option></select></label></div>
<div class="row row1" id="rec-card-row" hidden><label>Cartão<select id="rec-card"><option value="">Selecione o cartão</option></select></label></div>
<div class="row row2"><label>Categoria<select id="rec-category"></select></label><label>Subcategoria<select id="rec-subcategory"></select></label></div>
<div class="row row2"><label>Frequência<select id="rec-frequency"><option value="mensal">Mensal</option><option value="semanal">Semanal</option><option value="anual">Anual</option></select></label><label id="rec-date-label">Data da próxima cobrança<input id="rec-start" type="date" required></label><label id="rec-day-label" hidden>Dia da cobrança<input id="rec-day" type="number" min="1" max="31" step="1" inputmode="numeric" placeholder="10" aria-describedby="rec-guidance"></label></div>

<p class="rec-caption" id="rec-guidance">Informe o dia da cobrança ou do recebimento. A movimentação é programada a partir de hoje. Confira se o pagamento ou recebimento realmente ocorreu.</p>
<div class="rec-actions"><button type="submit" class="rec-button primary" id="rec-submit">Salvar recorrência</button><button type="button" class="rec-button" id="rec-close">Cancelar edição</button></div></form>
<div class="rec-list" id="rec-list"></div></div>`;
const anchor=document.querySelector('#page-extrato .add-form');anchor.parentNode.insertBefore(section,anchor);
const cardSection=document.createElement('section');cardSection.id='rec-cartao-area';cardSection.className='rec-area';
cardSection.innerHTML='<div class="rec-top"><button type="button" id="rec-card-toggle" aria-expanded="true" aria-controls="rec-card-body">Pagamentos recorrentes <span id="rec-card-toggle-symbol" aria-hidden="true">−</span></button></div><div id="rec-card-body"><button type="button" class="rec-button primary" id="rec-card-open">+ Novo pagamento</button><div class="rec-list" id="rec-card-list"></div></div>';
const cardAnchor=document.querySelector('#page-cartao .section-title:nth-of-type(2)')||document.querySelector('#page-cartao #cc-card').closest('.add-form');cardAnchor.parentNode.insertBefore(cardSection,cardAnchor);
const $=id=>document.getElementById(id);
const cardRow=$('rec-card-row');
const cardSelect=$('rec-card');
cardRow.hidden=true;cardRow.remove();
function placeCardRow(){
  if(editingRecMode==='cartao'){
    $('rec-form').insertBefore(cardRow,$('rec-category').closest('.row'));
    cardRow.hidden=false;cardRow.style.removeProperty('display');
  }else{cardRow.hidden=true;cardRow.remove();}
}
const datePlusOne=v=>{const d=new Date(v+'T12:00:00');d.setDate(d.getDate()+1);return isoDate(d.getFullYear(),d.getMonth(),d.getDate());};
const displayDate=v=>v?v.slice(8,10)+'/'+v.slice(5,7)+'/'+v.slice(0,4):'';
const kindLabel={debito_automatico:'Débito automático',debito:'Débito',pix:'Pix',transferencia:'Transferência',cartao:'Cartão de crédito',recebimento:'Conta / salário'};
function key(r,data){return String(r.id)+'|'+data;}
function originalJaRegistrado(r,data){
 const list=r.metodo==='cartao'?S.cartao:S.extrato;
 return list.some(x=>String(x.recorrenciaId)===String(r.id)&&x.recorrenciaData===data||(!x.recorrenciaId&&x.data===data&&Number(x.val)===Number(r.valor)&&String(x.desc||'').trim().toLowerCase()===r.nome.trim().toLowerCase()&&(r.metodo!=='cartao'||String(x.cardId)===String(r.cartaoId))));
}
function ocorrencias(r,ate){return datasRecorrentes(r,ate).filter(data=>!S.recorrenciaIgnoradas.includes(key(r,data)));}
function cardOptions(){
 const sel=cardSelect;const previous=sel.value;
 sel.innerHTML='<option value="">Selecione o cartão</option>'+S.cartoes.map(c=>`<option value="${c.id}">${escHtml(c.bank)} · vence dia ${c.dueDay}</option>`).join('');
 if(S.cartoes.some(c=>String(c.id)===previous))sel.value=previous;
}
function recurrenceCategories(){
 const type=$('rec-type').value,cat=$('rec-category'),prev=cat.value;
 cat.innerHTML='<option value="">Escolha a categoria</option>'+Object.keys(CATEGORIAS[type]||{}).filter(n=>n!=='Cartão de crédito').map(n=>`<option value="${escHtml(n)}">${escHtml(n)}</option>`).join('');
 if(Object.prototype.hasOwnProperty.call(CATEGORIAS[type]||{},prev))cat.value=prev;
 recurrenceSubcategories();
}
function recurrenceSubcategories(){
 const subs=$('rec-subcategory'),prev=subs.value;
 const arr=(CATEGORIAS[$('rec-type').value]||{})[$('rec-category').value]||[];
 subs.innerHTML='<option value="">Escolha a subcategoria</option>'+arr.filter(s=>s!=='Dinheiro do mês passado').map(s=>`<option value="${escHtml(s)}">${escHtml(s)}</option>`).join('');
 if(arr.includes(prev))subs.value=prev;
}
function recurrenceType(){
 const entrada=editingRecMode==='conta'&&$('rec-type').value==='entrada',sel=$('rec-method');
 if(editingRecMode==='cartao'){
  $('rec-type').value='saida';sel.innerHTML='<option value="cartao">Cartão de crédito</option>';
 }else if(entrada)sel.innerHTML='<option value="recebimento">Recebimento / salário</option><option value="pix">Pix recebido</option><option value="transferencia">Transferência recebida</option>';
 else sel.innerHTML='<option value="debito_automatico">Débito automático</option><option value="debito">Débito</option><option value="pix">Pix</option><option value="transferencia">Transferência</option>';
 $('rec-type').closest('label').hidden=editingRecMode==='cartao';
 $('rec-method').closest('label').hidden=editingRecMode==='cartao';
 placeCardRow();
 recurrenceCategories();recurrenceTiming();
}
function recurrenceTiming(){
 const mensal=$('rec-frequency').value==='mensal';
 const recebimento=editingRecMode==='conta'&&$('rec-type').value==='entrada';
 $('rec-day-label').hidden=!mensal;$('rec-date-label').hidden=mensal;
 $('rec-day').required=mensal;$('rec-start').required=!mensal;
 $('rec-day-label').firstChild.textContent=recebimento?'Dia do recebimento':'Dia da cobrança';
 $('rec-date-label').firstChild.textContent=recebimento?'Data do próximo recebimento':'Data da próxima cobrança';
 $('rec-guidance').textContent=mensal?(editingRecMode==='cartao'?'Informe apenas o dia do mês (1 a 31). A próxima cobrança será programada a partir de hoje; meses curtos usam o último dia. O pagamento da fatura é separado.':'Informe apenas o dia do mês (1 a 31). O próximo lançamento será programado a partir de hoje; meses curtos usam o último dia. O aplicativo não consulta bancos: confira se a movimentação ocorreu.'):(editingRecMode==='cartao'?'Para frequência semanal ou anual, informe a data da próxima cobrança. O vencimento e o pagamento da fatura são separados.':'Para frequência semanal ou anual, informe a data do próximo pagamento ou recebimento. O aplicativo não consulta bancos: confira a movimentação efetiva.');
}
function openRecEditor(id=null,mode='conta'){
 const r=S.recorrentes.find(x=>String(x.id)===String(id));editingRecId=r?r.id:null;
 editingRecMode=r?(r.metodo==='cartao'?'cartao':'conta'):mode;
 const area=$(editingRecMode==='cartao'?'rec-cartao-area':'recorrentes-area');
 if(editingRecMode==='conta')setRecAreaExpanded(true);
 else setCardRecAreaExpanded(true);
 const list=area.querySelector('.rec-list');list.parentNode.insertBefore($('rec-form'),list);
 $('rec-form').hidden=false;
 $('rec-form-title').textContent=r?'Editar '+(editingRecMode==='cartao'?'pagamento recorrente':'registro recorrente'):(editingRecMode==='cartao'?'Novo pagamento recorrente':'Novo registro recorrente');
 $('rec-name').value=r?r.nome:'';$('rec-value').value=r?r.valor:'';
 $('rec-type').value=r?r.tipo:'saida';recurrenceType();
 $('rec-method').value=editingRecMode==='cartao'?'cartao':r?r.metodo:'debito_automatico';
 placeCardRow();cardOptions();cardSelect.value=r&&r.cartaoId?String(r.cartaoId):'';
 $('rec-category').value=r?r.categoria:'';recurrenceSubcategories();$('rec-subcategory').value=r?r.subcategoria:'';
 $('rec-frequency').value=r?r.frequencia:'mensal';$('rec-start').value=r?r.inicio:today();
 $('rec-day').value=r&&r.frequencia==='mensal'?String(r.diaCobranca||Number(r.inicio.slice(8))):'';
 recurrenceTiming();
 $('rec-submit').textContent=r?'Salvar alterações':editingRecMode==='cartao'?'Salvar pagamento':'Salvar recorrência';$('rec-form').scrollIntoView({behavior:'smooth',block:'nearest'});$('rec-name').focus();
}
function setRecAreaExpanded(expanded){
 $('rec-body').hidden=!expanded;
 $('rec-toggle').setAttribute('aria-expanded',String(expanded));
 $('rec-toggle-symbol').textContent=expanded?'−':'+';
 if(!expanded&&$('rec-form').parentElement===$('rec-body'))closeRecEditor();
}
function setCardRecAreaExpanded(expanded){
 $('rec-card-body').hidden=!expanded;
 $('rec-card-toggle').setAttribute('aria-expanded',String(expanded));
 $('rec-card-toggle-symbol').textContent=expanded?'−':'+';
 if(!expanded&&$('rec-form').parentElement===$('rec-card-body'))closeRecEditor();
}
function closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';placeCardRow();$('rec-body').appendChild($('rec-form'));}
function cardForecasts(){
 const hoje=today(),horizon=new Date(hoje+'T12:00:00');horizon.setMonth(horizon.getMonth()+36);
 const selecionado=new Date(cartaoMes.getFullYear(),cartaoMes.getMonth()+13,1,12);
 if(selecionado>horizon)horizon.setTime(selecionado.getTime());
 const fim=isoDate(horizon.getFullYear(),horizon.getMonth(),horizon.getDate());
 return S.recorrentes.filter(r=>r.metodo==='cartao'&&!r.excluida).flatMap(r=>ocorrencias(r,fim).filter(d=>d>hoje&&!originalJaRegistrado(r,d)).map(data=>{
  const card=S.cartoes.find(c=>String(c.id)===String(r.cartaoId));if(!card)return null;
  return {id:'rec-prev-'+r.id+'-'+data,data,desc:r.nome,tipo:'compra',val:r.valor,parcelas:1,vencDia:card.dueDay,closeDay:card.closeDay,cardId:card.id,banco:card.bank,cardColor:card.color,categoria:r.categoria,subcategoria:r.subcategoria,gastoTipo:'',recorrenciaId:r.id,recorrenciaData:data,previsto:true};
 }).filter(Boolean));
}
function cashForecastsForMonth(y,m){
 const last=isoDate(y,m,new Date(y,m+1,0).getDate());
 return S.recorrentes.filter(r=>r.metodo!=='cartao'&&!r.excluida).flatMap(r=>ocorrencias(r,last).filter(d=>d>today()&&d.slice(0,7)===last.slice(0,7)&&(!saldoInicialValido(S.saldoInicial)||d>S.saldoInicial.data)&&!originalJaRegistrado(r,d)).map(data=>({id:'rec-futuro-'+r.id+'-'+data,data,desc:r.nome,val:r.valor,tipo:r.tipo,categoria:r.categoria,subcategoria:r.subcategoria,pagamento:r.metodo,auto:true,previsto:true}))).sort((a,b)=>a.data.localeCompare(b.data));
}
// O Extrato exibe previsões na própria tabela; só o registro efetivo entra no saldo e no JSON.
window.cashRecurringForecasts=cashForecastsForMonth;

function syncRecurring(){
 if(!Array.isArray(S.recorrentes)||!S.recorrentes.length){renderRecurring();return false;}
 let changed=false;const hoje=today();
 // O mês futuro no cartão é previsão derivada do cadastro, não uma compra duplicada no JSON.
 for(const r of S.recorrentes){
  if(r.excluida)continue;
  const card=r.metodo==='cartao'?S.cartoes.find(c=>String(c.id)===String(r.cartaoId)):null;
  for(const data of ocorrencias(r,hoje)){
   if(originalJaRegistrado(r,data))continue;
   if(r.metodo==='cartao'){
    if(!card)continue;
    S.cartao.push({id:novoIdGlobal(),data,desc:r.nome,tipo:'compra',val:r.valor,parcelas:1,vencDia:card.dueDay,closeDay:card.closeDay,cardId:card.id,banco:card.bank,cardColor:card.color,categoria:r.categoria,subcategoria:r.subcategoria,gastoTipo:'',recorrenciaId:r.id,recorrenciaData:data});changed=true;
   }else{
    if(saldoInicialValido(S.saldoInicial)&&data<=S.saldoInicial.data)continue;
    S.extrato.push({id:novoIdExtrato(),data,desc:r.nome,tipo:r.tipo,val:r.valor,categoria:r.categoria,subcategoria:r.subcategoria,gastoTipo:'',pagamento:r.metodo,recorrenciaId:r.id,recorrenciaData:data,geradoAutomaticamente:true});changed=true;
   }
  }
 }
 if(changed){saveData();renderCartao();renderExtrato();updateResumo();}
 renderRecurring();return changed;
}
function recurringNext(r){
 const horizon=new Date(today()+'T12:00:00');horizon.setFullYear(horizon.getFullYear()+3);
 const end=isoDate(horizon.getFullYear(),horizon.getMonth(),horizon.getDate());
 return ocorrencias(r,end).find(d=>d>=today())||'';
}
function renderRecurring(){
 if(!$('rec-list')||!$('rec-card-list'))return;cardOptions();
 const ativos=S.recorrentes.filter(r=>!r.excluida).slice().sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR'));
 function html(list,empty){
  if(!list.length)return '<div class="rec-caption">'+empty+'</div>';
  return list.map(r=>{
   const next=recurringNext(r),ended=!!r.fim&&r.fim<=today();
   const freq={semanal:'Semanal',mensal:'Mensal',anual:'Anual'}[r.frequencia]||r.frequencia;
   const card=S.cartoes.find(c=>String(c.id)===String(r.cartaoId));
   if(r.metodo==='cartao'){
    const cobranca=r.frequencia==='mensal'?'Dia da cobrança: '+(r.diaCobranca||Number(r.inicio.slice(8))):'Desde: '+displayDate(r.inicio);
    return `<div class="rec-item"><div class="rec-item-head"><span class="rec-item-name">${escHtml(r.nome)}</span><span class="rec-tag${ended?' inactive':''}">${ended?'Encerrado':'Saída'}</span><span class="rec-inline-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir agora</button></span></div>
    <div class="rec-item-sub"><strong style="color:#f5f5f2">−${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo])}${card?' ('+escHtml(card.bank)+')':''} · <span class="rec-item-date-inline">${cobranca}${next?' · Próxima: '+displayDate(next):''}</span></div></div>`;
   }
   const dia=r.frequencia==='mensal'?(r.tipo==='entrada'?'Dia do recebimento: ':'Dia da cobrança: ')+(r.diaCobranca||Number(r.inicio.slice(8))):'Desde: '+displayDate(r.inicio);
   return `<div class="rec-item"><div class="rec-item-head"><span class="rec-item-name">${escHtml(r.nome)}</span><span class="rec-tag${ended?' inactive':''}">${ended?'Encerrado':r.tipo==='entrada'?'Entrada':'Saída'}</span><span class="rec-inline-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir agora</button></span></div>
    <div class="rec-item-sub"><strong style="color:#f5f5f2">${r.tipo==='saida'?'−':'+'}${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo]||r.metodo)} · <span class="rec-item-date-inline">${dia}${r.fim?' · Encerramento: '+displayDate(r.fim):''}${next?' · Próxima: '+displayDate(next):''}</span></div></div>`;
  }).join('');
 }
 $('rec-list').innerHTML=html(ativos.filter(r=>r.metodo!=='cartao'),'Nenhum registro recorrente da conta. Cadastre salário, Pix ou débito automático.');
 $('rec-card-list').innerHTML=html(ativos.filter(r=>r.metodo==='cartao'),'Nenhum pagamento recorrente no cartão.');
}
function saveRecEditor(event){
 event.preventDefault();
 const existing=S.recorrentes.find(x=>String(x.id)===String(editingRecId));
 const nome=$('rec-name').value.trim(),valor=Number($('rec-value').value),tipo=$('rec-type').value,metodo=$('rec-method').value,cartaoId=metodo==='cartao'?Number($('rec-card').value):null;
 let inicio=$('rec-start').value;const fim=existing?existing.fim||null:null,frequencia=$('rec-frequency').value,categoria=$('rec-category').value,subcategoria=$('rec-subcategory').value;
 const mensal=frequencia==='mensal';
 const diaCobranca=mensal?Number($('rec-day').value):null;
 if(mensal){
  if($('rec-day').value.trim()===''||!Number.isInteger(diaCobranca)||diaCobranca<1||diaCobranca>31){appAlert('Informe o dia do mês entre 1 e 31.');return;}
  inicio=proximaCobrancaMensal(existing?datePlusOne(today()):today(),diaCobranca);
 }
 if(!nome||!valorMonetarioValido(valor)||valor<=0||!dataISOValida(inicio)||fim&&!dataISOValida(fim)||fim&&fim<=inicio||!['semanal','mensal','anual'].includes(frequencia)||!['entrada','saida'].includes(tipo)||!categoria||!subcategoria){appAlert('Preencha descrição, valor, categoria e datas válidas.');return;}
 if(tipo==='entrada'&&!['recebimento','pix','transferencia'].includes(metodo)||tipo==='saida'&&!['cartao','debito_automatico','debito','pix','transferencia'].includes(metodo)){appAlert('Escolha uma forma de pagamento válida.');return;}
 if((editingRecMode==='cartao')!==(metodo==='cartao')){appAlert('Escolha a aba correspondente ao registro.');return;}
 if(metodo==='cartao'&&!S.cartoes.some(c=>String(c.id)===String(cartaoId))){appAlert('Cadastre e selecione um cartão antes de salvar.');return;}
 let novoId=novoIdGlobal();while(S.recorrentes.some(x=>String(x.id)===String(novoId)))novoId++;
 const newRecord={id:existing?existing.id:novoId,nome,valor:Math.round(valor*100)/100,tipo,metodo,cartaoId,inicio,fim,frequencia,categoria,subcategoria,excluida:false,...(mensal?{diaCobranca}:{})};
 if(existing){
  // Passado imutável: edição troca apenas ocorrências a partir de amanhã.
  newRecord.vigenteDesde=datePlusOne(today());
  const idx=S.recorrentes.findIndex(x=>String(x.id)===String(existing.id));S.recorrentes[idx]=newRecord;
 }else S.recorrentes.push(newRecord);
 closeRecEditor();saveData();syncRecurring();renderExtrato();renderCartao();updateResumo();
 appAlert(existing?'Cadastro editado. Movimentações passadas foram preservadas; mudanças valem a partir de amanhã.':'Recorrência cadastrada. Previsões futuras aparecem nas abas correspondentes.');
}
async function deleteRec(id){
 const r=S.recorrentes.find(x=>String(x.id)===String(id));if(!r)return;
 if(!await appConfirm('Excluir agora o cadastro de '+r.nome+'? As movimentações já registradas ficam no histórico, mas todas as previsões futuras são removidas.'))return;
 r.excluida=true;r.fim=today();saveData();syncRecurring();renderCartao();renderExtrato();updateResumo();
}
function ignoreRecurring(row){
 if(!row||!row.recorrenciaId||!row.recorrenciaData)return;
 const id=String(row.recorrenciaId)+'|'+row.recorrenciaData;
 if(!S.recorrenciaIgnoradas.includes(id))S.recorrenciaIgnoradas.push(id);
}
// O JSON antigo continua aceito; os novos campos são opcionais e validados.
const oldValidate=validarDadosImportados;
validarDadosImportados=function(file){
 const dados=oldValidate(file);
 if(dados.recorrentes!==undefined){
  if(!Array.isArray(dados.recorrentes)||dados.recorrentes.length>2000)throw Error('Cadastro de recorrências inválido.');
  const ids=new Set();
  for(const r of dados.recorrentes){
   if(!r||typeof r!=='object'||!Number.isSafeInteger(Number(r.id))||Number(r.id)<=0||ids.has(String(r.id))||typeof r.nome!=='string'||!r.nome.trim()||r.nome.length>75||!valorMonetarioValido(r.valor)||r.valor<=0||!['entrada','saida'].includes(r.tipo)||!['cartao','debito_automatico','debito','pix','transferencia','recebimento'].includes(r.metodo)||!['semanal','mensal','anual'].includes(r.frequencia)||!dataISOValida(r.inicio)||r.fim!==null&&r.fim!==undefined&&!dataISOValida(r.fim)||r.vigenteDesde&&!dataISOValida(r.vigenteDesde)||r.diaCobranca!==undefined&&r.diaCobranca!==null&&(!Number.isInteger(r.diaCobranca)||r.diaCobranca<1||r.diaCobranca>31||r.frequencia!=='mensal'))throw Error('Recorrência inválida no arquivo.');
   ids.add(String(r.id));
  }
 }
 if(dados.recorrenciaIgnoradas!==undefined&&(!Array.isArray(dados.recorrenciaIgnoradas)||dados.recorrenciaIgnoradas.length>100000||dados.recorrenciaIgnoradas.some(x=>typeof x!=='string'||!/^[0-9]+\|\d{4}-\d\d-\d\d$/.test(x))))throw Error('Exceções recorrentes inválidas.');
 return dados;
};
const oldApply=applyDataFile;
applyDataFile=function(file){
 const dados=validarDadosImportados(file);
 const former=S.recorrentes;S.recorrentes=[];
 try{oldApply(file);}catch(error){S.recorrentes=former;throw error;}
 S.recorrentes=Array.isArray(dados.recorrentes)?dados.recorrentes:[];
 S.recorrenciaIgnoradas=Array.isArray(dados.recorrenciaIgnoradas)?dados.recorrenciaIgnoradas:[];
 const added=syncRecurring();renderCartao();renderExtrato();updateResumo();
 // Restauração assíncrona pode reaplicar o status antigo de salvamento após o cadastro ser gerado.
 if(added)setTimeout(()=>{hasUnsavedChanges=true;saveData();},0);
};
const oldCardList=renderRegisteredCards;
renderRegisteredCards=function(){oldCardList();cardOptions();};
const oldGetMap=getMesMap;
getMesMap=function(){
 const map=oldGetMap();for(const purchase of cardForecasts()){
  const card=S.cartoes.find(c=>String(c.id)===String(purchase.cardId));if(!card)continue;
  const d=dueDateFor(new Date(purchase.data+'T12:00:00'),card.dueDay,0,card.closeDay);
  const month=monthKey(d.getFullYear(),d.getMonth());map[month]=(map[month]||0)+purchase.val;
 }return map;
};
const oldGetParcelas=getParcelasCartao;
getParcelasCartao=function(){
 const rows=oldGetParcelas();
 return rows.concat(cardForecasts().map(x=>{
  const d=dueDateFor(new Date(x.data+'T12:00:00'),x.vencDia,0,x.closeDay);
  return {id:x.id+'-0',cardId:x.cardId,data:isoDate(d.getFullYear(),d.getMonth(),d.getDate()),desc:'Cartão previsto - '+x.desc,tipo:'cartao',categoria:x.categoria,subcategoria:x.subcategoria,val:x.val,auto:true,previsto:true};
 }));
};
// Mesmo modelo de lançamentos para compras avulsas e assinaturas futuras;
// a previsão não vira registro persistido até chegar sua data.
window.cardRecurringForecasts=cardForecasts;
window.editRecurringCardForecast=id=>openRecEditor(id,'cartao');

const oldEditPurchase=editCartao;
editCartao=function(id){const row=S.cartao.find(x=>String(x.id)===String(id));if(row&&row.recorrenciaId){showPage('cartao',document.querySelectorAll('.nav button')[2]);openRecEditor(row.recorrenciaId);return;}oldEditPurchase(id);};
const oldDelCC=delCC;
delCC=function(id){const row=S.cartao.find(x=>String(x.id)===String(id));oldDelCC(id);if(row&&!S.cartao.some(x=>String(x.id)===String(id))){ignoreRecurring(row);saveData();renderRecurring();}};
const oldDelExt=delExt;
delExt=function(id){const row=S.extrato.find(x=>String(x.id)===String(id));oldDelExt(id);if(row&&!S.extrato.some(x=>String(x.id)===String(id))){ignoreRecurring(row);saveData();renderRecurring();}};
const oldDelCard=delRegisteredCard;
delRegisteredCard=function(id){if(S.recorrentes.some(r=>!r.excluida&&r.metodo==='cartao'&&String(r.cartaoId)===String(id))){appAlert('Este cartão está vinculado a uma recorrência. Encerre ou exclua o cadastro antes de removê-lo.');return;}oldDelCard(id);};
$('rec-toggle').addEventListener('click',()=>setRecAreaExpanded($('rec-body').hidden));
$('rec-card-toggle').addEventListener('click',()=>setCardRecAreaExpanded($('rec-card-body').hidden));
$('rec-open').addEventListener('click',()=>openRecEditor());$('rec-close').addEventListener('click',closeRecEditor);
$('rec-card-open').addEventListener('click',()=>openRecEditor(null,'cartao'));
$('rec-form').addEventListener('submit',saveRecEditor);
$('rec-type').addEventListener('change',recurrenceType);
$('rec-method').addEventListener('change',placeCardRow);
$('rec-category').addEventListener('change',recurrenceSubcategories);
$('rec-frequency').addEventListener('change',recurrenceTiming);
for(const listId of ['rec-list','rec-card-list'])$(listId).addEventListener('click',event=>{
 const btn=event.target.closest('button');if(!btn)return;
 if(btn.dataset.recedit)openRecEditor(btn.dataset.recedit);
 if(btn.dataset.recdelete)void deleteRec(btn.dataset.recdelete);
});
const oldShowPage=showPage;
showPage=function(id,btn){oldShowPage(id,btn);if(id==='extrato'||id==='cartao')renderRecurring();};
$('rec-start').value=today();recurrenceType();closeRecEditor();renderRecurring();
const midnightPoll=setInterval(()=>{if(S.recorrentes.length)syncRecurring();},5*60*1000);
})();
}

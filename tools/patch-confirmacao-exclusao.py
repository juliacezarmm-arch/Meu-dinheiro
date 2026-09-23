from pathlib import Path

p=Path("index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count:
        raise SystemExit(f"Esperava {count} ocorrencia(s), encontrei {n}: {old[:120]!r}")
    s=s.replace(old,new,count)

old_confirm="""function appConfirm(message){
 return new Promise(resolve=>{
  const overlay=document.getElementById('app-confirm-overlay'),ok=document.getElementById('app-confirm-accept'),cancel=document.getElementById('app-confirm-cancel'),previous=document.activeElement;
  document.getElementById('app-confirm-message').textContent=String(message);
  function finish(answer){overlay.hidden=true;ok.removeEventListener('click',accept);cancel.removeEventListener('click',reject);document.removeEventListener('keydown',escape);if(previous&&previous.isConnected)previous.focus();resolve(answer);}
  function accept(){finish(true);}function reject(){finish(false);}function escape(event){if(event.key==='Escape'){event.preventDefault();reject();}}
  ok.addEventListener('click',accept);cancel.addEventListener('click',reject);document.addEventListener('keydown',escape);overlay.hidden=false;cancel.focus();
 });
}
"""
new_confirm=old_confirm+"""async function confirmarExclusao(message){
  const title=document.getElementById('app-confirm-title');
  const icon=document.querySelector('#app-confirm-overlay .site-dialog-icon');
  const accept=document.getElementById('app-confirm-accept');
  const prevTitle=title.textContent,prevIcon=icon.textContent,prevAccept=accept.textContent;
  title.textContent='Confirmar exclusão';
  icon.textContent='!';
  accept.textContent='Excluir';
  try{return await appConfirm(message||'Tem certeza que deseja excluir? Esta ação não pode ser desfeita.');}
  finally{title.textContent=prevTitle;icon.textContent=prevIcon;accept.textContent=prevAccept;}
}

// Protege qualquer X destrutivo renderizado no aplicativo, inclusive listas dinâmicas.
// X de fechar janela/aviso não entra aqui porque não apaga dados.
const exclusaoConfirmadaPorBotao=new WeakSet();
document.addEventListener('click',async event=>{
  const btn=event.target&&event.target.closest?event.target.closest('button'):null;
  if(!btn||btn.dataset.recdelete||btn.classList.contains('goal-delete'))return;
  const onclick=btn.getAttribute('onclick')||'';
  const label=[btn.getAttribute('aria-label')||'',btn.dataset.help||'',btn.getAttribute('title')||''].join(' ');
  const temX=btn.textContent.trim()==='×'||!!btn.querySelector('.ti-x');
  const chamaExclusao=/\\b(?:del|delete)[A-Za-z0-9_]*\\s*\\(/.test(onclick);
  const rotuloExclusao=/\\b(?:excluir|remover|apagar)\\b/i.test(label);
  if(!temX||(!chamaExclusao&&!rotuloExclusao))return;
  if(exclusaoConfirmadaPorBotao.has(btn)){exclusaoConfirmadaPorBotao.delete(btn);return;}
  event.preventDefault();
  event.stopImmediatePropagation();
  if(!await confirmarExclusao('Tem certeza que deseja excluir este registro? Essa ação não pode ser desfeita.'))return;
  exclusaoConfirmadaPorBotao.add(btn);
  btn.click();
},true);
"""
rep(old_confirm,new_confirm)

old_inv="""  if(temProgresso){
    const tipo=item.kind==='meta'?'esta meta':'este investimento';
    const alvo=item.kind==='meta'?'meta':'investimento';
    const concluida=item.kind==='meta'&&Number(item.meta||0)>0&&Number(item.valorAtual||0)>=Number(item.meta||0);
    const msg=concluida
      ? `Esta meta já tem progresso e parece estar concluída.\\n\\nSe excluir, o histórico e os lançamentos ligados a ela serão apagados.\\n\\nTem certeza que deseja excluir esta meta?`
      : `${tipo.charAt(0).toUpperCase()+tipo.slice(1)} já tem dinheiro, histórico ou lançamentos ligados.\\n\\nSe excluir, a pessoa pode perder o progresso desse ${alvo}.\\n\\nTem certeza que deseja excluir?`;
    if(!await appConfirm(msg))return;
  }
"""
new_inv="""  const tipo=item.kind==='meta'?'esta meta':'este investimento';
  const alvo=item.kind==='meta'?'meta':'investimento';
  const concluida=item.kind==='meta'&&Number(item.meta||0)>0&&Number(item.valorAtual||0)>=Number(item.meta||0);
  const msg=temProgresso
    ? (concluida
      ? `Esta meta já tem progresso e parece estar concluída.\\n\\nSe excluir, o histórico e os lançamentos ligados a ela serão apagados.\\n\\nTem certeza que deseja excluir esta meta?`
      : `${tipo.charAt(0).toUpperCase()+tipo.slice(1)} já tem dinheiro, histórico ou lançamentos ligados.\\n\\nSe excluir, a pessoa pode perder o progresso desse ${alvo}.\\n\\nTem certeza que deseja excluir?`)
    : `Tem certeza que deseja excluir ${tipo}? Essa ação não pode ser desfeita.`;
  if(!await confirmarExclusao(msg))return;
"""
rep(old_inv,new_inv)

p.write_text(s,encoding="utf-8")

r=Path("js/recorrentes.js")
rs=r.read_text(encoding="utf-8")
old=""" if(!await appConfirm('Excluir agora o cadastro de '+r.nome+'? As movimentações já registradas ficam no histórico, mas todas as previsões futuras são removidas.'))return;"""
new=""" if(!await confirmarExclusao('Excluir agora o cadastro de '+r.nome+'? As movimentações já registradas ficam no histórico, mas todas as previsões futuras são removidas.'))return;"""
if rs.count(old)!=1:
    raise SystemExit("Confirmacao de recorrencia nao encontrada")
rs=rs.replace(old,new)
r.write_text(rs,encoding="utf-8")

t=Path("tests/exclusao-confirmacao.test.js")
t.write_text(r'''const assert=require('assert'),fs=require('fs');
const html=fs.readFileSync('index.html','utf8');
const rec=fs.readFileSync('js/recorrentes.js','utf8');

assert(html.includes("async function confirmarExclusao(message)"),'Deve existir confirmacao especifica de exclusao');
assert(html.includes("title.textContent='Confirmar exclusão'"),'Dialogo deve identificar exclusao');
assert(html.includes("accept.textContent='Excluir'"),'Botao de confirmar deve dizer Excluir');
assert(html.includes("const exclusaoConfirmadaPorBotao=new WeakSet()"),'X destrutivos devem ser interceptados');
assert(html.includes("const temX=btn.textContent.trim()==='×'||!!btn.querySelector('.ti-x')"),'Protecao deve mirar X destrutivos');
assert(html.includes("if(!await confirmarExclusao(msg))return;"),'Investimento/meta deve sempre confirmar exclusao');
assert(rec.includes("if(!await confirmarExclusao('Excluir agora o cadastro de '+r.nome"),'Recorrencias devem usar a mesma caixa de exclusao');

for(const fn of ['delRegisteredCard','delCC','delExt','delInvestHistory']){
  assert(html.includes(fn+'('),'Funcao destrutiva ausente: '+fn);
}
assert(html.includes('aria-label="Remover cartão'),'X de cartão cadastrado deve continuar identificável');
assert(html.includes('aria-label="Remover" title="Apaga esta compra do cartão.'),'X de compra deve continuar identificável');
assert(html.includes('aria-label="Remover movimento"'),'X do histórico deve continuar identificável');

console.log('PASS: exclusoes por X exigem confirmacao e X de fechar nao e interceptado');
''',encoding="utf-8")

rt=Path("tests/recorrentes.test.js")
rts=rt.read_text(encoding="utf-8")
old_token="for(const token of ['recorrenciaData','recorrenciaIgnoradas','saldoInicial.data','originalJaRegistrado','syncRecurring','cardForecasts','cashForecastsForMonth','deleteRec','openRecEditor','appConfirm'])"
new_token="for(const token of ['recorrenciaData','recorrenciaIgnoradas','saldoInicial.data','originalJaRegistrado','syncRecurring','cardForecasts','cashForecastsForMonth','deleteRec','openRecEditor','confirmarExclusao'])"
if rts.count(old_token)!=1:
    raise SystemExit("Lista de regras do teste de recorrencias nao encontrada")
rt.write_text(rts.replace(old_token,new_token),encoding="utf-8")

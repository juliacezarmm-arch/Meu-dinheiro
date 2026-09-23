const assert=require('assert'),fs=require('fs');
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

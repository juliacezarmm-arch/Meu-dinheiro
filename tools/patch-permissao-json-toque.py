from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def rep(old,new):
 global s
 assert s.count(old)==1, f'Trecho nao encontrado ou ambiguo: {old[:90]!r} ({s.count(old)})'
 s=s.replace(old,new,1)
rep('    <button type="button" onclick="openDataFile()" title="Abra um JSON para consultar e editar seus registros.">Abrir dados</button>', '    <button type="button" onclick="openDataFile()" title="Abra um JSON para consultar e editar seus registros.">Abrir dados</button>\n    <button type="button" id="json-permission-button" onclick="autorizarJsonPendente()" title="Pedir autorização do Chrome para editar o JSON selecionado." hidden>Autorizar edição do JSON</button>')
rep('let knownFileSignature=null;','let knownFileSignature=null;\n// Identificadores temporarios apenas em memoria. Nunca armazenar dados financeiros no navegador.\nlet pendingJsonHandle=null;\nlet authorizedJsonHandle=null;')
needle='async function openDataFile(){'
authorize='''// O Chrome exige um novo gesto do usuario em alguns fluxos do seletor Android.
// A chamada de requestPermission acontece IMEDIATAMENTE no clique deste botao,
// sem aguardar queryPermission, leitura de arquivo ou outra promise antes.
function autorizarJsonPendente(){
 const handle=pendingJsonHandle;
 if(!handle)return Promise.resolve(false);
 const button=document.getElementById('json-permission-button');
 let permission;
 try{
  if(typeof handle.requestPermission!=='function')throw Error('Sem API de autorizacao');
  permission=handle.requestPermission({mode:'readwrite'});
 }catch(error){
  setSaveStatus('Edição bloqueada pelo navegador — abra no Chrome completo.');
  appAlert('O navegador não conseguiu solicitar permissão de edição. Abra este endereço diretamente no aplicativo Chrome, em uma guia normal, e selecione seu JSON. O original não foi alterado.');
  return Promise.resolve(false);
 }
 button.disabled=true;
 return Promise.resolve(permission).then(async status=>{
  if(pendingJsonHandle!==handle)return false;
  if(status!=='granted'){
   setSaveStatus('Sem permissão de edição — tente no Chrome completo.');
   appAlert('A edição continua bloqueada. Abra o Meu Dinheiro diretamente no Chrome, fora da janela integrada do aplicativo, e tente novamente. Seu JSON não foi alterado.');
   return false;
  }
  pendingJsonHandle=null;
  button.hidden=true;
  authorizedJsonHandle=handle;
  return await openDataFile();
 }).catch(error=>{
  setSaveStatus('Sem permissão de edição — tente no Chrome completo.');
  appAlert('O navegador não permitiu editar o arquivo nesta janela. Abra o endereço em uma guia normal do Chrome. Nenhum dado foi gravado.');
  return false;
 }).finally(()=>{button.disabled=false;});
}
'''
rep(needle,authorize+needle)
rep("  const handles=await window.showOpenFilePicker({multiple:false,types:[{description:'Dados Meu dinheiro',accept:{'application/json':['.json']}}]});\n  const handle=handles[0];if(!handle)return false;", "  const handles=authorizedJsonHandle?[authorizedJsonHandle]:await window.showOpenFilePicker({multiple:false,types:[{description:'Dados Meu dinheiro',accept:{'application/json':['.json']}}]});\n  authorizedJsonHandle=null;\n  const handle=handles[0];if(!handle)return false;")
rep("  if(!await fileWriteAllowed(handle,true)){\n   setSaveStatus('Edição não autorizada. Abra o JSON novamente e permita salvar.');\n   appAlert('O Chrome não autorizou a edição do JSON. Abra o arquivo novamente e permita salvar quando solicitado. Nenhum dado foi alterado.');\n   return false;\n  }", "  if(!await fileWriteAllowed(handle,true)){\n   pendingJsonHandle=handle;\n   document.getElementById('json-permission-button').hidden=false;\n   setSaveStatus('JSON selecionado — toque em Autorizar edição.');\n   appAlert('O JSON foi selecionado, mas o Chrome não autorizou a edição. Toque em Autorizar edição do JSON para solicitar a permissão diretamente. Nenhum dado foi alterado.');\n   return false;\n  }\n  pendingJsonHandle=null;\n  document.getElementById('json-permission-button').hidden=true;")
# O teste anterior simula somente o primeiro pedido de permissao: atualize-o
# para cobrir a segunda autorizacao por gesto e manter as demais verificacoes.
t=Path('tests/abertura-json-tablet.test.js')
x=t.read_text(encoding='utf-8')
def trep(old,new):
 global x
 assert x.count(old)==1, f'Teste: trecho nao encontrado: {old[:70]!r}'
 x=x.replace(old,new,1)
trep("assert(match,'Rotina de abertura ausente');", "assert(match,'Rotina de abertura ausente');\nassert(html.includes('id=\"json-permission-button\"'),'Botao de autorizacao faltando');\nconst permissionFn=src.match(/^function autorizarJsonPendente\\(\\)\\{[\\s\\S]*?^\\}\\n/m);assert(permissionFn,'Rotina de permissao por clique ausente');")
trep(" const handle={name:'dados.json',getFile:async()=>{seen.read++;seen.activation=false;if(readError)throw Error('Falha de leitura');return{text:async()=>text};}};", " let permitted=allow;\n const handle={name:'dados.json',getFile:async()=>{seen.read++;seen.activation=false;if(readError)throw Error('Falha de leitura');return{text:async()=>text};},requestPermission:()=>{seen.manualPermission=(seen.manualPermission||0)+1;assert(seen.activation,'A permissao por clique nao pode esperar leitura ou outras promises');permitted=true;return Promise.resolve('granted');}};\n const permissionButton={hidden:true,disabled:false};")
trep("  fileWriteAllowed:async()=>{seen.asked++;assert(seen.activation,'Chrome perdeu ativacao antes de solicitar permissao');return allow;},", "  document:{getElementById:id=>id==='json-permission-button'?permissionButton:null},\n  fileWriteAllowed:async()=>{seen.asked++;assert(seen.activation,'Chrome perdeu ativacao antes de solicitar permissao');return permitted;},")
trep(" vm.runInContext('let hasUnsavedChanges=false,dataFileHandle=null,knownFileSignature=null,dataRevision=0,isApplyingData=false;'+match[0],ctx);", " vm.runInContext('let hasUnsavedChanges=false,dataFileHandle=null,knownFileSignature=null,dataRevision=0,isApplyingData=false,pendingJsonHandle=null,authorizedJsonHandle=null;'+permissionFn[0]+match[0],ctx);")
trep(" x=scenario({allow:false});assert.strictEqual(await x.run(),false);assert.strictEqual(x.seen.read,0);assert.strictEqual(x.seen.loaded,0);assert(/não autorizou/.test(x.seen.alerts[0]));assert.strictEqual(x.S.extrato,x.old);", " x=scenario({allow:false});assert.strictEqual(await x.run(),false);assert.strictEqual(x.seen.read,0);assert.strictEqual(x.seen.loaded,0);assert(/não autorizou/.test(x.seen.alerts[0]));assert.strictEqual(x.S.extrato,x.old);\n assert.strictEqual(await vm.runInContext('autorizarJsonPendente()',x.ctx),true,'Clique de autorizacao deve abrir o MESMO arquivo');\n assert.strictEqual(x.seen.manualPermission,1);assert.strictEqual(x.seen.read,1);assert.strictEqual(x.seen.loaded,1);assert.strictEqual(x.S.extrato[0].id,1);assert.strictEqual(x.seen.writes,0);")
trep("PASS: autorizacao antes de leitura; abertura, permissao, JSON invalido, validacao, leitura e rollback sem escritas", "PASS: autorizacao explicita por gesto, mesmo arquivo; validacao, leitura, rollback sem escritas")
p.write_text(s,encoding='utf-8');t.write_text(x,encoding='utf-8')
print('PASS: patch de autorizacao explicita aplicado a index.html e teste de abertura')

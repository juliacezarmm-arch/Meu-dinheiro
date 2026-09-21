from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')
def replace(old,new):
    global s
    count=s.count(old)
    assert count==1, f'Esperada uma ocorrencia, encontradas {count}: {old[:110]!r}'
    s=s.replace(old,new,1)

replace('let diskSaveQueue=Promise.resolve();\nlet knownFileSignature=null;', 'let diskSaveQueue=Promise.resolve();\nlet fileSaveQueue=Promise.resolve();\nlet knownFileSignature=null;')
replace("async function fileSignature(handle){\n try{const file=await handle.getFile();return String(file.size)+':'+String(file.lastModified);}catch{return null;}\n}", "// Compare o CONTEUDO, nao size/lastModified: Android e provedores de arquivos\n// podem atualizar metadados sem alterar os dados do JSON.\nasync function fileSignature(handle){\n try{const file=await handle.getFile();return await file.text();}catch{return null;}\n}")
replace("async function fileUnchanged(handle,ask){\n if(!knownFileSignature)return false;", "async function fileUnchanged(handle,ask){\n if(knownFileSignature===null)return false;")
replace(" if(!current){setSaveStatus('Arquivo indisponível — abra o JSON novamente.');return false;}", " if(current===null){setSaveStatus('Arquivo indisponível — abra o JSON novamente.');return false;}")
replace(" if(!ask){setSaveStatus('Arquivo alterado fora do aplicativo. Clique Salvar para conferir.');return false;}\n return await appConfirm('O arquivo '+handle.name+' foi modificado fora do aplicativo. Substituir esse arquivo pelos dados desta tela?');", " if(!ask){setSaveStatus('O conteúdo do JSON mudou. Confira antes de salvar.');return false;}\n return await appConfirm('O conteúdo do arquivo '+handle.name+' mudou desde que foi aberto. Substituir pelo que aparece nesta tela? Confirme apenas se não houver alterações mais recentes em outra aba ou aplicativo.');")
replace("async function finishFileSave(handle,revision){\n if(handle!==dataFileHandle)return false;\n const signature=await fileSignature(handle);\n if(!signature)throw Error('Não foi possível verificar a gravação.');\n knownFileSignature=signature;\n if(dataRevision===revision)hasUnsavedChanges=false;", "async function finishFileSave(handle,write){\n if(handle!==dataFileHandle)return false;\n const signature=await fileSignature(handle);\n if(signature===null)throw Error('Não foi possível verificar a gravação.');\n if(signature!==write.content){\n  setSaveStatus('Não salvo — o conteúdo mudou durante a gravação.');return false;\n }\n knownFileSignature=signature;\n if(dataRevision===write.revision)hasUnsavedChanges=false;")
replace("  return revision;\n });\n diskSaveQueue=job;return job;\n}\nasync function saveDataFile(askPermission=true){\n const handle=dataFileHandle;\n if(!handle){setSaveStatus('Abra um arquivo JSON para salvar.');return false;}\n if(!hasUnsavedChanges){setSaveStatus('Salvo');return true;}\n try{\n  // Permissao do Chrome so e solicitada por um clique explicito.\n  if(!await fileWriteAllowed(handle,askPermission)){\n   setSaveStatus('Não salvo — autorize o JSON pelo botão Salvar.');return false;\n  }\n  if(!await fileUnchanged(handle,askPermission)){\n   setSaveStatus('Não salvo — arquivo externo alterado ou indisponível.');return false;\n  }\n  const revision=await writeDataFile(handle);\n  return await finishFileSave(handle,revision);\n }catch(error){setSaveStatus('Não salvo — falha ao gravar o JSON.');return false;}\n}", "  return {revision,content};\n });\n diskSaveQueue=job;return job;\n}\n// Serializa verificacao, escrita e leitura final juntas. Sem isso, dois\n// salvamentos simultaneos comparam uma assinatura ainda desatualizada.\nfunction queueFileSave(handle,askPermission){\n const job=fileSaveQueue.catch(()=>{}).then(async()=>{\n  if(handle!==dataFileHandle)return false;\n  if(!hasUnsavedChanges){setSaveStatus('Salvo');return true;}\n  try{\n   // Permissao do Chrome so e solicitada por um clique explicito.\n   if(!await fileWriteAllowed(handle,askPermission)){\n    setSaveStatus('Não salvo — autorize o JSON pelo botão Salvar.');return false;\n   }\n   if(!await fileUnchanged(handle,askPermission)){\n    setSaveStatus('Não salvo — conflito no conteúdo ou arquivo indisponível.');return false;\n   }\n   const write=await writeDataFile(handle);\n   return await finishFileSave(handle,write);\n  }catch(error){setSaveStatus('Não salvo — falha ao gravar o JSON.');return false;}\n });\n fileSaveQueue=job.catch(()=>{});\n return job;\n}\nasync function saveDataFile(askPermission=true){\n const handle=dataFileHandle;\n if(!handle){setSaveStatus('Abra um arquivo JSON para salvar.');return false;}\n return await queueFileSave(handle,askPermission);\n}")
replace("  const revision=await writeDataFile(handle);\n  const signature=await fileSignature(handle);\n  if(!signature){setSaveStatus('Não foi possível verificar o JSON criado.');return false;}\n  dataFileHandle=handle;knownFileSignature=signature;\n  hasUnsavedChanges=dataRevision!==revision;", "  // Nao criar outra gravacao enquanto uma escrita anterior esta pendente.\n  await fileSaveQueue.catch(()=>{});\n  const write=await writeDataFile(handle);\n  const signature=await fileSignature(handle);\n  if(signature===null||signature!==write.content){setSaveStatus('Não foi possível verificar o JSON criado.');return false;}\n  dataFileHandle=handle;knownFileSignature=signature;\n  hasUnsavedChanges=dataRevision!==write.revision;")
replace("async function autoSaveDataFile(){\n if(!appReady||isApplyingData||!hasUnsavedChanges||!dataFileHandle)return false;\n const handle=dataFileHandle;\n try{\n  if(!await fileWriteAllowed(handle,false)){setSaveStatus('Não salvo — clique Salvar.');return false;}\n  if(!await fileUnchanged(handle,false))return false;\n  const revision=await writeDataFile(handle);\n  return await finishFileSave(handle,revision);\n }catch(error){setSaveStatus('Não salvo — falha ao gravar o JSON.');return false;}\n}", "async function autoSaveDataFile(){\n if(!appReady||isApplyingData||!hasUnsavedChanges||!dataFileHandle)return false;\n const handle=dataFileHandle;\n return await queueFileSave(handle,false);\n}")
replace("  const file=await handle.getFile();const parsed=JSON.parse(await file.text());", "  const file=await handle.getFile();const originalText=await file.text();const parsed=JSON.parse(originalText);")
replace("  dataFileHandle=handle;knownFileSignature=String(file.size)+':'+String(file.lastModified);", "  dataFileHandle=handle;knownFileSignature=originalText;")
path.write_text(s,encoding='utf-8')

test=Path('tests/autosave.test.js')
t=test.read_text(encoding='utf-8')
t=t.replace("assert(src.includes('fileWriteAllowed(handle,false)'),'Autosave apenas com permissão existente');", "assert(src.includes('queueFileSave(handle,false)'),'Autosave apenas com permissao existente');")
t=t.replace("assert(src.includes('fileWriteAllowed(handle,true)')||src.includes('fileWriteAllowed(handle,askPermission)'),'Salvar precisa permitir autorização por clique');", "assert(src.includes('fileWriteAllowed(handle,askPermission)'),'Salvar precisa permitir autorizacao por clique');")
t=t.replace("dataRevision=0,diskSaveTimer=null;'+fn('saveData')+fn('autoSaveDataFile')", "dataRevision=0,diskSaveTimer=null,fileSaveQueue=Promise.resolve();'+fn('saveData')+fn('queueFileSave')+fn('autoSaveDataFile')")
assert t!=test.read_text(encoding='utf-8'),'Teste autosave nao atualizado'
test.write_text(t,encoding='utf-8')

Path('tests/json-falso-conflito.test.js').write_text(r'''const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const src=html.match(/<script\s*>([\s\S]*?)<\/script>/)[1];
function fn(name){const re=new RegExp('^(?:async )?function '+name+'\\([^\\n]*\\)\\{[\\s\\S]*?^\\}\\n','m');const m=src.match(re);assert(m,'Funcao ausente: '+name);return m[0];}
assert(src.includes('knownFileSignature=originalText'),'Abertura deve registrar texto original e nao metadados');
assert(!src.includes("String(file.size)+':'+String(file.lastModified)"),'Comparacao por metadados permanece no codigo');
let disk='{"dados":1}',stamp=1,confirmacoes=0,gravacoes=0,perm=[];
const handle={name:'dados.json',queryPermission:async()=> 'granted',getFile:async()=>({size:disk.length,lastModified:stamp,text:async()=>disk}),createWritable:async()=>({write:async text=>{gravacoes++;disk=text},close:async()=>{stamp++},abort:async()=>{}})};
const statuses=[];
const ctx=vm.createContext({Promise,Date,Math,JSON,String,Number,Error,console,handle,setSaveStatus:x=>statuses.push(x),appConfirm:async()=>{confirmacoes++;return true}});
vm.runInContext('let dataFileHandle=handle,knownFileSignature=disk,hasUnsavedChanges=true,dataRevision=1,diskSaveQueue=Promise.resolve(),fileSaveQueue=Promise.resolve();'+
fn('fileSignature')+fn('fileWriteAllowed')+fn('fileUnchanged')+fn('writeDataFile')+fn('finishFileSave')+fn('queueFileSave')+fn('saveDataFile')+fn('autoSaveDataFile')+
'function dataPayload(){return {versao:2,dados:{exemplo:1}};} function setFileAccessState(){} let appReady=true,isApplyingData=false;',ctx);
(async()=>{
  // lastModified muda sem mudar o conteudo: nao eh conflito.
  stamp+=100;
  assert.strictEqual(await vm.runInContext('fileUnchanged(handle,false)',ctx),true);
  assert.strictEqual(await vm.runInContext('autoSaveDataFile()',ctx),true);
  assert.strictEqual(confirmacoes,0,'Falso alerta de conflito');
  assert.strictEqual(gravacoes,1);
  assert.strictEqual(vm.runInContext('hasUnsavedChanges',ctx),false);
  // Conteudo realmente modificado: autosave nao sobrescreve sem consentimento.
  disk='{"alterado_por_outra_aba":true}';
  vm.runInContext('hasUnsavedChanges=true;dataRevision++',ctx);
  const antes=gravacoes;
  assert.strictEqual(await vm.runInContext('autoSaveDataFile()',ctx),false);
  assert.strictEqual(gravacoes,antes);
  assert.strictEqual(confirmacoes,0);
  // Salvamento manual exige confirmacao e entao atualiza a base.
  assert.strictEqual(await vm.runInContext('saveDataFile(true)',ctx),true);
  assert.strictEqual(confirmacoes,1);
  assert.strictEqual(gravacoes,antes+1);
  // Dois salvamentos juntos nao podem disparar conflito entre si.
  vm.runInContext('hasUnsavedChanges=true;dataRevision++',ctx);
  const both=await Promise.all([vm.runInContext('autoSaveDataFile()',ctx),vm.runInContext('saveDataFile(true)',ctx)]);
  assert.strictEqual(gravacoes,antes+2);
  assert.strictEqual(confirmacoes,1);
  assert(both.every(Boolean));
  console.log('PASS: metadados instaveis ignorados, mudanca real protegida, gravacao verificada e salvamentos serializados');
})().catch(e=>{console.error(e);process.exitCode=1});
''',encoding='utf-8')
print('PATCH OK: index.html, autosave.test.js, json-falso-conflito.test.js')

const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const src=html.match(/<script\s*>([\s\S]*?)<\/script>/)[1];
function fn(name){const re=new RegExp('^(?:async )?function '+name+'\\([^\\n]*\\)\\{[\\s\\S]*?^\\}\\n','m');const m=src.match(re);assert(m,'Funcao ausente: '+name);return m[0];}
assert(src.includes('knownFileSignature=originalText'),'Abertura deve registrar texto original e nao metadados');
assert(!src.includes("String(file.size)+':'+String(file.lastModified)"),'Comparacao por metadados permanece no codigo');
let disk='{"dados":1}',stamp=1,confirmacoes=0,gravacoes=0,perm=[];
const handle={name:'dados.json',queryPermission:async()=> 'granted',getFile:async()=>({size:disk.length,lastModified:stamp,text:async()=>disk}),createWritable:async()=>({write:async text=>{gravacoes++;disk=text},close:async()=>{stamp++},abort:async()=>{}})};
const statuses=[];
const ctx=vm.createContext({Promise,Date,Math,JSON,String,Number,Error,console,handle,disk,setSaveStatus:x=>statuses.push(x),appConfirm:async()=>{confirmacoes++;return true}});
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

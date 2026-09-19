"""Patch determinístico do salvamento; executado somente na branch de revisão."""
from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def rep(old,new,n=1):
 global s
 assert s.count(old)==n, (old[:90],s.count(old),n)
 s=s.replace(old,new)
def func(name,new,async_=False):
 global s
 prefix='async function' if async_ else 'function'
 pattern=r'(?ms)^'+prefix+r' '+name+r'\([^\n]*\)\{.*?^\}\n'
 s,count=re.subn(pattern,lambda _:new.strip()+'\n',s)
 assert count==1,(name,count)

rep('    <button onclick="manualSave()" title="Salva as mudanças no arquivo de dados que você abriu ou escolheu.">Salvar</button>', '    <button onclick="manualSave()" title="Os dados já são guardados neste navegador. Clique para autorizar ou atualizar o arquivo JSON vinculado.">Salvar</button>')
rep('    <button onclick="saveAsDataFile()" title="Cria ou escolhe um arquivo no computador para guardar seus dados.">Salvar como</button>', '    <button onclick="saveAsDataFile()" title="Escolha um arquivo JSON para manter uma cópia sincronizada. O navegador exige o seletor de arquivos nesta operação.">Salvar como</button>')
rep('    <div class="save-status" id="save-status"></div>', '    <div class="save-status" id="save-status" role="status" aria-live="polite">Recuperando salvamento automático…</div>')
rep('let isApplyingData=false;', '''let isApplyingData=false;
let dataRevision=0;
let localSaveTimer=null;
let diskSaveTimer=null;
let localSaveQueue=Promise.resolve();
let diskSaveQueue=Promise.resolve();
let knownFileSignature=null;
let lastLocalSaveFailed=false;''')

functions=r'''
// Backup local permanente (IndexedDB). O site NUNCA pede acesso ao disco em temporizadores.
let localDbPromise=null;
function localDb(){
 if(!window.indexedDB)return Promise.reject(new Error('IndexedDB indisponível'));
 if(!localDbPromise)localDbPromise=new Promise((resolve,reject)=>{
  const req=window.indexedDB.open('meu-dinheiro-sessao',1);
  req.onupgradeneeded=()=>{if(!req.result.objectStoreNames.contains('dados'))req.result.createObjectStore('dados');};
  req.onsuccess=()=>resolve(req.result);
  req.onerror=()=>reject(req.error||new Error('Falha ao abrir banco local'));
 });
 return localDbPromise;
}
async function localGet(key){
 const db=await localDb();
 return new Promise((resolve,reject)=>{
  const tx=db.transaction('dados','readonly');const req=tx.objectStore('dados').get(key);
  tx.oncomplete=()=>resolve(req.result);tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);
 });
}
async function localSet(key,value){
 const db=await localDb();
 return new Promise((resolve,reject)=>{
  const tx=db.transaction('dados','readwrite');tx.objectStore('dados').put(value,key);
  tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);
 });
}
async function persistLocalSession(){
 if(!appReady||isApplyingData)return false;
 const revision=dataRevision;
 const snapshot={payload:JSON.stringify(dataPayload()),dirty:hasUnsavedChanges,updatedAt:Date.now(),fileName:dataFileHandle?dataFileHandle.name:''};
 localSaveQueue=localSaveQueue.catch(()=>{}).then(()=>localSet('session',snapshot));
 try{
  await localSaveQueue;lastLocalSaveFailed=false;
  if(revision===dataRevision){
   const suffix=dataFileHandle?(hasUnsavedChanges?' · JSON aguarda sincronização.':' · JSON sincronizado.'):' · use Salvar como para criar um JSON.';
   setSaveStatus('Dados guardados automaticamente neste navegador'+suffix);
  }
  return true;
 }catch(error){
  lastLocalSaveFailed=true;
  setSaveStatus('Falha no backup local! Use Salvar como para preservar seus dados.');
  return false;
 }
}
function scheduleLocalSave(){
 clearTimeout(localSaveTimer);
 localSaveTimer=setTimeout(()=>{void persistLocalSession();},400);
}
async function fileSignature(handle){
 try{const file=await handle.getFile();return String(file.size)+':'+String(file.lastModified);}catch{return null;}
}
async function fileWriteAllowed(handle,ask){
 if(!handle||typeof handle.queryPermission!=='function')return false;
 let result=await handle.queryPermission({mode:'readwrite'});
 if(result==='granted')return true;
 if(ask&&typeof handle.requestPermission==='function')result=await handle.requestPermission({mode:'readwrite'});
 return result==='granted';
}
async function fileUnchanged(handle,ask){
 if(!knownFileSignature)return true;
 const current=await fileSignature(handle);
 if(current===knownFileSignature)return true;
 if(!ask){setSaveStatus('O JSON foi alterado fora do aplicativo. Backup preservado no navegador; use Salvar para decidir.');return false;}
 return await appConfirm('O arquivo JSON foi alterado fora do aplicativo. Substituir o conteúdo dele pelos dados atualmente exibidos?');
}
async function finishFileSave(handle,revision){
 if(handle!==dataFileHandle)return;
 knownFileSignature=await fileSignature(handle);
 try{await localSet('fileSignature',knownFileSignature);}catch{lastLocalSaveFailed=true;}
 if(dataRevision===revision)hasUnsavedChanges=false;
 await persistLocalSession();
 setSaveStatus(hasUnsavedChanges?'Nova alteração aguardando o próximo salvamento.':'Arquivo JSON salvo automaticamente.');
}
async function restoreLocalSession(){
 const revision=dataRevision;
 try{
  const snapshot=await localGet('session');
  const handle=await localGet('fileHandle');
  const signature=await localGet('fileSignature');
  if(dataRevision!==revision){setSaveStatus('Alteração recente mantida.');return;}
  if(snapshot&&typeof snapshot.payload==='string'){
   applyDataFile(JSON.parse(snapshot.payload));
   dataRevision++;
   hasUnsavedChanges=!!snapshot.dirty;
  }
  if(handle&&handle.kind==='file')dataFileHandle=handle;
  knownFileSignature=typeof signature==='string'?signature:null;
  if(snapshot&&dataFileHandle){
   setSaveStatus('Dados e arquivo selecionado restaurados. '+(hasUnsavedChanges?'Backup local protegido; clique Salvar se o Chrome precisar autorizar o arquivo.':'Arquivo sincronizado na última utilização.'));
   if(hasUnsavedChanges){clearTimeout(diskSaveTimer);diskSaveTimer=setTimeout(()=>{void autoSaveDataFile();},10000);}
  }else if(snapshot){
   setSaveStatus('Dados recuperados do salvamento automático neste navegador. '+(snapshot.fileName?'Reabra '+snapshot.fileName+' se desejar sincronizar o JSON.':'Use Salvar como para criar uma cópia JSON.'));
  }else setSaveStatus('Salvamento automático ativado. Seus dados serão guardados neste navegador.');
 }catch(error){
  setSaveStatus('Não foi possível restaurar o backup do navegador. Abra seu último JSON para recuperar os dados.');
 }
}
'''
rep('function saveData(){',functions+'\nfunction saveData(){')
func('saveData',r'''function saveData(){
 if(!appReady||isApplyingData)return;
 hasUnsavedChanges=true;dataRevision++;
 setSaveStatus('Alteração registrada. Salvando backup automático…');
 scheduleLocalSave();
 clearTimeout(diskSaveTimer);
 diskSaveTimer=setTimeout(()=>{void autoSaveDataFile();},10000);
}''')
func('setSaveStatus',r'''function setSaveStatus(text){
 const el=document.getElementById('save-status');if(!el)return;
 el.textContent=(dataFileHandle?'Arquivo: '+dataFileHandle.name+' · ':'')+text;
}''')
func('manualSave',r'''function manualSave(){void saveDataFile();}''')
func('downloadDataFile',r'''function downloadDataFile(){
 const blob=new Blob([JSON.stringify(dataPayload(),null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob);const a=document.createElement('a');
 a.href=url;a.download='meu-dinheiro-dados.json';document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
 dataFileHandle=null;knownFileSignature=null;hasUnsavedChanges=false;
 void localSet('fileHandle',null);void localSet('fileSignature',null);
 void persistLocalSession();setSaveStatus('JSON baixado. O backup automático permanece neste navegador.');
}''')
func('writeDataFile',r'''async function writeDataFile(handle){
 const job=diskSaveQueue.catch(()=>{}).then(async()=>{
  const revision=dataRevision;
  const content=JSON.stringify(dataPayload(),null,2);
  const writable=await handle.createWritable();
  try{await writable.write(content);await writable.close();}catch(error){try{await writable.abort();}catch{}throw error;}
  return revision;
 });
 diskSaveQueue=job;return job;
}''',True)
func('saveDataFile',r'''async function saveDataFile(){
 await persistLocalSession();
 if(!dataFileHandle){setSaveStatus('Salvo no navegador. Use Salvar como para escolher um arquivo JSON.');return;}
 const handle=dataFileHandle;
 try{
  if(!await fileWriteAllowed(handle,true)){setSaveStatus('Backup salvo no navegador. Para editar o JSON, autorize o acesso ao arquivo no Chrome.');return;}
  if(!await fileUnchanged(handle,true))return;
  const revision=await writeDataFile(handle);
  await finishFileSave(handle,revision);
 }catch(error){appAlert('Não consegui atualizar o JSON. Seus dados continuam guardados neste navegador.');setSaveStatus('Falha na sincronização com o arquivo JSON.');}
}''',True)
func('saveAsDataFile',r'''async function saveAsDataFile(){
 try{
  if(!window.showSaveFilePicker){downloadDataFile();return;}
  const handle=await window.showSaveFilePicker({suggestedName:dataFileHandle?dataFileHandle.name:'meu-dinheiro-dados.json',types:[{description:'Dados Meu dinheiro',accept:{'application/json':['.json']}}]});
  const revision=await writeDataFile(handle);
  dataFileHandle=handle;knownFileSignature=await fileSignature(handle);
  hasUnsavedChanges=dataRevision!==revision;
  try{await localSet('fileHandle',handle);await localSet('fileSignature',knownFileSignature);}catch{appAlert('JSON salvo, mas não consegui lembrar o arquivo para a próxima visita.');}
  await persistLocalSession();setSaveStatus('JSON selecionado e salvo. Próximas alterações serão sincronizadas automaticamente quando autorizadas.');
 }catch(error){if(error&&error.name==='AbortError')return;appAlert('Não consegui salvar o JSON. O backup no navegador continua disponível.');}
}''',True)
func('autoSaveDataFile',r'''async function autoSaveDataFile(){
 if(!appReady||isApplyingData||!hasUnsavedChanges)return;
 await persistLocalSession();
 if(!dataFileHandle){setSaveStatus('Salvo automaticamente no navegador. Use Salvar como para vincular um JSON.');return;}
 const handle=dataFileHandle;
 try{
  if(!await fileWriteAllowed(handle,false)){setSaveStatus('Backup automático salvo no navegador. Clique Salvar uma vez para autorizar a atualização do JSON.');return;}
  if(!await fileUnchanged(handle,false))return;
  const revision=await writeDataFile(handle);
  await finishFileSave(handle,revision);
 }catch(error){setSaveStatus('Backup salvo no navegador; não consegui sincronizar o JSON. Use Salvar.');}
}''',True)
func('openDataFile',r'''async function openDataFile(){
 try{
  if(hasUnsavedChanges&&!await appConfirm('Há dados guardados somente neste navegador. Abrir outro arquivo substituirá a sessão atual. Continuar?'))return;
  if(!window.showOpenFilePicker){document.getElementById('import-file').click();return;}
  const handles=await window.showOpenFilePicker({multiple:false,types:[{description:'Dados Meu dinheiro',accept:{'application/json':['.json']}}]});
  const handle=handles[0];const file=await handle.getFile();const parsed=JSON.parse(await file.text());
  applyDataFile(parsed);dataFileHandle=handle;knownFileSignature=String(file.size)+':'+String(file.lastModified);dataRevision++;
  try{await localSet('fileHandle',handle);await localSet('fileSignature',knownFileSignature);}catch{appAlert('Arquivo aberto, mas o navegador não conseguiu lembrar sua seleção.');}
  await persistLocalSession();
  setSaveStatus('Arquivo reaberto e preservado nesta sessão. Se necessário, clique Salvar uma vez para autorizar a atualização automática do JSON.');
 }catch(error){if(error&&error.name==='AbortError')return;appAlert('Não consegui abrir esse JSON. Seus dados atuais não foram apagados.');}
}''',True)
func('importData',r'''async function importData(event){
 const file=event.target.files&&event.target.files[0];if(!file)return;
 if(hasUnsavedChanges&&!await appConfirm('Há alterações guardadas neste navegador. Substituir a sessão atual pelo JSON importado?')){event.target.value='';return;}
 const reader=new FileReader();
 reader.onload=async()=>{
  try{
   const parsed=JSON.parse(reader.result);applyDataFile(parsed);
   dataFileHandle=null;knownFileSignature=null;dataRevision++;
   await localSet('fileHandle',null);await localSet('fileSignature',null);
   await persistLocalSession();setSaveStatus('JSON importado e guardado neste navegador. Use Salvar como para vincular um arquivo editável.');
  }catch(error){appAlert('Não consegui importar ou guardar o JSON. Confira o arquivo e tente novamente.');}
  finally{event.target.value='';}
 };
 reader.readAsText(file,'utf-8');
}''',True)
rep('setInterval(autoSaveDataFile,3*60*1000);','setInterval(()=>{if(hasUnsavedChanges)void autoSaveDataFile();},10000);')
rep("document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&hasUnsavedChanges&&dataFileHandle)autoSaveDataFile();});", "document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&hasUnsavedChanges){void persistLocalSession();void autoSaveDataFile();}});\nvoid restoreLocalSession();")
rep("  setSaveStatus('Saldo definido. Use Salvar ou Salvar como para guardar no arquivo de dados.');", "  setSaveStatus('Saldo definido. Backup automático ativado; o JSON será sincronizado quando autorizado.');")
assert not re.search(r'(?<![\w.])(?:alert|confirm|prompt)\s*\(',s[s.index('<script>'):]),'Aviso nativo encontrado'
p.write_text(s,encoding='utf-8')
print('PATCH_AUTOSAVE_OK')

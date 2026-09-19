from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
old='''async function saveDataFile(){
 await persistLocalSession();
 if(!dataFileHandle){setSaveStatus('Salvo no navegador. Use Salvar como para escolher um arquivo JSON.');return;}
 const handle=dataFileHandle;
 try{
  if(!await fileWriteAllowed(handle,true)){setSaveStatus('Backup salvo no navegador. Para editar o JSON, autorize o acesso ao arquivo no Chrome.');return;}
  if(!await fileUnchanged(handle,true))return;
  const revision=await writeDataFile(handle);
  await finishFileSave(handle,revision);
 }catch(error){appAlert('Não consegui atualizar o JSON. Seus dados continuam guardados neste navegador.');setSaveStatus('Falha na sincronização com o arquivo JSON.');}
}'''
new='''async function saveDataFile(){
 const handle=dataFileHandle;
 if(!handle){
  const localSaved=await persistLocalSession();
  setSaveStatus(localSaved?'Salvo no navegador. Use Salvar como para escolher um arquivo JSON.':'Backup local indisponível. Use Salvar como para preservar seus dados.');
  return;
 }
 try{
  // A solicitação de permissão precisa acontecer no gesto do clique, antes de IndexedDB.
  if(!await fileWriteAllowed(handle,true)){
   await persistLocalSession();
   setSaveStatus('Backup salvo no navegador. Para editar o JSON, autorize o acesso ao arquivo no Chrome.');
   return;
  }
  await persistLocalSession();
  if(!await fileUnchanged(handle,true))return;
  const revision=await writeDataFile(handle);
  await finishFileSave(handle,revision);
 }catch(error){appAlert('Não consegui atualizar o JSON. Seus dados continuam guardados neste navegador.');setSaveStatus('Falha na sincronização com o arquivo JSON.');}
}'''
assert s.count(old)==1,s.count(old)
p.write_text(s.replace(old,new),encoding='utf-8')
print('PERMISSION_USER_ACTIVATION_OK')

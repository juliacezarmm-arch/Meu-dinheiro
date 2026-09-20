from pathlib import Path


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: esperado 1 trecho, encontrados {count}')
    return text.replace(old, new, 1)

p = Path('index.html')
s = p.read_text(encoding='utf-8')
s = once(s, '.data-tools{display:grid;grid-template-columns:repeat(3,1fr);', '.data-tools{display:grid;grid-template-columns:repeat(4,1fr);', 'quatro controles')
s = once(s, '</style>\n</head>', '''/* O documento JSON e a unica fonte ativa. Nenhum formulario e editavel sem arquivo. */
body.file-closed .nav,body.file-closed .page{opacity:.45;pointer-events:none}
#refresh-file-name{font-size:13px;color:#9FE1CB;overflow-wrap:anywhere}
#refresh-error{font-size:12px;color:#ffb3b3;margin-top:12px}
@media(max-width:520px){#refresh-overlay .site-dialog-actions{flex-direction:column-reverse}#refresh-overlay .site-dialog-actions button{width:100%}}
</style>
</head>''', 'estilos')
start = s.index('  <div class="data-tools">')
end = s.index('  <nav class="nav">', start)
s = s[:start] + '''  <div class="data-tools">
    <button type="button" onclick="openDataFile()" title="Abra um JSON para consultar e editar seus registros.">Abrir dados</button>
    <button type="button" onclick="manualSave()" title="Grava diretamente as alteracoes no arquivo JSON aberto.">Salvar</button>
    <button type="button" onclick="saveAsDataFile()" title="Cria um JSON novo ou salva os dados em outro arquivo.">Salvar como</button>
    <button type="button" onclick="atualizarAplicativo()" title="Atualiza o aplicativo, fechando o arquivo atual.">Atualizar</button>
    <div class="save-status" id="save-status" role="status" aria-live="polite">Abra um arquivo JSON para começar.</div>
  </div>
''' + s[end:]
needle = '<div id="card-editor" class="site-dialog"'
assert s.count(needle) == 1
refresh_html = '''<div id="refresh-overlay" class="site-dialog" role="dialog" aria-modal="true" aria-labelledby="refresh-title" hidden><div class="site-dialog-panel">
  <div class="site-dialog-heading"><span class="site-dialog-icon" aria-hidden="true">↻</span><h2 id="refresh-title">Salvar alterações?</h2></div>
  <p id="refresh-file-name"></p><p id="refresh-error" role="alert" hidden></p>
  <div class="site-dialog-actions"><button type="button" class="site-button quiet" id="refresh-cancel" onclick="cancelarAtualizacao()">Cancelar</button><button type="button" class="site-button quiet" id="refresh-discard" onclick="atualizarSemSalvar()">Atualizar sem salvar</button><button type="button" class="site-button primary" id="refresh-save" onclick="salvarEAtualizar()">Salvar e atualizar</button></div>
</div></div>
'''
s = once(s, needle, refresh_html + needle, 'dialogo de atualizacao')
s = once(s, '''let localSaveTimer=null;
let diskSaveTimer=null;
let localSaveQueue=Promise.resolve();
let diskSaveQueue=Promise.resolve();
let knownFileSignature=null;
let lastLocalSaveFailed=false;''', '''let diskSaveTimer=null;
let diskSaveQueue=Promise.resolve();
let knownFileSignature=null;
let refreshBusy=false;''', 'estado sem indexeddb')
s = once(s, "  setSaveStatus('Saldo definido. Backup automático ativado; o JSON será sincronizado quando autorizado.');\n", '', 'saldo sem status antigo')
start = s.index('// Backup local permanente (IndexedDB).')
end = s.index('function applyDataFile(data){', start)
s = s[:start] + '''// O JSON e a unica fonte ativa. Os backups antigos do navegador nao sao lidos,
// atualizados nem apagados automaticamente: poderao ser recuperados separadamente
// se o usuario ainda nao tiver exportado uma versao antiga.
function setFileAccessState(open){
 document.body.classList.toggle('file-closed',!open);
 for(const area of document.querySelectorAll('.nav,.page'))area.inert=!open;
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
 if(!knownFileSignature)return false;
 const current=await fileSignature(handle);
 if(!current){setSaveStatus('Arquivo indisponível — abra o JSON novamente.');return false;}
 if(current===knownFileSignature)return true;
 if(!ask){setSaveStatus('Arquivo alterado fora do aplicativo. Clique Salvar para conferir.');return false;}
 return await appConfirm('O arquivo '+handle.name+' foi modificado fora do aplicativo. Substituir esse arquivo pelos dados desta tela?');
}
async function finishFileSave(handle,revision){
 if(handle!==dataFileHandle)return false;
 const signature=await fileSignature(handle);
 if(!signature)throw Error('Não foi possível verificar a gravação.');
 knownFileSignature=signature;
 if(dataRevision===revision)hasUnsavedChanges=false;
 setSaveStatus(hasUnsavedChanges?'Não salvo':'Salvo');
 return !hasUnsavedChanges;
}
function saveData(){
 if(!appReady||isApplyingData||!dataFileHandle)return;
 hasUnsavedChanges=true;dataRevision++;
 setSaveStatus('Não salvo');
 clearTimeout(diskSaveTimer);
 diskSaveTimer=setTimeout(()=>{void autoSaveDataFile();},10000);
}
function setSaveStatus(text){
 const el=document.getElementById('save-status');if(!el)return;
 el.textContent=dataFileHandle?(dataFileHandle.name+(text?' · '+text:'')):(text||'Abra um arquivo JSON para começar.');
}
function manualSave(){void saveDataFile(true);}
function dataPayload(){
 return {versao:2,exportadoEm:new Date().toISOString(),dados:S};
}
''' + s[end:]
start = s.index('function downloadDataFile(){')
end = s.index('// O fechamento do banco não é a data de pagamento.', start)
s = s[:start] + '''async function writeDataFile(handle){
 const job=diskSaveQueue.catch(()=>{}).then(async()=>{
  const revision=dataRevision;
  const content=JSON.stringify(dataPayload(),null,2);
  const writable=await handle.createWritable();
  try{await writable.write(content);await writable.close();}catch(error){try{await writable.abort();}catch{}throw error;}
  return revision;
 });
 diskSaveQueue=job;return job;
}
async function saveDataFile(askPermission=true){
 const handle=dataFileHandle;
 if(!handle){setSaveStatus('Abra um arquivo JSON para salvar.');return false;}
 if(!hasUnsavedChanges){setSaveStatus('Salvo');return true;}
 try{
  // Permissao do Chrome so e solicitada por um clique explicito.
  if(!await fileWriteAllowed(handle,askPermission)){
   setSaveStatus('Não salvo — autorize o JSON pelo botão Salvar.');return false;
  }
  if(!await fileUnchanged(handle,askPermission)){
   setSaveStatus('Não salvo — arquivo externo alterado ou indisponível.');return false;
  }
  const revision=await writeDataFile(handle);
  return await finishFileSave(handle,revision);
 }catch(error){setSaveStatus('Não salvo — falha ao gravar o JSON.');return false;}
}
async function saveAsDataFile(){
 if(!window.showSaveFilePicker){appAlert('Este navegador não permite vincular um JSON para edição. Use um navegador compatível no computador.');return false;}
 try{
  const handle=await window.showSaveFilePicker({suggestedName:dataFileHandle?dataFileHandle.name:'meu-dinheiro-dados.json',types:[{description:'Dados Meu dinheiro',accept:{'application/json':['.json']}}]});
  if(!await fileWriteAllowed(handle,true)){setSaveStatus('Não salvo — arquivo sem permissão de gravação.');return false;}
  const revision=await writeDataFile(handle);
  const signature=await fileSignature(handle);
  if(!signature){setSaveStatus('Não foi possível verificar o JSON criado.');return false;}
  dataFileHandle=handle;knownFileSignature=signature;
  hasUnsavedChanges=dataRevision!==revision;
  setFileAccessState(true);
  setSaveStatus(hasUnsavedChanges?'Não salvo':'Salvo');
  return !hasUnsavedChanges;
 }catch(error){
  if(error&&error.name==='AbortError')return false;
  setSaveStatus('Falha ao criar ou salvar o JSON.');return false;
 }
}
async function autoSaveDataFile(){
 if(!appReady||isApplyingData||!hasUnsavedChanges||!dataFileHandle)return false;
 const handle=dataFileHandle;
 try{
  if(!await fileWriteAllowed(handle,false)){setSaveStatus('Não salvo — clique Salvar.');return false;}
  if(!await fileUnchanged(handle,false))return false;
  const revision=await writeDataFile(handle);
  return await finishFileSave(handle,revision);
 }catch(error){setSaveStatus('Não salvo — falha ao gravar o JSON.');return false;}
}
async function openDataFile(){
 if(hasUnsavedChanges){setSaveStatus('Não salvo — salve antes de abrir outro JSON.');return false;}
 if(!window.showOpenFilePicker){
  appAlert('Este navegador não permite editar o mesmo arquivo JSON diretamente. Abra o Meu Dinheiro em um navegador compatível no computador.');return false;
 }
 try{
  const handles=await window.showOpenFilePicker({multiple:false,types:[{description:'Dados Meu dinheiro',accept:{'application/json':['.json']}}]});
  const handle=handles[0];if(!handle)return false;
  const file=await handle.getFile();const parsed=JSON.parse(await file.text());
  validarDadosImportados(parsed);
  if(!await fileWriteAllowed(handle,true)){
   setSaveStatus('Permita editar o arquivo JSON para continuar.');return false;
  }
  const previousHandle=dataFileHandle,previousSignature=knownFileSignature;
  dataFileHandle=handle;knownFileSignature=String(file.size)+':'+String(file.lastModified);
  try{applyDataFile(parsed);}catch(error){
   dataFileHandle=previousHandle;knownFileSignature=previousSignature;
   setFileAccessState(!!previousHandle);throw error;
  }
  dataRevision++;
  setFileAccessState(true);
  setSaveStatus(hasUnsavedChanges?'Não salvo — recorrência atualizada.':'Salvo');
  return true;
 }catch(error){
  if(error&&error.name==='AbortError')return false;
  appAlert('Não consegui abrir esse JSON. O arquivo original não foi alterado.');return false;
 }
}
function cancelarAtualizacao(){
 if(refreshBusy)return;
 document.getElementById('refresh-overlay').hidden=true;
}
function atualizarAplicativo(){
 if(refreshBusy)return;
 if(!hasUnsavedChanges){window.location.reload();return;}
 const overlay=document.getElementById('refresh-overlay');
 document.getElementById('refresh-file-name').textContent=dataFileHandle?dataFileHandle.name:'Arquivo JSON';
 document.getElementById('refresh-error').hidden=true;
 overlay.hidden=false;
 document.getElementById('refresh-cancel').focus();
}
function atualizarSemSalvar(){
 if(refreshBusy)return;
 hasUnsavedChanges=false;
 dataFileHandle=null;knownFileSignature=null;
 document.getElementById('refresh-overlay').hidden=true;
 window.location.reload();
}
async function salvarEAtualizar(){
 if(refreshBusy)return;
 refreshBusy=true;
 const button=document.getElementById('refresh-save');button.disabled=true;
 const error=document.getElementById('refresh-error');error.hidden=true;
 try{
  const success=await saveDataFile(true);
  if(success&&!hasUnsavedChanges){
   document.getElementById('refresh-overlay').hidden=true;
   dataFileHandle=null;knownFileSignature=null;
   window.location.reload();return;
  }
  error.textContent='Não foi possível salvar. Seus dados ainda estão nesta tela.';error.hidden=false;
 }finally{refreshBusy=false;button.disabled=false;}
}
// Em F5/atualização pela barra, o Chrome só permite seu aviso padrão.
// A janela personalizada com botão Salvar é exclusiva do botão Atualizar do app.
window.addEventListener('beforeunload',event=>{
 if(hasUnsavedChanges){event.preventDefault();event.returnValue='';}
});
''' + s[end:]
s = once(s, '''appReady=true;
setInterval(()=>{if(hasUnsavedChanges)void autoSaveDataFile();},10000);
setInterval(updateResumo,5*60*1000);
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&hasUnsavedChanges){void persistLocalSession();void autoSaveDataFile();}});
void restoreLocalSession();''', '''appReady=true;
setFileAccessState(false);
setSaveStatus('Abra um arquivo JSON para começar.');
setInterval(()=>{if(hasUnsavedChanges)void autoSaveDataFile();},10000);
setInterval(updateResumo,5*60*1000);''', 'inicializacao sem restauracao')
s = once(s, '<script src="js/recorrentes.js?v=20260920-dia2"></script>', '<script src="js/recorrentes.js?v=20260920-json1"></script>', 'script atualizado')
p.write_text(s,encoding='utf-8')

p = Path('tests/finance.test.js')
t = p.read_text(encoding='utf-8')
t = once(t, "assert(html.includes('applyDataFile(parsed);dataFileHandle=handle;'),'Handle só é trocado após validação');", "assert(html.includes('validarDadosImportados(parsed);')&&html.includes('dataFileHandle=handle;knownFileSignature='),'Arquivo só é associado após validação');", 'teste de validacao do arquivo')
p.write_text(t,encoding='utf-8')
p = Path('tests/card-ux.test.js')
t = p.read_text(encoding='utf-8')
t = once(t, "assert(!html.includes('beforeunload'),'A saída do site não pode acionar confirmação do navegador');", "assert(html.includes('beforeunload'),'F5 deve advertir quando houver alterações não salvas');", 'teste de f5')
p.write_text(t,encoding='utf-8')
p = Path('tests/recorrentes.test.js')
t = p.read_text(encoding='utf-8')
t = once(t,'<script src="js/recorrentes.js?v=20260920-dia2"></script>','<script src="js/recorrentes.js?v=20260920-json1"></script>','teste do cache')
p.write_text(t,encoding='utf-8')
p = Path('tests/recorrentes-browser-smoke.py')
t = p.read_text(encoding='utf-8')
t = once(t,'<script src="js/recorrentes.js?v=20260920-conta2"></script>','<script src="js/recorrentes.js?v=20260920-json1"></script>','cache smoke')
t = once(t, " if(!document.getElementById('recorrentes-area'))throw Error('Cadastro ausente');", " if(!document.body.classList.contains('file-closed'))throw Error('Sem JSON a tela deve ficar bloqueada');\n if(!document.getElementById('recorrentes-area'))throw Error('Cadastro ausente');", 'smoke bloqueio')
t = once(t, " S.saldoInicial={valor:500,data:isoDate(d.getFullYear(),d.getMonth(),d.getDate()),idsIgnorados:[]};", " dataFileHandle={kind:'file',name:'teste.json',getFile:async()=>({size:1,lastModified:1}),queryPermission:async()=> 'granted',createWritable:async()=>({write:async()=>{},close:async()=>{}})};\n knownFileSignature='1:1';setFileAccessState(true);\n S.saldoInicial={valor:500,data:isoDate(d.getFullYear(),d.getMonth(),d.getDate()),idsIgnorados:[]};", 'smoke json mock')
p.write_text(t,encoding='utf-8')

p = Path('tests/autosave.test.js')
p.write_text('''const fs=require('fs'),assert=require('assert'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const match=html.match(/<script\\s*>([\\s\\S]*?)<\\/script>/);
assert(match,'Script principal ausente');
const src=match[1];
for(const name of ['fileSignature','fileWriteAllowed','fileUnchanged','writeDataFile','finishFileSave','saveDataFile','autoSaveDataFile','saveAsDataFile','openDataFile','atualizarAplicativo','atualizarSemSalvar','salvarEAtualizar','setFileAccessState'])assert(src.includes('function '+name+'('),'Função ausente: '+name);
for(const token of ['indexedDB','localStorage','persistLocalSession','restoreLocalSession','localSet(','localGet(','downloadDataFile(','scheduleLocalSave('])assert(!src.includes(token),'Persistência no navegador proibida: '+token);
assert(src.includes("window.addEventListener('beforeunload'"),'F5 precisa proteger alterações pendentes');
assert(src.includes('fileWriteAllowed(handle,false)'),'Autosave apenas com permissão existente');
assert(src.includes('fileWriteAllowed(handle,true)')||src.includes('fileWriteAllowed(handle,askPermission)'),'Salvar precisa permitir autorização por clique');
for(const id of ['refresh-overlay','refresh-save','refresh-discard','refresh-cancel','refresh-file-name'])assert(html.includes('id="'+id+'"'),'Ação do diálogo ausente: '+id);
assert(html.includes('Salvar e atualizar')&&html.includes('Atualizar sem salvar'),'Opções de atualização incompletas');
assert(!/(?<![\\w.])(?:alert|confirm|prompt)\\s*\\(/.test(src),'Proibido usar alert/confirm/prompt nativos');
assert(src.includes('setFileAccessState(false)'),'O site deve iniciar sem documento ativo');
assert(!src.includes('void restoreLocalSession()'),'Proibido restaurar sessão anterior');
function fn(name){const re=new RegExp('^(?:async )?function '+name+'\\\\([^\\\\n]*\\\\)\\\\{.*?^\\\\}\\\\n','ms');const m=src.match(re);assert(m,'Não extraiu '+name);return m[0];}
let timer=0,write=0,permission=[];
const ctx=vm.createContext({console,Promise,Error,Date,Number,String,JSON,setTimeout:(f,n)=>{timer=n;return 1},clearTimeout:()=>{},fileWriteAllowed:async(h,ask)=>{permission.push(ask);return true;},fileUnchanged:async()=>true,writeDataFile:async()=>{write++;return 1;},finishFileSave:async()=>{vm.runInContext('hasUnsavedChanges=false',ctx);return true;},setSaveStatus:()=>{}});
vm.runInContext('let dataFileHandle=null,hasUnsavedChanges=false,appReady=true,isApplyingData=false,dataRevision=0,diskSaveTimer=null;'+fn('saveData')+fn('autoSaveDataFile'),ctx);
vm.runInContext('saveData()',ctx);
assert.strictEqual(vm.runInContext('hasUnsavedChanges',ctx),false,'Sem arquivo nao ha alteracoes permitidas');
vm.runInContext("dataFileHandle={name:'teste.json'};saveData()",ctx);
assert.strictEqual(vm.runInContext('hasUnsavedChanges',ctx),true);
assert.strictEqual(timer,10000,'Somente JSON em 10 segundos');
(async()=>{await vm.runInContext('autoSaveDataFile()',ctx);assert.deepStrictEqual(permission,[false]);assert.strictEqual(write,1);assert.strictEqual(vm.runInContext('hasUnsavedChanges',ctx),false);console.log('PASS: JSON exclusivo, bloqueio sem arquivo, autosave autorizado, aviso F5 e diálogo de atualização');})().catch(e=>{console.error(e);process.exitCode=1});
''',encoding='utf-8')
print('PATCH OK: salvamento somente JSON; dialogo Atualizar; backups antigos intactos; testes adaptados')

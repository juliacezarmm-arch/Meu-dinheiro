const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const body=html.match(/<script\s*>([\s\S]*?)<\/script>/);
assert(body,'Script do app não encontrado');
const src=body[1];fs.writeFileSync('/tmp/meu-dinheiro-validar.js',src);
for(const name of ['localDb','localGet','localSet','persistLocalSession','restoreLocalSession','scheduleLocalSave','fileSignature','fileWriteAllowed','fileUnchanged','writeDataFile','finishFileSave','saveDataFile','autoSaveDataFile'])assert(src.includes('function '+name+'('),'Função ausente: '+name);
assert(src.includes("indexedDB.open('meu-dinheiro-sessao',1)"),'Backup persistente não configurado');
assert(src.includes("localSet('fileHandle',handle)"),'Identificador do arquivo precisa ser lembrado');
assert(src.includes("localGet('fileHandle')"),'Identificador do arquivo não é restaurado');
assert(src.includes('setInterval(()=>{if(hasUnsavedChanges)void autoSaveDataFile();},10000)'),'Autosave deve repetir a cada 10 segundos');
assert(!src.includes('setInterval(autoSaveDataFile,3*60*1000)'),'Não manter intervalo antigo de três minutos');
assert(!html.includes('beforeunload'),'Não instalar alerta de fechamento nativo');
assert(!/(?<![\w.])(?:alert|confirm|prompt)\s*\(/.test(src),'Caixas nativas de avisos não podem ser usadas');
assert(src.includes('if(!await fileWriteAllowed(handle,false))'),'Autosave não pode solicitar autorização do Chrome');
assert(src.includes('fileWriteAllowed(handle,true)'),'A permissão de escrita deve depender de clique manual');
const fn=name=>{
 const r=new RegExp('(?ms)^(?:async )?function '+name+'\\([^\\n]*\\)\\{.*?^\\}\\n');
 const match=src.match(r);assert(match,'Não consegui obter '+name);return match[0];
};
const timers=[],status=[],actions=[];
const ctx=vm.createContext({
 console,Date,JSON,Promise,Error,Number,String,Math,
 setTimeout:(callback,delay)=>{timers.push({callback,delay});return timers.length;},clearTimeout:()=>{},
 document:{getElementById:()=>({textContent:''})},
 localSet:async()=>{},localGet:async key=>key==='session'?{payload:JSON.stringify({versao:2,dados:{extrato:[{id:1,tipo:'entrada',data:'2026-09-19',val:10}],cartao:[],invest:[],cartoes:[]}}),dirty:true,fileName:'dados.json'}:key==='fileHandle'?{kind:'file',name:'dados.json'}:key==='fileSignature'?'8:1':null,
 persistLocalSession:async()=>true,
 fileWriteAllowed:async(handle,prompt)=>{actions.push('permission:'+prompt);return false;},
 fileUnchanged:async()=>true,writeDataFile:async()=>{actions.push('write');return 1;},finishFileSave:async()=>{},
 setSaveStatus:x=>status.push(x),appAlert:x=>{throw Error(x)},appConfirm:async()=>true,
 applyDataFile:data=>{vm.runInContext('S.extrato='+JSON.stringify(data.dados.extrato)+';hasUnsavedChanges=false',ctx);},
 dataPayload:()=>({versao:2}),
});
vm.runInContext("let dataFileHandle=null;let hasUnsavedChanges=false;let appReady=true;let isApplyingData=false;let dataRevision=0;let localSaveTimer=null;let diskSaveTimer=null;let knownFileSignature=null;const S={extrato:[]};"+['saveData','scheduleLocalSave','autoSaveDataFile','restoreLocalSession'].filter(x=>!['scheduleLocalSave'].includes(x)).map(fn).join('\n')+"function scheduleLocalSave(){setTimeout(()=>{},400)}",ctx);
(async()=>{
 await vm.runInContext('restoreLocalSession()',ctx);
 assert.strictEqual(vm.runInContext('S.extrato.length',ctx),1,'Restauração tem de recuperar dados do backup');
 assert.strictEqual(vm.runInContext('dataFileHandle.name',ctx),'dados.json','Atualização não pode perder a seleção');
 vm.runInContext('saveData()',ctx);
 assert.strictEqual(vm.runInContext('hasUnsavedChanges',ctx),true);
 assert(timers.some(x=>x.delay===10000),'Mudança deve agendar sincronização em 10 segundos');
 await vm.runInContext('autoSaveDataFile()',ctx);
 assert(actions.includes('permission:false'),'Autosave só consulta permissão, nunca a solicita');
 assert(!actions.includes('write'),'Sem autorização, não é permitido tentar modificar arquivo');
 assert(status.some(x=>x.includes('Backup automático salvo no navegador')),'O backup local deve ser comunicado dentro do app');
 console.log('PASS: salvamento a cada 10 s, recuperação de sessão e JSON, permissão somente sob clique e nenhuma notificação nativa');
})().catch(e=>{console.error(e);process.exitCode=1;});

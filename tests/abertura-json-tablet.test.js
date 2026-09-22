const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const src=html.match(/<script\s*>([\s\S]*?)<\/script>/)[1];
const match=src.match(/^async function openDataFile\(\)\{[\s\S]*?^\}\n/m);
assert(match,'Rotina de abertura ausente');
assert(html.includes('id="json-permission-button"'),'Botao de autorizacao faltando');
const permissionFn=src.match(/^function autorizarJsonPendente\(\)\{[\s\S]*?^\}\n/m);assert(permissionFn,'Rotina de permissao por clique ausente');
assert(match[0].indexOf('fileWriteAllowed(handle,true)')<match[0].indexOf('handle.getFile()'),'Pedir autorizacao antes de consumir a ativacao lendo o arquivo');
function scenario({text='{"versao":2,"dados":{"extrato":[]}}',allow=true,readError=false,invalidSchema=false,renderError=false}={}){
 const seen={alerts:[],statuses:[],read:0,asked:0,writes:0,loaded:0,activation:true,opened:[]};
 let permitted=allow;
 const handle={name:'dados.json',getFile:async()=>{seen.read++;seen.activation=false;if(readError)throw Error('Falha de leitura');return{text:async()=>text};},requestPermission:()=>{seen.manualPermission=(seen.manualPermission||0)+1;assert(seen.activation,'A permissao por clique nao pode esperar leitura ou outras promises');permitted=true;return Promise.resolve('granted');}};
 const permissionButton={hidden:true,disabled:false};
 const S={extrato:[{id:99,val:10}],cartao:[],invest:[],cartoes:[],saldoInicial:null};
 const old=S.extrato;
 const ctx=vm.createContext({Promise,JSON,SyntaxError,Error,Number,String,Array,console,S,
  window:{showOpenFilePicker:async()=>[handle]},
  document:{getElementById:id=>id==='json-permission-button'?permissionButton:null},
  fileWriteAllowed:async()=>{seen.asked++;assert(seen.activation,'Chrome perdeu ativacao antes de solicitar permissao');return permitted;},
  validarDadosImportados:()=>{if(invalidSchema)throw Error('Identificador duplicado em extrato');},
  applyDataFile:()=>{seen.loaded++;S.extrato=[{id:1,val:20}];if(renderError)throw Error('Falha na tela');},
  appAlert:m=>seen.alerts.push(m),setSaveStatus:m=>seen.statuses.push(m),setFileAccessState:b=>seen.opened.push(b)});
 vm.runInContext('let hasUnsavedChanges=false,dataFileHandle=null,knownFileSignature=null,dataRevision=0,isApplyingData=false,pendingJsonHandle=null,authorizedJsonHandle=null;'+permissionFn[0]+match[0],ctx);
 return {seen,handle,S,old,run:()=>vm.runInContext('openDataFile()',ctx),ctx};
}
(async()=>{
 let x=scenario();assert.strictEqual(await x.run(),true);assert.strictEqual(x.seen.asked,1);assert.strictEqual(x.seen.read,1);assert.strictEqual(x.seen.writes,0);assert.strictEqual(x.seen.loaded,1);assert.strictEqual(x.S.extrato[0].id,1);assert(x.seen.statuses.includes('Salvo'));
 x=scenario({allow:false});assert.strictEqual(await x.run(),false);assert.strictEqual(x.seen.read,0);assert.strictEqual(x.seen.loaded,0);assert(/não autorizou/.test(x.seen.alerts[0]));assert.strictEqual(x.S.extrato,x.old);
 assert.strictEqual(await vm.runInContext('autorizarJsonPendente()',x.ctx),true,'Clique de autorizacao deve abrir o MESMO arquivo');
 assert.strictEqual(x.seen.manualPermission,1);assert.strictEqual(x.seen.read,1);assert.strictEqual(x.seen.loaded,1);assert.strictEqual(x.S.extrato[0].id,1);assert.strictEqual(x.seen.writes,0);
 x=scenario({text:'{JSON incompleto'});assert.strictEqual(await x.run(),false);assert.strictEqual(x.seen.loaded,0);assert(/não contém um JSON válido/.test(x.seen.alerts[0]));assert.strictEqual(x.S.extrato,x.old);
 x=scenario({invalidSchema:true});assert.strictEqual(await x.run(),false);assert.strictEqual(x.seen.loaded,0);assert(/Identificador duplicado em extrato/.test(x.seen.alerts[0]));assert.strictEqual(x.S.extrato,x.old);
 x=scenario({readError:true});assert.strictEqual(await x.run(),false);assert(/Não foi possível ler/.test(x.seen.alerts[0]));assert.strictEqual(x.S.extrato,x.old);
 x=scenario({renderError:true});assert.strictEqual(await x.run(),false);assert(/falha ao montar a tela/.test(x.seen.alerts[0]));assert.strictEqual(x.S.extrato,x.old);assert.strictEqual(vm.runInContext('dataFileHandle',x.ctx),null);assert.strictEqual(vm.runInContext('isApplyingData',x.ctx),false);
 console.log('PASS: autorizacao explicita por gesto, mesmo arquivo; validacao, leitura, rollback sem escritas');
})().catch(error=>{console.error(error);process.exitCode=1;});

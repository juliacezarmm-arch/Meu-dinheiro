from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
a = s.index('async function openDataFile(){')
b = s.index('\nfunction cancelarAtualizacao(){', a)
assert s.count('async function openDataFile(){') == 1
new = '''async function openDataFile(){
 if(hasUnsavedChanges){setSaveStatus('Não salvo — salve antes de abrir outro JSON.');return false;}
 if(!window.showOpenFilePicker){
  appAlert('Este navegador não permite editar o mesmo arquivo JSON diretamente. Abra o Meu Dinheiro em um navegador compatível no computador.');return false;
 }
 let etapa='selecao';
 try{
  const handles=await window.showOpenFilePicker({multiple:false,types:[{description:'Dados Meu dinheiro',accept:{'application/json':['.json']}}]});
  const handle=handles[0];if(!handle)return false;
  // No Chrome do Android, solicitar a autorizacao imediatamente apos o seletor:
  // ler e analisar o arquivo antes pode consumir a ativacao exigida pelo navegador.
  etapa='permissao';
  if(!await fileWriteAllowed(handle,true)){
   setSaveStatus('Edição não autorizada. Abra o JSON novamente e permita salvar.');
   appAlert('O Chrome não autorizou a edição do JSON. Abra o arquivo novamente e permita salvar quando solicitado. Nenhum dado foi alterado.');
   return false;
  }
  etapa='leitura';
  const file=await handle.getFile();
  const originalText=await file.text();
  etapa='formato';
  let parsed;
  try{parsed=JSON.parse(originalText);}
  catch(error){
   if(error instanceof SyntaxError){
    appAlert('O arquivo selecionado não contém um JSON válido. Ele não foi modificado. Não sobrescreva o original; verifique se existe uma cópia de segurança.');
    return false;
   }
   throw error;
  }
  etapa='validacao';
  try{validarDadosImportados(parsed);}
  catch(error){
   // A validacao produz somente mensagens de esquema, sem dados financeiros.
   appAlert('O JSON foi lido, mas não passou na verificação: '+(error&&error.message||'formato incompatível')+'. O original não foi alterado.');
   return false;
  }
  etapa='exibicao';
  const previousHandle=dataFileHandle,previousSignature=knownFileSignature;
  const previousData={extrato:S.extrato,cartao:S.cartao,invest:S.invest,cartoes:S.cartoes,saldoInicial:S.saldoInicial};
  dataFileHandle=handle;knownFileSignature=originalText;
  try{applyDataFile(parsed);}catch(error){
   // A tela so deve ser associada ao novo arquivo quando toda a carga concluir.
   Object.assign(S,previousData);
   isApplyingData=false;
   dataFileHandle=previousHandle;knownFileSignature=previousSignature;
   setFileAccessState(!!previousHandle);
   appAlert('O JSON foi lido e validado, mas houve uma falha ao montar a tela. Nenhuma gravação foi feita. Informe que o erro ocorreu na exibição.');
   return false;
  }
  dataRevision++;
  setFileAccessState(true);
  setSaveStatus(hasUnsavedChanges?'Não salvo — recorrência atualizada.':'Salvo');
  return true;
 }catch(error){
  if(error&&error.name==='AbortError')return false;
  const bloqueado=error&&['SecurityError','NotAllowedError'].includes(error.name);
  const descricao=bloqueado?'O Chrome bloqueou a autorização para editar o arquivo. Tente selecionar o JSON novamente e permita o acesso.':etapa==='leitura'?'Não foi possível ler o JSON selecionado. Confira se o arquivo continua acessível no dispositivo.':etapa==='permissao'?'O Chrome não conseguiu conceder acesso ao JSON. Tente abrir novamente.':'Não foi possível selecionar esse arquivo JSON.';
  appAlert(descricao+' Nenhum dado foi gravado.');return false;
 }
}'''
s=s[:a]+new+s[b:]
assert 'const originalText=await file.text();' in s
assert s.count('async function openDataFile(){') == 1
path.write_text(s,encoding='utf-8')
print('PASS: abertura pede permissao antes da leitura, mostra causa especifica e preserva dados em erro')

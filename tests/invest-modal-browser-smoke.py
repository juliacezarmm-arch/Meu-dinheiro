"""Exercita modais com dados fictícios em HTML temporário; nenhum JSON pessoal é aberto."""
from pathlib import Path
import shutil,subprocess,sys,tempfile
chrome=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
if not chrome:
 print('Navegador indisponível para teste visual.',file=sys.stderr);sys.exit(2)
root=Path.cwd()
html=(root/'index.html').read_text(encoding='utf-8')
script=r'''<script>
setTimeout(()=>{
 const report=(ok,txt)=>document.body.insertAdjacentHTML('beforeend','<pre id="invest-modal-smoke">'+(ok?'PASS: ':'FAIL: ')+String(txt).replace(/</g,'&lt;')+'</pre>');
 try{
  const id=9000001;
  S.invest=[{id,kind:'investimento',nome:'Teste Modal',tipo:'CDB',historico:[{id:'m1',tipo:'aporte',data:today(),valor:100},{id:'m2',tipo:'atualizacao',data:today(),valor:120}]}];
  setFileAccessState(true);renderInvest();
  const pct=document.getElementById('inv-rend-pct').textContent;
  if(!pct.includes('20,00%')||!document.getElementById('inv-rend').textContent.includes('20,00'))throw Error('Porcentagem de rendimento incorreta: '+pct);
  const card=document.getElementById('invest-card-'+id);
  if(!card)throw Error('Cartão de investimento ausente');
  const clickLabel=label=>{const b=Array.from(document.querySelectorAll('#invest-card-'+id+' .goal-actions button')).find(x=>x.textContent.trim()===label);if(!b)throw Error('Botão não encontrado: '+label);b.click();};
  clickLabel('Editar dados');
  const dialog=document.getElementById('invest-action-dialog');
  if(dialog.hidden||card.querySelector('.goal-panel')||!document.getElementById('inv-edit-nome-'+id))throw Error('Edição não abriu em modal isolado');
  document.getElementById('inv-edit-nome-'+id).value='Teste editado';
  salvarIdentificacaoInvestimento(id);
  if(!dialog.hidden||S.invest[0].nome!=='Teste editado')throw Error('Salvar edição não fechou o modal');
  clickLabel('Atualizar valor');
  if(dialog.hidden||!document.getElementById('update-val-'+id))throw Error('Atualização não abriu em modal');
  fecharPainelInvestimento();
  clickLabel('Resgatar');
  if(dialog.hidden||!document.getElementById('resgate-val-'+id))throw Error('Resgate não abriu em modal');
  fecharPainelInvestimento();
  clickLabel('Histórico');
  if(dialog.hidden||!dialog.textContent.includes('Entrada investida'))throw Error('Histórico não abriu em modal');
  fecharPainelInvestimento();
  clickLabel('Gráfico');
  if(dialog.hidden||!dialog.querySelector('.stock-chart'))throw Error('Gráfico não abriu em modal');
  changeInvestChartPeriod(id,'ano');
  if(dialog.hidden||!dialog.querySelector('.stock-chart'))throw Error('Gráfico não atualizou sem sumir');
  document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  if(!dialog.hidden||document.querySelector('#invest-card-'+id+' .goal-panel'))throw Error('Escape não fechou o modal ou abriu painel inline');
  S.invest.push({id:9000002,kind:'meta',nome:'Meta teste',modo:'separar',meta:100,storageId:id,historico:[]});renderMetas();
  const meta=document.getElementById('invest-card-9000002');
  const editar=Array.from(meta.querySelectorAll('.goal-actions button')).find(x=>x.textContent.trim()==='Editar meta');editar.click();
  if(dialog.hidden||!document.getElementById('meta-edit-nome-9000002')||meta.querySelector('.goal-panel'))throw Error('Edição da meta não abriu em modal');
  fecharPainelInvestimento();
  report(true,'percentual, editar, atualizar, resgatar, histórico, gráfico, Escape e metas sem expandir cards');
 }catch(error){report(false,error.stack||error.message);}
},900);
</script>'''
html=html.replace('</body>',script+'\n</body>',1)
target=root/'__invest_dialog_smoke_tmp__.html';target.write_text(html,encoding='utf-8')
try:
 with tempfile.TemporaryDirectory() as profile:
  result=subprocess.run([chrome,'--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--disable-extensions','--user-data-dir='+profile,'--virtual-time-budget=3500','--dump-dom',target.as_uri()],text=True,capture_output=True,timeout=40)
  if 'PASS: percentual, editar, atualizar, resgatar, histórico, gráfico, Escape e metas sem expandir cards' not in result.stdout:
   print('SMOKE_FAILED / Chrome rc',result.returncode,file=sys.stderr)
   spot=result.stdout.find('id="invest-modal-smoke"')
   print(result.stdout[spot:spot+1700] if spot>=0 else result.stdout[-2200:],file=sys.stderr)
   print(result.stderr[-900:],file=sys.stderr);sys.exit(1)
  print('PASS: Chrome headless — modais e percentual funcionando; nenhum JSON pessoal aberto')
finally:
 target.unlink(missing_ok=True)

"""Chrome headless: testa modal e rentabilidade com dados fictícios só em memória."""
from pathlib import Path
import os,shutil,subprocess,sys,tempfile
chrome=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
if not chrome: raise RuntimeError('Chrome headless necessário')
root=Path.cwd();html=(root/'index.html').read_text(encoding='utf-8')
script=r'''<script>
setTimeout(()=>{
 const report=(ok,msg)=>document.body.insertAdjacentHTML('beforeend','<pre id="invest-smoke-result">'+(ok?'PASS: ':'FAIL: ')+String(msg).replace(/</g,'&lt;')+'</pre>');
 try{
  setFileAccessState(true);
  const hoje=today();
  S.invest=[
   {id:77,kind:'investimento',nome:'Poupança teste',tipo:'Poupança',historico:[{id:'test-a',tipo:'aporte',data:hoje,valor:100,saldo:100}],valorAtual:100,totalAportado:100,totalResgatado:0},
   {id:78,kind:'investimento',nome:'CDB teste',tipo:'CDB',historico:[{id:'test-b',tipo:'aporte',data:hoje,valor:50,saldo:50},{id:'test-c',tipo:'atualizacao',data:hoje,valor:55,saldo:55}],valorAtual:55,totalAportado:50,totalResgatado:0}
  ];
  renderInvest();
  const el=id=>document.getElementById(id);
  if(el('inv-rend').textContent!=='R$ 5,00'||el('inv-rend-pct').textContent!=='3,3%')throw Error('Percentual de rendimento incorreto: '+el('inv-rend-pct').textContent);
  const card=document.querySelector('.goal-card[data-invest-id="77"]');
  if(!card)throw Error('Card não encontrado');
  const action=text=>Array.from(card.querySelectorAll('.goal-actions button')).find(b=>b.textContent.trim()===text);
  action('Editar dados').click();
  if(el('invest-modal').hidden||!el('invest-modal-content').querySelector('#inv-edit-nome-77')||card.querySelector('.goal-panel'))throw Error('Editar não foi movido para janela flutuante');
  if(S.invest[0].valorAtual!==100)throw Error('Abrir modal alterou patrimônio');
  el('invest-modal').querySelector('.invest-modal-close').click();
  if(!el('invest-modal').hidden||document.body.classList.contains('invest-modal-open'))throw Error('Fechamento deixou overlay ativo');
  action('Atualizar valor').click();
  if(el('invest-modal').hidden||!el('invest-modal-content').querySelector('#update-val-77'))throw Error('Atualizar valor não abriu modal');
  fecharPainelInvestimento();
  action('Resgatar').click();
  if(el('invest-modal').hidden||!el('invest-modal-content').querySelector('#resgate-val-77'))throw Error('Resgatar não abriu modal');
  fecharPainelInvestimento();
  action('Histórico').click();
  if(el('invest-modal').hidden||!el('invest-modal-content').textContent.includes('Entrada investida'))throw Error('Histórico não abriu modal');
  fecharPainelInvestimento();
  action('Gráfico').click();
  if(el('invest-modal').hidden||!el('invest-modal-content').querySelector('svg'))throw Error('Gráfico não abriu modal');
  fecharPainelInvestimento();
  S.invest=[];renderInvest();
  if(el('inv-rend-pct').textContent!=='—')throw Error('Base zero deve mostrar —');
  report(true,'Chrome: janelas de editar, atualizar, resgatar, histórico e gráfico; fechamento; taxa e base zero; nenhum dado persistido');
 }catch(e){report(false,e.stack||e.message);}
},1200);
</script>'''
html=html.replace('</body>',script+'\n</body>',1)
target=root/'__invest_modal_smoke_tmp__.html';target.write_text(html,encoding='utf-8')
try:
 with tempfile.TemporaryDirectory() as profile:
  result=subprocess.run([chrome,'--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--disable-extensions','--user-data-dir='+profile,'--virtual-time-budget=4500','--dump-dom',target.as_uri()],text=True,capture_output=True,timeout=45)
  ok='PASS: Chrome: janelas de editar, atualizar, resgatar, histórico e gráfico' in result.stdout
  if not ok:
   print('INVEST_MODAL_SMOKE_FAILED, Chrome rc='+str(result.returncode),file=sys.stderr)
   found=result.stdout.find('invest-smoke-result')
   print(result.stdout[max(0,found-100):found+1200] if found>=0 else result.stdout[-1900:],file=sys.stderr)
   print(result.stderr[-1000:],file=sys.stderr)
   sys.exit(1)
  print('PASS: Chrome — cinco janelas flutuantes, fechar, percentual 3,3%, base zero, dados fictícios')
finally:
 target.unlink(missing_ok=True)

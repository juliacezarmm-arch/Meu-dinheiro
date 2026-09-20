"""Teste de integração via Chrome headless em HTML descartável (não grava dados do usuário)."""
from pathlib import Path
import os,shutil,subprocess,sys,tempfile
chrome=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
if not chrome:
 print('Chrome ausente no runner: smoke não pode ser executado',file=sys.stderr)
 sys.exit(2)
root=Path.cwd()
html=(root/'index.html').read_text(encoding='utf-8')
assert '<script src="js/recorrentes.js?v=20260920-compact1"></script>' in html
script=r'''<script>
(function(){
const report=(ok,msg)=>{document.body.insertAdjacentHTML('beforeend','<pre id="smoke-result">'+(ok?'PASS: ':'FAIL: ')+String(msg).replace(/</g,'&lt;')+'</pre>');};
setTimeout(()=>{
try{
 if(!document.body.classList.contains('file-closed'))throw Error('Sem JSON a tela deve ficar bloqueada');
 if(!document.getElementById('recorrentes-area'))throw Error('Cadastro ausente');
 if(!document.getElementById('rec-card-open'))throw Error('Área própria de assinatura ausente');
 if(!document.getElementById('rec-card-toggle'))throw Error('Assinaturas sem botão para recolher');
 if(!document.querySelector('#cc-wrap'))throw Error('Tabela de lançamentos do cartão ausente');
 if(document.querySelector('#cc-gasto-tipo').closest('.row').style.display!=='none')throw Error('Tipo fixo/variável visível');
 const d=new Date(today()+'T12:00:00');d.setDate(d.getDate()-1);
 dataFileHandle={kind:'file',name:'teste.json',getFile:async()=>({size:1,lastModified:1}),queryPermission:async()=> 'granted',createWritable:async()=>({write:async()=>{},close:async()=>{}})};
 knownFileSignature='1:1';setFileAccessState(true);
 S.saldoInicial={valor:500,data:isoDate(d.getFullYear(),d.getMonth(),d.getDate()),idsIgnorados:[]};
 document.getElementById('rec-open').click();
 if(document.getElementById('rec-form').parentElement.id!=='rec-body')throw Error('Cadastro da conta fora do Extrato');
 elToggle=document.getElementById('rec-toggle');
 if(!elToggle||document.getElementById('rec-body').hidden)throw Error('Área de recorrência não abriu');
 if(Array.from(document.getElementById('rec-method').options).some(o=>o.value==='cartao'))throw Error('Opção cartão apareceu nos débitos da conta');
 if(document.querySelector('#rec-form #rec-card-row'))throw Error('Campo cartão ainda está dentro do formulário da conta');
 if(document.getElementById('rec-card-row'))throw Error('Campo cartão não deveria existir no Extrato');
 const el=id=>document.getElementById(id);
 el('rec-name').value='Salário smoke';el('rec-value').value='100';el('rec-type').value='entrada';el('rec-type').dispatchEvent(new Event('change'));
 el('rec-category').value='Trabalho';el('rec-category').dispatchEvent(new Event('change'));el('rec-subcategory').value='Salário';
 el('rec-frequency').value='mensal';el('rec-frequency').dispatchEvent(new Event('change'));el('rec-day').value=String(Number(today().slice(8)));
 if(el('rec-day-label').hidden||!el('rec-date-label').hidden)throw Error('Dia do mês não aparece no Extrato');
 if(el('rec-day-label').textContent.indexOf('Dia do recebimento')<0)throw Error('Rótulo de recebimento incorreto');
 el('rec-form').dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}));
 if(S.recorrentes.length!==1)throw Error('Cadastro não criado');
 const lines=S.extrato.filter(x=>x.recorrenciaId===S.recorrentes[0].id);
 if(lines.length!==1||lines[0].val!==100)throw Error('Lançamento automático ou valor incorreto');
 if(Math.abs(calcularSaldoDisponivelAte(today())-600)>0.001)throw Error('Saldo incorreto: '+calcularSaldoDisponivelAte(today()));
 renderExtrato();renderCartao();updateResumo();
 if(S.extrato.filter(x=>x.recorrenciaId===S.recorrentes[0].id).length!==1)throw Error('Lançamento duplicado');
 const amanha=new Date(today()+'T12:00:00');amanha.setDate(amanha.getDate()+1);
 const futureDate=isoDate(amanha.getFullYear(),amanha.getMonth(),amanha.getDate());
 S.recorrentes.push({id:989898,nome:'Despesa futura',valor:70,tipo:'saida',metodo:'debito_automatico',inicio:futureDate,frequencia:'mensal',diaCobranca:amanha.getDate(),categoria:'Casa',subcategoria:'Telefone',excluida:false});
 extratoMes=new Date(futureDate+'T12:00:00');renderExtrato();
 if(document.querySelector('#ext-wrap .rec-predictions'))throw Error('Caixa separada de previsões continua visível');
 if(!Array.from(document.querySelectorAll('#ext-wrap tbody tr')).some(tr=>tr.textContent.includes('Despesa futura')&&tr.textContent.includes('previsto')))throw Error('Futuro não entrou na tabela geral');
 if(S.extrato.some(x=>x.recorrenciaId===989898))throw Error('Futuro entrou antecipadamente como movimentação real');
 if(Math.abs(calcularSaldoDisponivelAte(today())-600)>0.001)throw Error('Previsão não pode reduzir saldo antes da data');
 el('rec-toggle').click();
 if(!el('rec-body').hidden||el('rec-toggle').getAttribute('aria-expanded')!=='false')throw Error('Recolher não funciona');
 el('rec-toggle').click();
 if(el('rec-body').hidden)throw Error('Expandir não funciona');
 if(!el('rec-list').querySelector('.rec-item-head .rec-inline-actions'))throw Error('Ações fora do cabeçalho compacto');
 el('rec-card-open').click();
 if(el('rec-form').parentElement.id!=='rec-card-body')throw Error('Assinatura não está na aba Cartão');
 if(el('rec-card-row').hidden||el('rec-method').value!=='cartao')throw Error('Assinatura sem seleção exclusiva de cartão');
 if(!el('rec-method').closest('label').hidden)throw Error('Forma de pagamento redundante na assinatura');
 if(el('rec-card-row').parentElement.id!=='rec-form')throw Error('Cartão exclusivo não inserido no formulário da assinatura');
 report(true,'Cadastro separado para conta e cartão, entrada automática, saldo e idempotência');
}catch(e){report(false,e.stack||e.message);}
},1200);
})();
</script>'''
html=html.replace('</body>',script+'\n</body>',1)
# HTML temporário no próprio repo: caminho dos assets e do script deve ser relativo.
target=root/'__recurring_smoke_tmp__.html';target.write_text(html,encoding='utf-8')
try:
 with tempfile.TemporaryDirectory() as profile:
  result=subprocess.run([chrome,'--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--disable-extensions','--user-data-dir='+profile,'--virtual-time-budget=4000','--dump-dom',target.as_uri()],text=True,capture_output=True,timeout=40)
  if 'PASS: Cadastro separado para conta e cartão, entrada automática, saldo e idempotência' not in result.stdout:
   print('SMOKE_FAILED / Chrome rc',result.returncode,file=sys.stderr)
   print(result.stdout[-3000:],file=sys.stderr)
   print(result.stderr[-1500:],file=sys.stderr)
   sys.exit(1)
  print('PASS: Chrome headless — conta e cartão separados, entrada automática, saldo, idempotência')
finally:
 target.unlink(missing_ok=True)

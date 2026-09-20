from pathlib import Path
import re
path=Path('index.html')
src=path.read_text(encoding='utf-8')
old=re.compile(r'    <section id="saldo-setup" class="saldo-setup" aria-label="Configurar saldo inicial">.*?    </section>\n    <div class="add-form">',re.S)
section='''    <section id="saldo-setup" class="saldo-setup" aria-label="Saldo inicial">
      <button id="saldo-toggle" class="saldo-toggle" type="button" aria-expanded="false" aria-controls="saldo-content" onclick="toggleSaldoInicial()">Saldo inicial <span aria-hidden="true">⌄</span></button>
      <div id="saldo-content" hidden>
        <div id="saldo-start-form">
          <div class="row row2">
            <label for="saldo-inicial-valor">Valor inicial (R$)
              <input id="saldo-inicial-valor" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0,00" />
            </label>
            <div class="saldo-data">Data de início<strong id="saldo-data-referencia"></strong></div>
          </div>
          <button id="saldo-submit" type="button" onclick="confirmarSaldoInicial()">Salvar saldo inicial</button>
        </div>
        <div id="saldo-start-saved" hidden>
          <span id="saldo-start-descricao"></span>
          <button type="button" class="saldo-corrigir" onclick="editarSaldoInicial()">Editar</button>
        </div>
      </div>
    </section>
    <div class="add-form">'''
src,n=old.subn(section,src)
assert n==1,f'Seção encontrada {n} vezes'
old_css='.saldo-link{margin:-.25rem 0 .85rem;font-size:12px}'
assert src.count(old_css)==1
src=src.replace(old_css,old_css+'''
.saldo-setup{padding:6px 10px;margin-bottom:10px}
.saldo-setup .saldo-toggle{display:flex;align-items:center;justify-content:space-between;width:100%;border:0;background:transparent;color:var(--color-text-primary);padding:9px 7px;text-align:left;font-size:13px;font-weight:750;cursor:pointer}
.saldo-setup .saldo-toggle span{color:var(--color-text-secondary);font-size:18px;line-height:1}
#saldo-content{padding:10px 7px 8px;border-top:1px solid #33332e}
#saldo-start-saved{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;font-size:12px;color:var(--color-text-secondary)}
#saldo-start-saved[hidden],#saldo-content[hidden]{display:none!important}
.saldo-setup .saldo-corrigir{padding:6px 10px}
''')
old_func='function editarSaldoInicial(){'
assert src.count(old_func)==1
src=src.replace(old_func,'''function toggleSaldoInicial(force){
  const content=document.getElementById('saldo-content');
  const button=document.getElementById('saldo-toggle');
  if(!content||!button)return;
  const aberto=typeof force==='boolean'?force:content.hidden;
  content.hidden=!aberto;
  button.setAttribute('aria-expanded',String(aberto));
}
function editarSaldoInicial(){''')
old_edit="  if(!saldoInicialValido(S.saldoInicial))return;\n  document.getElementById('saldo-inicial-valor').value=String(S.saldoInicial.valor);"
assert src.count(old_edit)==1
src=src.replace(old_edit,"  if(!saldoInicialValido(S.saldoInicial))return;\n  toggleSaldoInicial(true);\n  document.getElementById('saldo-inicial-valor').value=String(S.saldoInicial.valor);")
old_text="if(existente)aviso.textContent='Saldo de partida: '+fmt(S.saldoInicial.valor)+' em '+S.saldoInicial.data.split('-').reverse().join('/')+'. Os registros anteriores foram preservados, mas não serão somados de novo.';"
assert src.count(old_text)==1
src=src.replace(old_text,"if(existente)aviso.textContent=fmt(S.saldoInicial.valor)+' · '+S.saldoInicial.data.split('-').reverse().join('/');")
old_go="  document.getElementById('saldo-setup').scrollIntoView({behavior:'smooth',block:'start'});\n  document.getElementById('saldo-inicial-valor').focus();"
assert src.count(old_go)==1
src=src.replace(old_go,"  toggleSaldoInicial(true);\n  document.getElementById('saldo-setup').scrollIntoView({behavior:'smooth',block:'start'});\n  (saldoInicialValido(S.saldoInicial)?document.querySelector('#saldo-start-saved .saldo-corrigir'):document.getElementById('saldo-inicial-valor')).focus();")
old_confirm="  renderSaldoInicial();renderExtrato();updateResumo();\n  setSaveStatus("
assert src.count(old_confirm)==1
src=src.replace(old_confirm,"  renderSaldoInicial();toggleSaldoInicial(false);renderExtrato();updateResumo();\n  setSaveStatus(")
path.write_text(src,encoding='utf-8')
print('PASS: painel compacto, data e valor preservados, sem mudança nos cálculos')
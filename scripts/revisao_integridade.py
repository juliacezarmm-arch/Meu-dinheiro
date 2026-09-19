from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8-sig')
assert 'function valorParcela(' in s, 'Execute revisao_financeira.py antes'
def once(old,new):
    global s
    n=s.count(old)
    assert n==1, f'Esperado 1 ocorrência, obtidas {n}: {old[:115]!r}'
    s=s.replace(old,new,1)
def fn(name,old,new):
    global s
    start=s.index('function '+name+'(')
    end=s.find('\nfunction ',start+len(name)+10)
    if end<0:end=len(s)
    fragment=s[start:end]
    n=fragment.count(old)
    assert n==1, f'{name}: esperado 1 ocorrência, obtidas {n}: {old[:100]!r}'
    s=s[:start]+fragment.replace(old,new,1)+s[end:]

# monthKey() usa meses zero-based internamente; datas ISO e identificadores de fatura usam meses 1-based.
fn('renderAnnualSummary',"const anoMes=monthKey(viewYear,m);", "const anoMes=isoDate(viewYear,m,1).slice(0,7);")
fn('updateResumo',"const depoisAbertura=S.saldoInicial&&nowKey>=S.saldoInicial.data.slice(0,7);", "const depoisAbertura=S.saldoInicial&&isoDate(viewYear,viewMonth,1).slice(0,7)>=S.saldoInicial.data.slice(0,7);")
fn('renderCartao',"  const nowKey=monthKey(viewYear,viewMonth);", "  const nowKey=monthKey(viewYear,viewMonth);\n  const faturaKey=isoDate(viewYear,viewMonth,1).slice(0,7);")
fn('renderCartao',"const total=totalDaFatura(card.id,nowKey),pago=pagoNaFatura(card.id,nowKey);", "const total=totalDaFatura(card.id,faturaKey),pago=pagoNaFatura(card.id,faturaKey);")
fn('renderCartao',"registrarPagamentoFatura(${card.id},'${nowKey}')", "registrarPagamentoFatura(${card.id},'${faturaKey}')")
fn('dueDateFor',"const startOffset=closeDay?((baseDate.getDate()>closeDay?1:0)+(dueDay<=closeDay?1:0))", "const fechamento=closeDay?Math.min(closeDay,new Date(baseDate.getFullYear(),baseDate.getMonth()+1,0).getDate()):0;\n  const startOffset=closeDay?((baseDate.getDate()>fechamento?1:0)+(dueDay<=closeDay?1:0))")

# Quando o histórico é aberto, não confundir entradas realizadas com resgates e lançamentos futuros.
fn('renderExtrato',"const entradasMes=rows.filter(r=>r.tipo==='entrada').reduce((s,r)=>s+r.val,0);", "const entradasMes=rows.filter(r=>receitaReal(r)&&movimentoRealizado(r)).reduce((s,r)=>s+r.val,0);\n  const resgatesMes=rows.filter(r=>r.tipo==='entrada'&&r.categoria==='Resgate'&&movimentoRealizado(r)).reduce((s,r)=>s+r.val,0);")
fn('renderExtrato',"const saidasMes=rows.filter(r=>r.tipo==='saida').reduce", "const saidasMes=rows.filter(r=>r.tipo==='saida'&&movimentoRealizado(r)).reduce")
fn('renderExtrato',"const investimentoMes=rows.filter(r=>r.tipo==='investimento').reduce", "const investimentoMes=rows.filter(r=>r.tipo==='investimento'&&movimentoRealizado(r)).reduce")
fn('renderExtrato',"const metaMes=rows.filter(r=>r.tipo==='meta').reduce", "const metaMes=rows.filter(r=>r.tipo==='meta'&&movimentoRealizado(r)).reduce")
fn('renderExtrato',"    <div class=\"plain-card\"><strong>Saídas: ${fmt(saidasMes)}</strong>", "    <div class=\"plain-card\"><strong>Resgates: ${fmt(resgatesMes)}</strong><span>Transferências do investimento de volta ao dinheiro disponível, não são receitas.</span></div>\n    <div class=\"plain-card\"><strong>Saídas: ${fmt(saidasMes)}</strong>")
fn('renderExtrato',"const tipoLabel=r.tipo==='saldo_inicial'?'saldo'", "const tipoLabel=futuro?'previsto':r.tipo==='saldo_inicial'?'saldo'")
fn('renderExtrato',"${r.desc||'-'}${detalhe}","${escHtml(r.desc||'-')}${detalhe}")
fn('renderExtrato',"${categoria}</td><td>","${escHtml(categoria)}</td><td>")
fn('renderExtrato',"Guardado em ${r.storageNome}","Guardado em ${escHtml(r.storageNome)}")

# URLs / textos importados nunca podem virar HTML executável.
once('function novoIdGlobal(){', '''function escHtml(value){
  return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function dataISOValida(v){
  if(typeof v!=='string'||!/^\\d{4}-\\d{2}-\\d{2}$/.test(v))return false;
  const d=new Date(v+'T12:00:00');
  return !Number.isNaN(d.getTime())&&isoDate(d.getFullYear(),d.getMonth(),d.getDate())===v;
}
function validarDadosImportados(arquivo){
  if(!arquivo||typeof arquivo!=='object'||Array.isArray(arquivo))throw Error('Formato JSON inválido.');
  const dados=arquivo.dados||arquivo;
  if(!dados||typeof dados!=='object'||Array.isArray(dados))throw Error('Objeto de dados inválido.');
  const colecoes=['extrato','cartao','invest','cartoes'];
  if(!colecoes.some(k=>Array.isArray(dados[k])))throw Error('Este JSON não contém dados reconhecíveis do aplicativo.');
  for(const key of colecoes){
    const registros=dados[key]===undefined?[]:dados[key];
    if(!Array.isArray(registros)||registros.length>100000)throw Error('Coleção inválida: '+key);
    const ids=new Set();
    for(const r of registros){
      if(!r||typeof r!=='object'||Array.isArray(r)||!Number.isSafeInteger(Number(r.id))||Number(r.id)<=0)throw Error('Identificador inválido em '+key);
      const id=String(r.id);
      if(ids.has(id))throw Error('Identificador duplicado em '+key);
      ids.add(id);
      if(r.data!==undefined&&!dataISOValida(r.data))throw Error('Data inválida em '+key);
      if(key==='extrato'&&!dataISOValida(r.data))throw Error('Lançamento sem data.');
      if(key==='cartao'&&!dataISOValida(r.data))throw Error('Compra sem data.');
      if(key==='extrato'&&!['entrada','saida','investimento','meta'].includes(r.tipo))throw Error('Tipo de lançamento inválido.');
      for(const campo of ['val','valorAtual','totalAportado','totalResgatado','meta']){
        if(r[campo]!==undefined&&(!Number.isFinite(Number(r[campo]))||Number(r[campo])<0))throw Error('Valor financeiro inválido em '+key+': '+campo);
      }
      if(key==='cartao'&&(!Number.isInteger(Number(r.parcelas||1))||Number(r.parcelas||1)<1||Number(r.parcelas||1)>120))throw Error('Parcelamento inválido.');
      if(key==='invest'&&r.historico!==undefined){
        if(!Array.isArray(r.historico)||r.historico.length>100000)throw Error('Histórico de investimento inválido.');
        for(const h of r.historico){
          if(!h||typeof h!=='object'||!dataISOValida(h.data)||!['aporte','resgate','atualizacao'].includes(h.tipo)||!Number.isFinite(Number(h.valor))||Number(h.valor)<0)throw Error('Movimentação de investimento inválida.');
        }
      }
    }
  }
  if(dados.saldoInicial!==undefined&&dados.saldoInicial!==null){
    if(!saldoInicialValido(dados.saldoInicial)||!dataISOValida(dados.saldoInicial.data)||dados.saldoInicial.idsIgnorados.some(id=>!Number.isSafeInteger(Number(id))))throw Error('Saldo inicial inválido.');
  }
  return dados;
}
function novoIdGlobal(){''')
fn('applyDataFile',"  isApplyingData=true;\n  const dados=data.dados||data;", "  const dados=validarDadosImportados(data);\n  isApplyingData=true;")
fn('openDataFile',"  try{\n    if(window.showOpenFilePicker){", "  try{\n    if(hasUnsavedChanges&&!confirm('Existem alterações não salvas. Abrir outro arquivo descartará essas alterações. Continuar?'))return;\n    if(window.showOpenFilePicker){")
fn('openDataFile',"      dataFileHandle=handles[0];\n      const file=await dataFileHandle.getFile();", "      const novoHandle=handles[0];\n      const file=await novoHandle.getFile();")
fn('openDataFile',"      applyDataFile(parsed);\n      setSaveStatus('Arquivo aberto.", "      applyDataFile(parsed);\n      dataFileHandle=novoHandle;\n      setSaveStatus('Arquivo aberto.")
fn('importData',"  if(!file)return;", "  if(!file)return;\n  if(hasUnsavedChanges&&!confirm('Existem alterações não salvas. Importar outro arquivo descartará essas alterações. Continuar?')){event.target.value='';return;}")

fn('renderRegisteredCards',"${c.bank} - vence dia ${c.dueDay}","${escHtml(c.bank)} - vence dia ${c.dueDay}")
fn('renderRegisteredCards',"<div class=\"bank-name\">${c.bank}</div>","<div class=\"bank-name\">${escHtml(c.bank)}</div>")
fn('renderInvestDestinationOptions',"${i.nome}${extra}</option>","${escHtml(i.nome+extra)}</option>")
fn('renderMetaInvestOptions',"${i.nome} - ${i.tipo}</option>","${escHtml(i.nome+' - '+i.tipo)}</option>")
fn('renderCartao',"${desc}<div style=", "${escHtml(desc)}<div style=")
fn('renderCartao',"${cat}</div></td>","${escHtml(cat)}</div></td>")
fn('renderBarList',"${item.label}</div>","${escHtml(item.label)}</div>")
fn('renderDestinoCard',"<h3>${item.nome}</h3>","<h3>${escHtml(item.nome)}</h3>")
fn('renderDestinoCard',"<div class=\"goal-meta\">${subtitulo}","<div class=\"goal-meta\">${escHtml(subtitulo)}")
fn('renderDestinoCard',"<div><strong>${nome}</strong><div class=\"history-kind\">${extra}</div></div>","<div><strong>${escHtml(nome)}</strong><div class=\"history-kind\">${escHtml(extra)}</div></div>")
fn('renderDestinoCard',"<div class=\"goal-panel-title\">Colocar dinheiro no investimento</div>","<div class=\"goal-panel-title\">Colocar dinheiro no investimento</div>") if False else None

fn('renderStockChart',"<span>Variação: ${variacao>=0?'+':''}${fmt(variacao)}</span>","<span>Variação patrimonial (inclui aportes/resgates): ${variacao>=0?'+':''}${fmt(variacao)}</span>")
fn('renderDestinoCard',"${resultadoMes.pct.toFixed(1).replace('.',',')}% comparando com o mês anterior.","${resultadoMes.pct.toFixed(1).replace('.',',')}% aproximado; não considera o tempo de cada aporte.")
fn('renderDestinoCard',"${item.kind==='meta'?'Calculado pelo rendimento do investimento onde a meta está guardada.'", "${item.kind==='meta'?'Estimativa baseada na variação do investimento vinculado.'")

p.write_text(s,encoding='utf-8')
print('PATCH_INTEGRIDADE_OK')

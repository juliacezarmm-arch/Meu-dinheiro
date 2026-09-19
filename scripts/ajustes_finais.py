from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8-sig')
assert 'function valorParcela(' in s, 'Revisão inicial deve estar aplicada'
def once(a,b):
 global s
 assert s.count(a)==1,(s.count(a),a[:100])
 s=s.replace(a,b,1)
def fn(name,a,b):
 global s
 start=s.index('function '+name+'(')
 end=s.find('\nfunction ',start+len(name)+10)
 if end<0:end=len(s)
 frag=s[start:end]
 assert frag.count(a)==1,(name,frag.count(a),a[:100])
 s=s[:start]+frag.replace(a,b,1)+s[end:]

once('function reservadoEmMetas(id){', '''function ultimaDataFinanceira(item){
  return ensureInvestHistory(item).reduce((ultima,m)=>m.data&&m.data>ultima?m.data:ultima,'');
}
function reservadoEmMetas(id){''')
fn('saveInvestUpdate',"  if(data>today()){alert('Atualizações de patrimônio futuro não são permitidas.');return;}","  if(data>today()){alert('Atualizações de patrimônio futuro não são permitidas.');return;}\n  const relacionados=[item,...S.invest.filter(x=>x.kind==='meta'&&x.storageId===item.id)];\n  if(relacionados.some(x=>data<ultimaDataFinanceira(x))){alert('Atualize na data mais recente do histórico. Uma atualização retroativa pode alterar saldos de resgates posteriores.');return;}")
fn('saveInvestResgate',"  const resgate=val;\n  const extId=novoIdExtrato();\n  const storage=item.kind==='meta'?getMetaStorage(item):null;", "  const storage=item.kind==='meta'?getMetaStorage(item):null;\n  if(item.kind==='meta'&&!storage){alert('Esta meta está sem investimento vinculado. Regularize o vínculo antes de resgatar.');return;}\n  if(storage&&val>Number(storage.valorAtual||0)+0.000001){alert('O investimento vinculado não possui saldo suficiente para este resgate.');return;}\n  if(data<ultimaDataFinanceira(item)||(storage&&data<ultimaDataFinanceira(storage))){alert('Registre resgates após a última movimentação do histórico para evitar saldo incorreto.');return;}\n  const resgate=val;\n  const extId=novoIdExtrato();")
fn('renderCartao',"    const aberto=Math.max(0,total-pago);", "    const aberto=Math.max(0,total-pago);\n    const historica=S.saldoInicial&&faturaKey<S.saldoInicial.data.slice(0,7);")
fn('renderCartao',"      ${card.closeDay?'':'<span>Fechamento não definido: vencimentos são estimativas. Configure o fechamento do cartão.</span>'}", "      ${historica?'<span>Fatura anterior à abertura: pagamentos antigos não são conciliados automaticamente.</span>':''}\n      ${card.closeDay?'':'<span>Fechamento não definido: vencimentos são estimativas. Configure o fechamento do cartão.</span>'}")
fn('renderCartao',"${aberto>0?`<button class=\"btn-green\"", "${aberto>0&&!historica?`<button class=\"btn-green\"")
fn('updateResumo',"? 'Saldo real a partir de '+S.saldoInicial.data.split('-').reverse().join('/')", "? 'Saldo de hoje, calculado a partir de '+S.saldoInicial.data.split('-').reverse().join('/')")

fn('validarDadosImportados',"  const dados=arquivo.dados||arquivo;", "  if(arquivo.versao!==undefined&&(!Number.isInteger(arquivo.versao)||arquivo.versao>2||arquivo.versao<1))throw Error('Versão do arquivo incompatível.');\n  const dados=arquivo.dados||arquivo;")
fn('validarDadosImportados',"if(r[campo]!==undefined&&(!Number.isFinite(Number(r[campo]))||Number(r[campo])<0))", "if(r[campo]!==undefined&&(typeof r[campo]!=='number'||!Number.isFinite(r[campo])||r[campo]<0))")
fn('validarDadosImportados',"      if(key==='cartao'&&(!Number.isInteger", "      if(key==='cartoes'&&r.color!==undefined&&!/^#[0-9a-fA-F]{6}$/.test(r.color))throw Error('Cor de cartão inválida.');\n      if(key==='cartao'&&(!Number.isInteger")
fn('validarDadosImportados',"if(!h||typeof h!=='object'||!dataISOValida(h.data)||!['aporte','resgate','atualizacao'].includes(h.tipo)||!Number.isFinite(Number(h.valor))||Number(h.valor)<0)", "if(!h||typeof h!=='object'||!dataISOValida(h.data)||!['aporte','resgate','atualizacao'].includes(h.tipo)||typeof h.valor!=='number'||!Number.isFinite(h.valor)||h.valor<0||(h.id!==undefined&&!/^[A-Za-z0-9_-]{1,100}$/.test(String(h.id))))")
p.write_text(s,encoding='utf-8')
print('AJUSTES_FINAIS_OK')

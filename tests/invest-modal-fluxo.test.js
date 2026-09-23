const assert=require('assert'),fs=require('fs');
const html=fs.readFileSync('index.html','utf8');
const src=html.match(/<script\s*>([\s\S]*?)<\/script>/)[1];

function fn(name,next){
  const start=src.indexOf('function '+name+'(');
  assert(start>=0,'Funcao ausente: '+name);
  const end=next?src.indexOf('function '+next+'(',start+1):src.length;
  assert(end>start,'Fim da funcao nao encontrado: '+name);
  return src.slice(start,end);
}

const add=fn('addInvest','addMeta');
assert(add.includes('investUi.historico[item.id]=false'),'Novo investimento deve manter historico fechado');
assert(!add.includes('investUi.historico[item.id]=true'),'Novo investimento nao deve abrir historico');

const aporte=fn('saveInvestAporte','saveInvestUpdate');
assert(aporte.includes('investUi.historico[id]=false'),'Aporte deve manter historico fechado');
assert(!aporte.includes('investUi.historico[id]=true'),'Aporte nao deve abrir historico');

const update=fn('saveInvestUpdate','saveInvestResgate');
assert(update.includes('investUi.historico[id]=false'),'Atualizacao deve manter historico fechado');
assert(update.includes('investUi.historico[meta.id]=false'),'Metas vinculadas devem manter historico fechado');
assert(!update.includes('investUi.historico[id]=true'),'Atualizacao nao deve abrir historico');

const resgate=fn('saveInvestResgate','delInvestHistory');
assert(resgate.includes('investUi.historico[id]=false'),'Resgate deve manter historico fechado');
assert(!resgate.includes('investUi.historico[id]=true'),'Resgate nao deve abrir historico');

const reserva=fn('movimentarReservaInterna','getMetaStorage');
assert(reserva.includes('investUi.historico[id]=false'),'Reserva interna deve manter historico fechado');

assert(html.includes('Valor atual registrado: ${fmt(item.valorAtual||0)}. Informe o valor total que aparece hoje no banco.'),'Modal deve explicar o valor atual');
assert(html.includes('id="update-val-${item.id}" value="${Number(item.valorAtual||0)}"'),'Campo de atualizacao deve vir preenchido com o valor atual');

console.log('PASS: historico nao abre automaticamente e atualizar valor vem pre-preenchido');

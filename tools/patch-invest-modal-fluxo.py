from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f"Esperava {count} ocorrencia(s), encontrei {n}: {old[:100]!r}")
    s = s.replace(old, new, count)

# Investimento novo: nao abrir historico automaticamente.
rep(
"""    recalcInvestFromHistory(item);
    investUi.historico[item.id]=true;
    investUi.mes[item.id]=today().slice(0,7);""",
"""    recalcInvestFromHistory(item);
    investUi.historico[item.id]=false;
    investUi.mes[item.id]=today().slice(0,7);"""
)

# Aporte: fecha a janela e mantem historico fechado.
rep(
"""  investUi.acao[id]='';
  investUi.historico[id]=true;
  investUi.mes[id]=data.slice(0,7);
  saveData();refreshInvestViews();""",
"""  investUi.acao[id]='';
  investUi.historico[id]=false;
  investUi.mes[id]=data.slice(0,7);
  saveData();refreshInvestViews();""",
3
)

# Atualizacao: metas vinculadas tambem nao abrem historico sozinhas.
rep(
"""      recalcInvestFromHistory(meta);
      investUi.historico[meta.id]=true;
      investUi.mes[meta.id]=data.slice(0,7);""",
"""      recalcInvestFromHistory(meta);
      investUi.historico[meta.id]=false;
      investUi.mes[meta.id]=data.slice(0,7);"""
)

# Reserva/liberacao interna: manter historico fechado.
rep(
"""  investUi.acao[id]='';investUi.historico[id]=true;investUi.mes[id]=today().slice(0,7);""",
"""  investUi.acao[id]='';investUi.historico[id]=false;investUi.mes[id]=today().slice(0,7);"""
)

# Atualizar valor nao-cripto: mostrar valor atual e pre-preencher o campo.
rep(
"""      <div class="row row2">
        <input type="date" id="update-data-${item.id}" value="${today()}" title="Data em que você conferiu o valor atualizado."/>
        <input type="number" id="update-val-${item.id}" placeholder="Valor atual (R$)" min="0" step="0.01" title="Valor que existe hoje nesse investimento."/>
      </div>""",
"""      <div class="hint">Valor atual registrado: ${fmt(item.valorAtual||0)}. Informe o valor total que aparece hoje no banco.</div>
      <div class="row row2">
        <input type="date" id="update-data-${item.id}" value="${today()}" title="Data em que você conferiu o valor atualizado."/>
        <input type="number" id="update-val-${item.id}" value="${Number(item.valorAtual||0)}" placeholder="Valor atual (R$)" min="0" step="0.01" title="Valor total que aparece hoje nesse investimento."/>
      </div>"""
)

p.write_text(s, encoding="utf-8")

test = Path("tests/invest-modal-fluxo.test.js")
test.write_text(r'''const assert=require('assert'),fs=require('fs');
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
''', encoding="utf-8")

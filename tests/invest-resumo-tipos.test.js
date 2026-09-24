const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const src=html.match(/<script\s*>([\s\S]*?)<\/script>/)[1];

assert(html.includes('id="inv-type-summary"'),'Resumo por tipo ausente');
assert(html.includes('Por tipo de investimento'),'Titulo do resumo por tipo ausente');
assert(html.includes('<th>Valor inicial</th><th>Patrimônio atual</th><th>Rendimento</th><th>Rentabilidade</th>'),'Colunas esperadas ausentes');
assert(html.includes('<div class="label">Patrimônio atual</div>'),'Total geral deve representar patrimonio atual');
assert(html.includes('minimumFractionDigits:4,maximumFractionDigits:4'),'Rentabilidade deve ter quatro casas');
assert(!html.includes('aportes líquidos (aportes menos resgates)'),'Descricao antiga da base da porcentagem nao pode permanecer');

function extract(name,next){
  const start=src.indexOf('function '+name+'(');
  assert(start>=0,'Funcao ausente: '+name);
  const end=next?src.indexOf('function '+next+'(',start+1):src.length;
  assert(end>start,'Fim ausente: '+name);
  return src.slice(start,end);
}
const code=[extract('valorInicialInvestimento','resumoGrupoInvestimentos'),extract('resumoGrupoInvestimentos','renderInvestTypeSummary')].join('\n');
const ctx={Number,String,Array,Map,Math,ensureInvestHistory:item=>item.historico||[]};
vm.runInNewContext(code,ctx);

const a={valorAtual:600,totalAportado:1000,totalResgatado:500,historico:[{tipo:'aporte',origem:'saldo_inicial',valor:1000,data:'2026-01-01'}]};
const b={valorAtual:550,totalAportado:500,totalResgatado:0,historico:[{tipo:'aporte',origem:'saldo_inicial',valor:400,data:'2026-02-01'},{tipo:'aporte',origem:'aporte_manual',valor:100,data:'2026-03-01'}]};
const r=ctx.resumoGrupoInvestimentos([a,b]);
assert.strictEqual(r.inicial,1400,'Valor inicial deve somar apenas os valores iniciais informados');
assert.strictEqual(r.patrimonio,1150);
assert.strictEqual(r.aportado,1500);
assert.strictEqual(r.resgatado,500);
assert.strictEqual(r.rendimento,150,'Rendimento = patrimonio + resgates - aportes');
assert.strictEqual(r.pct,10,'Percentual deve usar total aportado como base; resgate nao deve reduzir o denominador');

console.log('PASS: resumo por tipo, valor inicial, rendimento com resgates e percentual de quatro casas');

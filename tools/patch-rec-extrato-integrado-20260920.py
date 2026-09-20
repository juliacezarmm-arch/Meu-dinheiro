from pathlib import Path


def once(text, old, new, description):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{description}: esperado 1 trecho; encontrados {count}')
    return text.replace(old, new, 1)

p = Path('js/recorrentes.js')
s = p.read_text(encoding='utf-8')
s = once(s,
    '.rec-form input,.rec-form select{width:100%}',
    '.rec-form input,.rec-form select{width:100%}#rec-toggle{width:100%;display:flex;justify-content:space-between;align-items:center;gap:10px;background:transparent;border:0;color:#f5f5f2;padding:0;text-align:left;font-size:15px;font-weight:750;cursor:pointer}#rec-toggle span{font-size:20px;color:#9FE1CB;line-height:1}#rec-body[hidden]{display:none!important}.rec-item-bottom{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-top:7px}.rec-item-date{font-size:12px;color:#c5c3ba;line-height:1.45;flex:1 1 225px}.rec-inline-actions{display:flex;align-items:center;gap:5px;flex-wrap:wrap;margin:0}.rec-inline-actions .rec-button{padding:6px 8px;font-size:11px;white-space:nowrap}',
    'estilos da área recolhível e ações na mesma linha')
s = once(s,
    '<div class="rec-top"><div><strong>Registros recorrentes</strong><p>Cadastre salário, débito automático, Pix ou transferência. Exclua o cadastro quando quiser; os lançamentos anteriores permanecem.</p></div><button type="button" class="rec-button primary" id="rec-open">+ Novo registro</button></div>\n<form class="rec-form"',
    '<div class="rec-top"><button type="button" id="rec-toggle" aria-expanded="true" aria-controls="rec-body">Registros recorrentes <span id="rec-toggle-symbol" aria-hidden="true">−</span></button></div>\n<div id="rec-body"><p class="rec-caption">Cadastre salário, débito automático, Pix ou transferência. Exclua o cadastro quando quiser; os lançamentos anteriores permanecem.</p><button type="button" class="rec-button primary" id="rec-open">+ Novo registro</button>\n<form class="rec-form"',
    'cabeçalho recolhível')
s = once(s,
    '<div class="rec-list" id="rec-list"></div>`;',
    '<div class="rec-list" id="rec-list"></div></div>`;',
    'fechar conteúdo recolhível')
s = once(s,
    " const area=$(editingRecMode==='cartao'?'rec-cartao-area':'recorrentes-area');\n area.insertBefore($('rec-form'),area.querySelector('.rec-list'));",
    " const area=$(editingRecMode==='cartao'?'rec-cartao-area':'recorrentes-area');\n if(editingRecMode==='conta')setRecAreaExpanded(true);\n const list=area.querySelector('.rec-list');list.parentNode.insertBefore($('rec-form'),list);",
    'editor permanece acessível dentro da área recolhível')
s = once(s,
    "function closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';placeCardRow();$('recorrentes-area').appendChild($('rec-form'));}",
    "function setRecAreaExpanded(expanded){\n $('rec-body').hidden=!expanded;\n $('rec-toggle').setAttribute('aria-expanded',String(expanded));\n $('rec-toggle-symbol').textContent=expanded?'−':'+';\n if(!expanded&&$('rec-form').parentElement===$('rec-body'))closeRecEditor();\n}\nfunction closeRecEditor(){$('rec-form').hidden=true;editingRecId=null;editingRecMode='conta';placeCardRow();$('rec-body').appendChild($('rec-form'));}",
    'expandir recolher e fechar editor')
start = s.index('function cashForecastsForMonth(y,m){')
end = s.index('\nfunction syncRecurring(){', start)
s = s[:start] + '''function cashForecastsForMonth(y,m){
 const last=isoDate(y,m,new Date(y,m+1,0).getDate());
 return S.recorrentes.filter(r=>r.metodo!=='cartao'&&!r.excluida).flatMap(r=>ocorrencias(r,last).filter(d=>d>today()&&d.slice(0,7)===last.slice(0,7)&&(!saldoInicialValido(S.saldoInicial)||d>S.saldoInicial.data)&&!originalJaRegistrado(r,d)).map(data=>({id:'rec-futuro-'+r.id+'-'+data,data,desc:r.nome,val:r.valor,tipo:r.tipo,categoria:r.categoria,subcategoria:r.subcategoria,pagamento:r.metodo,auto:true,previsto:true}))).sort((a,b)=>a.data.localeCompare(b.data));
}
// O Extrato exibe previsões na própria tabela; só o registro efetivo entra no saldo e no JSON.
window.cashRecurringForecasts=cashForecastsForMonth;
''' + s[end:]
s = once(s,
    '''    <div class="rec-item-sub"><strong style="color:#f5f5f2">${r.tipo==='saida'?'−':'+'}${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo]||r.metodo)}${card?' ('+escHtml(card.bank)+')':''}<br>${r.frequencia==='mensal'?(r.tipo==='entrada'?'Dia do recebimento: ':'Dia da cobrança: ')+(r.diaCobranca||Number(r.inicio.slice(8))):'Próxima programação desde: '+displayDate(r.inicio)}${r.fim?' · Encerramento anterior: '+displayDate(r.fim):''}${next?' · Próxima: '+displayDate(next):''}</div>
    <div class="rec-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir agora</button></div></div>`;''',
    '''    <div class="rec-item-sub"><strong style="color:#f5f5f2">${r.tipo==='saida'?'−':'+'}${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo]||r.metodo)}${card?' ('+escHtml(card.bank)+')':''}</div>
    <div class="rec-item-bottom"><span class="rec-item-date">${r.frequencia==='mensal'?(r.tipo==='entrada'?'Dia do recebimento: ':'Dia da cobrança: ')+(r.diaCobranca||Number(r.inicio.slice(8))):'Próxima programação desde: '+displayDate(r.inicio)}${r.fim?' · Encerramento anterior: '+displayDate(r.fim):''}${next?' · Próxima: '+displayDate(next):''}</span><span class="rec-inline-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir agora</button></span></div></div>`;''',
    'editar e excluir ao lado do dia')
s = once(s,
    "const oldExtratoRender=renderExtrato;\nrenderExtrato=function(){oldExtratoRender();const wrap=$('ext-wrap'),forecast=cashForecastsForMonth(extratoMes.getFullYear(),extratoMes.getMonth());\n if(!forecast.length)return;\n const box=document.createElement('div');box.className='rec-predictions';box.innerHTML='<strong>Recorrências previstas (não movimentam o saldo)</strong>'+forecast.map(x=>`<div class=\"rec-prediction\"><span>${displayDate(x.data)} · ${escHtml(x.desc)}<br><small>${escHtml(kindLabel[x.metodo]||x.metodo)}</small></span><b style=\"color:${x.tipo==='entrada'?'#9FE1CB':'#efaba4'}\">${x.tipo==='saida'?'−':'+'}${fmt(x.valor)}</b></div>`).join('');wrap.insertBefore(box,wrap.firstChild);\n};",
    '',
    'remover caixa avulsa de previsão no Extrato')
s = once(s,
    "$('rec-open').addEventListener('click',()=>openRecEditor());$('rec-close').addEventListener('click',closeRecEditor);",
    "$('rec-toggle').addEventListener('click',()=>setRecAreaExpanded($('rec-body').hidden));\n$('rec-open').addEventListener('click',()=>openRecEditor());$('rec-close').addEventListener('click',closeRecEditor);",
    'controle de minimizar e maximizar')
p.write_text(s, encoding='utf-8')

p = Path('index.html')
s = p.read_text(encoding='utf-8')
s = once(s,
    "  const rows=S.extrato.concat(resumoCartao?[resumoCartao]:[],linhaSaldo?[linhaSaldo]:[]).filter(r=>isSameMonthDate(r.data,viewYear,viewMonth)&&!(r.recorrenciaId&&saldoInicialValido(S.saldoInicial)&&(r.data<S.saldoInicial.data||S.saldoInicial.idsIgnorados.some(id=>String(id)===String(r.id))))).sort((a,b)=>b.data.localeCompare(a.data));",
    "  const rowsBase=S.extrato.concat(resumoCartao?[resumoCartao]:[],linhaSaldo?[linhaSaldo]:[]).filter(r=>isSameMonthDate(r.data,viewYear,viewMonth)&&!(r.recorrenciaId&&saldoInicialValido(S.saldoInicial)&&(r.data<S.saldoInicial.data||S.saldoInicial.idsIgnorados.some(id=>String(id)===String(r.id)))));\n  const proximas=typeof window.cashRecurringForecasts==='function'?window.cashRecurringForecasts(viewYear,viewMonth):[];\n  const rows=rowsBase.concat(proximas).sort((a,b)=>b.data.localeCompare(a.data));",
    'tabela única com previsões futuras não persistidas')
a=s.index('function renderExtrato(){'); b=s.index('\nfunction renderInvest(){',a)
block=s[a:b]
for name in ['entradasMes','resgatesMes','saidasMes','investimentoMes','metaMes','cartaoMes']:
    block=once(block,'const '+name+'=rows.filter','const '+name+'=rowsBase.filter','total '+name+' ignora previsões futuras')
block=once(block,"const tipoLabel=futuro?'previsto':", "const tipoLabel=r.previsto||futuro?'previsto':",'futuras identificadas sem rótulo de recorrência')
s=s[:a]+block+s[b:]
s=once(s,
    '<script src="js/recorrentes.js?v=20260920-json1"></script>',
    '<script src="js/recorrentes.js?v=20260920-integrado1"></script>',
    'atualizar versão de cache')
p.write_text(s, encoding='utf-8')

p = Path('tests/recorrentes.test.js')
t=p.read_text(encoding='utf-8')
t=once(t,'20260920-json1','20260920-integrado1','cache de testes')
t=once(t,
    "assert(js.includes('data-recdelete=\\\"${r.id}\\\">Excluir agora'),'Exclusão deve estar na lista dos registros criados');",
    "assert(js.includes('data-recdelete=\\\"${r.id}\\\">Excluir agora'),'Exclusão deve estar na lista dos registros criados');\nassert(js.includes('id=\\\"rec-toggle\\\"')&&js.includes('setRecAreaExpanded'),'Registros precisam abrir e fechar');\nassert(js.includes('rec-inline-actions')&&js.includes('rec-item-date'),'Editar e excluir devem ficar ao lado do dia');\nassert(!js.includes('Recorrências previstas (não movimentam o saldo)'),'Não mostrar caixa de previsões separada');\nassert(html.includes('rowsBase.concat(proximas)')&&html.includes('const entradasMes=rowsBase.filter'),'Previsões na tabela mas fora do saldo até a data');",
    'testes da nova interface e contabilização')
p.write_text(t,encoding='utf-8')

p = Path('tests/recorrentes-browser-smoke.py')
t=p.read_text(encoding='utf-8')
t=once(t,'20260920-json1','20260920-integrado1','cache do navegador')
t=once(t,
    " if(document.getElementById('rec-form').parentElement.id!=='recorrentes-area')throw Error('Cadastro da conta fora do Extrato');",
    " if(document.getElementById('rec-form').parentElement.id!=='rec-body')throw Error('Cadastro da conta fora do Extrato');\n elToggle=document.getElementById('rec-toggle');\n if(!elToggle||document.getElementById('rec-body').hidden)throw Error('Área de recorrência não abriu');",
    'formulário dentro do contêiner expansível')
t=once(t,
    " if(S.extrato.filter(x=>x.recorrenciaId===S.recorrentes[0].id).length!==1)throw Error('Lançamento duplicado');",
    " if(S.extrato.filter(x=>x.recorrenciaId===S.recorrentes[0].id).length!==1)throw Error('Lançamento duplicado');\n const amanha=new Date(today()+'T12:00:00');amanha.setDate(amanha.getDate()+1);\n const futureDate=isoDate(amanha.getFullYear(),amanha.getMonth(),amanha.getDate());\n S.recorrentes.push({id:989898,nome:'Despesa futura',valor:70,tipo:'saida',metodo:'debito_automatico',inicio:futureDate,frequencia:'mensal',diaCobranca:amanha.getDate(),categoria:'Casa',subcategoria:'Telefone',excluida:false});\n extratoMes=new Date(futureDate+'T12:00:00');renderExtrato();\n if(document.querySelector('#ext-wrap .rec-predictions'))throw Error('Caixa separada de previsões continua visível');\n if(!Array.from(document.querySelectorAll('#ext-wrap tbody tr')).some(tr=>tr.textContent.includes('Despesa futura')&&tr.textContent.includes('previsto')))throw Error('Futuro não entrou na tabela geral');\n if(S.extrato.some(x=>x.recorrenciaId===989898))throw Error('Futuro entrou antecipadamente como movimentação real');\n if(Math.abs(calcularSaldoDisponivelAte(today())-600)>0.001)throw Error('Previsão não pode reduzir saldo antes da data');\n el('rec-toggle').click();\n if(!el('rec-body').hidden||el('rec-toggle').getAttribute('aria-expanded')!=='false')throw Error('Recolher não funciona');\n el('rec-toggle').click();\n if(el('rec-body').hidden)throw Error('Expandir não funciona');\n if(!el('rec-list').querySelector('.rec-item-bottom .rec-inline-actions'))throw Error('Ações fora da linha do dia');",
    'teste de previsão integrada, saldo e recolhimento')
p.write_text(t,encoding='utf-8')
print('PATCH OK: recorrências na mesma tabela, efeito no saldo quando efetivadas, controles compactos e testes')
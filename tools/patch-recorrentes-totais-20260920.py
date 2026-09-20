from pathlib import Path

html_path=Path('index.html')
html=html_path.read_text(encoding='utf-8')
def once(old,new,what):
    global html
    n=html.count(old)
    assert n==1,f'{what}: encontrado {n} vezes, abortando por seguranca'
    html=html.replace(old,new,1)

css='#cc-wrap .cc-group-title:not(:first-child) th{padding-top:16px}'
more='''#cc-wrap .cc-group-subtotal td,#cc-wrap .cc-grand-total td{font-size:11px;overflow:visible;text-overflow:clip;white-space:normal;background:#171716;border-bottom:1px solid #3a3934;padding:8px 5px}
#cc-wrap .cc-group-subtotal td:first-child,#cc-wrap .cc-grand-total td:first-child{text-align:right;padding-right:10px;color:#c5c3ba}
#cc-wrap .cc-group-subtotal td.cc-money,#cc-wrap .cc-grand-total td.cc-money{white-space:nowrap;color:#9FE1CB;font-weight:800;text-align:left}
#cc-wrap .cc-grand-total td{border-top:1px solid #7abfa6;background:#202a25}
'''
once(css,css+'\n'+more,'CSS subtotais')
once('function renderCartao(){', '''// Somatorio de valores integrais das compras visiveis, em centavos.
// Nao e o valor devido na fatura (que utiliza somente as parcelas do mes).
function somarValoresTotaisCartao(itens){
  return itens.reduce((centavos,item)=>centavos+Math.round(Number(item.val||0)*100),0)/100;
}
function renderCartao(){''','funcao soma')
old='''      return `<tr class="cc-group-title"><th colspan="9" scope="rowgroup">${titulo}</th></tr>`+linhas;'''
new='''      const subtotal=somarValoresTotaisCartao(itens);
      return `<tr class="cc-group-title"><th colspan="9" scope="rowgroup">${titulo}</th></tr>`+linhas+
        `<tr class="cc-group-subtotal"><td colspan="7">Subtotal ${titulo} · valor integral das compras</td><td class="cc-money">${fmt(subtotal)}</td><td></td></tr>`;'''
once(old,new,'subtotal por grupo')
old="    }).join('')+'</tbody></table></div>';"
new='''    }).join('')+
    `<tr class="cc-grand-total"><td colspan="7">Total dos valores integrais exibidos · não é a fatura do mês</td><td class="cc-money">${fmt(somarValoresTotaisCartao(rows))}</td><td></td></tr>`+
    '</tbody></table></div>';'''
once(old,new,'soma geral')
html_path.write_text(html,encoding='utf-8')

js_path=Path('js/recorrentes.js')
js=js_path.read_text(encoding='utf-8')
old='''document.head.appendChild(style);'''
new='''// Extrato: mesma densidade e disposicao de linhas que a lista do Cartao.
style.textContent+=`#rec-list{gap:6px}#rec-list .rec-item{padding:8px 10px}#rec-list .rec-item-head{gap:7px;flex-wrap:wrap}#rec-list .rec-item-head .rec-inline-actions{margin-left:auto}#rec-list .rec-item-sub{margin-top:4px;font-size:11px;line-height:1.4}#rec-list .rec-item-date-inline{color:#c5c3ba}#rec-list .rec-inline-actions .rec-button{font-size:10px;padding:4px 6px}#rec-list .rec-item-name{min-width:0}@media(max-width:520px){#rec-list .rec-item-head{row-gap:5px}#rec-list .rec-item-head .rec-inline-actions{margin-left:0}}`;
document.head.appendChild(style);'''
assert js.count(old)==1,'CSS recorrente mudou, abortar'
js=js.replace(old,new,1)
old='''   return `<div class="rec-item"><div class="rec-item-head"><span class="rec-item-name">${escHtml(r.nome)}</span><span class="rec-tag${ended?' inactive':''}">${ended?'Encerrado':r.tipo==='entrada'?'Entrada':'Saída'}</span></div>
    <div class="rec-item-sub"><strong style="color:#f5f5f2">${r.tipo==='saida'?'−':'+'}${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo]||r.metodo)}${card?' ('+escHtml(card.bank)+')':''}</div>
    <div class="rec-item-bottom"><span class="rec-item-date">${r.frequencia==='mensal'?(r.tipo==='entrada'?'Dia do recebimento: ':'Dia da cobrança: ')+(r.diaCobranca||Number(r.inicio.slice(8))):'Próxima programação desde: '+displayDate(r.inicio)}${r.fim?' · Encerramento anterior: '+displayDate(r.fim):''}${next?' · Próxima: '+displayDate(next):''}</span><span class="rec-inline-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir agora</button></span></div></div>`;'''
new='''   const dia=r.frequencia==='mensal'?(r.tipo==='entrada'?'Dia do recebimento: ':'Dia da cobrança: ')+(r.diaCobranca||Number(r.inicio.slice(8))):'Desde: '+displayDate(r.inicio);
   return `<div class="rec-item"><div class="rec-item-head"><span class="rec-item-name">${escHtml(r.nome)}</span><span class="rec-tag${ended?' inactive':''}">${ended?'Encerrado':r.tipo==='entrada'?'Entrada':'Saída'}</span><span class="rec-inline-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir agora</button></span></div>
    <div class="rec-item-sub"><strong style="color:#f5f5f2">${r.tipo==='saida'?'−':'+'}${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo]||r.metodo)} · <span class="rec-item-date-inline">${dia}${r.fim?' · Encerramento: '+displayDate(r.fim):''}${next?' · Próxima: '+displayDate(next):''}</span></div></div>`;'''
assert js.count(old)==1,'Cartao de conta recorrente mudou, abortar'
js=js.replace(old,new,1)
js_path.write_text(js,encoding='utf-8')
print('PATCH OK: Extrato compacto como Cartao; dois subtotais e soma geral de valores integrais; sem mudar dados ou faturas')

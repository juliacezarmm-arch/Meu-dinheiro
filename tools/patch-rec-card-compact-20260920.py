from pathlib import Path
import re

p=Path('js/recorrentes.js')
s=p.read_text(encoding='utf-8')
def one(old,new):
    global s
    count=s.count(old)
    assert count==1, f'Trecho esperado {count} vezes: {old[:90]!r}'
    s=s.replace(old,new,1)

one('document.head.appendChild(style);', '''style.textContent+=`#rec-card-list{gap:6px}#rec-card-list .rec-item{padding:8px 10px}#rec-card-list .rec-item-head{gap:7px;flex-wrap:wrap}#rec-card-list .rec-item-head .rec-inline-actions{margin-left:auto}#rec-card-list .rec-item-sub{margin-top:4px;font-size:11px;line-height:1.4}#rec-card-list .rec-item-date-inline{color:#c5c3ba}#rec-card-list .rec-inline-actions .rec-button{font-size:10px;padding:4px 6px}#rec-card-open{margin:8px 0}#rec-card-list .rec-item-name{min-width:0}@media(max-width:520px){#rec-card-list .rec-item-head{row-gap:5px}#rec-card-list .rec-item-head .rec-inline-actions{margin-left:0}}`;
document.head.appendChild(style);''')
one('Assinaturas recorrentes no cartão','Pagamentos recorrentes')
one('<p class="rec-caption">Cadastre e edite assinaturas aqui. As cobranças aparecem junto às demais compras em Lançamentos.</p>','')
one('+ Nova assinatura','+ Novo pagamento')
one("editingRecMode==='cartao'?'assinatura':'registro recorrente'","editingRecMode==='cartao'?'pagamento recorrente':'registro recorrente'")
one("editingRecMode==='cartao'?'Nova assinatura recorrente':'Novo registro recorrente'","editingRecMode==='cartao'?'Novo pagamento recorrente':'Novo registro recorrente'")
one("editingRecMode==='cartao'?'Salvar assinatura':'Salvar recorrência'","editingRecMode==='cartao'?'Salvar pagamento':'Salvar recorrência'")
one('Nenhuma assinatura recorrente no cartão.','Nenhum pagamento recorrente no cartão.')
anchor='''   const card=S.cartoes.find(c=>String(c.id)===String(r.cartaoId));
   return `<div class="rec-item">'''
assert s.count(anchor)==1,'Render dos pagamentos não identificado'
compact='''   const card=S.cartoes.find(c=>String(c.id)===String(r.cartaoId));
   if(r.metodo==='cartao'){
    const cobranca=r.frequencia==='mensal'?'Dia da cobrança: '+(r.diaCobranca||Number(r.inicio.slice(8))):'Desde: '+displayDate(r.inicio);
    return `<div class="rec-item"><div class="rec-item-head"><span class="rec-item-name">${escHtml(r.nome)}</span><span class="rec-tag${ended?' inactive':''}">${ended?'Encerrado':'Saída'}</span><span class="rec-inline-actions"><button class="rec-button" type="button" data-recedit="${r.id}" aria-label="Editar ${escHtml(r.nome)}">✎ Editar</button><button class="rec-button danger" type="button" data-recdelete="${r.id}">Excluir agora</button></span></div>
    <div class="rec-item-sub"><strong style="color:#f5f5f2">−${fmt(r.valor)}</strong> · ${freq} · ${escHtml(kindLabel[r.metodo])}${card?' ('+escHtml(card.bank)+')':''} · <span class="rec-item-date-inline">${cobranca}${next?' · Próxima: '+displayDate(next):''}</span></div></div>`;
   }
   return `<div class="rec-item">'''
s=s.replace(anchor,compact,1)
p.write_text(s,encoding='utf-8')

p=Path('index.html')
html=p.read_text(encoding='utf-8')
html,count=re.subn(r'(<script src="js/recorrentes\.js\?v=)[^"]+("\s*></script>)',r'\g<1>20260920-compact1\2',html)
assert count==1,'Versão do JavaScript recorrente não encontrada'
p.write_text(html,encoding='utf-8')

p=Path('tests/recorrentes.test.js')
t=p.read_text(encoding='utf-8')
old='<script src="js/recorrentes.js?v=20260920-planejamento1"></script>'
assert t.count(old)==1,'Teste de versão não encontrado'
t=t.replace(old,'<script src="js/recorrentes.js?v=20260920-compact1"></script>',1)
assert t.count("assert(js.includes('id=\\\"rec-toggle\\\"')")==1
p.write_text(t,encoding='utf-8')
print('PATCH OK: pagamentos recorrentes compactos, sem mexer no ciclo de faturamento ou JSON')

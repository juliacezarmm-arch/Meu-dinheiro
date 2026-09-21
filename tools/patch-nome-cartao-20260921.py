from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def one(before,after,label):
 global s
 assert s.count(before)==1, f'{label}: encontrado {s.count(before)} vezes'
 s=s.replace(before,after,1)

one('''        </select>
        <input type="text" id="card-due-day"''','''        </select>
        <input type="text" id="card-name" placeholder="Nome do cartão (Black, Platinum, Azul...)" maxlength="60" autocomplete="off" title="Identifique o produto do cartão. Exemplos: Black, Platinum, Azul, LATAM Pass. Opcional."/>
      </div>
      <div class="row row2">
        <input type="text" id="card-due-day"''','cadastro: banco e nome separados')
one('''      <div class="row row1"><label class="input-caption" for="card-payment-day">Dia habitual do pagamento (opcional)</label><input type="number" id="card-payment-day"''','''        <input type="number" id="card-payment-day"''','cadastro: vencimento e pagamento lado a lado')
one(''' title="Dia em que você costuma pagar. A data efetiva será escolhida ao registrar cada pagamento."/></div>''',''' title="Dia em que você costuma pagar. A data efetiva será escolhida ao registrar cada pagamento."/>
      </div>''','cadastro: fechar segunda linha')
one('''  <label class="site-field">Banco / cartão<select id="card-edit-bank" required></select></label>''','''  <label class="site-field">Banco<select id="card-edit-bank" required></select></label>
  <label class="site-field">Nome do cartão (opcional)<input id="card-edit-name" type="text" maxlength="60" autocomplete="off" placeholder="Ex.: Black, Platinum, Azul, LATAM Pass"></label>''','modal: nome editavel')
one('''.bank-card .bank-name{font-size:15px;font-weight:800;margin-bottom:15px;position:relative;z-index:1}''','''.bank-card .bank-name{font-size:15px;font-weight:800;margin-bottom:15px;position:relative;z-index:1}.bank-card .bank-name.has-product{margin-bottom:3px}.bank-card .bank-product{font-size:12px;font-weight:750;position:relative;z-index:1;opacity:.93;margin-bottom:10px;overflow-wrap:anywhere}''','visual: produto abaixo do banco')
one("      if(key==='cartoes'&&r.color!==undefined", "      if(key==='cartoes'&&r.nome!==undefined&&(typeof r.nome!=='string'||r.nome.length>60))throw Error('Nome de cartão inválido.');\n      if(key==='cartoes'&&r.color!==undefined",'JSON: nome opcional seguro')
one(" document.getElementById('card-edit-due').value=String(card.dueDay||'');", " document.getElementById('card-edit-name').value=card.nome||'';\n document.getElementById('card-edit-due').value=String(card.dueDay||'');",'editar: carregar nome')
one(" const bank=document.getElementById('card-edit-bank').value,dueText=", " const bank=document.getElementById('card-edit-bank').value,nome=document.getElementById('card-edit-name').value.trim(),dueText=",'editar: capturar nome')
one(' card.bank=bank;card.dueDay=Number(dueText);', ' card.bank=bank;card.nome=nome;card.dueDay=Number(dueText);','editar: salvar nome')
one("pagamentoEmEdicao={cardId:card.id,mes};document.getElementById('card-payment-title').textContent='Marcar como pago · '+card.bank;", "pagamentoEmEdicao={cardId:card.id,mes};document.getElementById('card-payment-title').textContent='Marcar como pago · '+card.bank+(card.nome?' · '+card.nome:'');",'pagamento: nome no titulo')
one("desc:'Pagamento de fatura - '+card.bank+' '+mes", "desc:'Pagamento de fatura - '+card.bank+(card.nome?' · '+card.nome:'')+' '+mes",'pagamento: identificacao no registro')
one(" const bank=document.getElementById('card-bank').value,dueText=", " const bank=document.getElementById('card-bank').value,nome=document.getElementById('card-name').value.trim(),dueText=",'cadastro: capturar nome')
one(' S.cartoes.push({id:novoIdGlobal(),bank,dueDay:', ' S.cartoes.push({id:novoIdGlobal(),bank,nome,dueDay:','cadastro: persistir nome')
one(" document.getElementById('card-bank').value='';document.getElementById('card-due-day').value='';", " document.getElementById('card-bank').value='';document.getElementById('card-name').value='';document.getElementById('card-due-day').value='';",'cadastro: limpar nome')
one('''S.cartoes.map(c=>`<option value="${c.id}">${escHtml(c.bank)} - vence dia ${c.dueDay}</option>`)''','''S.cartoes.map(c=>`<option value="${c.id}">${escHtml(c.bank)}${c.nome?' · '+escHtml(c.nome):''} - vence dia ${c.dueDay}</option>`)''','seletor: identificar cartoes do mesmo banco')
one('''aria-label="Editar cartão ${escHtml(c.bank)}"''','''aria-label="Editar cartão ${escHtml(c.bank)}${c.nome?' '+escHtml(c.nome):''}"''','acessibilidade: editar')
one('''aria-label="Remover cartão ${escHtml(c.bank)}"''','''aria-label="Remover cartão ${escHtml(c.bank)}${c.nome?' '+escHtml(c.nome):''}"''','acessibilidade: remover')
one('''</div><div class="bank-chip"></div><div class="bank-name">${escHtml(c.bank)}</div>''','''</div><div class="bank-chip"></div><div class="bank-name${c.nome?' has-product':''}">${escHtml(c.bank)}</div>${c.nome?`<div class="bank-product">${escHtml(c.nome)}</div>`:''}''','cartao: nome no desenho')
one(" const registro={id:editingCartaoId||novoIdGlobal(),data,desc,tipo,val,parcelas:n,vencDia,closeDay:card.closeDay,cardId:card.id,banco:card.bank,cardColor:", " const registro={id:editingCartaoId||novoIdGlobal(),data,desc,tipo,val,parcelas:n,vencDia,closeDay:card.closeDay,cardId:card.id,banco:card.bank,nomeCartao:card.nome||'',cardColor:",'compra: preservar identificacao historica')
one("  S.cartao.forEach(c=>{\n    const d=new Date(c.data+'T12:00:00');\n    const n=c.parcelas||1;\n    // Cada parcela recebe centavos exatos.", "  S.cartao.forEach(c=>{\n    const d=new Date(c.data+'T12:00:00');\n    const n=c.parcelas||1;\n    const nomeProduto=(S.cartoes.find(card=>String(card.id)===String(c.cardId))||{}).nome||c.nomeCartao||'';\n    // Cada parcela recebe centavos exatos.",'parcelas: nome no detalhe')
one("+c.desc+(c.banco?' ('+c.banco+')':'')", "+c.desc+(c.banco?' ('+c.banco+(nomeProduto?' · '+nomeProduto:'')+')':'')",'parcelas: descricao com nome')
one("    return [{id:'fatura-pendente-'+card.id+'-'+mes,data:isoDate(y,m,dia),desc:'Fatura · '+card.bank,tipo:'cartao',categoria:'Cartão de crédito',subcategoria:card.bank,val:restante/100", "    const identificacao=card.bank+(card.nome?' · '+card.nome:'');\n    return [{id:'fatura-pendente-'+card.id+'-'+mes,data:isoDate(y,m,dia),desc:'Fatura · '+identificacao,tipo:'cartao',categoria:'Cartão de crédito',subcategoria:identificacao,val:restante/100",'extrato: identificar fatura')
one("        const desc=r.banco?`${r.desc} (${r.banco})`:r.desc;", "        const nomeProduto=(S.cartoes.find(card=>String(card.id)===String(r.cardId))||{}).nome||r.nomeCartao||'';\n        const desc=r.banco?`${r.desc} (${r.banco}${nomeProduto?' · '+nomeProduto:''})`:r.desc;",'lancamentos: identificar compra')
one("    prev.textContent=card.bank+': '+n+' parcelas", "    prev.textContent=card.bank+(card.nome?' · '+card.nome:'')+': '+n+' parcelas",'previa: parcelado')
one("    prev.textContent=card.bank+': à vista", "    prev.textContent=card.bank+(card.nome?' · '+card.nome:'')+': à vista",'previa: a vista')
one('''<script src="js/recorrentes.js?v=20260920-trio1"></script>''','''<script src="js/recorrentes.js?v=20260921-nome-cartao1"></script>''','atualizar cache JS')
p.write_text(s,encoding='utf-8')

j=Path('js/recorrentes.js');r=j.read_text(encoding='utf-8')
def rec(before,after,label):
 global r
 assert r.count(before)==1,f'{label}: encontrado {r.count(before)} vezes'
 r=r.replace(before,after,1)
rec('''S.cartoes.map(c=>`<option value="${c.id}">${escHtml(c.bank)} · vence dia ${c.dueDay}</option>`)''','''S.cartoes.map(c=>`<option value="${c.id}">${escHtml(c.bank)}${c.nome?' · '+escHtml(c.nome):''} · vence dia ${c.dueDay}</option>`)''','recorrentes: seletor')
rec("card?' ('+escHtml(card.bank)+')':''", "card?' ('+escHtml(card.bank)+(card.nome?' · '+escHtml(card.nome):'')+')':''",'recorrentes: identificar assinatura')
assert r.count('banco:card.bank,cardColor:card.color')==2,'Recorrentes: previsao e registro devem guardar a identificacao'
r=r.replace('banco:card.bank,cardColor:card.color',"banco:card.bank,nomeCartao:card.nome||'',cardColor:card.color")
j.write_text(r,encoding='utf-8')
print('PASS: campo opcional e edicao; identificacao nas listas, fatura, pagamentos e recorrentes. Sem mudanca financeira.')

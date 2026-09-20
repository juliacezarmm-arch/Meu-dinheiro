from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def replace_once(old,new,name):
 global s
 count=s.count(old)
 if count!=1: raise SystemExit(f'{name}: trecho encontrado {count} vezes (esperado 1)')
 s=s.replace(old,new,1)

replace_once('.app{max-width:760px;margin:0 auto;padding:1rem 0}', '.app{max-width:820px;margin:0 auto;padding:1rem 0}', 'largura')
replace_once('    <div class="section-title">Faturas e pagamentos</div>\n    <div id="cc-faturas" class="chart-panel"><div class="hint">Cadastre um cartão para acompanhar o pagamento.</div></div>\n', '', 'remover seção completa de faturas no cartão')
start=s.index("  const faturas=document.getElementById('cc-faturas');",s.index('function renderCartao(){'))
end=s.index("  const wrap=document.getElementById('cc-wrap');",start)
assert s.count("  const faturas=document.getElementById('cc-faturas');")==1
s=s[:start]+s[end:]
start=s.index("  wrap.innerHTML='<table><thead><tr>",s.index('function renderCartao(){'))
end=s.index('\n}\n\nfunction delCC(',start)
old=s[start:end]
assert 'rows.map(r=>' in old and 'Valor total' in old and 'const historico=' in old
new=r'''  // Separação somente visual: conserva as compras e todas as parcelas no JSON.
  // O valor da parcela corresponde ao mês da fatura que está sendo visualizado.
  const grupos=[['À vista',rows.filter(r=>r.tipo!=='parcelado')],['Parcelamentos',rows.filter(r=>r.tipo==='parcelado')]];
  wrap.innerHTML='<div class="cc-table-wrap"><table class="cc-launch-table"><thead><tr><th style="width:55px">Data</th><th>Descrição</th><th style="width:73px">Tipo</th><th style="width:53px">Vence</th><th style="width:55px">Parcelas</th><th style="width:105px">Valor da parcela</th><th style="width:105px">Valor total</th><th style="width:55px"></th></tr></thead><tbody>'+
    grupos.map(([titulo,itens])=>{
      if(!itens.length)return '';
      const linhas=itens.map(r=>{
        const d=new Date(r.data+'T12:00:00');
        const label=fmt(r.val);
        const qtdParcelas=Number(r.parcelas)||1;
        const parcelado=r.tipo==='parcelado';
        const tipoLabel=parcelado?'Parcelado':'À vista';
        const venc='dia '+(r.vencDia||10);
        const desc=r.banco?`${r.desc} (${r.banco})`:r.desc;
        const parcelaDoMes=parcelasNesteMes.find(x=>String(x.id).startsWith(String(r.id)+'-'));
        const valorDaParcela=parcelado?fmt(parcelaDoMes?parcelaDoMes.val:valorParcela(r,0)):'—';
        const historico=S.saldoInicial&&parcelaDoMes&&parcelaDoMes.data<S.saldoInicial.data;
        const cat=`${r.subcategoria||'Sem categoria'}${historico?' · Histórico anterior à abertura':''}`;
        const actions=r.previsto?`<button class="del" type="button" onclick="editRecurringCardForecast(${Number(r.recorrenciaId)})" aria-label="Editar assinatura" title="Edita a programação desta assinatura">✎</button>`:`<button class="del" onclick="editCartao(${r.id})" aria-label="Editar" title="Edita esta compra.">✎</button><button class="del" onclick="delCC(${r.id})" aria-label="Remover" title="Apaga esta compra do cartão."><i class="ti ti-x" aria-hidden="true"></i></button>`;
        return `<tr><td>${d.getDate().toString().padStart(2,'0')}/${(d.getMonth()+1).toString().padStart(2,'0')}</td><td class="cc-description">${escHtml(desc)}<div class="cc-subcategory">${escHtml(cat)}</div></td><td><span class="badge b-compra">${r.previsto?'Previsto':tipoLabel}</span></td><td>${venc}</td><td class="cc-installments">${parcelado?qtdParcelas+'x':'—'}</td><td class="cc-money">${valorDaParcela}</td><td class="cc-money">${label}</td><td class="cc-actions">${actions}</td></tr>`;
      }).join('');
      return `<tr class="cc-group-title"><th colspan="8" scope="rowgroup">${titulo}</th></tr>`+linhas;
    }).join('')+'</tbody></table></div>';
'''
s=s[:start]+new+s[end:]
replace_once('#cc-wrap td:nth-child(6){font-variant-numeric:tabular-nums;white-space:nowrap}', '#cc-wrap .cc-money{font-variant-numeric:tabular-nums;white-space:nowrap;overflow:visible;text-overflow:clip;font-size:11px;font-weight:700}\n#cc-wrap .cc-table-wrap{width:100%;overflow-x:auto}\n#cc-wrap .cc-launch-table{min-width:720px}\n#cc-wrap .cc-description{white-space:normal;overflow-wrap:anywhere;line-height:1.25}\n#cc-wrap .cc-subcategory{font-size:11px;color:var(--color-text-secondary);margin-top:3px}\n#cc-wrap .cc-installments{text-align:center;font-weight:700}\n#cc-wrap .cc-actions{white-space:nowrap;overflow:visible;text-align:right}\n#cc-wrap .cc-group-title th{background:#171716;color:#9FE1CB;font-size:11px;font-weight:800;letter-spacing:.02em;padding:10px 7px 6px;border-bottom:1px solid #363631}\n#cc-wrap .cc-group-title:not(:first-child) th{padding-top:16px}', 'estilos da tabela')
replace_once('#cc-wrap td:nth-child(5){font-size:11px;white-space:normal;line-height:1.25;font-weight:700}', '#cc-wrap td.cc-installments{font-size:11px;white-space:nowrap;line-height:1.25;font-weight:700}', 'estilo parcelas')
assert 'id="cc-faturas"' not in s and "getElementById('cc-faturas')" not in s
assert 'Valor da parcela</th>' in s and 'cc-group-title' in s and '.app{max-width:820px' in s
p.write_text(s,encoding='utf-8')
print('PATCH OK: painel de faturas removido integralmente da aba Cartão; divisão discreta à vista/parcelamentos; valores total e por parcela; largura 820px; cálculos e JSON preservados')

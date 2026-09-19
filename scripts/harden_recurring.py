from pathlib import Path
p=Path('js/recorrentes.js');s=p.read_text(encoding='utf-8')
def sub(old,new):
 global s
 assert s.count(old)==1,(old[:90],s.count(old))
 s=s.replace(old,new,1)
sub("const hoje=today(),horizon=new Date(hoje+'T12:00:00');horizon.setMonth(horizon.getMonth()+13);", "const hoje=today(),horizon=new Date(hoje+'T12:00:00');horizon.setMonth(horizon.getMonth()+36);\n const selecionado=new Date(cartaoMes.getFullYear(),cartaoMes.getMonth()+13,1,12);\n if(selecionado>horizon)horizon.setTime(selecionado.getTime());")
sub("const newRecord={id:existing?existing.id:novoIdGlobal(),nome,valor:","let novoId=novoIdGlobal();while(S.recorrentes.some(x=>String(x.id)===String(novoId)))novoId++;\n const newRecord={id:existing?existing.id:novoId,nome,valor:")
sub("syncRecurring();renderCartao();renderExtrato();updateResumo();\n};\nconst oldCardList=renderRegisteredCards;", "const added=syncRecurring();renderCartao();renderExtrato();updateResumo();\n // Restauração assíncrona pode reaplicar o status antigo de salvamento após o cadastro ser gerado.\n if(added)setTimeout(()=>{hasUnsavedChanges=true;saveData();},0);\n};\nconst oldCardList=renderRegisteredCards;")
sub("if(row&&row.recorrenciaId){openRecEditor(row.recorrenciaId);showPage('extrato',document.querySelectorAll('.nav button')[1]);return;}","if(row&&row.recorrenciaId){showPage('extrato',document.querySelectorAll('.nav button')[1]);openRecEditor(row.recorrenciaId);return;}")
sub("!Number.isSafeInteger(Number(r.id))||ids.has(String(r.id))||typeof r.nome!=='string'||r.nome.length>75", "!Number.isSafeInteger(Number(r.id))||Number(r.id)<=0||ids.has(String(r.id))||typeof r.nome!=='string'||!r.nome.trim()||r.nome.length>75")
sub("!['entrada','saida'].includes(r.tipo)||!['semanal','mensal','anual'].includes(r.frequencia)","!['entrada','saida'].includes(r.tipo)||!['cartao','debito_automatico','debito','pix','transferencia','recebimento'].includes(r.metodo)||!['semanal','mensal','anual'].includes(r.frequencia)")
p.write_text(s,encoding='utf-8')
p=Path('index.html');s=p.read_text(encoding='utf-8')
a="const rows=S.extrato.concat(resumoCartao?[resumoCartao]:[],linhaSaldo?[linhaSaldo]:[]).filter(r=>isSameMonthDate(r.data,viewYear,viewMonth)).sort((a,b)=>b.data.localeCompare(a.data));"
b="const rows=S.extrato.concat(resumoCartao?[resumoCartao]:[],linhaSaldo?[linhaSaldo]:[]).filter(r=>isSameMonthDate(r.data,viewYear,viewMonth)&&!(r.recorrenciaId&&saldoInicialValido(S.saldoInicial)&&(r.data<S.saldoInicial.data||S.saldoInicial.idsIgnorados.some(id=>String(id)===String(r.id))))).sort((a,b)=>b.data.localeCompare(a.data));"
assert s.count(a)==1
s=s.replace(a,b,1)
p.write_text(s,encoding='utf-8')
print('HARDEN_RECORRENTES_OK')

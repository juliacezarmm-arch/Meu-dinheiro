from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise RuntimeError(f'{label}: esperado um trecho, encontrado {count}')
    s=s.replace(old,new,1)

once('.save-status{grid-column:1/-1;min-height:14px;font-size:11px;color:#9FE1CB;text-align:center}', '''.save-status{grid-column:1/-1;justify-self:center;max-width:100%;min-height:23px;padding:4px 11px;border:1px solid #333b35;border-radius:999px;background:#151c18;color:#c5c3ba;font-size:11px;line-height:1.3;text-align:center;overflow-wrap:anywhere}
.save-status[data-state="saved"]{background:#15291f;border-color:#315f4b;color:#b2f0d7}
.save-status[data-state="unsaved"]{background:#2b2117;border-color:#866334;color:#ffda9b}
.save-status[data-state="idle"]{background:#171716;border-color:#34342f;color:#c5c3ba}''','estilo indicador do arquivo')

once("function setSaveStatus(text){\n const el=document.getElementById('save-status');if(!el)return;\n el.textContent=dataFileHandle?(dataFileHandle.name+(text?' · '+text:'')):(text||'Abra um arquivo JSON para começar.');\n}","""function setSaveStatus(text){
 const el=document.getElementById('save-status');if(!el)return;
 const state=text==='Salvo'?'saved':(/não salvo|falha|permita|autorize|alterado fora|indisponível|não autorizada/i.test(text||'')?'unsaved':'idle');
 el.dataset.state=state;
 el.textContent=dataFileHandle?(dataFileHandle.name+(text?' · '+text:'')):(text||'Abra um arquivo JSON para começar.');
}""",'status de gravacao acessivel')

once("setSaveStatus('Permita editar o arquivo JSON para continuar.');return false;","setSaveStatus('Edição não autorizada. Abra o JSON novamente e permita salvar.');return false;",'mensagem de recusa compacta')

p.write_text(s,encoding='utf-8')
print('PASS: aviso de arquivo compacto e estados acessiveis; permissao nativa e salvamento nao alterados')

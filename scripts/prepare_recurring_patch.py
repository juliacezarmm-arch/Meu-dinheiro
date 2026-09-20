from pathlib import Path
p=Path('scripts/fix_recurring_account_ui.py');s=p.read_text(encoding='utf-8')
a='"placeCardRow();",2)';b='"placeCardRow();",3)'
assert s.count(a)==1;s=s.replace(a,b)
a="change(\"$('rec-method').addEventListener('change',()=>{$('rec-card-row').hidden=editingRecMode!=='cartao';});\", \"$('rec-method').addEventListener('change',placeCardRow);\")"
b="change(\"$('rec-method').addEventListener('change',()=>{placeCardRow();});\", \"$('rec-method').addEventListener('change',placeCardRow);\")"
assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s,encoding='utf-8')
print('PREPARED_CORRECT_COUNT')

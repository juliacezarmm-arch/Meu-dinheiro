const fs=require('fs'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
assert(html.includes('#ext-wrap .ext-category-cell{font-size:12px;color:var(--color-text-secondary);white-space:normal;overflow-wrap:anywhere;overflow:visible;text-overflow:clip'),'Categoria do Extrato deve quebrar texto no desktop');
assert(html.includes('#ext-wrap .ext-category-cell{font-size:9px;line-height:1.2;white-space:normal;overflow-wrap:anywhere;overflow:visible'),'Categoria deve quebrar texto no celular');
assert(html.includes('#ext-wrap col.ext-col-category{width:18%}'),'Categoria ganha espaço no celular');
assert(html.includes('<th style="width:102px">Tipo</th>'),'Tipo do cartão deve caber Mensalidade');
assert(html.includes('#cc-wrap .cc-launch-table td:nth-child(3) .badge{white-space:nowrap}'),'Etiquetas do cartão não devem quebrar palavras');
assert(html.includes('#cc-wrap .cc-launch-table{min-width:735px}'),'Tabela permite rolagem horizontal quando necessário');
console.log('PASS: quebras de categoria e largura do tipo Mensalidade');

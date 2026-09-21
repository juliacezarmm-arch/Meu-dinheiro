const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const principal=html.match(/<script\s*>([\s\S]*?)<\/script>/);
assert(principal,'Script principal ausente');
const js=principal[1],rec=fs.readFileSync('js/recorrentes.js','utf8');
function fn(src,nome){const i=src.indexOf('function '+nome+'(');assert(i>=0,nome+' ausente');const j=src.indexOf('\nfunction ',i+10);assert(j>i,nome+' sem função seguinte');return src.slice(i,j);}
const start=js.indexOf('const CATEGORIAS='),end=js.indexOf('\nlet resumoMes',start);assert(start>0&&end>start,'Categorias ausentes');
const elements={},element=id=>elements[id]||(elements[id]={value:'',innerHTML:''});
const ctx=vm.createContext({document:{getElementById:element},$:element,escHtml:s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')});
vm.runInContext(js.slice(start,end)+'\nconst S={saldoInicial:null};\n'+['updateSubcategorias','updateCartaoSubcategorias'].map(n=>fn(js,n)).join('\n')+'\n'+fn(rec,'recurrenceSubcategories'),ctx);
const run=s=>vm.runInContext(s,ctx);
function options(id){return [...element(id).innerHTML.matchAll(/<option value="([^"]*)">/g)].map(m=>m[1]);}
for(const tipo of ['entrada','saida']){
 const categorias=run('Object.keys(CATEGORIAS.'+tipo+')');
 for(const categoria of categorias){
  element('ext-tipo').value=tipo;element('ext-categoria').value=categoria;
  run('updateSubcategorias()');
  assert.strictEqual(options('ext-subcategoria').filter(x=>x==='Outros').length,1,'Extrato '+tipo+'/'+categoria);
  assert.strictEqual(options('ext-subcategoria').at(-1),'Outros','Outros deve aparecer por último no Extrato');
  if(tipo==='saida'){
   element('cc-categoria').value=categoria;run('updateCartaoSubcategorias()');
   assert.strictEqual(options('cc-subcategoria').filter(x=>x==='Outros').length,1,'Cartão/'+categoria);
   assert.strictEqual(options('cc-subcategoria').at(-1),'Outros','Outros deve aparecer por último no Cartão');
  }
  element('rec-type').value=tipo;element('rec-category').value=categoria;element('rec-subcategory').value='Outros';
  run('recurrenceSubcategories()');
  assert.strictEqual(options('rec-subcategory').filter(x=>x==='Outros').length,1,'Recorrências '+tipo+'/'+categoria);
  assert.strictEqual(element('rec-subcategory').value,'Outros','Recorrência deve preservar Outros');
 }
}
run('S.saldoInicial={valor:100,data:"2026-09-21",idsIgnorados:[]}');
element('ext-tipo').value='entrada';element('ext-categoria').value='Outras entradas';run('updateSubcategorias()');
assert(!options('ext-subcategoria').includes('Dinheiro do mês passado'),'Regra do saldo inicial preservada');
assert(options('ext-subcategoria').includes('Outros'),'Outros também com saldo inicial');
assert(js.includes("'Outras entradas':['Dinheiro do mês passado'"),'Catálogo original preservado');
console.log('PASS: Outros em todas as subcategorias de Extrato, Cartão e Recorrências; sem duplicação e com regra de saldo inicial');

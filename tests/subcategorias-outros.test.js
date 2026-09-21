const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const match=html.match(/<script\s*>([\s\S]*?)<\/script>/);assert(match);
const src=match[1];
function get(name){const i=src.indexOf('function '+name+'(');assert(i>=0,name);const end=src.indexOf('\nfunction ',i+10);return src.slice(i,end<0?src.length:end);}
const start=src.indexOf('const CATEGORIAS=');assert(start>=0);const end=src.indexOf('\n};',start);assert(end>start);
const els={};for(const id of ['ext-tipo','ext-categoria','ext-subcategoria','cc-categoria','cc-subcategoria'])els[id]={value:'',innerHTML:''};
const ctx=vm.createContext({document:{getElementById:id=>els[id]},S:{saldoInicial:null}});
vm.runInContext(src.slice(start,end+3)+'\n'+['subcategoriasComOutros','updateSubcategorias','updateCartaoSubcategorias'].map(get).join('\n'),ctx);
const opts=id=>[...els[id].innerHTML.matchAll(/<option value="([^"]*)">/g)].map(m=>m[1]).slice(1);
for(const type of ['entrada','saida']){
  els['ext-tipo'].value=type;
  const cats=vm.runInContext('Object.keys(CATEGORIAS.'+type+')',ctx);
  for(const cat of cats){
    els['ext-categoria'].value=cat;
    vm.runInContext('updateSubcategorias()',ctx);
    const values=opts('ext-subcategoria');
    assert.strictEqual(values.at(-1),'Outros',type+' / '+cat);
    assert.strictEqual(values.filter(v=>v==='Outros').length,1,type+' / '+cat);
    const originals=vm.runInContext('CATEGORIAS.'+type+'['+JSON.stringify(cat)+']',ctx);
    for(const v of originals)assert(values.includes(v),type+' / '+cat+' perdeu '+v);
    if(type==='saida'){
      els['cc-categoria'].value=cat;vm.runInContext('updateCartaoSubcategorias()',ctx);
      assert.deepStrictEqual(opts('cc-subcategoria'),values,'Cartão divergiu do Extrato: '+cat);
    }
  }
}
ctx.S.saldoInicial={valor:1};els['ext-tipo'].value='entrada';els['ext-categoria'].value='Outras entradas';
vm.runInContext('updateSubcategorias()',ctx);
assert(!opts('ext-subcategoria').includes('Dinheiro do mês passado'));
assert.strictEqual(opts('ext-subcategoria').at(-1),'Outros');
els['ext-categoria'].value='';vm.runInContext('updateSubcategorias()',ctx);
assert.deepStrictEqual(opts('ext-subcategoria'),[],'Sem categoria, não oferecer subcategoria');
console.log('PASS: Outros por último e sem duplicação em todas as subcategorias de entrada, saída e cartão; opção de saldo anterior respeitada');

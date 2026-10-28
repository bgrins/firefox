const fs=require('fs'),vm=require('vm'),path=require('path');
const here=__dirname,policy=JSON.parse(fs.readFileSync(path.join(here,'POLICY.json'))),result={};
for(const page of Object.keys(policy.tests)) {
 const names=[],iframe={};
 const ctx=vm.createContext({test:(_,name)=>{if(typeof name!=="string")throw Error("unnamed");names.push(name)},iframe});
 const html=fs.readFileSync(path.join(here,'capture/testing/web-platform/tests',page),'utf8');
 for(const m of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
  const src=/src=["']([^"']+)["']/.exec(m[1]);
  if(src){if(src[1].startsWith('/resources/'))continue; const file=path.resolve(here,'capture/testing/web-platform/tests',path.dirname(page.slice(1)),src[1]);vm.runInContext(fs.readFileSync(file,'utf8'),ctx,{filename:file});}
  else vm.runInContext(m[2],ctx,{filename:page});
 }
 if(iframe.onload)iframe.onload();
 if(new Set(names).size!==names.length)throw Error("duplicate "+page);
 result[page]=names;
}
fs.writeFileSync(path.join(here,'ENUMERATED-SUBTESTS.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(Object.fromEntries(Object.entries(result).map(([k,v])=>[k,v.length]))));

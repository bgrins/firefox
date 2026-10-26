const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2],'utf8');const names=[];
const context=vm.createContext({promise_test:(callback,name)=>names.push(name)});
vm.runInContext(source,context,{timeout:1000});
const data=JSON.parse(vm.runInContext('JSON.stringify({config: CONFIG, cases: CASES})',context));
assert.equal(names.length,1);assert.equal(data.cases.length,6);
assert.deepEqual(data.cases.map(c=>c.id),['literal/1','variable/1','literal/8','variable/8','literal/32','variable/32']);
assert.deepEqual(data.config,{counts:[1,8,32],families:['literal','variable'],targets:16,warmups:2,measured:7,duration:1000,currentTime:500});
console.log(JSON.stringify({status:'INERT_REGISTRATION_PASS',harness_names:names,cases:data.cases.map(c=>c.id),rows:6*9,warmups:6*2,measured:6*7,callback_invoked:false}));

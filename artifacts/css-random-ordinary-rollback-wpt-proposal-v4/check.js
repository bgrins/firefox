const fs=require("fs"),vm=require("vm"),assert=require("assert");
function load(path) { const tests=[]; const c=vm.createContext({test:(fn,name)=>tests.push({fn,name}),assert_equals:(a,b,m)=>assert.strictEqual(a,b,m),assert_greater_than_equal:(a,b,m)=>assert.ok(a>=b,m)});vm.runInContext(fs.readFileSync(path,"utf8"),c);return {tests,c}; }
const old=load(process.argv[2]), fresh=load(process.argv[3]);
assert.strictEqual(old.tests.length,26);assert.strictEqual(fresh.tests.length,26);assert.strictEqual(new Set(fresh.tests.map(t=>t.name)).size,26);
let changed=0; for(let i=0;i<26;i++){ const a=old.tests[i],b=fresh.tests[i];if(a.name!==b.name || a.fn.toString()!==b.fn.toString()){changed++;assert.strictEqual(b.name,"A successful number line-height parse keeps random index one");}}
assert.strictEqual(changed,1);
const selected=fresh.tests.find(t=>t.name==="A successful number line-height parse keeps random index one");
function run(actual,expected){fresh.c.actual=actual;fresh.c.expected=expected;vm.runInContext('pair=()=>[{style:{lineHeight:"same-key"},computed:actual},{style:{lineHeight:"same-key"},computed:expected}];getComputedStyle=e=>({lineHeight:e.computed});',fresh.c);selected.fn({});}
run("20px","20px");assert.throws(()=>run("0px","0px"),/Reference resolves/);assert.throws(()=>run("21px","20px"),/Computed value/);
process.stdout.write(JSON.stringify({syntax:true,tests:26,unique_names:26,unchanged_callbacks_and_names:25,positive_control:true,rejected_zero_equality:true,rejected_value_mismatch:true,names:fresh.tests.map(t=>t.name)},null,2)+"\n");
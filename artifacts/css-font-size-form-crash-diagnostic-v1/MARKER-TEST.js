const assert = require('node:assert/strict');
const messages=[];const mode="diagnostic-control";function dump(s){messages.push(JSON.parse(s.slice(s.indexOf(" ")+1)));}
    let phase = "setup";
    let sequence = 0;
    const mark = stage => dump("CSS_SIZEFORMS_STAGE " + JSON.stringify({mode, phase, sequence: ++sequence, stage}) + "\n");
    const read = (stage, operation) => {
      mark(stage + ":before");
      const value = operation();
      mark(stage + ":after");
      return value;
    };
    mark("body:start");

let count=0;assert.equal(read("value",()=>{count++;return 37}),37);assert.equal(count,1);
const error=new Error("control");assert.throws(()=>read("throw",()=>{count++;throw error}),e=>e===error);assert.equal(count,2);
assert.deepEqual(messages.map(x=>x.stage),["body:start","value:before","value:after","throw:before"]);
assert.deepEqual(messages.map(x=>x.sequence),[1,2,3,4]);assert(messages.every(x=>x.mode===mode&&x.phase==="setup"));
console.log("marker exact-once return/throw/order controls passed");

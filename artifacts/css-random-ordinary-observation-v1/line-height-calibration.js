async () => {
 const frame=document.createElement("iframe");document.body.append(frame);
 try {
  const d=frame.contentDocument;d.open();d.write("<!doctype html><body>");d.close();
  const w=frame.contentWindow;
  const cases=[
   ["literal","2"],["calc-literal","calc(2)"],["fixed-number","random(fixed .25, 1, 3)"],
   ["named-number","random(--line-calibration, 1, 3)"],["named-length","random(--line-calibration, 10px, 30px)"],
   ["indexed-number","random(property-index-scoped, 1, 3)"],["key1-number","random(ua-line-height-1, 1, 3)"],
   ["key1-length","random(ua-line-height-1, 10px, 30px)"],["named-ratio","calc(random(--line-calibration, 10px, 30px) / 10px)"]
  ];
  const items=cases.map(([id,value])=>{const el=d.createElement("div");el.style.cssText="font-size:10px;font-family:monospace;margin:0;padding:0;border:0";el.style.lineHeight=value;el.textContent="x";d.body.append(el);return {id,value,el};});
  await new Promise(r=>w.requestAnimationFrame(()=>w.requestAnimationFrame(r)));
  return items.map(({id,value,el})=>{const s=w.getComputedStyle(el);return {id,value,supported:w.CSS.supports("line-height",value),specified:el.style.lineHeight,lineHeight:s.lineHeight,fontSize:s.fontSize,height:el.getBoundingClientRect().height};});
 }finally{frame.remove();}
}

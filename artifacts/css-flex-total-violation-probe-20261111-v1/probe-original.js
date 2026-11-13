() => {
 const rows = [];
 for (const direction of ["row","row-reverse","column","column-reverse"]) {
  const horizontal = direction.startsWith("row");
  const size = horizontal ? "width" : "height";
  const min = horizontal ? "minWidth" : "minHeight";
  for (const [count,magnitude] of [[5,1000],[3,10000000],[4,10000000],[5,10000000],[7,10000000]]) {
   const c=document.createElement("div");
   c.style.cssText="position:fixed;left:0;top:0;display:flex;width:1000px;height:1000px;align-items:flex-start";
   c.style.flexDirection=direction;
   for(let i=0;i<count;i++) {
    const e=document.createElement("div");
    e.style.cssText="width:0;height:0;min-width:0;min-height:0";
    e.style.flex="0 1 "+magnitude+"px"; e.style[min]=magnitude+"px"; c.append(e);
   }
   const last=document.createElement("div");
   last.style.cssText="width:0;height:0;min-width:0;min-height:0;flex:0 0.0000152587890625 1000px";
   c.append(last); document.body.append(c);
   const actual=last.getBoundingClientRect()[size];
   rows.push({direction,count,magnitude,actual,expected:Math.max(0,1000-count*magnitude/65536),primarySizes:[...c.children].slice(0,-1).map(e=>e.getBoundingClientRect()[size])});
   c.remove();
  }
 }
 return {ua:navigator.userAgent,rows};
}

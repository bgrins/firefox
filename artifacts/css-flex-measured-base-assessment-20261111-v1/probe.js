() => {
  const style = document.createElement("style");
  style.textContent = "html,body { margin:0 } .host { display:flex; flex-direction:column; width:10px; position:absolute; top:0; left:0; } .item { flex:1 1 auto; min-height:0; }";
  document.head.append(style);
  const rows = [];
  for (const childHeight of [1000, 10000000, 15000000, 17000000]) {
    for (const margin of [0, -10000000, -17000000]) {
      const host = document.createElement("div");
      host.className = "host";
      host.style.height = "10000000px";
      const item = document.createElement("div");
      item.className = "item";
      item.style.marginBlock = margin + "px";
      for (let i=0; i<2; i++) {
        const child = document.createElement("div");
        child.style.height = childHeight + "px";
        item.append(child);
      }
      host.append(item);
      document.body.append(host);
      const rect = item.getBoundingClientRect();
      rows.push({childHeight, margin, actual:rect.height, computed:getComputedStyle(item).height, children:Array.from(item.children, c=>c.getBoundingClientRect().height)});
      host.remove();
    }
  }
  return {userAgent:navigator.userAgent, rows};
}

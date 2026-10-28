async () => {
async function probeAtan2RelativeZero() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "position:fixed;left:0;top:0;width:320px;height:180px;border:0;visibility:hidden";
  const loaded = new Promise(resolve => frame.addEventListener("load", resolve, {once:true}));
  frame.srcdoc = "<!doctype html><meta charset=utf-8><style>html,body{margin:0;zoom:1}div{position:absolute;width:10px;height:10px;transform-origin:0 0}</style>";
  document.documentElement.append(frame);
  try {
    await loaded;
    const win = frame.contentWindow;
    const doc = frame.contentDocument;
    const rows = [[1,1], [1,-1], [-1,1], [-1,-1]].map(([y,x]) => {
      const nodes = {};
      for (const role of ["relative", "literal", "pixels", "positiveControl"]) {
        nodes[role] = doc.createElement("div");
        doc.body.append(nodes[role]);
      }
      const expression = `rotate(atan2(${y}em, ${x}em))`;
      nodes.relative.style.transform = expression;
      nodes.positiveControl.style.transform = `rotate(atan2(${y * 10}px, ${x * 10}px))`;
      return {y,x,expression,nodes,snapshots:[]};
    });
    const matrix = element => {
      const css = win.getComputedStyle(element).transform;
      const m = new win.DOMMatrixReadOnly(css);
      return {css, values:[m.a,m.b,m.c,m.d,m.e,m.f]};
    };
    const cssNumber = n => Object.is(n,-0) ? "-0" : String(n);
    for (const font of [10,0,10]) {
      for (const row of rows) {
        row.nodes.relative.style.fontSize = `${font}px`;
        const y = row.y * font;
        const x = row.x * font;
        const expectedDegrees = Math.atan2(y,x) * 180 / Math.PI;
        row.nodes.literal.style.transform = `rotate(${expectedDegrees}deg)`;
        row.nodes.pixels.style.transform = `rotate(atan2(${cssNumber(y)}px, ${cssNumber(x)}px))`;
        const actual = matrix(row.nodes.relative);
        const literal = matrix(row.nodes.literal);
        const pixels = matrix(row.nodes.pixels);
        row.snapshots.push({font, computedFont:win.getComputedStyle(row.nodes.relative).fontSize,
          expectedDegrees, resolvedY:cssNumber(y), resolvedX:cssNumber(x),
          specified:row.nodes.relative.style.transform, actual, literal, pixels,
          positiveControl:matrix(row.nodes.positiveControl),
          matchesLiteral:actual.values.every((n,i) => Math.abs(n-literal.values[i]) < 0.00001),
          pixelsMatchLiteral:pixels.values.every((n,i) => Math.abs(n-literal.values[i]) < 0.00001)});
      }
    }
    return {userAgent:navigator.userAgent, observationOnly:true,
      support:CSS.supports("transform","rotate(atan2(1em,1em))"),
      rows:rows.map(({nodes,...row}) => row)};
  } finally {
    frame.remove();
  }
}

return await probeAtan2RelativeZero();
}

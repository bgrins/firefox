async function observeOrdinarySiblingContext() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:400px;height:200px";
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const results = [];
    for (const property of ["width", "opacity", "font-weight"]) {
      for (const basis of ["count", "index"]) {
        doc.body.replaceChildren();
        const expression = property === "width" ? `calc(sibling-${basis}() * 10px)` :
          property === "opacity" ? `calc(sibling-${basis}() / 10)` : `calc(sibling-${basis}() * 100)`;
        const literal = input => property === "width" ? `${input * 10}px` : property === "opacity" ? `${input / 10}` : `${input * 100}`;
        const style = doc.createElement("style");
        style.textContent = `.probe { animation-name:none; transition-property:none; ${property}:${expression}; }`;
        const left = doc.createElement("div");
        const right = doc.createElement("div");
        const referenceHolder = doc.createElement("div");
        const targets = [0, 1, 2].map(() => {
          const target = doc.createElement("div");
          target.className = "probe";
          return target;
        });
        left.append(targets[0], targets[1]);
        right.append(doc.createElement("div"), doc.createElement("div"), targets[2]);
        doc.body.append(style, left, right, referenceHolder);
        const references = new Map([1, 2, 3, 4].map(input => {
          const reference = doc.createElement("div");
          reference.style.setProperty(property, literal(input));
          referenceHolder.append(reference);
          return [input, reference];
        }));
        const extraLeft = doc.createElement("div");
        const extraRight = doc.createElement("div");
        const row = {property, basis, expression, supported:win.CSS.supports(property, expression),
          specified:style.sheet.cssRules[0].style.getPropertyValue(property), snapshots:[]};
        for (const phase of ["initial", "siblings added", "restored"]) {
          if (phase === "siblings added") {
            left.prepend(extraLeft);
            right.append(extraRight);
          } else if (phase === "restored") {
            extraLeft.remove();
            extraRight.remove();
          }
          const leftStyle = win.getComputedStyle(left);
          const rightStyle = win.getComputedStyle(right);
          const parentDifferences = Array.from(leftStyle).filter(name =>
            leftStyle.getPropertyValue(name) !== rightStyle.getPropertyValue(name)).map(name =>
            ({property:name, left:leftStyle.getPropertyValue(name), right:rightStyle.getPropertyValue(name)}));
          const values = targets.map(target => {
            const index = Array.from(target.parentElement.children).indexOf(target) + 1;
            const count = target.parentElement.children.length;
            const input = basis === "count" ? count : index;
            const reference = references.get(input);
            return {index, count, input,
              actual:win.getComputedStyle(target).getPropertyValue(property),
              expected:win.getComputedStyle(reference).getPropertyValue(property),
              literalSpecified:reference.style.getPropertyValue(property),
              repeat:win.getComputedStyle(target).getPropertyValue(property),
              width:property === "width" ? target.getBoundingClientRect().width : null,
              literalWidth:property === "width" ? reference.getBoundingClientRect().width : null,
              animations:target.getAnimations().length};
          });
          row.snapshots.push({phase, parentDifferences, values});
        }
        results.push(row);
      }
    }
    return {schema:1, scope:"ordinary properties; no proof of a specific cache path", results};
  } finally {
    frame.remove();
  }
}

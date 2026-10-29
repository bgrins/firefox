async function observeContextualEasingSharing() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:400px;height:200px";
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const cases = [
      ["steps index", "steps(calc(sibling-index()), end)", "index", n => `steps(${n}, end)`],
      ["steps count", "steps(calc(sibling-count()), end)", "count", n => `steps(${n}, end)`],
      ["bezier", "cubic-bezier(0, calc(sibling-index() / 4), 1, 1)", "index",
       n => `cubic-bezier(0, ${n / 4}, 1, 1)`],
      ["linear output", "linear(0, calc(sibling-index() / 4) 50%, 1)", "index",
       n => `linear(0, ${n / 4} 50%, 1)`],
      ["linear second position", "linear(0 0% calc(sibling-index() * 20%), 1)", "index",
       n => `linear(0 0% ${n * 20}%, 1)`],
    ];
    const results = [];
    for (const property of ["animation-timing-function", "transition-timing-function"]) {
      for (const [name, expression, basis, literal] of cases) {
        doc.body.replaceChildren();
        const style = doc.createElement("style");
        style.textContent = `.probe { animation-name:none; transition-property:none; ${property}:${expression}; }`;
        doc.body.append(style);
        const left = doc.createElement("div");
        const right = doc.createElement("div");
        const referenceHolder = doc.createElement("div");
        const targets = [0, 1, 2].map(() => {
          const el = doc.createElement("div");
          el.className = "probe";
          return el;
        });
        left.append(targets[0], targets[1]);
        right.append(doc.createElement("div"), doc.createElement("div"), targets[2]);
        doc.body.append(left, right, referenceHolder);
        const extraLeft = doc.createElement("div");
        const extraRight = doc.createElement("div");
        const references = new Map([1, 2, 3, 4].map(input => {
          const el = doc.createElement("div");
          el.style.setProperty(property, literal(input));
          referenceHolder.append(el);
          return [input, el];
        }));
        const row = {
          property, name, expression,
          supported: win.CSS.supports(property, expression),
          specified: style.sheet.cssRules[0].style.getPropertyValue(property),
          snapshots: [],
        };
        for (const phase of ["initial", "siblings added", "restored"]) {
          if (phase === "siblings added") {
            left.prepend(extraLeft);
            right.append(extraRight);
          } else if (phase === "restored") {
            extraLeft.remove();
            extraRight.remove();
          }
          await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
          const values = targets.map(target => {
            const position = Array.from(target.parentElement.children).indexOf(target) + 1;
            const count = target.parentElement.children.length;
            const expectedInput = basis === "index" ? position : count;
            const reference = references.get(expectedInput);
            const expected = win.getComputedStyle(reference).getPropertyValue(property);
            const actual = win.getComputedStyle(target).getPropertyValue(property);
            return {
              position, count, expectedInput, actual, expected,
              literalSpecified: reference.style.getPropertyValue(property),
              repeat: win.getComputedStyle(target).getPropertyValue(property),
              animations: target.getAnimations().length,
              animationName: win.getComputedStyle(target).animationName,
              transitionProperty: win.getComputedStyle(target).transitionProperty,
            };
          });
          row.snapshots.push({phase, values});
        }
        results.push(row);
      }
    }
    return {schema: 1, scope: "static CSS easing diagnostic; no proof that sharing occurred", results};
  } finally {
    frame.remove();
  }
}

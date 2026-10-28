async function observeRelativeSteppedZero() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:320px;height:180px;border:0";
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    doc.open();
    doc.write("<!doctype html><style>html,body{margin:0}#container{container-type:size;position:relative;height:100px}i{display:block;position:absolute;height:1px;min-width:0;max-width:none;padding:0;border:0;box-sizing:content-box}</style><div id=container></div>");
    doc.close();
    const container = doc.getElementById("container");
    const operations = {
      mod: unit => `calc(10px + mod(3${unit}, 2${unit}))`,
      rem: unit => `calc(10px + rem(3${unit}, 2${unit}))`,
      round: unit => `calc(10px + round(nearest, 3${unit}, 2${unit}))`,
      division: unit => `calc(10px + (1${unit} / 1${unit}) * 1px)`,
      cancellation: unit => `calc(10px + 1${unit} - 1${unit})`,
      zeroProduct: unit => `calc(10px + 0 * 1${unit})`,
    };
    const pixelExpression = (operation, basis) => {
      if (operation === "mod" || operation === "rem") {
        return `calc(10px + ${operation}(${3 * basis}px, ${2 * basis}px))`;
      }
      if (operation === "round") {
        return `calc(10px + round(nearest, ${3 * basis}px, ${2 * basis}px))`;
      }
      if (operation === "division") {
        return `calc(10px + (${basis}px / ${basis}px) * 1px)`;
      }
      if (operation === "cancellation") return `calc(10px + ${basis}px - ${basis}px)`;
      return `calc(10px + 0 * ${basis}px)`;
    };
    const rows = [];
    for (const unit of ["em", "rem", "cqw"]) {
      for (const [operation, expression] of Object.entries(operations)) {
        const elements = Array.from({length: 5}, () => {
          const element = doc.createElement("i");
          container.append(element);
          return element;
        });
        const [target, resolved, literal, absolute, calibration] = elements;
        const specified = expression(unit);
        target.style.width = specified;
        absolute.style.width = expression("px");
        calibration.style.width = `1${unit}`;
        for (const basis of [10, 0, 10]) {
          doc.documentElement.style.fontSize = `${unit === "rem" ? basis : 16}px`;
          container.style.width = `${unit === "cqw" ? basis * 100 : 100}px`;
          for (const element of elements) element.style.fontSize = `${unit === "em" ? basis : 16}px`;
          const expected = operation === "cancellation" || operation === "zeroProduct" ? 10
            : basis === 0 ? 0 : operation === "round" ? 10 + 4 * basis
            : operation === "division" ? 11 : 10 + basis;
          resolved.style.width = pixelExpression(operation, basis);
          literal.style.width = `${expected}px`;
          await new Promise(resolve => frame.contentWindow.requestAnimationFrame(() => frame.contentWindow.requestAnimationFrame(resolve)));
          const read = element => ({specified: element.style.width, width: frame.contentWindow.getComputedStyle(element).width, rect: element.getBoundingClientRect().width});
          rows.push({unit, operation, basis, expected, supported: frame.contentWindow.CSS.supports("width", specified), target: read(target), resolved: read(resolved), literal: read(literal), absolute: read(absolute), calibration: read(calibration), targetFont: frame.contentWindow.getComputedStyle(target).fontSize, rootFont: frame.contentWindow.getComputedStyle(doc.documentElement).fontSize, containerWidth: frame.contentWindow.getComputedStyle(container).width});
        }
        elements.forEach(element => element.remove());
      }
    }
    return {rows, count: rows.length};
  } finally {
    frame.remove();
  }
}

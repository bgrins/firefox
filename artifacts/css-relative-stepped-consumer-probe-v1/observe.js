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

async function observeRelativeSteppedConsumers() {
  const original = await observeRelativeSteppedZero();
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:320px;height:180px;border:0";
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    doc.open();
    doc.write("<!doctype html><style>html,body{margin:0}i{position:absolute;display:block;width:1em;height:1px}@keyframes sample{from{opacity:0}to{opacity:1}}.sample{animation:sample 1000ms linear -750ms 1 both paused}</style><main></main>");
    doc.close();
    const win = frame.contentWindow;
    const holder = doc.querySelector("main");
    const operation = (op, unit, basis = 1) => op === "round"
      ? `round(nearest, ${3 * basis}${unit}, ${2 * basis}${unit})`
      : `${op}(${3 * basis}${unit}, ${2 * basis}${unit})`;
    const wrap = (kind, value) => {
      if (kind === "integer") return `calc(1 + sign(${value}))`;
      if (kind === "steps") return `steps(calc(1 + sign(${value})), end)`;
      if (kind === "bezier") return `cubic-bezier(0, sign(${value}), 1, 1)`;
      return `linear(sign(${value}), 1)`;
    };
    const literal = (kind, basis) => {
      if (kind === "integer") return basis ? "2" : "0";
      if (kind === "steps") return basis ? "steps(2, end)" : "steps(1, end)";
      if (kind === "bezier") return basis ? "cubic-bezier(0, 1, 1, 1)" : "cubic-bezier(0, 0, 1, 1)";
      return basis ? "linear(1, 1)" : "linear(0, 1)";
    };
    const rows = [];
    const cases = ["mod", "rem", "round"].flatMap(op =>
      ["integer", "steps", "bezier", "linear"].map(kind => ({op, kind})));
    cases.push({op: "sign-only", kind: "integer"});
    for (const {op, kind} of cases) {
      const property = kind === "integer" ? "z-index" : "animation-timing-function";
      const elements = Array.from({length: 4}, () => {
        const element = doc.createElement("i");
        if (kind !== "integer") element.className = "sample";
        holder.append(element);
        return element;
      });
      const [target, resolved, control, absolute] = elements;
      const expression = op === "sign-only" ? "calc(1 + sign(1em))" : wrap(kind, operation(op, "em"));
      target.style.setProperty(property, expression);
      absolute.style.setProperty(property, op === "sign-only" ? "calc(1 + sign(1px))" : wrap(kind, operation(op, "px")));
      const sampleAPI = (value, basis, location) => {
        const element = doc.createElement("i");
        element.style.fontSize = `${basis}px`;
        holder.append(element);
        let animation;
        try {
          const keyframes = location === "keyframe"
            ? [{opacity: 0, easing: value}, {opacity: 1}]
            : [{opacity: 0}, {opacity: 1}];
          animation = element.animate(keyframes, {duration: 1000, fill: "both", easing: location === "effect" ? value : "linear"});
          animation.pause();
          animation.currentTime = 750;
          return {admitted: true, easing: animation.effect.getTiming().easing,
            keyframes: animation.effect.getKeyframes().map(k => ({offset: k.computedOffset, easing: k.easing})),
            progress: animation.effect.getComputedTiming().progress,
            opacity: win.getComputedStyle(element).opacity};
        } catch (error) {
          return {admitted: false, error: {name: error.name, message: error.message}};
        } finally {
          if (animation) animation.cancel();
          element.remove();
        }
      };
      for (const basis of [10, 0, 10]) {
        for (const element of elements) element.style.fontSize = `${basis}px`;
        const pixel = op === "sign-only" ? `calc(1 + sign(${basis}px))` : wrap(kind, operation(op, "px", basis));
        const expectedLiteral = op === "sign-only" ? (basis ? "2" : "1") : literal(kind, basis);
        resolved.style.setProperty(property, pixel);
        control.style.setProperty(property, expectedLiteral);
        await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
        const read = element => {
          const style = win.getComputedStyle(element);
          return {specified: element.style.getPropertyValue(property), computed: style.getPropertyValue(property),
            fontSize: style.fontSize, width: style.width, rect: element.getBoundingClientRect().width,
            opacity: style.opacity, animationCount: element.getAnimations().length};
        };
        const row = {operation: op, kind, basis, property, expression, pixelExpression: pixel,
          literalExpression: expectedLiteral,
          supports: {target: win.CSS.supports(property, expression), resolved: win.CSS.supports(property, pixel),
            literal: win.CSS.supports(property, expectedLiteral)},
          target: read(target), resolved: read(resolved), literal: read(control), absolute: read(absolute),
          expectedInteger: kind === "integer" ? Number(expectedLiteral) : null,
          easingOracle: kind === "integer" ? null : "diagnostic; contextual admission and zero-step range policy require separate adjudication"};
        if (kind !== "integer") {
          row.api = {};
          for (const location of ["effect", "keyframe"]) {
            row.api[location] = {};
            for (const [role, value] of Object.entries({target: expression, resolved: pixel, literal: expectedLiteral})) {
              row.api[location][role] = sampleAPI(value, basis, location);
            }
          }
        }
        rows.push(row);
      }
      elements.forEach(element => element.remove());
    }
    return {original, consumers: {rows, cases: cases.length, count: rows.length},
      mode: "raw diagnostic; unsupported or rejected is an observation, never a passing repair",
      waapiSampling: "fresh effect and keyframe objects per state; not an invalidation proof"};
  } finally {
    frame.remove();
  }
}

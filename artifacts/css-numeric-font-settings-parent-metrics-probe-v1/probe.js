(async () => {
  const settings = [
    { property: "font-variation-settings", tag: "wdth", includeCh: false },
    { property: "font-variation-settings", tag: "XPRB", includeCh: true },
    { property: "font-feature-settings", tag: "XPRB", includeCh: true },
  ];
  const forms = [
    { name: "literal", value: '"XPRB" 20' },
    { name: "absolute-ratio", value: '"XPRB" calc(20px / 1px)' },
    { name: "em-ratio", value: '"XPRB" calc(1em / 1px)' },
    { name: "ch-ratio", value: '"XPRB" calc(1ch / 1px)' },
  ];
  const phases = [
    { name: "p20-c40", parent: 20, child: 40 },
    { name: "p30-c40", parent: 30, child: 40 },
    { name: "p30-c60", parent: 30, child: 60 },
  ];
  const result = {
    schema: "numeric-font-settings-parent-metrics-v1",
    userAgent: navigator.userAgent,
    samples: [],
    errors: [],
    cleanup: false,
  };
  const number = (raw, tag) => {
    const match = /^"([A-Za-z]{4})"\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)$/i.exec(raw);
    return match && match[1] === tag ? Number(match[2]) : null;
  };
  const rounded = (property, value) => property === "font-feature-settings"
    ? Math.floor(value + 0.5) : value;
  const near = (a, b) => a !== null && Math.abs(a - b) <= 0.03;
  let frame;
  try {
    for (const { property, tag, includeCh } of settings) {
      for (const template of forms) {
        if (!includeCh && template.name === "ch-ratio") {
          continue;
        }
        const form = { ...template, value: template.value.replace("XPRB", tag) };
        frame = document.createElement("iframe");
        frame.setAttribute("title", `${property} ${form.name} probe`);
        const loaded = new Promise(resolve => { frame.onload = resolve; });
        frame.srcdoc = `<!doctype html><meta charset="utf-8"><title>Numeric font settings</title>
          <style>
            #parent { font-family: monospace; font-size: 20px; }
            .child { font-size: 40px; }
            .p30-c40 #parent, .p30-c60 #parent { font-size: 30px; }
            .p30-c60 .child { font-size: 60px; }
            .metric { display: block; block-size: 0; padding: 0; border: 0; }
            .em { inline-size: 1em; }
            .ch { inline-size: 100ch; }
            #target { ${property}: ${form.value}; }
          </style>
          <div id="parent"><div id="parent-em" class="metric em"></div>
            <div id="parent-ch" class="metric ch"></div>
            <div id="target" class="child">0</div>
            <div class="child"><div id="child-em" class="metric em"></div>
              <div id="child-ch" class="metric ch"></div></div></div>`;
        document.body.append(frame);
        await loaded;
        const win = frame.contentWindow;
        const doc = frame.contentDocument;
        const target = doc.getElementById("target");
        const declaration = doc.styleSheets[0].cssRules[
          doc.styleSheets[0].cssRules.length - 1
        ].style.getPropertyValue(property);
        const supports = win.CSS.supports(property, form.value);
        const take = (phase, timing) => {
          const computed = win.getComputedStyle(target).getPropertyValue(property);
          const value = number(computed, tag);
          const width = id => doc.getElementById(id).getBoundingClientRect().width;
          const metrics = {
            parentEm: width("parent-em"), childEm: width("child-em"),
            parentCh: width("parent-ch") / 100, childCh: width("child-ch") / 100,
          };
          const unit = form.name === "ch-ratio" ? "Ch" : "Em";
          const relative = form.name === "em-ratio" || form.name === "ch-ratio";
          const parent = rounded(property, relative ? metrics[`parent${unit}`] : 20);
          const child = rounded(property, relative ? metrics[`child${unit}`] : 20);
          const roundingBoundary = property === "font-feature-settings" &&
            form.name === "ch-ratio" && [metrics.parentCh, metrics.childCh].some(
              metric => Math.abs((metric % 1) - 0.5) < 0.001
            );
          const admitted = supports && declaration !== "";
          result.samples.push({
            property, tag, form: form.name, specified: form.value, phase, timing,
            compatMode: doc.compatMode, supports, declaration, admitted,
            computed, value, metrics,
            parentFontSize: win.getComputedStyle(doc.getElementById("parent")).fontSize,
            childFontSize: win.getComputedStyle(target).fontSize,
            parentFamily: win.getComputedStyle(doc.getElementById("parent")).fontFamily,
            childFamily: win.getComputedStyle(target).fontFamily,
            expectedUnderCurrentDraft: parent, alternativeChildMetrics: child,
            discriminating: relative && !near(parent, child) && !roundingBoundary,
            classification: !admitted ? "not-admitted" : value === null ? "unparsed-computed-value" :
              roundingBoundary ? "rounding-boundary" : near(value, parent) && near(value, child) ?
                "matches-both" : near(value, parent) ? "matches-parent" :
                  near(value, child) ? "matches-child" : "matches-neither",
          });
        };
        for (const phase of phases) {
          doc.documentElement.className = phase.name;
          take(phase, "first");
          await doc.fonts.ready;
          await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
          take(phase, "settled");
        }
        frame.remove();
        frame = null;
      }
    }
  } catch (error) {
    result.errors.push({ name: error.name, message: error.message, stack: error.stack });
  } finally {
    if (frame) {
      frame.remove();
    }
    result.cleanup = !frame || !frame.isConnected;
  }
  return result;
})()

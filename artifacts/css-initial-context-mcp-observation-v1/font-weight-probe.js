async () => {
  const results = [];
  const frames = new Set();
  try {
    for (const failure of ["grammar", "missing"]) {
      for (const declarationOrder of ["provider-first", "length-first"]) {
        for (const queryOrder of ["provider-first", "consumer-first"]) {
          const frame = document.createElement("iframe");
          frame.style.cssText = "position:absolute;left:0;top:0;width:800px;height:300px;border:0";
          const loaded = new Promise(resolve => frame.addEventListener("load", resolve, {once:true}));
          frame.srcdoc = "<!doctype html><meta charset=utf-8><body></body>";
          frames.add(frame);
          document.body.append(frame);
          await loaded;
          const doc = frame.contentDocument;
          const win = frame.contentWindow;
          const css = win.CSS;
          const support = {
            fontWeightDivision: css.supports("font-weight", "calc(100cqw / 1px)"),
            numericDivision: css.supports("opacity", "calc(100cqw / 1px)"),
            cqwLength: css.supports("width", "100cqw"),
            lhLength: css.supports("width", "1lh"),
            fontWeightLiteral: css.supports("font-weight", "200"),
            containerSize: css.supports("container-type", "size"),
            registrationAPI: typeof css.registerProperty === "function",
          };
          const provider = failure === "grammar" ? "--weight:var(--ready,1vi)" : "--weight:var(--absent)";
          const declarations = ["--ready:bogus", provider, "--length:1lh", "font-weight:var(--weight,555)", "width:var(--length)"];
          if (declarationOrder === "length-first") declarations.reverse();
          const sheet = doc.createElement("style");
          sheet.textContent = `
            @property --weight { syntax:"<number>"; inherits:false; initial-value:calc(100cqw / 1px); }
            @property --length { syntax:"<length>"; inherits:false; initial-value:0px; }
            @property --fixed-weight { syntax:"<number>"; inherits:false; initial-value:200; }
            html, body { margin:0; zoom:1; writing-mode:horizontal-tb; }
            #container { position:relative; container-type:size; width:200px; height:150px; zoom:1; }
            #container > div { position:absolute; font-size:20px; line-height:40px; height:1px; }
            #target { ${declarations.join(";")}; }
            #direct { font-weight:calc(100cqw / 1px); }
            #literal { font-weight:200; }
            #fixed { --fixed-weight:var(--absent); --length:1lh; font-weight:var(--fixed-weight); width:var(--length); }
          `;
          doc.head.append(sheet);
          const container = doc.createElement("div");
          container.id = "container";
          const elements = {};
          for (const id of ["target", "direct", "literal", "fixed", "initial"]) {
            const element = doc.createElement("div");
            element.id = id;
            elements[id] = element;
            container.append(element);
          }
          doc.body.append(container);
          const snapshots = [];
          for (const width of [200, 300, 200]) {
            container.style.width = `${width}px`;
            elements.literal.style.fontWeight = String(width);
            const target = win.getComputedStyle(elements.target);
            const first = queryOrder === "provider-first" ? target.getPropertyValue("--weight") : target.fontWeight;
            const value = target.getPropertyValue("--weight").trim();
            const weight = target.fontWeight;
            const direct = win.getComputedStyle(elements.direct).fontWeight;
            const literal = win.getComputedStyle(elements.literal).fontWeight;
            const fixed = win.getComputedStyle(elements.fixed);
            const initial = win.getComputedStyle(elements.initial).getPropertyValue("--weight").trim();
            snapshots.push({
              requestedWidth:width, first, value, weight, direct, literal,
              fixedWeight:fixed.fontWeight, fixedValue:fixed.getPropertyValue("--fixed-weight").trim(),
              initialOnlyValue:initial, length:target.getPropertyValue("--length").trim(),
              lineHeight:target.lineHeight, targetWidth:target.width,
              containerWidth:win.getComputedStyle(container).width,
              containerRectWidth:container.getBoundingClientRect().width,
              viewportWidth:win.innerWidth,
              directCalibration:Number(direct) === width && Number(literal) === width,
              registrationObserved:initial !== "" && Number.isFinite(Number(initial)),
              providerMatchesConsumer:Number.isFinite(Number(value)) && Number(value) === Number(weight),
            });
            await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
          }
          results.push({failure, declarationOrder, queryOrder, support, snapshots});
          frame.remove();
          frames.delete(frame);
        }
      }
    }
    return {
      userAgent:navigator.userAgent,
      observationOnly:true,
      oracle:"Contextual @property admission is unresolved. Compare raw selected-provider/consumer values only after direct-math and registration calibration; no automatic conformance verdict.",
      expectedScenarios:8,
      expectedSnapshots:24,
      results,
    };
  } finally {
    for (const frame of frames) frame.remove();
  }
}

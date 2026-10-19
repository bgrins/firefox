window.probePromise = (async () => {
  await document.fonts.ready;
  const fixtures = document.querySelector("#fixtures");
  const measure = (text, partition, whitespace, policy, transform, width) => {
    const element = document.createElement("div");
    element.className = `sample ${whitespace} ${policy} ${transform}`;
    element.lang = "th";
    element.style.width = width;
    const lf = text.indexOf("\n");
    if (partition === "whole" || lf < 0) {
      element.append(document.createTextNode(text));
    } else {
      const cut = lf + (partition === "after-lf" ? 1 : 0);
      element.append(document.createTextNode(text.slice(0, cut)));
      const last = document.createTextNode(text.slice(cut));
      if (partition === "nested-before-lf") {
        const outer = document.createElement("span");
        const inner = document.createElement("span");
        inner.append(last);
        outer.append(inner);
        element.append(outer);
      } else {
        element.append(last);
      }
    }
    fixtures.append(element);
    const box = element.getBoundingClientRect();
    const glyphs = [];
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let globalOffset = 0;
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      let localOffset = 0;
      for (const scalar of node.data) {
        const range = document.createRange();
        range.setStart(node, localOffset);
        range.setEnd(node, localOffset + scalar.length);
        const rect = range.getBoundingClientRect();
        glyphs.push({scalar: scalar.codePointAt(0), offset: globalOffset + localOffset,
          x: rect.x - box.x, y: rect.y - box.y, width: rect.width, height: rect.height});
        localOffset += scalar.length;
      }
      globalOffset += node.length;
    }
    const result = {width: box.width, height: box.height, glyphs};
    element.remove();
    return result;
  };
  const calibration = Object.fromEntries(["一", "二", "一二"].map(text =>
    [text, measure(text, "whole", "calibration", "normal", "none", "max-content")]));
  const single = Math.max(calibration["一"].width, calibration["二"].width);
  const pair = calibration["一二"].width;
  if (!(single > 0 && pair > single + 2)) throw new Error("CJK calibration failed");
  const widths = {narrow: (single + pair) / 2, wide: pair + 10};
  const prefixes = {ahom: "\u0e01\u{11700}\u0e01", bmp: "\u0e01\u1950\u0e01", ascii: "A"};
  const controls = [];
  const rows = [];
  for (const whitespace of ["pre-wrap", "pre-line"]) {
    for (const policy of ["normal", "break-all", "keep-all"]) {
      for (const transform of ["none", "capitalize"]) {
        for (const [widthName, width] of Object.entries(widths)) {
          const reference = measure("一二", "whole", whitespace, policy, transform, `${width}px`);
          const expectedWrap = widthName === "narrow" && policy !== "keep-all";
          const referenceWrap = reference.glyphs[1].y > reference.glyphs[0].y + 1;
          controls.push({whitespace, policy, transform, widthName, reference, expectedWrap,
            passed: referenceWrap === expectedWrap});
          for (const [prefix, value] of Object.entries(prefixes)) {
            const text = `${value}\n一二`;
            const partitions = {};
            for (const partition of ["whole", "before-lf", "after-lf", "nested-before-lf"]) {
              const observation = measure(text, partition, whitespace, policy, transform, `${width}px`);
              const suffix = observation.glyphs.slice(-2);
              const wrap = suffix[1].y > suffix[0].y + 1;
              partitions[partition] = {...observation, suffixWrap: wrap,
                expectedSuffixWrap: expectedWrap, passed: wrap === expectedWrap};
            }
            rows.push({prefix, text, whitespace, policy, transform, widthName, width, partitions,
              partitionEqual: Object.values(partitions).every(value =>
                value.suffixWrap === partitions.whole.suffixWrap)});
          }
        }
      }
    }
  }
  const result = {calibration, widths, controls, rows};
  document.querySelector("#output").textContent = JSON.stringify(result, null, 2);
  return result;
})();

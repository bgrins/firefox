async function observeOrdinaryRandomIndexes() {
  const frame = document.createElement("iframe");
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    doc.open();
    doc.write("<!doctype html><body>");
    doc.close();
    const win = frame.contentWindow;
    const random = (key, min, max) => `random(${key}, ${min}, ${max})`;
    const cases = [
      ["opacity-number", "opacity", "0", "1", "property-index-scoped", 2],
      ["opacity-percentage-control", "opacity", "0%", "100%", "property-index-scoped", 1],
      ["line-height-length", "line-height", "10px", "90px", "property-index-scoped", 2],
      ["line-height-number-control", "line-height", "1", "3", "property-index-scoped", 1],
      ["opacity-named-control", "opacity", "0", "1", "--ordinary-random-probe", null],
      ["line-height-named-control", "line-height", "10px", "90px", "--ordinary-random-probe", null],
      ["opacity-fixed-control", "opacity", "0", "1", "fixed .25", null],
      ["line-height-fixed-control", "line-height", "10px", "90px", "fixed .25", null],
    ];
    const pending = cases.map(([id, property, min, max, key, predictedIndex]) => {
      const make = value => {
        const element = doc.createElement("div");
        element.style.fontSize = "10px";
        element.style.setProperty(property, value);
        doc.body.append(element);
        return {element, input: value, supported: win.CSS.supports(property, value)};
      };
      const indexed = [1, 2].map(index => make(random(`ua-${property}-${index}`, min, max)));
      const target = make(random(key, min, max));
      const expected = key === "fixed .25" ? make(property === "opacity" ? "0.25" : "30px")
        : predictedIndex === null ? make(random(key, min, max)) : indexed[0];
      return {id, property, predictedIndex, target, expected, indexed};
    });
    await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
    const rows = pending.map(item => {
      const read = ({element, input, supported}) => ({
        input,
        supported,
        specified: element.style.getPropertyValue(item.property),
        computed: win.getComputedStyle(element).getPropertyValue(item.property),
      });
      const target = read(item.target);
      const expected = read(item.expected);
      const indexed = item.indexed.map(read);
      const supported = [target, expected, ...indexed].every(value => value.supported && value.specified !== "");
      return {id: item.id, property: item.property, predictedIndex: item.predictedIndex,
        supported, target, expected, indexed,
        matchesExpected: supported ? target.computed === expected.computed : null,
        matchesIndex1: supported ? target.computed === indexed[0].computed : null,
        matchesIndex2: supported ? target.computed === indexed[1].computed : null};
    });
    return {cases: cases.length, rows};
  } finally {
    frame.remove();
  }
}

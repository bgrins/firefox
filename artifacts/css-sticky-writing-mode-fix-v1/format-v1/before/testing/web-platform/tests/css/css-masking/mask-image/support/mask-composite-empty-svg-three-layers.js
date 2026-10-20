function buildThreeLayerSVGMaskCases(empty) {
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("width", "0");
  svg.setAttribute("height", "0");
  svg.style.position = "absolute";
  document.body.append(svg);

  function makeMask(id, contentWidth, opacity) {
    const mask = document.createElementNS(svgNS, "mask");
    mask.id = id;
    mask.setAttribute("maskUnits", "userSpaceOnUse");
    mask.setAttribute("maskContentUnits", "userSpaceOnUse");
    for (const [name, value] of Object.entries({x: 0, y: 0, width: 40, height: 40})) {
      mask.setAttribute(name, value);
    }
    const rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("width", contentWidth);
    rect.setAttribute("height", "40");
    rect.setAttribute("fill", "white");
    rect.setAttribute("fill-opacity", opacity);
    mask.append(rect);
    svg.append(mask);
    return mask;
  }

  let index = 0;
  for (const mode of ["alpha", "luminance"]) {
    for (const axis of ["width", "height"]) {
      for (const operator of ["add", "subtract", "intersect", "exclude"]) {
        const top = makeMask(`top-${index}`, 20, 0.5);
        const middle = makeMask(`middle-${index}`, 40, empty ? 1 : 0);
        const bottom = makeMask(`bottom-${index++}`, 40, 0.5);
        if (empty) {
          middle.setAttribute(axis, "0");
        }
        const tile = document.createElement("div");
        tile.className = "tile";
        const target = document.createElement("div");
        target.className = "target";
        target.style.maskImage = [top, middle, bottom].map(mask => `url("#${mask.id}")`).join(", ");
        target.style.maskMode = mode;
        target.style.maskComposite = `add, ${operator}, add`;
        tile.append(target);
        document.getElementById("grid").append(tile);
      }
    }
  }
}

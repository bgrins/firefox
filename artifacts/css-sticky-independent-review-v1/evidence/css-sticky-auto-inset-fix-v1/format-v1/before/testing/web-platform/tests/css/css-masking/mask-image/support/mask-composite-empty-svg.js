function buildEmptySVGMaskCases(mutate) {
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("width", "0");
  svg.setAttribute("height", "0");
  svg.style.position = "absolute";
  document.body.append(svg);
  const updates = [];
  const operators = ["add", "subtract", "intersect", "exclude"];
  const expected = {
    forward: [1, 0, 0, 1],
    reverse: [1, 1, 0, 1],
    single: [0, 0, 0, 0],
    transparent: [1, 0, 0, 1],
    opaque: [1, 0, 1, 0],
  };

  function makeMask(id) {
    const mask = document.createElementNS(svgNS, "mask");
    mask.id = id;
    mask.setAttribute("maskUnits", "userSpaceOnUse");
    mask.setAttribute("maskContentUnits", "userSpaceOnUse");
    for (const [name, value] of Object.entries({x: 0, y: 0, width: 40, height: 40})) {
      mask.setAttribute(name, value);
    }
    const rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("width", "40");
    rect.setAttribute("height", "40");
    rect.setAttribute("fill", "white");
    mask.append(rect);
    svg.append(mask);
    return mask;
  }

  let index = 0;
  for (const mode of ["alpha", "luminance"]) {
    for (const axis of ["width", "height"]) {
      for (const variant of Object.keys(expected)) {
        for (const [opIndex, operator] of operators.entries()) {
          const variable = makeMask(`variable-${index}`);
          const opaque = makeMask(`opaque-${index++}`);
          const update = () => {
            if (variant === "transparent") {
              variable.firstElementChild.setAttribute("fill-opacity", "0");
            } else if (variant !== "opaque") {
              variable.setAttribute(axis, "0");
            }
          };
          if (mutate) {
            updates.push(update);
          } else {
            update();
          }
          const tile = document.createElement("div");
          tile.className = "tile";
          const target = document.createElement("div");
          target.className = "target";
          const visible = expected[variant][opIndex];
          tile.style.background = visible ? "red" : "lime";
          target.style.background = visible ? "lime" : "red";
          let masks = [variable, opaque];
          if (variant === "reverse") {
            masks.reverse();
          } else if (variant === "single") {
            masks = [variable];
          }
          target.style.maskImage = masks.map(mask => `url("#${mask.id}")`).join(", ");
          target.style.maskMode = mode;
          target.style.maskComposite = operator;
          tile.append(target);
          document.getElementById("grid").append(tile);
        }
      }
    }
  }
  if (mutate) {
    document.documentElement.addEventListener("TestRendered", () => {
      for (const update of updates) {
        update();
      }
      document.documentElement.classList.remove("reftest-wait");
    }, {once: true});
  }
}

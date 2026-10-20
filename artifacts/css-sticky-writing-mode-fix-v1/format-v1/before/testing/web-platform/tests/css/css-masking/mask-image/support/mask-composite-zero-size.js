function buildZeroSizeMaskCases(mutate) {
  const opaque = "linear-gradient(white, white)";
  const transparent = "linear-gradient(transparent, transparent)";
  const operators = ["add", "subtract", "intersect", "exclude"];
  const expected = {
    forward: [1, 0, 0, 1],
    reverse: [1, 1, 0, 1],
    single: [0, 0, 0, 0],
    transparent: [1, 0, 0, 1],
    opaque: [1, 0, 1, 0],
  };
  const updates = [];
  for (const mode of ["alpha", "luminance"]) {
    for (const size of ["0px 40px", "40px 0px"]) {
      for (const variant of Object.keys(expected)) {
        for (const [opIndex, operator] of operators.entries()) {
          const tile = document.createElement("div");
          tile.className = "tile";
          const target = document.createElement("div");
          target.className = "target";
          const visible = expected[variant][opIndex];
          tile.style.background = visible ? "red" : "lime";
          target.style.background = visible ? "lime" : "red";
          target.style.maskMode = mode;
          target.style.maskComposite = operator;
          target.style.maskImage = variant === "single" ? opaque : `${opaque}, ${opaque}`;
          target.style.maskSize = "40px 40px";
          const update = () => {
            if (variant === "transparent") {
              target.style.maskImage = `${transparent}, ${opaque}`;
            } else if (variant === "forward") {
              target.style.maskSize = `${size}, 40px 40px`;
            } else if (variant === "reverse") {
              target.style.maskSize = `40px 40px, ${size}`;
            } else if (variant === "single") {
              target.style.maskSize = size;
            }
          };
          if (mutate) {
            updates.push(update);
          } else {
            update();
          }
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

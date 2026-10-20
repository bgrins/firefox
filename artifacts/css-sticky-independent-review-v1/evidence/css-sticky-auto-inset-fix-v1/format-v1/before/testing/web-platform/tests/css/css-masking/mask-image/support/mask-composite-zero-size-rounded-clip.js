function buildRoundedClipMaskCases(empty) {
  for (const mode of ["alpha", "luminance"]) {
    for (const size of ["0px 64px", "64px 0px"]) {
      for (const operator of ["subtract", "intersect"]) {
        const tile = document.createElement("div");
        tile.className = "tile";
        const target = document.createElement("div");
        target.className = "target";
        const middle = empty ? "white" : "transparent";
        target.style.maskImage = `linear-gradient(to right, rgb(255 255 255 / .5) 50%, transparent 50%), linear-gradient(${middle}, ${middle}), linear-gradient(rgb(255 255 255 / .5), rgb(255 255 255 / .5))`;
        target.style.maskSize = `64px 64px, ${empty ? size : "64px 64px"}, 64px 64px`;
        target.style.maskMode = mode;
        target.style.maskComposite = `add, ${operator}, add`;
        tile.append(target);
        document.getElementById("grid").append(tile);
      }
    }
  }
}

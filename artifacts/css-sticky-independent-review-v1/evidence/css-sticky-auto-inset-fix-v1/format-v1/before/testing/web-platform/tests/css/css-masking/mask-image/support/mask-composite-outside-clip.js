function buildOutsideClipMaskCases(outside) {
  for (const mode of ["alpha", "luminance"]) {
    for (const position of ["100px 0px", "-100px 0px", "0px 100px", "0px -100px"]) {
      for (const operator of ["add", "subtract", "intersect", "exclude"]) {
        const target = document.createElement("div");
        const color = outside ? "white" : "transparent";
        target.style.maskImage = `linear-gradient(${color}, ${color}), linear-gradient(rgb(255 255 255 / .5), rgb(255 255 255 / .5))`;
        target.style.maskPosition = `${outside ? position : "0px 0px"}, 0px 0px`;
        target.style.maskMode = mode;
        target.style.maskComposite = operator;
        document.getElementById("grid").append(target);
      }
    }
  }
}

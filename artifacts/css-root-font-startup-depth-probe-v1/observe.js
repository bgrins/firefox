() => {
  const observations = window.rootFontStartupDepthObservations;
  const expected = ["animated:2", "literal:2", "animated:4", "literal:4"];
  if (!Array.isArray(observations) || observations.length !== expected.length ||
      observations.some((row, index) => `${row.mode}:${row.depth}` !== expected[index] ||
        !row.targetRestyle || !Array.isArray(row.styleReadOrder))) {
    throw new Error("Expected four completed depth observations");
  }
  return JSON.parse(JSON.stringify(observations));
}

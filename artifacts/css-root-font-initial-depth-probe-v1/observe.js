() => {
  const observations = window.rootFontInitialDepthObservations;
  const expected = ["animated:2", "literal:2", "animated:4", "literal:4"];
  if (!Array.isArray(observations) || observations.length !== expected.length ||
      observations.some((row, index) => `${row.mode}:${row.depth}` !== expected[index] ||
        row.startup !== "initial-stylesheet" || row.precondition !== null ||
        !row.targetRestyle || !Array.isArray(row.styleReadOrder) ||
        row.styleReadOrder[0]?.phase !== "first-leaf")) {
    throw new Error("Expected four completed initial depth observations");
  }
  return JSON.parse(JSON.stringify(observations));
}

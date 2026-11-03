() => {
  const observations = window.rootFontInitialAnimationObservations;
  if (!Array.isArray(observations) || observations.length !== 1 ||
      observations[0].mode !== "late" || !observations[0].targetRestyle) {
    throw new Error("Expected one completed late target-restyle observation");
  }
  return JSON.parse(JSON.stringify(observations));
}

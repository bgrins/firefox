function publicationFixture(t, inherits) {
  const name = `--publication-extra-${++serial}`;
  CSS.registerProperty({name, syntax: "*", inherits, initialValue: "20px"});
  const parent = document.createElement("div");
  const target = document.createElement("div");
  const reference = document.createElement("div");
  const calibration = document.createElement("div");
  parent.style.width = "200px";
  parent.style.setProperty(name, "var(--publication-missing)");
  target.style.setProperty(name, "44px");
  reference.style.setProperty(name, "var(--publication-missing)");
  for (const element of [target, reference]) {
    element.style.setProperty("--publication-alias", `var(${name}, 61px)`);
    element.style.width = `var(${name}, 61px)`;
  }
  parent.append(target, reference);
  document.body.append(parent, calibration);
  t.add_cleanup(() => { parent.remove(); calibration.remove(); });
  const observe = element => {
    const style = getComputedStyle(element);
    return [style.getPropertyValue(name).trim(),
            style.getPropertyValue("--publication-alias").trim(), style.width];
  };
  assert_equals(getComputedStyle(calibration).getPropertyValue(name), "20px", "registered initial calibration");
  assert_equals(getComputedStyle(parent).getPropertyValue(name), "", "parent guaranteed-invalid provider");
  assert_array_equals(observe(reference), ["", "61px", "61px"], "direct guaranteed-invalid reference");
  assert_array_equals(observe(target), ["44px", "44px", "44px"], "valid underlying declaration");
  const animate = value => {
    const animation = target.animate([{[name]: value}, {[name]: value}],
      {duration: 1000, fill: "both", easing: "linear"});
    t.add_cleanup(() => animation.cancel());
    animation.pause();
    animation.currentTime = 250;
    assert_equals(animation.effect.target, target, "effect target");
    assert_true(target.getAnimations().includes(animation), "active effect exists");
    assert_equals(animation.effect.getComputedTiming().progress, 0.25, "sampled progress");
    return animation;
  };
  return {name, parent, target, reference, observe, animate};
}

for (const inherits of [false, true]) {
  test(t => {
    const {target, observe, animate} = publicationFixture(t, inherits);
    const animation = animate("inherit");
    assert_array_equals(observe(target), ["", "61px", "61px"], "invalid animation suppresses valid underlying declaration");
    animation.cancel();
    assert_array_equals(observe(target), ["44px", "44px", "44px"], "cancellation restores underlying declaration");
  }, `invalid animation suppresses valid underlying declaration; inherits=${inherits}`);

  test(t => {
    const {target, observe, animate} = publicationFixture(t, inherits);
    const lower = animate("55px");
    assert_array_equals(observe(target), ["55px", "55px", "55px"], "lower effect calibration");
    const upper = animate("inherit");
    assert_array_equals(observe(target), ["", "61px", "61px"], "invalid upper effect suppresses valid lower effect");
    upper.cancel();
    assert_array_equals(observe(target), ["55px", "55px", "55px"], "cancellation restores lower effect");
    lower.cancel();
    assert_array_equals(observe(target), ["44px", "44px", "44px"], "cancellation restores underlying declaration");
  }, `invalid animation suppresses valid lower effect; inherits=${inherits}`);

  test(t => {
    const {name, target, reference, observe, animate} = publicationFixture(t, inherits);
    const animation = animate(" ");
    const frames = animation.effect.getKeyframes();
    assert_equals(frames.length, 2, "both keyframes retained");
    for (const frame of frames) {
      assert_own_property(frame, name, "empty custom value is retained");
      assert_equals(frame[name].trim(), "", "empty keyframe value");
    }
    assert_array_equals(observe(target), ["", "", "200px"], "valid empty value does not select a var fallback");
    assert_array_equals(observe(reference), ["", "61px", "61px"], "guaranteed-invalid value selects fallback");
    animation.cancel();
    assert_array_equals(observe(target), ["44px", "44px", "44px"], "cancellation restores underlying declaration");
  }, `valid empty animation value differs from guaranteed-invalid; inherits=${inherits}`);
}


const sourceURL = 'url("data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")';

function makeTarget(t, provider, observer) {
  const target = document.createElement("div");
  target.className = `${provider} ${observer}`;
  target.dataset.number = "8";
  document.body.appendChild(target);
  t.add_cleanup(() => target.remove());
  return target;
}

function assertValue(target, expected, tainted, observer, label) {
  const style = getComputedStyle(target);
  assert_equals(style.getPropertyValue("--mixed").trim(), expected, `${label}: registered value`);
  const blocked = tainted && observer === "bundle";
  assert_equals(style.borderImageSource, blocked ? "none" : sourceURL, `${label}: URL provenance`);
  assert_equals(style.borderImageWidth, blocked ? "1" : expected, `${label}: width grammar`);
}

for (const observer of ["bundle", "direct"]) {
  for (const [provider, value, tainted] of [["clean", "8", false], ["tainted", "8", true], ["length", "20px", false]]) {
    test(t => {
      assertValue(makeTarget(t, provider, observer), value, tainted, observer, "Static calibration");
    }, `Static ${provider} provider, ${observer}`);
  }
}

const cases = [
  {name: "retain composed number after mixed-type iteration", provider: "tainted", startComposite: "add", end: "20px", time: 1250, iteration: 1, progress: .25, expected: "10", tainted: true},
  {name: "same branch with clean underlying", provider: "clean", startComposite: "add", end: "20px", time: 1250, iteration: 1, progress: .25, expected: "10", tainted: false},
  {name: "first iteration has no accumulation", provider: "tainted", startComposite: "add", end: "20px", time: 250, iteration: 0, progress: .25, expected: "10", tainted: true},
  {name: "replacement start ignores underlying", provider: "tainted", startComposite: "replace", end: "20px", time: 1250, iteration: 1, progress: .25, expected: "2", tainted: false},
  {name: "same-type iteration actually accumulates", provider: "tainted", startComposite: "add", end: "20", time: 1250, iteration: 1, progress: .25, expected: "32.5", tainted: true},
  {name: "discrete late sample selects clean accumulated length", provider: "tainted", startComposite: "add", end: "20px", time: 1750, iteration: 1, progress: .75, expected: "40px", tainted: false},
];

for (const observer of ["bundle", "direct"]) {
  for (const c of cases) {
    test(t => {
      const target = makeTarget(t, c.provider, observer);
      assertValue(target, "8", c.provider === "tainted", observer, "Underlying calibration");
      const animation = target.animate([
        {"--mixed": "2", offset: 0, composite: c.startComposite},
        {"--mixed": c.end, offset: 1, composite: "replace"},
      ], {
        duration: 1000,
        iterations: 3,
        fill: "both",
        easing: "linear",
        composite: "replace",
        iterationComposite: "accumulate",
      });
      t.add_cleanup(() => animation.cancel());
      animation.pause();
      animation.currentTime = c.time;
      assert_true(target.getAnimations().includes(animation), "Effect is present");
      assert_equals(animation.effect.composite, "replace", "Effect composite");
      assert_equals(animation.effect.iterationComposite, "accumulate", "Iteration composite");
      const keyframes = animation.effect.getKeyframes();
      assert_equals(keyframes.length, 2, "Both keyframes admitted");
      assert_array_equals(keyframes.map(k => k.composite), [c.startComposite, "replace"], "Per-keyframe composites");
      assert_array_equals(keyframes.map(k => k["--mixed"]), ["2", c.end], "Unmodified keyframe providers");
      const timing = animation.effect.getComputedTiming();
      assert_equals(timing.currentIteration, c.iteration, "Current iteration");
      assert_equals(timing.progress, c.progress, "Iteration progress");
      assertValue(target, c.expected, c.tainted, observer, "Composed sample");
    }, `${c.name}, ${observer}`);
  }
}

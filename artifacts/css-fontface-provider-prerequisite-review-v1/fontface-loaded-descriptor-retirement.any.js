// META: title=Loaded FontFace descriptor changes retire obsolete worker family entries
// META: global=window,dedicatedworker

const fontSet = GLOBAL.isWindow() ? document.fonts : self.fonts;
let fontData;
let serial = 0;
promise_setup(async () => {
  const response = await fetch("/fonts/Ahem.ttf");
  assert_true(response.ok);
  fontData = await response.arrayBuffer();
});

function measure(context, families) {
  context.font = `20px ${families}`;
  return context.measureText("XXXX").width;
}

for (const sourceKind of ["buffer", "url"]) {
  for (const descriptor of ["family", "unicodeRange"]) {
    promise_test(async t => {
      const prefix = `DescriptorRetirement${serial++}`;
      const oldFamily = `${prefix}Old`;
      const newFamily = `${prefix}New`;
      const fallbackFamily = `${prefix}Fallback`;
      const source = () => sourceKind === "buffer" ? fontData.slice(0) : 'url("/fonts/Ahem.ttf")';
      const face = new FontFace(oldFamily, source());
      const fallback = new FontFace(fallbackFamily, source(), {sizeAdjust: "75%"});
      t.add_cleanup(() => { fontSet.delete(face); fontSet.delete(fallback); });
      fontSet.add(face);
      fontSet.add(fallback);
      await Promise.all([face.load(), fallback.load()]);
      const loaded = face.loaded;
      const context = new OffscreenCanvas(100, 100).getContext("2d");
      assert_approx_equals(measure(context, fallbackFamily), 60, 0.01, "Fallback calibration");
      assert_approx_equals(measure(context, `${oldFamily}, ${fallbackFamily}`), 80, 0.01, "Initial matching face");
      face[descriptor] = descriptor === "family" ? newFamily : "U+0059";
      assert_equals(face[descriptor], descriptor === "family" ? newFamily : "U+59");
      assert_true(fontSet.has(face), "The face remains in the set");
      assert_equals(face.status, "loaded");
      assert_equals(face.loaded, loaded);
      await fontSet.ready;
      if (descriptor === "family") {
        assert_approx_equals(measure(context, newFamily), 80, 0.01, "New family matches");
      }
      assert_approx_equals(measure(context, `${oldFamily}, ${fallbackFamily}`), 60, 0.01,
        "Obsolete descriptor no longer supplies X in the existing context");
      const fresh = new OffscreenCanvas(100, 100).getContext("2d");
      assert_approx_equals(measure(fresh, `${oldFamily}, ${fallbackFamily}`), 60, 0.01,
        "Obsolete descriptor no longer supplies X in a fresh context");
    }, `${sourceKind}: loaded ${descriptor} mutation retires the obsolete entry without deletion`);
  }
}

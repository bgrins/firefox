// META: title=Loaded FontFace sizeAdjust updates preserve independent faces
// META: global=window,dedicatedworker

const fontSet = GLOBAL.isWindow() ? document.fonts : self.fonts;
let fontData;
let nextFamily = 0;

promise_setup(async () => {
  const response = await fetch("/fonts/Ahem.ttf");
  assert_true(response.ok, "Ahem resource loads");
  fontData = await response.arrayBuffer();
});

function familyName() {
  return `CanvasSizeAdjust${nextFamily++}`;
}

async function loadedFace(t, sourceKind, family, descriptors = {}, add = true) {
  const source = sourceKind === "buffer" ? fontData.slice(0) : 'url("/fonts/Ahem.ttf")';
  const face = new FontFace(family, source, descriptors);
  t.add_cleanup(() => { fontSet.delete(face); });
  if (add) {
    fontSet.add(face);
  }
  assert_equals(await face.load(), face);
  assert_equals(face.status, "loaded");
  return face;
}

function context() {
  return new OffscreenCanvas(100, 100).getContext("2d");
}

function measure(ctx, family) {
  ctx.font = `20px ${family}`;
  return ctx.measureText("XXXX").width;
}

function update(face) {
  const promise = face.loaded;
  face.sizeAdjust = "50%";
  assert_equals(face.sizeAdjust, "50%");
  assert_equals(face.status, "loaded", "The face stays loaded");
  assert_equals(face.loaded, promise, "The loaded promise stays the same");
}

for (const sourceKind of ["buffer", "url"]) {
  for (const [sizeAdjust, width] of [["100%", 80], ["50%", 40]]) {
    promise_test(async t => {
      const face = await loadedFace(t, sourceKind, familyName(), {sizeAdjust});
      assert_approx_equals(measure(context(), face.family), width, 0.01);
    }, `${sourceKind}: fresh canvas face at ${sizeAdjust}`);
  }

  for (const phase of ["before addition", "existing context", "new context"]) {
    promise_test(async t => {
      const beforeAddition = phase === "before addition";
      const face = await loadedFace(t, sourceKind, familyName(), {}, !beforeAddition);
      let ctx = context();
      if (!beforeAddition) {
        assert_approx_equals(measure(ctx, face.family), 80, 0.01, "Initial width");
      }
      update(face);
      if (beforeAddition) {
        fontSet.add(face);
      } else if (phase === "new context") {
        ctx = context();
      }
      await fontSet.ready;
      assert_approx_equals(measure(ctx, face.family), 40, 0.01, "Updated width");
    }, `${sourceKind}: canvas sizeAdjust mutation, ${phase}`);
  }

  promise_test(async t => {
    const face = await loadedFace(t, sourceKind, familyName());
    const fallback = await loadedFace(t, sourceKind, familyName(), {sizeAdjust: "75%"});
    const ctx = context();
    const families = `${face.family}, ${fallback.family}`;
    assert_approx_equals(measure(ctx, fallback.family), 60, 0.01, "Fallback calibration");
    assert_approx_equals(measure(ctx, families), 80, 0.01, "Initial primary width");
    update(face);
    measure(ctx, families);
    assert_true(fontSet.delete(face));
    assert_approx_equals(measure(ctx, families), 60, 0.01, "Removed face stops matching");
  }, `${sourceKind}: removing a mutated face uses the fallback`);
}

for (const coverage of ["same descriptors", "different unicode ranges"]) {
  for (const remaining of ["changed face", "unchanged face"]) {
    promise_test(async t => {
      const family = familyName();
      const peer = await loadedFace(t, "url", family);
      assert_approx_equals(measure(context(), family), 80, 0.01, "Initial peer width");
      const descriptors = coverage === "different unicode ranges" ? {unicodeRange: "U+0058"} : {};
      const changed = await loadedFace(t, "url", family, descriptors);
      update(changed);
      assert_equals(peer.sizeAdjust, "100%", "Peer descriptor stays unchanged");
      fontSet.delete(remaining === "changed face" ? peer : changed);
      await fontSet.ready;
      const expected = remaining === "changed face" ? 40 : 80;
      assert_approx_equals(measure(context(), family), expected, 0.01,
        "Only the remaining face supplies metrics");
    }, `URL faces with ${coverage}: retain the ${remaining}`);
  }
}

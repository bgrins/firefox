// META: title=Removed FontFace objects stop supplying canvas fonts
// META: global=window,dedicatedworker
// META: spec=https://drafts.csswg.org/css-font-loading-3/#fontfaceset-interface
// META: spec=https://drafts.csswg.org/css-font-loading-3/#worker-fontfacesource

const fontSet = GLOBAL.isWindow() ? document.fonts : self.fonts;
let fontData;
let nextFamily = 0;

promise_setup(async () => {
  const response = await fetch("/fonts/Ahem.ttf");
  assert_true(response.ok, "Ahem resource loads");
  fontData = await response.arrayBuffer();
});

function familyName() {
  return `RemovedCanvasFont${nextFamily++}`;
}

async function addFace(t, sourceKind, family, sizeAdjust) {
  const source = sourceKind === "buffer" ? fontData.slice(0) : 'url("/fonts/Ahem.ttf")';
  const face = new FontFace(family, source, {sizeAdjust});
  t.add_cleanup(() => { fontSet.delete(face); });
  fontSet.add(face);
  await face.load();
  return face;
}

function measure(ctx, family) {
  ctx.font = `20px ${family}`;
  return ctx.measureText("XXXX").width;
}

for (const sourceKind of ["buffer", "url"]) {
  promise_test(async t => {
    const full = await addFace(t, sourceKind, familyName(), "100%");
    const half = await addFace(t, sourceKind, familyName(), "50%");
    const ctx = new OffscreenCanvas(100, 100).getContext("2d");
    assert_approx_equals(measure(ctx, full.family), 80, 0.01);
    assert_approx_equals(measure(ctx, half.family), 40, 0.01);
  }, `${sourceKind}: canvas font width calibration`);

  for (const operation of ["delete", "clear", "delete later face in family"]) {
    promise_test(async t => {
      const family = familyName();
      const fallback = await addFace(t, sourceKind, familyName(), "50%");
      const first = await addFace(t, sourceKind, family, "100%");
      const ctx = new OffscreenCanvas(100, 100).getContext("2d");
      const families = `${family}, ${fallback.family}`;
      assert_approx_equals(measure(ctx, fallback.family), 40, 0.01, "Fallback width");
      assert_approx_equals(measure(ctx, families), 80, 0.01, "Primary width");
      let expected = 40;
      if (operation === "clear") {
        fontSet.clear();
        fontSet.add(fallback);
      } else if (operation === "delete later face in family") {
        const later = await addFace(t, sourceKind, family, "50%");
        assert_approx_equals(measure(ctx, families), 40, 0.01, "Later face wins");
        assert_true(fontSet.delete(later));
        expected = 80;
      } else {
        assert_true(fontSet.delete(first));
      }
      const existingWidth = measure(ctx, families);
      const fresh = new OffscreenCanvas(100, 100).getContext("2d");
      const freshWidth = measure(fresh, families);
      const widths = JSON.stringify({existingWidth, freshWidth});
      assert_approx_equals(existingWidth, expected, 0.01,
        `Existing context uses only remaining faces: ${widths}`);
      assert_approx_equals(freshWidth, expected, 0.01,
        `Fresh context uses only remaining faces: ${widths}`);
    }, `${sourceKind}: ${operation} updates canvas font selection`);
  }
}

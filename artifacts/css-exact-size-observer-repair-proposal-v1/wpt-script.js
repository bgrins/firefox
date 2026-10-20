
function fixture(t, axis, size, hostSize, padded) {
  const host = document.createElement("div");
  host.className = "host";
  host.style.setProperty("--host-size", `${hostSize}px`);
  host.style.setProperty("--width", `${axis === "horizontal" ? size : 40}px`);
  host.style.setProperty("--height", `${axis === "vertical" ? size : 40}px`);
  const box = document.createElement("div");
  box.className = `box${padded ? " padded" : ""}`;
  const marker = document.createElement("span");
  marker.className = "marker";
  box.append(marker);
  host.append(box);
  document.body.append(host);
  t.add_cleanup(() => host.remove());
  return {host, box, marker};
}

for (const axis of ["horizontal", "vertical"]) {
  for (const size of [120.125, 131072.0666667, 139808.125]) {
    for (const hostSize of [100, 100.1]) {
      for (const padded of [false, true]) {
        test(t => {
          const {host, box, marker} = fixture(t, axis, size, hostSize, padded);
          const edge = axis === "horizontal" ? "right" : "bottom";
          const dimension = axis === "horizontal" ? "width" : "height";
          const expected = host.getBoundingClientRect()[edge];
          assert_approx_equals(box.getBoundingClientRect()[dimension], size, 0.05, "supported numeric size");
          assert_approx_equals(marker.getBoundingClientRect()[edge], expected, 0.0001, "small marker reaches the containing border edge");
          assert_approx_equals(box.getBoundingClientRect()[edge], expected, 0.0001, "bounding rectangle preserves the aligned edge");
          assert_equals(box.getClientRects().length, 1, "one nonfragmented box");
          assert_approx_equals(box.getClientRects()[0][edge], expected, 0.0001, "client rectangle preserves the aligned edge");
        }, `${axis}, box ${size}px, host ${hostSize}px, padding ${padded}`);
      }
    }
  }
}

for (const mode of ["scaled", "zoomed", "translated", "scrolled"]) {
  test(t => {
    const {host, box, marker} = fixture(t, "horizontal", 400, 100, true);
    let expectedRight;
    let expectedBottom;
    if (mode === "translated") {
      box.classList.add(mode);
      expectedRight = 107;
      expectedBottom = 111;
    } else if (mode === "scrolled") {
      host.classList.add("scroller");
      host.scrollLeft = 50;
      assert_equals(host.scrollLeft, 50, "scroll position applied");
      expectedRight = 350;
      expectedBottom = 40;
    } else {
      host.classList.add(mode);
      expectedRight = 200;
      expectedBottom = 200;
    }
    for (const element of [box, marker]) {
      const rect = element.getBoundingClientRect();
      assert_approx_equals(rect.right, expectedRight, 0.0001, "right edge retains coordinate effects");
      assert_approx_equals(rect.bottom, expectedBottom, 0.0001, "bottom edge retains coordinate effects");
    }
  }, `coordinate effect: ${mode}`);
}

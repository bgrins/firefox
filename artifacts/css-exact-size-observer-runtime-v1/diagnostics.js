"use strict";

const exactSizeConfigurations = [];
for (const direction of ["row-reverse", "column-reverse"]) {
  for (const boxSizing of ["content-box", "border-box"]) {
    for (const collapse of ["separate", "collapse"]) {
      for (const [captionSide, occupied] of [["top", 20], ["bottom", 0], ["top", -20], ["bottom", -20]]) {
        exactSizeConfigurations.push({kind: "table", direction, boxSizing, collapse, captionSide, occupied});
      }
    }
    for (const writingMode of ["horizontal-tb", "vertical-rl"]) {
      exactSizeConfigurations.push({kind: "percentage", direction, boxSizing, writingMode});
    }
    for (const kind of ["image", "ratio"]) {
      exactSizeConfigurations.push({kind, direction, boxSizing, writingMode: "horizontal-tb"});
    }
  }
}
exactSizeConfigurations.forEach((configuration, index) => {
  configuration.id = `${index}: ${Object.entries(configuration).map(([key, value]) => `${key}=${value}`).join(" ")}`;
});

const exactSmallBasis = 120.125;
const exactLargeBasis = 139808.125;
const exactImageSource = "data:image/svg+xml," + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="40"></svg>');

function exactApply(fixture, basis, boxSizing, warm = false) {
  fixture.host.style.setProperty("--basis", `${basis}px`);
  fixture.host.dataset.box = boxSizing;
  fixture.host.classList.toggle("warm", warm);
}

async function exactFixture(configuration, basis, boxSizing, reference = false) {
  const host = document.createElement("div");
  host.className = `exact-host ${reference ? "reference" : "flex"}`;
  host.dataset.axis = configuration.direction.startsWith("row") ? "horizontal" : "vertical";
  host.dataset.kind = configuration.kind;
  host.style.flexDirection = configuration.direction;
  host.style.setProperty("--item-wm", configuration.writingMode || "horizontal-tb");
  const item = document.createElement(configuration.kind === "table" ? "table" : configuration.kind === "image" ? "img" : "div");
  item.className = "exact-item";
  let caption = null;
  let marker = null;
  let percentage = null;
  let percentageMarker = null;
  if (configuration.kind === "image") {
    item.src = exactImageSource;
    await item.decode();
  } else if (configuration.kind === "table") {
    item.style.borderCollapse = configuration.collapse;
    item.style.captionSide = configuration.captionSide;
    caption = item.createCaption();
    caption.style.marginBlock = `${(configuration.occupied - 20) / 2}px`;
    item.insertRow().insertCell();
  } else {
    marker = document.createElement("span");
    marker.className = "exact-marker";
    item.append(marker);
    if (configuration.kind === "percentage") {
      percentage = document.createElement("div");
      percentage.className = "exact-percentage";
      percentageMarker = document.createElement("span");
      percentageMarker.className = "percentage-marker";
      percentage.append(percentageMarker);
      item.append(percentage);
    }
  }
  host.append(item);
  const calibration = document.createElement("div");
  calibration.className = "exact-calibration";
  host.append(calibration);
  const fixture = {host, item, caption, marker, percentage, percentageMarker, calibration};
  exactApply(fixture, basis, boxSizing);
  document.body.append(host);
  return fixture;
}

function exactSnapshot(fixture, configuration) {
  const host = fixture.host.getBoundingClientRect();
  const item = fixture.item.getBoundingClientRect();
  const style = getComputedStyle(fixture.item);
  const horizontal = configuration.direction.startsWith("row");
  const origin = horizontal ? host.left : host.top;
  const size = rectangle => horizontal ? rectangle.width : rectangle.height;
  const end = rectangle => (horizontal ? rectangle.right : rectangle.bottom) - origin;
  const metrics = {
    mainSize: size(item),
    crossSize: horizontal ? item.height : item.width,
    left: item.left - host.left,
    top: item.top - host.top,
    right: item.right - host.left,
    bottom: item.bottom - host.top,
    itemEnd: end(item),
    markerEnd: fixture.marker ? end(fixture.marker.getBoundingClientRect()) : end(item),
  };
  const calibration = {
    width: fixture.host.clientWidth,
    height: fixture.host.clientHeight,
    scrollLeft: fixture.host.scrollLeft,
    scrollTop: fixture.host.scrollTop,
    basisSize: size(fixture.calibration.getBoundingClientRect()),
    boxSizing: style.boxSizing,
    writingMode: style.writingMode,
  };
  if (fixture.caption) {
    const caption = fixture.caption.getBoundingClientRect();
    const captionStyle = getComputedStyle(fixture.caption);
    const marginStart = parseFloat(captionStyle.marginBlockStart);
    const marginEnd = parseFloat(captionStyle.marginBlockEnd);
    const occupied = caption.height + marginStart + marginEnd;
    Object.assign(calibration, {captionHeight: caption.height, marginStart, marginEnd, occupied,
      collapse: style.borderCollapse, captionSide: style.captionSide});
    Object.assign(metrics, {
      captionTop: caption.top - host.top,
      captionBottom: caption.bottom - host.top,
      wrapperEnd: horizontal ? end(item) : end(item) +
        (configuration.captionSide === "top" ? Math.max(0, -occupied) : Math.max(0, occupied)),
    });
  }
  if (fixture.percentage) {
    const child = fixture.percentage.getBoundingClientRect();
    Object.assign(metrics, {percentageMain: size(child),
      percentageCross: horizontal ? child.height : child.width,
      percentageEnd: end(fixture.percentageMarker.getBoundingClientRect())});
  }
  return {calibration, metrics};
}

async function runExactSizeSupplement() {
  const results = [];
  for (const configuration of exactSizeConfigurations) {
    const record = {configuration, controls: {}, samples: []};
    results.push(record);
    const live = new Set();
    const create = async (...args) => {
      const fixture = await exactFixture(...args);
      live.add(fixture);
      return fixture;
    };
    const remove = fixture => {
      fixture.host.remove();
      live.delete(fixture);
    };
    try {
      const flipped = configuration.boxSizing === "content-box" ? "border-box" : "content-box";
      for (const boxSizing of [configuration.boxSizing, flipped]) {
        const fixture = await create(configuration, exactSmallBasis, boxSizing);
        record.controls[boxSizing] = exactSnapshot(fixture, configuration);
        remove(fixture);
      }
      const fixture = await create(configuration, exactSmallBasis, configuration.boxSizing);
      for (const [phase, basis, boxSizing, warm] of [
        ["small", exactSmallBasis, configuration.boxSizing, false],
        ["large", exactLargeBasis, configuration.boxSizing, false],
        ["warm", exactLargeBasis, configuration.boxSizing, true],
        ["box-update", exactLargeBasis, flipped, true],
        ["restored", exactSmallBasis, configuration.boxSizing, false],
      ]) {
        exactApply(fixture, basis, boxSizing, warm);
        const observed = exactSnapshot(fixture, configuration);
        const fresh = await create(configuration, basis, boxSizing);
        exactApply(fresh, basis, boxSizing, warm);
        const freshObserved = exactSnapshot(fresh, configuration);
        const reference = configuration.kind === "table" ? null : await create(configuration, basis, boxSizing, true);
        record.samples.push({phase, basis, boxSizing, observed, fresh: freshObserved,
          reference: reference ? exactSnapshot(reference, configuration) : null});
        remove(fresh);
        if (reference) {
          remove(reference);
        }
      }
    } catch (error) {
      record.error = String(error.stack || error);
    } finally {
      for (const fixture of live) {
        fixture.host.remove();
      }
    }
  }
  window.exactSizeSupplementResults = results;
  return results;
}

function exactAssertCalibration(record) {
  assert_false(Boolean(record.error), record.error || "fixture completed");
  assert_equals(record.samples.length, 5, "all update phases ran");
  for (const sample of record.samples) {
    const value = sample.observed.calibration;
    assert_equals(value.width, 100, sample.phase + " scrollport width");
    assert_equals(value.height, 100, sample.phase + " scrollport height");
    assert_equals(value.scrollLeft, 0, sample.phase + " horizontal scroll position");
    assert_equals(value.scrollTop, 0, sample.phase + " vertical scroll position");
    assert_approx_equals(value.basisSize, sample.basis, 0.05, sample.phase + " independent numeric-range reference");
    assert_equals(value.boxSizing, sample.boxSizing, sample.phase + " box sizing");
    if (record.configuration.kind === "table") {
      assert_approx_equals(value.captionHeight, 20, 0.005, sample.phase + " caption height");
      assert_approx_equals(value.occupied, record.configuration.occupied, 0.005, sample.phase + " signed occupied caption size");
      assert_equals(value.collapse, record.configuration.collapse, "border collapse");
    } else {
      assert_equals(value.writingMode, record.configuration.writingMode, "item writing mode");
      assert_approx_equals(sample.observed.metrics.mainSize, sample.reference.metrics.mainSize, 0.05,
        sample.phase + " explicit-size reference and flex main size");
    }
  }
}

function exactAssertFresh(record) {
  assert_false(Boolean(record.error), record.error || "fixture completed");
  for (const sample of record.samples) {
    for (const [name, value] of Object.entries(sample.observed.metrics)) {
      assert_approx_equals(value, sample.fresh.metrics[name], 0.005,
        `${sample.phase}: warm/fresh ${name}`);
    }
  }
}

function exactAssertGeometry(record) {
  exactAssertCalibration(record);
  for (const sample of record.samples) {
    const metrics = sample.observed.metrics;
    if (record.configuration.kind === "table") {
      const control = record.controls[sample.boxSizing].metrics;
      assert_approx_equals(metrics.wrapperEnd, control.wrapperEnd, 0.005,
        sample.phase + ": reconstructed wrapper-end residual matches the small fractional control");
    } else {
      assert_approx_equals(metrics.markerEnd, 100, 0.005,
        sample.phase + ": flex-start main-start border edge");
      if (record.configuration.kind === "percentage") {
        assert_approx_equals(metrics.percentageEnd, 92, 0.005,
          sample.phase + ": 100% descendant reaches the content-box end");
      } else {
        assert_approx_equals(metrics.crossSize, sample.reference.metrics.crossSize, 0.05,
          sample.phase + ": ratio-dependent cross size matches explicit-size reference");
      }
    }
  }
}

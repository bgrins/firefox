"use strict";

function rectangleRecord(rect) {
  return Object.fromEntries(["x", "y", "width", "height", "left", "right", "top", "bottom"].map(name => [name, rect[name]]));
}

function geometryRecord(element, relativeTo) {
  const style = getComputedStyle(element);
  const result = {
    bounding: rectangleRecord(element.getBoundingClientRect()),
    clients: Array.from(element.getClientRects(), rectangleRecord),
    computed: Object.fromEntries(["width", "height", "boxSizing", "position", "transform", "zoom", "marginBlockStart", "marginBlockEnd", "borderTopWidth", "borderBottomWidth", "paddingTop", "paddingBottom"].map(name => [name, style[name]])),
  };
  if (typeof element.getBoxQuads === "function") {
    result.quads = {};
    for (const box of ["border", "margin"]) {
      try {
        result.quads[box] = element.getBoxQuads({box, relativeTo}).map(quad =>
          [quad.p1, quad.p2, quad.p3, quad.p4].map(point => ({x: point.x, y: point.y})));
      } catch (error) {
        result.quads[box] = {error: String(error)};
      }
    }
  }
  return result;
}

function observeScalarSizes(elements) {
  return new Promise(resolve => {
    const values = {};
    const pending = new Set(elements.map(([name]) => name));
    const names = new Map(elements.map(([name, element]) => [element, name]));
    let timer;
    const finish = () => {
      observer.disconnect();
      clearTimeout(timer);
      resolve({values, missing: [...pending]});
    };
    const observer = new ResizeObserver(entries => {
      for (const entry of entries) {
        const name = names.get(entry.target);
        const sizes = values[name] = {};
        for (const key of ["borderBoxSize", "contentBoxSize"]) {
          sizes[key] = Array.from(entry[key] || [], size => ({inlineSize: size.inlineSize, blockSize: size.blockSize}));
        }
        sizes.contentRect = rectangleRecord(entry.contentRect);
        pending.delete(name);
      }
      if (!pending.size) {
        finish();
      }
    });
    timer = setTimeout(finish, 1500);
    for (const [, element] of elements) {
      observer.observe(element, {box: "border-box"});
    }
  });
}

async function runObserverProbe() {
  const records = [];
  for (const basis of [120.125, 139808.125]) {
    for (const axis of ["horizontal", "vertical"]) {
      for (const padded of [false, true]) {
        const host = document.createElement("div");
        host.className = "edge-host";
        const box = document.createElement("div");
        box.className = `edge-box${padded ? " padded" : ""}`;
        box.style.width = `${axis === "horizontal" ? basis : 40}px`;
        box.style.height = `${axis === "vertical" ? basis : 40}px`;
        const marker = document.createElement("span");
        marker.className = "edge-marker";
        box.append(marker);
        host.append(box);
        document.body.append(host);
        try {
          const scalar = await observeScalarSizes([["box", box]]);
          records.push({kind: "non-flex", basis, axis, padded, scalar,
            host: geometryRecord(host, host), item: geometryRecord(box, host),
            marker: geometryRecord(marker, host), devicePixelRatio});
        } finally {
          host.remove();
        }
      }
    }
  }
  const selected = exactSizeConfigurations.filter(configuration =>
    configuration.kind === "image" || configuration.kind === "ratio" ||
    (configuration.kind === "table" && configuration.direction === "column-reverse"));
  for (const configuration of selected) {
    for (const basis of [exactSmallBasis, exactLargeBasis]) {
      const fixture = await exactFixture(configuration, basis, configuration.boxSizing);
      try {
        const elements = [["item", fixture.item]];
        if (fixture.caption) {
          elements.push(["caption", fixture.caption], ["cell", fixture.item.rows[0].cells[0]]);
        }
        const scalar = await observeScalarSizes(elements);
        records.push({kind: "supplement", configuration, basis, scalar,
          original: exactSnapshot(fixture, configuration),
          host: geometryRecord(fixture.host, fixture.host),
          elements: Object.fromEntries(elements.map(([name, element]) => [name, geometryRecord(element, fixture.host)])),
          marker: fixture.marker ? geometryRecord(fixture.marker, fixture.host) : null,
          devicePixelRatio});
      } finally {
        fixture.host.remove();
      }
    }
  }
  window.observerBoundaryResults = records;
  return records;
}

window.observerBoundaryPromise = runObserverProbe();

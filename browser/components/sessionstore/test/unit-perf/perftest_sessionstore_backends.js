/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

const SIZES = [50, 500, 5000, 20000];

const METRICS = [
  "json save main thread",
  "json save total",
  "db full save main thread",
  "db full save total",
  "db one-change save main thread",
  "db one-change save total",
  "db one-change save rows",
  "db recollected save main thread",
  "db recollected save total",
  "db export total",
  "db seed main thread",
  "db seeded first save main thread",
  "db seeded first save rows",
  "json deferred save main thread",
  "db deferred one-change save main thread",
  "json read",
  "db read",
  "json file size",
  "db file size",
];

function unitOf(metric) {
  if (metric.endsWith("size")) {
    return "bytes";
  }
  return metric.endsWith("rows") ? "count" : "ms";
}

var perfMetadata = {
  owner: "Session Restore",
  name: "SessionStoreBackends",
  description:
    "Save and startup-read costs of the JSON session file and the session database, for synthetic sessions.",
  options: {
    default: {
      perfherder: true,
      perfherder_metrics: SIZES.flatMap(size =>
        METRICS.map(metric => ({
          name: `${metric} ${size} tabs`,
          unit: unitOf(metric),
        }))
      ),
      verbose: true,
    },
  },
  tags: ["sessionstore"],
};

async function benchmark(tabCount) {
  let metrics = {};
  let record = (name, value) => (metrics[`${name} ${tabCount} tabs`] = value);
  let state = makeState(tabCount);
  let jsonPath = PathUtils.join(
    PathUtils.profileDir,
    `bench-${tabCount}.jsonlz4`
  );
  let dbPath = PathUtils.join(PathUtils.profileDir, `bench-${tabCount}.sqlite`);

  let jsonMain = [];
  record(
    "json save total",
    await measure(async () => {
      let start = ChromeUtils.now();
      let promise = MODULE_GLOBAL.IOUtils.writeJSON(jsonPath, state, {
        compress: true,
        tmpPath: jsonPath + ".tmp",
      });
      jsonMain.push(ChromeUtils.now() - start);
      await promise;
      return ChromeUtils.now() - start;
    })
  );
  record("json save main thread", median(jsonMain));

  let db = await SessionStoreDB.open(dbPath);
  let writer = new SessionDBWriter();
  let fullMain = [];
  record(
    "db full save total",
    await measure(async () => {
      writer.reset();
      let start = ChromeUtils.now();
      let ops = writer.materialize(state);
      fullMain.push(ChromeUtils.now() - start);
      await db.write(ops);
      return ChromeUtils.now() - start;
    })
  );
  record("db full save main thread", median(fullMain));

  let oneMain = [];
  let rows = [];
  record(
    "db one-change save total",
    await measure(async () => {
      let tabs = state.windows[0].tabs;
      tabs[0] = { ...tabs[0], scroll: { scroll: `0,${random()}` } };
      let start = ChromeUtils.now();
      let ops = writer.materialize(state);
      oneMain.push(ChromeUtils.now() - start);
      rows.push(ops.filter(op => op == "node" || op == "section").length);
      await db.write(ops);
      return ChromeUtils.now() - start;
    })
  );
  record("db one-change save main thread", median(oneMain));
  record("db one-change save rows", median(rows));

  // Collection builds a new object for every tab it collects, which shares
  // the tab state cache's objects with the previous one.
  let recollectedMain = [];
  record(
    "db recollected save total",
    await measure(async () => {
      state.windows.forEach(recollect);
      state.windows[0].tabs[0].scroll = { scroll: `0,${random()}` };
      let start = ChromeUtils.now();
      let ops = writer.materialize(state);
      recollectedMain.push(ChromeUtils.now() - start);
      await db.write(ops);
      return ChromeUtils.now() - start;
    })
  );
  record("db recollected save main thread", median(recollectedMain));

  let exportPath = jsonPath + ".exported";
  record(
    "db export total",
    await measure(async () => {
      let start = ChromeUtils.now();
      await db.exportJSON(exportPath, { tmpPath: exportPath + ".tmp" });
      return ChromeUtils.now() - start;
    })
  );
  await IOUtils.remove(exportPath);

  record(
    "db read",
    await measure(async () => {
      let start = ChromeUtils.now();
      await db.read();
      return ChromeUtils.now() - start;
    })
  );

  // Startup after a clean shutdown restores the JSON file, which holds the
  // database's generation.
  let seedMain = [];
  let seededMain = [];
  let seededRows = [];
  await measure(async () => {
    let restored = toModuleGlobal(state);
    let seeded = new SessionDBWriter(await db.readMeta());
    let orders = await db.readOrders();
    let start = ChromeUtils.now();
    seeded.seed(restored, orders);
    seedMain.push(ChromeUtils.now() - start);
    restored.windows.forEach(recollect);
    start = ChromeUtils.now();
    let ops = seeded.materialize(restored);
    seededMain.push(ChromeUtils.now() - start);
    seededRows.push(ops.filter(op => op == "node" || op == "section").length);
    await db.write(ops);
  });
  record("db seed main thread", median(seedMain));
  record("db seeded first save main thread", median(seededMain));
  record("db seeded first save rows", median(seededRows));
  await db.close();

  record(
    "json read",
    await measure(async () => {
      let start = ChromeUtils.now();
      MODULE_GLOBAL.JSON.parse(
        await IOUtils.readUTF8(jsonPath, { decompress: true })
      );
      return ChromeUtils.now() - start;
    })
  );

  record("json file size", await fileSize(jsonPath));
  record("db file size", await fileSize(dbPath));
  await IOUtils.remove(jsonPath);
  for (let suffix of ["", "-wal", "-shm"]) {
    await IOUtils.remove(dbPath + suffix, { ignoreAbsent: true });
  }
  return metrics;
}

/**
 * Measures saves of a small session that keeps a previous one, as it does
 * when the previous session wasn't restored at startup.
 */
async function benchmarkDeferred(tabCount) {
  let metrics = {};
  let record = (name, value) => (metrics[`${name} ${tabCount} tabs`] = value);
  let state = makeState(50);
  state.lastSessionState = makeState(tabCount);
  let jsonPath = PathUtils.join(PathUtils.profileDir, "deferred.jsonlz4");
  let dbPath = PathUtils.join(PathUtils.profileDir, "deferred.sqlite");

  let jsonMain = [];
  await measure(async () => {
    let start = ChromeUtils.now();
    let promise = MODULE_GLOBAL.IOUtils.writeJSON(jsonPath, state, {
      compress: true,
    });
    jsonMain.push(ChromeUtils.now() - start);
    await promise;
  });
  record("json deferred save main thread", median(jsonMain));

  let db = await SessionStoreDB.open(dbPath);
  let writer = new SessionDBWriter();
  await db.write(writer.materialize(state));
  let dbMain = [];
  await measure(async () => {
    let tabs = state.windows[0].tabs;
    tabs[0] = { ...tabs[0], scroll: { scroll: `0,${random()}` } };
    let start = ChromeUtils.now();
    let ops = writer.materialize(state);
    dbMain.push(ChromeUtils.now() - start);
    await db.write(ops);
  });
  record("db deferred one-change save main thread", median(dbMain));
  await db.close();

  await IOUtils.remove(jsonPath);
  for (let suffix of ["", "-wal", "-shm"]) {
    await IOUtils.remove(dbPath + suffix, { ignoreAbsent: true });
  }
  return metrics;
}

add_task(async function test_backends() {
  let metrics = {};
  for (let size of SIZES) {
    Object.assign(metrics, await benchmark(size));
    Object.assign(metrics, await benchmarkDeferred(size));
  }
  info("perfMetrics", metrics);
  Assert.ok(true, "Benchmarks ran");
});

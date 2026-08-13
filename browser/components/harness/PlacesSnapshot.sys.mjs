/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  Sqlite: "resource://gre/modules/Sqlite.sys.mjs",
});

/**
 * Snapshots the profile's places.sqlite into a workspace directory so
 * sandboxed code can query it. Shared by the VM and mxc backends.
 *
 * @returns {Promise<string>} the sandbox-visible leaf path
 */
export async function snapshotPlacesTo(workspacePath, log = () => {}) {
  await IOUtils.makeDirectory(workspacePath, {
    createAncestors: true,
    ignoreExisting: true,
  });
  const dest = PathUtils.join(workspacePath, "places.sqlite");
  const tmp = `${dest}.tmp`;
  await IOUtils.remove(tmp, { ignoreAbsent: true });
  const conn = await lazy.Sqlite.openConnection({
    path: PathUtils.join(PathUtils.profileDir, "places.sqlite"),
    readOnly: true,
  });
  const start = Date.now();
  try {
    // VACUUM INTO runs at full speed (~30ms for a 16MB db) while the
    // throttled backup() API takes ~25s on the same data; tmp + rename
    // so a reader never observes a torn file.
    await conn.execute(`VACUUM INTO '${tmp.replaceAll("'", "''")}'`);
  } finally {
    await conn.close();
  }
  await IOUtils.move(tmp, dest);
  log(`places snapshot written to ${dest} in ${Date.now() - start}ms`);
  return "places.sqlite";
}

// Keeps an existing snapshot in sync while the browser runs: cheap enough
// to call before every agent turn. A snapshot the user never took is never
// created ("absent") — sharing places data stays opt-in.
export async function refreshPlacesSnapshotIfStale(
  workspacePath,
  maxAgeMs = 5 * 60 * 1000
) {
  const dest = PathUtils.join(workspacePath, "places.sqlite");
  let stat;
  try {
    stat = await IOUtils.stat(dest);
  } catch (e) {
    return "absent";
  }
  if (Date.now() - stat.lastModified < maxAgeMs) {
    return "fresh";
  }
  await snapshotPlacesTo(workspacePath);
  return "refreshed";
}

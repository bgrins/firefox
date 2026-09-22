/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

/* exported SessionChangeJournal, SessionDBWriter, SessionStoreDB, makeTab,
            makeState, recollect, MODULE_GLOBAL, toModuleGlobal, median,
            measure, fileSize, random, randomString */

const { SessionChangeJournal } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionChangeJournal.sys.mjs"
);
const { SessionDBWriter } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionDBWriter.sys.mjs"
);
const { SessionStoreDB } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
);

do_get_profile();

// SessionStore collects and writes the state in the shared module global, as
// the writer runs there. Objects of another global, like this file's, are
// slower to copy, inspect and serialize.
const MODULE_GLOBAL = Cu.getGlobalForObject(SessionDBWriter);

function toModuleGlobal(value) {
  return MODULE_GLOBAL.JSON.parse(JSON.stringify(value));
}

let gSeed = 123456;
function random() {
  gSeed = Math.imul(gSeed, 22695477) + 1;
  return (gSeed >> 1) / 0x7fffffff + 0.5;
}

function randomString(length) {
  let chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars[Math.floor(random() * chars.length)];
  }
  return result;
}

const PRINCIPAL = btoa(randomString(120));
const FAVICONS = Array.from(
  { length: 20 },
  () => "data:image/png;base64," + btoa(randomString(3000))
);

/**
 * Builds a tab state whose shape follows what SessionStore collects: a few
 * history entries, sometimes with pushState data, a favicon on some tabs,
 * and form data, scroll positions and sessionStorage on a few.
 */
function makeTab(i) {
  let entries = [];
  let count = 1 + Math.floor(random() * 5);
  for (let e = 0; e < count; e++) {
    let url = `https://site${i % 300}.test/${randomString(30)}`;
    let entry = {
      url,
      title: randomString(40),
      cacheKey: 0,
      ID: i * 10 + e,
      docshellUUID: `{${randomString(36)}}`,
      triggeringPrincipal_base64: PRINCIPAL,
      hasUserInteraction: true,
      docIdentifier: i * 10 + e,
      persist: true,
    };
    if (random() < 0.1) {
      entry.structuredCloneState = btoa(
        randomString(random() < 0.02 ? 50000 : 1000)
      );
      entry.structuredCloneVersion = 8;
    }
    entries.push(entry);
  }
  let tab = {
    entries,
    index: entries.length,
    lastAccessed: 1700000000000 + i,
    hidden: false,
    userContextId: 0,
    attributes: {},
    image: random() < 0.3 ? FAVICONS[i % FAVICONS.length] : null,
    searchMode: null,
  };
  if (random() < 0.3) {
    tab.scroll = { scroll: `0,${Math.floor(random() * 5000)}` };
  }
  if (random() < 0.05) {
    tab.formdata = { id: { q: randomString(20) }, url: entries[0].url };
  }
  if (random() < 0.1) {
    tab.storage = {
      [`https://site${i % 300}.test`]: { key: randomString(500) },
    };
  }
  tab = toModuleGlobal(tab);
  SessionChangeJournal.setIdentity(tab, {});
  return tab;
}

/**
 * Builds a session with windows of up to 2,000 tabs, each with ten closed
 * tabs.
 */
function makeState(tabCount) {
  let windows = [];
  for (let w = 0; w < Math.max(1, Math.ceil(tabCount / 2000)); w++) {
    windows.push({
      tabs: [],
      selected: 1,
      _closedTabs: [],
      closedGroups: [],
      width: 1200,
      height: 800,
    });
  }
  for (let i = 0; i < tabCount; i++) {
    windows[i % windows.length].tabs.push(makeTab(i));
  }
  for (let win of windows) {
    for (let c = 0; c < 10; c++) {
      win._closedTabs.push({
        state: makeTab(tabCount + c),
        title: randomString(20),
        closedAt: 1,
        closedId: c,
        pos: 0,
      });
    }
  }
  return {
    version: ["sessionrestore", 1],
    windows,
    _closedWindows: [],
    savedGroups: [],
    session: { lastUpdate: 1, startTime: 1, recentCrashes: 0 },
    global: {},
    cookies: [],
    selectedWindow: 1,
  };
}

/**
 * Replaces the tabs of `win` with new objects, as collection does: they share
 * the tab state cache's objects and keep the identity of the tab they
 * describe.
 */
function recollect(win) {
  let { Object: ModuleObject } = MODULE_GLOBAL;
  win.tabs = win.tabs.map(tab => {
    let copy = ModuleObject.assign(new ModuleObject(), tab);
    copy.attributes = ModuleObject.assign(new ModuleObject(), tab.attributes);
    SessionChangeJournal.setIdentity(
      copy,
      SessionChangeJournal.identityOf(tab)
    );
    return copy;
  });
}

function median(values) {
  let sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

async function measure(fn, iterations = 3) {
  let values = [];
  for (let i = 0; i < iterations; i++) {
    values.push(await fn());
  }
  return median(values);
}

async function fileSize(path) {
  let total = 0;
  for (let suffix of ["", "-wal"]) {
    if (await IOUtils.exists(path + suffix)) {
      total += (await IOUtils.stat(path + suffix)).size;
    }
  }
  return total;
}

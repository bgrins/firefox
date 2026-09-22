/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Records which objects of the session state are edited in place, so that a
 * backend can tell whether an object it wrote before has changed without
 * serializing it again.
 *
 * Collection builds new tab state objects, and a backend can compare those
 * with the objects it wrote before. Some objects are kept across collections
 * and edited in place instead: the tab state cache's history entries and
 * session storage, custom tab values, and the states of closed tabs. Such a
 * comparison can't see those edits, so every in-place edit of an object that
 * collected state references must mark that object, and every object that
 * contains it and is itself kept across collections.
 */

let gVersion = 0;
const gMarks = new WeakMap();
const gIdentities = new WeakMap();

export const SessionChangeJournal = {
  /**
   * Increases with every mark. A backend records it when it writes, and later
   * asks whether an object was marked since.
   *
   * @type {number}
   */
  get version() {
    return gVersion;
  },

  /**
   * Records that the given objects were edited in place.
   *
   * @param {...any} objects
   */
  markChanged(...objects) {
    gVersion++;
    for (let object of objects) {
      if (object && typeof object == "object") {
        gMarks.set(object, gVersion);
      }
    }
  },

  /**
   * @param {object} object
   * @param {number} version
   * @returns {boolean} Whether `object` was marked after `version`.
   */
  changedSince(object, version) {
    return (gMarks.get(object) ?? 0) > version;
  },

  /**
   * Associates a collected object with what it describes, so that a backend
   * can match it with the object collected for the same thing before.
   *
   * @param {object} object
   * @param {object} identity
   *        An object that stays the same across collections, like the
   *        permanent key of a tab's browser.
   */
  setIdentity(object, identity) {
    gIdentities.set(object, identity);
  },

  /**
   * @param {object} object
   * @returns {object|undefined}
   */
  identityOf(object) {
    return gIdentities.get(object);
  },
};

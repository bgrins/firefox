/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Records which objects of the session state are edited in place, so that a
 * backend can tell whether what it wrote before has changed without
 * serializing it again. It also gives collected tab states the identity of the
 * tab they describe, so that a backend can match them with what it wrote.
 *
 * A backend keeps a shallow copy of each tab state it writes, and compares the
 * next state of the same tab with it, trusting the objects that both
 * reference. Tab state objects can be edited freely, since the copy keeps
 * their previous values. The objects they reference are shared with the tab
 * state cache and kept across collections, like the history entries, session
 * storage and custom tab values. Every in-place edit of such an object,
 * whether a tab state references it now or did when it was last written, must
 * mark the edited object, and every object that contains it up to the tab
 * state.
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

/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Turns session state into batches of row operations for SessionStoreDB,
 * writing only the rows that changed since the previous batch.
 *
 * The state is split into rows along properties that change independently or
 * are large: see SPLITS. Everything else stays in its object's payload, so any
 * value that JSON can round-trip, including properties this module doesn't
 * know about, is stored without loss.
 *
 * Tab states, which make up most of a session, aren't serialized again on
 * every save. Each is compared with a shallow copy of the tab state written
 * for it before, and a group of its properties, its payload or one of its
 * sections, is only serialized when a value in the group differs from the one
 * written, or is an object that was edited in place and marked in
 * SessionChangeJournal. The other kinds are
 * small and edited in place in many ways, so they are serialized on every
 * save and compared as text. With the audit option, the writer also
 * serializes the tab properties it judged unchanged, and reports the ones that
 * did change.
 */

import { XPCOMUtils } from "resource://gre/modules/XPCOMUtils.sys.mjs";

const lazy = XPCOMUtils.declareLazy({
  SessionChangeJournal:
    "moz-src:///browser/components/sessionstore/SessionChangeJournal.sys.mjs",
});

/**
 * @typedef {object} Kind
 * @property {Record<string, string>} [arrays]
 *   Array properties whose elements become child nodes, and the kind of those
 *   children.
 * @property {Record<string, string>} [objects]
 *   Object properties whose value becomes a single child node.
 * @property {Record<string, string[]>} [sections]
 *   Sections, each holding the listed properties of the node.
 * @property {boolean} [tracked]
 *   Whether objects of this kind are compared with snapshots of the objects
 *   written before instead of being serialized on every save. The objects
 *   they reference must follow the contract of SessionChangeJournal.
 */

const STATE_ARRAYS = {
  windows: "window",
  _closedWindows: "window",
  savedGroups: "group",
  cookies: "cookie",
};

/** @type {Record<string, Kind>} */
const SPLITS = {
  root: {
    arrays: STATE_ARRAYS,
    objects: { lastSessionState: "state" },
  },
  // A session kept inside the top-level one, like the previous session.
  state: { arrays: STATE_ARRAYS },
  window: {
    arrays: {
      tabs: "tab",
      _closedTabs: "closedTab",
      closedGroups: "group",
      groups: "group",
    },
  },
  group: { arrays: { tabs: "closedTab" } },
  closedTab: { objects: { state: "tab" } },
  tab: {
    tracked: true,
    sections: {
      history: ["entries", "index", "requestedIndex"],
      formdata: ["formdata"],
      scroll: ["scroll"],
      storage: ["storage"],
      image: ["image"],
    },
  },
  cookie: {},
};

/**
 * The section each property of a kind belongs to.
 *
 * @type {Map<string, Map<string, string>>}
 */
const SECTION_OF = new Map(
  Object.entries(SPLITS).map(([kind, { sections = {} }]) => [
    kind,
    new Map(
      Object.entries(sections).flatMap(([name, keys]) =>
        keys.map(key => [key, name])
      )
    ),
  ])
);

/**
 * Top-level properties stored as their own root rows.
 */
const ROOT_MEMBERS = ["global"];

const ROOT_PARENT = 0;

/**
 * The group of the properties that stay in a node's payload, as opposed to
 * the groups that are sections.
 */
const CORE = "core";

/**
 * @typedef {object} NodeRecord
 * @property {string} kind
 * @property {number} parent
 * @property {string} prop
 * @property {object|undefined} snapshot
 *   For tracked kinds, a shallow copy of the value written.
 * @property {string[]|undefined} snapshotKeys
 * @property {string|null|undefined} payload
 *   The node's JSON without its split properties, or null for JSON null.
 *   Undefined when the text isn't kept, as for tracked kinds outside audits.
 * @property {Map<string, string|undefined>} sections
 *   The node's sections, with their JSON when it's kept.
 * @property {Map<string, string>} orders
 *   The JSON of each split property's child ids.
 */

/**
 * @typedef {object} Split
 * @property {boolean} plain
 *   Whether the value is a plain object. Other values are stored whole.
 * @property {string|null} payload
 *   For other values, their JSON, or null for JSON null.
 * @property {Map<string, string[]>} groups
 *   The keys in CORE and in each section, in the value's key order.
 * @property {Array<[string, string, Array]>} arrays
 * @property {Array<[string, string, object]>} objects
 */

/**
 * @typedef {object} Miss
 *   A group of properties that the comparison judged unchanged, but whose
 *   JSON differs from the JSON written before.
 * @property {string} kind
 * @property {string} group
 *   CORE or the name of a section.
 */

export class SessionDBWriter {
  /** @type {Map<number, NodeRecord>|null} */
  #nodes = null;
  /** @type {Map<string, string>} */
  #roots = new Map();
  /** @type {Map<string, string>} */
  #rootOrders = new Map();
  /**
   * The ids of the nodes the previous batch wrote for each object.
   *
   * @type {WeakMap<object, number|number[]>}
   */
  #byObject = new WeakMap();
  /**
   * The ids of the nodes the previous batch wrote for each identity that
   * SessionChangeJournal gave an object.
   *
   * @type {WeakMap<object, number|number[]>}
   */
  #byIdentity = new WeakMap();
  // The journal's version when the previous batch was built.
  #journalVersion = 0;
  /**
   * Whether the journal marked an object since the previous batch.
   *
   * @type {(object: object) => boolean}
   */
  #isChanged = object =>
    this.#anyMarks &&
    lazy.SessionChangeJournal.changedSince(object, this.#journalVersion);
  // Whether the journal marked anything since the previous batch.
  #anyMarks = true;
  #audit;
  /** @type {Miss[]} */
  #misses = [];
  #nextId;
  #lineage;
  #seq;
  #dbLineage;
  #dbSeq;

  /**
   * @param {Record<string, string>} meta
   *        The database's meta values, as SessionStoreDB.read() returns them.
   * @param {object} [options]
   * @param {boolean} [options.audit]
   *        Whether to also serialize the properties of tracked nodes that the
   *        comparison judges unchanged, and report those that changed.
   */
  constructor(meta = {}, { audit = false } = {}) {
    this.#dbLineage = meta.lineage ?? "";
    this.#dbSeq = meta.seq ?? "";
    this.#lineage =
      this.#dbLineage || Services.uuid.generateUUID().toString().slice(1, -1);
    this.#seq = Number(meta.seq ?? 0);
    let nextId = Number(meta.next_node_id);
    this.#nextId = Number.isSafeInteger(nextId) && nextId >= 1 ? nextId : 1;
    this.#audit = audit;
  }

  /**
   * The lineage that batches write to the database.
   *
   * @type {string}
   */
  get lineage() {
    return this.#lineage;
  }

  /**
   * The seq of the most recent batch.
   *
   * @type {number}
   */
  get seq() {
    return this.#seq;
  }

  /**
   * What the audit of the most recent batch found. The batch writes the
   * missed groups anyway.
   *
   * @type {Miss[]}
   */
  get misses() {
    return this.#misses;
  }

  /**
   * Turns `state` into a batch that brings the database from the previous
   * batch's state to `state`. Batches may be written before earlier ones
   * finish: each guards on the generation that the previous one leaves
   * behind, so one queued after a failed batch fails too. The first batch,
   * and the first after reset(), clears the database and rewrites everything.
   *
   * @param {object} state
   * @returns {Array<string|number>} The operations, for SessionStoreDB.write().
   */
  materialize(state) {
    try {
      return this.#materialize(state);
    } catch (ex) {
      this.reset();
      throw ex;
    }
  }

  #materialize(state) {
    let fullRewrite = !this.#nodes;
    let previous = this.#nodes ?? new Map();
    let journalVersion = lazy.SessionChangeJournal.version;
    this.#anyMarks = journalVersion != this.#journalVersion;
    let context = {
      previous,
      nodes: new Map(),
      used: new Set(),
      byObject: new WeakMap(),
      byIdentity: new WeakMap(),
      /** @type {Miss[]} */
      misses: [],
      ops: [],
    };
    let { ops } = context;

    if (fullRewrite) {
      ops.push("clear");
      this.#roots = new Map();
      this.#rootOrders = new Map();
    } else {
      ops.push(
        "guard",
        "lineage",
        this.#dbLineage,
        "guard",
        "seq",
        this.#dbSeq
      );
    }

    let split = this.#split("root", state);
    this.#syncRoots(serialize(state, split.groups.get(CORE)), state, ops);

    let orders = new Map();
    for (let [prop, kind, values] of split.arrays) {
      let ids = this.#syncArray(context, ROOT_PARENT, prop, kind, values);
      orders.set(prop, JSON.stringify(ids));
    }
    for (let [prop, kind, object] of split.objects) {
      let id = this.#syncSingle(context, ROOT_PARENT, prop, kind, object);
      orders.set(prop, String(id));
    }
    this.#syncOrders(ROOT_PARENT, this.#rootOrders, orders, ops);
    this.#rootOrders = orders;

    for (let id of previous.keys()) {
      if (!context.used.has(id)) {
        ops.push("delnode", id);
      }
    }

    this.#seq++;
    ops.push(
      "meta",
      "lineage",
      this.#lineage,
      "meta",
      "seq",
      String(this.#seq),
      "meta",
      "next_node_id",
      String(this.#nextId)
    );

    this.#nodes = context.nodes;
    this.#byObject = context.byObject;
    this.#byIdentity = context.byIdentity;
    this.#journalVersion = journalVersion;
    this.#misses = context.misses;
    this.#dbLineage = this.#lineage;
    this.#dbSeq = String(this.#seq);
    return ops;
  }

  /**
   * Forgets what the database holds after a batch failed, so that the next
   * batch rewrites everything.
   */
  reset() {
    this.#nodes = null;
    this.#byObject = new WeakMap();
    this.#byIdentity = new WeakMap();
  }

  #syncRoots(payload, state, ops) {
    let roots = new Map([["state", payload]]);
    for (let name of ROOT_MEMBERS) {
      let json = JSON.stringify(state[name]);
      if (json !== undefined) {
        roots.set(name, json);
      }
    }
    for (let [name, json] of roots) {
      if (this.#roots.get(name) !== json) {
        ops.push("root", name, json);
      }
    }
    for (let name of this.#roots.keys()) {
      if (!roots.has(name)) {
        ops.push("delroot", name);
      }
    }
    this.#roots = roots;
  }

  #syncOrders(parent, previous, orders, ops) {
    for (let [prop, ids] of orders) {
      if (previous?.get(prop) !== ids) {
        ops.push("order", parent, prop, ids);
      }
    }
    for (let prop of previous?.keys() ?? []) {
      if (!orders.has(prop)) {
        ops.push("delorder", parent, prop);
      }
    }
  }

  /**
   * Assigns ids in three passes, so that a looser match never takes an id a
   * stricter one needs: a node written for the same object, then one written
   * for an object with the same identity, then the previous child at the same
   * index, which is updated in place.
   */
  #syncArray(context, parent, prop, kind, values) {
    let previousIds = this.#previousChildren(context, parent, prop);
    let ids = [];
    let claim = (i, id) => {
      if (id !== undefined) {
        ids[i] = id;
        context.used.add(id);
      }
    };
    for (let i = 0; i < values.length; i++) {
      claim(i, this.#match(context, this.#byObject, values[i], kind));
    }
    for (let i = 0; i < values.length; i++) {
      if (ids[i] === undefined) {
        let identity = lazy.SessionChangeJournal.identityOf(values[i]);
        claim(i, this.#match(context, this.#byIdentity, identity, kind));
      }
    }
    for (let i = 0; i < values.length; i++) {
      if (ids[i] === undefined) {
        claim(i, this.#unused(context, previousIds[i], kind) ?? this.#nextId++);
      }
    }
    for (let i = 0; i < values.length; i++) {
      this.#syncNode(context, ids[i], parent, prop, kind, values[i]);
    }
    return ids;
  }

  #syncSingle(context, parent, prop, kind, value) {
    let [previousId] = this.#previousChildren(context, parent, prop);
    let id =
      this.#match(context, this.#byObject, value, kind) ??
      this.#match(
        context,
        this.#byIdentity,
        lazy.SessionChangeJournal.identityOf(value),
        kind
      ) ??
      this.#unused(context, previousId, kind) ??
      this.#nextId++;
    this.#syncNode(context, id, parent, prop, kind, value);
    return id;
  }

  /**
   * Returns the ids that `parent`'s `prop` held in the previous batch.
   *
   * @returns {number[]}
   */
  #previousChildren(context, parent, prop) {
    let order =
      parent == ROOT_PARENT
        ? this.#rootOrders.get(prop)
        : context.previous.get(parent)?.orders.get(prop);
    if (order === undefined) {
      return [];
    }
    let ids = JSON.parse(order);
    return Array.isArray(ids) ? ids : [ids];
  }

  /**
   * Returns the first free id that the previous batch wrote for `key`.
   */
  #match(context, map, key, kind) {
    if (!key || typeof key != "object") {
      return undefined;
    }
    let ids = map.get(key);
    if (typeof ids == "number") {
      return this.#unused(context, ids, kind);
    }
    for (let id of ids ?? []) {
      if (this.#unused(context, id, kind) !== undefined) {
        return id;
      }
    }
    return undefined;
  }

  #unused(context, id, kind) {
    return id !== undefined &&
      context.previous.get(id)?.kind == kind &&
      !context.used.has(id)
      ? id
      : undefined;
  }

  #syncNode(context, id, parent, prop, kind, value) {
    let { ops } = context;
    context.used.add(id);
    if (value && typeof value == "object") {
      append(context.byObject, value, id);
      let identity = lazy.SessionChangeJournal.identityOf(value);
      if (identity) {
        append(context.byIdentity, identity, id);
      }
    }

    let previous = context.previous.get(id);
    if (this.#unchangedLeaf(previous, parent, prop, kind, value)) {
      context.nodes.set(id, previous);
      return;
    }
    let split = this.#split(kind, value);
    let tracked = split.plain && !!SPLITS[kind].tracked;
    let unchanged = tracked
      ? this.#unchangedGroups(previous, kind, value, split)
      : new Set();
    let keepText = !tracked || this.#audit;
    /** @type {NodeRecord} */
    let snapshot = tracked ? { ...value } : undefined;
    let record = {
      kind,
      parent,
      prop,
      snapshot,
      snapshotKeys: snapshot && Object.keys(snapshot),
      payload: undefined,
      sections: new Map(),
      orders: new Map(),
    };

    let moved = !previous || previous.parent != parent || previous.prop != prop;
    let core = this.#group(context, {
      kind,
      group: CORE,
      unchanged: unchanged.has(CORE),
      // A moved node's payload is written with its new place.
      keepText: keepText || moved,
      previousText: previous?.payload,
      serialize: () =>
        split.plain ? serialize(value, split.groups.get(CORE)) : split.payload,
    });
    if (core.write || moved) {
      if (core.text === null) {
        ops.push("nullnode", id, parent, prop);
      } else {
        ops.push("node", id, parent, prop, core.text);
      }
    }
    if (keepText) {
      record.payload = core.text;
    }

    for (let [name, keys] of split.groups) {
      if (name == CORE) {
        continue;
      }
      let section = this.#group(context, {
        kind,
        group: name,
        unchanged: unchanged.has(name),
        keepText,
        // Null stands for a section that isn't stored.
        previousText: previous?.sections.has(name)
          ? previous.sections.get(name)
          : null,
        serialize: () => {
          let json = serialize(value, keys);
          return json == "{}" ? null : json;
        },
      });
      if (section.text === undefined) {
        if (previous.sections.has(name)) {
          record.sections.set(name, undefined);
        }
        continue;
      }
      if (section.text === null) {
        if (section.write) {
          ops.push("delsection", id, name);
        }
        continue;
      }
      if (section.write) {
        ops.push("section", id, name, section.text);
      }
      record.sections.set(name, keepText ? section.text : undefined);
    }
    for (let name of previous?.sections.keys() ?? []) {
      if (!split.groups.has(name)) {
        ops.push("delsection", id, name);
      }
    }

    for (let [childProp, childKind, values] of split.arrays) {
      let ids = this.#syncArray(context, id, childProp, childKind, values);
      record.orders.set(childProp, JSON.stringify(ids));
    }
    for (let [childProp, childKind, object] of split.objects) {
      let childId = this.#syncSingle(context, id, childProp, childKind, object);
      record.orders.set(childProp, String(childId));
    }
    this.#syncOrders(id, previous?.orders, record.orders, ops);

    context.nodes.set(id, record);
  }

  /**
   * Decides whether a group of a node's properties must be written.
   *
   * @param {object} context
   * @param {object} options
   * @param {string} options.kind
   * @param {string} options.group
   * @param {boolean} options.unchanged
   *        Whether the comparison with the previous value found no change.
   * @param {boolean} options.keepText
   *        Whether the group's JSON is needed, and so must be serialized.
   * @param {string|null|undefined} options.previousText
   *        The group's JSON in the previous batch, or undefined if unknown.
   * @param {() => string|null} options.serialize
   * @returns {{text: string|null|undefined, write: boolean}}
   *          The group's JSON, or undefined if it wasn't serialized, and
   *          whether it must be written.
   */
  #group(
    context,
    { kind, group, unchanged, keepText, previousText, serialize: toJSON }
  ) {
    if (unchanged && !keepText) {
      return { text: undefined, write: false };
    }
    let text = toJSON();
    if (unchanged && this.#audit && text !== previousText) {
      context.misses.push({ kind, group });
      return { text, write: true };
    }
    return {
      text,
      write:
        !unchanged && (previousText === undefined || text !== previousText),
    };
  }

  /**
   * Whether nothing about a node of a tracked kind without children changed,
   * so that its previous record still holds. This is the common case, and
   * checking it costs less than comparing group by group. Audits don't take
   * this shortcut.
   *
   * @param {NodeRecord|undefined} previous
   * @param {number} parent
   * @param {string} prop
   * @param {string} kind
   * @param {any} value
   * @returns {boolean}
   */
  #unchangedLeaf(previous, parent, prop, kind, value) {
    let { tracked, arrays, objects } = SPLITS[kind];
    if (
      !tracked ||
      arrays ||
      objects ||
      this.#audit ||
      previous?.kind != kind ||
      previous.parent != parent ||
      previous.prop != prop
    ) {
      return false;
    }
    let before = previous.snapshot;
    if (!before || !isPlainObject(value)) {
      return false;
    }
    let keys = Object.keys(value);
    let beforeKeys = previous.snapshotKeys;
    if (beforeKeys.length != keys.length) {
      return false;
    }
    for (let i = 0; i < keys.length; i++) {
      let key = keys[i];
      if (
        beforeKeys[i] !== key ||
        !same(before[key], value[key], this.#isChanged)
      ) {
        return false;
      }
    }
    return true;
  }

  /**
   * Compares a tracked value with the snapshot of the value its node had in
   * the previous batch.
   *
   * @param {NodeRecord|undefined} previous
   * @param {string} kind
   * @param {object} value
   * @param {Split} split
   * @returns {Set<string>} The groups whose properties are unchanged.
   */
  #unchangedGroups(previous, kind, value, split) {
    let unchanged = new Set();
    let before = previous?.snapshot;
    if (!before) {
      return unchanged;
    }
    let beforeGroups = this.#split(kind, before).groups;
    for (let [name, keys] of split.groups) {
      let beforeKeys = beforeGroups.get(name);
      if (
        beforeKeys?.length == keys.length &&
        keys.every(
          (key, i) =>
            beforeKeys[i] === key &&
            same(before[key], value[key], this.#isChanged)
        )
      ) {
        unchanged.add(name);
      }
    }
    return unchanged;
  }

  /**
   * Splits a value into the groups of its properties and its split
   * properties, without serializing anything. Values that aren't plain
   * objects are stored whole.
   *
   * @param {string} kind
   * @param {any} value
   * @returns {Split}
   */
  #split(kind, value) {
    let split = {
      plain: isPlainObject(value),
      payload: null,
      groups: new Map([[CORE, []]]),
      arrays: [],
      objects: [],
    };
    if (!split.plain) {
      // JSON writes undefined, functions and symbols in arrays as null.
      split.payload = JSON.stringify(value) ?? null;
      if (split.payload == "null") {
        split.payload = null;
      }
      return split;
    }

    let { arrays = {}, objects = {} } = SPLITS[kind];
    let sectionOf = SECTION_OF.get(kind);
    for (let key of Object.keys(value)) {
      if (kind == "root" && ROOT_MEMBERS.includes(key)) {
        continue;
      }
      let child = value[key];
      if (Object.hasOwn(arrays, key) && Array.isArray(child)) {
        split.arrays.push([key, arrays[key], child]);
      } else if (Object.hasOwn(objects, key) && isPlainObject(child)) {
        split.objects.push([key, objects[key], child]);
      } else {
        let name = sectionOf.get(key) ?? CORE;
        let keys = split.groups.get(name);
        if (keys) {
          keys.push(key);
        } else {
          split.groups.set(name, [key]);
        }
      }
    }
    return split;
  }
}

function isPlainObject(value) {
  return (
    value !== null &&
    typeof value == "object" &&
    !Array.isArray(value) &&
    typeof value.toJSON != "function" &&
    !(
      value instanceof Number ||
      value instanceof String ||
      value instanceof Boolean
    )
  );
}

/**
 * Serializes the given properties of `value` as one JSON object.
 */
function serialize(value, keys) {
  // Without a prototype, so that a `__proto__` key is kept as a member.
  let members = Object.create(null);
  for (let key of keys) {
    members[key] = value[key];
  }
  return JSON.stringify(members);
}

/**
 * Whether `after` serializes to the same JSON that `before` did when it was
 * written. Objects reached through both are only trusted when the journal
 * has no mark for them, and anything this can't compare cheaply counts as
 * changed.
 *
 * @param {any} before
 * @param {any} after
 * @param {(object: object) => boolean} changed
 * @returns {boolean}
 */
function same(before, after, changed) {
  if (before === after) {
    return typeof before != "object" || before === null || !changed(before);
  }
  if (
    typeof before != "object" ||
    typeof after != "object" ||
    before === null ||
    after === null ||
    changed(before)
  ) {
    return false;
  }
  if (Array.isArray(before)) {
    if (!Array.isArray(after) || before.length != after.length) {
      return false;
    }
    // Not every(), which skips the holes of sparse arrays.
    for (let i = 0; i < before.length; i++) {
      if (!same(before[i], after[i], changed)) {
        return false;
      }
    }
    return true;
  }
  if (Array.isArray(after) || !isPlainObject(before) || !isPlainObject(after)) {
    return false;
  }
  let keys = Object.keys(before);
  let afterKeys = Object.keys(after);
  return (
    keys.length == afterKeys.length &&
    keys.every(
      (key, i) => afterKeys[i] === key && same(before[key], after[key], changed)
    )
  );
}

/**
 * Adds `id` to the ids of `key`. A single id is stored as a number, since most
 * objects appear once.
 */
function append(map, key, id) {
  let ids = map.get(key);
  if (ids === undefined) {
    map.set(key, id);
  } else if (typeof ids == "number") {
    map.set(key, [ids, id]);
  } else {
    ids.push(id);
  }
}

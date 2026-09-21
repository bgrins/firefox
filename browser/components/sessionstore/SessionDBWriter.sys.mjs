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
 * This writer finds changes by serializing every node on every save and
 * comparing the result with what it wrote before, which costs as much main
 * thread time as a JSON write. It is the reference that a change journal is
 * meant to make incremental.
 */

/**
 * @typedef {object} Kind
 * @property {Record<string, string>} [arrays]
 *   Array properties whose elements become child nodes, and the kind of those
 *   children.
 * @property {Record<string, string>} [objects]
 *   Object properties whose value becomes a single child node.
 * @property {Record<string, string[]>} [sections]
 *   Sections, each holding the listed properties of the node.
 */

/** @type {Record<string, Kind>} */
const SPLITS = {
  state: {
    arrays: {
      windows: "window",
      _closedWindows: "window",
      savedGroups: "group",
      cookies: "cookie",
    },
  },
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
 * Top-level properties stored as their own root rows.
 */
const ROOT_MEMBERS = ["global", "lastSessionState"];

const ROOT_PARENT = 0;

/**
 * @typedef {object} NodeRecord
 * @property {number} parent
 * @property {string} prop
 * @property {string|null} payload
 *   The node's JSON without its split properties, or null for JSON null.
 * @property {Map<string, string>} sections
 * @property {Map<string, string>} orders
 *   The JSON of each split property's child ids.
 */

/**
 * @typedef {object} Split
 * @property {string|null} payload
 * @property {Map<string, string>} sections
 * @property {Array<[string, string, Array]>} arrays
 * @property {Array<[string, string, object]>} objects
 */

export class SessionDBWriter {
  /** @type {Map<number, NodeRecord>|null} */
  #nodes = null;
  /** @type {Map<string, string>} */
  #roots = new Map();
  /** @type {Map<string, string>} */
  #rootOrders = new Map();
  #byObject = new WeakMap();
  #nextId;
  #lineage;
  #seq;
  #dbLineage;
  #dbSeq;

  /**
   * @param {Record<string, string>} meta
   *        The database's meta values, as SessionStoreDB.read() returns them.
   */
  constructor(meta = {}) {
    this.#dbLineage = meta.lineage ?? "";
    this.#dbSeq = meta.seq ?? "";
    this.#lineage =
      this.#dbLineage || Services.uuid.generateUUID().toString().slice(1, -1);
    this.#seq = Number(meta.seq ?? 0);
    this.#nextId = Number(meta.next_node_id ?? 1);
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
    let context = {
      previous,
      nodes: new Map(),
      used: new Set(),
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

    let split = this.#split("state", state);
    this.#syncRoots(split.payload, state, ops);

    let orders = new Map();
    for (let [prop, kind, values] of split.arrays) {
      let ids = this.#syncArray(context, ROOT_PARENT, prop, kind, values);
      orders.set(prop, JSON.stringify(ids));
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
   * stricter one needs: the same object, then identical content, then the
   * previous child at the same index, which is updated in place.
   */
  #syncArray(context, parent, prop, kind, values) {
    let previousIds = this.#previousChildren(context, parent, prop);
    let splits = [];
    let ids = [];
    let claim = (i, id) => {
      if (id !== undefined) {
        ids[i] = id;
        context.used.add(id);
      }
    };
    for (let i = 0; i < values.length; i++) {
      splits.push(this.#split(kind, values[i]));
      claim(i, this.#matchObject(context, values[i]));
    }
    let byPayload = null;
    for (let i = 0; i < values.length; i++) {
      if (ids[i] === undefined) {
        byPayload ??= this.#byPayload(context, previousIds);
        claim(i, this.#matchContent(context, splits[i], byPayload));
      }
    }
    for (let i = 0; i < values.length; i++) {
      if (ids[i] === undefined) {
        claim(i, this.#unused(context, previousIds[i]) ?? this.#nextId++);
      }
    }
    for (let i = 0; i < values.length; i++) {
      this.#syncNode(context, ids[i], parent, prop, kind, values[i], splits[i]);
    }
    return ids;
  }

  #syncSingle(context, parent, prop, kind, value) {
    let split = this.#split(kind, value);
    let [previousId] = this.#previousChildren(context, parent, prop);
    let id =
      this.#matchObject(context, value) ??
      this.#unused(context, previousId) ??
      this.#nextId++;
    this.#syncNode(context, id, parent, prop, kind, value, split);
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
   * @returns {Map<string|null, number[]>} The given previous nodes, by payload.
   */
  #byPayload(context, ids) {
    let byPayload = new Map();
    for (let id of ids) {
      let { payload } = context.previous.get(id);
      let bucket = byPayload.get(payload) ?? [];
      bucket.push(id);
      byPayload.set(payload, bucket);
    }
    return byPayload;
  }

  /**
   * Returns the id previously written for the same object, if it's free.
   */
  #matchObject(context, value) {
    if (!value || typeof value != "object") {
      return undefined;
    }
    return this.#unused(context, this.#byObject.get(value));
  }

  /**
   * Returns a free previous node whose payload and sections are identical to
   * `split`, for objects that are recreated with the same content, like the
   * states of tabs that didn't change.
   */
  #matchContent(context, split, byPayload) {
    for (let id of byPayload.get(split.payload) ?? []) {
      if (
        !context.used.has(id) &&
        sameSections(context.previous.get(id).sections, split.sections)
      ) {
        return id;
      }
    }
    return undefined;
  }

  #unused(context, id) {
    return id !== undefined && context.previous.has(id) && !context.used.has(id)
      ? id
      : undefined;
  }

  #syncNode(context, id, parent, prop, kind, value, split) {
    let { ops } = context;
    context.used.add(id);
    if (value && typeof value == "object") {
      this.#byObject.set(value, id);
    }
    let previous = context.previous.get(id);
    if (
      !previous ||
      previous.parent != parent ||
      previous.prop != prop ||
      previous.payload !== split.payload
    ) {
      if (split.payload === null) {
        ops.push("nullnode", id, parent, prop);
      } else {
        ops.push("node", id, parent, prop, split.payload);
      }
    }

    for (let [name, json] of split.sections) {
      if (previous?.sections.get(name) !== json) {
        ops.push("section", id, name, json);
      }
    }
    for (let name of previous?.sections.keys() ?? []) {
      if (!split.sections.has(name)) {
        ops.push("delsection", id, name);
      }
    }

    let orders = new Map();
    for (let [childProp, childKind, values] of split.arrays) {
      let ids = this.#syncArray(context, id, childProp, childKind, values);
      orders.set(childProp, JSON.stringify(ids));
    }
    for (let [childProp, childKind, object] of split.objects) {
      let childId = this.#syncSingle(context, id, childProp, childKind, object);
      orders.set(childProp, String(childId));
    }
    this.#syncOrders(id, previous?.orders, orders, ops);

    context.nodes.set(id, {
      parent,
      prop,
      payload: split.payload,
      sections: split.sections,
      orders,
    });
  }

  /**
   * Splits a value into its payload, its sections and its split properties.
   * Values that aren't plain objects are stored whole.
   *
   * @param {string} kind
   * @param {any} value
   * @returns {Split}
   */
  #split(kind, value) {
    let split = {
      payload: null,
      sections: new Map(),
      arrays: [],
      objects: [],
    };
    if (!isPlainObject(value)) {
      // JSON writes undefined, functions and symbols in arrays as null.
      split.payload = JSON.stringify(value) ?? null;
      if (split.payload == "null") {
        split.payload = null;
      }
      return split;
    }

    let { arrays = {}, objects = {}, sections = {} } = SPLITS[kind];
    let sectionOf = new Map();
    for (let [name, keys] of Object.entries(sections)) {
      for (let key of keys) {
        sectionOf.set(key, name);
      }
    }

    let core = {};
    let sectionValues = new Map();
    for (let key of Object.keys(value)) {
      let child = value[key];
      if (kind == "state" && ROOT_MEMBERS.includes(key)) {
        continue;
      }
      if (Object.hasOwn(arrays, key) && Array.isArray(child)) {
        split.arrays.push([key, arrays[key], child]);
      } else if (Object.hasOwn(objects, key) && isPlainObject(child)) {
        split.objects.push([key, objects[key], child]);
      } else if (sectionOf.has(key)) {
        let name = sectionOf.get(key);
        let members = sectionValues.get(name) ?? {};
        members[key] = child;
        sectionValues.set(name, members);
      } else {
        core[key] = child;
      }
    }
    split.payload = JSON.stringify(core);
    for (let [name, members] of sectionValues) {
      let json = JSON.stringify(members);
      if (json != "{}") {
        split.sections.set(name, json);
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
    typeof value.toJSON != "function"
  );
}

function sameSections(a, b) {
  if (a.size != b.size) {
    return false;
  }
  for (let [name, json] of a) {
    if (b.get(name) !== json) {
      return false;
    }
  }
  return true;
}

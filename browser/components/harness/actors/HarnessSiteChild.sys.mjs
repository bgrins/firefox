/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// Exists so the harness-site:// protocol handler (running in content
// processes) can getActor() a bridge to the parent; all logic is in
// HarnessSiteParent.
/**
 *
 */
export class HarnessSiteChild extends JSWindowActorChild {}

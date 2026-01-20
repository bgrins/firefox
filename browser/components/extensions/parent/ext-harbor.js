/* -*- Mode: indent-tabs-mode: nil; js-indent-level: 2 -*- */
/* vim: set sts=2 sw=2 et tw=80: */
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

ChromeUtils.defineESModuleGetters(this, {
  HarborMCPRegistry:
    "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs",
});

var { ExtensionError } = ExtensionUtils;

this.harbor = class extends ExtensionAPI {
  onShutdown() {
    HarborMCPRegistry.unregister(this.extension.id);
  }

  getAPI(context) {
    const { extension } = context;
    let onMCPMessageFire = null;

    return {
      harbor: {
        async registerMCPServer(metadata) {
          if (!onMCPMessageFire) {
            throw new ExtensionError(
              "Must add onMCPMessage listener before registering"
            );
          }

          HarborMCPRegistry.register(
            extension.id,
            metadata,
            (requestId, message) => {
              if (!onMCPMessageFire) {
                throw new Error("Extension listener removed");
              }
              onMCPMessageFire.async(requestId, message);
            }
          );
        },

        async unregisterMCPServer() {
          HarborMCPRegistry.unregister(extension.id);
        },

        sendMCPResponse(requestId, response) {
          HarborMCPRegistry.handleResponse(extension.id, requestId, response);
        },

        onMCPMessage: new EventManager({
          context,
          name: "harbor.onMCPMessage",
          register: fire => {
            onMCPMessageFire = fire;
            return () => {
              onMCPMessageFire = null;
              HarborMCPRegistry.unregister(extension.id);
            };
          },
        }).api(),
      },
    };
  }
};

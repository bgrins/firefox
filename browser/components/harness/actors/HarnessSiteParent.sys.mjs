/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// Network-blocking CSP injected into every served HTML document: sites are
// agent-authored (and may embed data derived from untrusted pages), so they
// must not exfiltrate. 'self' allows a site's own assets and fetches.
// 'wasm-unsafe-eval' permits client-side WASM (e.g. sql.js over a shipped
// database); it grants no capability inline JS lacks and the exfiltration
// guard is connect-src 'self' plus the scheme having no network at all.
const SITE_CSP =
  `<meta http-equiv="Content-Security-Policy" content="default-src 'self'; ` +
  `script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; ` +
  `style-src 'self' 'unsafe-inline'; ` +
  `img-src 'self' data: blob:; media-src 'self' data: blob:; ` +
  `font-src 'self' data:; connect-src 'self';">`;

const MIME_BY_EXTENSION = {
  html: "text/html",
  htm: "text/html",
  css: "text/css",
  js: "application/javascript",
  mjs: "application/javascript",
  json: "application/json",
  svg: "image/svg+xml",
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  gif: "image/gif",
  webp: "image/webp",
  txt: "text/plain",
  csv: "text/plain",
  woff2: "font/woff2",
  wasm: "application/wasm",
};

/**
 * Parent side of harness-site:// serving: the protocol handler runs in the
 * (sandboxed) content process and cannot read the profile, so it queries
 * this actor for the response bytes. Serves /workspace/sites/<name>/.
 */
export class HarnessSiteParent extends JSWindowActorParent {
  async receiveMessage(message) {
    if (message.name != "HarnessSite:Fetch") {
      return null;
    }
    return HarnessSiteParent.fetchSite(message.data.spec);
  }

  static async fetchSite(spec) {
    if (!Services.prefs.getBoolPref("browser.harness.enabled", false)) {
      throw new Error("harness disabled");
    }
    const uri = Services.io.newURI(spec);
    const site = uri.host;
    if (!/^[a-z0-9][a-z0-9.-]{0,63}$/.test(site)) {
      throw new Error(`invalid site name: ${site}`);
    }
    let path = uri.filePath;
    if (path.endsWith("/")) {
      path += "index.html";
    }
    const segments = path.split("/").filter(Boolean);
    if (segments.some(segment => segment == "." || segment == "..")) {
      throw new Error("path traversal");
    }
    // Sites live inside the (default session's) workspace: the guest's
    // /workspace/sites/<name>/ is served live, so the agent writing files
    // IS publishing — no copy step, and iteration is just a reload.
    const hostPath = PathUtils.join(
      PathUtils.profileDir,
      "harness",
      "workspace",
      "sites",
      site,
      ...segments
    );
    const extension = segments.at(-1).split(".").pop().toLowerCase();
    const contentType =
      MIME_BY_EXTENSION[extension] ?? "application/octet-stream";

    let bytes;
    if (contentType == "text/html") {
      let html = await IOUtils.readUTF8(hostPath);
      const headMatch = html.match(/<head[^>]*>/i);
      html = headMatch
        ? html.replace(headMatch[0], `${headMatch[0]}${SITE_CSP}`)
        : SITE_CSP + html;
      bytes = new TextEncoder().encode(html);
    } else {
      bytes = await IOUtils.read(hostPath);
    }
    // Transfer as ArrayBuffer for structured clone.
    const buffer = bytes.buffer.slice(
      bytes.byteOffset,
      bytes.byteOffset + bytes.byteLength
    );
    return { buffer, contentType };
  }
}

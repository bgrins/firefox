/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const lazy = {};

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "HarnessProxy",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

const AUDIT_LOG_LIMIT = 500;
const MAX_HEADER_BYTES = 64 * 1024;
const MAX_CLIENTHELLO_BYTES = 16 * 1024;
const ECH_EXTENSION = 0xfe0d;

function byteStringToText(bytes) {
  return new TextDecoder().decode(Uint8Array.from(bytes, c => c.charCodeAt(0)));
}

/**
 * Parses a TLS ClientHello (as a latin1 byte-string starting at the record
 * layer) and returns { sni, hasEch } or null if more bytes are needed.
 * Throws on data that is not a ClientHello.
 *
 * @param {string} bytes
 */
export function parseClientHello(bytes) {
  const b = i => bytes.charCodeAt(i);
  if (bytes.length < 9) {
    return null;
  }
  if (b(0) != 0x16) {
    throw new Error("not a TLS handshake record");
  }
  const recordLen = (b(3) << 8) | b(4);
  if (bytes.length < 5 + recordLen) {
    return null; // record incomplete
  }
  if (b(5) != 0x01) {
    throw new Error("not a ClientHello");
  }
  // handshake: type(1) len(3) version(2) random(32)
  let offset = 5 + 4 + 2 + 32;
  const need = extra => {
    if (offset + extra > 5 + recordLen) {
      throw new Error("truncated ClientHello");
    }
  };
  need(1);
  const sessionIdLen = b(offset);
  offset += 1 + sessionIdLen;
  need(2);
  const cipherLen = (b(offset) << 8) | b(offset + 1);
  offset += 2 + cipherLen;
  need(1);
  const compressionLen = b(offset);
  offset += 1 + compressionLen;
  need(2);
  const extensionsLen = (b(offset) << 8) | b(offset + 1);
  offset += 2;
  const extensionsEnd = offset + extensionsLen;
  let sni = null;
  let hasEch = false;
  while (offset + 4 <= extensionsEnd) {
    const extType = (b(offset) << 8) | b(offset + 1);
    const extLen = (b(offset + 2) << 8) | b(offset + 3);
    offset += 4;
    if (extType == ECH_EXTENSION) {
      hasEch = true;
    } else if (extType == 0 && extLen >= 5) {
      // server_name list: listLen(2) type(1) nameLen(2) name
      const nameLen = (b(offset + 3) << 8) | b(offset + 4);
      sni = byteStringToText(bytes.slice(offset + 5, offset + 5 + nameLen));
    }
    offset += extLen;
  }
  return { sni, hasEch };
}

function isPrivateAddress(address) {
  if (address.includes(":")) {
    const lower = address.toLowerCase();
    return (
      lower == "::1" ||
      lower.startsWith("fe80:") ||
      lower.startsWith("fc") ||
      lower.startsWith("fd") ||
      lower.startsWith("::ffff:127.") ||
      lower.startsWith("::ffff:10.") ||
      lower.startsWith("::ffff:192.168.")
    );
  }
  const parts = address.split(".").map(Number);
  return (
    parts[0] == 127 ||
    parts[0] == 10 ||
    parts[0] == 0 ||
    (parts[0] == 172 && parts[1] >= 16 && parts[1] <= 31) ||
    (parts[0] == 192 && parts[1] == 168) ||
    (parts[0] == 169 && parts[1] == 254)
  );
}

/**
 * Deny-by-default HTTP(S) egress proxy for the sandbox. Listens on a unix
 * socket that libkrun bridges to the guest's proxy forwarder; only two
 * request shapes exist: CONNECT host:443 (with SNI == CONNECT host and no
 * ECH) and absolute-form plain HTTP to port 80. Hostnames are checked
 * against browser.harness.proxy.allowlist (JSON array of "host" or
 * "host:port" entries; leading "*." wildcards match subdomains). DNS happens
 * host-side; resolutions to private ranges are rejected unless the entry is
 * an explicit literal match (e.g. "127.0.0.1:8080" in tests).
 */
export class HarnessProxy {
  constructor() {
    this._serverSocket = null;
    this._connections = new Set();
    this.auditLog = [];
  }

  get listening() {
    return !!this._serverSocket;
  }

  listen(socketPath) {
    const file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
    file.initWithPath(socketPath);
    const server = Cc["@mozilla.org/network/server-socket;1"].createInstance(
      Ci.nsIServerSocket
    );
    server.initWithFilename(file, 0o600, 8);
    server.asyncListen({
      onSocketAccepted: (_socket, transport) => {
        const connection = new ProxyConnection(this, transport);
        this._connections.add(connection);
      },
      onStopListening: () => {},
    });
    this._serverSocket = server;
    lazy.logConsole.log(`egress proxy at ${socketPath}`);
  }

  stop() {
    this._serverSocket?.close();
    this._serverSocket = null;
    for (const connection of [...this._connections]) {
      connection.close();
    }
  }

  allowlist() {
    try {
      const parsed = JSON.parse(
        Services.prefs.getStringPref("browser.harness.proxy.allowlist", "[]")
      );
      return Array.isArray(parsed)
        ? parsed.filter(e => typeof e == "string")
        : [];
    } catch (e) {
      return [];
    }
  }

  /**
   * @param {string} host
   * @param {number} port
   * @returns {{allowed: boolean, explicit: boolean}} explicit = the exact
   *   host[:port] literal is listed (opts out of the private-address guard).
   */
  policy(host, port) {
    const hostLower = host.toLowerCase();
    for (const entry of this.allowlist()) {
      const [entryHost, entryPort] = entry.toLowerCase().split(":");
      const portOk = entryPort
        ? Number(entryPort) == port
        : [80, 443].includes(port);
      if (!portOk) {
        continue;
      }
      if (entryHost == hostLower) {
        return { allowed: true, explicit: true };
      }
      if (
        entryHost.startsWith("*.") &&
        hostLower.endsWith(entryHost.slice(1))
      ) {
        return { allowed: true, explicit: false };
      }
    }
    return { allowed: false, explicit: false };
  }

  audit(verdict, detail) {
    const entry = { timeMs: Date.now(), verdict, detail };
    this.auditLog.push(entry);
    if (this.auditLog.length > AUDIT_LOG_LIMIT) {
      this.auditLog.shift();
    }
    lazy.logConsole.log(`${verdict}: ${detail}`);
  }

  async resolve(host, { explicit }) {
    const record = await new Promise((resolve, reject) => {
      Services.dns.asyncResolve(
        host,
        Ci.nsIDNSService.RESOLVE_TYPE_DEFAULT,
        0,
        null,
        {
          onLookupComplete(_request, rec, status) {
            if (Components.isSuccessCode(status)) {
              resolve(rec.QueryInterface(Ci.nsIDNSAddrRecord));
            } else {
              reject(new Error(`DNS resolution failed for ${host}`));
            }
          },
        },
        Services.tm.currentThread,
        {}
      );
    });
    const address = record.getNextAddrAsString();
    if (!explicit && isPrivateAddress(address)) {
      throw new Error(`${host} resolved to private address ${address}`);
    }
    return address;
  }
}

/** One guest connection: parse, apply policy, tunnel. */
class ProxyConnection {
  constructor(proxy, transport) {
    this._proxy = proxy;
    this._client = this._wrap(transport);
    this._upstream = null;
    this._buffer = "";
    this._state = "request"; // request -> clienthello (CONNECT only) -> splice
    this._connectHost = null;
    this._connectPort = 0;
    this._read(this._client, bytes => this._onClientData(bytes));
  }

  _wrap(transport) {
    const scriptable = Cc[
      "@mozilla.org/scriptableinputstream;1"
    ].createInstance(Ci.nsIScriptableInputStream);
    const input = transport.openInputStream(0, 0, 0);
    scriptable.init(input);
    return {
      transport,
      input,
      scriptable,
      output: transport.openOutputStream(0, 0, 0),
    };
  }

  _read(endpoint, onData) {
    endpoint.input.QueryInterface(Ci.nsIAsyncInputStream).asyncWait(
      {
        onInputStreamReady: () => {
          let bytes;
          try {
            const available = endpoint.scriptable.available();
            bytes = available ? endpoint.scriptable.readBytes(available) : "";
            if (!available) {
              this.close();
              return;
            }
          } catch (e) {
            this.close();
            return;
          }
          onData(bytes);
          if (!this._closed) {
            this._read(endpoint, onData);
          }
        },
      },
      0,
      0,
      Services.tm.currentThread
    );
  }

  _write(endpoint, bytes) {
    try {
      endpoint.output.write(bytes, bytes.length);
      endpoint.output.flush();
    } catch (e) {
      this.close();
    }
  }

  _deny(status, reason) {
    this._proxy.audit("denied", reason);
    this._write(
      this._client,
      `HTTP/1.1 ${status}\r\nConnection: close\r\n\r\n`
    );
    this.close();
  }

  async _onClientData(bytes) {
    if (this._state == "splice") {
      if (this._upstream) {
        this._write(this._upstream, bytes);
      }
      return;
    }
    this._buffer += bytes;
    if (this._buffer.length > MAX_HEADER_BYTES + MAX_CLIENTHELLO_BYTES) {
      this._deny("400 Bad Request", "oversized request");
      return;
    }
    if (this._state == "request") {
      const headerEnd = this._buffer.indexOf("\r\n\r\n");
      if (headerEnd < 0) {
        return;
      }
      const header = this._buffer.slice(0, headerEnd);
      const rest = this._buffer.slice(headerEnd + 4);
      this._buffer = "";
      await this._handleRequest(header, rest).catch(e => {
        this._deny("502 Bad Gateway", e.message);
      });
    } else if (this._state == "clienthello") {
      await this._tryClientHello().catch(e => {
        this._proxy.audit("denied", `tls inspection: ${e.message}`);
        this.close();
      });
    }
  }

  async _handleRequest(header, rest) {
    const requestLine = header.split("\r\n")[0];
    const connectMatch = requestLine.match(/^CONNECT\s+([^\s:]+):(\d+)\s/);
    if (connectMatch) {
      const host = connectMatch[1];
      const port = Number(connectMatch[2]);
      const { allowed, explicit } = this._proxy.policy(host, port);
      if (!allowed || (port != 443 && !explicit)) {
        this._deny("403 Forbidden", `CONNECT ${host}:${port}`);
        return;
      }
      this._connectHost = host;
      this._connectPort = port;
      this._connectExplicit = explicit;
      this._state = "clienthello";
      this._buffer = rest;
      this._write(this._client, "HTTP/1.1 200 Connection Established\r\n\r\n");
      await this._tryClientHello();
      return;
    }
    const absoluteMatch = requestLine.match(
      /^([A-Z]+)\s+http:\/\/([^/\s:]+)(?::(\d+))?(\/[^\s]*)?\s+(HTTP\/1\.\d)$/
    );
    if (absoluteMatch) {
      const [, method, host, portString, path, version] = absoluteMatch;
      const port = portString ? Number(portString) : 80;
      const { allowed, explicit } = this._proxy.policy(host, port);
      if (!allowed || (port != 80 && !explicit)) {
        this._deny("403 Forbidden", `${method} http://${host}:${port}`);
        return;
      }
      const address = await this._proxy.resolve(host, { explicit });
      this._proxy.audit(
        "allowed",
        `${method} http://${host}:${port}${path ?? "/"}`
      );
      await this._connectUpstream(address, port);
      // Rewrite to origin-form and force connection close.
      const headers = header
        .split("\r\n")
        .slice(1)
        .filter(line => !/^(proxy-connection|connection):/i.test(line));
      headers.push("Connection: close");
      this._write(
        this._upstream,
        `${method} ${path ?? "/"} ${version}\r\n${headers.join("\r\n")}\r\n\r\n${rest}`
      );
      this._state = "splice";
      return;
    }
    this._deny(
      "405 Method Not Allowed",
      `unsupported request: ${requestLine.slice(0, 80)}`
    );
  }

  async _tryClientHello() {
    let hello;
    try {
      hello = parseClientHello(this._buffer);
    } catch (e) {
      throw new Error(`${this._connectHost}: ${e.message}`);
    }
    if (!hello) {
      if (this._buffer.length > MAX_CLIENTHELLO_BYTES) {
        throw new Error("ClientHello too large");
      }
      return; // need more bytes
    }
    if (hello.hasEch) {
      throw new Error(`${this._connectHost}: ECH hides SNI; refusing tunnel`);
    }
    if ((hello.sni ?? "").toLowerCase() != this._connectHost.toLowerCase()) {
      throw new Error(
        `SNI mismatch: CONNECT ${this._connectHost} but SNI ${hello.sni}`
      );
    }
    const address = await this._proxy.resolve(this._connectHost, {
      explicit: this._connectExplicit,
    });
    this._proxy.audit(
      "allowed",
      `CONNECT ${this._connectHost}:${this._connectPort} (sni verified)`
    );
    await this._connectUpstream(address, this._connectPort);
    this._write(this._upstream, this._buffer);
    this._buffer = "";
    this._state = "splice";
  }

  async _connectUpstream(address, port) {
    const sts = Cc[
      "@mozilla.org/network/socket-transport-service;1"
    ].getService(Ci.nsISocketTransportService);
    const transport = sts.createTransport([], address, port, null, null);
    this._upstream = this._wrap(transport);
    this._read(this._upstream, bytes => this._write(this._client, bytes));
  }

  close() {
    if (this._closed) {
      return;
    }
    this._closed = true;
    for (const endpoint of [this._client, this._upstream]) {
      try {
        endpoint?.scriptable.close();
        endpoint?.output.close();
        endpoint?.transport.close(Cr.NS_OK);
      } catch (e) {
        // Already closed.
      }
    }
    this._proxy._connections.delete(this);
  }
}

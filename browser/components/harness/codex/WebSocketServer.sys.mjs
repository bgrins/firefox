/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const lazy = {};

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "WebSocketServer",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

const WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
const MAX_MESSAGE_BYTES = 64 * 1024 * 1024;

function sha1Base64(text) {
  const bytes = Array.from(text, c => c.charCodeAt(0) & 0xff);
  const hasher = Cc["@mozilla.org/security/hash;1"].createInstance(
    Ci.nsICryptoHash
  );
  hasher.init(Ci.nsICryptoHash.SHA1);
  hasher.update(bytes, bytes.length);
  return hasher.finish(true);
}

function toByteString(uint8) {
  let out = "";
  const CHUNK = 0x8000;
  for (let i = 0; i < uint8.length; i += CHUNK) {
    out += String.fromCharCode(...uint8.subarray(i, i + CHUNK));
  }
  return out;
}

/**
 * Minimal RFC6455 server for loopback JSON-message protocols: accepts exactly
 * one connection (then stops listening), one JSON document per text frame.
 * Used by CodexExecBridge; not a general-purpose server.
 */
export class WebSocketServer {
  constructor({ onMessage, onConnect, onDisconnect } = {}) {
    this.onMessage = onMessage;
    this.onConnect = onConnect;
    this.onDisconnect = onDisconnect;
    this._serverSocket = null;
    this._transport = null;
    this._input = null;
    this._output = null;
    this._scriptableIn = null;
    this._buffer = "";
    this._handshaken = false;
    this._fragments = "";
  }

  get port() {
    return this._serverSocket?.port ?? -1;
  }

  get connected() {
    return !!this._transport && this._handshaken;
  }

  start() {
    const server = Cc["@mozilla.org/network/server-socket;1"].createInstance(
      Ci.nsIServerSocket
    );
    server.init(-1, /* loopbackOnly */ true, 4);
    server.asyncListen({
      onSocketAccepted: (_socket, transport) => this._accept(transport),
      onStopListening: () => {},
    });
    this._serverSocket = server;
    lazy.logConsole.log(`listening on 127.0.0.1:${server.port}`);
    return server.port;
  }

  _accept(transport) {
    if (this._transport) {
      lazy.logConsole.warn("rejecting second connection");
      transport.close(Cr.NS_ERROR_ABORT);
      return;
    }
    this._transport = transport;
    this._input = transport.openInputStream(0, 0, 0);
    this._output = transport.openOutputStream(0, 0, 0);
    this._scriptableIn = Cc[
      "@mozilla.org/scriptableinputstream;1"
    ].createInstance(Ci.nsIScriptableInputStream);
    this._scriptableIn.init(this._input);
    // Single-accept: stop listening once the expected peer arrives.
    this._serverSocket?.close();
    this._waitForData();
  }

  _waitForData() {
    if (!this._input) {
      return;
    }
    this._input.QueryInterface(Ci.nsIAsyncInputStream).asyncWait(
      {
        onInputStreamReady: () => this._onData(),
      },
      0,
      0,
      Services.tm.currentThread
    );
  }

  _onData() {
    if (!this._scriptableIn) {
      return;
    }
    try {
      const available = this._scriptableIn.available();
      if (available) {
        this._buffer += this._scriptableIn.readBytes(available);
      }
    } catch (e) {
      this._teardown();
      return;
    }
    if (this._buffer.length > MAX_MESSAGE_BYTES) {
      lazy.logConsole.warn("buffer limit exceeded; closing");
      this._teardown();
      return;
    }
    try {
      if (!this._handshaken) {
        this._tryHandshake();
      }
      if (this._handshaken) {
        this._parseFrames();
      }
    } catch (e) {
      lazy.logConsole.warn(`protocol error: ${e.message}`);
      this._teardown();
      return;
    }
    this._waitForData();
  }

  _tryHandshake() {
    const end = this._buffer.indexOf("\r\n\r\n");
    if (end < 0) {
      return;
    }
    const header = this._buffer.slice(0, end);
    this._buffer = this._buffer.slice(end + 4);
    const keyMatch = header.match(/^Sec-WebSocket-Key:\s*(\S+)/im);
    if (!header.startsWith("GET ") || !keyMatch) {
      throw new Error("not a websocket upgrade request");
    }
    const accept = sha1Base64(keyMatch[1] + WS_GUID);
    const response =
      "HTTP/1.1 101 Switching Protocols\r\n" +
      "Upgrade: websocket\r\n" +
      "Connection: Upgrade\r\n" +
      `Sec-WebSocket-Accept: ${accept}\r\n\r\n`;
    this._output.write(response, response.length);
    this._handshaken = true;
    lazy.logConsole.log("websocket handshake complete");
    this.onConnect?.();
  }

  _parseFrames() {
    for (;;) {
      const buf = this._buffer;
      if (buf.length < 2) {
        return;
      }
      const b0 = buf.charCodeAt(0);
      const b1 = buf.charCodeAt(1);
      const fin = (b0 & 0x80) != 0;
      const opcode = b0 & 0x0f;
      const masked = (b1 & 0x80) != 0;
      let len = b1 & 0x7f;
      let offset = 2;
      if (len == 126) {
        if (buf.length < 4) {
          return;
        }
        len = (buf.charCodeAt(2) << 8) | buf.charCodeAt(3);
        offset = 4;
      } else if (len == 127) {
        if (buf.length < 10) {
          return;
        }
        len = 0;
        for (let i = 2; i < 10; i++) {
          len = len * 256 + buf.charCodeAt(i);
        }
        offset = 10;
      }
      if (len > MAX_MESSAGE_BYTES) {
        throw new Error("frame too large");
      }
      const maskOffset = offset;
      if (masked) {
        offset += 4;
      }
      if (buf.length < offset + len) {
        return;
      }
      let payload = buf.slice(offset, offset + len);
      this._buffer = buf.slice(offset + len);
      if (masked) {
        const key = [
          buf.charCodeAt(maskOffset),
          buf.charCodeAt(maskOffset + 1),
          buf.charCodeAt(maskOffset + 2),
          buf.charCodeAt(maskOffset + 3),
        ];
        let unmasked = "";
        for (let i = 0; i < payload.length; i++) {
          unmasked += String.fromCharCode(payload.charCodeAt(i) ^ key[i % 4]);
        }
        payload = unmasked;
      }
      this._handleFrame(fin, opcode, payload);
    }
  }

  _handleFrame(fin, opcode, payload) {
    switch (opcode) {
      case 0x0: // continuation
        this._fragments += payload;
        if (fin) {
          this._dispatch(this._fragments);
          this._fragments = "";
        }
        break;
      case 0x1: // text
      case 0x2: // binary (tolerated; payload is still JSON)
        if (fin) {
          this._dispatch(payload);
        } else {
          this._fragments = payload;
        }
        break;
      case 0x8: // close
        this._sendRaw(0x88, "");
        this._teardown();
        break;
      case 0x9: // ping
        this._sendRaw(0x8a, payload);
        break;
      case 0xa: // pong
        break;
      default:
        throw new Error(`unsupported opcode ${opcode}`);
    }
  }

  _dispatch(payloadBytes) {
    const bytes = Uint8Array.from(payloadBytes, c => c.charCodeAt(0));
    let message;
    try {
      message = JSON.parse(new TextDecoder().decode(bytes));
    } catch (e) {
      lazy.logConsole.warn(`unparseable frame: ${payloadBytes.slice(0, 120)}`);
      return;
    }
    this.onMessage?.(message);
  }

  send(obj) {
    if (!this.connected) {
      lazy.logConsole.warn("dropping message; not connected");
      return;
    }
    const payload = toByteString(new TextEncoder().encode(JSON.stringify(obj)));
    this._sendRaw(0x81, payload);
  }

  _sendRaw(firstByte, payload) {
    if (!this._output) {
      return;
    }
    let header = String.fromCharCode(firstByte);
    const len = payload.length;
    if (len < 126) {
      header += String.fromCharCode(len);
    } else if (len < 0x10000) {
      header += String.fromCharCode(126, (len >> 8) & 0xff, len & 0xff);
    } else {
      header += String.fromCharCode(127, 0, 0, 0, 0);
      header += String.fromCharCode(
        (len / 0x1000000) & 0xff,
        (len >> 16) & 0xff,
        (len >> 8) & 0xff,
        len & 0xff
      );
    }
    const frame = header + payload;
    try {
      this._output.write(frame, frame.length);
      this._output.flush();
    } catch (e) {
      lazy.logConsole.warn(`write failed: ${e.message}`);
      this._teardown();
    }
  }

  _teardown() {
    const wasConnected = this.connected;
    try {
      this._scriptableIn?.close();
      this._output?.close();
      this._transport?.close(Cr.NS_OK);
    } catch (e) {
      // Already closed.
    }
    this._transport = null;
    this._input = null;
    this._output = null;
    this._scriptableIn = null;
    this._buffer = "";
    this._handshaken = false;
    if (wasConnected) {
      this.onDisconnect?.();
    }
  }

  stop() {
    this._serverSocket?.close();
    this._serverSocket = null;
    this._teardown();
  }
}

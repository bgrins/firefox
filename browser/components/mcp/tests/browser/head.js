/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { MCPServer } = ChromeUtils.importESModule(
  "moz-src:///browser/components/mcp/MCPServer.sys.mjs"
);
const { MCPBridge } = ChromeUtils.importESModule(
  "moz-src:///browser/components/mcp/MCPBridge.sys.mjs"
);
const { MCPSessions } = ChromeUtils.importESModule(
  "moz-src:///browser/components/mcp/MCPSessions.sys.mjs"
);
const { NavigableManager } = ChromeUtils.importESModule(
  "chrome://remote/content/shared/NavigableManager.sys.mjs"
);

let gRpcId = 0;

// Raw HTTP over nsISocketTransportService: keeps the tests independent of the
// mochitest proxy and of fetch()'s Origin header (which the server rejects),
// and exercises the hand-rolled HTTP listener in MCPBridge directly.
function rawHttpRequest(
  port,
  { method = "POST", path = "/mcp", headers = {}, body = "" } = {}
) {
  return new Promise((resolve, reject) => {
    const sts = Cc[
      "@mozilla.org/network/socket-transport-service;1"
    ].getService(Ci.nsISocketTransportService);
    const transport = sts.createTransport([], "127.0.0.1", port, null, null);
    const output = transport.openOutputStream(
      Ci.nsITransport.OPEN_BLOCKING,
      0,
      0
    );
    const input = transport
      .openInputStream(0, 0, 0)
      .QueryInterface(Ci.nsIAsyncInputStream);
    const bin = Cc["@mozilla.org/binaryinputstream;1"].createInstance(
      Ci.nsIBinaryInputStream
    );
    bin.setInputStream(input);

    const lines = [
      `${method} ${path} HTTP/1.1`,
      `Host: 127.0.0.1:${port}`,
      `Content-Length: ${body.length}`,
      "Connection: close",
    ];
    for (const [k, v] of Object.entries(headers)) {
      lines.push(`${k}: ${v}`);
    }
    const request = lines.join("\r\n") + "\r\n\r\n" + body;

    let response = "";
    const finish = () => {
      try {
        input.close();
      } catch {}
      try {
        output.close();
      } catch {}
      resolve(parseRawResponse(response));
    };
    const readMore = () => {
      input.asyncWait(
        {
          onInputStreamReady() {
            let available;
            try {
              available = input.available();
            } catch {
              // Closed (end of response with Connection: close) or refused.
              finish();
              return;
            }
            try {
              if (available) {
                response += bin.readBytes(available);
              }
              readMore();
            } catch (e) {
              reject(e);
            }
          },
        },
        0,
        0,
        Services.tm.currentThread
      );
    };

    try {
      output.write(request, request.length);
    } catch (e) {
      reject(e);
      return;
    }
    readMore();
  });
}

function parseRawResponse(raw) {
  if (!raw) {
    return { status: 0, headers: {}, body: "" };
  }
  const headerEnd = raw.indexOf("\r\n\r\n");
  const head = raw.slice(0, headerEnd).split("\r\n");
  const status = parseInt(head[0].split(" ")[1], 10);
  const headers = {};
  for (const line of head.slice(1)) {
    const idx = line.indexOf(":");
    if (idx > 0) {
      headers[line.slice(0, idx).trim().toLowerCase()] = line
        .slice(idx + 1)
        .trim();
    }
  }
  const bodyBytes = raw.slice(headerEnd + 4);
  const body = new TextDecoder().decode(
    Uint8Array.from(bodyBytes, c => c.charCodeAt(0))
  );
  return { status, headers, body };
}

// token: undefined -> the running server's session token, null -> no
// Authorization header, string -> that value.
async function mcpRpc(port, rpcMethod, params = {}, { token } = {}) {
  const bearer = token === undefined ? MCPServer.session?.token : token;
  const headers = { "Content-Type": "application/json" };
  if (bearer != null) {
    headers.Authorization = `Bearer ${bearer}`;
  }
  const res = await rawHttpRequest(port, {
    headers,
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: ++gRpcId,
      method: rpcMethod,
      params,
    }),
  });
  if (res.status === 200) {
    res.json = JSON.parse(res.body);
  }
  return res;
}

async function callTool(port, name, args = {}) {
  const res = await mcpRpc(port, "tools/call", { name, arguments: args });
  Assert.equal(res.status, 200, `tools/call ${name} got an HTTP 200`);
  return res.json.result;
}

function toolText(result) {
  return (result?.content ?? []).map(c => c.text).join("\n");
}

// list_pages only reports tab titles, so tests load pages with known titles.
function testPageUrl(host, title) {
  return `https://${host}/document-builder.sjs?html=${encodeURIComponent(
    `<title>${title}</title>${title}`
  )}`;
}

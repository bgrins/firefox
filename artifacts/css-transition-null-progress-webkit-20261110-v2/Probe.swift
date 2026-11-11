import AppKit
import WebKit

final class Probe: NSObject, WKNavigationDelegate {
    let webView: WKWebView
    let window: NSWindow
    var finished = false
    var phase = "created"

    override init() {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .nonPersistent()
        webView = WKWebView(frame: NSRect(x: 0, y: 0, width: 800, height: 600),
                            configuration: configuration)
        window = NSWindow(contentRect: webView.frame,
                          styleMask: [.titled, .closable], backing: .buffered, defer: false)
        super.init()
        webView.navigationDelegate = self
        window.contentView = webView
        window.title = "Transition routing probe"
    }

    func finish(_ value: [String: Any], code: Int32) {
        guard !finished else { return }
        finished = true
        do {
            let data = try JSONSerialization.data(withJSONObject: value,
                                                  options: [.prettyPrinted, .sortedKeys])
            FileHandle.standardOutput.write(data)
            FileHandle.standardOutput.write(Data("\n".utf8))
        } catch {
            FileHandle.standardError.write(Data("JSON serialization failed: \(error)\n".utf8))
            exit(2)
        }
        window.orderOut(nil)
        exit(code)
    }

    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        phase = "loading"
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        phase = "executing"
        webView.callAsyncJavaScript("""
            const results = [];
            for (const mode of ['transition-only', 'active-overlap', 'current-no-fill']) {
                results.push(await runTransitionRoutingCase(mode));
            }
            return JSON.stringify({userAgent:navigator.userAgent, url:location.href,
                results, remainingProbeElements:document.querySelectorAll('.routing-probe').length,
                remainingAnimations:document.getAnimations().length});
            """, arguments: [:], in: nil, in: .page) { result in
                switch result {
                case .success(let value):
                    do {
                        guard let text = value as? String, let data = text.data(using: .utf8),
                              let payload = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                        else { throw NSError(domain: "Probe", code: 1) }
                        let version = Bundle(for: WKWebView.self).infoDictionary?["CFBundleVersion"] as? String ?? "unknown"
                        self.finish(["engine": "System WKWebView", "webkitBundleVersion": version,
                                     "ephemeralDataStore": true, "browserResult": payload], code: 0)
                    } catch {
                        self.finish(["error": String(describing: error)], code: 1)
                    }
                case .failure(let error):
                    self.finish(["error": String(describing: error)], code: 1)
                }
            }
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!,
                 withError error: Error) {
        finish(["error": String(describing: error)], code: 1)
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        finish(["error": String(describing: error)], code: 1)
    }
}

guard CommandLine.arguments.count == 2 else { exit(2) }
let application = NSApplication.shared
application.setActivationPolicy(.accessory)
let probe = Probe()
let page = URL(fileURLWithPath: CommandLine.arguments[1]).standardizedFileURL
application.finishLaunching()
probe.window.makeKeyAndOrderFront(nil)
application.activate(ignoringOtherApps: true)
probe.webView.loadFileURL(page, allowingReadAccessTo: page.deletingLastPathComponent())
DispatchQueue.main.asyncAfter(deadline: .now() + 30) {
    probe.finish(["error": "Timed out waiting for probe completion",
                  "phase": probe.phase, "isLoading": probe.webView.isLoading,
                  "windowVisible": probe.window.isVisible,
                  "occlusionVisible": probe.window.occlusionState.contains(.visible),
                  "url": probe.webView.url?.absoluteString ?? "none"], code: 1)
}
application.run()

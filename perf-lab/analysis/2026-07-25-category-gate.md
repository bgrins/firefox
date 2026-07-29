# SLIM_UI category gate — measured + QA'd

Date: 2026-07-25. Artifact build, about:blank, 3 runs + 1 warmup, 6s settle.
Pref-driven: browser.slimui.enabled=true, plus browser.newtab.preload=false.
72 of 73 skip entries matched (StartupTelemetry.bestEffortIdleStartup needs 20s idle).

TIMINGS ARE NOT CREDIBLE in this run — measured under concurrent build load.
Module counts and memory are contention-insensitive and are the real result.

## Manual QA (real MCP path: geckodriver + WebDriver BiDi)

Found and fixed three genuine breakages. Each produced a JS error with the gate
on and zero with it off:

| Skipped entry | Failure |
|---|---|
| AboutNewTab.init | AboutNewTabRedirector.sys.mjs:550 NS_ERROR_NOT_AVAILABLE — about:newtab protocol handler never registered |
| SidebarController.init | browser-sidebar.js:754 this._state undefined, via SessionStore/BackupService |
| PanelUI.init | panelUI.js:198 this.panel undefined, x3 |

All three removed from the default list (76 -> 73 entries). Re-verified: zero new
JS errors. Remaining console noise (GPU proc launch, FaviconLoader sniffing,
services-settings dummy server) reproduces with the gate OFF, so it is
environmental. Baseline additionally logs a Nimbus sync error the gate removes.

Exercised OK under the gate: navigate, snapshot, click (+link navigation),
fill, select, history back, multi-tab open/list, page screenshot, console
capture, network capture.

NOT exercised: dialogs, file upload, downloads, DevTools toolbox, chrome-level
screenshots, extension install, private browsing.

## compare base3 vs slim3

```
base    : base3  env=(none)
variant : slim3  env=(none)

metric                              base     variant       delta         
-------------------------------------------------------------------------
main                                31ms        35ms        +4ms  +12.9% 
createTopLevelWindow               618ms       663ms       +45ms   +7.3% 
firstPaint                         880ms       948ms       +68ms   +7.7% 
firstPaint2                        880ms       948ms       +68ms   +7.7% 
sessionRestored                    954ms      1013ms       +59ms   +6.2% 
wall (spawn->session)             1425ms      1348ms       -77ms   -5.4% 
ES modules @early                    618         419        -199  -32.2%*
ES modules @settled                  621         420        -201  -32.4%*
USS parent @early                300.5MB     205.1MB     -95.4MB  -31.8%*
USS parent @settled              311.2MB     206.2MB    -105.0MB  -33.7%*
heap parent @settled             278.7MB     202.1MB     -76.6MB  -27.5%*
JS GC heap @settled               30.4MB      24.1MB      -6.3MB  -20.7%*
system realms @settled                15          15           0   +0.0% 
RSS all procs @settled           649.9MB     497.5MB    -152.4MB  -23.4%*
process count @settled                 9           9           0   +0.0% 

* = |delta| exceeds observed run-to-run spread

=== esModules: 201 avoided, 0 newly loaded ===
  -30   newtab/lib
  -27   gre/modules
  -19   browser/components/urlbar/private
  -13   toolkit/components/ipprotection
  -11   modules
  -9    normandy/lib
  -6    newtab/lib/Widgets
  -6    browser/components/ipprotection
  -5    toolkit/components/uniffi-bindgen-gecko-js/components/generated
  -5    gre/modules/shared
  -4    browser/components/aiwindow/models/agents
  -4    actors
  -4    nimbus/lib
  -3    toolkit/components/doh
  -3    browser/components/urlbar
  -3    newtab/lib/InferredModel
  -3    newtab/common
  -3    gre/modules/psm
  -3    toolkit/components/ipprotection/fxa
  -3    modules/topsites
  -2    normandy
  -2    browser/content/ipprotection
  -2    newtab/lib/SmartShortcutsRanker
  -2    browser/components/places
  -2    modules/taskbartabs
  -2    browser/components/aiwindow/models
  -2    browser/components/search
  -2    autofill
  -1    newtab/lib/FrecencyBoostProvider
  -1    browser/components/aiwindow/ui/modules
  -1    browser/components/privatebrowsing
  -1    browser/components/customkeys
  -1    browser/components/genai
  -1    newtab/lib/Wallpapers
  -1    messaging-system/lib
  -1    browser/modules
  -1    browser/components/customizableui
  -1    browser/components/newtab
  -1    toolkit/modules
  -1    global/content/vendor
  -1    browser/components/contentanalysis/content
  -1    browser/components/reportbrokensite
  -1    browser/components/tabnotes
  -1    browser/components
  -1    browser/components/shell
  -1    browser/components/downloads
  -1    browser/components/tabbrowser
  -1    toolkit/components/captchadetection
  -1    services-settings
```

## memdiff

```
parent explicit: 293.4MB -> 193.8MB (-99.6MB)

movers >= 1000KB, rolled up to depth 3

     delta       base    variant  path
------------------------------------------------------------------------------
   -26173K     47817K     21644K  explicit/js-non-window/runtime
   -22191K     57559K     35369K  explicit/js-non-window/zones
   -16832K     92099K     75267K  explicit/gfx/webrender
   -15876K     21883K      6007K  explicit/storage/sqlite
   -12100K     12100K         0K  explicit/window-objects/top(about:newtab, id=24) [child]
    -4802K     18202K     13400K  explicit/js-non-window/runtime [child]
    -4639K      4639K         0K  explicit/workers/workers(chrome)
    -4285K     16353K     12069K  explicit/startup-cache/data
    -4167K      4171K         4K  explicit/network/cache2
    -3052K     18510K     15458K  explicit/script-preloader/heap
    -2738K      2738K         0K  explicit/images/content [child]
    -1118K      2847K      1729K  explicit/js-non-window/gc-heap [child]
```

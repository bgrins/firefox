# Installed-browser portable four-case observation

Run only after the active native pair has completed restoration and process cleanup. Root reported installed Firefox 158.0 and Nightly 160.0a1; those are preliminary inventory labels, not newly measured results. Observe each app separately without rebuilding or modifying either app or the native checkout.

Reuse `css-appearance-typed-attr-pair-v2/wpt.py:prepare_inputs` with its exact ordinary lane settings to stage the unchanged sealed four-case page, both frozen harness files, genuine manifest and empty page metadata. Create a new output, an owned temporary WPT root and an empty run-info directory per browser. In the generated config, replace the objdir run-info path with that empty directory. Standard WPT automation profile settings remain; there are no fixture preferences or CSS feature overrides. This is a stock installed binary under WPT automation, not a claim about every untouched consumer profile.

The existing runner command shape is:

```sh
MOZ_WPT_TEMP_ROOT="$owned_temp" /Users/bgrins/venvs/firefox/bin/python ./mach wpt \
  --headless --processes=1 --no-manifest-update --no-manifest-download --no-install-fonts \
  --browser-channel=stable \
  --binary=/Applications/Firefox.app/Contents/MacOS/firefox \
  --config="$output/wptrunner.ini" --run-info="$output/run-info" \
  --prefs-root=/Users/bgrins/code/firefox/testing/profiles \
  --log-raw="$output/raw.jsonl" \
  --include=/css/css-ui/appearance-typed-attr-scheduling.tentative.html
```

For the separate Nightly observation, select the root-reported `/Applications/Nightly.app/Contents/MacOS/firefox` after confirming and pinning the actual path, and use `--browser-channel=nightly`. Use a new profile/temp root/output for each app. Wptrunner creates and cleans its own fresh automation profile within the owned temporary root; do not pass the user's profile.

Before and after each run, record selected binary hashes and Info.plist/application.ini/platform.ini metadata plus the app entry identities. Preserve raw JSONL, full command/log/exit and cleanup receipts. Use the existing process helper and 180-second watchdog; verify the owned process group is absent before deleting the exact owned temporary directory. No build, source overlay, canonical epoch write or user-profile cleanup is needed. Do not call the native pair `wpt.run` unchanged because its local-build role/source checks do not describe an installed browser.

Do not import objdir run-info into the installed observation. The existing Firefox WPT backend reads browser BuildID, changeset and version using mozversion on the selected binary. Save these independently from the checkout harness revision. Report all four callback identities and the page ending, preserving every failure message. Missing callbacks, timeout or setup failure are incomplete observations.

The fixture checks typed attr syntax and registered-property setup, then independently checks nested-var typed attr width at absolute 20px/30px before target assertions. A syntax assertion, registration failure or width-control failure means missing/broken prerequisite capability; it must not be classified as the same appearance scheduling discrepancy. Only after those controls pass can target appearance/family/length differences support a comparable observation. PASS does not expose hidden diagnostic rows through raw WPT; do not invent them. Keep the published-original branch, selected-declaration candidate, installed Firefox and installed Nightly as distinct source/provenance roles.

This is a command/plan, not an executable owner or browser result. No installed app, profile, process or live native state was read or modified to prepare it.

Searchfox inspection found ProfileCreator includes `unittest-features` for an absent/nightly channel but omits it for other channels; the explicit stable channel is therefore significant. Indexed testing profiles and wptrunner contained no `layout.css.attr` override or properties-and-values override, and the indexed static `layout.css.properties-and-values.enabled` default is true. These are current indexed sources, not a proof of the installed builds’ historical defaults. Save the actual effective WPT profile preferences before cleanup. An untouched release-default comparison would require a distinct fresh-profile page observation outside the standard WPT feature profile; do not silently equate it with this harness-configured run. Searchfox calls: 8d75d3, e0b99d, d3038f, 7e3299, 82dada, 372e27.

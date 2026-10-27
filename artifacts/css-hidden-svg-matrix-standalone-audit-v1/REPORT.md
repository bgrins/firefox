# SVG matrix patch applicability

The exact two-path Gecko/WPT patch applies and reverses on both HEAD90 and the recorded upstream base976279105b2e. Both produce byte-identical candidate native and WPT files; reversal restores the original source and removes the added test. Both disposable scratch directories were removed.

This is textual independence only. No upstream-base build/browser execution or acceptance is claimed. The separate HEAD90 baseline/candidate experiment supplies runtime evidence, subject to its final restoration and review. No working native, index, browser or build changes occurred in this audit.

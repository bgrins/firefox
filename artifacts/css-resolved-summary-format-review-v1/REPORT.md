# Formatting addendum

Approved the formatting-only change from sealed candidate `d38d0831d0e4acc68e0a7064f03674de81e0e6e6f35e0243ab349305015dd794` to formatted candidate `71a507cba6ed20b40e690c29555844514870530a5bccc74e41459aa12e46d5bc`.

The complete diff contains exactly two expression wraps: the new-resolved call in the attribute persistence arm, and the corresponding call in the universal-registration arm. Each moves the initializer after `let mut value =` onto the next line and adjusts indentation. Arguments, token order, comments, helper, constructor and every other byte remain unchanged. The retained patch has SHA-256 `30a94accb8fcc6f99e130c604be0eb631ed480ca00dc00538259063518aae141`.

The checker reconstructs the formatted file using those two exact replacements and reproduces the entire patch. This transfers the preceding source/WPT review to the formatted source; it does not replace root's rebuild/retest of the exact formatted binary. No build, browser, Git or live source changes were performed here. The prior sealed reviews remain unchanged.

Replay: `python3 artifacts/css-resolved-summary-format-review-v1/check.py`.

# Corrected ordinary-attr landing WPT lint

PASS: the exact corrected fixture5514fb6debf5f5ac8bd19d5fd01f1958932cd4539ec4e0a6743e880e71aef3ef passed the real WPT lint engine with exit0 and empty stdout/stderr. Its logical path was css/css-animations/ordinary-keyframe-attr-initial.html within a disposable WPT-root Git repository. The source bytes were unchanged.

Reused the prior duration isolated-root workflow and pinned --lint-worker610f5b2f. Every previously loaded lint module hash was checked before execution; loaded module pins were captured and checked afterward. The existing WPT Python virtualenv, ignore configuration, interpreter and actual argv/cwd are retained in SOURCE-PINS, LOADED-SOURCE-PINS and EXECUTION. The worker invokes the same tools.lint.lint engine used by WPT lint, with the logical CSS-suite path and one job. This is targeted scratch lint, not a broad mach lint or a browser result.

All temporary files and the scratch Git directory were removed. No main-tree WPT fixture, native source, browser/build state or repository index was changed. Firefox frontend and mozlint skills were read; existing sealed fixture/controller capsules remain untouched.

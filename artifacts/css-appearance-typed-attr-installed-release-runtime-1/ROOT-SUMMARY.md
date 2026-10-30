# Installed release observation

The installed Firefox 158.0 binary, BuildID 20261007201254, ran the exact portable four-case page under a fresh WPT stable-channel profile: 3 PASS / 1 FAIL, one OK ending. The variable-length case produces appearance auto instead of none at both 20px and 30px; literal-length, missing-attribute and literal font-family controls pass. Full failure data records correct registered lengths, font sizes and independent width controls. Browser harness exit1 reflects the retained unexpected failure; owner session62591/434c4b/f40deb exited0 with complete observations and cleanup.

Browser BuildID and changeset identify the installed application. Other run_info fields include the local harness revision and Nightly build configuration despite the empty run-info directory. They are not evidence of release build properties. This is a WPT-configured installed release test, not a normal user-profile/default-settings test. Six captured preference files are retained. The five application critical files and staged inputs checked by the owner are unchanged; the owned process group and temporary profile root were removed. No native source or installed application update was performed, and no fix is accepted.

Independent saved interpretation: ../css-appearance-typed-attr-installed-release-review-v1/README.md.

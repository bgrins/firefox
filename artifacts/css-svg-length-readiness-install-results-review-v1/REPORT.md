# Expanded fix114 installation review

GO: the sealed installation evidence verifies the accepted expanded fix114 on the preserved working stack. This is installation validation, not a new accepted defect or a pristine-upstream runtime claim.

Runtime FILES.json: `e040a6c2898219cd9d4292c185bb41174dfdaf44a6f52198137cbfa273127245`. All 30 manifest payloads authenticate. The independent raw recount finds exactly 25 unique PASS subtests and three OK harness completions, with complete matching source/resource/binary maps before and after WPT, no infrastructure faults, and owned process group cleanup. Build and lint both exited 0. Four retained Mach resource-monitor KeyError diagnostics do not change the recorded successful build exit.

The final source map differs only by the accepted DOMSVGLength.cpp update from `9a5759f20448150f17ec7d9b541fddb23cd1563a40057e8463272e325e78da8e` to `61ef0fd08580513477043c6a0ff7a42f709c07c5982d163f956db96e53b0e1b3`. The accepted114 header and accepted115 SVGLength.cpp remain unchanged. The sole new file is SVGLength-viewport-unit-iframe-resize.html (`a884d63f09f5a544c9edbb24befcec830ca5f25177eb7f8ad6e7a78c4e2dda09`). Its identity joins the seven preserved installed WPT identities.

The authenticated root receipt and installation records agree on 53 source guards, 392 complete pins, 30 native differences, unchanged HEAD/index identities and 925 staged paths. This review authenticates historical preservation receipts; it does not claim a later live-state inspection. Successful installation intentionally keeps the accepted source and test installed.

Installed binaries are Firefox `80126083083a3361d1f70d4bdf27507c97f23c2c43e5730030417e0bfdcdf4ea` and XUL `df9dbe7f01b1a7c06f9317b61bdd51fdb530a0bc41431e12d6ed56dc8fdeb45b`. These replace the historical comparison-restoration epoch. Exact acceptance and bound-controller references are in REFERENCES.json; the previously reviewed six-field binding and unchanged installer logic remain applicable.

Scope remains the 25 landing cases and the earlier normalized-HEAD 51-case comparison, with conditional flush-policy proofs. This review does not establish every parsed-unit/provider/lifetime path, compatibility across browsers, or hidden-subtree completion. The reviewer authored the comparison controller and new fixture; the updater was authored by a separate agent, and this report independently recounts its installed runtime evidence.

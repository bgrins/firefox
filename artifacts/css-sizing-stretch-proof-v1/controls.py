LEAN_MUTATIONS = {
    'omit-auto': ('&& s == .auto &&', '&&'),
    'omit-end-margin': ('!c.startAuto && !c.endAuto && s == .auto', '!c.startAuto && s == .auto'),
    'omit-clamp-fill': ('⟨stretch, stretch || c.clamp, c.clamp, false⟩', '⟨stretch, stretch, c.clamp, false⟩'),
}
CPP_MUTATIONS = {
    'omit-auto': (' &&\n            styleISize->IsAuto()', ''),
    'auto-to-maxcontent': ('&&\n            styleISize->IsAuto()', '&&\n            styleISize->IsMaxContent()'),
    'ignore-margins': ('if (!StyleMargin()->HasInlineAxisAuto(\n              aWM, AnchorPosResolutionParams::From(this))) {', 'if (true) {'),
    'omit-clamp-fill': ('aFlags.contains(ComputeSizeFlag::IClampMarginBoxMinSize)) {', 'false) {'),
    'retain-unconstrained-clamp': ('aFlags -= ComputeSizeFlag::IClampMarginBoxMinSize;', ';'),
}
